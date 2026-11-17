"""MetadataDiscoveryV2 already uses a compiled StateGraph (A1, B1, C1).

Expose it through the consolidated LangGraph package without replacing or
reimplementing the original graph: doing so would alter notes and budgets.
"""
from __future__ import annotations

from scr.agents.metadata_discovery_v2 import (
    MetadataDiscoveryV2Workflow,
    build_workflow as legacy_build_workflow,
)


def build_workflow(store, metadata, model, model_name, prompt_variant="generalized-v1"):
    return legacy_build_workflow(store, metadata, model, model_name,
                                 prompt_variant=prompt_variant)
