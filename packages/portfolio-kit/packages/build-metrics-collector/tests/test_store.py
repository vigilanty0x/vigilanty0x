from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from build_metrics_collector.store import EventStore, StoreError, ZERO_HASH

from tests.helpers import event


class StoreTests(unittest.TestCase):
    def test_append_and_replay(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = EventStore(Path(directory) / "events.jsonl")
            store.append(event("commit", {"sha": "a" * 40}))
            self.assertEqual(len(store.events()), 1)
            self.assertNotEqual(store.head_hash(), ZERO_HASH)

    def test_repeat_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = EventStore(Path(directory) / "events.jsonl")
            item = event("commit", {"sha": "a" * 40})
            first = store.append(item)
            second = store.append(item)
            self.assertEqual(first, second)
            self.assertEqual(len(store.replay()), 1)

    def test_idempotency_conflict_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = EventStore(Path(directory) / "events.jsonl")
            store.append(event("commit", {"sha": "a" * 40}))
            changed = event("commit", {"sha": "b" * 40}, event_id="changed")
            with self.assertRaisesRegex(StoreError, "idempotency conflict"):
                store.append(changed)

    def test_tampering_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            store = EventStore(path)
            store.append(event("commit", {"sha": "a" * 40}))
            record = json.loads(path.read_text(encoding="utf-8"))
            record["event"]["data"]["sha"] = "b" * 40
            path.write_text(json.dumps(record) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(StoreError, "hash mismatch"):
                store.replay()

    def test_sequence_gap_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            store = EventStore(path)
            store.append(event("commit", {"sha": "a" * 40}))
            record = json.loads(path.read_text(encoding="utf-8"))
            record["sequence"] = 2
            path.write_text(json.dumps(record) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(StoreError, "chain mismatch"):
                store.replay()


if __name__ == "__main__":
    unittest.main()

