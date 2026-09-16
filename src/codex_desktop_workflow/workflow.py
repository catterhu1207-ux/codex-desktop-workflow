from __future__ import annotations

from datetime import datetime, timezone
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import sqlite3
import struct
import subprocess
import time
from typing import Any
import urllib.request
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

import frontend_feature_contracts
import hotfix_builder
from electron_update_safety.lifecycle import IsolatedRun


SUPPORTED_VERSION = "26.908.9136.0"
PACKAGE_FULL_NAME = "OpenAI.Codex_26.908.9136.0_x64__2p2nqsd0c76g0"
OFFICIAL_ASAR_SHA256 = "7a46bd6fe162050afbac27d7d5271d19524e887fa0cdd06c0f2d3fa9b606a31d"
OFFICIAL_BACKEND_SHA256 = "960c111d47afd61669954b9df9e56083e302edbfa3ef6962d81dcc14a30051dc"
OFFICIAL_BACKEND_POLICY_SHA256 = "7d1c29cdb6dc0f89b9e2966e776f9e7b47502f55e6ad35cf9c7bdb3fd57a93fb"
OFFICIAL_BACKEND_POLICY = Path(__file__).parent / "policies" / "official-26.908.9136.0.json"
OFFICIAL_ENTRIES = {
    "webview/assets/app-initial-bcc2ff475eb6.js": "3c15444f96a8d48844258618fe0d4278409e626f0ee563a77d2c669ec669c510",
    "webview/assets/app-primary-b36a719dba75.js": "255287957d4cf9a21d386948c997114bf039d5c15fc73258d3df5095114a047a",
    ".vite/build/main-D8abTQQE.js": "b55be874a9b5a262c09a7945df38cec9b0ce8f14bd584ef73d6feca301ed90b4",
    ".vite/build/window-all-closed-BxbCP6YG.js": "8939f42fd89899a649b8062699b386e9ff933c241155b611c3b5ec7a738673ed",
}
DATA_FILES = (
    ".codex-global-state.json",
    "state_5.sqlite",
    "logs_2.sqlite",
    "goals_1.sqlite",
    "queue_1.sqlite",
    "thread_history_1.sqlite",
)
DATA_DIRECTORIES = ("sessions", "archived_sessions", "rollout_summaries")


