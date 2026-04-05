> Minimal interface that all RNG engines must satisfy.

---

## `FastForwardNotSupported`

Raised when a rengine does not support O(1) fast-forward.

---

## `Rengine`

Minimal interface every RNG engine must satisfy.

Engines produce uniformly-distributed primitives that blueprints
use to randomize field values.

Built-in implementations: `RandomRengine` (stdlib),
`SobolRengine` (scipy).

---

### `randint(a: int, b: int) → int`

Random integer in [a, b] inclusive.

---

### `uniform(a: float, b: float) → float`

Random float in [a, b).

---

### `choice(seq: list[Any] | tuple[Any, ...]) → Any`

Pick one element from *seq*.

---

### `sample(population: list[Any], k: int) → list[Any]`

Choose *k* unique elements from *population*.

---

### `fast_forward(steps: int) → None`

Skip ahead by *steps* generation cycles.

For engines that support O(1) skipping (e.g. Sobol).
Others can implement this as a no-op or a loop.
