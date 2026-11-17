"""Stream node boundaries for an individual role-specialized inference."""
from __future__ import annotations

from time import perf_counter


def run_question(graph, question: dict) -> tuple[dict, list[dict]]:
    updated: dict = {}
    events: list[dict] = []
    started = perf_counter()
    # The review/generation loop is explicitly represented as graph transitions.
    for transition in graph.stream(
        {"question": question, "started_at": started},
        config={"recursion_limit": 50},
        stream_mode="updates",
    ):
        for node, values in transition.items():
            if not isinstance(values, dict):
                continue
            updated.update(values)
            events.append({
                "seq": len(events) + 1, "kind": "graph_node_complete",
                "node": node,
                "observed_at_ms": round((perf_counter() - started) * 1000, 3),
            })
    if "report" not in updated:
        raise RuntimeError("LangGraph ended without finalization report")
    return updated, events