class WorkflowError(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _extended(path: Path) -> str:
    """Return a Windows extended-length path for deep Electron package trees."""
    value = str(path.resolve())
    if os.name != "nt" or value.startswith("\\\\?\\"):
        return value
    if value.startswith("\\\\"):
        return "\\\\?\\UNC\\" + value[2:]
    return "\\\\?\\" + value


def _app_root(value: Path) -> tuple[Path, Path | None]:
    value = value.resolve()
    if (value / "resources" / "app.asar").is_file():
        return value, value.parent / "AppxManifest.xml"
    if (value / "app" / "resources" / "app.asar").is_file():
        return value / "app", value / "AppxManifest.xml"
    raise WorkflowError("official_app_directory_not_found")


def _package_version(app: Path, manifest: Path | None) -> str | None:
    if manifest and manifest.is_file():
        try:
            root = ET.parse(manifest).getroot()
            identity = next((item for item in root.iter() if item.tag.endswith("Identity")), None)
            if identity is not None:
                return identity.attrib.get("Version")
        except (ET.ParseError, OSError):
            pass
    for parent in (app.parent, app):
        if parent.name.startswith("OpenAI.Codex_") and "_x64__" in parent.name:
            return parent.name.split("OpenAI.Codex_", 1)[1].split("_x64__", 1)[0]
    return None


def inspect(source: Path) -> dict[str, Any]:
    app, appx = _app_root(source)
    asar = app / "resources" / "app.asar"
    backend = app / "resources" / "codex.exe"
    executable = app / "ChatGPT.exe"
    version = _package_version(app, appx)
    problems: list[str] = []
    if os.name != "nt":
        problems.append("windows_required")
    if version != SUPPORTED_VERSION:
        problems.append(f"unsupported_version:{version or 'unknown'}")
    asar_digest = _sha256(asar)
    if asar_digest != OFFICIAL_ASAR_SHA256:
        problems.append("official_asar_sha256_mismatch")
    if not backend.is_file() or _sha256(backend) != OFFICIAL_BACKEND_SHA256:
        problems.append("official_backend_sha256_mismatch")
    if not executable.is_file():
        problems.append("desktop_executable_missing")
    entry_results: dict[str, str] = {}
    if not problems or problems == ["windows_required"]:
        header_size, _, header = hotfix_builder.read_asar(asar)
        for name, expected in OFFICIAL_ENTRIES.items():
            _, data = hotfix_builder.read_entry(asar, header_size, hotfix_builder.get_entry_meta(header, name))
            actual = hashlib.sha256(data).hexdigest()
            entry_results[name] = actual
            if actual != expected:
                problems.append(f"official_entry_sha256_mismatch:{name}")
    return {
        "status": "passed" if not problems else "blocked",
        "supported_version": SUPPORTED_VERSION,
        "detected_version": version,
        "package_full_name": PACKAGE_FULL_NAME if version == SUPPORTED_VERSION else None,
        "app_directory": str(app),
        "asar_sha256": asar_digest,
        "backend_sha256": _sha256(backend) if backend.is_file() else None,
        "entry_sha256": entry_results,
        "problems": problems,
        "content_logged": False,
    }


def build(source: Path, target: Path) -> dict[str, Any]:
    result = inspect(source)
    if result["status"] != "passed":
        raise WorkflowError("source_inspection_blocked:" + ",".join(result["problems"]))
    app = Path(result["app_directory"])
    target = target.resolve()
    if target.exists():
        raise WorkflowError("target_must_not_exist")
    if _inside(target, app) or _inside(app, target):
        raise WorkflowError("source_target_must_not_be_nested")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(_extended(app), _extended(target), symlinks=False)
    source_asar = app / "resources" / "app.asar"
    target_asar = target / "resources" / "app.asar"
    if _sha256(target_asar) != OFFICIAL_ASAR_SHA256:
        raise WorkflowError("staged_source_copy_mismatch")
    manifest = target / "codex-desktop-workflow-manifest.json"
    built = hotfix_builder.build_archive(
        source_asar,
        target_asar,
        manifest,
        PACKAGE_FULL_NAME,
        SUPPORTED_VERSION,
        target,
        OFFICIAL_BACKEND_POLICY,
        OFFICIAL_BACKEND_POLICY_SHA256,
    )
    public = {
        "schema_version": 1,
        "status": "bundle_qualified",
        "created_at": _now(),
        "package_version": SUPPORTED_VERSION,
        "source_app": str(app),
        "portable_app": str(target),
        "official_asar_sha256": OFFICIAL_ASAR_SHA256,
        "portable_asar_sha256": built.get("portable_asar_sha256"),
        "builder_manifest": str(manifest),
        "backend_mode": "official",
        "backend_sha256": _sha256(target / "resources" / "codex.exe"),
        "content_logged": False,
    }
    (target / "codex-desktop-workflow.json").write_text(json.dumps(public, ensure_ascii=False, indent=2), encoding="utf-8")
    return public


def _attestation_value(text: str, artifact_id: str) -> dict[str, Any] | None:
    marker = text.find("[CF9]")
    if marker < 0:
        return None
    candidate = text[marker + 5 :]
    start = candidate.find("{")
    if start < 0:
        return None
    try:
        value, _ = json.JSONDecoder().raw_decode(candidate[start:])
    except (ValueError, json.JSONDecodeError):
        return None
    return value if value.get("artifact_id") == artifact_id and value.get("content_logged") is False else None


def _attestations(home: Path, artifact_id: str, log_path: Path | tuple[Path, ...] | None = None) -> dict[str, Any]:
    values: list[dict[str, Any]] = []
    paths = log_path if isinstance(log_path, tuple) else (() if log_path is None else (log_path,))
    for path in paths:
        if path.is_file():
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                value = _attestation_value(line, artifact_id)
                if value is not None:
                    values.append(value)
    for database in home.glob("*.sqlite"):
        try:
            with sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True) as connection:
                for (table,) in connection.execute("select name from sqlite_master where type='table'"):
                    columns = [row[1] for row in connection.execute(f'pragma table_info("{table}")')]
                    for column in columns:
                        try:
                            rows = connection.execute(f'select "{column}" from "{table}" where cast("{column}" as text) like ?', ("%[CF9]%",)).fetchall()
                        except sqlite3.DatabaseError:
                            continue
                        for (raw,) in rows:
                            value = _attestation_value(str(raw), artifact_id)
                            if value is not None:
                                values.append(value)
        except sqlite3.DatabaseError:
            continue
    passed = [item for item in values if item.get("status") == "passed"]
    loaded = [item for item in values if item.get("status") == "module_loaded"]
    return {"status": "passed" if passed and loaded else "blocked", "module_loaded": len(loaded), "passed": len(passed), "run_ids": sorted({str(item.get('run_id')) for item in values if item.get('run_id')})}


