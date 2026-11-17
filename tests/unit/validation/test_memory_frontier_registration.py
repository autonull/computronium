"""T6a's registration locks (TODO93 §4, §8.1).

The registration must fix, before the claim cells run:

- the L=4→8 depth rung, because T6c refused the deeper pass;
- the per-arm frozen LR from the L=8 ladder, with the claim seeds disjoint
  from the pilot and ladder seeds;
- both positive controls, the binding appendix, and the stop rule;
- the minimal claim ladder: 3 arms × 2 depths × 5 paired seeds, not the grid.

The claim is W1's sharper form -- accuracy within delta at ≤0.5× activation
bytes -- so no hypervolume reference point is registered. The committed JSON
is read by a claim-table test, and `ThresholdRegistration.from_dict` ignores
the extra keys: the loader does not enforce the box or the binding gate.
"""

from __future__ import annotations

import json
from dataclasses import replace
from typing import cast

import pytest

from computronium.validation import memory_frontier as frontier
from computronium.validation.preregistration import ThresholdRegistration

_POINT = frontier.PilotPoint(depth=8, width=512, batch=2048, steps=200)
_LADDER = {arm: {"0.1": 0.300, "0.3": 0.385, "1.0": 0.140} for arm in frontier.ARMS}
_STREAM_LADDER = {
    "backprop": {"0.003": 0.300, "0.01": 0.315, "0.03": 0.326},
    "backprop+ckpt": {"0.003": 0.300, "0.01": 0.315, "0.03": 0.326},
    "hybrid": {"0.003": 0.150, "0.01": 0.160, "0.03": 0.167},
    "local": {"0.003": 0.280, "0.01": 0.300, "0.03": 0.310},
}


def _instrument(measured_c: float = 4.125) -> frontier.InstrumentControl:
    return frontier.InstrumentControl(
        point=frontier.PilotPoint(),
        measured_c=measured_c,
        spread=0.0,
        tolerance=0.10,
        calibration=(),
    )


def _learning() -> frontier.LearningControl:
    return frontier.LearningControl(
        depth=8,
        steps=200,
        backprop_acc=0.385,
        checkpointed_acc=0.385,
        floor=0.375,
        margin=0.01,
        passed=True,
    )


def _arm(
    arm: str,
    *,
    acc: float,
    activations_mb: float,
    seed: int = 21,
    depth: int = 8,
) -> frontier.ArmCell:
    return frontier.ArmCell(
        arm=arm,
        seed=seed,
        depth=depth,
        batch=500,
        steps=200,
        lr=0.3,
        val_acc=acc,
        walltime_s=1.0,
        forward_equivalents=1.0,
        peak_mb=activations_mb + 2.0,
        params_mb=1.0,
        optimizer_mb=None,
        activations_mb=activations_mb,
        auxiliary_mb=None,
        activation_share=0.8,
        binding=True,
    )


def _screen(
    *,
    hybrid_acc: float = 0.385,
    hybrid_mb: float = 40.0,
    baseline_acc: float = 0.385,
    baseline_mb: float = 85.0,
    confirmation_hybrid_acc: float | None = None,
    confirmation_hybrid_mb: float | None = None,
) -> frontier.ScreenVerdict:
    return frontier.ScreenVerdict(
        hybrid=_arm("hybrid", acc=hybrid_acc, activations_mb=hybrid_mb),
        baseline=_arm("backprop+ckpt", acc=baseline_acc, activations_mb=baseline_mb),
        confirmation_hybrid=_arm(
            "hybrid",
            acc=hybrid_acc
            if confirmation_hybrid_acc is None
            else confirmation_hybrid_acc,
            activations_mb=hybrid_mb
            if confirmation_hybrid_mb is None
            else confirmation_hybrid_mb,
            seed=22,
        ),
        confirmation_baseline=_arm(
            "backprop+ckpt", acc=baseline_acc, activations_mb=baseline_mb, seed=22
        ),
    )


def _registration(
    *,
    point: frontier.PilotPoint | None = None,
    ladder: dict[str, dict[str, float]] | None = None,
    instrument: frontier.InstrumentControl | None = None,
    learning: frontier.LearningControl | None = None,
    screen: frontier.ScreenVerdict | None = None,
    box: frontier.RegistrationBox = frontier.AS_REGISTERED,
) -> frontier.MemoryFrontierRegistration:
    return frontier.build_registration(
        point=point or _POINT,
        ladder=ladder or _LADDER,
        instrument=instrument or _instrument(),
        learning=learning or _learning(),
        screen=screen,
        box=box,
    )


