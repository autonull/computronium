# TODO13.md — Consolidated Findings: What Is Actually Known

> **Assembled 2026-09-07.** Distillation of everything durable from
> [TODO11.md](TODO11.md) (library-complete; D1–D16, F1–F3, OrthoAdam hunt,
> LM capability) and [TODO12.md](TODO12.md)/[TODO12b.md](TODO12b.md) (the
> credit-channel repair program + the defect hunt). This is the map of what
> we *know*, separated sharply from what we *suspect* and what we *need*.
> Every number below is quoted from a pinned demo record or a probe
> docstring at HEAD; nothing here is carried by corroboration alone
> (R11.5.3). Items are tagged: ✅ verified capability · 🔬 measured
> mechanism · ⚠️ open / unverified · 🪤 lesson that must not be re-learned.

---

## 0. The One-Paragraph Picture

Computronium's library is complete and honest at demo scale. The repair
program found that **every local-learning "wall" we measured was either a
credit-channel property with a landed lever, or an implementation/regime
artifact** — the jpc-faithful depth wall dissolved (D14), the "unit_rms
noise floor" was an lr mislabel (H1), the "Muon explosion" was an lr
overshoot (H4). What survives all audits is a single unifying diagnosis —
**credit fidelity decays through depth; backprop's exact-transpose Jacobian
is the cheat** — plus a concrete repair surface (normalization, learned
feedback, task coupling, regime faithfulness). The two live frontiers are
**B4's per-layer contrastive credit** (probed real, library unbuilt — the
one lever that can flip both the locality claim and the memory story) and
**D17's seed-0 LM headline** (single-seed, step-asymmetric, unverified).
The honest gap: **Claim B (physical advantage) is NOT demonstrated at
HEAD** — the O(1)-memory class exists but our star algorithm's autograd
realization pays backprop's costs.

---

## 1. Verified Capabilities (the quotable record)

| # | Capability | Headline numbers | Source |
|---|-----------|------------------|--------|
| **D13** | Local credit × Muon is real | FF×Muon **0.838±0.009** vs FF×Euclid 0.568±0.041 (5 seeds); **ff_hybrid×Muon 0.857±0.010**, rescues Euclid 0.568→0.798 | `test_demo_uaxis_muon_swap.py` |
| **D14** | Depth 20 trains under the jpc-faithful regime | μPC+β=10 test **0.69–0.83** vs default-init memorization (train 1.00/test ≤0.24); **mupc×OrthoAdam 0.920** mean; default×OrthoAdam 0.851 vs Adam 0.204 — the memorization corner largely rescued | `test_demo_jpc_faithful_depth.py` (slow) |
| **D15** | The U-axis moves the depth wall, capacity-matched | d16/w128: Euclid 0.114 (chance) / Adam 0.303 / Muon 0.834 / **OrthoAdam 0.878**; FF×Muon 0.930 ≥ BP×Muon 0.911 at d4/w256; **FF×OrthoAdam 0.947** (~119k params, best acc/param) | `test_demo_uaxis_depth_frontier.py` (slow) |
| **D16** | No update rule dominates the geometry map | OrthoAdam takes mlp 0.930 / attention 0.911 / lattice 0.924 (beats both parents); Muon keeps graph 0.433; Adam beats Muon on attention | `test_demo_uaxis_coverage.py` (slow) |
| **D18** | The optimizer crutch is dead for ePC at w32–64 | ePC×unit_rms **w64 32.5 / w32 42.5** while registered-lr Muon overshoots (101/192); ePC width-robust w32–256 under unit_rms | `test_demo_update_ladder.py` |
| **F3** | The P-axis Pareto instrument discriminates (realized primitives) | per-gate masks (std 0.081), settled-activity fast weights; retention orderings recorded at matched effective lr — **no P-axis mechanism claim is quotable** | `test_demo_paxis_pareto.py` |
| **F4** | The credit-channel failure map is live | all 8 failure modes in one figure; A4 spectral repair live (per-layer credit norms flattened to ~1.0 through depth 16) | `test_demo_credit_channel_map.py` |
| **LM** | A local-error rule trains a Transformer LM | transformer/ff_hybrid/muon **6.74 ppl at 2.5 min** vs bp/adam 5.82 (~15% behind, matched wall-clock); width-robust (14.7–16.0 across w32–256) | `lm_comparison.py` smoke cells |

