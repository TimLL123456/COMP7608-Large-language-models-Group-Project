"""Offline CLI checks for the two-terminal 500-question experiment."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
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


    def test_resume_requires_explicit_pair_of_flags(self):
        for extra in (["--start-position", "108"], ["--replace-existing"]):
            with self.assertRaisesRegex(ValueError, "--start-position"):
                cli.main([
                    "infer", "--selection-id", "selection", "--split", "all",
                    "--run-id", "run", *extra,
                ])

    def test_resume_position_is_shard_local(self):
        args = cli.parser().parse_args([
            "infer", "--selection-id", "selection", "--split", "all",
            "--run-id", "run", "--shard-index", "1", "--shard-count", "2",
            "--start-position", "108", "--replace-existing",
        ])
        self.assertEqual(args.start_position, 108)
        self.assertTrue(args.replace_existing)

    def test_provider_failure_not_checkpointed(self):
        self.assertTrue(cli._transient_provider_failure({
            "report": {}, "extraction": {}, "attempts": [{
                "b0_report": {},
                "review": {"stop_reason": "review_provider_error"},
            }],
        }))
        self.assertTrue(cli._transient_provider_failure({
            "report": {}, "extraction": {"error": "SIWC usage limit reached"},
        }))
        self.assertFalse(cli._transient_provider_failure({
            "report": {}, "extraction": {"status": "PASS"}, "attempts": [],
        }))

    def test_infer_in_place_replaces_existing_records(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "selection"
            folder.mkdir()
            (folder / "selection_manifest.json").write_text("{}")
            selected = [
                {"question_id": i, "db_id": "demo", "question": f"Question {i}"}
                for i in (4, 9, 12)
            ]
            dataset = SimpleNamespace(
                manifest={"release": "test"},
                get_database_path=lambda db_id: root / "dummy.sqlite",
            )
            args = cli.parser().parse_args([
                "infer", "--selection-id", "selection", "--split", "all",
                "--run-id", "same-run", "--result-root", str(root),
            ])
            version = ["original"]
            calls = []

            class FakeCoordinator:
                def __init__(self, *args, **kwargs):
                    pass

                def run(self, question, store):
                    calls.append(question["question_id"])
                    return {
                        "report": {
                            "seconds": 0.1, "output_status": "verified",
                            "review_status": "PASS", "stop_reason": "reviewer_pass",
                        },
                        "final_sql": f"SELECT '{version[0]}'",
                        "attempts": [], "extraction": {"status": "PASS"},
                        "structured_events": [], "review_reports": [],
                        "generator_usage": {}, "reviewer_usage": {},
                    }

            with patch.object(cli, "_selected", return_value=(folder, dataset, selected)), \
                 patch.object(cli, "_role_model", return_value=("test-model", object())), \
                 patch.object(cli, "RoleSpecializedSelfReflectionAgent", FakeCoordinator), \
                 patch.object(cli, "ReadOnlySqlite", return_value=object()), \
                 patch.object(cli, "_revision", return_value="test-revision"):
                cli.infer(args)
                run_dir = cli._run_dir(args)
                prediction = run_dir / "predictions.jsonl"
                before = prediction.read_bytes()
                version[0] = "replacement"
                args.start_position = 2
                args.replace_existing = True
                cli.infer(args)

            rows = [json.loads(line) for line in prediction.read_text().splitlines()]
            self.assertEqual(len(rows), 3)
            self.assertEqual(calls, [4, 9, 12, 9, 12])
            self.assertEqual(rows[0]["predicted_sql"], "SELECT 'original'")
            self.assertEqual(rows[1]["predicted_sql"], "SELECT 'replacement'")
            self.assertEqual(prediction.read_bytes().splitlines(keepends=True)[0],
                             before.splitlines(keepends=True)[0])
            self.assertEqual(len(list((run_dir / "resume_backups").iterdir())), 1)
            manifest = json.loads((run_dir / "inference_manifest.json").read_text())
            self.assertEqual(manifest["expected_questions"], 3)
            self.assertEqual(manifest["missing_final_sql"], 0)
            self.assertEqual(len(manifest["resume_history"]), 1)
            from scr.agents.role_specialized.sharding import sha
            self.assertEqual(manifest["prediction_sha256"], sha(prediction))


if __name__ == "__main__":
    unittest.main()
