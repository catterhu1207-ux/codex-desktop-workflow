from __future__ import annotations

from datetime import datetime, timezone
from contextlib import closing
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
from . import backend, history


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
    "26.917.6896.0": PackageSupport(
        version="26.917.6896.0",
        package_full_name="OpenAI.Codex_26.917.6896.0_x64__2p2nqsd0c76g0",
        asar_sha256="00b7936388d11a3faede5fc736a8c6264eb66e1907bac4ef72c39b7399175d68",
        backend_sha256="97d4d67419d0ac2f71342f9a5e850f9468aa622618de8ea823223edb9a91926a",
        backend_policy=_POLICY_ROOT / "official-26.917.6896.0.json",
        backend_policy_sha256="b3d6aef7dc952d1c87e09606b20c0177c8c322fb85e4131bde3bb4faa1861b52",
        entries={
            "webview/assets/app-initial-78d977413c37.js": "e363fe7a0b31317c74b814de63f57ab85ad85128e9af67ff3195da16238d35b5",
            "webview/assets/app-primary-923a2b3e8cd1.js": "f0add13e80656997dab54686d7e8fd0c69fae85a9d364433d77dda351fdfe4ed",
            "webview/assets/composer-project-picker-content-531ef99549e8.js": "6e436c6eee1f234ae9626f0434205dff0f9a2c400285bb02ee6119f29c2e5996",
            ".vite/build/main-Bx5zswAj.js": "610ea8b045f207360ac50fcccfe43ca896c6298fa75562f323f1a45ed2364a1b",
            ".vite/build/bootstrap-DwqRMhlU.js": "79ad86bda1f6171d43bab09b1b4a5d379afefc07a13d6f4f58470a823f6f575f",
        },
    ),
    "26.917.9434.0": PackageSupport(
        version="26.917.9434.0",
        package_full_name="OpenAI.Codex_26.917.9434.0_x64__2p2nqsd0c76g0",
        asar_sha256="d4234b03eb532fe0f3e9a7d90caad51edb68af45f771cc786d966377e7446f5a",
        backend_sha256="9015c47d1714294ecd9033c4b5aefc3076797d867d1c36aa37749fcb76c8942f",
        backend_policy=_POLICY_ROOT / "official-26.917.9434.0.json",
        backend_policy_sha256="8856225104326a7a33dd3da278236e758b8506d77435683081221422724e0e48",
        entries={
            "webview/assets/app-initial-fc9a33fdda88.js": "34a60939a5f44634a65c956b7904d63236178e6d45a049717358fc163ecffe88",
            "webview/assets/app-primary-a7ff54c980af.js": "e8ac507e0a621099a2b82b9ae17b1d1930ab971b1d088fe4fb81f5437648d043",
            ".vite/build/main-BR_2NHW6.js": "1f2b91cf92fc023fb2fa41e1c1d03698fa6e37354ecd07dd0cebd21337607b08",
            ".vite/build/bootstrap-CiIGnI3y.js": "119bb54ee12ed5d2b0d3b98dd068a4322232a4aa342323eb9cb5dfa6575ca158",
        },
    ),
}
SUPPORTED_PACKAGES['26.924.1866.0'] = PackageSupport(version='26.924.1866.0', package_full_name='OpenAI.Codex_26.924.1866.0_x64__2p2nqsd0c76g0', asar_sha256='96b6aa6e1ea46dd8a30b3fa5166be12284ba66bd3901241a81a60684f150189d', backend_sha256='0122378c15dc0c3c0af0d6addf2dd278125c19676b41fadaa520f89d2c9e0079', backend_policy=_POLICY_ROOT / 'official-26.924.1866.0.json', backend_policy_sha256='b81928584a72f20fb18de747cab179554cd7c34745d1be450a9278415448ae17', entries={'webview/assets/app-primary-d6f740bc7e54.js': '615347d3d2b0bde27085a3531780a077e3f65dd477e52b1a0e8139109f1c70e9', '.vite/build/main-DhsWCh3w.js': 'fe0ba5e84514b894e2b6e8a282bd981b2b86db735ed4a719cc93d3fdb8063544', 'webview/assets/app-shared-d93bebbb48ab.js': 'c47c36ac7af90884e27d2439b8b577e260831d1819e56b4dd45e09ba89f854e9', 'webview/assets/app-initial-58e226417aae.js': '0389028e89d8ec1ff8bc169a88988b3af82965236cc0a515c7fd678ecfd7d6f5'})
SUPPORTED_PACKAGES['26.924.1866.0'].entries['.vite/build/app-protocol-IjFomtpu.js'] = '56566de85770635d1596d8078a6fb798c5d7e80088689165305454bf8fa25f4d'

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
    elif version == '26.924.1866.0' and _sha256(executable) != '5263bb43c717fc317655ae3aa8dfb7bb5d2b344832fa6ec449fa55dbe77d56b8':
        problems.append('official_desktop_executable_sha256_mismatch')
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


