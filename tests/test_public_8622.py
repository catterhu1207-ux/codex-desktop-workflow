import json,os,tempfile,unittest,zlib,struct
from pathlib import Path
from unittest import mock
import hotfix_builder as b
import hotfix_integration_261016_8622 as p
from codex_desktop_workflow import workflow,qualification
from codex_desktop_workflow.isolated_run import IsolatedRun

class Public8622(unittest.TestCase):
    def test_version_scoped_identity(self):
        self.assertEqual(workflow.SUPPORTED_PACKAGES[p.base.VERSION].asar_sha256,p.base.SOURCE_ASAR_SHA256)
        self.assertEqual(b.frontend_attestation_artifact_id(p.PROFILE),'2.11.0-a05dfd86ca50')
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
