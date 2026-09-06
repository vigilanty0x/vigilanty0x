import copy
import json
import unittest
from pathlib import Path

from scripts.check_portfolio_kit import validate

ROOT = Path(__file__).resolve().parents[1]
BASELINE = json.loads((ROOT / "PORTFOLIO_KIT.json").read_text(encoding="utf-8"))


class PortfolioKitContractTests(unittest.TestCase):
    def candidate(self):
        return copy.deepcopy(BASELINE)

    def assert_rejected(self, mutate, fragment):
        candidate = self.candidate()
        mutate(candidate)
        errors = validate(candidate, ROOT)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_baseline_is_valid(self):
        self.assertEqual(validate(BASELINE, ROOT), [])

    def test_counterproof_rejects_seventeenth_entity(self):
        self.assert_rejected(
            lambda data: data["architecture"]["entities"].append({"id": "extra", "repositories": ["extra"]}),
            "exactly 16",
        )

    def test_counterproof_rejects_active_repository_drift(self):
        self.assert_rejected(
            lambda data: data["architecture"]["activeRepositories"].__setitem__(0, "not-canonical"),
            "canonical set",
        )

    def test_counterproof_rejects_source_module_promoted_to_final_active_set(self):
        def mutate(data):
            data["architecture"]["activeRepositories"][-1] = "github-profile-dashboard"
        self.assert_rejected(mutate, "canonical set")

    def test_counterproof_rejects_lost_source_history_evidence(self):
        self.assert_rejected(
            lambda data: data["modules"][0].__setitem__("historyPreserved", False),
            "historyPreserved=true",
        )

    def test_counterproof_rejects_tree_mismatch(self):
        self.assert_rejected(
            lambda data: data["modules"][1].__setitem__("treeMatch", False),
            "treeMatch=true",
        )

    def test_counterproof_rejects_automatic_archive(self):
        self.assert_rejected(
            lambda data: data["archive"].__setitem__("automatic", True),
            "never be automatic",
        )

    def test_counterproof_rejects_missing_rollback_gate(self):
        self.assert_rejected(
            lambda data: data["archive"].__setitem__(
                "required", [gate for gate in data["archive"]["required"] if gate != "rollback"]
            ),
            "archive required gates",
        )

    def test_counterproof_rejects_malformed_governance_sha(self):
        self.assert_rejected(
            lambda data: data["governance"].__setitem__("commit", "main"),
            "exact 40-character SHA",
        )


if __name__ == "__main__":
    unittest.main()
