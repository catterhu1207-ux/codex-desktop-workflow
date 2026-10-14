"""Bound process ancestry to identities, including Windows PID reuse."""
from dataclasses import asdict
import json
import os
from pathlib import Path
import re
import subprocess
import time

from electron_update_safety import lifecycle
from .awake_clock import seconds
from .awake_process import run as run_awake


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
