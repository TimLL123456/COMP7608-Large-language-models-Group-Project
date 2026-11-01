"""Extra loader integrity and evaluator-reference isolation checks."""

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scr.datasets.bird import BirdDataset, BirdEvaluationReferences, read_annotations
from scr.datasets.setup_bird import setup
from tests.test_bird_setup import make_fixture


class LoaderTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        annotations, archive = make_fixture(base)
        self.root = base / "original-mini-dev"
        setup(self.root, archive=archive, annotations=annotations)

    def test_evaluator_reference_is_separate(self):
        ds = BirdDataset(self.root)
        ref = BirdEvaluationReferences(self.root)
        qid = ds.load_questions()[0]["question_id"]
        self.assertNotIn("SQL", str(ds.get_agent_input(qid)))
        self.assertEqual(ref.get_reference_sql(qid), "SELECT count(*) FROM records")
        with self.assertRaises(KeyError):
            ref.get_reference_sql(-1)

    def test_tampered_split_rejected(self):
        manifest_path = self.root / "dataset_manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["split"]["test"][0] = manifest["split"]["dev"][0]
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "Split manifest"):
            BirdDataset(self.root)

    def test_reference_fields_validate(self):
        wrong = self.root / "wrong.json"
        rows = json.loads((self.root / "annotations.json").read_text())
        rows[0]["SQL"] = ""
        wrong.write_text(json.dumps(rows))
        with self.assertRaisesRegex(ValueError, "Empty reference SQL"):
            read_annotations(wrong)


if __name__ == "__main__":
    unittest.main()
