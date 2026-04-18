"""Structural typing contracts for storable objects."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Storable(Protocol):
    """Any object that can be recorded by :class:`Store`.

    Implementors must expose:

    * ``id`` — a unique string identifier for the record.
    * ``to_dict()`` — a JSON-serialisable dict of the object's data.

    :class:`kigen.Key` satisfies this protocol automatically.
    """

    id: str

    def to_dict(self) -> dict[str, Any]: ...
