from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import subprocess
import unittest

import frontend_contract_26915
import hotfix_builder
from codex_desktop_workflow import workflow


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
CHINESE_LABEL = "\u4e2d\u6587\u8bf4\u660e"
NEW_26915_FILES = (
    SRC / "hotfix_profile_26917_9434.py",
    SRC / "frontend_contract_26917_9434.py",
    SRC / "frontend_work_contract_26917_9434.py",
    SRC / "frontend_row_contract_26917_9434.py",
    SRC / "codex_desktop_workflow/data/frontend_scenarios_26917_9434.js",
    SRC / "codex_desktop_workflow/data/frontend_row_scenarios_26917_9434.js",
    SRC / "hotfix_profile_26917_6896.py",
    SRC / "frontend_contract_26917_6896.py",
    SRC / "frontend_work_contract_26917_6896.py",
    SRC / "frontend_row_contract_26917_6896.py",
    SRC / "codex_desktop_workflow/data/frontend_scenarios_26917_6896.js",
    SRC / "hotfix_profile_26915_4065.py",
    SRC / "frontend_contract_26915_4065.py",
    SRC / "frontend_work_contract_26915_4065.py",
    SRC / "codex_desktop_workflow/data/frontend_scenarios_26915_4065.js",
    SRC / "hotfix_profile_26915_3509.py",
    SRC / "frontend_contract_26915.py",
    SRC / "frontend_work_contract_26915.py",
    SRC / "codex_desktop_workflow" / "data" / "frontend_scenarios_26915.js",
)
ASSETS = (
    ROOT / "docs" / "assets" / "demo-en.gif",
    ROOT / "docs" / "assets" / "demo-zh.gif",
    ROOT / "docs" / "assets" / "before-after-en.png",
    ROOT / "docs" / "assets" / "before-after-zh.png",
    ROOT / "docs" / "assets" / "social-preview.png",
)