---

## 2. The Unifying Diagnosis (survived every audit)

**One problem:** the credit signal loses fidelity as it propagates through
depth, and the loss compounds. Backprop preserves fidelity via the exact
transpose Jacobian; every local rule approximates it and leaks differently.

| Failure mode | The measured signature | Status of the repair |
|---|---|---|
| **Attenuating channel** (ePC) | ~4×/layer decay; exact 0.0 at layer 1 by depth 20 | A4 `credit_norm` spectral flattens norms to ~1.0; partial depth-8 lift (0.195 vs 0.113); faithful regime dissolves it |
| **Misaligned channel** (PEPITA) | fixed random B uncorrelated with feature space; bidirectional width fragility | 🅿️ PARKED — five causes ruled out; learned-B did not stop the runaway; revival needs the weight-trajectory probe or a faithful realization |
| **Unnormalized gain** (width fragility) | per-layer activity-scale compounding ∝ width (ePC w32 std→2028; pepita 0.35→0.05) | unit_rms kills it for ePC; ff_hybrid immune (autograd-scaled readout term) |
| **Disconnected channel** (pure FF) | norm-contrast is error-blind; flat at chance on LM | `readout_error=True` (the hybrid) fixes it |
| **Blocked channel** (sPC) | layered settle traps the nudge; hidden credit norms exactly 0.00 | ePC error-reparameterization fixes it (D12) |
| **Train/inference objective gap** (P2) | corrected forward fits by construction; free settle at chance | frozen-error retired for LM; contrastive (epc_thermo×Muon 2.81 train) is the working instrument |
| **Absent channel** (naive STDP/Hebbian) | correlation only, no task credit; subspace collapse survives homeostasis | reward-modulated STDP is the missing term (parked) |
| **Low-rank credit** (optimizer crutch) | ePC gradient 400× too small for Euclid | dead at matched lr for width; Muon's residual value is **depth-only** |

---

## 3. Mechanism Findings (the science that actually landed)

1. 🔬 **Muon's advantage is direction quality, not lr scale.** At matched
   effective step, ff_hybrid: Muon 13.84 vs Euclid 30.26 ppl. ePC's ÷β
   gradient is so small Euclid cannot deliver a usable step at any finite
   lr (400× too small at stable lr; matched lr ≈134 explodes). Muon is
   genuinely load-bearing for the PC family on LM.
2. 🔬 **OrthoAdam's lift is momentum-orthogonalization, not whitening.**
   Newton–Schulz preserves OrthoAdam everywhere (rescale-to-Adam-magnitude
   dominates) but collapses FF×Muon (whose update IS the raw polar factor).
   Adam's second-moment normalization is itself depth-fragile;
   orthogonalizing its momentum repairs it.
3. 🔬 **Momentum-orthogonalization and depth-scaled init are partially
   interchangeable repairs of the same depth pathology** — under OrthoAdam
   the μPC-vs-default gap narrows ≈0.58 → ≈0.07, μPC still leads.
4. 🔬 **Levers do not naively compose.** credit_norm harms the faithful
   regime (ε is *dynamics* there, injected into the forward); instantaneous
   normalization destroys contrastive objectives (gradient magnitude carries
   the softplus-gating information). Credit_norm is a simple-regime tool.
5. 🔬 **ff_hybrid at HEAD is output-pseudo-loss backprop.** The scope audit
   (f5b): under InstantaneousDynamics the nudged pass differs from free ONLY
   at the output act; every hidden goodness term is exactly zero; the
   closed-form detached variant gets exactly 0 hidden gradient (chance 0.104
   vs autograd 0.778). **The autograd chain IS the learning signal.**
6. 🔬 **The depth wall generalizes to three algorithm classes** (ePC,
   ff_hybrid, and per-layer targets) — attenuation is a credit-channel
   property, not an optimizer property (A3: unit_rms walls at depth 8+).
7. 🔬 **Routing's retention advantage is effective-lr alone** (F3 matched-lr
   pilot); fast-weights' deficit is real. No P-axis mechanism claim is
   quotable until lr-matched registered campaigns land.
8. 🔬 **Attention, not supervision density, is the transformer's lever**
   (P1b): zero-block dense supervision saturates at unigram (~12.2 ppl) at
   ANY capacity; local credit tracks bp within ~14% on the dense path.
