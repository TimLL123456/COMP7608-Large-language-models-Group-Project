"""Behavioral parity for the 4 remaining agents; no provider calls."""
from __future__ import annotations

import json
import random
from pathlib import Path
from types import MethodType
from unittest.mock import patch

import pytest

from langgraph_agents.self_reflection.graph import (
    LangGraphSelfReflectionAgent, build_graph as build_self_graph,
)
from langgraph_agents.rubric_self_reflection.graph import (
    LangGraphRubricSelfReflectionAgent, build_graph as build_rubric_graph,
)
from langgraph_agents.metadata_v1 import agent as metadata_v1
from langgraph_agents.metadata_discovery_v2 import workflow as metadata_v2
from scr.agents.self_reflection_agent import SelfReflectionAgent
from scr.agents.rubric_self_reflection import coordinator as rubric_module
from scr.agents.metadata_discovery_v2 import build_workflow as original_meta_v2

Q = {"question_id": 17, "db_id": "sample", "question": "Count entries",
     "evidence": "Use sample records."}


class Store:
    def execute(self, sql):
        return {"error": "invalid SQL"} if sql == "INVALID" else {
            "columns": ["n"], "rows": [[1]], "row_count": 1}


class SelfReviewer:
    max_model_calls = 40
    max_inspections = 39

    def __init__(self, decisions):
        self.decisions = iter(decisions)
        self.feedbacks = []

    def review(self, question, sql, store, *, previous_feedback=None):
        self.feedbacks.append((sql, previous_feedback))
        status = next(self.decisions)
        return {
            "status": status, "candidate_safe": sql != "INVALID",
            "stop_reason": "review_finished",
            "feedback": "Fix filter" if status == "FAIL" else "",
            "issues": [], "model_calls": 1, "tool_calls": 1,
            "sql_calls": 1, "input_tokens": 2, "output_tokens": 3,
            "latency_ms": 5,
        }


class RubricReviewer:
    max_model_calls = 40
    max_inspections = 39

    def __init__(self, decisions, extraction="PASS"):
        self.decisions = iter(decisions)
        self.extraction = extraction
        self.extractions = 0

    def extract(self, question, *, max_calls=2):
        self.extractions += 1
        return {"status": self.extraction, "error": "provider failed" if self.extraction != "PASS" else None,
                "requirements": [{"requirement_id": "metric", "expected": "COUNT",
                                  "material": True, "status": "PASS"}],
                "model_calls": 1, "tool_calls": 0, "sql_calls": 0}

    def review(self, question, sql, store, requirements, *,
               previous_feedback="", max_model_calls=None, max_inspections=None):
        status = next(self.decisions)
        return {
            "status": status, "candidate_safe": sql != "INVALID",
            "requirements": [{"requirement_id": "metric", "expected": "COUNT",
                              "material": True,
                              "status": "FAIL" if status == "FAIL" else "PASS"}],
            "coverage": {"status": "COMPLETE"}, "issues": [],
            "feedback": "Fix filter" if status == "FAIL" else "",
            "inspection_log": [], "execution": store.execute(sql),
            "stop_reason": "review_finished", "model_calls": 1,
            "tool_calls": 1, "sql_calls": 1,
        }


def normalized(result):
    report = {key: value for key, value in result["report"].items()
              if key != "seconds"}
    return {
        **{key: value for key, value in result.items()
           if key not in ("graph_events", "report")},
        "report": report,
    }


def _random_self_cases():
    rng = random.Random(20261117)
    sql_pool = ["SELECT 1", "SELECT 2", "SELECT 3", "INVALID", None]
    decisions = ["PASS", "FAIL", "UNCERTAIN", "ERROR"]
    return [
        ([rng.choice(sql_pool) for _ in range(3)],
         [rng.choice(decisions) for _ in range(3)],
         rng.choice([39, 40, 41, 80, 120, 240]))
        for _ in range(64)
    ]


def _random_rubric_cases():
    rng = random.Random(20261118)
    sql_pool = ["SELECT 1", "SELECT 2", "SELECT 3", "INVALID", None]
    decisions = ["PASS", "FAIL", "UNCERTAIN", "ERROR"]
    return [
        ([rng.choice(sql_pool) for _ in range(3)],
         [rng.choice(decisions) for _ in range(3)],
         rng.choice(["PASS", "PASS", "ERROR"]),
         rng.choice([39, 40, 41, 80, 120, 240]))
        for _ in range(64)
    ]


