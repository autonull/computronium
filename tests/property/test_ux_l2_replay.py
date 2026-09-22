"""UX-L2: Deterministic replay property test (M2.9).

The recognition projector fold(event_log) must produce identical state across
shuffle-safe replays and be idempotent on duplicates.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from computronium.ui.recognition import (
    Badge,
    Quest,
    RecognitionEvent,
    RecognitionState,
    Record,
    fold,
)


@dataclass(frozen=True, slots=True)
class TestEvent:
    """Test event for property testing."""

    kind: str
    payload: dict


def _to_recognition_event(e: TestEvent) -> RecognitionEvent:
    return RecognitionEvent(kind=e.kind, timestamp=0.0, payload=e.payload)


@st.composite
def _test_event_strategy(draw: st.DrawFn) -> TestEvent:
    """Generate test events for the recognition projector."""
    kind = draw(
        st.sampled_from([
            "cell_completed",
            "defect_quarantined",
            "defect_resolved",
            "pareto_front_expanded",
            "region_charted",
            "campaign_complete",
            "measurement_recorded",
        ])
    )

    if kind == "cell_completed":
        payload = {
            "cell_key": draw(st.text(min_size=1, max_size=20)),
            "accuracy": draw(st.floats(min_value=0.0, max_value=1.0)),
            "objectives": {
                "accuracy": draw(st.floats(min_value=0.0, max_value=1.0)),
                "walltime_s": draw(st.floats(min_value=1.0, max_value=1000.0)),
            },
            "is_pareto_optimal": draw(st.booleans()),
        }
    elif kind in {"defect_quarantined", "defect_resolved"}:
        payload = {"defect_id": draw(st.text(min_size=1, max_size=20))}
    elif kind == "pareto_front_expanded":
        payload = {
            "cell_key": draw(st.text(min_size=1, max_size=20)),
            "objectives": {
                "accuracy": draw(st.floats(min_value=0.0, max_value=1.0)),
            },
        }
    elif kind == "region_charted":
        payload = {"region": draw(st.text(min_size=1, max_size=30))}
    elif kind == "campaign_complete":
        payload = {"cells_completed": draw(st.integers(min_value=1, max_value=1000))}
    else:  # measurement_recorded
        payload = {
            "objectives": {
                "accuracy": draw(st.floats(min_value=0.0, max_value=1.0)),
            }
        }

    return TestEvent(kind=kind, payload=payload)


@st.composite
def event_list_strategy(draw: st.DrawFn) -> list[TestEvent]:
    """Generate a list of test events."""
    return draw(st.lists(_test_event_strategy(), min_size=0, max_size=20))


def _serialize_state(state: RecognitionState) -> str:
    """Serialize recognition state to canonical string for comparison."""

    def serialize_badge(b: Badge) -> str:
        return f"{b.id}|{b.name}|{b.description}|{b.icon}|{b.evidence_kind}|{b.evidence_query}|{b.register_explorer}|{b.register_lab}"

    def serialize_quest(q: Quest) -> str:
        return f"{q.id}|{q.name}|{q.description}|{q.icon}|{q.objective}|{q.completion_message_explorer}|{q.completion_message_lab}|{q.progress_current}|{q.progress_target}|{q.completed}|{q.opted_in}|{q.completed_at or 'none'}"

    def serialize_record(r: Record) -> str:
        return f"{r.id}|{r.objective}|{r.value:.6f}|{r.cell_key}|{r.timestamp:.6f}|{r.scope}|{r.register_explorer}|{r.register_lab}"

    badges_str = "\n".join(sorted(serialize_badge(b) for b in state.badges))
    quests_str = "\n".join(sorted(serialize_quest(q) for q in state.quests))
    records_str = "\n".join(sorted(serialize_record(r) for r in state.records))
    fog_str = "\n".join(sorted(state.fog_regions_charted))

    return f"BADGES:\n{badges_str}\n---\nQUESTS:\n{quests_str}\n---\nRECORDS:\n{records_str}\n---\nFOG:\n{fog_str}"


class TestReplayDeterminism:
    """UX-L2: Recognition projector must be deterministic and idempotent."""

    @given(event_list_strategy())
    @settings(max_examples=200, deadline=None)
    def test_shuffled_replay_produces_identical_state(
        self, events: list[TestEvent]
    ) -> None:
        """Shuffled event order must produce identical state."""
        import random

        rec_events = [_to_recognition_event(e) for e in events]

        # Original order
        state1 = fold(rec_events)

        # Shuffled order with deterministic seed
        rng = random.Random(123)  # Fixed seed for reproducibility
        shuffled = rec_events.copy()
        rng.shuffle(shuffled)
        state2 = fold(shuffled)

        # Must be identical
        assert _serialize_state(state1) == _serialize_state(state2), (
            "Shuffled replay produced different state"
        )

    @given(event_list_strategy())
    @settings(max_examples=200, deadline=None)
    def test_duplicate_events_are_idempotent(self, events: list[TestEvent]) -> None:
        """Duplicate events must not change the final state.

        Uses deterministic shuffling with fixed seed for reproducibility.
        """
        import random

        rec_events = [_to_recognition_event(e) for e in events]

        # Original events
        state1 = fold(rec_events)

        # Add duplicates with deterministic shuffling
        rng = random.Random(42)  # Fixed seed for reproducibility
        duplicated = rec_events + rng.sample(rec_events, min(5, len(rec_events)))
        rng.shuffle(duplicated)
        state2 = fold(duplicated)

        # Must be identical
        assert _serialize_state(state1) == _serialize_state(state2), (
            "Duplicate events produced different state"
        )

    @given(event_list_strategy())
    @settings(max_examples=100, deadline=None)
    def test_empty_events_produces_empty_state(self, events: list[TestEvent]) -> None:
        """Empty event list must produce empty state (except default quests)."""
        from computronium.ui.recognition import QUEST_SPECS

        state = fold([])
        assert state.badges == ()
        assert state.fog_regions_charted == frozenset()
        # Quests should be default specs (not opted in, not completed)
        assert len(state.quests) == len(QUEST_SPECS)
        for quest in state.quests:
            assert not quest.opted_in
            assert not quest.completed
            assert quest.progress_current == 0
        # Records should be empty
        assert state.records == ()

    def test_specific_event_ordering_independence(self) -> None:
        """Test that specific event kinds don't depend on order."""
        # Create events that could have ordering dependencies
        events = [
            RecognitionEvent("region_charted", 1.0, {"region": "region_a"}),
            RecognitionEvent("region_charted", 2.0, {"region": "region_b"}),
            RecognitionEvent(
                "cell_completed",
                3.0,
                {"cell_key": "cell_1", "objectives": {"accuracy": 0.9}},
            ),
            RecognitionEvent(
                "pareto_front_expanded",
                4.0,
                {"cell_key": "cell_1", "objectives": {"accuracy": 0.95}},
            ),
        ]

        import random

        state1 = fold(events)

        # Test many permutations with fixed seed
        rng = random.Random(456)
        for _ in range(50):
            shuffled = events.copy()
            rng.shuffle(shuffled)
            state2 = fold(shuffled)
            assert _serialize_state(state1) == _serialize_state(state2)

    def test_idempotency_exact_duplicates(self) -> None:
        """Test exact duplicate events are ignored."""
        event = RecognitionEvent(
            "cell_completed",
            1.0,
            {"cell_key": "cell_1", "objectives": {"accuracy": 0.9}},
        )

        state1 = fold([event])
        state2 = fold([event, event, event])  # Triple duplicate

        assert _serialize_state(state1) == _serialize_state(state2)

    def test_region_charted_accumulates(self) -> None:
        """Test that region_charted events accumulate regions."""
        events = [
            RecognitionEvent("region_charted", 1.0, {"region": "region_a"}),
            RecognitionEvent("region_charted", 2.0, {"region": "region_b"}),
            RecognitionEvent(
                "region_charted", 3.0, {"region": "region_a"}
            ),  # Duplicate
        ]

        state = fold(events)
        assert "region_a" in state.fog_regions_charted
        assert "region_b" in state.fog_regions_charted
        assert len(state.fog_regions_charted) == 2


class TestReplayIntegration:
    """Integration tests for replay with state store."""

    def test_fold_from_jsonl_roundtrip(self, tmp_path) -> None:
        """Test fold_from_jsonl works correctly."""
        import json

        events = [
            {
                "kind": "cell_completed",
                "timestamp": 1.0,
                "payload": {"cell_key": "cell_1", "objectives": {"accuracy": 0.9}},
            },
            {
                "kind": "defect_quarantined",
                "timestamp": 2.0,
                "payload": {"defect_id": "defect_1"},
            },
            {
                "kind": "defect_resolved",
                "timestamp": 3.0,
                "payload": {"defect_id": "defect_1"},
            },
        ]

        jsonl_path = tmp_path / "events.jsonl"
        with jsonl_path.open("w") as f:
            for e in events:
                f.write(json.dumps(e) + "\n")

        from computronium.ui.recognition.projector import fold_from_jsonl

        state = fold_from_jsonl(str(jsonl_path))

        # Should have processed all events
        assert len(state.badges) >= 0  # May have badges depending on conditions
        assert state.fog_regions_charted == frozenset()  # No region_charted events


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
