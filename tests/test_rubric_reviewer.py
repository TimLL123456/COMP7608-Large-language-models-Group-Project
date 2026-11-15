"""Pure contract checks for independent requirement coverage and verdicts."""
import unittest
import json
from scr.agents.rubric_self_reflection.reviewer import RubricReviewer
from scr.agents.rubric_self_reflection.rubric import (
    model_json, parse_requirements, parse_review,
)

QUESTION = {"question": "Average sales for active members in 2025 by region",
            "evidence": ""}


def requirements():
    return parse_requirements({"requirements": [
        {"requirement_id": "R01", "category": "metric", "expected": "Average sales",
         "source_quote": "Average sales", "material": True},
        {"requirement_id": "R02", "category": "filter", "expected": "Active members",
         "source_quote": "active members", "material": True},
        {"requirement_id": "R03", "category": "grain", "expected": "By region",
         "source_quote": "by region", "material": True},
    ]}, QUESTION)


def judgment(reqs, statuses, overall=None):
    assessments = [{"requirement_id": r["requirement_id"], "status": status,
                    "observed": "SQL clause", "evidence": "SQL clause and question",
                    "reason": "Grounded comparison"}
                   for r, status in zip(reqs, statuses)]
    issues = [{"requirement_id": a["requirement_id"],
               "description": "Wrong aggregation", "evidence": "SUM vs average",
               "suggested_action": "Review metric"} for a in assessments if a["status"] == "FAIL"]
    return {"overall_status": overall or ("FAIL" if issues else
        "UNCERTAIN" if "UNCERTAIN" in statuses else "PASS"),
        "assessments": assessments, "coverage": {"status": "COMPLETE", "details": "All clauses matched"},
        "issues": issues, "feedback": "Review metric" if issues else "",
        "needs_more_evidence": False, "inspection_requests": []}


class RubricContractTests(unittest.TestCase):
    def test_extract_stable_atomic_ids_and_quote_grounding(self):
        reqs = requirements()
        self.assertEqual([r["requirement_id"] for r in reqs], ["R01", "R02", "R03"])
        bad = {"requirements": [{"requirement_id": "R01", "category": "filter",
                                 "expected": "Not requested", "source_quote": "all customers",
                                 "material": True}]}
        with self.assertRaises(ValueError):
            parse_requirements(bad, QUESTION)
        bad["requirements"][0]["source_quote"] = "active members"
        bad["requirements"][0]["requirement_id"] = "R09"
        with self.assertRaises(ValueError):
            parse_requirements(bad, QUESTION)

    def test_pass_requires_complete_material_coverage(self):
        reqs = requirements()
        self.assertEqual(parse_review(judgment(reqs, ["PASS"]*3), reqs,
                                      finalizing=False)["status"], "PASS")
        bad = judgment(reqs, ["PASS"]*3)
        bad["assessments"] = bad["assessments"][:-1]
        with self.assertRaisesRegex(ValueError, "All extracted"):
            parse_review(bad, reqs, finalizing=False)
        bad = judgment(reqs, ["PASS"]*3)
        bad["coverage"]["status"] = "GAP"
        with self.assertRaisesRegex(ValueError, "Overall verdict"):
            parse_review(bad, reqs, finalizing=False)

    def test_fail_and_uncertain_precedence(self):
        reqs = requirements()
        self.assertEqual(parse_review(judgment(reqs, ["PASS", "FAIL", "UNCERTAIN"]),
                                      reqs, finalizing=False)["status"], "FAIL")
        self.assertEqual(parse_review(judgment(reqs, ["PASS", "UNCERTAIN", "PASS"]),
                                      reqs, finalizing=False)["status"], "UNCERTAIN")
        invalid = judgment(reqs, ["PASS", "FAIL", "PASS"], overall="PASS")
        with self.assertRaisesRegex(ValueError, "Overall verdict"):
            parse_review(invalid, reqs, finalizing=False)

    def test_no_speculative_issue_or_material_na(self):
        reqs = requirements()
        row = judgment(reqs, ["PASS"]*3)
        row["issues"] = [{"requirement_id": "R01", "description": "No evidence",
                          "evidence": "none", "suggested_action": "change SQL"}]
        with self.assertRaises(ValueError):
            parse_review(row, reqs, finalizing=False)
        row = judgment(reqs, ["N/A", "PASS", "PASS"])
        with self.assertRaises(ValueError):
            parse_review(row, reqs, finalizing=False)

    def test_complete_json_only_and_no_inspection_after_finalization(self):
        self.assertEqual(model_json('```json\n{"ok":true}\n```')["ok"], True)
        with self.assertRaises(ValueError):
            model_json('{"ok":true}\n{"more":true}')
        reqs = requirements()
        row = judgment(reqs, ["PASS", "UNCERTAIN", "PASS"])
        row["needs_more_evidence"] = True
        row["inspection_requests"] = [{"kind": "inspect_table", "table": "sales",
                                       "reason": "Need value meaning"}]
        self.assertEqual(parse_review(row, reqs, finalizing=False)["status"], "UNCERTAIN")
        with self.assertRaisesRegex(ValueError, "finalization"):
            parse_review(row, reqs, finalizing=True)


