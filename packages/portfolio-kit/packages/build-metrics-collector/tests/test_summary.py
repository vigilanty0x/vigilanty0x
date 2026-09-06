from __future__ import annotations

import unittest

from build_metrics_collector.summary import summarize

from tests.helpers import event


class SummaryTests(unittest.TestCase):
    def test_empty_project_is_explicit(self) -> None:
        summary = summarize((), project="demo", store_head_hash="0" * 64)
        self.assertEqual(summary.state, "empty")
        self.assertEqual(summary.metrics["commits"], 0)

    def test_metrics_are_aggregated(self) -> None:
        events = (
            event("commit", {"sha": "a" * 40, "additions": 10, "deletions": 2}, key="commit"),
            event(
                "test_run",
                {"total": 10, "passed": 8, "failed": 1, "skipped": 1, "duration_seconds": 4.5},
                key="tests",
            ),
            event("retry", {"operation": "tests", "attempt": 2, "reason": "synthetic failure"}, key="retry"),
            event(
                "artifact",
                {"path": "dist/app.whl", "size_bytes": 100, "sha256": "0" * 64, "kind": "wheel"},
                key="artifact",
            ),
            event(
                "human_intervention",
                {"category": "review", "minutes": 15, "description": "synthetic review"},
                key="human",
            ),
        )
        metrics = summarize(events, project="demo").metrics
        self.assertEqual(metrics["commits"], 1)
        self.assertEqual(metrics["test_pass_rate"], 80.0)
        self.assertEqual(metrics["retries_per_commit"], 1.0)
        self.assertEqual(metrics["human_minutes"], 15.0)

    def test_complete_session_has_duration(self) -> None:
        events = (
            event("session_started", {"session_id": "s1"}, key="start", occurred_at="2026-08-15T10:00:00Z"),
            event("session_ended", {"session_id": "s1"}, key="end", occurred_at="2026-08-15T10:02:00Z"),
        )
        summary = summarize(events)
        self.assertEqual(summary.metrics["build_seconds"], 120.0)
        self.assertEqual(summary.state, "success")

    def test_incomplete_session_is_degraded(self) -> None:
        summary = summarize((event("session_started", {"session_id": "s1"}),))
        self.assertEqual(summary.state, "degraded")
        self.assertEqual(summary.diagnostics, ("SESSION_INCOMPLETE:s1",))

    def test_multiple_projects_require_selection(self) -> None:
        events = (
            event("commit", {"sha": "a" * 40}, key="a", project="one"),
            event("commit", {"sha": "b" * 40}, key="b", project="two"),
        )
        summary = summarize(events)
        self.assertEqual((summary.state, summary.diagnostics), ("error", ("PROJECT_REQUIRED",)))

    def test_project_filter_is_exact(self) -> None:
        events = (
            event("commit", {"sha": "a" * 40}, key="a", project="one"),
            event("commit", {"sha": "b" * 40}, key="b", project="two"),
        )
        self.assertEqual(summarize(events, project="two").metrics["commits"], 1)

    def test_provenance_has_sources_and_freshness(self) -> None:
        summary = summarize(
            (event("commit", {"sha": "a" * 40}, key="a", source_kind="git"),),
            store_head_hash="f" * 64,
        )
        self.assertEqual(summary.provenance["source_kinds"], ["git"])
        self.assertEqual(summary.provenance["store_head_hash"], "f" * 64)


if __name__ == "__main__":
    unittest.main()

