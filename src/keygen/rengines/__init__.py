from __future__ import annotations


class Rengine:
    """Base class for random engine implementations."""

    pass


class RandomRengine(Rengine):
    """Random number generator using a standard random engine."""

    pass


class SobolRengine(Rengine):
    """Random number generator using sobol sequences."""

    pass