9. 🔬 **ψ-only adaptation is impossible at HEAD** (D22): no landed ψ law
   consumes a task-loss signal. The exact-θ-invariance mechanism is trivial
   without acquisition. Fine-tune acquires B 0.984 at real forgetting cost.
10. 🔬 **Claim B is not realized at HEAD** (F5): ff_hybrid stores ≥
    backprop (177.5 vs 143.5 KiB @d16) and costs ~1.3× FLOPs. The
    O(1)-memory class is real (thermo saves exactly 0 at every depth).

---

## 4. The Defect Hunt (what we learned about our own measurements)

TODO12b ran 8 pre-registered suspicion probes against every pessimistic
verdict. **4 CONFIRMED, 3 REFUTED, 1 partial.** The meta-finding: negative
verdicts were wrong exactly where a step-size/throughput semantics lurked
unexamined — and right where the contract was inspected directly.

| # | Verdict | Durable fact |
|---|---------|--------------|
| **H1** | CONFIRMED | unit_rms `step_size` is **per-element displacement**; the "convergence noise floor" was an lr mislabel. At its own lr (1e-3) unit_rms **beats euclid** (0.900 vs 0.878) |
| **H2** | CONFIRMED | Biases never train in ANY arm (weights-only backprop everywhere); impact at demo scale 0.000 — caveat, not re-run |
| **H4** | CONFIRMED | Muon lr 0.01 on ePC w64 is **worse than chance** (overshoot collapse, not divergence); trains at 0.003. D18's "crutch dead" re-scoped to lr-matched footing |
| **H8** | CONFIRMED | bp's nudged loss is target-blended CE ((1−β)-scaled); **β=1.0 is an exactly-zero pseudo-gradient** (forbidden, locked) |
| **H5** | REFUTED | F5's instrument is sound (packed count = 3L−1 analytic); bonus: local-ff packs ~3× bp (memory-angle corroboration of Claim A scope) |
| **H6** | REFUTED | PEPITA's historical ‖W_out‖ growth was the pre-p5 fixed-B channel; at HEAD the update path is exactly lr-bounded |
| **H7** | REFUTED | D22's routing-mode flip is a bitwise no-op; the miss is defect-audited |
| **R5** | structural fix | `step_semantics` property + `validate()` lr-sanity/β=1.0 guards — the lr-semantics defect class is now impossible to repeat |

🪤 **Standing rule extracted:** before any verdict, audit the instrument
against the claim's own terms — lr axis, step semantics, throughput
accounting, and regime faithfulness. A test proves the code behaves as
written, never that the algorithm is doomed (R11.5.5a).

---

## 5. The Per-Layer Frontier (B4 — the highest-leverage open lever)

The rev 16/17 probes made per-layer contrastive FF the single most
important unbuilt thing in the program:

- ✅ **Nonzero hidden credit with NO cross-layer sweep** (each layer's own
  local backward graph) — the true-locality mechanism exists.
- ✅ **Per-layer peak memory beats backprop's whole graph at depth ≥ 4**
  (268.8 vs 569.3 KiB) — this flips F5's pinned miss direction.
- ✅ **Learns LM without ANY readout CE**: top-1 15.8/15.6/16.0% vs unigram
  9.4%, chance 1.5%; leak controls pass (untrained 1.7%, shuffled 5.3%).
- ⚠️ **Depth wall present in this class too** (0.827 → 0.764, d2→d4) —
  "per-layer targets fix depth" is pre-falsified.
- ⚠️ **A4 credit_norm does NOT compose** (instantaneous normalization
  collapses learning at every depth — magnitude carries information).
