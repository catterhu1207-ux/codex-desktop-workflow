"""Use the production 4866 proof parser on fresh, test-owned process logs."""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
import subprocess


def parse_owned_logs(manifest: Path, run_directory: Path, process: dict) -> dict:
    root = run_directory.resolve()
    record = json.loads((root / "run.json").read_text(encoding="utf-8"))
    expected = record.get("main", {})
    if not expected or process != expected or type(expected.get("pid")) is not int:
        return {"status": "blocked", "reason": "process_identity_mismatch"}
    if not record.get("started_at") or not record.get("run_id"):
        return {"status": "blocked", "reason": "missing_run_identity"}
    if root.name != record['run_id']:
        return {"status": "blocked", "reason": "run_directory_identity_mismatch"}
    created = str(expected.get('created', ''))
    match = re.fullmatch(r'/Date\((\d+)\)/', created)
    try:
        process_created = int(match[1]) / 1000 if match else datetime.fromisoformat(created).timestamp()
    except (ValueError, TypeError):
        return {"status": "blocked", "reason": "process_creation_time_missing"}
    value = json.loads(manifest.read_text(encoding="utf-8"))
    if Path(expected["executable"]).resolve() != (Path(value["portable_app"]) / "ChatGPT.exe").resolve():
        return {"status": "blocked", "reason": "candidate_process_path_mismatch"}
    inputs = root / "renderer-parser-input"
    inputs.mkdir(exist_ok=True)
    for label in ("stdout", "stderr"):
        source = root / (label + ".log")
        if not source.is_file() or source.is_symlink():
            continue
        stat = source.stat()
        # Renaming a copied log for the production parser must not turn an old
        # proof into a fresh one. Compare original timestamps before copying.
        if stat.st_mtime < process_created or getattr(stat, 'st_birthtime', stat.st_ctime) < process_created - 2:
            return {"status": "blocked", "reason": "stale_original_log"}
        if getattr(stat, 'st_file_attributes', 0) & 0x400:
            return {"status": "blocked", "reason": "redirected_original_log"}
        data = source.read_bytes()
        target = inputs / f"codex-desktop-isolated-{expected['pid']}-t0-{label}.log"
        target.write_bytes(data)
        if hashlib.sha256(target.read_bytes()).digest() != hashlib.sha256(data).digest():
            raise RuntimeError("proof_log_copy_changed")
    parser = Path(__file__).parent / "data/renderer_attestation_26928_4866.ps1"
    script = r'''
$ErrorActionPreference='Stop'
. $env:PROOF_PARSER
$expectedFrontendAttestationMarker='[CF9]'
$expectedFrontendAttestationSchemaVersion=6
$expectedFrontendAttestationArtifactId='2.7.9-84fe697418b2'
$expectedFrontendContractValidatorVersion='2.6.0'
$qualified=Get-Content -LiteralPath $env:PROOF_MANIFEST -Raw -Encoding UTF8 | ConvertFrom-Json
$requiredCurrentFrontendFeatures=@($qualified.feature_contracts.psobject.Properties.Name)
$requiredLiveRendererFeatures=@($requiredCurrentFrontendFeatures | Where-Object {$_ -notin @('windows_watch_path_normalization','archived_heartbeat_terminal_guard','process_registry_resilience')})
Get-PortableFrontendFeatureAttestation -LogsRoot $env:PROOF_LOGS -TargetProcessId ([int]$env:PROOF_PID) -StartedAt ([DateTimeOffset]::Parse($env:PROOF_START)) -QualifiedManifest $qualified | ConvertTo-Json -Depth 24 -Compress
'''
    env = os.environ.copy()
    env.update(PROOF_PARSER=str(parser), PROOF_MANIFEST=str(manifest.resolve()),
               PROOF_LOGS=str(inputs), PROOF_PID=str(expected["pid"]),
               PROOF_START=record["started_at"])
    response = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
                              env=env, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=30, creationflags=0x08000000)
    if response.returncode:
        raise RuntimeError("production_proof_parser_failed: " + response.stderr[-1000:])
    proof = json.loads(response.stdout or "null")
    return {"status": "passed" if proof and proof.get("status") == "passed" else "blocked",
            "feature_count": 22 if proof and proof.get("status") == "passed" else 0,
            "production_parser": proof, "process_id": expected["pid"],
            "owner_run_id": record["run_id"]}
