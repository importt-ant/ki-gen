> categorical field whose options are supplied once at runtime.

---

## `Pool`

categorical field whose options are supplied at runtime.

unlike `Enum`, whose choices are fixed in the class body,
a `Pool` starts empty and is filled exactly once before
generation begins; after `populate`, the option set is
frozen.

handy for resources discovered at startup::

    class Sampler(Key):
        sample = Pool()
        pitch  = Param(min=-12, max=12)

    # before generating:
    wav_files = sorted(Path("./samples").glob("*.wav"))
    Sampler.sample.populate(wav_files)

sized, indexable, and iterable once populated.

### `is_populated`

whether `populate` has been called.

### `options`

the frozen option set; raises if not yet populated.

---

### `populate(items: Iterable[Any]) → None`

set the option list; can only be called once.

**Parameters**

| Name | Description |
|---|---|
| `items` | an iterable of items to populate the pool with. |

**Raises**

| Exception | When |
|---|---|
| `RuntimeError` | when the pool has already been populated. |
| `ValueError` | when attempting to populate with an empty collection. |

---

### `validate(value: Any) → None`

raise `RuntimeError` if unpopulated; raise `ValueError` if *value* is not in the pool.

**Parameters**

| Name | Description |
|---|---|
| `value` | the value to validate against the pool options. |

**Raises**

| Exception | When |
|---|---|
| `RuntimeError` | when the pool has not yet been populated. |
| `ValueError` | when the value is not in the pool. |
