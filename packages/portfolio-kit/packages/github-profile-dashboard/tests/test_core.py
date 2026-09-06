import unittest

from github_profile_dashboard import dashboard, probe

BASE = {"name": "x", "visibility": "public", "stars": 2}


class Tests(unittest.TestCase):
    def test_metrics_and_public_scope(self):
        result = dashboard({"repositories": [BASE]})
        self.assertEqual(result["stars"], 2)
        self.assertEqual(result["scope"], "declared_public_snapshot_only")

    def test_every_entry_validated_before_use(self):
        for repository in ("bad", {}, {"name": "x", "visibility": "private"},
                           {**BASE, "stars": -1}, {**BASE, "stars": True},
                           {**BASE, "stars": "2"}, {**BASE, "extra": 1}):
            self.assertFalse(dashboard({"repositories": [repository]})["ok"])

    def test_unique_names_and_malformed_container(self):
        self.assertFalse(dashboard({"repositories": [BASE, BASE]})["ok"])
        self.assertFalse(dashboard(None)["ok"])
        self.assertFalse(dashboard({"repositories": [None]})["ok"])

    def test_probe(self):
        self.assertTrue(probe()["ok"])


if __name__ == "__main__":
    unittest.main()
