from pathlib import Path
import os
import unittest
import hotfix_builder as builder
import hotfix_profile_26928_4866 as profile
import frontend_feature_contracts
from frontend_contract_26928_4866 import require_feature_signatures
from frontend_feature_contracts import ContractError


class Exact4866Profile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = os.environ.get('CODEX_WORKFLOW_TEST_SOURCE_4866')
        portable = os.environ.get('CODEX_WORKFLOW_TEST_ASAR_4866')
        if not source or not portable:
            raise unittest.SkipTest('Exact official MSIX source and independently built public artifact required')
        cls.source, cls.portable = Path(source), Path(portable)
        size, _, header = builder.read_asar(cls.portable)
        cls.entries = {name: builder.read_entry(cls.portable, size, builder.get_entry_meta(header, profile.PROFILE[name]))[1]
                       for name in ('entry_path', 'secondary_entry_path', 'shared_entry_path')}

    def test_exact_public_artifact_executes_all_25_contracts(self):
        result = frontend_feature_contracts.validate(self.source, self.portable)
        self.assertEqual(len(result['feature_contracts']), 25)
        self.assertTrue(all(item['status'] in ('native_verified', 'patched_verified') for item in result['feature_contracts'].values()))

    def test_orange_and_project_sort_wiring_cannot_be_reverted(self):
        for feature in ('user_action_pending_orange', 'project_sorting', 'plan_pending_detection'):
            original, fixed = profile.PAIRS[feature][0]
            self.assertEqual(self.entries['entry_path'].count(fixed), 1)
            broken = self.entries['entry_path'].replace(fixed, original, 1)
            with self.assertRaises(ContractError, msg=feature):
                require_feature_signatures(broken, self.entries['secondary_entry_path'], self.entries['shared_entry_path'])

    def test_new_identity_does_not_expand_old_proof_inventory(self):
        import hotfix_profile_26924_2738 as previous
        self.assertEqual(builder.frontend_attestation_artifact_id(profile.PROFILE), '2.7.9-84fe697418b2')
        self.assertEqual(builder.frontend_validator_version(profile.PROFILE), '2.6.0')
        self.assertEqual(len(builder.frontend_attestation_features(profile.PROFILE)), 22)
        self.assertEqual(len(builder.frontend_attestation_features(previous.PROFILE)), 21)


if __name__ == '__main__':
    unittest.main()
