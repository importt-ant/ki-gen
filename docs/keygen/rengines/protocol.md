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

Return a random integer in [a, b] inclusive.

**Parameters**

| Name | Description |
|---|---|
| `a` | Lower bound of the random integer. |
| `b` | Upper bound of the random integer. |

**Returns**

`int` — A random integer in the specified range.

---

### `uniform(a: float, b: float) → float`

Return a random float in [a, b).

**Parameters**

| Name | Description |
|---|---|
| `a` | Lower bound of the random float. |
| `b` | Upper bound of the random float. |

**Returns**

`float` — A random float in the specified range.

---

### `choice(seq: list[Any] | tuple[Any, ...]) → Any`

Pick and return one element from *seq*.

**Parameters**

| Name | Description |
|---|---|
| `seq` | A sequence from which to pick an element. |

**Returns**

`Any` — A randomly selected element from the sequence.

---

### `sample(population: list[Any], k: int) → list[Any]`

Choose and return *k* unique elements from *population*.

**Parameters**

| Name | Description |
|---|---|
| `population` | The population from which to sample. |
| `k` | The number of unique elements to choose. |

**Returns**

`list[Any]` — A list of *k* unique elements sampled from the population.

---

### `fast_forward(steps: int) → None`

Skip ahead by *steps* generation cycles.

This is for engines that support O(1) skipping, such as Sobol.
Other engines can implement this as a no-op or a loop.

**Parameters**

| Name | Description |
|---|---|
| `steps` | The number of generation cycles to skip. |
