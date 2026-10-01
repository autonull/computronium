Here is the **10-Minute Engine Check**: three smoke-tests that run on a single CPU core in under 10 minutes total. They bypass the heavy governance and benchmark infrastructure to directly test the three foundational hypotheses of the Computronium agenda.

If these three pass, the entire 6-axis trajectory is validated and you scale up. If they fail, you know exactly which root cause is structural versus engineering.

---

### Probe 1: The Depth Wall (Credit Normalization)
**The Hypothesis:** Equilibrium Propagation (ePC) fails at depth >10 because the credit signal attenuates ~4× per layer. This is an *unnormalized gain* problem, not a fundamental limit of local contrastive learning.
**The 2-Minute Experiment:**
1. Take the existing ePC harness.
2. Add a `credit_norm=rms` flag that normalizes the backward credit signal to unit RMS *per layer* before the update.
3. Run a depth sweep: 4, 8, 12, 20 layers on a tiny synthetic parity or XOR task.
* **🟢 GREEN (On Track):** The credit norm at layer 1 stops vanishing at depth 20, and accuracy stays > chance. **Conclusion:** The depth wall is an engineering problem. Scale up to μPC-style architectures.
* **🔴 RED (Pivot):** Credit still vanishes or accuracy collapses. **Conclusion:** Normalization isn't enough; the contrastive signal is structurally trapped. You must pivot immediately to **Learned Feedback Projections** (training the B matrix via autograd).

### Probe 2: The Width Wall (The Optimizer Crutch)
**The Hypothesis:** Local rules (PEPITA, FA) explode at high width and collapse at low width because credit *magnitude* is misaligned across layers. Global orthogonalizers (Muon) are just compensating for this. If we normalize magnitude *locally*, the crutch disappears.
**The 2-Minute Experiment:**
1. Implement `LocalAdamUpdate` (per-layer Adam, U-axis only—no new credit rules).
2. Run a PEPITA width sweep (w=32, 64, 128) using `LocalAdam` instead of Muon.
* **🟢 GREEN (On Track):** PEPITA at w=128 trains successfully without Muon. **Conclusion:** The credit *direction* is already correct; only magnitude was broken. Local rules can run on cheap, substrate-native optimizers (SGD/Adam).
* **🔴 RED (Pivot):** PEPITA still collapses at w=128. **Conclusion:** The credit *direction* is fundamentally wrong (fixed random B is uncorrelated with the feature space). You must pivot to **Adaptive/ Learned Feedback Alignment**.

### Probe 3: The P-Axis Thesis (Frozen-θ Adaptation)
**The Hypothesis:** Elevating the computational rule to a dynamical variable (ψ) yields a qualitatively different capability: adapting to new tasks *without* altering the base weights (θ).
**The 2-Minute Experiment:**
1. Take the L3.5 Algorithm Migration harness (Task A: cumulative sum → Task B: last symbol).
2. Meta-train θ, freeze it completely (`requires_grad_(False)`), and verify bitwise invariance.
3. Adapt *only* ψ for 50 steps on Task B.
* **🟢 GREEN (On Track):** ψ solves Task B at >95% accuracy while θ remains bitwise identical. **Conclusion:** The P-axis is a real computational primitive, not a software gimmick. The Z3 flagship and continual learning claims are viable.
* **🔴 RED (Pivot):** ψ fails to adapt, or θ leaks/updates. **Conclusion:** The joint transition operator is failing to isolate timescales. The P-axis is currently just a weight-preprocessor. You must halt Z3 and fix the `CoupledTransition` lifecycle boundaries.

---

### The Decision Matrix

Run these three probes today. Your next 6 months are dictated entirely by the combination of results:

| Probe 1 (Depth) | Probe 2 (Width) | Probe 3 (P-Axis) | Strategic Verdict | Next Move |
| :--- | :--- | :--- | :--- | :--- |
| 🟢 | 🟢 | 🟢 | **Full Validation.** The core engine works. | Execute the full AutoScientist campaigns and Z3 flagship. The ontology is real. |
| 🟢 | 🔴 | 🟢 | **Direction Failure.** Magnitude is fine, direction is wrong. | Drop Muon. Build **Learned Feedback Projections** (train B via local autoencoder loss). |
| 🔴 | 🟢 | 🟢 | **Signal Trapping.** Magnitude is fine, contrastive signal is trapped. | Abandon pure ePC. Pivot to **Predictive Targets** (local prediction error as credit). |
| 🟢 | 🟢 | 🔴 | **Timescale Leak.** Algorithms work, but joint architecture is broken. | Halt all science. Fix the `FrozenThetaAudit` and `CompositeState` lifecycle boundaries. |
| 🔴 | 🔴 | 🔴 | **Fundamental Mismatch.** Local learning as currently framed is a dead end. | Publish the negative results as a boundary paper. Pivot the lab entirely to **Architecture Co-Design** (Residual/Error Buses) rather than credit rules. |

**Why this works:** It costs ~10 minutes of compute and zero governance overhead, but it definitively separates *engineering bugs* (which the CEEC ledger and TODO26 kernel will eventually fix) from *scientific dead ends* (which no amount of ledger-keeping will rescue).


---

## EXECUTION RECORD (2026-09-14)

All three probes implemented and run in one session:
`scripts/probes/todo26b_engine_check.py` (~15 s CPU total, walltime
printed never recorded). Prior partial coverage consolidated rather
than re-run: A3/A4 (depth axis, MNIST), P4-A0 (width axis, LM),
D22 (P-axis, parity→last-symbol).

