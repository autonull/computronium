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


def test_no_hyperparameter_name_is_declared_by_two_axes() -> None:
    """Q3's gate: walk ``by_axis_specs``; a shared name is a seam defect."""
    shared: dict[str, set[str]] = {}
    for spec in harvest_schema().hyperparameters:
        shared.setdefault(spec.name, set()).add(spec.axis_name)
    doubled = {n: axes for n, axes in shared.items() if len(axes) > 1}
    assert not doubled, f"names declared by two axes: {doubled}"


def test_per_axis_names_are_the_declared_canonicals() -> None:
    """The split names exist on their axes — the rename is locked, not assumed."""
    schema = harvest_schema()
    by_axis = {
        axis: {s.name for s in specs} for axis, specs in schema.by_axis_specs.items()
    }
    assert {"settle_step", "settle_beta", "settle_momentum"} <= by_axis[
        StructuralAxis.DYNAMICS
    ]
    assert "update_lr" in by_axis[StructuralAxis.UPDATE]
    assert "credit_beta" in by_axis[StructuralAxis.CREDIT]
    for legacy in ("step_size", "beta"):
        assert legacy not in by_axis[StructuralAxis.DYNAMICS]
        assert legacy not in by_axis[StructuralAxis.CREDIT]
    assert "step_size" not in by_axis[StructuralAxis.UPDATE]


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
        "ruler_lr_mnist",
        "ruler_lr_catchall",
        "ruler_lr_non_feedforward",
        "step_size_override_energy_minimization_thermodynamic_contrast",
        "dynamics_step_size_diffusion",
        "hidden_width",
        "hidden_depth",
    ):
        assert name in PRIORS_REGISTRY, f"prior '{name}' missing from PRIORS_REGISTRY"


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


def test_alias_map_targets_real_config_fields() -> None:
    """Each alias maps to a dataclass field the axis's factories accept.

    Geometry is excluded: it is built by its own normalizer (``_fit_geometry``),
    whose key aliases live there.
    """
    from computronium.experiment.schema import CONFIG_FIELD_ALIASES

    schema = harvest_schema()
    for spec in schema.hyperparameters:
        if spec.axis_name == StructuralAxis.GEOMETRY.value:
            continue
        field_name = CONFIG_FIELD_ALIASES.get(spec.name, spec.name)
        cls = _config_cls(StructuralAxis(spec.axis_name))
        if spec.axis_name not in {StructuralAxis.PLASTICITY.value}:
            assert field_name in {f.name for f in fields(cls)}, (
                f"{spec.axis_name}.{spec.name} aliases to missing field {field_name}"
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
