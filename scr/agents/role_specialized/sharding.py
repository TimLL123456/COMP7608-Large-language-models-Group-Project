"""Deterministic, immutable sharded inference artifacts for KORA role specialization."""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile


ARTIFACTS = ("predictions.jsonl", "traces.jsonl", "reviews/review_reports.jsonl")
CONSISTENCY_KEYS = (
    "agent_variant", "dataset_manifest", "selection_sha256", "selection_id",
    "split", "run_id", "selection_size", "shard_count", "generator_provider",
    "generator_model", "generator_reasoning_effort", "reviewer_provider",
    "reviewer_model", "reviewer_reasoning_effort", "prompt_variant",
    "b0_prompt_sha256", "reviewer_prompt_version", "reviewer_prompt_sha256",
    "max_attempts", "max_review_model_calls", "max_inspections",
    "max_total_model_calls", "max_total_tool_calls", "max_total_sql_calls",
    "preview_rows", "source_revision", "output_format_version",
)


def sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def shard_slice(selected: list[dict], index: int, count: int):
    """1-based contiguous selection positions, NOT BIRD question IDs."""
    if type(index) is not int or type(count) is not int or not 1 <= count <= len(selected) or not 1 <= index <= count:
        raise ValueError("Shard index/count must identify a nonempty part of the selection")
    size = (len(selected) + count - 1) // count
    start = (index - 1) * size
    end = min(start + size, len(selected))
    if start >= end:
        raise ValueError("Empty shard")
    return selected[start:end], {"shard_index": index, "shard_count": count,
                                 "position_start": start + 1, "position_end": end,
                                 "selection_size": len(selected)}


def shard_dir(root: Path, index: int, count: int) -> Path:
    return root / "shards" / f"shard-{index:02d}-of-{count:02d}"


def _read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        raise ValueError(f"Missing shard artifact: {path}")
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"Non-object JSONL entry in {path}")
            rows.append(row)
    return rows


def _write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2,
                               allow_nan=False) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as out:
        for row in rows:
            out.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")


