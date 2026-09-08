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

- `local_contrastive` requires **label-augmented inputs** (last
  `label_dim` features = one-hot target) and trains a readout head on
  local CE; hidden layers on the softplus-gated goodness contrast with
  EMA normalization. For the NCA, the natural mapping is: **each cell
  (row of the flattened grid) is a "sample"** — reshape (B, H·W, C) →
  (B·H·W, C) so the existing per-layer contrast machinery runs
  unchanged; the target sprite occupies the label channels.
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

## §6 — NTM (W8.5): the memory stress test — CONDITIONAL

**Gate: starts only after W8.1–W8.3 produce at least one promoted
positive or a clean boundary.** NTM without BPTT is a bigger lift than
all of NCA; do not open it while NCA cells are still cheap.

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
| Lattice/tile |    ✓    |     ✓     |      partial      |       ✓       |         —         |
| NCA          |  W8.1   |   W8.1    |       W8.1        |       —       |       W8.2        |
| NTM          |  W8.5   |     —     |       W8.5        |       —       |        —          |
| DNC          | W8.5+   |     —     |       W8.5+       |       —       |        —          |

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

## §10 — Priority order (as actually executed)

1. **W8.1** — minimal NCA probe, four cells, pre-registered P1–P4.
   One session. Cheapest decisive information in the workstream.
2. **W8.2** — optimizer/degenerate-credit interaction on NCA (only if
   W8.1 shows a live signal worth interacting with).
3. **W8.3** — long-horizon/damage curves (attacks the temporal-credit
   objection directly; reuses W8.1 machinery, no new code).
4. **W8.4** — shared vs unshared weights (new axis, moderate lift).
5. **W8.5** — NTM copy (opens only on a W8.1–W8.3 result).
6. **W8.6** — combined cellular computer (moonshot; unscheduled).

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
