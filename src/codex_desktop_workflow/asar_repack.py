"""Stream a source-bound ASAR rebuild when reviewed entries change length."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import uuid


def _sha(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def _entries(header: dict, prefix: str = ''):
    files = header.get('files')
    if not isinstance(files, dict):
        raise ValueError('asar_directory_inventory_invalid')
    for name, entry in files.items():
        if not isinstance(name, str) or name in ('', '.', '..') or '/' in name or '\\' in name:
            raise ValueError('asar_entry_name_invalid')
        if not isinstance(entry, dict):
            raise ValueError('asar_entry_metadata_invalid')
        path = prefix + name
        if 'files' in entry:
            yield from _entries(entry, path + '/')
        else:
            yield path, entry


def _load(source: Path):
    with source.open('rb') as stream:
        prefix = stream.read(16)
        if len(prefix) != 16:
            raise ValueError('asar_header_truncated')
        size_field, header_size, pickle_size, json_size = struct.unpack('<4I', prefix)
        if (size_field != 4 or header_size < 8 or pickle_size != header_size - 4
                or not 2 <= json_size <= 8 * 1024**2 or json_size > header_size - 8):
            raise ValueError('asar_header_bounds_invalid')
        raw = stream.read(json_size)
        if len(raw) != json_size:
            raise ValueError('asar_header_truncated')
        header = json.loads(raw)
        stream.seek(0)
        serialized = stream.read(8 + header_size)
        if len(serialized) != 8 + header_size:
            raise ValueError('asar_header_truncated')
    return header, 8 + header_size


def plan(source: Path, replacements: dict[str, bytes], expected_source_sha256: str) -> dict:
    """Return deterministic metadata and ranges, without writing any file."""
    source = Path(source).resolve(strict=True)
    if not re.fullmatch('[0-9a-f]{64}', expected_source_sha256) or _sha(source) != expected_source_sha256:
        raise ValueError('asar_source_identity_mismatch')
    header, body_start = _load(source)
    changed = copy.deepcopy(header)
    original = dict(_entries(header))
    target = dict(_entries(changed))
    if not replacements or not set(replacements) <= original.keys():
        raise ValueError('asar_replacement_inventory_invalid')
    if any(not isinstance(value, bytes) or len(value) > 64 * 1024**2 for value in replacements.values()):
        raise ValueError('asar_replacement_bytes_invalid')
    stored = []
    data_size = source.stat().st_size - body_start
    for path, entry in original.items():
        if 'offset' not in entry:
            if path in replacements:
                raise ValueError('asar_unstored_entry_cannot_be_replaced')
            continue
        value, size = entry['offset'], entry.get('size')
        if (not isinstance(value, str) or not value.isdecimal() or type(size) is not int or size < 0
                or int(value) + size > data_size or entry.get('unpacked') or 'link' in entry):
            raise ValueError('asar_stored_range_invalid')
        stored.append((int(value), size, path))
    # Electron ASAR can deduplicate identical payloads: several inventory names
    # then share exactly one range. Preserve these aliases rather than copying
    # the shared bytes repeatedly or rejecting a valid official package.
    groups = {}
    for offset, size, path in stored:
        groups.setdefault((offset, size), []).append(path)
    ranges = []
    cursor = 0
    output_size = 0
    for (offset, size), names in sorted(groups.items(), key=lambda row: (row[0][0], row[0][1] != 0, row[1][0])):
        path = names[0]
        if size and offset < cursor:
            raise ValueError('asar_stored_ranges_overlap')
        if len(names) > 1:
            integrity = original[path].get('integrity')
            if not integrity or any(original[name].get('integrity') != integrity for name in names):
                raise ValueError('asar_alias_integrity_differs')
            changed_names = [name for name in names if name in replacements]
            if changed_names and (len(changed_names) != len(names)
                    or any(replacements[name] != replacements[path] for name in names)):
                raise ValueError('asar_shared_payload_replacement_ambiguous')
        if offset > cursor:
            ranges.append(('copy', cursor, offset - cursor))
            output_size += offset - cursor
            cursor = offset
        entry = target[path]
        for name in names:
            target[name]['offset'] = str(output_size)
        if path in replacements:
            payload = replacements[path]
            integrity = entry.get('integrity')
            if (not isinstance(integrity, dict) or integrity.get('algorithm') != 'SHA256'
                    or type(integrity.get('blockSize')) is not int or not 1 <= integrity['blockSize'] <= 16 * 1024**2):
                raise ValueError('asar_entry_integrity_invalid')
            block = integrity['blockSize']
            integrity['hash'] = hashlib.sha256(payload).hexdigest()
            integrity['blocks'] = [hashlib.sha256(payload[i:i + block]).hexdigest()
                                   for i in range(0, len(payload), block)]
            entry['size'] = len(payload)
            for name in names[1:]:
                target[name]['size'] = len(payload)
                target[name]['integrity'] = copy.deepcopy(integrity)
            ranges.append(('replacement', path, len(payload)))
            output_size += len(payload)
        elif size:
            ranges.append(('copy', offset, size))
            output_size += size
        cursor = max(cursor, offset + size)
    if cursor < data_size:
        ranges.append(('copy', cursor, data_size - cursor))
        output_size += data_size - cursor
    raw = json.dumps(changed, ensure_ascii=False, separators=(',', ':')).encode('utf8')
    padding = (-len(raw)) % 4
    header_size = 8 + len(raw) + padding
    serialized = struct.pack('<4I', 4, header_size, header_size - 4, len(raw)) + raw + b'\0' * padding
    return {'header': changed, 'serialized_header': serialized, 'source_body_start': body_start,
            'ranges': ranges, 'size': len(serialized) + output_size,
            'source_sha256': expected_source_sha256, 'header_json_sha256': hashlib.sha256(raw).hexdigest()}


def _chunks(source, prepared, replacements):
    yield prepared['serialized_header']
    with Path(source).open('rb') as stream:
        for kind, start, size in prepared['ranges']:
            if kind == 'replacement':
                yield replacements[start]
                continue
            stream.seek(prepared['source_body_start'] + start)
            remaining = size
            while remaining:
                value = stream.read(min(4 * 1024**2, remaining))
                if not value:
                    raise ValueError('asar_source_payload_truncated')
                remaining -= len(value)
                yield value


def expected_sha256(source: Path, replacements: dict[str, bytes], expected_source_sha256: str) -> tuple[str, dict]:
    prepared = plan(source, replacements, expected_source_sha256)
    h = hashlib.sha256()
    for value in _chunks(source, prepared, replacements):
        h.update(value)
    return h.hexdigest(), prepared


def rebuild(source: Path, target: Path, replacements: dict[str, bytes], expected_source_sha256: str,
            expected_target_sha256: str) -> dict:
    source, target = Path(source).resolve(strict=True), Path(target).resolve(strict=True)
    if source.samefile(target) or target.is_symlink() or _sha(target) != expected_source_sha256:
        raise ValueError('asar_staged_target_not_an_independent_official_copy')
    digest, prepared = expected_sha256(source, replacements, expected_source_sha256)
    if digest != expected_target_sha256:
        raise ValueError('asar_rebuild_plan_identity_mismatch')
    before = source.stat()
    temporary = target.with_name(target.name + '.repack-' + uuid.uuid4().hex)
    with temporary.open('xb') as stream:
        for value in _chunks(source, prepared, replacements):
            stream.write(value)
        stream.flush()
        os.fsync(stream.fileno())
    if temporary.stat().st_size != prepared['size'] or _sha(temporary) != expected_target_sha256:
        raise ValueError('asar_rebuilt_file_readback_mismatch')
    after = source.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns) or _sha(source) != expected_source_sha256:
        raise ValueError('asar_source_changed_during_rebuild')
    os.replace(temporary, target)
    return {'status': 'source_bound_rebuild_passed', 'target_sha256': digest, 'bytes': prepared['size'],
            'header_json_sha256': prepared['header_json_sha256'], 'source_unchanged': True,
            'modified_entries': {name: hashlib.sha256(value).hexdigest() for name, value in replacements.items()}}
