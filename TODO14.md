# TODO14.md — Overturn the Boundaries, Compose the Winners

> **Opened 2026-09-07.**
>

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

- ~~W6 promotion~~ DONE — Tier C closed (see above).
- W0: muon_mid with cosine-decayed step past 600 steps (tests the
  decay-past-peak lever directly); readout_scale sweep 0.3/3.0.
- W4 (§10): hidden-layer closed-form ψ, one layer, MNIST Task A→B; the
  ‖Δθ‖=0 bitwise gate is cheap to assert (~10 min).
- W1 (§7): credit ladder under muon — random-projection + noisy arms on
  MNIST d4, 150 batches (reuses hunt harness; ~5 min/cell).
- W0.2 (§4): DONE — falsified, deprioritized (see above).
- W5 (§11): depth-50 budget cell (300–600 batches) — long-run session.

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
| **PEPITA fixed-projection collapse**                | Learned-feedback alignment and co-adaptation were not tested; learned-B × Muon remains open.                                                                                         | Learned-feedback PEPITA × Muon; then co-adaptive feedback                                   |
| **P2 frozen-error LM failure**                      | Exact inference-network ε, γ, width-512, and steps > H cells remain untried.                                                                                                         | Targeted ε × γ × width × depth-horizon cells                                                |
| **D17 BP late-regime advantage**                    | The late deficit may be the Muon axis rather than credit.                                                                                                                            | ff_hybrid × OrthoAdam/Adam at ≥3M tokens                                                    |
| **STDP collapse**                                   | Reward-/error-modulated STDP is the missing supervised term.                                                                                                                         | TemporalTraceCredit + reward/error modulation                                               |
| **Closed-form ψ ceiling**                           | The demonstrated law is readout-only; frozen features necessarily impose a linear-probe ceiling.                                                                                     | Per-layer hidden closed-form ψ                                                              |
| **Depth-50 collapse**                               | Measured under a finite data/budget regime; classified as memorization, not a fundamental dynamical failure.                                                                         | Budget × regularization × depth-50 autopsy                                                  |
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
