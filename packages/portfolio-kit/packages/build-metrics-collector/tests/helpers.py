from __future__ import annotations

from typing import Any

from build_metrics_collector.models import Event


def event(
    event_type: str,
    data: dict[str, Any],
    *,
    key: str = "event-1",
    event_id: str | None = None,
    project: str = "demo",
    occurred_at: str = "2026-08-15T10:00:00Z",
    source_kind: str = "synthetic",
) -> Event:
    return Event.from_dict(
        {
            "event_version": "1.0",
            "event_id": event_id or key,
            "idempotency_key": key,
            "project": project,
            "type": event_type,
            "occurred_at": occurred_at,
            "source": {"kind": source_kind, "uri": "synthetic:fixture"},
            "data": data,
        }
    )

