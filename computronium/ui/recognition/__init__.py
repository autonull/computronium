"""Recognition package (badges, quests, records, projector, state store, fog)."""

from computronium.ui.recognition.badges import (
    BADGE_SPECS,
    Badge,
    check_badge_conditions,
    get_all_badges,
    get_badge_by_id,
)
from computronium.ui.recognition.fog import (
    FogOfWar,
    FogRegion,
    compute_fog_of_war,
    get_charted_regions,
    get_fog_overlay_data,
)
from computronium.ui.recognition.projector import (
    RecognitionEvent,
    RecognitionState,
    fold,
    fold_from_jsonl,
)
from computronium.ui.recognition.quests import (
    QUEST_SPECS,
    Quest,
    get_all_quests,
    get_quest_by_id,
    opt_in_quest,
    opt_out_quest,
    update_quest_progress,
)
from computronium.ui.recognition.records import (
    OBJECTIVE_CATEGORIES,
    Record,
    get_all_records,
    get_records_by_objective,
    update_records,
)
from computronium.ui.recognition.state_store import (
    RecognitionStateStore,
    get_state_store,
)

__all__ = [
    "BADGE_SPECS",
    "OBJECTIVE_CATEGORIES",
    "QUEST_SPECS",
    # Badges
    "Badge",
    # Fog
    "FogOfWar",
    "FogRegion",
    # Quests
    "Quest",
    # Projector
    "RecognitionEvent",
    "RecognitionState",
    # State store
    "RecognitionStateStore",
    # Records
    "Record",
    "check_badge_conditions",
    "compute_fog_of_war",
    "fold",
    "fold_from_jsonl",
    "get_all_badges",
    "get_all_quests",
    "get_all_records",
    "get_badge_by_id",
    "get_charted_regions",
    "get_fog_overlay_data",
    "get_quest_by_id",
    "get_records_by_objective",
    "get_state_store",
    "opt_in_quest",
    "opt_out_quest",
    "update_quest_progress",
    "update_records",
]
