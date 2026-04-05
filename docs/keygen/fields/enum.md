> Categorical field with a fixed set of allowed values.

---

## `Enum`

Categorical field with a fixed set of allowed values.

**Example**

```python
class DrumKit(Key):
    hit = Enum("kick", "snare", "hihat", "clap")
```Sized, indexable, and iterable::

    len(DrumKit.hit)             # 4
    DrumKit.hit[0]               # "kick"
    rng.choice(DrumKit.hit)      # picks one at random
    DrumKit.hit.options          # ("kick", "snare", "hihat", "clap")

**Parameters**

| Name | Description |
|---|---|
| `*options` | One or more allowed values. At least one is required. |

**Raises**

| Exception | When |
|---|---|
| `TypeError` | When no options are provided. |

---

### `validate(value: Any) → None`

Raise `ValueError` if *value* is not one of the allowed options.
