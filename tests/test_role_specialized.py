"""Offline three-node routing tests: no model network calls or gold answers."""
import unittest
from unittest.mock import patch

from scr.agents.role_specialized.coordinator import RoleSpecializedSelfReflectionAgent

QUESTION = {"question_id": 7, "db_id": "demo", "question": "Average sales by region",
            "evidence": "region is a store attribute"}
REQUIREMENT = {"requirement_id": "R01", "category": "metric",
               "expected": "Average sales", "source_quote": "Average sales",
               "material": True}


class Store:
    def execute(self, sql):
        return {"error": "invalid SQL"} if "bad" in sql.lower() else {
            "columns": ["value"], "rows": [[3.0]]}


class Reviewer:
    max_model_calls = 40
    max_inspections = 39

    def __init__(self, *statuses):
        self.model = object()
        self.statuses = list(statuses)
        self.calls = []
        self.order = []

    def extract(self, question, *, max_calls=2):
        self.order.append("extract")
        return {"status": "PASS", "requirements": [REQUIREMENT],
                "model_calls": 1, "tool_calls": 0, "sql_calls": 0}

    def review(self, question, sql, store, requirements, **kwargs):
        self.order.append("review")
        self.calls.append((question, sql, kwargs))
        status = self.statuses.pop(0)
        executed = store.execute(sql)
        if "error" in executed:
            status = "FAIL"
        return {
            "status": status, "candidate_safe": "error" not in executed,
            "requirements": [{**REQUIREMENT, "status": status
                              if status in ("PASS", "FAIL", "UNCERTAIN") else "UNCERTAIN",
                              "observed": sql, "evidence": "SQL and question"}],
            "coverage": {"status": "COMPLETE", "details": "Inspected"},
            "issues": [{"requirement_id": "R01", "description": "Wrong metric",
                        "evidence": sql, "suggested_action": "Check AVG"}]
                        if status == "FAIL" else [],
            "feedback": "Use AVG" if status == "FAIL" else "",
            "model_calls": 1, "tool_calls": 1, "sql_calls": 1,
            "inspection_log": [], "execution": executed,
            "stop_reason": "review_complete",
        }


def generated(sql, *, events=None):
    return {
        "candidate_sql": sql,
        "report": {"final_sql": sql, "graph_completed": True,
                   "model_calls": 1, "tool_calls": 0, "sql_calls": 0},
        "events": events or [],
        "completion": {"status": "not_needed", "triggered": False},
    }


class RoleSpecializedTests(unittest.TestCase):
    def run_agent(self, sqls, statuses, *, max_attempts=3):
        reviewer = Reviewer(*statuses)
        agent = RoleSpecializedSelfReflectionAgent(
            reviewer, generator_model=object(), max_attempts=max_attempts)
        produced = iter(sqls)
        requests = []

        def fake_generate(question, store):
            reviewer.order.append("generate")
            requests.append(question)
            return generated(next(produced), events=[
                {"kind": "tool_result", "name": "inspect_table",
                 "output": "region has one row per store"}])

        with patch.object(agent, "_b0_generate", side_effect=fake_generate):
            result = agent.run(QUESTION, Store())
        return result, reviewer, requests

    def test_pass_reports_and_does_not_loop(self):
        result, reviewer, requests = self.run_agent(
            ["SELECT AVG(sales) FROM t"], ["PASS"])
        self.assertEqual(reviewer.order, ["generate", "extract", "review"])
        self.assertEqual(result["report"]["output_status"], "verified")
        self.assertEqual(result["report"]["review_report_count"], 1)
        self.assertEqual(result["review_reports"][0]["overall_decision"], "PASS")
        self.assertEqual(len(requests), 1)
        self.assertIn("inspect_table", reviewer.calls[0][0]["evidence"])

    def test_fail_report_loops_to_lightweight_generator(self):
        result, reviewer, requests = self.run_agent(
            ["SELECT SUM(sales) FROM t", "SELECT AVG(sales) FROM t"],
            ["FAIL", "PASS"])
        self.assertEqual(result["report"]["attempt_count"], 2)
        self.assertEqual(result["report"]["output_status"], "verified")
        self.assertEqual(len(result["review_reports"]), 2)
        self.assertEqual(result["review_reports"][0]["overall_decision"], "NOT_PASS")
        self.assertEqual(result["review_reports"][1]["overall_decision"], "PASS")
        self.assertIn("Use AVG", requests[1]["evidence"])
        self.assertEqual(QUESTION["evidence"], "region is a store attribute")

    def test_budget_exhausted_falls_back_to_safe_sql(self):
        result, _, requests = self.run_agent(
            ["SELECT SUM(sales) FROM t"], ["FAIL"], max_attempts=1)
        self.assertEqual(len(requests), 1)
        self.assertEqual(result["report"]["output_status"], "generated_known_issues")
        self.assertEqual(len(result["review_reports"]), 1)
        self.assertEqual(result["review_reports"][0]["overall_decision"], "NOT_PASS")

    def test_invalid_sql_is_not_accepted(self):
        result, _, _ = self.run_agent(
            ["SELECT bad FROM t"], ["FAIL"], max_attempts=1)
        self.assertIsNone(result["final_sql"])
        self.assertEqual(result["report"]["output_status"], "missing")

    def test_review_error_does_not_retry(self):
        result, reviewer, requests = self.run_agent(
            ["SELECT AVG(sales) FROM t"], ["ERROR"])
        self.assertEqual(len(requests), 1)
        self.assertEqual(result["report"]["output_status"], "generated_unverified")
        self.assertEqual(result["review_reports"][0]["review_status"], "ERROR")


if __name__ == "__main__":
    unittest.main()
