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

from computronium.experiment.execution import compose_cell_system
from computronium.experiment.schema import (
    AXES_REGISTRIES,
    PRIORS_REGISTRY,
    AxisKind,
    Coordinate,
    Domain,
    HyperparameterSpec,
    InactiveHyperparameterError,
    Scale,
    StructuralAxis,
    UnresolvedHyperparameterError,
    config_field_name,
    harvest_schema,
    load_axis_config,
    prior_value,
)
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

    illegal = []
    for spec in harvest_schema().hyperparameters:
        if spec.prior is None:
            continue
        resolved = prior_value(spec.prior)
        if resolved is None:
            continue
        center = resolved[0]
        lo, hi = spec.domain.lo, spec.domain.hi
        if spec.domain.members is not None:
            if center not in spec.domain.members:
                illegal.append((spec.name, center, spec.domain.members))
        elif lo is not None and hi is not None and not lo <= center <= hi:
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

    coordinate = Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        credit="gradient",
        update="adam",
        params={"update_lr": 0.03125, "hidden_dim": 48, "num_layers": 3},
    )
    cell = compose_cell_system(
        coordinate=coordinate,
        geometry={},
        input_shape=(64,),
        output_dim=10,
    )
    assert cell.params["geometry.hidden_dim"] == 48
    assert cell.params["update.update_lr"] == pytest.approx(0.03125)
    # Effective values are recorded, so a prior or an override that wins is visible.
    assert "dynamics.settle_step" in cell.params


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
    assert energy.values["settle_beta"] > 0, (
        "settle_beta must be active for the EM×TC pairing"
    )
    assert energy.values["credit_beta"] > 0, (
        "credit_beta must be active for the EM×TC pairing"
    )


def test_no_name_is_declared_by_two_axes() -> None:
    """Q3 (TODO48): names are per-axis; a second claim is a seam defect.

    ``step_size`` was declared by dynamics and update — each pair a different
    physical quantity — and the resolve-once preference rule existed to paper
    over it. The names are split (``settle_step``, ``update_lr``, ...); a
    re-introduced shared name fails here and in the schema seam lock.
    """
    schema = harvest_schema()
    seen: dict[str, str] = {}
    shared = []
    for spec in schema.hyperparameters:
        if spec.name in seen and seen[spec.name] != spec.axis_name:
            shared.append(f"{spec.name}: {seen[spec.name]} + {spec.axis_name}")
        seen[spec.name] = spec.axis_name
    assert not shared, f"names declared by two axes: {shared}"


def test_unswept_values_have_a_declared_source() -> None:
    """Q4 (TODO48): override → prior → config default, and nothing else.

    The declaration audit inside ``harvest_schema()`` already rejected any row
    with no prior and no config default — reaching this line is the first
    half of the proof. The second half: the per-axis rename keeps its field
    alias map total, so a schema name reaches the config field the factory
    reads.
    """
    renamed = [
        name
        for name in (
            "settle_step",
            "settle_beta",
            "settle_momentum",
            "update_lr",
            "credit_beta",
        )
        if config_field_name(name) == name
    ]
    assert not renamed, f"renamed schema names lost their field alias: {renamed}"


def test_a_continuous_value_with_no_source_raises() -> None:
    """The resolve path raises instead of returning a domain edge."""
    from computronium.experiment.schema import _config_default

    spec = HyperparameterSpec(
        name="probe_lr",
        domain=Domain(lo=1e-5, hi=1.0, scale=Scale.LOG),
        axis_kind=AxisKind.CONTINUOUS,
        axis_name="dynamics",
    )
    with pytest.raises(UnresolvedHyperparameterError, match="probe_lr"):
        _config_default(spec, _coordinate())


def test_axis_kinds_are_honoured_by_the_schema() -> None:
    """Every spec carries one of the four kinds the sampler maps uniformly."""
    kinds = {s.axis_kind for s in harvest_schema().hyperparameters}
    assert kinds <= {
        AxisKind.STRUCTURAL,
        AxisKind.CONTINUOUS,
        AxisKind.INTEGER,
        AxisKind.CATEGORICAL,
    }


def test_per_axis_values_resolve_independently() -> None:
    """``settle_step`` (dynamics, prior-backed) and ``update_lr`` (update,
    factory-default) are different quantities and resolve separately.

    Before the split, one ``step_size`` name was declared by both axes and a
    resolve-once preference rule decided who owned it; last-writer-wins once
    trained every unswept cell at 1e-5 (TODO47 §6.1). Each axis now carries
    its own name, its own source, its own value.
    """
    schema = harvest_schema()
    coordinate = Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="energy_minimization",
        credit="gradient",
        update="euclidean",
        plasticity="null",
        params={},
    )
    space = schema.active(coordinate)
    settle_spec = next(s for s in space.specs if s.name == "settle_step")
    center, _, _ = prior_value(settle_spec.prior)  # type: ignore[arg-type]
    assert space.values["settle_step"] == center
    # The update axis resolves from its own factory default, not the dynamics prior.
    update_spec = next(s for s in space.specs if s.name == "update_lr")
    assert update_spec.prior is None
    assert space.values["update_lr"] == pytest.approx(
        inspect
        .signature(ParameterUpdateConfig.euclidean)
        .parameters["step_size"]
        .default
    )
    # And the values reach each axis under the field name the factory reads.
    assert space.by_axis(StructuralAxis.DYNAMICS)["step_size"] == center
    assert space.for_axis(StructuralAxis.UPDATE, "euclidean")[
        "step_size"
    ] == pytest.approx(0.01)
