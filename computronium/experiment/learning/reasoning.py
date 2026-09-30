"""Reasoning and literature records for the learning system.

Implements WP6 deliverable: hypothesis/literature records with mandatory provenance linkage (R57, Q15).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

from computronium.experiment.schema.coordinate import Coordinate


class HypothesisStatus(StrEnum):
    """Status of a hypothesis in the reasoning system."""

    PROPOSED = "proposed"  # Newly proposed, not yet tested
    TESTING = "testing"  # Currently being evaluated
    SUPPORTED = "supported"  # Evidence supports the hypothesis
    REJECTED = "rejected"  # Evidence contradicts the hypothesis
    INCONCLUSIVE = "inconclusive"  # Insufficient evidence either way
    SUPERSEDED = "superseded"  # Replaced by a better hypothesis


class HypothesisType(StrEnum):
    """Type of hypothesis."""

    MECHANISTIC = (
        "mechanistic"  # Why a mechanism works (e.g., "credit X works because...")
    )
    COMPARATIVE = (
        "comparative"  # A vs B (e.g., "update X outperforms update Y on task Z")
    )
    INTERACTION = (
        "interaction"  # Axis interaction (e.g., "dynamics D × credit C synergy")
    )
    SCALING = "scaling"  # Scaling law (e.g., "performance scales with compute as...")
    TRANSFER = (
        "transfer"  # Transfer learning (e.g., "knowledge from task A helps task B")
    )


class LiteratureType(StrEnum):
    """Type of literature reference."""

    PAPER = "paper"
    PREPRINT = "preprint"
    BLOG = "blog"
    DOCUMENTATION = "documentation"
    CODE = "code"
    INTERNAL = "internal"  # Internal notes/experiments


@dataclass(frozen=True, slots=True)
class ProvenanceLink:
    """Mandatory provenance linkage for hypotheses and literature (R57, Q15)."""

    # Source record IDs that support/refute this
    supporting_records: frozenset[str] = field(default_factory=frozenset)
    contradicting_records: frozenset[str] = field(default_factory=frozenset)

    # Related hypotheses/literature
    related_hypotheses: frozenset[str] = field(default_factory=frozenset)
    related_literature: frozenset[str] = field(default_factory=frozenset)

    # Human/agent who proposed this
    author: str = ""
    # Timestamp
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    # Code/commit hash for reproducibility
    code_hash: str = ""
    # Experiment/run ID
    run_id: str = ""

    def __post_init__(self) -> None:
        if not self.author:
            raise ValueError("author is required for provenance")
        if not self.code_hash:
            raise ValueError("code_hash is required for provenance")

    def add_support(self, record_id: str) -> ProvenanceLink:
        """Return new link with added supporting record."""
        return ProvenanceLink(
            supporting_records=self.supporting_records | {record_id},
            contradicting_records=self.contradicting_records,
            related_hypotheses=self.related_hypotheses,
            related_literature=self.related_literature,
            author=self.author,
            created_at=self.created_at,
            code_hash=self.code_hash,
            run_id=self.run_id,
        )

    def add_contradiction(self, record_id: str) -> ProvenanceLink:
        """Return new link with added contradicting record."""
        return ProvenanceLink(
            supporting_records=self.supporting_records,
            contradicting_records=self.contradicting_records | {record_id},
            related_hypotheses=self.related_hypotheses,
            related_literature=self.related_literature,
            author=self.author,
            created_at=self.created_at,
            code_hash=self.code_hash,
            run_id=self.run_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "supporting_records": sorted(self.supporting_records),
            "contradicting_records": sorted(self.contradicting_records),
            "related_hypotheses": sorted(self.related_hypotheses),
            "related_literature": sorted(self.related_literature),
            "author": self.author,
            "created_at": self.created_at,
            "code_hash": self.code_hash,
            "run_id": self.run_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProvenanceLink:
        return cls(
            supporting_records=frozenset(data.get("supporting_records", [])),
            contradicting_records=frozenset(data.get("contradicting_records", [])),
            related_hypotheses=frozenset(data.get("related_hypotheses", [])),
            related_literature=frozenset(data.get("related_literature", [])),
            author=data.get("author", ""),
            created_at=data.get("created_at", datetime.now().isoformat()),
            code_hash=data.get("code_hash", ""),
            run_id=data.get("run_id", ""),
        )


@dataclass(frozen=True, slots=True)
class Hypothesis:
    """A scientific hypothesis about learning mechanisms.

    Every hypothesis must have mandatory provenance linkage (R57, Q15).
    """

    hypothesis_id: str  # Content hash of statement + metadata
    statement: str  # Natural language statement
    hypothesis_type: HypothesisType
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    # Provenance linkage (mandatory)
    provenance: ProvenanceLink = field(default_factory=ProvenanceLink)
    # Structured prediction (if applicable)
    predicted_coordinate: Coordinate | None = None
    predicted_metric: str = ""  # e.g., "val_accuracy"
    predicted_value: float | None = None
    predicted_direction: str = ""  # "increase", "decrease", "no_change"
    # Confidence (0-1)
    confidence: float = 0.5
    # Tags for categorization
    tags: frozenset[str] = field(default_factory=frozenset)
    # Updated timestamp
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self) -> None:
        if not self.hypothesis_id:
            # Generate from content
            content = {
                "statement": self.statement,
                "type": self.hypothesis_type.value,
                "provenance": self.provenance.to_dict(),
            }
            object.__setattr__(
                self,
                "hypothesis_id",
                hashlib.sha256(
                    json.dumps(content, sort_keys=True).encode()
                ).hexdigest()[:16],
            )

        if not isinstance(self.provenance, ProvenanceLink):
            raise TypeError("provenance must be a ProvenanceLink")

        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be in [0, 1]")

    def with_status(self, status: HypothesisStatus) -> Hypothesis:
        """Return new hypothesis with updated status."""
        return Hypothesis(
            hypothesis_id=self.hypothesis_id,
            statement=self.statement,
            hypothesis_type=self.hypothesis_type,
            status=status,
            provenance=self.provenance,
            predicted_coordinate=self.predicted_coordinate,
            predicted_metric=self.predicted_metric,
            predicted_value=self.predicted_value,
            predicted_direction=self.predicted_direction,
            confidence=self.confidence,
            tags=self.tags,
            updated_at=datetime.now().isoformat(),
        )

    def with_confidence(self, confidence: float) -> Hypothesis:
        """Return new hypothesis with updated confidence."""
        return Hypothesis(
            hypothesis_id=self.hypothesis_id,
            statement=self.statement,
            hypothesis_type=self.hypothesis_type,
            status=self.status,
            provenance=self.provenance,
            predicted_coordinate=self.predicted_coordinate,
            predicted_metric=self.predicted_metric,
            predicted_value=self.predicted_value,
            predicted_direction=self.predicted_direction,
            confidence=confidence,
            tags=self.tags,
            updated_at=datetime.now().isoformat(),
        )

    def add_supporting_record(self, record_id: str) -> Hypothesis:
        """Return new hypothesis with added supporting record."""
        new_provenance = self.provenance.add_support(record_id)
        return Hypothesis(
            hypothesis_id=self.hypothesis_id,
            statement=self.statement,
            hypothesis_type=self.hypothesis_type,
            status=self.status,
            provenance=new_provenance,
            predicted_coordinate=self.predicted_coordinate,
            predicted_metric=self.predicted_metric,
            predicted_value=self.predicted_value,
            predicted_direction=self.predicted_direction,
            confidence=self.confidence,
            tags=self.tags,
            updated_at=datetime.now().isoformat(),
        )

    def add_contradicting_record(self, record_id: str) -> Hypothesis:
        """Return new hypothesis with added contradicting record."""
        new_provenance = self.provenance.add_contradiction(record_id)
        return Hypothesis(
            hypothesis_id=self.hypothesis_id,
            statement=self.statement,
            hypothesis_type=self.hypothesis_type,
            status=self.status,
            provenance=new_provenance,
            predicted_coordinate=self.predicted_coordinate,
            predicted_metric=self.predicted_metric,
            predicted_value=self.predicted_value,
            predicted_direction=self.predicted_direction,
            confidence=self.confidence,
            tags=self.tags,
            updated_at=datetime.now().isoformat(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "statement": self.statement,
            "hypothesis_type": self.hypothesis_type.value,
            "status": self.status.value,
            "provenance": self.provenance.to_dict(),
            "predicted_coordinate": self.predicted_coordinate.__dict__
            if self.predicted_coordinate
            else None,
            "predicted_metric": self.predicted_metric,
            "predicted_value": self.predicted_value,
            "predicted_direction": self.predicted_direction,
            "confidence": self.confidence,
            "tags": sorted(self.tags),
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Hypothesis:
        prov = ProvenanceLink.from_dict(data["provenance"])
        coord = None
        if data.get("predicted_coordinate"):
            coord = Coordinate(**data["predicted_coordinate"])
        return cls(
            hypothesis_id=data["hypothesis_id"],
            statement=data["statement"],
            hypothesis_type=HypothesisType(data["hypothesis_type"]),
            status=HypothesisStatus(data["status"]),
            provenance=prov,
            predicted_coordinate=coord,
            predicted_metric=data.get("predicted_metric", ""),
            predicted_value=data.get("predicted_value"),
            predicted_direction=data.get("predicted_direction", ""),
            confidence=data.get("confidence", 0.5),
            tags=frozenset(data.get("tags", [])),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )


@dataclass(frozen=True, slots=True)
class LiteratureRecord:
    """A literature reference with mandatory provenance linkage (R57, Q15)."""

    literature_id: str  # Content hash
    title: str
    authors: list[str]
    year: int
    literature_type: LiteratureType
    url: str = ""
    doi: str = ""
    # Summary of key findings relevant to computronium
    summary: str = ""
    # Provenance linkage (mandatory)
    provenance: ProvenanceLink = field(default_factory=ProvenanceLink)
    # Related hypotheses
    related_hypotheses: frozenset[str] = field(default_factory=frozenset)
    # Tags
    tags: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not self.literature_id:
            content = {
                "title": self.title,
                "authors": self.authors,
                "year": self.year,
                "type": self.literature_type.value,
            }
            object.__setattr__(
                self,
                "literature_id",
                hashlib.sha256(
                    json.dumps(content, sort_keys=True).encode()
                ).hexdigest()[:16],
            )

        if not isinstance(self.provenance, ProvenanceLink):
            raise TypeError("provenance must be a ProvenanceLink")

    def with_provenance(self, provenance: ProvenanceLink) -> LiteratureRecord:
        """Return new record with updated provenance."""
        return LiteratureRecord(
            literature_id=self.literature_id,
            title=self.title,
            authors=self.authors,
            year=self.year,
            literature_type=self.literature_type,
            url=self.url,
            doi=self.doi,
            summary=self.summary,
            provenance=provenance,
            related_hypotheses=self.related_hypotheses,
            tags=self.tags,
        )

    def add_related_hypothesis(self, hypothesis_id: str) -> LiteratureRecord:
        """Return new record with added related hypothesis."""
        return LiteratureRecord(
            literature_id=self.literature_id,
            title=self.title,
            authors=self.authors,
            year=self.year,
            literature_type=self.literature_type,
            url=self.url,
            doi=self.doi,
            summary=self.summary,
            provenance=self.provenance,
            related_hypotheses=self.related_hypotheses | {hypothesis_id},
            tags=self.tags,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "literature_id": self.literature_id,
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "literature_type": self.literature_type.value,
            "url": self.url,
            "doi": self.doi,
            "summary": self.summary,
            "provenance": self.provenance.to_dict(),
            "related_hypotheses": sorted(self.related_hypotheses),
            "tags": sorted(self.tags),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LiteratureRecord:
        prov = ProvenanceLink.from_dict(data["provenance"])
        return cls(
            literature_id=data["literature_id"],
            title=data["title"],
            authors=data["authors"],
            year=data["year"],
            literature_type=LiteratureType(data["literature_type"]),
            url=data.get("url", ""),
            doi=data.get("doi", ""),
            summary=data.get("summary", ""),
            provenance=prov,
            related_hypotheses=frozenset(data.get("related_hypotheses", [])),
            tags=frozenset(data.get("tags", [])),
        )


class ReasoningStore:
    """Store for hypotheses and literature records with provenance."""

    def __init__(self) -> None:
        self._hypotheses: dict[str, Hypothesis] = {}
        self._literature: dict[str, LiteratureRecord] = {}

    # Hypothesis operations
    def add_hypothesis(self, hypothesis: Hypothesis) -> None:
        """Add a hypothesis."""
        self._hypotheses[hypothesis.hypothesis_id] = hypothesis

    def get_hypothesis(self, hypothesis_id: str) -> Hypothesis | None:
        """Get a hypothesis by ID."""
        return self._hypotheses.get(hypothesis_id)

    def update_hypothesis(self, hypothesis: Hypothesis) -> None:
        """Update an existing hypothesis."""
        if hypothesis.hypothesis_id not in self._hypotheses:
            raise KeyError(f"Hypothesis {hypothesis.hypothesis_id} not found")
        self._hypotheses[hypothesis.hypothesis_id] = hypothesis

    def list_hypotheses(
        self,
        status: HypothesisStatus | None = None,
        hypothesis_type: HypothesisType | None = None,
        tag: str | None = None,
    ) -> list[Hypothesis]:
        """List hypotheses with optional filters."""
        results = []
        for hyp in self._hypotheses.values():
            if status and hyp.status != status:
                continue
            if hypothesis_type and hyp.hypothesis_type != hypothesis_type:
                continue
            if tag and tag not in hyp.tags:
                continue
            results.append(hyp)
        return results

    def get_supported_hypotheses(self) -> list[Hypothesis]:
        """Get all supported hypotheses."""
        return [
            hyp
            for hyp in self._hypotheses.values()
            if hyp.status == HypothesisStatus.SUPPORTED
        ]

    def get_hypotheses_by_record(self, record_id: str) -> list[Hypothesis]:
        """Get hypotheses that reference a specific record."""
        return [
            hyp
            for hyp in self._hypotheses.values()
            if record_id in hyp.provenance.supporting_records
            or record_id in hyp.provenance.contradicting_records
        ]

    # Literature operations
    def add_literature(self, literature: LiteratureRecord) -> None:
        """Add a literature record."""
        self._literature[literature.literature_id] = literature

    def get_literature(self, literature_id: str) -> LiteratureRecord | None:
        """Get a literature record by ID."""
        return self._literature.get(literature_id)

    def list_literature(
        self,
        literature_type: LiteratureType | None = None,
        tag: str | None = None,
    ) -> list[LiteratureRecord]:
        """List literature records with optional filters."""
        results = []
        for lit in self._literature.values():
            if literature_type and lit.literature_type != literature_type:
                continue
            if tag and tag not in lit.tags:
                continue
            results.append(lit)
        return results

    def get_literature_by_hypothesis(
        self, hypothesis_id: str
    ) -> list[LiteratureRecord]:
        """Get literature related to a hypothesis."""
        return [
            lit
            for lit in self._literature.values()
            if hypothesis_id in lit.related_hypotheses
        ]

    def export_all(self) -> dict[str, Any]:
        """Export all hypotheses and literature."""
        return {
            "hypotheses": {k: v.to_dict() for k, v in self._hypotheses.items()},
            "literature": {k: v.to_dict() for k, v in self._literature.items()},
            "exported_at": datetime.now().isoformat(),
        }

    def import_all(self, data: dict[str, Any]) -> None:
        """Import hypotheses and literature."""
        self._hypotheses = {
            k: Hypothesis.from_dict(v) for k, v in data.get("hypotheses", {}).items()
        }
        self._literature = {
            k: LiteratureRecord.from_dict(v)
            for k, v in data.get("literature", {}).items()
        }


# Global reasoning store
_REASONING_STORE: ReasoningStore | None = None


def get_reasoning_store() -> ReasoningStore:
    """Get or create the global reasoning store."""
    global _REASONING_STORE  # noqa: PLW0603 - singleton pattern
    if _REASONING_STORE is None:
        _REASONING_STORE = ReasoningStore()
    return _REASONING_STORE


def reset_reasoning_store() -> None:
    """Reset the global reasoning store (for testing)."""
    global _REASONING_STORE  # noqa: PLW0603 - singleton pattern
    _REASONING_STORE = None


@dataclass(frozen=True, slots=True)
class HypothesisConfig:
    """Configuration for creating a hypothesis."""

    statement: str
    hypothesis_type: HypothesisType
    author: str
    code_hash: str
    run_id: str = ""
    predicted_coordinate: Coordinate | None = None
    predicted_metric: str = ""
    predicted_value: float | None = None
    predicted_direction: str = ""
    confidence: float = 0.5
    tags: frozenset[str] = field(default_factory=frozenset)


def create_hypothesis(config: HypothesisConfig) -> Hypothesis:
    """Create a hypothesis with mandatory provenance."""
    provenance = ProvenanceLink(
        author=config.author,
        code_hash=config.code_hash,
        run_id=config.run_id,
    )
    return Hypothesis(
        hypothesis_id="",  # Will be auto-generated
        statement=config.statement,
        hypothesis_type=config.hypothesis_type,
        provenance=provenance,
        predicted_coordinate=config.predicted_coordinate,
        predicted_metric=config.predicted_metric,
        predicted_value=config.predicted_value,
        predicted_direction=config.predicted_direction,
        confidence=config.confidence,
        tags=config.tags,
    )


@dataclass(frozen=True, slots=True)
class LiteratureConfig:
    """Configuration for creating a literature record."""

    title: str
    authors: list[str]
    year: int
    literature_type: LiteratureType
    author: str
    code_hash: str
    url: str = ""
    doi: str = ""
    summary: str = ""
    run_id: str = ""
    tags: frozenset[str] = field(default_factory=frozenset)


def create_literature_record(config: LiteratureConfig) -> LiteratureRecord:
    """Create a literature record with mandatory provenance."""
    provenance = ProvenanceLink(
        author=config.author,
        code_hash=config.code_hash,
        run_id=config.run_id,
    )
    return LiteratureRecord(
        literature_id="",  # Will be auto-generated
        title=config.title,
        authors=config.authors,
        year=config.year,
        literature_type=config.literature_type,
        url=config.url,
        doi=config.doi,
        summary=config.summary,
        provenance=provenance,
        tags=config.tags,
    )


__all__ = [
    "Hypothesis",
    "HypothesisConfig",
    "HypothesisStatus",
    "HypothesisType",
    "LiteratureConfig",
    "LiteratureRecord",
    "LiteratureType",
    "ProvenanceLink",
    "ReasoningStore",
    "create_hypothesis",
    "create_literature_record",
    "get_reasoning_store",
    "reset_reasoning_store",
]
