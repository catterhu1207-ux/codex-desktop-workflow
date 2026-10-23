"""Keep disposable desktop verification out of the user's Chrome integration.

The bundled-resource override is consumed by the shipped production desktop.
Disabling an installed plugin is insufficient: its native host is reconciled
before the disabled configuration is restored. Never restore shared state here.
"""
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
from pathlib import PurePosixPath
import re
import stat
import struct
import threading
import time
import tomllib

CHROME_PLUGINS = frozenset({'chrome', 'chrome-dev', 'chrome-internal'})
NATIVE_NAMES = tuple('com.openai.codexextension' + suffix for suffix in ('', '.dev', '.internal'))
RESOURCE_OVERRIDE = 'CODEX_ELECTRON_BUNDLED_PLUGINS_RESOURCES_PATH'
PROTECTED_ENV = frozenset({RESOURCE_OVERRIDE, 'CODEX_ELECTRON_BUNDLED_PLUGINS_FORCE_RELOAD',
    'CODEX_USE_INTERNAL_CHROME_PLUGIN', 'CODEX_ELECTRON_DESKTOP_FEATURE_OVERRIDES',
    'CODEX_ENABLE_DEV_BUNDLED_PLUGINS', 'CODEX_BROWSER_USE_NODE_PATH', 'CODEX_NODE_REPL_PATH',
    'CODEX_CHROME_USER_DATA_DIR', 'NODE_ENV'})
REGISTRY_ROOT = r'Software\Google\Chrome\NativeMessagingHosts'


def _io_path(path):
    """Use extended Windows I/O without changing recorded paths or following links."""
    path = Path(path)
    if os.name != 'nt':
        return path
    text = str(path).replace('/', '\\')
    if (not path.is_absolute() or text.startswith(('\\\\?\\', '\\\\.\\'))
            or '\0' in text or any(part in ('.', '..') for part in text.split('\\'))):
        raise ValueError('browser_isolation_noncanonical_io_path')
    if re.match(r'^[A-Za-z]:\\', text):
        parts = text[3:].split('\\')
        extended = '\\\\?\\' + text
    elif re.match(r'^\\\\[^\\/:*?"<>|]+\\[^\\/:*?"<>|]+(?:\\|$)', text):
        parts = text[2:].split('\\')
        extended = '\\\\?\\UNC\\' + text[2:]
    else:
        raise ValueError('browser_isolation_noncanonical_io_path')
    if any(part and (part.endswith(('.', ' ')) or ':' in part) for part in parts):
        raise ValueError('browser_isolation_noncanonical_io_path')
    return Path(extended)


def _children(path):
    # scandir returns extended names when given an extended root. Reconstruct
    # ordinary paths so manifests, scope comparisons and external apps keep the
    # original identity. lstat checks still reject every reparse point.
    with os.scandir(_io_path(path)) as entries:
        names = sorted(entry.name for entry in entries)
    return [Path(path) / name for name in names]


def _resource_files(root):
    result, pending = set(), [Path(root)]
    while pending:
        directory = pending.pop()
        _plain(directory)
        for path in _children(directory):
            info = _plain(path)
            if stat.S_ISDIR(info.st_mode):
                pending.append(path)
            elif stat.S_ISREG(info.st_mode):
                result.add(path)
            else:
                raise ValueError('browser_isolation_unsupported_file_type')
    return result


def _plain(path):
    info = _io_path(path).lstat()
    if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
        raise ValueError('browser_isolation_redirected_path:' + str(path))
    return info


def _identity(info):
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def _digest(path):
    before = _plain(path)
    if not stat.S_ISREG(before.st_mode):
        raise ValueError('browser_isolation_not_regular_file')
    digest = hashlib.sha256()
    with _io_path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    if _identity(before) != _identity(_plain(path)):
        raise RuntimeError('browser_isolation_file_changed_during_read')
    return digest.hexdigest()


def _write(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + '.writing')
    _io_path(temporary).write_text(json.dumps(value, indent=2), encoding='utf8')
    os.replace(_io_path(temporary), _io_path(path))


