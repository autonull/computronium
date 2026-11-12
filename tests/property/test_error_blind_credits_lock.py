"""Lock: error-blindness is a declared category, not an accident (N10).

``homeostatic`` and ``temporal_trace`` read no label, so on a supervised task
they measure chance *by contract* (mnist recurrent: 0.0956/0.1234 against a
0.1018/0.1238 null; transformer mnist flat at 0.1009 for 9 epochs). Read as
"the credit is broken", that result sends the next investigator after a
dispatch bug. Read as a declared boundary, it says which credits the success
criterion counts: "≥3 credits work per geometry" means ≥3 **error-aware**
credits.

The declaration lives on each class (``error_blind``), every registered credit
carries it, and every error-blind credit must name the boundary on its
identity card. Falsified by adding a credit without the declaration, by
flipping a flag without a measured reason, or by dropping the card statement.
"""

from __future__ import annotations

from computronium.core.system_trainer.spec import _credit_from_config
from computronium.experiment.schema import AXES_REGISTRIES
from computronium.experiment.schema.axis import StructuralAxis
from computronium.ontology.credit import CreditAssignmentConfig, Phase

# The measured set. A third entry here is a measurement, not an opinion:
# name the run that showed it over chance-level episodes and add it beside
# the other two.
_ERROR_BLIND = {"homeostatic", "temporal_trace"}


def _credit(name: str) -> object:
    factory = getattr(CreditAssignmentConfig, name)
    return _credit_from_config(factory())


def _registered_credits() -> tuple[str, ...]:
    return tuple(sorted(AXES_REGISTRIES[StructuralAxis.CREDIT].keys()))


def test_every_registered_credit_declares_error_blind() -> None:
    """No class may inherit a default that silently reads as error-aware."""
    for name in _registered_credits():
        credit = _credit(name)
        assert hasattr(credit, "error_blind"), name
        assert isinstance(credit.error_blind, bool), name


def test_the_error_blind_set_is_the_measured_one() -> None:
    declared = {name for name in _registered_credits() if _credit(name).error_blind}
    assert declared == _ERROR_BLIND


def test_error_blind_is_not_derivable_from_the_phase_list() -> None:
    """``homeostatic`` settles both phases and still reads no error.

    The flag carries information the declarations around it cannot: a
    phase-list rule would call homeostatic error-aware, and a
    ``phases == (FREE,)`` rule would call local_contrastive error-blind.
    """
    phases = {name: _credit(name).phases for name in _ERROR_BLIND}
    assert phases["homeostatic"] != phases["temporal_trace"]
    assert _credit("homeostatic").phases == (Phase.FREE, Phase.NUDGED)
    assert _credit("local_contrastive").phases == (Phase.FREE,)


def test_a_label_channel_credit_is_not_error_blind() -> None:
    """``local_contrastive`` settles free-only but reads the target channel."""
    credit = _credit("local_contrastive")
    assert credit.phases == (Phase.FREE,)
    assert credit.error_blind is False
    assert credit.config.label_channel is True


def test_every_error_blind_credit_names_the_boundary_on_its_card() -> None:
    for name in _ERROR_BLIND:
        credit = _credit(name)
        card = credit.IDENTITY_CARD
        text = " ".join(card.deviations_from_literature + card.validated_limits)
        assert "error_blind" in text, name
        assert "chance" in text, name
