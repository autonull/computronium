"""Computronium domain profile for the CEEC kernel (TODO26 T26.G.1).

The lab declares its own vocabulary — scope dimensions, tier ladder,
ψ/θ constraints — as a :class:`ceec.profile.Profile`; the kernel stays
domain-free.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ceec.constraints import ConstraintResult
from ceec.profile import CORE_CONSTRAINTS, CORE_QUALITY, Constraint, Profile

if TYPE_CHECKING:
    from ceec.store import CEECStore

    from ceec import models


def _frozen_theta_audit(
    store: CEECStore, experiment: models.Experiment, _profile: Profile
) -> ConstraintResult:
    design = experiment.design
    ok = not design.get("psi_only") or "frozen_theta_audit" in experiment.hard_gates
    return ConstraintResult(
        "frozen_theta_audit_for_psi_only_claims",
        ok,
        f"psi_only={design.get('psi_only')}, "
        f"frozen_theta_audit gate={'frozen_theta_audit' in experiment.hard_gates}",
    )


def _identity_card(
    store: CEECStore, experiment: models.Experiment, _profile: Profile
) -> ConstraintResult:
    design = experiment.design
    ok = not design.get("new_primitive") or bool(design.get("identity_card_ref"))
    return ConstraintResult(
        "identity_card_for_new_primitive",
        ok,
        f"new_primitive={design.get('new_primitive')}, card="
        f"{design.get('identity_card_ref')!r}",
    )


COMPUTRONIUM_PROFILE = Profile(
    name="computronium-lab",
    policy_version="26.0",
    scope_dimensions={
        "domain": str,
        "task": str,
        "run_id": str,
        "substrate": str,
        "geometry": str,
        "credit": str,
        "budget": str,
    },
    budget_tiers=("quick", "standard", "nightly"),
    tier_budget={"smoke": "quick", "quick": "standard", "certified": "nightly"},
    default_cost={"quick": 1.0, "standard": 4.0, "nightly": 16.0},
    constraints=(
        *CORE_CONSTRAINTS,
        Constraint("frozen_theta_audit_for_psi_only_claims", _frozen_theta_audit),
        Constraint("identity_card_for_new_primitive", _identity_card),
    ),
    quality=CORE_QUALITY,
)