@pytest.mark.parametrize(
    "sqls,decisions,budget",
    [
        (["SELECT 1"], ["PASS"], 240),
        (["SELECT 1", "SELECT 2"], ["FAIL", "PASS"], 240),
        (["SELECT 1"], ["UNCERTAIN"], 240),
        (["SELECT 1"], ["ERROR"], 240),
        (["INVALID", "SELECT 2"], ["FAIL", "PASS"], 240),
        (["SELECT 1", "SELECT 1"], ["FAIL"], 240),
        ([None], [], 240),
        (["SELECT 1"], ["PASS"], 39),
    ] + _random_self_cases(),
)
def test_self_reflection_legacy_parity(sqls, decisions, budget):
    outputs = []
    traces = []
    for cls in (SelfReflectionAgent, LangGraphSelfReflectionAgent):
        reviewer = SelfReviewer(decisions)
        agent = cls(reviewer, model=object(), prompt_variant="generalized-v1",
                    max_total_model_calls=budget)
        calls = iter(sqls)

        def run_one(question, agent, log=None, trace_events=None):
            sql = next(calls)
            if trace_events is not None:
                trace_events.append({
                    "kind": "model", "model_call": 1, "content": "candidate",
                    "input_tokens": 1, "output_tokens": 1,
                })
            return {"graph_completed": bool(sql), "final_sql": sql,
                    "stop_reason": "final_sql_ready" if sql else "no_sql",
                    "model_calls": 2, "tool_calls": 1, "sql_calls": 1,
                    "input_tokens": 10, "output_tokens": 10}

        def finalize_b0(self, question, store, report, events):
            report["finalization"] = {
                "triggered": True, "status": "missing",
                "model_calls": 1, "tool_calls": 0, "sql_calls": 0,
            }
            report["model_calls"] += 1
            return None

        with patch("scr.baselines.bird_b0.make_agent", lambda *a, **kw: object()), \
             patch("scr.baselines.bird_b0.run_one", run_one), \
             patch.object(cls, "_finalize_b0", finalize_b0):
            result = agent.run(Q, Store())
        outputs.append(normalized(result))
        traces.append([e["node"] for e in result.get("graph_events", [])])
    assert outputs[0] == outputs[1]
    assert traces[1][0] == "prepare_input" and traces[1][-1] == "finalize_sql"
    assert len(outputs[1]["attempts"]) <= traces[1].count("generate_sql") <= len(outputs[1]["attempts"]) + 1


@pytest.mark.parametrize(
    "sqls,decisions,extract,budget",
    [
        (["SELECT 1"], ["PASS"], "PASS", 240),
        (["SELECT 1", "SELECT 2"], ["FAIL", "PASS"], "PASS", 240),
        (["SELECT 1"], ["UNCERTAIN"], "PASS", 240),
        (["SELECT 1"], ["ERROR"], "PASS", 240),
        (["SELECT 1"], [], "ERROR", 240),
        (["SELECT 1", "SELECT 1"], ["FAIL"], "PASS", 240),
        ([None], [], "PASS", 240),
        (["SELECT 1"], [], "PASS", 40),
        (["INVALID", "INVALID"], ["FAIL"], "PASS", 240),
    ] + _random_rubric_cases(),
)
def test_rubric_legacy_parity(sqls, decisions, extract, budget):
    outputs = []
    traces = []
    for cls in (rubric_module.RubricSelfReflectionAgent,
                LangGraphRubricSelfReflectionAgent):
        reviewer = RubricReviewer(decisions, extraction=extract)
        agent = cls(reviewer, model=object(), finalizer_model=object(),
                    prompt_variant="generalized-v1",
                    max_total_model_calls=budget)
        source = iter(sqls)

        def generate(self, question, store):
            sql = next(source)
            return {"candidate_sql": sql,
                    "report": {"graph_completed": bool(sql), "final_sql": sql,
                               "stop_reason": "ready", "model_calls": 1,
                               "tool_calls": 1, "sql_calls": 1,
                               "finalization": {"triggered": False}},
                    "events": [{"kind": "tool_result", "output": "schema"}],
                    "completion": {"triggered": False}}

        agent._b0_generate = MethodType(generate, agent)

        def refine(model, question, sql, review, observations, store,
                   *, allow_model, allow_execution):
            return {"triggered": True, "status": "not_executable",
                    "model_calls": 1, "tool_calls": 1, "sql_calls": 1,
                    "sql": None, "error": "Not enough evidence"}

        with patch.object(rubric_module, "refine_sql", refine):
            result = agent.run(Q, Store())
        outputs.append(normalized(result))
        traces.append([e["node"] for e in result.get("graph_events", [])])
    assert outputs[0] == outputs[1]
    assert traces[1][0] == "prepare_input"
    assert traces[1][1] == "extract_requirements"
    assert traces[1][-2:] == ["refine_sql", "finalize_sql"]


