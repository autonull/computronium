# TODO14.md — Overturn the Boundaries, Compose the Winners

> **Opened 2026-09-07.**
>

> **CURRENT FOCUS (2026-09-09, Session 14 = TODO15 §13, CLOSED).
> Resumption pointer for fresh context — the authoritative session log
> is TODO15 §13; the deltas that change THIS file's plan:**
>
> 1. **PepitaCredit PROMOTED** (§13.1) — the published PEPITA rule is a
>    library primitive on all wiring surfaces (config factory, three
>    dispatchers, campaign registry, exports) with a duck-typed
>    `set_substrate` hook reaching the rule through
>    `geometry.forward(x, substrate)` on both passes. Wiring lock:
>    `tests/integration/test_pepita_credit_parity.py` (green, 0.65 s).
> 2. **PEPITA × Muon γ=0.05 — BOUNDARY in the harm direction**
>    (§13.2): pepita/muon 0.746 vs pepita/adam 0.884 (bp 0.890), 3
>    seeds. The matrix rules DESTROY exact-modulated gradients while
>    rescuing degenerate local ones — the I(C,U) law now has both
>    quadrants measured. PEPITA's home optimizer is Adam-class.
> 3. **LEMMA closure harvest-audited** (§13.4): best 0.299 vs final
>    0.290 — plateau; the alignment-noise closure stands. Retroactive
>    harvest audit of the Overturn Table is DONE (no other suspect
>    trajectories).
> 4. **LEMMA API rename EXECUTED** (§13.5): `local_objective="lemma"`;
>    `credit_type="pepita"` now means the published rule only.
> 5. **Probe-free EMA harvest** is the default harvest instrument
>    (`d50_autopsy.py --probe-free`, §13.3).
> 6. **Breadth block DONE (§14)** — depth×task grid under probe-free
>    EMA: depth curve 20→0.917, 32→0.917, 50→0.824, 64→0.628,
>    100→~0.75 — the local-credit depth frontier sits near 32 layers.
>    Harvest law transfers to FashionMNIST (0.767) but fails on digits
>    (0.128). Depth-100 MIXED (1/2/1, seed 2 = 0.489) — NOT §22 #4.
>    GPU port measured: works but ~3× slower than CPU (launch-bound).
>    PEPITA LM cell: BOUNDARY with mechanism (§15) — eval leak caught
>    and retracted (0.988 → 0.24 clean); label-modulation trains a
>    label-copier, not a sequence model; family is classification-bound.
> 7. **FF/EqProp under harvest (§16)**: EqProp joins the depth law
>    (early peak → collapse; most severe depth wall); FF grid deferred
>    on an unresolved d4 harness gap — no FF claim made.
>
> **Open queue (all optional extensions, nothing blocking):** PEPITA on
> the LM/transformer cell; PEPITA paper-ablation variants (B
> deterministic seed / learned-B-in-modulated-pass). W7 rungs, mask-ψ,
> LEMMA redemption: stay closed.

> **PRIOR FOCUS (2026-09-08, Session 12): §24 CLOSED.** D1 (scaled
> overturn cell) earned the flagship a **Boundary at scale** — the
> §24.3 stop-loss fired with the §17 protocol complete; D3 (boosting)
> falsified as the full repair; **D2 SHIPPED as gallery demo D17**
> (`multi_psi_swap`) — the program's first tangible runnable
> deliverable. The queue freeze is LIFTED.

## PROGRESS LOG (2026-09-08, Session 12 — §24 CLOSED: D1 boundary at scale, D3 falsified-as-repair, D2 shipped as demo D17)

**Status: the flagship sprint executed to completion in one session.
The W4.1 hidden-ψ overturn was driven to MNIST→FashionMNIST scale
(backbone 784→(128,128,128,128)→10, task A = MNIST mastery 0.957,
task B = FashionMNIST, θ bitwise frozen via SHA-asserted snapshot
restore, 9 arms × 3 seeds, GPU) and the overturn FAILED seed-robustly:
no hidden arm beats the readout ceiling on any seed. hidden_s4 (Q-class,
crosses no ReLU) ≈ ceiling (0.670 vs 0.674 mean — the same Q-identity
as probe scale); deeper streams degrade MONOTONICALLY with reach
(s3 0.387 / s2 0.292 / s1 0.217) — the probe-scale deep-reach gain
INVERTS at scale. D3's boosting repair is real but bounded (0.388 vs
stacked-raw 0.096 catastrophic, single-correction 0.670 not recovered).
D2 is the session's positive deliverable: one frozen backbone + a
per-task ψ library (MNIST/FashionMNIST/KMNIST), each ψ one ridge solve,
swapped as a state variable — shipped as
`tests/integration/test_demo_multi_psi_swap.py` + gallery row D17,
locks re-pinned (23 figures). Two §17-class target-construction defects
found and fixed en route (calibration-poisoned softmax residual;
W Wᵀ≈I chain approximation → exact mask-aware Jacobian targets). Probe:
`scripts/probes/w4_scaled_psi.py`. Logs: `logs/w4_scaled_psi{,_s1,_s2}.log`.**

### D1 — scaled overturn cell: BOUNDARY at scale (stop-loss fired, §24.3)

| b_best | seed 0 | seed 1 | seed 2 | mean |
| --- | --- | --- | --- | --- |
| null | 0.096 | 0.097 | 0.101 | 0.098 |
| readout (ceiling replacement) | 0.667 | 0.676 | 0.679 | **0.674** |
| finetune (control) | 0.783 | 0.782 | 0.783 | 0.783 |
| hidden_s1 (deepest reach) | 0.227 | 0.166 | 0.259 | 0.217 |
| hidden_s2 | 0.365 | 0.322 | 0.188 | 0.292 |
| hidden_s3 | 0.525 | 0.316 | 0.318 | 0.387 |
| hidden_s4 (Q-class) | 0.656 | 0.679 | 0.675 | 0.670 |
| hidden_raw (stacked) | 0.138 | 0.102 | 0.048 | 0.096 |
| hidden_boost (fit-on-corrected) | 0.410 | 0.326 | 0.429 | 0.388 |

1. **P-A FALSIFIED (overturn fails at scale)**: the pre-registered
   criterion (stream-1 beats the ceiling by ≥ +0.02, 3 seeds) fails by
   ~0.45; the §17 protocol ran in full — 3 seeds, SHA-asserted matched
   θ snapshot per arm, theta_invariant True everywhere, both
   target-construction defects found and fixed, and the D3 repair
   tested. **The W4.1 mechanism is a probe-scale phenomenon: closed-form
   hidden ψ's class-expanding gain (+0.08-0.10, ReLU-crossing) does not
   transfer to a confidently-wrong frozen backbone at MNIST scale.** The
   winning closed-form move at scale is the readout-CEILING REPLACEMENT
   (h_last → onehot ridge; same affine class as readout ψ, since the
   readout is affine in h_last — this IS the frozen-feature linear-probe
   ceiling, reached exactly).
2. **P-D INVERTED**: at probe scale deeper injection = bigger gain; at
   scale deeper injection = monotonically worse. Mechanism: the stream
   correction must reproduce the ceiling's job through more ReLU mask
   patterns — a single linear correction per stream is increasingly
   invalid as the mask diversity it must average over grows.
3. **Retention at scale (honest)**: every closed-form arm is
   retention-expensive (readout replacement 0.07-0.10 on task A —
   intrinsic to replacement; hidden arms 0.06-0.44, noisy, non-monotone).
   The resolution is NOT a better correction but STATE MANAGEMENT —
   exactly D2: swap ψ's, never overwrite.

### D3 — stacking repair: FALSIFIED as the full repair

Stacking raw (fit-on-uncorrected) is catastrophic at scale (0.096 mean,
at/below null — worse than probe scale where stacking merely degraded).
Fit-on-corrected (boost) repairs stacking to 0.388 but does NOT recover
the single-correction level (0.670). **P-C falsified**: the
one-correction boundary stands, now with the repair tested at scale.

### D2 — multi-ψ demo SHIPPED (the tangible deliverable)

`tests/integration/test_demo_multi_psi_swap.py` (gallery D17,
`multi_psi_swap`): one frozen backbone (784→(64,64)→10, 300 stage-A
episodes), per-task ψ library over MNIST/FashionMNIST/KMNIST, each ψ ONE
ridge solve (instant acquisition, no episodes), swap = state variable.
Guarantees asserted: θ SHA bitwise across the lifecycle; own-ψ ≫ null
for the non-native tasks (0.65-0.83 vs ~0.10-0.25), own ≥ null − 0.02
for the native task; own ≫ foreign mean (a keyed variable, not a
blend). Gallery locks re-pinned (23 figures; `test_gallery_lock`
passes). §22 #2's usable form is demonstrated; the §24 success
criterion's D2 half is met.

### §17-class findings recorded for reuse

1. **Softmax-residual targets are calibration-poisoned at scale**: with
   a confidently-wrong frozen readout (post RMS ~1.9), R = onehot −
   softmax(post) swamps the ±1 onehot signal even IN-SAMPLE (0.088
   train-fit acc; the onehot ridge on the same features: 0.66). Any
   frozen-feature residual construction must first reach the CEILING
   and target the difference FROM it.
2. **W Wᵀ ≈ I chain propagation dies on trained weights**: the
   probe-scale T_s = R @ W-chain targets are chain-exact only for
   near-orthogonal weights. Fix (landed in the probe): exact mask-aware
   Jacobian targets, T_s = R @ pinv(J_s), J_s built batched through the
   ReLU masks (mask = post-ReLU stream > 0). This alone moved
   hidden_s3 from 0.0 → 0.53 (seed 0) — the mask structure, not the
   weight chain, is the carrier of deep credit at scale.
