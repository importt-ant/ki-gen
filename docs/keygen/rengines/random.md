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

Return a random integer in `[a, b]` inclusive.

**Parameters**

| Name | Description |
|---|---|
| `a` | Lower bound of the random integer. |
| `b` | Upper bound of the random integer. |

**Returns**

`int` — A random integer in the range `[a, b]`.

---

### `uniform(a: float, b: float) → float`

Return a random float in `[a, b)`.

**Parameters**

| Name | Description |
|---|---|
| `a` | Lower bound of the random float. |
| `b` | Upper bound of the random float. |

**Returns**

`float` — A random float in the range `[a, b)`.

---

### `choice(seq: list[Any] | tuple[Any, ...]) → Any`

Pick one element from *seq* uniformly at random.

**Parameters**

| Name | Description |
|---|---|
| `seq` | The sequence from which to pick an element. |

**Returns**

`Any` — A randomly selected element from the sequence.

---

### `sample(population: list[Any], k: int) → list[Any]`

Choose *k* unique elements from *population*.

**Parameters**

| Name | Description |
|---|---|
| `population` | The population to sample from. |
| `k` | The number of unique elements to choose. |

**Returns**

`list[Any]` — A list of *k* unique elements from the population.

---

### `fast_forward(steps: int) → None`

Not supported — raises `FastForwardNotSupported`.

**Parameters**

| Name | Description |
|---|---|
| `steps` | The number of steps to fast forward. |

**Raises**

| Exception | When |
|---|---|
| `FastForwardNotSupported` | When fast-forwarding is not supported. |
