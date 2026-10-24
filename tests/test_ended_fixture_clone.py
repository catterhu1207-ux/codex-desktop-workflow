import json,sqlite3,tempfile,tomllib,unittest
from contextlib import closing
from pathlib import Path
from unittest import mock
from codex_desktop_workflow import native_history_fixture as fixture,workflow
from codex_desktop_workflow.isolated_run import IsolatedRun

def prepare(directory):
    source=Path(directory)/'fixture-source';source.mkdir()
    target=Path(directory)/'fixture-target';run=Path(directory)/('run-'+'a'*32);run.mkdir()
    (source/'.browser-isolation-used.json').write_text(json.dumps({'run':str(run)}))
    (source/'native-history-fixture.json').write_text(json.dumps({'count':1,'ids':['synthetic-id'],
        'all_created_and_sent_by_actual_backend':True,'user_data_copied':False}))
    (source/'qualified-synthetic-files.json').write_text('{}')
    (source/'config.toml').write_text('model_provider="fixture"\nmodel="fixture-cold-global"\nmodel_reasoning_effort="low"\n[model_providers.fixture]\nbase_url="http://127.0.0.1:12345/v1"\nrequires_openai_auth=false\n')
    (source/'sessions').mkdir();history=source/'sessions/fixture.jsonl';history.write_text('{"synthetic":true}\n')
    with closing(sqlite3.connect(source/'state_5.sqlite')) as db:
        db.execute('create table threads(id text,rollout_path text)')
        db.execute('insert into threads values (?,?)',('synthetic-id',str(history)))
        db.commit()
    return source,target,run

class EndedFixtureClone(unittest.TestCase):
    def test_fixture_clone_preserves_sources_and_excludes_login_and_install_state(self):
        with tempfile.TemporaryDirectory() as directory:
            source,target,run=prepare(directory)
            (source/'auth.json').write_text('synthetic secret')
            (source/'plugins').mkdir();(source/'plugins/private-state').write_text('synthetic state')
            original=(source/'state_5.sqlite').read_bytes();raw=(source/'sessions/fixture.jsonl').read_bytes()
            with mock.patch.object(IsolatedRun,'status',return_value={'status':'exited'}):
                result=fixture.clone_ended(source,target,run)
            self.assertEqual(result['count'],1)
            self.assertEqual((source/'state_5.sqlite').read_bytes(),original)
            self.assertEqual((source/'sessions/fixture.jsonl').read_bytes(),raw)
            self.assertEqual((target/'sessions/fixture.jsonl').read_bytes(),raw)
            self.assertFalse((target/'auth.json').exists());self.assertFalse((target/'plugins').exists())
            with closing(sqlite3.connect(target/'state_5.sqlite')) as db:
                self.assertEqual(db.execute('select rollout_path from threads').fetchone()[0],str(target/'sessions/fixture.jsonl'))

    def test_desktop_added_hooks_plugins_and_mcp_are_not_cloned(self):
        with tempfile.TemporaryDirectory() as directory:
            source,target,run=prepare(directory)
            config=source/'config.toml'
            config.write_text(config.read_text()+'\n[plugins.synthetic]\nenabled=true\n[marketplaces.synthetic]\nsource="unused"\n[mcp_servers.synthetic]\ncommand="must-not-run"\n[windows]\nsandbox="unelevated"\n')
            original=config.read_bytes()
            with mock.patch.object(IsolatedRun,'status',return_value={'status':'exited'}):fixture.clone_ended(source,target,run)
            copied=tomllib.loads((target/'config.toml').read_text())
            self.assertNotIn('plugins',copied);self.assertNotIn('marketplaces',copied);self.assertNotIn('mcp_servers',copied)
            self.assertEqual(copied['model'],'fixture-cold-global');self.assertEqual(copied['model_reasoning_effort'],'low')
            self.assertEqual(copied['windows']['sandbox'],'unelevated');self.assertEqual(config.read_bytes(),original)

    def test_normal_import_keeps_its_global_process_guard(self):
        with tempfile.TemporaryDirectory() as directory:
            source,target,_=prepare(directory)
            with mock.patch.object(workflow,'_running_codex_processes',return_value=[{'ProcessId':123}]):
                with self.assertRaisesRegex(workflow.WorkflowError,'codex_processes_must_exit'):workflow.import_data(source,target)
            self.assertFalse(target.exists())

    def test_active_source_and_nonlocal_model_provider_stop_before_copy(self):
        from codex_desktop_workflow.isolated_run import IsolatedRun
        for conflict in ('active','provider','ownership'):
            with self.subTest(conflict=conflict),tempfile.TemporaryDirectory() as directory:
                source,target,run=prepare(directory)
                if conflict=='provider':
                    config=source/'config.toml';config.write_text(config.read_text().replace('127.0.0.1:12345','example.invalid'))
                if conflict=='ownership':(source/'.browser-isolation-used.json').write_text('{"run":"unrelated"}')
                with mock.patch.object(IsolatedRun,'status',return_value={'status':'running' if conflict=='active' else 'exited'}):
                    with self.assertRaises(ValueError):fixture.clone_ended(source,target,run)
                self.assertFalse(target.exists())

if __name__=='__main__':unittest.main()
