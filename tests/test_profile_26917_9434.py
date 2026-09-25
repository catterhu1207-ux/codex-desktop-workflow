"""Run the release contracts against an explicitly supplied real 9434 artifact."""
from pathlib import Path
import os
import unittest

import hotfix_builder as builder
import hotfix_profile_26917_9434 as profile
from frontend_feature_contracts import ContractError
from frontend_contract_26917_9434 import (
    require_feature_signatures,
    require_routes,
    run_drop,
    run_protocol,
    run_semantics,
)
from frontend_work_contract_26917_9434 import PICKER_PATH, run as run_work


class ExactProfile9434(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("CODEX_WORKFLOW_TEST_ASAR_9434")
        if not value:
            raise unittest.SkipTest("Set CODEX_WORKFLOW_TEST_ASAR_9434 to the exact built artifact")
        path = Path(value)
        if not path.is_file():
            raise RuntimeError("Explicit artifact does not exist")
        header_size, _, header = builder.read_asar(path)
        read = lambda name: builder.read_entry(path, header_size, builder.get_entry_meta(header, name))[1]
        cls.initial = read(profile.PROFILE["entry_path"])
        cls.primary = read(profile.PROFILE["secondary_entry_path"])
        cls.protocol = read(profile.PROFILE["attestation_protocol_entry_path"])
        cls.picker = read(PICKER_PATH)

    def test_actual_bundle_and_routes(self):
        require_feature_signatures(self.initial, self.primary)
        require_routes(self.initial, self.primary)
        self.assertEqual(run_semantics(self.initial, self.primary)["status"], "passed")
        self.assertEqual(run_work(self.initial, self.primary, self.picker)["status"], "passed")
        self.assertEqual(run_protocol(self.protocol, "node")["status"], "passed")
        self.assertEqual(run_drop(self.initial, self.primary, "node")["status"], "passed")

    def test_live_sort_patch_is_required(self):
        old, new = profile.PAIRS["priority_filter_live_resort"][0]
        self.assertEqual(self.initial.count(new), 1)
        with self.assertRaises(ContractError):
            require_feature_signatures(self.initial.replace(new, old, 1), self.primary)

    def test_route_cannot_point_to_missing_picker(self):
        route = b"import(`./composer-project-picker-content-38b3bdacb67c.js`)"
        self.assertEqual(self.primary.count(route), 1)
        with self.assertRaises(ContractError):
            require_routes(self.initial, self.primary.replace(route, b"import(`./missing.js`)", 1))

    def test_plan_pending_source_is_required(self):
        route = b"xt=st?.pendingRequest"
        self.assertEqual(self.initial.count(route), 1)
        with self.assertRaises(ContractError):
            require_routes(self.initial.replace(route, b"xt=st?.displayValue", 1), self.primary)


if __name__ == "__main__":
    unittest.main()
