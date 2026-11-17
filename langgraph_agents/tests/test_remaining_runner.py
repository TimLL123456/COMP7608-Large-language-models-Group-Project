"""Offline end-to-end CLI and SQLite artifact tests for the migrated agents."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest

from langgraph_agents.self_reflection import cli as self_cli
from langgraph_agents.rubric_self_reflection import cli as rubric_cli
from langgraph_agents.metadata_v1 import cli as metadata_cli
from langgraph_agents.metadata_discovery_v2 import cli as discovery_cli
from scr.agents import metadata_agent as legacy_metadata


@pytest.fixture()
def selected_fixture(tmp_path):
    root = tmp_path / "run-root"
    folder = root / "smoke"
    folder.mkdir(parents=True)
    (folder / "selection_manifest.json").write_text('{"selection":"immutable"}\n')
    with sqlite3.connect(tmp_path / "sample.sqlite") as connection:
        connection.execute("CREATE TABLE sample (value INTEGER)")
        connection.executemany("INSERT INTO sample VALUES (?)", [(1,), (2,)])
    dataset = SimpleNamespace(
        manifest={"dataset": "synthetic-for-test"},
        get_database_path=lambda db_id: tmp_path / "sample.sqlite",
        get_schema=lambda db_id: {"sample": {"value": "INTEGER"}},
        get_descriptions=lambda db_id: {},
    )
    questions = {
        "dev": [{"question_id": 1, "db_id": "sample",
                 "question": "Count sample rows", "evidence": ""}],
        "test": [{"question_id": 2, "db_id": "sample",
                  "question": "Count sample rows", "evidence": ""}],
    }

    def selected(args):
        return folder, dataset, questions[args.split]

    return root, folder, dataset, selected


class SelfReviewer:
    max_model_calls = 40
    max_inspections = 39

    def __init__(self, *args, **kwargs):
        pass

    def review(self, question, sql, store, *, previous_feedback=None):
        check = store.execute(sql)
        return {"status": "PASS", "candidate_safe": "error" not in check,
                "feedback": "", "issues": [], "stop_reason": "verified",
                "model_calls": 1, "tool_calls": 1, "sql_calls": 1}


class RubricReviewer:
    max_model_calls = 40
    max_inspections = 39

    def __init__(self, *args, **kwargs):
        pass

    def extract(self, question, *, max_calls=2):
        return {"status": "PASS", "requirements": [], "model_calls": 1,
                "tool_calls": 0, "sql_calls": 0}

    def review(self, question, sql, store, requirements, *,
               previous_feedback="", max_model_calls=None, max_inspections=None):
        check = store.execute(sql)
        return {"status": "PASS", "candidate_safe": "error" not in check,
                "requirements": [], "coverage": {"status": "COMPLETE"},
                "inspection_log": [], "execution": check, "issues": [],
                "feedback": "", "stop_reason": "verified",
                "model_calls": 1, "tool_calls": 1, "sql_calls": 1}


@pytest.mark.parametrize(
    "cli,reviewer_attr,reviewer_cls,variant,expected_nodes",
    [
        (self_cli, "SQLReflectionReviewer", SelfReviewer, "LangGraphSelfReflection",
         ["prepare_input", "generate_sql", "review_sql", "route_decision", "finalize_sql"]),
        (rubric_cli, "RubricReviewer", RubricReviewer, "LangGraphRubricSelfReflection",
         ["prepare_input", "extract_requirements", "generate_sql", "review_sql",
          "route_decision", "refine_sql", "finalize_sql"]),
    ],
)
def test_reflection_infer_score_visualize(
    monkeypatch, selected_fixture, cli, reviewer_attr, reviewer_cls,
    variant, expected_nodes,
):
    root, folder, dataset, selected = selected_fixture
    monkeypatch.setattr(cli.base_cli, "_selection", selected)
    monkeypatch.setattr(cli, "_configure_model",
                        lambda args: ("stub-model", object(), object()))
    monkeypatch.setattr(cli, reviewer_attr, reviewer_cls)
    from scr.baselines import bird_b0 as b0
    monkeypatch.setattr(b0, "make_agent", lambda *args, **kwargs: object())

    def fake_run_one(question, agent, *, log, trace_events):
        sql = "SELECT COUNT(*) FROM sample;"
        trace_events.append({"kind": "tool_result",
                             "name": "execute_sql",
                             "output": json.dumps({"rows": [[2]]})})
        return {"graph_completed": True, "final_sql": sql,
                "stop_reason": "final_sql_ready",
                "model_calls": 1, "tool_calls": 1,
                "sql_calls": 1, "usage_observed": True,
                "input_tokens": 3, "output_tokens": 4,
                "seconds": 0.05}
    monkeypatch.setattr(b0, "run_one", fake_run_one)
    args = cli.parser().parse_args([
        "infer", "--selection-id", "smoke", "--split", "dev",
        "--run-id", "run", "--result-root", str(root),
    ])
    assert cli.infer(args) == 0
    run = root / "smoke" / variant / "dev" / "run"
    manifest = json.loads((run / "inference_manifest.json").read_text())
    assert manifest["agent_variant"] == variant
    assert manifest["outer_graph_version"]
    assert manifest["completed"] is True
    pred = json.loads((run / "predictions.jsonl").read_text().strip())
    assert pred["predicted_sql"] == "SELECT COUNT(*) FROM sample;"
    trace = json.loads((run / "traces.jsonl").read_text().strip())
    assert [event["node"] for event in trace["graph_events"]] == expected_nodes
    from scr.tracing.graph import build_graph
    node_chart = build_graph(trace)
    assert [node["kind"] for node in node_chart["nodes"]] == (
        ["input"] + ["stage"] * (len(expected_nodes) - 1) + ["final"]
    )
    args = cli.parser().parse_args([
        "visualize", "--selection-id", "smoke", "--split", "dev",
        "--run-id", "run", "--result-root", str(root),
    ])
    assert cli.visualize(args) == 0
    assert (run / "trace-explorer.html").is_file()
    import scr.cli.evaluate_bird as evaluator
    calls = []
    def fake_score(options):
        calls.append(options)
        output = Path(options[options.index("--output-dir") + 1]) / "scores"
        output.mkdir()
        (output / "summary.json").write_text(
            json.dumps({"total": 1, "correct": 1, "ex": 1.0}))
        return 0
    monkeypatch.setattr(evaluator, "run", fake_score)
    args = cli.parser().parse_args([
        "score", "--selection-id", "smoke", "--split", "dev",
        "--run-id", "run", "--result-root", str(root),
    ])
    assert cli.score(args) == 0
    assert calls
    assert calls[0][calls[0].index("--variant") + 1] == variant


def _fake_metadata_result(question, *, trace_events=None):
    if trace_events is not None:
        trace_events.append({"kind": "model", "content": "SQL ready",
                             "model_call": 1})
    return {"graph_completed": True, "final_sql": "SELECT COUNT(*) FROM sample;",
            "stop_reason": "final_sql_ready", "seconds": 0.05,
            "model_calls": 1, "tool_calls": 1, "sql_calls": 1,
            "usage_observed": True, "input_tokens": 5, "output_tokens": 7}


@pytest.mark.parametrize("cli,variant", [
    (metadata_cli, "LangGraphMetadata"),
    (discovery_cli, "LangGraphMetadataDiscoveryV2"),
])
def test_metadata_dev_and_test_preserve_experiment_store_and_outputs(
    monkeypatch, selected_fixture, cli, variant,
):
    root, folder, dataset, selected = selected_fixture
    monkeypatch.setattr(cli.base_cli, "_selection", selected)
    monkeypatch.setattr(cli, "_configure_model", lambda args: ("stub-model", object()))
    captured = []

    if cli is metadata_cli:
        # Real MetadataEngine, graph wrapper, original run_one protocol.
        from langgraph_agents.metadata_v1 import agent as wrapper
        monkeypatch.setattr(wrapper, "make_agent",
                            lambda store, notes, **kwargs: notes)

        def original_run_one(question, notes, *, log, trace_events):
            captured.append((question["question_id"], notes.experiment_root,
                             notes.definition_mode))
            return _fake_metadata_result(question, trace_events=trace_events)

        monkeypatch.setattr(legacy_metadata, "run_one", original_run_one)
    else:
        import langgraph_agents.metadata_discovery_v2.workflow as wrapper

        def build_workflow(store, notes, model, model_name, prompt_variant):
            captured.append((notes.question_id, notes.experiment_root,
                             notes.definition_mode))

            class SyntheticWorkflow:
                def run_one(self, question, log, trace_events):
                    result = _fake_metadata_result(question, trace_events=trace_events)
                    result["workflow"] = "metadata-discovery-v2"
                    trace_events.extend([
                        {"kind": "knowledge_decision", "node": "a1"},
                        {"kind": "sufficiency_decision", "node": "b1"},
                        {"kind": "budget_consumed", "node": "c1"},
                    ])
                    return result

            return SyntheticWorkflow()

        monkeypatch.setattr(wrapper, "build_workflow", build_workflow)

    for split, qid in (("dev", 1), ("test", 2)):
        args = cli.parser().parse_args([
            "infer", "--selection-id", "smoke", "--split", split,
            "--run-id", "run-" + split, "--experiment-id", "shared",
            "--result-root", str(root),
        ])
        assert cli.infer(args) == 0
        run = root / "smoke" / variant / split / ("run-" + split)
        manifest = json.loads((run / "inference_manifest.json").read_text())
        assert manifest["completed"] and manifest["agent_variant"] == variant
        assert manifest["outer_graph_version"]
        prediction = json.loads((run / "predictions.jsonl").read_text().strip())
        assert prediction["predicted_sql"] == "SELECT COUNT(*) FROM sample;"
        trace = json.loads((run / "traces.jsonl").read_text().strip())
        from scr.tracing.graph import build_graph
        chart = build_graph(trace)
        if cli is metadata_cli:
            assert [n["detail"]["node"] for n in chart["nodes"]
                    if n["kind"] == "stage"] == [
                        "prepare_input", "run_metadata_v1", "collect_output"
                    ]
        else:
            assert [n["detail"]["node"] for n in chart["nodes"]
                    if n["kind"] == "stage"] == ["a1", "b1", "c1"]
    assert captured[0][0] == 1 and captured[1][0] == 2
    assert captured[0][1] == captured[1][1]
    assert captured[0][2] == captured[1][2] == (cli is discovery_cli)
    experiment = root / "smoke" / variant / "experiments" / "shared"
    info = json.loads((experiment / "experiment_manifest.json").read_text())
    assert info["dev_completed"] and info["test_completed"]
