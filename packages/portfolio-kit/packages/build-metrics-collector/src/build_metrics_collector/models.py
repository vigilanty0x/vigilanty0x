"""Versioned event, adapter, and view contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any

EVENT_TYPES = {
    "session_started",
    "session_ended",
    "commit",
    "test_run",
    "retry",
    "artifact",
    "human_intervention",
}
ADAPTER_STATES = {"success", "empty", "degraded", "timeout", "error"}


class EventError(ValueError):
    pass


def parse_timestamp(value: Any, label: str = "occurred_at") -> datetime:
    if not isinstance(value, str) or len(value) > 64:
        raise EventError(f"{label} must be an ISO 8601 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EventError(f"{label} must be valid ISO 8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise EventError(f"{label} must include a timezone")
    return parsed


def _nonnegative(value: Any, label: str, *, maximum: int | float = 10**12) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0 or value > maximum:
        raise EventError(f"{label} must be a non-negative number up to {maximum}")
    return value


def _text(value: Any, label: str, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise EventError(f"{label} must be a non-empty string up to {maximum} characters")
    return value


@dataclass(frozen=True)
class Event:
    event_id: str
    idempotency_key: str
    project: str
    type: str
    occurred_at: str
    source: dict[str, Any]
    data: dict[str, Any]

    @classmethod
    def from_dict(cls, raw: Any) -> "Event":
        if not isinstance(raw, dict):
            raise EventError("event must be an object")
        required = {"event_version", "event_id", "idempotency_key", "project", "type", "occurred_at", "source", "data"}
        if set(raw) != required:
            missing = sorted(required - set(raw))
            unknown = sorted(set(raw) - required)
            raise EventError(f"event fields mismatch; missing={missing}, unknown={unknown}")
        if raw["event_version"] != "1.0":
            raise EventError("event_version must be '1.0'")
        event_id = _text(raw["event_id"], "event_id", 128)
        key = _text(raw["idempotency_key"], "idempotency_key", 256)
        project = _text(raw["project"], "project", 128)
        event_type = raw["type"]
        if event_type not in EVENT_TYPES:
            raise EventError("type is not in the event 1.0 vocabulary")
        parse_timestamp(raw["occurred_at"])
        source = raw["source"]
        if not isinstance(source, dict) or set(source) != {"kind", "uri"}:
            raise EventError("source must contain exactly kind and uri")
        _text(source["kind"], "source.kind", 64)
        _text(source["uri"], "source.uri", 512)
        data = raw["data"]
        if not isinstance(data, dict):
            raise EventError("data must be an object")
        cls._validate_data(event_type, data)
        return cls(event_id, key, project, event_type, raw["occurred_at"], dict(source), dict(data))

    @staticmethod
    def _validate_data(event_type: str, data: dict[str, Any]) -> None:
        allowed: dict[str, set[str]] = {
            "session_started": {"session_id"},
            "session_ended": {"session_id"},
            "commit": {"sha", "additions", "deletions"},
            "test_run": {"total", "passed", "failed", "skipped", "duration_seconds", "suite"},
            "retry": {"operation", "attempt", "reason"},
            "artifact": {"path", "size_bytes", "sha256", "kind"},
            "human_intervention": {"category", "minutes", "description"},
        }
        required: dict[str, set[str]] = {
            "session_started": {"session_id"},
            "session_ended": {"session_id"},
            "commit": {"sha"},
            "test_run": {"total", "passed", "failed", "skipped", "duration_seconds"},
            "retry": {"operation", "attempt", "reason"},
            "artifact": {"path", "size_bytes", "sha256", "kind"},
            "human_intervention": {"category", "minutes", "description"},
        }
        if set(data) - allowed[event_type] or not required[event_type].issubset(data):
            raise EventError(f"invalid data fields for {event_type}")
        if event_type.startswith("session_"):
            _text(data["session_id"], "data.session_id", 128)
        elif event_type == "commit":
            sha = _text(data["sha"], "data.sha", 64)
            if not 7 <= len(sha) <= 64 or any(char not in "0123456789abcdefABCDEF" for char in sha):
                raise EventError("data.sha must be 7 to 64 hexadecimal characters")
            for field in ("additions", "deletions"):
                if field in data:
                    _nonnegative(data[field], f"data.{field}")
        elif event_type == "test_run":
            values = {}
            for field in ("total", "passed", "failed", "skipped"):
                value = _nonnegative(data[field], f"data.{field}", maximum=10**9)
                if not isinstance(value, int):
                    raise EventError(f"data.{field} must be an integer")
                values[field] = value
            _nonnegative(data["duration_seconds"], "data.duration_seconds", maximum=10**9)
            if values["passed"] + values["failed"] + values["skipped"] > values["total"]:
                raise EventError("test result counts may not exceed total")
            if "suite" in data:
                _text(data["suite"], "data.suite", 256)
        elif event_type == "retry":
            _text(data["operation"], "data.operation", 256)
            attempt = data["attempt"]
            if isinstance(attempt, bool) or not isinstance(attempt, int) or not 2 <= attempt <= 10**6:
                raise EventError("data.attempt must be an integer from 2 to 1000000")
            _text(data["reason"], "data.reason", 512)
        elif event_type == "artifact":
            path = _text(data["path"], "data.path", 512).replace("\\", "/")
            candidate = Path(path)
            if candidate.is_absolute() or ".." in candidate.parts or (len(path) > 1 and path[1] == ":"):
                raise EventError("data.path must be a safe relative path")
            _nonnegative(data["size_bytes"], "data.size_bytes")
            digest = data["sha256"]
            if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdefABCDEF" for c in digest):
                raise EventError("data.sha256 must be a 64-character hexadecimal digest")
            _text(data["kind"], "data.kind", 64)
        else:
            _text(data["category"], "data.category", 128)
            _nonnegative(data["minutes"], "data.minutes", maximum=10**7)
            _text(data["description"], "data.description", 1024)

    def as_dict(self) -> dict[str, Any]:
        return {
            "event_version": "1.0",
            "event_id": self.event_id,
            "idempotency_key": self.idempotency_key,
            "project": self.project,
            "type": self.type,
            "occurred_at": self.occurred_at,
            "source": self.source,
            "data": self.data,
        }


@dataclass(frozen=True)
class AdapterResult:
    state: str
    events: tuple[Event, ...]
    diagnostics: tuple[str, ...]
    provenance: dict[str, Any]

    def __post_init__(self) -> None:
        if self.state not in ADAPTER_STATES:
            raise ValueError("invalid adapter state")

    def as_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "events": [event.as_dict() for event in self.events],
            "diagnostics": list(self.diagnostics),
            "provenance": self.provenance,
        }


@dataclass(frozen=True)
class Summary:
    project: str
    state: str
    metrics: dict[str, int | float | None]
    provenance: dict[str, Any]
    diagnostics: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "view_version": "1.0",
            "project": self.project,
            "state": self.state,
            "metrics": self.metrics,
            "provenance": self.provenance,
            "diagnostics": list(self.diagnostics),
        }

