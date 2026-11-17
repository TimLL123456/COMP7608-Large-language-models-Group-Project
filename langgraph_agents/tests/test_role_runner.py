"""Artifact-level CLI regression without providers, credentials, or BIRD gold."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from langgraph_agents.role_specialized import cli
from scr.evaluation.bird import VARIANTS
from scr.tracing.graph import build_graph


def test_role_infer_manifest_score_and_visualize(tmp_path, monkeypatch):
    folder = tmp_path / "selection"
    folder.mkdir()
    (folder / "selection_manifest.json").write_text('{"frozen":true}\n')
    selection = [{"question_id": 101, "db_id": "sample",
                  "question": "Count sample rows", "evidence": ""}]
    import sqlite3
    with sqlite3.connect(tmp_path / "sample.sqlite") as conn:
        conn.execute("CREATE TABLE sample (value INTEGER)")
        conn.execute("INSERT INTO sample VALUES (1)")
    dataset = SimpleNamespace(
        manifest={"release": "synthetic"},
        get_database_path=lambda db_id: tmp_path / "sample.sqlite",
    )
    monkeypatch.setattr(cli, "_selected", lambda args: (folder, dataset, selection))
    monkeypatch.setattr(cli.base_cli, "_selection", lambda args: (
        folder, dataset, selection
    ))
    monkeypatch.setattr(cli, "_role_model", lambda provider, model, effort: (
        model or "configured-model", object(),
    ))
    monkeypatch.setattr(cli, "RubricReviewer", lambda *args, **kwargs: object())
    monkeypatch.setattr(cli, "_revision", lambda: "offline-test")

    class OfflineAgent:
        def __init__(self, reviewer, **kwargs):
            pass

        def run(self, question, store):
            sql = "SELECT COUNT(*) FROM sample;"
            report = {
                "question_id": 101, "db_id": "sample", "final_sql": sql,
                "graph_completed": True, "review_status": "PASS",
                "output_status": "verified", "stop_reason": "reviewer_pass",
                "attempt_count": 1, "review_report_count": 1,
                "seconds": 0.1, "model_calls": 3, "tool_calls": 2, "sql_calls": 2,
            }
            review = {"attempt": 1, "review_status": "PASS",
                      "criteria_findings": [], "overall_decision": "PASS"}
            return {
                "report": report, "final_sql": sql, "stop_reason": "reviewer_pass",
                "review_status": "PASS", "extraction": {"status": "PASS"},
                "attempts": [{"attempt": 1, "candidate_sql": sql,
                              "b0_report": report, "b0_events": [],
                              "review": {"status": "PASS"}, "review_report": review}],
                "review_reports": [review], "generator_usage": {"model_calls": 2},
                "reviewer_usage": {"model_calls": 1}, "structured_events": [],
                "graph_events": [
                    {"node": name, "kind": "graph_node_complete", "seq": idx}
                    for idx, name in enumerate((
                        "prepare_input", "generate_sql", "review_sql",
                        "route_decision", "finalize_sql",
                    ), 1)
                ],
            }

    monkeypatch.setattr(cli, "RoleSpecializedSelfReflectionAgent", OfflineAgent)
    args = cli.parser().parse_args([
        "infer", "--selection-id", "smoke", "--split", "dev",
        "--run-id", "synthetic", "--result-root", str(tmp_path / "results"),
    ])
    assert cli.infer(args) == 0
    run_dir = tmp_path / "results" / "smoke" / cli.VARIANT / "dev" / "synthetic"
    assert run_dir.is_dir()
    manifest = json.loads((run_dir / "inference_manifest.json").read_text())
    assert manifest["agent_variant"] == cli.VARIANT
    assert manifest["outer_graph_version"] == "role-specialized-v1"
    assert manifest["completed"] is True
    assert manifest["expected_questions"] == 1
    assert manifest["review_reports_sha256"]
    assert manifest["generator_reasoning_effort"] is None
    assert manifest["reviewer_reasoning_effort"] is None
    assert manifest["prompt_variant"] == "generalized-v1"
    row = json.loads((run_dir / "predictions.jsonl").read_text().strip())
    assert row["predicted_sql"] == "SELECT COUNT(*) FROM sample;"
    trace = json.loads((run_dir / "traces.jsonl").read_text().strip())
    chart = build_graph(trace)
    assert [node["kind"] for node in chart["nodes"]] == [
        "input", "stage", "stage", "stage", "stage", "final",
    ]
    assert [node["detail"].get("node") for node in chart["nodes"][1:5]] == [
        "prepare_input", "generate_sql", "review_sql", "route_decision",
    ]
    assert chart["nodes"][-1]["detail"]["final_sql"] == row["predicted_sql"]

    args = cli.parser().parse_args([
        "visualize", "--selection-id", "smoke", "--split", "dev",
        "--run-id", "synthetic", "--result-root", str(tmp_path / "results"),
    ])
    assert cli.visualize(args) == 0
    assert (run_dir / "trace-explorer.html").is_file()

    import scr.cli.evaluate_bird as scorer
    called = []
    monkeypatch.setattr(scorer, "run", lambda arguments: called.append(arguments) or 0)
    args = cli.parser().parse_args([
        "score", "--selection-id", "smoke", "--split", "dev",
        "--run-id", "synthetic", "--result-root", str(tmp_path / "results"),
    ])
    assert cli.score(args) == 0
    assert "--variant" in called[0]
    assert called[0][called[0].index("--variant") + 1] == cli.VARIANT
    assert cli.VARIANT in VARIANTS


def test_trace_viewer_ignores_inference_configuration(tmp_path):
    from scr.tracing.viewer import trace_sources
    for name in ("inference_config.json", "resume_history.jsonl",
                 "inference_manifest.json", "predictions.jsonl", "traces.jsonl"):
        (tmp_path / name).write_text("{}\n")
    assert [p.name for p in trace_sources(tmp_path)] == ["traces.jsonl"]
