"""Standalone coordinator feedback, retry, budget and fallback tests."""
import unittest
from unittest.mock import patch

from scr.agents.self_reflection_agent import SelfReflectionAgent, _compact_sql
from scr.baselines import bird_b0 as b0


class FakeReviewer:
    max_model_calls = 2
    max_inspections = 2

    def __init__(self, *statuses):
        self.results = list(statuses)
        self.calls = []

    def review(self, question, sql, store, previous_feedback=None):
        self.calls.append((question, sql, previous_feedback))
        status, safe = self.results.pop(0)
        return {"status": status, "candidate_safe": safe,
                "feedback": "Re-evaluate the query's aggregation",
                "stop_reason": "unsafe_final_sql" if not safe else "review_complete",
                "issues": [], "model_calls": 1, "tool_calls": 1, "sql_calls": 1,
                "input_tokens": 15, "output_tokens": 5, "latency_ms": 10}


def fake_report(sql):
    return {"graph_completed": sql is not None, "final_sql": sql,
            "model_calls": 2, "tool_calls": 3, "sql_calls": 1,
            "input_tokens": 20, "output_tokens": 4,
            "cached_input_tokens": None, "reasoning_tokens": None,
            "seconds": 0.1, "stop_reason": "final_sql_ready" if sql else "no_final_sql"}


