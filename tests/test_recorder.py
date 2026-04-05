"""Tests for keygen.recorders.recorder — dedup, flushing, persistence."""

from __future__ import annotations

import pytest

from keygen.recorders.recorder import Recorder, SpaceExhaustedError

from .conftest import SynthPatch


# ═══════════════════════════════════════════════════════════════════════
#  Construction & identity
# ═══════════════════════════════════════════════════════════════════════


class TestRecorderIdentity:
    def test_name_from_init(self):
        r = Recorder(name="test-session")
        assert r.name == "test-session"

    def test_name_missing_raises(self):
        r = Recorder()
        with pytest.raises(NotImplementedError, match="must either pass 'name'"):
            _ = r.name

    def test_gen_key_format(self):
        r = Recorder(name="demo")
        assert r.gen_key == "demo:recorder"

    def test_gen_type(self):
        r = Recorder(name="x")
        assert r.gen_type == "recorder"

    def test_initial_cursor_zero(self):
        r = Recorder(name="x")
        assert r.cursor == 0


# ═══════════════════════════════════════════════════════════════════════
#  Deduplication (in-memory)
# ═══════════════════════════════════════════════════════════════════════


class TestRecorderDedup:
    def test_accepts_new_key(self):
        r = Recorder(name="test")
        k = SynthPatch(pitch=440, velocity=100, attack=0.5, waveform="sine")
        assert r.record(k) is True

    def test_rejects_duplicate(self):
        r = Recorder(name="test")
        k1 = SynthPatch(pitch=440, velocity=100, attack=0.5, waveform="sine")
        k2 = SynthPatch(pitch=440, velocity=100, attack=0.5, waveform="sine")
        r.record(k1)
        assert r.record(k2) is False

    def test_accepts_different_keys(self):
        r = Recorder(name="test")
        k1 = SynthPatch(pitch=440, velocity=100, attack=0.5, waveform="sine")
        k2 = SynthPatch(pitch=880, velocity=100, attack=0.5, waveform="sine")
        assert r.record(k1) is True
        assert r.record(k2) is True

    def test_cursor_increments_on_accept(self):
        r = Recorder(name="test")
        k1 = SynthPatch(pitch=440, velocity=100, attack=0.5, waveform="sine")
        k2 = SynthPatch(pitch=880, velocity=100, attack=0.5, waveform="saw")
        r.record(k1)
        r.record(k2)
        assert r.cursor == 2

    def test_cursor_does_not_increment_on_reject(self):
        r = Recorder(name="test")
        k = SynthPatch(pitch=440, velocity=100, attack=0.5, waveform="sine")
        r.record(k)
        dup = SynthPatch(pitch=440, velocity=100, attack=0.5, waveform="sine")
        r.record(dup)
        assert r.cursor == 1


# ═══════════════════════════════════════════════════════════════════════
#  Flushing
# ═══════════════════════════════════════════════════════════════════════


class TestRecorderFlush:
    def test_flush_without_store_is_noop(self):
        r = Recorder(name="test")
        k = SynthPatch(pitch=440, velocity=100, attack=0.5, waveform="sine")
        r.record(k)
        r.flush()  # should not raise

    def test_auto_flush_triggered(self, tmp_store):
        r = Recorder(name="test", store=tmp_store, flush_interval=3)
        for i in range(4):
            k = SynthPatch(pitch=100 + i, velocity=50, attack=0.1, waveform="sine")
            r.record(k)
        # After 4 records with flush_interval=3, an auto-flush should have occurred.
        # Verify data is in the store.
        assert tmp_store.run_count(r.gen_key) >= 3

    def test_manual_flush(self, tmp_store):
        r = Recorder(name="test", store=tmp_store, flush_interval=100)
        k = SynthPatch(pitch=440, velocity=100, attack=0.5, waveform="sine")
        r.record(k)
        assert tmp_store.run_count(r.gen_key) == 0  # not yet flushed
        r.flush()
        assert tmp_store.run_count(r.gen_key) == 1


# ═══════════════════════════════════════════════════════════════════════
#  Persistence integration
# ═══════════════════════════════════════════════════════════════════════


class TestRecorderPersistence:
    def test_state_saved_on_flush(self, tmp_store):
        r = Recorder(name="persist", store=tmp_store)
        for i in range(5):
            k = SynthPatch(pitch=100 * (i + 1), velocity=50, attack=0.1, waveform="sine")
            r.record(k)
        r.flush()

        row = tmp_store.load_generator_by_key(r.gen_key)
        assert row is not None
        assert row["cursor"] == 5

    def test_resume_restores_cursor(self, tmp_store):
        r1 = Recorder(name="resume", store=tmp_store)
        for i in range(3):
            k = SynthPatch(pitch=100 * (i + 1), velocity=50, attack=0.1, waveform="sine")
            r1.record(k)
        r1.flush()

        r2 = Recorder(name="resume", store=tmp_store)
        assert r2.cursor == 3

    def test_resume_restores_seen_set(self, tmp_store):
        r1 = Recorder(name="seen", store=tmp_store)
        k = SynthPatch(pitch=440, velocity=100, attack=0.5, waveform="sine")
        r1.record(k)
        r1.flush()

        r2 = Recorder(name="seen", store=tmp_store)
        dup = SynthPatch(pitch=440, velocity=100, attack=0.5, waveform="sine")
        assert r2.record(dup) is False  # seen set was restored


# ═══════════════════════════════════════════════════════════════════════
#  SpaceExhaustedError
# ═══════════════════════════════════════════════════════════════════════


class TestSpaceExhausted:
    def test_default_handler_raises(self):
        r = Recorder(name="exhaust")
        with pytest.raises(SpaceExhaustedError, match="consecutive duplicates"):
            r._on_space_exhausted(30)

    def test_error_includes_gen_key(self):
        r = Recorder(name="x")
        with pytest.raises(SpaceExhaustedError, match="x:recorder"):
            r._on_space_exhausted(10)
