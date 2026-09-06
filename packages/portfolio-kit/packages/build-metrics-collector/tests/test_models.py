from __future__ import annotations

import unittest

from build_metrics_collector.models import AdapterResult, Event, EventError, parse_timestamp

from tests.helpers import event


class ModelTests(unittest.TestCase):
    def test_commit_event_is_valid(self) -> None:
        value = event("commit", {"sha": "a" * 40, "additions": 4, "deletions": 2})
        self.assertEqual(value.type, "commit")

    def test_unknown_event_field_is_rejected(self) -> None:
        raw = event("commit", {"sha": "a" * 40}).as_dict()
        raw["extra"] = True
        with self.assertRaisesRegex(EventError, "fields mismatch"):
            Event.from_dict(raw)

    def test_timestamp_requires_timezone(self) -> None:
        with self.assertRaisesRegex(EventError, "timezone"):
            parse_timestamp("2026-08-15T10:00:00")

    def test_test_counts_may_not_exceed_total(self) -> None:
        with self.assertRaisesRegex(EventError, "may not exceed"):
            event("test_run", {"total": 1, "passed": 1, "failed": 1, "skipped": 0, "duration_seconds": 1})

    def test_retry_attempt_starts_at_two(self) -> None:
        with self.assertRaisesRegex(EventError, "from 2"):
            event("retry", {"operation": "tests", "attempt": 1, "reason": "synthetic"})

    def test_artifact_parent_traversal_is_rejected(self) -> None:
        with self.assertRaisesRegex(EventError, "safe relative"):
            event("artifact", {"path": "../outside", "size_bytes": 1, "sha256": "0" * 64, "kind": "build"})

    def test_human_intervention_is_valid(self) -> None:
        value = event("human_intervention", {"category": "review", "minutes": 12.5, "description": "synthetic review"})
        self.assertEqual(value.data["minutes"], 12.5)

    def test_adapter_state_is_closed_vocabulary(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid adapter state"):
            AdapterResult("mystery", (), (), {})


if __name__ == "__main__":
    unittest.main()

