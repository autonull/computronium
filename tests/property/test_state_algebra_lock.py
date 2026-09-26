"""The settle contract names a surface, not a state algebra (TODO34 §5.3).

``StateDynamics.settle`` used to be annotated ``state: CompositeState`` while
``core/pipeline.py`` passed a ``SystemState`` and every implementation cast its
own return value back to the declared type. Eleven classes carried an
annotation pyright rejects, and the truth — that two state algebras share one
settle surface — was only in a comment.

Three claims are locked here, in the shape §0.6/§2.2 taught:

* the *surface* is what both algebras expose (``SettableState``), asserted
  against the two real classes rather than a hand-written field list;
* the *source* carries no algebra-named annotation on a settle signature
  (AST, so a docstring mention cannot satisfy or trip it);
* the *behaviour* — settle accepts each algebra and returns the same algebra —
  which is the half a source lock cannot see (TODO34 Notes: "a source lock
  cannot see an omission").
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
import torch

from computronium.ontology.dynamics import (
    DYNAMICS_REGISTRY,
    SettableState,
    StateDynamicsConfig,
    dynamics_from_config,
    is_composite_state,
    is_system_state,
)
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
from computronium.ontology.system import SystemState
from computronium.state import CompositeState

PACKAGE = Path(__file__).resolve().parents[2] / "computronium" / "ontology" / "dynamics"
ALGEBRA_NAMES = ("CompositeState", "SystemState")

CONFIGS = {
    "energy_minimization": lambda: StateDynamicsConfig.energy_minimization(
        max_steps=3, step_size=0.1
    ),
    "predictive_settling": lambda: StateDynamicsConfig.predictive_settling(
        max_steps=3, step_size=0.1
    ),
    "error_predictive_coding": lambda: StateDynamicsConfig.error_predictive_coding(
        max_steps=3, step_size=0.1
    ),
    "spike_integration": lambda: StateDynamicsConfig.spike_integration(
        max_steps=3, step_size=0.1
    ),
    "instantaneous": StateDynamicsConfig.instantaneous,
    "diffusion": lambda: StateDynamicsConfig.diffusion(max_steps=3, step_size=0.1),
    "lazy": lambda: StateDynamicsConfig.lazy(max_steps=3),
    "pc_alm": lambda: StateDynamicsConfig.pc_alm(max_steps=3, step_size=0.1),
}


def _algebra(name: str, x: torch.Tensor) -> SystemState | CompositeState:
    if name == "system":
        return SystemState(x=x)
    return CompositeState(activity={"x": x}, plastic={}, substrate={})


def _surfaces() -> tuple[SystemState, CompositeState]:
    x = torch.randn(4, 8)
    return SystemState(x=x), CompositeState(activity={"x": x}, plastic={}, substrate={})


class TestSurfaceContract:
    def test_both_algebras_satisfy_the_surface(self):
        system, composite = _surfaces()
        assert isinstance(system, SettableState)
        assert isinstance(composite, SettableState)

    def test_surface_members_exist_on_both_algebras(self):
        system, composite = _surfaces()
        fields = {n for n in vars(SettableState) if not n.startswith("_")}
        assert fields, "the surface must declare members"
        for field in fields:
            assert hasattr(system, field), f"SystemState lacks {field}"
            assert hasattr(composite, field), f"CompositeState lacks {field}"

    def test_narrowing_is_mutually_exclusive(self):
        system, composite = _surfaces()
        assert is_system_state(system) and not is_composite_state(system)
        assert is_composite_state(composite) and not is_system_state(composite)

    def test_writes_reach_the_owning_algebra(self):
        """``set_state_field`` is the write side of a read-only surface."""
        from computronium.ontology.dynamics._state import set_state_field

        system, composite = _surfaces()
        acts = [torch.zeros(4, 8)]
        set_state_field(system, "free_state", acts)
        set_state_field(composite, "free_state", acts)
        assert system.free_state is acts
        assert composite.activity["free_state"] is acts

    def test_fields_outside_the_surface_are_system_only(self):
        """The optional settler's fields are absent on the z_t view — that is
        why they are reached through getattr, not through the Protocol."""
        system, composite = _surfaces()
        for field in ("dual_vars", "spike_counts", "spike_rasters", "energy"):
            assert hasattr(system, field)
            assert not hasattr(composite, field)


class TestBothAlgebrasSettle:
    @pytest.mark.parametrize("dynamics_type", sorted(CONFIGS))
    @pytest.mark.parametrize("algebra", ("system", "composite"))
    def test_settle_returns_the_algebra_it_was_given(self, dynamics_type, algebra):
        torch.manual_seed(0)
        geometry = FeedforwardGeometry(
            GeometryConfig.feedforward(input_dim=8, hidden_dims=(8,), output_dim=4)
        )
        substrate = DigitalSubstrate(SubstrateConfig.digital())
        dynamics = dynamics_from_config(CONFIGS[dynamics_type]())
        assert type(dynamics) is DYNAMICS_REGISTRY[dynamics_type]

        state = _algebra(algebra, torch.randn(4, 8))
        settled = dynamics.settle(state, geometry, substrate)

        if algebra == "system":
            assert is_system_state(settled)
        else:
            assert is_composite_state(settled)
        assert settled.activations is not None


def _annotated_parameters(path: Path) -> set[str]:
    """Annotation names on parameters/returns of settle-shaped signatures."""
    return _annotations_in_source(path.read_text(encoding="utf-8"))


def _annotations_in_source(source: str) -> set[str]:
    tree = ast.parse(source)
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        args = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
        annotations = [a.annotation for a in args if a.annotation is not None]
        if node.returns is not None:
            annotations.append(node.returns)
        for annotation in annotations:
            for inner in ast.walk(annotation):
                if isinstance(inner, ast.Name):
                    found.add(inner.id)
    return found


class TestSourceLock:
    def test_no_algebra_named_annotation_in_the_dynamics_package(self):
        # _state.py is the module that *defines* the surface; its narrowing
        # helpers name both algebras by construction.
        offenders = {
            path.name: names
            for path in sorted(PACKAGE.glob("*.py"))
            if path.name != "_state.py"
            and (names := _annotated_parameters(path) & set(ALGEBRA_NAMES))
        }
        assert not offenders, (
            "settle must be annotated with SettableState, not a state algebra: "
            f"{offenders}"
        )

    def test_scan_sees_planted_annotations(self):
        """Probe-the-probe: the scan resolves real names, so it cannot pass by
        resolving nothing (the §0.6 lesson)."""
        planted = "def settle(state: CompositeState) -> SystemState: ..."
        assert _annotations_in_source(planted) == set(ALGEBRA_NAMES)
        assert not _annotations_in_source("def f(state: SettableState): ...") & set(
            ALGEBRA_NAMES
        )
