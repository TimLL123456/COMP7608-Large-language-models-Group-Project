"""LangChain chat adapter for the single-account Sign in with ChatGPT preview.

Uses KORA's existing Deep Agents tool executor. Only function tools are exposed;
no hosted tools, remote browser login, or paid API-key fallback.
"""
from __future__ import annotations

import json
from typing import Any, Literal

import requests
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.utils.function_calling import convert_to_openai_tool

from scr.baselines import siwc_auth

NAMESPACE = "kora"


def _text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list) and all(
        isinstance(item, dict) and item.get("type") == "text"
        and isinstance(item.get("text"), str) for item in value
    ):
        return "\n".join(item["text"] for item in value)
    raise ValueError("ChatGPT SIWC adapter currently supports text messages only")


def _to_input(messages: list) -> tuple[str, list[dict]]:
    """Replay explicit history: stored model output followed by tool results."""
    instructions, items = [], []
    for message in messages:
        if isinstance(message, SystemMessage) or message.type == "developer":
            instructions.append(_text(message.content))
        elif isinstance(message, HumanMessage):
            items.append({"role": "user", "content": _text(message.content)})
        elif isinstance(message, ToolMessage):
            if not message.tool_call_id:
                raise ValueError("Tool result is missing a call ID")
            items.append({
                "type": "function_call_output",
                "call_id": message.tool_call_id,
                "output": _text(message.content),
            })
        elif isinstance(message, AIMessage):
            output = message.additional_kwargs.get("siwc_output")
            if output is not None:
                items.extend(output)
            else:
                if message.content:
                    items.append({"role": "assistant", "content": _text(message.content)})
                for call in message.tool_calls:
                    items.append({
                        "type": "function_call", "namespace": NAMESPACE,
                        "call_id": call["id"], "name": call["name"],
                        "arguments": json.dumps(call["args"]),
                    })
        else:
            raise ValueError(f"Unsupported SIWC message type: {type(message).__name__}")
    return "\n\n".join(instructions), items


def _parse_response(output: list[dict]) -> tuple[str, list[dict]]:
    chunks, calls = [], []
    for item in output:
        kind = item.get("type")
        if kind == "message":
            for part in item.get("content", []):
                if part.get("type") == "output_text":
                    chunks.append(part.get("text", ""))
        elif kind == "function_call":
            namespace = item.get("namespace", NAMESPACE)
            if namespace != NAMESPACE:
                raise ValueError(f"Unexpected SIWC tool namespace: {namespace}")
            name, call_id = item.get("name"), item.get("call_id")
            if not name or not call_id:
                raise ValueError("Malformed SIWC function call (name/call_id)")
            args = json.loads(item.get("arguments", "{}"))
            if not isinstance(args, dict):
                raise ValueError("SIWC tool arguments must be an object")
            calls.append({"name": name, "args": args, "id": call_id, "type": "tool_call"})
        elif kind == "reasoning":
            continue  # Preserve these items in additional_kwargs for stateless replay.
        else:
            raise ValueError(f"Unsupported SIWC response item: {kind}")
    return "".join(chunks), calls


def _stream_response(token: str, body: dict, timeout: float) -> tuple[list[dict], dict]:
    """Wait for response.completed; discard text from incomplete requests."""
    completed = None
    done_items = {}
    text_deltas = []
    with requests.post(
        siwc_auth.API + "/responses",
        headers={"Authorization": f"Bearer {token}"},
        json=body, timeout=(20, timeout), stream=True,
    ) as response:
        response.raise_for_status()
        response.encoding = "utf-8"
        for line in response.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue
            data = line[6:]
            if data == "[DONE]":
                break
            event = json.loads(data)
            kind = event.get("type")
            if kind == "response.output_text.delta":
                text_deltas.append(event.get("delta", ""))
            elif kind == "response.output_item.done":
                done_items[event["output_index"]] = event["item"]
            elif kind == "response.completed":
                completed = event.get("response") or {}
            elif kind in {"response.failed", "response.incomplete", "error"}:
                detail = (event.get("response") or {}).get("error") or event.get("error") or {}
                raise RuntimeError(f"SIWC stream failed: {kind} ({detail.get('code', 'unknown')})")
    if completed is None:
        raise RuntimeError("SIWC stream ended without response.completed")
    output = completed.get("output") or [done_items[i] for i in sorted(done_items)]
    if not output and text_deltas:
        output = [{"type": "message", "content": [
            {"type": "output_text", "text": "".join(text_deltas)}
        ]}]
    # Return the completed envelope so optional usage AND reported reasoning
    # settings can be extracted without keeping the full response in traces.
    return output, completed


