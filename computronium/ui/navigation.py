"""Hash navigation helpers — pure, browser-free (GAME.todo7 Phase 2).

Hash format is ``#view`` or ``#view/tab`` (deep links share dashboard
state; use case (i) entry points). The dashboard writes the hash on every
navigation and syncs client → server on a 1 s timer, so load, refresh,
and back/forward all land on the right view.
"""

from __future__ import annotations


def parse_hash(raw: str | None) -> tuple[str | None, str | None]:
    """Split a URL hash into ``(view_key, tab_key | None)``.

    Unknown/empty hashes yield ``(None, None)``; callers validate keys
    against the view registry.
    """
    if not raw:
        return (None, None)
    text = raw.strip()
    if text.startswith("#"):
        text = text[1:]
    text = text.strip().strip("/")
    if not text:
        return (None, None)
    head, _, tail = text.partition("/")
    view = head.strip().strip("/")
    tab = tail.strip().strip("/") if tail else ""
    return (view or None, tab or None)


def format_hash(view_key: str, tab_key: str | None = None) -> str:
    """Format a ``(view, tab)`` pair as a URL hash."""
    if tab_key:
        return f"#{view_key}/{tab_key}"
    return f"#{view_key}"
