"""CEECStore facade composed from the records/query mixins."""

from __future__ import annotations

from ceec.store.base import StoreBase
from ceec.store.query import QueryMixin
from ceec.store.records import RecordsMixin


class CEECStore(RecordsMixin, QueryMixin, StoreBase):
    """Transactional, append-only CEEC ledger."""