- ⚠️ **Memory advantage has a depth floor** (at depth 2 the input layer's
  graph ≈ bp's whole graph); F5 rerun must sweep depth 4/8/16.
- 🔧 **The untried rung:** momentum-EMA normalizer (the canonical magnitude
  family per A6) for the per-layer goodness gradient.
- 🔧 **Library pull:** a `local_contrastive`/`local_predictive` credit with
  the no-grad recompute pattern (detached-carry keeps all graphs alive and
  is worse than bp) + per-layer stream normalization (load-bearing at
  depth 3+, shares A5's vocabulary).

---

## 6. The Honest Gaps (what we do NOT know)

1. ⚠️ **D17 seed-0 is unverified.** transformer/ff_hybrid/muon 5.05 (2,200
   steps) vs bp/adam 27.55 (15,217 steps) at 15 min — a ~7× throughput
   asymmetry and single seed. The verdict band (<15% / 15–25% / >25%) is
   NOT adjudicable. Needs matched-step re-pin from existing curves +
   per-step cost instrumentation + seeds 1–2 (~90 min, user-gated).
2. ⚠️ **Claim A's scope:** the canonical locality wording holds verbatim
   only for requires_autograd=False credits (thermo) and PEPITA-style
   closed-form routing. ff_hybrid is excluded until per-layer nudged passes
   exist. Never "fully local"; never "local learning beats backprop."
3. ⚠️ **The P-axis campaign at registered scale** (matched-effective-lr
   protocol pinned) is still the first finding-grade P-axis claim.
4. ⚠️ **C1 (contrastive LM parity):** epc_thermo×Muon 2.81 train / ~21 val
   vs bp 9.9 — the gap to parity is open; transformer×ePC needs a
   bias-free settle extension first.
5. ⚠️ **Reward-modulated STDP / supervised ψ term** — the missing primitive
   behind both F2 and D22.

---

## 7. Standing Doctrine (binding, carried into TODO13)

- **Prime directive:** nothing is claimed that the suite does not re-show
  at HEAD. The demo suite is the proof; probes precede promotions.
- **Canonical claim wording:** "forward-local credit with a single readout
  supervision term — no backward sweep through the hidden layers" — scoped
  per the Claim A audit. Claim A (locality) and Claim B (physical advantage)
  always ride separate lines.
- **Probe-first discipline:** pre-register the prediction in the probe
  docstring; reuse existing instruments (P4 harness, F1 harness,
  `lm_comparison.py`); promote only on variance-aware multi-seed evidence.
- **Matched-step protocol (P3):** every optimizer comparison at matched
  effective step; retention measured at matched effective lr per arm.
- **lr on the rule's own axis** (`step_semantics`): never sweep a
  per-element rule on euclid's grid.
- **Walltime printed, never recorded**; fixed-step arms for gallery pins.
- **D8 seeding:** seed before every loader/data draw, in every probe.
- **Budget:** gradual scaling, ~10–20 min/arm max without explicit
  approval; no multi-hour unattended runs.
- **Scope honesty:** demo-scale speaks for demo scale; registered claims
  live in the research track.

---

## 8. The Next Moves (ordered by leverage — the TODO13 agenda)

| # | Move | Why it's next | Cost / gate |
|---|------|---------------|-------------|
| **1** | **Verify D17 seed-0** — matched-step re-pin from existing curves + per-step cost instrumentation (the 7× throughput asymmetry); resume seeds 1–2 only after | The headline candidate is also the most suspicious number; promote-or-kill before anything builds on it | Cheap (analysis) → user-gated GPU |
| **2** | **B4 library pull** — `local_contrastive` credit (no-grad recompute pattern + per-layer stream normalization), probe-first with the momentum-EMA rung | The one lever that flips F5 and repairs Claim A — turns the story coherent instead of poster-only | ~1 session; property-suite gate (credit semantics) |
| **3** | **F5 rerun** on the B4 credit — pre-register the schema extension first, sweep depth 4/8/16, report plain + ortho variants | Converts the capstone miss into the memory/energy headline if the recompute pattern holds | probe → demo |
| **4** | **Depth-wall frontier** — momentum-EMA rung for the per-layer class, else C1 (contrastive LM parity) or error buses (C2) | The wall generalizes to three classes; it's the genuine scientific content | research track |
| **5** | **Registered-scale P-axis campaign** with matched-lr protocol pinned | The first finding-grade plasticity claim; the F3 instrument is ready | campaign YAML + GPU |
| **6** | **Supervised ψ term** (B5-generalization) when a neuromorphic/adaptive deliverable needs it | Unblocks both F2-close and D22 revival | pull-based |

**The through-line:** D17 verified is the poster; B4 realized is the spine;
the depth wall is the science. Claim B becomes real only through a
non-autograd local-rule realization — everything else is rearranging the
measurement of backprop's costs.

---

> *This document is the distilled record. It claims nothing the pinned
> demos and probe docstrings do not re-show; it defers everything the
> audits have not closed. When a number here and a live record disagree,
> the record wins.*
