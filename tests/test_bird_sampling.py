"""Offline deterministic Mini-Dev sampling and split integrity tests."""
import unittest
from scr.evaluation.bird_sampling import select_questions, difficulty_counts, LEVELS


class Dataset:
    def __init__(self):
        self.splits = {
            "dev": [dict(question_id=i, db_id=f"db{i%3}", difficulty=LEVELS[i%3], question=str(i), evidence="") for i in range(30)],
            "test": [dict(question_id=100+i, db_id=f"db{i%2}", difficulty=LEVELS[i%3], question=str(i), evidence="") for i in range(15)],
        }

    def get_split(self, split):
        return self.splits["test" if split == "heldout" else split]


class SamplingTests(unittest.TestCase):
    def setUp(self):
        self.dataset = Dataset()
        self.counts = dict(simple=4, moderate=3, challenging=2)

    def test_exact_counts_determinism_and_different_seed(self):
        first = select_questions(self.dataset, "dev", self.counts, 42)
        self.assertEqual(first, select_questions(self.dataset, "dev", self.counts, 42))
        self.assertEqual(difficulty_counts(first), self.counts)
        self.assertEqual(len(first), 9)
        self.assertNotEqual([x["question_id"] for x in first], [x["question_id"] for x in select_questions(self.dataset, "dev", self.counts, 7)])

    def test_dev_heldout_never_overlap(self):
        a = select_questions(self.dataset, "dev", self.counts, 42)
        b = select_questions(self.dataset, "test", self.counts, 42)
        self.assertEqual(b, select_questions(self.dataset, "heldout", self.counts, 42))
        self.assertTrue({x["question_id"] for x in a}.isdisjoint(x["question_id"] for x in b))
        self.assertEqual(difficulty_counts(b), self.counts)

    def test_invalid_counts_and_unavailable_quantity(self):
        for counts in ({"simple": -1, "moderate": 0, "challenging": 0},
                       {"simple": True, "moderate": 1, "challenging": 0},
                       {"simple": 100, "moderate": 0, "challenging": 0},
                       {"simple": 1}):
            with self.subTest(counts=counts), self.assertRaises(ValueError):
                select_questions(self.dataset, "dev", counts, 42)

    def test_round_robin_covers_database_where_possible(self):
        rows = [dict(question_id=i, db_id=f"db{i%3}", difficulty="simple") for i in range(9)]
        self.dataset.splits["dev"] = rows
        sampled = select_questions(self.dataset, "dev", dict(simple=3, moderate=0, challenging=0), 42)
        self.assertEqual(len({x["db_id"] for x in sampled}), 3)


if __name__ == "__main__":
    unittest.main()


class RatioTests(unittest.TestCase):
    def test_count_allocation(self):
        from scr.evaluation.bird_sampling import allocate_ratios
        selections = allocate_ratios(10, .8, "5:3:2", Dataset())
        self.assertEqual(sum(selections["dev"].values()), 8)
        self.assertEqual(sum(selections["test"].values()), 2)
