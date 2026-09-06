"""Bounded local adapters with normalized success states."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any
import uuid
import xml.etree.ElementTree as ET

from .models import AdapterResult, Event

MAX_ADAPTER_FILE_BYTES = 64 * 1024 * 1024


def _timestamp_from_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _event(
    *,
    project: str,
    event_type: str,
    occurred_at: str,
    source_kind: str,
    source_uri: str,
    idempotency_key: str,
    data: dict[str, Any],
) -> Event:
    raw = {
        "event_version": "1.0",
        "event_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"build-metrics:{idempotency_key}")),
        "idempotency_key": idempotency_key,
        "project": project,
        "type": event_type,
        "occurred_at": occurred_at,
        "source": {"kind": source_kind, "uri": source_uri},
        "data": data,
    }
    return Event.from_dict(raw)


def collect_git(
    root: str | Path,
    *,
    project: str,
    timeout_seconds: int = 10,
    max_commits: int = 1000,
) -> AdapterResult:
    root_path = Path(root)
    provenance = {"adapter": "git", "root": root_path.name or ".", "max_commits": max_commits}
    if not root_path.is_dir():
        return AdapterResult("error", (), ("GIT_ROOT_INVALID",), provenance)
    if not 1 <= timeout_seconds <= 300 or not 1 <= max_commits <= 10_000:
        return AdapterResult("error", (), ("GIT_BOUNDS_INVALID",), provenance)
    command = [
        "git",
        "-C",
        str(root_path),
        "log",
        f"--max-count={max_commits}",
        "--format=%H%x09%cI",
    ]
    try:
        completed = subprocess.run(command, check=False, capture_output=True, timeout=timeout_seconds, shell=False)
    except subprocess.TimeoutExpired:
        return AdapterResult("timeout", (), ("GIT_TIMEOUT",), provenance)
    except OSError as exc:
        return AdapterResult("error", (), (f"GIT_START_FAILED:{type(exc).__name__}",), provenance)
    if completed.returncode != 0:
        return AdapterResult("error", (), (f"GIT_EXIT_{completed.returncode}",), provenance)
    text = completed.stdout.decode("utf-8", "replace")
    if not text.strip():
        return AdapterResult("empty", (), (), provenance)
    events: list[Event] = []
    diagnostics: list[str] = []
    for index, line in enumerate(text.splitlines(), start=1):
        try:
            sha, occurred_at = line.split("\t", 1)
            events.append(
                _event(
                    project=project,
                    event_type="commit",
                    occurred_at=occurred_at,
                    source_kind="git",
                    source_uri="git:.",
                    idempotency_key=f"git:{sha}",
                    data={"sha": sha},
                )
            )
        except (ValueError, IndexError):
            diagnostics.append(f"GIT_LINE_INVALID:{index}")
    if events and diagnostics:
        state = "degraded"
    elif events:
        state = "success"
    else:
        state = "error"
    return AdapterResult(state, tuple(events), tuple(diagnostics), provenance)


def ingest_junit(path: str | Path, *, project: str, suite: str | None = None) -> AdapterResult:
    report_path = Path(path)
    provenance = {"adapter": "junit", "file": report_path.name}
    try:
        size = report_path.stat().st_size
        if size > MAX_ADAPTER_FILE_BYTES:
            return AdapterResult("error", (), ("JUNIT_TOO_LARGE",), provenance)
        root = ET.fromstring(report_path.read_bytes())
        occurred_at = _timestamp_from_mtime(report_path)
    except (OSError, ET.ParseError) as exc:
        return AdapterResult("error", (), (f"JUNIT_INVALID:{type(exc).__name__}",), provenance)
    suites = [root] if root.tag.endswith("testsuite") else [child for child in root if child.tag.endswith("testsuite")]
    if not suites:
        return AdapterResult("empty", (), ("JUNIT_NO_SUITES",), provenance)
    totals = {"total": 0, "failed": 0, "skipped": 0, "duration_seconds": 0.0}
    diagnostics: list[str] = []
    for index, item in enumerate(suites, start=1):
        try:
            totals["total"] += int(item.attrib.get("tests", "0"))
            totals["failed"] += int(item.attrib.get("failures", "0")) + int(item.attrib.get("errors", "0"))
            totals["skipped"] += int(item.attrib.get("skipped", item.attrib.get("disabled", "0")))
            totals["duration_seconds"] += float(item.attrib.get("time", "0"))
        except ValueError:
            diagnostics.append(f"JUNIT_SUITE_INVALID:{index}")
    if totals["total"] == 0 and not diagnostics:
        return AdapterResult("empty", (), (), provenance)
    passed = max(0, int(totals["total"] - totals["failed"] - totals["skipped"]))
    data: dict[str, Any] = {
        "total": int(totals["total"]),
        "passed": passed,
        "failed": int(totals["failed"]),
        "skipped": int(totals["skipped"]),
        "duration_seconds": round(float(totals["duration_seconds"]), 6),
    }
    if suite:
        data["suite"] = suite
    digest = hashlib.sha256(report_path.read_bytes()).hexdigest()
    event = _event(
        project=project,
        event_type="test_run",
        occurred_at=occurred_at,
        source_kind="junit",
        source_uri=f"file:{report_path.name}",
        idempotency_key=f"junit:{digest}",
        data=data,
    )
    return AdapterResult("degraded" if diagnostics else "success", (event,), tuple(diagnostics), provenance)


def collect_artifact(
    root: str | Path,
    relative_path: str,
    *,
    project: str,
    kind: str = "build",
) -> AdapterResult:
    root_path = Path(root).resolve()
    normalized = relative_path.replace("\\", "/")
    candidate = (root_path / normalized).resolve()
    provenance = {"adapter": "artifact", "root": root_path.name or ".", "file": normalized}
    if candidate != root_path and root_path not in candidate.parents:
        return AdapterResult("error", (), ("ARTIFACT_PATH_ESCAPE",), provenance)
    try:
        size = candidate.stat().st_size
        if not candidate.is_file():
            return AdapterResult("empty", (), ("ARTIFACT_NOT_FILE",), provenance)
        if size > MAX_ADAPTER_FILE_BYTES:
            return AdapterResult("error", (), ("ARTIFACT_TOO_LARGE",), provenance)
        content = candidate.read_bytes()
        occurred_at = _timestamp_from_mtime(candidate)
    except OSError as exc:
        return AdapterResult("error", (), (f"ARTIFACT_UNREADABLE:{type(exc).__name__}",), provenance)
    digest = hashlib.sha256(content).hexdigest()
    event = _event(
        project=project,
        event_type="artifact",
        occurred_at=occurred_at,
        source_kind="filesystem",
        source_uri=f"file:{normalized}",
        idempotency_key=f"artifact:{digest}:{normalized}",
        data={"path": normalized, "size_bytes": size, "sha256": digest, "kind": kind},
    )
    return AdapterResult("success", (event,), (), provenance)


def load_event_json(path: str | Path) -> Event:
    event_path = Path(path)
    if event_path.stat().st_size > 1024 * 1024:
        raise ValueError("event JSON exceeds 1048576 bytes")
    return Event.from_dict(json.loads(event_path.read_text(encoding="utf-8")))

