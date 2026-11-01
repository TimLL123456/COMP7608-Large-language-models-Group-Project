"""Offline KORA-03 EX, safety, coverage and CLI regression tests."""

import json
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from scr.evaluation.bird import (evaluate_predictions, execute_bounded_sql,
                                 load_predictions, validate_predictions)
from scr.cli import evaluate_bird as cli


class FakeDataset:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.manifest = {"dataset": "bird-mini-dev-original-sqlite", "split_seed": 42}
        self.questions = [
            {"question_id": 10, "db_id": "demo", "difficulty": "simple"},
            {"question_id": 11, "db_id": "demo", "difficulty": "moderate"},
            {"question_id": 12, "db_id": "demo", "difficulty": "challenging"},
        ]

    def get_split(self, name):
        if name == "dev":
            return self.questions
        return []

    def get_database_path(self, dbid):
        if dbid != "demo":
            raise KeyError(dbid)
        return self.db


class FakeReferences:
    def get_reference_sql(self, qid):
        return "SELECT amount FROM records"


class EvaluatorTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.db = self.root / "demo.sqlite"
        with closing(sqlite3.connect(self.db)) as conn, conn:
            conn.execute("CREATE TABLE records (id INTEGER PRIMARY KEY, amount INTEGER)")
            conn.executemany("INSERT INTO records VALUES (?, ?)", [(1, 10), (2, 10), (3, 20)])
        self.dataset = FakeDataset(self.root, self.db)
        self.refs = FakeReferences()
        self.questions = self.dataset.questions

    def prediction(self, qid=10, sql="SELECT DISTINCT amount FROM records", **extra):
        return {"question_id": qid, "db_id": "demo", "predicted_sql": sql, **extra}

    def score(self, predictions, questions=None):
        return evaluate_predictions(self.dataset, self.refs, questions or self.questions,
                                    predictions, variant="B0")

    def test_same_results_different_sql_and_duplicates(self):
        cases = [
            "SELECT DISTINCT amount FROM records",
            "SELECT amount FROM records ORDER BY amount DESC",
            "SELECT amount FROM records",
        ]
        for sql in cases:
            with self.subTest(sql=sql):
                records, summary = self.score([self.prediction(sql=sql)], [self.questions[0]])
                self.assertEqual(records[0]["ex"], 1)
                self.assertEqual(summary["ex"], 1)
        status, rows, _ = execute_bounded_sql(self.db, "SELECT amount FROM records WHERE 1=0")
        self.assertEqual((status, rows), ("ok", []))

    def test_wrong_result_and_empty_result(self):
        predictions = [self.prediction(sql="SELECT id FROM records"),
                       self.prediction(11, "SELECT amount FROM records WHERE 0")]
        records, summary = self.score(predictions)
        self.assertEqual([x["ex"] for x in records], [0, 0, 0])
        self.assertEqual(records[0]["status"], "incorrect_result")
        self.assertEqual(records[2]["status"], "missing_prediction")
        self.assertEqual((summary["total"], summary["missing_predictions"]), (3, 1))

    def test_missing_sql_and_nullable_usage(self):
        rows, summary = self.score([self.prediction(sql=None), self.prediction(11, sql="")])
        self.assertEqual(rows[0]["status"], "missing_sql")
        self.assertEqual(rows[1]["status"], "missing_sql")
        self.assertIsNone(summary["mean_cost_usd"])
        self.assertEqual(summary["observed_cost_usd"], 0)

    def test_reject_unknown_duplicate_wrong_db_and_bad_usage(self):
        for candidate in (
            [self.prediction(), self.prediction()],
            [self.prediction(999)],
            [{**self.prediction(), "db_id": "other"}],
            [self.prediction(input_tokens=-1)],
            [self.prediction(cost_usd=float("nan"))],
            [self.prediction(sql=123)],
        ):
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValueError):
                    validate_predictions(candidate, self.questions)
        with self.assertRaises(ValueError):
            self.score([self.prediction()], questions=[self.questions[1]])
        with self.assertRaises(ValueError):
            evaluate_predictions(self.dataset, self.refs, self.questions, [], variant="S0")

    def test_reject_sql_writes_attach_and_multiple_statements(self):
        for sql in ("DELETE FROM records", "CREATE TABLE unsafe(a)",
                    "ATTACH DATABASE ':memory:' AS extra", "SELECT 1; SELECT 2"):
            with self.subTest(sql=sql):
                status, rows, _ = execute_bounded_sql(self.db, sql)
                self.assertNotEqual(status, "ok")
                self.assertIsNone(rows)
        with closing(sqlite3.connect(self.db)) as conn, conn:
            self.assertEqual(conn.execute("SELECT count(*) FROM records").fetchone()[0], 3)

    def test_syntax_error_and_result_limit(self):
        status, _, _ = execute_bounded_sql(self.db, "SELECT missing_column FROM records")
        self.assertEqual(status, "sql_error")
        status, _, _ = execute_bounded_sql(self.db, "SELECT amount FROM records", max_result_rows=2)
        self.assertEqual(status, "result_limit")

    def test_timeout_bounded_recursive_query(self):
        sql = "WITH RECURSIVE seq(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM seq WHERE n<10000000) SELECT sum(n) FROM seq"
        status, _, _ = execute_bounded_sql(self.db, sql, timeout_seconds=0.001)
        self.assertEqual(status, "timeout")


    def test_missing_prediction_still_validates_gold(self):
        class InvalidRefs:
            def get_reference_sql(self, qid):
                return "SELECT nonexistent FROM records" if qid == 12 else "SELECT amount FROM records"
        with self.assertRaisesRegex(RuntimeError, "question_id 12"):
            evaluate_predictions(self.dataset, InvalidRefs(), self.questions,
                                 [self.prediction(10, sql=None)], variant="B0")

    def test_sql_timing_and_agent_efficiency_metrics(self):
        row = self.prediction(sql="SELECT amount FROM records", model_calls=4,
                              sql_calls=3, sql_success_calls=2, sql_error_calls=1,
                              agent_sql_execution_ms=7.25, latency_ms=100)
        records, summary = self.score([row], [self.questions[0]])
        self.assertEqual(summary["performance"]["sql_tool_success_rate"], 2/3)
        self.assertEqual(summary["performance"]["agent_sql_execution_ms"]["total"], 7.25)
        self.assertEqual(summary["performance"]["latency_ms"]["p95"], 100)
        self.assertIsNotNone(records[0]["gold_sql_execution_ms"])

    def test_reference_failure_invalidates_run(self):
        class BadRefs:
            def get_reference_sql(self, qid):
                return "SELECT does_not_exist FROM records"
        with self.assertRaisesRegex(RuntimeError, "Reference SQL failed"):
            evaluate_predictions(self.dataset, BadRefs(), self.questions[:1],
                                 [self.prediction()], variant="B0")

    def test_jsonl_and_cli_artifacts(self):
        predictions = self.root / "input.jsonl"
        predictions.write_text(json.dumps(self.prediction(tool_calls=4, latency_ms=12.5)) + "\n", encoding="utf-8")
        self.assertEqual(len(load_predictions(predictions)), 1)
        with patch.object(cli, "BirdDataset", return_value=self.dataset), \
             patch.object(cli, "BirdEvaluationReferences", return_value=self.refs):
            result = cli.run(["--variant", "B4", "--split", "dev", "--predictions", str(predictions),
                              "--output-dir", str(self.root / "results"), "--run-id", "test-run"])
        self.assertEqual(result, 0)
        output = self.root / "results" / "test-run"
        for name in ("per_question.jsonl", "per_question.csv", "summary.json", "run_manifest.json"):
            self.assertTrue((output / name).is_file(), name)
        summary = json.loads((output / "summary.json").read_text())
        manifest = json.loads((output / "run_manifest.json").read_text())
        self.assertEqual((summary["total"], summary["correct"]), (3, 1))
        self.assertEqual(summary["mean_tool_calls"], 4)
        self.assertEqual(manifest["question_ids"], [10, 11, 12])
        self.assertNotIn("reference_sql", (output / "per_question.jsonl").read_text())

    def test_smoke_subset_and_refuse_overwrite(self):
        predictions = self.root / "input.jsonl"
        predictions.write_text(json.dumps(self.prediction()) + "\n")
        args = ["--variant", "B0", "--split", "dev", "--predictions", str(predictions),
                "--output-dir", str(self.root / "results"), "--run-id", "smoke",
                "--question-ids", "10"]
        with patch.object(cli, "BirdDataset", return_value=self.dataset), \
             patch.object(cli, "BirdEvaluationReferences", return_value=self.refs):
            self.assertEqual(cli.run(args), 0)
            with self.assertRaises(SystemExit):
                cli.run(args)
        summary = json.loads((self.root / "results" / "smoke" / "summary.json").read_text())
        self.assertFalse(summary["is_full_split"])
        self.assertEqual(summary["total"], 1)


if __name__ == "__main__":
    unittest.main()
