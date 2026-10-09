"""Real native UI first-send and cold recovery against synthetic services only."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import threading
import time
import uuid
from http.server import ThreadingHTTPServer
from synthetic_service import Client, Handler
from codex_desktop_workflow.isolated_run import IsolatedRun
from codex_desktop_workflow import workflow
from codex_desktop_workflow.awake_process import run as run_awake
from codex_desktop_workflow.awake_clock import seconds


def qualify(app: Path, runs_root: Path) -> dict:
    app, runs_root = app.resolve(), runs_root.resolve()
    home = runs_root / ('native-home-' + uuid.uuid4().hex)
    workspace = home / 'workspace'
    workspace.mkdir(parents=True)
    binary = app / 'resources/codex.exe'
    digest = hashlib.sha256(binary.read_bytes()).hexdigest()
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    (home / 'config.toml').write_text(
        f'model_provider="custom"\nmodel="fixture-model"\nmodel_reasoning_effort="medium"\n'
        f'[model_providers.custom]\nname="Synthetic loopback"\n'
        f'base_url="http://127.0.0.1:{server.server_port}/v1"\nwire_api="responses"\nrequires_openai_auth=false\n', encoding='utf8')
    report = {'status': 'failed', 'backend_sha256': digest, 'synthetic_only': True,
              'encrypted_ssh_transport_tested': False}
    run = None
    try:
        port = workflow._available_loopback_port()
        run = IsolatedRun.start(app / 'ChatGPT.exe', runs_root,
            environment=workflow._portable_environment(app, home), debug_port=port, isolate_shell_folders=True)
        env = os.environ.copy()
        env.update(ISOLATED_DEBUG_PORT=str(port), SYNTHETIC_WORKSPACE=str(workspace))
        cp = run_awake(['node', str(Path(__file__).with_name('native_scope_lifecycle.cjs'))],
            env=env, root=run.run_directory, timeout=240)
        (run.run_directory / 'native-new-chat-command.json').write_text(json.dumps({
            'returncode': cp.returncode, 'stdout': cp.stdout, 'stderr': cp.stderr}, indent=2), encoding='utf8')
        if cp.returncode:
            raise RuntimeError('native_new_chat_failed: ' + cp.stderr[-1800:])
        ui = json.loads(cp.stdout)
        if ui.get('status') != 'passed' or not ui.get('actual_ui_manager_rpc') or len(ui.get('sent', [])) != 6:
            raise RuntimeError('native_new_chat_evidence_incomplete')
        report['ui'] = ui
        observations = []
        deadline = seconds() + 40
        stable = 0
        previous = None
        while seconds() < deadline and stable < 2:
            state = run.status('codex.exe')
            if not state.get('main_identity_match'):
                raise RuntimeError('native_new_chat_main_identity_mismatch')
            matched = workflow._current_app_server_match(state, app, digest)
            identities = [(p['pid'], p['created']) for p in state.get('alive_backends', [])]
            observations.append({'state': state, 'backend_match': matched})
            stable = stable + 1 if matched and identities == previous else (1 if matched else 0)
            previous = identities
            time.sleep(1)
        report['backend_observations'] = observations
        if stable < 2:
            raise RuntimeError('native_new_chat_backend_identity_mismatch')
        close = workflow._normal_codex_stop(run, 30)
        if close.get('close_status') != 'closed':
            raise RuntimeError('native_new_chat_close_failed')
        cold = Client(binary, home, workspace)
        recovered = []
        try:
            for row in ui['sent']:
                reply = cold.call('thread/resume', {'threadId': row['id'], 'historyMode': 'paginated'})
                if 'error' in reply:
                    raise RuntimeError(str(reply))
                result = reply['result']
                thread = result['thread']
                raw_path = thread['path']
                if raw_path.startswith('\\\\?\\'):
                    if len(raw_path)<7 or not raw_path[4].isalpha() or raw_path[5:7]!=':\\':
                        raise RuntimeError('unexpected_extended_rollout_path')
                    raw_path=raw_path[4:]
                path = Path(raw_path).resolve()
                if thread['id'] != row['id'] or result['model'] != 'fixture-model' or not path.is_relative_to(home):
                    raise RuntimeError('cold_identity_model_or_path_mismatch')
                page = cold.call('thread/turns/list', {'threadId': row['id'], 'limit': 10})
                if 'error' in page:
                    raise RuntimeError(str(page))
                turns = page['result']['data']
                if not turns or not all(t['status'] == 'completed' for t in turns):
                    raise RuntimeError('cold_completed_turn_missing')
                raw = json.dumps(turns)
                if 'Synthetic native facade first send ' + str(row['index']) not in raw or 'Synthetic completed.' not in raw:
                    raise RuntimeError('cold_sent_content_missing')
                recovered.append({'id': row['id'], 'model': result['model'], 'content_verified': True,
                                  'rollout_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        finally:
            cold.close()
        report.update(status='passed', run_directory=str(run.run_directory), home=str(home),
                      ui=ui, cold_recovery=recovered, normal_close=close)
        return report
    except BaseException as error:
        report['error'] = str(error)
        raise
    finally:
        if run is not None and run.status('codex.exe').get('main_identity_match'):
            workflow._normal_codex_stop(run, 30)
        server.shutdown()
        server.server_close()
        (home / 'new-chat-result.json').write_text(json.dumps(report, indent=2), encoding='utf8')
