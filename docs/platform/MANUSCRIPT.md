# MANUSCRIPT

> Promoted from `PUBLICATION_DRAFT.md` (kept as outline provenance).
> Claim set frozen per `PUBLICATION_VENUE.md`; every number traces to
> `REPRODUCIBILITY.md` and a registered evidence id (G-RELEASE-5).

# Composable Alternative Learning Mechanisms under Auditable Governance:
Frozen-Backbone Task Switching, Adaptive Local Feedback, and Stable
Transient Amplification

## Abstract

We present four learning mechanisms validated under an auditable,
pre-registration-based experimental governance protocol (CEEC), each scoped
to a stated regime and released as an independently installable package.
(1) A trace-decayed ridge readout on a frozen backbone switches between
conflicting tasks with the backbone bitwise-invariant, reaching 0.66–0.74
accuracy against a 0.25 frozen-null at quick budgets, with ~9× less
adaptation walltime than SGD readout retraining. (2) A slow-blend adaptive
feedback projection beats matched fixed feedback on all seeds for
late-trajectory improvement-per-norm. (3) A Riemannian-orthogonal update
confined to the readout weight beats its parent rules, with a concrete
boundary where the same orthogonalization collapses under local credit.
(4) Jordan-block coordinates with spectral radius ≤ 0.95 but largest
singular value > 1 yield 4×–2600× transient signal retention over matched
contractive coordinates, with paired replay showing noise divergence scales
identically — retention gain, not SNR gain. All experiments were run under
governance: pre-registered questions, gate-checked evidence, and calibrated
belief revision. We state boundaries and falsified branches explicitly and
release all packages, recipes, and evidence.

## 1. Introduction

Alternative learning mechanisms — local credit assignment, equilibrium
methods, orthogonalized updates, designed linear substrates — are typically
validated in isolation, with claims that silently outgrow their evidence.
This paper makes a deliberately narrow contribution: four mechanisms,
validated under governance, with claims frozen to their measured scope, and
a reusable protocol for doing so.

The mechanisms are expressed in a six-axis ontology — **substrate**,
**geometry**, **dynamics**, **credit**, **update**, and **plasticity** —
in which a learning system is a coordinate in a compatibility-constrained
subset of the axis product. Controlled comparisons hold axes fixed and swap
one; every validated mechanism here is such a controlled comparison. The
ontology is a design abstraction, not an established law of computation.

Our governance protocol (CEEC) requires that every experiment answer a
pre-registered question with a pre-registered prediction, pass gate checks,
and record evidence in an append-only ledger with belief revisions and
calibration records. The governance engine itself is released as a package.

### Contributions

1. Four validated mechanisms (§3), each with a recipe (when to use, when
   not to use), benchmark, validated scope, and limitations.
2. The CEEC governance protocol (§2), released and exercised by the same
   evidence that supports the mechanisms.
3. An explicit boundary record (§4): falsified and deferred branches, so
   negative results are first-class.
4. A reproducibility statement (§6) mapping every cited number to a single
   command and a registered artifact.

## 2. The CEEC protocol

CEEC is an evidence-ledger governance engine. Its primitives:

- **Experiments** are pre-registered: question, axes, prediction, budget,
  and success criterion are recorded before execution.
- **Evidence** records carry gate outcomes; claims must reference evidence
  that passed its gates.
- **Beliefs** carry intervals with revisions; each revision cites evidence
  and a calibration record, so interval honesty is itself measured.
- **Artifacts** (registered figures, benchmark outputs) are immutable and
  referenced by id.

In this work CEEC governed all four mechanism campaigns (evidence ids
E-000018, E-000022..E-000028). The protocol is not a simulation of good
practice; it is the actual execution substrate of the paper, and its ledger
ships with the reproducibility package.

## 3. Mechanisms

Each subsection states the mechanism, benchmark, validated scope, and
limitations. Full recipes are in the released recipe book; claims here do
not exceed them.

### 3.1 Temporal-ψ task switching (psi-peft)

A frozen backbone acquires, switches, and re-acquires tasks via a
lightweight ψ readout with trace-decayed ridge updates. Conflict between
task label geometries switches forgetting on (`AdaptivePsiReadout`); a
buffered variant amortizes the ridge solve (`BufferedPsiReadout`).

**Benchmark** (quick task, 3 seeds, mean): frozen_null 0.25; closed-form
ridge B=0.26 (it blends, as predicted); temporal trace decay (ρ=0.90)
B=0.66 with A-retention 0.76; adaptive conflict-gated trace decay B=0.74.
SGD readout retraining is ~9× slower in walltime at lower quick-budget
accuracy. The backbone parameters θ are bitwise-invariant in all ψ arms.

Conflict-adaptive trace decay turns forgetting on only when label geometry
conflicts — the mechanism keys forgetting to measured conflict, not to a
hyperparameter schedule (X-TAC-001).

**Validated scope:** quick-budget CPU probes on synthetic conflicting task
pairs, 3 seeds, frozen-feature setting.
**Limitations:** buffered arm trades ~0.1 conflict-phase accuracy for ~2×
speed; no optimality claim vs gradient readout retraining; no
transformer/LM evidence; non-conflicting incremental tasks leave the
adaptive machinery idle (correct but unexercised).

