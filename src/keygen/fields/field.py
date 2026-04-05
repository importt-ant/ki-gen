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
            def validate(self, value):
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
        """Raise :exc:`ValueError` if *value* is not acceptable.

        Parameters
        ----------
        value : Any
            The value to validate.

        Raises
        ------
        ValueError
            When *value* is not acceptable.
        """

    # ── Descriptor Protocol ──────────────────────────────────────────

    def __set_name__(self, owner: type, name: str) -> None:
        """Store the attribute name assigned on the owning class.

        Parameters
        ----------
        owner : type
            The class that owns this descriptor.
        name : str
            The name of the attribute being assigned.
        """

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        """Return the field spec (class access) or the stored value (instance access).

        Parameters
        ----------
        obj : Any
            The instance from which to retrieve the value.
        objtype : type, optional
            The type of the owner class.

        Returns
        -------
        Any
            The stored value or the field spec.
        """

    def __set__(self, obj: Any, value: Any) -> None:
        """Validate and store *value* on the Key instance.

        Parameters
        ----------
        obj : Any
            The Key instance to which the value is being assigned.
        value : Any
            The value to store.

        Raises
        ------
        ValueError
            When *value* is not acceptable.
        """