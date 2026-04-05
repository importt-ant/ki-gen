> Generation loop with dedup, seed+cursor resume, and blueprint delegation.

---

## `Generator`

Generator that produces `Key` instances via a `Rengine`.

Owns the generate/dedup loop and handles seed+cursor resume.
Field randomization is delegated to a `Blueprint`, which
describes *how* each field is produced (random within bounds,
pinned to a constant, etc.).

The engine is pluggable — pass any `Rengine` via the
*rengine* parameter, or omit it to get a `RandomRengine`
seeded with *seed*.

**Parameters**

| Name | Description |
|---|---|
| `blueprint` | A `Blueprint` that knows which Key subclass to build and how each field should be randomized or pinned. |
| `seed` | Seed forwarded to the default `RandomRengine` when no explicit engine is given.  Ignored if *rengine* is set. |
| `rengine` | A pre-built `Rengine`.  Takes priority over *seed*. |
| `store` | Optional `Store` for persistence and dedup. |
| `flush_interval` | Auto-flush cadence (inherited from `Recorder`). |
| `max_consecutive_skips` | Dedup skip limit before `_on_space_exhausted` fires. |

### `name`

Derived from the blueprint's Key subclass name.

### `blueprint`

The blueprint driving field randomization.

### `seed`

Seed passed at construction, or `None`.

### `rng`

The active RNG engine.

### `gen_type`

Class name of the underlying `Rengine`.

### `gen_key`

Unique identifier: `name:engine_type:seed`.

---

### `generate() → Key | None`

Produce a single deduplicated key.

Retries internally when a duplicate is drawn, up to
*max_consecutive_skips* times.

**Returns**

`Key or None` — The accepted key, or `None` when `_on_space_exhausted` is overridden to not raise.

---

### `generate_many(n: int) → list[Key]`

Generate up to *n* deduplicated keys.

**Parameters**

| Name | Description |
|---|---|
| `n` | Maximum number of keys to produce. |

**Returns**

`list[Key]` — The accepted keys.  May be shorter than *n* if `_on_space_exhausted` swallows the error.
