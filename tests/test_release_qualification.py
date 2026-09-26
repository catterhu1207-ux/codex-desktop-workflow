"""Keep the required local runtime acceptance bound to the shipped source."""
import hashlib,json,unittest
from pathlib import Path
import codex_desktop_workflow

PACKAGE=Path(codex_desktop_workflow.__file__).parent
SOURCE=PACKAGE.parent

class ReleaseQualification(unittest.TestCase):
    def test_current_source_has_complete_public_runtime_acceptance(self):
        evidence=json.loads((PACKAGE/'policies/qualification-26.924.1866.0.json').read_text())
        self.assertEqual(evidence['status'],'passed')
        actual={str(p.relative_to(SOURCE)).replace('\\','/') for p in SOURCE.rglob('*')
                if p.is_file() and p.suffix in ('.py','.js','.json')
                and p.name!='qualification-26.924.1866.0.json'}
        self.assertEqual(set(evidence['source_inputs']),actual)
        for name,digest in evidence['source_inputs'].items():
            raw=(SOURCE/name).read_bytes().replace(b'\r\n',b'\n')
            self.assertEqual(hashlib.sha256(raw).hexdigest(),digest,name)
        pin=json.loads((PACKAGE/'policies/backend-source.json').read_text())
        self.assertEqual(evidence['compat_commit'],pin['commit'])
        self.assertEqual(evidence['feature_contract_count'],24)
        for mode in ('official','compat'):
            runs=evidence['runtime'][mode]
            self.assertEqual({r['profile'] for r in runs},{'empty','synthetic_tasks'})
            self.assertEqual(len(runs),2)
            for run in runs:
                self.assertEqual(run['renderer_features'],21)
                self.assertGreaterEqual(run['observed_seconds'],60)
                self.assertTrue(run['current_app_server_match'])
                self.assertEqual(run['close_status'],'closed')
                self.assertEqual(run['status'],'passed')
                if mode=='official':self.assertEqual(run['backend_sha256'],pin['official_backend_sha256'])

if __name__=='__main__':unittest.main()
