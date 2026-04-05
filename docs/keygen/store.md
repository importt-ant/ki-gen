> SQLite persistence for generator state and key history.

---

## `Store`

Unified SQLite store for generator state and key history.

**Parameters**

| Name | Description |
|---|---|
| `db_path` | Path to the SQLite database file.  Created automatically. |

---

### `load_generator_by_key(gen_key: str) → dict | None`

Return the stored row for a generator, or `None`.

---

### `save_generator_by_key(gen_key: str, cursor: int = 0, state_extra: dict | None = None) → None`

Insert or update a generator row.

---

### `list_generators() → list[dict]`

Return all registered generators.

---

### `record_run(key: Key, gen_key: str) → None`

Record a single generated key.

---

### `record_runs(keys: list[Key], gen_key: str) → None`

Record multiple keys in a single transaction.

---

### `run_count(gen_key: str | None = None) → int`

Total recorded runs, optionally filtered by gen_key.

---

### `get_run(key_id: str) → dict | None`

Look up a single run by key ID.

---

### `recent_runs(n: int = 20, gen_key: str | None = None) → list[dict]`

Return the *n* most recent runs.

---

### `all_params(gen_key: str | None = None) → list[dict]`

Return all stored param dicts, for similarity comparisons.

---

### `load_seen_fingerprints(gen_key: str) → set[str]`

Return the set of canonical param-fingerprints for *gen_key*.

Used by generators to initialise their dedup seen-set on resume.

---

### `close() → None`

Close the underlying SQLite connection.
