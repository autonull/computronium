"""The evidence store's public class, composed from its concern modules."""

from __future__ import annotations

from ._artifacts import _ArtifactMixin
from ._queries import _QueryMixin
from ._schema import _SchemaMixin
from ._transactions import _TransactionMixin


class RecordStore(  # ruff: ignore[too-many-public-methods] - single-writer topology concentrates the read/write API here by design (§1.1)
    _SchemaMixin,
    _TransactionMixin,
    _ArtifactMixin,
    _QueryMixin,
):
    """DuckDB-backed record store with single-writer guarantee.

    All writes flow through a single instance guarded by a threading.RLock.
    DuckDB allows one writer process; this design concentrates writes
    in the orchestrating process.

    Features:
    - Atomic record + artifact append (single transaction)
    - Vector retrieval (brute-force + optional HNSW via vss)
    - Pydantic v2 validation at I/O boundaries
    """
