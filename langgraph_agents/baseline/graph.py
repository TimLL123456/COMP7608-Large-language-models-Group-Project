"""Outer LangGraph orchestration around the original B0 Deep Agent."""
from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from langgraph_agents.common.state import BaselineState
from langgraph_agents.baseline.nodes import collect_output, make_run_b0_node, prepare_input

GRAPH_VERSION = "baseline-v1"


def build_graph(*, database_path, model: Any, model_name: str,
                prompt_variant: str = "baseline", preview_rows: int = 20,
                checkpointer=None):
    if prompt_variant not in ("baseline", "generalized-v1"):
        raise ValueError("Unsupported prompt variant")
    if not 1 <= preview_rows <= 200:
        raise ValueError("preview_rows must be 1..200")
    graph = StateGraph(BaselineState)
    graph.add_node("prepare_input", prepare_input)
    graph.add_node("run_b0", make_run_b0_node(
        database_path=database_path, model=model, model_name=model_name,
        prompt_variant=prompt_variant, preview_rows=preview_rows,
    ))
    graph.add_node("collect_output", collect_output)
    graph.add_edge(START, "prepare_input")
    graph.add_edge("prepare_input", "run_b0")
    graph.add_edge("run_b0", "collect_output")
    graph.add_edge("collect_output", END)
    return graph.compile(checkpointer=checkpointer)
