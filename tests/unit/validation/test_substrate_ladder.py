"""The D1 substrate gate must promote only on repeated parity with less state.

The screen's verdict is a predicate the repository evaluates: parity at the
arm's best settle length on both seeds with device state below the digital
width promotes the track to its matched comparison; a flat or falling arm
refuses it at this box with a trigger; a constrained substrate that never
trains parks the track; a learning control below the floor invalidates the
run. The state ruler is the device width, and the per-arm LR ladder is the
fair chance -- a shared LR collapsed ternary and diverged the others
(pilot, CORRECTION 17).
"""

from __future__ import annotations

import json
from dataclasses import asdict

from computronium.validation.substrate_ladder import (
    DEVICE_BITS,
    FLOOR,
    PARITY_DELTA,
    SubstrateCell,
    _arm_parity,
    _build_system,
    _verdict,
    device_state,
    read_cells,
    replay_substrate_ladder,
)

DIGITAL_BYTES = 4000
MEMBER_BYTES = {"ternary": 250, "memristive": 2000}


def _cell(
    arm: str,
    *,
    stage: str = "steps",
    steps: int = 10,
    seed: int = 59,
    acc: float | None = 0.90,
    device_bytes: int | None = None,
    refused: bool = False,
) -> SubstrateCell:
    per_weight = 4.0 if arm in {"digital", "backprop"} else 0.25
    device_bytes = device_bytes if device_bytes is not None else DIGITAL_BYTES
    return SubstrateCell(
        arm=arm,
        stage=stage,
        seed=seed,
        lr=1e-2,
        max_steps=steps,
        device="cpu",
        val_acc=None if refused else acc,
        train_acc=None if refused else acc,
        device_state_bytes=device_bytes,
        device_state_per_weight=per_weight,
        train_state_bytes=2048,
        params_mb=1.0,
        optimizer_mb=1.0,
        activations_mb=1.0,
        steps=0 if refused else 600,
        time_s=1.0,
        forward_equivalents=None,
        note="refused" if refused else "",
        refused=refused,
    )


def _ladder(
    arm: str, accs: tuple[float, float, float], **kwargs
) -> tuple[SubstrateCell, ...]:
    return tuple(
        _cell(arm, steps=steps, acc=acc, **kwargs)
        for steps, acc in zip((5, 10, 20), accs, strict=True)
    )


def _confirmation(arm: str, acc: float, *, steps: int = 10, seed: int = 60):
    return _cell(
        arm,
        stage="confirm",
        steps=steps,
        seed=seed,
        acc=acc,
        device_bytes=MEMBER_BYTES.get(arm, DIGITAL_BYTES),
    )


def _gate(
    ladder: tuple[SubstrateCell, ...], confirmation: tuple[SubstrateCell, ...]
) -> tuple[str, str]:
    return _verdict(
        control=_cell("backprop", stage="control", acc=0.92),
        ladder=ladder,
        confirmation=confirmation,
    )


def test_parity_on_two_seeds_promotes_the_memristive_arm() -> None:
    ladder = (
        *_ladder("digital", (0.88, 0.90, 0.90), device_bytes=DIGITAL_BYTES),
        *_ladder("memristive", (0.87, 0.895, 0.885), device_bytes=2000),
        *_ladder("ternary", (0.60, 0.62, 0.61), device_bytes=250),
    )
    confirmation = (
        _cell(
            "digital",
            stage="confirm",
            steps=10,
            seed=60,
            acc=0.895,
            device_bytes=DIGITAL_BYTES,
        ),
        _cell(
            "memristive",
            stage="confirm",
            steps=10,
            seed=60,
            acc=0.89,
            device_bytes=2000,
        ),
    )
    verdict, reason = _gate(ladder, confirmation)
    assert verdict == "promote"
    assert "memristive" in reason
    assert "ternary" not in reason


def test_a_shared_parity_gap_refuses_at_this_box() -> None:
    ladder = (
        *_ladder("digital", (0.88, 0.90, 0.90), device_bytes=DIGITAL_BYTES),
        *_ladder("memristive", (0.80, 0.81, 0.80), device_bytes=2000),
        *_ladder("ternary", (0.60, 0.62, 0.61), device_bytes=250),
    )
    confirmation = (
        _cell(
            "digital",
            stage="confirm",
            steps=10,
            seed=60,
            acc=0.895,
            device_bytes=DIGITAL_BYTES,
        ),
        _cell(
            "memristive",
            stage="confirm",
            steps=10,
            seed=60,
            acc=0.80,
            device_bytes=2000,
        ),
    )
    verdict, reason = _gate(ladder, confirmation)
    assert verdict == "refuse"
    assert "two seeds" in reason


