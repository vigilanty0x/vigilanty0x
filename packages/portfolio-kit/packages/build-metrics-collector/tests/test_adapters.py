from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from build_metrics_collector.adapters import collect_artifact, collect_git, ingest_junit


class AdapterTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("git"), "git unavailable")
    def test_git_commit_collection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "synthetic@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Synthetic"], cwd=root, check=True)
            (root / "file.txt").write_text("demo", encoding="utf-8")
            subprocess.run(["git", "add", "file.txt"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "synthetic"], cwd=root, check=True)
            result = collect_git(root, project="demo")
            self.assertEqual(result.state, "success")
            self.assertEqual(result.events[0].type, "commit")

    def test_git_invalid_root_is_error(self) -> None:
        self.assertEqual(collect_git("/not/a/repo", project="demo").state, "error")

    def test_git_timeout_is_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch(
            "build_metrics_collector.adapters.subprocess.run", side_effect=subprocess.TimeoutExpired(["git"], 1)
        ):
            self.assertEqual(collect_git(directory, project="demo").state, "timeout")

    def test_junit_ingestion(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "junit.xml"
            path.write_text('<testsuite tests="3" failures="1" skipped="1" time="0.5"/>', encoding="utf-8")
            result = ingest_junit(path, project="demo", suite="unit")
            self.assertEqual(result.state, "success")
            self.assertEqual(result.events[0].data["passed"], 1)

    def test_invalid_junit_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "junit.xml"
            path.write_text("<broken", encoding="utf-8")
            self.assertEqual(ingest_junit(path, project="demo").state, "error")

    def test_empty_junit_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "junit.xml"
            path.write_text("<testsuites></testsuites>", encoding="utf-8")
            self.assertEqual(ingest_junit(path, project="demo").state, "empty")

    def test_artifact_collection_hashes_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "artifact.bin").write_bytes(b"synthetic")
            result = collect_artifact(root, "artifact.bin", project="demo")
            self.assertEqual(result.state, "success")
            self.assertEqual(len(result.events[0].data["sha256"]), 64)

    def test_artifact_escape_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = collect_artifact(directory, "../outside.bin", project="demo")
            self.assertEqual(result.state, "error")


if __name__ == "__main__":
    unittest.main()

