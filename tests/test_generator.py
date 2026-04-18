"""Tests for kigen.recorders.generator — generation loop, resume, dedup integration."""

from __future__ import annotations

import pytest

from kigen.blueprint import Blueprint
from kigen.fields import Enum, Param
from kigen.key import Key
from kigen.recorders import Generator, SpaceExhaustedError
from kigen.rengines import RandomRengine

from .conftest import MinimalKey, SynthPatch


# ═══════════════════════════════════════════════════════════════════════
#  Construction & identity
# ═══════════════════════════════════════════════════════════════════════


class TestGeneratorIdentity:
    def test_name_from_blueprint(self, synth_blueprint):
        gen = Generator(synth_blueprint, seed=42)
        assert gen.name == "SynthPatch"

    def test_gen_type_is_engine_class(self, synth_blueprint):
        gen = Generator(synth_blueprint, seed=42)
        assert gen.gen_type == "RandomRengine"

    def test_gen_key_format(self, synth_blueprint):
        gen = Generator(synth_blueprint, seed=42)
        assert gen.gen_key == "SynthPatch:RandomRengine:42"

    def test_seed_stored(self, synth_blueprint):
        gen = Generator(synth_blueprint, seed=99)
        assert gen.seed == 99

    def test_blueprint_accessible(self, synth_blueprint):
        gen = Generator(synth_blueprint, seed=42)
        assert gen.blueprint is synth_blueprint

    def test_rng_accessible(self, synth_blueprint):
        gen = Generator(synth_blueprint, seed=42)
        assert isinstance(gen.rng, RandomRengine)


# ═══════════════════════════════════════════════════════════════════════
#  generate (single)
# ═══════════════════════════════════════════════════════════════════════


class TestGenerateSingle:
    def test_returns_key(self, synth_blueprint):
        gen = Generator(synth_blueprint, seed=42)
        key = gen.generate()
        assert isinstance(key, SynthPatch)

    def test_increments_cursor(self, synth_blueprint):
        gen = Generator(synth_blueprint, seed=42)
        gen.generate()
        assert gen.cursor == 1

    def test_result_valid(self, synth_blueprint):
        gen = Generator(synth_blueprint, seed=42)
        key = gen.generate()
        assert 20 <= key.pitch <= 20000
        assert key.waveform in ("sine", "saw", "square", "triangle")

    def test_seeded_reproducibility(self, synth_patch_cls):
        bp = Blueprint(synth_patch_cls)
        g1 = Generator(bp, seed=42)
        g2 = Generator(bp, seed=42)
        k1 = g1.generate()
        k2 = g2.generate()
        assert k1 == k2


# ═══════════════════════════════════════════════════════════════════════
#  generate_many
# ═══════════════════════════════════════════════════════════════════════


class TestGenerateMany:
    def test_returns_correct_count(self, synth_blueprint):
        gen = Generator(synth_blueprint, seed=42)
        keys = gen.generate_many(10)
        assert len(keys) == 10

    def test_all_unique(self, synth_blueprint):
        gen = Generator(synth_blueprint, seed=42)
        keys = gen.generate_many(20)
        fingerprints = [k.fingerprint() for k in keys]
        assert len(set(fingerprints)) == len(fingerprints)

    def test_cursor_matches(self, synth_blueprint):
        gen = Generator(synth_blueprint, seed=42)
        gen.generate_many(15)
        assert gen.cursor == 15


# ═══════════════════════════════════════════════════════════════════════
#  Deduplication / space exhaustion
# ═══════════════════════════════════════════════════════════════════════


class TestGeneratorDedup:
    def test_space_exhaustion_on_tiny_space(self):
        """A 2-option enum with max 30 consecutive skips should exhaust quickly."""

        class TinyKey(Key):
            x = Enum("a", "b")

        bp = Blueprint(TinyKey)
        gen = Generator(bp, seed=42, max_consecutive_skips=30)

        # Generate the 2 unique keys
        keys = []
        keys.append(gen.generate())
        keys.append(gen.generate())
        assert len(keys) == 2

        # The next should exhaust the space
        with pytest.raises(SpaceExhaustedError):
            gen.generate()

    def test_dedup_across_generate_calls(self, synth_patch_cls):
        """Keys produced across separate generate() calls should not repeat."""
        bp = Blueprint(synth_patch_cls)
        gen = Generator(bp, seed=42)
        seen = set()
        for _ in range(10):
            key = gen.generate()
            fp = key.fingerprint()
            assert fp not in seen
            seen.add(fp)


# ═══════════════════════════════════════════════════════════════════════
#  Custom rengine
# ═══════════════════════════════════════════════════════════════════════


class TestGeneratorCustomRengine:
    def test_accepts_custom_rengine(self, synth_patch_cls):
        rng = RandomRengine(seed=99)
        bp = Blueprint(synth_patch_cls)
        gen = Generator(bp, rengine=rng)
        assert gen.rng is rng

    def test_custom_rengine_ignores_seed(self, synth_patch_cls):
        rng = RandomRengine(seed=99)
        bp = Blueprint(synth_patch_cls)
        gen = Generator(bp, seed=42, rengine=rng)
        assert gen.rng is rng  # rengine takes priority


# ═══════════════════════════════════════════════════════════════════════
#  Persistence / resume
# ═══════════════════════════════════════════════════════════════════════


class TestGeneratorPersistence:
    def test_flush_saves_to_store(self, synth_blueprint, tmp_store):
        gen = Generator(synth_blueprint, seed=42, store=tmp_store)
        gen.generate_many(5)
        gen.flush()

        row = tmp_store.load_generator_by_key(gen.gen_key)
        assert row is not None
        assert row["cursor"] == 5

    def test_runs_recorded(self, synth_blueprint, tmp_store):
        gen = Generator(synth_blueprint, seed=42, store=tmp_store)
        gen.generate_many(5)
        gen.flush()
        assert tmp_store.run_count(gen.gen_key) == 5

    def test_resume_continues_cursor(self, synth_patch_cls, tmp_store):
        bp = Blueprint(synth_patch_cls)
        g1 = Generator(bp, seed=42, store=tmp_store)
        g1.generate_many(5)
        g1.flush()

        g2 = Generator(bp, seed=42, store=tmp_store)
        assert g2.cursor == 5

    def test_resume_avoids_duplicates(self, synth_patch_cls, tmp_store):
        bp = Blueprint(synth_patch_cls)
        g1 = Generator(bp, seed=42, store=tmp_store)
        first_batch = g1.generate_many(5)
        g1.flush()

        fps_first = {k.fingerprint() for k in first_batch}

        g2 = Generator(bp, seed=42, store=tmp_store)
        second_batch = g2.generate_many(5)
        fps_second = {k.fingerprint() for k in second_batch}

        # No overlap between first and second batch
        assert fps_first.isdisjoint(fps_second)
