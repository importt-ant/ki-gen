"""kgen -- seeded parameter generation with deduplication and persistence.

Define a :class:`Key` subclass to describe your parameter space, wrap it
in a :class:`Blueprint` to control randomization, and hand it to a
:class:`Generator` to produce unique configurations::

    from kgen import Key, Blueprint, Store, Param, Enum, Generator

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

# fields
from .fields import Enum, Field, Param, Pool
from .key import Key

# recorders
from .recorders import Generator, Recorder, SpaceExhaustedError

# rengines
from .rengines import (
    FastForwardNotSupported,
    RandomRengine,
    Rengine,
    SobolRengine,
)
from .store import Store

__all__ = [
    # modules
    "fields",
    "recorders",
    "rengines",
    # core
    "Blueprint",
    "Key",
    "Store",
    # fields
    "Enum",
    "Field",
    "Param",
    "Pool",
    # recorders
    "Generator",
    "Recorder",
    "SpaceExhaustedError",
    # rengines
    "FastForwardNotSupported",
    "RandomRengine",
    "Rengine",
    "SobolRengine",
]

__version__ = "1.0.0"
