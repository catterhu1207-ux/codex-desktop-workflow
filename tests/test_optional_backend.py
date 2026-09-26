import json,tempfile,unittest
from pathlib import Path
from unittest import mock
from codex_desktop_workflow import backend,cli,workflow

class OptionalBackend(unittest.TestCase):
    def test_old_cli_defaults_to_official(self):
        args=cli.parser().parse_args(['build','--source','source','--target','target'])
        self.assertEqual(args.backend_mode,'official')
        self.assertIsNone(args.backend_manifest)

    def test_new_cli_exposes_explicit_compatibility_selection(self):
        args=cli.parser().parse_args(['build','--source','source','--target','target','--backend-mode','compat','--backend-manifest','manifest.json'])
        self.assertEqual(args.backend_mode,'compat')
        self.assertEqual(args.backend_manifest,Path('manifest.json'))

    def test_provenance_mismatch_is_rejected_before_binary_use(self):
        with tempfile.TemporaryDirectory() as raw:
            path=Path(raw)/'manifest.json'
            path.write_text(json.dumps({'mode':'patched','provenance':{'source_commit':'wrong'}}))
            with mock.patch.object(backend,'pin',return_value={'upstream_commit':'expected','profile_sha256':'p','commit':'c','repository':'r','build_recipe_sha256':'b'}):
                with self.assertRaisesRegex(ValueError,'provenance_mismatch'):backend.validate_manifest(path)

    def test_no_manifest_does_not_fall_back_to_official(self):
        inspected={'status':'passed','supported_version':'26.924.1866.0'}
        with mock.patch.object(workflow,'inspect',return_value=inspected):
            with self.assertRaisesRegex(workflow.WorkflowError,'manifest_required'):
                workflow.build(Path('source'),Path('target'),'compat')

    def test_old_registered_backend_does_not_prove_current_process(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);(root/'resources').mkdir();exe=root/'resources/codex.exe';exe.write_bytes(b'synthetic')
            old={'registered_backends':[{'executable':str(exe)}],'alive_backends':[]}
            self.assertFalse(workflow._registered_backend_match(old,root,workflow._sha256(exe)))

if __name__=='__main__':unittest.main()
