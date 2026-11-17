"""Five visible LangGraph nodes with bounded, evidence-driven retry edges."""
from __future__ import annotations

from langgraph.graph import START, END, StateGraph

from langgraph_agents.role_specialized.nodes import RoleNodes
from langgraph_agents.role_specialized.state import RoleState

GRAPH_VERSION = "role-specialized-v1"


def build_graph(*, coordinator, store, checkpointer=None):
    """Bind non-serializable dependencies to node closures, not graph state."""
    nodes = RoleNodes(coordinator, store)
    graph = StateGraph(RoleState)
    graph.add_node("prepare_input", nodes.prepare_input)
    graph.add_node("generate_sql", nodes.generate_sql)
    graph.add_node("review_sql", nodes.review_sql)
    graph.add_node("route_decision", nodes.route_decision)
    graph.add_node("finalize_sql", nodes.finalize_sql)
    graph.add_edge(START, "prepare_input")
    graph.add_edge("prepare_input", "generate_sql")
    graph.add_conditional_edges(
        "generate_sql", lambda s: s["next_action"],
        {"review": "review_sql", "finalize": "finalize_sql"},
    )
    graph.add_edge("review_sql", "route_decision")
    graph.add_conditional_edges(
        "route_decision", lambda s: s["next_action"],
        {"retry": "generate_sql", "finalize": "finalize_sql"},
    )
    graph.add_edge("finalize_sql", END)
    return graph.compile(checkpointer=checkpointer)
