# 🧬❗: ki-gen

Generic seeded generator framework with dedup and SQLite persistence.

## Install

```bash
pip install ki-gen

# With Sobol quasi-random engine (optional)
pip install ki-gen[sobol]
```

Requires Python 3.12+.

## Quick start

```python
from kigen import Blueprint, Enum, Generator, Key, Param

# 1. Define a Key with typed fields
class SoundKey(Key):
    pitch       = Param(min=20, max=20_000)
    sample_rate = Param(min=8000, max=96_000)
    osc         = Enum("sine", "square", "sawtooth", "triangle")

# 2. Create a Blueprint — configure overrides or pin static values
bp = (
    Blueprint(SoundKey)
    .configure("sample_rate", 44_100)                   # always 44100
    .configure("pitch", Param(min=1000, max=2000))      # narrow range
)

# 3. Run the generator
gen = Generator(bp, seed=42)
key = gen.generate()
# SoundKey(id='...', pitch=1427, sample_rate=44100, osc='sine')
```

## Core concepts

### Key

A `Key` subclass is a structured parameter container. Declare fields using descriptors:

| Field   | Description |
|---------|-------------|
| `Param` | Numeric with optional `min`, `max`, `step`. Validated on assignment. |
| `Enum`  | Categorical — options fixed at class definition. |
| `Pool`  | Categorical — options populated once at runtime, then frozen. |
| `Field` | Abstract base — subclass for custom field types. |

```python
class ToneKey(Key):
    pitch     = Param(min=40, max=20_000)
    amplitude = Param(min=0.0, max=1.0, step=0.01)
    osc       = Enum("sine", "square", "sawtooth")

key = ToneKey(pitch=440, amplitude=0.8, osc="sine")
key.pitch = 99_999  # ValueError: above maximum
```

### Blueprint

A `Blueprint` describes *how* each field should be produced — narrowed bounds, restricted choices, or pinned to a static value. It's engine-agnostic and reusable.

```python
bp = Blueprint(ToneKey).configure("pitch", Param(min=200, max=800))
```

### Recorder

`Recorder` handles **dedup** and **persistence**. It can be used directly as a recorder:

```python
from kigen import Recorder, Store

with Store("my.db") as store:
    recorder = Recorder(name="api-ingest", store=store)

    key = ToneKey(pitch=440, amplitude=0.8, osc="sine")
    is_new = recorder.record(key)   # True (first time)
    is_dup = recorder.record(key)   # False (duplicate)
    recorder.flush()
```

### Generator

`Generator` combines a `Blueprint` with a pluggable **Rengine** (RNG engine) and adds the generate/dedup loop:

```python
from kigen import Generator, Store

with Store("my.db") as store:
    gen = Generator(bp, seed=42, store=store)
    keys = gen.generate_many(100)
    gen.flush()
```

### Rengine

The RNG engine protocol. Two built-in implementations:

| Engine | Description |
|--------|-------------|
| `RandomRengine` | stdlib `random.Random` — default when no engine is specified. |
| `SobolRengine` | Quasi-random Sobol sequence (requires `scipy`). O(1) fast-forward on resume. |

```python
from kigen import SobolRengine

gen = Generator(bp, seed=42, rengine=SobolRengine(seed=42, dimensions=8))
```

### Persistence

`Store` is a SQLite-backed store. Generators auto-resume from where they left off:

```python
with Store("my.db") as store:
    gen = Generator(bp, seed=42, store=store)
    keys = gen.generate_many(50)
    gen.flush()

# Later — resumes at key 51
with Store("my.db") as store:
    gen = Generator(bp, seed=42, store=store)
    more = gen.generate_many(50)
    gen.flush()
```

## Project structure

```
src/kigen/
├── __init__.py
├── blueprint.py          # Blueprint — field randomization plan
├── key.py                # Key — structured parameter container
├── store.py              # Store — SQLite persistence
├── fields/
│   ├── field.py          # Field (base descriptor)
│   ├── param.py          # Param (numeric min/max/step)
│   ├── enum.py           # Enum (categorical, class-time)
│   └── pool.py           # Pool (categorical, runtime-populated)
├── recorders/
│   ├── recorder.py       # Recorder (dedup + persistence)
│   └── generator.py      # Generator (generation loop)
└── rengines/
    ├── protocol.py       # Rengine protocol + FastForwardNotSupported
    ├── random.py          # RandomRengine (stdlib)
    └── sobol.py           # SobolRengine (scipy)
```

## API reference

See docs/index.md.