def test_the_registration_carries_every_essential(tmp_path) -> None:
    registration = _registration()
    raw = json.loads(registration.write(tmp_path).read_text(encoding="utf-8"))
    assert raw["threshold"] == frontier.DELTA == 0.01
    assert raw["min_seeds"] == frontier.N_MAX == 5
    assert raw["depth_rung"] == [4, 8]
    assert len(raw["lr_ladder"]) == len(frontier.ARMS) * len(frontier.LR_LADDER)
    assert len(cast("list[object]", raw["claim_cells"])) == 30
    assert raw["box"]["depth_rung"] == [4, 8]
    assert raw["box"]["floor"] == pytest.approx(0.375, abs=1e-3)
    assert raw["box"]["depth_trigger"]
    assert raw["controls"]["instrument"]["tolerance"] == 0.10
    assert raw["controls"]["instrument"]["passed"] is True
    assert raw["controls"]["learning"]["passed"] is True
    assert raw["binding"]["rows"]
    assert raw["stop_rule"]
    assert raw["decision"] == "activation_ratio<=0.5x at accuracy within delta"


def test_the_loader_ignores_the_box_and_the_binding_gate() -> None:
    """The claim-table test must read the raw JSON, not trust the loader."""
    raw = _registration().to_dict()
    loaded = ThresholdRegistration.from_dict(raw)
    assert loaded.metric == "val_acc"
    assert loaded.threshold == frontier.DELTA
    assert loaded.min_seeds == frontier.N_MAX
    assert "binding" not in loaded.to_dict()
    assert _registration().binding.share_floor == frontier.BINDING_SHARE == 0.5


def test_the_claim_seeds_are_disjoint_from_the_pilot_and_ladder_seeds() -> None:
    registration = _registration()
    claim = set(registration.claim_seeds)
    assert len(claim) == frontier.N_MAX
    assert claim.isdisjoint(registration.ladder_seeds)
    assert claim.isdisjoint(registration.pilot_seeds)
    assert registration.data_seed not in claim
    assert registration.data_seed not in {
        *registration.ladder_seeds,
        *registration.pilot_seeds,
    }


def test_the_claim_ladder_is_the_minimal_rung_not_the_grid() -> None:
    registration = _registration()
    cells = registration.claim_cells
    assert len(cells) == 30
    assert {cell.arm for cell in cells} == set(frontier.CLAIM_ARMS)
    assert {cell.depth for cell in cells} == {4, 8}
    assert 16 not in {cell.depth for cell in cells}
    for arm in frontier.CLAIM_ARMS:
        for depth in (4, 8):
            seeds = [
                cell.seed for cell in cells if cell.arm == arm and cell.depth == depth
            ]
            assert seeds == list(frontier.CLAIM_SEEDS)
    assert all(cell.affordable and cell.runnable for cell in cells)
    assert not any(cell.measured for cell in cells)
    assert all(cell.lr == registration.lrs[cell.arm] for cell in cells)


def test_the_best_ladder_point_freezes_and_a_tie_keeps_the_smaller_lr() -> None:
    ladder = {
        **_LADDER,
        "backprop": {"0.1": 0.400, "0.3": 0.400, "1.0": 0.100},
    }
    registration = _registration(ladder=ladder)
    assert registration.lrs["backprop"] == 0.1
    assert registration.lrs["hybrid"] == 0.3


def test_a_failed_control_refuses_a_registration() -> None:
    with pytest.raises(ValueError, match="control"):
        _registration(learning=replace(_learning(), passed=False))
    with pytest.raises(ValueError, match="control"):
        _registration(instrument=_instrument(measured_c=1.0))


def test_the_binding_appendix_prices_the_claim_box() -> None:
    registration = _registration()
    rows = registration.binding.rows
    assert {row.depth for row in rows} == {4, 8}
    for row in rows:
        assert row.binding is True
        assert row.activation_share >= frontier.BINDING_SHARE
        assert row.peak_mb == pytest.approx(
            row.activations_mb + 2 * row.params_mb, abs=0.2
        )
    assert registration.binding.pilot_appendix.depth == 32
    assert registration.binding.pilot_appendix.width == 1024
    assert registration.binding.pilot_appendix.batch == 8192


def test_the_screen_refuses_the_claim_at_the_ladder_best_point() -> None:
    """The L=8 ladder: the hybrid is below both bars, so the claim is a trigger."""
    screen = _screen(
        hybrid_acc=0.167,
        hybrid_mb=103.0,
        baseline_acc=0.385,
        baseline_mb=85.0,
        confirmation_hybrid_acc=0.170,
        confirmation_hybrid_mb=103.0,
    )
    assert screen.activation_ratio == pytest.approx(103.0 / 85.0)
    assert not screen.meets_accuracy
    assert not screen.meets_memory
    assert screen.verdict == "refuse"
    assert "below" in screen.reason and "above" in screen.reason
    assert "T6c" in screen.trigger

    raw = json.loads(json.dumps(_registration(screen=screen).to_dict()))
    assert raw["screen"]["verdict"] == "refuse"
    assert raw["screen"]["hybrid"]["val_acc"] == pytest.approx(0.167)
    assert raw["screen"]["baseline"]["activations_mb"] == pytest.approx(85.0)


