"""Real outer LangGraph wrapper for the original Metadata V1 Deep Agent.

The existing metadata tools, prompt, note engine, and b0.run_one stay unchanged.
Only graph node boundaries and trace events are added.
"""
from __future__ import annotations

from time import perf_counter
from typing import Any, TypedDict

from langgraph.graph import START, END, StateGraph

from langgraph_agents.baseline.nodes import prepare_input as validate_input
from scr.agents import metadata_agent as legacy

make_agent = legacy.make_agent
system_prompt_for_variant = legacy.system_prompt_for_variant


class MetadataV1State(TypedDict, total=False):
    question: dict[str, Any]
    result: dict[str, Any]
    node_trace: list[dict[str, Any]]


def build_graph(agent, *, log=print):
    def prepare_input(state):
        validate_input({"agent_input": state["question"]})
        return {"node_trace": [{"node": "prepare_input"}]}

    def run_metadata(state):
        inner = []
        report = legacy.run_one(state["question"], agent, log=log, trace_events=inner)
        return {"result": {"report": report, "events": inner},
                "node_trace": [*state["node_trace"], {"node": "run_metadata_v1"}]}

    def finalize(state):
        return {"node_trace": [*state["node_trace"], {"node": "collect_output"}]}

    graph = StateGraph(MetadataV1State)
    graph.add_node("prepare_input", prepare_input)
    graph.add_node("run_metadata_v1", run_metadata)
    graph.add_node("collect_output", finalize)
    graph.add_edge(START, "prepare_input")
    graph.add_edge("prepare_input", "run_metadata_v1")
    graph.add_edge("run_metadata_v1", "collect_output")
    graph.add_edge("collect_output", END)
    return graph.compile()


def run_one(question, agent, log=print, trace_events=None):
    """Keep exact Metadata V1 call signature and return its original B0 report."""
    graph = build_graph(agent, log=log)
    started = perf_counter()
    state = graph.invoke({"question": question})
    if trace_events is not None:
        trace_events.extend(state["result"]["events"])
        for step, event in enumerate(state["node_trace"], 1):
            trace_events.append({
                "kind": "graph_node_complete", "node": event["node"],
                "seq": len(trace_events) + 1, "graph_step": step,
                "graph_elapsed_ms": round((perf_counter() - started) * 1000, 3),
            })
    return state["result"]["report"]
