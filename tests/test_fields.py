"""Tests for keygen.fields — Param, Enum, Pool, and the Field descriptor protocol."""

from __future__ import annotations

import pytest

from keygen.fields import Enum, Field, Param, Pool
from keygen.key import Key


# ═══════════════════════════════════════════════════════════════════════
#  Param
# ═══════════════════════════════════════════════════════════════════════


class TestParam:
    """Tests for the Param field descriptor."""

    # ── construction ─────────────────────────────────────────────────

    def test_stores_bounds(self):
        p = Param(min=0, max=100)
        assert p.min == 0
        assert p.max == 100
        assert p.step is None

    def test_stores_step(self):
        p = Param(min=0, max=100, step=5)
        assert p.step == 5

    def test_unbounded(self):
        p = Param()
        assert p.min is None
        assert p.max is None
        assert p.step is None

    def test_partial_bounds(self):
        p = Param(min=10)
        assert p.min == 10
        assert p.max is None

    # ── validation ───────────────────────────────────────────────────

    def test_accepts_in_range(self, synth_patch_cls):
        k = synth_patch_cls(pitch=440, velocity=64, attack=0.5, waveform="sine")
        assert k.pitch == 440

    def test_rejects_below_min(self, synth_patch_cls):
        with pytest.raises(ValueError, match="below minimum"):
            synth_patch_cls(pitch=-1, velocity=0, attack=0.01, waveform="sine")

    def test_rejects_above_max(self, synth_patch_cls):
        with pytest.raises(ValueError, match="above maximum"):
            synth_patch_cls(pitch=20001, velocity=0, attack=0.01, waveform="sine")

    def test_boundary_values_accepted(self, synth_patch_cls):
        k = synth_patch_cls(pitch=20, velocity=127, attack=2.0, waveform="sine")
        assert k.pitch == 20
        assert k.velocity == 127
        assert k.attack == 2.0

    def test_step_aligned_accepted(self, stepped_key_cls):
        k = stepped_key_cls(level=30, mode="a")
        assert k.level == 30

    def test_step_misaligned_rejected(self, stepped_key_cls):
        with pytest.raises(ValueError, match="not aligned to step"):
            stepped_key_cls(level=33, mode="a")

    def test_step_at_boundaries(self, stepped_key_cls):
        k0 = stepped_key_cls(level=0, mode="a")
        k100 = stepped_key_cls(level=100, mode="b")
        assert k0.level == 0
        assert k100.level == 100

    # ── repr ─────────────────────────────────────────────────────────

    def test_repr_full(self):
        assert repr(Param(min=0, max=10, step=2)) == "Param(min=0, max=10, step=2)"

    def test_repr_partial(self):
        assert repr(Param(min=0)) == "Param(min=0)"

    def test_repr_empty(self):
        assert repr(Param()) == "Param()"


# ═══════════════════════════════════════════════════════════════════════
#  Enum
# ═══════════════════════════════════════════════════════════════════════


class TestEnum:
    """Tests for the Enum field descriptor."""

    # ── construction ─────────────────────────────────────────────────

    def test_stores_options_as_tuple(self):
        e = Enum("a", "b", "c")
        assert e.options == ("a", "b", "c")

    def test_requires_at_least_one_option(self):
        with pytest.raises(TypeError, match="at least one option"):
            Enum()

    def test_single_option(self):
        e = Enum("only")
        assert len(e) == 1

    # ── validation ───────────────────────────────────────────────────

    def test_accepts_valid_option(self, synth_patch_cls):
        k = synth_patch_cls(pitch=440, velocity=64, attack=0.5, waveform="saw")
        assert k.waveform == "saw"

    def test_rejects_invalid_option(self, synth_patch_cls):
        with pytest.raises(ValueError, match="is not one of"):
            synth_patch_cls(pitch=440, velocity=64, attack=0.5, waveform="noise")

    # ── sequence protocol ────────────────────────────────────────────

    def test_len(self):
        e = Enum(1, 2, 3, 4)
        assert len(e) == 4

    def test_iter(self):
        e = Enum("x", "y")
        assert list(e) == ["x", "y"]

    def test_getitem(self):
        e = Enum("a", "b", "c")
        assert e[0] == "a"
        assert e[2] == "c"
        assert e[-1] == "c"

    # ── repr ─────────────────────────────────────────────────────────

    def test_repr(self):
        assert repr(Enum("a", "b")) == "Enum('a', 'b')"


