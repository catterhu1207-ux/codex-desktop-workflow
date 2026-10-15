import unittest,json,tempfile,copy
from pathlib import Path
from unittest import mock
import hotfix_builder as b,hotfix_profile_261007_9446 as p
from codex_desktop_workflow import qualification as q,workflow

class Public9446(unittest.TestCase):
    def test_exact_source_and_portable_main_identities(self):
        self.assertEqual(workflow.SUPPORTED_PACKAGES['26.1007.9446.0'].asar_sha256,p.PROFILE['asar_source_sha256'])
        self.assertEqual(b.frontend_attestation_artifact_id(p.PROFILE),'2.7.20-356c13dc7158')
        self.assertEqual(len(b.frontend_feature_statuses(p.PROFILE)),26)
        self.assertEqual(len(b.frontend_attestation_features(p.PROFILE)),23)
        self.assertIn(b'2.7.20-356c13dc7158',b.renderer_attestation_module(p.PROFILE))

    def test_unverified_new_candidate_cannot_launch_without_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);root.joinpath('codex-desktop-workflow-manifest.json').write_text(json.dumps({'package_version':'26.1007.9446.0'}))
            with mock.patch.object(workflow.IsolatedRun,'start') as start:
                with self.assertRaisesRegex(ValueError,'qualification_required'):workflow.launch(root,root,root/'runs')
                start.assert_not_called()

    def test_empty_file_integrity_record_is_not_a_nonempty_bypass(self):
        import hashlib
        empty=hashlib.sha256(b'').hexdigest()
        # Exercise the archive reader with real bytes and source metadata.
        with tempfile.TemporaryDirectory() as tmp:
            archive=Path(tmp)/'entry';archive.write_bytes(b'')
            meta={'size':0,'offset':'0','integrity':{'algorithm':'SHA256','hash':empty,'blockSize':4194304,'blocks':[empty]}}
            self.assertEqual(b.read_entry(archive,0,meta)[1],b'')
            archive.write_bytes(b'x');meta['size']=1
            with self.assertRaises(Exception):b.read_entry(archive,0,meta)

    def test_incomplete_receipts_cannot_be_sealed(self):
        for value in ({'status':'source_bundle_prepared'},{'status':'passed'},{'status':'passed','closed_log_readback':'passed','owned_cleanup':{'owned_job_empty':False}}):
            with self.assertRaises(ValueError):q.require_complete(value,{})

    def test_source_fingerprint_changes_when_executable_input_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name in ('ChatGPT.exe','resources/app.asar','resources/codex.exe','resources/x.js','resources/u.cjs','codex-desktop-workflow-manifest.json','codex-desktop-workflow.json'):
                file=root/name;file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(b'synthetic')
            previous=q.bindings(root);root.joinpath('resources/x.js').write_bytes(b'changed')
            self.assertNotEqual(previous,q.bindings(root))
