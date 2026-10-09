"""Preserve exact version identities and self-contained public update routing."""
import unittest
import hotfix_builder as builder
import hotfix_profile_261002_7124 as profile
from codex_desktop_workflow import workflow


class Public7124(unittest.TestCase):
    def test_public_native_menu_has_no_maintainer_directory_dependency(self):
        self.assertIn(b'codex_desktop_workflow.update_awareness',profile.UPDATE_MENU_NEW)
        self.assertIn(b'CODEX_WORKFLOW_PYTHON',profile.UPDATE_MENU_NEW)
        self.assertNotIn(b'maintenance',profile.UPDATE_MENU_NEW)
        self.assertNotIn(b'Manage-ChatGPT',profile.UPDATE_MENU_NEW)

    def test_precise_latest_frontend_identity(self):
        self.assertEqual(builder.frontend_attestation_identity(profile.PROFILE),('2.7.0','2.7.17-76fe7078248c'))
        self.assertEqual(len(builder.frontend_attestation_features(profile.PROFILE)),23)

    def test_restored_historical_public_identities(self):
        expected={'26.924.2738.0':('2.5.1','2.7.3-89fba67324ff'),'26.928.4866.0':('2.6.0','2.7.9-84fe697418b2')}
        for version,identity in expected.items():
            support=workflow.SUPPORTED_PACKAGES[version]
            selected=next(p for p in builder.FRONTEND_PROFILES if p['asar_source_sha256']==support.asar_sha256)
            self.assertEqual(builder.frontend_attestation_identity(selected),identity)

    def test_unknown_versions_do_not_inherit_latest_profile(self):
        self.assertNotIn('26.1003.9000.0',workflow.SUPPORTED_PACKAGES)


if __name__=='__main__':unittest.main()
