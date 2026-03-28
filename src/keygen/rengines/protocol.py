"""Minimal interface that all RNG engines must satisfy."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


class FastForwardNotSupported(Exception):
    """Raised when a rengine does not support O(1) fast-forward."""


@runtime_checkable
class Rengine(Protocol):
    """Minimal interface every RNG engine must satisfy.

    Engines produce uniformly-distributed primitives that blueprints
    use to randomize field values.

    Built-in implementations: :class:`RandomRengine` (stdlib),
    :class:`SobolRengine` (scipy).
    """

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
            A random integer in the specified range.
        """
        ...

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
            A random float in the specified range.
        """
        ...

    def choice(self, seq: list[Any] | tuple[Any, ...]) -> Any:
        """Pick and return one element from *seq*.

        Parameters
        ----------
        seq : list[Any] | tuple[Any, ...]
            A sequence from which to pick an element.

        Returns
        -------
        Any
            A randomly selected element from the sequence.
        """
        ...

    def sample(self, population: list[Any], k: int) -> list[Any]:
        """Choose and return *k* unique elements from *population*.

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
        ...

    def fast_forward(self, steps: int) -> None:
        """Skip ahead by *steps* generation cycles.

        This is for engines that support O(1) skipping, such as Sobol.
        Other engines can implement this as a no-op or a loop.

        Parameters
        ----------
        steps : int
            The number of generation cycles to skip.
        """
        ...
