import hashlib,json,tempfile,unittest
from pathlib import Path
import hotfix_builder as b
import hotfix_integration_261021_3705 as p
from codex_desktop_workflow import workflow,backend,qualification

class Public3705(unittest.TestCase):
    def test_independent_profile_and_backend_source(self):
        version='26.1021.3705.0'
        support=workflow.SUPPORTED_PACKAGES[version]
        self.assertEqual(workflow.SUPPORTED_VERSION,version)
        self.assertEqual(support.asar_sha256,p.base.SOURCE_ASAR_SHA256)
        self.assertEqual(b.frontend_attestation_artifact_id(p.PROFILE),'2.12.1-04862a659c6a')
        self.assertEqual(len(p.all_features()),26)
        self.assertEqual(len(p.features()),23)
        pin=backend.pin(version)
        self.assertEqual(pin['commit'],'fabd73f0370b279be6e57c74a14ec53cd6c3c945')
        self.assertEqual(pin['upstream_commit'],'6905ecede7816e91373e9eabda3f6b0368fc747b')
        self.assertNotEqual(pin,backend.pin('26.1016.8622.0'))

    def test_launch_binding_requires_exact_background_resource(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in ('ChatGPT.exe','resources/app.asar','resources/codex.exe','resources/x.js','resources/u.cjs','codex-desktop-workflow.json'):
                path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b'synthetic')
            (root/'codex-desktop-workflow-manifest.json').write_text(json.dumps({'package_version':'26.1021.3705.0'}))
            with self.assertRaises(FileNotFoundError):qualification.bindings(root)
            guard=root/'resources/g.cjs';guard.write_bytes(b'synthetic budget')
            before=qualification.bindings(root)
            self.assertEqual(before['candidate']['resources/g.cjs'],hashlib.sha256(guard.read_bytes()).hexdigest())
            guard.write_bytes(b'changed budget')
            self.assertNotEqual(before,qualification.bindings(root))
