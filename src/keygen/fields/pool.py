"""categorical field whose options are supplied once at runtime.

public api
----------
pool
    categorical field whose options are supplied at runtime.
"""

from __future__ import annotations

from typing import Any, Iterable, Iterator

from keygen.fields.field import Field


class Pool(Field):
    """categorical field whose options are supplied at runtime.

    unlike :class:`Enum`, whose choices are fixed in the class body,
    a ``Pool`` starts empty and is filled exactly once before
    generation begins; after :meth:`populate`, the option set is
    frozen.

    handy for resources discovered at startup::

        class Sampler(Key):
            sample = Pool()
            pitch  = Param(min=-12, max=12)

        # before generating:
        wav_files = sorted(Path("./samples").glob("*.wav"))
        Sampler.sample.populate(wav_files)

    sized, indexable, and iterable once populated.
    """

    def __init__(self) -> None:
        """initialize a Pool instance."""
        self._options: tuple[Any, ...] | None = None
        self._attr: str = ""

    # ── population ───────────────────────────────────────────────────

    def populate(self, items: Iterable[Any]) -> None:
        """set the option list; can only be called once.

        parameters
        ----------
        items : Iterable[Any]
            an iterable of items to populate the pool with.

        raises
        ------
        RuntimeError
            when the pool has already been populated.
        ValueError
            when attempting to populate with an empty collection.
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
    def is_populated(self) -> bool:
        """whether :meth:`populate` has been called.

        returns
        -------
        bool
            true if the pool has been populated, false otherwise.
        """
        return self._options is not None

    @property
    def options(self) -> tuple[Any, ...]:
        """the frozen option set; raises if not yet populated.

        returns
        -------
        tuple[Any, ...]
            the options available in the pool.

        raises
        ------
        RuntimeError
            when the pool has not yet been populated.
        """
        if self._options is None:
            raise RuntimeError(
                f"{self._attr}: pool not yet populated; call populate() before accessing options"
            )
        return self._options

    # ── validation ───────────────────────────────────────────────────

    def validate(self, value: Any) -> None:
        """raise :exc:`RuntimeError` if unpopulated; raise :exc:`ValueError` if *value* is not in the pool.

        parameters
        ----------
        value : Any
            the value to validate against the pool options.

        raises
        ------
        RuntimeError
            when the pool has not yet been populated.
        ValueError
            when the value is not in the pool.
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
        """number of options in the pool.

        returns
        -------
        int
            the number of options available in the pool.
        """
        return len(self.options)

    def __iter__(self) -> Iterator[Any]:
        """iterate over the pool options.

        returns
        -------
        Iterator[Any]
            an iterator over the pool options.
        """
        return iter(self.options)

    def __getitem__(self, idx: int) -> Any:
        """return the option at position *idx*.

        parameters
        ----------
        idx : int
            the index of the option to retrieve.

        returns
        -------
        Any
            the option at the specified index.
        """
        return self.options[idx]

    def __repr__(self) -> str:
        """return a string representation of the Pool.

        returns
        -------
        str
            a string representation of the Pool instance.
        """
        if self._options is None:
            return "Pool(<not populated>)"
        if len(self._options) <= 6:
            inner = ", ".join(repr(o) for o in self._options)
            return f"Pool({inner})"
        return f"Pool({len(self._options)} items)"