"""Difficulty-stratified deterministic selection from existing KORA-02 splits."""
from __future__ import annotations

from collections import Counter, defaultdict
import random

LEVELS = ("simple", "moderate", "challenging")


def select_questions(dataset, split: str, counts: dict[str, int], seed: int) -> list[dict]:
    """Select per-difficulty counts with database diversity when feasible."""
    if split not in ("dev", "test", "heldout"):
        raise ValueError("split must be dev or test")
    if set(counts) != set(LEVELS) or any(type(n) is not int or n < 0 for n in counts.values()):
        raise ValueError("counts must specify nonnegative integers for simple/moderate/challenging")
    if type(seed) is not int:
        raise ValueError("seed must be an integer")
    source_split = "dev" if split == "dev" else "test"
    # Preserve the historical test-question shuffle seed ("heldout") across renaming.
    legacy_seed_name = "dev" if split == "dev" else "heldout"
    pool = dataset.get_split(source_split)
    chosen = []
    for level in LEVELS:
        candidates = [row for row in pool if row["difficulty"] == level]
        requested = counts[level]
        if requested > len(candidates):
            raise ValueError(f"{split}/{level}: requested {requested}, available {len(candidates)}")
        by_db = defaultdict(list)
        for row in candidates:
            by_db[row["db_id"]].append(row)
        rng = random.Random(f"kora05-{seed}-{legacy_seed_name}-{level}")
        dbs = sorted(by_db)
        rng.shuffle(dbs)
        for db in dbs:
            by_db[db].sort(key=lambda row: row["question_id"])
            rng.shuffle(by_db[db])
        while requested:
            progressed = False
            for db in dbs:
                if requested and by_db[db]:
                    chosen.append(by_db[db].pop())
                    requested -= 1
                    progressed = True
            if not progressed:
                raise RuntimeError("sampling pool exhausted")
    chosen.sort(key=lambda row: row["question_id"])
    if len({row["question_id"] for row in chosen}) != len(chosen):
        raise ValueError("duplicate question IDs")
    return chosen


def difficulty_counts(rows: list[dict]) -> dict[str, int]:
    counts = Counter(row["difficulty"] for row in rows)
    return {level: counts[level] for level in LEVELS}

def allocate_ratios(total, dev_ratio, difficulty_ratio, dataset):
    """Apportion a fixed total without changing KORA-02 split membership."""
    import math
    if type(total) is not int or not 1 <= total <= 500 or not math.isfinite(dev_ratio) or not 0 <= dev_ratio <= 1:
        raise ValueError("Invalid total-questions or dev-ratio")
    def allocate(n, weights):
        if len(weights) != 3 or any(not math.isfinite(v) or v < 0 for v in weights) or not sum(weights):
            raise ValueError("Invalid difficulty ratio")
        raw = [n * v / sum(weights) for v in weights]
        counts = [int(v) for v in raw]
        for i in sorted(range(3), key=lambda i: (-(raw[i]-counts[i]), i))[:n-sum(counts)]:
            counts[i] += 1
        return dict(zip(LEVELS, counts))
    if difficulty_ratio == "auto":
        weights = {s: [sum(q["difficulty"] == level for q in dataset.get_split(s)) for level in LEVELS] for s in ("dev", "test")}
    else:
        try:
            values = [float(v) for v in difficulty_ratio.split(":")]
        except ValueError as exc:
            raise ValueError("Use auto or S:M:C difficulty ratio") from exc
        weights = {"dev": values, "test": values}
    dev_size = round(total * dev_ratio)
    return {"dev": allocate(dev_size, weights["dev"]), "test": allocate(total-dev_size, weights["test"])}
