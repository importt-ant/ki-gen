"""dbstorr -- SQLite persistence for generator state and run history.

Provides a :class:`Store` backed by SQLite for persisting generator
cursors and recording generated parameter sets.  Any object satisfying
the :class:`Storable` protocol can be recorded — no dependency on a
particular Key implementation.

Typical usage::

    from dbstorr import Store

    with Store("runs.db") as store:
        store.save_generator_by_key("my-gen:rng:42", cursor=10)
        store.record_run(some_storable, "my-gen:rng:42")
"""

from .protocols import Storable
from .store import Store

__all__ = [
    "Storable",
    "Store",
]

__version__ = "1.0.0"
