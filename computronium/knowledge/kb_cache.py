"""Fingerprint-keyed memo for read-only KnowledgeBase loads.

Lives in ``knowledge`` rather than in a view module because the invariant it
protects is a persistence invariant: ``KnowledgeBase`` runs SQLite in WAL
mode, so a correct cache key is a question about how the database stores
commits, not about how a chart is drawn. The defect this replaced had its
WAL-correctness fix applied inside a module named for charts, which is the
wrong place to look for a storage contract.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

UNBOUNDED_ROWS = 1_000_000_000

_KB_LOAD_CACHE: dict[tuple[str, tuple[object, ...], object], Any] = {}
_KB_CACHE_MAX_ENTRIES = 16


def _kb_fingerprint(path: Path) -> tuple[object, ...]:
    """Identity of the KB *data*, not just the main file.

    ``KnowledgeBase`` runs SQLite in WAL mode: a commit appends to the
    ``-wal`` sidecar and leaves the main database's mtime and size
    untouched, so keying on the main file alone pinned the cache to the
    rows read at first touch. Long-lived readers (the continuous campaign
    loop, the daemon) then never observed newly measured cells, and
    ``promote_candidates`` re-promoted cells it had already matured.
    """

    def stat_of(target: Path) -> tuple[object, ...]:
        try:
            info = target.stat()
        except OSError:
            return ("absent",)
        return (info.st_mtime_ns, info.st_size)

    return (stat_of(path), stat_of(path.with_name(f"{path.name}-wal")))


def kb_load_cached[T](
    path: Path,
    loader: Callable[[], T],
    clone: Callable[[T], T],
    *,
    key_extra: object = (),
) -> T:
    """Fingerprint-keyed memo for read-only KB loads; each caller gets ``clone()``.

    Keyed on ``(path, fingerprint, key_extra)`` where the fingerprint covers
    the main database and its WAL sidecar, so a campaign that grows mid-run
    invalidates naturally. The cached value is canonical; callers receive a
    clone (pandas CoW shallow copy / list copy) so mutation cannot leak
    across call sites. Stale keys are dropped when the cache is full.
    """
    key = (str(path), _kb_fingerprint(path), key_extra)
    hit = _KB_LOAD_CACHE.get(key)
    if hit is None:
        if len(_KB_LOAD_CACHE) >= _KB_CACHE_MAX_ENTRIES:
            _KB_LOAD_CACHE.clear()
        hit = loader()
        _KB_LOAD_CACHE[key] = hit
    return clone(hit)  # type: ignore[operator]
