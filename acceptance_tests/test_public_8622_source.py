"""Retained exact-source regression; unavailable historical samples are explicit skips."""
import os,unittest
from pathlib import Path
import hotfix_builder as b
import hotfix_integration_261016_8622 as p

class Exact8622Source(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=os.environ.get('CODEX_WORKFLOW_TEST_SOURCE_8622')
        portable=os.environ.get('CODEX_WORKFLOW_TEST_APP_8622')
        if not source or not portable:
            raise unittest.SkipTest('Historical 8622 original sample unavailable; immutable profile and packaged-function regressions are recorded separately')
        cls.source=Path(source);cls.app=Path(portable)

    def test_all_26_contracts_and_four_length_preserving_entries(self):
        result=p.validate(self.source,self.app/'resources/app.asar')
        self.assertEqual(len(result['feature_contracts']),26)
        self.assertEqual(len(result['actual_javascript']['source_and_archive']['transformations']),4)
        size,_,header=b.read_asar(self.source)
        for item in result['actual_javascript']['source_and_archive']['transformations']:
            self.assertEqual(item['length'],b.get_entry_meta(header,item['path'])['size'])
        for contract in result['feature_contracts'].values():
            self.assertEqual(contract['source_identity']['status'],'passed')
            self.assertEqual(contract['semantic_execution']['status'],'pending_native_runtime')

    def test_exact_packaged_native_watch_heartbeat_and_routes(self):
        from codex_desktop_workflow.native_checks_8622 import verify
        value=verify(self.app,self.source)
        self.assertEqual(value['status'],'passed')
        self.assertEqual(value['protocol_resource_route']['negative_cases'],13)
        self.assertTrue(value['archived_heartbeat_terminal_guard']['hosted_flag_preserved'])

    def test_executable_changes_only_unique_embedded_header(self):
        before=(self.source.parent.parent/'ChatGPT.exe').read_bytes()
        after=(self.app/'ChatGPT.exe').read_bytes()
        old=p.PROFILE['embedded_asar_header_source_sha256'].encode()
        self.assertEqual(before.count(old),1)
        offset=before.index(old)
        self.assertEqual(before[:offset],after[:offset])
        self.assertEqual(before[offset+64:],after[offset+64:])
        self.assertEqual(p.sha(after),p.TARGET_EXE_SHA256)

    def test_complete_row_recomputes_pending_and_pin_routes(self):
        from codex_desktop_workflow.native_row_8622 import verify
        value=verify(self.app)
        self.assertEqual(value['negative_controls_rejected'],['parent_pin','async_request','real_plan_source'])
        self.assertEqual(len(value['states']),14)
