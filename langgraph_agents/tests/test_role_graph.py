"""Compare real LangGraph routing against the untouched Role Agent."""
from __future__ import annotations

from types import MethodType

import pytest

from langgraph_agents.role_specialized.coordinator import LangGraphRoleSpecializedAgent
from langgraph_agents.role_specialized.graph import build_graph
from scr.agents.role_specialized.coordinator import RoleSpecializedSelfReflectionAgent


QUESTION = {"question_id": 21, "db_id": "sample", "question": "Count the rows",
            "evidence": "Use sample"}
REQ = {"requirement_id": "output", "material": True, "status": "UNCERTAIN",
       "expected": "COUNT(*)"}


class Store:
    def execute(self, sql):
        return {"error": "invalid SQL"} if sql == "BAD SQL" else {"rows": [[1]]}


class Reviewer:
    max_model_calls = 40
    max_inspections = 39

    def __init__(self, decisions, extraction="PASS"):
        self.decisions = iter(decisions)
        self.extraction = extraction
        self.extractions = 0
        self.reviews = []

    def extract(self, question, *, max_calls=2):
        self.extractions += 1
        return {"status": self.extraction,
                "requirements": [REQ] if self.extraction == "PASS" else [],
                "error": "provider error" if self.extraction == "ERROR" else None,
                "model_calls": 1, "tool_calls": 0, "sql_calls": 0}

    def review(self, question, sql, store, requirements, *,
               previous_feedback="", max_model_calls=None, max_inspections=None):
        self.reviews.append((question, sql, previous_feedback))
        decision = next(self.decisions)
        safe = decision.get("safe", True)
        return {"status": decision["status"], "candidate_safe": safe,
                "requirements": decision.get("requirements", [REQ]),
                "coverage": {"status": "COMPLETE"}, "issues": [],
                "feedback": decision.get("feedback", ""),
                "execution": {"rows": [[1]]} if safe else {"error": "invalid"},
                "inspection_log": [], "stop_reason": "review_finished",
                "model_calls": 1, "tool_calls": 1, "sql_calls": 1}


def make_agent(agent_cls, sqls, decisions, *, extraction="PASS", generated_usage=2, **config):
    reviewer = Reviewer(decisions, extraction=extraction)
    agent = agent_cls(reviewer, generator_model=object(),
                      prompt_variant="generalized-v1", **config)
    requests = []
    sql_iter = iter(sqls)

    def generate(self, question, store):
        requests.append(question)
        sql = next(sql_iter)
        return {"candidate_sql": sql,
                "report": {"graph_completed": bool(sql), "final_sql": sql,
                           "stop_reason": "ready", "model_calls": generated_usage,
                           "tool_calls": 40 if generated_usage == 40 else 1,
                           "sql_calls": 40 if generated_usage == 40 else 1},
                "events": [{"kind": "tool_result", "name": "inspect_table",
                            "output": "sample(id integer)"}],
                "completion": {"triggered": False, "status": "not_needed"}}

    agent._b0_generate = MethodType(generate, agent)
    return agent, reviewer, requests


@pytest.mark.parametrize(
    "sqls,decisions,expected_sql,status,stop",
    [
        (["SELECT 1"], [{"status": "PASS"}],
         "SELECT 1", "verified", "reviewer_pass"),
        (["SELECT 1", "SELECT 2"],
         [{"status": "FAIL", "feedback": "Fix metric"}, {"status": "PASS"}],
         "SELECT 2", "verified", "reviewer_pass"),
        (["SELECT 1", "SELECT 2"],
         [{"status": "UNCERTAIN"}, {"status": "PASS"}],
         "SELECT 2", "verified", "reviewer_pass"),
        (["SELECT 1"], [{"status": "ERROR"}],
         "SELECT 1", "generated_unverified", "review_finished"),
        (["SELECT 1"], [{"status": "FAIL", "safe": False}],
         None, "missing", "review_finished"),
        (["SELECT 1", "SELECT 1"],
         [{"status": "FAIL", "feedback": "Fix"}],
         "SELECT 1", "generated_known_issues", "no_progress_repeated_sql"),
        ([None], [], None, "missing", "generator_no_sql"),
    ],
)
def test_legacy_parity(sqls, decisions, expected_sql, status, stop):
    outputs = []
    for cls in (RoleSpecializedSelfReflectionAgent, LangGraphRoleSpecializedAgent):
        agent, reviewer, requests = make_agent(cls, sqls, decisions)
        result = agent.run(QUESTION, Store())
        assert result["final_sql"] == expected_sql
        assert result["report"]["output_status"] == status
        assert result["stop_reason"] == stop
        assert reviewer.extractions == (0 if sqls[0] is None else 1)
        assert len(requests) == result["report"]["attempt_count"]
        if len(requests) > 1 and sqls[1] != sqls[0]:
            assert "REVIEW DIAGNOSTIC CONTEXT" in requests[1]["evidence"]
        outputs.append(result)
    before, after = outputs
    for key in ("attempts", "review_reports", "extraction", "generator_usage",
                "reviewer_usage", "final_sql", "review_status", "stop_reason",
                "structured_events"):
        assert after[key] == before[key], key
    for key in ("graph_completed", "review_status", "output_status", "stop_reason",
                "attempt_count", "review_report_count", "model_calls", "tool_calls",
                "sql_calls"):
        assert after["report"][key] == before["report"][key], key
    assert after["graph_events"]


