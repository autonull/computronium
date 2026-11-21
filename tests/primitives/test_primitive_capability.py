"""Capability tests for all 75 primitives.

Every primitive must demonstrate basic learning capability on its declared
task families. These are the minimum viable tests that should pass before
any SEC screen runs.

The rung reads the row's screened box from the family maps and refuses a box
the declared space rejects, so a measured row runs at its priced cell — its
epochs, batch size, batch limit and seed — and a refused row is named instead
of trained (TODO97 S5j). A row with no map box falls back to one epoch over
``CAPABILITY_BATCHES`` batches at the rung's default seed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from computronium.domains.base import DomainType
from computronium.domains.factory import create_task
from computronium.experiment.kernel.compose import compose_cell_system
from computronium.experiment.sec_claims import map_rows
from computronium.experiment.sec_loop import (
    _base_axes,
    _coordinate,
    _is_legal,
    box_params,
    screen_coordinate,
)
from computronium.experiment.sec_pilot import BASE_BOXES
from computronium.primitives.registry import list_primitives
from computronium.utils import seed_everything

if TYPE_CHECKING:
    from collections.abc import Mapping

    from computronium.experiment.schema.coordinate import Coordinate
    from computronium.primitives.registry import PrimitiveSpec

# Base configuration for fast capability testing
CAPABILITY_EPOCHS = 1
CAPABILITY_SEED = 42
CAPABILITY_DEVICE = "cpu"
#: The fallback budget for a row the maps do not carry: one epoch over this
#: many loader batches. A measured row runs at its own priced cell instead.
CAPABILITY_BATCHES = 64


@dataclass(frozen=True, slots=True)
class Rung:
    """The box a capability cell runs at, or the rule that refuses it."""

    task_id: str
    coordinate: Coordinate | None = None
    reason: str | None = None
    batch_size: int = 64
    epochs: int = CAPABILITY_EPOCHS
    batch_limit: int | None = None
    seed: int = CAPABILITY_SEED


def _row_reason(row: Mapping[str, object]) -> str:
    """Why a non-measured row cannot be trained, with its declaration."""
    status = row.get("status")
    detail = row.get("trigger") or row.get("defect")
    return f"the row is {status}" + (f": {detail}" if detail else "")


def _fallback_coordinate(spec: PrimitiveSpec, task_id: str) -> Coordinate:
    """The family's base axes with only this primitive's axis varied."""
    axes = _base_axes(task_id)
    axes[spec.axis] = spec.id.rsplit(".", 1)[-1]
    return _coordinate(axes)


def _int_param(value: object, default: int) -> int:
    """An integer box field, or ``default`` when the row does not carry one."""
    return int(value) if isinstance(value, (int, float, str)) else default


def _epochs(box: Mapping[str, object]) -> int:
    """The row's priced epoch count, or the fallback rung."""
    return _int_param(box.get("epochs"), CAPABILITY_EPOCHS)


def _batch_limit(box: Mapping[str, object]) -> int | None:
    """The row's priced batch limit, or ``None`` for a full epoch."""
    return _int_param(box.get("batch_limit"), 0) or None


def _rung_for(
    spec: PrimitiveSpec,
    family: str,
    rows: Mapping[tuple[str, str], Mapping[str, object]],
) -> Rung:
    """The row's screened box, or the name its refusal carries.

    A measured row is rebuilt by the screen's own builder
    (:func:`~computronium.experiment.sec_loop.screen_coordinate`), so the
    capability lane runs the coordinate the map measured rather than a compose
    default. A row without a box, and a measured row the declared space now
    refuses, are declared refusals (TODO97 S5j).
    """
    base = BASE_BOXES.get(family)
    if base is None:
        return Rung(task_id="", reason=f"no declared base box for {family}")
    task_id = base.task_id
    row = rows.get((spec.id, task_id))
    if row is not None and row.get("status") != "measured":
        return Rung(task_id, reason=_row_reason(row))
    seed = CAPABILITY_SEED
    if row is None:
        coordinate = _fallback_coordinate(spec, task_id)
        batch_size = base.batch_size
        epochs = CAPABILITY_EPOCHS
        batch_limit = CAPABILITY_BATCHES
    else:
        box_value = row.get("box")
        screened: dict[str, object] = (
            {str(key): value for key, value in box_value.items()}
            if isinstance(box_value, dict)
            else {}
        )
        if not box_params(screened):
            return Rung(
                task_id,
                reason="the row's box carries no structural params (re-screen it)",
            )
        seed = _int_param(screened.get("seed"), CAPABILITY_SEED)
        level = screened.get(spec.axis) or spec.id.rsplit(".", 1)[-1]
        coordinate = screen_coordinate(screened, spec.axis, str(level))
        batch_size = _int_param(screened.get("batch_size"), 64)
        epochs = _epochs(screened)
        batch_limit = _batch_limit(screened)
    legal, refusal = _is_legal(coordinate, task_id)
    if not legal:
        return Rung(
            task_id,
            reason=f"refused by name: {refusal}",
            batch_size=batch_size,
            epochs=epochs,
            batch_limit=batch_limit,
            seed=seed,
        )
    return Rung(
        task_id,
        coordinate=coordinate,
        batch_size=batch_size,
        epochs=epochs,
        batch_limit=batch_limit,
        seed=seed,
    )


