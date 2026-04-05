"""Pseudo-random engine backed by stdlib :class:`random.Random`."""

from __future__ import annotations

import random
from typing import Any

from keygen.rengines.protocol import FastForwardNotSupported


class RandomRengine:
    """Standard pseudo-random engine backed by :class:`random.Random`.

    Parameters
    ----------
    seed:
        Optional seed for reproducibility.
    """

    def __init__(self, seed: int | None = None) -> None:
        self._seed = seed
        self._rng = random.Random(seed)

    @property
    def seed(self) -> int | None:
        """The seed this engine was initialized with, or ``None``."""
        return self._seed

    def randint(self, a: int, b: int) -> int:
        """Random integer in ``[a, b]`` inclusive."""
        return self._rng.randint(a, b)

    def uniform(self, a: float, b: float) -> float:
        """Random float in ``[a, b)``."""
        return self._rng.uniform(a, b)

    def choice(self, seq: list[Any] | tuple[Any, ...]) -> Any:
        """Pick one element from *seq* uniformly at random."""
        return self._rng.choice(seq)

    def sample(self, population: list[Any], k: int) -> list[Any]:
        """Choose *k* unique elements from *population*."""
        return self._rng.sample(population, k)

    def fast_forward(self, steps: int) -> None:
        """Not supported — raises :exc:`FastForwardNotSupported`."""
        raise FastForwardNotSupported("RandomRengine does not support O(1) fast-forward")

    def __repr__(self) -> str:
        return f"RandomRengine(seed={self._seed})"
