"""Mount all three English update states in one owned synthetic startup."""
from pathlib import Path
import json,os,sys,time,threading,subprocess
from http.server import ThreadingHTTPServer
from codex_desktop_workflow import workflow,awake_clock
from codex_desktop_workflow.awake_process import AwakeProcess
from codex_desktop_workflow.isolated_run import IsolatedRun
from codex_desktop_workflow.native_history_fixture import Handler
from codex_desktop_workflow.renderer_proof import parse_owned_logs
from codex_desktop_workflow.owned_verification import SpaceJob,owned_process_images,qualified_auxiliary
from codex_desktop_workflow.brokered_processes import pending_elevations


def worker(app,root):
    root.mkdir(parents=True,exist_ok=False);home=root/'home';home.mkdir()
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
    (home/'config.toml').write_text(f'model_provider="fixture"\nmodel="fixture-model"\n[model_providers.fixture]\nname="Synthetic English UI"\nbase_url="http://127.0.0.1:{server.server_port}/v1"\nwire_api="responses"\nrequires_openai_auth=false\n[windows]\nsandbox="unelevated"\n')
    (home/'.codex-global-state.json').write_text(json.dumps({'electron-persisted-atom-state':{'electron-language':'en'},'desktop-first-seen-at-ms':int(time.time()*1000)-86400000}))
    public=json.loads((app/'codex-desktop-workflow.json').read_text())
    assert public['portable_asar_sha256']==workflow._sha256(app/'resources/app.asar')
    assert public['backend_sha256']==workflow._sha256(app/'resources/codex.exe')
    env=workflow._portable_environment(app,home);port=workflow._available_loopback_port()
    run=IsolatedRun.start(app/'ChatGPT.exe',root,environment=env,debug_port=port,isolate_shell_folders=True)
    probe=None;value=None;started=awake_clock.seconds()
    try:
        environment=dict(os.environ,**env,ISOLATED_DEBUG_PORT=str(port),ISOLATED_RUNTIME_LOG=str(run.run_directory/'stdout.log'),ISOLATED_CODEX_HOME=str(home),PUBLIC_RENDERER_MODULE=str(app/'resources/x.js'))
        probe=AwakeProcess(['node',str(Path(__file__).with_suffix('.cjs'))],env=environment,root=run.run_directory)
        stdout,stderr=probe.communicate(timeout=300)
        if probe.returncode:raise RuntimeError('mounted_english_updates_failed:'+stderr.decode('utf8',errors='replace')[-1800:])
        value=json.loads(stdout.decode('utf8').strip().splitlines()[-1]);assert value['status']=='passed'
        while awake_clock.seconds()-started<60:time.sleep(.25)
        status=run.status('codex.exe');assert workflow._current_app_server_match(status,app,public['backend_sha256'])
    finally:
        if probe is not None and probe.poll() is None:probe.terminate();probe.wait(10)
        close=workflow._normal_codex_stop(run,30);server.shutdown();server.server_close()
    assert close['close_status']=='closed'
    value.update(close=close,backend_identity=status,run_directory=str(run.run_directory),observed_seconds=awake_clock.seconds()-started)
    (root/'result.json').write_text(json.dumps(value,indent=2),encoding='utf8')


def main():
    if sys.argv[1]=='--worker':
        assert sys.stdin.buffer.readline()==b'release-english-ui-worker\n'
        return worker(*map(Path,sys.argv[2:4]))
    app,root=map(lambda p:Path(p).resolve(),sys.argv[1:3]);assert pending_elevations(app)['status']=='none_for_owned_candidate'
    job=SpaceJob();process=None
    try:
        process=subprocess.Popen([sys.executable,'-B',__file__,'--worker',str(app),str(root)],stdin=subprocess.PIPE,creationflags=0x08000000)
        job.assign(process);process.stdin.write(b'release-english-ui-worker\n');process.stdin.close()
        deadline=awake_clock.seconds()+600
        while process.poll() is None:
            if awake_clock.seconds()>=deadline:raise RuntimeError('english_ui_worker_awake_timeout')
            time.sleep(.25)
        if process.returncode:raise RuntimeError('english_ui_worker_failed')
        pending=owned_process_images(job)
        if any(not qualified_auxiliary(row['image']) for row in pending):raise RuntimeError('unexpected_owned_english_ui_descendant')
        if pending:job.stop_and_wait()
        assert not job.pids()
        after=pending_elevations(app);assert after['status']=='none_for_owned_candidate'
        value=json.loads((root/'result.json').read_text());status=value['backend_identity']
        proof=parse_owned_logs(app/'codex-desktop-workflow-manifest.json',Path(value['run_directory']),status['main']);assert proof['status']=='passed'
        value.update(owned_cleanup={'owned_job_empty':True,'auxiliary_processes':pending},brokered_prompts=after,proof=proof,closed_log_readback='passed')
        (root/'result.json').write_text(json.dumps(value,indent=2),encoding='utf8')
        print('Three actual English sidebar states and distinct icons passed.')
    finally:
        job.close()
        if process is not None and process.poll() is None:process.terminate();process.wait(15)


if __name__=='__main__':main()
