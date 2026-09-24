"""Event projector — pure fold over event log (M2.1).

Deterministic: identical state across shuffle-safe replays; idempotent on duplicates.
No imports from campaign/gate mutation paths (UX-L7).

Design: Two-pass fold for order-independence.
Pass 1: Deduplicate events, collect payloads by kind.
Pass 2: Compute badges, quests, records from aggregated data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from computronium.ui.recognition.badges import Badge
    from computronium.ui.recognition.quests import Quest
    from computronium.ui.recognition.records import Record

# Runtime imports (no circular dependency - badges/quests/records don't import projector)
import pathlib

from computronium.ui.recognition.badges import (
    Badge,
    check_badge_conditions,
)
from computronium.ui.recognition.quests import (
    QUEST_SPECS,
    Quest,
    update_quest_progress,
)
from computronium.ui.recognition.records import (
    Record,
    update_records,
)


@dataclass(frozen=True, slots=True)
class RecognitionEvent:
    """An event from the campaign/event log that affects recognition."""

    kind: str
    timestamp: float
    payload: dict


@dataclass(frozen=True, slots=True)
class RecognitionState:
    """Complete recognition state derived from event log."""

    badges: tuple[Badge, ...] = ()
    quests: tuple[Quest, ...] = ()
    records: tuple[Record, ...] = ()
    fog_regions_charted: frozenset[str] = field(default_factory=frozenset)

    # For idempotency tracking
    _seen_event_hashes: frozenset[str] = field(default_factory=frozenset, repr=False)


@dataclass(frozen=True, slots=True)
class _AggregatedData:
    """Aggregated event data for order-independent computation."""

    cell_completed: tuple[dict, ...] = ()
    defect_quarantined: tuple[dict, ...] = ()
    defect_resolved: tuple[dict, ...] = ()
    pareto_front_expanded: tuple[dict, ...] = ()
    region_charted: tuple[str, ...] = ()
    campaign_complete: tuple[dict, ...] = ()
    measurement_recorded: tuple[dict, ...] = ()


def _event_hash(event: RecognitionEvent) -> str:
    """Compute a stable hash for an event (for idempotency)."""
    import hashlib
    import json

    data = json.dumps({"kind": event.kind, "payload": event.payload}, sort_keys=True)
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def fold(events: Iterable[RecognitionEvent]) -> RecognitionState:  # ruff: ignore[complex-structure,too-many-branches,too-many-locals]
    """Pure fold: process events to build recognition state.

    Properties:
    - Deterministic: same events in any order produce identical state
    - Idempotent: duplicate events don't change state
    - No side effects: pure function

    Args:
        events: Iterable of RecognitionEvent objects

    Returns:
        RecognitionState with all badges, quests, records, fog regions
    """
    # Pass 1: Deduplicate and aggregate
    seen_hashes: set[str] = set()

    cell_completed_list = []
    defect_quarantined_list = []
    defect_resolved_list = []
    pareto_front_expanded_list = []
    region_charted_set = set()
    campaign_complete_list = []
    measurement_recorded_list = []

    for event in events:
        # Idempotency: skip if we've seen this exact event
        event_hash = _event_hash(event)
        if event_hash in seen_hashes:
            continue
        seen_hashes.add(event_hash)

        # Collect payloads by kind
        kind = event.kind
        payload = event.payload

        if kind == "cell_completed":
            cell_completed_list.append(payload)
        elif kind == "defect_quarantined":
            defect_quarantined_list.append(payload)
        elif kind == "defect_resolved":
            defect_resolved_list.append(payload)
        elif kind == "pareto_front_expanded":
            pareto_front_expanded_list.append(payload)
        elif kind == "region_charted":
            region = payload.get("region")
            if region:
                region_charted_set.add(region)
        elif kind == "campaign_complete":
            campaign_complete_list.append(payload)
        elif kind == "measurement_recorded":
            measurement_recorded_list.append(payload)

    # Pass 2: Compute state from aggregated data (order-independent)
    badges: dict[str, Badge] = {}
    quests: dict[str, Quest] = {q.id: q for q in QUEST_SPECS}
    records: dict[str, Record] = {}
    fog_regions = set(region_charted_set)

    # Process each event kind from aggregated data
    for payload in cell_completed_list:
        _award_badges("cell_completed", payload, badges)
        quests = _update_quests("cell_completed", payload, quests)
        _update_records("cell_completed", payload, records)

    for payload in defect_quarantined_list:
        _award_badges("defect_quarantined", payload, badges)
        quests = _update_quests("defect_quarantined", payload, quests)

    for payload in defect_resolved_list:
        _award_badges("defect_resolved", payload, badges)
        quests = _update_quests("defect_resolved", payload, quests)

    for payload in pareto_front_expanded_list:
        _award_badges("pareto_front_expanded", payload, badges)
        quests = _update_quests("pareto_front_expanded", payload, quests)
        _update_records("pareto_front_expanded", payload, records)

    for payload in campaign_complete_list:
        _award_badges("campaign_complete", payload, badges)
        quests = _update_quests("campaign_complete", payload, quests)

    for payload in measurement_recorded_list:
        _award_badges("measurement_recorded", payload, badges)
        _update_records("measurement_recorded", payload, records)

    # Build final state
    return RecognitionState(
        badges=tuple(badges.values()),
        quests=tuple(quests.values()),
        records=tuple(records.values()),
        fog_regions_charted=frozenset(fog_regions),
        _seen_event_hashes=frozenset(seen_hashes),
    )


def _award_badges(event_kind: str, payload: dict, badges: dict[str, Badge]) -> None:
    """Award badges for an event kind from aggregated data."""
    for badge in check_badge_conditions(event_kind, payload):
        if badge.id not in badges:
            badges[badge.id] = badge


def _update_quests(
    event_kind: str, payload: dict, quests: dict[str, Quest]
) -> dict[str, Quest]:
    """Update quest progress for an event kind from aggregated data."""
    updated = dict(quests)
    for quest in update_quest_progress(event_kind, payload, updated.values()):
        updated[quest.id] = quest
    return updated


def _update_records(event_kind: str, payload: dict, records: dict[str, Record]) -> None:
    """Update records for an event kind from aggregated data."""
    for record in update_records(event_kind, payload, records.values()):
        records[record.id] = record


def fold_from_jsonl(path: str) -> RecognitionState:
    """Convenience: fold events from a JSONL file."""
    import json

    events = []
    with pathlib.Path(path).open(encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            raw = json.loads(line)
            events.append(
                RecognitionEvent(
                    kind=raw.get("kind", ""),
                    timestamp=raw.get("timestamp", 0.0),
                    payload=raw.get("payload", {}),
                )
            )
    return fold(events)
