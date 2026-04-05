"""Structured parameter container with auto-validated fields."""

from __future__ import annotations

import json
import uuid
from typing import Any

from keygen.fields import Field


class Key:
    """Structured container for a generated parameter set.

    Subclass and declare fields using :class:`Param` (numeric),
    :class:`Enum` (categorical), or :class:`Pool` (runtime-populated)
    descriptors::

        class SynthPatch(Key):
            pitch     = Param(min=20, max=20000)
            velocity  = Param(min=0, max=127)
            attack    = Param(min=0.01, max=2.0)
            waveform  = Enum("sine", "saw", "square", "triangle")

    Values are validated on assignment; out-of-bounds or invalid
    choices raise :exc:`ValueError`::

        p = SynthPatch(pitch=440, velocity=100, attack=0.1, waveform="saw")
        p.pitch    = -5         # ValueError: pitch: -5 is below minimum 20
        p.waveform = "noise"    # ValueError: waveform: 'noise' is not one of (...)

    Field specs are accessible on the class::

        SynthPatch.pitch.min           # 20
        SynthPatch.pitch.max           # 20000
        SynthPatch.waveform.options    # ("sine", "saw", "square", "triangle")
        len(SynthPatch.waveform)       # 4
    """

    _fields: dict[str, Field]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Collect :class:`Field` descriptors from the class hierarchy."""
        super().__init_subclass__(**kwargs)
        fields: dict[str, Field] = {}
        for base in reversed(cls.__mro__):
            for attr_name, attr_val in vars(base).items():
                if isinstance(attr_val, Field):
                    fields[attr_name] = attr_val
        cls._fields = fields

    def __init__(self, **values: Any) -> None:
        """Create a Key with the given field values.

        Parameters
        ----------
        **values:
            Field names mapped to their values. Every name must
            correspond to a declared :class:`Field` on the class.

        Raises
        ------
        TypeError
            If a name does not match any declared field.
        """
        self._values: dict[str, Any] = {}
        self.id: str = uuid.uuid4().hex[:12]

        missing = set(self._fields) - set(values)
        if missing:
            raise TypeError(
                f"{type(self).__name__} missing required field(s): "
                + ", ".join(sorted(missing))
            )

        for name, value in values.items():
            if name not in self._fields:
                raise TypeError(
                    f"{type(self).__name__} has no field {name!r}"
                )
            setattr(self, name, value)  # triggers validate via __set__

    @classmethod
    def field_specs(cls) -> dict[str, Field]:
        """Return all declared field specifications.

        Returns
        -------
        dict[str, Field]
            A dictionary mapping field names to their specifications.
        """
        return dict(cls._fields)

    def to_dict(self) -> dict[str, Any]:
        """Return field values as a plain dict.

        Returns
        -------
        dict[str, Any]
            A dictionary containing the field values.
        """
        return dict(self._values)

    def fingerprint(self) -> str:
        """Return a canonical string for deduplication.

        Returns
        -------
        str
            A JSON string representation of the field values.
        """
        return json.dumps(self._values, sort_keys=True, default=str)

    def __repr__(self) -> str:
        vals = ", ".join(f"{k}={v!r}" for k, v in self._values.items())
        return f"{type(self).__name__}(id={self.id!r}, {vals})"

    def __eq__(self, other: object) -> bool:
        """Determine equality of two keys based on type and field values.

        Parameters
        ----------
        other : object
            The object to compare against.

        Returns
        -------
        bool
            True if the keys are of the same type and have identical field values,
            False otherwise.
        """
        if not isinstance(other, Key):
            return NotImplemented
        return type(self) is type(other) and self._values == other._values

    def __hash__(self) -> int:
        """Return a hash based on the type and canonical field fingerprint.

        Returns
        -------
        int
            The hash value.
        """
        return hash((type(self).__qualname__, self.fingerprint()))