import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from codex_desktop_workflow.language import initialize_new_data
from codex_desktop_workflow.isolated_run import IsolatedRun
from electron_update_safety import lifecycle
import hotfix_profile_261007_9446 as profile


class PublicEnglish(unittest.TestCase):
    def test_new_independent_data_defaults_to_english(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw)
            self.assertTrue(initialize_new_data(root))
            state=json.loads((root/'.codex-global-state.json').read_text())
            self.assertEqual(state['electron-persisted-atom-state']['electron-language'],'en')

    def test_existing_state_and_history_are_preserved(self):
        for name,value in (('.codex-global-state.json',b'{"user-language":"zh-CN"}'),('retained-history',b'user-owned')):
            with tempfile.TemporaryDirectory() as raw:
                root=Path(raw);file=root/name;file.write_bytes(value)
                self.assertFalse(initialize_new_data(root))
                self.assertEqual(file.read_bytes(),value)
                self.assertEqual(len(list(root.iterdir())),1)

    def test_launch_passes_english_default_and_preserves_explicit_override(self):
        for args,expected in (([],['--lang=en-US']),(['--lang=fr'],['--lang=fr']),(['--lang','de'],['--lang','de'])):
            with tempfile.TemporaryDirectory() as raw,mock.patch.object(lifecycle.IsolatedRun,'start') as start:
                root=Path(raw)
                (root/'codex-desktop-workflow-manifest.json').write_text(json.dumps({'package_version':'26.1007.9446.0'}))
                IsolatedRun.start(root/'ChatGPT.exe',root,args=args)
                self.assertEqual(start.call_args.kwargs['args'],expected)

    def test_current_owned_update_literals_are_english(self):
        new=profile.PAIRS['portable_update_awareness'][0][1].decode('utf8')
        for value in ('Adaptation ready','Official package available','New version announced'):
            self.assertIn(value,new)
        self.assertFalse(any('\u4e00'<=c<='\u9fff' for c in new))
        self.assertFalse(any('\u4e00'<=c<='\u9fff' for c in profile.ATTESTATION_MODULE.decode('utf8')))
