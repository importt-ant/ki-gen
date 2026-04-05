"""Low-discrepancy quasi-random engine using Sobol sequences."""

from __future__ import annotations

from typing import Any


class SobolRengine:
    """RNG engine backed by a Sobol quasi-random sequence.

    Implements the :class:`~keygen.rengines.Rengine` protocol.
    Each ``randint``, ``uniform``, ``choice``, and ``sample`` call
    consumes the next Sobol dimension, wrapping around when
    dimensions are exhausted.

    Supports *O(1)* ``fast_forward`` via the underlying scipy
    engine, so resuming a generator does not require replaying
    previous draws.

    Requires ``scipy`` (optional dependency).

    Parameters
    ----------
    seed : int | None, optional
        Seed forwarded to the underlying Sobol engine.
    dimensions : int
        Number of Sobol dimensions per point (should be >= the number
        of draws per ``_randomize`` call).
    """

    def __init__(self, seed: int | None = None, dimensions: int = 32) -> None:
        from scipy.stats.qmc import Sobol  # lazy — optional dependency

        self._seed = seed
        self._dimensions = dimensions
        self._engine = Sobol(d=dimensions, seed=seed)
        self._point: list[float] = []
        self._dim_idx: int = 0
        self._advance()  # Prime the first point

    @property
    def seed(self) -> int | None:
        """The seed this engine was initialized with, or ``None``."""
        return self._seed

    # ── Point management ────────────────────────────────────────────

    def _advance(self) -> None:
        """Move to the next Sobol point and reset the dimension cursor."""
        self._point = self._engine.random(1)[0].tolist()
        self._dim_idx = 0

    def fast_forward(self, steps: int) -> None:
        """Skip *steps* Sobol points in *O(1)*."""
        self._engine.fast_forward(steps)
        self._advance()

    # ── Rengine interface ───────────────────────────────────────────

    def _next_uniform(self) -> float:
        """Return the next [0, 1) value, cycling through dimensions."""
        u = self._point[self._dim_idx % self._dimensions]
        self._dim_idx += 1
        return u

    def randint(self, a: int, b: int) -> int:
        """Return a random integer in [a, b] inclusive.

        Parameters
        ----------
        a : int
            Lower bound of the random integer.
        b : int
            Upper bound of the random integer.

        Returns
        -------
        int
            A random integer in the range [a, b].
        """
        return a + int(self._next_uniform() * (b - a + 1)) % (b - a + 1)

    def uniform(self, a: float, b: float) -> float:
        """Return a random float in [a, b).

        Parameters
        ----------
        a : float
            Lower bound of the random float.
        b : float
            Upper bound of the random float.

        Returns
        -------
        float
            A random float in the range [a, b).
        """
        return a + self._next_uniform() * (b - a)

    def choice(self, seq: list[Any] | tuple[Any, ...]) -> Any:
        """Pick one element uniformly from *seq*.

        Parameters
        ----------
        seq : list[Any] | tuple[Any, ...]
            The sequence from which to pick an element.

        Returns
        -------
        Any
            A randomly selected element from the sequence.
        """
        idx = int(self._next_uniform() * len(seq)) % len(seq)
        return seq[idx]

    def sample(self, population: list[Any], k: int) -> list[Any]:
        """Choose *k* unique elements (Fisher-Yates via Sobol draws).

        Parameters
        ----------
        population : list[Any]
            The population from which to sample.
        k : int
            The number of unique elements to choose.

        Returns
        -------
        list[Any]
            A list of *k* unique elements sampled from the population.
        """
        pool = list(population)
        n = len(pool)
        result: list[Any] = []
        for i in range(min(k, n)):
            j = i + int(self._next_uniform() * (n - i)) % (n - i)
            pool[i], pool[j] = pool[j], pool[i]
            result.append(pool[i])
        return result

    def __repr__(self) -> str:
        return f"SobolRengine(seed={self._seed}, dimensions={self._dimensions})"