def build_backend(source: Path, target: Path) -> dict[str, Any]:
    inspected = inspect(source)
    if inspected['status'] != 'passed' or inspected['supported_version'] != '26.924.1866.0':
        raise WorkflowError('compat_backend_source_unsupported')
    return backend.build(Path(inspected['app_directory']), target)


def build(source: Path, target: Path, backend_mode: str = 'official', backend_manifest: Path | None = None) -> dict[str, Any]:
    result = inspect(source)
    if result["status"] != "passed":
        raise WorkflowError("source_inspection_blocked:" + ",".join(result["problems"]))
    support = SUPPORTED_PACKAGES[str(result["supported_version"])]
    if backend_mode not in ('official', 'compat'):
        raise WorkflowError('unsupported_backend_mode')
    if backend_mode == 'compat':
        if support.version != '26.924.1866.0' or backend_manifest is None:
            raise WorkflowError('compatible_backend_manifest_required_for_supported_version')
        backend.validate_manifest(backend_manifest)
        selected_policy = backend_manifest
        selected_policy_sha256 = _sha256(backend_manifest)
    else:
        if backend_manifest is not None:
            raise WorkflowError('backend_manifest_requires_compat_mode')
        selected_policy = support.backend_policy
        selected_policy_sha256 = support.backend_policy_sha256
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
        selected_policy,
        selected_policy_sha256,
    )
    if backend_mode == 'compat':
        copied_policy = target / 'resources/backend-build-manifest.json'
        shutil.copy2(selected_policy, copied_policy)
        selected_policy = copied_policy
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
        "backend_mode": backend_mode,
        "backend_manifest_sha256": selected_policy_sha256,
        "backend_manifest": str(selected_policy.resolve()),
        "artifact_id": hotfix_builder.frontend_attestation_artifact_id(hotfix_builder.profile_for_asar(support.asar_sha256)) + '-' + backend_mode + '-' + _sha256(target / 'resources/codex.exe')[:12],
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
    required = set(hotfix_builder.FRONTEND_ATTESTATION_FEATURES)
    passed = [item for item in values if item.get('status') == 'passed'
              and item.get('transport') == 'renderer_log_message_v1'
              and set(item.get('features', {})) == required
              and all(isinstance(feature, dict) and feature.get('passed') is True for feature in item['features'].values())]
    loaded = [item for item in values if item.get("status") == "module_loaded"]
    valid_runs = {item.get('run_id') for item in passed} & {item.get('run_id') for item in loaded}
    valid_runs.discard(None)
    return {"status": "passed" if valid_runs else "blocked", "feature_count": len(required) if valid_runs else 0, "module_loaded": len(loaded), "passed": len(passed), "run_ids": sorted(valid_runs)}


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
    for item in value.get("alive_backends") or []:
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


def _current_app_server_match(value: dict[str, Any], portable: Path, expected_sha256: str) -> bool:
    if not _registered_backend_match(value, portable, expected_sha256):
        return False
    main_pid = value.get('main', {}).get('pid')
    if type(main_pid) is not int:
        return False
    expected = (portable / 'resources/codex.exe').resolve()
    candidates = [item['pid'] for item in value.get('alive_backends', [])
                  if type(item.get('pid')) is int and Path(item.get('executable', '')).resolve() == expected]
    if not candidates:
        return False
    # Commands are read only for the identity-checked backends of this isolated run.
    expression = "$rows=Get-CimInstance Win32_Process; $parents=@{}; foreach($row in $rows){$parents[[int]$row.ProcessId]=[int]$row.ParentProcessId}; $ok=$false; foreach($candidate in @(" + ','.join(map(str,candidates)) + ")){$row=$rows|Where-Object{$_.ProcessId -eq $candidate}; if($row.CommandLine -notmatch '(?:^|\\s)app-server(?:\\s|$)'){continue}; $ancestor=[int]$candidate; for($step=0;$step -lt 256;$step++){if($ancestor -eq " + str(main_pid) + "){$ok=$true;break}; if(-not $parents.ContainsKey($ancestor)){break}; $ancestor=$parents[$ancestor]}}; $ok|ConvertTo-Json -Compress"
    result = subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',expression],capture_output=True,text=True,timeout=15)
    return result.returncode == 0 and result.stdout.strip().lower() == 'true'


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


