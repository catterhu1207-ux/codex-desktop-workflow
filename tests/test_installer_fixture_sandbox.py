"""Isolated installation must neither elevate nor overwrite user settings."""
from pathlib import Path
import tempfile,tomllib,unittest
from codex_desktop_workflow.verification_6573 import _configure_fixture_sandbox

class InstallerFixtureSandbox(unittest.TestCase):
    def test_empty_home_uses_supported_restricted_token_mode(self):
        with tempfile.TemporaryDirectory() as folder:
            home=Path(folder)
            result=_configure_fixture_sandbox(home)
            self.assertEqual(result['scope'],'disposable_home_only')
            self.assertEqual(tomllib.loads((home/'config.toml').read_text()),{'windows':{'sandbox':'unelevated'}})

    def test_synthetic_provider_and_existing_bytes_are_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            home=Path(folder);file=home/'config.toml'
            original=b'model_provider="fixture"\r\n[model_providers.fixture]\r\nbase_url="http://127.0.0.1:12345/v1"\r\n'
            file.write_bytes(original)
            _configure_fixture_sandbox(home)
            self.assertTrue(file.read_bytes().startswith(original))
            parsed=tomllib.loads(file.read_text())
            self.assertEqual(parsed['model_provider'],'fixture')
            self.assertEqual(parsed['model_providers']['fixture']['base_url'],'http://127.0.0.1:12345/v1')
            self.assertEqual(parsed['windows']['sandbox'],'unelevated')

    def test_preexisting_windows_settings_stop_without_writing(self):
        for setting in ('elevated','unelevated','mxc'):
            with self.subTest(setting=setting),tempfile.TemporaryDirectory() as folder:
                home=Path(folder);file=home/'config.toml'
                original=('[windows]\nsandbox="'+setting+'"\n').encode();file.write_bytes(original)
                with self.assertRaisesRegex(ValueError,'unexpected_fixture_windows'):_configure_fixture_sandbox(home)
                self.assertEqual(file.read_bytes(),original)

    def test_invalid_config_stops_without_writing(self):
        with tempfile.TemporaryDirectory() as folder:
            home=Path(folder);file=home/'config.toml';original=b'[broken\n';file.write_bytes(original)
            with self.assertRaises(tomllib.TOMLDecodeError):_configure_fixture_sandbox(home)
            self.assertEqual(file.read_bytes(),original)
