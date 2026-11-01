"""Offline SQLite safety tests: no Ollama, LangChain or model downloads."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scr" / "baselines"))
from scr.baselines.sqlite_readonly import ReadOnlySqlite, create_demo_db


class SQLiteSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "demo.sqlite"
        create_demo_db(self.path)
        self.store = ReadOnlySqlite(self.path, max_rows=2)

    def test_list_and_inspect_tables(self):
        names = self.store.list_tables()
        self.assertNotIn("error", names)
        self.assertEqual({row[0] for row in names["rows"]}, {"customers", "orders"})
        details = self.store.inspect_table("orders")
        self.assertIn("amount", {c["name"] for c in details["columns"]})
        self.assertEqual(details["foreign_keys"][0]["table"], "customers")

    def test_valid_select_and_truncation(self):
        r = self.store.execute("SELECT customer_name FROM customers ORDER BY customer_id")
        self.assertEqual(r["rows"], [["Ada"], ["Ben"]])
        self.assertTrue(r["truncated"])
        self.assertEqual(self.store.execute("SELECT COUNT(*) FROM orders")["rows"], [[3]])

    def test_no_writes_or_unsafe_commands(self):
        for sql in [
            "DELETE FROM customers",
            "UPDATE customers SET customer_name='Bad'",
            "DROP TABLE customers",
            "PRAGMA writable_schema=ON",
            "ATTACH DATABASE 'other.db' AS other",
            "SELECT 1; DELETE FROM orders",
            "WITH x AS (SELECT 1) DELETE FROM orders",
            "SELECT load_extension('evil')",
        ]:
            with self.subTest(sql=sql):
                self.assertIn("error", self.store.execute(sql))
        self.assertEqual(self.store.execute("SELECT COUNT(*) FROM customers")["rows"], [[3]])

    def test_safe_identifier_handling(self):
        self.assertEqual(self.store.inspect_table('orders"; DROP TABLE customers;--'),
                         {"error": "Unknown table or view"})
        self.assertEqual(self.store.execute("SELECT COUNT(*) FROM customers")["rows"], [[3]])

    def test_create_demo_db_closes_connection(self):
        """Immediately deleting the database must work on Windows, too."""
        disposable = Path(self.tmp.name) / "disposable.sqlite"
        create_demo_db(disposable)
        disposable.unlink()
        self.assertFalse(disposable.exists())

    def test_refuses_to_overwrite_seeded_database(self):
        with self.assertRaises(FileExistsError):
            create_demo_db(self.path)


    def test_timed_sql_and_bounded_preview(self):
        store = ReadOnlySqlite(self.path, max_rows=1)
        result = store.execute("SELECT customer_name FROM customers ORDER BY customer_id")
        self.assertEqual(len(result["rows"]), 1)
        self.assertTrue(result["truncated"])
        self.assertGreaterEqual(result["execution_ms"], 0)
        failed = store.execute("SELECT nonexistent FROM customers")
        self.assertIn("error", failed)
        self.assertGreaterEqual(failed["execution_ms"], 0)

    def test_cte_read_only(self):
        result = self.store.execute("WITH x AS (SELECT 3 AS n) SELECT n FROM x")
        self.assertEqual(result["rows"], [[3]])


if __name__ == "__main__":
    unittest.main()
