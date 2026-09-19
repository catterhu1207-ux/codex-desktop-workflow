from __future__ import annotations

from datetime import datetime, timezone
import base64
from dataclasses import dataclass
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


@dataclass(frozen=True)
class PackageSupport:
    version: str
    package_full_name: str
    asar_sha256: str
    backend_sha256: str
    backend_policy: Path
    backend_policy_sha256: str
    entries: dict[str, str]


_POLICY_ROOT = Path(__file__).parent / "policies"
SUPPORTED_PACKAGES = {
    "26.908.9136.0": PackageSupport(
        version="26.908.9136.0",
        package_full_name="OpenAI.Codex_26.908.9136.0_x64__2p2nqsd0c76g0",
        asar_sha256="7a46bd6fe162050afbac27d7d5271d19524e887fa0cdd06c0f2d3fa9b606a31d",
        backend_sha256="960c111d47afd61669954b9df9e56083e302edbfa3ef6962d81dcc14a30051dc",
        backend_policy=_POLICY_ROOT / "official-26.908.9136.0.json",
        backend_policy_sha256="7d1c29cdb6dc0f89b9e2966e776f9e7b47502f55e6ad35cf9c7bdb3fd57a93fb",
        entries={
            "webview/assets/app-initial-bcc2ff475eb6.js": "3c15444f96a8d48844258618fe0d4278409e626f0ee563a77d2c669ec669c510",
            "webview/assets/app-primary-b36a719dba75.js": "255287957d4cf9a21d386948c997114bf039d5c15fc73258d3df5095114a047a",
            ".vite/build/main-D8abTQQE.js": "b55be874a9b5a262c09a7945df38cec9b0ce8f14bd584ef73d6feca301ed90b4",
            ".vite/build/window-all-closed-BxbCP6YG.js": "8939f42fd89899a649b8062699b386e9ff933c241155b611c3b5ec7a738673ed",
        },
    ),
    "26.915.3509.0": PackageSupport(
        version="26.915.3509.0",
        package_full_name="OpenAI.Codex_26.915.3509.0_x64__2p2nqsd0c76g0",
        asar_sha256="8227f6234cf2cc418ec8bbdeedec03f8d777f85520929ff2d9d38e774f681dfd",
        backend_sha256="ff9bc3ddc08fa52b43ea170be5f628ffad1c1d9c80c5770b8e2a2f817a9ee3c9",
        backend_policy=_POLICY_ROOT / "official-26.915.3509.0.json",
        backend_policy_sha256="eaec7e5f32dae86546b642caf14764c56b9d4baacc27766d71dd6e4dadb192ce",
        entries={
            "webview/assets/app-initial-f61fcec072b5.js": "ba7fe9c3b375d7766f9b8e9b686d1bc1987b6a45d5f42aeab9368d81f374dbf0",
            "webview/assets/app-primary-d11a781a17a9.js": "e92faca60efea1673d1f02c0ba1f839741e3b48fa17a800031cc3b695fbb4568",
            "webview/assets/composer-project-picker-content-21970821f4a5.js": "cdbabad8aa78f2584815da5ddfed151523c4a0f3ea02ab0a1728e148dbed8452",
            ".vite/build/main-CIvjSspu.js": "c85af4d37bc53b49fab69f4b48cd941d25b58cafb1b1e5eaa39b18e2497019ff",
            ".vite/build/bootstrap-CqlvPvwP.js": "5df70ea62a9c1689c4bd7e178900ccdcf67c695a2af8b0cc33e39739b1a3a5b2",
        },
    ),
    "26.915.4065.0": PackageSupport(
        version='26.915.4065.0',
        package_full_name='OpenAI.Codex_26.915.4065.0_x64__2p2nqsd0c76g0',
        asar_sha256='b8aeb817cd1ee6ef50efe8a97985d3be41de89688a5addfe0a444e1e52348096',
        backend_sha256='bc45017e8239dc150258f69309ced9df6bbcdf5b8e4f346decf780ac0999e226',
        backend_policy=_POLICY_ROOT / "official-26.915.4065.0.json",
        backend_policy_sha256='c81e789a31869f221730ade3cf901a9664cda843381da3d1cc3d3f2038b1f631',
        entries={'webview/assets/app-initial-6c4523b43a11.js': '146b5204b30bd1766f19c0dd5b76f23515a77708ae80bb66ded6469e11431374', 'webview/assets/app-primary-355549b35da9.js': 'b2ba870a12454be5134b17f538b8caa3314ce5d7b9f0412b637168d3aa682a24', '.vite/build/main-LM8MUIFp.js': 'c71bf3ffecef5fd390b4cd16d120d39dce30d30bffe3c563c8c74c1b691da018', '.vite/build/bootstrap-DK4EfNwt.js': 'dbdbdd3ef5dde93dd196a59846edf244dc653341213e0fd45eebb133b5df10ba', 'webview/assets/composer-project-picker-content-cee23446c3c9.js': '4c284006857748142df2855f486ba4c5724b9e71688736ff4fae6a586d98e1ec'},
    ),
}
SUPPORTED_VERSIONS = tuple(sorted(SUPPORTED_PACKAGES))
SUPPORTED_VERSION = max(SUPPORTED_VERSIONS)
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
    support = SUPPORTED_PACKAGES.get(version or "")
    problems: list[str] = []
    if os.name != "nt":
        problems.append("windows_required")
    if support is None:
        problems.append(f"unsupported_version:{version or 'unknown'}")
    asar_digest = _sha256(asar)
    if support is not None and asar_digest != support.asar_sha256:
        problems.append("official_asar_sha256_mismatch")
    if support is None or not backend.is_file() or _sha256(backend) != support.backend_sha256:
        problems.append("official_backend_sha256_mismatch")
    if not executable.is_file():
        problems.append("desktop_executable_missing")
    entry_results: dict[str, str] = {}
    if support is not None and (not problems or problems == ["windows_required"]):
        header_size, _, header = hotfix_builder.read_asar(asar)
        for name, expected in support.entries.items():
            _, data = hotfix_builder.read_entry(asar, header_size, hotfix_builder.get_entry_meta(header, name))
            actual = hashlib.sha256(data).hexdigest()
            entry_results[name] = actual
            if actual != expected:
                problems.append(f"official_entry_sha256_mismatch:{name}")
    return {
        "status": "passed" if not problems else "blocked",
        "supported_version": version if support is not None else None,
        "supported_versions": list(SUPPORTED_VERSIONS),
        "detected_version": version,
        "package_full_name": support.package_full_name if support is not None else None,
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
    support = SUPPORTED_PACKAGES[str(result["supported_version"])]
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
    if _sha256(target_asar) != support.asar_sha256:
        raise WorkflowError("staged_source_copy_mismatch")
    manifest = target / "codex-desktop-workflow-manifest.json"
    built = hotfix_builder.build_archive(
        source_asar,
        target_asar,
        manifest,
        support.package_full_name,
        support.version,
        target,
        support.backend_policy,
        support.backend_policy_sha256,
    )
    public = {
        "schema_version": 1,
        "status": "bundle_qualified",
        "created_at": _now(),
        "package_version": support.version,
        "source_app": str(app),
        "portable_app": str(target),
        "official_asar_sha256": support.asar_sha256,
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


def _portable_environment(portable: Path, data_home: Path) -> dict[str, str]:
    return {
        "CODEX_HOME": str(data_home),
        "CODEX_CLI_PATH": str((portable / "resources" / "codex.exe").resolve()),
    }


def _registered_backend_match(
    value: dict[str, Any], portable: Path, expected_sha256: str
) -> bool:
    expected = (portable / "resources" / "codex.exe").resolve()
    for item in value.get("registered_backends") or []:
        executable = item.get("executable") if isinstance(item, dict) else None
        if not isinstance(executable, str):
            continue
        try:
            actual = Path(executable).resolve()
        except OSError:
            continue
        if os.path.normcase(str(actual)) != os.path.normcase(str(expected)):
            continue
        if actual.is_file() and _sha256(actual) == expected_sha256:
            return True
    return False


def _websocket_frame(payload: bytes) -> bytes:
    mask = os.urandom(4)
    if len(payload) < 126:
        header = bytes((0x81, 0x80 | len(payload)))
    elif len(payload) <= 0xFFFF:
        header = bytes((0x81, 0xFE)) + struct.pack("!H", len(payload))
    else:
        header = bytes((0x81, 0xFF)) + struct.pack("!Q", len(payload))
    return header + mask + bytes(value ^ mask[index % 4] for index, value in enumerate(payload))


def _websocket_message(connection: Any) -> dict[str, Any]:
    def read_exact(size: int) -> bytes:
        result = bytearray()
        while len(result) < size:
            block = connection.recv(size - len(result))
            if not block:
                raise OSError("websocket_closed")
            result.extend(block)
        return bytes(result)

    first, second = read_exact(2)
    if first != 0x81 or second & 0x80:
        raise ValueError("unsupported_websocket_frame")
    size = second & 0x7F
    if size == 126:
        size = struct.unpack("!H", read_exact(2))[0]
    elif size == 127:
        size = struct.unpack("!Q", read_exact(8))[0]
    if size > 1024 * 1024:
        raise ValueError("websocket_response_too_large")
    return json.loads(read_exact(size))


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
                block = connection.recv(1)
                if not block:
                    break
                response += block
            if not response.startswith(b"HTTP/1.1 101"):
                return False
            command = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": expression, "returnByValue": True}}
            connection.sendall(_websocket_frame(json.dumps(command, separators=(",", ":")).encode("utf-8")))
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                reply = _websocket_message(connection)
                if reply.get("id") != 1:
                    continue
                result = reply.get("result", {})
                return not reply.get("error") and not result.get("exceptionDetails") and result.get("result", {}).get("value") is True
        return False
    except (OSError, ValueError, StopIteration, json.JSONDecodeError, TimeoutError):
        return False


def _request_codex_quit(port: int, timeout: float = 3) -> bool:
    """Invoke the same quit-app action exposed to the supported renderer."""
    return _cdp_evaluate(port, "(electronBridge.sendMessageFromView({type:'quit-app'}),true)", timeout)


def _request_renderer_attestation(port: int, timeout: float = 3) -> bool:
    # Navigating while Electron is still awaiting its first load aborts bootstrap.
    expression = """(() => {
        if (document.readyState !== 'complete' || !globalThis.electronBridge) return false;
        setTimeout(() => { location.href = 'app://-/local/codex-desktop-workflow-acceptance'; }, 500);
        return true;
    })()"""
    return _cdp_evaluate(port, expression, timeout)


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
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    support = SUPPORTED_PACKAGES.get(str(manifest_data.get("package_version") or ""))
    if support is None:
        raise WorkflowError("verified_portable_version_unsupported")
    if source_result["supported_version"] != support.version:
        raise WorkflowError("source_and_portable_version_mismatch")
    bundle = hotfix_builder.verify_manifest(
        manifest_path,
        support.backend_policy_sha256,
        support.backend_policy,
    )
    contracts = frontend_feature_contracts.validate(Path(source_result["app_directory"]) / "resources" / "app.asar", portable / "resources" / "app.asar")
    runs_root.mkdir(parents=True, exist_ok=True)
    expected_backend = (portable / "resources" / "codex.exe").resolve()
    if not expected_backend.is_file():
        raise WorkflowError("portable_backend_missing")
    expected_backend_sha256 = _sha256(expected_backend)
    if expected_backend_sha256 != support.backend_sha256:
        raise WorkflowError("portable_backend_identity_mismatch")
    runtime: list[dict[str, Any]] = []
    artifact_id = str(
        bundle.get("artifact_id")
        or hotfix_builder.frontend_attestation_artifact_id(
            hotfix_builder.profile_for_asar(support.asar_sha256)
        )
    )
    for _ in range(launches):
        home = (runs_root / ("home-" + os.urandom(8).hex())).resolve()
        home.mkdir(parents=True, exist_ok=False)
        debug_port = _available_loopback_port()
        run = IsolatedRun.start(
            portable / "ChatGPT.exe",
            runs_root,
            environment=_portable_environment(portable, home),
            debug_port=debug_port,
        )
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
        backend_match = _registered_backend_match(
            latest, portable, expected_backend_sha256
        )
        attestation = _attestations(home, artifact_id, (run.run_directory / "stdout.log", run.run_directory / "stderr.log"))
        close = _normal_codex_stop(run, 30)
        runtime.append({"run_directory": str(run.run_directory), "codex_home": str(home), "observed_seconds": observe_seconds, "attestation_requested": attestation_requested, "pre_close": latest, "close": close, "attestation": attestation, "backend_expected_sha256": expected_backend_sha256, "backend_match": backend_match})
        if latest.get("status") != "running" or not backend_match or close.get("close_status") != "closed" or attestation.get("status") != "passed":
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
    return IsolatedRun.start(
        portable / "ChatGPT.exe",
        runs_root,
        environment=_portable_environment(portable, data),
        debug_port=_available_loopback_port(),
    )._load()


def status(run: Path) -> dict[str, Any]:
    return IsolatedRun(run).status("codex.exe")


def stop(run: Path, timeout: float) -> dict[str, Any]:
    return _normal_codex_stop(IsolatedRun(run), timeout)
