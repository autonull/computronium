"""Locks for the KB read cache (``knowledge.kb_cache.kb_load_cached``).

Ratchet for the stale-read defect: the cache keyed on the main SQLite
file's ``(mtime_ns, size)``, but ``KnowledgeBase`` runs in WAL mode, so a
commit appends to the ``-wal`` sidecar and leaves both fields identical.
Every long-lived reader therefore kept serving the rows it read at first
touch. The concrete casualty was L1 maturation: ``promote_candidates``
re-promoted a cell whose ``maturity:l1`` marker was already in the KB.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.knowledge import KnowledgeBase, KnowledgeEntry
from computronium.knowledge.kb_cache import _KB_LOAD_CACHE, kb_load_cached

if TYPE_CHECKING:
    from pathlib import Path


def _entry(entry_id: str, tag: str) -> KnowledgeEntry:
    return KnowledgeEntry(
        id=entry_id,
        topic="experiment:digits",
        model_family="eqprop",
        finding="measured",
        details="lock",
        confidence=0.5,
        tags=[tag],
        hyperparameters={
            "dynamics": "energy_minimization",
            "credit": "thermodynamic_contrast",
            "update": "adam",
            "geometry": {"topology_type": "feedforward"},
        },
        metrics={"final_accuracy": 0.5},
    )


def _add(kb_path: Path, entry: KnowledgeEntry) -> None:
    KnowledgeBase(kb_path, auto_embed=False).add_entry(entry)


def test_wal_write_is_visible_to_the_cache(tmp_path: Path) -> None:
    """A commit that only grows the WAL sidecar must invalidate the cache."""
    kb_path = tmp_path / "kb.sqlite"
    _add(kb_path, _entry("KB-1", "maturity:l0"))

    def read_tags() -> list[list[str]]:
        def loader() -> list[list[str]]:
            entries = KnowledgeBase(kb_path, auto_embed=False).query(limit=1000)
            return [sorted(str(t) for t in entry.tags) for entry in entries]

        return kb_load_cached(kb_path, loader, list, key_extra=("lock",))

    first = read_tags()
    assert first and ["maturity:l0"] in first

    _add(kb_path, _entry("KB-2", "maturity:l1"))
    second = read_tags()
    assert second != first, "cache served a stale read after a WAL commit"
    assert any("maturity:l1" in tags for tags in second)


def test_repeat_reads_without_a_write_still_hit_the_cache(tmp_path: Path) -> None:
    """The memo keeps its purpose: no reload while the data is unchanged."""
    kb_path = tmp_path / "kb.sqlite"
    _add(kb_path, _entry("KB-1", "maturity:l0"))
    _KB_LOAD_CACHE.clear()

    loads: list[int] = []

    def loader() -> list[str]:
        loads.append(1)
        return ["maturity:l0"]

    for _ in range(5):
        assert kb_load_cached(kb_path, loader, list, key_extra=("lock",)) == [
            "maturity:l0"
        ]
    assert len(loads) == 1, "identical data reloaded on every call"


def test_caller_mutation_cannot_leak_into_the_cache(tmp_path: Path) -> None:
    """Callers get a clone, so a mutated result never poisons the memo."""
    kb_path = tmp_path / "kb.sqlite"
    _add(kb_path, _entry("KB-1", "maturity:l0"))
    _KB_LOAD_CACHE.clear()

    def loader() -> list[str]:
        return ["maturity:l0"]

    first = kb_load_cached(kb_path, loader, list, key_extra=("lock",))
    first.append("injected")
    second = kb_load_cached(kb_path, loader, list, key_extra=("lock",))
    assert second == ["maturity:l0"]


def test_absent_database_recovers_once_it_appears(tmp_path: Path) -> None:
    """A missing KB answers without raising, and appearing invalidates it."""
    kb_path = tmp_path / "absent.sqlite"
    _KB_LOAD_CACHE.clear()
    calls: list[int] = []

    def loader() -> str:
        calls.append(1)
        return "empty"

    assert kb_load_cached(kb_path, loader, lambda v: v, key_extra=("lock",)) == "empty"
    assert kb_load_cached(kb_path, loader, lambda v: v, key_extra=("lock",)) == "empty"
    assert len(calls) == 1, "an absent database was re-probed on every call"

    # The database is created: the fingerprint must change, or the memo would
    # keep reporting "empty" for a KB that now has rows.
    _add(kb_path, _entry("KB-1", "maturity:l0"))

    def read_tags() -> list[list[str]]:
        def read() -> list[list[str]]:
            return [
                sorted(str(t) for t in entry.tags)
                for entry in KnowledgeBase(kb_path, auto_embed=False).query(limit=1000)
            ]

        return kb_load_cached(kb_path, read, list, key_extra=("lock",))

    assert ["maturity:l0"] in read_tags()
