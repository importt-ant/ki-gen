> Categorical field whose options are supplied once at runtime.

---

## `Pool`

Categorical field whose options are supplied at runtime.

Unlike `Enum`, whose choices are fixed in the class body,
a `Pool` starts empty and is filled exactly once before
generation begins.  After `populate` the option set is
frozen.

Handy for resources discovered at startup::

    class Sampler(Key):
        sample = Pool()
        pitch  = Param(min=-12, max=12)

    # before generating:
    wav_files = sorted(Path("./samples").glob("*.wav"))
    Sampler.sample.populate(wav_files)

Sized, indexable, and iterable once populated.

### `populated`

Whether `populate` has been called.

### `options`

The frozen option set (raises if not yet populated).

---

### `populate(items: Iterable[Any]) → None`

Set the option list.  Can only be called once.

---

### `validate(value: Any) → None`

Raise `RuntimeError` if unpopulated, or `ValueError` if *value* is not in the pool.
