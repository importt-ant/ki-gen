"""Categorical field with a fixed set of allowed values."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from keygen.fields.field import Field


class Enum(Field):
    """Categorical field with a fixed set of allowed values.

    Example::

        class DrumKit(Key):
            hit = Enum("kick", "snare", "hihat", "clap")

    Sized, indexable, and iterable::

        len(DrumKit.hit)             # 4
        DrumKit.hit[0]               # "kick"
        rng.choice(DrumKit.hit)      # picks one at random
        DrumKit.hit.options          # ("kick", "snare", "hihat", "clap")

    Parameters
    ----------
    *options : Any
        One or more allowed values. At least one is required.

    Raises
    ------
    TypeError
        When no options are provided.
    """

    def __init__(self, *options: Any) -> None:
        if not options:
            raise TypeError("Enum requires at least one option")
        self.options: tuple[Any, ...] = tuple(options)
        self._attr = ""

    def validate(self, value: Any) -> None:
        """Raise :exc:`ValueError` if *value* is not one of the allowed options."""
        if value not in self.options:
            raise ValueError(f"{self._attr}: {value!r} is not one of {self.options}")

    def __len__(self) -> int:
        """Number of allowed options."""
        return len(self.options)

    def __iter__(self) -> Iterator[Any]:
        """Iterate over the allowed options."""
        return iter(self.options)

    def __getitem__(self, idx: int) -> Any:
        """Return the option at position *idx*."""
        return self.options[idx]

    def __repr__(self) -> str:
        inner = ", ".join(repr(o) for o in self.options)
        return f"Enum({inner})"
