# TODO17.md — The P-Axis as Computational Expressiveness: Unfolding Kolmogorov Complexity

> **Opened 2026-09-10.**
>
> **CURRENT FOCUS:** TODO16 mapped the P-axis as an *adaptation-and-efficiency
> layer* and found boundaries. TODO17 re-frames and re-tests the P-axis as a
> **computational-expressiveness axis**: the mechanism by which a fixed
> substrate unfolds arbitrarily deep computation, bounded only by time and
> memory. This is the "escape hatch" beyond fixed-depth ML. NTM is the tape,
> NCA is the emergent fabric, ψ is the program.
>
> **Constraint:** No cell exceeds **5 min** (10-min exception for the
> predictive-model fit only). Background anything longer
> (`nohup … > logs/<name>.log 2>&1 &`, poll ≤ 2 min, pre-registered kill).
> CPU-only (GPU is ~3× slower at probe scale per §11.6).
>
> **Doctrine (carried forward, non-negotiable):** *Autopsy before training.
> Prediction before measurement. Checkpoint first, diagnose second. Recorded-
> source verdicts count. Composition before invention. Feasibility-isolation
> ladder before any training.*
>
> **Ratchet policy:** REACTIVE ONLY. Lock defects we encounter, never
> hypothetical bugs.

---

## §0 — The Central Reframe

TODO16 asked: *"What can the P-axis do **without** changing θ?"* and answered:
select, route, recover, gate — narrow, bounded, a capability footnote.

