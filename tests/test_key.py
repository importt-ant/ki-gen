"""Tests for keygen.key — Key subclass behaviour, validation, fingerprinting."""

from __future__ import annotations

import json

import pytest

from keygen.key import Key
from keygen.fields import Enum, Param

from .conftest import SynthPatch, MinimalKey


# ═══════════════════════════════════════════════════════════════════════
#  Construction
# ═══════════════════════════════════════════════════════════════════════


class TestKeyConstruction:
    """Test Key.__init__ and field wiring."""

    def test_basic_creation(self, synth_patch_cls):
        k = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        assert k.pitch == 440
        assert k.velocity == 100
        assert k.attack == 0.5
        assert k.waveform == "sine"

    def test_id_is_generated(self, synth_patch_cls):
        k = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        assert isinstance(k.id, str)
        assert len(k.id) == 12

    def test_ids_are_unique(self, synth_patch_cls):
        k1 = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        k2 = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        assert k1.id != k2.id

    def test_unknown_field_raises_type_error(self, synth_patch_cls):
        with pytest.raises(TypeError, match="has no field"):
            synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine", bogus=42)

    def test_missing_fields_raises_type_error(self, synth_patch_cls):
        """Omitting required fields raises TypeError."""
        with pytest.raises(TypeError, match="missing required field"):
            synth_patch_cls()

    def test_partial_fields_raises_type_error(self, synth_patch_cls):
        """Providing only some fields raises TypeError."""
        with pytest.raises(TypeError, match="missing required field"):
            synth_patch_cls(pitch=440)


# ═══════════════════════════════════════════════════════════════════════
#  field_specs / init_subclass
# ═══════════════════════════════════════════════════════════════════════


class TestFieldSpecs:
    """Test the class-level _fields collection."""

    def test_field_specs_returns_all_declared(self, synth_patch_cls):
        specs = synth_patch_cls.field_specs()
        assert set(specs.keys()) == {"pitch", "velocity", "attack", "waveform"}

    def test_field_specs_is_copy(self, synth_patch_cls):
        s1 = synth_patch_cls.field_specs()
        s2 = synth_patch_cls.field_specs()
        assert s1 is not s2

    def test_inheritance_merges_fields(self):
        class Base(Key):
            x = Param(min=0, max=1)

        class Child(Base):
            y = Param(min=0, max=10)

        specs = Child.field_specs()
        assert "x" in specs
        assert "y" in specs

    def test_child_can_override_parent_field(self):
        class Base(Key):
            x = Param(min=0, max=10)

        class Child(Base):
            x = Param(min=0, max=100)

        assert Child.field_specs()["x"].max == 100
        assert Base.field_specs()["x"].max == 10


# ═══════════════════════════════════════════════════════════════════════
#  Serialization / fingerprinting
# ═══════════════════════════════════════════════════════════════════════


class TestSerialization:
    """Test to_dict and fingerprint."""

    def test_to_dict(self, synth_patch_cls):
        k = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        d = k.to_dict()
        assert d == {"pitch": 440, "velocity": 100, "attack": 0.5, "waveform": "sine"}

    def test_to_dict_is_copy(self, synth_patch_cls):
        k = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        d = k.to_dict()
        d["pitch"] = 9999
        assert k.pitch == 440

    def test_fingerprint_is_stable(self, synth_patch_cls):
        k = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        assert k.fingerprint() == k.fingerprint()

    def test_fingerprint_is_canonical_json(self, synth_patch_cls):
        k = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        fp = k.fingerprint()
        parsed = json.loads(fp)
        # keys should be sorted
        assert list(parsed.keys()) == sorted(parsed.keys())

    def test_different_values_different_fingerprint(self, synth_patch_cls):
        k1 = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        k2 = synth_patch_cls(pitch=880, velocity=100, attack=0.5, waveform="sine")
        assert k1.fingerprint() != k2.fingerprint()

    def test_same_values_same_fingerprint(self, synth_patch_cls):
        k1 = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        k2 = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        assert k1.fingerprint() == k2.fingerprint()


# ═══════════════════════════════════════════════════════════════════════
#  Equality / hashing
# ═══════════════════════════════════════════════════════════════════════


class TestEqualityAndHashing:
    """Test __eq__ and __hash__."""

    def test_equal_keys(self, synth_patch_cls):
        k1 = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        k2 = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        assert k1 == k2

    def test_unequal_keys(self, synth_patch_cls):
        k1 = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        k2 = synth_patch_cls(pitch=880, velocity=100, attack=0.5, waveform="sine")
        assert k1 != k2

    def test_different_types_not_equal(self):
        class A(Key):
            x = Param(min=0, max=1)

        class B(Key):
            x = Param(min=0, max=1)

        a = A(x=0.5)
        b = B(x=0.5)
        assert a != b

    def test_not_equal_to_non_key(self, synth_patch_cls):
        k = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        assert k != "not a key"

    def test_hash_consistency(self, synth_patch_cls):
        k1 = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        k2 = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        assert hash(k1) == hash(k2)

    def test_usable_in_set(self, synth_patch_cls):
        k1 = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        k2 = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        k3 = synth_patch_cls(pitch=880, velocity=100, attack=0.5, waveform="sine")
        s = {k1, k2, k3}
        assert len(s) == 2


# ═══════════════════════════════════════════════════════════════════════
#  repr
# ═══════════════════════════════════════════════════════════════════════


class TestKeyRepr:
    def test_repr_contains_class_name(self, synth_patch_cls):
        k = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        r = repr(k)
        assert "SynthPatch" in r

    def test_repr_contains_id(self, synth_patch_cls):
        k = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        assert k.id in repr(k)

    def test_repr_contains_values(self, synth_patch_cls):
        k = synth_patch_cls(pitch=440, velocity=100, attack=0.5, waveform="sine")
        r = repr(k)
        assert "pitch=440" in r
        assert "waveform='sine'" in r
