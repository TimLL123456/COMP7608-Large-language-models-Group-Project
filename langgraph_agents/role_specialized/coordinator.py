"""Drop-in Role Agent interface backed by five explicit LangGraph nodes."""
from __future__ import annotations

from scr.agents.role_specialized.coordinator import RoleSpecializedSelfReflectionAgent

from .graph import build_graph
from .runner import run_question


class LangGraphRoleSpecializedAgent(RoleSpecializedSelfReflectionAgent):
    def run(self, question: dict, store) -> dict:
        graph = build_graph(coordinator=self, store=store)
        state, graph_events = run_question(graph, question)
        return {
            "report": state["report"],
            "attempts": state["attempts"],
            "extraction": state["extraction"],
            "structured_events": state["structured_events"],
            "review_reports": state["review_reports"],
            "final_sql": state["final_sql"],
            "review_status": state["review_status"],
            "stop_reason": state["stop_reason"],
            "generator_usage": state["generator_usage"],
            "reviewer_usage": state["reviewer_usage"],
            "graph_events": graph_events,
        }
