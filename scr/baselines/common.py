"""Shared, inspectable Deep Agents runtime for local and API chat models."""

import os
import time


# These are the deliberately supported hosted NVIDIA NIM model IDs.
NVIDIA_MODELS = (
    "deepseek-ai/deepseek-v4.1-flash",
    "z-ai/glm-5.3-flash",
    "nvidia/nemotron-3-ultra-550b-a55b",
    "nvidia/nemotron-3.5-super-vl-120b-a12b",
)

DEFAULT_MODELS = {
    "ollama": "qwen3:1.7b",
    "gemini": "gemini-2.5-flash",
    "deepseek": "deepseek-chat",
    "nvidia": NVIDIA_MODELS[0],
}


def build_model(
    model_name=None, num_ctx=8192, *, provider="ollama",
    temperature=0, max_tokens=512, timeout=60, top_p=None,
):
    """Build a selected chat model; keep older build_model(name, ctx) calls working.

    The provider must be selected explicitly. API credentials are read from the
    environment, never persisted or logged. Ollama remains the default.
    """
    if not isinstance(provider, str) or provider.lower().strip() not in DEFAULT_MODELS:
        raise ValueError(f"Unsupported model provider: {provider!r}. Choose ollama, gemini, deepseek, or nvidia.")
    provider = provider.lower().strip()
    if model_name is None:
        model_name = DEFAULT_MODELS[provider]
    if not isinstance(model_name, str) or not model_name.strip():
        raise ValueError("model_name must be a non-empty string")
    if not isinstance(num_ctx, int) or num_ctx < 1:
        raise ValueError("num_ctx must be a positive integer")
    if not isinstance(max_tokens, int) or max_tokens < 1:
        raise ValueError("max_tokens must be a positive integer")
    if not isinstance(temperature, (float, int)) or not 0 <= temperature <= 2:
        raise ValueError("temperature must be between 0 and 2")
    if not isinstance(timeout, (float, int)) or timeout <= 0:
        raise ValueError("timeout must be positive")
    if top_p is not None and (not isinstance(top_p, (int, float)) or not 0 < top_p <= 1):
        raise ValueError("top_p must be in (0, 1]")

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=model_name, base_url="http://localhost:11434",
            temperature=temperature, num_ctx=num_ctx, num_predict=max_tokens,
            reasoning=False, validate_model_on_init=True,
        )

    if provider == "gemini":
        if not (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")):
            raise ValueError("Gemini requires GOOGLE_API_KEY or GEMINI_API_KEY in the environment")
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=model_name, temperature=temperature, max_tokens=max_tokens,
            timeout=timeout, max_retries=0, vertexai=False,
        )

    if provider == "nvidia":
        # Hosted context capacity is fixed by NVIDIA's endpoint. Do not pass
        # Ollama-specific num_ctx (or an unverified context-window parameter).
        if model_name not in NVIDIA_MODELS:
            raise ValueError(
                f"Unsupported NVIDIA model: {model_name!r}. Choose one of: {', '.join(NVIDIA_MODELS)}"
            )
        if not os.environ.get("NVIDIA_API_KEY"):
            raise ValueError("NVIDIA requires NVIDIA_API_KEY in the environment")
        from langchain_nvidia_ai_endpoints import ChatNVIDIA

        return ChatNVIDIA(
            model=model_name,
            base_url="https://integrate.api.nvidia.com/v1",
            temperature=temperature,
            max_completion_tokens=max_tokens,
            timeout=timeout,
            **({"top_p": top_p} if top_p is not None else {}),
        )

    if not os.environ.get("DEEPSEEK_API_KEY"):
        raise ValueError("DeepSeek requires DEEPSEEK_API_KEY in the environment")
    if model_name == "deepseek-reasoner":
        raise ValueError("deepseek-reasoner lacks tool calling for this agent; choose deepseek-chat")
    from langchain_deepseek import ChatDeepSeek

    return ChatDeepSeek(
        model=model_name, temperature=temperature, max_tokens=max_tokens,
        timeout=timeout, max_retries=0,
    )


def redact_credentials(message: str) -> str:
    """Remove configured API keys from provider errors before persisting traces."""
    for key in ("NVIDIA_API_KEY", "DEEPSEEK_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY"):
        value = os.environ.get(key)
        if value:
            message = message.replace(value, "[REDACTED]")
    return message


def invoke_with_trace(agent, question, recursion_limit=24):
    """Report observed top-level actions, not assumed subagent activity."""
    from langchain_core.messages import AIMessage, ToolMessage

    started = time.perf_counter()
    state, error, error_type = None, None, None
    snapshots = 0
    inputs = {"messages": [{"role": "user", "content": question}]}
    config = {"recursion_limit": recursion_limit}
    try:
        if hasattr(agent, "stream"):
            # Keep each completed graph state: invoke() would discard the whole
            # trace if GraphRecursionError or a provider timeout is raised.
            for snapshot in agent.stream(inputs, config=config, stream_mode="values"):
                if isinstance(snapshot, dict) and "messages" in snapshot:
                    state = snapshot
                    snapshots += 1
        else:
            # Preserve compatibility with simple invoke-only test agents.
            state = agent.invoke(inputs, config=config)
    except Exception as exc:
        error_type = type(exc).__name__
        error = redact_credentials(f"{error_type}: {exc}")

    calls, results = [], []
    tokens_in = tokens_out = 0
    usage_seen = False
    messages = state.get("messages", []) if isinstance(state, dict) else []
    for message in messages:
        if isinstance(message, AIMessage):
            for call in message.tool_calls:
                calls.append({"name": call["name"], "args": call.get("args", {})})
            usage = message.usage_metadata or {}
            if usage:
                usage_seen = True
                tokens_in += usage.get("input_tokens", 0)
                tokens_out += usage.get("output_tokens", 0)
        elif isinstance(message, ToolMessage):
            results.append({
                "name": message.name,
                "status": str(message.status),
                "preview": str(message.content)[:1200],
            })

    # A failed graph has no verified final answer, even with a partial trace.
    last = (messages[-1].content if messages and isinstance(messages[-1], AIMessage)
            and error is None else "")
    answer = last if isinstance(last, str) else str(last)
    return {
        "question": question,
        "answer": answer,
        "seconds": round(time.perf_counter() - started, 3),
        "tool_calls": calls,
        "tool_results": results,
        "tokens": {"input": tokens_in, "output": tokens_out} if usage_seen else None,
        "error": error,
        "error_type": error_type,
        "stop_reason": error_type or ("completed" if answer else "no_final_answer"),
        "stream_snapshots": snapshots,
        "trace_complete": error is None,
        "partial_state_observed": bool(messages),
    }
