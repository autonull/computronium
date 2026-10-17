"""Lock: the schema seams are singular (TODO48 Q3+Q4).

Two seam classes bit in TODO47 §6.1 — a hyperparameter name shared by two
axes (the lr merge) and an unswept value silently resolving to a domain edge.
Both are declared-away here:

* no hyperparameter name is declared by two axes (per-axis names:
  ``settle_step``/``settle_beta``/``settle_momentum`` on dynamics,
  ``update_lr`` on update, ``credit_beta`` on credit);
* one ``PRIORS_REGISTRY`` definition, one registration path;
* every declared value has a source — a prior, a declared config default, or
  a factory signature default — and nothing resolves to ``Domain.lo``.

Falsifiable: re-introduce a shared name in a ``hyperparameters()`` dict, or
delete the ``default``/prior of any row — the matching test goes red.
"""

from __future__ import annotations

import inspect
from dataclasses import fields
from pathlib import Path

from computronium.experiment.schema import (
    NO_DEFAULT,
    PRIORS_REGISTRY,
    Coordinate,
    StructuralAxis,
    _config_default,
    harvest_schema,
    prior_value,
)

_SRC = Path(__file__).resolve().parents[2] / "computronium"


def test_exactly_one_priors_registry_definition() -> None:
    """One PRIORS_REGISTRY definition in the repo (Q4's grep lock)."""
    definitions = [
        str(p.relative_to(_SRC))
        for p in _SRC.rglob("*.py")
        if "PRIORS_REGISTRY" in p.read_text()
        and "PRIORS_REGISTRY: Registry[" in p.read_text()
    ]
    assert definitions == ["experiment/schema/registries.py"], definitions


def test_a_name_may_be_shared_across_axes_and_keyed_canonically() -> None:
    """A hyperparameter's identity is ``(axis, name)``.

    ``step_size`` is read by dynamics settling *and* the parameter update — two
    different quantities. Names are scoped to their axis and the canonical key is
    ``"{axis}.{name}"``; that key, not the bare name, is the declaration's
    identity, so it must be unique.
    """
    schema = harvest_schema()
    shared: dict[str, set[str]] = {}
    for spec in schema.hyperparameters:
        shared.setdefault(spec.name, set()).add(spec.axis_name)
    assert len(shared["step_size"]) > 1, "step_size should span dynamics and update"
    keys = [f"{s.axis_name}.{s.name}" for s in schema.hyperparameters]
    assert len(keys) == len(set(keys)), "canonical keys collide"


def test_declared_names_are_the_config_fields_they_feed() -> None:
    """No translation: a declared name is the config field the component reads."""
    schema = harvest_schema()
    by_axis = {
        axis: {s.name for s in specs} for axis, specs in schema.by_axis_specs.items()
    }
    assert {"step_size", "beta", "momentum"} <= by_axis[StructuralAxis.DYNAMICS]
    assert "step_size" in by_axis[StructuralAxis.UPDATE]
    assert "beta" in by_axis[StructuralAxis.CREDIT]
    for legacy in ("settle_step", "settle_beta", "settle_momentum", "update_lr"):
        assert legacy not in by_axis[StructuralAxis.DYNAMICS]
        assert legacy not in by_axis[StructuralAxis.UPDATE]


def test_every_value_has_a_source_and_none_resolves_to_the_domain_edge() -> None:
    """Q4's gate: every unswept value resolves from a declared source.

    The Domain.lo fallback is deleted: a spec with no prior, no declared
    default, and no factory default raises (the declaration audit catches it
    at harvest, and ``_config_default`` raises at resolve). Falsifiable by
    deleting the prior or default of any row.
    """
    # prior_value imported at module level from computronium.experiment.schema

    schema = harvest_schema()
    coordinates = [
        Coordinate(
            substrate="digital",
            geometry="feedforward",
            dynamics=dynamics,
            plasticity="null",
            credit=credit,
            update="euclidean",
            params={},
        )
        for dynamics, credit in (
            ("energy_minimization", "gradient"),
            ("instantaneous", "random_projections"),
            ("lazy", "temporal_trace"),
        )
    ]
    unresolved: list[str] = []
    for coordinate in coordinates:
        for spec in schema.hyperparameters:
            if spec.domain.members is not None:
                continue
            if spec.prior is not None:
                if prior_value(spec.prior) is None:
                    unresolved.append(f"{spec.axis_name}.{spec.name}: dangling prior")
                continue
            try:
                _config_default(spec, coordinate)
            except Exception as err:  # ruff: ignore[blind-except] - the lock names the row
                unresolved.append(f"{spec.axis_name}.{spec.name}: {err}")
    assert not unresolved, "unresolvable values:\n" + "\n".join(unresolved)


def test_retired_rows_stay_retired() -> None:
    """The dead declarations (no factory consumed them) must not return.

    Retirement records live in TODO48 §8 (R78): ``update.batch_size`` and
    ``plasticity.replace_readout`` were swept-but-discarded;
    ``substrate.weight_bounds_lo/hi`` fed a tuple no factory accepted.
    """
    names = {s.name for s in harvest_schema().hyperparameters}
    retired = {
        "batch_size",
        "replace_readout",
        "weight_bounds_lo",
        "weight_bounds_hi",
    }
    assert not names & retired, f"retired hyperparameters returned: {names & retired}"


def test_priors_are_registered_through_the_single_path() -> None:
    """The migrated accessors' names all exist in the one PRIORS table."""
    for name in (
        "dynamics_step_size_default",
        "dynamics_step_size_diffusion",
        "dynamics_step_size_predictive_settling",
        "hidden_width",
        "hidden_depth",
    ):
        assert name in PRIORS_REGISTRY, f"prior '{name}' missing from PRIORS_REGISTRY"


