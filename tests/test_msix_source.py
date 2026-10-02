import hashlib
import importlib.util
import json
import shutil
import struct
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

spec = importlib.util.spec_from_file_location('msix_source', Path(__file__).parents[1] / 'msix_source.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class MsixSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'official.msix'
        self.manifest = f'<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"><Identity Name="OpenAI.Codex" Publisher="{module.PUBLISHER}" ProcessorArchitecture="x64" Version="26.928.4866.0"/></Package>'
        self.entries = {'AppxManifest.xml': self.manifest.encode(), 'AppxSignature.p7x': b'synthetic signature',
                        'app/resources/app.asar': b'synthetic asar', 'app/resources/codex.exe': b'synthetic backend', 'app/ChatGPT.exe': b'synthetic app'}
        self.contracts = {'26.928.4866.0': {'asar_sha256': hashlib.sha256(self.entries[module.CORE[0]]).hexdigest(), 'backend_sha256': hashlib.sha256(self.entries[module.CORE[1]]).hexdigest()}}
        self.signer = patch.object(module, 'signature', return_value={'status': 'Valid', 'subject': module.PUBLISHER})
        self.signer.start()
        self.addCleanup(self.signer.stop)

    def write(self, entries=None):
        with zipfile.ZipFile(self.source, 'w') as archive:
            for name, value in (entries or self.entries).items():
                info = zipfile.ZipInfo('placeholder')
                info.filename = name
                info.orig_filename = name
                archive.writestr(info, value)

    def test_known_inspection_does_not_extract(self):
        self.write()
        report = module.inspect(self.source, self.contracts)
        self.assertTrue(report['qualified_version'])
        self.assertFalse(report['installed'])
        self.assertNotIn('source_app', report)
        self.assertEqual(list(self.root.iterdir()), [self.source])

    def test_unknown_can_only_be_inspected(self):
        self.write()
        report = module.inspect(self.source, {})
        self.assertFalse(report['qualified_version'])
        with self.assertRaises(module.SourceError):
            module.extract(self.source, self.root / 'cache', report)
        self.assertFalse((self.root / 'cache').exists())

    def test_hash_mismatch_rejected(self):
        self.write()
        self.contracts['26.928.4866.0']['asar_sha256'] = '0' * 64
        with self.assertRaises(module.SourceError):
            module.inspect(self.source, self.contracts)

    def test_identity_architecture_and_bootstrap_rejected(self):
        for manifest in [self.manifest.replace('OpenAI.Codex', 'Other.App'), self.manifest.replace('x64', 'arm64')]:
            self.write(dict(self.entries, **{'AppxManifest.xml': manifest.encode()}))
            with self.assertRaises(module.SourceError):
                module.inspect(self.source, self.contracts)
        entries = dict(self.entries)
        del entries[module.CORE[0]]
        self.write(entries)
        with self.assertRaises(module.SourceError):
            module.inspect(self.source, self.contracts)

    def test_signature_failure_rejected(self):
        self.write()
        with patch.object(module, 'signature', side_effect=module.SourceError('invalid signature')):
            with self.assertRaises(module.SourceError):
                module.inspect(self.source, self.contracts)

    def test_unsafe_paths_and_case_conflicts_rejected(self):
        for name in ['../escape', '/absolute', 'app/../escape', 'app\\escape', 'app/con.txt', 'app/resources/App.asar', 'app/Resources/new.bin']:
            self.write(dict(self.entries, **{name: b'bad'}))
            with self.assertRaises(module.SourceError, msg=name):
                module.inspect(self.source, self.contracts)

    def test_source_change_before_extraction_rejected(self):
        self.write()
        report = module.inspect(self.source, self.contracts)
        self.source.write_bytes(b'changed')
        with self.assertRaises(module.SourceError):
            module.extract(self.source, self.root / 'cache', report)
        self.assertFalse((self.root / 'cache').exists())

    def valid_executables(self):
        header = bytearray(70)
        header[:2] = b'MZ'
        struct.pack_into('<I', header, 0x3c, 64)
        header[64:70] = b'PE\0\0\x64\x86'
        self.entries['app/ChatGPT.exe'] = bytes(header)
        self.entries['app/resources/codex.exe'] = bytes(header)
        self.contracts['26.928.4866.0']['backend_sha256'] = hashlib.sha256(header).hexdigest()

    def test_complete_extraction_and_automatic_reuse(self):
        self.valid_executables()
        long_name = 'app/' + '/'.join(['long_component' * 3] * 7) + '/retained.txt'
        self.entries[long_name] = b'long path preserved'
        self.write()
        report = module.inspect(self.source, self.contracts)
        cache = self.root / 'cache'
        first = module.extract(self.source, cache, report)
        root = Path(first['source_app']).parent
        retained = module.io_path(root / long_name)
        identity = retained.stat().st_mtime_ns
        second = module.extract(self.source, cache, report)
        self.assertEqual(first['source_app'], second['source_app'])
        self.assertEqual(first['files_readback'], second['files_readback'])
        self.assertEqual(identity, retained.stat().st_mtime_ns)
        self.assertEqual(len(list(cache.iterdir())), 1)
        # This test owns this fresh synthetic cache; use the same long-path API.
        self.assertEqual(root.parent, self.root / 'cache')
        shutil.rmtree(module.io_path(root))

    def test_changed_cache_is_rejected_without_overwrite(self):
        self.valid_executables()
        self.write()
        report = module.inspect(self.source, self.contracts)
        cache = self.root / 'cache'
        result = module.extract(self.source, cache, report)
        retained = Path(result['source_app']) / 'resources' / 'app.asar'
        retained.write_bytes(b'changed retained evidence')
        with self.assertRaises(module.SourceError):
            module.extract(self.source, cache, report)
        self.assertEqual(retained.read_bytes(), b'changed retained evidence')

    def test_unexpected_cache_file_and_ambiguous_attempts_rejected(self):
        self.valid_executables()
        self.write()
        report = module.inspect(self.source, self.contracts)
        cache = self.root / 'cache'
        result = module.extract(self.source, cache, report)
        root = Path(result['source_app']).parent
        (root / 'unqualified.bin').write_bytes(b'preserve')
        with self.assertRaises(module.SourceError):
            module.extract(self.source, cache, report)
        second = cache / (root.name[:-32] + 'b' * 32)
        second.mkdir()
        (second / 'extraction-failed.json').write_text('{}')
        with self.assertRaises(module.SourceError):
            module.extract(self.source, cache, report)

    def test_invalid_executable_blocks_source_return(self):
        self.write()
        report = module.inspect(self.source, self.contracts)
        with self.assertRaises(module.SourceError):
            module.extract(self.source, self.root / 'cache', report)
        self.assertFalse(list((self.root / 'cache').glob('*/source-verification.json')))

    def test_link_archive_and_resume_outside_cache_rejected(self):
        self.write()
        with zipfile.ZipFile(self.source, 'a') as archive:
            link = zipfile.ZipInfo('app/redirect')
            link.create_system = 3
            link.external_attr = (0o120777 << 16)
            archive.writestr(link, '../outside')
        with self.assertRaises(module.SourceError):
            module.inspect(self.source, self.contracts)
        self.write()
        report = module.inspect(self.source, self.contracts)
        with self.assertRaises(module.SourceError):
            module.extract(self.source, self.root / 'cache', report, resume=self.root)


if __name__ == '__main__':
    unittest.main()
