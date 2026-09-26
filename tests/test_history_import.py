import hashlib,json,shutil,sqlite3,tempfile,unittest
from pathlib import Path
from unittest import mock
from codex_desktop_workflow import history,workflow
import test_inherited_fork_history_base as fixtures
from contextlib import closing

class HistoryImport(unittest.TestCase):
    def fixture(self):
        source=fixtures.InheritedForkHistoryBaseTests('test_original_fork_of_archived_logical_parent_has_exact_ancestor_prefix')
        source.setUp();self.addCleanup(source.temp.cleanup)
        with closing(sqlite3.connect(source.root/'state_5.sqlite')) as c:
            c.execute('CREATE TABLE threads(id TEXT PRIMARY KEY,rollout_path TEXT,archived INTEGER,history_mode TEXT)')
            for tid,path in source.paths.items():c.execute('INSERT INTO threads VALUES(?,?,?,?)',(tid,str(path),int(path.parent==source.archived),'paginated'))
            c.commit()
        with closing(sqlite3.connect(source.root/'thread_history_1.sqlite')) as c:
            c.execute('CREATE TABLE thread_history_projection_state(thread_id TEXT PRIMARY KEY,next_rollout_byte_offset INTEGER,next_rollout_ordinal INTEGER)')
            for tid,path in source.paths.items():c.execute('INSERT INTO thread_history_projection_state VALUES(?,?,?)',(tid,path.stat().st_size,source.records[tid][-1]['ordinal']+1))
            c.commit()
        return source

    def test_indirect_fork_import_uses_only_target_paths_and_preserves_bytes(self):
        fixture=self.fixture();source=fixture.root
        before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*') if p.is_file()}
        with tempfile.TemporaryDirectory() as raw:
            target=Path(raw).resolve()/'independent'
            with mock.patch.object(workflow,'_running_codex_processes',return_value=[]):report=workflow.import_data(source,target)
            self.assertEqual(report['history']['status'],'passed')
            self.assertEqual(report['history']['kinds']['fork'],2)
            for item in report['copied_files']:
                self.assertEqual(item['sha256'],hashlib.sha256((target/item['path']).read_bytes()).hexdigest())
            with closing(sqlite3.connect(target/'state_5.sqlite')) as c:
                paths=[Path(row[0]) for row in c.execute('SELECT rollout_path FROM threads')]
            self.assertTrue(all(p.is_relative_to(target) for p in paths))
            for p,digest in before.items():self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),digest)
            for p in source.rglob('*.jsonl'):self.assertEqual(p.read_bytes(),(target/p.relative_to(source)).read_bytes())
            # Prove validation does not read the source directory after import.
            hidden=source.with_name(source.name+'-hidden')
            source.rename(hidden)
            try:self.assertEqual(history.inspect(target)['status'],'passed')
            finally:hidden.rename(source)

    def test_outside_rollout_path_is_rejected(self):
        fixture=self.fixture()
        with closing(sqlite3.connect(fixture.root/'state_5.sqlite')) as c:
            c.execute('UPDATE threads SET rollout_path=? WHERE id=?',(str(fixture.root.parent/'outside.jsonl'),fixture.c));c.commit()
        with self.assertRaisesRegex(history.HistoryError,'outside'):history.inspect(fixture.root)

    def test_changed_lineage_is_rechecked_each_time(self):
        fixture=self.fixture();history.inspect(fixture.root)
        fixture.records[fixture.b][0]['payload']['history_base']['end_byte_offset']+=1
        fixture.write(fixture.b)
        with self.assertRaises(history.HistoryError):history.inspect(fixture.root)

    def test_dependency_change_during_inspection_blocks_commit(self):
        fixture=self.fixture();original=history.base.validate_paginated_start
        def change(*args,**kwargs):
            proof=original(*args,**kwargs)
            if args[0]==fixture.c:
                with fixture.paths[fixture.b].open('ab') as stream:stream.write(b'\n')
            return proof
        with mock.patch.object(history.base,'validate_paginated_start',side_effect=change):
            with self.assertRaisesRegex(history.HistoryError,'dependency_changed'):history.inspect(fixture.root)

if __name__=='__main__':unittest.main()
