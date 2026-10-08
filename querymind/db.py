"""Read-only SQLite access for model-generated SQL.

The file is opened with mode=ro, an authorizer only allows reads, and a
progress handler enforces a time limit.
"""

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent.parent / "database" / "Chinook_Sqlite.sqlite"

_ALLOWED_ACTIONS = {
    sqlite3.SQLITE_SELECT,
    sqlite3.SQLITE_READ,
    sqlite3.SQLITE_FUNCTION,
    getattr(sqlite3, "SQLITE_RECURSIVE", 33),
}


class QueryError(Exception):
    """Raised for any rejected or failing query; the message is safe to show the LLM."""


@dataclass
class QueryResult:
    columns: list[str]
    rows: list[tuple]
    truncated: bool


def _authorizer(action, arg1, arg2, db_name, trigger):
    return sqlite3.SQLITE_OK if action in _ALLOWED_ACTIONS else sqlite3.SQLITE_DENY


class ReadOnlyDatabase:
    def __init__(self, path: Path | str = DEFAULT_DB, timeout_s: float = 5.0, max_rows: int = 200):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(self.path)
        self.timeout_s = timeout_s
        self.max_rows = max_rows

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(f"file:{self.path.as_posix()}?mode=ro", uri=True, check_same_thread=False)
        conn.set_authorizer(_authorizer)
        return conn

    def schema(self, sample_rows: int = 2) -> str:
        """CREATE statements plus a couple of example rows per table, for the prompt."""
        conn = sqlite3.connect(f"file:{self.path.as_posix()}?mode=ro", uri=True)
        try:
            parts = []
            tables = conn.execute(
                "SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            ).fetchall()
            for name, sql in tables:
                cur = conn.execute(f'SELECT * FROM "{name}" LIMIT {sample_rows}')
                cols = [d[0] for d in cur.description]
                rows = cur.fetchall()
                sample = "\n".join("  " + " | ".join(str(v) for v in r) for r in rows)
                parts.append(f"{sql.strip()}\n/* sample rows ({', '.join(cols)}):\n{sample}\n*/")
            return "\n\n".join(parts)
        finally:
            conn.close()

    def run(self, sql: str) -> QueryResult:
        sql = sql.strip().rstrip(";").strip()
        if not sql:
            raise QueryError("empty query")
        conn = self._connect()
        deadline = time.monotonic() + self.timeout_s
        conn.set_progress_handler(lambda: 1 if time.monotonic() > deadline else 0, 10_000)
        try:
            cur = conn.execute(sql)
            columns = [d[0] for d in cur.description] if cur.description else []
            rows = cur.fetchmany(self.max_rows + 1)
        except sqlite3.Error as exc:  # includes "one statement at a time" ProgrammingError
            msg = str(exc)
            if "one statement at a time" in msg:
                msg = "only a single SQL statement is allowed"
            elif "interrupted" in msg:
                msg = f"query exceeded the {self.timeout_s:.0f}s time limit"
            elif "not authorized" in msg or "readonly" in msg:
                msg = "only read-only SELECT queries are allowed"
            raise QueryError(msg) from exc
        finally:
            conn.close()
        return QueryResult(columns, rows[: self.max_rows], truncated=len(rows) > self.max_rows)
