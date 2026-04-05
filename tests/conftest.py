"""Shared fixtures for keygen test suite."""

from __future__ import annotations

import pytest

from keygen import Blueprint, Key, Store
from keygen.fields import Enum, Param, Pool


# ── Key subclasses used across tests ─────────────────────────────────


class SynthPatch(Key):
    """A typical Key with mixed field types."""

    pitch = Param(min=20, max=20000)
    velocity = Param(min=0, max=127)
    attack = Param(min=0.01, max=2.0)
    waveform = Enum("sine", "saw", "square", "triangle")


class SteppedKey(Key):
    """Key with a step-constrained Param."""

    level = Param(min=0, max=100, step=10)
    mode = Enum("a", "b")


class MinimalKey(Key):
    """Simplest possible Key — one field."""

    value = Param(min=0, max=1)


class PoolKey(Key):
    """Key that uses a Pool field."""

    sample = Pool()
    gain = Param(min=0.0, max=1.0)


class UnboundedParamKey(Key):
    """Key with a Param missing min or max (no auto-randomization)."""

    x = Param(min=0)


# ── Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def synth_patch_cls():
    """Return the SynthPatch class."""
    return SynthPatch


@pytest.fixture
def stepped_key_cls():
    """Return the SteppedKey class."""
    return SteppedKey


@pytest.fixture
def minimal_key_cls():
    """Return the MinimalKey class."""
    return MinimalKey


@pytest.fixture
def pool_key_cls():
    """Return the PoolKey class (pool NOT yet populated)."""
    return PoolKey


@pytest.fixture
def synth_blueprint(synth_patch_cls):
    """A default Blueprint for SynthPatch."""
    return Blueprint(synth_patch_cls)


@pytest.fixture
def tmp_store(tmp_path):
    """A Store backed by a temporary SQLite file."""
    db = tmp_path / "test.db"
    store = Store(db)
    yield store
    store.close()
