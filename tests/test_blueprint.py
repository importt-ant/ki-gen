"""Tests for keygen.blueprint — configuration, effective specs, and building."""

from __future__ import annotations

import pytest

from keygen.blueprint import Blueprint
from keygen.fields import Enum, Param, Pool
from keygen.key import Key
from keygen.rengines import RandomRengine

from .conftest import SynthPatch, SteppedKey, PoolKey


# ═══════════════════════════════════════════════════════════════════════
#  Construction
# ═══════════════════════════════════════════════════════════════════════


class TestBlueprintConstruction:
    def test_key_type(self, synth_patch_cls):
        bp = Blueprint(synth_patch_cls)
        assert bp.key_type is synth_patch_cls

    def test_no_overrides_by_default(self, synth_patch_cls):
        bp = Blueprint(synth_patch_cls)
        assert bp.overrides == {}


# ═══════════════════════════════════════════════════════════════════════
#  Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestBlueprintConfigure:
    def test_configure_returns_self(self, synth_blueprint):
        result = synth_blueprint.configure("pitch", Param(min=200, max=4000))
        assert result is synth_blueprint

    def test_chaining(self, synth_patch_cls):
        bp = (
            Blueprint(synth_patch_cls)
            .configure("pitch", Param(min=200, max=4000))
            .configure("waveform", Enum("sine", "saw"))
        )
        assert "pitch" in bp.overrides
        assert "waveform" in bp.overrides

    def test_configure_unknown_field_raises(self, synth_blueprint):
        with pytest.raises(ValueError, match="has no field"):
            synth_blueprint.configure("nonexistent", 42)

    def test_configure_with_static_value(self, synth_blueprint):
        synth_blueprint.configure("pitch", 440)
        assert synth_blueprint.overrides["pitch"] == 440

    def test_configure_with_field_spec(self, synth_blueprint):
        narrow = Param(min=200, max=4000)
        synth_blueprint.configure("pitch", narrow)
        assert synth_blueprint.overrides["pitch"] is narrow


# ═══════════════════════════════════════════════════════════════════════
#  Effective spec
# ═══════════════════════════════════════════════════════════════════════


class TestEffectiveSpec:
    def test_returns_default_when_no_override(self, synth_patch_cls):
        bp = Blueprint(synth_patch_cls)
        spec = bp.effective_spec("pitch")
        assert isinstance(spec, Param)
        assert spec.min == 20

    def test_returns_override_when_set(self, synth_patch_cls):
        bp = Blueprint(synth_patch_cls).configure("pitch", Param(min=200, max=4000))
        spec = bp.effective_spec("pitch")
        assert spec.min == 200
        assert spec.max == 4000

    def test_returns_static_override(self, synth_patch_cls):
        bp = Blueprint(synth_patch_cls).configure("pitch", 440)
        assert bp.effective_spec("pitch") == 440

    def test_unknown_field_raises(self, synth_patch_cls):
        bp = Blueprint(synth_patch_cls)
        with pytest.raises(ValueError, match="has no field"):
            bp.effective_spec("fake")


# ═══════════════════════════════════════════════════════════════════════
#  Building keys
# ═══════════════════════════════════════════════════════════════════════