def merge_shards(*, folder: Path, run_root: Path, split_dirs: dict[str, Path],
                 selections: dict[str, list[dict]], dataset_manifest: dict,
                 shard_count: int, variant: str, run_id: str) -> dict:
    """Verify every immutable shard before publishing combined and per-split outputs.

    No gold/reference SQL is read; only validated public question IDs are used.
    """
    if not 1 <= shard_count <= 999:
        raise ValueError("Invalid shard count")
    all_questions = selections["dev"] + selections["test"]
    expected_ids = [q["question_id"] for q in all_questions]
    if len(expected_ids) != len(set(expected_ids)):
        raise ValueError("Duplicate question IDs in selected dataset")
    if shard_count > len(expected_ids):
        raise ValueError("More shards than questions")
    if not run_root.is_dir():
        raise ValueError(f"Missing run root: {run_root}")
    for split, target in split_dirs.items():
        if split not in ("dev", "test") or target.exists() or target.is_symlink():
            raise ValueError(f"Refusing to overwrite target split: {target}")
    if any((run_root / name).exists() or (run_root / name).is_symlink()
           for name in (*ARTIFACTS, "inference_manifest.json")):
        raise ValueError("Merged output already exists: refusing to overwrite")
    selection_hash = sha(folder / "selection_manifest.json")
    manifests = []
    records = {name: [] for name in ARTIFACTS}
    for index in range(1, shard_count + 1):
        subdir = shard_dir(run_root, index, shard_count)
        manifest_file = subdir / "inference_manifest.json"
        if not manifest_file.is_file():
            raise ValueError(f"Missing completed shard {index}")
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        selected, info = shard_slice(all_questions, index, shard_count)
        ids = [q["question_id"] for q in selected]
        required = {
            "completed": True, "agent_variant": variant, "split": "all",
            "run_id": run_id, "selection_id": folder.name,
            "selection_sha256": selection_hash,
            "dataset_manifest": dataset_manifest, "expected_questions": len(ids),
            "question_ids": ids, **info,
        }
        if any(manifest.get(k) != value for k, value in required.items()):
            raise ValueError(f"Shard {index} metadata or question range mismatch")
        if manifests and any(manifest.get(k) != manifests[0].get(k)
                             for k in CONSISTENCY_KEYS):
            raise ValueError(f"Shard {index} model/prompt/budget/revision mismatch")
        for filename, digest_name in zip(
            ARTIFACTS, ("prediction_sha256", "trace_sha256", "review_reports_sha256")
        ):
            path = subdir / filename
            if sha(path) != manifest.get(digest_name):
                raise ValueError(f"Shard {index} checksum mismatch: {filename}")
            part = _read_jsonl(path)
            if [record.get("question_id") for record in part] != ids:
                raise ValueError(f"Shard {index} missing/reordered/duplicate IDs: {filename}")
            records[filename].extend(part)
        for row in records["predictions.jsonl"][-len(ids):]:
            if (row.get("provider") != manifest.get("generator_provider") or
                row.get("model") != manifest.get("generator_model") or
                row.get("reviewer_provider") != manifest.get("reviewer_provider") or
                row.get("reviewer_model") != manifest.get("reviewer_model")):
                raise ValueError(f"Shard {index} prediction model mismatch")
        manifests.append(manifest)
    if any([x["question_id"] for x in records[filename]] != expected_ids
           for filename in ARTIFACTS):
        raise ValueError("Merged question coverage mismatch")

    selected_id_sets = {split: {q["question_id"] for q in questions}
                        for split, questions in selections.items()}
    with tempfile.TemporaryDirectory(prefix=".merge-staging-", dir=run_root) as stage:
        staging = Path(stage)
        staged = {"all": staging / "all", **{split: staging / split
                                               for split in ("dev", "test")}}
        for split, directory in staged.items():
            if split == "all":
                parts = records
                questions = all_questions
            else:
                members = selected_id_sets[split]
                parts = {name: [row for row in records[name]
                                if row["question_id"] in members]
                         for name in ARTIFACTS}
                questions = selections[split]
            ids = [q["question_id"] for q in questions]
            if any([r["question_id"] for r in parts[name]] != ids for name in ARTIFACTS):
                raise ValueError(f"Merged {split} question order mismatch")
            for filename, rows in parts.items():
                _write_jsonl(directory / filename, rows)
            original = manifests[0]
            new_manifest = {k: v for k, v in original.items()
                            if k not in ("shard_index", "shard_count", "position_start", "position_end")}
            new_manifest.update({
                "split": split, "completed": True, "question_ids": ids,
                "expected_questions": len(ids), "selection_size": len(ids),
                "missing_final_sql": sum(row.get("predicted_sql") is None
                                         for row in parts["predictions.jsonl"]),
                "prediction_sha256": sha(directory / "predictions.jsonl"),
                "trace_sha256": sha(directory / "traces.jsonl"),
                "review_reports_sha256": sha(directory / "reviews/review_reports.jsonl"),
                "merged_from_shards": [str(shard_dir(run_root, i, shard_count))
                                       for i in range(1, shard_count + 1)],
                "merge_complete": True,
            })
            _write_json(directory / "inference_manifest.json", new_manifest)
        # All validation/staging happens before any publication. Never replace
        # existing runs, even if another process creates one after preflight.
        published = []
        try:
            for split in ("dev", "test"):
                target = split_dirs[split]
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists() or target.is_symlink():
                    raise ValueError(f"Target appeared during merge: {target}")
                os.rename(staged[split], target)
                published.append(target)
            for filename in (*ARTIFACTS, "inference_manifest.json"):
                target = run_root / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists() or target.is_symlink():
                    raise ValueError(f"Merged artifact appeared during merge: {target}")
                os.rename(staged["all"] / filename, target)
                published.append(target)
        except Exception:
            for target in reversed(published):
                if target.is_dir():
                    import shutil
                    shutil.rmtree(target)
                else:
                    target.unlink(missing_ok=True)
            raise
    return {"question_count": len(expected_ids),
            "dev_count": len(selections["dev"]),
            "test_count": len(selections["test"]),
            "shard_count": shard_count,
            "merged_root": str(run_root)}
