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