def test_metadata_v1_outer_graph_parity(monkeypatch):
    from scr.agents import metadata_agent as legacy
    observed = []
    def fake_run_one(question, agent, log=print, trace_events=None):
        observed.append(question["question_id"])
        if trace_events is not None:
            trace_events.append({"kind": "model", "content": "SQL ready"})
        return {"final_sql": "SELECT 1", "graph_completed": True,
                "model_calls": 2, "tool_calls": 1, "sql_calls": 1}
    monkeypatch.setattr(legacy, "run_one", fake_run_one)
    trace = []
    before = legacy.run_one(Q, object())
    after = metadata_v1.run_one(Q, object(), trace_events=trace)
    assert before == after
    assert observed == [Q["question_id"], Q["question_id"]]
    assert trace[0]["kind"] == "model"
    assert [e["node"] for e in trace[1:]] == [
        "prepare_input", "run_metadata_v1", "collect_output"]


def test_metadata_v2_contains_actual_a1_b1_c1_stategraph(tmp_path):
    from scr.agents.metadata_discovery_v2 import build_workflow
    from scr.metadata.engine import MetadataEngine
    notes = MetadataEngine(tmp_path, "sample", 1, schema={"sample": { }},
                           descriptions={}, definition_mode=True)
    instance = build_workflow(Store(), notes, object(), "fake-model")
    nodes = set(instance.graph.get_graph().nodes)
    assert {"a1", "b1", "c1", "exhausted"}.issubset(nodes)
    assert instance.report["budget_limits"]["global"]["models"] == 120
    assert instance.report["budget_limits"]["global"]["tools"] == 200
    assert instance.report["budget_limits"]["global"]["sql"] == 80


def test_metadata_v2_reuses_original_stategraph(monkeypatch):
    sentinel = object()
    from langgraph_agents.metadata_discovery_v2 import workflow
    monkeypatch.setattr(workflow, "legacy_build_workflow",
                        lambda *args, **kwargs: sentinel)
    assert workflow.build_workflow(None, None, None, "model") is sentinel
    from scr.agents.metadata_discovery_v2 import MetadataDiscoveryV2Workflow
    assert hasattr(MetadataDiscoveryV2Workflow, "a1")
    assert hasattr(MetadataDiscoveryV2Workflow, "b1")
    assert hasattr(MetadataDiscoveryV2Workflow, "c1")


def test_cli_parsers_and_independent_variants():
    from langgraph_agents.self_reflection import cli as scli
    from langgraph_agents.rubric_self_reflection import cli as rcli
    from langgraph_agents.metadata_v1 import cli as mcli
    from langgraph_agents.metadata_discovery_v2 import cli as vcli
    from scr.evaluation.bird import VARIANTS
    for cli, variant in (
        (scli, "LangGraphSelfReflection"),
        (rcli, "LangGraphRubricSelfReflection"),
        (mcli, "LangGraphMetadata"),
        (vcli, "LangGraphMetadataDiscoveryV2"),
    ):
        assert cli.VARIANT == variant if hasattr(cli, "VARIANT") else cli._variant(
            cli.parser().parse_args(["infer", "--selection-id", "s",
                                     "--split", "dev", "--run-id", "r",
                                     "--experiment-id", "exp"])) == variant
        assert variant in VARIANTS

    for cli in (mcli, vcli):
        args = cli.parser().parse_args([
            "infer", "--selection-id", "sample", "--split", "dev",
            "--run-id", "run", "--experiment-id", "exp",
        ])
        assert cli._variant(args) in VARIANTS
        assert args.provider == "nvidia"
        assert args.prompt_variant == "generalized-v1"
        assert args.workflow == ("v1" if cli is mcli else "metadata-discovery-v2")
