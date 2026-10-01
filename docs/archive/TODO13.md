# TODO13.md — What Was Actually Found

> **Purpose:** Every valuable result from the Computronium project, stripped
> of process. No audit trails, no revision numbers, no "re-pin" language.
> Just the findings, organized by what they mean to someone who wasn't here.
>
> **Status of this document:** A record of what is known, not a plan to
> follow. Items marked **OPEN** are questions with evidence but no verdict.
> Items marked **PROVEN** have multi-seed, live-demo evidence. Items marked
> **REFUTED** were tested and found false — the refutation is the finding.

---

## 1. The Optimizer Discovery: OrthoAdam

**PROVEN.** The single most actionable result in the project.

**What it is:** Adam's adaptive moments + Muon's SVD-polar orthogonalization,
applied only to matrix-shaped parameters. The SVD polar factor of the
bias-corrected first moment replaces Adam's raw momentum direction, then gets
rescaled to Adam's step magnitude. Vector parameters (biases, LayerNorm
gains) keep plain Adam.

**What it does:**
- Beats both Adam and Muon on 3 of 4 tested geometries (MLP, attention,
  lattice). Only graph stays with Muon.
- At depth 16 / width 128: OrthoAdam 0.878 vs Muon 0.834 vs Adam 0.303
  (Adam collapses; orthogonalization repairs it).
- At depth 4 / width 128: FF×OrthoAdam 0.947 — repo-best held-out accuracy
  per parameter.
- Rescues the depth-20 predictive-coding regime: μPC×OrthoAdam 0.920 vs
  Adam 0.782; default-init×OrthoAdam 0.851 vs Adam 0.204.
- Newton-Schulz (5-step quintic) is statistically identical to SVD for
  OrthoAdam on all geometries, and costs ~40% less. NS collapses FF×Muon
  (different mechanism — see §1b).

**Why it works (the mechanism):** Adam's second-moment normalization is
itself depth-fragile — it amputates gradient signal where it's smallest,
compounding through depth. Orthogonalizing the momentum *direction* restores
graceful degradation while keeping Adam's magnitude adaptation. The lift is
momentum-direction-orthogonalization-driven, not full-spectrum-whitening-driven
(the rescale-to-Adam-step-magnitude dominates).

**What to do with it:** Use it. It's a drop-in replacement for Adam on
matrix-shaped parameters. Config: `ParameterUpdateConfig.ortho_adam(step_size=1e-3, ortho_lr=3e-3)`.
Working lr plateau is 5e-4–1e-3 on most regimes; 3e-3 was calibrated on MLP.
The lr is sharp — 3e-3 degrades the jPC regime to 0.52.

### 1b. The Muon vs OrthoAdam distinction

**PROVEN.** Muon's update IS the raw polar factor (no magnitude rescale, no
second moment). This means Muon's direction spectrum is fully whitened — SVD
maps even tiny singular values to 1. OrthoAdam rescales to Adam's step
magnitude, making the spectrum nearly irrelevant. Consequence: NS
(approximate orthogonalization) preserves OrthoAdam everywhere but collapses
FF×Muon to 0.29 — because FF×Muon's update *is* the raw polar factor, and NS
doesn't whiten the low-rank directions that SVD would have explored. Quote
this distinction if either is cited.

### 1c. The lr-semantics trap

**PROVEN (defect-hunt finding).** Every normalized update rule (Muon,
OrthoAdam, unit_rms, mean_norm) carries **per-element displacement**
step semantics: ‖Δθ‖ = lr·√n per tensor. Euclidean SGD carries
**gradient-relative** semantics: step magnitude scales with gradient magnitude.

Every learning-rate grid borrowed from SGD and applied to a normalized rule
is a mislabeled axis. This is a whole class of confound that produced at
least three false verdicts during the project:
- unit_rms's "convergence noise floor" was an lr mislabel (works at lr 1e-3,
  beats SGD).
- Muon's "explosion" on ePC was an lr overshoot at 0.01 (trains fine at 0.003).
- Natural gradient's "chance" was a 10× overshoot (trains at lr 1e-3 on all geometries).

**Structural fix (implemented):** `ParameterUpdateConfig.step_semantics`
property distinguishes `"gradient_relative"` from `"per_element_displacement"`,
and `SystemConfig.validate()` warns when a per-element rule carries
step_size > 0.05. Any future framework should adopt this metadata.

### 1d. Muon's advantage is direction quality, not scale

**PROVEN (lr-matched controls).** At matched effective step size on
LM (perplexity task): Muon 13.84 vs matched-Euclidean 30.26. The advantage
is direction quality. For ePC predictive coding, Muon is genuinely
load-bearing: the ÷β-capped gradient is so small that Euclidean SGD cannot
deliver a usable step at any finite lr (matched lr ≈ 134, explodes to 1e13).

---

## 2. Local Learning: What Works and What Doesn't

### 2a. FF-Hybrid: the practical local-learning rule

**PROVEN.** Forward-Forward + a readout error term
(`readout_error=True` on `CreditAssignmentConfig.local_goodness`).

Hidden layers keep the layer-local goodness objective (no backward sweep
through hidden layers). The output layer gets CE on the free logits through
the shared autograd graph.

**What it does:**
- Trains a causal Transformer on Shakespeare to 6.74 perplexity at 2.5 min
  (vs backprop/Adam 5.82) — ~15% behind backprop at matched wall-clock.
- Beats pure FF on MNIST: 0.857±0.010 vs 0.838±0.009 over seeds 0–4.
- Rescues the Euclidean optimizer arm: 0.798 vs pure FF's 0.568.
- Width-robust on LM: trains at every tested width (14.7–16.0 ppl), unlike
  PEPITA and ePC which are bidirectionally fragile.
- The advantage comes from attention/context-mixing, not supervision density
  (verified via zero-block isolation experiment).

**What it does NOT do:**
- It is not fully layer-local. The readout CE's autograd chain reaches hidden
  layers. The honest claim: "forward-local credit with a single readout
  supervision term — no backward sweep through the hidden layers." Never
  "fully local."
