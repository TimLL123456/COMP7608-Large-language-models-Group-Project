"""Verify CLI output and compatibility with original frozen selections."""
import json
from argparse import Namespace
from pathlib import Path

import pytest

from langgraph_agents.baseline import cli, runner
from scr.baselines import bird_b0 as b0
from scr.evaluation.bird import VARIANTS


def test_manifest_and_predictions_are_isolated(monkeypatch, tmp_path):
    selection = tmp_path / "selection"
    selection.mkdir()
    (selection / "selection_manifest.json").write_text("frozen", encoding="utf-8")
    question = {"question_id": 1, "db_id": "demo", "question": "One row", "evidence": ""}
    dataset = type("Dataset", (), {"manifest": {"dataset": "fake"},
                                    "get_database_path": lambda self, db: tmp_path / "db.sqlite"})()
    monkeypatch.setattr(runner.original_cli, "_selection", lambda args:
                        (selection, dataset, [question]))
    monkeypatch.setattr(runner, "_model_for_args", lambda args: ("gpt-6-luna", object()))
    monkeypatch.setattr(runner, "build_graph", lambda **kwargs: object())
    monkeypatch.setattr(runner, "run_question", lambda *a, **kw: ({
        "final_sql": "SELECT 1;", "report": {
            "model": "gpt-6-luna", "graph_completed": True, "final_sql": "SELECT 1;",
            "model_calls": 1, "tool_calls": 0, "sql_calls": 0,
            "seconds": 0.1, "usage_observed": False,
        }, "events": [], "structured_events": [],
    }, [{"kind": "graph_node_complete", "node": "run_b0"}]))
    args = Namespace(selection_id="s", split="dev", run_id="r", provider="chatgpt-siwc",
                     model="gpt-6-luna", reasoning_effort="none", prompt_variant="baseline",
                     preview_rows=20, dataset_root=tmp_path, result_root=tmp_path)
    assert runner.infer(args) == 0
    path = selection / "LangGraphB0" / "dev" / "r"
    manifest = json.loads((path / "inference_manifest.json").read_text())
    row = json.loads((path / "predictions.jsonl").read_text())
    trace = json.loads((path / "traces.jsonl").read_text())
    assert row["predicted_sql"] == "SELECT 1;"
    assert manifest["provider"] == "chatgpt-siwc" and manifest["model"] == "gpt-6-luna"
    assert manifest["requested_reasoning_effort"] == "none"
    assert manifest["max_model_calls"] == b0.MAX_MODEL_CALLS == 40
    assert manifest["agent_variant"] == "LangGraphB0"
    assert trace["graph_events"][0]["node"] == "run_b0"
    assert not (selection / "B0").exists()
    with pytest.raises(ValueError, match="overwrite"):
        runner.infer(args)


def test_scorer_knows_new_variant():
    assert "LangGraphB0" in VARIANTS
