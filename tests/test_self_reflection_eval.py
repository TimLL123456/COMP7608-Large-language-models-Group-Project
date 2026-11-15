"""Standalone CLI contract, manifest, scoring and comparison regression tests."""
from contextlib import closing
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from scr.cli import run_bird_self_reflection_eval as cli
from scr.cli import run_bird_b0_eval as base_cli


class FakeDataset:
    manifest = {"dataset": "bird-mini-dev-2026-sqlite", "version": "fixture"}

    def __init__(self, root):
        self.root = root
        self.questions = [{"question_id": 1, "db_id": "one", "question": "How many?",
                           "evidence": "", "difficulty": "simple"}]

    def get_database_path(self, dbid):
        return self.root / (dbid + ".db")


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.dataset = FakeDataset(self.root)
        self.folder = self.root / "results" / "sample"
        self.folder.mkdir(parents=True)
        with closing(sqlite3.connect(self.dataset.get_database_path("one"))) as con, con:
            con.execute("CREATE TABLE items(n INTEGER)")
            con.execute("INSERT INTO items VALUES (1)")
        self.folder.joinpath("selection_manifest.json").write_text(json.dumps({
            "question_ids": {"dev": [1], "test": []},
            "dataset_manifest": self.dataset.manifest,
        }), encoding="utf-8")
        self.common = ["--selection-id", "sample", "--dataset-root", str(self.root),
                       "--result-root", str(self.root / "results"),
                       "--split", "dev", "--run-id", "self-run"]

    def fake_run(self, question, store):
        report = {
            "final_sql": "SELECT COUNT(*) FROM items", "graph_completed": True,
            "model_calls": 3, "tool_calls": 2, "sql_calls": 1,
            "review_status": "PASS", "stop_reason": "final_sql_ready",
            "seconds": 0.2, "input_tokens": 30, "output_tokens": 8,
        }
        return {"report": report, "final_sql": report["final_sql"],
                "review_status": "PASS", "stop_reason": "final_sql_ready",
                "attempts": [{"attempt": 1, "candidate_sql": report["final_sql"],
                              "review": {"status": "PASS"}}],
                "structured_events": [{"seq": 1, "kind": "tool_call", "name": "reflection_review",
                                       "tool_call_id": "review-1"}],
                "b0_usage": {"model_calls": 2}, "reviewer_usage": {"model_calls": 1}}

    def infer(self):
        with patch.object(base_cli, "_selection", return_value=(
                    self.folder, self.dataset, self.dataset.questions)), \
             patch.object(cli, "_configure_model", return_value=("fake-model", object(), object())), \
             patch.object(cli.SelfReflectionAgent, "run", self.fake_run):
            return cli.main(["infer", *self.common, "--provider", "openai",
                             "--model", "fake-model"])

    def test_infer_writes_independent_manifest_and_trace(self):
        self.assertEqual(self.infer(), 0)
        run = self.folder / "SelfReflection" / "dev" / "self-run"
        manifest = json.loads((run / "inference_manifest.json").read_text())
        self.assertEqual(manifest["agent_variant"], "SelfReflection")
        self.assertTrue(manifest["completed"])
        self.assertEqual(manifest["question_ids"], [1])
        self.assertEqual(manifest["model"], "fake-model")
        self.assertEqual(len(manifest["reviewer_prompt_sha256"]), 64)
        preds = [json.loads(x) for x in (run / "predictions.jsonl").read_text().splitlines()]
        self.assertEqual(preds[0]["predicted_sql"], "SELECT COUNT(*) FROM items")
        self.assertEqual(preds[0]["model_calls"], 3)
        self.assertEqual(preds[0]["input_tokens"], 30)
        self.assertTrue((run / "reviews" / "reflection_decisions.jsonl").is_file())
        self.assertFalse((run / "reflection_decisions.jsonl").exists())
        self.assertFalse((self.folder / "B0").exists())
        with self.assertRaises(ValueError):
            self.infer()  # Do not overwrite immutable run.

    def test_score_and_compare_reuse_independent_evaluator(self):
        self.infer()
        run = self.folder / "SelfReflection" / "dev" / "self-run"
        def fake_score(args):
            self.assertEqual(args[args.index("--variant") + 1], "SelfReflection")
            scores = run / "scores"
            scores.mkdir()
            (scores / "summary.json").write_text(json.dumps({
                "correct": 1, "total": 1, "ex": 1.0}))
            (scores / "per_question.jsonl").write_text(json.dumps({"question_id": 1, "ex": 1}) + "\n")
            return 0
        with patch.object(base_cli, "_selection", return_value=(
                   self.folder, self.dataset, self.dataset.questions)), \
             patch("scr.cli.evaluate_bird.run", side_effect=fake_score):
            self.assertEqual(cli.main(["score", *self.common]), 0)
        self.assertTrue((run / "scores" / "report.md").exists())
        manifest = json.loads((run / "inference_manifest.json").read_text())
        b0 = self.folder / "B0" / "dev" / "baseline"
        (b0 / "scores").mkdir(parents=True)
        b0_manifest = {k: manifest[k] for k in (
            "dataset_manifest", "selection_sha256", "question_ids", "provider", "model",
            "prompt_variant")}
        b0_manifest["system_prompt_sha256"] = manifest["b0_prompt_sha256"]
        (b0 / "inference_manifest.json").write_text(json.dumps(b0_manifest))
        (b0 / "scores" / "per_question.jsonl").write_text(
            json.dumps({"question_id": 1, "ex": 0}) + "\n")
        with patch.object(base_cli, "_selection", return_value=(
                    self.folder, self.dataset, self.dataset.questions)):
            self.assertEqual(cli.main(["compare", *self.common,
                                       "--baseline-run-id", "baseline"]), 0)
        comparison = (run / "comparison_report.md").read_text()
        self.assertIn("Corrected: **1**", comparison)
        self.assertIn("not a matched-compute", comparison)
        # Different thinking configurations are not valid paired comparisons.
        b0_manifest["requested_reasoning_effort"] = "medium"
        (b0 / "inference_manifest.json").write_text(json.dumps(b0_manifest))
        with patch.object(base_cli, "_selection", return_value=(
                    self.folder, self.dataset, self.dataset.questions)):
            with self.assertRaisesRegex(ValueError, "requested_reasoning_effort"):
                cli.main(["compare", *self.common,
                          "--baseline-run-id", "baseline"])

    def test_default_sql_first_budgets(self):
        from scr.cli.run_bird_self_reflection_eval import parser
        args = parser().parse_args(["infer", "--selection-id", "demo",
                                    "--split", "dev", "--run-id", "v2"])
        self.assertEqual(args.max_review_model_calls, 40)
        self.assertEqual(args.max_inspections, 39)
        self.assertEqual(args.max_total_model_calls, 240)
        self.assertEqual(args.max_total_tool_calls, 240)
        self.assertEqual(args.max_total_sql_calls, 240)

    def test_safe_path_and_budget_validation(self):
        with self.assertRaises(ValueError):
            cli.main(["infer", *self.common[:-1], "../unsafe"])
        with self.assertRaises(ValueError):
            cli.main(["infer", *self.common, "--max-attempts", "0"])


if __name__ == "__main__":
    unittest.main()
