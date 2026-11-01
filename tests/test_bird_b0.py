"""No-network B0 tests: direct Python Deep Agents baseline and trace handling."""
import unittest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage, ToolMessage
from scr.baselines import bird_b0 as b0


class StreamAgent:
    def __init__(self, snapshots, error=None):
        self.snapshots = snapshots
        self.error = error

    def stream(self, inputs, config, stream_mode):
        assert config["recursion_limit"] == 100
        assert stream_mode == "values"
        for snapshot in self.snapshots:
            yield {"messages": snapshot}
        if self.error:
            raise self.error


class B0Tests(unittest.TestCase):
    def setUp(self):
        self.q = {
            "question_id": 1409, "db_id": "student_club",
            "question": "Mention the total expense used on 8/20/2019.",
            "evidence": "total expense refers SUM(cost)",
            "SQL": "GOLD_NEVER_VISIBLE",
        }
        self.final = 'Final SQL Query:\n"""\nSELECT SUM(cost) FROM expense\n"""'

    def test_question_evidence_only(self):
        prompt = b0.make_prompt(self.q)
        self.assertIn("Mention the total expense", prompt)
        self.assertIn("SUM(cost)", prompt)
        self.assertNotIn("GOLD_NEVER_VISIBLE", prompt)

    def test_extract_one_labelled_sql_only(self):
        self.assertEqual(b0.extract_final_sql(self.final), "SELECT SUM(cost) FROM expense")
        self.assertEqual(b0.extract_final_sql('Final SQL Query:\n"""\nSELECT 42\n"""'), "SELECT 42")
        for invalid in ("SELECT 42", 'Final SQL Query:\n"""\nDELETE FROM a\n"""', "",
                        'Final SQL Query:\n"""\nSELECT 1\n"""\nFinal SQL Query:\n"""\nSELECT 2\n"""'):
            with self.subTest(invalid=invalid):
                self.assertIsNone(b0.extract_final_sql(invalid))

    def test_q45_inline_delimiter_is_valid(self):
        answer = 'Final SQL Query: """\nSELECT s.School, sc.AvgScrWrite FROM schools s JOIN satscores sc ON s.CDSCode = sc.cds;\n"""'
        self.assertIn("AvgScrWrite", b0.extract_final_sql(answer))
        self.assertIsNone(b0.extract_final_sql('Final SQL Query: """\nSELECT 1; SELECT 2;\n"""'))
        self.assertIsNone(b0.extract_final_sql('Final SQL Query: """\nDELETE FROM schools;\n"""'))

    def test_structured_trace_links_tools_and_validation(self):
        call = {"name": "execute_sql", "args": {"sql": "SELECT 42"},
                "id": "trace-tool", "type": "tool_call"}
        ai = AIMessage(content="", tool_calls=[call])
        result = ToolMessage(name="execute_sql", content='{"rows":[[42]],"execution_ms":1.2}',
                             tool_call_id="trace-tool")
        final = AIMessage(content='Final SQL Query: """\nSELECT 42;\n"""')
        events = []
        report = b0.run_one(self.q, StreamAgent([[ai], [ai, result], [ai, result, final]]),
                            log=lambda _: None, trace_events=events)
        self.assertEqual(report["stop_reason"], "final_sql_ready")
        self.assertEqual([item["kind"] for item in events],
                         ["model", "tool_call", "tool_result", "model", "final_validation"])
        self.assertEqual(events[1]["tool_call_id"], events[2]["tool_call_id"])
        self.assertEqual(events[2]["execution_ms"], 1.2)

    def test_q1409_graph_success_without_fallback(self):
        call = {"name": "execute_sql", "args": {"sql": "SELECT 42"},
                "id": "x1", "type": "tool_call"}
        ai = AIMessage(content="", tool_calls=[call],
                       usage_metadata={"input_tokens": 25, "output_tokens": 5, "total_tokens": 30})
        result = ToolMessage(name="execute_sql", content='{"rows":[[42]]}', tool_call_id="x1")
        final = AIMessage(content=self.final)
        agent = StreamAgent([[ai], [ai, result], [ai, result, final]])
        report = b0.run_one(self.q, agent, log=lambda _: None)
        self.assertTrue(report["graph_completed"])
        self.assertEqual(report["final_sql"], "SELECT SUM(cost) FROM expense")
        self.assertEqual(report["tool_calls"], 1)
        self.assertEqual(report["sql_calls"], 1)
        self.assertEqual(report["model_calls"], 2)

    def test_q1409_recursion_keeps_observation_not_prediction(self):
        agent = StreamAgent([[AIMessage(content=self.final)]],
                            RuntimeError("recursion limit reached"))
        report = b0.run_one(self.q, agent, log=lambda _: None)
        self.assertFalse(report["graph_completed"])
        self.assertIsNone(report["final_sql"])
        self.assertEqual(report["final_sql_observed"], "SELECT SUM(cost) FROM expense")
        self.assertEqual(report["stop_reason"], "RuntimeError")

    def test_builtin_virtual_filesystem_tool_is_allowed_in_trace(self):
        call = {"name": "write_file", "args": {"file_path": "/scratch/plan.md", "content": "plan"},
                "id": "builtin1", "type": "tool_call"}
        ai = AIMessage(content="", tool_calls=[call])
        tool_result = ToolMessage(
            name="write_file", content="File written to virtual state",
            tool_call_id="builtin1",
        )
        final = AIMessage(content=self.final)
        report = b0.run_one(
            self.q,
            StreamAgent([[ai], [ai, tool_result], [ai, tool_result, final]]),
            log=lambda _: None,
        )
        self.assertTrue(report["graph_completed"])
        self.assertEqual(report["final_sql"], "SELECT SUM(cost) FROM expense")
        self.assertEqual(report["tool_calls"], 1)
        self.assertEqual(report["sql_calls"], 0)
        self.assertIsNone(report["error"])


    def test_sql_tool_outcome_and_timing(self):
        call = {"name":"execute_sql", "args":{"sql":"SELECT 1"}, "id":"x", "type":"tool_call"}
        msg = AIMessage(content="", tool_calls=[call])
        output = ToolMessage(name="execute_sql", tool_call_id="x",
                             content='{"rows":[[1]],"truncated":true,"execution_ms":3.25}')
        final = AIMessage(content=self.final)
        report = b0.run_one(self.q, StreamAgent([[msg],[msg,output],[msg,output,final]]), log=lambda _:None)
        self.assertEqual(report["sql_success_calls"], 1)
        self.assertEqual(report["sql_truncated_calls"], 1)
        self.assertEqual(report["agent_sql_execution_ms"], 3.25)
        self.assertTrue(report["sql_execution_observed"])

    def test_plain_text_is_not_sql_success(self):
        r = b0.run_one(self.q, StreamAgent([[AIMessage(content="42")]]), log=lambda _: None)
        self.assertTrue(r["graph_completed"])
        self.assertIsNone(r["final_sql"])
        self.assertEqual(r["stop_reason"], "invalid_final_answer")

    def test_settings(self):
        self.assertEqual((b0.MAX_MODEL_CALLS, b0.MAX_TOTAL_TOOL_CALLS,
                          b0.MAX_SQL_EXECUTIONS), (20, 20, 20))
        self.assertEqual(b0.MODEL, "nvidia/nemotron-3.5-super-vl-120b-a12b")
        self.assertEqual(b0.RECURSION_LIMIT, 100)

    def test_deep_agent_tool_budgets_and_default_harness(self):
        store = MagicMock()
        with patch("deepagents.create_deep_agent") as create:
            b0.make_agent(store, model=MagicMock())
        options = create.call_args.kwargs
        self.assertEqual(
            {t.name for t in options["tools"]},
            {"list_tables", "inspect_table", "execute_sql"},
        )
        self.assertNotIn("backend", options)
        self.assertNotIn("subagents", options)
        self.assertEqual(len(options["middleware"]), 3)
        self.assertEqual([m.run_limit for m in options["middleware"]], [20, 20, 20])
        self.assertEqual(
            [m.exit_behavior for m in options["middleware"]],
            ["error", "error", "error"],
        )
        self.assertEqual(
            [m.tool_name for m in options["middleware"][1:]],
            [None, "execute_sql"],
        )

    def test_real_deep_agents_constructor_without_hosted_model(self):
        """Use real Deep Agents middleware, not a mocked create_deep_agent."""
        from langchain_core.language_models.chat_models import BaseChatModel
        from langchain_core.outputs import ChatGeneration, ChatResult

        class OfflineModel(BaseChatModel):
            @property
            def _llm_type(self):
                return "offline-bird-b0-test"

            def _generate(self, messages, stop=None, run_manager=None, **kwargs):
                return ChatResult(generations=[
                    ChatGeneration(message=AIMessage(content='Final SQL Query:\n"""\nSELECT 1\n"""'))
                ])

            def bind_tools(self, tools, **kwargs):
                return self

        store = MagicMock()
        agent = b0.make_agent(store, model=OfflineModel())
        self.assertIsNotNone(agent)
        report = b0.run_one(self.q, agent, log=lambda _: None)
        self.assertTrue(report["graph_completed"], report["error"])
        self.assertEqual(report["final_sql"], "SELECT 1")


if __name__ == "__main__":
    unittest.main()
