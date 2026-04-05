> Low-discrepancy quasi-random engine using Sobol sequences.

---

## `SobolRengine`

RNG engine backed by a Sobol quasi-random sequence.

Implements the `~keygen.rengines.Rengine` protocol.
Each `randint`, `uniform`, `choice`, and `sample` call
consumes the next Sobol dimension, wrapping around when
dimensions are exhausted.

Supports *O(1)* `fast_forward` via the underlying scipy
engine, so resuming a generator does not require replaying
previous draws.

Requires `scipy` (optional dependency).

**Parameters**

| Name | Description |
|---|---|
| `seed` | Seed forwarded to the underlying Sobol engine. |
| `dimensions` | Number of Sobol dimensions per point (should be >= the number of draws per `_randomize` call). |

### `seed`

The seed this engine was initialized with, or `None`.

---

### `fast_forward(steps: int) → None`

Skip *steps* Sobol points in *O(1)*.

---

### `randint(a: int, b: int) → int`

Random integer in [a, b] inclusive.

---

### `uniform(a: float, b: float) → float`

Random float in [a, b).

---

### `choice(seq: list[Any] | tuple[Any, ...]) → Any`

Pick one element uniformly from *seq*.

---

### `sample(population: list[Any], k: int) → list[Any]`

Choose *k* unique elements (Fisher-Yates via Sobol draws).