That was the wrong question. It evaluated the P-axis as one more ML-capability
axis ("can it beat backprop on task X?") when the P-axis is a
**computational-expressiveness axis** ("can it represent computation that the
fixed architecture cannot?").

### The argument

Standard ML embeds the "program" implicitly in the weights. The function a
network computes is bounded by its depth × width — the computational complexity
it can represent *efficiently* is capped by the architecture. A depth-32 MLP
expresses only functions decomposable into 32 bounded-width transformations.

The P-axis + external memory changes the class of computable functions:

```
θ           =  fixed hardware       (the operational repertoire)
ψ           =  the program           (data: written, read, composed, sequenced)
NTM memory  =  the tape              (unbounded intermediate storage)
NCA state   =  the emergent fabric   (spatially-distributed computation)
```

A program of Kolmogorov complexity $K$ can be **unfolded over time** on a
substrate of fixed architectural depth $D$, using $O(K/D)$ sequential steps and
$O(K)$ memory. The architecture need not be deep — it must be able to *execute
a sequence of simple steps, storing intermediate results*. This is exactly how a
universal Turing machine works: fixed hardware, unbounded computation, limited
only by time and tape.

> **The P-axis is the axis that elevates the computational rule from a fixed
> property of the architecture to a dynamical variable that can be written,
> composed, and sequenced — enabling a fixed substrate to unfold arbitrarily
> deep computation.**

### Why NTM and NCA are essential (not "just another geometry")

| Component | Role in the computational story |
|---|---|
| **NTM memory** | The tape. Without it, ψ does O(1) work per step (bounded by plastic-state dim). With it, ψ unfolds arbitrarily long computation by writing/reading intermediates. This is the difference between a finite automaton and a Turing machine. |
| **NCA substrate** | The emergent fabric. Complex global behavior unfolds from local rules. The P-axis on NCA means the *rules themselves* are reconfigurable — the computational fabric is programmable, not just the output. |
| **ψ (the P-axis)** | The program counter + instruction decoder. Decides the next operation, reads/writes memory, sequences steps into algorithms. |

### What frozen-θ actually is (correcting TODO16's framing)

Frozen-θ is an **experimental control**, not a design principle. It isolates
what ψ contributes. In a mature system θ and ψ co-adapt: θ learns the hardware,
ψ runs the software. The separation is what makes the system a **machine**
rather than a function approximator. TODO17 uses frozen-θ where it isolates a
mechanism, and co-adaptation where the question demands it.

---

## §1 — What TODO16 Established (the boundary map we inherit)

TODO16 is **closed** (all 10 success criteria met). We inherit its verified
results and must not re-run them:

| Result | Verdict | Carried into TODO17 as |
|---|---|---|
| I(C,U) law predictive | 0.944 held-out lattice | Foundation; extend to I(C,U,P) |
| Routing | Decaying mitigant (94% @d50, 62% @d100); does NOT break depth frontier | Depth frontier is representation-limited; expressiveness must come from ψ×memory, not gating |
| FastWeight vs fixed Hebbian | Learned ψ-writes add **nothing** over fixed Hebbian on ordinary tasks; ψ is causal (ablation −23 pts) | Ordinary tasks cannot discriminate; use retrieval-demanding tasks |
| Z3 toy | **ALIVE** — operator selection works, θ bitwise invariant | The selection machinery is real; Z3 full failed on *operator coverage*, not selection |
| Z3 full | Falsified — operator-coverage limit (no fixed operator carries global-mean/cumsum feature) | The library must be grown *or* ψ must *compose* primitives — E4 tests composition |
| Stability-plasticity | Biconditional confirmed intrinsic; cost is update-geometry-conditional (Muon absorbs, Euclid pays) | Use Muon for any ψ-reconfiguration cell |
| Transport graph | Fixed writes **strictly dominate** learned addressing on explicit-key recall (1.000 vs 0.63) | For E4, use fixed orthogonal writes (slot-capped/linear-read), not learned heads |
| Value binding | Structural limit of zero-history factorization (acc_given_hit 0.63) | E4 must address value binding or scope claims accordingly |
| Campaign 7.1 | ψ does **NOT** modulate I(C,U) surface on clean MNIST | ψ is a passenger on the credit×update surface — expressiveness is orthogonal to I(C,U) |
| Campaign 7.2 | Stability cost of reconfiguration is optimizer-conditional | Confirms Muon for P-axis cells |

**Key inheritance:** The Z3 selection machinery works (Z3 toy alive). The failure
of Z3 full was *operator coverage*, and the failure of FastWeight was *task
choice* (ordinary task). TODO17 attacks the two real gaps: **composition over a
primitive set** (not selection over a fixed library) and **memory-backed
unfolding** (on retrieval-demanding tasks).

---

## §2 — Status Discipline (carried forward, extended to papers)

A result occupies one of four states: **Promoted / Open / Reopened / Boundary.**
A "falsified" result is not automatically a "boundary" — a boundary requires:
known defects addressed + appropriate optimizer tested + signal/mechanism
verified + matched controls + multi-seed confirmation.

**NEW for TODO17 — Paper status:**

| Paper status | Meaning |
|---|---|
| `active_draft` | Claims stable, evidence complete, writing in progress |
| `parked` | Evidence complete but no viable headline; awaiting a new result or a fold decision |
| `blocked` | A claim depends on an open cell |
| `published` | Shipped; claims frozen against the release commit |
| `retracted` | A core claim was overturned; preserved as negative-result record |

---

## §3 — Phase A: Ship the Consolidation (~45 min, all cells ≤5 min)

Three infrastructure deliverables that convert TODO16's verified capabilities
into shippable, citable artifacts. **Do these first** — they unblock every
experiment's claim.

### §3.1 Paper-Tracking Infrastructure (~20 min)

**What:** Mirror the demo-gallery discipline for papers.

Create `computronium/papers/registry.py`:

```python
PAPERS = {
    "icu_law": {
        "title": "The Geometry of Local Credit: How Optimizer Displacement "
                 "Dictates Learnability",
        "status": "active_draft",
        "claim_tiers": ["Tier D"],
        "evidence": {
            "figures": ["d19_depth_harvest", "d2_swap_credit"],
            "run_records": ["logs/w1_credit_ladder.log",
                            "data/icu_measurements.csv"],
            "held_out_validation": 0.944,
        },
        "gaps": [],
    },
    "p_axis_expressiveness": {
        "title": "Plasticity as Computation: Unfolding Kolmogorov Complexity "
                 "on a Fixed Substrate",
        "status": "blocked",   # blocked on E1–E4
        "claim_tiers": ["E1", "E2", "E3", "E4"],
        "evidence": {},
        "gaps": ["E1 algorithmic-depth cell", "E4 sequential-composition cell"],
    },
    "p_axis_boundaries": {
        "title": "What Frozen Weights Can and Cannot Do",
        "status": "parked",   # folds into icu_law as negative result
        "claim_tiers": ["L2/L3 benchmarks", "Z3 toy", "campaign 7.1"],
        "evidence": {"figures": ["d17_multi_psi_swap"]},
        "gaps": ["needs a positive headline or folds into icu_law"],
    },
}
```

**The lock:** `tests/integration/test_paper_claims.py` — every claim in every
`active_draft` must resolve to an existing artifact:
- figure → `docs/figures/run_records/*.json` exists and passes its lock
- log → file exists and contains the cited number
- held-out metric → reproducible by running the cited probe

A claim without a backing artifact fails the test.

**Decision to record:** `p_axis_boundaries` **folds into `icu_law`** as the
"plasticity does not modulate the credit×update surface" negative-result section.
It does not stand alone (no positive headline). Record this fold in the registry.

### §3.2 Figure Fairness: Param-Count Labels (~15 min)

**Why:** G-axis comparisons (MLP vs NTM vs NCA vs Transformer) are unfair if
capacity silently mismatches. The demo figures currently omit parameter counts.

**Fix (three parts):**

1. **Extend run-record schema** — add `param_count` per arm. Compute via
   `sum(p.numel() for p in system.parameters())` at arm construction; store at
   record-write time.

2. **Render on figure + caption** for G-axis demos:
   - **D19 depth_harvest:** annotate `(d=32, 1.0M params)` / `(d=50, 1.6M params)`
     — makes visible that depth-50 gets 1.6× the parameters.
   - **D20 ntm_local:** annotate bptt vs local3 with matched param counts (they
     are matched — same `NtmGeometry` — but the figure must *say so*).
   - **D17 multi_psi_swap:** annotate backbone param count once; note ψ is a
     per-task additive cost (one ridge solve, not θ).

3. **Lock assertion** in `test_gallery_lock.py`: any demo whose registry entry
   declares a G-axis comparison must have `param_count` present for every arm.
   This turns the label into a lock-gated requirement.

### §3.3 README.md Update (~10 min)

Update the README to reflect the new P-axis understanding and the functionality
developed across TODO13–TODO17.

**(a) P-axis reframe** — in the *Six-Dimensional Decomposition* table and the
*Coupled Dynamical Systems* section, replace the P-axis description. Current
role column reads "Mechanism making the computational rule a dynamical variable."
Extend it to:

> **Plasticity (MetaDynamics)** $P$ — Mechanism elevating the computational rule
> to a dynamical variable. With external memory (NTM) and emergent substrates
> (NCA), ψ enables a fixed substrate to *unfold arbitrarily deep computation* —
> the program becomes data that can be written, composed, and sequenced. This is
> the axis of computational expressiveness: fixed hardware (θ), reconfigurable
> program (ψ), unbounded tape (NTM memory).

**(b) New functionality to add** to the *ML Library Capabilities* table and
relevant sections:

| Functionality | Where it lives | Provenance |
|---|---|---|
| **NCA geometry** (`NcaGeometry`, `GeometryConfig.nca`) | `ontology/geometry.py` | TODO.ntm_nca §11.8 — local credit solves growing NCA (fg 1.000, 3 seeds) |
| **NTM geometry** (`NtmGeometry`, `GeometryConfig.ntm`) | `ontology/geometry.py` | TODO.ntm_nca §11.14 — local credit learns copy via external memory (0.958 @8000) |
| **EMA harvest instrument** (`SystemTrainerConfig.harvest_mode`) | `SystemTrainer` | TODO15 §13.3 / TODO16 §0.1 — resurrected depth-50 (0.784→0.917) |
| **PepitaCredit** (published PEPITA, input-modulation) | `ontology/credit.py` | TODO15 §11.2 — BP parity 0.884 |
| **LEMMA naming distinction** (`local_objective="lemma"`) | `ontology/credit.py` | TODO15 §11.1 — separates input-modulation from per-layer closed-form |
| **Recipe cards** (`recipe_cards.py`) | `computronium/analysis/` | TODO16 §0.3 — family→optimizer/geometry/config registry |
| **I(C,U) predictive model** (`fit_icu_model.py`, `icu_report.py`) | `scripts/analysis/` | TODO16 §4 — 0.944 held-out lattice |
| **Inertness guard** (RandomProjectionsCredit warns on all-zero) | `ontology/credit.py` | TODO16 §0.3 |
| **Transport-graph probes** (`w16_transport_grid.py`) | `scripts/probes/` | TODO16 §6.1 — fixed writes dominate learned addressing |
| **Z3 operator selection** (`z3_toy.py`, `z3_full.py`) | `scripts/probes/` | TODO16 §2.3/§3A — selection works, coverage-limited |
| **Plasticity-wired benchmarks** (L1/L2/L3/L3.5, `psi_engaged`) | `experiments/joint/` | TODO16 §5 — frozen-θ ψ-only adaptation/recovery |

**(c) Terminology discipline** — ensure the README keeps the simulated/estimated/
hardware-measured energy distinction and does not over-claim the P-axis (it is a
research hypothesis, not a validated capability, until E1–E4 land).

---

## §4 — Phase B: The Expressiveness Probes (E1–E4)

Four probes, in ascending ambition, each pre-registered. All build on existing
promoted primitives (`NtmGeometry`, `NcaGeometry`, Z3 machinery). **Muon is the
default update for any ψ-reconfiguration cell** (campaign 7.2: Muon absorbs
reconfiguration stability cost). **Fixed orthogonal writes are the default
memory** (campaign 6.1: fixed writes dominate learned addressing).

### §4.1 E1 — Algorithmic Depth Beyond Architecture Depth

**Question:** Can ψ + NTM memory solve a task requiring $N$ sequential steps,
where the architecture has depth $D \ll N$?

**Why it's the escape hatch:** If yes, computational depth is unbounded (limited
by time + memory), decoupled from architectural depth. This is the single most
direct test of the Kolmogorov-unfolding thesis.

