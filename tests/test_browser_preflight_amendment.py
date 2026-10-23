"""Real Windows catalog-parent rejection and unchanged accepted-resource behavior."""
import copy
import json
import os
from pathlib import Path
import stat
import subprocess
import unittest
from unittest.mock import patch

from codex_desktop_workflow import browser_isolation as b
import test_browser_isolation as fixtures


class BrowserResourcePreflightAmendment(unittest.TestCase):
    setUp = fixtures.BrowserResourceIsolation.setUp
    prepare = fixtures.BrowserResourceIsolation.prepare

    @unittest.skipUnless(os.name == 'nt', 'Real Windows junction behavior')
    def test_both_catalog_layouts_reject_parent_junction_before_discovery_or_copy(self):
        for layout in ('direct', 'unpacked'):
            with self.subTest(layout=layout):
                original = self.resources / 'plugins'
                retained = self.root / ('retained-plugins-' + layout)
                junction = original if layout == 'direct' else self.resources / 'app.asar.unpacked/plugins'
                for path in (original, retained, junction):
                    self.assertTrue(path.is_absolute() and path.is_relative_to(self.root))
                    self.assertNotIn('..', path.parts)
                original.rename(retained)
                if layout == 'unpacked':
                    junction.parent.mkdir()
                try:
                    subprocess.run(['cmd.exe', '/d', '/c', 'mklink', '/J', str(junction), str(retained)],
                                   check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    self.assertTrue(junction.lstat().st_file_attributes & 0x400)
                    with patch.object(b, 'resource_capability', side_effect=AssertionError('discovery ran before rejection')):
                        with self.assertRaisesRegex(ValueError, 'browser_isolation_redirected_path'):
                            self.prepare()
                    self.assertFalse((self.run / 'browser-isolated-resources').exists())
                    self.assertFalse((self.run / 'browser-resource-isolation.json').exists())
                    self.assertFalse((self.home / '.browser-isolation-used.json').exists())
                finally:
                    # Unlink only the exact test junction; never recurse through it.
                    if junction.exists() or junction.is_symlink():
                        self.assertTrue(junction.is_relative_to(self.root))
                        self.assertTrue(junction.lstat().st_file_attributes & 0x400)
                        os.rmdir(b._io_path(junction))
                    self.assertTrue(retained.is_relative_to(self.root))
                    self.assertTrue(stat.S_ISDIR(retained.lstat().st_mode))
                    retained.rename(original)

    def test_plain_catalog_has_identical_resources_receipt_and_environment(self):
        environment = {'SYNTHETIC_ALLOWED_OPTION': 'unchanged'}
        inherited = {'SYNTHETIC_INHERITED_OPTION': 'unchanged'}
        before_environment, before_inherited = copy.deepcopy(environment), copy.deepcopy(inherited)
        source_bytes = {path: b._digest(path) for path in b._resource_files(self.resources)}
        guarded_env, guarded_receipt = self.prepare(environment=environment, inherited=inherited)
        second_home, second_run = self.root / 'home-without-added-check', self.root / 'run-without-added-check'
        second_home.mkdir()
        second_run.mkdir()
        for name in ('config.toml', 'synthetic-history.jsonl'):
            (second_home / name).write_bytes((self.home / name).read_bytes())
        # The amendment contains only this added call/function. Disabling it
        # reproduces the frozen source's behavior for the same accepted inputs.
        with patch.object(b, '_plain_catalog_inputs', return_value=None):
            baseline_env, baseline_receipt = b.prepare_resources(
                self.executable, second_home, second_run, environment, inherited)
        def relative_run(value, run):
            return json.loads(json.dumps(value).replace(str(run).replace('\\', '\\\\'), '<owned-run>'))
        self.assertEqual(relative_run(guarded_env, self.run), relative_run(baseline_env, second_run))
        self.assertEqual(relative_run(guarded_receipt, self.run), relative_run(baseline_receipt, second_run))
        for receipt in (guarded_receipt, baseline_receipt):
            for entry in receipt['files']:
                self.assertEqual(b._digest(Path(entry['copy'])), entry['sha256'])
        self.assertEqual(b.validate_resources(self.run)['status'], 'passed')
        self.assertEqual(b.validate_resources(second_run)['status'], 'passed')
        self.assertEqual({path: b._digest(path) for path in b._resource_files(self.resources)}, source_bytes)
        self.assertEqual(environment, before_environment)
        self.assertEqual(inherited, before_inherited)
        self.assertEqual((self.home / 'synthetic-history.jsonl').read_bytes(), b'preserved-history')


if __name__ == '__main__':
    unittest.main()