- Its current PyTorch implementation stores ≥ backprop activations (see §5).

### 2b. Realized PEPITA: distinct from FF, but slow

**PROVEN (as a distinct algorithm).** `local_objective="pepita"` implements
softmax output error × fixed random inverse projections (closed form,
CRC-seeded orthogonal B). FF and PEPITA produce measurably different
pseudo-gradients (ratchet lock prevents regression to byte-identity).

PEPITA learns at demo budget (0.226 Muon / 0.106 Euclid, 1 epoch) but is
far slower than FF. On LM at 1 min: stable but marginal (135–221 ppl).

**The bottleneck is the fixed random projections.** Five error-signal
transforms were tested (centering, RMSNorm, both, orthogonal init,
feedback_scale tuning). None rescues PEPITA. The collapse is in the
directionally-random channel — a fixed random B is uncorrelated with each
layer's feature space, and the misalignment compounds with depth/width.

**The remaining lever (OPEN):** learned feedback projections — train B
through the autograd graph alongside θ (PEPITA-as-inference-network).
Not yet implemented as a library primitive.

### 2c. ePC × Muon: energy-based learning on language

**PROVEN (at registered width).** Error Predictive Coding (Goemaere et al.)
with thermodynamic contrastive credit and Muon trains an LM at registered
width (w816×7, 7.4M params): 2.81 train / ~21 val perplexity at 1 min.

**Critical constraint:** Muon is load-bearing. The ÷β-capped ePC gradient
is 400× too small for Euclidean SGD at stable lr; scaling to parity diverges.
Standard Predictive Coding (sPC) flatlines on LM — its layered settle traps
the nudge (hidden credit norms exactly 0.0).

**Width constraint:** ePC explodes below width ~256 on LM (per-layer
activity-scale compounding — see §3b). Width ≥ 256 required.

### 2d. Pure Forward-Forward on LM: refuted

**REFUTED.** Pure FF's layer-local goodness objective is error-blind for
next-character prediction. Flat at chance on LM at every lr tried, both
geometries (MLP and Transformer), context 8–64. The norm-contrast objective
has no term that sees the target (β 0.5 vs 2.0 gives identical results —
the nudge strength is irrelevant). FF×Muon learns MNIST fine; the failure
is specific to next-char prediction. The hybrid (§2a) is the salvage.

### 2e. Per-layer contrastive FF: true locality works

**PROVEN (probe scale).** A per-layer contrastive FF implementation
(detached/recomputed inter-layer inputs, per-layer local backward) achieves:
- Nonzero hidden credit with NO cross-layer sweep (mechanism live).
- Per-layer peak memory (268.8 KiB at depth 4) beats backprop's whole graph
  (569.3 KiB) — the physical advantage is real for this realization.
- Learns LM without any readout CE: top-1 next-char 15.8% vs unigram 9.4%
  (seeds 0–2, leak-controlled).
- Depth wall still present: d2 0.827 → d4 0.764.

