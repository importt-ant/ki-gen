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

    Built-in implementations: :class:`RandomRengine` (stdlib);
    :class:`SobolRengine` (scipy).
    """

    def randint(self, a: int, b: int) -> int:
        """Return a random integer in [a, b] inclusive."""
        ...

    def uniform(self, a: float, b: float) -> float:
        """Return a random float in [a, b)."""
        ...

    def choice(self, seq: list[Any] | tuple[Any, ...]) -> Any:
        """Return one element from *seq*."""
        ...

    def sample(self, population: list[Any], k: int) -> list[Any]:
        """Return *k* unique elements from *population*."""
        ...

    def fast_forward(self, steps: int) -> None:
        """Skip ahead by *steps* generation cycles; for engines that support O(1) skipping, others can implement this as a no-op or a loop."""
        ...
