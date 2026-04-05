> Field randomization plan for building Key instances.

---

## `Blueprint`

Describes how each field of a Key subclass should be randomized.

Starts with the Key's own field specs as defaults.  Use
`configure` to narrow bounds, restrict choices, or pin
a field to a constant::

    bp = (
        Blueprint(SynthPatch)
        .configure("pitch", Param(min=200, max=4000))
        .configure("waveform", Enum("sine", "saw"))
    )

Call `build` with an RNG engine to produce a Key.
Blueprints are engine-agnostic and reusable.

**Parameters**

| Name | Description |
|---|---|
| `key_type` | The `Key` subclass whose fields will be randomized. |

### `key_type`

The Key subclass this blueprint targets.

### `overrides`

Current field overrides (read-only copy).

---

### `configure(field_name: str, spec: Field | Any) → Blueprint`

Set how a field is produced.

**Parameters**

| Name | Description |
|---|---|
| `field_name` | Name of a field declared on the Key subclass. |
| `spec` | A `Field` descriptor (e.g. `Param(min=1000, max=2000)`) to override randomization bounds, or a plain value to pin the field to a static constant. |

**Returns**

`Blueprint` — For method chaining.

**Raises**

| Exception | When |
|---|---|
| `ValueError` | If *field_name* does not exist on the Key subclass. |

---

### `effective_spec(field_name: str) → Field | Any`

Return the active spec for *field_name*.

Returns the override if one was set via `configure`,
otherwise the default spec declared on the Key subclass.

**Parameters**

| Name | Description |
|---|---|
| `field_name` | Name of a field declared on the Key subclass. |

**Raises**

| Exception | When |
|---|---|
| `ValueError` | If *field_name* does not exist on the Key subclass. |

---

### `build(rng: Any) → Key`

Produce a Key instance using *rng* for randomization.

**Parameters**

| Name | Description |
|---|---|
| `rng` | Any object satisfying the `Rengine` protocol (`randint`, `uniform`, `choice`, etc.). |
| `Static` |  |
| `overrides` |  |

**Returns**

`Key` — The constructed key with all fields populated.
