"""GlossaryService — register-aware string lookup (M0.2).

Single source of truth for all UI copy. Two registers:
- "explorer": plain language, ≤ Flesch–Kincaid grade 8
- "lab": technical precision

i18n-ready: locale can be added as a third key in the future.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal

logger = logging.getLogger("glossary")

Register = Literal["explorer", "lab"]


@dataclass(frozen=True, slots=True)
class GlossaryEntry:
    """One term in both registers."""

    explorer: str
    lab: str


class GlossaryService:
    """Register-aware string service backed by ``ui/glossary.json``.

    Usage:
        svc = GlossaryService()
        svc.get("pareto_optimal", register="explorer")  # "Best trade-off"
        svc.get("pareto_optimal", register="lab")       # "Pareto optimal"
    """

    def __init__(self, glossary_path: Path | None = None) -> None:
        self._glossary_path = glossary_path or Path(__file__).parent / "glossary.json"
        self._entries: dict[str, GlossaryEntry] = {}
        self._load()

    def _load(self) -> None:
        """Load and parse the glossary JSON."""
        try:
            raw = json.loads(self._glossary_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            logger.exception("Failed to load glossary from %s", self._glossary_path)
            raise RuntimeError(f"Glossary load failed: {e}") from e

        terms = raw.get("terms", {})
        for key, entry in terms.items():
            self._entries[key] = GlossaryEntry(
                explorer=entry.get("explorer", key),
                lab=entry.get("lab", key),
            )
        logger.info(
            "Glossary loaded: %d terms from %s", len(self._entries), self._glossary_path
        )

    def get(self, key: str, register: Register = "explorer") -> str:
        """Lookup a term in the given register.

        Falls back to the key itself if not found (with a warning).
        """
        entry = self._entries.get(key)
        if entry is None:
            logger.warning("Glossary key not found: %s (register=%s)", key, register)
            return key
        return entry.explorer if register == "explorer" else entry.lab

    def get_both(self, key: str) -> tuple[str, str]:
        """Return (explorer, lab) pair for a key."""
        entry = self._entries.get(key)
        if entry is None:
            logger.warning("Glossary key not found: %s", key)
            return key, key
        return entry.explorer, entry.lab

    def has(self, key: str) -> bool:
        """Check if a key exists in the glossary."""
        return key in self._entries

    def all_keys(self) -> list[str]:
        """All registered keys (for linting/totality checks)."""
        return sorted(self._entries.keys())

    def all_entries(self) -> dict[str, GlossaryEntry]:
        """All entries (for i18n extraction)."""
        return dict(self._entries)


@lru_cache(maxsize=1)
def get_glossary_service() -> GlossaryService:
    """Singleton accessor (module-level cache)."""
    return GlossaryService()


def tr(key: str, register: Register = "explorer") -> str:
    """Convenience function: ``tr("pareto_optimal")`` → "Best trade-off".

    Use this in components instead of hardcoded strings.
    """
    return get_glossary_service().get(key, register)


def tr_both(key: str) -> tuple[str, str]:
    """Convenience: ``tr_both("pareto_optimal")`` → ("Best trade-off", "Pareto optimal")."""
    return get_glossary_service().get_both(key)
