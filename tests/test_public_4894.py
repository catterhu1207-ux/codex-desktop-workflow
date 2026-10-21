import json,tempfile,unittest
from pathlib import Path
from unittest import mock
from codex_desktop_workflow import workflow,qualification
from codex_desktop_workflow.isolated_run import IsolatedRun
import hotfix_builder as b,hotfix_integration_261013_4894 as p

class Public4894(unittest.TestCase):
    def test_version_identity_and_inventory(self):
        self.assertEqual(workflow.UNQUALIFIED_PACKAGES['26.1013.4894.0'].asar_sha256,p.base.SOURCE_ASAR_SHA256)
        self.assertNotIn('26.1013.4894.0',workflow.SUPPORTED_PACKAGES)
        self.assertEqual(b.frontend_attestation_artifact_id(p.PROFILE),'2.8.1-bbec1d64e135')
        self.assertEqual(len(p.all_features()),26)
        self.assertEqual(len(p.features()),23)
    def test_unqualified_new_version_cannot_launch(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);(root/'codex-desktop-workflow-manifest.json').write_text(json.dumps({'package_version':'26.1013.4894.0'}))
            with mock.patch.object(IsolatedRun,'start') as start:
                with self.assertRaisesRegex(ValueError,'qualification_required'):workflow.launch(root,root,root/'runs')
                start.assert_not_called()
    def test_regular_launch_accepts_explicit_data_outside_test_root(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);(root/'codex-desktop-workflow-manifest.json').write_text(json.dumps({'package_version':'26.1013.4894.0'}))
            with mock.patch.object(IsolatedRun,'_start_owl',return_value='owned') as start:
                result=IsolatedRun.start(root/'ChatGPT.exe',root/'runs',environment={'CODEX_HOME':str(root/'independent-data')})
                self.assertEqual(result,'owned');self.assertFalse(start.call_args.args[-1])
    def test_acceptance_rejects_external_or_implicit_home_before_start(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);(root/'codex-desktop-workflow-manifest.json').write_text(json.dumps({'package_version':'26.1013.4894.0'}))
            with mock.patch.object(IsolatedRun,'_start_owl') as start:
                for environment in ({},{'CODEX_HOME':'relative'},{'CODEX_HOME':str(root/'external')}):
                    with self.assertRaises(ValueError):IsolatedRun.start(root/'ChatGPT.exe',root/'runs',environment=environment,isolate_shell_folders=True)
                start.assert_not_called()
    def test_runtime_module_tamper_is_rejected(self):
        with mock.patch.object(p,'MODULE_SHA256','0'*64):
            with self.assertRaisesRegex(ValueError,'module changed'):p.module_bytes()
    def test_legacy_gate_does_not_accept_new_two_profile_shape(self):
        value={'status':'passed','closed_log_readback':'passed','owned_cleanup':{'owned_job_empty':True},'runtime':[{'profile':'empty'},{'profile':'synthetic_tasks'}]}
        with self.assertRaisesRegex(ValueError,'three_profile'):qualification.require_complete(value,{'package_version':'26.1007.9446.0','frontend_runtime_attestation':{'live_renderer_probe':{'feature_ids':[]}}})
