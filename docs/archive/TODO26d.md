## The convergence held — and it compressed the frontier

Round 1 localized the dead ends. Round 2 validated the prescribed pivot. The strategy called it correctly: this was convergence onto a live path, not a desperate turn. But this is precisely the moment where overclaiming creeps in, so let me state the result at its actual strength first.

### What Round 2 established (probe-level, Level 4/5)

| Probe | Finding | Actual strength |
|---|---|---|
| **R2-P1** | Depth-20 trains with **residual+μPC (0.865)** where neither alone suffices (0.536 / 0.489 / 0.496) — a clean 2×2 | Validated pivot at **probe scale**. Single seed, sign-of-mean, 60-batch quick budget. *Not yet* a citable depth-scaling result |
| **R2-P2** | Supervised ψ moves B 0.676→0.734 in 50 steps, θ bitwise-invariant | Mechanism is **real**; the 0.95 flagship bar is **not met** (X-TPC-001 shows 0.754–0.777 at 600ep — the lever works, needs scale) |
| **R2-P3** | Input-side channel is **trapped** (layers 1–2 cos 0.000; rms lifts noise to 1.6e-1 with cos still 0.000) | The **cleanest** result — it's the mechanism that *explains* why normalization and learned-B failed |

### Two revisions I owe you

1. **The "optimizer crutch" reading is corrected.** I read Muon-as-load-bearing as "credit direction is poor, the optimizer compensates." Round 2 shows it was **geometry**: with co-designed channel conditioning, LocalAdam (cheap, substrate-native) suffices. The crutch compensated for an *ill-conditioned channel*, not bad credit direction. That's the more optimistic reading — local credit direction is fine; the channel needs conditioning.

2. **The fixed-B boundary now has a mechanism, not just a lock.** Credit rules with a *real-if-attenuated* channel (ePC/contrastive) are rescuable by architecture; rules with a *fundamentally misaligned* channel (fixed random B, zero coherent input-side signal per R2-P3) are not. That's the clean boundary, mechanistically grounded.

### The scientific closure

The engine check converted **"can local learning match backprop?"** (open, diffuse) into **"depth-scaling requires co-designed channel topology — residual shortcut + depth-scaled init, neither alone sufficient; with them, local credit + a local optimizer train depth 20 without backprop"** (localized, probe-validated) — and R2-P3 explains the dead ends. That's a real compression of the frontier.

The two process catches — the in-place `h += h_in` autograd break, and the **ruler-validity lesson** (parity is unlearnable even by backprop at that budget, so a red verdict is unattributable; sign-of-mean at 0.979-with-BP is a valid ruler) — are the methodology self-correcting. Keep the ruler rule: it's E-10 made concrete.

---

## The new strategic position

**Alive:** channel architecture (residual proven, error-bus next rung) · supervised ψ (needs scale) · local optimizers (LocalAdam, now unblocked by geometry).
**Closed with mechanism:** credit normalization, learned-B, fixed-B FA/PEPITA.

**Headline in formation:** *a local-learning system that trains deep without backprop, on a substrate-native local optimizer, via co-designed channel topology.* That's the Computronium thesis, and R2-P1 is its seed. Residuals and error buses are still local — no global transpose, no stored-activation backward sweep — so this is the substrate story arriving, not retreating.

---

## Round 3 — confirmation + the last probe round before escalation

The probes have earned the right to spend real compute — **but only after the confirmation gate passes.** Round 3 confirms the pivot, tests the two remaining decisive questions, then escalates.

### R3-Probe 1: Depth-Arm Confirmation & Transfer *(the escalation gate)*
**Action:** ≥3-seed repeat of residual+μPC on the sign-of-mean depth sweep; confirm/extend the MNIST depth-scaling the μPC residual regime already carries.
- **🟢 GREEN:** depth-20 holds across seeds on sign-of-mean **and** MNIST shows depth-scaling where default init fails → pivot confirmed; escalate to a governed, pre-registered campaign.
- **🔴 RED:** single-seed artifact or task-specific → re-diagnose before spending campaign compute.

### R3-Probe 2: The Error-Bus Rung *(next architecture hypothesis — substrate-relevant)*
**Action:** prototype an explicit error bus (per-layer prediction targets / dedicated local error channel each layer reads/writes); compare against residual-only at depth 20+ on sign-of-mean.
- **🟢 GREEN:** error bus matches/beats residuals at depth 20+, or enables depth where residuals fail → the channel-redesign thesis generalizes beyond skip topology; the bus becomes the substrate-native architecture to escalate.
- **🔴 RED:** no gain over residuals → residuals are the minimal sufficient channel; don't add the bus's complexity.