**OPEN:** momentum-EMA normalization for this class (the canonical magnitude
family per §1c's lesson); same-metric ff_hybrid comparison; library-grade
realization with the recompute pattern.

### 2f. Credit-space normalization: spectral flattening works

**PROVEN (mechanism).** `credit_norm="spectral"` on
`CreditAssignmentConfig` flattens per-layer credit norms from ~4×/layer
decay to exactly ~1.0 through depth 16. Depth-8 learning lifts:
0.195 (spectral+euclid) vs 0.113 (none, matched).

**Does NOT transfer to contrastive objectives.** Per-layer unit-RMS
normalization of the goodness gradient collapses learning at every depth
and displacement — the gradient's magnitude CARRIES information in
contrastive objectives (softplus gating), and instantaneous normalization
erases it. Contrastive credit_norm modes must be EMA-based or margin-aware
if ever built. Never instantaneous.

**Does NOT compose with the faithful regime.** In the jPC-faithful regime
(Adam + β grid + steps=H), credit_norm actively harms: ε in the
reparameterized channel is dynamics, not just credit. Rescaling breaks the
μPC/β scale structure. Levers do not naively compose.

---

## 3. The Depth Problem

### 3a. The depth wall is regime-bound, not physics

**PROVEN.** The apparent wall (local learning dies at depth ~8) dissolved
under the jPC-faithful regime:
- μPC init + ePC + PC-native weight gradient + Adam + β=10 + inference
  steps=H: depth 20 / width 128 residual reaches test 0.69–0.83
  (seeds 0–2), vs default init 0.14–0.24 (memorization).
- OrthoAdam lifts the whole regime further: μPC×OrthoAdam 0.920 at depth 20.
- BP×Euclid at chance at depth 16; BP×Muon 0.834; BP×OrthoAdam 0.878.
  The U-axis moves the depth wall.

The earlier "no lift" verdicts were trainer-regime artifacts (Euclidean SGD,
β=0.5, fixed 60 settle steps — not the paper's Adam/β-grid/steps=H).

**Structural finding:** momentum-orthogonalization and depth-scaled
initialization are partially interchangeable repairs of the same depth
pathology. Under OrthoAdam, the μPC-vs-default gap narrows from ≈0.58 to
≈0.07, but μPC still leads per seed.

### 3b. The structural gain-control thesis

**PROVEN (three families).** Local-learning depth/width failures reduce to
one mechanism: **per-layer activity-scale compounding when the error signal
is not self-normalized.** Demonstrated across three algorithm families:

| Family | Failure mode | Mechanism |
|--------|-------------|-----------|
| Error-based credit (ePC) | ÷β error compounds ∝ width | Telescoping decay through depth |
| Unnormalized local (Hebbian/tile chains) | Per-layer gain 1.2–1.5× compounds to inf | Runaway gain |
| Fixed random projections (PEPITA) | B uncorrelated with feature space | Directional collapse |

Normalized variants (Oja with unit-RMS, μPC init) fix the gain but introduce
subspace collapse (effective rank decays ~0.5/layer through depth).

**The bottleneck is structural gain control, not credit direction alone.**
Any rule whose error signal carries width- or depth-proportional scale
without per-layer normalization will hit this wall.

### 3c. β is a working-regime knob, not a monotone dial

**PROVEN.** At depth 20 / width 128: β=10 generalizes (test 0.78),
β=1e3 lands in the memorization corner (train 1.00, test 0.09–0.36).
β=1.0 with autograd credit is a dead loss surface (exactly zero
pseudo-gradient — config-time guard implemented).

---

## 4. Plasticity (P-axis): What Was Measured

### 4a. Routing retention advantage is effective-lr alone

**PROVEN (lr-matched controls).** RoutingPlasticity's retention advantage
over NullPlasticity disappears when null's lr is matched to routing's
effective step (null@matched retains 0.294 vs routing 0.273). The ordering
is effective learning rate, not a routing mechanism. No mechanism claim is
quotable.

### 4b. FastWeight retention deficit is real

**PROVEN.** FastWeightPlasticity's step matches null's (0.032 ≈ 0.03),
yet its retention is below null (0.155 vs 0.184). The deficit is real,
not an lr artifact. (Note: ψ re-initializes per episode under the current
`train_step` contract — this is a scope-honest boundary, not a verdict
on fast weights as a mechanism.)

### 4c. ψ-only adaptation: impossible at HEAD

**PROVEN (as a boundary).** With θ bitwise frozen (SHA-verified), neither
RoutingPlasticity nor FastWeightPlasticity can acquire a new task. Root
cause: no landed ψ law consumes a task-loss signal. The ψ-step contract
feeds ψ only the FREE (target-free) settled activity. The mechanism
assert (‖Δθ‖=0) is trivially true; the value claim evaporates.

**The missing primitive:** a supervised ψ term (target-conditioned
Hebbian outer product, or reward-modulated plasticity). Pre-register
before building. The D22 probe is the reusable instrument.

### 4d. STDP collapse survives homeostatic scaling

**OPEN.** Synaptic scaling (normalize incoming weight rows to a target norm)
holds row norms at target, yet the centroid readout still collapses
(0.36 → 0.18) at every target tried. The STDP fixed point itself destroys
class structure, not norm growth. Gain control is necessary but not
sufficient.

**Remaining audit:** reward-modulated STDP (a supervised error term).
Without it, no supervised spiking claim is possible — `TemporalTraceCredit`
declares `phases=(FREE,)` and never consumes the loss.

---

## 5. The Physical Advantage: Not Yet Realized

**PROVEN (as a miss).** The capstone resource-accounting demo (F5) measured
memory and FLOPs for the local-learning variants vs backprop:

- **Memory:** ff_hybrid's autograd realization saves MORE than backprop
  (177.5 vs 143.5 KiB at depth 16). The autograd chain is load-bearing.
- **FLOPs:** ff_hybrid costs ~1.3× backprop. OrthoAdam's SVD premium is
  real but modest at demo scale (+11%; grows as d³ at registered scale).
- **The O(1)-memory class is real:** thermodynamic contrast (ePC) saves
  exactly 0 bytes at every depth. The algorithmic locality exists.

**The lever:** a non-autograd local-rule realization. The per-layer
contrastive FF probe (§2e) demonstrated the recompute pattern: per-layer
peak memory beats backprop's whole graph at depth ≥ 4. A library-grade
credit using that pattern would flip F5's ratchets.

**OPEN:** per-layer memory advantage requires depth ≥ 4. At depth 2, the
input layer's own local graph ≈ backprop's whole graph. Any resource
claim must sweep depth, never quote depth-2 cells.

---

## 6. The Defect-Hunt Methodology

**PROVEN (as a practice).** TODO12b pre-registered 8 suspicion probes
against the project's own pessimistic conclusions. Results: 4 confirmed,
3 refuted, 1 partial. The confirmed defects overturned 2 verdicts
(unit_rms "noise floor" → lr mislabel; Muon "explosion" → lr overshoot).
The refuted suspicions upgraded 3 pessimistic verdicts to "defect-audited"
status (D22 ψ-only, PEPITA structural, F5 instrument).

**The reusable lesson:** before accepting any negative verdict about an
algorithm, check:
1. **lr semantics** — is the lr axis appropriate for the update rule's
   step semantics? (gradient-relative vs per-element displacement)
2. **Regime fidelity** — does the implementation match the source paper's
   stated regime? (architecture, optimizer, schedule)
3. **Instrument sanity** — does the measurement instrument itself work?
   (packed-tensor counts, eval metric definitions, data leakage)
4. **Bias/contract gaps** — are biases training? Is the loss surface
   actually live? (β=1.0 dead surface, weights-only backprop)

All four classes produced false verdicts in this project.

**Standing locks (implemented):** `test_defect_hunt_locks.py` — 8 tests
locking the lr-semantics identity, weights-only contract, thermodynamic×
instantaneous hidden zero, β=1.0 dead surface, and the routing-flip no-op.

---

## 7. What Remains Open

These are the questions with evidence but no verdict, ordered by
expected leverage:

| Question | Evidence so far | Next step |
|----------|----------------|-----------|
| Learned feedback projections for PEPITA | Fixed B is the measured bottleneck; 5 error transforms failed | Train B through autograd graph alongside θ |
| Per-layer contrastive FF as a library credit | Probe works (memory beats bp, learns LM without CE) | Library realization with recompute pattern + EMA normalization |
| Non-autograd ff_hybrid realization | F5 pinned the miss; the O(1)-memory class is real | Hand-written local-goodness update (no autograd graph) |
| Reward-modulated STDP | STDP collapse survives homeostatic scaling; no task-loss signal | Add supervised error term to TemporalTraceCredit |
| Supervised ψ term for P-axis adaptation | D22 proved ψ-only impossible without task signal | Target-conditioned Hebbian outer product, pre-registered |
| ePC on LM at full parity | epc_thermo×Muon reaches ~21 ppl vs bp 9.9 | Contrastive repairs + propagation fixes (credit_norm + learned B) |
| Momentum-EMA normalization for per-layer class | Instantaneous norm destroys contrastive learning | EMA-based credit_norm mode, pre-registered |
| TransformerGeometry × ePC settle extension | Block-structured settle needed for transformer PC cells | Geometry extension (bias-free transformer needs error routing) |

---

## 8. The Library (What Exists)

A fully implemented, tested 6-axis ontology for composing learning systems:

**System = Substrate × Geometry × StateDynamics × Plasticity × CreditAssignment × ParameterUpdate**

- **6 substrates:** Digital, Memristive, Neuromorphic, Photonic, Quantum, Ternary
- **7 geometries:** Feedforward, Recurrent, Conv, Graph, Attention, SpatialLattice3D, TileMesh, Transformer
- **6 dynamics:** EnergyMinimization, PredictiveSettling, ErrorPredictiveCoding, SpikeIntegration, Instantaneous, Lazy, Diffusion
- **4 plasticity primitives:** Null, Routing, FastWeight, SubstrateCoupled
- **8 credit rules:** Backprop, ThermodynamicContrast, RandomProjections, LocalGoodness (FF/PEPITA/hybrid), TemporalTrace, TargetInversion, Homeostatic, PredictiveCoding
- **9 update rules:** Euclidean, Adam, OrthoAdam, Muon, UnitRMS, LocalAdam, MeanNorm, Spectral, ElasticConsolidation

**1772 tests passing.** Every claim re-demonstrated on demand in the demo
suite. 19 demo tests (fast tier ~205s) + 3 slow-tier registered-scale demos.

**Key infrastructure:**
- `SystemTrainer`: single training loop for all learning rules
- `compose_joint_system`: 6-axis composition with type-safe config
- Resumable trainer with `fold_in` RNG (bitwise resume)
- `torch.compile` settle fast paths
- Gallery/figure lock system for drift-immune evidence

---

## 9. The One-Paragraph Summary

Computronium is a composable ML library that treats learning rules as
swappable components across six axes. The most actionable finding is
**OrthoAdam** (Adam moments + momentum orthogonalization), which beats both
parents and repairs Adam's depth fragility. The most important local-learning
result is **FF-hybrid** (Forward-Forward + readout error), which trains a
Transformer LM to within ~15% of backprop without a backward sweep through
hidden layers. The depth wall in local learning is **regime-bound, not
physics** — predictive coding trains to depth 20 under the right optimizer
and initialization regime. The structural bottleneck for local rules is
**gain control**: any rule whose error signal carries width-proportional
scale without per-layer normalization will hit a wall. The physical
advantage (memory/energy savings) is **algorithmically real but not yet
realized in implementation** — the non-autograd recompute pattern is the
known path. The most valuable methodological finding is that **lr-semantics
mismatch is a systematic confound class**: every normalized update rule
carries per-element-displacement step semantics, and every lr grid borrowed
from SGD is mislabeled. None of the "pure" local rules (FF, PEPITA, sPC,
naive STDP) work on language modeling without modification; all require
either a global readout signal, a heavy optimizer crutch, or a regime
change to survive.

----

# TODO13.md — Active Plan: Build on the Wins

> **Opened 2026-09-07 (rev 2).** Successor to TODO12.md (credit-channel
> repair program, closed) and TODO12b.md (the defect hunt: 4 CONFIRMED /
> 1 partial / 3 REFUTED). Research catalog: RESEARCH4.md.
>
> **Identity (unchanged):** Computronium is an ML library whose every claim
> is a live demonstration. Tests are the evidence system. A claim stands
> only while the current code re-demonstrates it, on demand, in under two
> minutes. Verification is continuous, not archival.
>
> **Prime directive:** *Nothing is claimed that the suite does not re-show
> at HEAD. The demo suite is the proof; everything else is history or
> hypothesis.*
>
> **Posture (user directive):** disappointed with progress; reconsider
> strategy; focus on the most valuable and exciting opportunities,
> optimistically, with open-minded clever speculation. The repair-and-audit
> era made the instrument honest but produced no visible capability. TODO13
> converts confirmed assets into artifacts. **Optimism with a probe budget,
> not optimism as a mood.** Every session ends in a pinned demo, a killed
> speculation, or a promoted probe — audit-only sessions are retired.
>
> **Rev 2 changes:** the D17 seed-0 bombshell elevated to first-class
> status (§1) with its anomalies, anchors, and verification protocol;
> dead-item ledger added (§4); carried queue with revival conditions (§7);
> SP6 (OrthoAdam-on-LM cheap cells) added; operational details (commands,
> LR table, harness) restored from TODO11/12.

---

## 🚨 §1 — THE BOMBSHELL: D17 seed-0 (verify or kill before anything else)

**What was measured (2026-09-06, rev 13, single seed, 15-min walltime arms,
registered shape — transformer d320/6L/C128, 7.41M params, capacity-matched
to mlp w816×7L 7.43M; chance = 65 ppl):**

| Arm | val_ppl @ 15 min | Steps taken |
|---|---|---|
| **transformer/ff_hybrid/muon** | **5.05** | 2,200 |
| transformer/bp/adam | 27.55 | 15,217 |
| mlp/ff_hybrid/muon | 27.94 | — |

If this survives audit, it is the biggest result in the repo: a
hybrid local-credit transformer **5.5× better than backprop at matched
walltime while taking 7× fewer steps**. Run paused at seed 0 by budget
directive; salvaged arms in `benchmark_results/d17_seed0.json` (untracked).

### Why it could be REAL (the anchors)

- **2.5-min smoke:** ff_hybrid 6.74 vs bp/adam 5.82 (~15% behind) — the
  gap at 15 min is a continuation, not an apparition.
- **P1a:** ff_hybrid beats pure FF on every seed (0.857±0.010 vs
  0.838±0.009) and rescues the Euclid arm (0.568→0.798).
- **P1b:** the deficit rides on attention-based contextual mixing, and
  ff_hybrid tracks bp on the dense path (13.9 vs 12.16) — no
  supervision-density pathology.
- **P3:** Muon's advantage is direction quality (matched-step 13.84 vs
  30.26 ppl) — the ff_hybrid×Muon pairing is a verified combination.
- **P4:** ff_hybrid is width-robust (14.7–16.0 across w32–256) — the one
  local rule without a fragility window.

### Why it could be WRONG (the anomalies — audit these FIRST)

1. **bp/adam's 27.55 is inconsistent with its own smoke trajectory.**
   bp/adam hit 5.82 at 2.5 min on the 156k smoke shape; at 7.4M params and
   15 min it should be *better*, not 5× worse. 27.55 sits near unigram
   entropy for tiny_shakespeare (~22–30 ppl) — the baseline may have
   collapsed to unigram (lr wrong at registered scale? warmup missing?
   residual mixed-ctx defect?). **Check the train-loss curve in
   d17_seed0.json before anything else.**
2. **The 7× throughput asymmetry is unexplained.** Muon SVD on
   320×1280-class matrices should not cost 7×/step. Candidates: ff_hybrid's
   autograd chain IS a backward sweep through the hidden layers (Claim A
   scope audit — it pays bp's cost plus goodness overhead); or a harness
   accounting asymmetry. Either way, know the per-step cost before quoting.
3. **Single seed.** The μPC fake-2× scar is the standing warning.
4. **Walltime-budgeted arms can never be gallery-pinned** — promotion
   requires converting to a fixed-step regime regardless of verdict.
5. **The `_val_sets` mixed-ctx defect was fixed en route** (windows were
   cut at max(ctx); crashed the registered mlp arm's eval; now per-family
   ctx). Confirm which arms ran pre-fix vs post-fix.

### Verification protocol (ordered by cost)

| Step | Action | Cost |
|---|---|---|
| **0** | Regime reconciliation from data already on disk: read d17_seed0.json curves — where is bp/adam at step 2,200? Where is ff_hybrid extrapolated? Tokens seen per arm; check registered lrs against the `step_semantics` guard | free |
| **1** | Instrument per-step cost + per-step val_ppl on both arms at ~1 min; explain the throughput asymmetry; if bp/adam's registered lr is suspect, micro-sweep it (the H1/H4 lesson: never trust a baseline at an unverified lr) | ~10 min |
| **2** | Smoke-verify every registered arm end-to-end (the D17 lesson: 1-min arms before minute-scale arms) | ~15 min |
| **3** | Resume seeds 1–2 on VERIFIED arms (per-batch approval per the runs directive): `uv run python scripts/probes/lm_comparison.py --minutes 15 --arms transformer/ff_hybrid/muon,transformer/bp/adam,mlp/ff_hybrid/muon --seed 1` (then `--seed 2`); copy `benchmark_results/lm_comparison.json` → `d17_seed<N>.json` after each | ~90 min GPU, user-gated |
| **4** | Seed-mean, apply the pre-registered band mechanically, promote to fixed-step D17 demo + gallery lock | 1 session |

**Pre-registered verdict band (from TODO12, unchanged):** reported number =
mean val_ppl over seeds 0–2; gap = (ff_hybrid − bp)/bp. **<15% headline
parity · 15–25% competitive-with-caveat · >25% MISS → C1 fallback triggers
mechanically.** If the audit shows the baseline was sick, the band is
recomputed against a healthy baseline — same mechanical rule, honest
denominator.

**If verified:** the headline needs no advertising — "hybrid local credit
trains a transformer LM 5× better than backprop at matched walltime."
Immediate follow-ups: ff_hybrid×OrthoAdam cell (SP6), scale curves,
matched-token analysis, the fixed-step gallery pin.
**If killed:** honest mechanism note; the ff_hybrid story reverts to the
2.5-min anchor (~15% behind, still the best local rule); nothing was ever
quoted, so nothing is lost.

**Claim scoping (binding):** ff_hybrid at HEAD performs a backward sweep
through the hidden layers (Claim A scope audit). The bombshell is a
**performance** claim, not a **locality** claim. Locality is S3's job.
Never "fully local"; never "local learning beats backprop" — the canonical
wording ("forward-local credit with a single readout supervision term — no
backward sweep through the hidden layers") holds only for
requires_autograd=False credits and the B4-style per-layer class.

---

## 🏆 §2 — The Asset Inventory (every confirmed, pinned result)

### The headline capabilities

| Result | Numbers | Why it matters |
|---|---|---|
| **OrthoAdam** (Adam moments + momentum orthogonalization) | mlp **0.930** / attention **0.911** / lattice **0.924** (beats both parents; graph 0.411 where Muon keeps 0.433); depth-16 **0.878±0.035** vs Adam's collapse 0.303±0.079; **FF×OrthoAdam 0.947±0.002 @ ~119k params** — repo-best acc/param; NS variant statistically identical, ~40% cheaper | The strongest empirical asset. Momentum-orthogonalization is the dominant repair across credit rules and geometries |
| **The jpc-faithful regime — depth-20 local learning WORKS (D14)** | μPC+β=10 test **0.686/0.828/0.831** (default init memorizes: train 1.00 / test ≤0.24); **mupc×OrthoAdam 0.920 mean**; **default×OrthoAdam 0.851** vs Adam 0.204; plain SGD alone 0.528; β=1e3 = memorization corner | The depth wall is regime-bound, not physics. ePC + PC-native weight gradient + Adam + β grid + steps=H dissolves it |
| **ff_hybrid — the local-credit LM rule** | 6.74 ppl @2.5 min vs bp 5.82 (~15%); beats pure FF everywhere; rescues Euclid 0.568→0.798; width-robust at every width tested | First local-error rule training a transformer LM through the ontology pipeline; the bombshell's star |
| **Muon/OrthoAdam lift on local credit (multi-seed)** | FF×Muon **0.838±0.009** vs Euclid 0.568±0.041 (5 seeds, min lift +0.241); direction quality not lr scale (P3) | Verified combination, quotable |
| **ePC on LM** | epc_thermo×Muon val ~21 vs bp 9.9 at 7.4M params (w816×7); train 2.81 @1 min; Muon genuinely load-bearing (euclid step 400× too small) | The PC family is alive on language |
| **unit_rms — width fragility killed** | ePC w32–256 trains WITHOUT Muon (D18: w64 32.5 vs Muon-registered-lr 101.2); Muon works at 0.003 (36.8) but trails | Magnitude normalization alone is the width repair |
| **credit_norm flattens ePC decay** | spectral: per-layer norms ~1.0 flat through depth 16 (vs 4×/layer); depth-8 lift 0.195 vs 0.113 | The credit channel is repairable by normalization |
| **B4 per-layer FF — the flagship mechanism** | Nonzero layer-local credit with NO cross-layer sweep; per-layer peak **268.8 KiB < bp's whole graph 569.3 KiB** (d4); LM top-1 **15.8/15.6/16.0% vs unigram 9.4%**, chance 1.5%, leak-controlled (untrained 1.7%, shuffled 5.3%) | Proof that TRUE locality + physical advantage + real learning coexist. The seed of the Claim A/B repair |
| **μPC + OrthoAdam are interchangeable depth repairs** | gap narrows 0.58 → 0.07 under OrthoAdam; μPC still leads per seed | Two knobs, one dial — momentum-space orthogonalization substitutes for parameter-space scaling |
| **Defect hunt (TODO12b)** | unit_rms beats euclid at its own lr (0.900 @1e-3 vs 0.878 @0.1); Muon trains at 0.003; biases delta 0.000; β=1.0 = dead surface (guarded); F5 counter sound; D22 defect-audited | The instrument is trustworthy; most "impossible" results were regime or measurement artifacts |
| **D22 contract finding** | ψ-only adaptation impossible (no ψ law consumes a loss term) — but ‖Δθ‖=0 is bitwise-assertable; fine-tune acquires B 0.984 at real forgetting cost | The exact boundary AND the exact lever |
| **P-axis primitives realized (F3)** | per-gate routing (mask std 0.081) + settled-activity fast weights; retention orderings survive realization; effective-lr confound quantified (routing's advantage = lr alone); fast-weight deficit real | The P-axis instruments are their advertised mechanisms |

### The unifying insight

**Credit-signal fidelity is the whole story.** Backprop's cheat is the exact
transpose Jacobian; every local rule leaks fidelity in one classified way —
misaligned (PEPITA), attenuating (ePC depth), unnormalized gain (width
fragility), disconnected (pure FF), blocked (sPC), low-rank (optimizer
crutch). Each has a measured repair. Nobody else has this map.

### Meta-lesson (the grounds for optimism)

**The algorithms kept being better than the measurements said.** F1 depth
wall → regime-bound (D14). μPC "no lift" → trainer artifact. unit_rms
"noise floor" → lr mislabel. Muon "explosion" → lr confound. PEPITA →
fixed projections. Natural gradient "boundary" → step-size artifact. Every
pessimistic verdict that got a defect audit either dissolved or got
sharper. The pessimistic conclusions were systematically wrong — exactly as
the user predicted. This is the empirical basis for TODO13's optimism.

---

## 📋 §3 — Carried operational details (don't re-derive)

- **LM harness:** `scripts/probes/lm_comparison.py` — ready; both families
  through one pipeline; capacity-matched (ratio asserted + printed);
  fixed shared val windows; JSON → `benchmark_results/lm_comparison.json`.
  Registered: transformer d320/6L/C128 7.41M vs mlp w816/7L/C64 7.43M
  (ratio 1.003). Smoke: 156,544 vs 149,889.
- **LR table (smoke-tuned):** bp/adam 1e-3; bp/muon 0.01; bp/ortho
  ortho_lr 1e-3; ff/muon 0.01; pepita 5e-4 on transformer / 0.002 MLP
  (wildcard-LR ordering: specific patterns before wildcards).
- **Registered-scale CELLS:** transformer {bp/adam, bp/muon, ff_hybrid/muon,
  pepita/muon}; mlp {bp/adam, ff_hybrid/muon, epc_thermo/muon, ff/muon,
  ff/ortho_adam, pepita/muon}.
- **jpc manual loop (the D14 reference):** ePC settle free+nudged (steps=H,
  β grid) → freeze settled errors → d(β·CE)/dθ → Adam 1e-3. β is a
  working knob, not a monotone dial (β=10 generalizes; β=1e3 memorizes).
- **Walltime asymmetry is structural:** transformer arms see ~9× more
  tokens/s than mlp arms (dense per-position CE vs single target) —
  comparisons are wall-clock-budgeted by directive; the asymmetry is
  recorded, not hidden.
- **Probe hygiene:** seed before every loader draw (D8 trap, confirmed
  3×); probes in `scripts/probes/` with pre-registered predictions in the
  docstring; verdict numbers live in the docstring.
- **Gallery pinning:** fixed-step arms only; walltime printed never
  recorded; manifest re-pins additive-only; drift-immunity = 2 consecutive
  green runs.
- **Gates:** fast tier ~205 s (D1–D13 + F1–F3 + locks); slow tier
  `pytest -m slow -k demo` (D14+D15+D16, ~14 min); invoke as
  `uv run python -m pytest` (user-site pytest drift).

---

## ⚰️ §4 — The Dead-Item Ledger (do not retry without a new lever)

| Item | Verdict | Revival condition |
|---|---|---|
| **Pure FF on LM** | Error-blind objective; flat at chance; β irrelevant | Only via readout_error hybrid (landed) or per-layer targets (S3) |
| **PEPITA** | Parked after 5-cause audit (feedback_scale, centered-e1, row space, hidden gain, output step shape all ruled out); cheap error transforms refuted (P5); collapse in the fixed random projections | New probe on the weight-trajectory channel or a faithful forward-modulation realization; learned-B feedback_lr sane regime 0.01–0.05 if ever re-pinned |
| **ψ-only adaptation (current ψ laws)** | Impossible — no ψ law consumes a loss term (D22, defect-audited) | A supervised ψ-law primitive (S4), pre-registered |
| **F5 physical advantage at HEAD** | ff_hybrid's autograd realization stores ≥ bp, ~1.3× FLOPs; both targets falsified | The non-autograd / recompute realization (S3) flips the ratchets |
| **A4 instantaneous normalization on contrastive objectives** | Gradient magnitude CARRIES information (softplus gating); instantaneous norm collapses learning at every depth | EMA-based or margin-aware normalization only — never instantaneous for goodness-contrast |
| **jpc frozen-error gradient on LM** | 13 regimes negative; corrected forward fits while free settle lands at chance | Untried cells only: exact inference-network ε, γ grid, width 512, steps > H — and only if the contrastive path (epc_thermo) stalls |
| **sPC layered settle** | Nudge trapped; hidden credit exactly 0.0 | ePC supersedes it; no revival path |
| **STDP + homeostatic scaling** | Collapse survives fix #1 (norms held, readout 0.36→0.18) | Reward-modulated STDP (B5) — the supervised error term |
| **Muon NS for FF×Muon** | FF×Muon lift is whitening-driven; NS collapses it to 0.29 | None for that pair — SVD stays default for FF×Muon; NS fine for OrthoAdam |
| **"Natural gradient" mechanism claims** | The primitive is a mean-\|grad\| normalizer (renamed MeanNormUpdate) | A real diag-Fisher implementation as a NEW primitive |

---

## 🧭 §5 — The Reconsideration (what actually went wrong)

1. **Budget went to measurement honesty, not capability.** Four audit
   rounds, four re-pins, five ruled-out PEPITA causes. All correct, all
   invisible outside the repo.
2. **The most exciting result (B4) is still a probe.** Per-layer FF with a
   real memory advantage and real LM learning has no library home.
3. **The biggest number (D17 seed-0) was paused mid-protocol** by the
   (correct) budget directive — it has been sitting unverified.
4. **The winning cells are known but uncomposed:** OrthoAdam has never run
   on LM; ePC×OrthoAdam has never run on LM; per-layer targets have never
   touched a transformer.

**Strategic correction:** build on confirmed wins; compose the winners;
verify the bombshell; give B4 a library home. Every session ends in a
pinned demo, a killed speculation, or a promoted probe.

---

## 🚀 §6 — The Opportunity Portfolio

### S1 — Push the deep-local frontier past depth 20
**Anchors:** D14 (depth 20, 0.92 with OrthoAdam), D15 (OrthoAdam moves the
wall), μPC×OrthoAdam substitution, SGD-alone 0.528.

- **Experiment:** depth sweep {20, 32, 50, 100} × {mupc+residual+OrthoAdam,
  mupc+jpc-Adam, jpc+OrthoAdam} on MNIST-quick (cheap, CPU). Pre-register:
  "the recipe reaches depth ≥ 32 at test ≥ 0.8."
- **The clever bit:** μPC's paper claims **zero-shot LR transfer across
  width and depth**. Probe it: tune at depth 8, run at depth 20/50
  unchanged. If it holds: "tune once, run anywhere" — a genuinely new
  capability.
- **Win:** "local learning scales to 100 layers with the right optimizer —
  and here's the recipe."

### S2 — The bombshell (§1)
Verification protocol above. This is priority zero: it's free-to-cheap
until step 3, and it either hands us the headline or teaches us exactly
where the baseline breaks.

### S3 — Build the per-layer local-contrastive credit (the flagship)
**Anchors:** B4 probe (all mechanisms confirmed), F5's pinned miss, A6's
EMA finding, rev-17's magnitude-is-information finding.

- **Build:** `local_contrastive` credit as a library primitive — per-layer
  recompute pattern (O(1) peak memory), per-layer stream normalization
  (load-bearing at depth ≥ 3), **EMA-based** magnitude normalization
  (instantaneous is pre-falsified).
- **Then:** compose with TransformerGeometry — per-layer targets on a
  transformer with no global CE. This is also SP4.
- **Win:** deep, local, O(1)-peak-memory LM that learns — Claim A + Claim B
  + competitive learning in one artifact. F5's ratchets flip.
- **Known boundary (pre-registered):** the depth wall exists in this class
  (0.827→0.764, d2→d4); the EMA rung is the untried repair.

### S4 — ψ-supervised adaptation: the thing backprop cannot do
**Anchors:** D22's contract finding, B1's closed-form ridge solver, F3's
realized primitives.

- **The clever speculation:** B1 solved feedback matrices in **closed
  form** — ridge regression on settled activities, no gradients, one shot.
  What else can be computed rather than trained? **A ψ that is set in
  closed form from a handful of examples — "LoRA without gradients."**
- **Build:** a ψ-law receiving NUDGED-phase settled activity
  (target-conditioned Hebbian outer / closed-form ridge). Pipeline note:
  `run_train_step` steps ψ on `credit.phases[0]` (always FREE at HEAD) —
  needs a `psi_phase` knob or a NUDGED-first credit.
- **Measure:** Task B acquisition with θ bitwise frozen; speed-vs-fine-tune
  (fine-tune acquires B 0.984 — that's the bar); A-retention by
  construction.
- **Win:** instant, forget-free adaptation — structurally impossible for
  backprop.

### Speculative plays (open-minded, cheap-probe-gated)

| Play | Anchor | The bet |
|---|---|---|
| **SP1 — compute-memory frontier** | B4's recompute beats bp's memory at depth ≥ 4 | Map WHERE local wins: per-layer recompute trades FLOPs for activation memory — decisive on memory-bound hardware. The resource-Pareto figure hardware people care about |
| **SP2 — optimizer-dominant learning** | OrthoAdam dominates every credit family, repairs Adam's depth collapse, partially substitutes μPC | How little credit suffices? Probe OrthoAdam with degraded/random/Hebbian pseudo-gradients. If it works: "the optimizer, not the credit rule, is the learning" |
| **SP3 — inference-time settling** | ePC free-equilibrium = feedforward bitwise; settling is cheap and iterative | ePC can KEEP SETTLING at inference for harder inputs — free test-time compute a bp-trained model cannot get. Probe: accuracy vs settle-steps at test time |
| **SP4 — global-free ff** | ff_hybrid works with ONE global term; B4 shows per-layer targets work | Replace the global term entirely (S3 on transformer). Zero global signals = absolute locality claim |
| **SP5 — non-autograd credit realization** | B1's ridge solver is autograd-free; ff_hybrid's autograd chain is the F5 cost | Hand-written closed-form updates → thermo-class O(1) memory. Flips F5 into the ~10× headline |
| **SP6 — OrthoAdam on LM (NEW)** | OrthoAdam dominates mlp/attention/lattice and the jpc regime; it has NEVER run on LM | Two cheap harness cells: `transformer/ff_hybrid/ortho_adam` and `mlp/epc_thermo/ortho_adam` at 2.5-min smoke. If OrthoAdam does to LM what it did to everything else, the bombshell arm upgrades for free |

---

## 📜 §7 — Carried queue (open items, none silently dropped)

| Item | Status | Lands as |
|---|---|---|
| D17 seeds 1–2 | Gated behind §1 steps 0–2 + per-batch approval | D17 demo |
| C1 contrastive-LM parity (epc_thermo 21 vs bp 9.9 gap) | Mechanical fallback iff D17 verdict lands >25% | C1 probe |
| Registered-scale P-axis campaign (matched-effective-lr protocol pinned) | QUEUED | D3 finding-grade claim |
| Reward-modulated STDP | OPEN — closes F2 | B5 |
| TransformerGeometry × ePC settle extension (bias-free block settle) | PREREQ for transformer PC-family cells | C1 prereq |
| P2 untried cells (inference-network ε, γ grid, w512, steps>H) | OPEN — only if contrastive path stalls | C1 |
| Demo API roadmap items 3–8 (vector export, captions, labels, graph polish, cookbook, D9/D11 exemplars) | Deferred — research first (user directive) | pull-based |
| Bias training option (`train_biases` flag) | Contract honesty, not performance (H2 delta 0.000) | as-touch |
| learned-B `feedback_lr` default 0.5 → 0.05 | Measured insane at 0.5 (‖B‖ collapses 10×/150 steps) | as-touch |
| Diverged-arm sentinel hygiene (exp(23.0) → NaN/flag) | Evidence hygiene | as-touch |
| Z3 flagship | Parked — its minimal kernel is S4; rides CP-6 findings | S4 first |

---

## 📦 §8 — Standing directives & lessons (carried, binding)

- `benchmark_results/` untracked, gitignored — never re-add.
- README never edited. Evidence lives in RESULTS.md + the gallery.
- Probe-first; pre-register predictions in the probe docstring; multi-seed
  before quoting; matched-step/lr controls before mechanism claims;
  capacity-matching on all comparisons; walltime printed never recorded.
- **Runs budget (tightened):** no multi-hour or unattended long runs;
  per-arm 10–20 min only with explicit per-batch approval; smoke-verify
  every registered arm at ~1-min first.
- **step_semantics discipline:** per-element-displacement updates
  (unit_rms/mean_norm/muon/ortho/adam family) get lrs on their OWN axis;
  `validate()` warns >0.05; never sweep a borrowed euclid grid (H1/H4).
- **Standing baseline caveats:** all bp baselines are weights-only (H2,
  delta 0.000) and (1−β)-scaled target-blended CE (H8, cos ≥0.99); β=1.0
  forbidden with autograd credit (config guard landed).
- R11.5.5a (no boundary verdict until known fixes applied) and TODO12b's
  defect-hunt posture apply to **optimistic** verdicts too: every big
  positive gets matched-step, multi-seed, defect-audit treatment.
- Canonical locality wording, scope-honest per the Claim A audit (§1).
- Fast/slow demo tiers; gallery pinning discipline (§3).

---

## 🎯 §9 — Sequencing

1. **§1 steps 0–1 (free/cheap):** bombshell regime reconciliation +
   per-step instrumentation. This session.
2. **SP6 smoke cells (cheap, parallel):** ff_hybrid×OrthoAdam and
   epc_thermo×OrthoAdam at 2.5 min — the cheapest possible bombshell
   upgrade.
3. **S1 depth sweep (CPU, 1–2 sessions):** the recipe is confirmed; find
   its real limit + zero-shot LR transfer.
4. **S3 build (the main build):** per-layer local-contrastive credit →
   transformer composition.
5. **S4 (parallel once S3's EMA rung is understood):** ψ-supervised /
   closed-form adaptation.
6. **§1 step 3 (gated):** D17 seeds 1–2 once the baseline is verified —
   per-batch approval.
7. Speculative plays as interstitial probes — one cheap probe, one
   pre-registered prediction, then promote or kill.

---

## 🏁 §10 — Completion criteria for TODO13

1. **Bombshell verdict rendered** — verified, matched-step, multi-seed,
   promoted (or honestly killed with the mechanism named).
2. **The deep frontier measured** — S1's sweep pinned; the recipe's real
   limit known; zero-shot LR transfer probed.
3. **local_contrastive landed** — library primitive, O(1)-peak-memory,
   learns LM without global CE; F5's ratchets flipped or the boundary named.
4. **ψ-supervised adaptation demonstrated** — exact ‖Δθ‖=0, Task B
   acquisition, A-retention, fine-tune comparison — or the closed-form
   boundary mapped.
5. **At least one speculative play promoted** to a D/F-table entry.
6. **No audit-only sessions** — every session ends in a pinned demo, a
   killed speculation, or a promoted probe.

The bar: **a result someone would cross a room to see.** The instrument is
honest, the map is drawn, the wins are real, and one of them is sitting in
`benchmark_results/d17_seed0.json` waiting to be verified. Time to build.
