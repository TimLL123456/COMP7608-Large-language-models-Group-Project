"""Offline prepare/infer/score orchestration using fake B0 model and dataset."""
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from scr.cli import run_bird_b0_eval as cli


class FakeBirdDataset:
    def __init__(self, root=None):
        self.manifest = {"dataset": "bird-mini-dev-original-sqlite", "split_seed": 42}
        self.root = Path(root)
        self.questions = {
            1: dict(question_id=1, db_id="db1", difficulty="simple", question="sum?", evidence=""),
            2: dict(question_id=2, db_id="db2", difficulty="moderate", question="count?", evidence=""),
            3: dict(question_id=3, db_id="db1", difficulty="challenging", question="join?", evidence=""),
            4: dict(question_id=4, db_id="db2", difficulty="simple", question="test?", evidence=""),
        }

    def get_split(self, split):
        ids = [1, 2, 3] if split == "dev" else [4]
        return [self.questions[i] for i in ids]

    def get_agent_input(self, qid):
        return self.questions[qid]

    def get_database_path(self, dbid):
        return self.root / f"{dbid}.sqlite"


class PipelineTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.results = self.root / "results"
        self.dataset = FakeBirdDataset(self.root)
        for dbid in ("db1", "db2"):
            with closing(sqlite3.connect(self.root / f"{dbid}.sqlite")) as db, db:
                db.execute("CREATE TABLE t (n INTEGER)")
                db.execute("INSERT INTO t VALUES (1)")
        self.common = ["--selection-id", "fixture", "--dataset-root", str(self.root), "--result-root", str(self.results)]

    def prepare(self):
        with patch.object(cli, "BirdDataset", return_value=self.dataset):
            return cli.main(["prepare", *self.common,
                             "--dev-simple", "1", "--dev-moderate", "1", "--dev-challenging", "1",
                             "--test-simple", "1", "--seed", "42"])

    def test_prepare_and_refuse_overwrite(self):
        self.assertEqual(self.prepare(), 0)
        path = self.results / "fixture"
        self.assertEqual(len((path / "dev.jsonl").read_text().splitlines()), 3)
        self.assertEqual(len((path / "test.jsonl").read_text().splitlines()), 1)
        self.assertNotIn('"SQL"', (path / "dev.jsonl").read_text())
        self.assertEqual(json.loads((path / "selection_manifest.json").read_text())["question_ids"], {"dev": [1, 2, 3], "test": [4]})
        with patch.object(cli, "BirdDataset", return_value=self.dataset), self.assertRaises(SystemExit):
            cli.main(["prepare", *self.common, "--dev-simple", "1"])

    def test_force_replaces_unused_selection(self):
        self.prepare()
        folder = self.results / "fixture"
        with patch.object(cli, "BirdDataset", return_value=self.dataset):
            self.assertEqual(cli.main(["prepare", *self.common, "--force",
                                       "--dev-simple", "1", "--test-simple", "1"]), 0)
        manifest = json.loads((folder / "selection_manifest.json").read_text())
        self.assertEqual(manifest["question_ids"], {"dev": [1], "test": [4]})
        self.assertFalse((folder / "B0").exists())

    def test_force_refuses_existing_runs_and_unknown_files(self):
        self.prepare()
        folder = self.results / "fixture"
        (folder / "B0").mkdir()
        (folder / "B0" / "important.txt").write_text("keep")
        with patch.object(cli, "BirdDataset", return_value=self.dataset), self.assertRaises(SystemExit):
            cli.main(["prepare", *self.common, "--force", "--dev-simple", "1"])
        self.assertEqual((folder / "B0" / "important.txt").read_text(), "keep")
        (folder / "B0" / "important.txt").unlink()
        (folder / "B0").rmdir()
        (folder / "notes.txt").write_text("keep")
        with patch.object(cli, "BirdDataset", return_value=self.dataset), self.assertRaises(SystemExit):
            cli.main(["prepare", *self.common, "--force", "--dev-simple", "1"])
        self.assertEqual((folder / "notes.txt").read_text(), "keep")

    def test_force_is_prepare_only(self):
        with self.assertRaises(SystemExit):
            cli.build_parser().parse_args(["infer", *self.common, "--split", "dev",
                                           "--run-id", "one", "--force"])

    def test_reject_tampered_selection_and_unsafe_identifier(self):
        self.prepare()
        selected = self.results / "fixture" / "dev.jsonl"
        rows = [json.loads(x) for x in selected.read_text().splitlines()]
        rows[0]["question"] = "tampered"
        selected.write_text("\n".join(json.dumps(x) for x in rows) + "\n")
        args = cli.build_parser().parse_args(["infer", *self.common, "--split", "dev", "--run-id", "one"])
        with patch.object(cli, "BirdDataset", return_value=self.dataset), self.assertRaises(ValueError):
            cli._selection(args)
        with self.assertRaises(SystemExit):
            cli.main(["prepare", "--selection-id", "../escape"])

    def test_infer_and_score_argument_bridge(self):
        self.prepare()
        class FakeB0:
            MODEL = "nvidia/nemotron-3.5-super-vl-120b-a12b"
            TEMPERATURE = 1.0
            TOP_P = .95
            MAX_CONTEXT_TOKENS = 262_144
            MAX_OUTPUT_TOKENS = 16_384
            REQUEST_TIMEOUT = 300
            MAX_MODEL_CALLS = MAX_TOTAL_TOOL_CALLS = MAX_SQL_EXECUTIONS = 20
            RECURSION_LIMIT = 100
            OUTPUT_FORMAT_VERSION = "final-sql-query-v2"
            @staticmethod
            def make_agent(store):
                return store
            @staticmethod
            def run_one(q, agent, log, trace_events=None):
                if trace_events is not None:
                    trace_events.append({"seq": 1, "kind": "model", "model_call": 1})
                if q["question_id"] == 2:
                    raise RuntimeError("simulated provider failure")
                log("TOOL CALL execute_sql")
                return {"final_sql": "SELECT n FROM t", "graph_completed": True,
                        "model_calls": 2, "tool_calls": 1, "sql_calls": 1,
                        "input_tokens": 50, "output_tokens": 9, "usage_observed": True,
                        "seconds": 0.25, "stop_reason": "final_sql_ready", "error": None}
        import sys
        import types
        fake_b0 = types.ModuleType("scr.baselines.bird_b0")
        for k in dir(FakeB0):
            if not k.startswith("__"):
                setattr(fake_b0, k, getattr(FakeB0, k))
        with patch.dict(sys.modules, {"scr.baselines.bird_b0": fake_b0}), \
             patch("scr.baselines.bird_b0", fake_b0, create=True), \
             patch.object(cli, "BirdDataset", return_value=self.dataset), \
             patch.dict(os.environ, {"NVIDIA_API_KEY": "fake"}):
            self.assertEqual(cli.main(["infer", *self.common, "--split", "dev", "--run-id", "one"]), 0)
        run_dir = self.results / "fixture" / "B0" / "dev" / "one"
        manifest = json.loads((run_dir / "inference_manifest.json").read_text())
        self.assertEqual(manifest["request_timeout_seconds"], 300)
        self.assertEqual(manifest["max_output_tokens"], 16_384)
        self.assertEqual(manifest["max_context_tokens"], 262_144)
        self.assertIs(manifest["context_budget_enforced"], False)
        preds = [json.loads(x) for x in (run_dir / "predictions.jsonl").read_text().splitlines()]
        self.assertEqual(len(preds), 3)
        self.assertIsNone(preds[1]["predicted_sql"])
        self.assertIsNone(preds[1]["input_tokens"])
        self.assertEqual(preds[0]["latency_ms"], 250)
        self.assertEqual(len((run_dir / "traces.jsonl").read_text().splitlines()), 3)
        entries = [json.loads(row) for row in (run_dir / "traces.jsonl").read_text().splitlines()]
        self.assertEqual(entries[0]["structured_events"][0]["kind"], "model")
        self.assertEqual(cli.main(["visualize", *self.common, "--split", "dev",
                                   "--run-id", "one"]), 0)
        self.assertTrue((run_dir / "trace-explorer.html").is_file())
        with patch.object(cli, "BirdDataset", return_value=self.dataset), patch.dict(os.environ, {"NVIDIA_API_KEY":"fake"}), self.assertRaises(SystemExit):
            cli.main(["infer", *self.common, "--split", "dev", "--run-id", "one"])
        from unittest.mock import MagicMock
        import types
        evaluator = MagicMock()
        def fake_evaluate(argv):
            output = Path(argv[argv.index("--output-dir")+1]) / argv[argv.index("--run-id")+1]
            output.mkdir(parents=True)
            payload = {"correct": 2, "total": 3, "ex": 2/3,
                       "by_difficulty": {
                           "simple": {"correct": 1, "total": 1, "ex": 1.0},
                           "moderate": {"correct": 0, "total": 1, "ex": 0.0},
                           "challenging": {"correct": 1, "total": 1, "ex": 1.0}},
                       "performance": {"model_calls": {"observed": 3, "total": 6,
                                         "mean": 2.0, "p50": 2.0, "p95": 2.0}}}
            (output / "summary.json").write_text(json.dumps(payload))
            with (output / "per_question.jsonl").open("w") as file:
                for qid, difficulty, ex in [(1,"simple",1),(2,"moderate",0),(3,"challenging",1)]:
                    file.write(json.dumps({"question_id":qid,"difficulty":difficulty,"ex":ex,
                        "status":"correct" if ex else "missing_sql","model_calls":2,
                        "tool_calls":1,"sql_calls":1,"latency_ms":250})+"\n")
            return 0
        evaluator.side_effect = fake_evaluate
        with patch.object(cli, "BirdDataset", return_value=self.dataset), \
             patch.dict(sys.modules, {"scr.cli.evaluate_bird": types.SimpleNamespace(run=evaluator)}):
            self.assertEqual(cli.main(["score", *self.common, "--split", "dev", "--run-id", "one"]), 0)
        self.assertTrue((run_dir / "scores" / "report.md").is_file())
        called = evaluator.call_args.args[0]
        self.assertEqual(called[called.index("--question-ids")+1], "1,2,3")
        self.assertEqual(called[called.index("--split")+1], "dev")
        self.assertEqual(called[called.index("--run-id")+1], "scores")


    def test_score_refuses_tampered_manifest(self):
        self.test_infer_and_score_argument_bridge()
        run_dir = self.results / "fixture" / "B0" / "dev" / "one"
        manifest_path = run_dir / "inference_manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["model"] = "different-provider/model"
        manifest_path.write_text(json.dumps(manifest))
        args = cli.build_parser().parse_args(["score", *self.common, "--split", "dev", "--run-id", "one"])
        with patch.object(cli, "BirdDataset", return_value=self.dataset), self.assertRaises(ValueError):
            cli.score(args)

    def test_score_refuses_prediction_hash_mismatch(self):
        self.test_infer_and_score_argument_bridge()
        run_dir = self.results / "fixture" / "B0" / "dev" / "one"
        file = run_dir / "predictions.jsonl"
        file.write_text(file.read_text() + "\n")
        args = cli.build_parser().parse_args(["score", *self.common, "--split", "dev", "--run-id", "one"])
        with patch.object(cli, "BirdDataset", return_value=self.dataset), self.assertRaises(ValueError):
            cli.score(args)


if __name__ == "__main__":
    unittest.main()
