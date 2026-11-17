"""A LangGraph wrapper must not bypass the existing SQLite read-only guard."""
import sqlite3

from scr.baselines.sqlite_readonly import ReadOnlySqlite


def test_sqlite_read_only_and_row_cap(tmp_path):
    db = tmp_path / "sqlite.db"
    with sqlite3.connect(db) as con:
        con.execute("CREATE TABLE sample (id INTEGER)")
        con.executemany("INSERT INTO sample VALUES (?)", [(1,), (2,), (3,)])
    store = ReadOnlySqlite(db, max_rows=2)
    assert store.execute("SELECT id FROM sample ORDER BY id")["truncated"] is True
    assert len(store.execute("SELECT id FROM sample ORDER BY id")["rows"]) == 2
    assert "error" in store.execute("DELETE FROM sample")
    assert "error" in store.execute("WITH x AS (SELECT 1) DELETE FROM sample")
    with sqlite3.connect(db) as con:
        assert con.execute("SELECT COUNT(*) FROM sample").fetchone()[0] == 3