### Results

| Probe | Sub-result | Outcome |
| :--- | :--- | :--- |
| 1 Depth | credit_norm=rms lifts deep-hidden credit at depth 20 (hidden norms 2.1e-1..3.2e+1 vs 3.5e-10..5.6e-4 unnormalized) | 🟢 hidden-layer magnitude |
| 1 Depth | layer-1 (input-weight) credit at depth 20 under rms | 🔴 stays EXACTLY 0.00 — the 5-step settle never reaches layer 1 through 20 layers; `_apply_credit_norm` leaves zeros untouched, so rms cannot repair a zero |
| 1 Depth | accuracy > chance with normalized credit | 🔴 (parity harness chance even at depth 4; MNIST A3 walls at depth 8+ regardless) |
| 2 Width | PEPITA-family (LEMMA per-layer fixed-B, γ=0.05) + LocalAdam at w=32/64/128 | 🔴 chance at every width (0.489–0.507) |
| 3 P-Axis | θ bitwise frozen (SHA-256) | 🟢 invariance holds |
| 3 P-Axis | ψ-only 50 steps solves Task B >95% | 🔴 B 0.676→0.686 (noise), ‖ψ‖ inflates to 18.3 with no gain |

### Verdict: 🔴 / 🔴 / 🔴 (with P1's magnitude sub-result green)
"Fundamental Mismatch" branch — but NOT a publish-and-pivot-to-zero
outcome: the vanishing-credit magnitude repair works, and the
architecture co-design path the matrix prescribes is already measured
positive in-repo (D14 faithful regime + mupc residual regime train
depth 20+).

### Root causes (consolidated)
1. **P1**: normalized credit carries no usable contrastive signal —
   per-layer RMS rescales noise and trapped signal alike, and cannot
   repair an exactly-zero layer (the settle never reaches layer 1 at
   depth 20). The depth wall is credit-channel *structure*, not gain
   (A3/A5 confirmed from credit and activity sides).
2. **P2**: fixed random B is directionally uncorrelated with the
   feature space; no local optimizer (Adam included) rescues it. The
   boundary records close the entire family including the learned-B
   escape route (0.306 fixed-B w32, 0.214 fixed-B depth-8, 0.107
   learned-B, all × Muon — `LemmaCredit.IDENTITY_CARD`,
   `computronium/ontology/credit.py:2326`) — fixed-B PEPITA/LEMMA is
   boundary-locked.
3. **P3**: the ψ-step contract consumes no supervised/loss term
   (D22's missing-supervised-term disease). θ invariance is solid;
   the adaptation mechanism is not.

### Verification note (2026-09-14 recheck, second pass)
First pass found and fixed:
- Probe 2 originally wrapped `CreditAssignmentConfig.pepita()` in
  `LocalGoodnessCredit`, which silently runs the FF goodness path (the
  published-PEPITA config sets `local_objective="ff"`; the per-layer
  PEPITA-family gradient requires `local_objective="lemma"`). Corrected
  to the LEMMA fixed-B mode (γ=0.05) and re-run — verdict unchanged
  (chance at every width).
- Probe 1's first-pass verdict misread the depth-20 rms norms
  (min-hidden is 0.00, not 0.20 — the 2.1e-1 is the first hidden
  weight, the input weight is exactly zero). Corrected above.

Second pass found and fixed (attribution/precision only, no code
changes, no re-run needed):
- Probe 1 verdict said "the deepest layer's signal is exactly zero" —
  wrong end: the ZERO is the input weight (shallowest in propagation
  order); the deep layers have the largest norms. Also the rms range
  is 2.1e-1..3.2e+1 (not ..2.6e+1 — 2.6e+1 is an interior peak) and
  the unnormalized hidden range is 3.5e-10..5.6e-4 (not 4.7e-10).
- Probe 2 pivot line attributed 0.214–0.306 to the learned-B rung;
  those are the FIXED-B records (w32, depth-8 lattice). The learned-B
  record is 0.107 (LemmaCredit IDENTITY_CARD, credit.py:2326).

### New improvement opportunities
- **Supervised ψ term** (B5-adjacent, generalized to the P-axis): the
  single lever that would flip Probe 3. Design a plasticity law whose
  `step` reads a loss/target from `CompositeState.activity["y"]`.
- **Error-bus co-design probe** (matrix pivot): port the D14 faithful
  composition (residual + μPC-scale init + Adam) onto the tiny parity
  harness to give the engine check a 🟢-capable depth arm.
- **Credit-signal SNR instrument**: probe 1 showed norm-per-layer is
  readable; a directional-SNR readout (signal variance vs noise floor
  per layer) would separate "trapped" from "noisy" credit directly.

### Changes facilitating remaining work
- `CreditAssignmentConfig.thermodynamic_contrast(credit_norm=...)` and
  `_apply_credit_norm` are production-ready (rms/spectral/relative/
  beta_adaptive) — no new primitives needed for any normalization rung.
- `LocalAdamUpdate` ("local_adam") is exported and trainer-compatible.
- `RoutingPlasticity` + `CompositeState` + `_Context` stand-in form a
  reusable frozen-θ ψ harness (see the probe's `probe_3_p_axis`).
- The engine-check script is the template for future 3-probe round
  trips: ~15 s CPU, zero governance overhead.
