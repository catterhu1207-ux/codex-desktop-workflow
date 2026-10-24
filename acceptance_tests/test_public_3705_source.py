"""Mandatory current-version checks against complete official and built inputs."""
import os,unittest
from pathlib import Path
import hotfix_builder as b
import hotfix_integration_261021_3705 as p

class Exact3705Source(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=os.environ.get('CODEX_WORKFLOW_TEST_SOURCE_3705')
        portable=os.environ.get('CODEX_WORKFLOW_TEST_APP_3705')
        if not source or not portable:raise AssertionError('Current 3705 native acceptance inputs are required')
        cls.source=Path(source);cls.app=Path(portable)

    def test_all_contracts_and_source_inventory(self):
        value=p.validate(self.source,self.app/'resources/app.asar')
        self.assertEqual(len(value['feature_contracts']),26)
        self.assertEqual(b.sha256_path(self.source),p.base.SOURCE_ASAR_SHA256)
        self.assertEqual(b.sha256_path(self.app/'resources/app.asar'),p.TARGET_ASAR_SHA256)

    def test_packaged_watch_heartbeat_and_protocol(self):
        from codex_desktop_workflow.native_checks_3705 import verify
        value=verify(self.app,self.source)
        self.assertEqual(value['status'],'passed')
        self.assertEqual(value['protocol_resource_route']['negative_cases'],13)

    def test_full_native_row_pipeline(self):
        from codex_desktop_workflow.native_row_3705 import verify
        value=verify(self.app)
        self.assertEqual(value['status'],'passed')
        self.assertEqual(len(value['states']),14)
        self.assertEqual(len(value['negative_controls_rejected']),3)

    def test_native_background_reader_and_no_copy_budget(self):
        from codex_desktop_workflow.native_background_3705 import verify
        value=verify(self.app)
        self.assertEqual(value['status'],'passed')
        self.assertFalse(value['native_metadata_request_include_turns'])
        self.assertTrue(value['native_host_config_getter'])
        self.assertEqual(len(value['negative_controls_rejected']),2)

    def test_only_unique_executable_header_changes(self):
        before=(self.source.parent.parent/'ChatGPT.exe').read_bytes()
        after=(self.app/'ChatGPT.exe').read_bytes()
        old=p.PROFILE['embedded_asar_header_source_sha256'].encode()
        self.assertEqual(before.count(old),1)
        offset=before.index(old)
        self.assertEqual(before[:offset],after[:offset])
        self.assertEqual(before[offset+64:],after[offset+64:])
        self.assertEqual(p.sha(after),p.TARGET_EXE_SHA256)
