"""Tests for keygen.rengines — RandomRengine, SobolRengine, protocol conformance."""

from __future__ import annotations

import pytest

from keygen.rengines import FastForwardNotSupported, RandomRengine, Rengine


# ═══════════════════════════════════════════════════════════════════════
#  RandomRengine
# ═══════════════════════════════════════════════════════════════════════


class TestRandomRengine:
    # ── construction ─────────────────────────────────────────────────

    def test_seed_stored(self):
        r = RandomRengine(seed=42)
        assert r.seed == 42

    def test_seed_none(self):
        r = RandomRengine()
        assert r.seed is None

    # ── randint ──────────────────────────────────────────────────────

    def test_randint_in_range(self):
        r = RandomRengine(seed=0)
        for _ in range(100):
            v = r.randint(0, 10)
            assert 0 <= v <= 10
            assert isinstance(v, int)

    def test_randint_single_value(self):
        r = RandomRengine(seed=0)
        assert r.randint(5, 5) == 5

    # ── uniform ──────────────────────────────────────────────────────

    def test_uniform_in_range(self):
        r = RandomRengine(seed=0)
        for _ in range(100):
            v = r.uniform(0.0, 1.0)
            assert 0.0 <= v < 1.0

    # ── choice ───────────────────────────────────────────────────────

    def test_choice_from_list(self):
        r = RandomRengine(seed=0)
        opts = ["a", "b", "c"]
        for _ in range(50):
            assert r.choice(opts) in opts

    def test_choice_from_tuple(self):
        r = RandomRengine(seed=0)
        opts = (1, 2, 3)
        for _ in range(50):
            assert r.choice(opts) in opts

    # ── sample ───────────────────────────────────────────────────────

    def test_sample_length(self):
        r = RandomRengine(seed=0)
        result = r.sample([1, 2, 3, 4, 5], 3)
        assert len(result) == 3

    def test_sample_unique(self):
        r = RandomRengine(seed=0)
        result = r.sample(list(range(100)), 10)
        assert len(set(result)) == 10

    def test_sample_subset(self):
        r = RandomRengine(seed=0)
        pop = [10, 20, 30, 40]
        result = r.sample(pop, 2)
        for v in result:
            assert v in pop

    # ── fast_forward ─────────────────────────────────────────────────

    def test_fast_forward_raises(self):
        r = RandomRengine(seed=0)
        with pytest.raises(FastForwardNotSupported):
            r.fast_forward(10)

    # ── reproducibility ──────────────────────────────────────────────

    def test_seeded_determinism(self):
        r1 = RandomRengine(seed=123)
        r2 = RandomRengine(seed=123)
        for _ in range(20):
            assert r1.randint(0, 1000) == r2.randint(0, 1000)

    def test_different_seeds_diverge(self):
        r1 = RandomRengine(seed=1)
        r2 = RandomRengine(seed=2)
        vals1 = [r1.randint(0, 10000) for _ in range(10)]
        vals2 = [r2.randint(0, 10000) for _ in range(10)]
        assert vals1 != vals2

    # ── repr ─────────────────────────────────────────────────────────

    def test_repr(self):
        assert repr(RandomRengine(seed=42)) == "RandomRengine(seed=42)"
        assert repr(RandomRengine()) == "RandomRengine(seed=None)"

    # ── protocol conformance ─────────────────────────────────────────

    def test_satisfies_rengine_protocol(self):
        assert isinstance(RandomRengine(seed=0), Rengine)


# ═══════════════════════════════════════════════════════════════════════
#  SobolRengine (requires scipy)
# ═══════════════════════════════════════════════════════════════════════

# Guard: skip the entire class if scipy is not installed.
scipy = pytest.importorskip("scipy")

from keygen.rengines import SobolRengine  # noqa: E402


class TestSobolRengine:
    # ── construction ─────────────────────────────────────────────────

    def test_seed_stored(self):
        s = SobolRengine(seed=42, dimensions=4)
        assert s.seed == 42

    # ── randint ──────────────────────────────────────────────────────

    def test_randint_in_range(self):
        s = SobolRengine(seed=0, dimensions=8)
        for _ in range(50):
            v = s.randint(0, 100)
            assert 0 <= v <= 100
            assert isinstance(v, int)

    # ── uniform ──────────────────────────────────────────────────────

    def test_uniform_in_range(self):
        s = SobolRengine(seed=0, dimensions=8)
        for _ in range(50):
            v = s.uniform(0.0, 10.0)
            assert 0.0 <= v <= 10.0

    # ── choice ───────────────────────────────────────────────────────

    def test_choice_from_seq(self):
        s = SobolRengine(seed=0, dimensions=4)
        opts = ("a", "b", "c", "d")
        for _ in range(50):
            assert s.choice(opts) in opts

    # ── sample ───────────────────────────────────────────────────────

    def test_sample_unique(self):
        s = SobolRengine(seed=0, dimensions=16)
        result = s.sample(list(range(20)), 5)
        assert len(result) == 5
        assert len(set(result)) == 5

    # ── fast_forward ─────────────────────────────────────────────────

    def test_fast_forward_does_not_raise(self):
        s = SobolRengine(seed=0, dimensions=4)
        s.fast_forward(10)  # should not raise

    def test_fast_forward_advances_state(self):
        s1 = SobolRengine(seed=42, dimensions=4)
        s2 = SobolRengine(seed=42, dimensions=4)

        # Fast-forward both by the same amount — they should stay in sync.
        s1.fast_forward(10)
        s2.fast_forward(10)

        assert s1.randint(0, 100) == s2.randint(0, 100)
        assert s1.uniform(0.0, 1.0) == s2.uniform(0.0, 1.0)

    def test_fast_forward_changes_output(self):
        s1 = SobolRengine(seed=42, dimensions=4)
        s2 = SobolRengine(seed=42, dimensions=4)

        # Without fast-forward they match
        assert s1.randint(0, 1000) == s2.randint(0, 1000)

        # After fast-forwarding one, they diverge
        s2.fast_forward(5)
        assert s1.randint(0, 1000) != s2.randint(0, 1000)

    # ── protocol conformance ─────────────────────────────────────────

    def test_satisfies_rengine_protocol(self):
        assert isinstance(SobolRengine(seed=0, dimensions=2), Rengine)

    # ── repr ─────────────────────────────────────────────────────────

    def test_repr(self):
        r = repr(SobolRengine(seed=42, dimensions=8))
        assert "SobolRengine" in r
        assert "seed=42" in r
        assert "dimensions=8" in r