**Design:**
- Task: **iterated recurrence** — compute the $N$-th element of a recurrence
  (e.g., Fibonacci mod $k$, or an $N$-step counter/parity chain). Vary
  $N \in \{4, 8, 16, 32\}$.
- Architecture: fixed-depth controller ($D = 4$) + `NtmGeometry` memory
  (slot-capped, width 16, the §11.16 recipe).
- ψ: sequences $D$-step chunks. Each chunk reads the current intermediate from
  memory, applies one recurrence step, writes the new intermediate back. Iterate
  $N/D$ times.
- Update: Muon (reconfiguration-stable). Memory write: fixed orthogonal.

**Arms:**
1. `null` — no ψ, no memory (fixed-depth baseline; should collapse as $N/D$ grows)
2. `memory_no_psi` — NTM present, no ψ sequencing (BPTT through memory)
3. `psi_sequential` — ψ sequences chunks over memory (the expressiveness arm)

**Pre-registered prediction:** `psi_sequential` accuracy is **independent of $N$**
(up to memory capacity) while `null` collapses monotonically with $N/D$.

**Falsification:** `psi_sequential` accuracy drops with $N$ at the same rate as
`null` → ψ is a fixed-depth adapter, not an unfolding mechanism. Expressiveness
thesis falsified at this task class.

