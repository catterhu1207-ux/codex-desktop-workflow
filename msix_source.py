"""Verify and extract a full official MSIX without registering a Windows app.

The release bundle generates source_contracts from workflow.SUPPORTED_PACKAGES.
Unknown versions may be inspected but cannot be returned as build inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import struct
import subprocess
import time
import uuid
import xml.etree.ElementTree as ET
import zipfile

PUBLISHER = "CN=50BDFD77-8903-4850-9FFE-6E8522F64D5B"
CORE = ("app/resources/app.asar", "app/resources/codex.exe", "app/ChatGPT.exe")
GIB = 1024**3


class SourceError(RuntimeError):
    pass


def io_path(path: Path) -> Path:
    text = str(path.absolute())
    if os.name == 'nt' and not text.startswith('\\\\?\\'):
        text = '\\\\?\\UNC\\' + text[2:] if text.startswith('\\\\') else '\\\\?\\' + text
    return Path(text)


def stream_digest(handle) -> str:
    hashed = hashlib.sha256()
    for block in iter(lambda: handle.read(1024 * 1024), b''):
        hashed.update(block)
    return hashed.hexdigest()


def digest(path: Path) -> str:
    with io_path(path).open("rb") as handle:
        return stream_digest(handle)


def signature(path: Path, *, package: bool) -> dict:
    if os.name != "nt":
        raise SourceError("Authenticode verification requires Windows")
    environment = os.environ.copy()
    environment["CODEX_MSIX_VERIFY_PATH"] = str(path.absolute())
    command = "[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false); $ErrorActionPreference='Stop'; Import-Module (Join-Path $PSHOME 'Modules/Microsoft.PowerShell.Security/Microsoft.PowerShell.Security.psd1') -ErrorAction Stop; $s=Get-AuthenticodeSignature -LiteralPath $env:CODEX_MSIX_VERIFY_PATH; @{status=[string]$s.Status;subject=[string]$s.SignerCertificate.Subject}|ConvertTo-Json -Compress"
    cp = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
                        env=environment, capture_output=True, timeout=90,
                        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if cp.returncode:
        raise SourceError("Authenticode verification failed: " + cp.stderr.decode('utf8', errors='replace')[-1500:])
    result = json.loads(cp.stdout.decode('utf8').lstrip("\ufeff"))
    expected = result.get("subject") == PUBLISHER if package else result.get("subject", "").startswith('CN="OpenAI OpCo, LLC",')
    if result.get("status") != "Valid" or not expected:
        raise SourceError("The official signature or publisher does not match")
    return result


def plain_path(path: Path) -> Path:
    path = path.absolute()
    for part in [path, *path.parents]:
        try:
            info = io_path(part).lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise SourceError("A source or cache path contains a directory link")
    return path


def inventory(archive: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    entries = archive.infolist()
    if len(entries) > 100000 or sum(e.file_size for e in entries) > 12 * GIB:
        raise SourceError("The archive exceeds the full-package size limit")
    seen, prefixes = set(), {}
    devices = re.compile(r"^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)", re.I)
    for entry in entries:
        if entry.orig_filename != entry.filename:
            raise SourceError("Archive filename was silently normalized")
        name = entry.filename.rstrip("/") if entry.is_dir() else entry.filename
        parts = name.split("/")
        if not name or name.startswith("/") or "\\" in name or any(
                p in ("", ".", "..") or p[-1:] in (" ", ".") or
                re.search(r'[<>:"|?*\x00-\x1f]', p) or devices.match(p) for p in parts):
            raise SourceError("Unsafe Windows archive path")
        if PurePosixPath(name).is_absolute():
            raise SourceError("Absolute archive path")
        kind = stat.S_IFMT(entry.external_attr >> 16)
        if kind not in (0, stat.S_IFREG, stat.S_IFDIR) or entry.external_attr & 0x400:
            raise SourceError("Archive links and special files are not allowed")
        folded = name.casefold()
        if folded in seen:
            raise SourceError("Duplicate archive path")
        seen.add(folded)
        for length in range(1, len(parts) + 1):
            prefix = "/".join(parts[:length])
            key = prefix.casefold()
            directory = length < len(parts) or entry.is_dir()
            if key in prefixes and prefixes[key] != (prefix, directory):
                raise SourceError("Conflicting archive path or parent casing")
            prefixes[key] = (prefix, directory)
    return entries


def inspect(source: Path, contracts: dict) -> dict:
    source = plain_path(source)
    if source.suffix.lower() != ".msix" or not source.is_file():
        raise SourceError("Source must be a full .msix file")
    before = digest(source)
    signer = signature(source, package=True)
    with zipfile.ZipFile(source) as archive:
        entries = inventory(archive)
        names = {e.filename for e in entries}
        if not set(CORE + ("AppxManifest.xml", "AppxSignature.p7x")).issubset(names):
            raise SourceError("This file is not a full official application package")
        manifest = archive.getinfo("AppxManifest.xml")
        if manifest.file_size > 1024 * 1024:
            raise SourceError("Package manifest is too large")
        tree = ET.fromstring(archive.read(manifest))
        identity = tree.find("{http://schemas.microsoft.com/appx/manifest/foundation/windows10}Identity")
        if identity is None:
            raise SourceError("Package identity missing")
        identity = dict(identity.attrib)
        if identity.get("Name") != "OpenAI.Codex" or identity.get("Publisher") != PUBLISHER or identity.get("ProcessorArchitecture") != "x64":
            raise SourceError("Package product, publisher or architecture mismatch")
        version = identity.get("Version", "")
        if not re.fullmatch(r"\d+\.\d+\.\d+\.\d+", version):
            raise SourceError("Invalid package version")
        hashes = {}
        for name in CORE:
            with archive.open(name) as stream:
                hashes[name] = stream_digest(stream)
        contract = contracts.get(version)
        if contract and (hashes[CORE[0]] != contract["asar_sha256"] or hashes[CORE[1]] != contract["backend_sha256"]):
            raise SourceError("The package does not match its immutable version contract")
        report = {"identity": identity, "package_sha256": before, "signature": signer,
                  "files": hashes, "expanded_bytes": sum(e.file_size for e in entries),
                  "qualified_version": bool(contract), "installed": False}
    if digest(source) != before:
        raise SourceError("Source changed during verification")
    return report


def x64(path: Path) -> None:
    with io_path(path).open("rb") as stream:
        header = stream.read(64)
        if len(header) != 64 or header[:2] != b"MZ":
            raise SourceError("Invalid executable header")
        stream.seek(struct.unpack_from("<I", header, 0x3C)[0])
        pe = stream.read(6)
    if len(pe) != 6 or pe[:4] != b"PE\0\0" or struct.unpack_from("<H", pe, 4)[0] != 0x8664:
        raise SourceError("Executable is not x64")


def extract(source: Path, cache: Path, report: dict, *, resume: Path | None = None) -> dict:
    if not report["qualified_version"]:
        raise SourceError("This version can be inspected but has not been adapted; activation is blocked")
    source, cache = plain_path(source), plain_path(cache)
    if digest(source) != report["package_sha256"]:
        raise SourceError("Source changed before extraction")
    existing = next((p for p in [cache, *cache.parents] if p.exists()), None)
    prefix = report["identity"]["Version"] + "-" + report["package_sha256"][:16] + "-"
    if resume is None and cache.is_dir():
        retained = [p for p in cache.iterdir() if p.name.startswith(prefix) and
                    (io_path(p / 'source-verification.json').is_file() or io_path(p / 'extraction-failed.json').is_file())]
        if len(retained) > 1:
            raise SourceError("Multiple retained source attempts exist; select a separate cache root")
        if retained:
            resume = plain_path(retained[0])
    if existing is None or shutil.disk_usage(existing).free < (0 if resume else report["expanded_bytes"]) + 4 * GIB:
        raise SourceError("Insufficient space for extraction plus the 4 GiB cache reserve")
    cache.mkdir(parents=True, exist_ok=True)
    if resume:
        target = plain_path(resume)
        if target.parent != cache or not target.name.startswith(prefix) or not target.is_dir():
            raise SourceError("Resume target is not an owned source-cache attempt")
    else:
        target = cache / (prefix + uuid.uuid4().hex)
        target.mkdir()  # Every attempt owns a fresh directory. Nothing is overwritten.
    inventory_receipt = []
    last_check = 0.0
    try:
        with zipfile.ZipFile(source) as archive:
            entries = inventory(archive)
            if resume:
                allowed = {e.filename.rstrip('/') for e in entries}
                allowed.update({'source-verification.json', 'extraction-failed.json'})
                remaining = sum(e.file_size for e in entries if not e.is_dir() and not io_path(target / e.filename).exists())
                if shutil.disk_usage(cache).free < remaining + 4 * GIB:
                    raise SourceError("Insufficient space to finish the retained source attempt")
                for directory, dirs, files in os.walk(io_path(target), followlinks=False):
                    for name in dirs + files:
                        full = Path(directory) / name
                        plain_path(full)
                        if name in files and full.relative_to(io_path(target)).as_posix() not in allowed:
                            raise SourceError("Retained source cache contains an unexpected file")
            for entry in entries:
                destination = target.joinpath(*PurePosixPath(entry.filename).parts)
                if not destination.absolute().is_relative_to(target.absolute()):
                    raise SourceError("Extraction target escaped its cache")
                plain_path(destination)
                if entry.is_dir():
                    io_path(destination).mkdir(parents=True, exist_ok=True)
                    continue
                io_path(destination.parent).mkdir(parents=True, exist_ok=True)
                hashed = hashlib.sha256()
                retained = io_path(destination).exists()
                if retained:
                    with archive.open(entry) as reader:
                        expected = stream_digest(reader)
                    if io_path(destination).stat().st_size != entry.file_size or digest(destination) != expected:
                        raise SourceError("Retained source file differs; it will not be overwritten")
                    inventory_receipt.append({"path": entry.filename, "size": entry.file_size, "sha256": expected})
                    continue
                with archive.open(entry) as reader, io_path(destination).open("xb") as writer:
                    while block := reader.read(1024 * 1024):
                        now = time.monotonic()
                        if now - last_check >= 1:
                            if shutil.disk_usage(cache).free <= 4 * GIB:
                                raise SourceError("Cache space reserve reached; extraction stopped")
                            last_check = now
                        writer.write(block)
                        hashed.update(block)
                if io_path(destination).stat().st_size != entry.file_size or digest(destination) != hashed.hexdigest():
                    raise SourceError("Extracted file readback mismatch")
                inventory_receipt.append({"path": entry.filename, "size": entry.file_size, "sha256": hashed.hexdigest()})
        for name in CORE:
            if digest(target / name) != report["files"][name]:
                raise SourceError("Extracted source identity changed")
        for name in CORE[1:]:
            x64(target / name)
            signature(target / name, package=False)
        if digest(source) != report["package_sha256"]:
            raise SourceError("Source changed during extraction")
        result = dict(report, source_app=str(target / "app"), files_readback=inventory_receipt)
        (target / "source-verification.json").write_text(json.dumps(result, indent=2), encoding="utf8")
        return result
    except Exception as error:
        (target / "extraction-failed.json").write_text(json.dumps({"status": "failed", "reason": str(error), "installed": False}), encoding="utf8")
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--contracts", type=Path, required=True)
    parser.add_argument("--cache-root", type=Path)
    parser.add_argument("--inspect-only", action="store_true")
    args = parser.parse_args()
    contracts = json.loads(args.contracts.read_text(encoding="utf-8-sig")).get("source_contracts", {})
    report = inspect(args.source, contracts)
    if not args.inspect_only:
        if args.cache_root is None:
            parser.error("--cache-root is required for extraction")
        report = extract(args.source, args.cache_root, report)
    print(json.dumps(report))


if __name__ == "__main__":
    main()
