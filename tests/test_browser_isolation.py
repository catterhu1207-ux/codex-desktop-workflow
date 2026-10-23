import copy
import json
import os
from pathlib import Path
import shutil
import struct
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

from codex_desktop_workflow import browser_isolation as b


def write_asar(path, main):
    package = json.dumps({'main': '.vite/build/main.js'}).encode()
    main = main.encode()
    tree = {'files': {'package.json': {'offset': '0', 'size': len(package)},
        '.vite': {'files': {'build': {'files': {'main.js': {'offset': str(len(package)), 'size': len(main)}}}}}}}
    header = json.dumps(tree).encode()
    path.write_bytes(struct.pack('<4I', 4, 8 + len(header), 4 + len(header), len(header)) + header + package + main)


def write_bootstrap_asar(path):
    entries = {'package.json': json.dumps({'main': '.vite/build/early-bootstrap.js'}).encode(),
               '.vite/build/early-bootstrap.js': b'require("./bootstrap-hash.js")',
               '.vite/build/bootstrap-hash.js': b'require("./main-hash.js")',
               '.vite/build/main-hash.js': MAIN.encode()}
    tree, payload = {'files': {}}, b''
    for name, raw in entries.items():
        node = tree
        parts = name.split('/')
        for part in parts[:-1]:
            node = node['files'].setdefault(part, {'files': {}})
        node['files'][parts[-1]] = {'offset': str(len(payload)), 'size': len(raw)}
        payload += raw
    header = json.dumps(tree).encode()
    path.write_bytes(struct.pack('<4I', 4, 8 + len(header), 4 + len(header), len(header)) + header + payload)


MAIN = ('var Ma=`CODEX_ELECTRON_BUNDLED_PLUGINS_RESOURCES_PATH`,Na=`other`;'
        'function Pa(e){return(e?.env??process.env)[Ma]?.trim()||e?.resourcesPath||process.resourcesPath}'
        'var lifecycleName=`chrome-native-host`;')


