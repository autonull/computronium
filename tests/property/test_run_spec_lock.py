"""§3.2 lock: a bad RunSpec fails naming the field; two specs diff cleanly.

The gate D4 named. The old shape was a bare ``dict`` whose keys were an
implicit contract spread across six modules, so a wrong task, objective or
stage name was either never checked or silently dropped (see
``pipeline._build_search_space``, which filtered unknown objectives away
without a word).
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest
from pydantic import ValidationError

from computronium.experiment.evidence import RecordStore, StoreConfig, StoreError
from computronium.experiment.execution import PipelineConfig, StageId
from computronium.experiment.schema import (
    AXES_REGISTRIES,
    Domain,
    StructuralAxis,
    RUN_SPEC_VERSION,
    RunSpec,
    seed_all_registries,
)

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture(autouse=True)
def _seed() -> None:
    seed_all_registries()


def _spec(**overrides: Any) -> RunSpec:
    return RunSpec.model_validate({"task": "digits", **overrides})


# ---------------------------------------------------------------------------
# A bad spec fails, naming the offending field
# ---------------------------------------------------------------------------


def test_unknown_task_is_named() -> None:
    with pytest.raises(ValidationError, match="unknown task"):
        _spec(task="not_a_task")


def test_run_naming_no_task_fails() -> None:
    with pytest.raises(ValidationError, match="names no task"):
        RunSpec()


def test_unknown_objective_is_named() -> None:
    with pytest.raises(ValidationError, match="unknown objective"):
        _spec(objectives=("accuracy",))


def test_unknown_stage_is_named() -> None:
    with pytest.raises(ValidationError, match="unknown stage"):
        _spec(stages=("s1_frame", "s12_nonsense"))


def test_unknown_policy_is_named() -> None:
    with pytest.raises(ValidationError, match="unknown policy"):
        _spec(policy="model_based_tpe")


def test_unknown_axis_primitive_is_named() -> None:
    with pytest.raises(ValidationError, match="unknown primitive"):
        RunSpec.model_validate({
            "task": "digits",
            "axes": [{"axis": "credit", "primitives": ["nope"]}],
        })


def test_unknown_hyperparameter_domain_is_named() -> None:
    with pytest.raises(ValidationError, match="unknown name"):
        RunSpec.model_validate({
            "task": "digits",
            "hyperparameters": {"not_a_hyperparameter": {"lo": 0.0, "hi": 1.0}},
        })


def test_hyperparameter_domains_belong_to_the_run_not_to_an_axis() -> None:
    """``update_lr`` is read by dynamics and update; its owner is not an axis."""
    with pytest.raises(ValidationError, match="Extra inputs"):
        RunSpec.model_validate({
            "task": "digits",
            "axes": [
                {"axis": "credit", "domains": {"update_lr": {"lo": 1e-4, "hi": 1e-1}}}
            ],
        })
    RunSpec.model_validate({
        "task": "digits",
        "hyperparameters": {"update_lr": {"lo": 1e-4, "hi": 1e-1, "scale": "log"}},
    })


def test_extra_field_is_rejected_rather_than_ignored() -> None:
    """Write-only keys must die here, not become dead config (abc3 §5.1)."""
    with pytest.raises(ValidationError, match="data_origin_allocation"):
        RunSpec.model_validate({
            "task": "digits",
            "data_origin_allocation": {"exploration": 0.6},
        })


def test_negative_seed_is_rejected() -> None:
    with pytest.raises(ValidationError):
        _spec(n_seeds=0)


# ---------------------------------------------------------------------------
# Two specs diff cleanly (R41)
# ---------------------------------------------------------------------------


def test_diff_names_only_the_changed_fields() -> None:
    a = _spec(fidelity="L0", epochs=1)
    b = _spec(fidelity="L1", epochs=1)
    assert a.diff(b) == {"fidelity": ("L0", "L1")}
    assert b.diff(a) == {"fidelity": ("L1", "L0")}
    assert a.diff(a) == {}


def test_diff_reaches_into_axis_selections() -> None:
    a = _spec(axes=[{"axis": "credit", "primitives": ["gradient"]}])
    b = _spec(axes=[{"axis": "credit", "primitives": ["gradient", "pepita"]}])
    assert set(a.diff(b)) == {"axes"}


def test_spec_is_json_round_trippable() -> None:
    spec = _spec(objectives=("validation_accuracy",), policy="uniform_random")
    assert RunSpec.model_validate_json(spec.model_dump_json()) == spec
    assert RunSpec.from_dict(json.loads(json.dumps(spec.to_dict()))) == spec


def test_spec_version_is_declared_not_passed_separately(tmp_path: Path) -> None:
    """One source of truth: the store persists the version the spec claims."""
    assert _spec().version == RUN_SPEC_VERSION
    with RecordStore(StoreConfig(path=tmp_path / "v.duckdb")) as store:
        run_id = store.create_run(spec=_spec())
        info = store.query_run(run_id)
    assert info is not None
    assert info.spec_version == RUN_SPEC_VERSION
    assert info.spec == _spec()


def test_persisted_spec_that_no_longer_validates_fails_closed(tmp_path: Path) -> None:
    """A spec nobody can re-read means a run nobody can reproduce."""
    path = tmp_path / "drift.duckdb"
    with RecordStore(StoreConfig(path=path)) as store:
        run_id = store.create_run(spec=_spec())
        conn = store._conn  # ruff: ignore[private-member-access] - deliberate corruption
        assert conn is not None
        conn.execute(
            "UPDATE runs SET spec = ? WHERE run_id = ?",
            ['{"task": "digits", "seeds": 1}', run_id],
        )
    with (
        pytest.raises(StoreError, match="does not validate"),
        RecordStore(StoreConfig(path=path)) as store,
    ):
        store.query_runs()


# ---------------------------------------------------------------------------
# A run reproduces from its spec alone
# ---------------------------------------------------------------------------


def test_spec_alone_determines_stages_seed_and_budget() -> None:
    spec = _spec(
        stages=("s1_frame", "s2_space"),
        seed=7,
        budget_seconds=90.0,
        objectives=("validation_accuracy",),
    )
    config = PipelineConfig(run_id="r", run_spec=spec, seed=spec.seed)
    assert [StageId(s) for s in spec.stage_names] == [
        StageId.S1_FRAME,
        StageId.S2_SPACE,
    ]
    assert config.seed == 7
    assert spec.budget_seconds == 90.0


def test_spec_names_no_task_means_the_evaluator_cannot_load_one() -> None:
    """D14's shape as a type rule: the spec, not a literal, owns the task."""
    assert _spec().task_names == ("digits",)
    assert _spec(task="digits", tasks=("iris", "spiral")).task_names == (
        "digits",
        "iris",
        "spiral",
    )


def test_axis_selection_narrows_and_defaults_to_every_primitive() -> None:
    unrestricted = _spec().selected_primitives(StructuralAxis.CREDIT)
    assert unrestricted == tuple(
        sorted(
            n for n, s in AXES_REGISTRIES[StructuralAxis.CREDIT].items() if s.available
        )
    )
    narrowed = _spec(
        axes=[{"axis": "credit", "primitives": ["gradient"]}],
        hyperparameters={"update_lr": {"lo": 1e-4, "hi": 1e-1, "scale": "log"}},
    )
    assert narrowed.selected_primitives(StructuralAxis.CREDIT) == ("gradient",)
    selection = narrowed.selection(StructuralAxis.CREDIT)
    assert selection is not None
    assert narrowed.selection(StructuralAxis.UPDATE) is None
    domain = narrowed.hyperparameters["update_lr"]
    assert isinstance(domain, Domain)
    assert (domain.lo, domain.hi, domain.scale) == (1e-4, 1e-1, "log")
