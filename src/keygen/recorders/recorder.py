"""Deduplication and persistence layer for generated keys."""

from __future__ import annotations

from typing import TYPE_CHECKING

from keygen.key import Key

if TYPE_CHECKING:
    from keygen.store import Store

_DEFAULT_FLUSH_INTERVAL = 10


class SpaceExhaustedError(Exception):
    """Raised when a generator hits too many consecutive duplicate skips."""


class Recorder:
    """Deduplication and persistence layer for keys.

    Works standalone as a recorder when keys come from an external
    source::

        recorder = Recorder(name="session-1", store=my_store)
        key = SynthPatch(pitch=440, velocity=100, attack=0.1, waveform="saw")
        accepted = recorder.record(key)

    Or subclass it to add a generation strategy: see
    :class:`Generator` for the built-in RNG approach.

    Parameters
    ----------
    name:
        Human-readable label used to build :attr:`gen_key`.  Required
        when instantiating ``Recorder`` directly; subclasses may
        override the :attr:`name` property instead.
    store:
        :class:`Store` for persistence and dedup state.
        ``None`` gives an in-memory-only recorder.
    flush_interval:
        Number of :meth:`record` calls between automatic flushes.
    """

    def __init__(
        self,
        name: str | None = None,
        store: Store | None = None,
        flush_interval: int = _DEFAULT_FLUSH_INTERVAL,
    ) -> None:
        if name is not None:
            self._name = name
        self._flush_interval = flush_interval
        self._cursor: int = 0
        self._store: Store | None = store
        self._dirty: int = 0
        self._pending_keys: list[Key] = []
        self._seen: set[str] = set()

        if self._store is not None:
            self._attach(self._store)

    # ── identity ─────────────────────────────────────────────────────

    @property
    def name(self) -> str:
        """Human-readable generator name (used in gen_key)."""
        try:
            return self._name
        except AttributeError:
            raise NotImplementedError(
                f"{type(self).__name__} must either pass 'name' to "
                f"__init__ or override the 'name' property"
            )

    @property
    def gen_type(self) -> str:
        """Strategy label stored alongside the name in gen_key."""
        return "recorder"

    @property
    def gen_key(self) -> str:
        """Unique identifier for this recorder (``name:gen_type``)."""
        return f"{self.name}:{self.gen_type}"

    @property
    def cursor(self) -> int:
        """Number of keys accepted so far."""
        return self._cursor

    # ── store bootstrap (private) ─────────────────────────────────

    def _attach(self, store: Store) -> None:
        """Restore state from *store* if a prior session exists."""
        existing = store.load_generator_by_key(self.gen_key)
        if existing is not None:
            self._cursor = existing["cursor"]
            self._on_resume(existing)
        else:
            self._flush_state()

        self._seen = store.load_seen_fingerprints(self.gen_key)

    def _on_resume(self, state: dict) -> None:
        """Hook called when resuming from a stored session.

        *state* is the full generator row dict.  Override to replay
        or fast-forward RNG state, etc.
        """

    # ── persistence ──────────────────────────────────────────────────

    def flush(self) -> None:
        """Force-write pending keys to the store."""
        if self._store is None:
            return
        if self._pending_keys:
            self._store.record_runs(self._pending_keys, self.gen_key)
            self._pending_keys.clear()
        self._flush_state()
        self._dirty = 0

    def _flush_state(self) -> None:
        if self._store is None:
            return
        self._store.save_generator_by_key(
            self.gen_key,
            cursor=self._cursor,
        )

    def _maybe_flush(self) -> None:
        if self._dirty >= self._flush_interval:
            self.flush()

    # ── deduplication (private) ───────────────────────────────────

    def _is_duplicate(self, fingerprint: str) -> bool:
        return fingerprint in self._seen

    def _on_space_exhausted(self, consecutive_skips: int) -> None:
        """Called when dedup hits too many skips in a row.

        Default raises :class:`SpaceExhaustedError`.  Override to
        retire the generator gracefully instead.
        """
        raise SpaceExhaustedError(
            f"{self.gen_key}: {consecutive_skips} consecutive duplicates — "
            f"exploration space likely exhausted"
        )

    # ── context manager ──────────────────────────────────────────────

    def __enter__(self) -> Recorder:
        """Enter the context manager, returning the recorder."""
        return self

    def __exit__(self, *exc: object) -> None:
        """Flush pending keys on context exit."""
        self.flush()

    # ── recording ────────────────────────────────────────────────────

    def record(self, key: Key) -> bool:
        """Record a key, deduplicating and persisting automatically.

        Parameters
        ----------
        key:
            The :class:`Key` instance to record.

        Returns
        -------
        bool
            ``True`` if the key was new and accepted, ``False`` if it
            was a duplicate.
        """
        return self._record(key)

    def _record(self, key: Key) -> bool:
        """Internal recording — dedup check, seen-set, batched write."""
        fp = key.fingerprint()
        if self._is_duplicate(fp):
            return False
        self._seen.add(fp)
        self._pending_keys.append(key)
        self._cursor += 1
        self._dirty += 1
        self._maybe_flush()
        return True
