import unittest

from open_source_portfolio_generator import generate, probe

BASE = {"name": "x", "visibility": "public", "description": "safe", "stars": 1}


class Tests(unittest.TestCase):
    def test_public_only_and_unique(self):
        self.assertTrue(generate({"repositories": [BASE]})["ok"])
        self.assertFalse(generate({"repositories": [{**BASE, "visibility": "private"}]})["ok"])
        self.assertFalse(generate({"repositories": [BASE, BASE]})["ok"])

    def test_safe_bounded_markdown_and_strict_stars(self):
        result = generate({"display_name": "<b>Title</b>",
                           "repositories": [{**BASE, "description": "# injected"}]})
        self.assertNotIn("<b>", result["markdown"])
        self.assertIn("\\# injected", result["markdown"])
        self.assertFalse(generate({"repositories": [{**BASE, "description": "x\nevil"}]})["ok"])
        for stars in (True, "1", -1):
            self.assertFalse(generate({"repositories": [{**BASE, "stars": stars}]})["ok"])

    def test_malformed_does_not_crash(self):
        for value in (None, [], {"repositories": [None]}):
            self.assertFalse(generate(value)["ok"])

    def test_probe(self):
        self.assertTrue(probe()["ok"])


if __name__ == "__main__":
    unittest.main()
