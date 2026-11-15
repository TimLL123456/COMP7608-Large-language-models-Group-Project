"""Offline sharding/merge regression tests. No model calls or gold data."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scr.agents.role_specialized.sharding import (
    ARTIFACTS, merge_shards, sha, shard_dir, shard_slice,
)


class ShardingTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.folder = root / "selection"
        self.folder.mkdir()
        (self.folder / "selection_manifest.json").write_text('{"id":"demo"}\n')
        self.root = root / "result" / "all" / "run"
        self.root.mkdir(parents=True)
        self.split_dirs = {s: root / "result" / s / "run"
                           for s in ("dev", "test")}
        self.selections = {
            s: [{"question_id": n, "db_id": "demo"} for n in vals]
            for s, vals in {"dev": [100, 12, 44, 7], "test": [19, 62]}.items()
        }

    def populate(self, **changes):
        all_questions = self.selections["dev"] + self.selections["test"]
        for i in (1, 2):
            selected, info = shard_slice(all_questions, i, 2)
            path = shard_dir(self.root, i, 2)
            (path / "reviews").mkdir(parents=True)
            for filename in ARTIFACTS:
                with (path / filename).open("w", encoding="utf-8") as stream:
                    for question in selected:
                        row = {"question_id": question["question_id"]}
                        if filename == "predictions.jsonl":
                            row.update({
                                "db_id": question["db_id"],
                                "provider": "chatgpt-siwc", "model": "gpt-6-luna",
                                "reviewer_provider": "chatgpt-siwc",
                                "reviewer_model": "gpt-6.1-terra",
                                "predicted_sql": "SELECT 1",
                            })
                        stream.write(json.dumps(row) + "\n")
            manifest = {
                "completed": True, "agent_variant": "RoleSpecializedSelfReflection",
                "split": "all", "run_id": "run", "selection_id": "selection",
                "dataset_manifest": {"release": "2026"},
                "selection_sha256": sha(self.folder / "selection_manifest.json"),
                "expected_questions": len(selected),
                "question_ids": [q["question_id"] for q in selected],
                "generator_provider": "chatgpt-siwc", "generator_model": "gpt-6-luna",
                "reviewer_provider": "chatgpt-siwc", "reviewer_model": "gpt-6.1-terra",
                **info,
                "prediction_sha256": sha(path / ARTIFACTS[0]),
                "trace_sha256": sha(path / ARTIFACTS[1]),
                "review_reports_sha256": sha(path / ARTIFACTS[2]),
            }
            if i == 2:
                manifest.update(changes)
            (path / "inference_manifest.json").write_text(json.dumps(manifest))

    def merge(self):
        return merge_shards(
            folder=self.folder, run_root=self.root, split_dirs=self.split_dirs,
            selections=self.selections, dataset_manifest={"release": "2026"},
            shard_count=2, variant="RoleSpecializedSelfReflection", run_id="run",
        )

    def test_500_questions_split_exactly_250_each(self):
        selected = [{"question_id": 1000 + i * 7} for i in range(500)]
        first, first_meta = shard_slice(selected, 1, 2)
        second, second_meta = shard_slice(selected, 2, 2)
        self.assertEqual((len(first), len(second)), (250, 250))
        self.assertEqual((first_meta["position_start"], first_meta["position_end"]), (1, 250))
        self.assertEqual((second_meta["position_start"], second_meta["position_end"]), (251, 500))
        self.assertEqual([q["question_id"] for q in first + second],
                         [q["question_id"] for q in selected])

    def test_selection_position_sharding(self):
        rows = [{"question_id": n} for n in [100, 20, 444, 12, 91, 66]]
        a, left = shard_slice(rows, 1, 2)
        b, right = shard_slice(rows, 2, 2)
        self.assertEqual([q["question_id"] for q in a], [100, 20, 444])
        self.assertEqual([q["question_id"] for q in b], [12, 91, 66])
        self.assertEqual((left["position_start"], left["position_end"]), (1, 3))
        self.assertEqual((right["position_start"], right["position_end"]), (4, 6))
        with self.assertRaises(ValueError):
            shard_slice(rows, 3, 2)

    def test_merge_all_and_original_dev_test(self):
        self.populate()
        summary = self.merge()
        self.assertEqual(
            (summary["question_count"], summary["dev_count"], summary["test_count"]),
            (6, 4, 2),
        )
        for split, root in [("all", self.root), *self.split_dirs.items()]:
            manifest = json.loads((root / "inference_manifest.json").read_text())
            ids = [json.loads(line)["question_id"] for line in
                   (root / "predictions.jsonl").read_text().splitlines()]
            self.assertEqual(manifest["question_ids"], ids)
            self.assertEqual(manifest["prediction_sha256"],
                             sha(root / "predictions.jsonl"))
            self.assertTrue(manifest["merge_complete"])
            self.assertEqual(manifest["split"], split)
        with self.assertRaisesRegex(ValueError, "overwrite"):
            self.merge()

    def test_mismatched_model_aborts_without_publishing(self):
        self.populate(reviewer_model="wrong")
        with self.assertRaisesRegex(ValueError, "mismatch"):
            self.merge()
        self.assertFalse((self.root / "inference_manifest.json").exists())
        self.assertFalse(self.split_dirs["dev"].exists())

    def test_invalid_checksum_aborts(self):
        self.populate()
        path = shard_dir(self.root, 2, 2) / ARTIFACTS[0]
        path.write_text(path.read_text() + "{}\n")
        with self.assertRaisesRegex(ValueError, "checksum"):
            self.merge()

    def test_missing_shard_aborts(self):
        self.populate()
        (shard_dir(self.root, 2, 2) / "inference_manifest.json").unlink()
        with self.assertRaisesRegex(ValueError, "Missing completed shard"):
            self.merge()


if __name__ == "__main__":
    unittest.main()
