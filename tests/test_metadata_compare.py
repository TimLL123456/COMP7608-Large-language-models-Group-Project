"""Offline test for score-only Metadata comparison; no model or gold references."""
import json
from pathlib import Path
import tempfile
import unittest

from scr.cli.compare_metadata_runs import compare


class MetadataComparisonTests(unittest.TestCase):
    def test_accuracy_gain_and_regression_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base, candidate, output = [root / x for x in ("control.jsonl", "metadata.jsonl", "compare.md")]
            records = [
                {"question_id": 1, "db_id": "db1", "difficulty": "simple",
                 "ex": 0, "input_tokens": 100, "tool_calls": 3},
                {"question_id": 2, "db_id": "db1", "difficulty": "moderate",
                 "ex": 1, "input_tokens": None, "tool_calls": 5},
            ]
            base.write_text("".join(json.dumps(x) + "\n" for x in records))
            changed = [dict(x) for x in records]
            changed[0]["ex"] = 1
            changed[1]["ex"] = 0
            candidate.write_text("".join(json.dumps(x) + "\n" for x in changed))
            compare(base, candidate, output)
            report = output.read_text()
            self.assertIn("Fixed:** 1", report)
            self.assertIn("regressed:** 1", report)
            self.assertIn("n=1", report)
            changed[1]["question_id"] = 3
            candidate.write_text("".join(json.dumps(x) + "\n" for x in changed))
            with self.assertRaises(ValueError):
                compare(base, candidate, output)


if __name__ == "__main__":
    unittest.main()
