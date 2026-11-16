"""Lock: every credit row declares its estimator coordinate (TODO93 §2, B6).

W3 asks a bias/variance question, which is only well posed for arms that
*estimate a gradient*. A rule that optimizes a local objective has no gradient
to be biased about, so the taxonomy must be declared, never inferred from a
name or a shape. This lock fails as soon as a credit row loses its declaration:
``AxisSpec`` defaults to ``unspecified``, which is not a taxonomy member.
"""

from __future__ import annotations

import pytest

from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis
from computronium.experiment.schema.seed_registries import seed_all_registries

seed_all_registries()

_CREDITS = AXES_REGISTRIES[StructuralAxis.CREDIT]

# Rules that optimize a local objective rather than estimate the global
# gradient. Their report is update-direction alignment, not bias.
_OBJECTIVE_LOCAL = {"local_goodness", "local_contrastive", "pepita", "homeostatic"}
_GRADIENT_ESTIMATORS = {
    "gradient",
    "random_projections",
    "target_inversion",
    "thermodynamic_contrast",
    "pc_alm",
}


def _rows() -> list[str]:
    return sorted(_CREDITS.keys())


@pytest.mark.parametrize("name", _rows())
def test_every_credit_row_declares_a_kind(name: str) -> None:
    spec = _CREDITS[name]
    assert spec.estimator_kind != "unspecified", f"{name} has no estimator_kind"
    assert spec.bias_reference != "unspecified", f"{name} has no bias_reference"


@pytest.mark.parametrize("name", sorted(_OBJECTIVE_LOCAL))
def test_a_local_objective_is_not_labelled_a_biased_gradient(name: str) -> None:
    spec = _CREDITS[name]
    assert spec.estimator_kind == "objective_local"
    assert spec.bias_reference == "none", (
        "an objective-local rule has no gradient reference to be biased against"
    )


@pytest.mark.parametrize("name", sorted(_GRADIENT_ESTIMATORS))
def test_a_gradient_estimator_names_its_reference(name: str) -> None:
    spec = _CREDITS[name]
    assert spec.estimator_kind in {"exact", "gradient_approx"}
    assert spec.bias_reference == "exact_tractable"


def test_a_temporal_local_rule_is_declared_as_such() -> None:
    spec = _CREDITS["temporal_trace"]
    assert spec.estimator_kind == "temporal_local"
    assert spec.bias_reference == "none"


def test_non_credit_axes_carry_no_estimator_coordinate() -> None:
    """The taxonomy is a property of credit rules, not of every axis row."""
    for axis in StructuralAxis:
        if axis is StructuralAxis.CREDIT:
            continue
        kinds = {spec.estimator_kind for spec in AXES_REGISTRIES[axis].values()}
        assert kinds == {"unspecified"}
