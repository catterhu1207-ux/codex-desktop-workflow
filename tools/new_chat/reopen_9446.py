"""Read six actually sent synthetic native chats after a cold application restart."""
from pathlib import Path
import json,os,sys,time,hashlib,threading
from http.server import ThreadingHTTPServer
from codex_desktop_workflow import workflow
from codex_desktop_workflow.isolated_run import IsolatedRun
from codex_desktop_workflow.awake_process import AwakeProcess
from codex_desktop_workflow.awake_clock import seconds
from codex_desktop_workflow.native_history_fixture import Handler

def qualify(app,runs_root,previous_round):
 app,runs_root=Path(app).resolve(),Path(runs_root).resolve()
 previous=json.loads(Path(previous_round).read_text());row=previous['round'];home=Path(row['codex_home']).resolve()
 assert previous['status']=='passed' and row['close']['close_status']=='closed' and home.is_relative_to(runs_root)
 sent=row['native_sidebar']['native_six_lifecycle']['records'];assert len(sent)==6
 config=home/'config.toml';original=config.read_bytes()
 assert b'model="fixture-model"' in original or b'model = "fixture-model"' in original
 server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 config.write_text(f'model_provider="fixture"\nmodel="fixture-global-changed"\nmodel_reasoning_effort="low"\n[model_providers.fixture]\nname="Synthetic cold restart"\nbase_url="http://127.0.0.1:{server.server_port}/v1"\nwire_api="responses"\nrequires_openai_auth=false\n[windows]\nsandbox="unelevated"\n',encoding='utf8')
 run=None;probe=None;result={'status':'failed','synthetic_only':True,'original_round_sha256':hashlib.sha256(Path(previous_round).read_bytes()).hexdigest()}
 try:
  port=workflow._available_loopback_port();run=IsolatedRun.start(app/'ChatGPT.exe',runs_root,environment=workflow._portable_environment(app,home),debug_port=port,isolate_shell_folders=True)
  spec=run.run_directory/'native-reopen-spec.json';workspace=home/'synthetic-workspaces'/'0';spec.write_text(json.dumps({'workspace':str(workspace),'sent':sent}))
  env=dict(os.environ,ISOLATED_DEBUG_PORT=str(port),ISOLATED_RUNTIME_LOG=str(run.run_directory/'stdout.log'),NATIVE_REOPEN_SPEC=str(spec))
  probe=AwakeProcess(['node',str(Path(__file__).with_name('native_reopen_9446.cjs'))],env=env,root=run.run_directory)
  manifest=app/'codex-desktop-workflow-manifest.json';artifact=json.loads(manifest.read_text())['frontend_runtime_attestation']['live_renderer_probe']['artifact_id']
  deadline=seconds()+240;proof=None;started=None
  while seconds()<deadline:
   state=run.status('codex.exe');workflow._request_renderer_attestation(port)
   fresh=workflow._attestations(home,artifact,(run.run_directory/'stdout.log',run.run_directory/'stderr.log'),manifest=manifest,run_directory=run.run_directory,process=state.get('main'))
   if fresh.get('status')=='passed' and started is None:
    proof=fresh;started=seconds();deadline=started+60
    (run.run_directory/'renderer-proof-accepted.json').write_text(json.dumps(fresh))
   time.sleep(1)
  assert proof and seconds()-started>=60,'Fresh same-run proof/observation missing'
  stdout,stderr=probe.communicate(timeout=45)
  (run.run_directory/'native-reopen-command.json').write_text(json.dumps({'returncode':probe.returncode,'stdout':stdout.decode(),'stderr':stderr.decode()},indent=2))
  if probe.returncode:raise RuntimeError(stderr.decode()[-2400:])
  native=json.loads(stdout);assert native['status']=='passed' and len(native['records'])==6
  state=run.status('codex.exe');assert workflow._current_app_server_match(state,app,row['backend_expected_sha256'])
  result.update(status='passed',native=native,backend_identity=state,proof=proof,observed_seconds=seconds()-started,backend_sha256=row['backend_expected_sha256'])
 except BaseException as error:result['error']=str(error);raise
 finally:
  if probe and probe.poll() is None:probe.terminate();probe.wait(timeout=10)
  if run:
   result['close']=workflow._normal_codex_stop(run,30);result['run_directory']=str(run.run_directory)
   if result['close'].get('close_status')!='closed':result['status']='failed'
  config.write_bytes(original);assert config.read_bytes()==original
  server.shutdown();server.server_close()
  (runs_root/'native-six-cold-reopen-result.json').write_text(json.dumps(result,indent=2))
 return result

if __name__=='__main__':
 value=qualify(*sys.argv[1:4]);print(json.dumps({'status':value['status'],'run_directory':value['run_directory']}))
