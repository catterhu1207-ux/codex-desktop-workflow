"""Exercise the packaged update component in a separate synthetic profile."""
from pathlib import Path
import json, os, sys, time
from codex_desktop_workflow import workflow, awake_clock
from codex_desktop_workflow.awake_process import AwakeProcess
from codex_desktop_workflow.renderer_proof import parse_owned_logs
from codex_desktop_workflow.isolated_run import IsolatedRun


def main():
    portable=Path(sys.argv[1]).resolve();root=Path(sys.argv[2]).resolve()
    root.mkdir(parents=True,exist_ok=False)
    home=root/'home';home.mkdir()
    identity=json.loads((portable/'codex-desktop-workflow.json').read_bytes())
    for name,key in [('resources/app.asar','portable_asar_sha256'),('resources/codex.exe','backend_sha256')]:
        if workflow._sha256(portable/name)!=identity[key]:raise RuntimeError('candidate_identity_changed')
    env=workflow._portable_environment(portable,home)
    port=workflow._available_loopback_port()
    run=IsolatedRun.start(portable/'ChatGPT.exe',root,environment=env,debug_port=port,isolate_shell_folders=True)
    probe=None;result=None
    try:
        environment=dict(os.environ,**env)
        environment.update(ISOLATED_DEBUG_PORT=str(port),ISOLATED_RUNTIME_LOG=str(run.run_directory/'stdout.log'),ISOLATED_CODEX_HOME=str(home),PUBLIC_NATIVE_DATA=str(Path(workflow.__file__).parent/'data'),PUBLIC_UPDATE_CACHE=str(home/'.cache/codex-desktop-workflow/official-update-awareness.json'))
        probe=AwakeProcess(['node',str(Path(__file__).with_name('run.cjs'))],env=environment,root=run.run_directory)
        started=awake_clock.seconds();stdout,stderr=probe.communicate(timeout=150)
        if probe.returncode:raise RuntimeError('native_icon_probe_failed: '+stderr.decode('utf8',errors='replace')[-2000:])
        result=json.loads(stdout.decode('utf8').strip().splitlines()[-1])
        if result.get('status')!='passed':raise RuntimeError('native_icon_result_rejected')
        while awake_clock.seconds()-started<60:time.sleep(.25)
        status=run.status('codex.exe')
        if not workflow._current_app_server_match(status,portable,identity['backend_sha256']):raise RuntimeError('backend_identity_mismatch')
    finally:
        if probe is not None and probe.poll() is None:probe.terminate();probe.wait(10)
        close=workflow._normal_codex_stop(run,30)
    if close.get('close_status')!='closed':raise RuntimeError('native_icon_normal_close_failed')
    proof=parse_owned_logs(portable/'codex-desktop-workflow-manifest.json',run.run_directory,status['main'])
    if proof.get('status')!='passed':raise RuntimeError('native_icon_renderer_proof_failed')
    result.update(renderer_proof=proof,backend_identity=status,close=close,run_directory=str(run.run_directory),observed_seconds=awake_clock.seconds()-started)
    (root/'result.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print('Actual packaged update component: three distinct icons passed.',flush=True)


if __name__=='__main__':main()
