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
| NCA          | harness |     —     |     harness       |       —       |         —         |
| NTM          | ✓ 1.000 |     —     |    ✓ 0.708 1-seed |       —       |         —         |
| DNC          | W8.5+   |     —     |       W8.5+       |       —       |        —          |

(NCA row = harness landed, verdict open, §11; NTM row = §11.1, single
seed, fixed-batch eval — promotion round pending.)

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

## §10 — Priority order (REVISED post-first-sprint, 2026-09-07)

1. **W8.5 promotion round** — 3 seeds + fresh-draw eval + extended
   budget (the 0.708 curve was still climbing at 3000 steps) + the
   local × muon cell (I(C,U) on memory credit; muon on per-module
   pseudo-grads). Cheapest decisive information in the workstream; a
   positive here is the ontology-promotion evidence for NTM.
2. **W8.1 unblock** — the §11 lever list in order: (a) verify the MSE
   path is live (per-episode loss print, 20 eps); (b) per-step loss
   averaging; (c) 600+ episodes; (d) fixed mask schedule. Then the
   four-cell verdict.
3. **W8.2** — NCA optimizer interaction (after W8.1's verdict).
4. **W8.3** — long-horizon/damage curves (reuses W8.1 machinery).
5. **W8.4** — shared vs unshared weights.
6. **W8.6** — combined cellular computer (moonshot; unscheduled).

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

## §12 — Next-sprint operational notes (for a fresh context)

**File inventory (all gates green: ruff clean, pyright 0 errors):**
- `scripts/probes/w8_nca_local.py` (REV 2026-09-07-r2) — W8.1 four-arm
  harness with ontology update rules, P1 horizon sweep, P3
  inversion-rate, P4 inject-r; NOW with per-step BPTT credit (the §11
  lever b, default on) and `--arm=`/`--seed=` single-cell flags (skip
  screens; recorded lr picks euclid 0.1 / muon 0.02). Per-step credit
  ALONE did not unblock fg learning (400-ep smoke still flat) — the
  remaining levers are (c) 600+ episodes, (d) fixed mask schedule, or
  the design pivot to pure-growth NCA.
- `scripts/probes/w8_ntm_copy.py` (REV 2026-09-07-r2) — W8.5 minimal
  NTM with FRESH-DRAW eval (`_eval_batch`, seed 999, independent of
  training), `--arm=`/`--seed=` flags, and `--len-eval` length
  generalization sweep (L=6/12/18/24; decays off-train-length at 600
  steps as expected). `_local_step` is the zero-history seam.
- Logs: `logs/w8_nca_local.log` (stale — pre-fix run), `logs/w8_ntm_copy.log`.

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