def _copy_tree(source, destination, entries):
    info = _plain(source)
    if stat.S_ISDIR(info.st_mode):
        _io_path(destination).mkdir()
        for child in _children(source):
            _copy_tree(child, destination / child.name, entries)
    elif stat.S_ISREG(info.st_mode):
        digest = hashlib.sha256()
        with _io_path(source).open('rb') as src, _io_path(destination).open('xb') as dst:
            for chunk in iter(lambda: src.read(1024 * 1024), b''):
                digest.update(chunk)
                dst.write(chunk)
        expected = digest.hexdigest()
        if _identity(info) != _identity(_plain(source)) or _digest(destination) != expected:
            raise RuntimeError('browser_isolation_copy_changed')
        entries.append({'source': str(source), 'copy': str(destination), 'sha256': expected,
                        'size': info.st_size})
    else:
        raise ValueError('browser_isolation_unsupported_file_type')


def _reject_used_home(home):
    _plain(home)
    # Fresh fixtures may already contain synthetic history or a copied login.
    # They must never contain plugin install state, which can trigger removal
    # callbacks even when Chrome is absent from the new resource catalog.
    for relative in ('plugins', '.tmp/bundled-marketplaces', '.browser-isolation-used.json',
                     'chrome-native-hosts-v2.json'):
        if _io_path(home / relative).exists() or _io_path(home / relative).is_symlink():
            raise ValueError('browser_isolation_home_not_fresh:' + relative)
    config = home / 'config.toml'
    if _io_path(config).exists():
        _plain(config)
        parsed = tomllib.loads(_io_path(config).read_text(encoding='utf8'))
        if parsed.get('plugins') or parsed.get('marketplaces'):
            raise ValueError('browser_isolation_existing_plugin_configuration')
    state = home / '.codex-global-state.json'
    if _io_path(state).exists():
        _plain(state)
        if json.loads(_io_path(state).read_text(encoding='utf8')).get('electron-chrome-extension-sync-managed-plugin-ids'):
            raise ValueError('browser_isolation_existing_chrome_sync_state')


def resource_capability(resources):
    """Read only the bounded ASAR header and actual main entry, never the blob."""
    asar = Path(resources) / 'app.asar'
    initial = _plain(asar)
    with _io_path(asar).open('rb') as stream:
        lead = stream.read(16)
        if len(lead) != 16:
            raise ValueError('browser_isolation_invalid_asar')
        header_block, header_size = struct.unpack_from('<I', lead, 4)[0], struct.unpack_from('<I', lead, 12)[0]
        if not 0 < header_size <= 8 * 1024 * 1024 or header_block < header_size:
            raise ValueError('browser_isolation_invalid_asar_header')
        tree = json.loads(stream.read(header_size))

        def read_entry(name, limit):
            parts = name.removeprefix('./').split('/')
            if any(p in ('', '.', '..') for p in parts):
                raise ValueError('browser_isolation_asar_entry_escape')
            node = tree
            for part in parts:
                node = node['files'][part]
            size, offset = int(node['size']), 8 + header_block + int(node['offset'])
            if node.get('unpacked') or node.get('link') or not 0 < size <= limit or offset + size > initial.st_size:
                raise ValueError('browser_isolation_invalid_asar_entry')
            stream.seek(offset)
            raw = stream.read(size)
            if len(raw) != size:
                raise ValueError('browser_isolation_truncated_asar_entry')
            return raw

        package = json.loads(read_entry('package.json', 256 * 1024))
        entry_name = package['main']
        chain = []
        # Owl loads early-bootstrap -> bootstrap -> main. Follow only these
        # literal shipped entry links, without evaluating JavaScript or reading
        # unrelated modules/the complete ASAR into memory.
        for _ in range(4):
            entry = read_entry(entry_name, 16 * 1024 * 1024)
            chain.append({'entry': entry_name, 'sha256': hashlib.sha256(entry).hexdigest()})
            text = entry.decode('utf8')
            if RESOURCE_OVERRIDE in text:
                break
            targets = set(re.findall(r'require\([\"\'](\./(?:bootstrap|main)[^/\"\']*\.js)[\"\']\)', text))
            if not targets:
                break
            if len(targets) != 1:
                raise ValueError('browser_isolation_ambiguous_main_chain')
            entry_name = str(PurePosixPath(entry_name).parent / next(iter(targets)))
            if entry_name in {item['entry'] for item in chain}:
                raise ValueError('browser_isolation_cyclic_main_chain')
        else:
            raise ValueError('browser_isolation_main_chain_too_deep')
    if _identity(initial) != _identity(_plain(asar)):
        raise RuntimeError('browser_isolation_asar_changed')
    binding = re.search(r'(?:var |,)([\w$]+)=[`\"]' + RESOURCE_OVERRIDE + r'[`\"]', text)
    supported = False
    if binding:
        variable = re.escape(binding.group(1))
        # Both retained 8120 and current 8622 use this ungated Prod resolver.
        # An unfamiliar resolver must be reviewed instead of silently falling back.
        resolver = r'function [\w$]+\([\w$]+\)\{return\([^{}]{0,100}process\.env\)\[' + variable + r'\]\?\.trim\(\)\|\|[^{}]{0,100}process\.resourcesPath\}'
        supported = re.search(resolver, text) is not None
    return {'main_entry': entry_name, 'main_sha256': hashlib.sha256(entry).hexdigest(), 'entry_chain': chain,
            'production_resource_override': supported,
            'chrome_lifecycle_present': any(term in text for term in
                ('chrome-native-host', 'chrome_native_host', 'Chrome native host', 'syncInstallStateWithChromeExtension'))}


