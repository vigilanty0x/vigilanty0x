from __future__ import annotations

import unittest

from build_metrics_collector.models import Summary
from build_metrics_collector.render import render_html


def summary(state: str = "success") -> Summary:
    return Summary(
        project="Synthetic <project>",
        state=state,
        metrics={
            "commits": 3,
            "tests_total": 10,
            "test_pass_rate": 90.0,
            "retries": 1,
            "artifacts": 2,
            "human_interventions": 1,
            "human_minutes": 12.0,
            "build_seconds": 42.0,
        },
        provenance={
            "event_count": 5,
            "last_event_at": "2026-08-15T10:00:00Z",
            "source_kinds": ["git", "junit"],
            "store_head_hash": "a" * 64,
        },
        diagnostics=("SYNTHETIC_DIAGNOSTIC",) if state == "degraded" else (),
    )


class RenderTests(unittest.TestCase):
    def test_html_escapes_project(self) -> None:
        html = render_html(summary())
        self.assertIn("Synthetic &lt;project&gt;", html)
        self.assertNotIn("Synthetic <project>", html)

    def test_semantics_and_keyboard_focus_are_present(self) -> None:
        html = render_html(summary())
        for marker in ('<main id="metrics"', "aria-labelledby", "focus-visible", 'href="#metrics"'):
            self.assertIn(marker, html)

    def test_mobile_and_reduced_motion_styles_are_present(self) -> None:
        html = render_html(summary())
        self.assertIn("@media (max-width:32rem)", html)
        self.assertIn("prefers-reduced-motion", html)
        self.assertIn('name="viewport"', html)

    def test_download_action_is_functional_and_no_button_exists(self) -> None:
        html = render_html(summary())
        self.assertIn("data:application/json", html)
        self.assertIn("download=", html)
        self.assertNotIn("<button", html)

    def test_all_view_states_have_explicit_copy(self) -> None:
        expected = {
            "success": "All recorded events",
            "loading": "no completion claim",
            "empty": "No events are available",
            "degraded": "one or more sessions",
            "timeout": "exceeded its reviewed time limit",
            "error": "could not be normalized",
        }
        for state, phrase in expected.items():
            with self.subTest(state=state):
                self.assertIn(phrase, render_html(summary(state)))

    def test_provenance_and_freshness_are_visible(self) -> None:
        html = render_html(summary())
        self.assertIn("Provenance and freshness", html)
        self.assertIn('<time datetime="2026-08-15T10:00:00Z">', html)
        self.assertIn("git, junit", html)


if __name__ == "__main__":
    unittest.main()
