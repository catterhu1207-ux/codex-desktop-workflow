import hashlib,json,tempfile,unittest
from pathlib import Path
from codex_desktop_workflow.release_sources import digest,source_inventory,validate

class HistoricalSourceDelegation(unittest.TestCase):
    def prepare(self,directory):
        root=Path(directory);package=root/'codex_desktop_workflow';package.mkdir()
        shared=package/'shared.py';shared.write_text('CURRENT=True\n')
        profile=root/'hotfix_profile_legacy.py';profile.write_text('IDENTITY="retained"\n')
        old={'desktop_version':'26.1016.8622.0','source_inputs':{'codex_desktop_workflow/shared.py':'0'*64,'hotfix_profile_legacy.py':digest(profile)}}
        path=package/'qualification-legacy.json';path.write_text(json.dumps(old))
        current={'status':'passed','desktop_version':'26.1021.3705.0','package_version':'0.3.14','source_inputs':source_inventory(root),
          'legacy_profile_regressions':{'26.1016.8622.0':{'status':'passed','tests':3,'historical_policy_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
               'profile_source_inputs':{'hotfix_profile_legacy.py':digest(profile)}}}}
        proof={'status':'passed','observed_seconds':60,'normal_exit':True,'actual_backend_matched':True,'renderer_features':23,'browser_shared_state_unchanged':True}
        current['runtime_matrix']={mode:{case:dict(proof) for case in ('empty','synthetic_tasks')} for mode in ('official','compat')}
        for cases in current['runtime_matrix'].values():cases['synthetic_tasks']['synthetic_tasks']=400
        current['native_ui']={mode:{'status':'passed','first_send_cases':6,'cold_reopened_chats':6,'history_original_bytes_preserved':True,'priority_and_activity_ordering':'passed'} for mode in ('official','compat')}
        current.update(frontend_contracts={'status':'passed','count':26},background_history_budget={'status':'passed'})
        fresh=package/'qualification-current.json';fresh.write_text(json.dumps(current))
        return root,old,path,current,fresh

    def test_explicit_qualified_framework_retains_immutable_historical_policy_and_profile(self):
        with tempfile.TemporaryDirectory() as d:
            root,old,path,current,fresh=self.prepare(d);before=path.read_bytes()
            result=validate(path,old,root=root,current_path=fresh,package_version='0.3.14')
            self.assertEqual(result['status'],'passed');self.assertIn('framework_qualification_sha256',result)
            self.assertEqual(path.read_bytes(),before)

    def test_missing_evidence_changed_current_source_and_rewritten_profile_are_rejected(self):
        for conflict in ('missing','current_source','old_record','profile','profile_allowance','runtime_incomplete'):
            with self.subTest(conflict=conflict),tempfile.TemporaryDirectory() as d:
                root,old,path,current,fresh=self.prepare(d)
                if conflict=='missing':current['legacy_profile_regressions']={}
                if conflict=='current_source':(root/'codex_desktop_workflow/shared.py').write_text('UNQUALIFIED=True\n')
                if conflict=='old_record':path.write_text(json.dumps(old)+'\n')
                if conflict=='runtime_incomplete':current['runtime_matrix']['compat']['empty']['normal_exit']=False
                if conflict in ('profile','profile_allowance'):
                    p=root/'hotfix_profile_legacy.py';p.write_text('IDENTITY="changed"\n');current['source_inputs']=source_inventory(root)
                    if conflict=='profile_allowance':current['legacy_profile_regressions']['26.1016.8622.0']['profile_source_inputs']['hotfix_profile_legacy.py']=digest(p)
                fresh.write_text(json.dumps(current))
                with self.assertRaises(ValueError):validate(path,old,root=root,current_path=fresh,package_version='0.3.14')
