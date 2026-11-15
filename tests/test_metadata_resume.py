"""Offline tests: safe partial Metadata inference resume and model-label provenance."""
from hashlib import sha256
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from scr.baselines import bird_b0 as b0
from scr.cli import run_bird_b0_eval as base_cli
from scr.cli import run_bird_metadata_eval as metadata_cli
from scr.metadata.engine import MetadataEngine
from tests.test_metadata_agent import MetadataRunnerTests


class MetadataResumeTests(unittest.TestCase):
    def setUp(self):
        self.fixture = MetadataRunnerTests(methodName="test_test_before_dev_fails_safely")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.folder = self.fixture.folder
        self.root = self.folder / "Metadata"
        self.experiment_dir = self.root / "experiments" / "exp001"
        self.run_dir = self.root / "dev" / "partial001"

    def make_partial(self):
        args = metadata_cli.parser().parse_args(self.fixture.args("dev", "partial001"))
        settings = metadata_cli._experiment_settings(args, self.fixture.dataset, "fake")
        settings["selection_sha256"] = metadata_cli._hash(
            self.folder / "selection_manifest.json")
        settings.update({
            "created_utc": "2026-11-10T12:00:00+00:00",
            "dev_completed": False,
            "test_completed": False,
            "dev_run_id": "partial001",
            "dev_knowledge_sha256_before": sha256(b"").hexdigest(),
        })
        self.experiment_dir.mkdir(parents=True)
        metadata_cli._write_json(
            self.experiment_dir / "experiment_manifest.json", settings)
        note_engine = MetadataEngine(
            self.experiment_dir, "db_a", 1, self.fixture.dataset.get_schema("db_a"))
        note = note_engine.create(
            "metric", "sales", "gross_sales", "Gross sales",
            "Sum of sales values", "gross sales",
            "Source amount from sales table.", "schema:sales.amount")
        self.assertTrue(note["created"])
        self.run_dir.mkdir(parents=True)
        prediction = {
            "question_id": 1, "db_id": "db_a", "provider": "openai",
            "model": "fake", "predicted_sql": "SELECT SUM(amount) FROM sales",
        }
        trace = {
            "question_id": 1,
            "report": {"model": b0.MODEL, "graph_completed": True,
                       "final_sql": "SELECT SUM(amount) FROM sales"},
            "events": [], "structured_events": [],
        }
        (self.run_dir / "predictions.jsonl").write_text(
            json.dumps(prediction) + "\n", encoding="utf-8")
        (self.run_dir / "traces.jsonl").write_text(
            json.dumps(trace) + "\n", encoding="utf-8")

    def resume(self):
        with patch.object(base_cli, "BirdDataset", return_value=self.fixture.dataset), \
             patch.object(metadata_cli, "_configure_model", return_value=("fake", object())), \
             patch.object(metadata_cli.agent, "make_agent",
                          side_effect=self.fixture.fake_make_agent), \
             patch.object(metadata_cli.agent, "run_one",
                          side_effect=self.fixture.fake_run_one):
            return metadata_cli.main(
                self.fixture.args("dev", "partial001") + ["--resume"])

    def test_legacy_partial_resume_keeps_completed_records_and_fixes_new_labels(self):
        self.make_partial()
        old_prediction = (self.run_dir / "predictions.jsonl").read_bytes()
        old_trace = (self.run_dir / "traces.jsonl").read_bytes()
        self.assertEqual(self.resume(), 0)
        predictions = [
            json.loads(x) for x in
            (self.run_dir / "predictions.jsonl").read_text().splitlines()
        ]
        traces = [
            json.loads(x) for x in
            (self.run_dir / "traces.jsonl").read_text().splitlines()
        ]
        self.assertEqual([p["question_id"] for p in predictions], [1, 2])
        self.assertTrue((self.run_dir / "predictions.jsonl").read_bytes().startswith(old_prediction))
        self.assertTrue((self.run_dir / "traces.jsonl").read_bytes().startswith(old_trace))
        self.assertEqual(traces[0]["report"]["model"], b0.MODEL)
        self.assertEqual(traces[1]["report"]["model"], "fake")
        audit = [
            json.loads(x) for x in
            (self.run_dir / "trace_model_corrections.jsonl").read_text().splitlines()
        ]
        self.assertEqual(audit[0]["question_id"], 1)
        self.assertEqual(audit[0]["configured_model"], "fake")
        self.assertEqual(self.fixture.search_hits, [("db_b", False)])
        manifest = json.loads((self.run_dir / "inference_manifest.json").read_text())
        self.assertEqual(manifest["resumed_from_questions"], 1)
        self.assertEqual(manifest["historical_trace_model_corrections"], 1)
        self.assertEqual(manifest["knowledge_sha256_before"], sha256(b"").hexdigest())

    def test_incomplete_question_activity_refuses_resume_without_overwrite(self):
        self.make_partial()
        MetadataEngine(
            self.experiment_dir, "db_b", 2,
            self.fixture.dataset.get_schema("db_b")).search("gross sales")
        old = (self.run_dir / "predictions.jsonl").read_bytes()
        with self.assertRaisesRegex(ValueError, "Uncommitted question"):
            self.resume()
        self.assertEqual((self.run_dir / "predictions.jsonl").read_bytes(), old)
        self.assertFalse((self.run_dir / "inference_manifest.json").exists())

    def test_tampered_knowledge_refuses_resume(self):
        self.make_partial()
        note = next((self.experiment_dir / "knowledge" / "db_a" / "notes").glob("*.md"))
        note.write_text("tampered", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "differs from its index"):
            self.resume()

    def test_nonprefix_predictions_refuse_resume(self):
        self.make_partial()
        prediction_path = self.run_dir / "predictions.jsonl"
        item = json.loads(prediction_path.read_text())
        item["question_id"] = 2
        prediction_path.write_text(json.dumps(item) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "do not match question order"):
            self.resume()

    def test_sql_mismatch_refuses_resume(self):
        self.make_partial()
        trace_path = self.run_dir / "traces.jsonl"
        trace = json.loads(trace_path.read_text())
        trace["report"]["final_sql"] = "SELECT 1"
        trace_path.write_text(json.dumps(trace) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Prediction and trace SQL disagree"):
            self.resume()

    def test_model_mismatch_refuses_resume(self):
        self.make_partial()
        predictions_path = self.run_dir / "predictions.jsonl"
        prediction = json.loads(predictions_path.read_text())
        prediction["model"] = "unexpected-model"
        predictions_path.write_text(json.dumps(prediction) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "do not match question order"):
            self.resume()

    def test_refuse_rerun_of_completed_split(self):
        self.assertEqual(self.fixture.run_fake("dev", "dev001"), 0)
        with patch.object(base_cli, "BirdDataset", return_value=self.fixture.dataset), \
             patch.object(metadata_cli, "_configure_model", return_value=("fake", object())):
            with self.assertRaisesRegex(ValueError, "already completed"):
                metadata_cli.main(
                    self.fixture.args("dev", "dev001") + ["--resume"])


if __name__ == "__main__":
    unittest.main()
