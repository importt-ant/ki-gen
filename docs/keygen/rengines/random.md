> Pseudo-random engine backed by stdlib `random.Random`.

---

## `RandomRengine`

Standard pseudo-random engine backed by `random.Random`.

**Parameters**

| Name | Description |
|---|---|
| `seed` | Optional seed for reproducibility. |

### `seed`

The seed this engine was initialized with, or `None`.

---

### `randint(a: int, b: int) → int`

Random integer in `[a, b]` inclusive.

---

### `uniform(a: float, b: float) → float`

Random float in `[a, b)`.

---

### `choice(seq: list[Any] | tuple[Any, ...]) → Any`

Pick one element from *seq* uniformly at random.

---

### `sample(population: list[Any], k: int) → list[Any]`

Choose *k* unique elements from *population*.

---

### `fast_forward(steps: int) → None`

Not supported — raises `FastForwardNotSupported`.
