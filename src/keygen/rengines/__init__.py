from __future__ import annotations


class Rengine:
    """Base class for random engine implementations."""

    pass


class RandomRengine(Rengine):
    """Random number generator engine using a standard library."""

    pass


class SobolRengine(Rengine):
    """Quasi-random number generator engine based on Sobol sequences."""

    pass
