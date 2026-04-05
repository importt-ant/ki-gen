"""Generation loop with dedup, seed+cursor resume, and blueprint delegation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from keygen.blueprint import Blueprint
from keygen.recorders.recorder import Recorder
from keygen.key import Key
from keygen.rengines import FastForwardNotSupported, RandomRengine, Rengine

if TYPE_CHECKING:
    from keygen.store import Store

_DEFAULT_MAX_CONSECUTIVE_SKIPS = 30


class Generator(Recorder):
    """Generator that produces :class:`Key` instances via a :class:`Rengine`.

    Owns the generate/dedup loop and handles seed+cursor resume.
    Field randomization is delegated to a :class:`Blueprint`, which
    describes *how* each field is produced (random within bounds,
    pinned to a constant, etc.).

    The engine is pluggable — pass any :class:`Rengine` via the
    *rengine* parameter, or omit it to get a :class:`RandomRengine`
    seeded with *seed*.

    Parameters
    ----------
    blueprint : Blueprint
        A :class:`Blueprint` that knows which Key subclass to build
        and how each field should be randomized or pinned.
    seed : int, optional
        Seed forwarded to the default :class:`RandomRengine` when
        no explicit engine is given.  Ignored if *rengine* is set.
    rengine : Rengine, optional
        A pre-built :class:`Rengine`.  Takes priority over *seed*.
    store : Store, optional
        Optional :class:`Store` for persistence and dedup.
    flush_interval : int, optional
        Auto-flush cadence (inherited from :class:`Recorder`).
    max_consecutive_skips : int, optional
        Dedup skip limit before :meth:`_on_space_exhausted` fires.
    """

    def __init__(
        self,
        blueprint: Blueprint,
        seed: int | None = None,
        rengine: Rengine | None = None,
        store: Store | None = None,
        flush_interval: int = 10,
        max_consecutive_skips: int = _DEFAULT_MAX_CONSECUTIVE_SKIPS,
    ) -> None:
        self._blueprint = blueprint
        self._seed = seed
        self._max_consecutive_skips = max_consecutive_skips

        if rengine is not None:
            self._rengine = rengine
        else:
            self._rengine = RandomRengine(seed)

        super().__init__(store=store, flush_interval=flush_interval)

    # ── identity ─────────────────────────────────────────────────────

    @property
    def name(self) -> str:
        """Derived from the blueprint's Key subclass name."""
        return self._blueprint.key_type.__name__

    @property
    def blueprint(self) -> Blueprint:
        """The blueprint driving field randomization."""
        return self._blueprint

    @property
    def seed(self) -> int | None:
        """Seed passed at construction, or ``None``."""
        return self._seed

    @property
    def rng(self) -> Rengine:
        """The active RNG engine."""
        return self._rengine

    @property
    def gen_type(self) -> str:
        """Class name of the underlying :class:`Rengine`."""
        return type(self._rengine).__name__

    @property
    def gen_key(self) -> str:
        """Unique identifier: ``name:engine_type:seed``."""
        return f"{self.name}:{self.gen_type}:{self._seed}"

    # ── resume ───────────────────────────────────────────────────────

    def _on_resume(self, state: dict[str, Any]) -> None:
        """Resume the generator state from a saved state.

        Parameters
        ----------
        state : dict
            The saved state containing the cursor to resume from.
        """
        saved_cursor = state["cursor"]
        try:
            self._rengine.fast_forward(saved_cursor)
        except FastForwardNotSupported:
            self._fast_forward_fallback(saved_cursor)

    def _fast_forward_fallback(self, steps: int) -> None:
        """Replay ``_randomize`` calls to advance engines without O(1) skip.

        Parameters
        ----------
        steps : int
            The number of steps to fast forward.
        """
        for _ in range(steps):
            self._randomize()
        self._cursor = steps

    # ── randomization ────────────────────────────────────────────────

    def _randomize(self) -> Key:
        """Delegate to the blueprint to produce a randomized Key."""
        return self._blueprint.build(self._rengine)

    # ── generation ───────────────────────────────────────────────────

    def generate(self) -> Key | None:
        """Produce a single deduplicated key.

        Retries internally when a duplicate is drawn, up to
        *max_consecutive_skips* times.

        Returns
        -------
        Key or None
            The accepted key, or ``None`` when
            :meth:`_on_space_exhausted` is overridden to not raise.
        """
        skips = 0
        while skips < self._max_consecutive_skips:
            key = self._randomize()

            if self.record(key):
                return key

            skips += 1

        self._on_space_exhausted(skips)
        return None

    def generate_many(self, n: int) -> list[Key]:
        """Generate up to *n* deduplicated keys.

        Parameters
        ----------
        n : int
            Maximum number of keys to produce.

        Returns
        -------
        list[Key]
            The accepted keys.  May be shorter than *n* if
            :meth:`_on_space_exhausted` swallows the error.
        """
        keys: list[Key] = []
        for _ in range(n):
            key = self.generate()
            if key is not None:
                keys.append(key)
        return keys