class TestBlueprintBuild:
    def test_build_returns_key_instance(self, synth_patch_cls):
        bp = Blueprint(synth_patch_cls)
        rng = RandomRengine(seed=42)
        key = bp.build(rng)
        assert isinstance(key, synth_patch_cls)

    def test_build_populates_all_fields(self, synth_patch_cls):
        bp = Blueprint(synth_patch_cls)
        rng = RandomRengine(seed=42)
        key = bp.build(rng)
        d = key.to_dict()
        assert set(d.keys()) == {"pitch", "velocity", "attack", "waveform"}

    def test_build_respects_param_bounds(self, synth_patch_cls):
        bp = Blueprint(synth_patch_cls)
        rng = RandomRengine(seed=42)
        for _ in range(50):
            key = bp.build(rng)
            assert 20 <= key.pitch <= 20000
            assert 0 <= key.velocity <= 127
            assert 0.01 <= key.attack <= 2.0

    def test_build_respects_enum_choices(self, synth_patch_cls):
        bp = Blueprint(synth_patch_cls)
        rng = RandomRengine(seed=42)
        for _ in range(50):
            key = bp.build(rng)
            assert key.waveform in ("sine", "saw", "square", "triangle")

    def test_build_with_static_override(self, synth_patch_cls):
        bp = Blueprint(synth_patch_cls).configure("pitch", 440)
        rng = RandomRengine(seed=42)
        for _ in range(20):
            key = bp.build(rng)
            assert key.pitch == 440

    def test_build_with_narrowed_bounds(self, synth_patch_cls):
        bp = Blueprint(synth_patch_cls).configure("pitch", Param(min=1000, max=2000))
        rng = RandomRengine(seed=42)
        for _ in range(50):
            key = bp.build(rng)
            assert 1000 <= key.pitch <= 2000

    def test_build_with_narrowed_enum(self, synth_patch_cls):
        bp = Blueprint(synth_patch_cls).configure("waveform", Enum("sine", "saw"))
        rng = RandomRengine(seed=42)
        for _ in range(50):
            key = bp.build(rng)
            assert key.waveform in ("sine", "saw")

    def test_build_stepped_param(self, stepped_key_cls):
        bp = Blueprint(stepped_key_cls)
        rng = RandomRengine(seed=42)
        for _ in range(50):
            key = bp.build(rng)
            assert key.level % 10 == 0
            assert 0 <= key.level <= 100

    def test_build_seeded_reproducibility(self, synth_patch_cls):
        bp = Blueprint(synth_patch_cls)
        keys_a = [bp.build(RandomRengine(seed=99)) for _ in range(5)]
        keys_b = [bp.build(RandomRengine(seed=99)) for _ in range(5)]
        for a, b in zip(keys_a, keys_b):
            assert a.to_dict() == b.to_dict()

    def test_build_with_pool_field(self, pool_key_cls):
        pool_key_cls.sample.populate(["kick.wav", "snare.wav", "hat.wav"])
        bp = Blueprint(pool_key_cls)
        rng = RandomRengine(seed=42)
        key = bp.build(rng)
        assert key.sample in ("kick.wav", "snare.wav", "hat.wav")
        assert 0.0 <= key.gain <= 1.0

    def test_build_unbounded_param_raises(self):
        from .conftest import UnboundedParamKey

        bp = Blueprint(UnboundedParamKey)
        rng = RandomRengine(seed=42)
        with pytest.raises(TypeError, match="needs both min and max"):
            bp.build(rng)


# ═══════════════════════════════════════════════════════════════════════
#  _randomize_field (static)
# ═══════════════════════════════════════════════════════════════════════


class TestRandomizeFieldDispatch:
    def test_unknown_field_type_raises(self):
        from keygen.fields.field import Field

        class CustomField(Field):
            def validate(self, value):
                pass

        with pytest.raises(TypeError, match="cannot be auto-randomized"):
            Blueprint._randomize_field("test", CustomField(), RandomRengine(0))

    def test_float_param_uniform(self):
        spec = Param(min=0.0, max=1.0)
        rng = RandomRengine(seed=42)
        val = Blueprint._randomize_field("f", spec, rng)
        assert isinstance(val, float)
        assert 0.0 <= val <= 1.0

    def test_int_param_randint(self):
        spec = Param(min=0, max=10)
        rng = RandomRengine(seed=42)
        val = Blueprint._randomize_field("f", spec, rng)
        assert isinstance(val, int)
        assert 0 <= val <= 10


# ═══════════════════════════════════════════════════════════════════════
#  repr
# ═══════════════════════════════════════════════════════════════════════


class TestBlueprintRepr:
    def test_repr_no_overrides(self, synth_patch_cls):
        bp = Blueprint(synth_patch_cls)
        assert repr(bp) == "Blueprint(SynthPatch)"

    def test_repr_with_overrides(self, synth_patch_cls):
        bp = Blueprint(synth_patch_cls).configure("pitch", 440)
        r = repr(bp)
        assert "SynthPatch" in r
        assert "pitch=440" in r
