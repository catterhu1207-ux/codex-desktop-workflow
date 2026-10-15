import unittest,json,tempfile,copy
from pathlib import Path
from unittest import mock
import hotfix_builder as b,hotfix_profile_261007_9446 as p
from codex_desktop_workflow import qualification as q,workflow

class Public9446(unittest.TestCase):
    def test_each_contract_uses_current_artifact_identity(self):
        # Unit check of the real metadata constructor; native semantics are
        # qualified separately by the packaged-runtime matrix.
        import frontend_contract_261007_9446 as contract
        roles=('entry_path','secondary_entry_path','shared_entry_path','main_entry_path','attestation_protocol_entry_path')
        entries={role:b'metadata-unit-input' for role in roles}
        gate={'source_asar_sha256':p.PROFILE['asar_source_sha256'],'portable_asar_sha256':'b'*64,'non_target_inventory_sha256':'c'*64,'live_renderer_probe':{'protocol':'component_contract_v1','artifact_id':b.frontend_attestation_artifact_id(p.PROFILE)}}
        inspected={'features':{name:{'status':'patchable'}for name in b.frontend_feature_statuses(p.PROFILE)}}
        with mock.patch.object(contract,'validate_source',return_value=(gate,entries,entries)),mock.patch.object(b,'inspect_archive',return_value=(inspected,None)),mock.patch('frontend_ssh_261007_9446.execute_merge',return_value={'status':'unit-only'}):
            value=contract.validate(Path('unit-source.asar'),Path('unit-target.asar'))
        expected=b.frontend_attestation_artifact_id(p.PROFILE)
        self.assertEqual({c['runtime_attestation']['artifact_id']for c in value['feature_contracts'].values()},{expected})

    def test_exact_source_and_portable_main_identities(self):
        self.assertEqual(workflow.SUPPORTED_PACKAGES['26.1007.9446.0'].asar_sha256,p.PROFILE['asar_source_sha256'])
        self.assertEqual(b.frontend_attestation_artifact_id(p.PROFILE),'2.7.21-356c13dc7158')
        self.assertEqual(len(b.frontend_feature_statuses(p.PROFILE)),26)
        self.assertEqual(len(b.frontend_attestation_features(p.PROFILE)),23)
        self.assertIn(b'2.7.21-356c13dc7158',b.renderer_attestation_module(p.PROFILE))

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
