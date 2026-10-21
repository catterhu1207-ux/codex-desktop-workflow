"""Bound process ancestry to identities, including Windows PID reuse."""
from dataclasses import asdict
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import time
import socket
import uuid
from datetime import datetime, timezone

from electron_update_safety import lifecycle
from .awake_clock import seconds
from .awake_process import run as run_awake


def _redirected(path):
    """Reject symlinks/reparse points using APIs available in Python 3.11."""
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, 'st_file_attributes', 0) & 0x400)


def _created(identity):
    match = re.fullmatch(r'/Date\((\d+)(?:[+-]\d{4})?\)/', identity.created)
    if not match:
        raise RuntimeError('process_creation_identity_unavailable')
    return int(match.group(1))


def descendants(rows, expected_main):
    by_pid = {row.pid: row for row in rows}
    if len(by_pid) != len(rows):
        raise RuntimeError('ambiguous_process_snapshot')
    if not lifecycle._same(expected_main, by_pid.get(expected_main.pid)):
        return []
    children = {}
    for row in rows:
        children.setdefault(row.parent_pid, []).append(row)
    visited = {expected_main.pid}
    frontier = [expected_main]
    result = []
    while frontier:
        parent = frontier.pop()
        parent_created = _created(parent)
        for child in children.get(parent.pid, []):
            if child.pid in visited:
                continue
            visited.add(child.pid)
            # A child born before this incarnation of its parent refers to a
            # reused PID, not a descendant of the owned application.
            if _created(child) < parent_created:
                continue
            result.append(child)
            frontier.append(child)
    return result


