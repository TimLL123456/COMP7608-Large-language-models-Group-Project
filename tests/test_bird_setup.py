"""Offline KORA-02 setup tests with synthetic fixtures (no downloads)."""

import json
import sqlite3
import tempfile
import warnings
from contextlib import closing
import unittest
import zipfile
from pathlib import Path

from scr.datasets.bird import BirdDataset, make_split, read_annotations
from scr.datasets.setup_bird import safe_extract_zip, setup, verify


def make_fixture(folder: Path) -> tuple[Path, Path]:
    """Build 500 fake original-shaped questions and 11 tiny SQLite DBs."""
    folder.mkdir(parents=True, exist_ok=True)
    rows = [{"question_id": 2000 + i, "db_id": f"demo_{i % 11}",
             "question": f"How many entries in demo_{i % 11}?", "evidence": "",
             "SQL": "SELECT count(*) FROM records", "difficulty": ["simple", "moderate", "challenging"][i % 3]}
            for i in range(500)]
    annotations = folder / "sample_annotations.json"
    annotations.write_text(json.dumps(rows), encoding="utf-8")
    archive = folder / "sample_databases.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for n in range(11):
            scratch = folder / f"db{n}.sqlite"
            with closing(sqlite3.connect(scratch)) as conn:
                conn.execute("CREATE TABLE records (id INTEGER PRIMARY KEY, amount REAL)")
                conn.execute("INSERT INTO records VALUES (1, 2)")
                conn.commit()
            bundle.write(scratch, f"minidev/dev_databases/demo_{n}/demo_{n}.sqlite")
            bundle.writestr(f"minidev/dev_databases/demo_{n}/database_description/records.csv",
                            "column_name,column_description\nid,Identifier\n")
            scratch.unlink()
    return annotations, archive


class OriginalMiniDevTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.annotations, self.archive = make_fixture(self.base)
        self.root = self.base / "data" / "original-mini-dev"

    def test_setup_verify_idempotence_and_checksums(self):
        result = setup(self.root, archive=self.archive, annotations=self.annotations)
        self.assertEqual({k: result[k] for k in ("questions", "databases", "dev", "test")},
                         {"questions": 500, "databases": 11, "dev": 400, "test": 100})
        self.assertEqual(verify(self.root)["status"], "PASS")
        self.assertEqual(setup(self.root)["status"], "PASS")
        manifest = json.loads((self.root / "dataset_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["source_verification"], "manual_annotation_unverified_against_hf")
        self.assertEqual(len(manifest["databases"]), 11)
        db = BirdDataset(self.root).get_database_path("demo_1")
        with db.open("ab") as handle:
            handle.write(b"X")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            verify(self.root)

    def test_verify_only_cli(self):
        from io import StringIO
        from contextlib import redirect_stdout
        from scr.datasets.setup_bird import main
        setup(self.root, archive=self.archive, annotations=self.annotations)
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--root", str(self.root), "--verify-only"]), 0)
        self.assertIn('"status": "PASS"', output.getvalue())
        self.assertIn("manual_annotation_unverified_against_hf", output.getvalue())

    def test_loader_gold_isolation_splits_schema_descriptions(self):
        setup(self.root, archive=self.archive, annotations=self.annotations)
        ds = BirdDataset(self.root)
        public = ds.load_questions()
        self.assertEqual(len(public), 500)
        self.assertNotIn("SQL", public[0])
        self.assertNotIn("SQL", ds.get_agent_input(public[0]["question_id"]))
        self.assertEqual(len(ds.get_split("dev")), 400)
        self.assertEqual(len(ds.get_split("test")), 100)
        self.assertTrue(set(r["question_id"] for r in ds.get_split("dev")).isdisjoint(
            r["question_id"] for r in ds.get_split("test")))
        self.assertIn("records", ds.get_schema("demo_0"))
        self.assertEqual(ds.get_descriptions("demo_0")["records.csv"][0]["column_name"], "id")
        with self.assertRaises(KeyError):
            ds.get_database_path("../bad")

    def test_split_determinism_unchanged_order(self):
        data = read_annotations(self.annotations)
        a = make_split(data)
        self.assertEqual(a, make_split(list(reversed(data))))
        self.assertNotEqual(a, make_split(data, seed=7))
        self.assertEqual((len(a["dev"]), len(a["test"])), (400, 100))

    def test_legacy_heldout_manifest_read_without_rewriting(self):
        setup(self.root, archive=self.archive, annotations=self.annotations)
        manifest_path = self.root / "dataset_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        original_ids = manifest["split"]["test"]
        manifest["split"]["heldout"] = manifest["split"].pop("test")
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        dataset = BirdDataset(self.root)
        self.assertEqual([q["question_id"] for q in dataset.get_split("test")], original_ids)
        self.assertEqual(dataset.get_split("heldout"), dataset.get_split("test"))
        self.assertEqual(verify(self.root)["test"], 100)
        self.assertIn("heldout", json.loads(manifest_path.read_text())["split"])

    def test_difficulty_distribution_counts(self):
        result = setup(self.root, archive=self.archive, annotations=self.annotations)
        self.assertEqual(sum(result["difficulty_distribution"]["dev"].values()), 400)
        self.assertEqual(sum(result["difficulty_distribution"]["test"].values()), 100)

    def test_refuse_v2_wrong_counts_duplicates(self):
        data = json.loads(self.annotations.read_text())
        data += data[:280]
        self.annotations.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "Expected 500"):
            read_annotations(self.annotations)
        with self.assertRaises(ValueError):
            setup(self.root, archive=self.archive, annotations=self.annotations)
        self.assertFalse(self.root.exists())

    def test_reject_zip_traversal_symlink_duplicate(self):
        bad_cases = {
            "traversal": [("../evil", "content")],
            "absolute": [("/outside", "content")],
            "drive": [("C:/outside", "content")],
            "duplicate": [("foo.txt", "one"), ("foo.txt", "two")],
        }
        for name, entries in bad_cases.items():
            with self.subTest(name=name):
                path = self.base / f"{name}.zip"
                with zipfile.ZipFile(path, "w") as z, warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    for item, content in entries:
                        z.writestr(item, content)
                with self.assertRaises(ValueError):
                    safe_extract_zip(path, self.base / "bad_result")
                self.assertFalse((self.base.parent / "evil").exists())

    def test_partial_archive_never_installs_root(self):
        broken = self.base / "broken.zip"
        with zipfile.ZipFile(broken, "w") as z:
            z.writestr("other/thing.txt", "hello")
        with self.assertRaisesRegex(ValueError, "Expected exactly one SQLite"):
            setup(self.root, archive=broken, annotations=self.annotations)
        self.assertFalse(self.root.exists())

    def test_write_denied_on_readonly_connection(self):
        from scr.datasets.bird import read_only_connection
        setup(self.root, archive=self.archive, annotations=self.annotations)
        db = BirdDataset(self.root).get_database_path("demo_2")
        with read_only_connection(db) as conn:
            self.assertEqual(conn.execute("SELECT count(*) FROM records").fetchone()[0], 1)
            with self.assertRaises(sqlite3.OperationalError):
                conn.execute("INSERT INTO records (id) VALUES (2)")


if __name__ == "__main__":
    unittest.main()