def test_the_screen_is_a_candidate_only_when_the_confirmation_repeats() -> None:
    assert _screen().verdict == "candidate"
    assert _screen(confirmation_hybrid_acc=0.36).verdict == "coordinate"
    assert _screen(confirmation_hybrid_mb=60.0).verdict == "coordinate"


def test_the_screen_is_marginal_at_the_floor() -> None:
    """Within one held-out resolution of the floor is a coordinate, not a claim."""
    screen = _screen(hybrid_acc=0.376)
    assert screen.meets_accuracy
    assert screen.verdict == "coordinate"


def test_the_registration_is_written_then_committed_without_overwrite(tmp_path) -> None:
    registration = _registration()
    registration.write(tmp_path)
    committed = tmp_path / "committed.json"
    registration.commit(committed)
    first = committed.read_text(encoding="utf-8")

    other = _registration(
        ladder={
            arm: {lr: value / 2 for lr, value in points.items()}
            for arm, points in _LADDER.items()
        }
    )
    other.commit(committed)
    assert committed.read_text(encoding="utf-8") == first


def test_the_stream_box_states_its_own_rung_and_path(tmp_path) -> None:
    """The re-registration is a different box, not the same claim re-run."""
    box = replace(frontier.STREAM_BOX, committed=tmp_path / "stream.json")
    registration = _registration(box=box, point=box.point, ladder=_STREAM_LADDER)
    raw = registration.to_dict()
    box_raw = cast("dict[str, object]", raw["box"])
    assert registration.depth_rung == (8, 32)
    assert registration.point.stream_norm is True
    assert registration.point.batch == 4096
    assert registration.committed_path == tmp_path / "stream.json"
    assert registration.lrs == dict.fromkeys(frontier.ARMS, 0.03)
    assert box_raw["label"] == "l8-32-stream"
    assert box_raw["stream_norm"] is True
    assert box_raw["box_triage_activation_ratio"] == 0.48
    assert "4 steps" in cast("str", box_raw["box_triage_ruler"])
    assert len(cast("list[object]", raw["claim_cells"])) == 30
    assert {cell.depth for cell in registration.claim_cells} == {8, 32}
    assert {row.depth for row in registration.binding.rows} == {8, 32}
    assert all(cell.affordable for cell in registration.claim_cells)
    assert all(
        cell.lr == registration.lrs[cell.arm] for cell in registration.claim_cells
    )


def test_a_box_whose_own_ratio_misses_the_memory_bar_is_refused() -> None:
    """The B=2048 box measures 0.53×, so it cannot register the 0.5× claim."""
    infeasible = replace(frontier.STREAM_BOX, label="l32-b2048", measured_ratio=0.53)
    with pytest.raises(ValueError, match="activation ratio"):
        _registration(
            box=infeasible, point=frontier.STREAM_BOX.point, ladder=_STREAM_LADDER
        )
    assert frontier.STREAM_BOX.meets_memory_bar is True


def test_the_learning_control_bars_a_chance_level_stack() -> None:
    """A control at chance passes the relative floor, so it must fail the box."""
    chance = frontier.learning_control_gate(
        depth=8, steps=200, backprop_acc=0.100, checkpointed_acc=0.100
    )
    assert chance.floor == pytest.approx(0.09)
    assert chance.passed is False
    trained = frontier.learning_control_gate(
        depth=8, steps=200, backprop_acc=0.385, checkpointed_acc=0.385
    )
    assert trained.passed is True
    below = frontier.learning_control_gate(
        depth=8, steps=200, backprop_acc=0.360, checkpointed_acc=0.385
    )
    assert below.passed is False


def test_the_two_boxes_commit_to_their_own_paths(tmp_path) -> None:
    first = replace(frontier.AS_REGISTERED, committed=tmp_path / "first.json")
    second = replace(frontier.STREAM_BOX, committed=tmp_path / "second.json")
    a = _registration(box=first)
    b = _registration(box=second, point=second.point, ladder=_STREAM_LADDER)
    a.commit()
    b.commit()
    assert json.loads(a.committed_path.read_text(encoding="utf-8"))["box"]["label"] == (
        "l4-8"
    )
    assert json.loads(b.committed_path.read_text(encoding="utf-8"))["box"]["label"] == (
        "l8-32-stream"
    )
    assert a.committed_path != b.committed_path
