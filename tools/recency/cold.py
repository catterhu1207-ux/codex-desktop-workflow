"""Cold-start the same generated fixture, observe and quit normally."""
import argparse,json,os,re,sqlite3,subprocess,time
from pathlib import Path
from codex_desktop_workflow import workflow as w
from codex_desktop_workflow.isolated_run import IsolatedRun
from mock_responses import FixtureServer
p=argparse.ArgumentParser();p.add_argument('--portable',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--mode',required=True);a=p.parse_args()
r=json.loads((a.output/(a.mode+'-run.json')).read_text());assert r['synthetic_only']
home=Path(r['home'])
assert (home/'synthetic-fixture.json').is_file()
service=FixtureServer().start();service.release.set()
config=home/'config.toml'
config.write_text(re.sub(r'base_url="http://127\.0\.0\.1:\d+/v1"',f'base_url="http://127.0.0.1:{service.port}/v1"',config.read_text()),encoding='utf8')
with sqlite3.connect((home/'state_5.sqlite').as_uri()+'?mode=ro',uri=True) as db:
 before=db.execute('select id,model_provider,sandbox_policy,approval_mode,recency_at,recency_at_ms from threads order by id').fetchall()
port=w._available_loopback_port();run=IsolatedRun.start(a.portable/'ChatGPT.exe',a.output/'cold-runs',environment=w._portable_environment(a.portable,home),debug_port=port,isolate_shell_folders=True)
(a.output/(a.mode+'-cold-run.json')).write_text(json.dumps({**r,'debug_port':port,'run_directory':str(run.run_directory)}),encoding='utf8')
try:
 subprocess.run(['node',str(Path(__file__).with_name('cold.cjs')),a.mode],env={**os.environ,'RECENCY_OUTPUT':str(a.output)},check=True)
 state=run.status('codex.exe');expected=w._sha256(a.portable/'resources/codex.exe');assert w._current_app_server_match(state,a.portable,expected)
 close=w._normal_codex_stop(run,30);assert close['close_status']=='closed'
 with sqlite3.connect((home/'state_5.sqlite').as_uri()+'?mode=ro',uri=True) as db:
  after=db.execute('select id,model_provider,sandbox_policy,approval_mode,recency_at,recency_at_ms from threads order by id').fetchall()
 assert before==after,'Cold startup changed task settings or recency'
 (a.output/(a.mode+'-cold-result.json')).write_text(json.dumps({'status':'passed','settings_and_times_preserved':True,'backend_match':True,'close_status':'closed','task_count':len(after)}),encoding='utf8')
 print('Cold order and task settings retained',flush=True)
finally:
 service.close()
 if run.status('codex.exe').get('status')=='running':w._normal_codex_stop(run,30)
