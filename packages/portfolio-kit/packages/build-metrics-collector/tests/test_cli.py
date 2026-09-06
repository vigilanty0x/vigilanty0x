from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from build_metrics_collector.cli import main


class CliTests(unittest.TestCase):
    def test_record_replay_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = Path(directory) / "events.jsonl"
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(
                    main(
                        [
                            "record",
                            "--store",
                            str(store),
                            "--project",
                            "demo",
                            "--type",
                            "commit",
                            "--occurred-at",
                            "2026-08-15T10:00:00Z",
                            "--idempotency-key",
                            "commit-1",
                            "--data",
                            json.dumps({"sha": "a" * 40}),
                        ]
                    ),
                    0,
                )
                self.assertEqual(main(["replay", str(store), "--json"]), 0)
                self.assertEqual(main(["summarize", str(store), "--project", "demo"]), 0)
            self.assertIn('"commits": 1', output.getvalue())

    def test_html_summary_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = Path(directory) / "events.jsonl"
            report = Path(directory) / "report.html"
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["summarize", str(store), "--project", "demo", "--format", "html", "--output", str(report)]), 0)
            self.assertIn("No data", report.read_text(encoding="utf-8"))

    def test_invalid_manual_data_returns_three(self) -> None:
        with tempfile.TemporaryDirectory() as directory, redirect_stderr(io.StringIO()):
            code = main(
                [
                    "record",
                    "--store",
                    str(Path(directory) / "events"),
                    "--project",
                    "demo",
                    "--type",
                    "commit",
                    "--occurred-at",
                    "2026-08-15T10:00:00Z",
                    "--idempotency-key",
                    "bad",
                    "--data",
                    "not-json",
                ]
            )
            self.assertEqual(code, 3)

    def test_artifact_command_persists_event(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "artifact.txt").write_text("synthetic", encoding="utf-8")
            store = root / "events.jsonl"
            with redirect_stdout(io.StringIO()):
                code = main(
                    [
                        "artifact",
                        "artifact.txt",
                        "--root",
                        str(root),
                        "--store",
                        str(store),
                        "--project",
                        "demo",
                    ]
                )
            self.assertEqual(code, 0)
            self.assertTrue(store.exists())

    def test_invalid_artifact_path_returns_two(self) -> None:
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()):
            code = main(
                [
                    "artifact",
                    "../outside",
                    "--root",
                    directory,
                    "--store",
                    str(Path(directory) / "events"),
                    "--project",
                    "demo",
                ]
            )
            self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()

