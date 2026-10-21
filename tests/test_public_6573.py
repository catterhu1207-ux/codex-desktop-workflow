import json,os,tempfile,unittest,zlib,struct
from pathlib import Path
from unittest import mock
import hotfix_builder as b
import hotfix_integration_261016_6573 as p
from codex_desktop_workflow import workflow,qualification
from codex_desktop_workflow.isolated_run import IsolatedRun

class Public6573(unittest.TestCase):
    def test_version_scoped_identity(self):
        self.assertEqual(workflow.SUPPORTED_PACKAGES[p.base.VERSION].asar_sha256,p.base.SOURCE_ASAR_SHA256)
        self.assertEqual(b.frontend_attestation_artifact_id(p.PROFILE),'2.9.2-6f56542b508e')
        self.assertEqual(len(p.all_features()),26)
        self.assertEqual(len(p.features()),23)
        import hotfix_integration_261013_4894 as previous
        self.assertEqual(b.frontend_attestation_artifact_id(previous.PROFILE),'2.8.1-bbec1d64e135')
        self.assertNotEqual(p.TARGET_ASAR_SHA256,previous.TARGET_ASAR_SHA256)

    def test_source_bundle_is_not_runtime_qualification(self):
        self.assertEqual({v['status'] for v in p.load_packet()['feature_semantics'].values()},{'pending'})
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'codex-desktop-workflow-manifest.json').write_text(json.dumps({'package_version':p.base.VERSION}))
            with mock.patch.object(IsolatedRun,'start') as start:
                with self.assertRaisesRegex(ValueError,'qualification_required'):
                    workflow.launch(root,root,root/'runs')
                start.assert_not_called()

    def test_wrong_source_rejected_before_delta_decoding(self):
        with mock.patch.object(p.base,'_sha',return_value='0'*64):
            with self.assertRaisesRegex(ValueError,'official ASAR identity'):
                p.prepared_entries(Path('untrusted.asar'))

    def test_delta_rejects_bounds_truncation_and_unknown_operation(self):
        encode=lambda body:zlib.compress(b'CF9DELTA1'+struct.pack('<I',1)+body)
        cases=[struct.pack('<BQ',0,3)+struct.pack('<Q',1),
               struct.pack('<BQ',1,3)+b'a',struct.pack('<BQ',7,3)]
        for case in cases:
            with self.subTest(case=case),self.assertRaises(ValueError):p.base._decode(b'abc',encode(case),3)

    def test_runtime_module_tamper_rejected(self):
        with mock.patch.object(p,'MODULE_SHA256','0'*64):
            with self.assertRaisesRegex(ValueError,'runtime module changed'):p.module_bytes()

    def test_acceptance_rejects_implicit_or_external_home(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'codex-desktop-workflow-manifest.json').write_text(json.dumps({'package_version':p.base.VERSION}))
            with mock.patch.object(IsolatedRun,'_start_owl') as start:
                for env in ({},{'CODEX_HOME':'relative'},{'CODEX_HOME':str(root/'external')}):
                    with self.assertRaises(ValueError):
                        IsolatedRun.start(root/'ChatGPT.exe',root/'runs',environment=env,isolate_shell_folders=True)
                start.assert_not_called()

class Exact6573Source(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=os.environ.get('CODEX_WORKFLOW_TEST_SOURCE_6573')
        portable=os.environ.get('CODEX_WORKFLOW_TEST_APP_6573')
        if not source or not portable:
            raise unittest.SkipTest('6573 release acceptance requires the exact official source and built candidate')
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
        from codex_desktop_workflow.native_checks_6573 import verify
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
        from codex_desktop_workflow.native_row_6573 import verify
        value=verify(self.app)
        self.assertEqual(value['negative_controls_rejected'],['parent_pin','async_request','real_plan_source'])
        self.assertEqual(len(value['states']),14)
