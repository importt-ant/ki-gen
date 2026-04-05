> categorical field with a fixed set of allowed values.

---

## `Enum`

categorical field with a fixed set of allowed values.

example::

    class DrumKit(Key):
        hit = Enum("kick", "snare", "hihat", "clap")

sized, indexable, and iterable::

    len(DrumKit.hit)             # 4
    DrumKit.hit[0]               # "kick"
    rng.choice(DrumKit.hit)      # picks one at random
    DrumKit.hit.options          # ("kick", "snare", "hihat", "clap")

**Parameters**

| Name | Description |
|---|---|
| `*options` | one or more allowed values; at least one is required. |

**Raises**

| Exception | When |
|---|---|
| `TypeError` | when no options are provided. |

---

### `validate(value: Any) → None`

raise `ValueError` if *value* is not one of the allowed options.