def _available_loopback_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def _websocket_frame(payload: bytes) -> bytes:
    mask = os.urandom(4)
    if len(payload) < 126:
        header = bytes((0x81, 0x80 | len(payload)))
    elif len(payload) <= 0xFFFF:
        header = bytes((0x81, 0xFE)) + struct.pack("!H", len(payload))
    else:
        header = bytes((0x81, 0xFF)) + struct.pack("!Q", len(payload))
    return header + mask + bytes(value ^ mask[index % 4] for index, value in enumerate(payload))


def _cdp_evaluate(port: int, expression: str, timeout: float = 3) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=timeout) as response:
            targets = json.loads(response.read())
        target = next(item for item in targets if item.get("type") == "page" and item.get("url") == "app://-/index.html")
        endpoint = target.get("webSocketDebuggerUrl")
        if not isinstance(endpoint, str):
            return False
        parsed = urlsplit(endpoint)
        if parsed.scheme != "ws" or parsed.hostname not in {"127.0.0.1", "localhost"} or parsed.port is None:
            return False
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        path = parsed.path + (("?" + parsed.query) if parsed.query else "")
        with socket.create_connection((parsed.hostname, parsed.port), timeout=timeout) as connection:
            handshake = (
                f"GET {path} HTTP/1.1\r\nHost: {parsed.hostname}:{parsed.port}\r\n"
                "Upgrade: websocket\r\nConnection: Upgrade\r\n"
                f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
            ).encode("ascii")
            connection.sendall(handshake)
            response = b""
            while b"\r\n\r\n" not in response and len(response) < 16384:
                block = connection.recv(4096)
                if not block:
                    break
                response += block
            if not response.startswith(b"HTTP/1.1 101"):
                return False
            command = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": expression, "returnByValue": True}}
            connection.sendall(_websocket_frame(json.dumps(command, separators=(",", ":")).encode("utf-8")))
        return True
    except (OSError, ValueError, StopIteration, json.JSONDecodeError, TimeoutError):
        return False


def _request_codex_quit(port: int, timeout: float = 3) -> bool:
    """Invoke the same quit-app action exposed to the supported renderer."""
    return _cdp_evaluate(port, "electronBridge.sendMessageFromView({type:'quit-app'})", timeout)


def _request_renderer_attestation(port: int, timeout: float = 3) -> bool:
    return _cdp_evaluate(port, "location.href='app://-/local/codex-desktop-workflow-acceptance'", timeout)


def _normal_codex_stop(run: IsolatedRun, timeout: float, backend_name: str = "codex.exe") -> dict[str, Any]:
    before = run.status(backend_name)
    if not before.get("main_identity_match"):
        return {**before, "close_status": "refused_identity_mismatch", "codex_quit_sent": False}
    port = before.get("debug_port")
    sent = isinstance(port, int) and _request_codex_quit(port, min(timeout, 3))
    result = run.wait_for_exit(timeout, backend_name)
    return {**result, "close_status": "closed" if result.get("status") == "exited" else "timeout", "codex_quit_sent": sent}


