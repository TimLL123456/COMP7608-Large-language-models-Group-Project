"""Synthetic SQLite and fake-LLM tests for the generalized SQL reviewer."""
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from scr.agents.sql_reflection_reviewer import (
    SQLReflectionReviewer, PROMPT_FILE, _parse_decision,
)
from scr.baselines.sqlite_readonly import ReadOnlySqlite


class FakeReply:
    def __init__(self, content, *, tokens=None):
        self.content = content
        self.usage_metadata = tokens
        self.response_metadata = {}
        self.additional_kwargs = {}


class FakeModel:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.messages = []

    def invoke(self, messages):
        self.messages.append(messages)
        value = self.responses.pop(0)
        if isinstance(value, Exception):
            raise value
        if isinstance(value, FakeReply):
            return value
        if isinstance(value, dict):
            return FakeReply(json.dumps(value), tokens={"input_tokens": 12,
                "output_tokens": 6, "input_token_details": {"cache_read": 4}})
        return FakeReply(value)


def decision(status, *, requests=None):
    result = {
        "status": status,
        "requirements": [{"name": "requested aggregation", "expected": "average",
                          "observed": "SQL expression", "status": "PASS" if status == "PASS"
                          else "FAIL" if status == "FAIL" else "UNCERTAIN",
                          "evidence": "question and SQL"}],
        "issues": [], "feedback": "", "needs_more_evidence": False,
        "inspection_requests": [],
    }
    if status == "FAIL":
        result["issues"] = [{"category": "aggregation_logic", "severity": "critical",
                             "description": "Wrong aggregation", "evidence": "question and SQL",
                             "suggested_action": "Recheck calculation"}]
        result["feedback"] = "Recheck calculation"
    if requests:
        result["needs_more_evidence"] = True
        result["inspection_requests"] = requests
    return result


class SQLReviewTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "demo.db"
        with closing(sqlite3.connect(path)) as con, con:
            con.execute("CREATE TABLE sales (amount INTEGER, status TEXT)")
            con.executemany("INSERT INTO sales VALUES (?, ?)", [(2, "A"), (4, "A"), (6, None)])
        self.store = ReadOnlySqlite(path, max_rows=1, max_seconds=4)
        self.question = {"question_id": 1, "db_id": "demo", "question": "Average amount?",
                         "evidence": ""}

    def test_provisional_pass_and_token_usage(self):
        model = FakeModel(decision("PASS"))
        result = SQLReflectionReviewer(model).review(self.question, "SELECT AVG(amount) FROM sales", self.store)
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["candidate_safe"])
        self.assertEqual(result["model_calls"], 1)
        self.assertEqual(result["input_tokens"], 12)
        self.assertEqual(result["cached_input_tokens"], 4)
        self.assertEqual(result["tool_calls"], 1)
        self.assertIn("candidate_sql", model.messages[0][1].content)
        self.assertEqual(result["execution"]["rows"], [[4.0]])

    def test_evidence_backed_failure(self):
        result = SQLReflectionReviewer(FakeModel(decision("FAIL"))).review(
            self.question, "SELECT SUM(amount) FROM sales", self.store)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("aggregation", result["issues"][0]["category"])
        self.assertTrue(result["candidate_safe"])

    def test_invalid_final_sql_stops_without_model(self):
        model = FakeModel(decision("PASS"))
        result = SQLReflectionReviewer(model).review(self.question, "SELECT nonexisting FROM sales", self.store)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["model_calls"], 0)
        self.assertFalse(result["candidate_safe"])
        self.assertIn("no such column", result["issues"][0]["evidence"])
        unsafe = SQLReflectionReviewer(model).review(self.question, "DELETE FROM sales", self.store)
        self.assertEqual(unsafe["status"], "FAIL")
        self.assertFalse(unsafe["candidate_safe"])
        self.assertEqual(model.messages, [])

    def test_targeted_inspection_and_truncation(self):
        requests = [{"kind": "inspect_table", "table": "sales",
                     "reason": "Need to check the source columns"}]
        model = FakeModel(decision("UNCERTAIN", requests=requests), decision("PASS"))
        result = SQLReflectionReviewer(model).review(self.question,
                                                      "SELECT amount FROM sales", self.store)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["model_calls"], 2)
        self.assertEqual(result["tool_calls"], 2)
        self.assertTrue(result["execution"]["truncated"])
        self.assertEqual(result["inspection_log"][0]["kind"], "inspect_table")
        self.assertIn("inspection_observations", model.messages[1][1].content)

    def test_limited_inspection_results_in_uncertain(self):
        requests = [{"kind": "list_tables", "reason": "Verify table inventory"}]
        result = SQLReflectionReviewer(FakeModel(decision("UNCERTAIN", requests=requests)),
                                       max_model_calls=1).review(
            self.question, "SELECT amount FROM sales", self.store)
        self.assertEqual(result["status"], "UNCERTAIN")
        self.assertEqual(result["stop_reason"], "review_model_budget_exhausted")
        self.assertTrue(result["finalization_triggered"])

    def test_invalid_json_and_provider_timeout_are_not_pass(self):
        for bad in ("not json", "{}", "[]", {**decision("FAIL"), "issues": []}):
            value = bad if isinstance(bad, str) else json.dumps(bad)
            result = SQLReflectionReviewer(FakeModel(value), max_model_calls=1).review(
                self.question, "SELECT AVG(amount) FROM sales", self.store)
            self.assertEqual(result["status"], "ERROR")
            self.assertTrue(result["candidate_safe"])
        error = SQLReflectionReviewer(FakeModel(TimeoutError("provider timeout"))).review(
            self.question, "SELECT AVG(amount) FROM sales", self.store)
        self.assertEqual(error["status"], "ERROR")
        self.assertEqual(error["model_calls"], 1)
        self.assertEqual(error["stop_reason"], "review_provider_error")
        self.assertEqual(error["response_diagnostics"][0]["kind"], "provider_error")

    def test_observed_invalid_responses_repair_within_two_calls(self):
        extra_data = json.dumps(decision("PASS")) + "\\n" + json.dumps({"extra": True})
        contradictory = decision("FAIL")
        contradictory["status"] = "UNCERTAIN"  # Confirmed issues cannot be UNCERTAIN.
        no_coverage = decision("PASS")
        no_coverage["requirements"] = [{
            "name": "not applicable", "expected": "", "observed": "",
            "status": "N/A", "evidence": "",
        }]
        for invalid in (extra_data, contradictory, no_coverage):
            with self.subTest(invalid=str(invalid)[:45]):
                model = FakeModel(invalid, decision("PASS"))
                reviewed = SQLReflectionReviewer(model).review(
                    self.question, "SELECT AVG(amount) FROM sales", self.store)
                self.assertEqual(reviewed["status"], "PASS")
                self.assertEqual(reviewed["model_calls"], 2)
                self.assertEqual(reviewed["tool_calls"], 1)
                self.assertEqual(reviewed["response_diagnostics"][0]["kind"], "invalid_response")
                self.assertEqual(reviewed["response_diagnostics"][1]["kind"], "valid_decision")
                self.assertIn("response_repair", model.messages[1][1].content)

    def test_structured_format_rejection_falls_back_only_within_budget(self):
        class UnsupportedFormat(Exception):
            def __init__(self):
                super().__init__("format unsupported")
                self.response = type("Response", (), {"status_code": 400})()

        class SchemaOnlyModel:
            def __init__(self):
                self.calls = 0

            def invoke(self, messages):
                self.calls += 1
                raise UnsupportedFormat()

        class AdaptiveModel(FakeModel):
            _llm_type = "chatgpt-siwc"

            def __init__(self):
                super().__init__(decision("PASS"), decision("PASS"))
                self.strict = SchemaOnlyModel()

            def bind(self, **kwargs):
                self.requested_schema = kwargs["text_format"]
                return self.strict

        model = AdaptiveModel()
        reviewer = SQLReflectionReviewer(model)
        first = reviewer.review(self.question, "SELECT AVG(amount) FROM sales", self.store)
        self.assertEqual(first["status"], "PASS")
        self.assertEqual(first["model_calls"], 2)
        self.assertEqual(first["response_diagnostics"][0]["kind"], "provider_error")
        self.assertTrue(reviewer.structured_disabled)
        second = reviewer.review(self.question, "SELECT AVG(amount) FROM sales", self.store)
        self.assertEqual(second["status"], "PASS")
        self.assertEqual(second["model_calls"], 1)
        self.assertEqual(model.strict.calls, 1)

    def test_openai_structured_reply_keeps_raw_usage(self):
        class StructuredRunnable:
            def invoke(self, messages):
                raw = FakeReply(json.dumps(decision("PASS")), tokens={
                    "input_tokens": 31, "output_tokens": 8,
                })
                return {"raw": raw, "parsed": decision("PASS"),
                        "parsing_error": None}

        class StructuredModel:
            _llm_type = "openai-chat"

            def with_structured_output(self, schema, **kwargs):
                self.schema = schema
                self.options = kwargs
                return StructuredRunnable()

        model = StructuredModel()
        result = SQLReflectionReviewer(model).review(
            self.question, "SELECT AVG(amount) FROM sales", self.store)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["model_calls"], 1)
        self.assertEqual(result["input_tokens"], 31)
        self.assertEqual(result["output_tokens"], 8)
        self.assertTrue(model.options["include_raw"])
        self.assertTrue(model.options["strict"])

    def test_format_retry_exhaustion_preserves_unverified_sql_and_usage(self):
        tokens = {"input_tokens": 10, "output_tokens": 5,
                  "input_token_details": {"cache_read": 2}}
        model = FakeModel(FakeReply("not json", tokens=tokens),
                          FakeReply('{"status": "PASS"}', tokens=tokens))
        result = SQLReflectionReviewer(model, max_model_calls=2).review(
            self.question, "SELECT AVG(amount) FROM sales", self.store)
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["stop_reason"], "review_response_retry_exhausted")
        self.assertTrue(result["candidate_safe"])
        self.assertEqual(result["model_calls"], 2)
        self.assertEqual(result["input_tokens"], 20)
        self.assertEqual(result["output_tokens"], 10)
        self.assertEqual(result["cached_input_tokens"], 4)
        self.assertEqual(result["input_tokens_observed_calls"], 2)
        self.assertEqual(len(result["response_diagnostics"]), 2)

    def test_bad_response_after_inspection_does_not_become_pass(self):
        req = [{"kind": "list_tables", "reason": "Verify available tables"}]
        model = FakeModel(decision("UNCERTAIN", requests=req), "bad")
        result = SQLReflectionReviewer(model, max_model_calls=2).review(
            self.question, "SELECT AVG(amount) FROM sales", self.store)
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["model_calls"], 2)
        self.assertEqual(result["tool_calls"], 2)
        self.assertEqual(len(result["inspection_log"]), 1)

    def test_multiround_inspection_and_early_finalization(self):
        req = [{"kind": "list_tables", "reason": "Check available schemas"}]
        model = FakeModel(decision("UNCERTAIN", requests=req),
                          decision("UNCERTAIN", requests=req), decision("PASS"))
        result = SQLReflectionReviewer(model, max_model_calls=40, max_inspections=2).review(
            self.question, "SELECT amount FROM sales", self.store)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["model_calls"], 3)
        self.assertEqual(result["tool_calls"], 3)
        self.assertTrue(result["finalization_triggered"])
        self.assertEqual(result["finalization_reason"], "review_tool_budget_exhausted")
        self.assertTrue(json.loads(model.messages[2][1].content)["review_finalization"])

    def test_hard_40_call_cap_and_uncertain_sql(self):
        req = [{"kind": "list_tables", "reason": "Verify row semantics"}]
        model = FakeModel(*([decision("UNCERTAIN", requests=req)] * 39),
                          decision("UNCERTAIN"))
        result = SQLReflectionReviewer(model, max_model_calls=40, max_inspections=39).review(
            self.question, "SELECT amount FROM sales", self.store)
        self.assertEqual(result["status"], "UNCERTAIN")
        self.assertEqual(result["model_calls"], 40)
        self.assertEqual(result["tool_calls"], 40)
        self.assertEqual(result["sql_calls"], 1)
        self.assertTrue(result["candidate_safe"])
        self.assertTrue(result["finalization_triggered"])
        self.assertEqual(result["stop_reason"], "review_tool_budget_exhausted")
        self.assertEqual(len(model.messages), 40)

    def test_all_na_or_ungrounded_pass_is_rejected(self):
        for invalid in (
            {"name": "irrelevant", "expected": "", "observed": "",
             "status": "N/A", "evidence": ""},
            {"name": "requested aggregation", "expected": "average",
             "observed": "", "status": "PASS", "evidence": ""},
        ):
            item = decision("PASS")
            item["requirements"] = [invalid]
            with self.assertRaisesRegex(ValueError, "substantive"):
                _parse_decision(FakeReply(json.dumps(item)))

    def test_redaction_is_bounded(self):
        from scr.agents.sql_reflection_reviewer import _redact_diagnostic
        preview = _redact_diagnostic("Bearer very-private-token " + "x" * 2000)
        self.assertNotIn("very-private-token", preview)
        self.assertLess(len(preview), 1000)
        self.assertIn("[truncated]", preview)

    def test_generalized_prompt_and_false_positive_guard(self):
        prompt = PROMPT_FILE.read_text(encoding="utf-8")
        self.assertNotIn("Q431", prompt)
        self.assertNotIn("SELECT 0", prompt)
        rejected = decision("PASS")
        rejected["requirements"][0]["status"] = "UNCERTAIN"
        with self.assertRaises(ValueError):
            _parse_decision(FakeReply(json.dumps(rejected)))


if __name__ == "__main__":
    unittest.main()
