"""Exact 8622 launcher integration; historical profiles remain immutable."""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any

import hotfix_profile_261016_8622 as base

BUILDER_VERSION = VALIDATOR_VERSION = "2.11.0"
ARTIFACT_ID = "2.11.0-a05dfd86ca50"
TARGET_ASAR_SHA256 = 'cd79e94e44ba27e01ecf99700f683366de3a608f940b7b8a6fbd23a7222d90d3'
TARGET_EXE_SHA256 = '1c21b663245047fa69cdb4c10e93fe4dab60fe996a477efb7a98c4e9110c6900'
MODULE_SHA256 = '3fc21212df772d96c09065b0a99478592178370cfef1b15f576871014163ab7d'
UPDATE_HELPER_SHA256 = 'f636d173df2298e81659d82bcce7d4095473ada4378e9fec57417d37cf1cc29c'

DATA = Path(__file__).parent / "codex_desktop_workflow/data"
HOOK = b'import("app://-/x").then(m=>m.r(()=>[K0i,F6i,d6i,qZRemoteName,Q3i,$3i,h6i,YXi,xKc,b4t,iq,_Ga,m2i,H7t,GJi,i7t,Stn,zWa,HB,AZi,EO,VB,pinSort,e4,Cva,xV,KB,Ctn,x8i,qZW,dQc,mQc,Ei]));'
TAIL = b"return Z(g,S).map(e=>m.get(e))}"
PROTOCOL_NEW = b'if(e===`app://-/x`)return t+`/../../x.js`;'
HANDLER_OLD = b'process.platform===`win32`?await o.net.fetch((0,l.pathToFileURL)(n).toString()):await B(n)'
HANDLER_NEW = b'process.platform===`win32`&&!n.endsWith(`/x.js`)?await o.net.fetch((0,l.pathToFileURL)(n).toString()):await B(n)'
PROFILE = {'package_version': '26.1016.8622.0', 'asar_source_sha256': 'a05dfd86ca508148c83c25590639cf91a52c6647733cdf200723d85357052b49', 'profile_spec_id': '261016_8622', 'entry_path': 'webview/assets/app-initial-ad16eaadf81f.js', 'entry_source_sha256': '84d1c97245fec7be606fd1d263459d9a4c841836751c6ba5e9b348b69687332f', 'secondary_entry_path': 'webview/assets/app-primary-3e00728c2a4c.js', 'secondary_entry_source_sha256': 'c61df07674363782ea42c4b34fabaa306e75832359a455a64bd064594b450a82', 'shared_entry_path': 'webview/assets/app-shared-2feb3d4c6fcc.js', 'shared_entry_source_sha256': 'd73051468be4c5521d4e53b4ac53a0d1cd52ddede37035183871a1845b4e1dc3', 'main_entry_path': '.vite/build/main-CT5a1yCd.js', 'main_entry_source_sha256': 'cdac659a830908ec5202a887e5a37b302074bfc9e9ab0f52fed3e8abbdb9e713', 'attestation_protocol_entry_path': '.vite/build/browser-background-switches-oSaaOz4s.js', 'attestation_protocol_source_sha256': 'e45e03af9526ac3b9ce1221348893174229fd5714be143bac12c6885f234d605', 'attestation_log_bridge_identifier': 'Ei', 'executable_source_sha256': 'f7f605cceb2e75dca52e03362329a889f917cc1f8d1036cd26386727a2319415', 'embedded_asar_header_source_sha256': '4a73080abfb68f83e8c079ce00d8502257cda91730ee13f5776b6c8907fabbd7'}


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def module_bytes() -> bytes:
    raw = (DATA / "frontend_runtime_261016_8622.mjs").read_bytes()
    if sha(raw) != MODULE_SHA256:
        raise ValueError("8622 runtime module changed")
    return raw


def features() -> tuple[str, ...]:
    import hotfix_builder as b
    return b.FRONTEND_ATTESTATION_FEATURES + ("user_action_pending_orange", "portable_update_awareness")