### 3.2 Adaptive local feedback (local-feedback)

In a local-learning loop (without weight transport), the feedback projection B
drifts slowly toward the normalized forward weight (EMA blend, matched
norm), making `e @ B` approach true backprop through the readout and
improving local descent quality without a global backward pass.

**Benchmark** (3 seeds × 60 steps, matched displacement norm): adaptive
late improvement-per-norm 0.0427±0.004 vs fixed 0.0381±0.004, with
per-seed wins asserted; feedback alignment 0.95 vs 0.43. Short-trajectory
protocol (10 steps): adaptive late improvement-per-norm 0.88/0.88/0.69 vs
fixed 0.49/0.48/0.53 across seeds.

**Validated scope:** two-layer local trainer, matched displacement norm,
slow blend (`feedback_lr=0.02`), 3 seeds.
**Limitations:** not validated end-to-end against internal equilibrium
systems; depth scaling unvalidated (X-ALI-003 deferred); very short
horizons on saturated tasks and fast re-projection (lr=1.0) are
out-of-scope settings.

### 3.3 Role-split orthogonal updates (computronium-lab) — boundary only

A role-split dispatcher applies a Riemannian-orthogonal (Muon-class)
update to the readout weight and euclidean updates elsewhere. The readout
confinement beats both parent rules on the mlp task (X-USU-001); the same
orthogonalization collapses under Forward-Forward × Muon local credit at
width 32.

We report this mechanism as a **boundary**, not a general recipe: the
X-USU-001 result is the validated scope, the FF×Muon collapse is the
heterogeneous-hardware caveat, and no wider boundary is claimed (the
defect hunt on muon-on-forward degradation was explicitly deferred, so
any such explanation would be unsupported).

### 3.4 Stable transient amplification (stability + lab)

A linear coordinate with realized spectral radius ρ ≤ 0.95 and largest
singular value σ_max > 1 (size-4 rotated Jordan blocks) settles in budget
and yields large transient signal retention over matched contractive
coordinates. `stability.matrices` builds and verifies the spectrum;
`computronium_lab.build_recipe("stable_amplification")` wraps it.

**Benchmark** (X-STA-002, 3 seeds, horizon 20, paired replay): signal
retention vs matched contractive control at ρ=0.85 — 4.2–5.5× at
σ_max=1.21, 19–40× at σ_max=1.60, 940–2600× at σ_max=4.06; all
amplifying coordinates settle within the 500-step budget (238–344).

The paired replay is the key finding: isotropic noise is amplified at the
*same* transient rate as the signal (noise-divergence ratio ≈ retention
ratio), so the mechanism buys retention, not noise robustness. The
distinction was confirmed experimentally and the belief interval narrowed
accordingly.

**Validated scope:** linear transitions (J = W measured exactly), quick
family ρ_t=0.85, amplification factor c ≤ 4, 3 seeds, paired-replay
protocol.
**Limitations:** linear-coordinate scope only; isotropic-noise SNR
unchanged; no nonlinear-system evidence; the transient decays, so this is
not long-horizon memory.

## 4. Boundaries, falsified and deferred branches

First-class negative results from the same governance pipeline:

- **Buffered-ψ accuracy tradeoff:** ~0.1 conflict-phase accuracy for ~2×
  speed at quick budget — documented, not hidden (§3.1).
- **FF×Muon collapse:** Newton–Schulz whitening destroys Forward-Forward
  local credit at width 32 — the concrete boundary of §3.3.
- **Routing blocked by baseline defect:** the dense-baseline routing
  comparison (X-RSE) never produced a paper-claimable result because the
  baseline could not beat chance in budget; the boundary is restated
  rather than papered over.
- **Noise ≠ SNR:** stable amplification preserves SNR rather than
  improving it — the "when not to use" entry is load-bearing (§3.4).

## 5. Hardware blueprint (simulation-only)

The stability and feedback mechanisms motivate an edge blueprint in which
transient amplification is a substrate property and feedback blending is a
device-level update. All validation here is CPU float32 simulation; no
physical hardware was measured, and the blueprint is design-level. Any
future hardware claim requires a pre-registered experiment under the same
governance (quantization and noisy-update simulations are the sanctioned
first steps, and they simulate hardware — they are not hardware).

## 6. Reproducibility statement

All five packages (psi-peft, local-feedback, computronium-lab, stability,
ceec-core) install from the repository lockfile. Every number in this
paper maps to one command and a registered artifact/evidence id in
`docs/platform/REPRODUCIBILITY.md`. A fresh clone reproduces the quick
budgets in a single session on CPU.

## Threats to validity

Verbatim from the governing outline:

- Quick synthetic tasks only; no large-scale or real-dataset results.
- CPU float32 simulation; no hardware measurements.
- Linear-coordinate analysis for the stability family (J = W exact).
- Belief intervals are heuristic, not Bayesian posteriors (method noted per
  revision).

## Non-claims

Verbatim from the governing outline:

- Not "backprop replacement"; all local-learning results are relative to
  matched fixed-feedback baselines within stated scopes.
- No universal efficiency claim for any mechanism.
- No neuromorphic hardware validation (blueprint is design-level).
