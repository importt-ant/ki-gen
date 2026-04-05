"""keygen -- seeded parameter generation with deduplication and persistence.

Define a :class:`Key` subclass to describe your parameter space, wrap it
in a :class:`Blueprint` to control randomization, and hand it to a
:meth:`Generator` to produce unique configurations::

    from keygen import Key, Blueprint, Store, Param, Enum, Generator

    class SynthPatch(Key):
        pitch    = Param(min=20, max=20000)
        velocity = Param(min=0, max=127)
        waveform = Enum("sine", "saw", "square", "triangle")

    bp  = Blueprint(SynthPatch)
    gen = Generator(bp, seed=42, store=Store("patches.db"))
    patches = gen.generate_many(10)

Subpackages
-----------
fields
    Field descriptors (:class:`Param`, :class:`Enum`,
    :class:`Pool`, :class:`Field`).
recorders
    :class:`Recorder` for dedup/persistence and
    :class:`Generator` for the full generation loop.
rengines
    Pluggable RNG backends (:class:`RandomRengine`,
    :class:`SobolRengine`).
"""

from . import fields, recorders, rengines
from .blueprint import Blueprint

# Fields
from .fields import Enum, Field, Param, Pool
from .key import Key

# Recorders
from .recorders import Generator, Recorder, SpaceExhaustedError

# Rengines
from .rengines import (
    FastForwardNotSupported,
    RandomRengine,
    Rengine,
    SobolRengine,
)
from .store import Store

__all__ = [
    # Modules
    "fields",
    "recorders",
    "rengines",
    # Core
    "Blueprint",
    "Key",
    "Store",
    # Fields
    "Enum",
    "Field",
    "Param",
    "Pool",
    # Recorders
    "Generator",
    "Recorder",
    "SpaceExhaustedError",
    # Rengines
    "FastForwardNotSupported",
    "RandomRengine",
    "Rengine",
    "SobolRengine",
]
