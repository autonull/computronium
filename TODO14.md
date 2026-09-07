# TODO14.md — Overturn the Boundaries, Compose the Winners

> **Opened 2026-09-07.**
>
> TODO13b made the instrument honest. TODO14 asks what happens when we apply
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