def test_confirmation_below_the_margin_refuses_even_when_the_ladder_matches() -> None:
    ladder = (
        *_ladder("digital", (0.88, 0.90, 0.90), device_bytes=DIGITAL_BYTES),
        *_ladder("memristive", (0.87, 0.895, 0.885), device_bytes=2000),
    )
    confirmation = (
        _cell(
            "digital",
            stage="confirm",
            steps=10,
            seed=60,
            acc=0.895,
            device_bytes=DIGITAL_BYTES,
        ),
        _cell(
            "memristive",
            stage="confirm",
            steps=10,
            seed=60,
            acc=0.80,
            device_bytes=2000,
        ),
    )
    verdict, _ = _gate(ladder, confirmation)
    assert verdict == "refuse"


def test_parity_without_a_smaller_device_state_is_not_a_promotion() -> None:
    ladder = (
        *_ladder("digital", (0.88, 0.90, 0.90), device_bytes=DIGITAL_BYTES),
        *_ladder("memristive", (0.87, 0.895, 0.885), device_bytes=DIGITAL_BYTES),
    )
    confirmation = (
        _cell(
            "digital",
            stage="confirm",
            steps=10,
            seed=60,
            acc=0.895,
            device_bytes=DIGITAL_BYTES,
        ),
        _cell(
            "memristive",
            stage="confirm",
            steps=10,
            seed=60,
            acc=0.89,
            device_bytes=DIGITAL_BYTES,
        ),
    )
    verdict, _ = _gate(ladder, confirmation)
    assert verdict == "refuse"


def test_a_control_below_the_floor_invalidates_the_run() -> None:
    verdict, reason = _verdict(
        control=_cell("backprop", stage="control", acc=FLOOR - 0.01),
        ladder=_ladder("memristive", (0.90, 0.90, 0.90), device_bytes=2000),
        confirmation=(_confirmation("memristive", 0.90),),
    )
    assert verdict == "invalid-learning-control"
    assert "not the substrate" in reason


def test_no_trained_constrained_arm_parks_with_a_trigger() -> None:
    ladder = (
        *_ladder("digital", (0.88, 0.90, 0.90), device_bytes=DIGITAL_BYTES),
        _cell("ternary", refused=True),
        _cell("memristive", refused=True),
    )
    verdict, reason = _verdict(
        control=_cell("backprop", stage="control", acc=0.92),
        ladder=ladder,
        confirmation=(),
    )
    assert verdict == "park"
    assert "trigger" in reason


def test_the_parity_margin_is_the_registered_one() -> None:
    reference = _cell("digital", acc=0.90, device_bytes=DIGITAL_BYTES)
    at_margin = _cell("memristive", acc=0.90 - PARITY_DELTA, device_bytes=2000)
    inside = _cell("memristive", acc=0.90 - PARITY_DELTA / 2, device_bytes=2000)
    outside = _cell("memristive", acc=0.90 - PARITY_DELTA - 1e-3, device_bytes=2000)
    digital_by_steps = {10: reference}
    confirm = (
        _cell(
            "digital",
            stage="confirm",
            steps=10,
            seed=60,
            acc=0.90,
            device_bytes=DIGITAL_BYTES,
        ),
        _cell(
            "memristive",
            stage="confirm",
            steps=10,
            seed=60,
            acc=0.90,
            device_bytes=2000,
        ),
    )
    assert _arm_parity(
        "memristive",
        ladder=(inside,),
        confirmation=confirm,
        digital_by_steps=digital_by_steps,
    )
    assert not _arm_parity(
        "memristive",
        ladder=(outside,),
        confirmation=confirm,
        digital_by_steps=digital_by_steps,
    )
    assert at_margin.val_acc is not None


def test_device_state_uses_each_substrate_width_and_is_not_a_zero() -> None:
    widths = {}
    for arm in ("digital", "ternary", "memristive"):
        system = _build_system(arm, seed=59, lr=1e-3, max_steps=5)
        total, per_weight = device_state(system, arm)
        assert total > 0
        widths[arm] = per_weight
    assert DEVICE_BITS["ternary"] < DEVICE_BITS["memristive"] < DEVICE_BITS["digital"]
    assert widths["ternary"] < widths["memristive"] < widths["digital"]
    assert widths["memristive"] == 2.0


def test_the_cell_log_round_trips_and_replays(tmp_path) -> None:
    cells = (
        _cell("backprop", stage="control", acc=0.92),
        *_ladder("digital", (0.88, 0.90, 0.90), device_bytes=DIGITAL_BYTES),
        *_ladder("memristive", (0.87, 0.895, 0.885), device_bytes=2000),
        _cell(
            "digital",
            stage="confirm",
            steps=10,
            seed=60,
            acc=0.895,
            device_bytes=DIGITAL_BYTES,
        ),
        _cell(
            "memristive",
            stage="confirm",
            steps=10,
            seed=60,
            acc=0.89,
            device_bytes=2000,
        ),
    )
    progress = tmp_path / "substrate.cells.jsonl"
    progress.write_text(
        "\n".join(json.dumps(asdict(cell)) for cell in cells) + "\n",
        encoding="utf-8",
    )
    assert read_cells(progress) == cells
    report = replay_substrate_ladder(progress=progress)
    assert report.verdict == "promote"
    assert report.control.val_acc == 0.92
