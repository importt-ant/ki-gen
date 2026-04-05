"""Numeric field with optional min, max, and step bounds."""

from __future__ import annotations

from typing import Any

from keygen.fields.field import Field


class Param(Field):
    """Numeric field with optional min, max, and step constraints.

    Example::

        class Oscillator(Key):
            frequency = Param(min=20, max=20000)
            detune    = Param(min=-100, max=100, step=1)

    Bounds are accessible on the class::

        Oscillator.frequency.min  # 20
        Oscillator.frequency.max  # 20000

    Parameters
    ----------
    min : float | int, optional
        Lower bound (inclusive).  ``None`` means unbounded below.
    max : float | int, optional
        Upper bound (inclusive).  ``None`` means unbounded above.
    step : float | int, optional
        If set, values must land on ``min + n * step``.
    """

    def __init__(
        self,
        *,
        min: float | int | None = None,
        max: float | int | None = None,
        step: float | int | None = None,
    ) -> None:
        self.min = min
        self.max = max
        self.step = step
        self._attr = ""

    def validate(self, value: Any) -> None:
        """Raise :exc:`ValueError` if *value* violates the min/max/step constraints."""
        if self.min is not None and value < self.min:
            raise ValueError(
                f"{self._attr}: {value!r} is below minimum {self.min}"
            )
        if self.max is not None and value > self.max:
            raise ValueError(
                f"{self._attr}: {value!r} is above maximum {self.max}"
            )
        if self.step is not None and self.min is not None:
            offset = value - self.min
            # Use round() to handle floating-point precision issues
            if round(offset / self.step) * self.step != round(offset, 12):
                raise ValueError(
                    f"{self._attr}: {value!r} is not aligned to "
                    f"step {self.step} (from min {self.min})"
                )

    def __repr__(self) -> str:
        parts = []
        if self.min is not None:
            parts.append(f"min={self.min}")
        if self.max is not None:
            parts.append(f"max={self.max}")
        if self.step is not None:
            parts.append(f"step={self.step}")
        return f"Param({', '.join(parts)})"