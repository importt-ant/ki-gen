# API Reference

| Module | Public API | Description |
|---|---|---|
| [keygen](keygen.md) |  | keygen -- seeded parameter generation with deduplication and persistence. |
| [keygen.blueprint](keygen/blueprint.md) | `Blueprint` | Field randomization plan for building Key instances. |
| [keygen.fields](keygen/fields.md) |  | Field descriptors for declaring validated Key attributes. |
| [keygen.key](keygen/key.md) | `Key` | Structured parameter container with auto-validated fields. |
| [keygen.recorders](keygen/recorders.md) |  | Recording, deduplication, and generation machinery. |
| [keygen.rengines](keygen/rengines.md) |  | Pluggable RNG engines for key generation. |
| [keygen.store](keygen/store.md) | `Store` | SQLite persistence for generator state and key history. |
