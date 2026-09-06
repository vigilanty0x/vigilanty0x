"""Build Metrics Collector command line interface."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Sequence
import uuid

from . import __version__
from .adapters import collect_artifact, collect_git, ingest_junit, load_event_json
from .models import AdapterResult, Event, EventError
from .render import render_html
from .store import EventStore, StoreError
from .summary import summarize


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="build-metrics", description="Collect reproducible metrics for AI-assisted builds.")
    parser.add_argument("--version", action="version", version=f"build-metrics {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    record = sub.add_parser("record", help="record a validated version 1.0 event")
    record.add_argument("--store", required=True)
    record.add_argument("--project", required=True)
    record.add_argument("--type", required=True)
    record.add_argument("--occurred-at", required=True)
    record.add_argument("--idempotency-key", required=True)
    record.add_argument("--data", required=True, help="JSON object matching the selected event type")

    import_event = sub.add_parser("import-event", help="import a complete event 1.0 JSON file")
    import_event.add_argument("event")
    import_event.add_argument("--store", required=True)

    git = sub.add_parser("collect-git", help="collect bounded local git commit events")
    git.add_argument("path", nargs="?", default=".")
    git.add_argument("--store", required=True)
    git.add_argument("--project", required=True)
    git.add_argument("--timeout", type=int, default=10)
    git.add_argument("--max-commits", type=int, default=1000)

    junit = sub.add_parser("ingest-junit", help="ingest a local JUnit XML report")
    junit.add_argument("report")
    junit.add_argument("--store", required=True)
    junit.add_argument("--project", required=True)
    junit.add_argument("--suite")

    artifact = sub.add_parser("artifact", help="hash and record a bounded local artifact")
    artifact.add_argument("path")
    artifact.add_argument("--root", default=".")
    artifact.add_argument("--store", required=True)
    artifact.add_argument("--project", required=True)
    artifact.add_argument("--kind", default="build")

    summary = sub.add_parser("summarize", help="derive a versioned metric view")
    summary.add_argument("store")
    summary.add_argument("--project")
    summary.add_argument("--format", choices=("json", "html"), default="json")
    summary.add_argument("--output")

    replay = sub.add_parser("replay", help="verify the complete event-store chain")
    replay.add_argument("store")
    replay.add_argument("--json", action="store_true", dest="json_output")
    return parser


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False)
    temporary = Path(handle.name)
    try:
        with handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            temporary.unlink()
        except OSError:
            pass
        raise


def _persist_adapter(result: AdapterResult, store: EventStore) -> int:
    for event in result.events:
        store.append(event)
    print(json.dumps(result.as_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    return 0 if result.state in {"success", "empty"} else 2


def _manual_event(args: argparse.Namespace) -> Event:
    try:
        data = json.loads(args.data)
    except json.JSONDecodeError as exc:
        raise EventError(f"--data must be valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise EventError("--data must be a JSON object")
    raw: dict[str, Any] = {
        "event_version": "1.0",
        "event_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"build-metrics:{args.idempotency_key}")),
        "idempotency_key": args.idempotency_key,
        "project": args.project,
        "type": args.type,
        "occurred_at": args.occurred_at,
        "source": {"kind": "manual", "uri": "manual:cli"},
        "data": data,
    }
    return Event.from_dict(raw)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "record":
            event = _manual_event(args)
            record = EventStore(args.store).append(event)
            print(json.dumps(record, sort_keys=True, separators=(",", ":")))
            return 0
        if args.command == "import-event":
            record = EventStore(args.store).append(load_event_json(args.event))
            print(json.dumps(record, sort_keys=True, separators=(",", ":")))
            return 0
        if args.command == "collect-git":
            result = collect_git(args.path, project=args.project, timeout_seconds=args.timeout, max_commits=args.max_commits)
            return _persist_adapter(result, EventStore(args.store))
        if args.command == "ingest-junit":
            return _persist_adapter(ingest_junit(args.report, project=args.project, suite=args.suite), EventStore(args.store))
        if args.command == "artifact":
            return _persist_adapter(
                collect_artifact(args.root, args.path, project=args.project, kind=args.kind),
                EventStore(args.store),
            )
        if args.command == "replay":
            store = EventStore(args.store)
            records = store.replay()
            payload = {
                "valid": True,
                "records": len(records),
                "head_hash": store.head_hash(),
                "projects": sorted({record["event"]["project"] for record in records}),
            }
            if args.json_output:
                print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
            else:
                print(f"event store is valid ({len(records)} records)")
            return 0

        store = EventStore(args.store)
        summary = summarize(store.events(), project=args.project, store_head_hash=store.head_hash())
        content = (
            json.dumps(summary.as_dict(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"
            if args.format == "json"
            else render_html(summary)
        )
        if args.output:
            _atomic_write(Path(args.output), content)
        else:
            print(content, end="")
        return 0 if summary.state in {"success", "empty"} else 2
    except (EventError, StoreError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())

