"""Offline CLI checks for the two-terminal 500-question experiment."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from scr.agents.role_specialized import cli


class RoleShardCliTests(unittest.TestCase):
    def test_defaults_target_siwc_luna_generator_terra_reviewer(self):
        args = cli.parser().parse_args([
            "infer", "--selection-id", "selection", "--split", "all",
            "--run-id", "luna-terra", "--shard-index", "1", "--shard-count", "2",
        ])
        self.assertEqual(args.generator_provider, "chatgpt-siwc")
        self.assertEqual(args.reviewer_provider, "chatgpt-siwc")
        self.assertIsNone(args.generator_model)
        self.assertIsNone(args.reviewer_model)
        self.assertEqual((args.shard_index, args.shard_count), (1, 2))

    def test_all_selection_is_dev_then_test_without_question_id_sort(self):
        args = SimpleNamespace(split="all", selection_id="selection", run_id="run")
        expected = {
            "dev": [{"question_id": 55}, {"question_id": 7}],
            "test": [{"question_id": 13}],
        }
        def selected(inner):
            return "folder", SimpleNamespace(manifest={"release": "2026"}), expected[inner.split]
        with patch.object(cli.base_cli, "_selection", side_effect=selected) as mock:
            folder, _, rows = cli._selected(args)
        self.assertEqual(folder, "folder")
        self.assertEqual([r["question_id"] for r in rows], [55, 7, 13])
        self.assertEqual(mock.call_count, 2)

    def test_non_all_sharding_is_rejected_before_inference(self):
        with self.assertRaisesRegex(ValueError, "--split all"):
            cli.main([
                "infer", "--selection-id", "selection", "--split", "dev",
                "--run-id", "run", "--shard-index", "2", "--shard-count", "2",
            ])

    def test_merge_requires_shard_count(self):
        with self.assertRaises(SystemExit):
            cli.parser().parse_args([
                "merge", "--selection-id", "selection",
                "--split", "all", "--run-id", "run",
            ])


if __name__ == "__main__":
    unittest.main()
