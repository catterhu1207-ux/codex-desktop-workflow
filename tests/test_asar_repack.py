import hashlib
import copy
import json
from pathlib import Path
import shutil
import struct
import tempfile
import unittest

from codex_desktop_workflow import asar_repack


def digest(value):
    return hashlib.sha256(value).hexdigest()


def fixture(path):
    def file(offset, value):
        return {'size': len(value), 'offset': str(offset), 'integrity': {
            'algorithm': 'SHA256', 'hash': digest(value), 'blockSize': 2,
            'blocks': [digest(value[i:i + 2]) for i in range(0, len(value), 2)]}}
    header = {'files': {'a.js': file(0, b'old'), 'empty': file(3, b''),
                        'nested': {'files': {'b.json': file(5, b'keep')}},
                        'external.node': {'size': 7, 'unpacked': True}, 'alias': {'link': 'a.js'}}}
    raw = json.dumps(header, separators=(',', ':')).encode()
    padding = (-len(raw)) % 4
    size = 8 + len(raw) + padding
    value = struct.pack('<4I', 4, size, size - 4, len(raw)) + raw + b'\0' * padding + b'old!!keepTAIL'
    path.write_bytes(value)
    return value


def read(path):
    value = path.read_bytes()
    magic, size, pickle, length = struct.unpack_from('<4I', value)
    assert magic == 4 and pickle == size - 4
    return json.loads(value[16:16 + length]), value[8 + size:]


class AsarRepack(unittest.TestCase):
    def test_official_style_deduplicated_ranges_are_preserved_and_guarded(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.asar'
            fixture(source)
            header, body = read(source)
            header['files']['duplicate.js'] = copy.deepcopy(header['files']['a.js'])
            raw = json.dumps(header, separators=(',', ':')).encode()
            padding = (-len(raw)) % 4
            size = 8 + len(raw) + padding
            value = struct.pack('<4I', 4, size, size - 4, len(raw)) + raw + b'\0' * padding + body
            source.write_bytes(value)
            with self.assertRaisesRegex(ValueError, 'shared_payload_replacement_ambiguous'):
                asar_repack.plan(source, {'a.js': b'larger'}, digest(value))
            expected, prepared = asar_repack.expected_sha256(
                source, {'a.js': b'larger', 'duplicate.js': b'larger'}, digest(value))
            self.assertEqual(prepared['header']['files']['a.js'], prepared['header']['files']['duplicate.js'])
            target = Path(directory) / 'target.asar'
            shutil.copyfile(source, target)
            asar_repack.rebuild(source, target, {'a.js': b'larger', 'duplicate.js': b'larger'}, digest(value), expected)
            result, actual_body = read(target)
            self.assertEqual(actual_body, b'larger!!keepTAIL')
            self.assertEqual(result['files']['a.js']['size'], 6)
            header['files']['duplicate.js']['integrity']['hash'] = '0' * 64
            raw = json.dumps(header, separators=(',', ':')).encode()
            source.write_bytes(struct.pack('<4I', 4, size, size - 4, len(raw)) + raw + b'\0' * padding + body)
            with self.assertRaisesRegex(ValueError, 'alias_integrity_differs'):
                asar_repack.plan(source, {'nested/b.json': b'larger'}, digest(source.read_bytes()))

    def test_grow_shrink_gap_tail_and_unpacked_entries_preserve_source(self):
        for replacement in (b'a substantially longer module', b'x', b''):
            with self.subTest(size=len(replacement)), tempfile.TemporaryDirectory() as directory:
                source, target = Path(directory) / 'source.asar', Path(directory) / 'target.asar'
                original = fixture(source)
                shutil.copyfile(source, target)
                expected, _ = asar_repack.expected_sha256(source, {'a.js': replacement}, digest(original))
                result = asar_repack.rebuild(source, target, {'a.js': replacement}, digest(original), expected)
                header, body = read(target)
                first = header['files']['a.js']
                kept = header['files']['nested']['files']['b.json']
                self.assertEqual(body[int(first['offset']):int(first['offset']) + first['size']], replacement)
                self.assertEqual(body[int(kept['offset']):int(kept['offset']) + kept['size']], b'keep')
                self.assertEqual(body, replacement + b'!!keepTAIL')
                self.assertEqual(first['integrity']['hash'], digest(replacement))
                self.assertEqual(header['files']['external.node'], {'size': 7, 'unpacked': True})
                self.assertEqual(header['files']['alias'], {'link': 'a.js'})
                self.assertEqual(source.read_bytes(), original)
                self.assertEqual(digest(target.read_bytes()), expected)
                self.assertTrue(result['source_unchanged'])

    def test_wrong_source_or_target_identity_never_replaces_staged_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            source, target = Path(directory) / 'source.asar', Path(directory) / 'target.asar'
            original = fixture(source)
            shutil.copyfile(source, target)
            for source_hash, target_hash in [('0' * 64, '0' * 64), (digest(original), '0' * 64)]:
                with self.subTest(source_hash=source_hash), self.assertRaises(ValueError):
                    asar_repack.rebuild(source, target, {'a.js': b'new'}, source_hash, target_hash)
                self.assertEqual(target.read_bytes(), original)
                self.assertEqual(source.read_bytes(), original)

    def test_unknown_external_and_shared_source_targets_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.asar'
            original = fixture(source)
            for name in ('missing.js', 'external.node', 'alias'):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    asar_repack.plan(source, {name: b'new'}, digest(original))
            expected, _ = asar_repack.expected_sha256(source, {'a.js': b'new'}, digest(original))
            with self.assertRaisesRegex(ValueError, 'independent_official_copy'):
                asar_repack.rebuild(source, source, {'a.js': b'new'}, digest(original), expected)

    def test_overlapping_payload_ranges_stop_before_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.asar'
            fixture(source)
            header, body = read(source)
            header['files']['nested']['files']['b.json']['offset'] = '1'
            raw = json.dumps(header, separators=(',', ':')).encode()
            padding = (-len(raw)) % 4
            size = 8 + len(raw) + padding
            value = struct.pack('<4I', 4, size, size - 4, len(raw)) + raw + b'\0' * padding + body
            source.write_bytes(value)
            with self.assertRaisesRegex(ValueError, 'overlap'):
                asar_repack.plan(source, {'a.js': b'new'}, digest(value))


if __name__ == '__main__':
    unittest.main()
