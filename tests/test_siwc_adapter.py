"""Offline, credential-free checks for ChatGPT SIWC LangChain tool conversion."""
import json
import unittest
from unittest.mock import patch

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from scr.baselines import chatgpt_siwc as siwc


class FakeResponse:
    def __init__(self, events):
        self.events = events
        self.encoding = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def raise_for_status(self):
        pass

    def iter_lines(self, decode_unicode=False):
        assert decode_unicode is True
        for event in self.events:
            yield "data: " + json.dumps(event)
        yield "data: [DONE]"


class SIWCTests(unittest.TestCase):
    def test_explicit_effort_is_sent_without_inventing_reported_effort(self):
        events = [{"type": "response.completed", "response": {"output": []}}]
        with patch.object(siwc.siwc_auth, "read_json", return_value={"x": 1}), \
             patch.object(siwc.siwc_auth, "access_token", return_value="fake"), \
             patch.object(siwc.requests, "post", return_value=FakeResponse(events)) as post:
            message = siwc.ChatGPTSIWC(model="demo", reasoning_effort="none")._generate(
                [HumanMessage(content="hello")]).generations[0].message
        self.assertEqual(post.call_args.kwargs["json"]["reasoning"], {"effort": "none"})
        self.assertNotIn("reasoning_effort", message.response_metadata)

    def test_reviewer_only_json_schema_format(self):
        response = [{"type": "response.completed", "response": {"output": [{
            "type": "message", "content": [{"type": "output_text", "text": "{}"}],
        }]}}]
        schema = {"type": "json_schema", "name": "reflection",
                  "strict": True, "schema": {"type": "object",
                  "properties": {}, "required": [], "additionalProperties": False}}
        reviewer = siwc.ChatGPTSIWC(model="demo").bind(text_format=schema)
        with patch.object(siwc.siwc_auth, "read_json", return_value={"x": 1}), \
             patch.object(siwc.siwc_auth, "access_token", return_value="fake"), \
             patch.object(siwc.requests, "post", return_value=FakeResponse(response)) as post:
            reviewer.invoke([HumanMessage(content="Review SQL")])
        self.assertEqual(post.call_args.kwargs["json"]["text"], {"format": schema})

        with patch.object(siwc.siwc_auth, "read_json", return_value={"x": 1}), \
             patch.object(siwc.siwc_auth, "access_token", return_value="fake"), \
             self.assertRaisesRegex(ValueError, "strict JSON schema"):
            siwc.ChatGPTSIWC(model="demo")._generate(
                [HumanMessage(content="Review SQL")],
                text_format={"type": "json_object"})

    def test_function_call_and_stateless_history(self):
        output = [{
            "type": "function_call", "namespace": "kora",
            "name": "list_tables", "call_id": "call_1", "arguments": "{}",
        }]
        events = [
            {"type": "response.output_item.done", "output_index": 0, "item": output[0]},
            {"type": "response.completed", "response": {
                "output": output, "usage": {"input_tokens": 17, "output_tokens": 8}
            }},
        ]
        model = siwc.ChatGPTSIWC(model="demo", timeout=15)
        with patch.object(siwc.siwc_auth, "read_json", return_value={"access_token": "fake"}), \
             patch.object(siwc.siwc_auth, "access_token", return_value="fake-token"), \
             patch.object(siwc.requests, "post", return_value=FakeResponse(events)) as post:
            result = model._generate([SystemMessage(content="You are a SQL agent"),
                                      HumanMessage(content="List tables")],
                                     tools=[{"name": "list_tables", "type": "function",
                                             "parameters": {"type": "object", "properties": {}}}])
        message = result.generations[0].message
        self.assertEqual(message.tool_calls[0]["name"], "list_tables")
        self.assertEqual(message.tool_calls[0]["id"], "call_1")
        self.assertEqual(message.usage_metadata["input_tokens"], 17)
        request = post.call_args.kwargs["json"]
        self.assertEqual(request["instructions"], "You are a SQL agent")
        self.assertEqual(request["tools"][0]["type"], "namespace")
        self.assertEqual(request["tools"][0]["tools"][0]["name"], "list_tables")
        self.assertEqual(request["input"], [{"role": "user", "content": "List tables"}])
        self.assertIs(request["store"], False)
        self.assertIs(request["stream"], True)
        self.assertNotIn("temperature", request)
        self.assertNotIn("max_output_tokens", request)
        self.assertNotIn("top_p", request)
        instructions, history = siwc._to_input([
            SystemMessage(content="You are a SQL agent"),
            HumanMessage(content="List tables"), message,
            ToolMessage(content='{"tables": ["items"]}',
                        name="list_tables", tool_call_id="call_1"),
        ])
        self.assertEqual(instructions, "You are a SQL agent")
        self.assertEqual(history[1], output[0])
        self.assertEqual(history[2]["type"], "function_call_output")
        self.assertEqual(history[2]["call_id"], "call_1")

    def test_usage_details_and_reported_reasoning_settings(self):
        """Save only response-reported fields, never synthesize an effort level."""
        output = [{"type": "message", "role": "assistant", "content": [
            {"type": "output_text", "text": "42"}
        ]}]
        completed = {"output": output, "usage": {
            "input_tokens": 120, "output_tokens": 80, "total_tokens": 200,
            "input_tokens_details": {"cached_tokens": 40},
            "output_tokens_details": {"reasoning_tokens": 55},
        }, "reasoning": {"effort": "high", "mode": "pro"},
           "thinking": {"level": "deep"}}
        events = [{"type": "response.completed", "response": completed}]
        with patch.object(siwc.siwc_auth, "read_json", return_value={"x": 1}), \
             patch.object(siwc.siwc_auth, "access_token", return_value="x"), \
             patch.object(siwc.requests, "post", return_value=FakeResponse(events)) as post:
            msg = siwc.ChatGPTSIWC(model="demo")._generate(
                [HumanMessage(content="42")]
            ).generations[0].message
        self.assertEqual(msg.usage_metadata["input_token_details"]["cache_read"], 40)
        self.assertEqual(msg.usage_metadata["output_token_details"]["reasoning"], 55)
        self.assertEqual(msg.usage_metadata["total_tokens"], 200)
        self.assertEqual(msg.response_metadata["cached_input_tokens"], 40)
        self.assertEqual(msg.response_metadata["reasoning_tokens"], 55)
        self.assertEqual(msg.response_metadata["reasoning_effort"], "high")
        self.assertEqual(msg.response_metadata["reasoning_mode"], "pro")
        self.assertEqual(msg.response_metadata["thinking_level"], "deep")
        request = post.call_args.kwargs["json"]
        self.assertNotIn("reasoning", request)
        self.assertNotIn("thinking", request)

    def test_missing_malformed_optional_usage_never_breaks_inference(self):
        events = [{"type": "response.completed", "response": {
            "output": [{"type": "message", "content": [
                {"type": "output_text", "text": "ok"}
            ]}],
            "usage": {"input_tokens": "invalid", "input_tokens_details": None,
                      "output_tokens_details": {"reasoning_tokens": "invalid"}},
            "reasoning": {"effort": None}, "thinking": "unavailable",
        }}]
        with patch.object(siwc.siwc_auth, "read_json", return_value={"x": 1}), \
             patch.object(siwc.siwc_auth, "access_token", return_value="x"), \
             patch.object(siwc.requests, "post", return_value=FakeResponse(events)):
            msg = siwc.ChatGPTSIWC(model="demo")._generate(
                [HumanMessage(content="hello")]
            ).generations[0].message
        self.assertEqual(msg.content, "ok")
        self.assertIsNone(msg.usage_metadata)
        self.assertNotIn("cached_input_tokens", msg.response_metadata)
        self.assertNotIn("reasoning_tokens", msg.response_metadata)
        self.assertNotIn("reasoning_effort", msg.response_metadata)

    def test_partial_usage_details_survive_without_base_counts(self):
        events = [{"type": "response.completed", "response": {
            "output": [{"type": "message", "content": [
                {"type": "output_text", "text": "ok"}
            ]}],
            "usage": {
                "input_tokens_details": {"cached_tokens": 18},
                "output_tokens_details": {"reasoning_tokens": 6},
            },
            "reasoning": {"effort": "medium"},
        }}]
        with patch.object(siwc.siwc_auth, "read_json", return_value={"x": 1}), \
             patch.object(siwc.siwc_auth, "access_token", return_value="x"), \
             patch.object(siwc.requests, "post", return_value=FakeResponse(events)):
            msg = siwc.ChatGPTSIWC(model="demo")._generate(
                [HumanMessage(content="hello")]
            ).generations[0].message
        self.assertIsNone(msg.usage_metadata)
        self.assertEqual(msg.response_metadata["cached_input_tokens"], 18)
        self.assertEqual(msg.response_metadata["reasoning_tokens"], 6)
        self.assertEqual(msg.response_metadata["reasoning_effort"], "medium")

    def test_final_text_and_replay(self):
        output = [{"type": "message", "role": "assistant", "content": [
            {"type": "output_text", "text": "Final SQL Query:\n\"\"\"\nSELECT 1;\n\"\"\""}
        ]}]
        events = [{"type": "response.completed", "response": {"output": output}}]
        model = siwc.ChatGPTSIWC(model="demo")
        with patch.object(siwc.siwc_auth, "read_json", return_value={"fake": True}), \
             patch.object(siwc.siwc_auth, "access_token", return_value="x"), \
             patch.object(siwc.requests, "post", return_value=FakeResponse(events)):
            message = model._generate([HumanMessage(content="SQL")]).generations[0].message
        self.assertIn("SELECT 1", message.content)
        self.assertEqual(siwc._to_input([message])[1], output)

    def test_incomplete_stream_never_becomes_an_answer(self):
        with patch.object(siwc.siwc_auth, "read_json", return_value={"fake": True}), \
             patch.object(siwc.siwc_auth, "access_token", return_value="x"), \
             patch.object(siwc.requests, "post", return_value=FakeResponse([
                 {"type": "response.output_text.delta", "delta": "partial"}
             ])):
            with self.assertRaisesRegex(RuntimeError, "response.completed"):
                siwc.ChatGPTSIWC(model="demo")._generate([HumanMessage(content="SQL")])

    def test_reject_wrong_namespace_and_unhandled_messages(self):
        with self.assertRaisesRegex(ValueError, "namespace"):
            siwc._parse_response([{"type": "function_call", "namespace": "other",
                                   "name": "list_tables", "call_id": "call_1",
                                   "arguments": "{}"}])
        with self.assertRaisesRegex(ValueError, "text messages only"):
            siwc._to_input([HumanMessage(content=[{"type": "image_url",
                                                    "image_url": "data:text/plain;base64,eA=="}])])

    def test_missing_credentials_are_explicit(self):
        with patch.object(siwc.siwc_auth, "read_json", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "login required"):
                siwc.ChatGPTSIWC(model="demo")._generate([HumanMessage(content="hello")])

    def test_bind_tools_delegates_to_langchain(self):
        model = siwc.ChatGPTSIWC(model="demo")
        tool = {
            "type": "function",
            "function": {"name": "list_tables", "description": "List tables",
                         "parameters": {"type": "object", "properties": {}}},
        }
        bound = model.bind_tools([tool])
        self.assertEqual(bound.kwargs["tools"][0]["name"], "list_tables")


if __name__ == "__main__":
    unittest.main()