def all_features() -> tuple[str, ...]:
    import hotfix_builder as b
    return features() + b.NON_RENDERER_ATTESTATION_FEATURES


def prepared_entries(source: Path) -> tuple[int, dict, dict[str, bytes]]:
    import hotfix_builder as b
    return base._prepared_entries(source, b)


def source_gate(source: Path, target: Path) -> dict:
    import hotfix_builder as b
    if b.sha256_path(target) != TARGET_ASAR_SHA256:
        raise ValueError("8622 runtime archive identity differs")
    size, header, expected = prepared_entries(source)
    ts, _, th = b.read_asar(target)
    transforms = []
    for name, data in expected.items():
        if b.read_entry(target, ts, b.get_entry_meta(th, name))[1] != data:
            raise ValueError("8622 exact transformation differs: " + name)
        transforms.append({"path": name, "source_sha256": sha(b.read_entry(source, size, b.get_entry_meta(header, name))[1]),
                           "portable_sha256": sha(data), "length": len(data)})
    # Exact whole-archive digest plus exact changed entries bind the unchanged
    # inventory previously proved for the semantic candidate.
    return {"source_asar_sha256": base.SOURCE_ASAR_SHA256,
            "portable_asar_sha256": TARGET_ASAR_SHA256,
            "semantic_baseline_asar_sha256": base.TARGET_ASAR_SHA256,
            "bootstrap_only_in_trailing_padding": True, "transformations": transforms}


def load_packet() -> dict:
    """Builds do not import private runtime receipts or claim native acceptance."""
    return {"feature_semantics": {name: {
        "status": "pending", "verified_status": "source_checked_pending_runtime",
        "method": "fresh_public_packaged_runtime_required", "evidence_sha256": None
    } for name in all_features()}}


def route() -> dict:
    manifest = json.loads(base.MANIFEST.read_bytes())
    record = next(e for e in manifest["entries"] if e["path"] == PROFILE["attestation_protocol_entry_path"])
    return {"protocol": "app_resource_route_v2", "app_url": "app://-/x",
            "entry_path": record["path"], "source_sha256": record["source_sha256"],
            "patched_sha256": record["target_sha256"], "module_relative_path": "x.js",
            "physical_resolution": "resources/x.js", "mime_type": "text/javascript",
            "response_strategy": "node_stream_response_v1", "general_traversal_enabled": False,
            "old_signature_count": 0, "new_signature_count": 1}


def validate(source_asar: Path, portable_asar: Path, node: str = "node") -> dict:
    import hotfix_builder as b
    gate = source_gate(source_asar, portable_asar)
    packet = load_packet()
    module = portable_asar.parent / "x.js"
    helper = portable_asar.parent / "u.cjs"
    if (not module.is_file() or module.is_symlink() or module.read_bytes() != module_bytes()
            or not helper.is_file() or helper.is_symlink() or b.sha256_path(helper) != UPDATE_HELPER_SHA256):
        raise ValueError("8622 runtime/update resource identity differs")
    probe = {"status": "pending_live_renderer", "protocol": "live_renderer_attestation_v3",
        "transport": "renderer_log_message_v1", "schema_version": 7,
        "log_bridge_identifier": "Ei", "marker": "[CF9]", "artifact_id": ARTIFACT_ID,
        "validator_version": VALIDATOR_VERSION, "feature_ids": list(features()),
        "script_sha256": sha(HOOK), "module_relative_path": "x.js",
        "module_sha256": MODULE_SHA256, "module_size": len(module_bytes()),
        "app_url": "app://-/x", "content_logged": False}
    contracts = {}
    for name, item in packet["feature_semantics"].items():
        nonrenderer = name in b.NON_RENDERER_ATTESTATION_FEATURES
        contracts[name] = {"status": item["verified_status"],
            "source_identity": {"status": "passed", "official_asar_sha256": base.SOURCE_ASAR_SHA256,
                "portable_asar_sha256": TARGET_ASAR_SHA256, "entry_paths": [e["path"] for e in gate["transformations"]]},
            "semantic_execution": {"status": "pending_native_runtime", "method": item["method"], "evidence_sha256": item["evidence_sha256"]},
            "route_wiring": {"status": "passed", "exact_transformations": True},
            "runtime_attestation": {"status": "pending_native_runtime" if nonrenderer else "pending_live_renderer",
                "attestation_version": VALIDATOR_VERSION,
                "protocol": "component_contract_v1" if nonrenderer else "live_renderer_attestation_v3",
                "scope": "main_process" if nonrenderer else "renderer", "artifact_id": ARTIFACT_ID, "content_logged": False},
            "evidence_sha256": item["evidence_sha256"]}
    result = {"schema_version": 2, "validator_version": VALIDATOR_VERSION, "status": "bundle_qualified_only",
        "source_asar_sha256": base.SOURCE_ASAR_SHA256, "portable_asar_sha256": TARGET_ASAR_SHA256,
        "frontend_entry_path": PROFILE["entry_path"], "frontend_entry_sha256": gate["transformations"][0]["portable_sha256"],
        "feature_contracts": contracts, "blocked_feature_ids": [],
        "actual_javascript": {"source_and_archive": gate, "native_semantics": "pending_public_runtime_not_private_evidence"},
        "live_renderer_probe": probe, "content_logged": False}
    result["summary_sha256"] = sha(json.dumps(result, sort_keys=True, separators=(",", ":")).encode())
    return result


