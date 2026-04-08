"""Tests for keygen.store — SQLite persistence, generator state, run history."""

from __future__ import annotations

import json

import pytest

from keygen.store import Store

from .conftest import SynthPatch


# ═══════════════════════════════════════════════════════════════════════
#  Construction
# ═══════════════════════════════════════════════════════════════════════


class TestStoreConstruction:
    def test_creates_db_file(self, tmp_path):
        db = tmp_path / "test.db"
        store = Store(db)
        assert db.exists()
        store.close()

    def test_creates_parent_dirs(self, tmp_path):
        db = tmp_path / "sub" / "dir" / "test.db"
        store = Store(db)
        assert db.exists()
        store.close()

    def test_default_path(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        store = Store()
        assert (tmp_path / "keygen.db").exists()
        store.close()

    def test_context_manager(self, tmp_path):
        db = tmp_path / "ctx.db"
        with Store(db) as store:
            assert store.db_path == db
        # After exiting, the connection should be closed.
        # Attempting operations on a closed connection raises.
        with pytest.raises(Exception):
            store._conn.execute("SELECT 1")


# ═══════════════════════════════════════════════════════════════════════
#  Generator state
# ═══════════════════════════════════════════════════════════════════════


class TestGeneratorState:
    def test_save_and_load(self, tmp_store):
        tmp_store.save_generator_by_key("gen:test:42", cursor=10)
        row = tmp_store.load_generator_by_key("gen:test:42")
        assert row is not None
        assert row["gen_key"] == "gen:test:42"
        assert row["cursor"] == 10

    def test_load_nonexistent(self, tmp_store):
        assert tmp_store.load_generator_by_key("missing") is None

    def test_upsert_updates_cursor(self, tmp_store):
        tmp_store.save_generator_by_key("gen:up:0", cursor=0)
        tmp_store.save_generator_by_key("gen:up:0", cursor=42)
        row = tmp_store.load_generator_by_key("gen:up:0")
        assert row["cursor"] == 42

    def test_state_extra_saved(self, tmp_store):
        extra = {"custom_field": "hello", "count": 99}
        tmp_store.save_generator_by_key("gen:ext:0", cursor=0, state_extra=extra)
        row = tmp_store.load_generator_by_key("gen:ext:0")
        assert row["state_extra"] == extra

    def test_state_extra_defaults_empty(self, tmp_store):
        tmp_store.save_generator_by_key("gen:def:0", cursor=0)
        row = tmp_store.load_generator_by_key("gen:def:0")
        assert row["state_extra"] == {}

    def test_list_generators(self, tmp_store):
        tmp_store.save_generator_by_key("b:gen:0", cursor=0)
        tmp_store.save_generator_by_key("a:gen:0", cursor=5)
        gens = tmp_store.list_generators()
        assert len(gens) == 2
        # Ordered by gen_key
        assert gens[0]["gen_key"] == "a:gen:0"
        assert gens[1]["gen_key"] == "b:gen:0"

    def test_timestamps_present(self, tmp_store):
        tmp_store.save_generator_by_key("gen:ts:0", cursor=0)
        row = tmp_store.load_generator_by_key("gen:ts:0")
        assert "created_at" in row
        assert "updated_at" in row


# ═══════════════════════════════════════════════════════════════════════
#  Run recording
# ═══════════════════════════════════════════════════════════════════════


class TestRunRecording:
    def _make_key(self, pitch=440):
        return SynthPatch(pitch=pitch, velocity=100, attack=0.5, waveform="sine")

    def test_record_run(self, tmp_store):
        k = self._make_key()
        tmp_store.record_run(k, "gen:x:0")
        assert tmp_store.run_count("gen:x:0") == 1

    def test_record_runs_batch(self, tmp_store):
        keys = [self._make_key(pitch=100 * i) for i in range(1, 6)]
        tmp_store.record_runs(keys, "gen:batch:0")
        assert tmp_store.run_count("gen:batch:0") == 5

    def test_duplicate_key_id_ignored(self, tmp_store):
        k = self._make_key()
        tmp_store.record_run(k, "gen:dup:0")
        tmp_store.record_run(k, "gen:dup:0")  # same key_id
        assert tmp_store.run_count("gen:dup:0") == 1

    def test_run_count_global(self, tmp_store):
        k1 = self._make_key(100)
        k2 = self._make_key(200)
        tmp_store.record_run(k1, "gen:a:0")
        tmp_store.record_run(k2, "gen:b:0")
        assert tmp_store.run_count() == 2

    def test_run_count_filtered(self, tmp_store):
        k1 = self._make_key(100)
        k2 = self._make_key(200)
        tmp_store.record_run(k1, "gen:a:0")
        tmp_store.record_run(k2, "gen:b:0")
        assert tmp_store.run_count("gen:a:0") == 1


# ═══════════════════════════════════════════════════════════════════════
#  Run retrieval
# ═══════════════════════════════════════════════════════════════════════


class TestRunRetrieval:
    def _make_key(self, pitch=440):
        return SynthPatch(pitch=pitch, velocity=100, attack=0.5, waveform="sine")

    def test_get_run(self, tmp_store):
        k = self._make_key()
        tmp_store.record_run(k, "gen:get:0")
        row = tmp_store.get_run(k.id)
        assert row is not None
        assert row["key_id"] == k.id
        assert row["params"]["pitch"] == 440

    def test_get_run_missing(self, tmp_store):
        assert tmp_store.get_run("nonexistent") is None

    def test_recent_runs(self, tmp_store):
        keys = [self._make_key(pitch=100 * i) for i in range(1, 6)]
        tmp_store.record_runs(keys, "gen:recent:0")
        recent = tmp_store.recent_runs(n=3, gen_key="gen:recent:0")
        assert len(recent) == 3

    def test_recent_runs_ordering(self, tmp_store):
        keys = [self._make_key(pitch=100 * i) for i in range(1, 4)]
        for k in keys:
            tmp_store.record_run(k, "gen:order:0")
        recent = tmp_store.recent_runs(n=10, gen_key="gen:order:0")
        # Most recent first (DESC)
        dates = [r["created_at"] for r in recent]
        assert dates == sorted(dates, reverse=True)

    def test_recent_runs_global(self, tmp_store):
        k1 = self._make_key(100)
        k2 = self._make_key(200)
        tmp_store.record_run(k1, "gen:a:0")
        tmp_store.record_run(k2, "gen:b:0")
        recent = tmp_store.recent_runs(n=10)
        assert len(recent) == 2

    def test_all_params(self, tmp_store):
        keys = [self._make_key(pitch=100 * i) for i in range(1, 4)]
        tmp_store.record_runs(keys, "gen:params:0")
        params = tmp_store.all_params("gen:params:0")
        assert len(params) == 3
        assert all("params" in p for p in params)

    def test_all_params_global(self, tmp_store):
        k1 = self._make_key(100)
        k2 = self._make_key(200)
        tmp_store.record_run(k1, "gen:a:0")
        tmp_store.record_run(k2, "gen:b:0")
        params = tmp_store.all_params()
        assert len(params) == 2


# ═══════════════════════════════════════════════════════════════════════
#  Fingerprint loading (dedup support)
# ═══════════════════════════════════════════════════════════════════════


class TestFingerprints:
    def _make_key(self, pitch=440):
        return SynthPatch(pitch=pitch, velocity=100, attack=0.5, waveform="sine")

    def test_load_seen_fingerprints(self, tmp_store):
        keys = [self._make_key(pitch=100 * i) for i in range(1, 4)]
        tmp_store.record_runs(keys, "gen:fp:0")
        fps = tmp_store.load_seen_fingerprints("gen:fp:0")
        assert len(fps) == 3

    def test_fingerprints_are_canonical_json(self, tmp_store):
        k = self._make_key()
        tmp_store.record_run(k, "gen:canon:0")
        fps = tmp_store.load_seen_fingerprints("gen:canon:0")
        for fp in fps:
            parsed = json.loads(fp)
            assert list(parsed.keys()) == sorted(parsed.keys())

    def test_empty_for_unknown_gen_key(self, tmp_store):
        fps = tmp_store.load_seen_fingerprints("nonexistent")
        assert fps == set()

    def test_fingerprints_match_key_fingerprint(self, tmp_store):
        k = self._make_key(pitch=440)
        tmp_store.record_run(k, "gen:match:0")
        fps = tmp_store.load_seen_fingerprints("gen:match:0")
        assert k.fingerprint() in fps
