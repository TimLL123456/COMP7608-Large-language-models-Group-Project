"""Offline lifecycle regression for the separate Metadata Agent CLI."""
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from scr.cli import run_bird_b0_eval as base_cli
from scr.cli import run_bird_metadata_eval as metadata_cli
from scr.evaluation.bird import VARIANTS


class Dataset:
    manifest = {"dataset": "bird-mini-dev-original-sqlite", "split_seed": 42}

    def __init__(self, root):
        self.root = root
        self.questions = {
            1: dict(question_id=1, db_id="db_a", difficulty="simple",
                    question="gross sales?", evidence=""),
            2: dict(question_id=2, db_id="db_b", difficulty="moderate",
                    question="gross sales?", evidence=""),
            3: dict(question_id=3, db_id="db_a", difficulty="challenging",
                    question="gross sales by month?", evidence=""),
        }

    def get_split(self, split):
        return [self.questions[i] for i in ([1, 2] if split == "dev" else [3])]

    def get_agent_input(self, qid):
        return self.questions[qid]

    def get_database_path(self, dbid):
        return self.root / f"{dbid}.sqlite"

    def get_schema(self, dbid):
        return {"sales": {"columns": [{"name": "amount", "type": "integer"}]}}

    def get_descriptions(self, dbid):
        return {}


class MetadataRunnerTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.dataset = Dataset(self.root)
        self.folder = self.root / "results" / "sel"
        self.folder.mkdir(parents=True)
        for db_id in ("db_a", "db_b"):
            with closing(sqlite3.connect(self.root / f"{db_id}.sqlite")) as conn, conn:
                conn.execute("CREATE TABLE sales(amount INTEGER)")
                conn.execute("INSERT INTO sales VALUES (42)")
        for split in ("dev", "test"):
            self.folder.joinpath(f"{split}.jsonl").write_text(
                "".join(json.dumps(q) + "\n" for q in self.dataset.get_split(split)))
        self.folder.joinpath("selection_manifest.json").write_text(json.dumps({
            "dataset_manifest": self.dataset.manifest,
            "question_ids": {"dev": [1, 2], "test": [3]},
        }))
        self.common = ["--selection-id", "sel", "--result-root", str(self.root / "results"),
                       "--dataset-root", str(self.root)]
        self.search_hits = []

    def args(self, split, run):
        return ["infer", *self.common, "--split", split, "--run-id", run,
                "--experiment-id", "exp001", "--provider", "openai", "--model", "fake"]

    def fake_make_agent(self, store, metadata, model, prompt_variant):
        found = metadata.search("gross sales", "sales")["candidates"]
        self.search_hits.append((metadata.db_id, bool(found)))
        if found:
            read = metadata.read(found[0]["note_id"])
            self.assertEqual(read["revision"], 1)
        else:
            created = metadata.create(
                "metric", "sales", "gross_sales", "Gross sales", "Sum of sales values",
                "gross sales", "Source amount from sales table.", "schema:sales.amount")
            self.assertTrue(created["created"])
        return object()

    @staticmethod
    def fake_run_one(question, active, log, trace_events):
        trace_events.append({"seq": 1, "kind": "model", "model_call": 1})
        return {"final_sql": "SELECT SUM(amount) FROM sales", "graph_completed": True,
                "model_calls": 1, "tool_calls": 2, "sql_calls": 1,
                "usage_observed": False, "seconds": 0.01, "stop_reason": "final_sql_ready"}

    def run_fake(self, split, run):
        with patch.object(base_cli, "BirdDataset", return_value=self.dataset), \
             patch.object(metadata_cli, "_configure_model", return_value=("fake", object())), \
             patch.object(metadata_cli.agent, "make_agent", side_effect=self.fake_make_agent), \
             patch.object(metadata_cli.agent, "run_one", side_effect=self.fake_run_one):
            return metadata_cli.main(self.args(split, run))

    def test_dev_test_share_notes_and_experiments_isolated(self):
        self.assertEqual(self.run_fake("dev", "dev001"), 0)
        self.assertEqual(self.search_hits, [("db_a", False), ("db_b", False)])
        self.assertEqual(self.run_fake("test", "test001"), 0)
        self.assertEqual(self.search_hits[-1], ("db_a", True))
        root = self.folder / "Metadata"
        dev_manifest = json.loads((root / "dev" / "dev001" /
                                   "inference_manifest.json").read_text())
        test_manifest = json.loads((root / "test" / "test001" /
                                    "inference_manifest.json").read_text())
        self.assertEqual(dev_manifest["knowledge_sha256_after"],
                         test_manifest["knowledge_sha256_before"])
        self.assertEqual(test_manifest["agent_variant"], "Metadata")
        test_traces = [
            json.loads(line) for line in
            (root / "test" / "test001" / "traces.jsonl").read_text().splitlines()
        ]
        self.assertEqual(test_traces[0]["report"]["model"], "fake")
        self.assertEqual(test_traces[0]["report"]["model"], test_manifest["model"])
        self.assertEqual(len((root / "test" / "test001" /
                              "predictions.jsonl").read_text().splitlines()), 1)
        notes = root / "experiments" / "exp001" / "knowledge"
        self.assertTrue((notes / "db_a" / "index.json").is_file())
        self.assertTrue((notes / "db_b" / "index.json").is_file())
        ops = (root / "experiments" / "exp001" / "knowledge_operations.jsonl").read_text()
        self.assertIn('"action": "read"', ops)
        self.assertIn('"question_id": 3', ops)
        with self.assertRaises(ValueError):
            self.run_fake("dev", "dev002")  # Same experiment may not be reinitialized.
        with self.assertRaises(ValueError):
            self.run_fake("test", "test002")  # Test may not silently run twice.

    def test_test_before_dev_fails_safely(self):
        with patch.object(base_cli, "BirdDataset", return_value=self.dataset), \
             patch.object(metadata_cli, "_configure_model", return_value=("fake", object())):
            with self.assertRaises(ValueError):
                metadata_cli.main(self.args("test", "test001"))
        self.assertFalse((self.folder / "Metadata" / "test").exists())

    def test_scoring_reuses_original_evaluator(self):
        self.run_fake("dev", "dev001")
        out = self.folder / "Metadata" / "dev" / "dev001" / "scores"
        calls = []
        def fake_score(argv):
            calls.append(argv)
            out.mkdir()
            (out / "summary.json").write_text(json.dumps(
                {"correct": 2, "total": 2, "ex": 1.0}))
            return 0
        with patch.object(base_cli, "BirdDataset", return_value=self.dataset), \
             patch("scr.cli.evaluate_bird.run", side_effect=fake_score):
            self.assertEqual(metadata_cli.main([
                "score", *self.common, "--split", "dev", "--run-id", "dev001"]), 0)
        args = calls[0]
        self.assertEqual(args[args.index("--variant") + 1], "Metadata")
        self.assertIn("Metadata", VARIANTS)
        self.assertTrue((out / "report.md").is_file())

    def test_reject_unsafe_identifiers(self):
        with self.assertRaises(ValueError):
            metadata_cli.main(self.args("dev", "../escape"))


if __name__ == "__main__":
    unittest.main()