def verify(source: Path, portable: Path, runs_root: Path, observe_seconds: float = 60.0, launches: int = 2) -> dict[str, Any]:
    if launches < 2:
        raise WorkflowError("verification_requires_two_launches")
    if observe_seconds < 60:
        raise WorkflowError("verification_requires_60_seconds_per_launch")
    source_result = inspect(source)
    if source_result["status"] != "passed":
        raise WorkflowError("source_inspection_blocked")
    portable = portable.resolve()
    manifest_path = portable / "codex-desktop-workflow-manifest.json"
    if not manifest_path.is_file():
        raise WorkflowError("builder_manifest_missing")
    bundle = hotfix_builder.verify_manifest(
        manifest_path,
        OFFICIAL_BACKEND_POLICY_SHA256,
        OFFICIAL_BACKEND_POLICY,
    )
    contracts = frontend_feature_contracts.validate(Path(source_result["app_directory"]) / "resources" / "app.asar", portable / "resources" / "app.asar")
    runs_root.mkdir(parents=True, exist_ok=True)
    runtime: list[dict[str, Any]] = []
    artifact_id = str(bundle.get("artifact_id") or hotfix_builder.FRONTEND_ATTESTATION_ARTIFACT_ID)
    for _ in range(launches):
        home = (runs_root / ("home-" + os.urandom(8).hex())).resolve()
        home.mkdir(parents=True, exist_ok=False)
        debug_port = _available_loopback_port()
        run = IsolatedRun.start(portable / "ChatGPT.exe", runs_root, environment={"CODEX_HOME": str(home)}, debug_port=debug_port)
        deadline = time.monotonic() + observe_seconds
        latest: dict[str, Any] = {}
        attestation_requested = False
        while time.monotonic() < deadline:
            latest = run.status("codex.exe")
            if latest.get("status") in {"exited", "backend_orphaned"}:
                break
            if not attestation_requested:
                attestation_requested = _request_renderer_attestation(debug_port)
            time.sleep(1)
        latest = run.status("codex.exe")
        attestation = _attestations(home, artifact_id, (run.run_directory / "stdout.log", run.run_directory / "stderr.log"))
        close = _normal_codex_stop(run, 30)
        runtime.append({"run_directory": str(run.run_directory), "codex_home": str(home), "observed_seconds": observe_seconds, "attestation_requested": attestation_requested, "pre_close": latest, "close": close, "attestation": attestation})
        if latest.get("status") != "running" or not latest.get("registered_backends") or close.get("close_status") != "closed" or attestation.get("status") != "passed":
            failure = {"status": "blocked", "stage": "isolated_renderer_qualification", "bundle": bundle, "feature_contracts": contracts, "runtime": runtime, "content_logged": False}
            (portable / "codex-desktop-workflow-verification-failed.json").write_text(json.dumps(failure, ensure_ascii=False, indent=2), encoding="utf-8")
            raise WorkflowError("two_run_lifecycle_validation_failed")
    result = {"status": "passed", "stage": "isolated_renderer_qualified", "bundle": bundle, "feature_contracts": contracts, "runtime": runtime, "content_logged": False}
    report = portable / "codex-desktop-workflow-verification.json"
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def _running_codex_processes() -> list[dict[str, Any]]:
    if os.name != "nt":
        return []
    command = "Get-CimInstance Win32_Process | Where-Object {$_.Name -in @('ChatGPT.exe','codex.exe')} | Select-Object ProcessId,Name,ExecutablePath | ConvertTo-Json -Compress"
    completed = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command], capture_output=True, text=True, encoding="utf-8", errors="replace", check=True, timeout=15)
    rows = json.loads(completed.stdout or "[]")
    return rows if isinstance(rows, list) else [rows]


def import_data(source: Path, target: Path) -> dict[str, Any]:
    source, target = source.resolve(), target.resolve()
    if not source.is_dir():
        raise WorkflowError("data_source_not_found")
    if target.exists():
        raise WorkflowError("data_target_must_not_exist")
    if _inside(target, source) or _inside(source, target):
        raise WorkflowError("data_source_target_must_not_be_nested")
    active = _running_codex_processes()
    if active:
        raise WorkflowError("codex_processes_must_exit_before_import")
    target.mkdir(parents=True)
    copied: list[dict[str, Any]] = []
    for name in DATA_FILES:
        original = source / name
        if not original.is_file():
            continue
        destination = target / name
        if original.suffix == ".sqlite":
            read = sqlite3.connect(f"file:{original.as_posix()}?mode=ro", uri=True)
            write = sqlite3.connect(destination)
            try:
                read.backup(write)
                write.commit()
            finally:
                write.close()
                read.close()
        else:
            shutil.copy2(original, destination)
        copied.append({"path": name, "sha256": _sha256(destination), "size": destination.stat().st_size})
    for name in DATA_DIRECTORIES:
        original = source / name
        if original.is_dir():
            shutil.copytree(original, target / name)
    report = {"schema_version": 1, "status": "passed", "created_at": _now(), "source": str(source), "target": str(target), "copied_files": copied, "excluded": ["auth.json", "config.toml", "plugins", "skills"], "content_logged": False}
    (target / "codex-desktop-workflow-import.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def launch(portable: Path, data: Path, runs_root: Path) -> dict[str, Any]:
    portable, data = portable.resolve(), data.resolve()
    if not (portable / "codex-desktop-workflow-manifest.json").is_file():
        raise WorkflowError("verified_portable_manifest_missing")
    if not data.is_dir():
        raise WorkflowError("independent_data_directory_missing")
    return IsolatedRun.start(portable / "ChatGPT.exe", runs_root, environment={"CODEX_HOME": str(data)}, debug_port=_available_loopback_port())._load()


def status(run: Path) -> dict[str, Any]:
    return IsolatedRun(run).status("codex.exe")


def stop(run: Path, timeout: float) -> dict[str, Any]:
    return _normal_codex_stop(IsolatedRun(run), timeout)