class IsolatedRun(lifecycle.IsolatedRun):
    @classmethod
    def start(cls, executable, runs_root, args=None, environment=None, debug_port=None, isolate_shell_folders=False):
        arguments=list(args or [])
        metadata=Path(executable).parent/'codex-desktop-workflow-manifest.json'
        if metadata.is_file() and json.loads(metadata.read_text(encoding='utf8')).get('package_version') in ('26.1007.9446.0','26.1013.4894.0','26.1016.6573.0'):
            if not any(value.startswith('--lang=') or value == '--lang' for value in arguments):
                arguments.append('--lang=en-US')
        if debug_port is not None and metadata.is_file() and json.loads(metadata.read_text(encoding='utf8')).get('package_version') in ('26.1007.9446.0','26.1013.4894.0','26.1016.6573.0'):
            for flag in ('--disable-renderer-backgrounding','--disable-background-timer-throttling','--disable-features=CalculateNativeWinOcclusion'):
                if flag not in arguments:arguments.append(flag)
        if metadata.is_file() and json.loads(metadata.read_text(encoding='utf8')).get('package_version') in ('26.1013.4894.0','26.1016.6573.0'):
            environment = dict(environment or {})
            if not environment.get('CODEX_HOME') or not Path(environment['CODEX_HOME']).is_absolute():
                raise ValueError('explicit_absolute_codex_home_required')
            home = Path(environment['CODEX_HOME']).resolve()
            if isolate_shell_folders and (not home.is_relative_to(Path(runs_root).resolve()) or home == Path(runs_root).resolve()):
                raise ValueError('4894_acceptance_home_must_be_inside_owned_runs_root')
            return cls._start_owl(executable, runs_root, home, arguments, environment, debug_port, isolate_shell_folders)
        return super().start(executable,runs_root,args=arguments,environment=environment,debug_port=debug_port,isolate_shell_folders=isolate_shell_folders)

    @classmethod
    def _start_owl(cls, executable, runs_root, home, arguments, environment, debug_port, isolate_shell_folders):
        """Keep Owl known folders readable while owning all application state."""
        executable = Path(executable).resolve(strict=True)
        if any(a.startswith('--user-data-dir') for a in arguments):
            raise ValueError('user_data_dir_is_managed_by_the_tool')
        for key in ('USERPROFILE', 'LOCALAPPDATA', 'APPDATA'):
            if key in environment: raise ValueError('protected_environment_override:'+key)
        if debug_port is not None:
            with socket.socket() as probe: probe.bind(('127.0.0.1', debug_port))
            arguments = [*arguments, '--remote-debugging-address=127.0.0.1', f'--remote-debugging-port={debug_port}']
        run = Path(runs_root).resolve() / ('run-'+uuid.uuid4().hex)
        run.mkdir(parents=True, exist_ok=False)
        profile = Path(runs_root).resolve()/'profile-4894' if isolate_shell_folders else Path(os.environ['USERPROFILE'])
        user_data = run/'user-data' if isolate_shell_folders else home/'.electron-user-data'
        if _redirected(user_data): raise ValueError('redirected_user_data')
        if isolate_shell_folders:
            if _redirected(profile): raise ValueError('redirected_owned_profile')
            profile.mkdir(exist_ok=True)
        user_data.mkdir(exist_ok=True)
        env = {**os.environ, **environment}
        for key in ('CODEX_APP_TOOLS_PIPE_PATH', 'CODEX_MCP_NODE_PATH', 'CODEX_TECTONIC_PATH'):
            env.pop(key, None)
        temporary = run/'temp'; temporary.mkdir()
        env.update(TEMP=str(temporary), TMP=str(temporary), USERPROFILE=str(profile), CODEX_HOME=str(home), CODEX_SQLITE_HOME=str(home),
                   CODEX_ELECTRON_USER_DATA_PATH=str(user_data),
                   CODEX_CLI_PATH=str(executable.parent/'resources/codex.exe'))
        record = dict(schema_version=1, status='starting', run_id=run.name,
                      started_at=datetime.now(timezone.utc).isoformat(), registered_backends=[],
                      executable_sha256=lifecycle._sha256(executable),
                      shell_folders=('owl_explicit_profile_home_known_folders_inherited' if isolate_shell_folders else 'owl_persistent_data_inherited_user_profile'), debug_port=debug_port)
        instance = cls(run); instance._save(record)
        with (run/'stdout.log').open('xb') as stdout, (run/'stderr.log').open('xb') as stderr:
            process = subprocess.Popen([str(executable), *arguments, f'--user-data-dir={user_data}'],
                cwd=executable.parent, env=env, stdout=stdout, stderr=stderr,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        instance._process = process
        time.sleep(.2)
        current = next((p for p in lifecycle._processes() if p.pid == process.pid), None)
        if current is None:
            record.update(status='failed_before_identity_capture', exit_code=process.poll(), pid=process.pid)
            instance._save(record)
            raise RuntimeError('main_exited_before_identity_capture:'+str(run))
        record.update(status='started', main=asdict(current)); instance._save(record)
        return instance

    def _snapshot(self):
        if os.name != 'nt':
            raise RuntimeError('process_inspection_requires_windows')
        command = "$ErrorActionPreference='Stop'; [Console]::OutputEncoding=[System.Text.UTF8Encoding]::new(); Get-CimInstance -Namespace root/cimv2 Win32_Process -ErrorAction Stop | Select-Object ProcessId,ParentProcessId,ExecutablePath,CreationDate | ConvertTo-Json -Compress"
        last_error=None
        for attempt in range(3):
            try:
                result = run_awake(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', command],
                                   env=os.environ.copy(), root=self.run_directory, timeout=15)
                if result.returncode:
                    raise RuntimeError('process_snapshot_command_failed:'+result.stderr[-400:])
                values = json.loads(result.stdout)
                if isinstance(values, dict):values=[values]
                if not isinstance(values,list) or not values:raise RuntimeError('empty_process_snapshot')
                rows=[lifecycle.ProcessIdentity(int(row['ProcessId']), int(row['ParentProcessId']),
                    row.get('ExecutablePath') or '', row.get('CreationDate') or '') for row in values]
                return rows
            except (RuntimeError,ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError) as error:
                if str(error).startswith('acceptance_awake_clock_unavailable'):raise
                last_error=error
                with (self.run_directory/'process-snapshot-retries.jsonl').open('a',encoding='utf8') as log:
                    log.write(json.dumps({'attempt':attempt+1,'error':str(error),'successful_snapshot_required':True})+'\n')
                if attempt<2:time.sleep(.2)
        raise RuntimeError('process_snapshot_failed_after_three_reads') from last_error

    def status(self, backend_name=None):
        self._reap_started_process()
        record = self._load()
        rows = self._snapshot()
        by_pid = {row.pid: row for row in rows}
        expected = lifecycle.ProcessIdentity(**record['main'])
        main_alive = lifecycle._same(expected, by_pid.get(expected.pid))
        owned = descendants(rows, expected)
        if backend_name:
            for row in owned:
                if Path(row.executable).name.casefold() == backend_name.casefold() and asdict(row) not in record['registered_backends']:
                    record['registered_backends'].append(asdict(row))
            self._save(record)
        registered = [lifecycle.ProcessIdentity(**row) for row in record['registered_backends']]
        alive = [asdict(row) for row in registered if lifecycle._same(row, by_pid.get(row.pid))]
        state = 'running' if main_alive else 'exited'
        if main_alive and backend_name and not record['registered_backends']:
            state = 'running_without_backend'
        if not main_alive and alive:
            state = 'backend_orphaned'
        return {**record, 'status': state, 'main_identity_match': main_alive, 'alive_backends': alive,
                'process_tree_validation': 'visited_identity_and_creation_order'}

    def wait_for_exit(self, timeout, backend_name=None):
        deadline = seconds() + timeout
        while True:
            result = self.status(backend_name)
            if result['status'] == 'exited':
                return result
            if seconds() >= deadline:
                return {**result, 'wait_status': 'timeout'}
            time.sleep(.2)
