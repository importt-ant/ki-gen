"""Recording, deduplication, and generation machinery."""

from .recorder import Recorder, SpaceExhaustedError
from .generator import Generator

__all__ = [
    # classes
    "Recorder",
    "Generator",
    
    # errors
    "SpaceExhaustedError",
]
