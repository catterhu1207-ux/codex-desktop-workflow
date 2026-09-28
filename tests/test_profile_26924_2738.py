from pathlib import Path
import os,unittest
import hotfix_builder as builder
import hotfix_profile_26924_2738 as profile
import frontend_feature_contracts
from frontend_contract_26924_2738 import require_feature_signatures
from frontend_feature_contracts import ContractError

class ExactNewProfile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=os.environ.get('CODEX_WORKFLOW_TEST_SOURCE_2738')
        portable=os.environ.get('CODEX_WORKFLOW_TEST_ASAR_2738')
        if not source or not portable:raise unittest.SkipTest('Set the exact new official source and public artifact')
        cls.source=Path(source);cls.portable=Path(portable)
        hs,_,header=builder.read_asar(cls.portable)
        cls.entries={name:builder.read_entry(cls.portable,hs,builder.get_entry_meta(header,profile.PROFILE[name]))[1] for name in ('entry_path','secondary_entry_path','shared_entry_path')}

    def test_protocol_patch_preserves_previous_profile_output(self):
        import hotfix_profile_26924_1866 as previous
        for prefix, module in (('1866', previous), ('2738', profile)):
            source = Path(os.environ['CODEX_WORKFLOW_TEST_SOURCE_' + prefix])
            portable = Path(os.environ['CODEX_WORKFLOW_TEST_ASAR_' + prefix])
            path = module.PROFILE['attestation_protocol_entry_path']
            hs, _, header = builder.read_asar(source)
            original = builder.read_entry(source, hs, builder.get_entry_meta(header, path))[1]
            hs, _, header = builder.read_asar(portable)
            expected = builder.read_entry(portable, hs, builder.get_entry_meta(header, path))[1]
            actual = builder.patch_frontend_attestation_protocol_entry(original, module.PROFILE)
            self.assertEqual(actual, expected, prefix)

    def test_exact_artifact_executes_all_24_contracts(self):
        result=frontend_feature_contracts.validate(self.source,self.portable)
        self.assertEqual(len(result['feature_contracts']),24)
        self.assertTrue(all(c['status'] in ('native_verified','patched_verified') for c in result['feature_contracts'].values()))

    def test_plan_and_live_sort_patches_cannot_be_removed(self):
        for name in ('plan_pending_detection','priority_filter_live_resort','priority_filter_pinned_recency_sorting'):
            old,new=profile.PAIRS[name][0]
            broken=self.entries['entry_path'].replace(new,old,1)
            with self.assertRaises(ContractError):
                require_feature_signatures(broken,self.entries['secondary_entry_path'],self.entries['shared_entry_path'])

    def test_real_start_reducer_selector_and_project_chain(self):
        from frontend_recency_contract_26924_2738 import run
        result=run(self.entries['entry_path'],self.entries['shared_entry_path'])
        self.assertEqual(result['status'],'passed')
        self.assertTrue(result['official_start_event'])
        for index in (4,):
            old,new=profile.SHARED_PAIRS['priority_filter_live_resort'][index]
            broken=self.entries['shared_entry_path'].replace(new,old,1)
            with self.assertRaises(ContractError):run(self.entries['entry_path'],broken)
        old,new=profile.PAIRS['project_sorting'][0]
        with self.assertRaises(ContractError):
            run(self.entries['entry_path'].replace(new,old,1),self.entries['shared_entry_path'])

    def test_source_and_artifact_identities_remain_version_scoped(self):
        self.assertEqual(builder.frontend_attestation_artifact_id(profile.PROFILE),'2.7.3-89fba67324ff')
        self.assertEqual(builder.sha256_path(self.source),profile.PROFILE['asar_source_sha256'])

if __name__=='__main__':unittest.main()