class CoordinatorTests(unittest.TestCase):
    question = {"question_id": 27, "db_id": "synthetic", "question": "Compute average",
                "evidence": "Use the active population"}

    def run_fake(self, sqls, statuses, *, store=None, **kwargs):
        calls = []
        reviewer = FakeReviewer(*statuses)
        sqls = list(sqls)

        def fake_make_agent(store, **kw):
            return object()

        def fake_run_one(question, agent, log, trace_events):
            calls.append(dict(question))
            trace_events.append({"seq": 1, "kind": "model", "model_call": 1})
            return fake_report(sqls.pop(0))
        with patch.object(b0, "make_agent", side_effect=fake_make_agent), \
             patch.object(b0, "run_one", side_effect=fake_run_one):
            result = SelfReflectionAgent(reviewer, **kwargs).run(self.question, store or object())
        return result, calls, reviewer

    def test_pass_without_retry(self):
        result, calls, reviewer = self.run_fake(["SELECT 2"], [("PASS", True)])
        self.assertEqual(result["final_sql"], "SELECT 2")
        self.assertEqual(result["review_status"], "PASS")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0], self.question)
        self.assertEqual(result["report"]["model_calls"], 3)
        self.assertEqual(result["report"]["input_tokens"], 35)
        self.assertEqual(len(reviewer.calls), 1)

    def test_fail_retries_whole_b0_without_mutating_question(self):
        sqls = ["SELECT SUM(amount) FROM sales", "SELECT AVG(amount) FROM sales"]
        result, calls, reviewer = self.run_fake(sqls, [("FAIL", True), ("PASS", True)])
        self.assertEqual(result["final_sql"], sqls[1])
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0], self.question)
        self.assertEqual(calls[1]["question"], self.question["question"])
        self.assertIn("Use the active population", calls[1]["evidence"])
        self.assertIn(sqls[0], calls[1]["evidence"])
        self.assertIn("Re-evaluate the query's aggregation", calls[1]["evidence"])
        self.assertNotIn("REFLECTION FEEDBACK", self.question["evidence"])
        self.assertEqual(result["report"]["attempt_count"], 2)
        self.assertTrue(any(event.get("name") == "reflection_review"
                            for event in result["structured_events"]))

    def test_repeated_sql_terminates_and_preserves_safe_candidate(self):
        result, calls, reviewer = self.run_fake(["SELECT 7", "SELECT  7"], [("FAIL", True)])
        self.assertEqual(result["stop_reason"], "no_progress_repeated_sql")
        self.assertEqual(result["final_sql"], "SELECT 7")
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(reviewer.calls), 1)

    def test_literal_case_and_whitespace_are_semantically_distinct(self):
        self.assertEqual(_compact_sql(" SELECT  7 "), _compact_sql("select 7"))
        self.assertNotEqual(_compact_sql("SELECT 'a'"), _compact_sql("SELECT 'A'"))
        self.assertNotEqual(_compact_sql("SELECT 'a  b'"), _compact_sql("SELECT 'a b'"))
        self.assertNotEqual(_compact_sql("SELECT 'it''s'"),
                            _compact_sql("SELECT 'IT''S'"))
        result, calls, reviewer = self.run_fake(
            ["SELECT * FROM sales WHERE status = 'a'",
             "SELECT * FROM sales WHERE status = 'A'"],
            [("FAIL", True), ("PASS", True)])
        self.assertEqual(result["review_status"], "PASS")
        self.assertEqual(result["report"]["attempt_count"], 2)
        self.assertEqual(len(reviewer.calls), 2)
        self.assertEqual(result["final_sql"], reviewer.calls[1][1])

    def test_uncertain_and_error_preserve_unverified_sql(self):
        for status in ("UNCERTAIN", "ERROR"):
            result, calls, _ = self.run_fake(["SELECT 9"], [(status, True)])
            self.assertEqual(result["final_sql"], "SELECT 9")
            self.assertEqual(result["review_status"], status)
            self.assertTrue(result["report"]["graph_completed"])
            self.assertEqual(result["report"]["output_status"], "generated_unverified")
            self.assertEqual(len(calls), 1)

    def test_unsafe_sql_never_returned(self):
        result, _, _ = self.run_fake(["SELECT bad"], [("FAIL", False)], max_attempts=1)
        self.assertIsNone(result["final_sql"])
        self.assertEqual(result["stop_reason"], "unsafe_final_sql")

    def test_forced_sql_finalization_generates_executable_sql(self):
        class Finalizer:
            def invoke(self, messages):
                self.messages = messages
                return type("Reply", (), {
                    "content": 'Final SQL Query:\n"""\nSELECT 42;\n"""',
                    "usage_metadata": {"input_tokens": 10, "output_tokens": 5},
                    "response_metadata": {}, "additional_kwargs": {},
                })()

        class Store:
            def execute(self, sql):
                assert sql == "SELECT 42"
                return {"rows": [[42]], "columns": ["42"]}

        model = Finalizer()
        result, _, _ = self.run_fake(
            [None], [("UNCERTAIN", True)], store=Store(),
            finalizer_model=model)
        self.assertEqual(result["final_sql"], "SELECT 42")
        self.assertEqual(result["report"]["output_status"], "generated_unverified")
        self.assertTrue(result["report"]["finalization_triggered"])
        self.assertEqual(result["report"]["model_calls"], 4)
        self.assertEqual(result["report"]["sql_calls"], 3)
        self.assertIn("FINALIZATION ONLY", model.messages[0].content)

    def test_review_budget_exhaustion_reason_preserved(self):
        class BudgetReviewer(FakeReviewer):
            def review(self, *args, **kwargs):
                result = super().review(*args, **kwargs)
                result["stop_reason"] = "review_tool_budget_exhausted"
                return result

        reviewer = BudgetReviewer(("UNCERTAIN", True))
        with (patch.object(b0, "make_agent", return_value=object()),
              patch.object(b0, "run_one", return_value=fake_report("SELECT 5"))):
            result = SelfReflectionAgent(reviewer).run(self.question, object())
        self.assertEqual(result["final_sql"], "SELECT 5")
        self.assertEqual(result["stop_reason"], "review_tool_budget_exhausted")

    def test_known_issue_sql_is_output_when_no_repair_succeeds(self):
        result, _, _ = self.run_fake(
            ["SELECT 3"], [("FAIL", True)], max_attempts=1)
        self.assertEqual(result["final_sql"], "SELECT 3")
        self.assertEqual(result["report"]["output_status"], "generated_known_issues")
        self.assertNotEqual(result["review_status"], "PASS")

    def test_unsafe_first_candidate_can_be_repaired(self):
        result, calls, _ = self.run_fake(
            ["DELETE FROM sales", "SELECT 2"],
            [("FAIL", False), ("PASS", True)])
        self.assertEqual(len(calls), 2)
        self.assertEqual(result["final_sql"], "SELECT 2")
        self.assertEqual(result["report"]["output_status"], "verified")

    def test_missing_final_sql_stops(self):
        result, _, reviewer = self.run_fake([None], [])
        self.assertIsNone(result["final_sql"])
        self.assertEqual(reviewer.calls, [])

    def test_outer_budget_prevents_new_b0_invocation(self):
        result, calls, _ = self.run_fake(["SELECT 2", "SELECT 3"],
                                         [("FAIL", True)], max_total_model_calls=41)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["stop_reason"], "global_budget_before_b0")
        self.assertEqual(result["final_sql"], "SELECT 2")


if __name__ == "__main__":
    unittest.main()