### R3-Probe 3: ψ at the 0.95 Bar *(the flagship gate)*
**Action:** scale supervised-ψ episodes (600+) and/or ψ capacity on the L3.5 switch; θ frozen, SHA-256 audited.
- **🟢 GREEN:** ψ reaches ≥0.95 on Task B with θ bitwise-invariant → Z3 flagship is live; promote to the Z3 benchmark suite.
- **🔴 RED:** plateaus below 0.95 at scale → the P-axis has a ceiling below the flagship bar; re-scope the claim or change the mechanism before escalating Z3.

---

## The escalation rule

After Round 3:
- **R3-P1 green** → register the depth arm as a CEEC campaign (pre-registered threshold + seeds + the BP-learnable ruler), run it governed, and let it become the first **certified** architecture-co-design finding — promotion or boundary, never limbo.
- **R3-P2** decides whether the escalation target is residuals or the error bus.
- **R3-P3** decides whether Z3 escalation is warranted.

This is the transition from **probe-level** (Level 4/5, minutes, zero governance) to **campaign-level** (multi-seed, real task, CEEC pre-registered, citable). The probes localized, validated, and explained. Now the validated pivot gets the evidence ladder it earned.


---

## EXECUTION RECORD (2026-09-14) — Round 3: the gate returned RED ×3

Implemented and run: `scripts/probes/todo26d_round3.py` (~34 s CPU).
All three probes came back with the *less convenient* answer. The gate
worked exactly as designed — it stopped the escalation.

### Results

| Probe | Verdict | Evidence |
|---|---|---|
| R3-P1 Confirmation | 🔴 **RED (fragile)** | Depth-20 residual+μPC across 3 seeds: **0.849 / 0.633 / 0.854** — seed 1 collapses. MNIST mupc lift NOT reproduced at this operating point (mupc 0.453 vs default 0.727 at depth 8, 100 batches). |
| R3-P2 Error Bus | 🔴 **RED (bus adds nothing)** | TargetInversion (transpose targets) at chance everywhere: depth 20/30, with and without residual+μPC (0.491–0.499). Meanwhile residual+μPC+ePC holds **depth 30: 0.821** — the regime extends past R2's frontier without the bus. |
| R3-P3 ψ at 0.95 | 🔴 **RED (ceiling)** | 600 episodes: temporal_090 final B **0.699**, closed-form **0.709**; trajectories oscillate 0.68–0.74 from ep 100 — no trend toward 0.95. θ bitwise-invariant in both. |

### What round 3 actually establishes

1. **R2-P1's green is real but seed-fragile.** 2/3 seeds hold (0.85), one
   collapses (0.633). The depth-20 arm sits near a stability boundary.
   Depth 30 trains (0.821) but was only run single-seed.
2. **Residuals are the minimal sufficient channel.** The explicit
   transpose-target error bus contributes nothing at depth 20 or 30 —
   consistent with the R2-P3 mechanism (the channel needs a *short path*
   and *conditioned init*, not more signal machinery). Don't add the bus.
3. **The P-axis has a measured ceiling: ~0.73.** Supervised-ψ is a
   frozen-θ readout regression; it saturates there on this switch. The
   honest claim scope is "frozen-θ readout adaptation to ~0.73", not
   "solves the switch". Z3 escalation is not warranted at this mechanism.
4. **MNIST non-replication is an operating-point mismatch, not a
   falsification** — three axes differ from the recorded positive
   (mupc_residual_regime: Euclid 0.2, sPC 60 steps, 600 batches). But the
   burden is now on us to name the working operating point before any
   campaign registers the depth arm.

### Escalation decision per TODO26d's own rule

**NO campaign compute.** R3-P1's RED clause triggers: re-diagnose
(seed sensitivity + operating point) first. Revised next probes, in cost
order:
1. **Seed map** (cheapest): 5-seed × depth {12, 20, 30} × lr {1e-3, 3e-3,
   1e-2} on sign-of-mean — is the depth-20 collapse a seed outlier or an
   instability? Does depth 30 hold across seeds?
2. **MNIST operating-point alignment**: re-run the mupc arm at the
   *recorded* operating point (Euclid 0.2, sPC 60 steps, 600 batches)
   before concluding anything about μPC on MNIST under local optimizers.
3. **ψ mechanism change before scale**: the plateau is flat by ep 100 —
   more episodes buy nothing. The lever is a *different* ψ law (e.g.,
   multi-layer correction, not readout-only), not 6000 episodes.

### Method notes
- Round 3 probes are lint/pyright clean; walltime printed, never recorded.
- The depth-30 extension is a new datum worth keeping regardless of the
  gate outcome: the R2 regime was NOT at its depth frontier.

## Round 3b addendum (2026-09-14) — re-diagnosis + the zoo grid

### Seed map (`todo26d_seedmap.py`, 5 seeds × depth × lr, sign-of-mean)
- **Depth 12/20/30 are robust across all 5 seeds at lr 1e-3 and 3e-3**
  (depth 20 lr 3e-3: mean 0.843, min 0.766; depth 30 lr 3e-3: mean 0.823,
  min 0.762). The round-3 seed-1 collapse was **batch-draw variance near
  a sharp lr boundary**, not a broken arm: **lr 1e-2 is systematically
  unstable** at every depth (means 0.558–0.639). Robust operating point
  identified: lr 3e-3. Depth 30 holds — the regime extends past R2's
  frontier.