3. **Piecewise-ψ opportunity (queued, not frozen-queue)**: since the
   mask pattern is observable per settle, the natural rescue of the
   depth story is a MASK-GATED ψ library (per-mask-pattern corrections,
   keyed like D2's task library). That is a design session, not a cell.

### §24 disposition

- D1: Boundary at scale (§22 #2 NOT met at scale; the open question is
  retired — the probe-scale result stands as the mechanism map).
- D3: falsified-as-repair (recorded above).
- D2: shipped (D17). **The §24 queue freeze is LIFTED.**
- Next-session menu (Session-11 order resumes): W4.2 3-seed firming is
  ABSORBED/closed by the D3 result; the retention lever is demonstrated
  (D2); ontology promotion of `modulate_mid_stream` is MOOT (the
  mechanism is scale-bounded); W5 depth-50 and the per-site FA design
  session are the remaining frozen items, now unfrozen.

## PROGRESS LOG (2026-09-08, Session 11 — W4.1 hidden ψ: ceiling OVERTURNED seed-robust (§22 #2 MET); W4.2 depth-composition falsified (stacking); recurrent-family audit closes)

**Status: three results. (1) The pre-registered W4.1 cell (§10, Session
9) EXECUTED and the overturn criterion is MET on all 3 seeds —
hidden-layer closed-form ψ exceeds the frozen-feature linear-probe
ceiling (+0.093/+0.098/+0.100 b_best, spread 0.007) with θ bitwise
frozen (SHA-verified per arm). Gradient-free adaptation that MODIFIES
REPRESENTATIONS, not merely re-reads them — §22 success condition #2
MET at probe scale; Flagship B has its first positive cell. The
mechanism is fully attributed (bit-exact algebra, verified on every
seed): a stream correction before a LINEAR readout ≡ the readout-ridge
solution composed with Q = W_L W_Lᵀ (hidden_second ≡ readout_q
byte-identical, 3 seeds; frozen-metric effect only +0.012-0.014), while
the correction crossing ReLU(W₁·) adds +0.082-0.098 — the dominant,
class-expanding component. Honest costs measured: feature reorganization
is NOT forget-free (a_retained 0.786 mean vs 0.96 null — between
readout-ψ 0.95 and fine-tune 0.69), and the backward-propagated target
beats the raw readout residual for the same affine class (the mlp1
degeneracy control's real finding: closed-form-FA targeting is a better
regression target even where the class cannot expand). (2) W4.2 first
rung (depth 4): composition across depth FALSIFIED — by correction
STACKING (fit-on-uncorrected, applied-downstream mismatch), not depth;
a single early-stream correction keeps the full gain; retention cost
scales with the correction's REACH. (3) The recurrent-family audit
closes the Session-7 pairing class with no defect — and surfaces that
the self-connection credit route is credit-rule-dependent (pepita
starves, rp feeds). Probes: `scripts/probes/w4_hidden_psi.py` (18-35
s/seed), `scripts/probes/w1_recurrent_graph_audit.py` (0.2 s); ruff
clean, pyright 0 on both. Logs: `logs/w4_hidden_psi{,_s1,_s2}.log`,
`logs/w1_recurrent_graph_audit.log`.**

### W4.1 cell record (§10) — EXECUTED, Tier B overturn evidence

Cell: the W3 A→B switch task (parity→last-symbol, 300 stage-A episodes,
frozen θ), hidden (32,32) mechanism cell + (32,) degeneracy control,
16-batch (512-sample) fresh-draw eval, 200 stage-B episodes.

- Arms: null / readout ψ (W3 replay through the real pipeline) /
  hidden_raw (all hidden streams, raw targets) / hidden_norm
  (RMS-matched) / hidden_first (stream 1 only) / hidden_second (stream 2
  only, post-hoc) / readout_q (readout ridge @ Q, post-hoc) / θ
  fine-tune control. Statistics: the D22 nudged-settle seam; targets
  T_i = R propagated backward through FROZEN θ weights (closed-form FA,
  no derivative masks); the same bias-augmented scale-free ridge as
  `ClosedFormRidgePlasticity`.
- Design necessity recorded BEFORE measurement: with ONE hidden layer a
  hidden correction before a linear readout spans the readout ψ class —
  the pre-registered mechanism sentence ("ReLU(L_{i+1}) sees the
  CORRECTED stream") requires the correction to cross a nonlinearity;
  the (32,) cell is therefore the degeneracy control and (32,32) is the
  mechanism cell. This design choice is what made the attribution
  possible.
- P1 (control equality) FALSIFIED with explanation (the Q identity); P2
  (overturn) MET seed-robust; P3 answered (raw ≥ norm — depth-2 chain
  scale-neutral); P4 CONFIRMED (stream-2 inert); P5 all green (θ SHA
  identical across arms after matched stage A; theta_invariant True
  everywhere; target/correction RMS logged).
- Readout-class numbers replicate W3's verdict in-run (ceiling ≈
  0.71-0.74 best vs W3's 0.699 at 8-batch eval — protocol delta noted).

### W4.2 first rung — EXECUTED same session (depth 4): composition across depth FALSIFIED — by correction STACKING, not depth

Depth-4 cell (32,32,32,32), same harness, seed 0:

| mlp4 arm | b_best/b_final | a_retained |
| --- | --- | --- |
| null | 0.693 / 0.662 | 0.945 |
| readout | 0.719 / 0.680 | 0.951 |
| hidden_raw (all 4 streams) | 0.762 / 0.707 | **0.494 (below chance)** |
| hidden_first4 (stream 1 only, post-hoc) | **0.826 / 0.746** | 0.598 |
| hidden_near4 (last hidden stream, post-hoc) | 0.721 / 0.682 | 0.941 |
| finetune | 0.967 / 0.967 | 0.660 |

1. **§10 W4.2's "local closed-form adaptation composes across depth" is
   FALSIFIED at probe scale**: stacking all four corrections DEGRADES
   acquisition below the single deep correction (0.762 < 0.826) and
   destroys retention (0.494). Mechanism: each Δ is fit on
   uncorrected-stream statistics but applied downstream of the other
   corrections — the mismatch compounds with stack count.
2. **A SINGLE early-stream correction at depth 4 (crossing three
   ReLUs) KEEPS the full gain (0.826 ≈ mlp2's 0.816)** — the gain lives
   in one well-placed deep-reach correction, not in the count of
   corrected streams. Depth itself is not the enemy.
3. **Retention cost scales with the correction's REACH**: last-hidden
   (Q-class) 0.94 > stream-1@depth-2 0.79 > stream-1@depth-4 0.60 >
   all-streams 0.49. Deeper reach steers more shared representation
   toward task B.
4. Status per §1: single-seed first rung — OPEN (3-seed + §17 before a
   boundary claim); the mlp2 3-seed round anchors the depth-2 numbers.
   Boundary candidate: **closed-form hidden ψ is a ONE-CORRECTION
   mechanism (early stream, reach matched to the task), not a
   depth-composable one.**

### Recurrent-family audit — EXECUTED same session: the pairing class CLOSES

`scripts/probes/w1_recurrent_graph_audit.py` (0.2 s; static audit first,
then one dynamic rung per geometry × credit). The Session-7 queued
improvement opportunity ("the index-vs-settle-stream assumption may
misalign other index-paired credit paths") is RESOLVED — no defect:

- recurrent × pepita: feedforward weights live, `recurrent_weight`
  EXACTLY zero (the documented "self-connection: no PEPITA route"
  fallback); recurrent × rp: ALL weights live including
  `recurrent_weight` (rp's documented self-connection route). **The
  self-connection credit route is credit-rule-dependent** (pepita
  starves it, rp feeds it) — an I(C,U)-class observation for future
  recurrent-substrate work.
- graph × pepita / rp: all weights live on the 16→32→32→4 width chain
  (smallest 2.4e-5, backward attenuation through the random B's —
  nonzero and correctly shaped). The `_pepita_covariate_stream`
  monotone-width cursor generalizes to both geometries; the layered FA
  width-contract also passes.
- Harness lessons: GraphGeometry is node-classification layout (batch
  dim IS the node dim); RecurrentGeometry layer keys follow the
  Linear/ReLU interleave convention ('0.weight'/'2.weight').

### Remaining TODO14 menu (post-Session-11) — SUPERSEDED by §24

The menu below is **FROZEN** by the §24 flagship sprint; it resumes only
on §24's stop-loss (flagship boundary at scale) or completion. Full
definitions live in §24; the frozen items, for the record:

- W4.2 3-seed firming of the stacking/REACH boundary — ABSORBED into
  §24 P-C (the stacking fix is a flagship deliverable, not a side cell).
- Retention lever (task-gated ψ / multi-ψ library) — ABSORBED into §24
  P-B/D2 (the multi-ψ library IS the retention lever, demonstrated).
- Ontology promotion of `modulate_mid_stream` — deferred until the
  scaled cell (§24 D1) confirms the mechanism transfers; promotion pays
  the checklist once, on scaled evidence.
- W5 depth-50 (long-run session), per-site FA primitive (design
  session) — deferred with the queue freeze.

## PROGRESS LOG (2026-09-08, Session 10 — W8.4 weight-sharing verdict + NTM slot-identity collision fixed)

**Status: TODO.ntm_nca.md §10 items 2-tail and 5 both executed.
W8.4 (§11.15): weight-sharing is LOAD-BEARING — unshared local × euclid
fg 0.852 (3 seeds) vs shared 0.998; the ~13% fg sites' credit is pooled
by sharing (the class-imbalance attractor re-appearing at per-site
granularity); the rollout law INVERTS under unsharing (local h96 1.000 →
0.62–0.79); unshared BPTT converts seed-2's catastrophic divergence into
soft mediocrity (0.712, no explosion). Muon-on-unshared deferred (SVD on
the flat matrix mixes sites). Parameter SHARING is now a third measured
I(C,U)-adjacent axis. W8.5 Q4 (§11.16): the pre-registered slot-identity
collision fix (mem_slots ≤ mem_width, probe `--width=16`) moves
acc_given_hit 0.78–0.86 → 0.947 (mechanism MET) and local copy-acc mean
0.816 → 0.886 (all seeds ≥0.84; BPTT control unchanged 0.993); promoted
into `NtmGeometry.init_mem` (one-hot when mem_slots ≤ mem_width, distinct
fixed vectors otherwise) with tests updated. The NTM residual
(local 0.886 vs BPTT 0.993) is now fully decomposed: read_hit_rate 0.781
+ write precision — a tuning surface, no structural break.**

TODO14's own menu unchanged: W4 hidden ψ (pre-registered, dedicated
session), W5 depth-50 (long-run), per-site FA primitive (design
session), recurrent-family audit rungs (deferred with W4).

## PROGRESS LOG (2026-09-08, Session 9 — W8: NCA/NTM verdicts + two ontology promotions; NTM memory primitive lands)

**Status: the W8 arc (TODO.ntm_nca.md) closed its main cells and promoted
TWO new geometry primitives. W8.1 NCA: local credit SOLVES the growing
NCA (fg 1.000, 3 seeds, rollout-flat) via distill-init — BPTT × euclid
diverges on seed 2 while local is stable; `NcaGeometry` promoted (§11.8).
W8.2: the "adam-family wobbles local" theory FALSIFIED (lr artifact).
W8.3: label-free hole regeneration real (local 0.952 k8, 3 seeds) —
I(C,U) stability signature replicates without labels; label-free growth
from a point seed is a representation boundary (memoryless cell).
W8.5 NTM: zero-history local factorization reaches 0.816 mean vs 0.990
BPTT control (3 seeds, mechanism chain verified) and `NtmGeometry`
(content-addressed memory: slot embeddings + retrievable non-negative
content + supervised addressing) is PROMOTED (§11.14) with a short-BPTT
copy learnability gate. I(C,U) breadth: the credit×update interaction is
now measured on MLP, transformer, lattice, NCA, and NTM.**
TODO14's own menu: W4 hidden ψ (PRE-REGISTERED, §10 — execute in a
dedicated session), W5 depth-50 (long-run session), per-site FA
primitive (design session), recurrent-family audit rungs (cheap probe
code — the index-vs-settle-stream misalignment class check on
RecurrentGeometry/GraphGeometry, one rung each; deferred with W4).

## PROGRESS LOG (2026-09-07, Session 8 — W8.1 NCA harness landed; verdict OPEN)

**Status: W8.1 (TODO.ntm_nca.md) harness LANDED with the full
pre-registration (4 arms, ontology update rules as the real U axis,
P3/P4 instrumentation, P1 horizon sweep) — but the four-cell verdict is
NOT in. The session was consumed by three task-design pathologies,
each found via its measurement signature and fixed (see TODO.ntm_nca.md
§11 for the full chain): (1) class-imbalance trivial attractor →
balanced CE; (2) global-clip lr-invariance (third §17 sighting this
week) → grad_clip 0; (3) clamp-ceiling saturation / CE gradient-free
attractor on additive state → STATE_MAX above target range + MSE loss.
Remaining blocker: fg learning not demonstrated within budget; next
session verifies the MSE path is live, then per-step loss averaging.
TODO14's own menu is unchanged: W4 hidden ψ, W5 depth-50.**


## PROGRESS LOG (2026-09-07, Session 7 — W1 lattice cell: the rescue profile is sign-general but NOT magnitude-general; FA/DFA is unrealizable on lattice; pepita covariate-pairing defect fixed)

**Status: the W1 lattice cell (second geometry, Tier D qualification) is
DONE. The optimizer-specific recovery profile does NOT quantitatively
replicate: on lattice the only realizable degenerate rung (pepita)
shows weak positive interaction (I = +0.047 muon / +0.007 ortho vs the
MLP rp rungs' +0.44..0.46), and the rungs that carried the strong-form
law (rp_weak/ortho/vweak) are CONTRACT-INERT on lattice — the layered
FA/DFA walk cannot chain over a settle stream that omits the raw input
and per-site weights, so those rows are byte-identical no-op runs at
chance. A real pepita defect (index-paired covariates, correct only on
stack geometries) was found and fixed en route.**

### W1 lattice I(C,U) table (§7) — EXECUTED, Tier D narrows

Probe: `scripts/probes/w1_lattice_ladder.py` (hunt_cells harness reused;
lattice3d = SpatialLattice3DGeometry (4,3,3), hidden (2,), MNIST 150
batches, seeds 0-2, test acc; credit ladder + update registry imported
from w1_credit_ladder). Log: `logs/w1_lattice_ladder.log` (~7 min).
External anchors: bp × muon 0.905 EXACTLY matches hunt_hybrid's
recorded lattice bp × muon 0.905; harness verified.

| credit            | euclid.2 | muon  | ortho |
| ----------------- | -------- | ----- | ----- |
| bp (anchor)       | 0.810    | 0.905 | 0.907 |
| ff                | 0.844    | 0.871 | 0.903 |
| pepita            | 0.071    | 0.214 | 0.175 |
| rp_weak/ortho/vweak | 0.102 (all three byte-identical, every optimizer) | | |

I(C,U) vs euclid.2 (anchor = bp): muon {ff −0.068, pepita **+0.047**,
rp — no-op}; ortho {ff −0.038, pepita +0.007, rp — no-op}.

1. **Pre-registered P1/P2 NOT falsified — UNREALIZABLE.** The rp rungs
   (which carried the MLP strong-form law) return all-zeros on lattice:
   the layered FA contract (`RandomProjectionsCredit.compute_pseudo_gradient`)
   requires B_k to map act_{k+1} widths to act_k widths over a linear
   stack that includes the raw input; lattice settles omit the input
   (acts start at the 72-wide post-input features) and the per-site
   (2,2) weights are not transition-ordered. The contract's designed
   fallback is zeros — so the rp rows are NO-OP runs (0.102 ≈ chance,
   byte-identical across feedback_scale 1e-3/0.01/1e-4 AND
   orthogonal_init True/False — the inertness signature). Documented as
   the second inertness mode on
   `CreditAssignmentConfig.random_projections`. They are a no-op
   control here, NOT credit evidence.
2. **Defect found + fixed (measurement integrity, §17)**:
   `_pepita_gradient` paired weight k with act k by INDEX — correct on
   stack geometries (where acts[0] is the raw input), misaligned on
   lattice (input_proj would pair with a 72-wide hidden act → (72,72)
   grad vs (72,784) param; momentum crash, silent misalignment under
   clipless rules). Fix: `_pepita_covariate_stream` (prepend the raw
   input when the settle stream's first width disagrees) + monotone
   in_features matching — reproduces the shipped acts[k] pairing on
   stacks exactly (targeted credit/learned-feedback/parity tests,
   demo_update_ladder + learned_feedback_resume integration, and a
   0.071 exact re-run of pepita × lattice × euclid.2 after the
   post-review refactor all pass; MLP behavior untouched).
3. **Valid lattice reading (bp/ff/pepita only)**: the interaction's
   SIGN-CONCENTRATION on degenerate credit replicates (pepita is the
   only positive-I credit under both muon and ortho; ff and bp I ≤ 0)
   but the magnitude collapses: pepita × muon reaches only 0.214 (MLP:
   0.306) and I is +0.047 (MLP rp rungs: +0.44..0.46). **Tier D
   narrows: the credit-optimizer interaction is sign-general across
   geometries, but its strong-form magnitude is carried by FA-ladder
   rungs that only exist on stack geometries.** "Predictive" holds
   within geometry; cross-geometry it is qualitative, not quantitative.
4. SP2's "ff ≥ bp under plain optimizers" replicates on a second
   geometry: ff × euclid.2 0.844 > bp × euclid.2 0.810 (the third
   independent replication after SP2 and the w1 MLP ladder).

### Next (short-cell menu)

- W4 (§10): hidden-layer closed-form ψ — PRE-REGISTERED (Session 9,
  §10), execution deferred to a dedicated session.
- W5 (§11): depth-50 budget cell — long-run session.
- W8 (TODO.ntm_nca.md): NCA probe — independent arc; the W0.4
  "right-or-absent" injection principle applies to its label-channel.
- W0: BOUNDARY at probe scale. W0.2, hinge, W0.3, W0.4: falsified.
  W6: Tier C closed. W1: MLP matrix done incl. lion; lattice cell DONE
  (rp-realizability caveat recorded).

### New improvement opportunities (queued, not invented ad hoc)

- **Per-site FA feedback primitive**: a lattice-native FA/DFA variant
  (per-site B shaped like each site weight, error walked over the
  message-passing layout) would make the rp ladder realizable on
  lattice and let the strong-form I(C,U) law be tested where it
  currently cannot be. Design work — belongs in a dedicated session,
  not a short cell.
- **Inertness guard**: RandomProjectionsCredit could log/warn when the
  layered contract fails (currently silent zeros — the lattice no-op
  rows were only caught because they were byte-identical). Cheap
  hygiene candidate for the Register C pass.
- **Recurrent-family audit**: the same index-vs-settle-stream
  assumption the pepita fix removed may misalign other index-paired
  credit paths (RecurrentGeometry, GraphGeometry) — one probe rung per
  geometry (any momentum update crashes loudly; euclid silently
  misaligns) would close the class.

### Session-6 events (kept for context)

## PROGRESS LOG (2026-09-07, Session 6 — W0.4 causal targets: alignment is load-bearing; W0 → Boundary at probe scale)

**Status: W0's LAST rescue hypothesis (§6 causal local targets) is
CLOSED — every misalignment degrades, and a random task-uninformative
channel (0.114/3.365) BEATS misaligned real labels (0.094/3.740,
0.073/4.005). Real-but-wrong supervision poisons the injected stream;
noise can be ignored, wrong labels cannot. W0 graduates to Boundary at
probe scale: the full §17/§21 overturn protocol (optimizer matrix,
schedules, gain, contrast tracking, threshold, hinge, component
ablation, supervision geometry) has run with baseline best throughout.**

### W0.4 causal local targets (§6) — EXECUTED, alignment is load-bearing

Probe: `scripts/probes/w0_causal_targets.py` (TargetVariantCredit —
hidden-layer y_lab transformed per arm; the readout keeps TRUE targets).
Key realization recorded in the probe docstring: the shipped
construction is ALREADY the token-local next-token arm of §6
(`_tf_recompute` injects per-position `label_emb[y_lab]`), so the
untried variants are the MISALIGNED ones. muon 0.005, 600 steps, seed 0.
Log: `logs/w0_causal_targets.log`.

| arm           | top-1 | CE    | reading |
| ------------- | ----- | ----- | ------- |
| baseline      | 0.190 | 3.225 | token-local next-token (replicates) |
| shuffled_pos  | 0.094 | 3.740 | same token stats, wrong positions |
| seq_label     | 0.073 | 4.005 | one label per window |
| random_target | 0.114 | 3.365 | task-uninformative noise channel |

1. **P-A confirmed (top-1)**: causal alignment carries real signal —
   baseline > shuffled_pos > seq_label. The supervision geometry
   question does NOT dissolve; the contrast learns position-aligned
   next-token structure, not token statistics.
2. **P-B FALSIFIED, and the falsification is the finding**: random
   labels beat BOTH misaligned real-label arms. Mechanism: the label
   embedding is injected into the stream for ALL deeper recomputes —
   misaligned real labels write systematically wrong token information
   into every layer's input; random labels are unstructured noise the
   layers can discount. **A local supervision channel must be either
   causally right or absent — "approximately right" is worse than
   noise.** This is a reusable principle for any stream-injected
   supervision design (the MLP label-channel contract, NCA W8.1
   injection, etc.).
3. **W0 verdict**: with W0.4 closed, every §2/§3 overturn lever has
   been pulled (optimizers × schedules × gain × contrast instrument ×
   threshold × objective shape × components × supervision geometry).
   State: **local_contrastive on causal transformers at probe scale —
   rescue real but bounded (beats bp at 600-step matched tokens, 3
   seeds; decays past ~1–2k steps under every schedule tested);
   mechanism mapped (per-layer sign inversions, protective gate,
   load-bearing alignment). Boundary at probe scale.** Longer-context /
   larger-model cells remain untested and are the only honest
   generalization caveat.

### Next (short-cell menu)

- W1 lattice: I(C,U) table on lattice geometry (second geometry) —
  Tier D qualification; the optimizer-specific recovery profile
  (muon thresholdless / ortho sharp / lion sign-blind) is the
  prediction to test. hunt_cells-style harness + lattice geometry.
- W4 (§10): hidden-layer closed-form ψ — PRE-REGISTERED (Session 9,
  §10), execution deferred to a dedicated session.
- W5 (§11): depth-50 budget cell — long-run session.
- W8 (TODO.ntm_nca.md): NCA probe — independent arc, plan revised;
  the W0.4 "right-or-absent" injection principle applies directly to
  its label-channel design.
- W0: BOUNDARY at probe scale (all levers pulled). W0.2, hinge, W0.3,
  W0.4: falsified. W6: Tier C closed. W1: optimizer matrix done incl.
  lion fingerprint; lattice cell remains.

### Session-5 events (kept for context)

## PROGRESS LOG (2026-09-07, Session 5 — W0.3 ablation: baseline is locally optimal; Lion primitive lands)

**Status: W0.3 (§5) EXECUTED and FALSIFIED in the rescue direction —
every component ablation degrades (baseline 0.190/3.225 beats all four
arms; attention-output goodness EXONERATED, preattn_good CE 3.867).
Combined with threshold-independence + hinge falsification + full
optimizer coverage, W0 graduates STRONGLY toward Boundary at probe
scale. Lion added as an update primitive: diverges on the transformer
cell (sign class = Adam class), rescues weak credit on MLP but its rp
rungs are scale-invariant (sign makes sub-dominant credit invisible).**

### W0.3 component ablation (§5) — EXECUTED, P-A falsified, boundary firms

Probe: `scripts/probes/w0_component_ablation.py` (AblatedCredit subclass
of LocalContrastiveCredit; per-arm `_tf_layer_grad` overrides — zeroed
layers / pre-attention in_proj goodness). muon 0.005, 600 steps, seed 0.
Log: `logs/w0_component_ablation.log`.

| arm             | top-1 | CE    | vs baseline |
| --------------- | ----- | ----- | ----------- |
| baseline        | 0.190 | 3.225 | (replicates exactly) |
| embed_excluded  | 0.141 | 3.287 | worse — embed is load-bearing |
| preattn_good    | 0.175 | 3.867 | worse — attention output in the contrast is BENEFICIAL |
| attention_only  | 0.161 | 4.105 | worse |
| ffn_only        | 0.181 | 3.527 | worse on CE, near-parity top-1 |

1. **P-A FALSIFIED**: the out_proj-first inversion is NOT attention-
   output sabotage — removing attention from the in_proj goodness
   degrades CE by 0.64. The inversions, whatever their origin, are
   PART of what works.
2. **P-B confirmed**: no single-component exclusion rescues. Among the
   5 configurations the shipped objective is locally optimal. §5's
   "highly valuable result" (a compatibility theorem via exclusion)
   did not materialize in this direction — instead the negative is
   itself valuable: local_contrastive on causal transformers survives
   the full §17-style overturn protocol (optimizer matrix, schedules,
   gain diagnostic, contrast tracking, threshold sweep, hinge variant,
   component ablation) with baseline best throughout. **W0 graduates
   toward Boundary at probe scale** (3 seeds on the rescue cell exist;
   the ablation was seed 0, matching the base cell).
3. Component map: the label-independent FFN representation is the
   load-bearing part for top-1 (ffn_only 0.181 ≈ baseline 0.190);
   attention-output goodness contributes calibration (CE), the embed
   contributes both. The remaining W0 directions are architectural
   (causal local targets, §6 W0.4 — never attempted) rather than
   component surgery.

### Lion primitive (added this session; TODO14 I(C,U) datapoint)

`LionUpdate` + `ParameterUpdateConfig.lion(...)` landed across all five
wiring surfaces (update.py, root/ontology exports, both factory
dispatches, SystemConfig validation sweep). Measured calibration note in
the docstring: canonical "3–10× Adam LR" does NOT transfer to local
pseudo-gradients (MNIST ff peak at Adam-equal 1e-3 → 0.781 vs Adam
0.739; collapse ≥1e-2); sign steps are global-clip-invariant above zero.

- **W0 transformer cell (pre-registered: Lion diverges) — CONFIRMED,
  and it is the worst diverger yet**: CE 1334 (2e-3) / 9921 (5e-3) /
  115347 (1e-2) / 511 (1e-3) at 300 steps, all far above chance regime
  (muon 3.3, euclid 3.5, adam 604). Sign-class joins Adam's rescale-
  class as per-coordinate poison; orthogonalization remains the only
  rescue class on this cell. Log: `logs/w0_lion_screen.log`.
- **W1 ladder lion column** (`logs/w1_credit_ladder_lion.log`):
  bp 0.863, ff 0.892, rp_weak 0.792, rp_ortho 0.792, rp_vweak 0.792 —
  I(C,U) vs euclid anchor: ff +0.02, rp_weak +0.437, rp_ortho +0.419,
  rp_vweak +0.436. **Critical caveat: the three rp rungs are
  near-identical across a 100× feedback-scale range** (spread ≤1e-3;
  seed 1 differs at the 4th decimal — channel live but negligible).
  Under sign descent a sub-dominant credit component almost never flips
  the sign: Lion's I(C,U) measures the BASE RP direction, not the
  feedback channel. Sign-based rules are blind to weak-credit
  structure — a new mechanism distinction (muon: magnitude-sensitive
  rescue, thresholdless; lion: sign-blind).
- Probe plumbing: `--only-arms=` filter in w0_tf_local_optimizers;
  lion column in w1_credit_ladder `_register_updates`.

### Next (short-cell menu)

- W0.4 (§6): causal local targets — the ONLY untried W0 direction
  (sequence-level label vs token-local next-token target vs block-local
  target embedding, causal masking preserved). Needs a small
  `_tf_layer_grad`-adjacent change (the label channel is currently the
  class label embedding; a token-local target variant injects the
  NEXT token's embedding). Decides whether local credit needs
  causally-aligned supervision — the last rescue hypothesis.
- W1 lattice: I(C,U) table on lattice geometry (second geometry) —
  Tier D qualification; hunt_cells-style harness + lattice geometry.
- W4 (§10): hidden-layer closed-form ψ — PRE-REGISTERED (Session 9,
  §10), execution deferred to a dedicated session.
- W5 (§11): depth-50 budget cell — long-run session.
- W8 (TODO.ntm_nca.md): NCA probe — independent arc, plan revised.
- DONE: W0.2 (falsified), W0 threshold (independent), W0 hinge
  (falsified), W0.3 (falsified), W1 optimizer matrix incl. lion
  (optimizer-specific recovery profile established), W6 (Tier C).

### Session-4 events (kept for context)

## PROGRESS LOG (2026-09-07, Session 4 — W0 hinge lever FALSIFIED: the gate is load-bearing)

**Status: the hinge/signed objective made W0 WORSE at both budgets
(0.077/3.705 @600, 0.083/4.629 @1200 vs gate's 0.190/3.225 and
0.142/4.472). Sign-inverted layers keep-training is actively harmful —
the softplus gate's shutdown is a PROTECTIVE mechanism, not a defect.
The degeneration is in the contrast stream itself: W0.3 component
ablation (§5) is unambiguously the primary W0 lever. W1's
optimizer-specific recovery profile stands as the Tier D evidence.**

### W0 hinge lever (§3 lever b) — FALSIFIED, gate shutdown vindicated

Mechanism landed: `CreditAssignmentConfig.local_contrastive(
contrast_objective="hinge")` — softplus(θ − |ΔG|) at BOTH loss sites
(`_layer_grad` linear-stack, `_tf_layer_grad` transformer), default
"gate" is unchanged. Probe: `w0_tf_local_optimizers.py --hinge`.
Gates: ruff clean, pyright 0 errors, 91 targeted credit tests pass.

| objective | 600 steps     | 1200 steps    |
| --------- | ------------- | ------------- |
| gate (θ2) | 0.190 / 3.225 | 0.142 / 4.472 |
| gate (θ1) | 0.191 / 3.229 | 0.144 / 4.520 |
| hinge     | **0.077 / 3.705** | **0.083 / 4.629** |

1. Pre-registered criterion (beat CE 4.0 @1200) failed — and not
   narrowly: hinge is worse ALREADY at 600 steps, long before the
   gate-shutdown regime. The contrast sign inversions are not "layers
   that need more training" — they are layers being pushed the wrong
   way, and forcing them to keep moving corrupts the shared stream.
2. **Refined mechanism statement**: the W0 boundary is now
   three-sided — (i) per-layer sign inversions arise in the goodness
   contrast (contrast_track), (ii) acting on them is harmful (hinge),
   (iii) freezing them is only a partial mitigation that goes stale
   (gate). The remaining question is WHICH components invert first and
   why — exactly W0.3 (§5). The two out_proj layers inverted first;
   the ablation arms (−PE / embed-excluded / attention-only / FFN-only)
   map whether attention-output goodness is the inversion source.
3. Optimizer axis remains honestly covered (euclid/adam/muon/ortho_adam,
   schedules); the gate lever is now closed both ways (threshold +
   objective shape). A negative result that passes this protocol
   graduates toward a Boundary for local_contrastive on causal
   transformers at probe scale.

### Next (short-cell menu)

- W0.3 (§5): component ablation — NOW the only open W0 lever. Arms:
  baseline / −PE / embed-excluded / attention-only / FFN-only; log
  WHICH layers invert (out_proj first) per arm. Needs a small probe
  that restricts `compute_pseudo_gradient`'s per-layer targets (the
  transformer path already special-cases pe/in_proj — the seams exist).
- W1: feedback_scale 1e-5 / sign-flipped B under muon (does the
  thresholdless rescue survive a channel with no usable signal?); then
  the I(C,U) table on lattice (second geometry) for Tier D.
- W4 (§10): hidden-layer closed-form ψ — PRE-REGISTERED (Session 9,
  §10), execution deferred to a dedicated session.
- W5 (§11): depth-50 budget cell — long-run session.
- W6: DONE (Tier C, session 1). W0.2: DONE (falsified). W0 hinge:
  DONE (falsified). W0 threshold: DONE (independent).

### Session-3 events (kept for context)

## PROGRESS LOG (2026-09-07, Session 3 — W1 ortho column + muon recovery edge; W0 gate threshold ruled out)

**Status: W1's I(C,U) law now has an OPTIMIZER-SPECIFIC RECOVERY PROFILE
(muon thresholdless ≥ 1e-4, ortho collapses between 1e-4 and 1e-3) —
the strongest Tier D evidence yet. W0's gate shutdown is
THRESHOLD-INDEPENDENT (θ 1.0 ≡ θ 2.0 at 1200 steps); the signed/hinge
objective (small credit.py change) is the remaining cheap gate lever,
then W0.3 component ablation.**

### W1 extension (§7) — ortho column + feedback_scale 1e-4 rung

Probe: `scripts/probes/w1_credit_ladder.py` (extended: `ortho` update
registered into hunt_cells, `rp_vweak` = feedback_scale 1e-4 rung,
`--only=` cell filter; session-2 euclid/muon means reused from
`_SESSION2` — no re-measurement). Logs: `logs/w1_credit_ladder_ext.log`
(30 s walltime).

| credit (weakest → strongest) | euclid 0.2 | muon 0.02 | ortho (0.02, olr 1e-3) |
| ---------------------------- | ---------- | --------- | ---------------------- |
| bp (anchor)                  | 0.816      | 0.919     | 0.913                  |
| ff (no feedback)             | 0.825      | 0.896     | 0.918                  |
| pepita                       | 0.101      | 0.306     | 0.239                  |
| rp_weak (1e-3)               | 0.308      | 0.870     | 0.757                  |
| rp_ortho (0.01, ortho B)     | 0.326      | 0.873     | 0.780                  |
| rp_vweak (1e-4)              | 0.309      | **0.871** | **0.464**              |

I(C,U) vs euclid anchor: muon column {ff −0.03, pepita +0.10,
rp_weak +0.46, rp_ortho +0.44, rp_vweak +0.46}; ortho column {ff −0.00,
pepita +0.04, rp_weak +0.35, rp_ortho +0.36, **rp_vweak +0.06**}.

1. **Muon's rescue edge is NOT at 1e-3**: 10,000×-weakened feedback
   (rp_vweak) is rescued identically (0.871 ≈ rp_weak's 0.870). Under
   muon the interaction is thresholdless over the whole 1e-4–1e-3
   decade — the weak feedback channel contributes almost nothing
   measurable, yet ff (channel ABSENT) is NOT rescued (0.896 < 0.919).
   Open question: what does an effectively-zero-scale channel still
   provide? Candidate: sign/structure of B suffices; next rung is
   feedback_scale 1e-5 or a sign-flipped B.
2. **Ortho_adam has a SHARP recovery boundary between 1e-4 and 1e-3**
   (0.464 vs 0.757): the first measured cell where muon and ortho
   DISAGREE on which credit they rescue. This is the quantitative
   basis for a predictive I(C,U) law (Flagship C / Tier D): the
   recovery profile is an optimizer fingerprint, not a generic
   "matrix rules rescue weak credit" effect.
3. ff × ortho (0.918) ≥ bp × ortho (0.913) on this harness — SP2's
   MLP replication confirmed a second time under the extended grid.
4. Hygiene landed: `CreditAssignmentConfig.random_projections`
   docstring now warns it is inert under `LocalGoodnessCredit` (the
   session-2 audit-note defect).

### W0 gate-threshold sweep (§3 lever a) — THRESHOLD-INDEPENDENT

Probe: `w0_tf_local_optimizers.py` gained `--threshold=` (plumbed into
`_build`). muon_mid, seed 0, constant LR:

| θ     | 600 steps        | 1200 steps      |
| ----- | ---------------- | --------------- |
| 2.0   | 0.190 / 3.225    | 0.142 / 4.472 (contrast-track) |
| 1.0   | 0.191 / 3.229    | **0.144 / 4.520** |
| 0.5   | 0.191 / 3.234    | —               |

1. Lowering the gate threshold changes NOTHING at either budget — the
   post-peak degradation is not the shutdown *threshold*; at 600 steps
   the gate is open everywhere anyway (the contrast_track finding),
   and at 1200 the layers that invert do so by far more than either θ.
2. **The remaining gate lever is the signed/hinge objective** (train
   on |G+−G−| or drop the gate so sign-inverted layers keep training).
   Small, well-scoped `computronium/ontology/credit.py` change
   (`local_contrastive` config knob + the softplus site ~line 1133) —
   pre-register: if hinge @1200 beats 0.144/4.520 materially (CE
   < 4.0), the objective shape was the boundary; if not, the
   degeneration is in the contrast stream itself and W0.3 (§5)
   component ablation is the primary lever.

### Next (short-cell menu)

- W0.3 (§5): component ablation — DONE (Session 5: falsified, baseline
  locally optimal; boundary firms).
- W1: 1e-5/sign-flipped-B rung (NOTE: lion column showed sign rules
  are blind to sub-dominant credit — interpret future rungs
  accordingly); then I(C,U) on lattice (second geometry) for Tier D.
- W4 (§10): hidden-layer closed-form ψ — PRE-REGISTERED (Session 9,
  §10), execution deferred to a dedicated session.
- W5 (§11): depth-50 budget cell — long-run session.

### Session-2 events (kept for context)

## PROGRESS LOG (2026-09-07, Session 2 — W0 mechanism found + W1 interaction law)

**Status: W0's decay boundary has a MECHANISM (per-layer gate shutdown via
goodness-sign inversion — the objective, not the optimizer); W1 (§7)
major result MET in its strong form (degenerate credit rescued by muon,
I(C,U) = +0.46); W0.3 component ablation is now the primary W0 lever.**

### W0 contrast-track diagnostic — DECISIVE (the unrun instrument, run)

Probe: `scripts/probes/w0_contrast_track.py` (muon_mid arm, checkpoints
0–1200, per-linear r_i = ‖G+−G−‖/‖G+‖ and raw pre-EMA grad RMS logged
alongside val top-1/CE). Log: `logs/w0_contrast_track.log`.

| step | top-1 | CE    | finding                                                    |
| ---- | ----- | ----- | ---------------------------------------------------------- |
| 0    | 0.006 | 4.257 | init: r_embed 1.08, deeper 0.10–0.20 (gain-diag parity)    |
| 200  | 0.156 | 3.256 | signals healthy, grads 1e-5 → 1e-4                          |
| 400  | 0.193 | 3.128 | peak; deeper r 0.17–0.30, grads up to 5.7e-3               |
| 600  | 0.190 | 3.225 | r_i all ≥ 0.18 — NO signal starvation                       |
| 900  | 0.167 | 3.667 | **b0.out_proj, b1.out_proj grads EXACTLY 0**               |
| 1200 | 0.142 | 4.472 | r_i still 0.19–0.54, **b1.ffn2 grad 1.3e-18**              |

1. **The moving-target-drift hypothesis is FALSIFIED.** The raw label
   contrast does NOT decay as the stream organizes — r_i holds at
   0.15–0.54 through step 1200 (embed declines 1.08 → 0.245 but stays
   the largest). W0.2's falsification stands for a second reason.
2. **The real mechanism is per-layer GATE SHUTDOWN**: the softplus
   gate `softplus(θ − (G+ − G−))` saturates to exact zero gradient on
   individual layers once their goodness contrast INVERTS (G+ < G− by
   more than θ = 2.0). Those layers freeze (zero update) while the
   rest of the stack keeps moving — the trajectory then degrades as
   the frozen layers' representations go stale relative to their
   downstream consumers.
3. **Verdict: the post-peak boundary is the OBJECTIVE (gate + sign
   inversion), not the optimizer schedule.** Cosine decay only delays
   the inversion; no LR schedule can fix a per-layer shutdown. This
   converts W0's boundary from "loses signal past ~1–2k steps" into a
   structural statement: **fixed-threshold softplus gating on a
   moving stream self-freezes layers.**
4. New concrete levers (in order of cost): (a) contrast_threshold
   sweep 0.5/1.0 — is shutdown threshold-dependent? (b) signed/hinge
   objective (train on |G+−G−| or drop the gate) — sign-inverted
   layers keep training; (c) W0.3 component ablation (§5) to map
   WHICH layers invert first (the two out_proj layers were first).

### W1 credit ladder (§7) — MAJOR RESULT, strong form MET

Probe: `scripts/probes/w1_credit_ladder.py` (~27 s; hunt_cells harness
reused verbatim, credit rows extended; seeds 0-2, MNIST 150 batches,
test acc). Logs: `logs/w1_credit_ladder.log`.

| credit (weakest → strongest)   | euclid 0.2 | muon 0.02 |
| ------------------------------ | ---------- | --------- |
| pepita (fixed B, β 0.5)        | 0.101      | 0.306     |
| rp_weak (FA, feedback_scale 1e-3) | 0.308   | **0.870** |
| rp_ortho (FA, orthogonal B)    | 0.326      | **0.873** |
| ff (no feedback)               | 0.825      | 0.896     |
| bp (anchor)                    | 0.816      | 0.919     |

Interaction I(C,U) = Δ_muon(credit) − Δ_muon(bp anchor):
ff −0.031, pepita **+0.103**, rp_weak **+0.459**, rp_ortho **+0.446**.

1. **§7's "major result" is MET in its strong form**: credit degraded
   100× (feedback_scale 1e-3 vs the 0.01 default) collapses under
   euclid (0.31) and is rescued to 0.87 under muon — within 0.03 of
   ff and 0.05 of bp at the same optimizer. **Exact credit direction
   is nearly dispensable once the parameter geometry is right.**
2. The interaction is CONCENTRATED on degenerate credit (I grows
   monotonically down the ladder: −0.03 → +0.10 → +0.46) — the
   predicted sign and the quantitative basis for Flagship C
   (predictive credit × optimizer compatibility).
3. P2's "sharp boundary under ALL optimizers" is rejected: the
   boundary is optimizer-DEPENDENT, which IS the interaction law.
4. Defect-audit note (hygiene pass): `random_projections` configs
   belong to `RandomProjectionsCredit` (FA/DFA); handing one to
   `LocalGoodnessCredit` silently runs pure FF (first wiring of this
   probe did; the byte-identical-to-ff numbers exposed it, and a
   feedback_scale 0.01/1/10 identity confirmed the channel was inert).
   A docstring warning belongs on `CreditAssignmentConfig.random_projections`.
5. Reproduction: run twice, identical to 3 decimals. Cheap extension
   queued: rp ladder × ortho_adam + feedback_scale 1e-4 rung (find the
   muon recovery edge), then the I(C,U) table graduates toward a
   Tier D headline if the law predicts on a second geometry (lattice).

### Session-1 events (kept for context)

## PROGRESS LOG (2026-09-07, Session 1 — W0.1 + §8 infrastructure)

**Status: W0 (transformer local credit) REOPENED — 3-seed-confirmed rescue
at 600 steps; W6 CLOSED (Tier C headline: recipe transfers across depth ×
width × task, §22 #5 MET); W0.2 gain sweep falsified/deprioritized; §8
infrastructure fix LANDED.**

### §8 infrastructure fix — LANDED

- `actual_parameter_displacement(update, params, grads, ...)` added to
  `computronium/ontology/update.py`: snapshot-replay (get_state → step →
  load_state) yielding the optimizer's REAL per-parameter Δθ without consuming
  state. Snapshot protocol covers momentum buffers AND step counters for every
  rule, so replays are exact.
- `LocalContrastiveCredit.set_update_rule()` +
  `_sequential_view()`: `sequential_lr` recompute views (both linear-stack and
  transformer paths) now use the actual displacement when an update rule is
  registered; plain-SGD fallback otherwise. Wired automatically for ALL
  compositions in `factory.compose_system` (duck-typed, credit-optional).
- Fixed `compose_system_from_configs` missing `adam` / `ortho_adam` branches
  (pre-existing gap — ortho_adam was unbuildable from configs).
- Contract change (intentional): euclid+momentum views previously used
  step_size·grad; now use the real momentum displacement. Parity probes that
  assumed `sequential_lr == step_size` with momentum>0 will shift.
- Gates: ruff clean on changed files, pyright 0 errors (update.py, probe),
  94 targeted unit/property tests pass.

### W0.1 optimizer matrix (§3) — screen + short cells, seed 0

Probe: `scripts/probes/w0_tf_local_optimizers.py` (screen 300 steps; short
cells via `full --skip-screen --arm=X --steps=N`). Logs: `logs/w0_*.log`.
Unigram anchor 0.153; chance 0.015; bp 600-step reference at the identical
cell: top-1 0.152 / CE 3.329.

| arm (300 steps)          | top-1  | CE      | verdict                          |
| ------------------------ | ------ | ------- | -------------------------------- |
| euclid (0.005, clip 1.0) | 0.150  | 3.505   | matches w2_p4's marginal regime  |
| adam 0.005 / 0.01        | 0.025 / 0.046 | 604 / 93 | DIVERGES — see mechanism below |
| muon 0.01                | 0.183  | 3.337   | best at 300; collapses by 1000   |
| muon 0.02                | 0.113  | 6.596   | diverges                         |
| ortho_adam (0.003/0.01)  | 0.178 / 0.143 | 3.716 / 5.580 | top-1 ok, CE miscalibrated |
| **muon 0.005** (600)     | **0.190** | **3.225** | **BEATS bp at matched tokens** |
| muon 0.005 (1000)        | 0.169  | 3.971   | degrades, does NOT collapse      |
| muon 0.01 (1000)         | 0.105  | 8.511   | collapsed (cf. 300-step peak)    |

### Mechanism findings (reusable beyond W0)

1. **I(C,U) confirmed directionally**: same credit/data, optimizer flips the
   trajectory sign (euclid ↓, adam ↑↑ divergent, muon ↑ then slow decay).
2. **Double-normalization blowup**: Adam (per-coordinate rescale) on
   EMA-normalized pseudo-gradients amplifies small coordinates → divergence.
   Rules that ORTHOGONALIZE compose with local credit; rules that
   PER-COORDINATE RESCALE don't. Predicts: local_adam also diverges here;
   spectral_constrained safe.
3. **Muon rescue is real but non-monotone**: 0.005 degrades gently past its
   600-step peak, 0.01 collapses hard — the decay is LR-dependent, so a
   decayed/scheduled muon step or early-stop-at-peak is the obvious lever.

### W0 3-seed confirmation (muon 0.005, 600 steps, seeds 0-2)

| seed | top-1 | val CE |
| ---- | ----- | ------ |
| 0    | 0.190 | 3.225  |
| 1    | 0.180 | 3.354  |
| 2    | 0.181 | 3.304  |

All 3 seeds above the unigram anchor (0.153); mean top-1 0.184 vs the bp
600-step reference 0.152 at the identical cell (w2_p4). **§3's overturn
criterion is MET at the 600-step budget**: CE materially down, top-1 above
unigram, 3 seeds. NOT yet the headline: bp at 3000 steps still wins
(0.219/2.936), and the muon trajectory decays past its ~600-step peak
(non-monotone). Honest state: **local_contrastive × muon > bp at matched
600-step tokens, 3 seeds; the open question is the post-peak decay, not
the rescue itself.**

### W0.2 gain diagnostic (§4) — prediction FALSIFIED, gain sweep deprioritized

Probe: `scripts/probes/w0_gain_diagnostic.py` (2.5 s, measurement only).
Per-block contrast r_i = ‖G+−G−‖/‖G+‖ on fresh weights: embed 1.08; all
deeper blocks **0.10–0.20**. The w2_p4 "~1% noise-domination" hypothesis is
WRONG at the goodness-stream level — the label contrast is 10–20% everywhere
(injection contrast ~11% by RMS). The failure mechanism is therefore NOT
signal starvation; suspicion shifts to (a) the EMA-normalized random-walk
dynamics, (b) contrast direction quality (not magnitude), (c) the softplus
gate. The §4 kill condition ("scaling above 1% produces runaway") is moot at
these measured contrasts. **W0.2 as a gain sweep is deprioritized; W0's
lever is the decay-past-peak schedule, not injection gain.**

### W6 width transfer (§12) — P1 PASS, Tier C headline EXTENDED

Probe: `scripts/probes/w6_width_transfer.py` (reuses `w4_depth_frontier.run_arm`
verbatim, WIDTH monkey-patched per arm; ~5 min total). Depth 8, mupc init,
residual, OrthoAdam ortho_lr 1e-3 (the depth-8-selected value), 150 batches,
seed 0, no retuning of anything per width:

| width | train | test |
| ----- | ----- | ---- |
| 64    | 0.831 | 0.898 |
| 128   | 0.857 | 0.928 |
| 256   | 0.881 | 0.942 |

Spread 0.044 ≤ 0.05 -> **P1 PASS**: the single depth-8-selected recipe
transfers across width 64→256 (and, with w4_depth_frontier, across depth
8→32). Monotone improvement with width — no width-fragility in this recipe.

### W6 promotion round (3 seeds + task axis) — P1s PASS, P3 PASS: Tier C CLOSED

Promotion run (same probe, extension): 9 mnist arms + 3 fashion_mnist arms.

- **P1s PASS**: per-width 3-seed spreads ≤ 0.044; width-mean spread 0.035 —
  seed-robust.
- **P3 PASS**: fashion_mnist (784→10, width 128, recipe COMPLETELY
  untouched — same lr, init, optimizer, batches) seeds 0-2: 0.834/0.827/0.838,
  mean 0.833, range 0.011.

**Headline Tier C, final form: one tuned recipe (mupc init + residual +
OrthoAdam ortho_lr 1e-3, 150 batches, tuned once at depth 8 / width 128 /
mnist) transfers across depths {8,20,32} × widths {64,128,256} × tasks
{mnist, fashion_mnist} with zero retuning.** This is §22 success
condition #5, met. Remaining rigor for full promotion protocol: the
3-seed criterion is satisfied per cell; a defect-audit pass on the w4/w6
harnesses (measurement-integrity items: seed-before-loader-draw OK,
matched batches OK) is queued for the hygiene pass.

### Other fronts (breadth notes, no new runs this session)

- W6 zero-shot transfer: w4_depth_frontier.py already CONFIRMED depth
  8→20/32 lr transfer ("tune once, run anywhere") — §12's remaining open
  axis is WIDTH (64/128/256, no retune) and one non-MNIST task. The
  jpc harness (`w4_depth_frontier.run_arm`) is directly reusable for the
  width cells; est. ~5 min/arm.
- W5 depth-50: w4_depth_frontier measured the 150-batch collapse
  (0.397). W5.1's budget cell (300–600 batches) is the cheapest next
  lever but ~30+ min CPU — schedule for a long-run session, not a
  short-cell one.
- W1 credit ladder / W4 hidden ψ: not started; both need new probe code
  (W1 can reuse the hunt harness; W4 needs the ψ statistics mechanism).

### W0 decay + readout_scale cells (next-step menu #1 executed)

- **readout_scale is a NO-OP under Muon for matrix weights** (ro 0.3/1.0/3.0
  @ 600 steps: all exactly 0.190/3.225). Mechanism: the SVD polar factor is
  scale-invariant — `polar(s·M) = polar(M)` — so the head/hidden step share
  CANNOT be tuned via readout_scale on the muon axis (only the eps term in
  the EMA normalizer leaks scale). Under euclid/OrthoAdam (which rescales to
  the Adam norm) it would matter. §17 update-integrity finding: the w2_p4
  head/hidden imbalance worry is structurally unfixable by readout_scale
  under Muon; the lever is the sequential_lr axis or an OrthoAdam head rule.
- **Cosine decay CURES the post-peak degradation** (muon 0.005, decayed to 0
  over the run): @1200 steps top-1 0.194 / CE 3.152 and still climbing, vs
  0.169/3.971 (constant LR, degrading) at the same budget. The decay was a
  constant-LR artifact, not a dynamics boundary. Decisive 3000-step cell vs
  bp (0.219/2.936) RUNNING — logs/w0_decay3k.log.
- **3000-step decayed VERDICT (seed 0): 0.131 / 4.716 — degradation returns
  despite the schedule.** Decay extends the useful regime (~600 → ~1200
  steps) but the trajectory still turns down before 3000; bp wins at that
  budget. W0 stays REOPENED with a firming boundary: **local goodness
  contrast on the transformer loses usable signal past ~1–2k steps under
  ANY muon schedule tested.** Not yet run: an instrumented run logging the
  per-block goodness CONTRAST MAGNITUDE over training — if the contrast
  itself decays as the stream organizes (moving-target drift), the boundary
  is the objective, not the optimizer, and W0.3's component ablation
  (§5) becomes the primary lever.

### Next (short-cell menu, ≤10 min each, breadth first)

- W0.3 (§5): component ablation — see Session-3 menu (hinge lever first,
  then this).
- W0 gate lever: RESOLVED as threshold-independent (Session 3); hinge/
  signed objective is the remaining variant.
- W1 extension: DONE (Session 3 — ortho column + 1e-4 rung); next:
  1e-5 / sign-flipped B, then lattice for Tier D.
- W4 (§10): hidden-layer closed-form ψ, one layer, MNIST Task A→B; the
  ‖Δθ‖=0 bitwise gate is cheap to assert (~10 min). NOT STARTED —
  needs the hidden-ψ statistics code (w3_closed_form_psi skeleton).
- W5 (§11): depth-50 budget cell (300–600 batches) — long-run session.
- W6: DONE (Tier C closed, session 1). W0.2: DONE (falsified).

>> TODO13b made the instrument honest. TODO14 asks what happens when we apply
> that honesty symmetrically to the negative results:
>
> **Do not protect the falsifications. Attack them with the strongest mechanisms
> the project itself has since discovered.**
>
> The project's strongest repeated empirical finding is that **local / weak
> credit lives or dies by the update rule**. Yet several of the project's own
> falsifications were obtained using weak or untested update rules.
>
> Under the standing R11.5.5a / defect-hunt doctrine, those are not yet hard
> boundaries. The benefit of the doubt is not optimism for its own sake; it is
> consistency with the evidence already accumulated.
>
> TODO14 therefore has one central question:
>
> > **Which apparent limits are real, and which disappear when credit,
> > normalization, state, and optimizer are composed correctly?**
>
> The target is not to rescue every hypothesis. The target is to find the
> smallest mechanism changes capable of producing a qualitatively new result.
>
> **Priority is cross-the-room value × overturnability × cost.**
>
> Every major negative gets one serious mechanism-targeted overturn attempt
> before it graduates to a permanent boundary.

---

# §0 — The Central Hypothesis

Across D17, SP2, W2, and W4, the same pattern keeps recurring:

```text
credit direction
      ↓
   optimizer
      ↓
actual parameter geometry
      ↓
learning outcome
```

Backprop is relatively insensitive to the optimizer in the tested regimes.

Weak / local credit is not.

The strongest measured examples:

* MLP: ff × OrthoAdam ≈ BP × OrthoAdam
* Lattice: ff × OrthoAdam ≈ BP × OrthoAdam
* Attention: ff × OrthoAdam moves from 0.799 → 0.860 with the correct rung
* D17: Muon improves ff_hybrid more strongly than BP
* W2: local contrastive learning has never yet been tested with Muon or
  OrthoAdam on the transformer
* W3: ψ-only readout adaptation fails exactly at the frozen-feature ceiling,
  but hidden ψ has never been attempted

This suggests a stronger research framing:

> **Credit assignment and parameter update are not independent axes of
> difficulty. Their interaction may determine the practical learnability of
> local algorithms.**

The research object is therefore not merely:

$$
C \quad \text{or} \quad U
$$

but:

$$
I(C,U)
$$

the **credit–update interaction**.

TODO14 should deliberately search for large positive interaction effects.

---

# §1 — Status Discipline

A result occupies one of four states.

| State        | Meaning                                                                               |
| ------------ | ------------------------------------------------------------------------------------- |
| **Promoted** | Survives controls, defect audit, multi-seed confirmation, and fixed-step reproduction |
| **Open**     | Interesting signal; insufficient evidence                                             |
| **Reopened** | Previously negative result materially improved under a stronger mechanism             |
| **Boundary** | Survives mechanism-targeted retries and the known defect-hunt protocol                |

A “falsified” result is therefore not automatically a “boundary.”

A boundary requires:

```text
known defects addressed
+
appropriate optimizer tested
+
signal/mechanism verified
+
matched controls
+
multi-seed confirmation
```

---

# §2 — The Overturn Table

The following are the highest-value negative results to challenge.

| Falsification                                       | Why it may not be fundamental                                                                                                                                                        | Overturning experiment                                                                      |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| **W2 P4: `local_contrastive` fails transformer LM** | Tested with SGD on EMA-normalized pseudo-gradients; never with Muon/OrthoAdam. Label injection produced only ~1% stream modulation; readout/hidden update scales differed by ~5×10⁴. | `local_contrastive × {Muon, OrthoAdam}` + gain-matched injection + representation ablations |
| **PEPITA fixed-projection collapse**                | Learned-feedback alignment and co-adaptation were not tested; learned-B × Muon remains open. **SUPERSEDED (Session 13, TODO15 §10-11): this rung is LEMMA, not published PEPITA. Learned-B × Muon 0.107 (scale-invariant, 3 seeds) — CLOSED; LEMMA mechanism-bound (BP-gradient cos ≈ 0 at all layers). Published PEPITA validated at BP parity 0.884.** | ~~Learned-feedback~~ → done; `PepitaCredit` promotion + PEPITA × Muon γ=0.05 queued |
| **P2 frozen-error LM failure**                      | Exact inference-network ε, γ, width-512, and steps > H cells remain untried.                                                                                                         | Targeted ε × γ × width × depth-horizon cells                                                |
| **D17 BP late-regime advantage**                    | The late deficit may be the Muon axis rather than credit.                                                                                                                            | ff_hybrid × OrthoAdam/Adam at ≥3M tokens                                                    |
| **STDP collapse**                                   | Reward-/error-modulated STDP is the missing supervised term. **CLOSED structural (Session 13, TODO15 §9.3): `phases=(FREE,)` — no error term exists for any optimizer; Muon 0.110 boundary. W7.3b recommended kill.** | ~~TemporalTraceCredit + modulation~~ → new credit design or nothing |
| **Closed-form ψ ceiling**                           | The demonstrated law is readout-only; frozen features necessarily impose a linear-probe ceiling.                                                                                     | Per-layer hidden closed-form ψ                                                              |
| **Depth-50 collapse**                               | Measured under a finite data/budget regime; classified as memorization, not a fundamental dynamical failure. **SUPERSEDED (Session 13, TODO15 §9.5): the collapse was a final-step evaluation artifact — val peaks 0.80-0.85 @ batches 30-70 (3/3 seeds), harvest passes the 0.75 gate. Depth-50 REOPENED.** | ~~Budget × regularization~~ → harvest instrument; 3-seed round DONE |
| **Attention “credit boundary”**                     | Initial failure disappeared substantially after optimizer retuning.                                                                                                                  | Replicate with optimizer-aware local-credit protocol                                        |

The rows are deliberately not weighted equally.

### Most overturnable

**W2 P4**

### Most novel

**Hidden-layer ψ**

### Most practically useful

**Zero-shot scaling transfer**

### Most theoretically interesting

**Credit × optimizer interaction boundary**

### Most mathematically constrained

**Readout-only closed-form ψ beyond the linear-probe ceiling**

The last item should still be challenged architecturally, but not with the expectation
that ridge regression itself will violate its known representational limit.

---

# §3 — W0: Resurrect the Transformer Local-Credit Flagship

## Objective

Current result:

> Transformer `local_contrastive` does not learn useful contextual LM behavior,
> although the O(1)-memory mechanism works.

This is the single most consequential falsification and the most plausibly
regime-dependent.

If overturned, it combines:

* true local credit,
* no hidden-layer backward sweep,
* O(1) peak memory,
* competitive learning,
* transformer-scale architecture,
* a direct physical/resource advantage.

This is the highest-value experiment in TODO14.

---

## W0.1 — Optimizer rescue

Run the same transformer cell with:

```text
local_contrastive × Euclidean
local_contrastive × Adam
local_contrastive × Muon
local_contrastive × OrthoAdam
```

Keep fixed:

* architecture,
* initialization,
* tokenizer/vocabulary,
* label injection,
* EMA rule,
* sequential semantics,
* training/evaluation protocol,
* token budget.

Primary metrics:

* top-1,
* validation CE,
* feature drift,
* goodness contrast,
* per-layer update norm.

### Pre-registered overturn criterion

The current P4 failure is overturned if:

```text
validation CE decreases materially with training
AND
top-1 rises above unigram
AND
the effect survives 3 seeds
```

### Strong overturn

```text
local_contrastive >= BP
```

at a matched-token budget while retaining O(1) peak memory.

### Dream result

```text
local_contrastive > BP
+
~O(1) memory
+
true local credit
```

This is the flagship.

---

# §4 — W0.2: Gain-Matched Label Injection

The current label injection modulates a much larger hidden stream by only ~1%.

Do not perform a blind gain sweep.

Measure:

$$
r_i =
\frac{
\|G_i^{+}-G_i^{-}\|
}{
\|G_i\|
}
$$

for every block.

Then tune the label injection so that the contrast occupies controlled
regimes:

```text
0.1%
0.5%
1%
2%
5%
10%
```

while tracking:

* contrast magnitude,
* feature drift,
* goodness saturation,
* gradient variance,
* task accuracy.

### Hypothesis

There is an intermediate regime in which:

```text
label signal > stochastic local variation
```

without entering positive-feedback runaway.

### Kill condition

If contrast scaling above ~1% reliably produces either runaway dynamics or
worse representations, the injection channel itself becomes a genuine boundary.

---

# §5 — W0.3: Representation-Sabotage Ablation

The current failure trail implicates several components.

Run local-goodness objectives separately on:

```text
embedding
attention Q/K/V/O
FFN
residual stream
output head
```

with combinations:

```text
baseline
- positional embedding from goodness
- embedding excluded
- PE only
- attention only
- FFN only
- attention + FFN
```

Question:

> **Which subspaces are compatible with local contrast, and which are
> actively sabotaged by it?**

A highly valuable result would be:

> **Local contrast is viable for transformer blocks after excluding a
> specific incompatible representation component.**

That converts P4 from “transformers don't work” into a structural
compatibility theorem.

---

# §6 — W0.4: Causal Local Targets

The current transformer construction uses a fixed label channel.

That may be the wrong supervision geometry for autoregressive computation.

Test:

```text
sequence-level label
token-local next-token target
block-local target
random low-dimensional target embedding
```

with causal masking preserved.

The key question:

> **Does local credit need local supervision aligned with the causal
> structure of the task?**

This is a mechanism test, not a general architecture sweep.

---

# §7 — W1: Define the Boundary of “The Optimizer Does the Learning”

SP2 currently supports:

> Under the right optimizer, weak credit can approach BP on multiple geometries.

Do not stop at the positive result.

Find out **how weak the credit can become** before the optimizer stops being able
to recover it.

## W1.1 — Credit degradation ladder

Construct deliberately weaker directions:

```text
BP
FF
PEPITA
random projection
noisy random projection
Hebbian-like direction
partially corrupted credit
```

Run under:

```text
Euclid
Muon
OrthoAdam
```

Measure:

$$
A(C,U)
$$

and interaction:

$$
I(C,U)
=
A(C,U)-A(C,U_0)-A(C_0,U)+A(C_0,U_0).
$$

### Major result

If surprisingly degenerate credit remains competitive under OrthoAdam:

> **the practical importance of exact credit direction is dramatically
> lower than expected once parameter geometry is appropriate.**

### Equally valuable result

If performance collapses sharply beyond a corruption threshold:

> **the optimizer-credit boundary is measurable and predictive.**

Either outcome is useful.

---

# §8 — W2: Compose `local_contrastive × Muon × sequential_lr`

This is the architectural synthesis experiment.

The current `sequential_lr` semantics assume plain parameter displacement.

That is not sufficient for matrix-aware optimizers.

## Required infrastructure fix

Replace the assumption:

```text
displacement ≈ configured step size
```

with an explicit per-layer displacement surface:

```python
actual_parameter_displacement(...)
```

The recompute view must use the **actual optimizer-induced parameter change**.

Otherwise a failed Muon/OrthoAdam cell is ambiguous.

### Test

```text
MNIST d4
MNIST d8
Transformer d128/L2
```

with:

```text
local_contrastive × Muon
local_contrastive × OrthoAdam
```

### Expected value

This experiment directly connects:

* W2's local objective,
* SP2's optimizer rescue,
* D17's optimizer synergy,
* sequential layer semantics.

This is the most important composition in the codebase.

---

# §9 — W3: Reopen D17's Late-Regime Crossover

Current result:

```text
≤1–2M tokens: ff_hybrid/Muon wins
≈3M: parity
≥7–11M: BP wins
```

Do not assume the crossover is intrinsic.

### W3.1 — Alternate optimizer

Run:

```text
ff_hybrid / Muon
ff_hybrid / OrthoAdam
ff_hybrid / Adam
```

at:

```text
1M
3M
7M
```

with matched token counts.

The immediate question:

> **Can the local-credit crossover be moved by changing the update rule?**

### W3.2 — Crossover mechanism

Track:

* gradient cosine,
* parameter displacement,
* representation drift,
* training loss,
* validation loss,
* update norm,
* optimizer state norm.

Look for the point where the local method stops adding useful information.

### W3.3 — Hybrid schedule

If the crossover is robust:

```text
local credit during early regime
→ BP or another efficient rule later
```

Test whether a phase switch beats both pure methods under a fixed total
compute/token budget.

A practical adaptive schedule that beats pure BP is a major result even if no
single local rule dominates forever.

---

# §10 — W4: Hidden-Layer Closed-Form ψ

> **W4.1 PRE-REGISTERED (2026-09-08, Session 9) — EXECUTED (2026-09-08,
> Session 11): OVERTURN MET on 3 seeds; see the Session-11 log and
> `scripts/probes/w4_hidden_psi.py` for the verdict. One design delta
> from the mechanism below: the one-hidden-layer W3 cell is
> mechanism-degenerate (a hidden correction before a LINEAR readout
> spans the readout-ψ class), so the probe adds a second hidden layer —
> (32,) kept as the degeneracy control, (32,32) as the mechanism cell.**

### W4.1 mechanism (per-layer closed-form correction INSIDE the settle graph)

The readout-only ψ ceiling exists because a linear correction composed
with a linear readout is still a linear probe. The overturn lever: apply
the correction to the hidden stream BEFORE the next layer's nonlinearity,
so downstream features reorganize nonlinearly:

```text
settled h_i  →  ψ_i correction  →  ReLU(L_{i+1}) sees the CORRECTED stream
```

- ψ_i = (G_i + λI)⁻¹ C_i, the same ridge sufficient-statistics machinery
  as `ClosedFormRidgePlasticity` (G = Σ X_iᵀ X_i, C = Σ X_iᵀ T_i),
  accumulated per stage-B episode with the input X_i = layer i's input
  stream.
- Local target T_i: the readout error (onehot − softmax post) propagated
  backwards through FROZEN θ weights (closed-form, layer-local,
  gradient-free — a "closed-form FA": frozen weights ARE the feedback
  matrix, exact by construction, solving W1's FA-realizability critique
  on stacks).
- Δθ = 0 bitwise (SHA-256, the W3 instrument) — corrections live in ψ,
  never in θ.
- Seam: probe-local first (a probe that re-drives the MLP settle loop
  with corrections injected between layers); ontology promotion of a
  `modulate_mid_stream` plasticity contract only if the cell is alive.

### Arms: null ψ / readout-only ψ (W3 replay) / hidden ψ (per-layer) / θ fine-tune (control)

### Overturn criterion (unchanged)

Task B accuracy exceeds the frozen-feature linear-probe ceiling (W3
measured 0.699 at the same cell). Falsified → the ceiling is the
composition depth, not the injection point — a second boundary for the
closed-form family.

### Leak controls

Probes never see training batches (fresh seeded draws); null and
readout arms re-measured in-run; θ SHA before/after every arm; hidden-ψ
targets derived ONLY from the readout error + frozen weights (no label
leakage into deeper targets beyond the error term itself).

The readout-only ψ result should be preserved as a **confirmed boundary for that
specific law**:

> closed-form readout adaptation = frozen-feature linear probe.

Now test the missing capability.

## W4.1 — One hidden layer

Construct:

```text
settled h_i
   ↓
local sufficient statistics
   ↓
closed-form ψ_i
   ↓
modified local transform
```

Compare:

```text
null ψ
readout-only ψ
hidden ψ
full θ fine-tune
```

Require:

$$
\Delta\theta = 0
$$

bitwise.

### Overturn criterion

Task B accuracy exceeds the frozen-feature linear-probe ceiling.

That would establish:

> **gradient-free adaptation can modify representations rather than merely
> re-read them.**

---

## W4.2 — Per-layer ψ

> **FIRST RUNG EXECUTED (2026-09-08, Session 11): "composes across
> depth" FALSIFIED at probe scale — by correction STACKING (each Δ fit
> on uncorrected-stream statistics, applied downstream of the others),
> not by depth itself; a single early-stream correction retains the
> full gain at depth 4 (0.826), stacked-all-4 degrades (0.762) and
> destroys retention (0.494 below chance). Retention cost scales with
> the correction's REACH. Single seed — OPEN pending 3-seed + §17.
> See the Session-11 log.**

Extend independently:

```text
ψ_1, ψ_2, ..., ψ_L
```

using W2's recomputation pattern.

Do not begin with a monolithic controller.

The desired mechanism is:

> **local closed-form adaptation composes across depth.**

---

## W4.3 — Algorithm migration

Revisit Z3 using hidden ψ:

```text
θ frozen
ψ changes local operators
Task A → Task B → Task C
```

Require:

```text
exact θ invariance
fast acquisition
low retention cost
```

This is potentially the most novel capability in the whole project.

---

# §11 — W5: Break the Depth-32 Frontier

> **SUPERSEDED IN PART (Session 13, TODO15 §9.5/§10.4): the depth
> frontier is peak-limited, not depth-limited. Depth 32/50/100 all
> pass the 0.75 gate under val-peak harvesting (0.917 / 0.824-mean /
> ≥0.828); the "collapse at depth" is peak-then-memorize read at the
> final step. The live question is no longer "can depth-50 learn" but
> "how does the peak shape scale with depth" — instrument: EMA
> harvest. The 150/300/600-batch cells below are obsolete as
> prescriptions; re-read them as peak-harvest cells.**

Current:

```text
depth 32 = 0.867
depth 50 = 0.397
```

The 50-layer failure is classified as memorization/data-budget collapse.

Challenge that classification directly.

## W5.1 — Budget scaling

Depth 50:

```text
150
300
600
1200 batches
```

## W5.2 — Regularization scaling

One axis at a time:

```text
beta
gamma
residual scale
```

## W5.3 — Initialization comparison

Compare:

```text
μPC initialization
default initialization
scaled initialization
```

The key distinction:

```text
data-limited
vs
optimization-limited
vs
representation-limited
vs
initialization-limited
```

A successful depth-50 cell is valuable.

A clean proof that depth 50 remains impossible despite these controls is
also valuable.

---

# §12 — W6: Zero-Shot Transfer Beyond Depth

The current result:

> depth-8 selected LR works unchanged at depths 20 and 32.

Now test whether this is a broader scaling law.

## Width

```text
64
128
256
```

with no LR retuning.

## Task

Repeat on at least one non-MNIST task.

The high-value result is:

$$
\text{one tuned recipe}
\rightarrow
\text{multiple depths}
\times
\text{multiple widths}
\times
\text{multiple tasks}
$$

That could become a concrete systems advantage.

---

# §13 — W7: Reopen Other Major Negative Results

These should remain secondary to W0/W2/W4 but are high-upside.

> **SESSION 13 STATUS (TODO15 §9-§11): W7.1 ANSWERED and REFRAMED.**
> W7.3 (STDP) closed structural; W7.1's rungs measured LEMMA (closed
> mechanism-bound), and the *published* PEPITA was implemented and
> validated at BP parity (0.884 vs 0.890). W7.2 (frozen-error LM ×
> Muon 0.02) recorded boundary val_ppl 28.01 — boundary-locked this
> session.

## W7.1 — PEPITA

Try:

```text
learned-B
feedback co-adaptation
learned-B × Muon
```

Question:

> Does the apparent PEPITA failure arise from a fixed random feedback
> bottleneck?

---

## W7.2 — Frozen-error LM

Prioritize the explicitly untried cells:

```text
inference-network ε
γ
width 512
steps > H
```

Do not broad-sweep.

The question is whether the objective was simply evaluated outside its
intended regime.

---

## W7.3 — Reward-modulated STDP

Add an explicit reward/error term to `TemporalTraceCredit`.

Compare:

```text
plain STDP
reward-modulated STDP
BP
```

under the same task and data budget.

The goal is to determine whether the collapse was caused by the absence of a
supervisory modulation channel.

---

# §14 — W8: Resource and Physical-Constraint Payoff

Do not broaden substrates merely for coverage.

Use them only after a learning mechanism demonstrates a meaningful advantage.

The most interesting comparison is:

```text
same algorithm
same task
same target quality
different substrate
```

and measure:

$$
\mathcal C =
(
\text{compute},
\text{memory},
\text{energy},
\text{latency},
\text{plastic-state capacity}
)
$$

The question is:

> **Does substrate choice change which learning strategy is Pareto-optimal?**

The terminology remains strict:

* simulated energy,
* estimated energy,
* hardware-measured energy.

Never collapse these into a generic “energy efficiency” claim.

---

# §15 — The Three Flagships

TODO14 should concentrate narrative attention on three possible flagship
results.

## Flagship A — Local Transformer Learning

```text
Transformer
×
true local credit
×
Muon / OrthoAdam
×
O(1) memory
```

Potentially:

> local learning matches or beats BP while avoiding the global backward
> graph.

This is the highest-probability huge win.

---

## Flagship B — Gradient-Free Representation Adaptation

> **STATUS (2026-09-08, Session 11): FIRST POSITIVE CELL. The
> frozen-feature ceiling is OVERTURNED at probe scale (§10 W4.1, 3
> seeds, mechanism attributed bit-exactly — see the Session-11 log and
> `scripts/probes/w4_hidden_psi.py`). Promoted to the program's
> FLAGSHIP OF RECORD; §24 is its sprint plan.**

```text
θ frozen
+
hidden-layer closed-form ψ
```

Potentially:

> instant local adaptation that changes representation without gradient
> descent.

This is the most novel.

---

## Flagship C — Predictive Credit–Optimizer Compatibility

Build a model predicting performance from:

```text
credit quality
×
optimizer geometry
×
depth
×
architecture
```

Potentially:

> the project can predict which optimizer makes a local credit rule viable.

This could unify more of the repository than any individual benchmark.

---

# §16 — What We Must Not Prematurely Conclude

Do **not** currently conclude:

* transformer local contrastive learning fundamentally fails;
* local contrast cannot work on transformers;
* the D17 crossover is intrinsic;
* OrthoAdam is universally superior;
* weak credit only works on MLP/lattice-like geometries;
* depth 50 is a fundamental limit;
* closed-form ψ cannot perform representation adaptation;
* STDP is intrinsically noncompetitive;
* PEPITA's fixed feedback is the fundamental bottleneck;
* simulated substrate behavior predicts physical hardware efficiency.

The evidence does not justify those stronger statements yet.

---

# §17 — Defect-Hunt Protocol for Negative Results

Before promoting a failure to **Boundary**, run:

### Signal integrity

```text
positive vs negative stream actually differs
target signal reaches intended component
no accidental normalization removes the contrast
train/eval distributions match
```

### State integrity

```text
ψ written back
fast state not silently reset
persistent θ unchanged when supposed to be frozen
episode boundaries correct
snapshot/resume preserves state
```

### Update integrity

```text
correct LR semantic axis
actual optimizer displacement used
global clipping not crushing local signals
matrix optimizer not applied to vectors/biases
EMA bias correction correct
sequential vs Jacobi semantics correct
```

### Measurement integrity

```text
matched tokens
matched steps where appropriate
capacity ratio asserted
same loader draws
seed before loader draw
fixed validation windows
no walltime endpoint comparisons
```

### Resource integrity

```text
peak ≠ cumulative allocation
simulated ≠ measured energy
actual FLOPs ≠ proxy FLOPs
backend equivalence checked
```

A negative result that passes this protocol becomes substantially more valuable.

---

# §18 — Execution Spine

| Session | Main objective                                       | End state                         |
| ------- | ---------------------------------------------------- | --------------------------------- |
| **1**   | Transformer local credit × Muon                      | rescue / no-rescue                |
| **2**   | Transformer local credit × OrthoAdam + gain matching | rescue / mechanism boundary       |
| **3**   | Representation/component ablations                   | structural compatibility map      |
| **4**   | Hidden-layer ψ                                       | ceiling overturned / strengthened |
| **5**   | Credit degradation × optimizer matrix                | interaction boundary              |
| **6**   | D17 late crossover under alternate optimizers        | crossover moved / intrinsic       |
| **7**   | Depth-50 + zero-shot width transfer                  | scaling frontier                  |
| **8**   | Strongest rescued mechanism composed                 | flagship candidate                |
| **9**   | 3-seed fixed-step reproduction                       | promotion                         |
| **10**  | Substrate/resource Pareto test                       | co-design result                  |

Sessions 1–4 are the core.

Everything else is subordinate until a flagship emerges.

> **REVISED (2026-09-08, Session 11): a flagship emerged — Flagship B
> (§15 status note). The spine for the next sessions is §24's table
> (D1 → D3 → D2), which supersedes sessions 11+ of this table.**

---

# §19 — Probe Rules

Every new probe must specify before execution:

```text
question
mechanism
prediction
control
budget
metric
falsification criterion
overturn criterion
```

For optimistic hypotheses:

> **R11.5.5a applies fully.**

A positive result receives the same:

```text
matched-step/token control
multi-seed test
defect audit
capacity check
reproduction
```

as a negative result.

The purpose of TODO14 is not to replace negative-result discipline with
optimism.

It is to make optimism **testable**.

---

# §20 — Promotion Criteria for the Biggest Wins

A result becomes a headline only after:

```text
≥3 seeds
+
matched control
+
fixed-step evaluation
+
mechanism audit
+
reproduction
```

### Headline Tier A

```text
local_contrastive ≥ BP
at matched tokens
+
O(1) peak memory
+
true local credit
```

### Headline Tier B

```text
hidden ψ > frozen-feature probe ceiling
+
‖Δθ‖ = 0
```

### Headline Tier C

```text
single LR recipe transfers across depth + width
```

### Headline Tier D

```text
predictive credit × optimizer interaction
```

### Headline Tier E

```text
substrate changes Pareto-optimal learning strategy
```

---

# §21 — The Benefit-of-the-Doubt Rule

The project has earned the right to be aggressive because several apparently
strong conclusions have already changed after careful investigation.

The correct response is neither:

```text
“it failed, therefore it is impossible”
```

nor:

```text
“keep tuning until it wins”
```

It is:

```text
“what exact mechanism failed?”
            ↓
“what known stronger mechanism has not yet been applied?”
            ↓
“can one controlled intervention overturn the result?”
            ↓
YES → reopen
NO  → strengthen boundary
```

The project should especially distrust any failure obtained where a known,
measured rescue mechanism was omitted.

---

# §22 — TODO14 Success Condition

> **STATUS (2026-09-09, Session 13): #4 MET — Depth ≥ 50 is viable**
> (val-peak harvest: 0.797/0.827/0.848 @ seeds 0-2, depth 32 → 0.917,
> depth 100 → ≥ 0.828; TODO15 §9.5). Validation shape: 3 seeds at
> depth 50, single-seed at 32/100, held-out eval shared with the
> original frontier sweep; snapshot selected on the 20-batch eval draw
> (mild selection optimism, absorbed by the 3-seed margin).

TODO14 succeeds if it produces at least one of the following:

1. **Transformer local contrastive learning is rescued.**
2. **Hidden-layer closed-form ψ exceeds the frozen-feature ceiling.**
3. **A measurable optimizer–credit interaction law predicts performance.**
4. **Depth ≥50 becomes viable.**
5. **Zero-shot hyperparameter transfer extends across width/task, not merely depth.**
6. **A substrate changes the Pareto-optimal learning strategy.**
7. **A previously attractive falsification becomes a stronger, mechanistically
   useful boundary after surviving the full overturn protocol.**

The largest possible outcome is a composition:

```text
TransformerGeometry
×
LocalContrastiveCredit
×
Muon / OrthoAdam
×
O(1) recomputation
×
Hidden-layer ψ
```

with:

* local credit,
* competitive LM learning,
* O(1) peak activation memory,
* adaptive computation,
* and frozen/persistent separation that permits rapid adaptation.

That would not merely improve one benchmark.

It would demonstrate a qualitatively different training regime.

---

# §23 — Final Research Principle

> **Attack the boundary where the project has the strongest reason to doubt it.**
>
> Apply the strongest optimizer to weak credit.
>
> Match the signal before judging the objective.
>
> Respect causal structure before condemning locality.
>
> Give ψ a chance to modify representations before declaring it a readout trick.
>
> Separate optimizer effects from credit effects.
>
> Reopen every negative result whose decisive control was never actually run.
>
> When the boundary survives, promote it proudly.
>
> When it breaks, promote the mechanism that broke it.
>
> **The objective is not to make the hypotheses win.**
>
> **The objective is to discover the largest true capability hiding behind
> the current boundaries.**

---

# §24 — The Forcing Function: Flagship B to a Tangible Deliverable

> **Opened 2026-09-08 (Session 11).** The program has crossed from
> "scattered negatives" to "a small set of verified, mechanistically
> understood capabilities." The remaining step from verified capability
> to beneficial result is consolidation and scale — and it does not
> happen by running more short cells. This section is the forcing
> function: one flagship, concrete deliverables, a frozen queue, and a
> stop-loss.

## §24.0 — What is at stake (one paragraph)

W4.1 established, at probe scale, the program's most product-shaped
result: a frozen network plus a *solved, stored correction* (ψ) acquires
a new task instantly, without gradients, without weight transport, with
retention as an explicit placement dial. The claims are mechanistically
attributed (the Q-identity and the ReLU-crossing attribution are exact).
What is missing is everything an outsider would care about: non-toy
scale, real tasks, a runnable demonstration, and the retention story
made operational (swap, don't overwrite). This sprint closes that gap or
records the boundary at scale — either outcome retires the open question
permanently.

## §24.1 — Deliverables (define before executing)

- **D1 — Scaled overturn cell (MNIST-class)**: the W4.1 construction on
  a real task pair (e.g., MNIST digit-swap A→B, or MNIST→FashionMNIST)
  on a real MLP (width ≥ 128, depth ≥ 4). Arms: null / readout ψ
  (in-run ceiling) / hidden ψ (pre-registered placement: the deepest
  stream that crosses the most nonlinearities — the Session-11
  attribution rule) / θ fine-tune control. Overturn criterion
  unchanged: hidden ψ > readout ceiling by ≥ +0.02, 3 seeds, θ SHA
  bitwise, §20 round. The **reach dial** is a measured curve: a_retained
  and b_acc vs injection depth — the probe-scale "retention cost scales
  with reach" claim must replicate or break here.
- **D2 — Multi-ψ demo (adaptation as a state variable)**: one frozen
  backbone; a library of per-task solved corrections (≥ 3 tasks);
  swapping ψ's shows (i) each task at its own solved accuracy under its
  own ψ, (ii) off-task retention at the null level by construction (no
  overwrite — the probe-scale 0.786 retention cost is an artifact of
  overwriting, and this demonstrates it), (iii) instant acquisition
  (one ridge solve per task). Ships as a repo demo following the static
  `_ARMS` table pattern (walltime printed, never recorded), one
  `DEMOS` registry row in `computronium/visualization/gallery.py`, and
  the gallery lock re-pinned. This is the tangible artifact.
- **D3 — Stacking repair (the boosting hypothesis)**: fit deeper
  corrections on the *corrected* stream (re-settle between solves) —
  pre-registered prediction: depth-4 stacked performance recovers to ≥
  the single-correction level (probe-scale 0.762 → ≥ 0.826) while
  retention recovers toward the single-correction level. Falsified →
  the one-correction boundary is confirmed with the fix tested; that is
  also a clean result.

## §24.2 — Pre-registered predictions (written before execution)

- **P-A (scale transfer)**: the overturn replicates at MNIST scale
  (criterion in D1). Falsified after the full §17 protocol → **the
  flagship earns a boundary at scale**, §24 lifts, the queue resumes at
  the Session-11 menu. Either way the question is retired.
- **P-B (swap > overwrite)**: the multi-ψ library eliminates the
  retention cost (off-task retention at null level) while preserving
  per-task acquisition. This is the §22 #2 capability in its usable
  form.
- **P-C (boosting fixes stacking)**: D3's prediction above. Connects to
  the project-wide "stale statistics corrupt" theme — third independent
  test of the mechanism.
- **P-D (reach dial)**: retention varies monotonically with injection
  depth at scale (the dial is real and tunable on real tasks).

## §24.3 — Queue freeze and stop-loss

- **FROZEN while §24 runs**: no new geometries, no new credit rungs, no
  W5, no W7, no per-site FA, no W8.6, no recurrence-family extensions.
- **Permitted during the freeze**: §17 defect hunts on §24's own
  harnesses (instrument honesty outranks the freeze — the EMA,
  weight-name, and slot-collision catches all happened mid-run), the
  demo/gallery gate for D2, and targeted tests for touched modules.
- **Stop-loss**: if P-A fails after the full §17 protocol at scale, the
  boundary is written (probe result preserved as the mechanism map),
  the freeze lifts, and the program returns to the Session-11 menu with
  the ontology-promotion decision re-opened on the scaled evidence.
- **Success criterion for §24**: §22 #2 demonstrated at scale (D1) plus
  a runnable demo in the gallery (D2). That is the program's first
  tangible deliverable that a person outside the project can run.

## §24.4 — Budget and sequencing

| Session | Deliverable | Est. cost |
| ------- | ----------- | --------- |
| 1 | D1 scaled cell (arm plumbing + 3-seed round) | ~1-2 h |
| 2 | D3 stacking repair + reach-dial curve | ~1 h |
| 3 | D2 multi-ψ demo + gallery lock + promotion decision | ~2 h |

Cell costs at probe scale were 18-35 s; the scaled cells are the first
non-toy runs — budget in cells, not wall-clock hopes (§13.1-5), and
checkpoint before diagnosing (TODO.ntm_nca.md §12 rule, adopted here).
