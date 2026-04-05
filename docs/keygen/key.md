> Structured parameter container with auto-validated fields.

---

## `Key`

Structured container for a generated parameter set.

Subclass and declare fields using `Param` (numeric),
`Enum` (categorical), or `Pool` (runtime-populated)
descriptors::

    class SynthPatch(Key):
        pitch     = Param(min=20, max=20000)
        velocity  = Param(min=0, max=127)
        attack    = Param(min=0.01, max=2.0)
        waveform  = Enum("sine", "saw", "square", "triangle")

Values are validated on assignment; out-of-bounds or invalid
choices raise `ValueError`::

    p = SynthPatch(pitch=440, velocity=100, attack=0.1, waveform="saw")
    p.pitch    = -5         # ValueError: pitch: -5 is below minimum 20
    p.waveform = "noise"    # ValueError: waveform: 'noise' is not one of (...)

Field specs are accessible on the class::

    SynthPatch.pitch.min           # 20
    SynthPatch.pitch.max           # 20000
    SynthPatch.waveform.options    # ("sine", "saw", "square", "triangle")
    len(SynthPatch.waveform)       # 4

---

### `field_specs(cls) → dict[str, Field]`

Return all declared field specifications.

---

### `to_dict() → dict[str, Any]`

Field values as a plain dict.

---

### `fingerprint() → str`

Canonical string for deduplication.
