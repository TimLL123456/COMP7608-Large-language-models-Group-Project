"""Synthetic read-only fallback and one-call refinement checks."""
import unittest
from scr.agents.rubric_self_reflection.finalizer import refine_sql


class FakeReply:
    def __init__(self, content):
        self.content = content
        self.usage_metadata = {"input_tokens": 10, "output_tokens": 5}
        self.response_metadata = {}
        self.additional_kwargs = {}


class Model:
    def __init__(self, text):
        self.text, self.calls = text, 0
    def invoke(self, messages):
        self.calls += 1
        return FakeReply(self.text)


class Store:
    def execute(self, sql):
        if "wrong" in sql.lower() or "DELETE" in sql:
            return {"error": "invalid SQL"}
        return {"columns": ["n"], "rows": [[3]]}


class FinalRefinementTests(unittest.TestCase):
    def test_refinement_executes_and_counts_one_model_one_sql(self):
        model = Model('Final SQL Query:\n"""\nSELECT 3;\n"""')
        result = refine_sql(model, {"question": "Count rows", "evidence": ""},
                            "SELECT 2;", {"status": "FAIL", "requirements": [], "issues": []},
                            [], Store(), allow_model=True, allow_execution=True)
        self.assertEqual(result["status"], "executable")
        self.assertEqual(result["sql"], "SELECT 3;")
        self.assertEqual((result["model_calls"], result["sql_calls"]), (1, 1))

    def test_invalid_sql_does_not_replace_fallback(self):
        model = Model('Final SQL Query:\n"""\nSELECT wrong;\n"""')
        result = refine_sql(model, {"question": "Count", "evidence": ""},
                            "SELECT 2;", {"status": "FAIL"}, [], Store(),
                            allow_model=True, allow_execution=True)
        self.assertEqual(result["status"], "invalid_execution")
        self.assertIsNone(result["sql"])
        self.assertEqual(result["sql_calls"], 1)

    def test_budget_exhaustion_makes_no_calls(self):
        model = Model('Final SQL Query:\n"""\nSELECT 1;\n"""')
        result = refine_sql(model, {"question": "Count"}, "SELECT 2;", {}, [],
                            Store(), allow_model=False, allow_execution=True)
        self.assertEqual(result["status"], "budget_exhausted")
        self.assertEqual(model.calls, 0)


if __name__ == "__main__":
    unittest.main()