def _plain_catalog_inputs(resources):
    """Reject redirected catalog parents before any resource discovery or copy."""
    resources = Path(resources)
    # Checking only the catalog leaf misses a junction in plugins or in the
    # unpacked layout. Inspect each component without resolving its target.
    for directory in reversed((resources, *resources.parents)):
        if not stat.S_ISDIR(_plain(directory).st_mode):
            raise ValueError('browser_isolation_catalog_parent_not_directory')
    for relative in ('plugins/openai-bundled/.agents/plugins/marketplace.json',
                     'app.asar.unpacked/plugins/openai-bundled/.agents/plugins/marketplace.json'):
        parts = Path(relative).parts
        path = resources
        for index, part in enumerate(parts):
            path = path / part
            try:
                info = _plain(path)
            except FileNotFoundError:
                break  # An optional layout may be absent; never follow links.
            expected = stat.S_ISREG if index == len(parts) - 1 else stat.S_ISDIR
            if not expected(info.st_mode):
                raise ValueError('browser_isolation_catalog_component_type')


def prepare_resources(executable, home, run, environment, inherited=None):
    """Prepare a separate catalog; never edit or link the installed resources."""
    inherited = os.environ if inherited is None else inherited
    for key in PROTECTED_ENV:
        if key in environment or inherited.get(key):
            raise ValueError('browser_isolation_environment_override:' + key)
    home, run = Path(home), Path(run)
    _reject_used_home(home)
    _plain(run)
    resources = Path(executable).parent / 'resources'
    _plain(resources)
    _plain_catalog_inputs(resources)
    capability = resource_capability(resources)
    catalogs = [resources / 'plugins/openai-bundled',
                resources / 'app.asar.unpacked/plugins/openai-bundled']
    present = [p for p in catalogs if _io_path(p / '.agents/plugins/marketplace.json').is_file()]
    if not present and not capability['chrome_lifecycle_present']:
        receipt = {'schema_version': 1, 'status': 'not_applicable',
            'scope': 'disposable_verification_only', 'reason': 'legacy_without_bundled_chrome',
            'capability': capability, 'preserved_plugins': [], 'excluded_plugins': [],
            'resources': str(resources)}
        with _io_path(home / '.browser-isolation-used.json').open('x', encoding='utf8') as claim:
            json.dump({'run': str(run)}, claim)
        _write(run / 'browser-resource-isolation.json', receipt)
        return {}, receipt
    if len(present) != 1:
        raise ValueError('browser_isolation_expected_one_bundled_catalog')
    if not capability['production_resource_override']:
        raise ValueError('browser_isolation_production_resource_override_unverified')
    source = present[0]
    for part in (source, source / '.agents', source / '.agents/plugins'):
        _plain(part)
    manifest = source / '.agents/plugins/marketplace.json'
    source_digest = _digest(manifest)
    catalog = json.loads(_io_path(manifest).read_text(encoding='utf8'))
    if catalog.get('name') != 'openai-bundled' or not isinstance(catalog.get('plugins'), list):
        raise ValueError('browser_isolation_invalid_catalog')
    names = [p.get('name') for p in catalog['plugins']]
    if any(not isinstance(name, str) or not name for name in names) or len(names) != len(set(names)):
        raise ValueError('browser_isolation_duplicate_or_invalid_plugin')
    selected = [p for p in catalog['plugins'] if p['name'] not in CHROME_PLUGINS]
    if not selected:
        raise ValueError('browser_isolation_unrecognized_bundled_catalog')
    root = run / 'browser-isolated-resources'
    _io_path(root).mkdir()
    destination = root / 'plugins/openai-bundled'
    _io_path(destination / '.agents/plugins').mkdir(parents=True)
    entries = []
    for plugin in selected:
        local = plugin.get('source', {})
        relative = Path(local.get('path', ''))
        if local.get('source') != 'local' or relative.is_absolute() or '..' in relative.parts or not relative.parts:
            raise ValueError('browser_isolation_plugin_path_escape')
        origin = source / relative
        target = destination / relative
        if not origin.is_relative_to(source) or not target.is_relative_to(destination):
            raise ValueError('browser_isolation_plugin_path_escape')
        # Check intermediate directories as well as recursively copied children.
        for ancestor in origin.parents:
            if ancestor == source.parent:
                break
            _plain(ancestor)
        plugin_manifest = origin / '.codex-plugin/plugin.json'
        _plain(origin / '.codex-plugin')
        _digest(plugin_manifest)
        if json.loads(_io_path(plugin_manifest).read_text(encoding='utf8')).get('name') != plugin['name']:
            raise ValueError('browser_isolation_plugin_name_mismatch')
        _io_path(target.parent).mkdir(parents=True, exist_ok=True)
        _copy_tree(origin, target, entries)
    filtered = {**catalog, 'plugins': selected}
    filtered_manifest = destination / '.agents/plugins/marketplace.json'
    _io_path(filtered_manifest).write_text(json.dumps(filtered, indent=2) + '\n', encoding='utf8')
    # This override is also used by upstream browser runtime resolution.
    # Preserve the complete runtime instead of silently losing node/node-repl.
    runtime = resources / 'cua_node'
    _plain(runtime)
    _plain(runtime / 'bin')
    for relative in ('manifest.json', 'bin/node.exe', 'bin/node_repl.exe'):
        _digest(runtime / relative)
    _copy_tree(runtime, root / 'cua_node', entries)
    if _digest(manifest) != source_digest:
        raise RuntimeError('browser_isolation_source_catalog_changed')
    backend = resources / 'codex.exe'
    receipt = {'schema_version': 1, 'status': 'prepared', 'scope': 'disposable_verification_only',
        'resources': str(root), 'capability': capability, 'source_catalog_sha256': source_digest,
        'filtered_catalog_sha256': _digest(filtered_manifest),
        'excluded_plugins': sorted(set(names) & CHROME_PLUGINS),
        'preserved_plugins': [p['name'] for p in selected], 'files': entries,
        'backend': str(backend), 'backend_sha256': _digest(backend)}
    with _io_path(home / '.browser-isolation-used.json').open('x', encoding='utf8') as claim:
        json.dump({'run': str(run), 'resources': str(root)}, claim)
    _write(run / 'browser-resource-isolation.json', receipt)
    return {RESOURCE_OVERRIDE: str(root)}, receipt