def _seed_synthetic_tasks(home: Path, empty_home: Path) -> None:
    import uuid
    with closing(sqlite3.connect((empty_home / 'state_5.sqlite').as_uri() + '?mode=ro', uri=True)) as source, closing(sqlite3.connect(home / 'state_5.sqlite')) as target:
        if source.execute('SELECT COUNT(*) FROM threads').fetchone()[0] != 0:
            raise WorkflowError('acceptance_seed_must_be_empty')
        source.backup(target)
        now = int(time.time())
        for index in range(400):
            tid = str(uuid.uuid4())
            project = home / 'synthetic-workspaces' / str(index % 12)
            project.mkdir(parents=True, exist_ok=True)
            rollout = home / 'sessions' / ('synthetic-' + tid + '.jsonl')
            rollout.parent.mkdir(exist_ok=True)
            metadata = {'timestamp': _now(), 'type': 'session_meta', 'payload': {'id': tid, 'cwd': str(project), 'source': 'vscode', 'model_provider': 'openai', 'cli_version': '0.158.0-alpha.2'}}
            rollout.write_text(json.dumps(metadata) + '\n', encoding='utf8')
            row = (tid, str(rollout), now-index, now-index, 'vscode', 'openai', str(project), 'Synthetic acceptance task '+str(index), '{"type":"read-only"}', 'never', 1, 0, '0.158.0-alpha.2', 'Synthetic acceptance task '+str(index), now-index, (now-index)*1000, int(index<10))
            target.execute('INSERT INTO threads(id,rollout_path,created_at,updated_at,source,model_provider,cwd,title,sandbox_policy,approval_mode,has_user_event,archived,cli_version,first_user_message,recency_at,recency_at_ms,is_pinned) VALUES('+','.join('?'*17)+')', row)
        target.commit()


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
    public_path = portable / 'codex-desktop-workflow.json'
    public = json.loads(public_path.read_text()) if public_path.is_file() else {'backend_mode': 'official'}
    support = SUPPORTED_PACKAGES.get(str(manifest_data.get("package_version") or ""))
    if support is None:
        raise WorkflowError("verified_portable_version_unsupported")
    if source_result["supported_version"] != support.version:
        raise WorkflowError("source_and_portable_version_mismatch")
    selected_policy = support.backend_policy
    selected_digest = support.backend_policy_sha256
    if public.get('backend_mode') == 'compat':
        selected_policy = Path(public['backend_manifest'])
        backend.validate_manifest(selected_policy)
        selected_digest = _sha256(selected_policy)
        if public.get('backend_manifest_sha256') != selected_digest:
            raise WorkflowError('backend_manifest_changed_after_build')
    elif public.get('backend_mode') != 'official':
        raise WorkflowError('unsupported_backend_mode')
    bundle = hotfix_builder.verify_manifest(manifest_path, selected_digest, selected_policy)
    contracts = frontend_feature_contracts.validate(Path(source_result["app_directory"]) / "resources" / "app.asar", portable / "resources" / "app.asar")
    runs_root.mkdir(parents=True, exist_ok=True)
    expected_backend = (portable / "resources" / "codex.exe").resolve()
    if not expected_backend.is_file():
        raise WorkflowError("portable_backend_missing")
    expected_backend_sha256 = _sha256(expected_backend)
    selected_hash = backend.validate_manifest(selected_policy)['patched']['sha256'] if public.get('backend_mode') == 'compat' else support.backend_sha256
    if expected_backend_sha256 != selected_hash:
        raise WorkflowError("portable_backend_identity_mismatch")
    runtime: list[dict[str, Any]] = []
    artifact_id = str(
        bundle.get("artifact_id")
        or hotfix_builder.frontend_attestation_artifact_id(
            hotfix_builder.profile_for_asar(support.asar_sha256)
        )
    )
    for index in range(launches):
        home = (runs_root / ("home-" + os.urandom(8).hex())).resolve()
        home.mkdir(parents=True, exist_ok=False)
        if index % 2 == 1:
            _seed_synthetic_tasks(home, Path(runtime[-1]['codex_home']))
        history.inspect(home)
        debug_port = _available_loopback_port()
        run = IsolatedRun.start(
            portable / "ChatGPT.exe",
            runs_root,
            environment=_portable_environment(portable, home),
            debug_port=debug_port,
        )
        proof_deadline = time.monotonic() + 240
        deadline = proof_deadline
        proof_at = None
        latest: dict[str, Any] = {}
        attestation_requested = False
        while time.monotonic() < deadline:
            latest = run.status("codex.exe")
            if latest.get("status") in {"exited", "backend_orphaned"}:
                break
            if not attestation_requested:
                attestation_requested = _request_renderer_attestation(debug_port)
            fresh = _attestations(home, artifact_id, (run.run_directory / 'stdout.log', run.run_directory / 'stderr.log'))
            if fresh.get('status') == 'passed' and proof_at is None:
                proof_at = time.monotonic()
                deadline = proof_at + observe_seconds
            time.sleep(1)
        latest = run.status("codex.exe")
        backend_match = _current_app_server_match(
            latest, portable, expected_backend_sha256
        )
        attestation = _attestations(home, artifact_id, (run.run_directory / "stdout.log", run.run_directory / "stderr.log"))
        observed = time.monotonic() - proof_at if proof_at is not None else 0
        close = _normal_codex_stop(run, 30)
        runtime.append({"run_directory": str(run.run_directory), "codex_home": str(home), "profile": 'empty' if index % 2 == 0 else 'synthetic_tasks', "observed_seconds": observed, "attestation_requested": attestation_requested, "pre_close": latest, "close": close, "attestation": attestation, "backend_expected_sha256": expected_backend_sha256, "backend_match": backend_match})
        if proof_at is None or observed < observe_seconds or latest.get("status") != "running" or not backend_match or close.get("close_status") != "closed" or attestation.get("status") != "passed":
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
    for name in (*DATA_FILES, *DATA_DIRECTORIES):
        candidate = source / name
        if candidate.exists():
            candidates = [candidate, *candidate.rglob('*')] if candidate.is_dir() else [candidate]
            if any(not _inside(item.resolve(), source) for item in candidates):
                raise WorkflowError('data_import_path_escape')
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
    remapped = history.remap_copy(source, target)
    history_result = history.inspect(target)
    for item in copied:
        destination = target / item['path']
        item.update(sha256=_sha256(destination), size=destination.stat().st_size)
    report = {"schema_version": 1, "status": "passed", "created_at": _now(), "source": str(source), "target": str(target), "copied_files": copied, "excluded": ["auth.json", "config.toml", "plugins", "skills"], "content_logged": False}
    (target / "codex-desktop-workflow-import.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report['remapped_rollout_paths'] = remapped
    report['history'] = history_result
    (target / 'codex-desktop-workflow-import.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
    return report


def launch(portable: Path, data: Path, runs_root: Path) -> dict[str, Any]:
    portable, data = portable.resolve(), data.resolve()
    if not (portable / "codex-desktop-workflow-manifest.json").is_file():
        raise WorkflowError("verified_portable_manifest_missing")
    if not data.is_dir():
        raise WorkflowError("independent_data_directory_missing")
    public_path = portable / 'codex-desktop-workflow.json'
    if public_path.is_file():
        public = json.loads(public_path.read_text(encoding='utf8'))
        if public.get('backend_mode') == 'compat':
            backend.validate_manifest(Path(public['backend_manifest']))
        if public.get('backend_sha256') != _sha256(portable / 'resources/codex.exe'):
            raise WorkflowError('portable_backend_changed_before_launch')
        if public.get('portable_asar_sha256') != _sha256(portable / 'resources/app.asar'):
            raise WorkflowError('portable_frontend_changed_before_launch')
    history.inspect(data)
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
