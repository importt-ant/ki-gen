> Numeric field with optional min, max, and step bounds.

---

## `Param`

Numeric field with optional min, max, and step constraints.

::

    class Oscillator(Key):
        frequency = Param(min=20, max=20000)
        detune    = Param(min=-100, max=100, step=1)

Bounds are accessible on the class::

    Oscillator.frequency.min  # 20
    Oscillator.frequency.max  # 20000

**Parameters**

| Name | Description |
|---|---|
| `min` | Lower bound (inclusive).  `None` means unbounded below. |
| `max` | Upper bound (inclusive).  `None` means unbounded above. |
| `step` | If set, values must land on `min + n * step`. |

---

### `validate(value: Any) → None`

Raise `ValueError` if *value* violates the min/max/step constraints.