**Cost:** ~3 min/cell × 3 arms × 4 values of $N$ × 3 seeds = 36 cells.
**Background** (3 parallel). ~36 min total walltime.

**Value-binding caveat (from TODO16 §5.4):** zero-history value binding is the
known structural limit. If `psi_sequential` solves addressing but fails value
binding, record it and scope the claim to "ψ sequences addressing over memory;
value binding remains the bottleneck." Do not silently broaden.

### §4.2 E2 — Kolmogorov Compression via ψ-Programs

**Question:** Can a SHORT ψ-program unfold into a complex output?

**Why it matters:** This is the direct Kolmogorov-complexity measurement.
Learning-as-compression: if ψ can generate a long structured output from a short
program, the P-axis is doing real compression, not readout.

**Design:**
- Target: a structured spatial pattern — a **procedural sprite field** or a
  self-similar fractal on a 32×32 grid (NCA-native).
- Measure: **compression ratio** $= |\text{output}| / |\psi|$, where $|\psi|$ is
  the number of free parameters in the ψ-program and $|\text{output}|$ is the
  number of bits in the pattern.
- ψ unfolds the pattern over $T$ rollout steps (NCA dynamics). Vary $T$.

**Arms:**
1. `readout_adapter` — ψ directly encodes the output (no unfolding). Expected
   ratio ≈ 1.