class ChatGPTSIWC(BaseChatModel):
    """Responses API adapter for an explicitly authorized local ChatGPT account."""

    model: str
    timeout: float = 240
    reasoning_effort: Literal["none", "low", "medium", "high", "xhigh", "max"] | None = None

    @property
    def _llm_type(self) -> str:
        return "chatgpt-siwc"

    @property
    def _identifying_params(self) -> dict:
        return {"model": self.model, "auth": "chatgpt-siwc",
                "reasoning_effort": self.reasoning_effort}

    def bind_tools(self, tools, *, tool_choice=None, **kwargs):
        schemas = []
        for tool in tools:
            spec = convert_to_openai_tool(tool)
            if spec.get("type") != "function":
                raise ValueError("SIWC supports function tools only")
            fn = spec.get("function", spec)
            schemas.append({
                "type": "function", "name": fn["name"],
                "description": fn.get("description", ""),
                "parameters": fn.get("parameters", {"type": "object", "properties": {}}),
            })
        if tool_choice not in (None, "auto"):
            raise ValueError("SIWC only supports automatic tool choice in this adapter")
        return self.bind(tools=schemas, **kwargs)

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        if stop:
            raise ValueError("SIWC stop sequences are not supported")
        # No interactive OAuth during batch inference. Refresh remains automatic.
        saved = siwc_auth.read_json(siwc_auth.CREDS)
        if not saved:
            raise RuntimeError(
                "ChatGPT login required: uv run python -m scr.baselines.siwc_auth"
            )
        token = siwc_auth.access_token(saved)
        instructions, items = _to_input(messages)
        body = {"model": self.model, "input": items, "store": False, "stream": True}
        if self.reasoning_effort is not None:
            body["reasoning"] = {"effort": self.reasoning_effort}
        if instructions:
            body["instructions"] = instructions
        text_format = kwargs.get("text_format")
        if text_format is not None:
            if (not isinstance(text_format, dict)
                    or text_format.get("type") != "json_schema"
                    or not isinstance(text_format.get("schema"), dict)
                    or not text_format.get("strict")):
                raise ValueError("SIWC text_format requires a strict JSON schema")
            # This is opt-in; unchanged B0 requests never send a text format.
            body["text"] = {"format": text_format}
        tools = kwargs.get("tools") or []
        if tools:
            body["tools"] = [{
                "type": "namespace", "name": NAMESPACE,
                "description": "KORA local read-only database and agent tools",
                "tools": tools,
            }]
        output, completed = _stream_response(token, body, self.timeout)
        content, tool_calls = _parse_response(output)
        usage = completed.get("usage")
        usage = usage if isinstance(usage, dict) else {}
        input_details = usage.get("input_tokens_details")
        output_details = usage.get("output_tokens_details")
        input_details = input_details if isinstance(input_details, dict) else {}
        output_details = output_details if isinstance(output_details, dict) else {}

        def count(value):
            # Optional metrics must never reject a valid response or become
            # fake zeros when absent.
            return value if type(value) is int and value >= 0 else None

        cached = count(input_details.get("cached_tokens"))
        reasoning_tokens = count(output_details.get("reasoning_tokens"))
        input_tokens = count(usage.get("input_tokens"))
        output_tokens = count(usage.get("output_tokens"))
        total_tokens = count(usage.get("total_tokens"))

        usage_metadata = None
        if input_tokens is not None and output_tokens is not None:
            usage_metadata = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens if total_tokens is not None
                                else input_tokens + output_tokens,
            }
            if cached is not None:
                usage_metadata["input_token_details"] = {"cache_read": cached}
            if reasoning_tokens is not None:
                usage_metadata["output_token_details"] = {"reasoning": reasoning_tokens}

        # Whitelist scalar metadata; do not persist raw response bodies or
        # unpublished thinking/reasoning text in LangChain trace metadata.
        response_metadata = {"model_name": self.model, "finish_reason": "stop"}
        if cached is not None:
            response_metadata["cached_input_tokens"] = cached
        if reasoning_tokens is not None:
            response_metadata["reasoning_tokens"] = reasoning_tokens
        if total_tokens is not None:
            response_metadata["total_tokens"] = total_tokens

        reasoning = completed.get("reasoning")
        reasoning = reasoning if isinstance(reasoning, dict) else {}
        thinking = completed.get("thinking")
        thinking = thinking if isinstance(thinking, dict) else {}
        for key, candidate in (
            ("reasoning_effort", reasoning.get("effort") or completed.get("reasoning_effort")),
            ("reasoning_mode", reasoning.get("mode") or completed.get("reasoning_mode")),
            ("thinking_level", thinking.get("level") or completed.get("thinking_level")),
        ):
            if isinstance(candidate, str) and 0 < len(candidate) <= 64:
                response_metadata[key] = candidate

        answer = AIMessage(
            content=content, tool_calls=tool_calls,
            additional_kwargs={"siwc_output": output},
            usage_metadata=usage_metadata,
            response_metadata=response_metadata,
        )
        return ChatResult(generations=[ChatGeneration(message=answer)])


def list_available_models() -> list[dict]:
    """Read the authenticated account's advertised model slugs."""
    saved = siwc_auth.read_json(siwc_auth.CREDS)
    if not saved:
        raise RuntimeError("Sign in first: uv run python -m scr.baselines.siwc_auth")
    token = siwc_auth.access_token(saved)
    response = requests.get(
        siwc_auth.API + "/models",
        headers={"Authorization": f"Bearer {token}"}, timeout=30,
    )
    response.raise_for_status()
    return [
        {"slug": item["slug"], "name": item.get("display_name", item["slug"])}
        for item in response.json().get("models", [])
        if item.get("visibility") == "list" and item.get("slug")
    ]


if __name__ == "__main__":
    for item in list_available_models():
        print(f"{item['slug']} — {item['name']}")
