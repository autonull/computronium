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
    set_state_field,
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


CREDIT = PACKAGE.parent / "credit.py"
PACKAGE_ROOT = PACKAGE.parents[1]


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
        system, composite = _surfaces()
        acts = [torch.zeros(4, 8)]
        set_state_field(system, "free_state", acts)
        set_state_field(composite, "free_state", acts)
        assert system.free_state is acts
        assert composite.activity["free_state"] is acts

    def test_optional_field_readers_return_none_on_the_z_t_view(self):
        """``state_energy`` / ``state_dual_vars`` are the documented way to
        read the SystemState-only fields from a layer that accepts both
        algebras (the credit layer)."""
        from computronium.ontology.dynamics._state import state_dual_vars, state_energy

        system, composite = _surfaces()
        system.energy = torch.zeros(())
        set_state_field(system, "dual_vars", [torch.zeros(2)])
        energy = state_energy(system)
        assert energy is not None and float(energy) == 0.0
        assert state_dual_vars(system) is not None
        assert state_energy(composite) is None
        assert state_dual_vars(composite) is None

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


def _type_checking_names(tree: ast.Module) -> set[str]:
    """Names bound only inside an ``if TYPE_CHECKING:`` block."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if not (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING"):
            continue
        for stmt in node.body:
            if isinstance(stmt, ast.ImportFrom):
                names |= {alias.asname or alias.name for alias in stmt.names}
            elif isinstance(stmt, ast.Import):
                names |= {
                    (alias.asname or alias.name).split(".")[0] for alias in stmt.names
                }
    return names


def _runtime_bindings(tree: ast.Module) -> set[str]:
    """Names bound by an import that is *not* under TYPE_CHECKING.

    Function-local runtime imports count: a module may legitimately declare
    a name under TYPE_CHECKING for its annotations and re-import it inside
    the one function that calls it.
    """
    guarded = {
        id(n)
        for n in ast.walk(tree)
        if isinstance(n, ast.If)
        and isinstance(n.test, ast.Name)
        and n.test.id == "TYPE_CHECKING"
        for stmt in n.body
        for n in ast.walk(stmt)
    }
    bound: set[str] = set()
    for node in ast.walk(tree):
        if id(node) in guarded:
            continue
        if isinstance(node, ast.ImportFrom):
            bound |= {alias.asname or alias.name for alias in node.names}
        elif isinstance(node, ast.Import):
            bound |= {
                (alias.asname or alias.name).split(".")[0] for alias in node.names
            }
    return bound


def _runtime_callees(tree: ast.Module) -> set[str]:
    """Names *called* (or used in an isinstance/issubclass test) at runtime.

    Restricted to direct call targets and type-test arguments, and it must
    be: attribute bases are excluded because ``pd.DataFrame(...)`` with
    ``import pandas as pd`` under TYPE_CHECKING is a *typing-only* import
    used inside a string annotation's helper — flagging it would be a false
    positive, and a lock with false positives gets switched off (§2.5).
    """
    guarded = {
        id(n)
        for n in ast.walk(tree)
        if isinstance(n, ast.If)
        and isinstance(n.test, ast.Name)
        and n.test.id == "TYPE_CHECKING"
        for stmt in n.body
        for n in ast.walk(stmt)
    }
    called: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or id(node) in guarded:
            continue
        if isinstance(node.func, ast.Name):
            called.add(node.func.id)
        if isinstance(node.func, ast.Name) and node.func.id in {
            "isinstance",
            "issubclass",
        }:
            called |= {
                n.id
                for arg in node.args
                for n in ast.walk(arg)
                if isinstance(n, ast.Name)
            }
    return called


class TestSourceLock:
    def test_credit_annotations_name_the_surface(self):
        """§5.8: the credit layer named ``SystemState`` on 17 signatures while
        every reference kernel passes ``CompositeState`` and silenced the
        mismatch with ``# type: ignore[arg-type]``. The retyping is only worth
        anything if the next one has to be the surface too."""
        offenders = _annotations_in_source(CREDIT.read_text(encoding="utf-8")) & set(
            ALGEBRA_NAMES
        )
        assert not offenders, (
            f"credit signatures must name SettableState, not a state algebra: {offenders}"
        )

    def test_type_checking_imports_are_not_called_at_runtime(self):
        """A name imported under ``TYPE_CHECKING`` and then *called* is a
        NameError waiting for a path that reaches it.

        Found twice in one pass while landing §5.8: the optional-state-field
        readers were TYPE_CHECKING imports in ``credit.py``, and every
        PC-ALM run raised ``NameError: name 'state_dual_vars' is not
        defined``. ``ruff``'s F821 cannot see it — the binding exists as far
        as the linter is concerned — which is why this is a test.
        """
        offenders: dict[str, set[str]] = {}
        for path in sorted(PACKAGE_ROOT.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            bad = (
                _type_checking_names(tree) - _runtime_bindings(tree)
            ) & _runtime_callees(tree)
            if bad:
                offenders[str(path.relative_to(PACKAGE_ROOT))] = bad
        assert not offenders, (
            f"TYPE_CHECKING-only imports called at runtime: {offenders}"
        )

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
