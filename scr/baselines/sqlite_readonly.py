"""Read-only SQLite adapter moved from the original KORA SQL baseline."""
from contextlib import closing
from pathlib import Path
import sqlite3
import time

PROJECT_ROOT = Path(__file__).resolve().parents[2]

class ReadOnlySqlite:
    """A database-level read-only boundary, independent of LLM instructions."""

    def __init__(self, database, max_rows=20, max_seconds=5.0):
        self.database = Path(database).expanduser().resolve()
        if not self.database.is_file():
            raise FileNotFoundError(f"Database does not exist: {self.database}")
        if max_rows < 1 or max_seconds <= 0:
            raise ValueError("max_rows and max_seconds must be positive")
        self.max_rows = max_rows
        self.max_seconds = max_seconds

    def _connect(self):
        db_uri = self.database.as_uri() + "?mode=ro"
        connection = sqlite3.connect(db_uri, uri=True, timeout=1)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only=ON")
        deadline = time.monotonic() + self.max_seconds
        connection.set_progress_handler(
            lambda: int(time.monotonic() >= deadline), 1000
        )

        permitted = {sqlite3.SQLITE_READ, sqlite3.SQLITE_SELECT,
                     sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}
        blocked_functions = {"load_extension", "readfile", "writefile"}

        def authorize(action, arg1, arg2, db_name, trigger):
            # Read-only table-valued PRAGMAs are needed for inspect_table().
            if action == sqlite3.SQLITE_PRAGMA:
                return (sqlite3.SQLITE_OK if (arg1 or "").lower() in
                        {"table_info", "foreign_key_list"} else sqlite3.SQLITE_DENY)
            if action not in permitted:
                return sqlite3.SQLITE_DENY
            if action == sqlite3.SQLITE_FUNCTION and (arg2 or arg1 or "").lower() in blocked_functions:
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK

        connection.set_authorizer(authorize)
        return connection

    def execute(self, sql):
        started = time.perf_counter()
        if not isinstance(sql, str) or len(sql) > 6000:
            return {"error": "SQL must be a string of at most 6000 characters", "execution_ms": 0.0}
        if not sql.lstrip().upper().startswith(("SELECT ", "SELECT\n", "WITH ", "WITH\n")):
            return {"error": "Only SELECT or SELECT-producing WITH statements are allowed", "execution_ms": 0.0}
        try:
            with closing(self._connect()) as con:
                cursor = con.execute(sql)
                columns = [item[0] for item in cursor.description or []]
                rows = cursor.fetchmany(self.max_rows + 1)
                return {
                    "columns": columns,
                    "rows": [[self._safe_value(value) for value in row] for row in rows[:self.max_rows]],
                    "truncated": len(rows) > self.max_rows,
                    "execution_ms": round((time.perf_counter() - started) * 1000, 3),
                }
        except (sqlite3.Error, ValueError) as exc:
            return {"error": f"{type(exc).__name__}: {exc}",
                    "execution_ms": round((time.perf_counter() - started) * 1000, 3)}

    @staticmethod
    def _safe_value(value):
        if isinstance(value, bytes):
            return f"<binary {len(value)} bytes>"
        if isinstance(value, str):
            return value[:400]
        return value

    def list_tables(self):
        return self.execute(
            "SELECT name, type FROM sqlite_master "
            "WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )

    def inspect_table(self, name):
        with closing(self._connect()) as con:
            found = con.execute(
                "SELECT sql FROM sqlite_master WHERE name=? "
                "AND type IN ('table','view')", (name,)
            ).fetchone()
            if found is None:
                return {"error": "Unknown table or view"}
            # Table-valued PRAGMA functions bind the table name safely.
            columns = con.execute(
                "SELECT name, type, pk FROM pragma_table_info(?)", (name,)
            ).fetchall()
            foreign_keys = con.execute(
                "SELECT \"table\", \"from\", \"to\" FROM pragma_foreign_key_list(?)", (name,)
            ).fetchall()
            return {
                "ddl": str(found["sql"] or "")[:4000],
                "columns": [dict(item) for item in columns],
                "foreign_keys": [dict(item) for item in foreign_keys],
            }


def create_demo_db(path):
    """Create an explicitly requested, disposable example database."""
    target = Path(path)
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    seed = (PROJECT_ROOT / "tests" / "fixtures" / "demo_schema.sql").read_text(encoding="utf-8")
    # sqlite3.Connection's context manager commits but does not close the file.
    with closing(sqlite3.connect(target)) as con, con:
        con.executescript(seed)
    return target


