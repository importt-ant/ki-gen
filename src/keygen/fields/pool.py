"""Categorical field whose options are supplied once at runtime.

Public API
----------
Pool
    Categorical field whose options are supplied at runtime.
"""

from __future__ import annotations

from typing import Any, Iterable, Iterator

from keygen.fields.field import Field


class Pool(Field):
    """Categorical field whose options are supplied at runtime.

    Unlike :class:`Enum`, whose choices are fixed in the class body,
    a ``Pool`` starts empty and is filled exactly once before
    generation begins.  After :meth:`populate`, the option set is
    frozen.

    Handy for resources discovered at startup::

        class Sampler(Key):
            sample = Pool()
            pitch  = Param(min=-12, max=12)

        # before generating:
        wav_files = sorted(Path("./samples").glob("*.wav"))
        Sampler.sample.populate(wav_files)

    Sized, indexable, and iterable once populated.

    Parameters
    ----------
    None

    Raises
    ------
    None
    """

    def __init__(self) -> None:
        """Initialize the Pool with no options."""
        self._options: tuple[Any, ...] | None = None
        self._attr = ""

    # ── population ───────────────────────────────────────────────────

    def populate(self, items: Iterable[Any]) -> None:
        """Set the option list. Can only be called once.

        Parameters
        ----------
        items : Iterable[Any]
            The items to populate the pool with.

        Raises
        ------
        RuntimeError
            When the pool has already been populated.
        ValueError
            When attempting to populate with an empty collection.
        """
        if self._options is not None:
            raise RuntimeError(
                f"{self._attr}: pool already populated; cannot repopulate a frozen pool"
            )
        opts = tuple(items)
        if not opts:
            raise ValueError(
                f"{self._attr}: cannot populate with an empty collection"
            )
        self._options = opts

    @property
    def populated(self) -> bool:
        """Whether :meth:`populate` has been called.

        Returns
        -------
        bool
            True if the pool has been populated, False otherwise.
        """
        return self._options is not None

    @property
    def options(self) -> tuple[Any, ...]:
        """The frozen option set (raises if not yet populated).

        Returns
        -------
        tuple[Any, ...]
            The options in the pool.

        Raises
        ------
        RuntimeError
            When the pool has not yet been populated.
        """
        if self._options is None:
            raise RuntimeError(
                f"{self._attr}: pool not yet populated; call populate() before accessing options"
            )
        return self._options

    # ── validation ───────────────────────────────────────────────────

    def validate(self, value: Any) -> None:
        """Raise :exc:`RuntimeError` if unpopulated, or :exc:`ValueError` if *value* is not in the pool.

        Parameters
        ----------
        value : Any
            The value to validate against the pool.

        Raises
        ------
        RuntimeError
            When the pool has not yet been populated.
        ValueError
            When the value is not in the pool.
        """
        if self._options is None:
            raise RuntimeError(
                f"{self._attr}: pool not yet populated; call populate() before assigning values"
            )
        if value not in self._options:
            raise ValueError(
                f"{self._attr}: {value!r} is not in the pool "
                f"({len(self._options)} items)"
            )

    # ── sequence protocol ────────────────────────────────────────────

    def __len__(self) -> int:
        """Number of options in the pool.

        Returns
        -------
        int
            The number of options in the pool.
        """
        return len(self.options)

    def __iter__(self) -> Iterator[Any]:
        """Iterate over the pool options.

        Returns
        -------
        Iterator[Any]
            An iterator over the options in the pool.
        """
        return iter(self.options)

    def __getitem__(self, idx: int) -> Any:
        """Return the option at position *idx*.

        Parameters
        ----------
        idx : int
            The index of the option to retrieve.

        Returns
        -------
        Any
            The option at the specified index.
        """
        return self.options[idx]

    def __repr__(self) -> str:
        """Return a string representation of the Pool.

        Returns
        -------
        str
            A string representation of the Pool, indicating whether it is populated.
        """
        if self._options is None:
            return "Pool(<not populated>)"
        if len(self._options) <= 6:
            inner = ", ".join(repr(o) for o in self._options)
            return f"Pool({inner})"
        return f"Pool({len(self._options)} items)"