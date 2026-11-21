"""Locks for the breadth gate: the AGENTS condition, not its prose.

The gate must fail when a credit has one family, when a cell is legacy and
below its task bar, when it is on a refused combination, or when it is not
L2/n>=5. Removing any of those filters makes a test fail.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from computronium.experiment.evidence.breadth import breadth_gate
from computronium.experiment.registry.task_registry import PassBar
from computronium.experiment.schema.seed_registries import seed_all_registries

BAR = PassBar("val_acc", "maximize", 0.5)


@pytest.fixture(autouse=True, scope="module")
def _registries() -> None:
    seed_all_registries()


def _record(
    credit: str,
    task: str,
    *,
    key: str | None = None,
    value: float = 0.8,
    cleared: bool | None = True,
    fidelity: str = "L2",
    n_seeds: int = 5,
    substrate: str = "digital",
    verdict: str = "PASS",
) -> SimpleNamespace:
    payload: dict[str, object] = {"val_acc": value}
    if cleared is not None:
        payload["pass_bar_cleared"] = cleared
    return SimpleNamespace(
        credit=credit,
        measurement_key=key or f"{credit}:{task}:{value}",
        substrate=substrate,
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        update="adam",
        params={},
        schedule=SimpleNamespace(fidelity=fidelity, n_seeds=n_seeds, task_id=task),
        status=SimpleNamespace(gate_verdict=SimpleNamespace(value=verdict)),
        payload=payload,
    )


def _families(task: str) -> tuple[str, ...]:
    return {
        "mnist": ("vision",),
        "cora": ("graph",),
        "copy_task": ("memory",),
        "delayed_cue": ("sequence", "continual"),
    }[task]


def _run(records, refusal=None):
    return breadth_gate(records, _families, lambda _task: BAR, refusal=refusal)


def test_two_families_pass_and_one_family_fails() -> None:
    gate = _run([
        _record("gradient", "mnist", key="g1"),
        _record("gradient", "cora", key="g2"),
        _record("local_goodness", "mnist", key="l1"),
    ])
    rows = {row.credit: row for row in gate.credits}
    assert rows["gradient"].green is True
    assert rows["gradient"].families == (("graph", 1), ("vision", 1))
    assert rows["local_goodness"].green is False
    assert gate.green is False


def test_a_task_that_declares_two_families_counts_for_both() -> None:
    """One cell on a two-family task is a cell on each declared family."""
    gate = _run([_record("local_goodness", "delayed_cue")])
    row = next(row for row in gate.credits if row.credit == "local_goodness")
    assert row.families == (("continual", 1), ("sequence", 1))
    assert row.green is True


def test_duplicate_measurement_key_counts_once() -> None:
    gate = _run([
        _record("gradient", "mnist", key="same"),
        _record("gradient", "mnist", key="same"),
        _record("gradient", "cora", key="other"),
    ])
    row = next(row for row in gate.credits if row.credit == "gradient")
    assert row.families == (("graph", 1), ("vision", 1))
    assert row.keys == 2


def test_legacy_record_is_reassessed_against_its_bar() -> None:
    gate = _run([
        _record("gradient", "mnist", cleared=None, value=0.8),
        _record("gradient", "cora", cleared=None, value=0.4),
    ])
    row = next(row for row in gate.credits if row.credit == "gradient")
    assert row.families == (("vision", 1),)
    assert gate.assessed_legacy == 1
    assert gate.excluded_unbarred == 1


def test_refused_cell_is_excluded() -> None:
    def refusal(_coordinate, _task):
        return "void constraint: complex_substrate_real_compute"

    gate = _run(
        [_record("gradient", "mnist", substrate="complex")],
        refusal=refusal,
    )
    row = next(row for row in gate.credits if row.credit == "gradient")
    assert row.keys == 0
    assert gate.excluded_refused == 1


def test_error_blind_credit_has_no_row() -> None:
    gate = _run([_record("homeostatic", "mnist")])
    assert all(row.credit != "homeostatic" for row in gate.credits)


def test_fidelity_and_seed_floor() -> None:
    gate = _run([
        _record("gradient", "mnist", fidelity="L1"),
        _record("gradient", "cora", n_seeds=4),
    ])
    row = next(row for row in gate.credits if row.credit == "gradient")
    assert row.keys == 0


def test_failed_gate_verdict_is_excluded() -> None:
    gate = _run([_record("gradient", "mnist", verdict="FAIL")])
    row = next(row for row in gate.credits if row.credit == "gradient")
    assert row.keys == 0


def test_unseeded_registry_is_never_green(monkeypatch) -> None:
    """An empty credit list must fail loud, not pass by vacuity."""
    monkeypatch.setattr(
        "computronium.experiment.evidence.breadth._error_aware_credits",
        lambda: (),
    )
    with pytest.raises(RuntimeError, match="no error-aware credits"):
        _run([])
