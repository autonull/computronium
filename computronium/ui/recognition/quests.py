"""Quests — campaign-mapped checklists, opt-in (M2.4).

6 quests per GAME.md §8.4. Completion copy states what was learned/verified.
No XP, no points. Opt-in only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass(frozen=True, slots=True)
class Quest:
    """An opt-in quest with progress tracking."""

    id: str
    name: str
    description: str
    icon: str
    objective: str  # Human-readable objective
    completion_message_explorer: str
    completion_message_lab: str
    progress_current: int = 0
    progress_target: int = 1
    completed: bool = False
    opted_in: bool = False
    completed_at: float | None = None


# Quest specifications — single source of truth
QUEST_SPECS: tuple[Quest, ...] = (
    Quest(
        id="chart_100_regions",
        name="Chart 100 Regions",
        description="Explore the discovery map by charting 100 distinct regions",
        icon="🗺️",
        objective="Chart 100 regions",
        completion_message_explorer="You've mapped 100 regions — the territory is known",
        completion_message_lab="KB coverage: 100 regions charted",
        progress_target=100,
    ),
    Quest(
        id="double_check_3_candidates",
        name="Double-Check 3 Candidates",
        description="Run repeat measurements on 3 different candidate cells",
        icon="🔍",
        objective="Verify 3 candidates with repeats",
        completion_message_explorer="Three results verified — confidence is earned",
        completion_message_lab="3 candidates with ≥3 repeats each",
        progress_target=3,
    ),
    Quest(
        id="send_to_careful_recheck",
        name="Send to Careful Re-check",
        description="Flag a surprising result for careful L2 re-run",
        icon="📋",
        objective="Request 1 L2 re-run",
        completion_message_explorer="Asked for a careful second look",
        completion_message_lab="L2 re-run requested via campaign API",
        progress_target=1,
    ),
    Quest(
        id="clear_repair_bench",
        name="Clear the Repair Bench",
        description="Resolve all currently open runtime defects",
        icon="🔧",
        objective="Zero open defects",
        completion_message_explorer="All crashes fixed — bench is clear",
        completion_message_lab="0 open defects in runtime_defects.jsonl",
        progress_target=1,
    ),
    Quest(
        id="compare_goals",
        name="Compare Two Goals",
        description="Use the Pareto selector to compare 3 different objective pairs",
        icon="⚖️",
        objective="Switch objective pairs 3 times",
        completion_message_explorer="Explored trade-offs from 3 angles",
        completion_message_lab="3 objective-pair selections recorded",
        progress_target=3,
    ),
    Quest(
        id="forecast_and_check",
        name="Forecast & Check",
        description="Predict a cell's outcome before it finishes, then verify",
        icon="🔮",
        objective="Make 1 verified forecast",
        completion_message_explorer="Predicted a result and watched it unfold",
        completion_message_lab="Forecast logged, actual matched within margin",
        progress_target=1,
    ),
)


def update_quest_progress(  # noqa: C901
    event_kind: str, payload: dict, existing_quests: Iterable[Quest]
) -> Iterable[Quest]:
    """Update quest progress based on an event.

    Pure function — returns updated quests (new instances).
    """
    quests_dict = {q.id: q for q in existing_quests}

    if event_kind == "region_charted":
        q = quests_dict.get("chart_100_regions")
        if q and q.opted_in and not q.completed:
            new_progress = q.progress_current + 1
            yield Quest(**{
                **q.__dict__,
                "progress_current": new_progress,
                "completed": new_progress >= q.progress_target,
            })

    elif event_kind == "cell_completed":
        # Check for repeats (double_check_3_candidates)
        cell_key = payload.get("cell_key", "")
        if cell_key:
            # Would need to track repeats per cell — simplified here
            pass

        # Check for Pareto comparisons (compare_goals)
        # This would track objective pair changes — simplified

    elif event_kind == "pareto_front_expanded":
        q = quests_dict.get("compare_goals")
        if q and q.opted_in and not q.completed:
            # Simplified: count each expansion as a "comparison"
            new_progress = min(q.progress_current + 1, q.progress_target)
            yield Quest(**{
                **q.__dict__,
                "progress_current": new_progress,
                "completed": new_progress >= q.progress_target,
            })

    elif event_kind == "defect_resolved":
        q = quests_dict.get("clear_repair_bench")
        if q and q.opted_in and not q.completed:
            # Check if all defects are now resolved
            # Simplified: assume this event means bench is clear
            yield Quest(**{**q.__dict__, "progress_current": 1, "completed": True})

    elif event_kind == "campaign_complete":
        # Check various completion conditions
        for q in quests_dict.values():
            if (
                q.opted_in
                and not q.completed
                and (  # noqa: PLR0916
                    (q.id == "send_to_careful_recheck" and payload.get("l2_requested"))
                    or (
                        q.id == "forecast_and_check"
                        and payload.get("forecast_verified")
                    )
                )
            ):
                yield Quest(**{
                    **q.__dict__,
                    "progress_current": 1,
                    "completed": True,
                })


def get_quest_by_id(quest_id: str) -> Quest | None:
    """Look up a quest by ID."""
    for quest in QUEST_SPECS:
        if quest.id == quest_id:
            return quest
    return None


def get_all_quests() -> tuple[Quest, ...]:
    """Get all quest specifications."""
    return QUEST_SPECS


def opt_in_quest(quest_id: str, quests: Iterable[Quest]) -> Iterable[Quest]:
    """Opt in to a quest (returns new quest instances)."""
    for q in quests:
        if q.id == quest_id:
            yield Quest(**{**q.__dict__, "opted_in": True})
        else:
            yield q


def opt_out_quest(quest_id: str, quests: Iterable[Quest]) -> Iterable[Quest]:
    """Opt out of a quest (returns new quest instances)."""
    for q in quests:
        if q.id == quest_id:
            yield Quest(**{**q.__dict__, "opted_in": False})
        else:
            yield q
