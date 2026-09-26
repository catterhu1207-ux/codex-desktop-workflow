from pathlib import Path
import os,unittest
import hotfix_builder as builder
import hotfix_profile_26924_1866 as profile
import frontend_feature_contracts
from frontend_contract_26924_1866 import require_feature_signatures
from frontend_feature_contracts import ContractError

class ExactNewProfile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=os.environ.get('CODEX_WORKFLOW_TEST_SOURCE_1866')
        portable=os.environ.get('CODEX_WORKFLOW_TEST_ASAR_1866')
        if not source or not portable:raise unittest.SkipTest('Set the exact new official source and public artifact')
        cls.source=Path(source);cls.portable=Path(portable)
        hs,_,header=builder.read_asar(cls.portable)
        cls.entries={name:builder.read_entry(cls.portable,hs,builder.get_entry_meta(header,profile.PROFILE[name]))[1] for name in ('entry_path','secondary_entry_path','shared_entry_path')}

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

    def test_source_and_artifact_identities_remain_version_scoped(self):
        self.assertEqual(builder.frontend_attestation_artifact_id(profile.PROFILE),'2.7.0-96b6aa6e1ea4')
        self.assertEqual(builder.sha256_path(self.source),profile.PROFILE['asar_source_sha256'])

if __name__=='__main__':unittest.main()