class BrowserResourceIsolation(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.resources = self.root / 'app/resources'
        self.catalog = self.resources / 'plugins/openai-bundled'
        (self.catalog / '.agents/plugins').mkdir(parents=True)
        self.names = ['codex-app-tools', 'browser', 'unified-computer-use', 'computer-use',
                      'latex', 'code-review', 'deep-research', 'visualize', 'image-guided-assets']
        plugins = []
        for name in self.names + sorted(b.CHROME_PLUGINS):
            origin = self.catalog / 'plugins' / name
            (origin / '.codex-plugin').mkdir(parents=True)
            (origin / '.codex-plugin/plugin.json').write_text(json.dumps({'name': name, 'version': '1'}))
            (origin / 'payload.bin').write_bytes((name + '\0unchanged').encode())
            plugins.append({'name': name, 'source': {'source': 'local', 'path': './plugins/' + name},
                            'policy': {'installation': 'AVAILABLE'}})
        self.manifest = self.catalog / '.agents/plugins/marketplace.json'
        self.manifest.write_text(json.dumps({'name': 'openai-bundled', 'plugins': plugins}))
        self.original_manifest = self.manifest.read_bytes()
        (self.resources / 'cua_node/bin/node_modules').mkdir(parents=True)
        for relative in ('manifest.json', 'bin/node.exe', 'bin/node_repl.exe', 'bin/node_modules/runtime.js'):
            (self.resources / 'cua_node' / relative).write_bytes(relative.encode())
        (self.resources / 'codex.exe').write_bytes(b'unchanged-selected-backend')
        write_asar(self.resources / 'app.asar', MAIN)
        self.home, self.run = self.root / 'home', self.root / 'run'
        self.home.mkdir()
        self.run.mkdir()
        (self.home / 'config.toml').write_text('[windows]\nsandbox="unelevated"\n')
        (self.home / 'synthetic-history.jsonl').write_bytes(b'preserved-history')
        self.executable = self.resources.parent / 'ChatGPT.exe'
        self.executable.write_bytes(b'disposable-synthetic-app')

    def prepare(self, **kwargs):
        return b.prepare_resources(self.executable, self.home, self.run,
                                   kwargs.get('environment', {}), kwargs.get('inherited', {}))

    def test_only_chrome_catalog_entries_removed_and_nine_plugins_and_runtime_preserved(self):
        env, receipt = self.prepare()
        self.assertEqual(set(env), {b.RESOURCE_OVERRIDE})
        self.assertEqual(receipt['preserved_plugins'], self.names)
        self.assertEqual(set(receipt['excluded_plugins']), b.CHROME_PLUGINS)
        for entry in receipt['files']:
            self.assertEqual(Path(entry['source']).read_bytes(), Path(entry['copy']).read_bytes())
            self.assertNotEqual(Path(entry['source']).stat().st_ino, Path(entry['copy']).stat().st_ino)
        self.assertEqual(self.manifest.read_bytes(), self.original_manifest)
        self.assertEqual((self.home / 'synthetic-history.jsonl').read_bytes(), b'preserved-history')
        self.assertEqual(b.validate_resources(self.run)['status'], 'passed')

    @unittest.skipUnless(os.name == 'nt', 'Windows extended filesystem paths')
    def test_actual_deep_windows_payload_and_receipt_copy_and_readback(self):
        # Exercise real mkdir/open/scandir/stat/replace beyond MAX_PATH, even
        # when Windows long-path policy is disabled. No application is started.
        self.addCleanup(shutil.rmtree, b._io_path(self.root))
        nested = Path(*['nested-node-dependency-' + str(index) + '-' + 'x' * 18 for index in range(7)])
        source = self.resources / 'cua_node/bin/node_modules' / nested / 'payload.js'
        b._io_path(source.parent).mkdir(parents=True)
        b._io_path(source).write_bytes(b'actual-deep-runtime-payload')
        self.run = self.root / Path(*['deep-owned-run-' + str(index) + '-' + 'y' * 20 for index in range(7)])
        b._io_path(self.run).mkdir(parents=True)
        self.assertGreater(len(str(source)), 260)
        self.assertGreater(len(str(self.run)), 260)
        environment, receipt = self.prepare()
        selected = next(entry for entry in receipt['files'] if entry['source'] == str(source))
        destination = Path(selected['copy'])
        self.assertGreater(len(str(destination)), 260)
        self.assertEqual(b._io_path(destination).read_bytes(), b._io_path(source).read_bytes())
        self.assertNotEqual(b._plain(source).st_ino, b._plain(destination).st_ino)
        self.assertFalse(environment[b.RESOURCE_OVERRIDE].startswith('\\\\?\\'))
        for entry in receipt['files']:
            self.assertFalse(entry['source'].startswith('\\\\?\\'))
            self.assertFalse(entry['copy'].startswith('\\\\?\\'))
        self.assertEqual(b.validate_resources(self.run)['status'], 'passed')
        b._write(self.run / 'readonly-guard.json', {'status': 'synthetic'})
        self.assertEqual(json.loads(b._io_path(self.run / 'readonly-guard.json').read_text()), {'status': 'synthetic'})
        b._io_path(destination).write_bytes(b'changed-deep-payload')
        with self.assertRaisesRegex(RuntimeError, 'prepared_bytes_changed'):
            b.validate_resources(self.run)

    @unittest.skipUnless(os.name == 'nt', 'Windows path syntax')
    def test_only_normal_absolute_drive_or_unc_paths_are_extended(self):
        self.assertEqual(str(b._io_path(Path('C:/owned/file'))), '\\\\?\\C:\\owned\\file')
        self.assertEqual(str(b._io_path(Path('//server/share/owned/file'))), '\\\\?\\UNC\\server\\share\\owned\\file')
        for path in ('relative/file', 'C:relative', 'C:/owned/../escape', 'C:/owned/file:stream',
                     'C:/owned/trailing.', 'C:/owned/trailing ', '//?/C:/owned', '//./C:/owned'):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'noncanonical_io_path'):
                b._io_path(Path(path))

    def test_used_fixture_cannot_be_relaunched(self):
        self.prepare()
        fresh_run = self.root / 'run2'
        fresh_run.mkdir()
        with self.assertRaisesRegex(ValueError, 'home_not_fresh'):
            b.prepare_resources(self.executable, self.home, fresh_run, {}, {})

    def test_existing_plugin_state_rejected_even_if_disabled(self):
        (self.home / 'config.toml').write_text('[plugins."chrome@openai-bundled"]\nenabled=false\n')
        with self.assertRaisesRegex(ValueError, 'existing_plugin_configuration'):
            self.prepare()

    def test_existing_cache_and_marketplace_state_rejected(self):
        for relative in ('plugins', '.tmp/bundled-marketplaces', 'chrome-native-hosts-v2.json'):
            with self.subTest(relative=relative):
                target = self.home / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text('synthetic')
                with self.assertRaisesRegex(ValueError, 'home_not_fresh'):
                    self.prepare()
                target.unlink()

    def test_inherited_or_explicit_override_cannot_escape_isolation(self):
        for key in b.PROTECTED_ENV:
            for source in ('environment', 'inherited'):
                with self.subTest(key=key, source=source):
                    with self.assertRaisesRegex(ValueError, 'environment_override'):
                        self.prepare(**{source: {key: 'untrusted'}})

    def test_plugin_path_escape_rejected_before_copy(self):
        catalog = json.loads(self.manifest.read_text())
        catalog['plugins'][0]['source']['path'] = '../../outside'
        self.manifest.write_text(json.dumps(catalog))
        with self.assertRaisesRegex(ValueError, 'path_escape'):
            self.prepare()

    def test_unknown_prod_resolver_is_rejected(self):
        write_asar(self.resources / 'app.asar', MAIN.replace('return(e?.env', 'if(isDev)return(e?.env'))
        with self.assertRaisesRegex(ValueError, 'production_resource_override_unverified'):
            self.prepare()

    def test_actual_bootstrap_chain_is_resolved_without_executing_javascript(self):
        write_bootstrap_asar(self.resources / 'app.asar')
        result = b.resource_capability(self.resources)
        self.assertEqual(len(result['entry_chain']), 3)
        self.assertTrue(result['production_resource_override'])
        self.assertEqual(result['main_entry'], '.vite/build/main-hash.js')

    def test_missing_runtime_is_not_silently_replaced(self):
        (self.resources / 'cua_node/bin/node_repl.exe').unlink()
        with self.assertRaises(FileNotFoundError):
            self.prepare()

    def test_changed_backend_or_catalog_cannot_finish_acceptance(self):
        env, _ = self.prepare()
        target = Path(env[b.RESOURCE_OVERRIDE]) / 'plugins/openai-bundled/.agents/plugins/marketplace.json'
        before = target.read_bytes()
        target.write_bytes(before + b' ')
        with self.assertRaisesRegex(RuntimeError, 'catalog_changed'):
            b.validate_resources(self.run)
        target.write_bytes(before)
        (self.resources / 'codex.exe').write_bytes(b'swapped-backend')
        with self.assertRaisesRegex(RuntimeError, 'inventory_changed'):
            b.validate_resources(self.run)

    def test_new_chrome_file_in_overlay_is_rejected(self):
        env, _ = self.prepare()
        (Path(env[b.RESOURCE_OVERRIDE]) / 'unexpected-native-host.exe').write_bytes(b'new')
        with self.assertRaisesRegex(RuntimeError, 'inventory_changed'):
            b.validate_resources(self.run)

    def test_legacy_without_chrome_keeps_interface_and_still_requires_shared_guard(self):
        old = self.root / 'old/resources'
        old.mkdir(parents=True)
        write_asar(old / 'app.asar', 'var normalApplication=true;')
        env, receipt = b.prepare_resources(old.parent / 'ChatGPT.exe', self.home, self.run, {}, {})
        self.assertEqual(env, {})
        self.assertEqual(receipt['status'], 'not_applicable')
        self.assertTrue(b.validate_resources(self.run)['shared_state_guard_required'])

    def test_redirected_source_is_rejected(self):
        original = b._plain
        def reject(path):
            if Path(path).name == 'payload.bin':
                raise ValueError('browser_isolation_redirected_path')
            return original(path)
        with patch.object(b, '_plain', side_effect=reject), self.assertRaisesRegex(ValueError, 'redirected_path'):
            self.prepare()

    def test_two_isolated_starts_have_distinct_profiles_and_no_production_profile(self):
        from codex_desktop_workflow.isolated_run import IsolatedRun
        from electron_update_safety import lifecycle
        identity = lifecycle.ProcessIdentity(123, 1, str(self.executable), '/Date(1000)/')
        process = Mock(pid=123)
        guard = Mock()
        guard.start.return_value = guard
        clean_env = {k: v for k, v in os.environ.items() if k not in b.PROTECTED_ENV}
        clean_env['USERPROFILE'] = str(self.root / 'production-profile')
        with patch.dict(os.environ, clean_env, clear=True), \
             patch('codex_desktop_workflow.windows_integrity.check_native_desktop', return_value={'status': 'passed'}), \
             patch('codex_desktop_workflow.isolated_run.subprocess.Popen', return_value=process) as popen, \
             patch.object(lifecycle, '_processes', return_value=[identity]), \
             patch('codex_desktop_workflow.isolated_run.time.sleep'), \
             patch.object(b, 'SharedBrowserGuard', return_value=guard):
            first = IsolatedRun._start_owl(self.executable, self.root, self.home, [], {}, None, True)
            second_home = self.root / 'second-home'
            second_home.mkdir()
            second = IsolatedRun._start_owl(self.executable, self.root, second_home, [], {}, None, True)
        first_env, second_env = [call.kwargs['env'] for call in popen.call_args_list]
        self.assertNotEqual(first_env['USERPROFILE'], second_env['USERPROFILE'])
        self.assertEqual(Path(first_env['USERPROFILE']), first.run_directory / 'profile')
        self.assertEqual(Path(second_env['USERPROFILE']), second.run_directory / 'profile')
        self.assertIn(b.RESOURCE_OVERRIDE, first_env)
        self.assertEqual(first_env['CODEX_CLI_PATH'], str(self.resources / 'codex.exe'))

    def test_normal_production_launch_does_not_create_test_resources_or_guard(self):
        from codex_desktop_workflow.isolated_run import IsolatedRun
        from electron_update_safety import lifecycle
        identity = lifecycle.ProcessIdentity(123, 1, str(self.executable), '/Date(1000)/')
        environment = {'USERPROFILE': str(self.root / 'production-profile'),
                       b.RESOURCE_OVERRIDE: 'existing-production-setting'}
        with patch.dict(os.environ, environment), \
             patch('codex_desktop_workflow.windows_integrity.check_native_desktop', return_value={'status': 'passed'}), \
             patch('codex_desktop_workflow.isolated_run.subprocess.Popen', return_value=Mock(pid=123)) as popen, \
             patch.object(lifecycle, '_processes', return_value=[identity]), \
             patch('codex_desktop_workflow.isolated_run.time.sleep'), \
             patch.object(b, 'prepare_resources', side_effect=AssertionError('must not alter production')) as prepare, \
             patch.object(b, 'SharedBrowserGuard') as guard:
            IsolatedRun._start_owl(self.executable, self.root, self.home, [], {}, None, False)
        prepare.assert_not_called()
        guard.assert_not_called()
        self.assertEqual(popen.call_args.kwargs['env'][b.RESOURCE_OVERRIDE], 'existing-production-setting')