# ═══════════════════════════════════════════════════════════════════════
#  Pool
# ═══════════════════════════════════════════════════════════════════════


class TestPool:
    """Tests for the Pool field descriptor."""

    # ── population ───────────────────────────────────────────────────

    def test_starts_unpopulated(self):
        p = Pool()
        assert not p.populated

    def test_populate_freezes_options(self):
        p = Pool()
        p.populate(["a", "b", "c"])
        assert p.populated
        assert p.options == ("a", "b", "c")

    def test_cannot_repopulate(self):
        p = Pool()
        p.populate([1, 2])
        with pytest.raises(RuntimeError, match="already populated"):
            p.populate([3, 4])

    def test_cannot_populate_empty(self):
        p = Pool()
        with pytest.raises(ValueError, match="empty collection"):
            p.populate([])

    # ── options access before populate ───────────────────────────────

    def test_options_raises_before_populate(self):
        p = Pool()
        with pytest.raises(RuntimeError, match="not yet populated"):
            _ = p.options

    # ── validation ───────────────────────────────────────────────────

    def test_validate_raises_before_populate(self):
        p = Pool()
        with pytest.raises(RuntimeError, match="not yet populated"):
            p.validate("x")

    def test_validate_accepts_pooled_value(self):
        p = Pool()
        p.populate(["x", "y"])
        p.validate("x")  # should not raise

    def test_validate_rejects_unknown_value(self):
        p = Pool()
        p.populate(["x", "y"])
        with pytest.raises(ValueError, match="not in the pool"):
            p.validate("z")

    # ── sequence protocol ────────────────────────────────────────────

    def test_len(self):
        p = Pool()
        p.populate(range(5))
        assert len(p) == 5

    def test_iter(self):
        p = Pool()
        p.populate(["a", "b"])
        assert list(p) == ["a", "b"]

    def test_getitem(self):
        p = Pool()
        p.populate([10, 20, 30])
        assert p[1] == 20

    def test_len_raises_before_populate(self):
        p = Pool()
        with pytest.raises(RuntimeError):
            len(p)

    # ── repr ─────────────────────────────────────────────────────────

    def test_repr_unpopulated(self):
        assert repr(Pool()) == "Pool(<not populated>)"

    def test_repr_small(self):
        p = Pool()
        p.populate([1, 2])
        assert repr(p) == "Pool(1, 2)"

    def test_repr_large(self):
        p = Pool()
        p.populate(range(10))
        assert repr(p) == "Pool(10 items)"


# ═══════════════════════════════════════════════════════════════════════
#  Field base class
# ═══════════════════════════════════════════════════════════════════════


class TestFieldDescriptorProtocol:
    """Tests for the Field descriptor __get__/__set__/__set_name__ mechanics."""

    def test_class_access_returns_field_spec(self, synth_patch_cls):
        spec = synth_patch_cls.pitch
        assert isinstance(spec, Param)
        assert spec.min == 20

    def test_instance_access_returns_value(self, synth_patch_cls):
        k = synth_patch_cls(pitch=440, velocity=64, attack=0.5, waveform="sine")
        assert k.pitch == 440

    def test_set_triggers_validation(self, synth_patch_cls):
        k = synth_patch_cls(pitch=440, velocity=64, attack=0.5, waveform="sine")
        with pytest.raises(ValueError):
            k.pitch = -999

    def test_set_name_is_recorded(self, synth_patch_cls):
        assert synth_patch_cls.pitch._attr == "pitch"
        assert synth_patch_cls.waveform._attr == "waveform"

    def test_field_validate_is_abstract(self):
        """Field.validate is decorated @abstractmethod — subclasses must implement it."""
        import inspect

        assert inspect.isabstract(Field) or hasattr(Field.validate, "__isabstractmethod__")
        assert getattr(Field.validate, "__isabstractmethod__", False) is True
