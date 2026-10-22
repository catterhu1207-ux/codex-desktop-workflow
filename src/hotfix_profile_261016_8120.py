"""Exact, source-gated 26.1016.8120.0 partial build contract.

This profile is intentionally not registered for daily launcher activation until
the complete frontend and genuine-launch gates have passed.
"""
from __future__ import annotations

import hashlib
import io
import json
import struct
import zlib
from pathlib import Path

VERSION = "26.1016.8120.0"
PACKAGE_FULL_NAME = "OpenAI.Codex_26.1016.8120.0_x64__2p2nqsd0c76g0"
SOURCE_ASAR_SHA256 = '760eae730e57438a0693cab4aba5ed8b7eb0ea1c5b7a7dc26dd0e84c2398810f'
SOURCE_EXE_SHA256 = '976b90e7e465bd8b4789989e7e145a9509102545b8033500d416595888f94642'
TARGET_ASAR_SHA256 = '835de958785c67c0e3547c96da441e8fa7407e9d5b7a243da13c1a62f95c1245'
TARGET_EXE_SHA256 = 'e896d33d19d350ec6affe15e299c31736a98bac61edf451b0fe929c10386e5c7'
DATA = Path(__file__).parent / "codex_desktop_workflow/data"
DELTA = DATA / "desktop-261016-8120.delta.bin"
MANIFEST = DATA / "desktop-261016-8120.delta.json"


def _sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _decode(source: bytes, encoded: bytes, expected_length: int) -> bytes:
    stream = io.BytesIO(zlib.decompress(encoded))
    if stream.read(9) != b"CF9DELTA1":
        raise ValueError("8120 delta magic differs")
    count = struct.unpack("<I", stream.read(4))[0]
    if count > 10000:
        raise ValueError("8120 delta operation count exceeds bound")
    output = io.BytesIO()
    for _ in range(count):
        kind, length = struct.unpack("<BQ", stream.read(9))
        if length > expected_length:
            raise ValueError("8120 delta operation length exceeds bound")
        if kind == 0:
            offset = struct.unpack("<Q", stream.read(8))[0]
            if offset + length > len(source):
                raise ValueError("8120 delta copy escapes source")
            output.write(source[offset:offset + length])
        elif kind == 1:
            inserted = stream.read(length)
            if len(inserted) != length:
                raise ValueError("8120 delta insert truncated")
            output.write(inserted)
        else:
            raise ValueError("8120 delta operation invalid")
        if output.tell() > expected_length:
            raise ValueError("8120 delta output exceeds source length")
    if stream.read(1) or output.tell() != expected_length:
        raise ValueError("8120 delta output length differs")
    return output.getvalue()


def _prepared_entries(source_asar: Path, builder) -> tuple[int, dict, dict[str, bytes]]:
    if _sha(source_asar) != SOURCE_ASAR_SHA256:
        raise ValueError("8120 official ASAR identity differs")
    manifest_bytes, delta_bytes = MANIFEST.read_bytes(), DELTA.read_bytes()
    manifest = json.loads(manifest_bytes)
    if (manifest.get("official_asar_sha256") != SOURCE_ASAR_SHA256
            or manifest.get("candidate_asar_sha256") != TARGET_ASAR_SHA256
            or hashlib.sha256(delta_bytes).hexdigest() != manifest.get("delta_package_sha256")
            or len(delta_bytes) != manifest.get("delta_package_bytes")
            or len(manifest.get("entries", [])) != 4):
        raise ValueError("8120 delta manifest identity differs")
    source_size, _, header = builder.read_asar(source_asar)
    stream = io.BytesIO(delta_bytes)
    if stream.read(8) != b"CF9PACK1":
        raise ValueError("8120 delta package magic differs")
    prepared = {}
    for record in manifest["entries"]:
        name = record["path"]
        part_len = struct.unpack("<I", stream.read(4))[0]
        part = stream.read(part_len)
        if len(part) != part_len or hashlib.sha256(part).hexdigest() != record["delta_sha256"]:
            raise ValueError("8120 delta part identity differs: " + name)
        old = builder.read_entry(source_asar, source_size, builder.get_entry_meta(header, name))[1]
        if (len(old) != record["source_bytes"] or
                hashlib.sha256(old).hexdigest() != record["source_sha256"]):
            raise ValueError("8120 source entry identity differs: " + name)
        new = _decode(old, part, len(old))
        if hashlib.sha256(new).hexdigest() != record["target_sha256"]:
            raise ValueError("8120 target entry identity differs: " + name)
        prepared[name] = new
    if stream.read(1):
        raise ValueError("8120 delta package has trailing data")
    return source_size, header, prepared


def build_partial(source_root: Path, target_root: Path) -> dict:
    """Patch a previously staged exact official ASAR/EXE; never copy the app."""
    import hotfix_builder as builder

    source_root, target_root = source_root.resolve(strict=True), target_root.resolve(strict=True)
    source_asar, target_asar = source_root / "app.asar", target_root / "resources/app.asar"
    source_exe, target_exe = source_root / "ChatGPT.exe", target_root / "ChatGPT.exe"
    if (_sha(source_exe) != SOURCE_EXE_SHA256 or _sha(target_asar) != SOURCE_ASAR_SHA256
            or _sha(target_exe) != SOURCE_EXE_SHA256):
        raise ValueError("8120 staged official source identity differs")
    source_size, header, prepared = _prepared_entries(source_asar, builder)
    _, serial, target_header = builder.read_asar(target_asar)
    original_header_bytes = serial[16:16 + struct.unpack_from("<I", serial, 12)[0]]
    if target_header != header or json.dumps(header, ensure_ascii=False, separators=(",", ":")).encode() != original_header_bytes:
        raise ValueError("8120 staged ASAR header differs")
    with target_asar.open("r+b") as output:
        for name, new in prepared.items():
            meta = builder.get_entry_meta(header, name)
            output.seek(8 + source_size + int(meta["offset"]))
            output.write(new)
            integrity = meta["integrity"]
            integrity["hash"] = hashlib.sha256(new).hexdigest()
            block_size = integrity["blockSize"]
            integrity["blocks"] = [hashlib.sha256(new[i:i + block_size]).hexdigest()
                                   for i in range(0, len(new), block_size)]
        patched_header = json.dumps(header, ensure_ascii=False, separators=(",", ":")).encode()
        if len(patched_header) != len(original_header_bytes):
            raise ValueError("8120 patched ASAR header length differs")
        output.seek(16)
        output.write(patched_header)
    identity = {"executable_source_sha256": SOURCE_EXE_SHA256,
                "embedded_asar_header_source_sha256": hashlib.sha256(original_header_bytes).hexdigest()}
    builder.synchronize_executable_asar_integrity(
        source_root, target_root, source_asar, target_asar, identity)
    verification = builder.verify_executable_asar_integrity(
        source_root, target_root, source_asar, target_asar, identity)
    if (verification is None or _sha(target_asar) != TARGET_ASAR_SHA256
            or _sha(target_exe) != TARGET_EXE_SHA256):
        raise ValueError("8120 exact partial build verification differs")
    return {"status": "exact_partial_build_passed", "version": VERSION,
            "official_asar_sha256": SOURCE_ASAR_SHA256,
            "candidate_asar_sha256": TARGET_ASAR_SHA256,
            "candidate_executable_sha256": TARGET_EXE_SHA256,
            "modified_entries": {name: hashlib.sha256(data).hexdigest() for name, data in prepared.items()},
            "complete_feature_qualification": False}