class ReleaseSurfaceTests(unittest.TestCase):
    def test_profile_registry_contains_both_supported_versions(self):
        profiles = {
            profile["package_version"]: profile
            for profile in hotfix_builder.FRONTEND_PROFILES
        }
        self.assertTrue(set(workflow.SUPPORTED_VERSIONS).issubset(profiles))
        for version, support in workflow.SUPPORTED_PACKAGES.items():
            profile = hotfix_builder.profile_for_asar(support.asar_sha256)
            self.assertIsNotNone(profile)
            self.assertEqual(profile["package_version"], version)

    def test_profile_scoped_release_identities_are_stable(self):
        legacy = hotfix_builder.profile_for_asar(
            workflow.SUPPORTED_PACKAGES["26.908.9136.0"].asar_sha256
        )
        current = hotfix_builder.profile_for_asar(
            workflow.SUPPORTED_PACKAGES["26.915.3509.0"].asar_sha256
        )
        self.assertEqual(
            hotfix_builder.frontend_attestation_artifact_id(legacy),
            "2.6.9-7a46bd6fe162",
        )
        self.assertEqual(
            hotfix_builder.frontend_attestation_artifact_id(current),
            "2.6.10-8227f6234cf2",
        )
        self.assertEqual(hotfix_builder.frontend_validator_version(legacy), "2.4.6")
        self.assertEqual(hotfix_builder.frontend_validator_version(current), "2.4.7")

    def test_new_profile_identity_and_packaged_scenarios(self):
        import frontend_contract_26915_4065 as contract
        profile = hotfix_builder.profile_for_asar(workflow.SUPPORTED_PACKAGES["26.915.4065.0"].asar_sha256)
        self.assertEqual(hotfix_builder.frontend_attestation_artifact_id(profile), "2.6.11-b8aeb817cd1e")
        self.assertEqual(hotfix_builder.frontend_validator_version(profile), "2.4.8")
        self.assertIn("project-alpha", contract._scenario_source())

    def test_6896_profile_identity_and_packaged_scenarios(self):
        import frontend_contract_26917_6896 as contract
        profile = hotfix_builder.profile_for_asar(workflow.SUPPORTED_PACKAGES["26.917.6896.0"].asar_sha256)
        self.assertEqual(hotfix_builder.frontend_attestation_artifact_id(profile), "2.6.12-00b7936388d1")
        self.assertEqual(hotfix_builder.frontend_validator_version(profile), "2.4.9")
        self.assertIn("project-alpha", contract._scenario_source())

    def test_9434_profile_identity_and_packaged_scenarios(self):
        import frontend_contract_26917_9434 as contract
        import frontend_row_contract_26917_9434 as row

        profile = hotfix_builder.profile_for_asar(workflow.SUPPORTED_PACKAGES["26.917.9434.0"].asar_sha256)
        self.assertEqual(hotfix_builder.frontend_attestation_artifact_id(profile), "2.6.13-d4234b03eb53")
        self.assertEqual(hotfix_builder.frontend_validator_version(profile), "2.4.10")
        self.assertIn("project-alpha", contract._scenario_source())
        self.assertIn("pending_recompute", row._scenario_source())

    def test_backend_policy_hashes_match_committed_bytes(self):
        for support in workflow.SUPPORTED_PACKAGES.values():
            digest = hashlib.sha256(support.backend_policy.read_bytes()).hexdigest()
            self.assertEqual(digest, support.backend_policy_sha256)

    def test_source_and_tests_use_an_english_baseline(self):
        cjk = re.compile(r"[\u4e00-\u9fff]")
        for path in list(SRC.rglob("*.py")) + list(SRC.rglob("*.js")) + list((ROOT / "tests").rglob("*.py")):
            self.assertIsNone(cjk.search(path.read_text(encoding="utf-8")), str(path))

    def test_readme_is_english_by_default(self):
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        self.assertIn(f"[{CHINESE_LABEL}](README.zh-CN.md)", english)
        self.assertIn("[English README](README.md)", chinese)
        self.assertFalse((ROOT / "README.en.md").exists())
        cjk = re.compile(r"[\u4e00-\u9fff]")
        self.assertEqual(
            [line for line in english.splitlines() if cjk.search(line)],
            [f"[{CHINESE_LABEL}](README.zh-CN.md)"],
        )
        self.assertIsNotNone(cjk.search(chinese))

    def test_release_assets_and_pages_are_declared(self):
        for path in ASSETS:
            self.assertTrue(path.is_file(), str(path))
            self.assertGreater(path.stat().st_size, 1000, str(path))
        release = (ROOT / ".github" / "workflows" / "release.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("codex-desktop-workflow-bundle.zip", release)
        self.assertIn("SHA256SUMS.txt", release)
        pages = (ROOT / ".github" / "workflows" / "pages.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("actions/deploy-pages", pages)

    def test_installer_script_parses(self):
        installer = ROOT / "install.ps1"
        self.assertIn(
            "install.ps1 | iex",
            (ROOT / "README.md").read_text(encoding="utf-8"),
        )
        if os.name != "nt":
            self.skipTest("Windows PowerShell is required for parser validation")
        command = (
            "$errors=$null; "
            f"[System.Management.Automation.Language.Parser]::ParseFile('{installer}',"
            "[ref]$null,[ref]$errors)|Out-Null; "
            "if($errors){$errors|ForEach-Object{$_.Message};exit 1}"
        )
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_profile_fixtures_do_not_carry_private_paths_or_tokens(self):
        forbidden = (
            "C:/Users/",
            "C:\\Users\\",
            "D:/Documents/",
            "gho_",
            "sk-",
        )
        for path in NEW_26915_FILES:
            text = path.read_text(encoding="utf-8")
            for value in forbidden:
                self.assertNotIn(value, text, str(path))
        self.assertIn(
            "project-alpha",
            (SRC / "codex_desktop_workflow" / "data" / "frontend_scenarios_26915.js").read_text(
                encoding="utf-8"
            ),
        )
        self.assertTrue(frontend_contract_26915._scenario_source())


if __name__ == "__main__":
    unittest.main()
