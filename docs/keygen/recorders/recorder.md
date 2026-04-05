> Deduplication and persistence layer for generated keys.

---

## `SpaceExhaustedError`

Raised when a generator hits too many consecutive duplicate skips.

---

## `Recorder`

Deduplication and persistence layer for keys.

Works standalone as a recorder when keys come from an external
source::

    recorder = Recorder(name="session-1", store=my_store)
    key = SynthPatch(pitch=440, velocity=100, attack=0.1, waveform="saw")
    accepted = recorder.record(key)

Or subclass it to add a generation strategy: see
`Generator` for the built-in RNG approach.

**Parameters**

| Name | Description |
|---|---|
| `name` | Human-readable label used to build `gen_key`.  Required when instantiating `Recorder` directly; subclasses may override the `name` property instead. |
| `store` | `Store` for persistence and dedup state. `None` gives an in-memory-only recorder. |
| `flush_interval` | Number of `record` calls between automatic flushes. |

### `name`

Human-readable generator name (used in gen_key).

### `gen_type`

Strategy label stored alongside the name in gen_key.

### `gen_key`

Unique identifier for this recorder (`name:gen_type`).

### `cursor`

Number of keys accepted so far.

---

### `flush() → None`

Force-write pending keys to the store.

---

### `record(key: Key) → bool`

Record a key, deduplicating and persisting automatically.

**Parameters**

| Name | Description |
|---|---|
| `key` | The `Key` instance to record. |

**Returns**

`bool` — `True` if the key was new and accepted, `False` if it was a duplicate.
