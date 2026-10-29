"""Atomic artifact append and vector retrieval for the evidence store."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import duckdb

from computronium.experiment.schema.record import Record

from ._base import _StoreBase
from ._models import DuplicateMeasurementError, StoreError

if TYPE_CHECKING:
    from computronium.experiment.evidence.artifacts import ArtifactInput


class _ArtifactMixin(_StoreBase):
    _conn: duckdb.DuckDBPyConnection | None
    _write_lock: Any
    _artifact_store: Any

    def append_with_artifacts(
        self, record: Record, artifacts: list[ArtifactInput]
    ) -> Record:
        """Atomic append: record + all artifacts in single transaction.

        Args:
            record: The record to append
            artifacts: List of ArtifactInput objects

        Returns:
            Record with assigned seq

        Raises:
            DuplicateMeasurementError: If measurement_key already exists
            StoreError: On any storage failure (transaction rolled back)
        """
        if self._conn is None:
            raise StoreError("Connection not initialized")
        if self._artifact_store is None:
            raise StoreError("Artifact store not initialized")

        with self._write_lock:
            self._conn.execute("BEGIN")
            try:
                # Insert record
                self._conn.execute(
                    """
                    INSERT INTO records (
                        record_id, run_id, schema_version, cell_key, measurement_key,
                        substrate, geometry, dynamics, plasticity, credit, update,
                        params, schedule, provenance, status, payload, unknown,
                        effective_params
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        record.record_id,
                        record.run_id,
                        record.schema_version,
                        record.cell_key,
                        record.measurement_key,
                        record.substrate,
                        record.geometry,
                        record.dynamics,
                        record.plasticity,
                        record.credit,
                        record.update,
                        json.dumps(record.params),
                        {
                            "fidelity": record.schedule.fidelity,
                            "seed": record.schedule.seed,
                            "n_seeds": record.schedule.n_seeds,
                            "epochs": record.schedule.epochs,
                            "batch_limit": record.schedule.batch_limit,
                            "budget_id": record.schedule.budget_id,
                            "task_id": record.schedule.task_id,
                            "param_budget": record.schedule.param_budget,
                        },
                        json.dumps(record.provenance.to_dict()),
                        {
                            "gate_verdict": record.status.gate_verdict.value,
                            "defect": record.status.defect,
                            "cause": record.status.cause.value,
                            "severity": record.status.severity.value,
                            "quarantine": record.status.quarantine,
                            "maturity": record.status.maturity.value,
                            "uncertainty": json.dumps(record.status.uncertainty),
                            "reproducibility": record.status.reproducibility.value,
                            "assessment_procedure_version": record.status.assessment_procedure_version,
                            "ceec_link": record.status.ceec_link,
                        },
                        json.dumps(record.payload),
                        json.dumps(record.unknown) if record.unknown else None,
                        json.dumps(record.effective_params),
                    ],
                )

                # Store artifacts
                for art_input in artifacts:
                    self._artifact_store.put(art_input, record.record_id)

                self._conn.execute("COMMIT")

            except duckdb.ConstraintException as e:
                self._conn.execute("ROLLBACK")
                if "measurement_key" in str(e) or "record_id" in str(e):
                    raise DuplicateMeasurementError(record.measurement_key) from e
                raise StoreError(f"Constraint violation: {e}") from e
            except Exception:
                self._conn.execute("ROLLBACK")
                raise

            # Fetch the assigned seq and return updated record (inside lock for thread safety)
            result = self._conn.execute(
                "SELECT seq FROM records WHERE record_id = ?", [record.record_id]
            ).fetchone()

            if result is None:
                raise StoreError("Failed to retrieve seq after insert")

            # A reader in another process cannot open this store: publish the
            # picture for it.
            self._publish_mirror()

            return Record(
                record_id=record.record_id,
                seq=result[0],
                run_id=record.run_id,
                schema_version=record.schema_version,
                cell_key=record.cell_key,
                measurement_key=record.measurement_key,
                substrate=record.substrate,
                geometry=record.geometry,
                dynamics=record.dynamics,
                plasticity=record.plasticity,
                credit=record.credit,
                update=record.update,
                params=record.params,
                effective_params=record.effective_params,
                schedule=record.schedule,
                provenance=record.provenance,
                status=record.status,
                payload=record.payload,
                unknown=record.unknown,
            )

    def add_embedding(
        self,
        record_id: str,
        embedding: list[float],
        version: int = 1,
    ) -> None:
        """Add or update a vector embedding for a record."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        if len(embedding) != 384:
            raise ValueError(f"Embedding must be 384-dimensional, got {len(embedding)}")

        with self._write_lock:
            self._conn.execute(
                """
                INSERT INTO vector_index (record_id, embedding, embedding_version)
                VALUES (?, ?, ?)
                ON CONFLICT (record_id) DO UPDATE SET
                    embedding = EXCLUDED.embedding,
                    embedding_version = EXCLUDED.embedding_version
                """,
                [record_id, embedding, version],
            )

    def get_embedding(self, record_id: str) -> list[float] | None:
        """Get embedding for a record."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        row = self._conn.execute(
            "SELECT embedding FROM vector_index WHERE record_id = ?", [record_id]
        ).fetchone()
        return list(row[0]) if row else None

    def vector_search_brute_force(
        self,
        query_embedding: list[float],
        k: int = 10,
        metric: str = "cosine",
        filter_run_id: str | None = None,
    ) -> list[tuple[Record, float]]:
        """Brute-force vector search using DuckDB's array operations.

        Args:
            query_embedding: Query vector (384-dim)
            k: Number of results to return
            metric: "cosine" or "dot"
            filter_run_id: Optional run_id to restrict search

        Returns:
            List of (Record, score) tuples, highest score first
        """
        if self._conn is None:
            raise StoreError("Connection not initialized")
        if len(query_embedding) != 384:
            raise ValueError(
                f"Embedding must be 384-dimensional, got {len(query_embedding)}"
            )

        # Build filter
        where_clause = ""
        params: list[Any] = []
        if filter_run_id:
            where_clause = "WHERE r.run_id = ?"
            params.append(filter_run_id)

        if metric == "cosine":
            score_expr = (
                "list_dot(vi.embedding, ?) / (list_norm(vi.embedding) * list_norm(?))"
            )
            params.extend([query_embedding, query_embedding])
        else:
            # Dot product
            score_expr = "list_dot(vi.embedding, ?)"
            params.append(query_embedding)

        query = f"""
            SELECT r.*, {score_expr} AS score
            FROM records r
            JOIN vector_index vi ON r.record_id = vi.record_id
            {where_clause}
            ORDER BY score DESC
            LIMIT ?
        """
        params.append(k)

        rows = self._conn.execute(query, params).fetchall()
        return [(self._row_to_record(row[:-1]), row[-1]) for row in rows]

    def vector_search_hnsw(
        self,
        query_embedding: list[float],
        k: int = 10,
        filter_run_id: str | None = None,
    ) -> list[tuple[Record, float]]:
        """HNSW vector search via DuckDB vss extension (experimental).

        Falls back to brute-force if vss not available.

        Args:
            query_embedding: Query vector (384-dim)
            k: Number of results to return
            filter_run_id: Optional run_id to restrict search

        Returns:
            List of (Record, score) tuples, highest score first
        """
        if self._conn is None:
            raise StoreError("Connection not initialized")

        # Check if vss extension is available
        try:
            self._conn.execute("LOAD vss")
        except duckdb.CatalogException:
            # Fall back to brute force
            return self.vector_search_brute_force(
                query_embedding, k, "cosine", filter_run_id
            )

        where_clause = ""
        params = [query_embedding, k]
        if filter_run_id:
            where_clause = "AND r.run_id = ?"
            params.append(filter_run_id)

        query = f"""
            SELECT r.*, vi.embedding <=> ? AS distance
            FROM records r
            JOIN vector_index vi ON r.record_id = vi.record_id
            WHERE 1=1 {where_clause}
            ORDER BY distance ASC
            LIMIT ?
        """

        try:
            rows = self._conn.execute(query, params).fetchall()
            # Convert distance to similarity score (1 - distance for cosine)
            return [(self._row_to_record(row[:-1]), 1.0 - row[-1]) for row in rows]
        except Exception:
            # Fall back on any error
            return self.vector_search_brute_force(
                query_embedding, k, "cosine", filter_run_id
            )

    def vector_search(
        self,
        query_embedding: list[float],
        k: int = 10,
        metric: str = "cosine",
        filter_run_id: str | None = None,
        use_hnsw: bool = False,
    ) -> list[tuple[Record, float]]:
        """Unified vector search interface.

        Args:
            query_embedding: Query vector (384-dim)
            k: Number of results
            metric: "cosine" or "dot" (for brute force)
            filter_run_id: Optional run filter
            use_hnsw: Try HNSW first (requires vss extension)

        Returns:
            List of (Record, score) tuples
        """
        if use_hnsw:
            return self.vector_search_hnsw(query_embedding, k, filter_run_id)
        return self.vector_search_brute_force(query_embedding, k, metric, filter_run_id)

    def _import_artifacts(self, artifacts_data: list[dict[str, Any]]) -> int:
        """Import artifact manifests from snapshot data. Returns count imported."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        count = 0
        for artifact_data in artifacts_data:
            digest = artifact_data["digest"]
            existing = self._conn.execute(
                "SELECT digest FROM artifacts WHERE digest = ?", [digest]
            ).fetchone()
            if existing is None:
                self._conn.execute(
                    """
                    INSERT INTO artifacts (
                        digest, role, record_id, created_at,
                        external_uri, external_size, external_checksum
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        digest,
                        artifact_data["role"],
                        artifact_data["record_id"],
                        artifact_data.get("created_at"),
                        artifact_data.get("external_uri"),
                        artifact_data.get("external_size"),
                        artifact_data.get("external_checksum"),
                    ],
                )
                count += 1
        return count

    def _import_vector_index(self, vectors_data: list[dict[str, Any]]) -> int:
        """Import vector index from snapshot data. Returns count imported."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        count = 0
        for vector_data in vectors_data:
            record_id = vector_data["record_id"]
            existing = self._conn.execute(
                "SELECT record_id FROM vector_index WHERE record_id = ?", [record_id]
            ).fetchone()
            if existing is None:
                self._conn.execute(
                    """
                    INSERT INTO vector_index (record_id, embedding, embedding_version)
                    VALUES (?, ?, ?)
                    """,
                    [
                        record_id,
                        vector_data["embedding"],
                        vector_data["embedding_version"],
                    ],
                )
                count += 1
        return count
