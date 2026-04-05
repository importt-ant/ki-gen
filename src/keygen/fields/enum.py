"""categorical field with a fixed set of allowed values."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from keygen.fields.field import Field


class Enum(Field):
    """categorical field with a fixed set of allowed values.

    example::

        class DrumKit(Key):
            hit = Enum("kick", "snare", "hihat", "clap")

    sized, indexable, and iterable::

        len(DrumKit.hit)             # 4
        DrumKit.hit[0]               # "kick"
        rng.choice(DrumKit.hit)      # picks one at random
        DrumKit.hit.options          # ("kick", "snare", "hihat", "clap")

    parameters
    ----------
    *options : Any
        one or more allowed values; at least one is required.

    raises
    ------
    TypeError
        when no options are provided.
    """

    def __init__(self, *options: Any) -> None:
        if not options:
            raise TypeError("Enum requires at least one option")
        self.options: tuple[Any, ...] = tuple(options)
        self._attr = ""

    def validate(self, value: Any) -> None:
        """raise :exc:`ValueError` if *value* is not one of the allowed options."""
        if value not in self.options:
            raise ValueError(f"{self._attr}: {value!r} is not one of {self.options}")

    def __len__(self) -> int:
        """number of allowed options."""
        return len(self.options)

    def __iter__(self) -> Iterator[Any]:
        """iterate over the allowed options."""
        return iter(self.options)

    def __getitem__(self, idx: int) -> Any:
        """return the option at position *idx*."""
        return self.options[idx]

    def __repr__(self) -> str:
        inner = ", ".join(repr(o) for o in self.options)
        return f"Enum({inner})"
