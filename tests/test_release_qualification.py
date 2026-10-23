"""Require current-source evidence; historical release proof stays immutable."""
import hashlib,json,unittest
from pathlib import Path
import codex_desktop_workflow
PACKAGE=Path(codex_desktop_workflow.__file__).parent
SOURCE=PACKAGE.parent
ROOT=Path(__file__).resolve().parents[1]
CURRENT='qualification-26.1016.8622.0.json'

def digest(p):
    raw=p.read_bytes()
    return hashlib.sha256(raw if p.suffix=='.bin' else raw.replace(b"\r\n",b"\n")).hexdigest()

class ReleaseQualification(unittest.TestCase):
    def test_current_source_has_complete_public_runtime_acceptance(self):
        path=PACKAGE/'policies'/CURRENT
        self.assertTrue(path.is_file(),'Current release qualification is incomplete')
        e=json.loads(path.read_text())
        self.assertEqual(e['status'],'passed')
        self.assertEqual(e['desktop_version'],'26.1016.8622.0')
        # Bind evidence to the source actually built, not an invented earlier
        # version string or a later documentation-only commit.
        self.assertEqual(e['package_version'],codex_desktop_workflow.__version__)
        artifacts=e['tested_artifacts']
        self.assertEqual(set(artifacts),{'official','compat','installed_wheel'})
        for artifact in artifacts.values():
            self.assertRegex(artifact['source_commit'],r'^[0-9a-f]{40}$')
            self.assertRegex(artifact['artifact_sha256'],r'^[0-9a-f]{64}$')
            # Keep original artifact evidence intact. A narrowly scoped
            # installer-fixture amendment has its own regression evidence;
            # final installation runtime remains a separate release gate.
            amended=dict(artifact['source_inputs'])
            for change in e.get('source_amendments',[]):
                self.assertEqual(change['scope'],'installation_fixture_only')
                self.assertEqual(change['path'],'codex_desktop_workflow/verification_8622.py')
                self.assertEqual(amended[change['path']],change['before_sha256'])
                self.assertEqual(change['regression']['status'],'passed')
                self.assertEqual(change['regression']['tests'],4)
                self.assertEqual(change['regression']['test_source_sha256'],digest(ROOT/'tests/test_installer_fixture_sandbox.py'))
                self.assertTrue(change['native_application_bytes_unchanged'])
                self.assertRegex(change['previous_qualification_sha256'],r'^[0-9a-f]{64}$')
                amended[change['path']]=change['after_sha256']
            self.assertEqual(amended,e['source_inputs'])
        actual={str(p.relative_to(SOURCE)).replace('\\','/') for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ('.py','.js','.cjs','.mjs','.bin','.json','.ps1') and p.name!=CURRENT}
        self.assertEqual(set(e['source_inputs']),actual)
        for name,value in e['source_inputs'].items():self.assertEqual(digest(SOURCE/name),value,name)
        tools={str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'tools').rglob('*') if p.is_file() and p.suffix in ('.py','.js','.cjs','.json','.ps1')}
        tools.update(str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'acceptance_tests').glob('*.py'))
        tools.update({'install.ps1','msix_source.py','tests/test_release_qualification.py','tests/test_awake_probes.py'})
        self.assertEqual(set(e['acceptance_tools']),tools)
        for name,value in e['acceptance_tools'].items():self.assertEqual(digest(ROOT/name),value,name)
        pin=json.loads((PACKAGE/'policies/backend-source-26.1016.8622.0.json').read_text())
        self.assertEqual(e['compat_commit'],pin['commit'])
        self.assertEqual(e['feature_contract_count'],26)
        self.assertEqual(e['frontend_build'],'2.11.0')
        self.assertEqual(e['native_source_checks']['status'],'passed')
        self.assertEqual(e['native_source_checks']['tests'],4)
        self.assertFalse(e['native_source_checks']['skipped'])
        for mode in ('official','compat'):
            runs=e['runtime'][mode]
            self.assertEqual({r['profile'] for r in runs},{'empty','synthetic_tasks'})
            self.assertEqual(len(runs),2)
            for run in runs:
                self.assertEqual(run['renderer_features'],23)
                self.assertGreaterEqual(run['observed_seconds'],60)
                for flag in ('current_app_server_match','shell_folders_isolated','runtime_cache_isolated','owned_job_empty'):self.assertTrue(run[flag])
                if run['profile']=='empty':
                    self.assertEqual(run['acceptance_scope'],'signed_out_onboarding')
                    self.assertTrue(run['onboarding_visible'])
                else:
                    self.assertTrue(run['native_sidebar_mounted'])
                    self.assertGreaterEqual(run['synthetic_threads'],400)
                self.assertEqual(run['close_status'],'closed')
                self.assertEqual(run['status'],'passed')
                if mode=='official':self.assertEqual(run['backend_sha256'],pin['official_backend_sha256'])
        self.assertEqual(set(e['backend_cases']),{'http','websocket','cold-resume','local-compaction','remote-compaction','migrations','paginated-history'})
        for case in e['backend_cases'].values():self.assertEqual(case['status'],'passed')
        self.assertEqual(e['backend_cases']['migrations']['migration_count'],77)
        self.assertEqual(e['backend_cases']['migrations']['database_count'],6)
        for flag in ('native_first_send','native_cold_reopen','proof_rejections','official_source_and_installer','installed_wheel','previous_profile_regression','process_ancestry_regression','sensitive_content_scan'):self.assertEqual(e['checks'][flag],'passed')
        self.assertEqual(e['new_chat']['synthetic_sent_chats'],6)
        self.assertTrue(e['new_chat']['encrypted_ssh_transport_tested'])
        self.assertTrue(e['native_sort']['read_only_cold_chat_not_promoted'])
        self.assertTrue(e['native_sort']['new_reply_moves_to_front'])
        self.assertTrue(e['native_sort']['manual_pin_order_preserved'])
        self.assertEqual(e['native_row']['cases'],14)
        self.assertEqual(e['native_row']['negative_controls_rejected'],['parent_pin','async_request','real_plan_source'])
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
