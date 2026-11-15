"""Offline regression tests for the run-scoped scoped metadata engine."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import tempfile
import unittest

from scr.metadata.engine import MetadataEngine, MAX_NOTE_CHARS


SCHEMA = {
    "online_transactions": {"columns": [{"name": "amount"}]},
    "store_transactions": {"columns": [{"name": "amount"}]},
}


class MetadataEngineTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "experiment-001"
        self.engine = MetadataEngine(
            self.root, "retail_db", 1, SCHEMA,
            descriptions={"online.csv": [
                {"column": "amount", "meaning": "Online gross sales amount"},
            ]},
        )

    def create(self, engine=None, **overrides):
        kwargs = {
            "note_type": "metric", "table_name": "online_transactions",
            "concept_id": "gross_sales", "title": "Online gross sales",
            "summary": "Online gross sales before discounts",
            "keywords": "gross sales, online",
            "body": "Candidate column: amount. Refund handling is unknown.",
            "source_refs": "schema:online_transactions.amount",
        }
        kwargs.update(overrides)
        return (engine or self.engine).create(**kwargs)

    def test_create_search_read_and_index(self):
        made = self.create()
        self.assertTrue(made["created"])
        self.assertEqual(made["revision"], 1)
        found = self.engine.search("gross sales")
        self.assertEqual(found["candidates"][0]["note_id"], made["note_id"])
        self.assertLessEqual(len(found["description_hints"]), 3)
        read = self.engine.read(made["note_id"])
        self.assertIn("Online gross sales", read["content"])
        self.assertLessEqual(len(read["content"]), MAX_NOTE_CHARS)
        self.assertEqual(read["source_refs"], ["schema:online_transactions.amount"])
        index = json.loads((self.root / "knowledge" / "retail_db" / "index.json").read_text())
        self.assertEqual(index[made["note_id"]]["revision"], 1)
        operations = [
            json.loads(x) for x in
            (self.root / "knowledge_operations.jsonl").read_text().splitlines()
        ]
        self.assertEqual([x["action"] for x in operations],
                         ["create", "search", "read"])

    def test_create_collision_and_revision_update(self):
        made = self.create()
        self.assertIn("error", self.create())
        updated = self.engine.update(
            made["note_id"], 1, "Online gross sales",
            "Source amount for online gross sales", "online, gross sales",
            "Candidate column amount; cancellation handling still unknown.",
            "schema:online_transactions.amount")
        self.assertEqual(updated["revision"], 2)
        self.assertIn("error", self.engine.update(
            made["note_id"], 1, "Stale", "Stale definition", "sales",
            "Old note.", "schema:online_transactions.amount"))
        self.assertEqual(self.engine.read(made["note_id"])["revision"], 2)

    def test_database_and_table_isolation(self):
        online = self.create()
        store = self.create(table_name="store_transactions",
                            summary="Store gross sales uses a different convention")
        self.assertNotEqual(online["note_id"], store["note_id"])
        filtered = self.engine.search("gross sales", "store_transactions")
        self.assertEqual([x["note_id"] for x in filtered["candidates"]], [store["note_id"]])
        database_b = MetadataEngine(self.root, "another_db", 2, SCHEMA)
        self.assertEqual(database_b.search("gross sales")["candidates"], [])
        self.assertIn("error", database_b.read(online["note_id"]))
        self.assertIn("error", database_b.update(
            online["note_id"], 1, "wrong", "wrong db", "sales",
            "bad", "schema:online_transactions.amount"))
        self.assertIn("error", self.create(table_name="unknown_table"))

    def test_new_experiment_starts_empty_but_question_reuses(self):
        original = self.create()
        next_question = MetadataEngine(self.root, "retail_db", 99, SCHEMA)
        self.assertEqual(next_question.read(original["note_id"])["revision"], 1)
        other = MetadataEngine(self.root.parent / "experiment-002",
                               "retail_db", 1, SCHEMA)
        self.assertFalse(other.search("gross sales")["candidates"])

    def test_reject_oversize_and_invalid_sources_without_corrupting(self):
        original = self.create()
        before = self.engine.read(original["note_id"])["content"]
        self.assertIn("error", self.create(concept_id="large", body="x" * 1600))
        self.assertIn("error", self.engine.update(
            original["note_id"], 1, "Online", "Large update", "sales",
            "x" * 1600, "schema:online_transactions.amount"))
        self.assertIn("error", self.create(concept_id="no_evidence", source_refs=""))
        self.assertIn("error", self.create(concept_id="leak", body="Gold SQL: SELECT 1"))
        self.assertEqual(self.engine.read(original["note_id"])["content"], before)

    def test_note_ids_are_opaque_and_no_parent_traversal(self):
        made = self.create()
        for bad in ("../../secrets", "gross_sales", made["note_id"] + "/anything"):
            self.assertIn("error", self.engine.read(bad))
        self.assertIn("error", self.engine.search("sales", "../escape"))

    def test_search_loads_index_only_and_has_context_budget(self):
        note = self.create()
        for i in range(12):
            self.assertTrue(self.engine.search("sales")["candidates"])
        failures = []
        for _ in range(30):
            result = self.engine.read(note["note_id"])
            if "error" in result:
                failures.append(result)
                break
        self.assertTrue(failures)
        self.assertIn("budget", failures[0]["error"])

    def test_parallel_creates_do_not_drop_index_entries(self):
        def write(i):
            engine = MetadataEngine(self.root, "retail_db", i + 10, SCHEMA)
            return self.create(engine=engine, concept_id=f"gross_sales_{i}",
                               title=f"Metric {i}", summary=f"Metric {i}")

        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(write, range(24)))
        self.assertTrue(all(row.get("created") for row in results), results)
        directory = self.root / "knowledge" / "retail_db"
        index = json.loads((directory / "index.json").read_text())
        notes = list((directory / "notes").glob("*.md"))
        self.assertEqual(len(index), 24)
        self.assertEqual(len(notes), 24)

    def test_orphan_note_refuses_further_writes_non_destructively(self):
        first = self.create()
        folder = self.root / "knowledge" / "retail_db" / "notes"
        orphan = folder / ("n_" + "a" * 24 + ".md")
        orphan.write_text("not indexed", encoding="utf-8")
        result = self.create(concept_id="another_metric")
        self.assertIn("inconsistent", result["error"])
        self.assertTrue(orphan.is_file())
        self.assertEqual(self.engine.read(first["note_id"])["revision"], 1)

    def test_metadata_discovery_v2_repeated_note_read_is_not_charged_twice(self):
        v2 = MetadataEngine(self.root, "graph_db", 1, SCHEMA, definition_mode=True)
        body = (
            "## Business Summary\nAn online transaction table.\n"
            "## Business Use Cases\nAnalyze online activity.\n"
            "## Data Granularity\nRow uniqueness is unverified.\n"
            "## Data Scope & Exclusions\nScope unverified.\n"
        )
        # Use the actual four required sections, not a question-specific answer.
        made = v2.create("table", "online_transactions", "table_definition",
                         "Online transactions", "Online transaction records",
                         "online, transactions", body, "schema:online_transactions")
        self.assertTrue(made["created"], made)
        first = v2.read(made["note_id"])
        initial = v2.loaded_chars
        for _ in range(30):
            again = v2.read(made["note_id"])
            self.assertNotIn("error", again)
            self.assertTrue(again["cached"])
        self.assertEqual(v2.loaded_chars, initial)
        self.assertFalse(first["cached"])

    def test_updating_preserves_independent_notes(self):
        online = self.create()
        store = self.create(table_name="store_transactions",
                            summary="Store gross sales")
        updated = self.engine.update(
            online["note_id"], 1, "Online gross sales", "Updated online meaning",
            "online, gross sales", "Refund handling remains unknown.",
            "schema:online_transactions.amount")
        self.assertEqual(updated["revision"], 2)
        self.assertEqual(self.engine.read(store["note_id"])["revision"], 1)


if __name__ == "__main__":
    unittest.main()
