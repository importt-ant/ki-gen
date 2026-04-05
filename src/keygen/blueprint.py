"""Field randomization plan for building Key instances."""

from __future__ import annotations

from typing import Any

from keygen.fields import Enum, Field, Param, Pool
from keygen.key import Key


class Blueprint:
    """Describes how each field of a Key subclass should be randomized.

    Starts with the Key's own field specs as defaults.  Use
    :meth:`configure` to narrow bounds, restrict choices, or pin
    a field to a constant::

        bp = (
            Blueprint(SynthPatch)
            .configure("pitch", Param(min=200, max=4000))
            .configure("waveform", Enum("sine", "saw"))
        )

    Call :meth:`build` with an RNG engine to produce a Key.
    Blueprints are engine-agnostic and reusable.

    Parameters
    ----------
    key_type : type[Key]
        The :class:`Key` subclass whose fields will be randomized.
    """

    def __init__(self, key_type: type[Key]) -> None:
        self._key_type = key_type
        self._overrides: dict[str, Field | Any] = {}

    # ── Configuration ────────────────────────────────────────────────

    def configure(self, field_name: str, spec: Field | Any) -> Blueprint:
        """Set how a field is produced.

        Parameters
        ----------
        field_name : str
            Name of a field declared on the Key subclass.
        spec : Field | Any
            A :class:`Field` descriptor (e.g. ``Param(min=1000, max=2000)``)
            to override randomization bounds, or a plain value to pin
            the field to a static constant.

        Returns
        -------
        Blueprint
            For method chaining.

        Raises
        ------
        ValueError
            If *field_name* does not exist on the Key subclass.
        """
        if field_name not in self._key_type.field_specs():
            raise ValueError(
                f"{self._key_type.__name__} has no field {field_name!r}"
            )
        self._overrides[field_name] = spec
        return self

    # ── Introspection ────────────────────────────────────────────────

    @property
    def key_type(self) -> type[Key]:
        """The Key subclass this blueprint targets."""
        return self._key_type

    @property
    def overrides(self) -> dict[str, Field | Any]:
        """Current field overrides (read-only copy)."""
        return dict(self._overrides)

    def effective_spec(self, field_name: str) -> Field | Any:
        """Return the active spec for *field_name*.

        Returns the override if one was set via :meth:`configure`,
        otherwise the default spec declared on the Key subclass.

        Parameters
        ----------
        field_name : str
            Name of a field declared on the Key subclass.

        Raises
        ------
        ValueError
            If *field_name* does not exist on the Key subclass.
        """
        if field_name in self._overrides:
            return self._overrides[field_name]
        specs = self._key_type.field_specs()
        if field_name not in specs:
            raise ValueError(
                f"{self._key_type.__name__} has no field {field_name!r}"
            )
        return specs[field_name]

    # ── Building ─────────────────────────────────────────────────────

    def build(self, rng: Any) -> Key:
        """Produce a Key instance using *rng* for randomization.

        Parameters
        ----------
        rng : Any
            Any object satisfying the :class:`Rengine` protocol
            (``randint``, ``uniform``, ``choice``, etc.).

        Static overrides (plain values) are used as-is; field
        overrides and default specs are dispatched to
        :meth:`_randomize_field`.

        Returns
        -------
        Key
            The constructed key with all fields populated.
        """
        values: dict[str, Any] = {}
        for fname, spec in self._key_type.field_specs().items():
            if fname in self._overrides:
                override = self._overrides[fname]
                if isinstance(override, Field):
                    values[fname] = self._randomize_field(fname, override, rng)
                else:
                    values[fname] = override
            else:
                values[fname] = self._randomize_field(fname, spec, rng)
        return self._key_type(**values)

    @staticmethod
    def _randomize_field(name: str, spec: Field, rng: Any) -> Any:
        """Produce a single random value from *spec* using *rng*.

        Dispatches on the field type: :class:`Enum` and :class:`Pool`
        use ``rng.choice``; :class:`Param` uses ``rng.randint`` or
        ``rng.uniform`` depending on the bound types.

        Raises
        ------
        TypeError
            If *spec* has no randomization strategy or is missing
            required bounds.
        """
        if isinstance(spec, (Enum, Pool)):
            return rng.choice(spec.options)
        if isinstance(spec, Param):
            if spec.min is None or spec.max is None:
                raise TypeError(
                    f"{name}: Param needs both min and max for "
                    f"auto-randomization; use configure({name!r}, ...) "
                    f"to set bounds or pin a value"
                )
            if spec.step is not None:
                n_steps = int((spec.max - spec.min) / spec.step)
                idx = rng.randint(0, n_steps)
                return spec.min + idx * spec.step
            if isinstance(spec.min, int) and isinstance(spec.max, int):
                return rng.randint(spec.min, spec.max)
            return rng.uniform(float(spec.min), float(spec.max))
        raise TypeError(
            f"{name}: field type {type(spec).__name__} "
            f"cannot be auto-randomized"
        )

    # ── Representation ───────────────────────────────────────────────

    def __repr__(self) -> str:
        overrides = ", ".join(
            f"{k}={v!r}" for k, v in self._overrides.items()
        )
        if overrides:
            return f"Blueprint({self._key_type.__name__}, {overrides})"
        return f"Blueprint({self._key_type.__name__})"