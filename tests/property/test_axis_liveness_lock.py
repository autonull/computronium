"""Lock: TODO92 §3.9's refusal/liveness verdicts stay measured.

Three things are easy to break and are locked here:

* the two inert plasticity rows stay declared unavailable, with a reason and a
  reversal trigger, and are still reachable as primitives (a benchmark may use
  them outside the standard step);
* the declaration is true: ``rule_state`` and ``substrate_coupled`` are
  bit-identical to a joint null after one step, while ``fast_weights`` is not
  (the live control that proves the fixture can fail);
* the ruler itself works: Lion and Adam have identical ``train_loss`` after one
  step but different parameters, so a loss-based audit would miss the update
  axis. ``complex`` stays refused by ``complex_substrate_real_compute``.
"""

from __future__ import annotations

import pytest

from computronium.experiment.evidence.liveness import (
    CANONICAL,
    one_step_fingerprint,
    same_fingerprint,
)
from computronium.experiment.legality.dsl import CoordinateContext, evaluate
from computronium.experiment.legality.engine import void_rules
from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis
from computronium.experiment.schema.coordinate import Coordinate
from computronium.experiment.schema.seed_registries import (
    _UNAVAILABLE,
    seed_all_registries,
)

pytestmark = pytest.mark.timeout(180)

PLASTICITY = StructuralAxis.PLASTICITY


def _selection(**overrides: str) -> dict[str, str]:
    return dict(CANONICAL, **overrides)


def _one_step_vs_joint_null(plasticity: str) -> bool:
    """Whether a plasticity changes the post-step geometry vs a joint null."""
    selection = _selection(plasticity=plasticity)
    before, after, _ = one_step_fingerprint("digits", selection)
    reference = dict(selection, plasticity="null")
    _, null_after, _ = one_step_fingerprint(
        "digits", reference, initial=before, joint_null=True
    )
    return same_fingerprint(after, null_after)


def test_inert_plasticity_rows_are_declared_unavailable_with_a_trigger() -> None:
    seed_all_registries()
    for row in ("rule_state", "substrate_coupled"):
        spec = AXES_REGISTRIES[PLASTICITY][row]
        assert spec.available is False
        assert spec.unavailable_reason
        assert "TODO92 §3.9" in spec.unavailable_reason
        assert (PLASTICITY, row) in _UNAVAILABLE
        # The row is parked, not deleted: a benchmark can still construct it.
        assert row in AXES_REGISTRIES[PLASTICITY]


def test_the_unavailable_rows_are_inert_and_the_live_control_is_not() -> None:
    assert _one_step_vs_joint_null("rule_state") is True
    assert _one_step_vs_joint_null("substrate_coupled") is True
    # Control: a plasticity that does modulate must fail this fixture, or the
    # lock would pass with the mechanism removed.
    assert _one_step_vs_joint_null("fast_weights") is False


def test_one_step_parameters_see_lion_where_the_loss_does_not() -> None:
    adam_before, adam_after, _ = one_step_fingerprint("digits", CANONICAL)
    _, lion_after, _ = one_step_fingerprint(
        "digits", _selection(update="lion"), initial=adam_before
    )
    assert same_fingerprint(adam_after, lion_after) is False


def test_conflict_adaptive_is_live_under_a_compatible_credit() -> None:
    selection = _selection(plasticity="conflict_adaptive", credit="local_goodness")
    before, after, _ = one_step_fingerprint("digits", selection)
    reference = dict(selection, plasticity="null")
    _, null_after, _ = one_step_fingerprint(
        "digits", reference, initial=before, joint_null=True
    )
    assert same_fingerprint(after, null_after) is False


def test_complex_is_still_refused_by_its_named_rule() -> None:
    seed_all_registries()
    selection = _selection(substrate="complex")
    ctx = CoordinateContext(Coordinate(**selection, params={}), task="digits")
    rules = [rule.name for rule in void_rules() if not evaluate(rule.predicate, ctx)]
    assert "complex_substrate_real_compute" in rules
