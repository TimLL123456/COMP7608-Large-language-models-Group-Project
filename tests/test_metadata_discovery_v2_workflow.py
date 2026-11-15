"""Offline metadata-discovery-v2 tests: routing, shared calls, and table/column definitions."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from langchain_core.messages import AIMessage

from scr.agents.metadata_discovery_v2 import (
    MAX_A1_ATTEMPTS, _observed_schema_facts, _validate_discovery, _validate_judgement,
    build_workflow,
)
from scr.metadata.engine import MetadataEngine


SCHEMA = {"sales lines": {"columns": [
    {"name": "status code", "type": "TEXT"},
    {"name": "amount", "type": "REAL"},
]}}

TABLE_BODY = (
    "## Business Summary\nStores purchase line records; exact exclusions unverified.\n"
    "## Business Use Cases\nSupports investigating purchases by status.\n"
    "## Data Granularity\nObserved at line level; uniqueness unverified.\n"
    "## Data Scope & Exclusions\nStatus exclusions unknown; verify before totals.\n"
)
COLUMN_BODY = (
    "## Business Meaning\nProcessing status indicator.\n"
    "## Business Usage\nUseful to filter statuses; codes unverified.\n"
    "## Value Meaning\nObserved A and B; business mapping unknown.\n"
    "## Calculation Meaning\nN/A - source column.\n"
)


class DefinitionFrameworkTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "exp-v2"
        self.engine = MetadataEngine(
            self.root, "shop", 1, SCHEMA, definition_mode=True)

    def test_table_has_four_required_components(self):
        saved = self.engine.create(
            "table", "sales lines", "table_definition", "Sales lines",
            "Sales transaction lines", "sales, transaction",
            TABLE_BODY, "schema:sales lines")
        self.assertTrue(saved["created"], saved)
        note = self.engine.read(saved["note_id"])
        self.assertIn("## Data Granularity", note["content"])
        self.assertIn("Status: provisional", note["content"])

    def test_column_uses_exact_name_even_with_spaces(self):
        saved = self.engine.create(
            "column", "sales lines", "status code", "Status code",
            "Status of transaction", "status, code",
            COLUMN_BODY, "schema:sales lines.status code")
        self.assertTrue(saved["created"], saved)
        self.assertIn("Scope: status code", self.engine.read(saved["note_id"])["content"])
        bad = self.engine.create(
            "column", "sales lines", "status_code", "Wrong", "Wrong identity",
            "status", COLUMN_BODY, "schema:sales lines.status_code")
        self.assertIn("error", bad)

    def test_reject_missing_component_and_other_types(self):
        missing = TABLE_BODY.replace("## Data Granularity", "## Other")
        self.assertIn("error", self.engine.create(
            "table", "sales lines", "table_definition", "Sales lines",
            "Summary", "sales", missing, "schema:sales lines"))
        self.assertIn("error", self.engine.create(
            "metric", "sales lines", "total_sales", "Total", "Summary",
            "sales", TABLE_BODY, "schema:sales lines"))

    def test_revision_and_decisions(self):
        item = self.engine.create(
            "table", "sales lines", "table_definition", "Sales lines",
            "Summary", "sales", TABLE_BODY, "schema:sales lines")
        updated = self.engine.update(
            item["note_id"], 1, "Sales lines", "Expanded scope",
            "sales", TABLE_BODY, "schema:sales lines")
        self.assertEqual(updated["revision"], 2)
        self.engine.record_decision(
            attempt=1, action="updated", reason="Additional evidence",
            note_ids=[item["note_id"]])
        events = [json.loads(line) for line in
                  (self.root / "knowledge_operations.jsonl").read_text().splitlines()]
        self.assertEqual(events[-1]["decision"], "updated")

    def test_old_v1_format_unchanged(self):
        legacy = MetadataEngine(self.root, "legacy", 1, SCHEMA)
        saved = legacy.create(
            "metric", "sales lines", "gross", "Sales metric",
            "Observed metric", "gross, sales", "Single observed metric",
            "schema:sales lines.amount")
        self.assertTrue(saved["created"], saved)


class FakeAgent:
    def __init__(self, content, on_start=None):
        self.content = content
        self.on_start = on_start

    def stream(self, ignored, **kwargs):
        if self.on_start:
            self.on_start()
        yield {"messages": [AIMessage(content=self.content)]}


class FakeJudge:
    def __init__(self, values):
        self.values = iter(values)

    def invoke(self, ignored):
        return AIMessage(content=json.dumps(next(self.values)))


class MetadataDiscoveryV2Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "exp-v2"
        self.engine = MetadataEngine(
            self.root, "shop", 1, SCHEMA, definition_mode=True)
        self.question = {
            "question_id": 1, "db_id": "shop",
            "question": "How many sales lines have a status code?",
            "evidence": "",
        }
        self.actions = []
        self.a1_limits = []

    def discovery(self, *, action="no_note", on_start=None):
        return FakeAgent(json.dumps({
            "note_action": action,
            "note_reason": "Existing note reused" if action == "reused" else
                           "Schema inspection shows the row level",
            "relevant_notes": [], "verified_facts": [{
                "table": "sales lines", "column": "status code",
                "finding": "Status code exists", "source_ref": "schema:sales lines.status code",
            }],
            "unresolved_facts": [],
        }), on_start=on_start)

    @staticmethod
    def sql():
        return FakeAgent('Final SQL Query:\n"""\nSELECT COUNT(*) FROM "sales lines";\n"""')

    @staticmethod
    def judge(sufficient, missing=None):
        return {"sufficient": sufficient, "missing_info": missing or [],
                "reason": "Schema sufficient" if sufficient else "Need more investigation"}

    def run_graph(self, outcomes, discovery_factory):
        fake_model = FakeJudge(outcomes)
        calls = {"a1": 0, "c1": 0}

        def create_a1(*args, **kwargs):
            calls["a1"] += 1
            self.a1_limits.append(args[-1])
            return discovery_factory(calls["a1"])

        def create_c1(*args, **kwargs):
            calls["c1"] += 1
            return self.sql()

        with patch("scr.agents.metadata_agent.make_discovery_agent",
                   side_effect=create_a1), \
             patch("scr.agents.metadata_agent.make_sql_agent",
                   side_effect=create_c1):
            graph = build_workflow(
                store=object(), metadata=self.engine, model=fake_model,
                model_name="fake", prompt_variant="generalized-v1")
            events = []
            report = graph.run_one(self.question, log=lambda x: None,
                                   trace_events=events)
        return report, events, calls

    def test_one_pass_reaches_sql(self):
        report, events, calls = self.run_graph(
            [self.judge(True)], lambda i: self.discovery())
        self.assertEqual(calls, {"a1": 1, "c1": 1})
        self.assertEqual(report["a1_attempts"], 1)
        self.assertEqual(report["b1_evaluations"], 1)
        self.assertEqual(report["model_calls"], 3)
        self.assertTrue(report["graph_completed"], report)
        self.assertIn("SELECT COUNT(*)", report["final_sql"])
        self.assertEqual(report["knowledge_decisions"], ["no_note"])
        self.assertTrue(any(e.get("kind") == "knowledge_decision" for e in events))

    def test_refinement_loops_twice(self):
        report, _, calls = self.run_graph(
            [self.judge(False, ["Meaning of status code"]), self.judge(True)],
            lambda i: self.discovery())
        self.assertEqual(calls, {"a1": 2, "c1": 1})
        self.assertEqual(report["a1_attempts"], 2)
        self.assertEqual(report["b1_evaluations"], 2)
        self.assertTrue(report["graph_completed"])

    def test_three_attempts_fall_back_to_sql_with_uncertainty(self):
        report, events, calls = self.run_graph(
            [self.judge(False, ["Missing semantics"])] * MAX_A1_ATTEMPTS,
            lambda i: self.discovery())
        self.assertEqual(calls, {"a1": 3, "c1": 1})
        self.assertEqual(report["stop_reason"], "final_sql_ready")
        self.assertTrue(report["graph_completed"])
        self.assertTrue(any(e.get("kind") == "c1_fallback" for e in events))

    def test_discovery_limits_and_global_reservation(self):
        report, _, _ = self.run_graph(
            [self.judge(True)], lambda i: self.discovery())
        self.assertEqual(self.a1_limits[0],
                         {"models": 20, "tools": 40, "sql": 20})
        self.assertEqual(report["budget_limits"]["global"],
                         {"models": 120, "tools": 200, "sql": 80})
        self.assertEqual(report["budget_limits"]["c1_reserved"],
                         {"models": 30, "tools": 40, "sql": 20})

    def test_incomplete_discovery_keeps_successful_note_writes(self):
        def make_invalid_agent(_):
            def create_note():
                made = self.engine.create(
                    "column", "sales lines", "status code", "Status code",
                    "Status field", "status, code", COLUMN_BODY,
                    "schema:sales lines.status code")
                self.assertTrue(made["created"], made)
            return FakeAgent("A1 did not finalize valid JSON", on_start=create_note)

        report, events, calls = self.run_graph(
            [self.judge(False, [])], make_invalid_agent)
        self.assertEqual(calls, {"a1": 1, "c1": 1})
        self.assertEqual(report["knowledge_decisions"], ["created"])
        self.assertTrue(report["graph_completed"])
        self.assertTrue(any(e.get("kind") == "c1_fallback" for e in events))

    def test_real_write_and_later_read(self):
        note_id = []

        def create_note():
            made = self.engine.create(
                "column", "sales lines", "status code", "Status code",
                "Status field", "status, code", COLUMN_BODY,
                "schema:sales lines.status code")
            self.assertTrue(made["created"], made)
            note_id.append(made["note_id"])

        report, _, calls = self.run_graph(
            [self.judge(True)],
            lambda i: self.discovery(action="created", on_start=create_note))
        self.assertEqual(report["knowledge_decisions"], ["created"])
        self.assertEqual(self.engine.read(note_id[0])["revision"], 1)
        later = MetadataEngine(self.root, "shop", 99, SCHEMA, definition_mode=True)
        found = later.search("status code")
        self.assertEqual(found["candidates"][0]["note_id"], note_id[0])

    def test_false_claim_of_write_is_detected(self):
        report, _, _ = self.run_graph(
            [self.judge(True)],
            lambda i: self.discovery(action="created"))
        self.assertEqual(report["knowledge_decisions"], ["decision_inconsistent"])

    def test_schema_inspection_facts_survive_missing_a1_json(self):
        events = [
            {"kind": "tool_call", "name": "inspect_table",
             "tool_call_id": "ins-1", "args": {"table_name": "sales lines"}},
            {"kind": "tool_result", "name": "inspect_table",
             "tool_call_id": "ins-1", "status": "success",
             "output": json.dumps({"columns": [
                 {"name": "status code", "type": "TEXT"},
                 {"name": "amount", "type": "REAL"},
             ], "foreign_keys": []})},
        ]
        recovered = _observed_schema_facts(events)
        self.assertEqual(len(recovered), 2)
        self.assertEqual(recovered[0]["source_ref"],
                         "schema:sales lines.status code")
        self.assertTrue(all(item["finding"].startswith("Column exists")
                            for item in recovered))

    def test_invalid_judge_shape_rejected(self):
        with self.assertRaises(ValueError):
            _validate_judgement('{"sufficient":"yes","reason":"x","missing_info":[]}')
        with self.assertRaises(ValueError):
            _validate_discovery('{"note_action":"created"}')


if __name__ == "__main__":
    unittest.main()
