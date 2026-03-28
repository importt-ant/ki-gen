"""keygen -- seeded parameter generation with deduplication and persistence.

Define a :class:`Key` subclass to describe your parameter space, wrap it
in a :class:`Blueprint` to control randomization, and hand it to a
:meth:`~keygen.recorders.Generator` to produce unique configurations::

    from keygen import Key, Blueprint, Store
    from keygen.fields import Param, Enum
    from keygen.recorders import Generator

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
    Field descriptors (:class:`~keygen.fields.Param`,
    :class:`~keygen.fields.Enum`, :class:`~keygen.fields.Pool`).
recorders
    :class:`~keygen.recorders.Recorder` for deduplication and
    :class:`~keygen.recorders.Generator` for the full generation loop.
rengines
    Pluggable RNG backends (:class:`~keygen.rengines.RandomRengine`,
    :class:`~keygen.rengines.SobolRengine`).
"""

from . import fields, recorders, rengines
from .blueprint import Blueprint
from .key import Key
from .store import Store

__all__ = [
    "fields",
    "recorders",
    "rengines",
    "Blueprint",
    "Key",
    "Store",
]