class SharedStateGuard(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.receipt = Path(self.temporary.name) / 'guard.json'
        self.state = {'registry': {'32': None, '64': None}, 'files': {'index': None}}
        self.events = Mock()

    def guard(self):
        return b.SharedBrowserGuard(self.receipt, snapshot=lambda: copy.deepcopy(self.state),
                                    notifications=lambda: self.events, interval=.005).start()

    def wait_failure(self, guard):
        deadline = time.monotonic() + 2
        while not guard.failure and time.monotonic() < deadline:
            time.sleep(.005)
        self.assertTrue(guard.failure)

    def test_unchanged_state_passes_and_close_is_idempotent(self):
        guard = self.guard()
        result = guard.close()
        self.assertEqual(result, guard.close())
        self.assertTrue(result['before_during_after_unchanged'])
        self.events.close.assert_called_once()

    def test_changed_index_fails_without_restoration(self):
        guard = self.guard()
        self.state['files']['index'] = 'changed'
        self.wait_failure(guard)
        with self.assertRaisesRegex(RuntimeError, 'state_changed'):
            guard.close()
        self.assertEqual(self.state['files']['index'], 'changed')
        self.assertEqual(json.loads(self.receipt.read_text())['status'], 'failed')

    def test_native_event_catches_write_then_restore_between_hash_samples(self):
        guard = self.guard()
        self.events.check.side_effect = RuntimeError('browser_isolation_shared_registry_changed')
        self.wait_failure(guard)
        with self.assertRaisesRegex(RuntimeError, 'registry_changed'):
            guard.close()

    def test_final_snapshot_change_cannot_be_reported_as_passed(self):
        guard = self.guard()
        self.state['registry']['64'] = 'changed-after-last-poll'
        with self.assertRaisesRegex(RuntimeError, 'state_changed'):
            guard.close()

    def test_monitor_read_failure_is_not_an_unchanged_state(self):
        guard = self.guard()
        guard.snapshot = Mock(side_effect=PermissionError('access denied'))
        self.wait_failure(guard)
        with self.assertRaisesRegex(RuntimeError, 'access denied'):
            guard.close()


if __name__ == '__main__':
    unittest.main()
