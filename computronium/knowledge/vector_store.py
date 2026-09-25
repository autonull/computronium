"""
Vector store and embedding utilities for the knowledge base.

Provides FAISS-based semantic search with scikit-learn fallback.
"""

import json
import pathlib
import sqlite3
from dataclasses import dataclass
from enum import Enum

import numpy as np

from computronium.core._paths import db_path
from computronium.core.logging import get_logger

# Optional dependencies for vector search
try:
    import faiss

    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

try:
    from sklearn.neighbors import NearestNeighbors

    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    from sentence_transformers import SentenceTransformer

    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

logger = get_logger()


class VectorBackend(Enum):
    """Available vector search backends."""

    FAISS = "faiss"
    SKLEARN = "sklearn"
    NONE = "none"


@dataclass(frozen=True, slots=True)
class VectorStoreConfig:
    """Configuration for the vector store."""

    vector_dim: int = 384
    embedding_model: str = "all-MiniLM-L6-v2"
    auto_embed: bool = True


class VectorStore:
    """
    Vector store for semantic similarity search.

    Uses FAISS when available, falls back to scikit-learn NearestNeighbors,
    and finally to keyword search.
    """

    def __init__(
        self,
        db_path: str = db_path("computronium_kb.db"),
        config: VectorStoreConfig | None = None,
    ):
        self.db_path = db_path
        self.config = config or VectorStoreConfig()

        # Initialize vector index
        self._init_vector_index()

        # Try to load persisted index
        self.load_persisted()

        # Initialize embedding model
        self.embedding_model = None
        if self.config.auto_embed and HAS_SENTENCE_TRANSFORMERS:
            try:
                self.embedding_model = SentenceTransformer(self.config.embedding_model)
                logger.info("Loaded embedding model: %s", self.config.embedding_model)
            except (OSError, RuntimeError, ValueError) as e:
                logger.warning("Failed to load embedding model: %s", e)

    def _init_vector_index(self) -> None:
        """Initialize vector index with best available backend."""
        if HAS_FAISS:
            self.backend = VectorBackend.FAISS
            self._vector_index = faiss.IndexFlatIP(self.config.vector_dim)
            self.vector_ids = []
            logger.info("Initialized FAISS vector index")
        elif HAS_SKLEARN:
            self.backend = VectorBackend.SKLEARN
            self._init_sklearn_index()
            logger.info("Initialized scikit-learn NearestNeighbors index")
        else:
            self.backend = VectorBackend.NONE
            self._vector_index = None
            self.vector_ids = []
            logger.warning(
                "No vector search backend available. "
                "Install 'faiss-cpu' or 'scikit-learn' for semantic search."
            )

    def _init_sklearn_index(self) -> None:
        """Initialize scikit-learn NearestNeighbors index."""
        self._vectors = np.empty((0, self.config.vector_dim), dtype=np.float32)
        self._ids = []
        self._nn = None

    def _embed_text(self, text: str) -> np.ndarray | None:
        """Generate embedding for text."""
        if self.embedding_model is None:
            return None
        try:
            embedding = self.embedding_model.encode(text, normalize_embeddings=True)
            return embedding.astype(np.float32)
        except (OSError, RuntimeError, ValueError) as e:
            logger.warning("Embedding failed: %s", e)
            return None

    def add_embedding(self, entry_id: str, embedding: list[float] | np.ndarray) -> None:
        """Add an embedding to the vector index."""
        if self.backend == VectorBackend.NONE:
            return

        emb = np.array(embedding, dtype=np.float32).reshape(1, -1)

        if self.backend == VectorBackend.FAISS:
            self.vector_index.add(emb)
            self.vector_ids.append(entry_id)
        elif self.backend == VectorBackend.SKLEARN:
            self._vectors = np.vstack([self._vectors, emb])
            self._ids.append(entry_id)
            # Refit index (inefficient for many adds, but OK for <10k vectors)
            n_neighbors = min(10, len(self._ids))
            self._nn = NearestNeighbors(n_neighbors=n_neighbors, metric="cosine")
            self._nn.fit(self._vectors)

    def search(
        self,
        query: str,
        k: int = 10,
        min_similarity: float = 0.5,
        filters: dict[str, object] | None = None,
    ) -> list[tuple[str, float]]:
        """
        Semantic search using vector embeddings.

        Returns list of (entry_id, similarity_score) tuples.
        """
        if self.backend == VectorBackend.NONE or self.embedding_model is None:
            logger.warning(
                "Vector search not available. Falling back to keyword search."
            )
            return self._keyword_search(query, k, min_similarity)

        # Generate query embedding
        query_embedding = self._embed_text(query)
        if query_embedding is None:
            return []

        query_embedding = query_embedding.reshape(1, -1)

        if self.backend == VectorBackend.FAISS:
            return self._search_faiss(query_embedding, k, min_similarity)
        elif self.backend == VectorBackend.SKLEARN:
            return self._search_sklearn(query_embedding, k, min_similarity)

        return []

    def _search_faiss(
        self, query_embedding: np.ndarray, k: int, min_similarity: float
    ) -> list[tuple[str, float]]:
        """Search using FAISS index."""
        scores, indices = self.vector_index.search(
            query_embedding, min(k * 2, len(self.vector_ids))
        )

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if 0 <= idx < len(self.vector_ids):
                if score >= min_similarity:
                    entry_id = self.vector_ids[idx]
                    results.append((entry_id, float(score)))
                    if len(results) >= k:
                        break
        return results

    def _search_sklearn(
        self, query_embedding: np.ndarray, k: int, min_similarity: float
    ) -> list[tuple[str, float]]:
        """Search using scikit-learn NearestNeighbors."""
        if self._nn is None or len(self._ids) == 0:
            return []

        # sklearn returns distances, we need similarity (1 - distance for cosine)
        distances, indices = self._nn.kneighbors(
            query_embedding, n_neighbors=min(k, len(self._ids))
        )

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self._ids):
                similarity = 1.0 - float(dist)  # cosine distance to similarity
                if similarity >= min_similarity:
                    entry_id = self._ids[idx]
                    results.append((entry_id, similarity))
        return results

    def _keyword_search(
        self, query: str, k: int, min_similarity: float
    ) -> list[tuple[str, float]]:
        """Term-overlap fallback over the knowledge table when FAISS/embeddings
        are unavailable. Score is the fraction of query terms present in the
        entry's searchable text."""
        terms = query.lower().split()
        if not terms:
            return []
        try:
            with sqlite3.connect(self.db_path) as conn:
                rows = conn.execute(
                    "SELECT rowid, id, topic, model_family, finding, details, tags"
                    " FROM knowledge"
                ).fetchall()
        except sqlite3.OperationalError as e:
            logger.warning("Keyword search failed: %s", e)
            return []
        results: list[tuple[int, str, float]] = []
        for rowid, entry_id, *text_fields in rows:
            text = " ".join(str(field) for field in text_fields if field).lower()
            score = sum(term in text for term in terms) / len(terms)
            if score >= min_similarity:
                results.append((rowid, entry_id, score))
        return [
            (entry_id, score)
            for _, entry_id, score in sorted(results, key=lambda r: (-r[2], -r[0]))
        ][:k][:k]

    def get_stats(self) -> dict[str, object]:
        """Get vector store statistics."""
        return {
            "backend": self.backend.value,
            "vector_index_size": len(self.vector_ids)
            if self.backend == VectorBackend.FAISS
            else len(self._ids) if self.backend == VectorBackend.SKLEARN else 0,
            "has_embeddings": self.embedding_model is not None,
            "embedding_model": self.config.embedding_model,
            "vector_dim": self.config.vector_dim,
        }

    @property
    def vector_index(self):
        """Backward compatibility: return FAISS index or None."""
        if self.backend == VectorBackend.FAISS:
            return self._vector_index if hasattr(self, '_vector_index') else None
        return None

    @vector_index.setter
    def vector_index(self, value):
        """Backward compatibility setter for FAISS index."""
        if self.backend == VectorBackend.FAISS:
            self._vector_index = value
            if hasattr(self, 'vector_ids'):
                pass  # Already initialized

    def persist(self) -> None:
        """Persist vector index to disk."""
        if self.backend == VectorBackend.FAISS and self.vector_index is not None:
            index_path = pathlib.Path(self.db_path).with_suffix(".faiss")
            faiss.write_index(self.vector_index, str(index_path))
            ids_path = pathlib.Path(self.db_path).with_suffix(".faiss_ids.json")
            with ids_path.open("w") as f:
                json.dump(self.vector_ids, f)
        elif self.backend == VectorBackend.SKLEARN and self._vectors.size > 0:
            index_path = pathlib.Path(self.db_path).with_suffix(".sklearn.npz")
            ids_path = pathlib.Path(self.db_path).with_suffix(".sklearn_ids.json")
            np.savez_compressed(index_path, vectors=self._vectors)
            with ids_path.open("w") as f:
                json.dump(self._ids, f)

    def load_persisted(self) -> bool:
        """Load persisted vector index from disk."""
        # Try FAISS first
        if HAS_FAISS:
            index_path = pathlib.Path(self.db_path).with_suffix(".faiss")
            ids_path = pathlib.Path(self.db_path).with_suffix(".faiss_ids.json")
            if index_path.exists() and ids_path.exists():
                try:
                    self.backend = VectorBackend.FAISS
                    self.vector_index = faiss.read_index(str(index_path))
                    with ids_path.open() as f:
                        self.vector_ids = json.load(f)
                    logger.info(
                        "Loaded persisted FAISS index with %d vectors",
                        len(self.vector_ids),
                    )
                    return True
                except (OSError, RuntimeError, ValueError) as e:
                    logger.warning("Failed to load FAISS index: %s", e)

        # Try sklearn
        if HAS_SKLEARN:
            index_path = pathlib.Path(self.db_path).with_suffix(".sklearn.npz")
            ids_path = pathlib.Path(self.db_path).with_suffix(".sklearn_ids.json")
            if index_path.exists() and ids_path.exists():
                try:
                    self.backend = VectorBackend.SKLEARN
                    data = np.load(index_path)
                    self._vectors = data["vectors"]
                    with ids_path.open() as f:
                        self._ids = json.load(f)
                    # Refit the index
                    n_neighbors = min(10, len(self._ids))
                    self._nn = NearestNeighbors(n_neighbors=n_neighbors, metric="cosine")
                    self._nn.fit(self._vectors)
                    logger.info(
                        "Loaded persisted sklearn index with %d vectors",
                        len(self._ids),
                    )
                    return True
                except (OSError, RuntimeError, ValueError) as e:
                    logger.warning("Failed to load sklearn index: %s", e)

        return False


__all__ = [
    "HAS_FAISS",
    "HAS_SKLEARN",
    "HAS_SENTENCE_TRANSFORMERS",
    "VectorBackend",
    "VectorStore",
    "VectorStoreConfig",
]
