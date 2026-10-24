"""Exact, source-gated 26.1021.3705.0 partial build contract.

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

VERSION = "26.1021.3705.0"
PACKAGE_FULL_NAME = "OpenAI.Codex_26.1021.3705.0_x64__2p2nqsd0c76g0"
SOURCE_ASAR_SHA256 = '04862a659c6a90fc50514d8c0b8016709d97dece58839726c57495ed72f1d9f0'
SOURCE_EXE_SHA256 = 'c5a6ea0f6d99d696e9976c0ecefb6b8410a7dd5b17d96fb69a72c83a8192b649'
TARGET_ASAR_SHA256 = '148fc5ffcaec60511fff6f214fb93de49798efeebc1172e9ab2913451b7d2db2'
TARGET_EXE_SHA256 = '53922ba458912716d91e2041c208d0cfdf93c3ba14f280aee888670642ca81ee'
DATA = Path(__file__).parent / "codex_desktop_workflow/data"
DELTA = DATA / "desktop-261021-3705.delta.bin"
MANIFEST = DATA / "desktop-261021-3705.delta.json"


def _sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _decode(source: bytes, encoded: bytes, expected_length: int) -> bytes:
    stream = io.BytesIO(zlib.decompress(encoded))
    if stream.read(9) != b"CF9DELTA1":
        raise ValueError("3705 delta magic differs")
    count = struct.unpack("<I", stream.read(4))[0]
    if count > 10000:
        raise ValueError("3705 delta operation count exceeds bound")
    output = io.BytesIO()
    for _ in range(count):
        kind, length = struct.unpack("<BQ", stream.read(9))
        if length > expected_length:
            raise ValueError("3705 delta operation length exceeds bound")
        if kind == 0:
            offset = struct.unpack("<Q", stream.read(8))[0]
            if offset + length > len(source):
                raise ValueError("3705 delta copy escapes source")
            output.write(source[offset:offset + length])
        elif kind == 1:
            inserted = stream.read(length)
            if len(inserted) != length:
                raise ValueError("3705 delta insert truncated")
            output.write(inserted)
        else:
            raise ValueError("3705 delta operation invalid")
        if output.tell() > expected_length:
            raise ValueError("3705 delta output exceeds source length")
    if stream.read(1) or output.tell() != expected_length:
        raise ValueError("3705 delta output length differs")
    return output.getvalue()


def _prepared_entries(source_asar: Path, builder) -> tuple[int, dict, dict[str, bytes]]:
    if _sha(source_asar) != SOURCE_ASAR_SHA256:
        raise ValueError("3705 official ASAR identity differs")
    manifest_bytes, delta_bytes = MANIFEST.read_bytes(), DELTA.read_bytes()
    manifest = json.loads(manifest_bytes)
    if (manifest.get("official_asar_sha256") != SOURCE_ASAR_SHA256
            or manifest.get("candidate_asar_sha256") != TARGET_ASAR_SHA256
            or hashlib.sha256(delta_bytes).hexdigest() != manifest.get("delta_package_sha256")
            or len(delta_bytes) != manifest.get("delta_package_bytes")
            or len(manifest.get("entries", [])) != 5):
        raise ValueError("3705 delta manifest identity differs")
    source_size, _, header = builder.read_asar(source_asar)
    stream = io.BytesIO(delta_bytes)
    if stream.read(8) != b"CF9PACK1":
        raise ValueError("3705 delta package magic differs")
    prepared = {}
    for record in manifest["entries"]:
        name = record["path"]
        part_len = struct.unpack("<I", stream.read(4))[0]
        part = stream.read(part_len)
        if len(part) != part_len or hashlib.sha256(part).hexdigest() != record["delta_sha256"]:
            raise ValueError("3705 delta part identity differs: " + name)
        old = builder.read_entry(source_asar, source_size, builder.get_entry_meta(header, name))[1]
        if (len(old) != record["source_bytes"] or
                hashlib.sha256(old).hexdigest() != record["source_sha256"]):
            raise ValueError("3705 source entry identity differs: " + name)
        new = _decode(old, part, record["target_bytes"])
        if hashlib.sha256(new).hexdigest() != record["target_sha256"]:
            raise ValueError("3705 target entry identity differs: " + name)
        prepared[name] = new
    if stream.read(1):
        raise ValueError("3705 delta package has trailing data")
    return source_size, header, prepared


def build_partial(source_root: Path, target_root: Path) -> dict:
    """Patch a previously staged exact official ASAR/EXE; never copy the app."""
    import hotfix_builder as builder

    source_root, target_root = source_root.resolve(strict=True), target_root.resolve(strict=True)
    source_asar, target_asar = source_root / "app.asar", target_root / "resources/app.asar"
    source_exe, target_exe = source_root / "ChatGPT.exe", target_root / "ChatGPT.exe"
    if (_sha(source_exe) != SOURCE_EXE_SHA256 or _sha(target_asar) != SOURCE_ASAR_SHA256
            or _sha(target_exe) != SOURCE_EXE_SHA256):
        raise ValueError("3705 staged official source identity differs")
    from codex_desktop_workflow.asar_repack import rebuild
    _, _, prepared = _prepared_entries(source_asar, builder)
    original_header_hash = builder.asar_header_json_sha256(source_asar)
    rebuild(source_asar, target_asar, prepared, SOURCE_ASAR_SHA256, TARGET_ASAR_SHA256)
    identity = {"executable_source_sha256": SOURCE_EXE_SHA256,
                "embedded_asar_header_source_sha256": original_header_hash}
    builder.synchronize_executable_asar_integrity(
        source_root, target_root, source_asar, target_asar, identity)
    verification = builder.verify_executable_asar_integrity(
        source_root, target_root, source_asar, target_asar, identity)
    if (verification is None or _sha(target_asar) != TARGET_ASAR_SHA256
            or _sha(target_exe) != TARGET_EXE_SHA256):
        raise ValueError("3705 exact partial build verification differs")
    return {"status": "exact_partial_build_passed", "version": VERSION,
            "official_asar_sha256": SOURCE_ASAR_SHA256,
            "candidate_asar_sha256": TARGET_ASAR_SHA256,
            "candidate_executable_sha256": TARGET_EXE_SHA256,
            "modified_entries": {name: hashlib.sha256(data).hexdigest() for name, data in prepared.items()},
            "complete_feature_qualification": False}
