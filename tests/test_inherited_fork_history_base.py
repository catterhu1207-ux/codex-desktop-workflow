from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from codex_desktop_workflow.paginated_history_base import HistoryInventoryEntry, validate_paginated_start


def encode(records):
    return b"".join(json.dumps(row, separators=(",", ":")).encode() + b"\n" for row in records)


class InheritedForkHistoryBaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        # Windows runners may expose TEMP through an 8.3 path alias.
        self.root = Path(self.temp.name).resolve()
        self.sessions = self.root / "sessions"
        self.archived = self.root / "archived_sessions"
        self.sessions.mkdir()
        self.archived.mkdir()
        self.a = "11111111-1111-4111-8111-111111111111"
        self.b = "22222222-2222-4222-8222-222222222222"
        self.c = "33333333-3333-4333-8333-333333333333"
        self.d = "44444444-4444-4444-8444-444444444444"
        self.other = "55555555-5555-4555-8555-555555555555"
        self.paths = {}
        self.records = {}
        self.inventory = {}
        self.create(self.a, 0, 9)
        self.create(self.b, 5, 7, base=self.a, logical=self.a, archived=True)
        self.create(self.c, 3, 4, base=self.a, logical=self.b)

    def create(self, identity, start, last, base=None, logical=None, archived=False):
        meta = {"id": identity, "history_mode": "paginated"}
        if base is not None:
            meta["history_base"] = {
                "thread_id": base,
                "end_ordinal_exclusive": start,
                "end_byte_offset": self.boundary(base, start),
            }
        if logical is not None:
            meta["forked_from_id"] = logical
            meta["forked_from_ordinal_exclusive"] = start
        self.records[identity] = [
            {"ordinal": start, "type": "session_meta", "payload": meta},
            *({"ordinal": i, "type": "event_msg", "payload": {"type": "fixture"}}
              for i in range(start + 1, last + 1)),
        ]
        self.paths[identity] = (self.archived if archived else self.sessions) / f"rollout-{identity}.jsonl"
        self.write(identity)
        entry = HistoryInventoryEntry(self.paths[identity], archived, "paginated")
        self.inventory[identity] = entry
        self.inventory[f"registered::{identity}"] = entry

    def boundary(self, identity, ordinal):
        return len(encode([r for r in self.records[identity] if r["ordinal"] < ordinal]))

    def write(self, identity):
        self.paths[identity].write_bytes(encode(self.records[identity]))

    def prove(self):
        path = self.paths[self.c]
        return validate_paginated_start(
            self.c, self.records[self.c][0],
            (path.stat().st_size, self.records[self.c][-1]["ordinal"] + 1),
            path.stat().st_size, self.inventory, (self.sessions, self.archived),
            ValueError, path,
        )

    def test_original_fork_of_archived_logical_parent_has_exact_ancestor_prefix(self):
        original = {p: p.read_bytes() for p in self.paths.values()}
        proof = self.prove()
        self.assertEqual(proof.kind, "fork")
        self.assertEqual(proof.base_thread_id, self.a)
        self.assertEqual(proof.start_ordinal, 3)
        self.assertEqual(proof.lineage_parent_sha256, tuple(
            (self.paths[identity], hashlib.sha256(original[self.paths[identity]]).hexdigest())
            for identity in (self.b, self.a)
        ))
        self.assertEqual(original, {p: p.read_bytes() for p in original})

    def test_multiple_inherited_segments_are_proven_in_order(self):
        self.create(self.d, 7, 8, base=self.b, logical=self.b)
        self.records[self.c][0]["payload"]["forked_from_id"] = self.d
        self.write(self.c)
        proof = self.prove()
        self.assertEqual([p for p, _ in proof.lineage_parent_sha256],
                         [self.paths[i] for i in (self.d, self.b, self.a)])

    def test_legacy_direct_parent_without_new_cutoff_remains_accepted(self):
        meta = self.records[self.c][0]["payload"]
        meta["forked_from_id"] = self.a
        del meta["forked_from_ordinal_exclusive"]
        self.write(self.c)
        self.assertEqual(self.prove().kind, "fork")
        self.assertEqual(self.prove().lineage_parent_sha256, ())

    def test_registered_parent_segment_preserves_filename_owner(self):
        original = self.paths[self.b]
        segment = original.with_name(f"rollout-{self.b}_{self.other}.jsonl")
        segment.write_bytes(original.read_bytes())
        self.paths[self.b] = segment
        self.inventory[f"registered::{self.b}"] = HistoryInventoryEntry(segment, True, "paginated")
        proof = self.prove()
        self.assertEqual([p for p, _ in proof.lineage_parent_sha256],
                         [segment, self.paths[self.a]])

    def test_intermediate_filename_owner_mismatch_is_rejected(self):
        self.create(self.d, 7, 8, base=self.b, logical=self.b)
        self.records[self.c][0]["payload"]["forked_from_id"] = self.d
        self.write(self.c)
        # Keep both the UUID width and every byte boundary unchanged.
        size = self.paths[self.b].stat().st_size
        self.records[self.b][0]["payload"]["id"] = self.other
        self.write(self.b)
        self.assertEqual(self.paths[self.b].stat().st_size, size)
        with self.assertRaisesRegex(ValueError, "lineage identity"):
            self.prove()

    def test_indirect_fork_requires_exact_integer_cutoff(self):
        meta = self.records[self.c][0]["payload"]
        for value in (None, True, False, -1, 0, 2, 4, 3.0, "3"):
            with self.subTest(value=value):
                meta["forked_from_ordinal_exclusive"] = value
                self.write(self.c)
                with self.assertRaisesRegex(ValueError, "Inherited fork boundary"):
                    self.prove()
        del meta["forked_from_ordinal_exclusive"]
        self.write(self.c)
        with self.assertRaisesRegex(ValueError, "Inherited fork boundary"):
            self.prove()

    def test_indirect_replacement_rollout_is_not_inferred(self):
        old = self.paths[self.c]
        self.paths[self.c] = self.sessions / f"rollout-{self.c}_{self.other}.jsonl"
        self.paths[self.c].write_bytes(old.read_bytes())
        with self.assertRaisesRegex(ValueError, "Inherited fork boundary"):
            self.prove()

    def test_unregistered_logical_parent_is_rejected(self):
        self.inventory.pop(f"registered::{self.b}")
        with self.assertRaisesRegex(ValueError, "logical parent is not registered"):
            self.prove()

    def test_unrelated_registered_parent_is_rejected(self):
        self.create(self.other, 0, 7)
        self.records[self.c][0]["payload"]["forked_from_id"] = self.other
        self.write(self.c)
        with self.assertRaisesRegex(ValueError, "history base lineage"):
            self.prove()

    def test_logical_parent_identity_mismatch_is_rejected(self):
        self.records[self.b][0]["payload"]["id"] = self.other
        self.write(self.b)
        with self.assertRaisesRegex(ValueError, "lineage identity"):
            self.prove()

    def test_logical_parent_mode_must_be_paginated(self):
        self.inventory[f"registered::{self.b}"] = HistoryInventoryEntry(self.paths[self.b], True, "legacy")
        with self.assertRaisesRegex(ValueError, "logical parent mode"):
            self.prove()

    def test_logical_parent_path_must_be_managed(self):
        outside = self.root / f"rollout-{self.b}.jsonl"
        outside.write_bytes(self.paths[self.b].read_bytes())
        self.inventory[f"registered::{self.b}"] = HistoryInventoryEntry(outside, True, "paginated")
        with self.assertRaisesRegex(ValueError, "lineage path"):
            self.prove()

    def test_missing_logical_parent_path_is_rejected(self):
        missing = self.archived / f"missing-{self.b}.jsonl"
        self.inventory[f"registered::{self.b}"] = HistoryInventoryEntry(missing, True, "paginated")
        with self.assertRaisesRegex(ValueError, "lineage path"):
            self.prove()

    def test_duplicate_rollout_identity_is_rejected(self):
        duplicate = self.sessions / f"duplicate-{self.b}.jsonl"
        duplicate.write_bytes(self.paths[self.b].read_bytes())
        with self.assertRaisesRegex(ValueError, "2 source rollouts"):
            self.prove()

    def test_child_boundary_beyond_logical_parent_inheritance_is_rejected(self):
        self.create(self.c, 6, 7, base=self.a, logical=self.b)
        with self.assertRaisesRegex(ValueError, "exceeds parent history"):
            self.prove()

    def test_intermediate_byte_boundary_is_checked(self):
        self.records[self.b][0]["payload"]["history_base"]["end_byte_offset"] -= 1
        self.write(self.b)
        with self.assertRaisesRegex(ValueError, "ordinal boundary"):
            self.prove()

    def test_intermediate_exclusive_ordinal_is_checked(self):
        self.records[self.b][0]["payload"]["history_base"]["end_ordinal_exclusive"] = 4
        self.write(self.b)
        with self.assertRaisesRegex(ValueError, "history base lineage"):
            self.prove()

    def test_intermediate_discontinuity_is_rejected(self):
        self.records[self.b][1]["ordinal"] = 7
        self.write(self.b)
        with self.assertRaisesRegex(ValueError, "Non-contiguous"):
            self.prove()

    def test_boolean_intermediate_ordinal_is_rejected(self):
        self.records[self.b][1]["ordinal"] = True
        self.write(self.b)
        with self.assertRaisesRegex(ValueError, "lineage record"):
            self.prove()

    def test_invalid_intermediate_json_is_rejected(self):
        with self.paths[self.b].open("ab") as stream:
            stream.write(b"not-json\n")
        with self.assertRaisesRegex(ValueError, "lineage JSON"):
            self.prove()

    def test_intermediate_cycle_is_rejected(self):
        self.records[self.b][0]["payload"]["history_base"]["thread_id"] = self.b
        self.write(self.b)
        with self.assertRaisesRegex(ValueError, "cyclic"):
            self.prove()

    def test_missing_intermediate_source_is_rejected(self):
        self.records[self.b][0]["payload"]["history_base"]["thread_id"] = self.other
        self.write(self.b)
        with self.assertRaisesRegex(ValueError, "0 source rollouts"):
            self.prove()

    def test_child_self_parent_is_rejected(self):
        self.records[self.c][0]["payload"]["forked_from_id"] = self.c
        self.write(self.c)
        with self.assertRaisesRegex(ValueError, "Inherited fork boundary"):
            self.prove()


if __name__ == "__main__":
    unittest.main()
