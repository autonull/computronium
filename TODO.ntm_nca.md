# TODO.ntm_nca.md — W8: Local Credit on Stateful / Emergent Computers

> **Opened 2026-09-07.** Workstream designation: **W8** (TODO14 §14's
> substrate/stateful slot; "W5" in the original draft collided with
> TODO14's existing W5 = depth-50).
>
> **Thesis alignment**: these are NOT architecture ports. NCA and NTM
> exist here as **adversarial testbeds for the central TODO14 claim** —
> credit × update interaction I(C,U) — in the two regimes the project
> has never touched: *iterative local dynamics* (NCA) and *differentiable
> external memory* (NTM).

---

## §0 — The Central Question

> **How much can a completely local learning rule accomplish when the
> computation itself is also local and recurrent?**

And its memory analogue:

> **Can local credit train a controller that writes, reads, and retrieves
> from external memory — without backpropagating through the entire
> computational history?**

Both are instruments for I(C,U). The project's strongest law — weak
credit lives or dies by the update rule — has been measured on MLP,
transformer, and (partially) lattice. NCA adds **thousands of local
learning sites iterated over a long rollout**; NTM adds **credit through
an addressing mechanism**. If the law generalizes, it is a law; if it
does not, the geometry boundary is the result.

### The W0 transfer (why this is timely)

TODO14 Session 2–4 established a concrete instrument and a concrete
mechanism on the transformer:

- **Instrument**: per-layer goodness contrast r_i = ‖G+−G−‖/‖G+‖, raw
  pre-EMA gradient RMS, and gate-saturation logging
  (`scripts/probes/w0_contrast_track.py` pattern).
- **Mechanism**: per-layer sign inversions of the goodness contrast
  (ΔG < −θ) cause softplus-gate shutdown; acting on inverted layers is
  harmful (hinge falsified); freezing them only partially mitigates.

An NCA applies one update at many sites over many steps — the single
best place to find out whether **contrast sign inversion under local
goodness is a general property of iterative local dynamics** or a
transformer artifact. That question alone justifies W8.1.

---

## §1 — Strategy: probe first, ontology second

The codebase has no NCA or NTM. The nearest relatives are the tile
lattice (`computronium/ontology/_tile_blocks.py`, spatial tiles with
local credit) and the transformer geometry (per-layer recomputed
contrast in `LocalContrastiveCredit._tf_layer_grad`).

**Two integration routes; deliberate order:**

1. **Standalone probe** (`scripts/probes/w8_nca_local.py`): torch model
   + `compose_system`-assembled credit/update objects where convenient,
   plain autograd for the BPTT control. Gets a four-cell result in one
   session. This mirrors how W0–W6 all ran; **default route**.
2. **Ontology promotion** (only if W8.1 is alive): new
   `GeometryConfig.nca(...)` + `NcaGeometry`, crossed with existing
   `CreditAssignment` / `ParameterUpdate` via
   `core/system_trainer/factory.compose_system_from_configs`. Pays the
   AGENTS.md new-primitive checklist (registry, wiring lockstep lock,
   `SystemConfig.validate` branches, `__all__`/`_LAZY` surfaces).
   Do not pay this cost before the experiment earns it.

### Key ontology mapping facts (design constraints)

**REVISED after the first execution passes (§11)** — the per-cell
reshape into `local_contrastive` machinery was NOT the construction
used; the W8.1 probe runs probe-local credit (per-layer goodness
contrast on the shared cell MLP, per the local_contrastive RECIPE:
softplus gate θ, EMA-RMS normalization, readout on raw CE) crossed
with the REAL ontology update rules (`EuclideanUpdate` /
`RiemannianOrthogonalUpdate` — the U axis is shipped code, not a
reimplementation). Ontology promotion therefore requires an
`NcaGeometry` whose settle/credit seam accepts this per-cell credit —
the prerequisite evidence is now partially in hand (harness landed;
verdict open).

Constraints learned the hard way (each verified; see §11 for the full
signatures):

- **Additive state channels must live under MSE, never CE** (CE on
  clamped additive state has a gradient-free confidently-wrong
  attractor) and the state ceiling must sit ABOVE the target range
  (`STATE_MAX = 10`) or every channel pins and argmax tie-breaks.
- **Balanced (inverse-frequency) per-cell loss is mandatory** —
  ~87%-background sprites have an all-background trivial attractor.
- **`grad_clip` must be 0** on the update rules for rollout-trained
  cells (the fixed-norm-jump lr-invariance signature), with the
  substrate state bound as the explosion guard.
- BPTT quality is budget-limited at the first-pass episode counts;
  per-step loss averaging (32× denser credit) is the designated
  unblock lever.
- `sequential_lr` / `set_update_rule` wiring (TODO14 §8) uses
  `actual_parameter_displacement` snapshot-replay — with a **shared**
  cell weight the pseudo-gradients from all sites must be **aggregated
  (summed) before the optimizer step**; Muon then sees one matrix. With
  **unshared per-cell weights** every site is its own learning problem
  (the "thousands of local sites" regime, at probe scale). Probe both;
  shared-first is the cheaper parameter count, unshared-first is the
  cleaner locality claim. **Decision: W8.1 uses a SHARED cell MLP**
  (Mordvintsev-style, one small weight set) with summed
  pseudo-gradients; unshared is a W8.4 axis.
- `InstantaneousDynamics.settle` semantics: the NCA rollout is a
  sequence of settle→update cycles; O(1)-memory local credit applies
  per step, BPTT control truncates at horizon H (the truncation horizon
  is a control axis, not a confound — log it).
- Optimizer axis comes free: `ParameterUpdateConfig.euclidean /
  riemannian_orthogonal / ortho_adam` (the D16-calibrated settings are
  the starting LRs; re-screen 300 steps before trusting any cell).

---

## §2 — W8.1: Minimal NCA probe (the first experiment)

### Task

Pattern regeneration (Mordvintsev-style, minimal): 16×16 grid, 4
state channels + 1 target/label channel, per-cell shared MLP
(neighborhood concat → hidden → Δstate), Adam-free init (unit-RMS style
consistent with mupc practice), seed cell → grow → damage → regenerate.

### Arms (exactly four cells — no more)

| arm | credit | update |
| --- | ------ | ------ |
| 1 (control) | BPTT (autograd through rollout, MSE/CE to target) | euclid, tuned once |
| 2 (control) | BPTT | muon, screened |
| 3 | local_contrastive (per-cell reshaping, §1) | euclid |
| 4 | local_contrastive | muon |

### Pre-registered predictions (write results BEFORE running)

- **P1 (rollout-length law)**: BPTT quality degrades or explodes with
  rollout length / truncation horizon tradeoff; local_contrastive is
  rollout-length-flat (O(1) memory, per-step credit) but possibly
  lower-ceilinged. Falsified → the temporal-credit objection stands
  even here; that is a boundary worth having.
- **P2 (I(C,U) replication)**: local × muon > local × euclid by a
  materially larger margin than BPTT × muon > BPTT × euclid (the SP2/W1
  signature in a new regime). Falsified → the law is geometry-bound;
  lattice becomes the deciding third geometry before any Tier D claim.
- **P3 (inversion generality)**: per-site contrast sign inversions
  (ΔG < −θ) appear in the NCA as they did in the transformer
  (w0_contrast_track instrument, per-site instead of per-layer), and
  correlate with regeneration failure loci. Falsified → the W0
  mechanism is transformer-specific; W0's boundary framing weakens.
- **P4 (sanity)**: local_contrastive's label channel actually reaches
  the cells (§17 signal-integrity: the injection contrast is measured,
  not assumed — the w0_gain_diagnostic lesson).

### Budget

Grid 16×16, rollout ≤ 64 steps, few hundred training iterations,
CPU-scale (~minutes/cell). Walltime printed, never recorded. Probe
lives in `scripts/probes/w8_nca_local.py` with a static `_ARMS` table,
`_train_arm`/`_probe_arm` extracted (the demo-test pattern if it ever
becomes a demo).

### Promotion gates (§20 discipline)

Any positive cell: 3 seeds, matched-step control, defect audit against
TODO14 §17 (signal/state/update/measurement integrity — the
feedback-scale-inert trap from W1 applies: verify the label channel is
live by a scale-identity check), fixed-step reproduction. Only then
does "local NCA learns regeneration" exist.

---

## §3 — W8.2: NCA optimizer interaction (after W8.1)

The W1 ladder transplanted: local_contrastive × {euclid, muon,
ortho_adam} plus deliberately degraded pseudo-gradients (shuffle a
fraction of sites' credit, scale the label channel down a decade) —
find the optimizer-dominance boundary on iterative dynamics.

The interesting question is whether the **W1 recovery profile is an
optimizer fingerprint here too** (muon thresholdless, ortho sharp-edged
on MLP). If the fingerprint reproduces on a third geometry, the
predictive-I(C,U) claim (Flagship C / Tier D) has MLP + transformer
(qualitative) + NCA — the lattice cell (TODO14 next-menu) closes the
set.

---

## §4 — W8.3: Long-horizon / damage experiments

- Regeneration fidelity vs rollout length (the P1 curve, measured).
- Damage size sweep (how much of the organism can die before
  regeneration fails — per credit type).
- Persistent-memory variant: encode, perturb, recover (the cheap
  "NCA as memory" probe; no new machinery).

This is the direct attack on the temporal-credit objection: the claim
to test is not "local matches BPTT" but **"local credit's advantage
grows with rollout length"** — the one place O(1)-memory learning
should structurally win.

---

## §5 — W8.4: Shared vs unshared weights

- Shared cell MLP (W8.1 default): one parameter set, summed
  pseudo-gradients — tests whether Muon's geometry rescue survives
  gradient aggregation across sites.
- Unshared per-cell weights: thousands of independent local learning
  problems — the max-locality claim; expect slower, noisier, but the
  cleanest "local learning sites" story.
- Weight-sharing as an axis has never been touched by the I(C,U)
  framework anywhere in the repo; whichever way it breaks is new.

---

## §6 — NTM (W8.5): the memory stress test — OPENED, first cell POSITIVE

**Status revision (2026-09-07): the §6 gate was consciously overridden
by user directive and the first cell EXECUTED — with a positive result
(§11.1: BPTT control solves copy 1.000; zero-history local
factorization 0.708 and climbing). NTM is no longer conditional; it is
the WORKSTREAM'S CHEAPEST PROMOTION TARGET (~2.5 min/cell) and the
ontological breadth case the user asked for (demonstrate usefulness →
promote into the Ontology).**

Minimal NTM (deliberately small):

```text
input → controller → {read head, write head} → external memory → output
```

- Tasks in order: **copy** (first serious "can local credit learn an
  algorithm?" challenge) → repeat-copy → associative recall.
- Local factorization (the interesting version): controller, key
  generation, addressing, gates, and output projection trained with
  local targets — **never the global loss back through the
  computational history**. The per-module local-target pattern is
  b4_per_layer_ff / per-layer-LM heritage.
- BPTT control retained at every cell (gold standard, §9).
- The addressing mechanism is the novel credit question: goodness
  contrast through a soft attention read is a different geometry than
  anything measured (attention in_proj was the transformer's first
  layer to invert — W0.3's open question may answer itself here).

**W8.5 DNC** — only if NTM produces a meaningful result. Dynamic
allocation + temporal links are exactly the machinery local credit is
least likely to survive; that is the point, but it is last.

---

## §7 — The combined moonshot (W8.6)

Local-credit Neural Cellular Computer: NCA-like local controller + NTM
external memory. Test whether **useful computation emerges from local
learning in a system with both distributed state and persistent
external memory**. Explicitly not scheduled; it is the direction W8.1's
result either earns or kills.

---

## §8 — Realistic first-pass coverage matrix

| Architecture | BP/BPTT | mupc init | local_contrastive | Hebbian/trace | degenerate credit |
| ------------ | :-----: | :-------: | :---------------: | :-----------: | :---------------: |
| MLP          |    ✓    |     ✓     |         ✓         |       ✓       |         ✓         |
| Transformer  |    ✓    |     ✓     |         ✓         |       —       |         —         |
| Lattice/tile |    ✓    |     ✓     |      partial      |       ✓       | contract-inert (§ TODO14 S7) |
| NCA          | ✓ 1.000 (distill+ft) |     —     |     ✓ 1.000 3-seed |       —       |         —         |
| NTM          | ✓ 1.000 3-seed |     —     |    ✓ ~0.69 3-seed plateau |       —       |         —         |
| DNC          | W8.5+   |     —     |       W8.5+       |       —       |        —          |

(NCA row = §11.5 VERDICT: local fg 1.000 on 3 seeds, rollout-flat,
BPTT control diverges at euclid/seed-2 while local is stable; NTM row =
§11.2 promotion round: 3 seeds, fresh-draw eval, ~0.69 plateau.)

Do not fill this table for its own sake — each ✓ must be a pre-registered
cell under §2's discipline.

---

## §9 — Non-negotiables (inherited from TODO14)

1. **BPTT gold-standard control at every cell.** The objective is to
   find where local credit genuinely breaks, not to flatter it.
2. **§19 probe rules**: question, mechanism, prediction, control,
   budget, metric, falsification criterion — written before execution.
3. **§17 defect-hunt protocol** before any negative result graduates to
   a boundary — including the W1 lesson: verify the credit channel is
   actually live (a silently inert label/feedback channel produces
   byte-identical-to-ff numbers; check for them).
4. **§1 status discipline**: Promoted / Open / Reopened / Boundary. A
   falsification is not a boundary until the protocol has run.
5. Optimizer axis is never "SGD only" — the project's own history
   (SP2, D17, W0) makes an untested matrix rule an uncontrolled
   negative.

---

## §10 — Priority order (REVISED 2026-09-08, post-§11.2/§11.3)

1. **W8.1 promotion decision** — the evidence is in (§11.5): local
   credit solves the growing NCA (fg 1.000, 3 seeds, rollout-flat) and
   both promotion criteria are met. If confirmed, pay the AGENTS.md
   new-primitive checklist for an `NcaGeometry` (registry row, config
   classmethod, wiring lockstep lock, `SystemConfig.validate` branch,
   export surfaces) — the distill-init + zero-history-credit recipe in
   `w8_nca_local.py` REV r7 is the reference implementation.
2. **W8.5 writer-surrogate redesign (now the decisive NTM task)** —
   the 3-seed muon extension washed out (§11.6: ~0.7 for adam AND
   muon); the plateau is writer-capacity-limited. Replace the
   task-shaped content-code surrogate with expected-content MSE under
   the writer's own addressing distribution.
3. **W8.2 full screen** — {euclid, muon, ortho_adam} × {bptt, local} ×
   lr on seed-2-style hard cases; test the §11.6 theory candidate
   (local credit rejects per-coordinate normalization: adam-family
   wobbles, magnitude-annealing euclid and direction-only muon don't).
   Keep cells SHORT (300 eps) — ortho_adam is slow (SVD per step).
4. **W8.3 damage curves — NEEDS A LABEL-FREE VARIANT FIRST** (§11.7:
   with the label channel injected, damage regeneration is a
   near-tautology — k=16 full-grid zeroing regenerates perfectly
   because every cell independently knows its target). The informative
   damage experiment requires removing the label channel so cells must
   infer the pattern from neighbors (true autonomous growth);
   regeneration from damage is then non-trivial.
5. **W8.5 writer-surrogate improvement** — the local plateau at ~0.69
   is writer-capacity-limited (§11.2 finding 2); a less task-shaped
   write-local rule (e.g., expected-content MSE under the writer's own
   addressing) is the lever toward ≥0.85 and a clean promotion case.
6. **W8.4 shared vs unshared weights.**
7. **W8.6** — combined cellular computer (moonshot; unscheduled).

**Ontology promotion criteria (user goal: breadth via demonstrated
usefulness)**: a primitive earns promotion when (i) its task shows a
promoted positive per §20 discipline (3 seeds, fresh-draw eval,
matched control, reproduction), AND (ii) at least one non-Adam update
rule composes with it. Promotion then pays the full AGENTS.md
checklist (registry, config classmethod, wiring lockstep lock,
validate branches, export surfaces). NTM is closest; NCA follows its
verdict.

**Relative to the TODO14 queue**: W8.1 is a legitimate parallel track —
it reuses the W0 instrument, needs no ontology surgery, and answers a
generality question (P3) that TODO14's W0 boundary work actively needs.
TODO14's own short-cell menu (W0.3 ablation, W1 edge rungs, lattice
I(C,U)) remains the default when a session is short; W8.1 is the pick
when a full session is available for a new arc.

The target end state, in one sentence:

> *Here is the maximum temporal/spatial complexity local credit can
> learn, here is the optimizer dependence, here is where it fails — and
> here is the regime where it structurally beats BPTT.*

---

## §11 — W8.1 session record (2026-09-07, first pass — OPEN, not yet executed to a verdict)

**Status: the W8.1 harness is LANDED and instrumented
(`scripts/probes/w8_nca_local.py`: 4 pre-registered arms, ontology
update rules as the real U axis, P3 inversion-rate + P4 injection-
contrast instrumentation, P1 horizon sweep). The four-cell verdict is
NOT in. The first passes were consumed by three task-design
pathologies, each found via its measurement signature and fixed; the
remaining blocker is that the fixed task still trains toward the
all-background attractor within the tested budget, so P1–P4 are
UNRESOLVED.**

### Pathologies found and fixed (each is a reusable §17-class finding)

1. **Class-imbalance trivial attractor**: sprites are ~87% background;
   unweighted CE converges to all-background (CE = ln 4 exactly,
   fg-acc 0). Fixed: inverse-frequency-weighted CE (`_weighted_ce`).
2. **Global-clip lr-invariance**: BPTT screens were byte-identical
   across lr 0.01→1.0 — the §17 update-integrity signature (grad_clip
   1.0 default makes every step a fixed-norm jump). Fixed: grad_clip 0
   on both rules (substrate state bound replaces the explosion guard).
3. **Clamp-ceiling saturation attractor**: with the state ceiling at
   the target max (3.0), additive Δ dynamics saturate every channel at
   the ceiling; argmax tie-breaks to channel 0 and CE floors at ln 4
   with zero gradient. Fixed: STATE_MAX = 10 (above target range) and
   BPTT loss switched to one-hot MSE (plan §2 "MSE/CE"); CE on clamped
   additive state has a gradient-free confidently-wrong attractor
   (softmax gradient ~e^-gap) — MSE keeps a linear error signal.

### Remaining blocker (next session's first move)

Even with MSE + STATE_MAX = 10, the smoke did not show fg learning
within 120 episodes; the last smoke output was ambiguous (identical to
the pre-MSE numbers — verify the patched module actually executed
before anything else; rule out a stale-process/cache artifact).
Candidate next levers, in order: (a) verify the MSE path is live by
printing the bptt loss per episode for 20 eps (it should descend); (b)
per-step loss averaging instead of final-step-only (32× denser credit);
(c) 600+ episodes or per-step BPTT updates; (d) if still flat, suspect
the mask stochasticity + single-sample-per-episode noise floor and use
a fixed mask schedule. The harness itself passed all gates (ruff
clean, pyright 0 errors) and every arm path is exercised end-to-end.

### §11.1 — W8.5 first cell EXECUTED (2026-09-07): BPTT control SOLVES copy; zero-history local factorization reaches 0.71

Probe: `scripts/probes/w8_ntm_copy.py` (minimal NTM: LSTM-32 controller,
16x8 content-addressed memory, erase+add write; copy task L=6, 13
timesteps; adam 1e-3, batch 16, 3000 steps, ~2.5 min/cell CPU).
Pre-registered Q1/Q2 in the docstring; opened early by user directive
(the §6 gate consciously overridden).

| arm                        | copy-acc @3000 | note |
| -------------------------- | -------------- | ---- |
| bptt x adam (control)      | **1.000**      | loss 0.046; >0.9 by step 1500 |
| local factorized x adam    | **0.708** (peak 0.708, still climbing) | ZERO history-backprop: LSTM state and memory detached every timestep |

1. **Q1 MET**: the gold-standard BPTT control learns copy at CPU probe
   budget (1.000 in 3000 steps / 2.5 min). The NTM cell is REAL — every
   §9 non-negotiable is satisfiable here.
2. **Q2 first answer**: the zero-history local factorization (per-step
   CE for controller/out, read-head CE with h detached, writer on a
   content-code MSE + addressing-KL toward the least-similar slot)
   reaches 0.71 with no gradient ever crossing a timestep boundary —
   far above chance (0.5) and still climbing at cutoff. The addressing
   mechanism does NOT need backprop-through-time to become useful.
   This is the first positive local-credit result on external memory.
3. Honest caveats: single seed, batch-16 training bits (eval on the
   same generator draw — a fixed-batch control, promotion requires
   fresh-draw eval + 3 seeds); local arm peak may be budget-limited
   (curve still rising at 3000). The writer addressing surrogate is
   task-shaped (bit code in channels 0-1); a general write rule is the
   open design question.
4. Promotion path (§20): 3 seeds + fresh-draw eval + matched-step
   control are cheap here (~2.5 min/cell); then the interesting cell is
   local x muon (the I(C,U) axis — muon on the per-module pseudo-grads).

---

## §11.2 — W8.5 promotion round EXECUTED (2026-09-08): local factorization
seed- and fresh-draw-robust at ~0.69 plateau; muon composes but does NOT beat adam

Probe `scripts/probes/w8_ntm_copy.py` (REV 2026-09-08-r3: added
`local-muon` arm — `_Muon` optimizer wrapping the ontology's shipped
`newton_schulz5` kernel on 2D params, plain SGD on biases/`beta`;
`loss.detach()` in prints). Full log: `logs/w8_promotion.log`.

| arm | steps | seed | copy-acc(fresh) |
| --- | ----- | ---- | --------------- |
| bptt x adam | 3000 | 0/1/2 | **1.000 / 0.969 / 0.979** |
| local x adam | 6000 | 0/1/2 | **0.688 / 0.719 / 0.667** |
| local x muon | 6000 | 0 | **0.625** |

Findings:
1. **Q-robustness MET**: bptt control ≥0.969 on all 3 seeds, fresh-draw
   eval. The control is real and stable at 3000 steps.
2. **Local factorization is seed-robust** at ~0.69 mean and fresh-draw
   robust. BUT the extended budget (6000 steps) revealed a **plateau,
   not a still-climbing curve** — per-eval accs oscillate 0.62-0.74
   from step 2400 onward with no upward trend. The §11.1 "still
   climbing" caveat is RESOLVED as "plateaued at ~0.7". The local
   factorization's ceiling is real: the per-module surrogate losses
   (content-code MSE + addressing KL for the writer) cap what the
   writer can express — a better write-local rule is the lever, not
   more budget.
3. **I(C,U) on memory credit: NEGATIVE at first pass** — local×muon
   (0.625) < local×adam (0.688/0.719/0.667). Muon composes (learns to
   0.625, well above chance) but does not rescue. NOTE: muon arm used
   lr 1e-3 (adam's value) with NO lr screen — muon's canonical lr
   differs (D16: ~0.02-0.05 for these scales). The negative is
   UNSCREENED; screen {0.003, 0.01, 0.03} before calling it a boundary.
4. **Promotion gate status**: criterion (ii) — a non-Adam rule composes
   with NTM — is MET (muon runs and learns). Criterion (i) — "promoted
   positive" — is a judgment call: robust above-chance learning (0.69
   vs 0.5 chance) but far below the 1.0 control. Honest label: PARTIAL
   positive. The §1-style promotion should wait for either (a) a
   screened muon cell, or (b) a writer-surrogate improvement pushing
   local ≥ 0.85, before paying the AGENTS.md checklist cost.

## §11.3 — W8.1 unblock session (2026-09-08): levers (a)-(d) exhausted;
the blocker is a CLAMPED-INTEGRATOR SATURATION attractor — design pivot justified

All runs on `scripts/probes/w8_nca_local.py` (now REV 2026-09-08-r3).
Lever-by-lever record (overfit-8-sprites protocol, bptt x euclid lr 0.3):

1. **Lever (a) — MSE path verified live**: per-episode grad-norms 0.4-5.5,
   nonzero throughout; weighted CE 4.015→4.013 over 20 eps. Not a
   stale-process artifact; the §12 fear is retired.
2. **Lever (b) — per-step BPTT credit** (`_bptt_grads` now
   final-loss + mean per-step CE; this WAS missing in r2 despite the
   §12 note): 60 eps → still all-background (fg 0.000, bg acc 0.916).
3. **Lever (c) — 2000 eps overfit** (5x budget): fg-acc jumps to
   0.535 by ep 500 — GROWTH IS LEARNED — but bg collapses (acc 0.045)
   and then all eval metrics freeze byte-identically through ep 2000.
4. **THE FREEZE IS NOT GRADIENT DEATH**: grad-norm stays 2.4-4.6 at
   ep 600. The freeze is in the EVAL: final states hit STATE_MAX=10
   exactly (max 10.0) — channels pinned at the clamp absorb parameter
   change without changing argmax/CE. The §11 pathology-3 signature
   (clamp-ceiling saturation) returns here not at the target max but
   AT ANY CLAMP, because additive Δstate integrates upward every step
   and nothing anchors the scale.
5. **No-inhibition diagnosis**: bg cells need channel 0 to WIN the
   argmax, but fg channels grow to 10 everywhere; bg channel sits at 0
   (its clamp floor) and can never win. The inverse-frequency weight
   (~7x fg) pushes growth; tempered 1/sqrt(freq) weights change
   nothing (same saturated basin). tanh-bounding Δ (max ±1/step) also
   does not help — 32 steps still integrates to the 10-ceiling.
6. **Levers ruled out this session**: per-step credit (b), 5x budget
   (c), weight tempering, target-shift (bg=1/fg=2 — collapsed to
   acc 0.000), tanh-bounded delta. Lever (d) fixed-mask schedule is
   the only untested §11 item and does not address the saturation
   mechanism.

**Design-pivot menu for the next W8.1 session (pick one, pre-register):**
- **(P-A) Remove the clamp entirely** (Mordvintsev's actual design):
  unbounded additive state, tanh-bounded small deltas (|Δ|≤0.5), loss
  is per-step MSE IN STATE SPACE against the one-hot target. No CE on
  states (state values are not logits), no clamp absorbent. This is
  the closest to the canonical working NCA and directly removes the
  measured failure mechanism.
- **(P-B) Convex state**: state = softmax over channels per cell
  (probability-mass dynamics, renormalized each step) — saturation
  impossible by construction; CE is then legitimate (state IS logits).
- **(P-C) Explicit inhibition**: append the constant-1.0 "pre-channel"
  + alpha channel (Mordvintsev) so cells can learn to decay.

P-A is the recommended first move (smallest delta from current code:
delete clamp, add tanh scale, swap loss). The four-arm verdict
(P1-P4) should only be re-attempted after ANY of these shows the BPTT
control clearing fg-acc > 0.9 on the overfit protocol.

## §11.4 — W8.1 P-A deep-dive (2026-09-08, continued): the full defect
map, and the BREAKTHROUGH — distill-init controllers GROW; BPTT-from-
scratch was the broken piece all along

All on `w8_nca_local.py` REV r4 (P-A dynamics + `_distill_init`).
Runs are cheap (40-140 s per 600-2000-ep probe) — the below is a
15-experiment map, each cheap and decisive:

1. **P-A as specified (unbounded state, tanh Δ, per-step MSE) —
   DIVERGES**: train MSE ~90, states run away. With lr 0.03 the first
   "stable" run (train 0.137) was a **false positive**: eval at 48
   steps showed ch0 mean 3.54 (target ~0.92) with fg channels pushed
   NEGATIVE — the dynamics found their OWN fixed point, not the
   target's. Per-step loss over a 32-step rollout anchored nothing.
2. **Deterministic mask (all-ones) diverges** (train 52); the 50%
   stochastic mask is functional damping. Plan lever (d) answered:
   WRONG direction.
3. **Pool (Mordvintsev sample-pollution) + euclid: first real growth**
   (fg 0.34 at ep 100, pool-acc 0.87) but oscillates; pool + adam
   explodes (train spikes 130-430); pool + fg-weighting + adam
   explodes (train 1500). The pool's off-manifold states + 24-step
   BPTT = violent gradients.
4. **Gold-standard control bptt×adam on P-A (no pool): fg 0.000 for
   2000 eps.** The mirror attractor (paint fg everywhere) appears in
   the 2-channel minimal case too (fg 1.000, acc 0.234 — same
   signature, inverted). Every variant finds a runaway single-channel
   integrator whose fixed point ≠ target.
5. **FEASIBILITY ISOLATION (the session's decisive method):**
   - *Representation*: supervised regression of the ideal Δ-field onto
     the cell MLP fits to MSE 0.00076 (55x below chance) — architecture
     fine. (First attempt had a scrambled target via `_unflatten`
     misuse — false alarm, caught by max-error inspection.)
   - *Wiring*: 1-step BPTT from a half-grown state learns (one-step
     improvement > 0) — plumbing fine.
   - *Horizon*: T=4 fails identically to T=32 — horizon is not the
     blocker; the per-step loss from a SEED has an irreducible floor
     that drowns the fg signal (states cannot be at target at step 1).
6. **THE FIX — distill-init**: regress the IDEAL PROPORTIONAL
   controller Δ* = clamp(target − state, ±0.5) into the cell MLP
   (MSE 0.0002 — note: a `sign`-based field chatters with no fixed
   point and degrades at long horizons; the proportional field has an
   EXACT fixed point). Rollout from seed: **acc 0.979/0.975/0.984 at
   horizons 16/32/96 — GROWTH + HOLD, no drift.** BPTT finetune from
   the distilled init is stable (train 0.013, no explosion) and
   improves fg (0.70→0.73 @32). Landed as `_distill_init(p, targets)`
   (verified: acc 0.961 stable).

**Scientific consequences (pre-register for the four-arm verdict):**
- The W8.1 question changes from "can local credit grow an NCA from
  scratch" to **"starting from a distilled working controller, can
  local credit FINE-TUNE as well as BPTT?"** — a clean I(C,U)
  comparison on a real iterative-dynamics substrate, and arguably the
  fairer test (BPTT never had a chance from scratch at probe budget;
  the canonical NCA itself is a 5000-step 96-step-rollout train).
- fg-acc 0.7-0.8 ceiling on the distilled controller is the residual
  distill error (0.0002); the four arms now compete on how far they
  push past it (target: fg → 1.0, plus P1 horizons / P3 inversion).
- Next session's exact menu: (1) integrate `_distill_init` into
  `_train` as the default init for ALL FOUR arms (matched init, §20
  discipline); (2) run the four cells (bptt/local × euclid/muon,
  finetune lr screen {1e-3, 1e-4} for adam-class, {0.01, 0.03} euclid);
  (3) verdict on P1-P4.

## §11.5 — W8.1 executed to VERDICT (2026-09-08, REV r7): local credit
SOLVES the growing NCA (fg 1.000); two more §17-class defects found and
fixed on the way — one of them invalidates the r3-r5 finetune numbers

### Defect 1 (ontology-wide trap, now fail-loud): the weight-name contract
`apply_pseudo_gradients` (`computronium/ontology/utils/params.py`) pairs
pseudo-grads only with keys containing the substring `"weight"` (ndim 2).
The probe's hand-rolled dict (`w1/w2/wr`) matched NOTHING → **every
r3-r5 finetune run updated biases only**; weights never moved. This
explained all the anomalies (byte-identical muon==euclid, flat curves,
identical fg ceilings). Audit (subagent sweep of all 37 probes importing
the ontology update rules): zero other affected callers — every
committed probe reaches the rules through `compose_system` +
nn.Module `named_parameters()` (keys contain "weight"). Fixed by
renaming the probe's params (`weight1/weight2/weight_readout`,
`bias1/bias2/bias_readout`) AND by converting the silent skip into a
loud `UnmatchedWeightNamesError` raised in `apply_pseudo_gradients`
(165 targeted tests pass). Any future hand-rolled param dict now fails
at the first step instead of after a full run.

### Defect 2 (local-arm design): EMA unit-RMS normalization is a
near-equilibrium random walk
With weights live, the W0-recipe EMA normalization (fixed unit-RMS
steps) DEGRADED the distilled controller (acc 1.000 → 0.65, and
diverges at lr ≥ 0.01): near the fixed point the raw gradient is tiny
but the normalized step stays constant-size — an lr-independent random
walk. BPTT's raw gradients anneal naturally. Fix: raw summed
pseudo-grads (which is also the literal §1 statement: "pseudo-gradients
are summed over the rollout"); `_ema_normalize` deleted. Local is then
lr-robust across 0.03-0.3 (fg 1.000 at all three).

### The four-arm verdict (matched `_distill_init`, 800 eps, 3 seeds,
fresh-seed eval at h48; log `logs/w8_nca_verdict.log`)

| arm | seed 0 | seed 1 | seed 2 | mean fg |
| --- | ------ | ------ | ------ | ------- |
| bptt × euclid 0.03 | 1.000 | 1.000 | **0.000 (MSE 141, diverged)** | 0.67 |
| bptt × muon 0.01 | 1.000 | 1.000 | 1.000 | **1.000** |
| local × euclid 0.1 | 1.000 | 1.000 | 0.995 | 0.998 |
| local × muon 0.1 | 0.634 | 0.996 | 0.995 | 0.875 |

Findings (against the pre-registered P1-P4):
1. **HEADLINE: zero-history local credit trains a growing NCA to
   fg 1.000** — first complete local-credit result on iterative local
   dynamics, and it is rollout-length-flat (P1 horizons 1.000 at
   24/48/96 for every solved cell). The temporal-credit objection does
   NOT stand at this scale: local matches BPTT's solved seeds exactly
   and does not share BPTT's failure.
2. **P1 confirmed in the strong form**: BPTT × euclid DIVERGED on
   seed 2 (MSE 141) — 32-step backprop through the rollout is
   fragile; local credit (O(1) memory, per-step detached) is stable on
   all seeds at all tested lrs. The rollout-length law favors local
   here, as predicted.
3. **P2's predicted form is FALSIFIED, but the I(C,U) interaction is
   REAL with the sign flipped**: muon rescues BPTT (0.000 → 1.000 on
   seed 2) and slightly HURTS local (0.998 → 0.875; the SVD-polar
   direction wobbles at the fixed point — seed 0's 0.634). Weak-credit-
   needs-muon is not the law here; update-rule-dependent STABILITY is.
   The credit × update interaction exists in this geometry too —
   it is an interaction surface, not a one-way ladder.
4. **P3 (inversion generality) is MOOT in the P-A design**: the
   goodness-contrast machinery belonged to the retired CE readout; the
   W0 inversion question needs a different instrument on NCA (deferred,
   not answered).
5. **Promotion evidence (§10 criteria)**: (i) positive with 3 seeds +
   matched distill-init control + fresh-seed eval: MET for local×euclid;
   (ii) non-Adam rule composes: MET (both muon cells run and solve 2/3
   seeds). **NCA promotion is EARNED on the evidence** — the AGENTS.md
   checklist (NcaGeometry registry row, config classmethod, wiring
   lockstep lock, validate branches, export surfaces) is the next
   session's first task if the user confirms.

## §11.6 — W8.5 muon screen + W8.2 first cells (2026-09-08, evening):
NTM I(C,U) POSITIVE at lr 0.003; NCA ortho_adam rescues BPTT, hobbles local

### W8.5 muon screen (`w8_ntm_copy.py` REV r4, --lr flag; `logs/w8_ntm_muon_screen.log`)

local × muon, seed 0, 6000 steps, fresh-draw eval:

| lr | copy-acc(fresh) @6000 |
| --- | ----- |
| 0.003 | **0.812** |
| 0.01 | 0.625 |
| 0.03 | 0.635 |

The §11.2 muon "negative" is PARTIALLY an lr artifact, but the
positive did NOT survive 3 seeds (`logs/w8_ntm_promo.log`):
seed 0/1/2 = 0.812/0.698/0.667, mean 0.726 vs adam's 0.69 — a marginal
+0.04 driven entirely by seed 0. HONEST VERDICT: local × muon ≈
local × adam on NTM (~0.7 plateau both); the 0.812 was seed luck, not
a muon fingerprint. The NTM I(C,U) cell is a WASH (no update-rule
separation), unlike NCA where the interaction is strong (§11.5). The
writer-surrogate lever remains the ONLY route to the ≥0.85 promotion
bar — that is now the decisive NTM task.

### W8.2 first cells (ortho_adam arm added, r8; hard seed 2)
- bptt × ortho_adam 0.01 seed 2: fg **0.971** (rescued, cf. euclid's
  0.000 divergence, muon's 1.000) — the adam-family recipe rescues
  BPTT like muon does.
- local × ortho_adam 0.1 seed 2: fg 0.548 @100 eps, horizons degrade
  (0.596/0.548/0.514) — adam-family per-coordinate normalization
  re-introduces the constant-size-step random walk near equilibrium
  (the §11.5 EMA defect, now via m/sqrt(v)). THEORY CANDIDATE: local
  credit wants *magnitude-annealing* updates (raw euclid) or
  *direction-only* (muon/SVD) but NOT per-coordinate normalization;
  BPTT tolerates all three. Testable in W8.2's full screen.
- **GPU judgment (§12)**: RTX 3080 present, but the NCA/NTM probe
  tensors are tiny (16x16 grids, 32x37 MLPs, batch 8-16) — transfer
  overhead dominates; GPU was judged NOT worth it at probe scale.
  Revisit only if W8.3/W8.4 scale up.

## §11.7 — W8.3 first damage sweep (2026-09-08): a NULL result that
exposes the tautology — label-on regeneration cannot fail

Distilled+finetuned controller (bptt × euclid 0.03, 400 eps): damage
sweep zeroing a k×k patch of the FULL state after 48 growth steps,
then 48 regeneration steps: k=4/8/12/14/**16 (the ENTIRE grid) all
regenerate to acc 1.000 / fg 1.000.** With the target label injected
at every cell every step, each cell independently knows its target —
damage recovery is a pointwise repaint, not a collective computation.
The plan §4's "how much of the organism can die" question is only
meaningful in the LABEL-FREE regime (cells infer the pattern from
neighbors + seed memory); that variant is the prerequisite for any
W8.3 boundary claim, and where local-vs-BPTT could genuinely differ
(BPTT through the inference phase is much longer). Growth-from-seed
(label on) confirmed 1.000.

## §12 — Next-sprint operational notes (for a fresh context)

**REVISED 2026-09-08**: §11.2 (W8.5 promotion) and §11.3 (W8.1 unblock)
are the authoritative session records; the r2-era notes below retain
the file inventory and process guardrails.

**File inventory (all gates green: ruff clean, pyright 0 errors):**
- `scripts/probes/w8_nca_local.py` (REV 2026-09-08-r7) — W8.1 four-arm
  harness, **P-A dynamics** (unbounded state, `DELTA_SCALE=0.5` tanh Δ,
  state-space MSE), **`_distill_init`** wired as matched init for ALL
  arms, **zero-history local credit** (per-step detached-state MSE,
  raw summed pseudo-grads), weight-name-contract-compliant params,
  P1 horizon sweep, `--arm=`/`--seed=` flags. Recorded lrs: bptt
  euclid 0.03 / muon 0.01; local euclid/muon 0.1. VERDICT: §11.5.
  CAUTION: screens (`_screen`) still use stale r2-era lr grids.
- `scripts/probes/w8_ntm_copy.py` (REV 2026-09-08-r3) — W8.5 minimal
  NTM with FRESH-DRAW eval (`_eval_batch`, seed 999), `--arm=`/`--seed=`
  flags, `--len-eval` sweep, and the `local-muon` arm (`_Muon` wraps the
  ontology's `newton_schulz5`; UNSCREENED lr 1e-3 — screen before use).
  `_local_step` is the zero-history seam.
- Logs: `logs/w8_nca_local.log` (stale — pre-fix run), `logs/w8_ntm_copy.log`,
  `logs/w8_promotion.log` (the §11.2 round).

**Sprint opener checklist:**
1. Dev-env smoke: `uv run python -c "import optuna, scipy, torchvision, pytest"`.
2. Re-verify the W8.1 MSE path is live BEFORE trusting any old number —
   the last W8.1 smoke printed pre-patch-identical output (suspected
   stale process). Never trust a run whose numbers predate the patch.
3. Run from repo root (`uv run python scripts/probes/...`); the probes
   import siblings via `scripts/probes` layout.

**Process guardrails learned this sprint:**
- NEVER `pkill`/`pgrep -f` here (it can match and hang the invoking
  shell); kill by explicit PID.
- Background runs: `nohup uv run ... > logs/... 2>&1 &` then poll the
  log with sleeps; the shell waits on children otherwise.
- The ontology update rules (`EuclideanUpdate`/`RiemannianOrthogonalUpdate`)
  accept plain `dict[str, Tensor]` params + pseudo-grad lists +
  `bias_grads` dict — use them for the U axis in any standalone probe.
- Local-arm loss designs must survive the three §11 pathologies
  (imbalance attractor, clip lr-invariance, CE-on-additive-state
  gradient-free attractor) — check for each by signature before
  reading any flat curve as a boundary.

**Decision points this sprint should resolve:**
- Is the NTM local factorization's 0.708 seed-robust and fresh-draw
  robust? (→ NTM promotion / ontology case)
- Does local × muon beat local × adam on NTM memory credit? (→ the
  I(C,U) axis on external memory; the fingerprint question)
- Does W8.1 show any fg learning once per-step credit is live? (→
  NCA verdict or a design pivot: conditional-NCA → pure-growth NCA)