def feature_metadata(patched: bool) -> dict:
    result = {name: {"status": "patched" if patched else "patchable", "path": PROFILE["entry_path"],
        "source_sha256": PROFILE["entry_source_sha256"], "reason": None} for name in all_features()}
    result["windows_watch_path_normalization"].update(status="official_fixed", scope="fs/watch", host_scope="local", dependencies=[])
    result["archived_heartbeat_terminal_guard"].update(status="official_fixed")
    result["process_registry_resilience"].update(status="official_fixed", path=PROFILE["main_entry_path"],
                                                 source_sha256=PROFILE["main_entry_source_sha256"])
    result["paginated_tail_retention"].update(policy="official_canonical_pagination", scope="history_mode_paginated")
    result["resume_history_on_demand"].update(policy="native_lazy_paginated_completion", factory_policy="official_paginated_history",
        initial_turn_page_limit=25, auto_drain_remaining_turns=False, prevents_new_paginated_threads=False,
        supports_existing_paginated_threads=True, supports_existing_paginated_threads_after_recovery=True,
        projection_recovery="official_canonical_history")
    result["automation_priority_gate"].update(policy="scheduled_attention_before_idle_toggle",
        scheduled_indicator_included=True, dormant_schedule_excluded=True)
    return result


def inspect(source: Path) -> tuple[dict, dict]:
    import hotfix_builder as b
    digest = b.sha256_path(source)
    if digest not in (base.SOURCE_ASAR_SHA256, TARGET_ASAR_SHA256):
        raise ValueError("8622 archive identity differs")
    return ({"source": str(source), "source_sha256": digest, "source_size": source.stat().st_size,
             "frontend_profile_id": "261016_8622", "features": feature_metadata(digest == TARGET_ASAR_SHA256)},
            {"current_profile": True, "frontend_profile": PROFILE})


