"""Categorical field whose options are supplied once at runtime."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any

from keygen.fields.field import Field


class Pool(Field):
    """Categorical field whose options are supplied at runtime.

    Unlike :class:`Enum`, whose choices are fixed in the class body,
    a ``Pool`` starts empty and is filled exactly once before
    generation begins.  After :meth:`populate` the option set is
    frozen.

    Handy for resources discovered at startup::

        class Sampler(Key):
            sample = Pool()
            pitch  = Param(min=-12, max=12)

        # before generating:
        wav_files = sorted(Path("./samples").glob("*.wav"))
        Sampler.sample.populate(wav_files)

    Sized, indexable, and iterable once populated.
    """

    def __init__(self) -> None:
        self._options: tuple[Any, ...] | None = None
        self._attr = ""

    # ── population ───────────────────────────────────────────────────

    def populate(self, items: Iterable[Any]) -> None:
        """Set the option list.  Can only be called once."""
        if self._options is not None:
            raise RuntimeError(
                f"{self._attr}: pool already populated; cannot repopulate a frozen pool"
            )
        opts = tuple(items)
        if not opts:
            raise ValueError(f"{self._attr}: cannot populate with an empty collection")
        self._options = opts

    @property
    def populated(self) -> bool:
        """Whether :meth:`populate` has been called."""
        return self._options is not None

    @property
    def options(self) -> tuple[Any, ...]:
        """The frozen option set (raises if not yet populated)."""
        if self._options is None:
            raise RuntimeError(
                f"{self._attr}: pool not yet populated; call populate() before accessing options"
            )
        return self._options

    # ── validation ───────────────────────────────────────────────────

    def validate(self, value: Any) -> None:
        """Raise :exc:`RuntimeError` if unpopulated, or :exc:`ValueError` if *value* is not in the pool."""
        if self._options is None:
            raise RuntimeError(
                f"{self._attr}: pool not yet populated; call populate() before assigning values"
            )
        if value not in self._options:
            raise ValueError(
                f"{self._attr}: {value!r} is not in the pool ({len(self._options)} items)"
            )

    # ── sequence protocol ────────────────────────────────────────────

    def __len__(self) -> int:
        """Number of options in the pool."""
        return len(self.options)

    def __iter__(self) -> Iterator[Any]:
        """Iterate over the pool options."""
        return iter(self.options)

    def __getitem__(self, idx: int) -> Any:
        """Return the option at position *idx*."""
        return self.options[idx]

    def __repr__(self) -> str:
        if self._options is None:
            return "Pool(<not populated>)"
        if len(self._options) <= 6:
            inner = ", ".join(repr(o) for o in self._options)
            return f"Pool({inner})"
        return f"Pool({len(self._options)} items)"