- **Readout ceiling: ridge on frozen penultimate features = 0.721.** The
  ψ plateau (~0.73) IS the frozen-features linear ceiling — supervised-ψ
  is already optimal in its class. The 0.95 flagship bar is a
  *feature-quality* problem (the frozen θ's features don't linearly
  encode Task B better than 0.72), not an optimization problem. The ψ
  lever for 0.95 is better frozen features or a multi-layer correction —
  more episodes are provably useless.
- **MNIST at the recorded operating point (Euclid 0.2, sPC 60 compiled,
  600 batches): BOTH mupc and default sit at chance (0.135)** — the
  recorded-positive could not be reproduced under the recorded recipe
  either. The prior "μPC residual regime trains MNIST depth 8+" claim
  now needs its original result record located and re-audited before it
  is cited anywhere. Treat the in-repo MNIST-depth evidence as UNVERIFIED.

### Zoo grid (`todo26d_zoo_grid.py`) — credit family × geometry, depth 20
| family × geometry | none+default | residual+μPC |
|---|---|---|
| ePC (round-2 winner) | 0.507 | **0.880** |
| FF (forward-only goodness) | 0.506 | **0.875** |
| FA (one-hop fixed random backward) | 0.504 | 0.514 |
| EqProp (symmetric energy settle) | 0.494 | **0.466 (harmed)** |
| TargetInversion (transpose targets) | 0.501 | 0.479 |
| BP ruler (depth 4) | 0.845 | — |

**New zoo law (measured, not inherited):** co-design rescues exactly the
families whose credit reads the settle stream along the forward path
(ePC *and* FF — two different rules, same rescue) and leaves-or-harms
structurally different channels (FA directional-locked; EqProp
energy-contract broken by μPC init — replicating w9's MNIST warning).
The round-2 finding is a per-family law with a mechanism, NOT an ePC
artifact and NOT a blanket recipe.

## Round 3c addendum (2026-09-14) — AutoScientist readiness verdict

`scripts/probes/todo26d_autoscientist.py` seeded the KnowledgeBase with the
engine-check findings and drove a live campaign. **The answer: the
AutoScientist was NOT ready — three dead-wired defects found and fixed
in the library — and is now operational for vision tasks, with the
language lane broken upstream.**

### Defects found & fixed (library)
1. **The discovery loop could never propose anything.** `run_iteration`
   called `proposer.propose_batch()` → `reasoner.generate_hypotheses()`
   with no arguments — `recent_results` was always `None`, so both
   rule-based hypothesis generators returned `[]` unconditionally, on
   ANY KnowledgeBase. Fixed: the campaign now reads its own experiment
   history back from the KB (`_recent_kb_results`) and passes it through
   (`propose_batch(recent_results=...)`).
2. **`list_experiments` returns `metrics`/`config` as JSON strings** —
   the first fix read empty records until the helper learned to parse
   them (`_load_jsonish`). (Latent KB contract inconsistency; the
   insight path reads entry objects and worked, which is why this hid.)
3. **Executor/task mismatch is contained, not silent**: language-task
   proposals crash in `trainer.fit()` (LM loader yields scalar tensors —
   pre-existing LM-pipeline defect, separately recorded) and the loop
   records them as failed without dying. Verified live: backprop_mlp on
   mnist executes standalone to **0.942 val accuracy in 5 epochs**.

### Readiness verdict
- **Persistence, insights, proposal→execution loop, failure containment:
  working.** A campaign now proposes (rule-based: "vision success →
  transfer to language") and executes vision trials end-to-end.
- **Hypothesis diversity is thin**: two rule generators (cross-domain
  transfer, bio-accuracy tradeoff) plus an optional LLM backend that is
  not configured. The reasoner's transfer rule hardcodes
  tiny_shakespeare as the transfer target — which the executor cannot
  currently run. The *bold exploration* the zoo deserves needs either
  the LLM backend wired or a geometry/co-design-aware proposal family;
  neither exists yet.
- Targeted tests: 83 passed (`-k "autoscientist or campaign or proposer"`).

### What the AutoScientist should be pointed at next
The engine-check findings are exactly the seed corpus it lacks: the
family-specific co-design law (rescue ePC+FF, harm EqProp, ignore FA),
the lr boundary (3e-3 robust / 1e-2 unstable), and the ψ=feature-ceiling
result are all proposeable structure. Wiring the LLM backend
(`computronium/autoscientist/local_llm.py`, llama-cpp) or extending the
rule set to propose *geometry* (the axis the engine checks showed is
load-bearing) is the next readiness rung — the current proposer can only
vary model/task, never geometry, which is the one variable this program
just proved decisive.
