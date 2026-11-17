"""Exercise the actual outer StateGraph with deterministic B0 stubs."""
import sqlite3

import pytest

from langgraph_agents.baseline import cli, graph, runner
from langgraph_agents.common.state import BaselineState


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "sample.sqlite"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE sample (id INTEGER PRIMARY KEY, value TEXT)")
        conn.execute("INSERT INTO sample VALUES (1, 'hello')")
    return path


def question():
    return {"question_id": 10, "db_id": "test", "question": "Count the rows", "evidence": ""}


def test_langgraph_nodes_and_b0_contract(monkeypatch, db):
    from scr.baselines import bird_b0 as b0
    calls = []

    def fake_agent(store, *, model, prompt_variant):
        calls.append(("factory", store.max_rows, model, prompt_variant))
        return object()

    def fake_run(question, agent, log, trace_events):
        calls.append(("run", question["question_id"]))
        log("tool test output")
        trace_events.append({"seq": 1, "kind": "model"})
        return {"graph_completed": True, "final_sql": "SELECT COUNT(*) FROM sample;",
                "model_calls": 2, "tool_calls": 1, "sql_calls": 1,
                "seconds": 0.123, "usage_observed": False,
                "stop_reason": "final_sql_ready"}

    monkeypatch.setattr(b0, "make_agent", fake_agent)
    monkeypatch.setattr(b0, "run_one", fake_run)
    compiled = graph.build_graph(database_path=lambda _: db, model="dummy", model_name="gpt-6-luna")
    output, transitions = runner.run_question(compiled, question(), run_id="a1", config_snapshot={})
    assert output["final_sql"] == "SELECT COUNT(*) FROM sample;"
    assert output["report"]["model_calls"] == 2
    assert output["report"]["model"] == "gpt-6-luna"
    assert output["events"] == ["tool test output"]
    assert output["structured_events"] == [{"seq": 1, "kind": "model"}]
    assert [e["node"] for e in transitions] == ["prepare_input", "run_b0", "collect_output"]
    assert calls == [("factory", 20, "dummy", "generalized-v1"), ("run", 10)]


def test_generalized_prompt_is_explicit(monkeypatch, db):
    from scr.baselines import bird_b0 as b0
    observed = []
    monkeypatch.setattr(b0, "make_agent", lambda store, *, model, prompt_variant:
                        observed.append(prompt_variant) or object())
    monkeypatch.setattr(b0, "run_one", lambda *args, **kwargs: {
        "graph_completed": True, "final_sql": "SELECT 1;", "stop_reason": "final_sql_ready",
        "model_calls": 1, "tool_calls": 0, "sql_calls": 0,
    })
    compiled = graph.build_graph(database_path=lambda _: db, model="dummy",
                                 model_name="gpt-6-luna", prompt_variant="generalized-v1")
    output, _ = runner.run_question(compiled, question(), run_id="a2", config_snapshot={})
    assert observed == ["generalized-v1"]
    assert output["final_sql"] == "SELECT 1;"


def test_graph_rejects_gold_sql(monkeypatch, db):
    from scr.baselines import bird_b0 as b0
    monkeypatch.setattr(b0, "make_agent", lambda *a, **k: pytest.fail("must not invoke model"))
    compiled = graph.build_graph(database_path=lambda _: db, model="dummy", model_name="gpt-6-luna")
    result, transitions = runner.run_question(
        compiled, {**question(), "SQL": "SELECT 42"}, run_id="invalid", config_snapshot={},
    )
    assert result["final_sql"] is None
    assert result["report"]["stop_reason"] == "ValueError"
    assert transitions[-1]["kind"] == "graph_error"


def test_incomplete_or_invalid_b0_never_forced(monkeypatch, db):
    from scr.baselines import bird_b0 as b0
    monkeypatch.setattr(b0, "make_agent", lambda *a, **k: object())
    monkeypatch.setattr(b0, "run_one", lambda *a, **k: {
        "graph_completed": False, "final_sql": "SELECT 1;",
        "stop_reason": "provider_timeout", "model_calls": 1, "tool_calls": 0,
    })
    compiled = graph.build_graph(database_path=lambda _: db, model="dummy", model_name="gpt-6-luna")
    output, _ = runner.run_question(compiled, question(), run_id="a3", config_snapshot={})
    assert output["final_sql"] is None
    assert output["status"] == "missing_final_sql"


