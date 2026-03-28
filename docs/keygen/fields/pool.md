> Categorical field whose options are supplied once at runtime.

---

## `Pool`

Categorical field whose options are supplied at runtime.

Unlike `Enum`, whose choices are fixed in the class body,
a `Pool` starts empty and is filled exactly once before
generation begins. After `populate`, the option set is
frozen.

Handy for resources discovered at startup::

    class Sampler(Key):
        sample = Pool()
        pitch  = Param(min=-12, max=12)

    # Before generating, populate the sample with wav files
    wav_files = sorted(Path("./samples").glob("*.wav"))
    Sampler.sample.populate(wav_files)

Sized, indexable, and iterable once populated.

**Parameters**

| Name | Description |
|---|---|
| `None` |  |

**Raises**

| Exception | When |
|---|---|
| `None` |  |

### `is_populated`

Whether `populate` has been called.

### `options`

The frozen option set (raises if not yet populated).

---

### `populate(items: Iterable[Any]) → None`

Set the option list. Can only be called once.

**Parameters**

| Name | Description |
|---|---|
| `items` | An iterable of items to populate the pool with. |

**Raises**

| Exception | When |
|---|---|
| `RuntimeError` | When the pool has already been populated. |
| `ValueError` | When attempting to populate with an empty collection. |

---

### `validate(value: Any) → None`

Raise `RuntimeError` if unpopulated, or `ValueError` if *value* is not in the pool.

**Parameters**

| Name | Description |
|---|---|
| `value` | The value to validate against the pool. |

**Raises**

| Exception | When |
|---|---|
| `RuntimeError` | When the pool has not yet been populated. |
| `ValueError` | When the value is not in the pool. |