@pytest.mark.parametrize(
    "sqls,extraction,budget,expected_sql,stop",
    [
        (["SELECT 1"], "ERROR", 240, "SELECT 1", "requirements_extraction_error"),
        (["SELECT 1"], "PASS", 41, "SELECT 1", "global_budget_before_review"),
        (["SELECT 1"], "PASS", 39, None, "global_budget_before_generator"),
        (["BAD SQL"], "ERROR", 240, None, "requirements_extraction_error"),
    ],
)
def test_budget_fallback_parity(sqls, extraction, budget, expected_sql, stop):
    for cls in (RoleSpecializedSelfReflectionAgent, LangGraphRoleSpecializedAgent):
        agent, reviewer, _ = make_agent(
            cls, sqls, [], extraction=extraction, max_total_model_calls=budget,
            generated_usage=40 if budget == 41 else 2,
        )
        result = agent.run(QUESTION, Store())
        assert result["final_sql"] == expected_sql
        assert result["stop_reason"] == stop
        assert result["review_reports"] == []
        assert reviewer.reviews == []


def test_real_conditional_retry_edges_and_reports():
    agent, reviewer, _ = make_agent(
        LangGraphRoleSpecializedAgent, ["SELECT 1", "SELECT 2"],
        [{"status": "FAIL", "feedback": "Fix"}, {"status": "PASS"}],
    )
    result = agent.run(QUESTION, Store())
    assert [e["node"] for e in result["graph_events"]] == [
        "prepare_input", "generate_sql", "review_sql", "route_decision",
        "generate_sql", "review_sql", "route_decision", "finalize_sql",
    ]
    assert reviewer.extractions == 1
    assert [r["review_status"] for r in result["review_reports"]] == ["FAIL", "PASS"]
    assert "GENERATOR OBSERVATIONS" in reviewer.reviews[0][0]["evidence"]


def test_no_gold_sql_to_models():
    agent, _, requests = make_agent(LangGraphRoleSpecializedAgent, [], [])
    with pytest.raises(ValueError, match="Reference SQL"):
        agent.run({**QUESTION, "SQL": "SELECT 42"}, Store())
    assert requests == []


def test_checkpoint_serializable_state():
    import time
    from langgraph.checkpoint.memory import MemorySaver
    agent, _, _ = make_agent(LangGraphRoleSpecializedAgent, ["SELECT 1"],
                              [{"status": "PASS"}])
    graph = build_graph(coordinator=agent, store=Store(), checkpointer=MemorySaver())
    result = graph.invoke(
        {"question": QUESTION, "started_at": time.monotonic()},
        config={"configurable": {"thread_id": "sample"}},
    )
    assert result["final_sql"] == "SELECT 1"
    assert "store" not in result and "model" not in result


def test_isolated_cli_defaults_and_control_variants():
    from langgraph_agents.role_specialized import cli
    from scr.agents.role_specialized import cli as original
    args = cli.parser().parse_args([
        "infer", "--selection-id", "sample", "--split", "dev", "--run-id", "run",
    ])
    assert args.generator_provider == args.reviewer_provider == "chatgpt-siwc"
    assert args.generator_model is args.reviewer_model is None
    assert args.generator_reasoning_effort is args.reviewer_reasoning_effort is None
    assert (args.max_attempts, args.max_review_model_calls, args.max_inspections) == (3, 40, 39)
    assert (args.max_total_model_calls, args.max_total_tool_calls,
            args.max_total_sql_calls) == (240, 240, 240)
    assert args.prompt_variant == "generalized-v1"
    assert cli.VARIANT == "LangGraphRoleSpecializedSelfReflection"
    assert original.VARIANT == "RoleSpecializedSelfReflection"
    assert cli.parser().parse_args([
        "compare", "--selection-id", "sample", "--split", "dev", "--run-id", "test",
        "--control-run-id", "original", "--control-variant",
        "RoleSpecializedSelfReflection",
    ]).control_variant == "RoleSpecializedSelfReflection"


def test_failed_first_generator_still_visible_in_trace():
    from scr.tracing.graph import build_graph as trace_graph
    agent, _, _ = make_agent(LangGraphRoleSpecializedAgent, [None], [])
    result = agent.run(QUESTION, Store())
    graph = trace_graph({"question_id": QUESTION["question_id"],
                         "question": QUESTION["question"], "evidence": "",
                         **result})
    assert [node["kind"] for node in graph["nodes"]] == [
        "input", "stage", "stage", "final",
    ]
    assert graph["nodes"][-1]["detail"]["status"] == "missing"
