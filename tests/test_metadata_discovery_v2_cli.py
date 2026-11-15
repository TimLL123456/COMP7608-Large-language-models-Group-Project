"""CLI regression: metadata-discovery-v2 has isolated paths but shares the original scorer."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from scr.cli import run_bird_b0_eval as base_cli
from scr.cli import run_bird_metadata_eval as metadata_cli
from tests.test_metadata_agent import MetadataRunnerTests


class _FakeWorkflow:
    def run_one(self, question, log, trace_events):
        trace_events.append({"node": "a1", "kind": "knowledge_decision",
                             "action": "no_note", "attempt": 1})
        return {
            "final_sql": "SELECT COUNT(*) FROM sales",
            "graph_completed": True, "model_calls": 3, "tool_calls": 1,
            "sql_calls": 1, "usage_observed": False, "seconds": 0.01,
            "a1_attempts": 1, "b1_evaluations": 1,
            "knowledge_decisions": ["no_note"],
            "stop_reason": "final_sql_ready",
        }


class MetadataDiscoveryV2CliTests(unittest.TestCase):
    def setUp(self):
        fixture = MetadataRunnerTests(methodName="test_test_before_dev_fails_safely")
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.fixture = fixture

    def run_dev(self):
        def fake_builder(store, metadata, model, model_name, prompt_variant):
            self.assertTrue(metadata.definition_mode)
            self.assertEqual(model_name, "fake")
            return _FakeWorkflow()

        with patch.object(base_cli, "BirdDataset", return_value=self.fixture.dataset), \
             patch.object(metadata_cli, "_configure_model",
                          return_value=("fake", object())), \
             patch("scr.agents.metadata_discovery_v2.build_workflow",
                   side_effect=fake_builder):
            return metadata_cli.main(
                self.fixture.args("dev", "graph001") +
                ["--workflow", "metadata-discovery-v2"])

    def test_graph_paths_counters_and_old_v1_isolation(self):
        self.assertEqual(self.run_dev(), 0)
        dest = self.fixture.folder / "MetadataDiscoveryV2" / "dev" / "graph001"
        self.assertTrue((dest / "predictions.jsonl").is_file())
        self.assertFalse((self.fixture.folder / "Metadata").exists())
        manifest = json.loads((dest / "inference_manifest.json").read_text())
        prediction = json.loads((dest / "predictions.jsonl").read_text().splitlines()[0])
        trace = json.loads((dest / "traces.jsonl").read_text().splitlines()[0])
        self.assertEqual(manifest["agent_variant"], "MetadataDiscoveryV2")
        self.assertEqual(manifest["workflow"], "metadata-discovery-v2")
        self.assertEqual(manifest["max_model_calls"], 120)
        self.assertEqual(manifest["max_total_tool_calls"], 200)
        self.assertEqual(manifest["max_sql_executions"], 80)
        self.assertEqual(manifest["max_a1_tool_calls_per_attempt"], 40)
        self.assertEqual(manifest["c1_reserved_tool_calls"], 40)
        self.assertEqual(manifest["metadata_context_chars_per_question"], 20000)
        self.assertEqual(prediction["a1_attempts"], 1)
        self.assertEqual(prediction["b1_evaluations"], 1)
        self.assertEqual(trace["report"]["model"], "fake")
        self.assertEqual(trace["structured_events"][0]["node"], "a1")

    def test_graph_scoring_uses_same_evaluator(self):
        self.run_dev()
        folder = self.fixture.folder / "MetadataDiscoveryV2" / "dev" / "graph001"
        score_dir = folder / "scores"
        calls = []

        def fake_score(arguments):
            calls.append(arguments)
            score_dir.mkdir()
            (score_dir / "summary.json").write_text(
                json.dumps({"correct": 2, "total": 2, "ex": 1.0}))
            return 0

        with patch.object(base_cli, "BirdDataset", return_value=self.fixture.dataset), \
             patch("scr.cli.evaluate_bird.run", side_effect=fake_score):
            args = ["score", *self.fixture.common, "--split", "dev",
                    "--run-id", "graph001", "--workflow", "metadata-discovery-v2"]
            self.assertEqual(metadata_cli.main(args), 0)
        self.assertEqual(calls[0][calls[0].index("--variant") + 1],
                         "MetadataDiscoveryV2")
        self.assertTrue((score_dir / "report.md").is_file())


if __name__ == "__main__":
    unittest.main()
