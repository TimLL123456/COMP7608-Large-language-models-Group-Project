"""Safety and schema tests for description-only restoration (no network)."""
import csv
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import warnings
import zipfile

from scr.datasets.restore_bird_descriptions import restore_descriptions


class FixtureDataset:
    def __init__(self, root, schemas):
        self.root = root
        self.schemas = schemas
        self.manifest = {"databases": dict.fromkeys(schemas)}
        for db in schemas:
            folder = root / db
            folder.mkdir()
            (folder / f"{db}.sqlite").write_bytes(b"protected database bytes")
        (root / "annotations.json").write_text('"protected annotations"')

    def get_schema(self, db):
        return self.schemas[db]

    def get_database_path(self, db):
        return self.root / db / f"{db}.sqlite"


def table(*columns):
    return {"columns": [{"name": c, "type": "TEXT"} for c in columns]}


def description(*columns):
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(["original_column_name", "column_description"])
    writer.writerows((c, f"Description for {c}") for c in columns)
    return stream.getvalue().encode()


class DescriptionRestorationTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "dataset"
        self.root.mkdir()
        self.archive = self.base / "official.zip"
        self.schema = self.base / "schema.json"
        self.schema.write_text("{}")

    def write_archive(self, entries):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(self.archive, "w") as out:
                for name, raw in entries:
                    out.writestr(name, raw)

    def dataset(self):
        return FixtureDataset(self.root, {"example": {"items": table("id", "name")}})

    def test_restore_preserves_existing_files_and_verifies_identical_csv(self):
        dataset = self.dataset()
        protected = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        raw = description("id", "name")
        self.write_archive([("package/example/database_description/items.csv", raw),
                            ("package/example/example.sqlite", b"must not extract")])
        result = restore_descriptions(dataset, self.archive, self.schema)
        self.assertEqual(result["csv_files"], 1)
        self.assertEqual((self.root / "example/database_description/items.csv").read_bytes(), raw)
        self.assertTrue(all(p.read_bytes() == content for p, content in protected.items()))
        self.assertEqual(restore_descriptions(dataset, self.archive, self.schema,
                                             verify_existing=True)["status"], "PASS")

    def test_existing_description_is_never_overwritten(self):
        dataset = self.dataset()
        self.write_archive([("p/example/database_description/items.csv", description("id", "name"))])
        folder = self.root / "example/database_description"
        folder.mkdir()
        target = folder / "items.csv"
        target.write_bytes(b"retain this")
        with self.assertRaises(FileExistsError):
            restore_descriptions(dataset, self.archive, self.schema)
        self.assertEqual(target.read_bytes(), b"retain this")
        with self.assertRaises(ValueError):
            restore_descriptions(dataset, self.archive, self.schema, verify_existing=True)

    def test_invalid_later_table_prevents_all_writes(self):
        dataset = FixtureDataset(self.root, {"example": {"items": table("id"), "other": table("value")}})
        self.write_archive([("p/example/database_description/items.csv", description("id")),
                            ("p/example/database_description/other.csv", description("wrong"))])
        with self.assertRaisesRegex(ValueError, "Column mismatch"):
            restore_descriptions(dataset, self.archive, self.schema)
        self.assertFalse((self.root / "example/database_description").exists())

    def test_duplicate_table_and_duplicate_columns_are_rejected(self):
        dataset = self.dataset()
        name = "p/example/database_description/items.csv"
        self.write_archive([(name, description("id", "name")), (name, description("id", "name"))])
        with self.assertRaisesRegex(ValueError, "duplicate description"):
            restore_descriptions(dataset, self.archive, self.schema)
        self.write_archive([(name, description("id", "id", "name"))])
        with self.assertRaisesRegex(ValueError, "Duplicate or empty column"):
            restore_descriptions(dataset, self.archive, self.schema)

    def test_symlinked_output_directory_is_rejected(self):
        dataset = self.dataset()
        outside = self.base / "outside"
        outside.mkdir()
        (self.root / "example/database_description").symlink_to(outside, target_is_directory=True)
        self.write_archive([("p/example/database_description/items.csv", description("id", "name"))])
        with self.assertRaisesRegex(ValueError, "Symlinked description directory"):
            restore_descriptions(dataset, self.archive, self.schema)
        self.assertEqual(list(outside.iterdir()), [])

    def test_only_documented_release_adaptations_are_allowed(self):
        dataset = FixtureDataset(self.root, {
            "formula_1": {"constructors": table("constructorId")},
            "toxicology": {"element": table("element_id", "element_name")},
        })
        self.schema.write_text(json.dumps({"toxicology": "CREATE TABLE `element` (\n`element_id` TEXT,\n`element_name` TEXT\n);"}))
        self.write_archive([("p/formula_1/database_description/constructors.csv", description("constructorId", "wins"))])
        result = restore_descriptions(dataset, self.archive, self.schema)
        self.assertEqual(result["csv_files"], 2)
        with (self.root / "formula_1/database_description/constructors.csv").open() as stream:
            self.assertEqual([r["original_column_name"] for r in csv.DictReader(stream)], ["constructorId"])
        with (self.root / "toxicology/database_description/element.csv").open() as stream:
            self.assertTrue(all(r["column_description"] == "" for r in csv.DictReader(stream)))


if __name__ == "__main__":
    unittest.main()
