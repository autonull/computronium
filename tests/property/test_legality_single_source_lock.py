"""Lock: one table per legality rule (TODO90 B9).

Two NCA × instantaneous voids lived twice — as constraint rows and as
``SystemConfig.validate`` methods — and the S5 stage carried a third copy of
the "does this rule read a hyperparameter" traversal that ignored
``output_dim``. This lock pins the consolidated form:

* ``NCA_CELL_MODE_CREDITS`` is the one table. ``SystemConfig.validate`` reads
  it at call time, and the constraint rows are its projection; a credit
  removed from the table stops being refused.
* the runtime message is the row's description, so a refusal names the rule.
* ``references_params`` is the only traversal, and it answers True for a rule
  that reads ``output_dim``.

Each test fails if a second copy returns.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from computronium.experiment.legality.dsl import const, has_key, references_params, var
from computronium.experiment.schema.registries import CONSTRAINTS_REGISTRY
from computronium.experiment.schema.seed_registries import seed_all_registries
from computronium.ontology import system as system_module
from computronium.ontology.credit import CreditAssignmentConfig
from computronium.ontology.dynamics import StateDynamicsConfig
from computronium.ontology.geometry import GeometryConfig
from computronium.ontology.substrate import SubstrateConfig
from computronium.ontology.system import NCA_CELL_MODE_CREDITS, SystemConfig
from computronium.ontology.update import ParameterUpdateConfig
from computronium.state import PlasticityConfig

_ROOT = Path(__file__).resolve().parents[2]
_STAGES = _ROOT / "computronium/experiment/execution/stages_impl.py"


def _nca(credit: str, dynamics: str = "instantaneous") -> SystemConfig:
    return SystemConfig(
        substrate=SubstrateConfig.digital(),
        geometry=GeometryConfig.nca(
            channels=1, hidden=8, grid_hw=(4, 4), output_dim=10
        ),
        dynamics=StateDynamicsConfig.instantaneous()
        if dynamics == "instantaneous"
        else StateDynamicsConfig.energy_minimization(),
        plasticity=PlasticityConfig.null(),
        credit=getattr(CreditAssignmentConfig, credit)(),
        update=ParameterUpdateConfig.euclidean(),
    )


def test_the_registry_is_a_projection_of_the_declared_table() -> None:
    seed_all_registries()
    expected = {f"nca_instantaneous_{credit}" for credit in NCA_CELL_MODE_CREDITS}
    present = {
        spec.name
        for spec in CONSTRAINTS_REGISTRY
        if spec.name.startswith("nca_instantaneous_")
    }
    assert present == expected
    assert set(NCA_CELL_MODE_CREDITS) == {"homeostatic", "pc_alm"}


def test_the_runtime_refusal_names_the_declared_row() -> None:
    seed_all_registries()
    for credit in NCA_CELL_MODE_CREDITS:
        row = CONSTRAINTS_REGISTRY[f"nca_instantaneous_{credit}"]
        with pytest.raises(ValueError) as excinfo:
            _nca(credit).validate()
        assert row.description in str(excinfo.value)


def test_the_runtime_reads_the_shared_table(monkeypatch: pytest.MonkeyPatch) -> None:
    # pc_alm is only refused because the table names it. Remove it there and the
    # same configuration validates: the registry copy is not the authority.
    monkeypatch.setattr(system_module, "NCA_CELL_MODE_CREDITS", ("homeostatic",))
    _nca("pc_alm").validate()
    with pytest.raises(ValueError, match="homeostatic"):
        _nca("homeostatic").validate()


def test_a_legal_nca_control_still_composes() -> None:
    _nca("gradient").validate()


def test_references_params_is_the_only_traversal() -> None:
    tree = ast.parse(_STAGES.read_text())
    local = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_references_params"
    ]
    assert local == [], "a local _references_params copy is a second rule"

    imported = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == (
            "computronium.experiment.legality.dsl"
        ):
            imported += sum(alias.name == "references_params" for alias in node.names)
    assert imported >= 2, "S4 Gate and S5 Compose must both import the dsl helper"

    assert references_params(var("output_dim"))
    assert references_params(has_key(var("params"), const("residual")))
    assert not references_params(var("credit"))


# The axis-value tables the validators and the declarative rows share: one
# table per rule, projected into the planner's predicate. A literal set on
# either side is the second copy this test exists to catch.
_SHARED_TABLES = (
    ("RECURRENT_DYNAMICS", "recurrent_geometry_dynamics", 2, {"geometry": "recurrent"}),
    (
        "THERMO_CREDIT_DYNAMICS",
        "thermodynamic_contrast_dynamics",
        2,
        {"credit": "thermodynamic_contrast"},
    ),
    (
        "SPIKE_INTEGRATION_CREDITS",
        "spike_integration_credit",
        4,
        {"dynamics": "spike_integration"},
    ),
    (
        "PREDICTIVE_SETTLING_CREDITS",
        "predictive_settling_credit",
        4,
        {"dynamics": "predictive_settling"},
    ),
    (
        "QUANTUM_DYNAMICS",
        "quantum_substrate_dynamics",
        2,
        {"substrate": "quantum"},
    ),
)
_AXIS_FIELDS = ("substrate", "geometry", "dynamics", "plasticity", "credit", "update")


def _values(index: int, overrides: dict[str, str]) -> tuple[str, ...]:
    values = [
        "digital",
        "feedforward",
        "instantaneous",
        "null",
        "gradient",
        "euclidean",
    ]
    for field, value in overrides.items():
        values[_AXIS_FIELDS.index(field)] = value
    return (*values, "")


def _candidates(index: int) -> list[str]:
    from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis

    axis = StructuralAxis(_AXIS_FIELDS[index])
    return [spec.name for spec in AXES_REGISTRIES[axis].values()]


@pytest.mark.parametrize(
    ("table", "rule_name", "index", "overrides"),
    _SHARED_TABLES,
    ids=[case[0] for case in _SHARED_TABLES],
)
def test_the_declared_row_is_the_shared_table(
    table: str,
    rule_name: str,
    index: int,
    overrides: dict[str, str],
) -> None:
    """The row's verdict is membership in the table, for every axis value."""
    from computronium.experiment.kernel.search_space import (
        _compiled_void_constraints,
    )

    seed_all_registries()
    rule = dict(_compiled_void_constraints()[0])[rule_name]
    allowed = getattr(system_module, table)
    for value in _candidates(index):
        values = _values(index, {**overrides, _AXIS_FIELDS[index]: value})
        assert rule(values) is (value in allowed), (table, value)


def test_removing_a_value_from_the_table_stops_the_refusal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The runtime validator reads the table, not a literal of its own."""
    from computronium.ontology.dynamics import StateDynamicsConfig
    from computronium.ontology.geometry import GeometryConfig

    monkeypatch.setattr(
        system_module, "RECURRENT_DYNAMICS", frozenset({"instantaneous"})
    )

    def recurrent(dynamics: str) -> SystemConfig:
        return SystemConfig(
            substrate=SubstrateConfig.digital(),
            geometry=GeometryConfig.recurrent(
                input_dim=784, output_dim=10, hidden_dims=(16,)
            ),
            dynamics=getattr(StateDynamicsConfig, dynamics)(),
            plasticity=PlasticityConfig.null(),
            credit=CreditAssignmentConfig.homeostatic(),
            update=ParameterUpdateConfig.euclidean(),
        )

    recurrent("instantaneous").validate()
    with pytest.raises(ValueError, match=r"requires one of \['instantaneous'\]"):
        recurrent("diffusion").validate()
