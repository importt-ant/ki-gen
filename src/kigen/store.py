"""Backward-compatible re-export of :class:`dbstorr.Store`.

.. deprecated::
    Import directly from :mod:`dbstorr` instead::

        from dbstorr import Store
"""

from dbstorr.store import Store

__all__ = ["Store"]
