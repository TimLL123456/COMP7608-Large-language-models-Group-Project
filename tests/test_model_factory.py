"""Offline KORA-18 provider tests (no real credentials, model calls or downloads)."""

import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scr" / "baselines"))
from common import DEFAULT_MODELS, NVIDIA_MODELS, build_model, invoke_with_trace  # noqa: E402


class FakeModel:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class ModelFactoryTests(unittest.TestCase):
    def setUp(self):
        modules = {
            "langchain_ollama": types.SimpleNamespace(ChatOllama=FakeModel),
            "langchain_google_genai": types.SimpleNamespace(ChatGoogleGenerativeAI=FakeModel),
            "langchain_deepseek": types.SimpleNamespace(ChatDeepSeek=FakeModel),
            "langchain_nvidia_ai_endpoints": types.SimpleNamespace(ChatNVIDIA=FakeModel),
        }
        patcher = patch.dict(sys.modules, modules)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_legacy_default_ollama(self):
        with patch.dict(os.environ, {}, clear=True):
            model = build_model()
            self.assertEqual(model.kwargs, {
                "model": "qwen3:1.7b", "base_url": "http://localhost:11434",
                "temperature": 0, "num_ctx": 8192, "num_predict": 512,
                "reasoning": False, "validate_model_on_init": True,
            })
            self.assertEqual(build_model("other:1b", 4096).kwargs["num_ctx"], 4096)
            self.assertEqual(build_model(provider="OLLAMA").kwargs["model"], DEFAULT_MODELS["ollama"])

    def test_gemini_api_key_and_parameters(self):
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "dummy"}, clear=True):
            kwargs = build_model(provider="gemini", temperature=0.2, max_tokens=256, timeout=12).kwargs
            self.assertEqual(kwargs, {
                "model": "gemini-2.5-flash", "temperature": 0.2,
                "max_tokens": 256, "timeout": 12, "max_retries": 0, "vertexai": False,
            })
        with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy"}, clear=True):
            self.assertEqual(build_model(provider="gemini").kwargs["model"], "gemini-2.5-flash")

    def test_deepseek_key_and_parameters(self):
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "dummy"}, clear=True):
            kwargs = build_model(provider="deepseek", max_tokens=96, timeout=12).kwargs
            self.assertEqual(kwargs["model"], "deepseek-chat")
            self.assertEqual(kwargs["max_tokens"], 96)
            self.assertEqual(kwargs["timeout"], 12)
            self.assertEqual(kwargs["max_retries"], 0)
            with self.assertRaisesRegex(ValueError, "lacks tool calling"):
                build_model("deepseek-reasoner", provider="deepseek")

    def test_nvidia_default_and_supported_models(self):
        self.assertEqual(NVIDIA_MODELS, (
            "deepseek-ai/deepseek-v4.1-flash",
            "z-ai/glm-5.3-flash",
            "nvidia/nemotron-3-ultra-550b-a55b",
            "nvidia/nemotron-3.5-super-vl-120b-a12b",
        ))
        self.assertEqual(DEFAULT_MODELS["nvidia"], NVIDIA_MODELS[0])
        with patch.dict(os.environ, {"NVIDIA_API_KEY": "dummy"}, clear=True):
            for name in NVIDIA_MODELS:
                with self.subTest(name=name):
                    kwargs = build_model(
                        name, provider="nvidia", temperature=0.2,
                        max_tokens=256, timeout=12,
                    ).kwargs
                    self.assertEqual(kwargs, {
                        "model": name,
                        "base_url": "https://integrate.api.nvidia.com/v1",
                        "temperature": 0.2,
                        "max_completion_tokens": 256,
                        "timeout": 12,
                    })
            self.assertEqual(
                build_model(provider="NVIDIA").kwargs["model"], NVIDIA_MODELS[0],
            )

    def test_nemotron_vl_sampling_and_top_p_validation(self):
        with patch.dict(os.environ, {"NVIDIA_API_KEY": "dummy"}, clear=True):
            kwargs = build_model(
                "nvidia/nemotron-3.5-super-vl-120b-a12b",
                provider="nvidia", temperature=1.0, top_p=0.95,
                max_tokens=16_384, timeout=300,
            ).kwargs
        self.assertEqual(kwargs["top_p"], 0.95)
        self.assertEqual(kwargs["max_completion_tokens"], 16_384)
        self.assertEqual(kwargs["timeout"], 300)
        with self.assertRaisesRegex(ValueError, "top_p"):
            build_model(top_p=1.5)

    def test_b0_nvidia_request_and_token_budgets(self):
        # B0 uses the NVIDIA hosted context capacity as metadata, not num_ctx.
        from scr.baselines import bird_b0 as b0
        self.assertEqual(b0.MAX_CONTEXT_TOKENS, 262_144)
        self.assertEqual(b0.MAX_OUTPUT_TOKENS, 16_384)
        self.assertEqual(b0.REQUEST_TIMEOUT, 300)
        with patch.dict(os.environ, {"NVIDIA_API_KEY": "dummy"}, clear=True):
            kwargs = build_model(
                b0.MODEL, provider="nvidia", temperature=b0.TEMPERATURE,
                top_p=b0.TOP_P, max_tokens=b0.MAX_OUTPUT_TOKENS,
                timeout=b0.REQUEST_TIMEOUT,
            ).kwargs
        self.assertEqual(kwargs["timeout"], 300)
        self.assertEqual(kwargs["max_completion_tokens"], 16_384)
        self.assertNotIn("num_ctx", kwargs)
        self.assertNotIn("max_context_tokens", kwargs)

    def test_nvidia_missing_key_and_unsupported_model(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "NVIDIA_API_KEY"):
                build_model(provider="nvidia")
        with patch.dict(os.environ, {"NVIDIA_API_KEY": "a-sensitive-placeholder"}, clear=True):
            with self.assertRaisesRegex(ValueError, "Unsupported NVIDIA model") as error:
                build_model("other/model", provider="nvidia")
            self.assertNotIn("a-sensitive-placeholder", str(error.exception))

    def test_no_silent_cloud_fallback(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "GOOGLE_API_KEY"):
                build_model(provider="gemini")
            with self.assertRaisesRegex(ValueError, "DEEPSEEK_API_KEY"):
                build_model(provider="deepseek")
            with self.assertRaisesRegex(ValueError, "NVIDIA_API_KEY"):
                build_model(provider="nvidia")
            self.assertEqual(build_model().kwargs["model"], "qwen3:1.7b")

    def test_stream_trace_survives_recursion_exception(self):
        from langchain_core.messages import AIMessage, ToolMessage

        class InterruptedAgent:
            def stream(self, inputs, config, stream_mode):
                self.seen_config = config
                assert stream_mode == "values"
                yield {"messages": inputs["messages"]}
                yield {"messages": [
                    *inputs["messages"],
                    AIMessage(
                        content="",
                        tool_calls=[{
                            "name": "execute_sql",
                            "args": {"sql": "SELECT 42"},
                            "id": "call_1",
                            "type": "tool_call",
                        }],
                        usage_metadata={
                            "input_tokens": 25, "output_tokens": 4, "total_tokens": 29,
                        },
                    ),
                    ToolMessage(content='{"rows": [[42]]}', tool_call_id="call_1",
                                name="execute_sql"),
                ]}
                raise RuntimeError("recursion limit reached")

        agent = InterruptedAgent()
        record = invoke_with_trace(agent, "test", 12)
        self.assertEqual(agent.seen_config["recursion_limit"], 12)
        self.assertEqual(record["answer"], "")
        self.assertEqual(record["tool_calls"][0]["args"]["sql"], "SELECT 42")
        self.assertEqual(record["tool_results"][0]["name"], "execute_sql")
        self.assertEqual(record["tokens"]["input"], 25)
        self.assertIn("RuntimeError", record["error"])
        self.assertFalse(record["trace_complete"])
        self.assertTrue(record["partial_state_observed"])
        self.assertEqual(record["stop_reason"], "RuntimeError")
        self.assertEqual(record["stream_snapshots"], 2)

    def test_invoke_trace_compatibility_and_credentials_redaction(self):
        class InvokeOnlyAgent:
            def invoke(self, inputs, config):
                raise RuntimeError("danger: test-secret-123")

        with patch.dict(os.environ, {"NVIDIA_API_KEY": "test-secret-123"}, clear=True):
            record = invoke_with_trace(InvokeOnlyAgent(), "test")
        self.assertNotIn("test-secret-123", record["error"])
        self.assertIn("[REDACTED]", record["error"])
        self.assertFalse(record["partial_state_observed"])

    def test_input_validation(self):
        invalid = [
            ({"provider": "openai"}, "Unsupported model provider"),
            ({"provider": ""}, "Unsupported model provider"),
            ({"model_name": " "}, "model_name"),
            ({"num_ctx": 0}, "num_ctx"),
            ({"max_tokens": 0}, "max_tokens"),
            ({"temperature": 4}, "temperature"),
            ({"timeout": 0}, "timeout"),
        ]
        for kwargs, message in invalid:
            with self.subTest(kwargs=kwargs), self.assertRaisesRegex(ValueError, message):
                build_model(**kwargs)


if __name__ == "__main__":
    unittest.main()
