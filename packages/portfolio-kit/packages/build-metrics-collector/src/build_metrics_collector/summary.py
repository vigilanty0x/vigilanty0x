"""Deterministic metric derivation and provenance."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Iterable

from .models import Event, Summary, parse_timestamp


def summarize(
    events: Iterable[Event],
    *,
    project: str | None = None,
    store_head_hash: str | None = None,
) -> Summary:
    all_events = tuple(events)
    projects = sorted({event.project for event in all_events})
    if project is None:
        if len(projects) > 1:
            return Summary(
                project="multiple",
                state="error",
                metrics=_empty_metrics(),
                provenance={"event_count": len(all_events), "projects": projects, "store_head_hash": store_head_hash},
                diagnostics=("PROJECT_REQUIRED",),
            )
        project = projects[0] if projects else "unknown"
    selected = tuple(event for event in all_events if event.project == project)
    if not selected:
        return Summary(
            project=project,
            state="empty",
            metrics=_empty_metrics(),
            provenance={"event_count": 0, "source_kinds": [], "store_head_hash": store_head_hash},
            diagnostics=(),
        )

    ordered = tuple(sorted(selected, key=lambda event: (parse_timestamp(event.occurred_at), event.event_id)))
    metrics = _empty_metrics()
    metrics["event_count"] = len(ordered)
    commits: set[str] = set()
    sessions: dict[str, list[tuple[str, datetime]]] = defaultdict(list)
    diagnostics: list[str] = []
    for event in ordered:
        data = event.data
        if event.type == "commit":
            commits.add(data["sha"])
            metrics["lines_added"] += int(data.get("additions", 0))
            metrics["lines_deleted"] += int(data.get("deletions", 0))
        elif event.type == "test_run":
            metrics["test_runs"] += 1
            metrics["tests_total"] += int(data["total"])
            metrics["tests_passed"] += int(data["passed"])
            metrics["tests_failed"] += int(data["failed"])
            metrics["tests_skipped"] += int(data["skipped"])
            metrics["test_seconds"] += float(data["duration_seconds"])
        elif event.type == "retry":
            metrics["retries"] += 1
            metrics["maximum_attempt"] = max(int(metrics["maximum_attempt"]), int(data["attempt"]))
        elif event.type == "artifact":
            metrics["artifacts"] += 1
            metrics["artifact_bytes"] += int(data["size_bytes"])
        elif event.type == "human_intervention":
            metrics["human_interventions"] += 1
            metrics["human_minutes"] += float(data["minutes"])
        elif event.type in {"session_started", "session_ended"}:
            sessions[data["session_id"]].append((event.type, parse_timestamp(event.occurred_at)))

    metrics["commits"] = len(commits)
    for session_id, points in sorted(sessions.items()):
        starts = [stamp for kind, stamp in points if kind == "session_started"]
        ends = [stamp for kind, stamp in points if kind == "session_ended"]
        if len(starts) != 1 or len(ends) != 1 or ends[0] < starts[0]:
            diagnostics.append(f"SESSION_INCOMPLETE:{session_id}")
            continue
        metrics["completed_sessions"] += 1
        metrics["build_seconds"] += (ends[0] - starts[0]).total_seconds()
    if metrics["tests_total"]:
        metrics["test_pass_rate"] = round(100 * metrics["tests_passed"] / metrics["tests_total"], 3)
    if metrics["commits"]:
        metrics["retries_per_commit"] = round(metrics["retries"] / metrics["commits"], 3)

    provenance = {
        "event_count": len(ordered),
        "first_event_at": ordered[0].occurred_at,
        "last_event_at": ordered[-1].occurred_at,
        "source_kinds": sorted({event.source["kind"] for event in ordered}),
        "store_head_hash": store_head_hash,
    }
    return Summary(project, "degraded" if diagnostics else "success", metrics, provenance, tuple(diagnostics))


def _empty_metrics() -> dict[str, int | float | None]:
    return {
        "event_count": 0,
        "commits": 0,
        "lines_added": 0,
        "lines_deleted": 0,
        "test_runs": 0,
        "tests_total": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "tests_skipped": 0,
        "test_seconds": 0.0,
        "test_pass_rate": None,
        "retries": 0,
        "maximum_attempt": 0,
        "retries_per_commit": None,
        "artifacts": 0,
        "artifact_bytes": 0,
        "human_interventions": 0,
        "human_minutes": 0.0,
        "completed_sessions": 0,
        "build_seconds": 0.0,
    }