def validate_resources(run):
    """Read back the prepared bytes after application exit before acceptance."""
    run = Path(run)
    receipt = json.loads(_io_path(run / 'browser-resource-isolation.json').read_text(encoding='utf8'))
    if receipt.get('status') == 'not_applicable':
        if receipt.get('reason') != 'legacy_without_bundled_chrome' or resource_capability(Path(receipt['resources'])) != receipt['capability']:
            raise RuntimeError('browser_isolation_legacy_capability_changed')
        return {'status': 'passed', 'mode': 'legacy_without_bundled_chrome',
                'shared_state_guard_required': True}
    root = run / 'browser-isolated-resources'
    if receipt.get('resources') != str(root) or receipt.get('status') != 'prepared':
        raise RuntimeError('browser_isolation_resource_receipt_mismatch')
    _plain(root)
    expected = set()
    for entry in receipt['files']:
        path = Path(entry['copy'])
        if not path.is_relative_to(root) or '..' in path.parts:
            raise RuntimeError('browser_isolation_prepared_path_escape')
        for ancestor in path.parents:
            if ancestor == root.parent:
                break
            _plain(ancestor)
        if _digest(path) != entry['sha256']:
            raise RuntimeError('browser_isolation_prepared_bytes_changed')
        expected.add(path)
    manifest = root / 'plugins/openai-bundled/.agents/plugins/marketplace.json'
    if _digest(manifest) != receipt['filtered_catalog_sha256']:
        raise RuntimeError('browser_isolation_filtered_catalog_changed')
    expected.add(manifest)
    actual = _resource_files(root)
    if actual != expected or _digest(Path(receipt['backend'])) != receipt['backend_sha256']:
        raise RuntimeError('browser_isolation_resource_inventory_changed')
    return {'status': 'passed', 'preserved_plugins': receipt['preserved_plugins'],
            'excluded_plugins': receipt['excluded_plugins'], 'copied_files': len(receipt['files']),
            'backend_unchanged': True, 'prepared_bytes_unchanged': True}