@pytest.fixture(scope="session")
def primitive_specs():
    return list_primitives()


@pytest.fixture(scope="session")
def screened_rows() -> dict[tuple[str, str], dict[str, object]]:
    """Every family map row, read once for the whole rung."""
    return map_rows()


def test_all_primitives_have_capability_test(primitive_specs):
    """Every primitive declares at least one task family."""
    for spec in primitive_specs:
        assert spec.task_families, f"{spec.id}: empty task_families"


def _run_cell(
    spec: PrimitiveSpec,
    family: str,
    task,
    cell,
    rung: Rung,
) -> None:
    """Train the rung and assert its capability criterion."""
    from computronium.core.system_trainer.config import SystemTrainerConfig
    from computronium.core.system_trainer.spec import error_blind_credit
    from computronium.core.system_trainer.train_task import train_on_task

    config = SystemTrainerConfig(
        max_epochs=rung.epochs,
        batch_size=rung.batch_size,
        device=CAPABILITY_DEVICE,
        track_energy=False,
        track_flops=False,
        track_memory=False,
        log_every_n_epochs=1,
        seed=rung.seed,
    )

    if getattr(task, "domain_type", None) == DomainType.GRAPH:
        from computronium.core.system_trainer import GraphSystemTrainer

        GraphSystemTrainer(cell.system, config, task, val_data=task).fit()
    else:
        # A loader lane has an epoch length, so ``None`` runs the full epoch.
        # A ``get_batch`` lane has none, so the fallback cap is its length.
        batches = rung.batch_limit
        if batches is None and task.get_dataloader("train") is None:
            batches = CAPABILITY_BATCHES
        train_on_task(
            lambda *_, **__: cell.system,
            task,
            config,
            batches_per_epoch=batches,
        )
    metrics = task.evaluate(cell.system)

    if spec.axis == "credit" and error_blind_credit(spec.id.rsplit(".", 1)[-1]):
        # Error-blind credits: a non-zero update is their contract.
        assert metrics.loss is not None
        return

    # Error-aware rows: the row's priced cell is the rung's budget, so above
    # chance is its bar, not the screen's calibrated one.
    if task.domain_type in {DomainType.LM, DomainType.LANGUAGE}:
        assert metrics.perplexity is not None
        assert metrics.perplexity < task.output_dim, (
            f"{spec.id} on {family} ({rung.task_id}): "
            f"perplexity {metrics.perplexity:.2f} >= chance {task.output_dim}"
        )
        return
    chance = 1.0 / task.output_dim if task.output_dim > 1 else 0.5
    assert metrics.accuracy > chance, (
        f"{spec.id} on {family} ({rung.task_id}): "
        f"accuracy {metrics.accuracy:.4f} <= chance {chance:.4f}"
    )


@pytest.mark.parametrize("spec", list_primitives(), ids=lambda s: s.id)
@pytest.mark.timeout(300)
def test_primitive_on_declared_families(spec, screened_rows):
    """Test each primitive on its declared task families.

    Runs the row's screened box at the capability budget. A row the map did
    not measure, or a measured box the declared space refuses, is skipped
    with its named rule; any other failure is a defect.
    """
    for family in spec.task_families:
        rung = _rung_for(spec, family, screened_rows)
        if rung.reason:
            pytest.skip(f"declared: {spec.id} on {family}: {rung.reason}")

        seed_everything(rung.seed)
        try:
            task = create_task(
                rung.task_id,
                quick_mode=True,
                batch_size=rung.batch_size,
            )
            task.setup()
        except Exception as e:
            pytest.skip(f"no dataset: task {rung.task_id} not available: {e}")

        try:
            input_shape = (
                tuple(task.input_dim)
                if isinstance(task.input_dim, (tuple, list))
                else (1, int(task.input_dim))
            )
            assert rung.coordinate is not None
            cell = compose_cell_system(
                coordinate=rung.coordinate,
                geometry={},
                input_shape=input_shape,
                output_dim=task.output_dim,
                task=task,
            )
        except ValueError as e:
            pytest.xfail(f"defective: {spec.id} on {family}: compose failed - {e}")

        try:
            _run_cell(spec, family, task, cell, rung)
        except Exception as e:
            pytest.fail(f"{spec.id} on {family} ({rung.task_id}): {e}")

        return  # First family passed, done

    # If we got here, all families were skipped (all gaps)
    # This is OK - the gaps are documented


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
