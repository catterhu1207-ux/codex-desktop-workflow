import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock

EXAMPLE = Path(__file__).resolve().parents[1] / 'examples' / 'channel-preview'
sys.path.insert(0, str(EXAMPLE))
import preview
import diagnostics
from profiles import load_profiles


class ChannelPreviewExampleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name)
        (self.home / 'sessions').mkdir()
        profiles, _ = load_profiles()
        self.profiles = profiles
        for item in profiles.values():
            filename = item['catalog'] or 'models_cache.json'
            model = {'slug': item['model'], 'base_instructions': '',
                     'experimental_supported_tools': [],
                     'supported_reasoning_levels': [{'effort': item['effort']}],
                     'input_modalities': ['text']}
            (self.home / filename).write_text(json.dumps({'models': [model]}), encoding='utf-8')
        sections = []
        for item in profiles.values():
            if item['route_type'] == 'subscription':
                continue
            sections += [f"[model_providers.{item['provider']}]", 'base_url = "https://example.invalid/v1"',
                         'wire_api = "responses"']
            if item['env_key']:
                sections.append(f'env_key = "{item["env_key"]}"')
        (self.home / 'config.toml').write_text(
            'model = "gpt-5.6-sol"\nmodel_reasoning_effort = "medium"\nservice_tier = "default"\n'
            + '\n'.join(sections) + '\n', encoding='utf-8')
        state = sqlite3.connect(self.home / 'state_5.sqlite')
        state.execute('CREATE TABLE threads (id TEXT, rollout_path TEXT, archived INTEGER, model_provider TEXT)')
        state.executemany('INSERT INTO threads VALUES (?,?,?,?)', [
            ('one', str(self.home / 'sessions' / 'one.jsonl'), 0, 'openai'),
            ('two', str(self.home / 'sessions' / 'two.jsonl'), 0, 'mimo'),
            ('old', str(self.home / 'sessions' / 'old.jsonl'), 1, 'openai'),
            ('foreign', str(self.home.parent / 'foreign.jsonl'), 0, 'openai')])
        state.commit()
        state.close()

    def tearDown(self):
        self.temp.cleanup()

    def test_all_profiles_preview_without_writes(self):
        original = (self.home / 'config.toml').read_bytes()
        with mock.patch.object(preview, 'credential_available', return_value=True):
            for target in self.profiles:
                result = preview.preview(self.home, target)
                self.assertEqual(result['status'], 'ready')
                self.assertEqual(result['inheritance_estimate']['external_unarchived'], 1)
                self.assertEqual(result['inheritance_estimate']['managed_unarchived'], 2)
        self.assertEqual((self.home / 'config.toml').read_bytes(), original)
        self.assertFalse((self.home / 'maintenance').exists())

    def test_online_probe_requires_explicit_flag(self):
        with mock.patch.object(diagnostics, 'credential_available', return_value=True), \
             mock.patch.object(diagnostics, 'probe') as network:
            result = diagnostics.diagnose(self.home, 'mimo')
        self.assertEqual(result['online']['status'], 'not_requested')
        network.assert_not_called()


if __name__ == '__main__':
    unittest.main()