def _registry_snapshot():
    import winreg
    result = {}
    for view, flag in (('32', winreg.KEY_WOW64_32KEY), ('64', winreg.KEY_WOW64_64KEY)):
        for name in NATIVE_NAMES:
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_ROOT + '\\' + name,
                                    0, winreg.KEY_READ | flag) as key:
                    values = []
                    for index in range(winreg.QueryInfoKey(key)[1]):
                        label, value, kind = winreg.EnumValue(key, index)
                        if isinstance(value, bytes):
                            value = {'sha256': hashlib.sha256(value).hexdigest()}
                        values.append([label, value, kind])
                    result[view + ':' + name] = sorted(values, key=lambda item: item[0])
            except FileNotFoundError:
                result[view + ':' + name] = None
    return result


def shared_paths(registry):
    profile = Path(os.environ['USERPROFILE'])
    paths = {Path(os.environ['LOCALAPPDATA']) / 'OpenAI/Codex/chrome-native-hosts-v2.json'}
    paths.update(profile / 'AppData/Local/OpenAI/extension' / (name + '.json') for name in NATIVE_NAMES)
    for values in registry.values():
        for label, value, kind in values or []:
            if label == '':
                if not isinstance(value, str) or not Path(value).is_absolute() or value.startswith('\\\\') or Path(value).name not in {name + '.json' for name in NATIVE_NAMES}:
                    raise RuntimeError('browser_isolation_unknown_native_manifest_path')
                paths.add(Path(value))
    return sorted(paths, key=str)


def shared_snapshot(paths=None):
    if os.name != 'nt':
        raise RuntimeError('browser_isolation_monitor_requires_windows')
    registry = _registry_snapshot()
    paths = shared_paths(registry) if paths is None else paths
    files = {}
    for path in paths:
        try:
            info = _plain(path)
        except FileNotFoundError:
            files[str(path)] = None
            continue
        if info.st_size > 16 * 1024 * 1024:
            raise RuntimeError('browser_isolation_shared_file_too_large')
        files[str(path)] = {'identity': _identity(info), 'sha256': _digest(path)}
    return {'registry': registry, 'files': files}


