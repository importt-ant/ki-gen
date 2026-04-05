> Base descriptor for validated Key fields.

---

## `Field`

Base descriptor for `~keygen.Key` fields.

Subclass this to create custom field types. Implement
`validate` to raise `ValueError` on bad input.
Validation runs automatically on every assignment to a Key
instance.

**Example**

```python
class MidiNote(Field):
    def validate(self, value: Any) -> None:
        if not isinstance(value, int) or not (0 <= value <= 127):
            raise ValueError(f"{self._attr}: expected MIDI note 0–127, got {value!r}")
```

**Parameters**

| Name | Description |
|---|---|
| `None` |  |

**Raises**

| Exception | When |
|---|---|
| `None` |  |

---

### `validate(value: Any) → None`

Raise `ValueError` if *value* is not acceptable.
