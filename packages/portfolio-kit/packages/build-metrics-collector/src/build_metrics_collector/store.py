"""Hash-chained, idempotent JSON Lines event store."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from .models import Event, EventError

ZERO_HASH = "0" * 64
MAX_STORE_BYTES = 128 * 1024 * 1024
MAX_RECORD_BYTES = 512 * 1024


class StoreError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise StoreError(f"value is not JSON serializable: {exc}") from exc


def record_hash(unsigned: dict[str, Any]) -> str:
    return hashlib.sha256(canonical(unsigned)).hexdigest()


class EventStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def replay(self) -> tuple[dict[str, Any], ...]:
        if not self.path.exists():
            return ()
        try:
            if self.path.stat().st_size > MAX_STORE_BYTES:
                raise StoreError(f"event store exceeds {MAX_STORE_BYTES} bytes")
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except StoreError:
            raise
        except (OSError, UnicodeError) as exc:
            raise StoreError(f"cannot read event store: {exc}") from exc
        records: list[dict[str, Any]] = []
        previous = ZERO_HASH
        ids: set[str] = set()
        keys: set[str] = set()
        for sequence, line in enumerate(lines, start=1):
            if not line.strip():
                raise StoreError(f"blank event-store line at {sequence}")
            if len(line.encode("utf-8")) > MAX_RECORD_BYTES:
                raise StoreError(f"record at line {sequence} exceeds {MAX_RECORD_BYTES} bytes")
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise StoreError(f"invalid JSON at line {sequence}: {exc}") from exc
            required = {"sequence", "previous_hash", "event", "hash"}
            if not isinstance(record, dict) or set(record) != required:
                raise StoreError(f"invalid record fields at line {sequence}")
            if record["sequence"] != sequence or record["previous_hash"] != previous:
                raise StoreError(f"event-store chain mismatch at line {sequence}")
            try:
                event = Event.from_dict(record["event"])
            except EventError as exc:
                raise StoreError(f"invalid event at line {sequence}: {exc}") from exc
            if event.event_id in ids or event.idempotency_key in keys:
                raise StoreError(f"duplicate event identity at line {sequence}")
            unsigned = dict(record)
            claimed = unsigned.pop("hash")
            if claimed != record_hash(unsigned):
                raise StoreError(f"record hash mismatch at line {sequence}")
            previous = claimed
            ids.add(event.event_id)
            keys.add(event.idempotency_key)
            records.append(record)
        return tuple(records)

    def events(self) -> tuple[Event, ...]:
        return tuple(Event.from_dict(record["event"]) for record in self.replay())

    def append(self, event: Event) -> dict[str, Any]:
        records = self.replay()
        for record in records:
            existing = Event.from_dict(record["event"])
            if existing.idempotency_key == event.idempotency_key:
                if existing.as_dict() == event.as_dict():
                    return record
                raise StoreError(f"idempotency conflict for key: {event.idempotency_key}")
        unsigned = {
            "sequence": len(records) + 1,
            "previous_hash": records[-1]["hash"] if records else ZERO_HASH,
            "event": event.as_dict(),
        }
        record = {**unsigned, "hash": record_hash(unsigned)}
        encoded = canonical(record) + b"\n"
        if len(encoded) > MAX_RECORD_BYTES:
            raise StoreError(f"record exceeds {MAX_RECORD_BYTES} bytes")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.path.open("ab") as handle:
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
        except OSError as exc:
            raise StoreError(f"cannot append event store: {exc}") from exc
        return record

    def head_hash(self) -> str:
        records = self.replay()
        return records[-1]["hash"] if records else ZERO_HASH