2. `unfolded_psi` — ψ encodes a *rule* that generates the output over $T$ steps.

**Pre-registered prediction:** `unfolded_psi` achieves compression ratio $\gg 1$
(short program, long output), and the ratio grows with $T$. `readout_adapter`
stays ≈ 1.

**Falsification:** `unfolded_psi` ratio ≈ 1 → ψ must encode the entire output;
no unfolding occurs. Kolmogorov-compression claim closed.

**Cost:** ~5 min/cell (NCA rollout + ψ solve) × 2 arms × 3 patterns × 3 seeds
= 18 cells. **Background.** ~30 min.

**Connection to existing work:** This extends TODO.ntm_nca §11.13 (label-free
regeneration was real; label-free *growth* was a representation boundary). E2
asks whether ψ can supply the missing positional/recursive structure that
label-free growth lacked.

### §4.3 E3 — NCA Rule Reconfiguration for Pattern *Generation*

**Question:** Can ψ change the NCA rules to generate **different** spatial
patterns from the same seed?

**Why it matters:** Regeneration (fill a hole in a known target) is the regime
TODO.ntm_nca already solved. *Generation of distinct patterns from a shared seed
via rule selection* is the expressiveness claim: O(log K) ψ-bits → O(K) distinct
outputs.

**Design:**
- Train `NcaGeometry` with rule set $R_1$ to generate pattern $P_1$ from seed $s$.
- With θ frozen, change ψ to select rule set $R_2$; generate $P_2$ from the same
  seed $s$. Assert θ bitwise invariance (SHA).
- Vary the number of selectable rule sets $K \in \{2, 4, 8\}$.

**Arms:**
1. `single_rule` — one rule, regenerates only $P_1$ (control)
2. `psi_rule_select` — ψ selects among $K$ rules, θ frozen

**Pre-registered prediction:** the number of distinct generated patterns grows
with $K$ (exponentially if ψ encodes rule combinations), with exact θ invariance.
`single_rule` produces only $P_1$.

**Falsification:** `psi_rule_select` produces only $P_1$ regardless of ψ, or θ
changes → ψ cannot reconfigure the computational fabric. Expressiveness claim on
NCA closed.

**Cost:** ~3 min/cell × 2 arms × 3 values of $K$ × 3 seeds = 18 cells.
**Background.** ~18 min.

**Stability note:** use Muon for the rule-training phase (campaign 7.2). Track
ρ(J_F) — rule reconfiguration may sacrifice contraction margin (the §2.4
biconditional), and that cost is expected and measurable, not a defect.

### §4.4 E4 — Sequential Composition on NTM (The Real Z3)

**Question:** Can ψ implement a multi-step algorithm by **composing** primitive
operations and using memory for intermediate state?

**Why it's the decisive one:** Z3 toy proved *selection* works. Z3 full failed on
*coverage* (fixed library lacked the needed operators). E4 tests the real
capability: **sequencing + composition + memory**, not selection over a fixed
library. This is the experiment that most directly realizes the user's vision.

**Design:**
- Give ψ a small **primitive set**: `{read, write, add, compare, branch}` — the
  minimal instruction set of a counter machine.
- Task: synthesize a multi-step algorithm requiring intermediate state — e.g.,
  "read three values, sort them, write the median" or "compute the max of an
  $N$-element list."
- ψ must **sequence** primitives and use NTM memory for intermediates. Architectural
  depth $D = 4$; algorithm requires $O(N)$ steps.
- ψ-program is *written by a closed-form solve* (Z3-toy ridge machinery) or
  *searched* over primitive sequences — record which.

**Arms:**
1. `single_op` — ψ selects one primitive (the Z3-toy regime; should fail on
   tasks needing intermediates)
2. `composed_ops` — ψ sequences primitives over memory (the expressiveness arm)

**Pre-registered prediction:** `composed_ops` solves tasks requiring $O(N)$ steps
with $O(1)$ architectural depth; `single_op` fails on any task needing
intermediate state. Adaptation is fast (episodes to acquire the ψ-program ≪
episodes to train θ).

