import json,tempfile,tomllib,unittest
from pathlib import Path
from codex_desktop_workflow.verification_3705 import _configure_fixture_sandbox

class CurrentFixtureSandbox(unittest.TestCase):
    def test_empty_home_is_restricted_before_any_native_start(self):
        with tempfile.TemporaryDirectory() as d:
            home=Path(d);_configure_fixture_sandbox(home)
            self.assertEqual(tomllib.loads((home/'config.toml').read_text())['windows'],{'sandbox':'unelevated'})

    def test_only_the_actual_fresh_generated_fixture_can_reuse_its_preconfigured_mode(self):
        for kind in ('native','unproved','used','different','extra'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as d:
                home=Path(d);config=home/'config.toml'
                config.write_text('[windows]\nsandbox="'+('elevated' if kind=='different' else 'unelevated')+'"\n'+('other=true\n' if kind=='extra' else ''))
                if kind!='unproved':(home/'native-history-fixture.json').write_text(json.dumps({'all_created_and_sent_by_actual_backend':True}))
                if kind=='used':(home/'.browser-isolation-used.json').write_text('{}')
                before=config.read_bytes()
                if kind=='native':
                    result=_configure_fixture_sandbox(home)
                    self.assertTrue(result['configured_before_native_fixture_generation'])
                else:
                    with self.assertRaises(ValueError):_configure_fixture_sandbox(home)
                self.assertEqual(config.read_bytes(),before)
