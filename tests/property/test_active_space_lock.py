"""Lock: one mechanism decides what a coordinate's primitives can accept.

TODO46 §3.0.1. Availability is a predicate declared in ``AXES``, so composition
never reflects on a factory to learn which knobs exist and never branches on a
pair of axis names. These are the acceptance conditions, stated as tests:

* every declared prior resolves — a dangling prior is a silent magic number
* every primitive's factory accepts exactly the hyperparameters its availability
  predicates admit, so composition never has to drop a value
* no numeric literal naming a known task shape reaches ``experiment/execution``
* a coordinate carrying a dead parameter is rejected

A lock that asserts only that a name is importable is the failure mode this
plan exists to stop, so each assertion below exercises the mechanism.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from computronium.experiment.schema.axis import (
    AXES_REGISTRIES,
    AxisKind,
    Domain,
    HyperparameterSpec,
    Scale,
    StructuralAxis,
)
from computronium.experiment.schema.coordinate import Coordinate
from computronium.experiment.schema.harvest import (
    ConflictingHyperparameterError,
    InactiveHyperparameterError,
    declare,
    harvest_schema,
    load_axis_config,
)
from computronium.experiment.schema.registries import PRIORS_REGISTRY
from computronium.ontology.credit import CreditAssignmentConfig
from computronium.ontology.dynamics import StateDynamicsConfig
from computronium.ontology.geometry import GeometryConfig
from computronium.ontology.substrate import SubstrateConfig
from computronium.ontology.update import ParameterUpdateConfig
from computronium.state.transitions import PlasticityConfig

_EXECUTION = Path(__file__).resolve().parents[2] / "computronium/experiment/execution"

# The task shapes D2 hardcoded. None may appear as a literal in search or
# evaluation code: dimension comes from the task descriptor.
_TASK_SHAPES = frozenset({784, 768})

_AXIS_CONFIG_CLASSES = {
    StructuralAxis.SUBSTRATE: SubstrateConfig,
    StructuralAxis.GEOMETRY: GeometryConfig,
    StructuralAxis.DYNAMICS: StateDynamicsConfig,
    StructuralAxis.PLASTICITY: PlasticityConfig,
    StructuralAxis.CREDIT: CreditAssignmentConfig,
    StructuralAxis.UPDATE: ParameterUpdateConfig,
}


def _coordinate(**overrides: str) -> Coordinate:
    selection = {
        "substrate": "digital",
        "geometry": "feedforward",
        "dynamics": "instantaneous",
        "plasticity": "null",
        "credit": "gradient",
        "update": "euclidean",
        **overrides,
    }
    return Coordinate(**selection, params={})


def test_every_declared_prior_resolves() -> None:
    """A prior named by a spec must exist; otherwise the value is a domain edge."""
    dangling = [
        f"{spec.axis_name}.{spec.name}"
        for spec in harvest_schema().hyperparameters
        if spec.prior is not None and spec.prior not in PRIORS_REGISTRY
    ]
    assert not dangling, f"Hyperparameters naming unregistered priors: {dangling}"


def test_prior_center_falls_inside_the_declared_domain() -> None:
    """The fallback a prior supplies must be a legal value for the spec."""
    from computronium.experiment.schema.registries import prior_value

    illegal = []
    for spec in harvest_schema().hyperparameters:
        if spec.prior is None:
            continue
        resolved = prior_value(spec.prior)
        if resolved is None:
            continue
        center = resolved[0]
        if spec.domain.members is not None:
            if center not in spec.domain.members:
                illegal.append((spec.name, center, spec.domain.members))
        elif not spec.domain.lo <= center <= spec.domain.hi:
            illegal.append((spec.name, center, spec.domain))
    assert not illegal, f"Priors whose center is outside the domain: {illegal}"


def test_composition_never_reflects_on_a_config_factory() -> None:
    """D5: availability is declared, not discovered by inspecting a factory.

    Every config factory mirrors the whole dataclass field set, so a signature
    says nothing about which knobs a primitive reads — which is why the D5
    reflection was a lie dressed as generality.
    """
    source = (
        Path(__file__).resolve().parents[2]
        / "computronium/experiment/execution/compose.py"
    ).read_text()
    assert "inspect.signature" not in source, (
        "compose must read AxisSpec.accepted_params, not inspect a factory"
    )


@pytest.mark.parametrize("axis", list(StructuralAxis))
def test_no_primitive_is_handed_a_keyword_it_rejects(axis: StructuralAxis) -> None:
    """No primitive may be handed a keyword its factory does not accept.

    This is the D5 failure made executable: a value admitted by availability but
    rejected by the factory is a value composition would drop. Only the extra-
    keyword direction is an invariant — several primitives (``role_split``,
    ``graph``, ``causal_transformer``) require structural arguments the
    composer supplies separately, and geometry is built by its own normalizer.
    """
    config_cls = _AXIS_CONFIG_CLASSES[axis]
    problems: list[str] = []
    for name, axis_spec in sorted(AXES_REGISTRIES[axis].items()):
        factory = getattr(config_cls, name, None)
        if not callable(factory):
            continue
        accepted = set(inspect.signature(factory).parameters)
        assert axis_spec.accepted_params == accepted, (
            f"{axis.value}/{name}: accepted_params drifted from the factory"
        )
        kwargs = (
            harvest_schema()
            .active(_coordinate(**{axis.value: name}))
            .for_axis(axis, name)
        )
        extra = sorted(set(kwargs) - accepted)
        if extra:
            problems.append(f"{axis.value}/{name}: would reject {extra}")
    assert not problems, "\n".join(problems)


def test_spec_axis_always_has_a_config_class() -> None:
    """The axis→config correspondence is one table, and it must stay total."""
    for axis in StructuralAxis:
        assert load_axis_config(axis) is not None, axis
        assert _AXIS_CONFIG_CLASSES[axis] is load_axis_config(axis), axis


def test_mnist_shape_literals_do_not_return() -> None:
    """D2: no task shape may appear as a literal in search or evaluation code.

    Shape comes from the task descriptor. The seven ``input_dim: 784`` sites
    that held this at a ratchet of seven are gone with the enumerator
    (§3.3); the ratchet is now zero.
    """
    offenders = [
        f"{path.name}:{node.lineno}"
        for path in sorted(_EXECUTION.glob("*.py"))
        for node in ast.walk(ast.parse(path.read_text(), filename=str(path)))
        if isinstance(node, ast.Constant)
        and isinstance(node.value, int)
        and not isinstance(node.value, bool)
        and node.value in _TASK_SHAPES
    ]
    assert not offenders, f"MNIST-shaped literals returned: {offenders}"


def test_inactive_parameter_is_rejected() -> None:
    """Dead configuration is a defect, so a coordinate carrying one fails."""
    schema = harvest_schema()
    coordinate = _coordinate()
    inactive = next(iter(schema.active(coordinate).inactive))
    poisoned = Coordinate(
        substrate=coordinate.substrate,
        geometry=coordinate.geometry,
        dynamics=coordinate.dynamics,
        plasticity=coordinate.plasticity,
        credit=coordinate.credit,
        update=coordinate.update,
        params={inactive: 1.0},
    )
    with pytest.raises(InactiveHyperparameterError, match=inactive):
        schema.active(poisoned)


def test_active_values_reach_the_composed_configs() -> None:
    """The falsification half: a searched value must actually be applied."""
    from computronium.experiment.execution.compose import compose_cell_system

    coordinate = Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        credit="gradient",
        update="adam",
        params={"step_size": 0.03125, "hidden_dim": 48, "num_layers": 3},
    )
    cell = compose_cell_system(
        coordinate=coordinate,
        geometry={},
        input_dim=64,
        output_dim=10,
    )
    assert cell.params["geometry.hidden_dim"] == 48
    assert cell.params["dynamics.step_size"] == pytest.approx(0.03125)
    # Effective values are recorded, so a prior or an override that wins is visible.
    assert "update.step_size" in cell.params


def test_coupling_needs_no_axis_name_branch() -> None:
    """The D5 couplings are availability, so a spec row alone carries them."""
    source = (
        Path(__file__).resolve().parents[2]
        / "computronium/experiment/execution/compose.py"
    ).read_text()
    for comparison in ("dynamics_type ==", "credit_type ==", "update_type =="):
        assert comparison not in source, (
            f"composition branches on {comparison}; add an availability predicate"
        )
    energy = harvest_schema().active(
        _coordinate(dynamics="energy_minimization", credit="thermodynamic_contrast")
    )
    assert energy.values["beta"] > 0, "beta must be active for the EM×TC pairing"


def test_conflicting_domains_are_a_registry_failure() -> None:
    """Two axes declaring one name with different domains must raise, not merge."""
    schema = harvest_schema()
    conflict = next(
        (
            spec
            for spec in schema.hyperparameters
            if len(
                {
                    s.domain
                    for s in schema.hyperparameters
                    if s.name == spec.name
                }
            )
            > 1
        ),
        None,
    )
    assert conflict is None, f"merged conflicting domains for {conflict}"

    merged = HyperparameterSpec(
        name="probe",
        domain=Domain(lo=1.0, hi=2.0, scale=Scale.LOG),
        axis_kind=AxisKind.CONTINUOUS,
        axis_name="dynamics",
    )
    other = HyperparameterSpec(
        name="probe",
        domain=Domain(lo=1.0, hi=100.0, scale=Scale.LINEAR),
        axis_kind=AxisKind.CONTINUOUS,
        axis_name="update",
    )
    with pytest.raises(ConflictingHyperparameterError, match="probe"):
        declare({"probe": merged}, other)


def test_axis_kinds_are_honoured_by_the_schema() -> None:
    """Every spec carries one of the four kinds the sampler maps uniformly."""
    kinds = {s.axis_kind for s in harvest_schema().hyperparameters}
    assert kinds <= {
        AxisKind.STRUCTURAL,
        AxisKind.CONTINUOUS,
        AxisKind.INTEGER,
        AxisKind.CATEGORICAL,
    }
