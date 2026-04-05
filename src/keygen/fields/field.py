"""Base descriptor for validated Key fields."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any


class Field:
    """Base descriptor for :class:`~keygen.Key` fields.

    Subclass this to create custom field types. Implement
    :meth:`validate` to raise :exc:`ValueError` on bad input.
    Validation runs automatically on every assignment to a Key
    instance.

    Example::

        class MidiNote(Field):
            def validate(self, value: Any) -> None:
                if not isinstance(value, int) or not (0 <= value <= 127):
                    raise ValueError(f"{self._attr}: expected MIDI note 0–127, got {value!r}")

    Parameters
    ----------
    None

    Raises
    ------
    None
    """

    _attr: str = ""

    @abstractmethod
    def validate(self, value: Any) -> None:
        """Raise :exc:`ValueError` if *value* is not acceptable."""

    # ── descriptor protocol ──────────────────────────────────────────

    def __set_name__(self, owner: type, name: str) -> None:
        """Store the attribute name assigned on the owning class."""
        self._attr = name

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        """Return the field spec (class access) or the stored value (instance access)."""
        if obj is None:
            return self  # class access; this returns the field spec
        return obj._values.get(self._attr)

    def __set__(self, obj: Any, value: Any) -> None:
        """Validate and store *value* on the Key instance."""
        self.validate(value)
        obj._values[self._attr] = value
