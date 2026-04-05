"""Pseudo-random engine backed by stdlib :class:`random.Random`."""

from __future__ import annotations

import random
from typing import Any

from keygen.rengines.protocol import FastForwardNotSupported


class RandomRengine:
    """Standard pseudo-random engine backed by :class:`random.Random`.

    Parameters
    ----------
    seed : int, optional
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
        """Return a random integer in ``[a, b]`` inclusive.

        Parameters
        ----------
        a : int
            Lower bound of the random integer.
        b : int
            Upper bound of the random integer.

        Returns
        -------
        int
            A random integer in the range ``[a, b]``.
        """
        return self._rng.randint(a, b)

    def uniform(self, a: float, b: float) -> float:
        """Return a random float in ``[a, b)``.

        Parameters
        ----------
        a : float
            Lower bound of the random float.
        b : float
            Upper bound of the random float.

        Returns
        -------
        float
            A random float in the range ``[a, b)``.
        """
        return self._rng.uniform(a, b)

    def choice(self, seq: list[Any] | tuple[Any, ...]) -> Any:
        """Pick one element from *seq* uniformly at random.

        Parameters
        ----------
        seq : list[Any] | tuple[Any, ...]
            The sequence from which to pick an element.

        Returns
        -------
        Any
            A randomly selected element from the sequence.
        """
        return self._rng.choice(seq)

    def sample(self, population: list[Any], k: int) -> list[Any]:
        """Choose *k* unique elements from *population*.

        Parameters
        ----------
        population : list[Any]
            The population to sample from.
        k : int
            The number of unique elements to choose.

        Returns
        -------
        list[Any]
            A list of *k* unique elements from the population.
        """
        return self._rng.sample(population, k)

    def fast_forward(self, steps: int) -> None:
        """Not supported — raises :exc:`FastForwardNotSupported`.

        Parameters
        ----------
        steps : int
            The number of steps to fast forward.

        Raises
        ------
        FastForwardNotSupported
            When fast-forwarding is not supported.
        """
        raise FastForwardNotSupported(
            "RandomRengine does not support O(1) fast-forward"
        )

    def __repr__(self) -> str:
        return f"RandomRengine(seed={self._seed})"