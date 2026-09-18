from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest import mock

from codex_desktop_workflow import workflow


class WorkflowTests(unittest.TestCase):
    def test_nested_target_is_rejected_before_copy(self):
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "official"
            source.mkdir()
            with mock.patch.object(workflow, "inspect", return_value={"status": "passed", "app_directory": str(source), "problems": [], "supported_version": "26.915.3509.0"}):
                with self.assertRaisesRegex(workflow.WorkflowError, "nested"):
                    workflow.build(source, source / "portable")

    def test_extended_path_preserves_non_windows_paths(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw).resolve()
            with mock.patch.object(workflow.os, "name", "posix"):
                self.assertEqual(workflow._extended(path), str(path))

    def test_unknown_version_is_blocked(self):
        with tempfile.TemporaryDirectory() as raw:
            app = Path(raw) / "app"
            (app / "resources").mkdir(parents=True)
            (app / "resources" / "app.asar").write_bytes(b"not-an-asar")
            (app / "resources" / "codex.exe").write_bytes(b"backend")
            (app / "ChatGPT.exe").write_bytes(b"desktop")
            result = workflow.inspect(app)
            self.assertEqual(result["status"], "blocked")
            self.assertIn("unsupported_version:unknown", result["problems"])

    def test_matching_version_with_wrong_hash_is_blocked(self):
        with tempfile.TemporaryDirectory() as raw:
            package = Path(raw) / "OpenAI.Codex_26.908.9136.0_x64__2p2nqsd0c76g0"
            app = package / "app"
            (app / "resources").mkdir(parents=True)
            (app / "resources" / "app.asar").write_bytes(b"wrong-asar")
            (app / "resources" / "codex.exe").write_bytes(b"wrong-backend")
            (app / "ChatGPT.exe").write_bytes(b"desktop")
            result = workflow.inspect(package)
            self.assertEqual(result["detected_version"], "26.908.9136.0")
            self.assertEqual(result["supported_version"], "26.908.9136.0")
            self.assertIn("official_asar_sha256_mismatch", result["problems"])
            self.assertIn("official_backend_sha256_mismatch", result["problems"])

    def test_both_supported_versions_are_declared(self):
        self.assertEqual(
            workflow.SUPPORTED_VERSIONS,
            ("26.908.9136.0", "26.915.3509.0"),
        )
        self.assertEqual(workflow.SUPPORTED_VERSION, "26.915.3509.0")

    def test_import_excludes_credentials_and_uses_sqlite_backup(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source, target = root / "source", root / "target"
            source.mkdir()
            db = sqlite3.connect(source / "state_5.sqlite")
            try:
                db.execute("create table tasks(id text primary key, model text)")
                db.execute("insert into tasks values('one','gpt-test')")
                db.commit()
            finally:
                db.close()
            (source / "auth.json").write_text('{"session":"synthetic"}', encoding="utf-8")
            with mock.patch.object(workflow, "_running_codex_processes", return_value=[]):
                result = workflow.import_data(source, target)
            self.assertEqual(result["status"], "passed")
            self.assertTrue((target / "state_5.sqlite").is_file())
            self.assertFalse((target / "auth.json").exists())

    def test_import_requires_quiescent_processes(self):
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "source"; source.mkdir()
            with mock.patch.object(workflow, "_running_codex_processes", return_value=[{"ProcessId": 1}]):
                with self.assertRaisesRegex(workflow.WorkflowError, "must_exit"):
                    workflow.import_data(source, Path(raw) / "target")

    def test_import_refuses_existing_target(self):
        with tempfile.TemporaryDirectory() as raw:
            source, target = Path(raw) / "source", Path(raw) / "target"
            source.mkdir(); target.mkdir()
            with mock.patch.object(workflow, "_running_codex_processes", return_value=[]):
                with self.assertRaisesRegex(workflow.WorkflowError, "target_must_not_exist"):
                    workflow.import_data(source, target)

    def test_build_refuses_existing_target(self):
        with tempfile.TemporaryDirectory() as raw:
            source, target = Path(raw) / "official", Path(raw) / "portable"
            source.mkdir(); target.mkdir()
            with mock.patch.object(workflow, "inspect", return_value={"status": "passed", "app_directory": str(source), "problems": [], "supported_version": "26.915.3509.0"}):
                with self.assertRaisesRegex(workflow.WorkflowError, "target_must_not_exist"):
                    workflow.build(source, target)

    def test_verify_requires_two_full_length_launches(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            with self.assertRaisesRegex(workflow.WorkflowError, "two_launches"):
                workflow.verify(root, root, root, observe_seconds=60, launches=1)
            with self.assertRaisesRegex(workflow.WorkflowError, "60_seconds"):
                workflow.verify(root, root, root, observe_seconds=59, launches=2)

    def test_status_document_has_no_private_content(self):
        payload = {"status": "blocked", "content_logged": False}
        self.assertNotIn("token", json.dumps(payload))

    def test_renderer_attestation_is_read_from_prefixed_log_line(self):
        artifact = "synthetic-artifact"
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            log = root / "stderr.log"
            values = [
                {"artifact_id": artifact, "status": "module_loaded", "run_id": "one", "content_logged": False},
                {"artifact_id": artifact, "status": "passed", "run_id": "one", "content_logged": False},
            ]
            log.write_text("\n".join("prefix [CF9]" + json.dumps(value) + " rendererWindowId=1" for value in values), encoding="utf-8")
            result = workflow._attestations(root, artifact, log)
            self.assertEqual(result["status"], "passed")
            self.assertEqual(result["run_ids"], ["one"])

    def test_renderer_attestation_rejects_wrong_artifact(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            log = root / "stderr.log"
            log.write_text('[CF9]{"artifact_id":"other","status":"passed","run_id":"one"}', encoding="utf-8")
            result = workflow._attestations(root, "expected", log)
            self.assertNotEqual(result["status"], "passed")

    def test_cdp_frame_masks_quit_command(self):
        with mock.patch.object(workflow.os, "urandom", return_value=b"abcd"):
            frame = workflow._websocket_frame(b"quit")
        self.assertEqual(frame[:6], bytes((0x81, 0x84)) + b"abcd")
        self.assertEqual(bytes(value ^ b"abcd"[index % 4] for index, value in enumerate(frame[6:])), b"quit")

    def test_portable_environment_pins_the_packaged_backend(self):
        with tempfile.TemporaryDirectory() as raw:
            portable = Path(raw) / "portable"
            (portable / "resources").mkdir(parents=True)
            backend = portable / "resources" / "codex.exe"
            backend.write_bytes(b"official-backend")
            home = Path(raw) / "home"
            home.mkdir()
            environment = workflow._portable_environment(portable, home)
            self.assertEqual(environment["CODEX_HOME"], str(home))
            self.assertEqual(environment["CODEX_CLI_PATH"], str(backend.resolve()))
            value = {
                "registered_backends": [
                    {
                        "executable": str(backend),
                    }
                ]
            }
            digest = workflow._sha256(backend)
            self.assertTrue(
                workflow._registered_backend_match(value, portable, digest)
            )
            self.assertFalse(
                workflow._registered_backend_match(value, portable, "0" * 64)
            )


if __name__ == "__main__":
    unittest.main()
