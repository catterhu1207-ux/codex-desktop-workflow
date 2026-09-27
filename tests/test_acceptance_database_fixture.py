"""The populated acceptance fixture must exercise all database identities."""
import json,sqlite3,tempfile,unittest
from contextlib import closing
from pathlib import Path
from unittest import mock
from codex_desktop_workflow import workflow

class AcceptanceDatabaseFixture(unittest.TestCase):
    def fixture(self,root):
        inventory=json.loads((workflow._POLICY_ROOT/'sqlite-migrations-26.924.2738.0.json').read_text())['migrations']
        databases=root/'fixture';databases.mkdir()
        for name in {r['database'] for r in inventory}:
            with closing(sqlite3.connect(databases/name)) as db:
                db.execute('CREATE TABLE _sqlx_migrations(version INTEGER PRIMARY KEY,success BOOLEAN,checksum BLOB)')
                db.executemany('INSERT INTO _sqlx_migrations VALUES(?,1,?)',[(r['version'],bytes.fromhex(r['sqlx_sha384'])) for r in inventory if r['database']==name])
                db.commit()
        empty=root/'empty';empty.mkdir()
        with closing(sqlite3.connect(databases/'state_5.sqlite')) as read,closing(sqlite3.connect(empty/'state_5.sqlite')) as write:
            read.backup(write)
        with closing(sqlite3.connect(empty/'state_5.sqlite')) as db:
            db.execute('CREATE TABLE threads(id TEXT PRIMARY KEY,rollout_path TEXT,created_at INTEGER,updated_at INTEGER,source TEXT,model_provider TEXT,cwd TEXT,title TEXT,sandbox_policy TEXT,approval_mode TEXT,has_user_event BOOLEAN,archived BOOLEAN,cli_version TEXT,first_user_message TEXT,recency_at INTEGER,recency_at_ms INTEGER,is_pinned BOOLEAN,preview TEXT)')
        home=root/'home';home.mkdir()
        return databases,empty,home,inventory
    def test_400_tasks_have_visible_previews_and_all_six_migration_inventories(self):
        with tempfile.TemporaryDirectory() as folder:
            databases,empty,home,inventory=self.fixture(Path(folder))
            with mock.patch.dict('os.environ',{'CODEX_WORKFLOW_TEST_DATABASE_FIXTURE':str(databases)}):
                workflow._seed_synthetic_tasks(home,empty)
            with closing(sqlite3.connect(home/'state_5.sqlite')) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM threads WHERE preview <> ''").fetchone()[0],400)
            for rollout in (home/'sessions').glob('*.jsonl'):
                record = json.loads(rollout.read_text())
                self.assertEqual(record['payload']['session_id'], record['payload']['id'])
                self.assertEqual(record['payload']['timestamp'], record['timestamp'])
                self.assertEqual(record['payload']['originator'], 'synthetic-acceptance')
            for name in {r['database'] for r in inventory}:
                with closing(sqlite3.connect(home/name)) as db:
                    self.assertEqual(db.execute('SELECT COUNT(*) FROM _sqlx_migrations').fetchone()[0],sum(r['database']==name for r in inventory))
            with closing(sqlite3.connect(empty/'state_5.sqlite')) as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM threads').fetchone()[0],0)
    def test_changed_auxiliary_checksum_blocks_task_seeding(self):
        with tempfile.TemporaryDirectory() as folder:
            databases,empty,home,_=self.fixture(Path(folder))
            with closing(sqlite3.connect(databases/'memories_1.sqlite')) as db:
                db.execute("UPDATE _sqlx_migrations SET checksum=x'00'")
                db.commit()
            with mock.patch.dict('os.environ',{'CODEX_WORKFLOW_TEST_DATABASE_FIXTURE':str(databases)}):
                with self.assertRaisesRegex(workflow.WorkflowError,'fixture_migration_mismatch'):
                    workflow._seed_synthetic_tasks(home,empty)
            self.assertFalse((home/'state_5.sqlite').exists())

    def test_legacy_schema_without_preview_keeps_the_previous_seed_interface(self):
        with tempfile.TemporaryDirectory() as folder:
            _,empty,home,_=self.fixture(Path(folder))
            with closing(sqlite3.connect(empty/'state_5.sqlite')) as db:
                db.execute('ALTER TABLE threads DROP COLUMN preview')
                db.commit()
            with mock.patch.dict('os.environ',{'CODEX_WORKFLOW_TEST_DATABASE_FIXTURE':''}):
                workflow._seed_synthetic_tasks(home,empty)
            with closing(sqlite3.connect(home/'state_5.sqlite')) as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM threads').fetchone()[0],400)