def build(source: Path, target: Path, manifest_path: Path, package_full_name: str,
          package_version: str, final_portable_app: Path, codex_patch_manifest: Path | None = None,
          expected_codex_patch_descriptor_sha256: str | None = None) -> dict:
    import hotfix_builder as b
    if package_full_name != base.PACKAGE_FULL_NAME or package_version != base.VERSION:
        raise ValueError("8622 package identity differs")
    load_packet()
    if b.sha256_path(target) != base.SOURCE_ASAR_SHA256:
        raise ValueError("8622 build requires an exact staged official archive")
    size, header, entries = prepared_entries(source)
    _, serial, _ = b.read_asar(target)
    changes = []
    with target.open("r+b") as stream:
        for name, data in entries.items():
            meta = b.get_entry_meta(header, name)
            stream.seek(8 + size + int(meta["offset"]))
            stream.write(data)
            meta["integrity"]["hash"] = sha(data)
            block = meta["integrity"]["blockSize"]
            meta["integrity"]["blocks"] = [sha(data[i:i+block]) for i in range(0, len(data), block)]
            changes.append({"path": name, "patched_sha256": sha(data), "size": len(data)})
        raw = json.dumps(header, ensure_ascii=False, separators=(",", ":")).encode()
        if len(raw) != struct.unpack_from("<I", serial, 12)[0]:
            raise ValueError("8622 header size changed")
        stream.seek(16)
        stream.write(raw)
    b.atomic_replace_bytes(target.parent / "x.js", module_bytes())
    update_bytes = (DATA / "update_bridge_261016_8622.cjs").read_bytes()
    if sha(update_bytes) != UPDATE_HELPER_SHA256:
        raise ValueError("8622 update helper changed")
    b.atomic_replace_bytes(target.parent / "u.cjs", update_bytes)
    app = target.parent.parent
    source_app = source.parent.parent
    integrity = b.synchronize_executable_asar_integrity(source_app, app, source, target, PROFILE)
    if b.sha256_path(app / "ChatGPT.exe") != TARGET_EXE_SHA256:
        raise ValueError("8622 executable differs")
    frontend = validate(source, target)
    if codex_patch_manifest:
        backend = b.prepare_codex_backend_patch(source_app, app, codex_patch_manifest,
            package_full_name, package_version, expected_codex_patch_descriptor_sha256 or "")
    else:
        backend = {"status": "official", "path": "resources/codex.exe",
            "official": {"size": (source_app / "resources/codex.exe").stat().st_size,
                        "sha256": b.sha256_path(source_app / "resources/codex.exe"), "pe_machine": "amd64"}}
    manifest = make_manifest(source, app, final_portable_app, frontend, integrity, backend, changes)
    b.atomic_write_json(manifest_path, manifest)
    return manifest


def make_manifest(source: Path, app: Path, final_app: Path, frontend: dict,
                  integrity: dict, backend: dict, changes: list) -> dict:
    import hotfix_builder as b
    runtime = {key: frontend[key] for key in ("schema_version","validator_version","status",
        "source_asar_sha256","portable_asar_sha256","frontend_entry_path","frontend_entry_sha256",
        "actual_javascript","live_renderer_probe","content_logged","summary_sha256")}
    runtime.update(attestation_module={"relative_path":"x.js","sha256":MODULE_SHA256,"size":len(module_bytes())},
                   protocol_route=route())
    return {"schema_version": 2, "builder_version": BUILDER_VERSION, "frontend_profile_id": "261016_8622",
        "frontend_profile": PROFILE,
        "frontend_output": {"entry_path": PROFILE["entry_path"],
            "entry_sha256": frontend["frontend_entry_sha256"], "asar_sha256": TARGET_ASAR_SHA256,
            "replacement_set_sha256": b.sha256_path(base.MANIFEST)},
        "portable_update_helper": {"relative_path":"u.cjs","sha256":UPDATE_HELPER_SHA256,
            "size":(app/"resources/u.cjs").stat().st_size},
        "frontend_attestation_protocol_route":route(), "created_at":b.utc_now(),
        "package_full_name":base.PACKAGE_FULL_NAME, "package_version":base.VERSION,
        "official_source_asar":str(source.resolve()), "official_source_sha256":base.SOURCE_ASAR_SHA256,
        "official_source_size":source.stat().st_size, "portable_app":str(final_app.resolve()),
        "portable_asar":str((final_app/"resources/app.asar").resolve()), "portable_asar_sha256":TARGET_ASAR_SHA256,
        "executable_asar_integrity":integrity, "launch_mode":"portable", "features":feature_metadata(True),
        "feature_contracts":frontend["feature_contracts"], "frontend_runtime_attestation":runtime,
        "entry_changes":changes, "runtime_monitor":{"version":b.RUNTIME_MONITOR_VERSION,
            "core_pressure_policy_version":b.CORE_PRESSURE_POLICY_VERSION,"tool_pressure_policy_version":b.TOOL_PRESSURE_POLICY_VERSION},
        "codex_backend":backend, "critical_files":b.verify_critical_files(source.parent.parent,app,integrity),
        "validation":{"size_unchanged":True,"header_verified":True,"target_entries_verified":True,
            "launch_status":"pending","runtime_status":"pending"}}


