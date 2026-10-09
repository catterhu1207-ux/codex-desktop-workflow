"""Require current-source evidence; historical release proof stays immutable."""
import hashlib,json,unittest
from pathlib import Path
import codex_desktop_workflow
PACKAGE=Path(codex_desktop_workflow.__file__).parent
SOURCE=PACKAGE.parent
ROOT=Path(__file__).resolve().parents[1]
CURRENT='qualification-26.1002.7124.0.json'

def digest(p):return hashlib.sha256(p.read_bytes().replace(b"\r\n",b"\n")).hexdigest()

class ReleaseQualification(unittest.TestCase):
    def test_current_source_has_complete_public_runtime_acceptance(self):
        path=PACKAGE/'policies'/CURRENT
        self.assertTrue(path.is_file(),'Current release qualification is incomplete')
        e=json.loads(path.read_text())
        self.assertEqual(e['status'],'passed')
        self.assertEqual(e['desktop_version'],'26.1002.7124.0')
        # Bind evidence to the source actually built, not an invented earlier
        # version string or a later documentation-only commit.
        self.assertEqual(e['package_version'],codex_desktop_workflow.__version__)
        artifacts=e['tested_artifacts']
        self.assertEqual(set(artifacts),{'official','compat','installed_wheel'})
        for artifact in artifacts.values():
            self.assertRegex(artifact['source_commit'],r'^[0-9a-f]{40}$')
            self.assertRegex(artifact['artifact_sha256'],r'^[0-9a-f]{64}$')
            self.assertEqual(artifact['source_inputs'],e['source_inputs'])
        actual={str(p.relative_to(SOURCE)).replace('\\','/') for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ('.py','.js','.cjs','.json','.ps1') and p.name!=CURRENT}
        self.assertEqual(set(e['source_inputs']),actual)
        for name,value in e['source_inputs'].items():self.assertEqual(digest(SOURCE/name),value,name)
        tools={str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'tools').rglob('*') if p.is_file() and p.suffix in ('.py','.js','.cjs','.json','.ps1')}
        tools.update({'install.ps1','msix_source.py','tests/test_release_qualification.py','tests/test_awake_probes.py'})
        self.assertEqual(set(e['acceptance_tools']),tools)
        for name,value in e['acceptance_tools'].items():self.assertEqual(digest(ROOT/name),value,name)
        pin=json.loads((PACKAGE/'policies/backend-source-26.1002.7124.0.json').read_text())
        self.assertEqual(e['compat_commit'],pin['commit'])
        self.assertEqual(e['feature_contract_count'],26)
        self.assertEqual(e['frontend_build'],'2.7.17')
        for mode in ('official','compat'):
            runs=e['runtime'][mode]
            self.assertEqual({r['profile'] for r in runs},{'empty','synthetic_tasks','faithful_projects'})
            self.assertEqual(len(runs),3)
            for run in runs:
                self.assertEqual(run['renderer_features'],23)
                self.assertGreaterEqual(run['observed_seconds'],60)
                for flag in ('current_app_server_match','shell_folders_isolated','runtime_cache_isolated','native_sidebar_mounted','owned_job_empty'):self.assertTrue(run[flag])
                self.assertEqual(run['close_status'],'closed')
                self.assertEqual(run['status'],'passed')
                if mode=='official':self.assertEqual(run['backend_sha256'],pin['official_backend_sha256'])
        self.assertEqual(set(e['backend_cases']),{'http','websocket','cold-resume','local-compaction','remote-compaction','migrations'})
        for case in e['backend_cases'].values():self.assertEqual(case['status'],'passed')
        self.assertEqual(e['backend_cases']['migrations']['migration_count'],74)
        self.assertEqual(e['backend_cases']['migrations']['database_count'],6)
        for flag in ('native_first_send','native_cold_reopen','proof_rejections','msix_installer','installed_wheel','previous_profile_regression','process_ancestry_regression','sensitive_content_scan'):self.assertEqual(e['checks'][flag],'passed')
        self.assertEqual(e['new_chat']['synthetic_sent_chats'],6)
        self.assertFalse(e['new_chat']['encrypted_ssh_transport_tested'])
        self.assertTrue(e['old_runtime'])
        for run in e['old_runtime']:
            if run['status']=='skipped':
                self.assertEqual(run['reason'],'official_source_unavailable')
                self.assertFalse(run['counted_as_passed'])
                continue
            self.assertEqual(run['status'],'passed')
            self.assertEqual(run['renderer_features'],21)
            self.assertGreaterEqual(run['observed_seconds'],60)
            self.assertTrue(run['owned_job_empty'])

    def test_historical_qualification_keeps_original_contract(self):
        e=json.loads((PACKAGE/'policies/qualification-26.924.2738.0.json').read_text())
        self.assertEqual(e['feature_contract_count'],24)
        self.assertEqual(e['frontend_build'],'2.7.3')
        for runs in e['runtime'].values():
            self.assertEqual(len(runs),2)
            self.assertTrue(all(r['renderer_features']==21 for r in runs))

if __name__=='__main__':unittest.main()
