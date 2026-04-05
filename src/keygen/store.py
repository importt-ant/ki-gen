"""SQLite persistence for generator state and key history."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from keygen.key import Key

_DEFAULT_DB = "keygen.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS generators (
    gen_key     TEXT PRIMARY KEY,
    cursor      INTEGER NOT NULL DEFAULT 0,
    state_extra TEXT NOT NULL DEFAULT '{}',
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS runs (
    key_id      TEXT PRIMARY KEY,
    gen_key     TEXT NOT NULL,
    params      TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    FOREIGN KEY (gen_key) REFERENCES generators(gen_key)
);
CREATE INDEX IF NOT EXISTS idx_runs_gen_key ON runs(gen_key);
"""


class Store:
    """Unified SQLite store for generator state and key history.

    Parameters
    ----------
    db_path:
        Path to the SQLite database file.  Created automatically.
    """

    def __init__(self, db_path: str | Path = _DEFAULT_DB) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)

    # ── generator state ───────────────────────────────────────────────

    def load_generator_by_key(self, gen_key: str) -> dict | None:
        """Return the stored row for a generator, or ``None``."""
        row = self._conn.execute(
            "SELECT * FROM generators WHERE gen_key = ?", (gen_key,)
        ).fetchone()
        if row is None:
            return None
        d = dict(row)
        d["state_extra"] = json.loads(d["state_extra"])
        return d

    def save_generator_by_key(
        self,
        gen_key: str,
        *,
        cursor: int = 0,
        state_extra: dict | None = None,
    ) -> None:
        """Insert or update a generator row."""
        now = datetime.now(UTC).isoformat()
        extra_json = json.dumps(state_extra or {})

        self._conn.execute(
            """
            INSERT INTO generators
                (gen_key, cursor, state_extra, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(gen_key) DO UPDATE SET
                cursor      = excluded.cursor,
                state_extra = excluded.state_extra,
                updated_at  = excluded.updated_at
            """,
            (gen_key, cursor, extra_json, now, now),
        )
        self._conn.commit()

    def list_generators(self) -> list[dict]:
        """Return all registered generators."""
        rows = self._conn.execute("SELECT * FROM generators ORDER BY gen_key").fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["state_extra"] = json.loads(d["state_extra"])
            result.append(d)
        return result

    # ── key history ───────────────────────────────────────────────────

    def record_run(self, key: Key, gen_key: str) -> None:
        """Record a single generated key."""
        now = datetime.now(UTC).isoformat()
        self._conn.execute(
            "INSERT OR IGNORE INTO runs (key_id, gen_key, params, created_at) VALUES (?, ?, ?, ?)",
            (key.id, gen_key, json.dumps(key.to_dict(), default=str), now),
        )
        self._conn.commit()

    def record_runs(self, keys: list[Key], gen_key: str) -> None:
        """Record multiple keys in a single transaction."""
        now = datetime.now(UTC).isoformat()
        rows = []
        for key in keys:
            rows.append((key.id, gen_key, json.dumps(key.to_dict(), default=str), now))
        self._conn.executemany(
            "INSERT OR IGNORE INTO runs (key_id, gen_key, params, created_at) VALUES (?, ?, ?, ?)",
            rows,
        )
        self._conn.commit()

    def run_count(self, gen_key: str | None = None) -> int:
        """Total recorded runs, optionally filtered by gen_key."""
        if gen_key is not None:
            row = self._conn.execute(
                "SELECT COUNT(*) FROM runs WHERE gen_key = ?", (gen_key,)
            ).fetchone()
        else:
            row = self._conn.execute("SELECT COUNT(*) FROM runs").fetchone()
        return row[0]

    def get_run(self, key_id: str) -> dict | None:
        """Look up a single run by key ID."""
        row = self._conn.execute("SELECT * FROM runs WHERE key_id = ?", (key_id,)).fetchone()
        if row is None:
            return None
        return self._run_to_dict(row)

    def recent_runs(self, n: int = 20, gen_key: str | None = None) -> list[dict]:
        """Return the *n* most recent runs."""
        if gen_key is not None:
            rows = self._conn.execute(
                "SELECT * FROM runs WHERE gen_key = ? ORDER BY created_at DESC LIMIT ?",
                (gen_key, n),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM runs ORDER BY created_at DESC LIMIT ?", (n,)
            ).fetchall()
        return [self._run_to_dict(r) for r in rows]

    def all_params(self, gen_key: str | None = None) -> list[dict]:
        """Return all stored param dicts, for similarity comparisons."""
        if gen_key is not None:
            rows = self._conn.execute(
                "SELECT key_id, gen_key, params FROM runs WHERE gen_key = ?",
                (gen_key,),
            ).fetchall()
        else:
            rows = self._conn.execute("SELECT key_id, gen_key, params FROM runs").fetchall()
        return [
            {
                "key_id": r["key_id"],
                "gen_key": r["gen_key"],
                "params": json.loads(r["params"]),
            }
            for r in rows
        ]

    def load_seen_fingerprints(self, gen_key: str) -> set[str]:
        """Return the set of canonical param-fingerprints for *gen_key*.

        Used by generators to initialise their dedup seen-set on resume.
        """
        rows = self._conn.execute(
            "SELECT params FROM runs WHERE gen_key = ?", (gen_key,)
        ).fetchall()
        return {json.dumps(json.loads(r["params"]), sort_keys=True) for r in rows}

    # ── housekeeping ──────────────────────────────────────────────────

    def close(self) -> None:
        """Close the underlying SQLite connection."""
        self._conn.close()

    def __enter__(self) -> Store:
        """Enter the context manager, returning the store."""
        return self

    def __exit__(self, *exc: object) -> None:
        """Close the connection on context exit."""
        self.close()

    @staticmethod
    def _run_to_dict(row: sqlite3.Row) -> dict:
        """Convert a ``runs`` row to a plain dict, deserializing params."""
        d = dict(row)
        d["params"] = json.loads(d["params"])
        return d
