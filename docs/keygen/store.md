> SQLite persistence for generator state and key history.

---

## `Store`

Unified SQLite store for generator state and key history.

**Parameters**

| Name | Description |
|---|---|
| `db_path` | Path to the SQLite database file. Created automatically. |

---

### `load_generator_by_key(gen_key: str) → dict | None`

Return the stored row for a generator, or None.

---

### `save_generator_by_key(gen_key: str, cursor: int = 0, state_extra: dict | None = None) → None`

Insert or update a generator row.

**Parameters**

| Name | Description |
|---|---|
| `gen_key` | Unique key for the generator. |
| `cursor` | Cursor position for the generator. Defaults to 0. |
| `state_extra` | Additional state information for the generator. |

---

### `list_generators() → list[dict]`

Return all registered generators.

---

### `record_run(key: Key, gen_key: str) → None`

Record a single generated key.

**Parameters**

| Name | Description |
|---|---|
| `key` | The generated key to record. |
| `gen_key` | The key of the generator that produced the key. |

---

### `record_runs(keys: list[Key], gen_key: str) → None`

Record multiple keys in a single transaction.

**Parameters**

| Name | Description |
|---|---|
| `keys` | List of generated keys to record. |
| `gen_key` | The key of the generator that produced the keys. |

---

### `run_count(gen_key: str | None = None) → int`

Total recorded runs, optionally filtered by gen_key.

**Parameters**

| Name | Description |
|---|---|
| `gen_key` | The key of the generator to filter runs by. |

**Returns**

`int` — The total number of recorded runs.

---

### `get_run(key_id: str) → dict | None`

Look up a single run by key ID.

**Parameters**

| Name | Description |
|---|---|
| `key_id` | The ID of the key to look up. |

**Returns**

`dict or None` — The run data as a dictionary, or None if not found.

---

### `recent_runs(n: int = 20, gen_key: str | None = None) → list[dict]`

Return the n most recent runs.

**Parameters**

| Name | Description |
|---|---|
| `n` | The number of recent runs to return. Defaults to 20. |
| `gen_key` | The key of the generator to filter runs by. |

**Returns**

`list[dict]` — A list of the most recent runs as dictionaries.

---

### `all_params(gen_key: str | None = None) → list[dict]`

Return all stored param dicts, for similarity comparisons.

**Parameters**

| Name | Description |
|---|---|
| `gen_key` | The key of the generator to filter runs by. |

**Returns**

`list[dict]` — A list of parameter dictionaries for the stored runs.

---

### `load_seen_fingerprints(gen_key: str) → set[str]`

Return the set of canonical param-fingerprints for gen_key.

This is used by generators to initialise their dedup seen-set on resume.

**Parameters**

| Name | Description |
|---|---|
| `gen_key` | The key of the generator to load fingerprints for. |

**Returns**

`set[str]` — A set of canonical parameter fingerprints.

---

### `close() → None`

Close the underlying SQLite connection.
