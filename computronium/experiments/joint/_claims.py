"""Claims-scope markers for the shakedown suites (per-suite audit, session 5).

Scopes are AUDIT STATUS, not verdicts:
- ``plumbing_only``: forward loop contains no ψ mediation, so results
  cannot evidence ψ-mediated behavior. (Historical: L3/L3.5 held this
  scope until 2026-09-09, when per-batch ψ stepping + modulation landed
  via ``_plasticity_wiring``.)
- ``psi_wired_uncontrolled``: ψ IS stepped inside forward and modulates
  computation (empirically confirmed to differentiate plasticity types), but
  θ trains concurrently, ``plasticity.step`` receives ``None`` context, and
  there is no frozen-θ control — so these are suggestive, not clean, ψ
  evidence. Rewiring with frozen-θ phases + ``ThetaInvarianceAudit`` remains
  open and would upgrade these suites rather than invalidate them.
"""

CLAIMS_SCOPE_PLUMBING_ONLY = "plumbing_only"
CLAIMS_SCOPE_PSI_WIRED_UNCONTROLLED = "psi_wired_uncontrolled"
CLAIMS_SCOPE_PSI_ENGAGED = "psi_engaged"

# R7 probe #3 (imp-43) engagement verdicts per suite. A suite may only carry
# an P-axis claim at PSI_ENGAGED. Locks: tests/property/test_psi_engagement.py
# (pipeline-level: ψ moves, modulate reaches activations, metrics respond to
# a frozen-ψ control).
#
# | Suite                 | Verdict                   | Blocking gap              |
# |-----------------------|---------------------------|---------------------------|
# | L1 adaptation         | psi_wired_uncontrolled    | adapt-time metric redone  |
# |                       | (2026-09-09)              | (held-out eval-acc        |
# |                       |                           | threshold + `adapted`     |
# |                       |                           | flag; pooling defect that |
# |                       |                           | collapsed A/B fixed); θ   |
# |                       |                           | still trains concurrently |
# | L2 compute_efficiency | psi_wired_uncontrolled    | gate entropy/FLOPs        |
# |                       |                           | discriminate routing, but |
# |                       |                           | θ trains concurrently     |
# | L3 robustness         | psi_engaged (2026-09-09)  | frozen-θ ψ-only recovery  |
# |                       |                           | arm added with            |
# |                       |                           | ThetaInvarianceAudit;     |
# |                       |                           | scope upgrades to         |
# |                       |                           | psi_engaged iff every     |
# |                       |                           | frozen audit is invariant |
# |                       |                           | AND ψ moved (no-op laws   |
# |                       |                           | stay uncontrolled)        |
# | L3.5 migration        | psi_engaged (2026-09-09)  | migration phase is now    |
# |                       |                           | ψ-only by construction: θ |
# |                       |                           | frozen + audited, ψ-moved |
# |                       |                           | check; measured verdict   |
# |                       |                           | (2026-09-09 real budget): |
# |                       |                           | frozen-ψ migration does   |
# |                       |                           | NOT solve A1 (0.55-0.59   |
# |                       |                           | vs A0 0.64-0.73) —        |
# |                       |                           | representation-limited,   |
# |                       |                           | consistent with z3_full   |
# | Z3 flagship           | psi_engaged (R8 gate      | gate is embedded per run  |
# |                       | landed 2026-09-01)        | (``psi_gate``: exact θ    |
# |                       |                           | invariance, ψ non-const., |
# |                       |                           | ψ task-conditioning, ψ→gate|
# |                       |                           | wiring, frozen-ψ control, |
# |                       |                           | above-chance probe acc);  |
# |                       |                           | a failed gate downgrades  |
# |                       |                           | that run to plumbing_only |
#
# The Z3 upgrade is enforced by tests/property/test_z3_engagement.py (R8.1
# lock + R8.2 planted-ψ positive control: engaged vs ψ-disabled arms, identical
# θ/task/seed/budget, detected through the suite path; the disabled arm is the
# engineered-broken variant the gate must flag).
