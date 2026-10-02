"""Run the public build through a credential-free native composer fixture."""
import argparse,json,os,sqlite3,subprocess,time,urllib.request
from pathlib import Path
from codex_desktop_workflow import workflow as w
from codex_desktop_workflow.isolated_run import IsolatedRun
from bootstrap_fixture import seed
from native_fixture_projects import prepare
from mock_responses import FixtureServer

parser=argparse.ArgumentParser()
parser.add_argument('--portable',type=Path,required=True)
parser.add_argument('--empty-home',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--mode',choices=['official','compat'],required=True)
a=parser.parse_args();a.output.mkdir(parents=True,exist_ok=False)
service=FixtureServer().start();home=a.output/'synthetic-home'
fixtures=seed(home,a.empty_home,service.port)
prepare(home,a.portable/'resources/codex.exe')
port=w._available_loopback_port()
run=IsolatedRun.start(a.portable/'ChatGPT.exe',a.output/'runs',environment=w._portable_environment(a.portable,home),debug_port=port,isolate_shell_folders=True)
record={'run_directory':str(run.run_directory),'debug_port':port,'fixtures':fixtures,'synthetic_only':True,'backend':str(a.portable/'resources/codex.exe'),'home':str(home),'run_id':run.run_directory.name,'task_count':400}
with sqlite3.connect(home/'state_5.sqlite') as db:record['group_peer']=db.execute("select id from threads where title='Synthetic task 27'").fetchone()[0]
(a.output/(a.mode+'-run.json')).write_text(json.dumps(record),encoding='utf8')
print(json.dumps({'mode':a.mode,'port':port,'run':str(run.run_directory)}),flush=True)
env={**os.environ,'RECENCY_OUTPUT':str(a.output)}
try:
 for i in range(180):
  try:
   with urllib.request.urlopen(f'http://127.0.0.1:{port}/json/list',timeout=2) as reply:
    pages=json.load(reply)
   if any(p.get('url')=='app://-/index.html' for p in pages):break
  except Exception:pass
  time.sleep(1)
 else:raise RuntimeError('Primary renderer unavailable')
 subprocess.run(['node',str(Path(__file__).with_name('native_start_acceptance.cjs')),a.mode],env=env,check=True)
 print('Native start acceptance passed; additional UI checks may now run',flush=True)
 while not (a.output/'finish').exists():
  (a.output/'requests.json').write_text(json.dumps(service.requests),encoding='utf8')
  time.sleep(1)
 latest=run.status('codex.exe')
 expected=w._sha256(a.portable/'resources/codex.exe')
 assert w._current_app_server_match(latest,a.portable,expected)
 close=w._normal_codex_stop(run,30)
 assert close.get('close_status')=='closed',close
 (a.output/'result.json').write_text(json.dumps({'status':'passed','backend_sha256':expected,'backend_match':True,'close_status':'closed','profile':'synthetic_tasks','real_composer':True}),encoding='utf8')
finally:
 service.close()
 if run.status('codex.exe').get('status')=='running':w._normal_codex_stop(run,30)
