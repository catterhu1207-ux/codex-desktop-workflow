from pathlib import Path
import hashlib,json,tempfile,unittest
from codex_desktop_workflow import workflow


class VerificationSource(unittest.TestCase):
    def test_identical_explicit_source_preserves_original_manifest(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);source=root/'retained.asar';source.write_bytes(b'qualified-source')
            digest=hashlib.sha256(source.read_bytes()).hexdigest()
            value={'official_source_asar':str(root/'moved.asar'),'official_source_sha256':digest,'official_source_size':source.stat().st_size,'preserved':'value'}
            original=root/'manifest.json';original.write_text(json.dumps(value))
            frozen=original.read_bytes()
            rebound,receipt=workflow._bind_verification_source(original,source,root/'runs',digest)
            self.assertEqual(original.read_bytes(),frozen)
            actual=json.loads(rebound.read_text());actual['official_source_asar']=value['official_source_asar']
            self.assertEqual(actual,value)
            self.assertTrue(receipt['original_manifest_preserved'])

    def test_changed_source_or_size_cannot_be_rebound(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);source=root/'source.asar';source.write_bytes(b'qualified')
            digest=hashlib.sha256(source.read_bytes()).hexdigest()
            value={'official_source_asar':str(root/'old.asar'),'official_source_sha256':digest,'official_source_size':999}
            manifest=root/'manifest.json';manifest.write_text(json.dumps(value))
            with self.assertRaisesRegex(workflow.WorkflowError,'size_mismatch'):
                workflow._bind_verification_source(manifest,source,root/'runs',digest)
            source.write_bytes(b'wrong')
            with self.assertRaisesRegex(workflow.WorkflowError,'identity_mismatch'):
                workflow._bind_verification_source(manifest,source,root/'runs',digest)
            self.assertFalse((root/'runs').exists())


if __name__=='__main__':unittest.main()