class FakeReply:
    def __init__(self, obj):
        self.content = json.dumps(obj)
        self.usage_metadata = {"input_tokens": 9, "output_tokens": 3}
        self.response_metadata = {}
        self.additional_kwargs = {}


class FakeModel:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.messages = []
    def invoke(self, messages):
        self.messages.append(messages)
        return FakeReply(self.responses.pop(0))


class Store:
    def __init__(self):
        self.inspections = 0
    def execute(self, sql):
        return {"columns": ["avg"], "rows": [[3.5]]}
    def inspect_table(self, name):
        self.inspections += 1
        return {"table": name, "columns": ["sales", "region"]}
    def list_tables(self):
        self.inspections += 1
        return ["sales"]


class ReviewerRuntimeTests(unittest.TestCase):
    def test_extract_and_review_full_coverage(self):
        reqs = requirements()
        payload = {"requirements": reqs}
        model = FakeModel(payload, judgment(reqs, ["PASS"]*3))
        reviewer = RubricReviewer(model, max_model_calls=3, max_inspections=1)
        extracted = reviewer.extract(QUESTION)
        self.assertEqual(extracted["status"], "PASS")
        store = Store()
        review = reviewer.review(QUESTION, "SELECT AVG(sales) FROM sales GROUP BY region",
                                 store, extracted["requirements"])
        self.assertEqual(review["status"], "PASS")
        self.assertTrue(review["candidate_safe"])
        self.assertEqual((review["tool_calls"], review["sql_calls"]), (1,1))
        self.assertEqual(len(model.messages), 2)

    def test_inspection_round_and_reserved_finalization(self):
        reqs = requirements()
        uncertain = judgment(reqs, ["PASS", "UNCERTAIN", "PASS"])
        uncertain["needs_more_evidence"] = True
        uncertain["inspection_requests"] = [{"kind": "inspect_table", "table": "sales",
                                             "reason": "Check value scope"}]
        model = FakeModel(uncertain, judgment(reqs, ["PASS"]*3))
        store = Store()
        review = RubricReviewer(model, max_model_calls=3, max_inspections=1).review(
            QUESTION, "SELECT AVG(sales) FROM sales", store, reqs)
        self.assertEqual(review["status"], "PASS")
        self.assertEqual(store.inspections, 1)
        self.assertEqual(review["model_calls"], 2)
        self.assertTrue(review["finalization_triggered"])

    def test_unverified_pass_rejected_then_exhausts_budget(self):
        reqs = requirements()
        bad = judgment(reqs, ["PASS"]*3)
        bad["assessments"].pop()
        model = FakeModel(bad)
        review = RubricReviewer(model, max_model_calls=1).review(
            QUESTION, "SELECT AVG(sales) FROM sales", Store(), reqs)
        self.assertEqual(review["status"], "ERROR")
        self.assertEqual(review["model_calls"], 1)
        self.assertTrue(review["candidate_safe"])


if __name__ == "__main__":
    unittest.main()
