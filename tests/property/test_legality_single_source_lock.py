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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

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
# table per rule, projected into the planner's predicate. A literal set on the
# trigger side or the axis side is the second copy this test exists to catch.
#
# Each case is one clause of a VOID row: ``trigger axis in trigger values
# implies dependent axis (in | not in) table``. ``trigger`` and ``table`` are
# read from ``computronium.ontology.system`` at call time, so the test fails
# when the row and the table disagree in either direction.
@dataclass(frozen=True)
class _RuleCase:
    rule: str
    trigger_axis: str
    trigger_values: str
    dependent_axis: str
    table: str
    polarity: Literal["in", "not_in"]
    base: dict[str, str] = field(default_factory=dict)

    @property
    def id(self) -> str:
        return f"{self.rule}:{self.table}"


_RULE_CASES = (
    _RuleCase(
        "recurrent_geometry_dynamics",
        "geometry",
        "RECURRENT_TRIGGER",
        "dynamics",
        "RECURRENT_DYNAMICS",
        "in",
    ),
    _RuleCase(
        "thermodynamic_contrast_dynamics",
        "credit",
        "THERMO_CREDITS",
        "dynamics",
        "THERMO_CREDIT_DYNAMICS",
        "in",
    ),
    _RuleCase(
        "spike_integration_credit",
        "dynamics",
        "SPIKE_TRIGGER",
        "credit",
        "SPIKE_INTEGRATION_CREDITS",
        "in",
    ),
    _RuleCase(
        "predictive_settling_credit",
        "dynamics",
        "PREDICTIVE_TRIGGER",
        "credit",
        "PREDICTIVE_SETTLING_CREDITS",
        "in",
    ),
    _RuleCase(
        "quantum_substrate_dynamics",
        "substrate",
        "QUANTUM_TRIGGER",
        "dynamics",
        "QUANTUM_DYNAMICS",
        "in",
    ),
    _RuleCase(
        "local_contrastive_geometry",
        "credit",
        "LOCAL_STACK_CREDITS",
        "geometry",
        "LOCAL_STACK_GEOMETRIES",
        "in",
    ),
    _RuleCase(
        "attention_geometry_compatibility",
        "geometry",
        "ATTENTION_TRIGGER",
        "credit",
        "ATTENTION_INCOMPATIBLE_CREDITS",
        "not_in",
    ),
    _RuleCase(
        "transformer_pairing_credit",
        "geometry",
        "TRANSFORMER_TRIGGER",
        "credit",
        "TRANSFORMER_UNPAIRED_CREDITS",
        "not_in",
    ),
    _RuleCase(
        "pc_alm_dynamics",
        "dynamics",
        "PC_ALM_TRIGGER",
        "credit",
        "PC_ALM_CREDITS",
        "in",
        {"credit": "pc_alm"},
    ),
    _RuleCase(
        "pc_alm_dynamics",
        "dynamics",
        "PC_ALM_TRIGGER",
        "geometry",
        "PC_ALM_GEOMETRIES",
        "in",
        {"credit": "pc_alm"},
    ),
    _RuleCase(
        "pc_alm_credit_dynamics",
        "credit",
        "PC_ALM_DUAL_CREDITS",
        "dynamics",
        "PC_ALM_CREDIT_DYNAMICS",
        "in",
    ),
    _RuleCase(
        "fast_weight_plasticity_geometry",
        "geometry",
        "NO_FAST_WEIGHT_GEOMETRIES",
        "plasticity",
        "FAST_WEIGHT_TRIGGER",
        "not_in",
    ),
)

# Trigger sets that are a literal of the row (one value or the dependent axis'
# forbidden row) rather than a shared table.
_LITERAL_TRIGGERS = {
    "RECURRENT_TRIGGER": frozenset({"recurrent"}),
    "SPIKE_TRIGGER": frozenset({"spike_integration"}),
    "PREDICTIVE_TRIGGER": frozenset({"predictive_settling", "error_predictive_coding"}),
    "QUANTUM_TRIGGER": frozenset({"quantum"}),
    "ATTENTION_TRIGGER": frozenset({"attention"}),
    "TRANSFORMER_TRIGGER": frozenset({"causal_transformer"}),
    "PC_ALM_TRIGGER": frozenset({"pc_alm"}),
    "FAST_WEIGHT_TRIGGER": frozenset({"fast_weights"}),
}
_AXIS_FIELDS = ("substrate", "geometry", "dynamics", "plasticity", "credit", "update")


def _values(overrides: dict[str, str]) -> tuple[str, ...]:
    values = [
        "digital",
        "feedforward",
        "instantaneous",
        "null",
        "gradient",
        "euclidean",
    ]
    for axis_name, value in overrides.items():
        values[_AXIS_FIELDS.index(axis_name)] = value
    return (*values, "")


def _candidates(axis: str) -> list[str]:
    from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis

    return [spec.name for spec in AXES_REGISTRIES[StructuralAxis(axis)].values()]


def _table(name: str) -> frozenset[str]:
    literal = _LITERAL_TRIGGERS.get(name)
    return literal if literal is not None else getattr(system_module, name)


@pytest.mark.parametrize("case", _RULE_CASES, ids=[case.id for case in _RULE_CASES])
def test_the_declared_row_is_the_shared_table(case: _RuleCase) -> None:
    """The row's verdict is the table's membership, for every axis value."""
    from computronium.experiment.kernel.search_space import (
        _compiled_void_constraints,
    )

    seed_all_registries()
    rule = dict(_compiled_void_constraints()[0])[case.rule]
    trigger = _table(case.trigger_values)
    table = _table(case.table)
    assert trigger, case
    trigger_values = (*sorted(trigger), _off_trigger(case))
    for value in trigger_values:
        for candidate in _candidates(case.dependent_axis):
            values = _values(
                case.base | {case.trigger_axis: value, case.dependent_axis: candidate}
            )
            member = candidate in table
            expected = member if case.polarity == "in" else not member
            if values[_AXIS_FIELDS.index(case.trigger_axis)] not in trigger:
                expected = True
            assert rule(values) is expected, (case.id, value, candidate)


def _off_trigger(case: _RuleCase) -> str:
    """A trigger-axis candidate that does not trigger the rule."""
    trigger = _table(case.trigger_values)
    return next(
        value for value in _candidates(case.trigger_axis) if value not in trigger
    )


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