**Falsification:** `composed_ops` fails on all tasks requiring intermediate state
→ ψ cannot sequence/compose; the expressiveness thesis is closed for this
primitive set. (If it fails only on value-binding-heavy tasks, scope accordingly
per §4.1's caveat.)

**Cost:** ~5 min/cell × 2 arms × 3 tasks × 3 seeds = 18 cells. **Background.**
~30 min.

**Reuse:** build on `z3_toy.py`'s frozen-θ + SHA-invariance + closed-form-ψ
infrastructure. Extend the operator set from "fixed callables" to "primitives
that read/write a shared tape."

### Phase B stop-loss

If **all four** of E1–E4 falsify: the P-axis expressiveness thesis is closed at
probe scale. Record the boundaries with mechanisms. Fold the negatives into
`icu_law` (per §3.1) as the definitive "what ψ cannot do" section. Do not
theorize. **But note:** even partial survival (e.g., E1 alive, E4 dead) is a
major result — it localizes *which* expressiveness mechanism is real.

---

## §5 — Phase C: Integration & Prediction (gated by Phase B survival)

### §5.1 Extend the predictive model to I(C,U,P)

If any E1–E4 probe is alive, add its data to `data/icu_measurements.csv`
(schema already has a `plasticity` field). Refit `fit_icu_model.py`. Test
whether ψ is a *third axis* of the interaction law or orthogonal to it
(campaign 7.1 said orthogonal on clean MNIST; E1–E4 test retrieval-demanding
tasks, where the answer may differ).

**Cost:** ~10 min (the one 10-min exception).

### §5.2 The stability-plasticity-expressiveness frontier

Combine campaign 7.2 (stability cost is optimizer-conditional) with E3's
ρ(J_F) measurements. The hypothesis: **expressiveness (rule reconfiguration,
pattern generation) is achievable within a stability budget that Muon's
displacement geometry absorbs.** Ship as an extension of `icu_report.py`.

### §5.3 AutoScientist campaign (optional, background)

If E1 or E4 is alive, run a bounded 6-D campaign varying P × memory-type on the
winning task:

```yaml
campaign: expressiveness_memory_sweep
fixed: {S: Digital, G: NtmGeometry, D: InstantaneousPass}
varied: P × memory_write_rule = {null, psi_sequential} × {slot_capped, linear_read, hebbian}
hypothesis: "expressiveness is memory-write-rule-conditional"
```

~2 min/cell, background. Only run if Phase B survives.

---

## §6 — The P-Axis Thesis (what TODO17 is trying to establish)

One sentence:

> **The P-axis elevates the computational rule from a fixed property of the
> architecture to a dynamical variable that can be written, composed, and
> sequenced — enabling a fixed substrate to unfold arbitrarily deep computation,
> bounded only by time and memory.**

| Probe | Which part of the thesis it tests |
|---|---|
| E1 | "arbitrarily deep computation" (depth decoupled from architecture) |
| E2 | "bounded only by memory" (Kolmogorov compression) |
| E3 | "the computational rule is a dynamical variable" (fabric reconfiguration) |
| E4 | "written, composed, and sequenced" (program synthesis over a tape) |

If E1–E4 survive, the P-axis graduates from "adaptation footnote" to **flagship**
— the thing that makes Computronium more than "local learning rules on standard
architectures." The `p_axis_expressiveness` paper unblocks.

---

## §7 — Probe Rules (carried forward, §19)

Every new probe must specify before execution:

```
question, mechanism, prediction, control, budget, metric,
falsification criterion, overturn criterion
```

For optimistic hypotheses, the positive result receives the same matched-step/
token control, multi-seed test, defect audit, capacity check, and reproduction as
a negative result. **Single-seed reopen is sufficient to change status; 3-seed +
§20 round is required for a headline.**

---

## §8 — Defect-Hunt Protocol (carried forward, §17)

Before promoting any failure to **Boundary**, audit:
- **Signal integrity** — positive vs negative stream differ; target reaches
  intended component; no normalization removes the contrast; train/eval match.
- **State integrity** — ψ written back; fast state not silently reset; persistent
  θ unchanged when supposed frozen; episode boundaries correct.
- **Update integrity** — correct LR axis; actual optimizer displacement; no global
  clip crushing local signals; matrix optimizer not applied to vectors/biases.
- **Measurement integrity** — matched steps/tokens; capacity ratio asserted;
  **param-count matched for G-axis comparisons (§3.2)**; same loader draws; seed
  before loader draw; `batches_seen ≥ budget`.
- **Resource integrity** — peak ≠ cumulative; simulated ≠ measured energy.

**Known traps to re-check in E1–E4** (each cost a verdict before):
- weight-name substring contract (`apply_pseudo_gradients` pairs only keys
  containing "weight") — TODO.ntm_nca §11.5 defect 1
- scrambled-reshape on per-cell substrates (invisible to cell-space losses) —
  §11.8
- loader-capping silently truncating budget — TODO15 §14.1 / §17.5
- slot-identity collision when `mem_slots > mem_width` — §11.16
- signed content unretrievable by cosine softmax — §11.10
- cold-start addressing impossibility (need slot embeddings) — §11.10

---

## §9 — Execution Spine

| Session | Focus | Foreground | Background launched |
|---|---|---|---|
| 1 | Phase A: paper registry + claim lock; param-count labels + lock; README update | ~45 min | — |
| 2 | E1 (algorithmic depth) + E2 (Kolmogorov compression) | ~15 min | 36 + 18 cells |
| 3 | E3 (NCA rule reconfiguration) + E4 (sequential composition) | ~15 min | 18 + 18 cells |
| 4 | Phase B verdicts; §5.1 I(C,U,P) refit (if alive) | ~25 min | §5.3 campaign (if alive) |
| 5 | Integration: §5.2 frontier report; unblock `p_axis_expressiveness` paper; re-pin gallery | ~25 min | — |

**Total foreground:** ~2 hours across 5 sessions.
**Total background:** ~2.5 hours (all parallel, thread-capped OMP=2, max 3 concurrent).

---

## §10 — Stop-Loss Conditions (hard)

1. **All of E1–E4 falsify** → P-axis expressiveness closed at probe scale.
   Fold negatives into `icu_law`. Do not theorize. The boundaries are the result.
2. **E1 falsifies but E4 survives** (or vice versa) → the expressiveness thesis
   is *mechanism-localized*, not dead. Record which mechanism is real; pivot
   Phase C to that mechanism only.
3. **Value binding blocks E1/E4** → scope claims to addressing/sequencing; record
   value binding as the structural limit (per TODO16 §5.4). Do not silently
   broaden to "ψ solves retrieval."
4. **The paper-claim lock fails on `icu_law`** → fix the evidence gap before any
   E-probe claim is written. Claims without artifacts do not ship.
5. **Any cell exceeds 5 min foreground** → background it per the standing policy.
   No exceptions except the §5.1 model fit (10 min).

---

## §11 — What We Must Not Prematurely Conclude

Do **not** conclude (until the relevant probe lands):
- the P-axis is "just an adaptation layer" (TODO16's framing — under test)
- ψ cannot unfold computation (E1 pending)
- ψ cannot compress / generate (E2, E3 pending)
- ψ cannot compose primitives (E4 pending)
- value binding is *always* the bottleneck (may be task-dependent; E1/E4 test)
- fixed writes dominate on *all* retrieval tasks (only explicit-key recall tested;
  E4 uses richer tasks)
- the I(C,U) law is unaffected by ψ on retrieval-demanding tasks (campaign 7.1
  tested clean MNIST only)
- expressiveness requires new ontology primitives (composition before invention —
  E1–E4 build on existing `NtmGeometry`/`NcaGeometry`/Z3 machinery)

---

## §12 — Success Conditions

TODO17 succeeds if it produces at least one of:

1. **E1 alive:** ψ + memory solves a task with algorithmic depth $N$ at
   architectural depth $D \ll N$, accuracy independent of $N$.
2. **E2 alive:** unfolded ψ achieves compression ratio $\gg 1$, growing with $T$.
3. **E3 alive:** ψ generates $O(K)$ distinct patterns from $O(\log K)$ ψ-bits
   with exact θ invariance.
4. **E4 alive:** ψ sequences primitives over memory to solve an $O(N)$-step task
   at $O(1)$ architectural depth.
5. **The paper pipeline ships:** `icu_law` moves to `published`-ready;
   `p_axis_expressiveness` unblocks (or is honestly parked with the fold recorded).
6. **The consolidation ships:** paper-claim lock green, param-count labels live
   and lock-gated, README reflects the P-axis reframe + TODO13–17 functionality.

**The largest outcome:** E1 + E4 both alive → the P-axis is a genuine
computational-expressiveness axis, and Computronium demonstrates a qualitatively
different training regime: *fixed substrate, unbounded computation, local credit,
local interactions.* That is the search for computronium realized.

---

## §13 — Final Research Principle

> **The P-axis is not a way to adapt faster. It is a way to compute more.**
>
> Test it as computation, not as adaptation.
> Give ψ a tape before judging its depth.
> Give ψ primitives before judging its operator library.
> Give ψ a seed before judging its generation.
> Use Muon for reconfiguration; use fixed orthogonal writes for memory.
> Respect the value-binding boundary; scope claims to what the probe measured.
> Reopen TODO16's "adaptation footnote" framing before promoting it to doctrine.
>
> **The objective is not to make the P-axis win.**
> **The objective is to discover whether a fixed substrate can unfold
> unbounded computation — and, if it can, to build the machine that does.**

---

## §14 — Cost Ledger & Time Budget

| Cell type | Budget | Method |
|---|---|---|
| E1 algorithmic-depth cell | ≤3 min | NTM + ψ, Muon, fixed writes |
| E2 Kolmogorov cell | ≤5 min | NCA rollout + ψ solve |
| E3 rule-reconfiguration cell | ≤3 min | NCA + ψ, Muon, θ frozen |
| E4 sequential-composition cell | ≤5 min | NTM + primitive ψ, Muon |
| I(C,U,P) model refit | ≤10 min | **the 10-min exception** |
| Paper-claim lock test | ≤1 min | artifact resolution |
| Param-count re-pin | ≤3 min | render_gallery over run_records |

**Rules:** background anything > 5 min; poll ≤ 2 min; pre-register kill time.
OMP_NUM_THREADS=2, max 3 concurrent. CPU-only. Assert `batches_seen ≥ budget`.

**Inherited process guardrails (TODO.ntm_nca §12):** never `pkill`/`pgrep -f`
(kill by explicit PID); checkpoint first, diagnose second; run from repo root;
pre-verdict smoke gate (‖Δw‖ > 0, muon ≠ euclid step) before any multi-cell launch.

---

## §15 — File Inventory & Restart Protocol (for a fresh context)

**Existing probes to reuse (do not rebuild):**
- `scripts/probes/z3_toy.py`, `z3_full.py` — frozen-θ + SHA-invariance + closed-form ψ
- `scripts/probes/w8_ntm_copy.py` (REV r7) — NTM copy/recall, `--width` slot fix
- `scripts/probes/w8_nca_local.py` (REV r10) — NCA, distill-init, `--regen`
- `scripts/probes/w16_transport_grid.py` — fixed-write memory types
- `scripts/probes/w16_campaign.py` — 6-D campaign driver
- `scripts/analysis/harvest_icu_table.py`, `fit_icu_model.py`, `icu_report.py`
- `computronium/analysis/recipe_cards.py`

**Promoted primitives:** `NtmGeometry`, `NcaGeometry`, `PepitaCredit`,
`SystemTrainerConfig.harvest_mode`.

**Restart protocol:**
1. Dev-env smoke: `uv run python -c "import optuna, scipy, torchvision, pytest"`.
2. Read §1 (inherited boundary map) before running anything — do not re-run
   TODO16 cells.
3. Execute Phase A first (§3): it unblocks every claim.
4. Then Phase B (E1–E4), pre-registered, backgrounded, thread-capped.
5. Joint suites are slow-marked: run
   `uv run python -m pytest tests/integration/joint/test_benchmarks.py -m slow`.

---

*The boundaries are mapped. The capabilities are verified at probe scale. The
question TODO17 answers is the one the project was founded on: **can a physical,
local, fixed substrate unfold unbounded computation?** The P-axis is the answer.
Go find out if it's yes.*