def test_new_cli_defaults_and_old_b0_unchanged(monkeypatch):
    from scr.baselines import bird_b0 as b0
    from scr.cli import run_bird_b0_eval as old
    assert old.build_parser().parse_args(["infer", "--selection-id", "s", "--split", "dev",
                                          "--run-id", "r"]).provider == "nvidia"
    called = []
    monkeypatch.setattr(cli, "infer", lambda args: called.append(args) or 0)
    assert cli.main(["infer", "--selection-id", "s", "--split", "dev", "--run-id", "r"]) == 0
    assert called[0].provider == "chatgpt-siwc"
    assert called[0].model == "gpt-6-luna"
    assert called[0].reasoning_effort == "none"
    assert called[0].prompt_variant == "generalized-v1"
    assert b0.MAX_MODEL_CALLS == b0.MAX_TOTAL_TOOL_CALLS == b0.MAX_SQL_EXECUTIONS == 40


def test_nvidia_override_no_siwc_effort(monkeypatch):
    called = []
    monkeypatch.setattr(cli, "infer", lambda args: called.append(args) or 0)
    assert cli.main(["infer", "--selection-id", "s", "--split", "dev", "--run-id", "r",
                     "--provider", "nvidia"]) == 0
    assert called[0].provider == "nvidia" and called[0].reasoning_effort is None
    assert cli.main(["infer", "--selection-id", "s", "--split", "dev", "--run-id", "r",
                     "--provider", "nvidia", "--reasoning-effort", "none"]) == 0
    with pytest.raises(ValueError, match="requires --provider chatgpt-siwc"):
        runner._model_for_args(called[-1])



def test_optional_outer_checkpoint_retains_final_state(monkeypatch, db):
    from langgraph.checkpoint.memory import MemorySaver
    from scr.baselines import bird_b0 as b0

    monkeypatch.setattr(b0, "make_agent", lambda *a, **k: object())
    monkeypatch.setattr(b0, "run_one", lambda *a, **k: {
        "graph_completed": True, "final_sql": "SELECT 1;", "stop_reason": "final_sql_ready",
        "model_calls": 1, "tool_calls": 0, "sql_calls": 0,
    })
    compiled = graph.build_graph(database_path=lambda _: db, model="dummy",
                                 model_name="gpt-6-luna", checkpointer=MemorySaver())
    config = {"configurable": {"thread_id": "checkpoint-test"}}
    assert compiled.invoke({"agent_input": question()}, config=config)["final_sql"] == "SELECT 1;"
    assert compiled.get_state(config).values["final_sql"] == "SELECT 1;"


def test_path_traversal_rejected_before_b0(monkeypatch, db):
    from scr.baselines import bird_b0 as b0
    monkeypatch.setattr(b0, "make_agent", lambda *a, **k: pytest.fail("B0 called"))
    compiled = graph.build_graph(database_path=lambda _: db, model="dummy", model_name="x")
    for bad_db_id in ("../secret", r"secret\\other", ".."):
        output, _ = runner.run_question(
            compiled, {**question(), "db_id": bad_db_id}, run_id="path", config_snapshot={},
        )
        assert output["final_sql"] is None
        assert output["report"]["stop_reason"] == "ValueError"


def test_original_baseline_prompt_remains_opt_in(monkeypatch, db):
    from scr.baselines import bird_b0 as b0
    observed = []
    monkeypatch.setattr(b0, "make_agent", lambda store, *, model:
                        observed.append("original_baseline") or object())
    monkeypatch.setattr(b0, "run_one", lambda *args, **kwargs: {
        "graph_completed": True, "final_sql": "SELECT 1;", "stop_reason": "final_sql_ready",
        "model_calls": 1, "tool_calls": 0, "sql_calls": 0,
    })
    compiled = graph.build_graph(database_path=lambda _: db, model="dummy",
                                 model_name="gpt-6-luna", prompt_variant="baseline")
    output, _ = runner.run_question(compiled, question(), run_id="base", config_snapshot={})
    assert observed == ["original_baseline"]
    assert output["final_sql"] == "SELECT 1;"


def test_default_prompt_hash_matches_original_generalized_v1(monkeypatch):
    from hashlib import sha256
    from scr.baselines import bird_b0 as b0
    expected = "6a8a3662204ecdad26bf917691ec14662332bcf6ae7f4cd49e492b3409136f98"
    called = []
    monkeypatch.setattr(cli, "infer", lambda args: called.append(args) or 0)
    assert cli.main(["infer", "--selection-id", "s", "--split", "dev", "--run-id", "r"]) == 0
    variant = called[0].prompt_variant
    assert variant == "generalized-v1"
    assert sha256(b0.system_prompt_for_variant(variant).encode()).hexdigest() == expected
    assert sha256(b0.system_prompt_for_variant("baseline").encode()).hexdigest() != expected