class RegistryNotifications:
    """Read-only native events catch a registry write followed by restoration."""
    def __init__(self):
        import winreg
        self.keys, self.events = [], []
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        self.advapi = ctypes.WinDLL('advapi32', use_last_error=True)
        self.kernel.CreateEventW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.BOOL, wintypes.LPCWSTR]
        self.kernel.CreateEventW.restype = wintypes.HANDLE
        self.kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        self.advapi.RegNotifyChangeKeyValue.argtypes = [wintypes.HANDLE, wintypes.BOOL, wintypes.DWORD, wintypes.HANDLE, wintypes.BOOL]
        try:
            for flag in (winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY):
                parts = REGISTRY_ROOT.split('\\')
                while parts:
                    try:
                        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, '\\'.join(parts), 0,
                                             winreg.KEY_NOTIFY | winreg.KEY_READ | flag)
                        break
                    except FileNotFoundError:
                        parts.pop()
                else:
                    raise RuntimeError('browser_isolation_registry_watch_root_missing')
                self.keys.append(key)
                event = self.kernel.CreateEventW(None, True, False, None)
                if not event:
                    raise ctypes.WinError(ctypes.get_last_error())
                self.events.append(event)
                # THREAD_AGNOSTIC prevents an issuing thread's exit being
                # mistaken for a registry mutation.
                error = self.advapi.RegNotifyChangeKeyValue(int(key), True, 0x10000000 | 0x1 | 0x4, event, True)
                if error:
                    raise OSError(error, 'browser_isolation_registry_watch_failed')
        except BaseException:
            self.close()
            raise

    def check(self):
        for event in self.events:
            result = self.kernel.WaitForSingleObject(event, 0)
            if result == 0:
                raise RuntimeError('browser_isolation_shared_registry_changed')
            if result != 258:
                raise RuntimeError('browser_isolation_registry_watch_failed')

    def close(self):
        for key in self.keys:
            key.Close()
        self.keys.clear()
        for event in self.events:
            self.kernel.CloseHandle(event)
        self.events.clear()


class SharedBrowserGuard:
    """Observe shared state outside the owned job; an error is never repaired."""
    def __init__(self, receipt, *, snapshot=shared_snapshot, notifications=RegistryNotifications, interval=.1):
        self.receipt = Path(receipt)
        self.snapshot, self.notification_factory, self.interval = snapshot, notifications, interval
        self.stop = threading.Event()
        self.failure = None
        self.thread = self.notifications = None
        self.samples = 0
        self.baseline = None
        self.closed = False
        self.result = None

    def start(self):
        if self.thread is not None:
            raise RuntimeError('browser_isolation_guard_already_started')
        self.notifications = self.notification_factory()
        try:
            self.baseline = self.snapshot()
            self.notifications.check()
            _write(self.receipt, {'status': 'observing', 'baseline': self.baseline,
                                 'automatic_restore': False})
            self.thread = threading.Thread(target=self._observe, daemon=True,
                                           name='shared-browser-readonly-monitor')
            self.thread.start()
            return self
        except BaseException:
            self.notifications.close()
            raise

    def _sample(self):
        self.notifications.check()
        if self.snapshot() != self.baseline:
            raise RuntimeError('browser_isolation_shared_browser_state_changed')
        self.notifications.check()
        self.samples += 1

    def _observe(self):
        while not self.stop.wait(self.interval):
            try:
                self._sample()
            except BaseException as error:
                self.failure = str(error)
                _write(self.receipt, {'status': 'failed', 'reason': self.failure,
                    'samples': self.samples, 'automatic_restore': False})
                return

    def check(self):
        if self.failure:
            raise RuntimeError(self.failure)
        if self.thread is None or not self.thread.is_alive():
            raise RuntimeError('browser_isolation_monitor_not_running')

    def close(self):
        if self.closed:
            if self.failure:
                raise RuntimeError(self.failure)
            return self.result
        self.stop.set()
        if self.thread is not None:
            self.thread.join(timeout=10)
            if self.thread.is_alive():
                self.failure = 'browser_isolation_monitor_failed_to_stop'
        try:
            if self.failure:
                raise RuntimeError(self.failure)
            if self.baseline is None:
                raise RuntimeError('browser_isolation_monitor_not_started')
            self._sample()
            result = {'status': 'passed', 'samples': self.samples, 'registry_views': ['32', '64'],
                'before_during_after_unchanged': True, 'automatic_restore': False,
                'baseline': self.baseline}
            _write(self.receipt, result)
            self.result = result
            return result
        except BaseException as error:
            self.failure = str(error)
            _write(self.receipt, {'status': 'failed', 'reason': str(error),
                                 'samples': self.samples, 'automatic_restore': False})
            raise
        finally:
            self.closed = True
            if self.notifications:
                self.notifications.close()
                self.notifications = None
