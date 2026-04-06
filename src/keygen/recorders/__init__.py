"""Recording, deduplication, and generation machinery."""

from .generator import Generator
from .recorder import Recorder, SpaceExhaustedError

__all__ = [
    # classes
    "Recorder",
    "Generator",
    # errors
    "SpaceExhaustedError",
]