def verify(manifest_path: Path, expected_descriptor: str | None,
           descriptor: Path | None) -> dict:
    """Read back every immutable build field and both actual executables."""
    import hotfix_builder as b
    manifest = json.loads(manifest_path.read_bytes())
    source = Path(manifest["official_source_asar"])
    app = Path(manifest["portable_app"])
    target = app / "resources/app.asar"
    for path in (source, app, target, app / "ChatGPT.exe", app / "resources/codex.exe"):
        if not path.exists() or path.is_symlink():
            raise ValueError("8622 build path missing or redirected")
    if manifest["portable_asar"] != str(target.resolve()):
        raise ValueError("8622 portable archive escaped the application")
    frontend = validate(source, target)
    integrity = b.verify_executable_asar_integrity(source.parent.parent, app, source, target, PROFILE)
    if (b.sha256_path(app / "ChatGPT.exe") != TARGET_EXE_SHA256
            or b.sha256_path(source.parent.parent / "ChatGPT.exe") != base.SOURCE_EXE_SHA256):
        raise ValueError("8622 executable identity differs")
    if descriptor is None or expected_descriptor is None:
        raise ValueError("8622 backend policy is required")
    policy, digest = b.load_codex_backend_patch_policy(descriptor, expected_descriptor)
    if policy.get("mode") != "official":
        from codex_desktop_workflow.backend import validate_manifest
        validate_manifest(descriptor, base.VERSION)
    matched = b.select_codex_backend_package(policy, base.PACKAGE_FULL_NAME, base.VERSION)
    official = source.parent / "codex.exe"
    actual = app / "resources/codex.exe"
    for path, declared in ((official, policy["official"]),
                            (actual, policy["official"] if policy.get("mode") == "official" else policy["patched"])):
        if (path.stat().st_size != declared["size"] or b.sha256_path(path) != declared["sha256"]
                or b.pe_machine(path) != declared["pe_machine"]):
            raise ValueError("8622 actual backend does not match its policy")
    backend = {"status": "official" if policy.get("mode") == "official" else "patched",
        "path": "resources/codex.exe", "patch_id": policy["patch_id"],
        "descriptor_sha256": digest, "official": policy["official"],
        "compatibility": {"policy_schema_version": 2, "matched_package": matched},
        "provenance": policy["provenance"]}
    if backend["status"] == "official":
        backend["version_output"] = b.codex_version_output(actual)
        backend["authenticode_status"] = b.pe_authenticode_status(actual)
    if backend["status"] == "patched":
        patched = policy["patched"]
        if (b.pe_authenticode_status(actual) != patched["authenticode_status"]
                or b.codex_version_output(actual) != patched["version_output"]):
            raise ValueError("8622 backend version or PE signature differs")
        backend["patched"] = {k: patched[k] for k in
            ("size", "sha256", "pe_machine", "authenticode_status", "version_output")}
    changes = [{"path": e["path"], "patched_sha256": e["portable_sha256"], "size": e["length"]}
               for e in frontend["actual_javascript"]["source_and_archive"]["transformations"]]
    expected = make_manifest(source, app, app, frontend, integrity, backend, changes)
    # Launch/runtime results are appended by the locked manager. They do not
    # replace any immutable provenance or semantic qualification.
    mutable = {"created_at", "validation", "runtime_validation", "launch_validation"}
    for key, value in expected.items():
        if key not in mutable and manifest.get(key) != value:
            raise ValueError("8622 manifest field differs: " + key)
    return {"ok": True, "package_version": base.VERSION, "launch_mode": "portable",
        "portable_asar_sha256": TARGET_ASAR_SHA256, "backend_status": backend["status"],
        "frontend_feature_count": len(all_features())}