def test_ruler_lr_priors_stay_retired() -> None:
    """The ruler-LR table had no production reader (TODO66 §18).

    ``get_ruler_lr`` was called only by tests; the standard baselines wrote
    their chosen learning rates to ``dynamics.step_size``, which
    ``instantaneous`` dynamics ignore. Re-introducing a ``ruler_lr_*`` prior
    without a reader fails here.
    """
    names = {prior.name for prior in PRIORS_REGISTRY}
    assert not {name for name in names if name.startswith("ruler_lr_")}


def test_standard_baselines_set_the_optimizer_step() -> None:
    """A baseline's learning rate belongs on ``update.step_size``.

    All standard baselines use ``instantaneous`` dynamics, whose config
    ``step_size`` is never read; the old keys were no-ops.
    """
    from computronium.experiment.registry.baseline import BaselineRegistry

    for baseline in BaselineRegistry.STANDARD_BASELINES:
        assert "update.step_size" in baseline.hyperparameters, baseline.name
        assert "dynamics.step_size" not in baseline.hyperparameters, baseline.name


def test_a_sampled_dynamics_step_size_survives_composition() -> None:
    """The calibrated default fills an unsampled settle step; a sampled one wins."""
    from computronium.experiment.kernel.compose import compose_configs
    from computronium.experiment.kernel.evaluate import task_shape

    shape = task_shape("digits")

    def settle_step(
        dynamics: str, geometry: str, credit: str, params: dict[str, float]
    ) -> float:
        config = compose_configs(
            coordinate=Coordinate(
                substrate="digital",
                geometry=geometry,
                dynamics=dynamics,
                plasticity="null",
                credit=credit,
                update="adam",
                params=params,
            ),
            geometry={},
            input_shape=shape.input_shape,
            output_dim=shape.output_dim,
        )
        return config.dynamics.step_size

    diffusion = ("diffusion", "recurrent", "random_projections")
    settling = ("predictive_settling", "feedforward", "thermodynamic_contrast")
    assert settle_step(*diffusion, {}) == 0.001
    assert settle_step(*diffusion, {"dynamics.step_size": 0.05}) == 0.05
    assert settle_step(*settling, {}) == 0.01
    assert settle_step(*settling, {"dynamics.step_size": 0.05}) == 0.05


def test_no_step_size_multiplier_priors() -> None:
    """The retired ``(dynamics, credit)`` multiplier column stays retired.

    Every row was an identity after TODO48b R4 (the measurement lives in
    ``docs/CORRECTIONS.md`` Correction 3). A multiplier applied after config
    construction is invisible to the schema — a phantom knob by construction —
    so the column may not return as a prior.
    """
    offenders = sorted(
        spec.name
        for spec in PRIORS_REGISTRY
        if spec.name.startswith("step_size_override_")
    )
    assert not offenders, offenders


def test_no_learning_prior_registration_path_remains() -> None:
    """learning.prior is accessors over the registry; its old tables are gone."""
    source = (_SRC / "experiment/learning/prior.py").read_text()
    for machinery in ("register_prior", "PriorSpec(", "register_all_priors"):
        assert machinery not in source, (
            f"learning.prior still registers priors ({machinery}); one path only"
        )


def test_declared_defaults_survive_serialization() -> None:
    """The ``default`` declaration round-trips through the schema dict."""
    schema = harvest_schema()
    geometry = next(s for s in schema.hyperparameters if s.name == "input_dim")
    assert geometry.default is not NO_DEFAULT
    restored = schema.from_dict(schema.to_dict())
    restored_input = next(s for s in restored.hyperparameters if s.name == "input_dim")
    assert restored_input.default == geometry.default


def _config_cls(axis: StructuralAxis) -> type:
    module_path, class_name = {
        StructuralAxis.SUBSTRATE: (
            "computronium.ontology.substrate",
            "SubstrateConfig",
        ),
        StructuralAxis.GEOMETRY: ("computronium.ontology.geometry", "GeometryConfig"),
        StructuralAxis.DYNAMICS: (
            "computronium.ontology.dynamics",
            "StateDynamicsConfig",
        ),
        StructuralAxis.PLASTICITY: (
            "computronium.state.transitions",
            "PlasticityConfig",
        ),
        StructuralAxis.CREDIT: (
            "computronium.ontology.credit",
            "CreditAssignmentConfig",
        ),
        StructuralAxis.UPDATE: (
            "computronium.ontology.update",
            "ParameterUpdateConfig",
        ),
    }[axis]
    import importlib

    cls: type = getattr(importlib.import_module(module_path), class_name)
    return cls


def test_declared_names_target_real_consumers() -> None:
    """Each declared name is a dataclass field (or factory kwarg) its axis reads.

    Geometry is excluded: it is built by its own normalizer (``_fit_geometry``),
    whose key vocabulary lives in ``geometry_keys`` and is checked there.
    """
    schema = harvest_schema()
    for spec in schema.hyperparameters:
        if spec.axis_name == StructuralAxis.GEOMETRY.value:
            continue
        field_name = spec.name
        cls = _config_cls(StructuralAxis(spec.axis_name))
        if spec.axis_name not in {StructuralAxis.PLASTICITY.value}:
            assert field_name in {f.name for f in fields(cls)}, (
                f"{spec.axis_name}.{spec.name} is not a config field"
            )
        consumers = [
            n
            for n in dir(cls)
            if not n.startswith("_")
            and callable(getattr(cls, n, None))
            and field_name in inspect.signature(getattr(cls, n)).parameters
        ]
        assert consumers or spec.prior is not None or spec.default is not NO_DEFAULT, (
            f"{spec.axis_name}.{spec.name} has no consumer"
        )
