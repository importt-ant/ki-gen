# API Reference

| Module | Public API | Description |
|---|---|---|
| [keygen](keygen.md) |  | keygen -- seeded parameter generation with deduplication and persistence. |
| [keygen.blueprint](keygen/blueprint.md) | `Blueprint` | Field randomization plan for building Key instances. |
| [keygen.fields](keygen/fields.md) | `Field`, `Parameter`, `Enum`, `Pool` |  |
| [keygen.key](keygen/key.md) | `Key` | Structured parameter container with auto-validated fields. |
| [keygen.recorders](keygen/recorders.md) | `Recorder`, `Generator` |  |
| [keygen.rengines](keygen/rengines.md) | `Rengine`, `RandomRengine`, `SobolRengine` |  |
| [keygen.store](keygen/store.md) | `Store` | SQLite persistence for generator state and key history. |
