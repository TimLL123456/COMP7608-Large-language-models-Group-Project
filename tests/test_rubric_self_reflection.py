"""Independent orchestrator tests using a fake B0 and reviewer; no paid calls."""
import unittest
from unittest.mock import patch

from scr.agents.rubric_self_reflection.coordinator import RubricSelfReflectionAgent
from scr.agents.rubric_self_reflection.reviewer import RubricReviewer

QUESTION = {"question_id": 1, "db_id": "demo", "question": "Average sales by region",
            "evidence": ""}
REQS = [{"requirement_id": "R01", "category": "metric", "expected": "Average sales",
         "source_quote": "Average sales", "material": True}]


class FakeStore:
    def execute(self, sql):
        return {"error": "unsafe or invalid"} if "bad" in sql.lower() else {
            "columns": ["sales"], "rows": [[3.0]]}


class FakeReviewer:
    max_model_calls = 40
    max_inspections = 39
    def __init__(self, *statuses):
        self.statuses = list(statuses)
        self.model = object()
        self.calls = []
    def extract(self, question, *, max_calls=2):
        return {"status": "PASS", "requirements": REQS,
                "model_calls": 1, "tool_calls": 0, "sql_calls": 0}
    def review(self, question, sql, store, requirements, **kwargs):
        self.calls.append((question, sql, kwargs))
        status = self.statuses.pop(0)
        if "error" in store.execute(sql):
            return {"status": "FAIL", "candidate_safe": False,
                    "requirements": [], "coverage": {}, "issues": [], "feedback": "Fix SQL",
                    "model_calls": 0, "tool_calls": 1, "sql_calls": 1}
        return {"status": status, "candidate_safe": True,
                "requirements": [{**REQS[0], "status": status if status != "ERROR" else "UNCERTAIN",
                                  "observed": "SQL clause", "evidence": "SQL and question"}],
                "coverage": {"status": "COMPLETE", "details": "All covered"},
                "issues": [{"requirement_id": "R01", "description": "Wrong metric",
                            "evidence": "SQL metric", "suggested_action": "Use average"}]
                if status == "FAIL" else [],
                "feedback": "Use AVG from the original question" if status == "FAIL" else "",
                "model_calls": 1, "tool_calls": 1, "sql_calls": 1,
                "inspection_log": [], "stop_reason": "review_complete"}


def fake_report(sql):
    return {"final_sql": sql, "graph_completed": True, "model_calls": 1,
            "tool_calls": 0, "sql_calls": 0, "stop_reason": "final_sql_ready"}


class CoordinatorTests(unittest.TestCase):
    def _run(self, sqls, statuses):
        reviewer = FakeReviewer(*statuses)
        generated = iter(sqls)
        def make_agent(store, **kw):
            return None
        def run_one(q, agent, log, trace_events):
            return fake_report(next(generated))
        with patch("scr.agents.rubric_self_reflection.coordinator.b0.make_agent", make_agent), \
             patch("scr.agents.rubric_self_reflection.coordinator.b0.run_one", run_one):
            result = RubricSelfReflectionAgent(reviewer, finalizer_model=object()).run(QUESTION, FakeStore())
        return result, reviewer

    def test_pass_returns_candidate_without_refinement(self):
        result, reviewer = self._run(["SELECT AVG(sales) FROM t"], ["PASS"])
        self.assertEqual(result["report"]["output_status"], "verified")
        self.assertEqual(result["report"]["refinement_status"], "not_needed")
        self.assertEqual(len(reviewer.calls), 1)

    def test_confirmed_fail_retries_full_b0(self):
        result, reviewer = self._run(["SELECT SUM(sales) FROM t", "SELECT AVG(sales) FROM t"],
                                     ["FAIL", "PASS"])
        self.assertEqual(result["report"]["attempt_count"], 2)
        self.assertEqual(result["report"]["output_status"], "verified")
        self.assertEqual(result["final_sql"], "SELECT AVG(sales) FROM t")
        self.assertEqual(QUESTION["evidence"], "")
        # Reviewer always sees original authorized question; feedback goes to B0 only.
        self.assertEqual(reviewer.calls[1][0]["evidence"], "")

    def test_uncertain_refinement_falls_back_safely(self):
        result, _ = self._run(["SELECT AVG(sales) FROM t"], ["UNCERTAIN"])
        self.assertEqual(result["final_sql"], "SELECT AVG(sales) FROM t")
        self.assertEqual(result["report"]["output_status"], "generated_unverified")
        self.assertTrue(result["refinement"]["triggered"])
        self.assertIn(result["refinement"]["status"], ("error", "invalid_format"))

    def test_budget_gates_are_not_overrun(self):
        reviewer = FakeReviewer("PASS")
        coordinator = RubricSelfReflectionAgent(reviewer, max_total_model_calls=5,
                                                max_total_tool_calls=5, max_total_sql_calls=5)
        result = coordinator.run(QUESTION, FakeStore())
        self.assertEqual(result["report"]["output_status"], "missing")
        self.assertEqual(result["report"]["model_calls"], 0)

    def test_invalid_b0_sql_not_accepted(self):
        result, _ = self._run(["SELECT bad FROM t"], ["FAIL"])
        self.assertIsNone(result["final_sql"])
        self.assertEqual(result["report"]["output_status"], "missing")


if __name__ == "__main__":
    unittest.main()
