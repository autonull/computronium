# TODO93 — Local learning that wins on the hardware people own
**Status:** 2026-11-17 · **v26 — capability program. Every verdict the plan recorded as a refusal is retagged a defect probe with a fix queue (CORRECTION 25); "more primitives is not progress" and the trigger-gated admission map are retired, because they made capability building a byproduct of negative measurements. The work program is the new primitives, in capability order: the estimator family (`ForwardTangentCredit`, `ScoreFunctionCredit`, `ZerothOrderCredit`), routing (`SurrogateCredit` + a hard top-k task family), the depth fix (normalization + a decoupled trunk LR), temporal credits (a new axis), the streaming lifts. Memory is an instrument (`c=4.1`, peak, checkpointing), not the queue. No track is closed by a low cell; T6c/T6a/T6a₂/T6d/F1/D2/B1 are defect probes with named fixes. Next session: land the estimator family.**
T1 + T4a + T4c + T4b + T3 + T3b + T6 + B1 + C1 + C2 + E1 + D1 + D2 + F1 + T6a
+ T6a₂ + T6d
landed: the truth pass, the memory decomposition, the ladder runner, the
checkpointed baseline, the lockstep two-pass rung, the hybrid, the composed
pilot, the routing refusal, the plasticity ladder, the retention ladder, the
estimator atlas, the substrate ladder, its matched comparison, the
composition screen, the memory-frontier registration, its re-registration, and
the hybrid's update diagnostic.
**Reading the narrative below.** Entries written before v26 say "refused" or
"closed"; those words are historical — every one is a defect probe or a
capability map in §0.6 (CORRECTION 25). The measurements stand.
Measured: **c≈4.1** (not 1), lockstep **flat in depth** (66.3 MB FF / 58.5 MB
PEPITA), hybrid trunk **flat at 81.0 MB**, pilot controls **pass** (c = 4.125,
spread 0.0 %; L=8 learns 0.419); the pilot's two blockers are decided:
**T6b is fixed** (a credit owns its free pass, so the hybrid reads 0.37× the
checkpointed arm's activation set; CORRECTION 18) and **T6c refused its cheap
pass at the box** (unit-scale streams leave the plateau but miss the floor;
the LayerNorm fallback is the trigger, §2.10). v12
changes what the plan *is*: a portfolio of six capability tracks ordered by
information per session, not a serial DAG through one publishable unit. **v13
states the phase's purpose: grow and stabilise the apparatus and record
observations; do not adjudicate algorithms (§0.5).** B1's routing screen landed
first because it was the cheapest that could cancel a whole track; it has now
refused that track at its box. E1 has now produced its atlas, and D1 has
produced its first matched row: memristive reaches parity with the digital rule
inside 0.05 pp on two seeds at 2 B/weight against 4 B/weight, while ternary
refuses at this box (0.861 vs 0.913 on the confirmation seed). D2 has now
refused that parity on cost (2.09× walltime, the programming budget); **F1 then
landed and refused composition at its box** (screen 0.669, family ladder 0.783
vs 0.797 reference), and **T6a has now registered the memory frontier and its
rung-2 screen refused the claim** (hybrid 0.167 vs floor 0.375; 1.22× the
checkpointed arm's activation set at L=8; confirmation 0.154 vs 0.363). The
claim run is still not scheduled: **T6d localised the gap at the split, so the
split's position (T6e) is the defect fix inside A**, and F2 remains a
five-seed trigger. The session order is §19 row 1 (the estimator family).

**T6a's re-registration refused at the pass-carrying box (2026-11-17).** The
claim moved to L=8→32, W=512/B=4096, stream-norm at the frozen per-arm LR,
200 steps, because the box triage showed the old L=4→8 ratio measured the OOM
guard's box and the B=2048 re-registration would miss its own memory bar
(0.53×) — **CORRECTION 21**. One run, 21 cells, ~300 s (one probe at the box:
14.0 s/cell, seed 99): both controls pass (c = 4.125, spread 0.0 %; the
learning control at L=8/B=4096 plain reads 0.409 against floor 0.399, and
**CORRECTION 22** now bars a chance-level control). The ladder's best point is
the interior edge for the hybrid (LR 1e-2, 0.184) and the upper edge for every
other arm (LR 3e-2: backprop/ckpt 0.364, local 0.354, hybrid 0.171). The
rung-2 screen **refuses**: hybrid 0.184 / 210 MB vs ckpt 0.364 / 453 MB —
**0.46× the activation set (the memory bar is met)** and 17 pp below the floor
(0.354); the confirmation seed reads 0.201 vs 0.357 at the same 0.46×. So the
claim is now decided at a **trained, memory-passing** box: the refusal is the
hybrid's composed update, not the box. At L=8 the same arm reads 0.163 (plain,
LR 0.3) and 0.184 (stream, LR 1e-2), while its parts read 0.354-0.409. Next:
**T6d**, the hybrid's update diagnostic (`train_biases`, `feedback_scale`, a
head-only control at the pilot box), not another depth — measured 2026-11-17:
refused, the split is the mechanism (below). Artifacts:
`results/t93_a_stream/memory_frontier.registered.{json,md}`, committed
`configs/preregistrations/t93_memory_frontier_stream_registered.json`.

**T6d landed and refused the hybrid's update diagnostic (2026-11-17).** One
run at the pilot box its trigger names (L=8/W=1024/B=8192, 200 steps, LR 0.3,
CIFAR-10 10k/10k, seeds 21/22): 12 measured cells (14 planned), ~200 s
(10-15 s/cell, 516-1037 MB peak). The reference trains (0.419/0.416, floor
0.408) and the baseline repeats T6a₂'s level (0.163/0.169), so the box is
sound. **No trunk knob reaches the floor:** `train_biases` reads 0.167/0.175
(+0.5 pp, the only gain the grid shows), the `feedback_scale` ladder reads
0.163/0.100/0.100 --
it peaks at the registered scale and **collapses to chance at 0.3 and 1.0** --
and head-only (gamma=0) reads 0.149. **The sibling control names the
mechanism:** the same trunk rule as a whole stack (`local`, no head) reads
0.400/0.405/0.384 at the same box, LR, and seeds -- within 1.5 pp of the
reference and 24 pp above the hybrid -- and it does not collapse where the
hybrid does. So the gap is the **split at the boundary** (a 2-layer
exact-gradient head over a slowly trained trunk), not the trunk's rule, its
bias path, or its scale (CORRECTION 24). **The memory half does not hold at
this box either:** the hybrid's activation set is 516 MB against the
checkpointed arm's 485 MB (**1.06×**), so L=8 is an accuracy diagnostic box;
the bar is met at L=32 under the stream-normalized pass (0.46×, §2.14).
Artifacts: `results/t93_a_stream/hybrid_update.{json,md}` plus a kill-safe
cell log; replay `uv run python -m computronium.validation.hybrid_update
--replay`. Next for A: **T6e**, the split's position (`split_layer` on the
last Linear, a 7-trunk/1-head hybrid) or a decoupled trunk learning rate — a
defect fix, not the session order (§19 row 1).

**D1 landed and promoted the memristive arm (2026-11-16).** The substrate
ladder ran 24 cells at one box: MNIST quick mode, 784-32-10, batch 32, 600
batches, one epoch, β=0.5, `energy_minimization` settling, full 10k test split
(1σ = 0.3 pp). The learning control (digital backprop) reads **0.9234**, so the
task is valid; the parity reference is the same rule on a digital substrate.
Each arm got its own 3-point LR viability ladder at settle 10 (CORRECTION 17: a
shared LR collapsed ternary to 0.381 at 1e-2 while its best point is 3e-3), then
the 5/10/20 settle ladder at its best LR.

- **memristive** reads 0.893 / 0.911 / 0.915 at settle 5/10/20 (LR 1e-2)
  against the digital rule's 0.913 / 0.914 / 0.916; on the confirmation seed
  at settle 20 it reads **0.9097** against digital **0.9097** (0.05 pp), so it
  reaches **parity at 2 B/weight against 4 B/weight (0.5×)**. Verdict:
  **promote to D2** (coordinate, 2 seeds; best settle at the ladder's upper
  edge, so D2 includes a settle extension).
- **ternary** reads 0.801 / 0.835 / 0.728 at LR 1e-3/3e-3/1e-2, and 0.821 /
  0.835 / 0.796 at settle 5/10/20 (LR 3e-3); its confirmation at settle 10
  reads **0.861** against digital 0.913 — **5.2 pp below**, so it **refuses at
  this box** (2 bits/weight, 16× less state, does not buy parity at width 32).
  Its re-open command is the cell log with a wider hidden layer or a learnable α
  per layer.
- **State ruler:** device state per step is 0.25 B/weight (ternary), 2 B/weight
  (memristive pair), 4 B/weight (digital); train state is the fp32 latent set
  plus optimizer buffer, 0.2 MB and equal for every arm — declared, never
  claimed as a saving (a device would hold the weights, not a second fp32 copy).
- Cost: 24 cells, 617 s (~10 min) on CPU; 8–66 s/cell; forward-equivalents
  read 10/20/40 at settle 5/10/20 (the structural 2×settle estimate).
- **Ladder edges:** digital and memristive best LR at 1e-2 (upper edge) and best
  settle at 20 (upper edge); the pilot read 3e-2 at 0.913 digital / 0.874
  memristive, so D2's upward LR check needs no new ladder at this box.

**D2 — the matched substrate comparison (next rung of track D).** D1 promoted
a substrate at one cheap box; D2 must decide whether the saving survives a
matched-budget comparison. *Arms:* memristive + `energy_min` against (a) the
same rule on digital at matched settle compute, (b) digital backprop at matched
walltime, and (c) the int8-quantised digital control (the same width, no
device model). *Rulers:* accuracy, walltime, forward-equivalents, device state
per step, and the constraint that binds (conductance levels, programming
budget, drift) — a parity claim must name it. *Stop:* within 1 pp of the
digital rule at ≤1.2× walltime → D3 (a device-drift/retention model); a
disadvantage >1 pp at matched walltime → the programming budget is the defect,
and a device-level or compiled quantisation of the pair is the fix. *Box:* CIFAR-10 quick mode or MNIST at 2× width, 5 paired
seeds. D2 needs no new primitive: it reuses `MemristiveSubstrate`,
`EnergyMinimizationDynamics`, and the D1 runner.

**E1 landed and closed (2026-11-16).** The estimator atlas ran its E-lite
screen (4 arms × 1 seed) and then the full rung (6 arms × 3 disjoint seeds) at
a matched compute box: MNIST quick mode, 600 batches of 32, one epoch,
feedforward 784-32-10, CPU. Each arm got its own 3-point LR viability ladder
(1e-3/1e-2/1e-1) at ladder seed 59, a confirmation at the best point (seed
60), and claim seeds 61/62/63. The exact arm reads **0.914 ± 0.006** (floor
0.25) and the FD reference validates autograd at **1.0000**, so both controls
pass. The table is the artifact: PEPITA aligns **0.972 ± 0.001** at **1.60×**
the exact scale and reads **0.923 ± 0.003**; FA reads **0.125 ± 0.079** at
**0.002×** and **0.821 ± 0.007**; the hybrid reads **0.185 ± 0.007** at
**0.395 ± 0.020** and **0.827 ± 0.007**; Forward-Forward reads **0.143 ±
0.109** at **1.211 ± 0.308** and **0.816 ± 0.089**. PC-ALM is outside its
card's validated limit at depth 2: it refuses at LR 1e-2/1e-1 (settle NaN) and
reads chance at 1e-3 (**0.105 ± 0.013**, one seed refused), a recorded
regime-mismatch with a depth-100 trigger, not a verdict. One apparatus defect
was found and fixed (CORRECTION 16): a shared LR collapsed FA at 1e-3 and
diverged the hybrid at 1e-1, so the per-arm ladder is the fair chance.
**E1 is closed as an atlas, not promoted or refused; the empty unbiased cells
(score-function, forward-mode, zeroth order) are visible, not pulled.**

**B1 landed and refused (2026-11-16).** The routing ladder measured the STE
gap's trend over 1/2/4/8 parallel averaged selections: **0.819 → 0.660
(−0.159)** on the ladder seed and **−0.037** on the disjoint confirmation
seed, against δ = 0.05. The smoothed reference agreed with its own finite
difference to 0.013 (tol 0.10) and both ends of the ladder were trained arms
(0.933 / 1.000 end-task accuracy), so the refusal is not a broken arm. Depth
does not compound the surrogate's bias at this box, B2 is not run, and the
trigger is recorded in §14. Three apparatus defects were found and fixed on the
way (CORRECTIONS 13–15): a chained stack measured its own depth, an
end-of-training probe measured the one-hot limit, and the probe split drew its
own task. The remaining cheap screen is streaming (C3); D's substrate ladder is
the next probe of a promise that has never had a matched row. Everything
already built — the instrumented decomposition, the lockstep kernels, the
hybrid, the evidence store, the 6-axis generator, the identity cards — is a
**reused asset** in the new tracks, not sunk cost. v1 (composition-wide search,
substrate inversion) stays in §12 as a triggered track; v2–v11 are the
correctness history (§3–§9).
**Successor to TODO92** (closed: 12 claim-grade rows, breadth gate 8/8, parity
on two families, **0 capability wins at those coordinates**). That base rate is
the reason a portfolio beats one bet: the space is wide, and a single hard claim
is a poor use of the apparatus-building sessions.
**What this phase buys even with no win:** a system that can *run* the
exhaustive HPO later without optimising a broken objective — legality, identity,
matched budgets, controls, cost models, and locks (§0.5).
**The pivot, restated.** TODO92 competed with backprop on backprop's home turf.
v12 competes where the **structure** is different: activation memory, substrate
constraints, non-differentiable computation, batch-1 streaming, and the
composition question itself. Every track names the structure it exploits and the
baseline that structure cannot trivially match.
**The claim we are trying to earn:** a practitioner with a consumer GPU can
train something a *composition* of local and global credit makes possible at
matched memory and matched compute, with a reproducible command.

**C1 landed and promoted (2026-11-16).** On SplitMNIST at batch 1, one epoch per
task, W=256, the local (PEPITA) arm reads **0.945 / 0.947** mean final accuracy
on two disjoint seeds at LR 1e-3 (pre-registered floor 0.55, 4.5 σ above chance),
while the exact-gradient control reads **0.839 / 0.893** at the same point. C moves
to its retention protocol (C2, the EWC-strength ladder at frozen LR); it is not
refused. The ladder bought two measured apparatus fixes on the way — the credit's
label channel and the data-order seed (CORRECTIONS 9–10) — and the row is a
**coordinate, not a claim** (n=1 per point; the best local point is the ladder's
lower edge, so a downward LR extension is the next rung). Details: §14 and
`docs/BENCHMARKS.md` §2.5.
**C2 closed at its saturation point (2026-11-16).** At the frozen LR 1e-3,
the EWC-strength ladder λ=1/10/100 measured local × EWC against backprop ×
EWC at matched per-step cost (1.07–1.13×, ≤1.5× gate; 3.1 MiB state each).
At the best point λ=100: local **0.952 / 0.015** (mean final acc / forgetting),
control **0.963 / 0.020**; the confirmation seed repeats it (0.951 / 0.016 vs
0.958 / 0.024). The local gain is +0.005, below the pre-registered δ=0.032,
while the control's accuracy is 1.1 pp higher; the local ladder moves only
0.6 pp from λ=1 to λ=100 (the control 2.2 pp), both below δ — so the knob
saturates at λ=10/100 and **C closes with λ=100 as its saturation point**
(coordinate, not a claim). Re-open probes: a 5-seed retention protocol (rung
3), a matched-byte replay composition, or SI/cascade at the frozen LR. One
apparatus defect was found and fixed on the way: the runner re-consolidated
at every task start and erased the drift importance (CORRECTION 12); the
fixed ladder then lost one launch to a kill after seven cells, and the
runner now resumes and dedupes its cell log.
Details: §14 and `docs/BENCHMARKS.md` §2.6.
**The amendment that governs the whole plan.** A contest posed where the
structural advantage cannot bind is as uninformative as one posed where it cannot
lose. That is TODO92's lesson, and the mirror image of it is the failure mode of
every lift-vs-backprop comparison: at width 512, depth ≤64, batch 1k, activations
are ~134 MB next to ~200 MB of params and Adam state, so both arms fit and the
"memory" claim is vacuous. **No cell counts as evidence unless the baseline arm's
activations are ≥50% of its peak memory** (§9 binding gate).
**Execution surface:** §0 (portfolio + promise map + ledger), §8 (tracks and
gates), §14 (rank, rewritten each session), §16 (handoff). §1–§7 and §9–§20 are
the contract those tickets must satisfy; read them when writing the test, not
when scheduling the work.
---
## 0. Start here — the portfolio
**The unit is a capability card, not a ticket.** One sentence a practitioner can
act on, the strongest baseline that structure can reach, the budget at which it
holds, the floor, the ruler, and the stop rule. A track that cannot state all
six is not a track.

**Six tracks, cheap-first.** Tracks A–C are the v10 MPUs; D–F are the parts of
Computronium's own promise that no previous TODO has measured. Every track reuses
something already built, and every track names what parks it and the fix that
reopens it, so the portfolio grows instead of accumulating verdicts.

**Reading note (2026-11-17).** The verdict words in this table predate
CORRECTION 25: read `⛔` / "refused" as **defect probe** — a named defect with
a fix queue and the capability it unlocks (§0.6), never a conclusion about a
mechanism. Memory columns are instruments.

| Track | Capability card (what a user could do) | Strongest baseline | Cheapest decisive probe | Cost | Kill rule |
|---|---|---|---|---|---|
| **A. Memory frontier** (MPU1) | Train deeper at 8 GB at parity accuracy | `backprop+ckpt(√L)` | T6b ✅ (credit owns its free pass: 0.37× at the claim point) + **T6a₂ ⛔: the pass-carrying L=8→32/B=4096 box meets the memory bar (0.46×) and trains (0.364 vs 0.354), but the hybrid reads 0.184/0.201 — 17 pp below** + **T6d ⛔: no trunk knob reaches the floor (bias +0.5 pp, gamma peaks at the registered scale, collapses at 0.3/1.0, head alone 0.149), while the same trunk rule as a whole stack reads 0.405 — the split is the mechanism** | 1 session (T6e) | the hybrid not ≤0.5× the baseline's **activation bytes** at parity at the frozen LR ladder's best point → **refused at the pilot box; the mechanism is the split's position, so T6e is the defect fix, not another knob** |
| **B. Non-differentiable routing** (MPU2) | Train hard top-k without a surrogate | STE + load-balancing/z-loss | stacked discrete-op count 1/2/4/8 × 3 STE temperatures/LRs (`benchmarks/joint/z3_fixed_weights.py`) | **hours** | gap flat across the 4-op ladder **at its best temperature/LR** → the missing surrogate is the defect; B's claim narrows (§19 row 4) |
| **C. Streaming without replay** (MPU3) | Adapt at batch 1 with no replay buffer | backprop + SI/EWC ± small replay at matched bytes | batch-1 `SplitMNIST`: 3-point consolidation/LR ladder + 1 confirmation seed | **hours** | local at chance **at the best ladder point on 2 seeds** → the label channel or step scale is the defect; retention is not yet tested |
| **D. Substrate-native training** ⛔ | Train on a constrained substrate at digital parity with less state | digital backprop at matched accuracy | **D1 landed**: memristive **0.910 vs 0.910** at settle 20, 2 vs 4 B/weight; ternary refused (0.861 vs 0.913). **D2 landed and refused**: −0.31 pp (CI [−0.41, −0.22]) at **2.09× walltime**; QDQ −0.01 pp | 10 + 20 min | **D2 refused the substrate path at its walltime box** (the programming budget binds, not the width or drift); D3 is a trigger, not scheduled; ternary re-opens on a wider width or learnable α |
| **E. Estimator atlas** ✅ | Cite a measured bias/variance/compute table for every estimator kind | exact gradient + smoothed/finite-difference reference | **E-lite**: 4 arms × 1 task × 1 seed; then 6 arms × 3 seeds | hours + 1 session | **closed as an atlas (2026-11-16)**: controls pass, table is the artifact; PC-ALM depth-100 trigger, empty unbiased cells visible but not pulled |
| **F. Does composition matter? ⛔** | Say whether a 6-axis composition beats the best single-axis default, by ≥δ | best-of-single-axis at matched budget | **F1 landed**: 50 legal cells vs 41 legal single-axis arms on `digits`, then the family ladder | 1 session | **refused at this box**: reference 0.797, screen 0.669, family ladder 0.783 vs bar 0.807; confirmation 0.814 (3.1 pp seed spread > δ); F2 needs five seeds |

**The rule that changes the plan.** *No ticket is scheduled ahead of a cheaper
screen that could cancel it.* D1 promoted one arm; D2 spent the matched
comparison and refused the path on cost, so **D3 does not fire**; F1 spent the
composition screen and refused at its box, so **F2 does not fire on one seed**.
**The session order is the capability program (§19, CORRECTION 25).** The
estimator family lands first (§19 row 1: `ForwardTangentCredit`,
`ScoreFunctionCredit`, `ZerothOrderCredit`), then routing (`SurrogateCredit` +
a hard top-k task family), then the **depth fix** (normalization + a decoupled
trunk LR — the T6c/T6d defect, not a verdict), then the temporal axis, then the
streaming lifts. The rows above are measurements, not conclusions: each ⛔ row is
a defect probe with the fix that widens the system (§0.6). F2, D3, and T6e are
defect fixes inside their tracks, not gates on the program.

**Ranking, recomputed every session (§14):** capability added ÷ measured build
cost, with the cost taken from the last build of that primitive, never guessed.
A defect fix rides the track it unblocks; a primitive rides the task family it
unlocks. A row whose next step adds no capability is a side track, not work.

**Assets this portfolio protects.** The decomposition + binding gate (A), the
lockstep kernels and the `TrunkContrast` Protocol (A/B), the checkpointed arm
(A), the evidence store + survey harness + policies (F), the identity cards and
estimator coordinates (E), the substrate models, `energy_minimization`, and the
D1 ladder (D), the continual runner (C). D1 found no defect: the moving-scale
probe rejected a frozen-α "fix", so the apparatus grew by a measured LR box,
not a code change.

### 0.1 The promise map (PURPOSE.md → nearest asset → cheapest decisive probe)

Computronium's stated promises are much wider than one frontier claim. This table
keeps the plan honest about the space it claims to explore: a promise with no
probe is a claim with no evidence path.

| Promise (PURPOSE §) | Nearest asset today | Evidence today | Cheapest decisive probe | Gate |
|---|---|---|---|---|
| 1. Discover never-tried systems | 6-axis generator, survey harness | breadth gate 8/8; **0 capability wins**; F1 screened 50 cells and refused at its box | track **F**: 50 legal cells vs best single-axis default | ≥δ above best single-axis; F2 is a five-seed trigger |
| 2. Better digital algorithms | 11 credit rows, 7 dynamics, lockstep kernels | parity on 2 families; memory rung landed | tracks **A**, **B**, **E** | parity/dominance at a named budget |
| 3–4. Substrate-native / co-design | memristive, ternary, neuromorphic substrates; energy dynamics | models exist; **no matched digital-vs-substrate row** | track **D**: ternary + `energy_min` at 10 steps | parity accuracy with less state |
| 5. Re-evaluate published configs | `run_parity` ladder, `BENCHMARKS.md` | P1 rows open (T5) | T5: 3 publishables at published coordinates | within ±1 pp or σ |
| 6. Find defects | 28-test truth lock, anti-fabrication scan | **14 fabricated zeros + 5 live defects found** | already producing (T1/T3/T3b/T6) | a failing test per defect |
| 7. Fair comparison ground | matched budgets, rulers, binding gate | binding gate enforced; σ recorded | every track | a claim without a budget is refused |
| 8. Capability ledger | `negative_results.py`, the defect ledger (§0.6) | defect probes recorded with fixes | every track writes its defect *in the same session* | a fix and the capability it unlocks, not silence |
| 9. Atlas of the space | identity cards, evidence store, fingerprinting | partial: 3.5k measurements | **E** (estimator atlas) + F (composition map) | a table a third party can read |
| 10. Trade-offs, not one best | Pareto analysis, multi-objective metrics | harness exists, no frontier claimed | A's two-budget table | hypervolume or the ≤0.5× byte rule |
| 11. Local/alternative paradigms | 11 credits, energy dynamics, streaming | parity, no structural win | A/B/C/D | a structural win, or a capability gap with the primitive that closes it |
| 12. Growing architectures | routing plasticity, NCA/tile, tape memory | registered, partly unavailable | §19 rows 4–6: the routing primitive, the temporal axis, and the long-stream lift | a legal cell that trains and beats its fixed-topology twin |
| 13–15. New mechanisms, discovery systems, cheap screening | plugin registry, policies, staged evaluation | present and used | F + the surprise channel | a promoted unexpected cell |
| 16–18. Physical hardware, shared infrastructure, community | provenance, identity cards, store | present, unused externally | a collaborator brings a device or a dataset; the store is ready | a shared measurement or an external reproduction |

**What this map says.** Three promises (3–4, 9, 1) have *never* had a probe in
any TODO. Those are the least-explored, most distinctive regions, and D/E/F are
sized to reach them in one session each. That is where new questions come from.

### 0.2 The surprise channel

A plan that can only confirm its own hypotheses converges to "as expected" and
teaches nothing. **10 % of every session's compute is reserved for probes whose
outcome the plan does not predict**, chosen from the map above or from an
unexpected cell in the last run. Rules:

- a cell that beats its declared expectation by ≥2σ, or a rule that trains where
  the plan said it cannot, gets a ticket **in the same session**;
- an unexplained chance-level cell is a defect probe (§14), never a table row;
- the surprise and its follow-up are recorded in §14 under "surprise", so the
  next session starts from the new question, not from the old DAG.

### 0.3 Opportunity ledger (specific, cheap, unpriced)

The promise map says *where* the unexplored regions are. This ledger names
specific probes that fit the surprise budget or a screen slot. They are ordered
by "how surprising would a positive be", not by cost — cost is in the screen
column above.

| Probe | Asset already in the repo | Why it could be remarkable | Gate |
|---|---|---|---|
| **Graph capability**: Cora node classification with a legal local credit | Cora cached; the dry-run gate refuses `gradient` there (`GradientCredit: no gradient reaching learnable weights`, detached settle path); legal arms are `random_projections`, `homeostatic`, `pc_alm`, `target_inversion`, `temporal_trace`; bar 0.75 in AGENTS.md | if backprop's absence is **structural** (no autograd path through the graph operator) a local win is a capability, not a tie | ≥0.75 against a torch GCN reference, **and** a written check that the refusal is structural, not a harness gap |
| **Trunk-rule ladder**: hybrid with FF, local_goodness, target-inversion trunks | `TrunkContrast` Protocol; only `PepitaTrunk` implemented; adapters are small | decides whether the hybrid's L=8 weakness is the boundary or the rule | hybrid ≥ its own trunk rule at L=8 |
| **Settling as compute**: `energy_min` (10 steps) on denoising/attractor tasks vs backprop at matched walltime | `EnergyMinimizationDynamics`, measured optimum `max_steps=10` | settling may buy robustness that no feedforward pass has | accuracy at ≤ matched forward-equivalents |
| **Ternary + energy_min**: the substrate claim with a state ruler | ternary substrate; TWN thresholding fixed; `SubstrateSettleKernel` | the only result a digital backprop baseline cannot express | parity with less state per step (D1) |
| **Grow the architecture**: routing/tile/NCA at fixed budget | `algorithms/routing/`, tile/NCA kernels, availability flags | architecture as a learned variable is the project's §12 promise | one legal cell that trains and beats its fixed-topology twin |
| **Memristive drift as consolidation** | memristive model; SI/replay arms | a hardware defect becomes free EWC-like anchoring | needs a retention/device model — parked until one exists |

**How a probe enters:** it names the capability, the baseline, and what would
park it in one line before it runs. A probe that would only add a row to a table
belongs in a screen, not the ledger.

### 0.4 Screen ≠ verdict — a defect needs a fix

"Cheap" means *few cells*, never *one un-tuned cell*. A low number at one
setting is a **defect probe**, not evidence about an idea. A mechanism is parked
only at rung 2 of the SEC ladder, and only as a capability gap:

| Level | Evidence required | Cells | What it may decide |
|---|---|---|---|
| 0 — wired | positive control passes; pseudo-gradient non-zero; the arm fits; label channel declared | 1 | a defect, not viability |
| 2 — viable | **3-point ladder on the track's primary knob**, 1 seed each, + 1 confirmation seed at the best point | 4 | a defect with a knob box, or promotion |
| 3 — claim | 5 paired seeds, pre-registered threshold, CI | 5+ | a claim |

**Primary knob, declared before the ladder runs:** B = stacked discrete-op
count and STE temperature/LR; C = consolidation strength and LR; D = `max_steps`
and quantization width; A = LR and depth (frozen at 0.3 from the measured
ladder); E = none (descriptive); F = family, not a knob — a composition defect
probe is a breadth statement over 50 cells. The box is declared, never fixed:
when a defect names a missing knob, the box widens and the ladder re-runs.

**Every defect probe carries its fix.** A low cell goes into §0.6 / §14 with
(a) the knob box measured, (b) the **named defect candidate**, (c) the fix and
the capability it unlocks. A defect fix moves the track; it never deletes the
mechanism. A mechanism is parked only as a capability gap with the primitive
that closes it, and the row stays in the ledger as work.

**Why this is not slower.** A 4-cell ladder at L0 costs minutes. What it buys is
the difference between "one config was bad" and "the knob box is exhausted" —
the exact confusion that turns tuning into a verdict. A ladder that stays empty
names the defect; it does not end the idea.

### 0.5 What this phase is for — and what it is not

**This phase grows, stabilises, and fixes the apparatus.** It is not algorithm
adjudication, and it is not the exhaustive HPO that a mature apparatus will
eventually support. Every track is expected to produce some of:

| Yield | What it looks like |
|---|---|
| **A working capability at a named coordinate** | "the hybrid trains at L=8/B=8192/W=1024, 200 steps, 0.419 val_acc, 4.2 forward-equivalents" |
| **A new observation** | "the composed path pays 1.98× the checkpointed activation set because the pipeline holds the free pass"; "the plain stack sits on the loss plateau at L=32" |
| **A defect fixed, or a lock that stops a fake number** | strict xfail, stub detector, binding gate, identity completeness |
| **A cost model** | measured cells/second, bytes/step, forward-equivalents, so the later HPO can be priced instead of guessed |
| **A laddered scope statement** | "at this knob box, with this wiring, the effect is absent" — plus the trigger and command that would reopen it |

**What we do not expect from this phase.** We do not expect "local learning
doesn't work", "PEPITA is bad", or a leaderboard. Those are conclusions this
apparatus is not yet entitled to draw, because no track has run its knob box to
exhaustion and no cell has been through the claim-grade protocol. A low cell
here is a **defect probe** about coordinates, not a verdict about an idea — and
§0.4 keeps its fix.

**Why the order is apparatus-first.** Exhaustive HPO on this system today would
optimise an objective with four known hazards: cells that cannot train (T6c, a
defect probe), memory attributed to the wrong term (T1, fixed), baselines that
are not matched (the binding gate), and compositions whose mechanism never runs
on the claim path (T6b, fixed). Tuning around those hazards produces numbers
that look like results and are not. The ladders remove them for minutes, not
sessions — and a primitive that needs no apparatus starts today (§19 row 1).

**Primitives are the work.** §19 is a build program, not an admission map:
surrogate, forward-tangent, score-function, zeroth-order, local supervision, SI
lift, cascade, Bayesian-online, e-prop, UORO, and the RTRL reference are each a
capability row with the task family it unlocks, its build cost, and the price
every row pays (spec, kernel, reference, cases, identity card, registry, parity,
lock). Nothing waits for a negative measurement; the first three rows land
first.

**The one bonus.** If a screen or a surprise produces a real claim-grade effect,
it is taken seriously and promoted immediately (§14). The plan is built so that a
win is *found*, not forced — and so that a blank is *recorded*, not mourned.

### 0.6 The capability program (2026-11-17) — the plan's culture fix

**What went wrong.** Two rules turned capability work into a byproduct of
negative measurements: *"more primitives is not progress"* and a trigger-gated
admission map whose triggers were produced by the refusal loop. The queues that
could not move were measured repeatedly, and the primitives that would have
widened the system stayed in a table. §0.5 said *grow and stabilise the
apparatus; do not adjudicate*; the sessions did the opposite. **CORRECTION 25**
retags every refusal as a defect probe.

**What replaces it.**

1. **The work is a capability**: a new primitive, a new task family, or a
   constraint met. A negative measurement is not a deliverable; a defect is.
2. **"Refused" is a box statement** (infeasible at this geometry, over budget)
   and never closes a mechanism. A mechanism that cannot train is a **defect**
   until a fix is tested.
3. **A capability gap is a work row**: the primitive or feature that closes it,
   its build cost, and the task family it unlocks. Primitives are admitted by
   the capability they add, not by a claim they unblock (§19).
4. **Memory is an instrument**: `c = 4.1`, the peak decomposition, and the
   checkpointed arm are tools other capabilities report with. No track is ranked
   by activation bytes.
5. **A measurement verdict is never final for a mechanism.** The fix is the next
   rung.

**The defect ledger (what the measurements become).**

| Ticket | Measurement | Retag | Named defect candidates | Capability unlocked by the fix |
|---|---|---|---|---|
| T6c | plain L=32 at 0.100; stream-norm 0.314/0.326 vs floor 0.375 | defect probe | no depth normalization in the plain pass; a fixed `sqrt(W)` stream scale; one LR for all depths | deep training at L≥16 (unblocks A, F, D at depth) |
| T6a₂ | hybrid 0.184/0.201 at 0.46× memory | defect probe | two step scales on one LR; the head split at the boundary | deep local learning at parity |
| T6d | no trunk knob reaches 0.408; sibling 0.405 | defect probe (mechanism localized) | the split's position and the head/trunk LR coupling; head capacity | the trunk rule at parity |
| D2 | memristive −0.31 pp at 2.09× walltime | defect probe | no programming-budget model; per-step host↔device conductance writes | substrate-native training with a priced budget |
| B1 | STE gap 0.819 → 0.660 over depth | defect probe | no `SurrogateCredit` (STE/Gumbel-ST with a baseline); no load-balance term | hard top-k training |
| F1 | screen 0.669 / ladder 0.783 vs bar 0.807 | defect probe | the composition is measured on an untrainable deep box; the axis space lacks the temporal and routing primitives | a real multi-axis search |
| C2 | EWC gain +0.005 < δ at λ=100 | closed capability (measured) | SI and cascade absent; no ≥20-task stream | replay-free long-horizon continual learning |
| E1 | atlas | capability map | three empty estimator cells (forward-mode, score-function, zeroth order) | three new credits (§19) |

No row above is a conclusion about an algorithm. Each is a defect to fix or a
capability to build.

### 0.7 Operating philosophy — relaxed (binding)

**The mode is build, not judge.** Ideal operation is a lab that ships
capabilities and records costs, not a tribunal that closes ideas.

1. **Explore in parallel.** A claim run is serial and pre-registered; capability
   work is not. Several primitives may be in flight; a session lands one row.
2. **Tune before comparing, not instead of it.** Find each mechanism's best
   declared box (its ladder), then compare at matched boxes. An under-tuned
   comparison is a defect, not a ranking.
3. **Pre-registration is for claims.** A primitive needs a capability card and a
   parity lock, not a registration. Only a claim freezes `n_max`, a seed plan,
   and a threshold before its first run.
4. **Four rulers, one capability.** Memory, accuracy, walltime, and
   forward-equivalents are peers; the capability is the deliverable.
5. **Rules are defaults.** Every rule in this document yields to a named reason
   and a working capability. Write the reason where the number lives.
6. **No ceremony between an idea and its measurement.** A primitive is one row
   (class, identity card, row, registry, parity, lock); a defect is one fix; a
   claim is one pre-registered run.
7. **A defect is the good news.** A low cell is where the system gets faster,
   smaller, or able to do something it could not.

**The only hard rules.** No fabricated number, no fake gate, no unmeasured
claim. Everything else is a default.

**Progress (2026-11-16 — T1, T4a, T4c, T4b, T3, T3b, T6, B1, C1, C2, E1, D1).** Every row is a runnable
check, not a claim, and each fails when its mechanism is removed.

| Ticket | Landed | Lock | Consequence |
|---|---|---|---|
| T1 | `complexity_verified` + `available`/`unavailable_reason` on every kernel backend; `activations_mb=None` at all 14 fabricated-zero sites; PEPITA contrastive nudge rebuilt (two-forward error modulation); FF/SNN contrastive marked unavailable with triggers; `estimator_kind`/`bias_reference` declared on all 10 credit rows via their identity cards | `test_kernel_truth_lock.py` (28), `test_estimator_lock.py` (21) | no memory claim can rest on a self-reported zero; a stub kernel cannot be routed to (`KernelRegistry.get` refuses it); W3's taxonomy is declared, not inferred |
| T4a | `EpochResource` decomposition (params / optimizer / activations / auxiliary / RSS) + `activation_share` + `binding_verdict`; emitted per cell beside `memory_usage` | `test_memory_binding.py` (6, CUDA) | the decomposition sums to the peak; the gate rejects a non-binding cell; **measured c = 4.1** |
| T4c | `run_parity(batch_size=...)` threaded to the driver and the baseline; `pepita` family in the ladder portfolio; **fixed a live defect: `backprop_baseline` referenced a `batch_size` it did not have, so every campaign raised `NameError`** | `test_backprop_parity_runner.py` (2) | one runner for the ladder; 2 cells in 4.9 s |
| T4b | `core/gradient_checkpointing.py` + `FeedforwardGeometry.set_gradient_checkpointing`: √L segments split at Linear starts, `use_reentrant=False`, `preserve_rng_state=True`, geometry forward wrapped (never `train_step`); `create_backprop_mlp(checkpoint_segments=...)` is the arm | `test_checkpoint_parity.py` (7) | checkpointed grads ≡ plain under dropout (bit-exact), RNG-preservation is a negative control, retained set is segment boundaries; **epoch peak 3894 MB < 6554 MB at L=64/W=1024/B=8192** (§4.1) |
| T3 | one `lockstep_contrasts` stream serves both families (FF contrasts positive/negative, PEPITA standard/error-modulated — same expression); `train_step` + `kernel_train_step` run it; store-all `forward_*`/`backward` stay as the reference rung; `complexity_verified=True` for FF and PEPITA | `test_lockstep_parity.py` (8, 4 CUDA) | deltas ≡ store-all at `atol=0` per layer; **peak flat 66.3 MB (FF) / 58.5 MB (PEPITA) at L=4→32** vs 576/568 MB retained; **three live defects fixed**: FF `train_step` called a nonexistent `backward_contrastive`, PEPITA `backward` required an `error` argument no caller passed, and the bespoke PEPITA step used the standard pre-activation for both chains (the Triton twin's tested equation uses each chain's own) |
| T3b | `HybridCredit` in `ontology/credit/_hybrid.py`: `PepitaTrunk` contrast + `GradientCredit.gradient_of` head; `step_layer` threads the residual input across one layer; `split_layer` must land on a Linear; one registry row (`estimator_kind="hybrid"`) and feedforward-geometry refusal | `test_hybrid_parity.py` (8, 2 CUDA) | trunk deltas ≡ store-all hybrid **max\|Δ\| = 0.0**; head ≡ plain backprop; **trunk peak flat 81.0 MB above gradients at L=4→32** vs store-all 122→1018 MB; composed `train_step` decreases loss and moves every weight |
| T6 | `validation/memory_frontier.py`: one operating point, four arms, two controls, appendix writer; `run_pilot`, `run_learning_ladder`, `claim_ladder`, `depth_rung`, `build_arm` | `test_memory_frontier.py` (12; T6b's `0.5×` lock is live, T6c's verdict is a pure-function lock) | **c = 4.125 (0.0 % spread) at L=32/B=8192/W=1024**; gate green (share 0.941); learning control passes (0.419 vs floor 0.409); **two defects found** — T6b (composed hybrid 3249 MB vs ckpt 1637 MB) and T6c (loss plateau at L=32) |
| **C1 ✅** | **Plasticity ladder**: `validation/plasticity_ladder.py`; batch-1 SplitMNIST, 5 tasks, LR ladder (1e-3/1e-2/1e-1) + confirmation seed; local (PEPITA) vs exact-gradient control | `test_plasticity_ladder.py` (3), `test_cl_credit_arms.py` (5) | **local 0.945 / 0.947 at LR 1e-3 on two seeds**, control 0.839 / 0.893, floor 0.55 → **verdict: promote**. Two apparatus defects fixed: credit label channel (local scored 0.030 on task 4 before) and data-order seed (backprop swung 0.926→0.839) |
| **C2 ✅** | **Retention ladder**: `validation/plasticity_ladder.py --stage consolidation`; batch-1 SplitMNIST, 3-point EWC-strength ladder at the frozen LR (1/10/100), local × EWC vs backprop × EWC; 1 seed + confirmation; kill-safe resume/replay | `test_plasticity_ladder.py` (9), `test_cl_credit_arms.py` (6) | **close at the saturation point λ=100**: local 0.952 / 0.015 vs control 0.963 / 0.020 (gain +0.005 < δ 0.032; accuracy −1.1 pp); confirmation 0.951 / 0.016 vs 0.958 / 0.024; cost ratio 1.07×; λ ladder moves 0.6 pp (local) / 2.2 pp (control), both < δ. Defect fixed en route: task-start re-consolidation erased the Fisher importance (CORRECTION 12) |
| **D1 ✅** | **Substrate ladder**: `validation/substrate_ladder.py`; ternary/memristive + `energy_min` at settle 5/10/20, per-arm LR ladder, 2 seeds, device state | `test_substrate_ladder.py` (9) | **promoted memristive** (0.9097 vs 0.9097 at settle 20 on the confirmation seed, 2 vs 4 B/weight); ternary refused at 0.861 vs 0.913 (2 bits/weight); CORRECTION 17 (per-arm LR) |
| **D2 ⛔** | **Matched substrate comparison**: `validation/matched_substrate.py`; 784-64-10, settle 20/40 screen, 5 paired seeds, digital backprop control, int8 QDQ control | `test_matched_substrate.py` (13) | **refused at the walltime box**: −0.31 pp (CI [−0.41, −0.22]) at **2.09× walltime** (limit 1.2×); QDQ −0.01 pp (the width is harmless); the programming budget binds; D3's drift trigger stays parked. Correction: the QDQ control now quantises (it cast to int8 and did not) |
**Next (three sessions, not a DAG).**

1. **The estimator family is the next session (§19 row 1):**
   `ForwardTangentCredit`, `ScoreFunctionCredit`, and `ZerothOrderCredit` —
   three credits the system does not have, each with an identity card, a
   primitive row, and a parity lock. They need nothing from any track: they are
   capability, and they turn E1's empty atlas cells into three honest kinds
   (biased-pathwise, unbiased-pathwise, unbiased-for-expected-loss).
   The T6c/T6d split fix (§19 row 3) follows as a defect fix, not a verdict.
2. **A's blockers are decided:** T6b landed (a credit owns its free pass),
   T6a₂'s re-registration refused at the pass-carrying box where the memory
   bar is met, and T6c's re-open is a side track (the pass trains within
   1.1 pp of the old floor); **the hybrid's update is the open mechanism**. The
   registered boxes are the L=4→8 and L=8→32 pass-carrying boxes (30 priced
   cells each, none run).
3. **Triggers, not tickets:** D3's drift row (D2 held parity but missed the
   1.2× walltime), a device-level/compiled quantisation of the pair, PC-ALM at
   its depth-100 box, the empty unbiased cells (score-function, forward-mode,
   zeroth order), C's 5-seed retention protocol, ternary's wider-width/learnable-α
   box, B's chained/Gumbel/k≥4 re-open, and F2's five-seed composition are
   all in §14.

T6a **is** registered before the claim, and the rung-2 screens refused the
claim at both boxes: a threshold written while the treatment's accuracy is 17 pp
below the baseline would be decided by the hybrid's own update, which is why the
claim run is parked rather than scheduled. T5 (published parity) is a standing side track —
it needs no primitive and every track's credibility depends on it.

**Credibility runs in parallel (P1).** A low number from a weak implementation
is a defect, not a verdict. Each credit we intend to publish reproduces its
*published* number at the published architecture within tolerance; a claim run
needs that row, but the audit is not a gate on exploration. P1 is also where
the claimed-vs-measured complexity audit lands, because the audit is what makes
the memory ruler checkable at all.
**What changed from v2 and why**
| v2 | v3 | Reason |
|---|---|---|
| §1 cited `contrastive_kernels.py` as the "no stored activations" family | §1 states the measured truth: two full activation passes; only layer-sequential rules are O(1) | the cited file holds `free_acts` + `nudged_acts` and hardcodes `activations_mb: 0.0` |
| lead arm = "the best local rule from P1" | lead arm = hybrid (lockstep-local trunk + 2–4 layer backprop head); pure local is the control | arm selection by accuracy confounds credit quality with memory; the frontier is *within* the local family |
| W2 = "2× depth" | W2 = 2× depth **with an accuracy floor** | depth without learning is gameable |
| W4 vs backprop+replay at matched memory | W4 vs backprop+online EWC/SI ± small replay; plasticity first | batch-1 replay is cheap; forgetting is weight interference, not credit routing |
| "nobody publishes memory-matched comparisons" | deleted; position against InfoPro, TinyFoA, DGL, greedy layerwise | false as written |
| T0/D1 on the critical path | deferred §12; manual `regime` tag now | the search is deferred; the MPUs are targeted and need no proposal bias |
| no primitive admissions | §19 admits primitives by the capability they add; `estimator_kind` gives the C axis an estimator coordinate | W3 is a bias/variance question, not "local vs weak STE" |
| headline "2× depth at equal walltime" | headline = accuracy per GB at iso-walltime (Pareto) | see §2 |

**What changed in v12 and why.**
| v11 | v12 | Reason |
|---|---|---|
| one MPU at a time, serial DAG | six tracks, parallel, each with a kill rule | seven sessions produced one pilot; a serial plan pays a full session for every blocker |
| cheap screens are "parallel afterthoughts" | **the screens are the first three sessions** | B/C/E can each cancel a track for hours; A's claim is two defects away |
| substrate promise deferred (§12) | track **D**, probed now | substrate→algorithm pairing is the most distinctive promise and has never had a probe |
| W3's credits "conditional on the screen" | track **E**, the atlas is the artifact | a measured estimator table is publishable without a win and makes every later claim commensurable |
| composition search deferred (D1) | track **F**, 50 cells, one session | the 6-axis generator is the repo's central claim; if composition never beats the best single axis, that is the most important result available |
| "no remarkable results" accepted as base rate | **10 % surprise budget + same-session tickets** | a plan that can only confirm itself converges to "as expected". Surprises are results (§0.2) |
| DAG order fixed in the plan | **portfolio rank rewritten every session** (§14) | the ranking must move when a screen lands, not when a document is edited |

**What changed in v20→v21 and why.**
| v20 | v21 | Reason |
|---|---|---|
| F1 is the next screen | **F1 landed and refused composition at its box** | 50 legal compositions vs 41 legal single-axis arms: reference 0.797, screen 0.669, family ladder 0.783, bar 0.807; the confirmation seed reads 0.814, a 3.1 pp seed spread, so F2's five seeds are the trigger, not a claim |
| the screen's reference is a composition | **the reference is the best legal single-axis arm, never a composition it judges** | a composition cannot be its own bar; the 41-arm sweep is the strongest default that structure reaches |
| one seed can decide a composition | **a confirmation seed at the ladder's best width is a ruler, and δ must exceed the seed spread** | the family ladder moved 3.1 pp between seeds; a 1 pp δ is smaller than the measured spread, so the point is `refuse` with F2's five seeds as the trigger |
| no composition box | **the box is `digits` at 57 forward-equivalents, a 50k parameter ceiling, and a 10 pp control band fixed from the pilot** | digits' parameter ceiling changes the composed cell, so it is part of the measurement; the pilot measured a 6.9 pp data-order swing before the run |

**What changed in v21→v22 and why.**
| v21 | v22 | Reason |
|---|---|---|
| T6a is the next screen | **T6a landed and its rung-2 screen refused the claim** | at the registered L=4→8 box the hybrid's best ladder point reads 0.167/103 MB against the ckpt arm's 0.385/85 MB (1.22×), and the confirmation seed reads 0.154 vs 0.363; no claim run is scheduled |
| the pilot point is L=32/W=1024/B=8192 | **the registration's claim point is L=4→8/W=512/B=2048**, with the instrument control at the smaller L=16/W=512/B=2048 pilot | the 4.5 GiB pilot allocation is replaced by the smaller L=16/W=512/B=2048 instrument point under the OOM guard; the coefficient still measures from two depth deltas (c=4.25, spread 0.0%) and the claim cells price from the measured c |
| the registration's claim is W1 at the 8 GB frontier | **the registered claim is W1's ≤0.5× activation-bytes form at the reduced box**, so no hypervolume reference point is registered | the reduced box is a screen, not the 8 GB claim; the claim run stays parked behind T6c |
| T6a's registration has no screen | **`ScreenVerdict` is the rung-2 falsifier** | `verdict=refuse`, `reason` and `trigger` are in the raw JSON; a claim-table test reads them without trusting `ThresholdRegistration.from_dict`, which ignores the box and the binding gate |
| next is the claim run | **next is T6c's re-open (LayerNorm c≈2 / Innocenti init)** | a registration whose treatment misses both bars at its own box cannot open a claim run; the depth crossover (L≥16) and trainability must meet first |

**What changed in v17→v18 and why.**
| v17 | v18 | Reason |
|---|---|---|
| D1 is the next screen | **D1 landed**: memristive promoted to D2; ternary refused with a trigger | the first matched substrate row exists; the promoted arm's next rung is a matched comparison, not another screen |
| A's blockers are second | **A's blockers are first** | A's instrument is done and D1's promotion does not unblock its claim; the two defects are the cheapest remaining decision |
| one DP/DR device width per substrate, unstated | **the state ruler is explicit**: 0.25 / 2 / 4 B/weight device, fp32 train state declared | a "less state" claim must name what a device holds; the latent set is a simulator cost, never a saving |
| "shared LR is fine for the substrate screen" | **per-arm LR viability ladder** (CORRECTION 17) | a shared LR collapsed ternary to 0.381 while its best point is 3e-3; a screening gate must not be decided by a tuning defect |
| D2 unnamed | **D2 defined**: matched settle compute, matched walltime, int8 QDQ control, 5 paired seeds | a promoted arm needs its matched comparison written before it runs |
---
## 1. The cost thesis — a capability at a declared budget (memory is one ruler)
**The thesis.** Expand what the system can do, and state each capability at its
measured cost. Memory is one ruler beside accuracy, walltime, and
forward-equivalents; it is not the thesis.

**Measured fact (was wrong in v2).** Backprop stores per-layer activations:
O(L·B·W). Local rules as *implemented* store two full activation lists — the free
and nudged passes — so their peak is ≈2× a forward pass, not O(1):

| Path | Declared | What the code holds | Verdict |
|---|---|---|---|
| `acceleration/contrastive_kernels.py` `contrastive_step` (:208–210) | `memory_complexity="O(1)"` (:77), `activations_mb=0.0` (:235) | `free_acts` **and** `nudged_acts`, full per-layer lists | claim false; ≈2× forward |
| `acceleration/ff_kernels.py` `FFKernelBackend` (:90–94) | O(1) (:42), 0.0 (:240) | `pos_acts` + `neg_acts` | claim false |
| `acceleration/ff_kernels.py` `PEPITAKernelBackend` (:373–384) | O(1) (:321), 0.0 (:576) | `std_acts` + `err_acts`; two forwards | claim false; 2 forwards is PEPITA's published design |
| `acceleration/backprop_kernels.py` (:50) | O(L) | O(L) | complexity honest, counter still hardcoded 0.0 (:181) |
| `acceleration/hebbian_kernels.py` (:38), layer-sequential FF | O(1) | one layer at a time | plausible; **must be measured, not asserted** |
| `acceleration/tp_kernels.py` (:60) | O(1) | stores inverses (≈2× params) | complexity claim wrong even where activations are flat |

Only **layer-sequential** rules (FF done properly, Hebbian, STDP) are O(1) in
depth. PEPITA as published requires two forward passes; TinyFoA states it "still
needs to store all the parameters and activations". This is a defect ticket, not
a design choice: a hardcoded `activations_mb: 0.0` is a claim that masquerades as
a measurement, and it would have poisoned every memory verdict in this plan.

**Two implementations per rule.** `algorithms/` holds the faithful
reference paths; `acceleration/*_kernels.py` holds the fused kernels. They are
different implementations with different memory behaviour, and
`contrastive_kernels.py` has `pass` where error modulation belongs
(`PEPITAContrastiveKernel.nudged_phase` :507, `SNNContrastiveKernel._simulate`
:747). Any cell routed there measures nothing. **Backend path is part of the
identity card.**

**Fact (honest, corrected).** `core/checkpoint.py` is save/resume of training
state, not gradient checkpointing. But two assumptions in v4 were wrong:
1. **Peak memory is already measured on the claim path.** `SystemTrainer`
   captures `peak_memory_mb` per epoch in `core/system_trainer/_resources.py`
   (:73, reset at :133, read at :155), `SystemTrainerConfig.track_memory` is on,
   and `_trainer_utils.py:194-207` emits it as `memory_usage` in every cell.
   What is missing is the **decomposition** (params / optimizer / activations /
   auxiliary) and CPU RSS — hours, not 1–2 sessions.
2. **Checkpointing already has a working precedent.** `torch.utils.checkpoint`
   (with `use_reentrant=False`) is used for settle steps in
   `core/local_learning/settling.py:403,446,760` and
   `ontology/dynamics/_settle_driver.py:167,186`. Backprop-activation
   checkpointing is new, but the API risk is retired.
`domains/trainer.py` `_TaskTrainer` (:237) is **not** the claim path; the claim
path is `experiment/kernel/evaluate.py` → `SystemTrainer.train_epoch`. Instrument
the shared trainer, never the domain helper.
So `backprop+checkpointing` is √L segments via `torch.utils.checkpoint`,
`preserve_rng_state=True` for dropout parity, wrapping the **geometry forward**
(not the step, which contains updates), plus the decomposition.

**Compute ruler.** Walltime is hardware-bound; **forward-equivalents** is the
portable compute unit. Backprop ≈3, backprop+ckpt(√L) ≈4, two-pass local ≈2,
lockstep local ≈3, hybrid trunk ≈3L layer-ops vs backprop's ≈4L. Local may buy
*more steps* at iso-walltime; v2 undersold this.

**Where local keeps an advantage even against checkpointing:**
1. **composition**: a local trunk stores no autograd graph; only the head does
   (approximately 4–8·B·W vs 16·B·W for √L checkpointing at L=64, head=4);
2. no batch required → batch-1 streaming has no checkpoint segment to trade;
3. non-differentiable ops need no surrogate → no bias to correct;
4. no global backward channel → shardable, asynchronous, heterogeneous.

**Where local is expected to lose, stated in advance:** accuracy per parameter on
small saturated tasks; walltime on matmul-optimised GPUs where the backward pass
is cheap; anything where the global gradient is the only signal that propagates
credit across many layers; and any comparison whose activation memory never binds.
---
## 2. The win conditions (falsifiable, with floors)
| # | Prediction | Floor / baseline | Falsifier | If false |
|---|---|---|---|---|
| W0 | **Capability:** a new primitive trains its task family above chance, or trains it at a smaller constraint (state, memory, steps) | the task family's chance rate; the capability card | the primitive does not train above chance on its target family | the primitive is a defect probe with a named fix (§0.6), not a failure |
| W1 | **ε-dominance (ε=1 pp):** on ≥1 task family the hybrid or local front improves hypervolume on (accuracy, peak GB) by ≥δ over `backprop+ckpt(√L)`, **or** reaches accuracy ≥ baseline −1 pp at ≤0.5× **activation bytes** (peak reported alongside; the ≤0.5× *peak* form is rejected — params+optimizer is an arm-neutral floor) | reference point fixed in T6a (`(floor−5 pp, max_peak×1.1)`); δ pre-registered; floor per task; binding gate | no arm dominates and no arm reaches the floor | memory frontier closed; the measured frontier is still the artifact |
| W2 | At fixed peak memory (8 GB), max depth at val-acc ≥ floor for local/hybrid ≥ 2× `backprop+ckpt` | floor locked before seed 1; "trainable" must mean "learns" | ratio <2, or floor not met at depth | report the measured ratio; do not claim depth |
| W3 | On hard top-k routing, the local arm beats the **best backprop-compatible estimator** (STE + load-balancing/z-loss) by ≥2 pp at matched walltime. **Bias is measured only among gradient-estimator arms; objective-local arms report update-direction alignment, not bias** | soft-relaxation gradient and/or finite-difference reference for the estimator arms; `bias_reference="none"` for objective-local; expert-choice and dense-backprop-MoE are positioning controls | STE+aux ≥ local−2 pp | negative with the measured mechanism named; no category error |
| W4 | On batch-1 streams under a pre-registered **analytic byte cap** (buffer + consolidation state ≤ cap, enforced in the GPU runner), local×consolidation **BWT** and **avg_forgetting** beat `backprop+EWC/SI` ± replay at matched per-step cost | plasticity gate first; cap and per-step cost in T6a; byte cap is a budget, not an MCU hardware claim | replay saturates BWT, or local fails plasticity | report the buffer size / cap at which replay saturates |
**Pareto-nondominated is not a claim.** A low-accuracy, low-memory point is
trivially non-dominated. W1 is **ε-dominance (ε=1 pp)** with a margin: hypervolume
gain ≥ δ against a pre-registered reference point (reuse
`experiment/analysis/pareto_analysis.py:compute_hypervolume`), or the sharper,
cheaper test — accuracy ≥ baseline −1 pp at **≤0.5× activation bytes**. The
≤0.5× *peak* form is structurally unreachable (params+optimizer is an
arm-neutral floor); do not use it. Pick one and pre-register it.
**Error control and floors.** Fix `n_max=5` paired seeds per depth before the
first run; do not peek. **Floor:** val accuracy at L=8 for the
`backprop+ckpt` arm minus 1 pp, measured on the same task, and then held fixed at
every deeper rung. The floor is set from the **pilot**, and the claim seeds are
**disjoint** from the pilot seeds; otherwise the floor is a peek. If the CI is
inconclusive at `n_max`, that is a coordinate result, not a claim. W1/W2 are
**relative** claims: the repo's absolute vision criterion (>0.95) does not govern
a flat-MLP memory ladder.
**Pre-registration essentials (T6a).** (1) a **per-arm LR viability ladder** at
L=8 — three points, one seed each, **seeds disjoint from the claim**, best point
frozen before the claim (without it, a bad LR is a defect masquerading as a
verdict); (2) fixed epochs and `batches_per_epoch` for both arms; (3) the claim
seed list and the data-order seed, disjoint from pilot and LR-ladder seeds;
(4) **both positive controls** — instrument (calibration cell reads
`c·L·B·W·4` within tol) and learning (backprop at L=8 reaches the pilot floor);
(5) δ **and** the hypervolume reference point, or the ≤0.5× **activation** rule;
(6) the binding arithmetic; (7) the **minimal claim ladder** (see §4), not the
full grid. A claim missing any of these is not registered.
**Estimator taxonomy (the reason §19 exists).** W3 is not "local vs weak STE". It
is: *which bias/variance tradeoff wins at matched compute on hard routing* —
biased-pathwise (`surrogate`), biased gradient-approximation (`gradient_approx`:
FA/DFA/TP/EqProp/PC), unbiased-score-function (`score_function`), unbiased-
pathwise (`forward_mode`), smoothed (`zeroth_order`). **Objective-local rules
(`objective_local`: FF/PEPITA/goodness; `local_supervised`: layerwise/DGL/InfoPro)
do not estimate the global gradient — they optimize a local objective.** Their
`bias_reference` is `"none"`; report **update-direction alignment** against the
reference, not bias. Measure bias/variance only among the gradient-estimator
arms. W3's accuracy comparison still includes the objective-local arm. Every
credit declares its kind, or it cannot enter the claim table.
**Metric discipline.** Every number carries: peak memory (bytes), walltime,
forward-equivalents, params, optimizer state, accuracy, σ, and the **matched**
budget. `[regime-mismatch]` marks a cell whose activation share is below the
binding gate — it is not evidence either way.
---
## 3. P1 — The credibility step (published-parity audit, in parallel)
**Decision.** Do our implementations of the credits we intend to publish reproduce
their published numbers at their published architecture and schedule?
**Why first.** A reference implementation weaker than the literature is a defect
that masquerades as a research finding. It is the cheapest session in the plan
and it protects every later claim. It is also where the complexity audit lands.
**Scope — three publishables plus the arm P2–P4 actually uses.** `pepita`,
`local_goodness`, `random_projections`, and the hybrid trunk's local rule. Do not
audit all eight; an unreferenced row is cost without a decision.
**Method, per credit:**
1. locate the published architecture, dataset, epochs, and reported accuracy;
2. reproduce at that coordinate with this repo's implementation;
3. record our number, published number, delta, σ, and the exact command;
4. **tolerance:** within ±1 pp or the published run-to-run σ, else defect.
5. **complexity audit:** measured peak activation bytes vs declared
   `memory_complexity` on a seeded 4/8/16/32 depth ladder. A class mismatch is a
   defect ticket, not a footnote.
**Deliverable.** `docs/BENCHMARKS.md` (does not exist yet): one row per
(credit, dataset, architecture, backend path) with published / ours / delta / σ /
command / date. Rows for a `pass`-stub backend are marked `unavailable`, never
measured.
**Caveat.** Published local-rule numbers are often single-seed or best-of.
Reproduce the protocol, compare means, record σ, and say when ours is a mean over
more seeds than theirs.
**Defect policy.** A gap beyond tolerance opens a defect ticket before any new
measurement. Fix the implementation, do not tune the benchmark. A second failure
after the fix pass is a capability gap with the named mechanism, never a quiet
exclusion.
**Cost.** 1–2 sessions (scoped down from 2–4). Most cells are minutes.
---
## 4. P2 — MPU1: the memory frontier
**Instrument first — mostly built.** `SystemTrainer` already reports
`peak_memory_mb` per epoch (`core/system_trainer/_resources.py`), surfaced as
`memory_usage` by `_trainer_utils.py:194-207`. Extend `EpochResource` with the
**decomposition** (`params`, `optimizer`, `activations = peak − params −
optimizer − auxiliary`, `auxiliary`, `cpu_rss`) and forward-equivalents from the
existing FLOP counter. Acceptance ladder, on a synthetic depth task used **only**
for instrument acceptance:
- backprop peak is monotone in depth;
- a true layer-sequential rule is flat in depth;
- checkpointing bends the backprop curve down at depth;
- `preserve_rng_state=True` gives gradient parity with plain backprop under
  dropout;
- **calibration:** measured activation bytes match the analytic `c·L·B·W·4`
  within 10%, with **c measured on the declared claim geometry** (c≈1 for
  Linear+ReLU; c≈2 when LayerNorm saves input *and* output). Lock the measured c,
  never a hardcoded 1. A non-binding cell is rejected by the guard;
- forward-equivalents are a **measurement**: measured FLOPs ÷ one-forward FLOPs
  (the counter exists). The ≈3/≈4 values in §1 are predictions to compare, not a
  lock target.
**Binding gate — on the *unrecovered* arm.** The gate asks "is this regime
memory-bound?", so it is computed on **plain `backprop`**, not
`backprop+ckpt`: checkpointing's job is to shrink activations below the gate, so
gating on it self-defeats. At the pilot (B=8192, W=1024, L=64, c=1) plain-backprop
activation share is 89% (SGD) / 73% (Adam). Report the ckpt arm's decomposition
separately; do not gate on it. If the plain-backprop share is <50%, the cell is
`[regime-mismatch]` and enters no claim table. Enforce it as a test over the
claim table. **Name the optimizer per table** — params+Adam state changes the
share, and the Appendix must never mix SGD-primary with an Adam share. **CUDA is
required for the claim:** CPU runs measure RSS only and are instrument-validity
cells, never claim rows.
**Claim task.** CIFAR-10 with headroom. **Primary geometry: Linear+ReLU, no norm**
(c≈1). LayerNorm is the fallback only if the plain stack fails the floor; it sets
c≈2 and requires the Appendix recompute in the same commit. BatchNorm is
excluded (non-local, breaks batch-1 streaming). The data is cached
(`data/cifar-10-batches-py`), but the registry marks it `CostClass.EXPENSIVE`:
use a **fixed 10k-image train subset and the full test split** for the ladder, and
name that bound in every row. The absolute vision criterion (>0.95) does not apply
to a flat-MLP memory ladder: W1/W2 are **relative** claims, and a 45–60% MLP is
not a failure verdict.
**Binding operating point.** Depth/width/batch are **hyperparameters and run
settings, not registry axes** (`num_layers` is an integer hyperparameter,
`batch_size` a run setting). Ladder: depth 4/8/16/32/64, width 1024/2048,
**batch 1k/8k/16k**, dtype fp32 for both arms (local rules often need it; a bf16
backprop vs fp32 local comparison is confounded). **SGD is the primary table;
Adam is a second table and its shares are computed separately.** Never print an
Adam share next to an SGD-primary label.
**Pilot appendix (one binding point, not the grid): B=8192, W=1024, L=64, c=1.**
| Arm (optimizer) | Activations | Params | Optimizer | Peak | Act. share |
|---|---|---|---|---|---|
| `backprop` (SGD) | 2.0 GiB | 256 MiB | — | 2.25 GiB | **89%** |
| `backprop` (Adam) | 2.0 GiB | 256 MiB | 512 MiB | 2.75 GiB | **73%** |
| `backprop+ckpt` √L=8 (SGD) | ~0.53 GiB | 256 MiB | — | ~0.78 GiB | 68% (report only) |
| `backprop+ckpt` √L=8 (Adam) | ~0.53 GiB | 256 MiB | 512 MiB | ~1.28 GiB | 41% (report only) |
The gate reads the **plain `backprop`** row. The ckpt rows are reported, never
gated: at Adam they fall below 50% *by design*, which is why gating on the
recovered arm self-defeats. At B=1024, W=512 the same arithmetic gives
activations ≈134 MB against ≈200 MB params+Adam — the v2 failure mode. Write this
appendix into the pre-registration so the binding check is arithmetic, not
assertion.
### 4.1 Measured binding arithmetic (T4a, 2026-11-15) — **supersedes the c≈1 rows above**
The appendix assumed `c≈1` (stored matmul inputs only). The claim path was
measured: `EpochResources` decomposes the CUDA peak and a two-point depth delta
gives **c = 4.1** (±1 %, W=256, B=2048, L=4/8/16, fp32, Linear+ReLU). The peak
carries four per-layer tensors — stored input, layer output, and the two
backward gradient buffers — and the coefficient is now *measured*, not assumed.
`docs/CORRECTIONS.md` correction 8 records the supersession.

Re-priced at the pilot point (L=64, B=8192, W=1024, fp32, c=4.1):

| Arm (optimizer) | Activations | Params | Optimizer | Peak | Fits 8 GB? |
|---|---|---|---|---|---|
| `backprop` (SGD+momentum) | 8.2 GiB | 256 MiB | 256 MiB | **≈8.7 GiB** | **no** |
| `backprop` (Adam) | 8.2 GiB | 256 MiB | 512 MiB | ≈8.9 GiB | **no** |
| `backprop+ckpt` √L=8 (SGD) | ≈1.0 GiB | 256 MiB | 256 MiB | ≈1.5 GiB | yes |

**Consequence.** The pilot's operating point moves: the claim ladder must be
posed where the arm fits, not where the old arithmetic said it would. Affordable
points at W=1024 with an 8 GB card and 20 % headroom (≈6.4 GiB budget):

| B | L | Activations (c=4.1) | Peak (SGD+momentum) |
|---|---|---|---|
| 8192 | 32 | 4.1 GiB | ≈4.6 GiB |
| 16384 | 16 | 4.1 GiB | ≈4.6 GiB |
| 8192 | 64 | 8.2 GiB | 8.7 GiB — **skip** |

So the **claim ladder is B=8192 at L≤32, or B=16k at L≤16**, and the depth rung
that wins W2 is bounded by the card, not by the model. The gate still binds
(measured share 0.95 at B=2048/L=8, and the share rises with depth), so the
verdict is unchanged; only the coordinates move. **The checkpointed arm's ≈1.0
GiB activation set is what makes the depth claim possible at all** — that is the
measured reason T4b gated T6, and the landed arm measures 3894 MB of epoch peak
at L=64/W=1024/B=8192 (forward retained set 480 MB, §9.4).
**Minimal claim ladder (register this, not the grid).** B=16k for L=16/32;
B=8192 for L=64 when c>1; W=1024; both arms; 5 paired seeds → **~30 cells**. The
5×2×3 grid is the artifact/screen, not the claim. Admission-check each cell's
measured cost against the 8 GB card with 20% headroom; skip the unaffordable.
**Arms.**
1. `hybrid` — lockstep-local trunk (O(B·W) working set) + 2–4 layer backprop
   head; PEPITA-trunk first (one global error from the head, no auxiliary params
   beyond the feedback matrix); InfoPro-style auxiliary heads second, with their
   params and optimizer state inside the memory ruler.
2. `local` — pure local control (the rule P1 validated).
3. `backprop` — plain.
4. `backprop+checkpointing` — √L segments.
5. optional `backprop+ckpt+optimizer-offload` — a **priced** arm; offload trades
   PCIe bandwidth, and optimizer offload is arm-neutral, so the differential is
   activations only. Say so; do not present it as extra arm surface.
**Hybrid integration (T3b ✅, landed 2026-11-16).** `System.credit` is a single
config (`ontology/system.py:426`); there is no per-layer credit. `HybridCredit`
is a C wrapper that owns a `PepitaTrunk` contrast and a `GradientCredit` head and
dispatches by layer index; it delegates the head to
`GradientCredit.gradient_of` rather than reimplementing autograd. No schema
change; one registry row and one declared `estimator_kind`.
**Composed pilot (T6 ✅, landed 2026-11-16).** The point and both controls are
measured on the claim path (`validation/memory_frontier.py`; §2.4). Two blockers
came out of it; both are now decided: **T6b ✅** — the pipeline's eager store-all
forward survived composition (hybrid 1.98× the checkpointed arm's activation
set); a credit may now own its free pass, and the hybrid reads **611 MB against
the checkpointed arm's 1637 MB (0.37×)** at the claim point (CORRECTION 18);
**T6c ⛔** — the plain stack sits on the loss plateau at L=32. Its cheap pass
(`stream_norm`) leaves the plateau but misses the floor and costs 1.45× bytes
(§2.10), so the depth rung needs §4's LayerNorm fallback (c≈2) with a recomputed
appendix, or the Innocenti init on a residual geometry. Neither is a verdict on
the credit; T6b is a memory precondition now met, T6c a depth precondition still
open.
**Reuse the runner, do not build a second ladder.** `validation/backprop_parity.py`
already implements a depth loop with per-depth baseline, seeds, bootstrap CIs,
peak memory, FLOPs, and parameter counts (`run_parity`, :729). Extend it with a
`batch_size` parameter and the `pepita`/`local_goodness` families (its portfolio
today is backprop/FA/PC/eqprop) and use it as the cell runner. Add only the Pareto
aggregation on top.
**Budgets.** Report params as a column, **not** a matched budget: matching params
across hybrid/local/backprop needs a width search and buys nothing the claim
needs. Report accuracy at (a) matched peak memory and (b) iso-walltime/
forward-equivalents. Two tables, one Pareto figure
(`computronium/experiment/analysis/pareto_analysis.py:compute_pareto_frontier`),
plus a stacked memory decomposition (params / optimizer / activations /
auxiliary) per arm.
**Claim shape (if W1/W2 hold).** "At 8 GB and matched walltime, the hybrid
dominates √L-checkpointed backprop on (accuracy, peak GB) — ≥δ hypervolume or
baseline accuracy at ≤0.5× **activation bytes** — and the local trunk reaches 2×
depth at
the accuracy floor." Pre-register the floor, the budgets, δ, the LR box, and the
binding arithmetic before seed 1.
**Stop rule.** Hybrid loses to `backprop+ckpt` at matched memory and matched
walltime → close MPU1 entirely, one verdict, no rescue tuning. Pure local losing
while the hybrid wins is the expected result and is not a stop.
---
## 5. P3 — MPU2: an architecture backprop cannot differentiate
**Why this is the novelty engine.** The only genuinely new capability available is
an architecture whose forward pass has operations with no useful derivative: hard
top-k routing, discrete selection, learned sparse connectivity, spiking
thresholds, in-network memory writes. Local credit needs no surrogate; backprop
must invent one, and the surrogate is biased.
**Run the cheap screen now, in parallel with P1.** STE-gap versus stacked
discrete-op count (1/2/4/8) against a soft-relaxation upper bound. If the gap
grows with depth, the matched pair is worth running. If it is flat, drop the
track after one session — that is the stop rule, not a failure.
**Candidate (pick one, not four).** Hard top-k routing where only k of n experts
receive a gradient-bearing path. `algorithms/routing/` already holds the routing
implementation; start there, do not build a new router.
**Baseline (strongest, not most convenient).** STE **plus load-balancing/z-loss**.
Expert-choice routing and dense-backprop-for-sparse-MoE are positioning controls
and literature anchors, not extra arms. "Local beats vanilla STE" is not a
publishable claim; vanilla STE is not the strongest baseline.
**Mechanism metric, defined.** Gradient bias of the estimator arm relative to a
**declared reference**: the temperature-smoothed routing gradient, and/or a
finite-difference estimate on a small net. "Bias magnitude" without a reference is
undefined — the true gradient of hard top-k is zero almost everywhere. The
forward-mode reference is scoped to a pure `nn.Sequential` first; if the composed
system is not functional (in-place ops, stateful settle), it is
**reference-only**, never an arm.
**Design.** Router accuracy and end-task accuracy at matched walltime; the bias
measurement is the mechanism claim.
**Stop rule.** STE+aux wins by ≥1 pp at the ladder's best point → publish the
bounded observation with the measured bias; do not tune the local arm to rescue
it.
---
## 6. P4 — MPU3: streaming without replay
**Why.** Batch-1, non-stationary data, no replay buffer: the regime where the
memory advantage is structural rather than a trade against checkpointing. But
locality does not address forgetting — that is weight interference — so the
mechanism under test is local credit **composed with consolidation**.
**Plasticity first (cheapest falsifier).** Final-task accuracy at batch 1. If the
local arm cannot learn the stream at all, retention is moot; stop there.
**Protocol.** A fixed sequence of 5 tasks, 1 epoch each, fixed order
(`SplitMNIST` first), presented once. Metrics: final-task accuracy (plasticity),
`CLMetrics.backward_transfer`, `avg_forgetting`, and `peak_memory_mb`, at
matched per-step cost. Name the order and the epoch budget in the registration;
a drifting distribution needs a declared generator, not a description.
**Arms.** The continual runner and its arms already exist
(`core/continual/runner.py`, `create_ewc_arm`, `create_si_arm`,
`create_replay_arm`, `SplitMNIST`). P4 is a **protocol and measurement** ticket,
not an implementation ticket:
- `local × EWC/SI` — `ElasticConsolidationUpdate` (`core/continual/arms.py:90`);
  `SynapticIntelligence` already exists at `core/continual/losses.py:84` and is
  lifted to a U row by T8, not rewritten;
- `backprop × EWC/SI` (the strong baseline);
- `backprop × EWC/SI ± small replay` — replay is priced at matched memory, and in
  the GB regime it is cheap, so a matched-memory replay comparison is a **foregone
  negative** and must not be the claim;
- optional compositional: `local × EWC` vs `backprop × EWC` at matched memory and
  iso-cost.
**Runner.** Use the existing `run_continual_learning`
(`core/continual/runner.py`); do not build a stream harness.
**Matched budget.** A pre-registered **analytic byte cap** (replay buffer +
consolidation state ≤ cap), enforced in the GPU runner, plus matched per-step
cost. "MCU-class" is a byte budget, not a device claim — the run is CUDA. If the
contest is GB-scale memory, replay wins by design and the result is
uninformative. **Consolidation state counts:** EWC's Fisher/importance vectors and
SI's +1× parameter state enter the cap, or the local arm gets a free budget.
**Stop rule.** Replay saturates retention at the tiny budget → close MPU3 and
record the saturation point. A replay-wins negative is a coordinate result, not a
verdict on local credit.
---
## 6a. The three unprobed tracks (D, E, F)

These carry promises from `PURPOSE.md` that no TODO has ever measured. Each is
sized to reach a decision in one session, and each reuses an existing asset — no
new primitive is admitted before the screen promotes.

**D — substrate-native training (D1 promoted; D2 refused the walltime box).** *Question:*
on a constrained substrate model, does a learning system reach digital parity at
lower state? *Arms:* ternary + `energy_minimization`, memristive + the same
credit that works digitally, and a digital control. *Rulers:* device state per
step (bytes), train state (declared), accuracy, and the constraint that binds
(quantization, bounds, drift) — a parity claim must name it. *Stop:* cannot
train on the substrate, or no state saving at parity → park with a reversal
trigger. *Why this one matters:* substrate → algorithm pairing is the project's
most distinctive promise and the only one that cannot be copied from the ML
literature. The models and the settle kernel already exist; the missing artifact
is one matched row.

**D1 landed (2026-11-16) and promoted memristive.** The ladder ran 24 cells
(617 s on CPU): a per-arm 3-point LR viability ladder at settle 10, then the
5/10/20 settle ladder at the arm's best LR. The learning control reads 0.9234;
at settle 20 the memristive arm reads **0.9097** against the digital rule's
**0.9097** on the confirmation seed (0.05 pp), at **2 B/weight against
4 B/weight**. Ternary's best point is 3e-3 (0.835 / 0.861), 5.2 pp below the
digital rule, so it **refuses at this box** at 2 bits/weight. **D2** is
therefore the matched comparison: memristive + `energy_min` against the digital
rule at matched settle compute, digital backprop at matched walltime, and the
int8-quantised digital control at the same width; 5 paired seeds, CIFAR-10 quick
mode or MNIST at 2× width. D2 needs no new primitive.

**D2 landed and refused the matched walltime (2026-11-16).** D2 reused the
D1 runner at *2×* D1's width (MNIST quick mode, 784-64-10, batch 32, 600
batches, one epoch, β=0.5, full 10k test split), froze the LR at D1's 1e-2,
and ran 24 cells (915 s, CPU; ~16 min of cells, ~20 min wall clock). It
added the int8 quantise-dequantise control and a replayable paired gate; it
did **not** add a primitive.

- **Settle extension: refused.** At 2× width the memristive arm reads 0.9259 /
  0.9276 at settle 20/40 (seed 57) and 0.9245 / 0.9240 (seed 58): +0.17 and
  −0.05 pp, below the 0.5 pp adoption margin. D1's upper-edge gain did not
  reappear, so the matched box stayed at settle 20.
- **Five paired seeds at settle 20 (LR 1e-2).** The digital rule reads 0.9280
  / 0.9277 / 0.9322 / 0.9258 / 0.9298; the memristive arm 0.9237 / 0.9253 /
  0.9293 / 0.9224 / 0.9272. The paired gap is −0.43 / −0.24 / −0.29 / −0.34
  / −0.26 pp, **mean −0.31 pp, paired 95% interval [−0.41, −0.22]** — inside
  the 1 pp parity margin at 2 vs 4 B/weight.
- **The cost ruler fails.** The memory arm costs 2.18 / 2.21 / 1.35 / 2.26 /
  2.44× the digital rule's walltime at matched settle compute (**mean 2.09×**,
  limit 1.2×; 4/5 seeds over the line). The forward-equivalents ratio is
  **1.00×**: the extra cost is the differential pair's conductance
  programming on every forward and update, not extra passes.
- **The int8 width is harmless.** The QDQ control reads 0.9278 / 0.9275 /
  0.9303 / 0.9263 / 0.9310, **−0.01 pp mean** against the digital rule; a
  parity claim cannot be attributed to the width. The learning control reads
  0.9367 / 0.9351 / 0.9277 / 0.9377 / 0.9376, far above the 0.55 floor.
- **Verdict: refuse the substrate path at this box.** The saving does not
  survive the matched-budget comparison: accuracy parity holds, but the device
  path costs 2.09× walltime at matched settle compute. The measured mechanism
  is the **programming budget** (host-side conductance programming), not the
  conductance levels and not drift. D3 does not fire: its trigger is parity at
  matched walltime. The re-open is a device-level or compiled quantisation of
  the conductance pair, not another seed.
- **One apparatus correction.** `QuantizedSubstrate` claimed int8 precision,
  but its forward cast operands to int8 and never quantised. It now uses the
  float forward with asymmetric per-tensor int8 QDQ and a straight-through
  gradient, so the control prices the representation. `DEVICE_BITS` gains
  `qdq = 8` bits/weight (+ one fp32 scale per tensor), and `_build_system` /
  `_box` take `hidden_dims`, so the 2× box needed no second runner.
- **Locks.** `tests/unit/validation/test_matched_substrate.py` (13 tests)
  pins the paired interval, the cost ruler, the QDQ forward/STE and width,
  the extension screen, the box width, and the cell-log replay. The table is
  `results/t93_d2/matched.md` + `matched.json`; `matched.cells.jsonl` replays
  the gate without training.

**E — estimator atlas.** *Question:* at matched compute on one task, what are the
bias/variance/compute coordinates of each estimator kind? *Arms:* exact
(`gradient`), gradient-approximation (FA/DFA/TP/PC-ALM), objective-local
(PEPITA/local_goodness/FF), hybrid. *References:* the smoothed-routing gradient
and a finite-difference estimate on a small net; objective-local arms report
update-direction alignment and `bias_reference="none"`, never "bias". *Rulers:*
angle and magnitude vs the declared reference, variance across seeds,
forward-equivalents, matched budget. *Stop:* six arms, then the table is the
artifact — it is publishable whether or not anything wins, and it makes every
later comparison commensurable. This is T7's real job, promoted from
"conditional on the screen".

**F — composition screen.** *Question:* does any legal 6-axis composition beat
the best single-axis default by ≥δ at matched budget? *Design:* one cheap task,
~50 legal cells drawn from the existing search space (the generator already
filters compatibility), with the best single-axis default as the reference —
best credit × default everything else. *Metric:* task metric at matched
forward-equivalents; δ pre-registered before the cells run. *Stop:* flat → the
composition thesis gets a written defect probe, and the artifact records the flat
region. *Why:* the 6-axis generator is the repository's central claim. If
composition never beats the best single axis, that is the most important thing
this plan can learn — and it is one session, not a campaign.

---
## 7. T0/D1 — deferred, manual tag now
The affinity instrument serves the composition-wide **search**, which §12 defers.
The six tracks are targeted experiments and need no proposal bias. So:
- now: one manual `regime` tag on cells (a `StrEnum`, no proposal bias, no A/B);
- schema (`AxisSpec.regime_affinity` beside `target_kind` at
  `experiment/schema/axis.py:116`), coverage, and locks stay written for when the
  search re-enters;
- **D1 after P2**, and power it first: promotion is rare by design, so 300
  cells/arm yields single-digit events and "CI excludes 0" is likely undecidable.
  Use a continuous surrogate (screen-score uplift, native share) or pre-register
  a larger n.
**Invariants (unchanged):** affinity biases a proposal, never refuses a cell;
`--no-affinity` exists; an empty affinity set needs a written reason; the lock
fails if the field's removal leaves proposals unchanged on a seeded fixture; a
below-bar foreign cell is `[regime-mismatch]`, not a defect.
---
## 8. Tickets by track (parallel, unparked)
The DAG is gone. A ticket belongs to a **track**, a track promotes on a gate,
and the portfolio rank (§14) decides what runs next. Landed tickets stay as the
record of what exists.

| # | Ticket | Track | Cost | Gate / output |
|---|---|---|---|---|
| T1 ✅ | **Truth pass** (stub fixes, measured complexity table, estimator declarations, locks) | all | 1 session | each lock fails on the pre-change code |
| T3 ✅ | Lockstep two-pass FF/PEPITA | A | 1 session | O(B·W) peak, flat in depth; max\|ΔW\| ≡ 0 |
| T4a ✅ | Memory decomposition + binding guard + calibration lock | A | hours | `c·L·B·W·4` within 10 % |
| T4b ✅ | `backprop+ckpt` (√L segments) | A | 1 session | §4 ladder; gradient parity under dropout |
| T4c ✅ | Ladder runner with `batch_size` + `pepita` family | A | hours | one runner, no second depth loop |
| T3b ✅ | `HybridCredit` (trunk local + head backprop) | A | 1–2 sessions | composes; trunk flat; head exact |
| T6 ✅ | Composed pilot at one binding point | A | 1 session | controls pass; two blockers named |
| **T6b ✅** | **Composed-path memory**: a credit owns its free pass | A | landed 2026-11-16 | hybrid 210 vs ckpt 437 MB (0.48×) at the lock point and 611 vs 1637 MB (0.37×) at the claim point; xfail flipped; CORRECTION 18 |
| **T6c ⛔** | **Trainable claim depth**: LayerNorm (c≈2) or depth-stable init, appendix recomputed | A | landed 2026-11-16 | **refused its cheap pass** (`stream_norm`): 0.314 / 0.326 vs floor 0.375, edge 1e-1 collapses, 3× steps 0.360, 1.45× bytes; trigger = LayerNorm (c≈2) or the Innocenti init |
| **T6a ✅** | **Memory-frontier registration**: floor, budgets, `n_max=5`, binding appendix, stop rule | A | landed 2026-11-16 (~2 min) | **registered and its rung-2 screen refused the claim**: at the L=4→8 box (W=512/B=2048) hybrid 0.167/103 MB vs ckpt 0.385/85 MB (1.22×); confirmation 0.154 vs 0.363; controls pass (c=4.25, spread 0.0%; backprop 0.385 vs floor 0.375); 30 claim cells priced, none run |
| **T6a₂ ⛔** | **Re-registration at the pass-carrying box**: L=8→32, W=512/B=4096, stream-norm, its own committed path | A | landed 2026-11-17 (21 cells, ~300 s) | **refused**: hybrid 0.184 / 210 MB vs ckpt 0.364 / 453 MB (**0.46×**, memory met); confirmation 0.201 vs 0.357; controls PASS (c=4.125; learning 0.409 vs 0.399); CORRECTIONS 21–22; 30 priced cells, none run |
| **T6d ⛔** | **The hybrid's update**: `train_biases`, `feedback_scale`, a head-only control at the pilot box, plus the sibling whole-stack control | A | landed 2026-11-17 (~200 s) | **refused at the pilot box**: no trunk knob reaches the floor, and the sibling localizes the mechanism at the split; T6e is the defect fix |
| T6c re-open | Depth rung: LayerNorm (c≈2) or the Innocenti init, appendix recomputed (side track) | A | trigger only | the pass already trains at L=32/B=4096 (0.364, 1.1 pp below the old floor), so only the stack's last pp of trainability, not the hybrid's 17 pp gap |
| **B1 ⛔** | **Routing ladder**: STE-gap vs stacked discrete-op count 1/2/4/8 × 3 STE temperatures/LRs; soft-relaxation bound | B | landed 2026-11-16 | **refused at this box**: gap 0.819 → 0.660 (−0.159) at τ=0.25 and −0.037 on the confirmation seed vs δ=0.05; reference FD 0.013; both ends above the floor; B2 not run, trigger in §14 |
| **C1 ✅** | **Plasticity ladder**: batch-1 SplitMNIST, 5 tasks, LR ladder (1e-3/1e-2/1e-1) + confirmation seed | C | landed 2026-11-16 | local **0.945 / 0.947** at LR 1e-3 on 2 seeds, control 0.839 / 0.893, floor 0.55 → **promote to C2**. Best point is the lower edge; a downward extension (3e-4/1e-4) is the next rung if an optimum is claimed |
| **C2 ✅** | **Retention ladder**: 3-point EWC-strength ladder (λ = 1/10/100) at the frozen LR, local × EWC vs backprop × EWC, matched per-step cost | C | landed 2026-11-16 | local 0.952 / 0.015 vs control 0.963 / 0.020 at λ=100 (gain +0.005 < δ 0.032); confirmation 0.951 / 0.016 vs 0.958 / 0.024 → **close C at the saturation point**; task-start anchor defect fixed (CORRECTION 12) |
| **D1 ✅** | **Substrate ladder**: ternary/memristive + `energy_min` at `max_steps` 5/10/20 vs the digital rule; per-arm LR ladder, 2 seeds, device state | D | landed 2026-11-16 (617 s) | **promoted memristive**: 0.9097 vs 0.9097 at settle 20 on the confirmation seed, 2 vs 4 B/weight; ternary refused (0.861 vs 0.913, 2 bits/weight); CORRECTION 17 (per-arm LR) |
| **D2 ⛔** | **Matched substrate comparison**: memristive + `energy_min` vs digital rule at matched settle compute, digital backprop at matched walltime, int8-quantised digital control | D | landed 2026-11-16 (915 s) | **refused at the walltime box**: −0.31 pp (CI [−0.41, −0.22]) at 2.09× walltime (limit 1.2×); QDQ −0.01 pp → the programming budget binds; D3 does not fire; re-open = device-level/compiled quantisation of the pair |
| **E1 ✅** | **Estimator atlas**: bias/variance/compute for 6 estimator kinds at matched compute | E | landed 2026-11-16 | 18 claim cells (6 arms × 3 seeds) + 22 ladder/confirmation cells; controls pass; table is the artifact; PC-ALM depth-2 regime mismatch/refusal with a depth-100 trigger |
| **F1 ⛔** | **Composition ladder**: 50 legal cells vs 41 legal single-axis arms, then a 3-point ladder on the best-looking family | F | landed 2026-11-16 (~19 min) | **refused at this box**: reference 0.797 (`update`), screen best 0.669 (4 axes), family (`random_projections`) ladder 0.092/0.783/refused at w=6 vs bar 0.807; confirmation 0.814 is a 3.1 pp seed spread > δ; trigger = F2's five seeds, a matched-parameter composition, or a real task family |
| T5 | P1 scoped: 3 publishables + the hybrid trunk rule | side | 1–2 sessions | rows with backend path, dtype, optimizer, σ |
| T7 | The estimator family: `ForwardTangentCredit`, `ScoreFunctionCredit`, `ZerothOrderCredit` (§19 row 1) | C | 1 session | **next session**: three credits, each with an identity card, parity lock, and capability card |
| T8 | Lift `SynapticIntelligence`; `CascadeSynapsePlasticity` (§19 row 7) | C | 1–2 sessions | C1 promoted; the lift is the capability |
| T9 | Temporal taxonomy (`EligibilityProp`, UORO, RTRL ref; §19 row 6) | C, G | 2–3 sessions | the sequence axis is the capability |

**Defect gates.** A track advances when its gate is met at a **named budget**,
not when a cell looks good. A low cell is a defect probe (rung 0: does the
mechanism update at all?) and enters the record as a defect with its fix, never
as a verdict. A ladder that stays empty writes (a) the knob box, (b) the named
defect candidate, (c) the fix and the capability it unlocks in §0.6/§14 — that
is work, and it never deletes the idea.

**Two falsifiers, two numbers, restated.** The implementation falsifiers are
closed (T1–T3b, T6), **B1's depth axis is a defect probe** with its fix kept,
**E1's atlas is a capability map** with its table, and **D1 promoted one
substrate arm** with the other a defect probe. D2's matched comparison measures
the programming budget. F1 has now screened 50 legal compositions and refused them at its
box, so F2 is a trigger, not a rung. What remains is a **portfolio of cheap
falsifiers**: A's two blockers can each cancel a track for hours; D3 and F2 are
triggers. The expensive falsifier (A's claim) is deliberately last, because it
is the only one that needs five paired seeds on a real task.

### 8.1 Remaining work, ordered (start here next session)

| Order | Track | First command / file | Done when |
|---|---|---|---|
| 0a ⏳ | **P0 — estimator family** (next) | `ontology/credit/` + `primitives/credit_assignment/{forward_tangent,score_function,zeroth_order}/`; three identity cards, registry rows, parity locks (§19) | each primitive trains a tiny task above chance; the unbiased estimates match finite differences and their variance falls as 1/√n; dispatch and identity locks pass |
| 0b ⏳ | **P0b — routing** | `SurrogateCredit` + a hard top-k geometry and task family | hard top-k trains; the surrogate estimate tracks the smoothed reference within δ on the routing task |
| 0c ⏳ | **P0c — depth fix** | normalization + a decoupled trunk LR (the T6c/T6d defect, not a verdict) | the plain stack trains at L=16/32 above the floor; the hybrid's split is priced |
| 1 ✅ | A — `backprop+ckpt` | landed 2026-11-15 | checkpointed grads ≡ plain under dropout; segments=√L; epoch peak 3894 MB < 6554 MB at L=64/W=1024/B=8192 |
| 2 ✅ | A — lockstep two-pass FF/PEPITA | landed 2026-11-16 | deltas ≡ store-all at `atol=0`; peak flat 66.3 / 58.5 MB at L=4→32 |
| 3 ✅ | A — hybrid trunk + head | landed 2026-11-16 | parity max\|Δ\| = 0.0; head ≡ backprop; trunk flat 81.0 MB |
| 4 ✅ | A — composed pilot | landed 2026-11-16 | c=4.125; controls pass; blockers T6b/T6c |
| 5 ⛔ | **B — routing ladder** | `computronium/validation/routing_ladder.py`; landed 2026-11-16 | **refused at this box**: gap 0.819 → 0.660 (−0.159) at τ=0.25, −0.037 on the confirmation seed vs δ=0.05; reference FD 0.013; trigger in §14 |
| 6 ✅ | **C — plasticity ladder** | landed 2026-11-16 | local 0.945/0.947 at LR 1e-3 on two seeds; control 0.839/0.893; floor 0.55 → **promote to C2** (retention); best point is the ladder's lower edge, so the downward extension is the next rung |
| 7a ✅ | **C2 — retention ladder** | `results/t93_c1/consolidation.json` (replay: `... --stage consolidation --replay`) | **closed at the saturation point λ=100**: local forgets 0.005 less than the control, below δ=0.032, at 1.07× cost; confirmation seed repeats |
| 7b ✅ | **E — estimator atlas** | `computronium/validation/estimator_atlas.py`; E-lite then `--full`; replay from the cell log | **landed 2026-11-16**: controls pass (FD 1.0000; exact 0.914 ± 0.006); 6 arms × 3 seeds at a matched box with a per-arm LR ladder; table is the artifact; PC-ALM depth-2 regime mismatch/refusal with a depth-100 trigger |
| 8 ✅ | **D — substrate ladder** | `computronium/validation/substrate_ladder.py`; landed 2026-11-16 | **promoted memristive** (0.9097 vs 0.9097, 2 vs 4 B/weight on two seeds); ternary refused with a re-open trigger |
| 9a ✅ | **A — T6b: a credit owns its free pass** | `core/pipeline.py::_run_free_pass`; `HybridCredit.free_activations`; landed 2026-11-16 | **landed**: hybrid 210 vs ckpt 437 MB (0.48×) at the lock point and 611 vs 1637 MB (0.37×) at the claim point; strict xfail flipped; tripwire lock; CORRECTION 18 |
| 9b ⛔ | **A — T6c: the depth rung** | `validation/memory_frontier.py::depth_rung`; `--rung`; landed 2026-11-16 | **refused at this box**: plain L=32 0.100, stream-normalized 0.314 (seed 21) / 0.326 (seed 23) vs floor 0.375; edge 1e-1 → 0.100; 3× steps → 0.360; 1.45× activation bytes; trigger = LayerNorm (c≈2) or the Innocenti init on residual (§2.10) |
| 10 ✅ | **D — D2 matched comparison** | `computronium/validation/matched_substrate.py`; landed 2026-11-16 | **refused at this box**: parity −0.31 pp (CI [−0.41, −0.22]) at **2.09× walltime** (limit 1.2×); QDQ −0.01 pp (width harmless); control 0.9366; the programming budget binds; D3's drift trigger stays parked |
| 11 ✅ | **F — composition ladder** | `validation/composition_ladder.py`; landed 2026-11-16 | **refused at this box**: 50/50 cells measured; screen 0.669, family ladder 0.783, reference 0.797, bar 0.807, confirmation 0.814 (3.1 pp drift); replayable from `results/t93_f1/`; next is **F2** (5 seeds) or T6a |
| 12 ⚠️ | **A — T6a registration** | `configs/preregistrations/t93_memory_frontier_registered.json`; replay `--register` | **`invalid-box` (CORRECTIONS 19–20)**: the ratio is depth-declared — 1.22× (L=8), 0.75× (L=16), 0.53× (L=32) at W=512/B=2048, and 0.48× at L=32/B=4096 (1.16 GB, fits); the accuracy bar ends at L=8 (0.385) while L=16/32 read 0.100 for **every** arm (both seeds, both batches), so no point satisfies both bars. The registration stands as measured; the claim re-registers at L=32/stream-norm 3e-2 or as the ratio curve |
| 12b ✅ | **A — T6a re-registration** | `validation/memory_frontier.py::run_registration(STREAM_BOX)`; `--re-register`; landed 2026-11-17 | **refused at the pass-carrying box** (L=8→32, W=512/B=4096, stream-norm, 21 cells, ~300 s): controls PASS (c=4.125; learning 0.409 vs 0.399), memory bar **met** (0.46×), accuracy missed by 17 pp (hybrid 0.184/0.201 vs ckpt 0.364/0.357, floor 0.354); the mechanism is the hybrid's own update; CORRECTIONS 21–22; artifacts `results/t93_a_stream/` |
| 12c ✅ | **A — T6d: the hybrid's update diagnostic** | `computronium/validation/hybrid_update.py` (new); 12 measured cells (14 planned), ~200 s; cell log + `--replay`; landed 2026-11-17 | **refused at the pilot box**: no trunk knob reaches the floor (bias flag +0.5 pp, `feedback_scale` 0.163/0.100/0.100, head-only 0.149) while the same trunk rule as a whole stack reads 0.400/0.405/0.384 and does not collapse; the mechanism is the **split at the boundary**, and the hybrid's activation set is 1.06× the reference's at L=8; CORRECTION 24; artifacts `results/t93_a_stream/hybrid_update.{json,md}` |
| 12d | **A — T6e: the split's position** (defect fix) | `validation/hybrid_update.py` at the pilot box with `split_layer` on the last Linear (7 trunk layers + a readout-only head), then a decoupled trunk learning rate (gamma × lr as one box); the unit test prices both | the hybrid reaches the ckpt's floor when the head is one layer, or the split's position is refused with the mechanism and a new trigger; no claim run is scheduled before a mechanism reaches the floor |
| 13 | **A — T6c re-open** (trigger only) | `validation/memory_frontier.py::depth_rung`; LayerNorm (c≈2) or the Innocenti init at L=16/32 | the pass already trains at L=32/B=4096 (0.364, 1.1 pp below the old floor), so this is a side track: only the stack's last pp of trainability, not the hybrid's 17 pp gap |
| ∥ | **T5** — published parity | §3 method | one row per (credit, dataset, arch, backend path) with Δ and σ |
| gate | **T7 / T8 / T9** | E1 closed (not promoted) / C1 promoted / trigger | T7 stays parked (E did not promote); T8's trigger fired but is a side track; T9 waits on MPU1 or a sequence axis |

**Rows 5, 9b, 10, 11 and 12a–12c are defect probes (CORRECTION 25).** The
numbers stand as measurements; the verdict words do not. Each carries its named
defect and the capability the fix unlocks (§0.6). Rows 0a–0c are the new order:
primitives first.

**What the next session must not re-derive:** the decomposition API
(`EpochResource.{params,optimizer,activations,auxiliary,cpu_rss}_mb`,
`binding_verdict`), the measured coefficient (`c=4.1`, so the peak is 4× the v6
appendix), the ladder runner (`run_parity(batch_size=...)` with the `pepita`
family), the checkpointed arm (`create_backprop_mlp(checkpoint_segments=...)`,
`enable_gradient_checkpointing`, segments split at Linear starts), the lockstep
rung (`lockstep_contrasts(chain_a, chain_b, final_activation=...)` — one stream
for both families; `apply_contrast` updates in place; the store-all `forward_*`/
`backward` methods are the reference rung the lock holds at `atol=0`), the
hybrid (`HybridCredit` in `ontology/credit/_hybrid.py`: `PepitaTrunk` contrast,
`GradientCredit.gradient_of` for the head, `split_layer` on a Linear, and
`FeedforwardGeometry.step_layer` for one-layer lockstep with the residual input
threaded; the store-all reference is written from the equations in
`test_hybrid_parity.py`), the pilot (`validation/memory_frontier.py`:
`PilotPoint.activation_mb/peak_mb/affordable/stream_norm`, `build_arm` with one
shared geometry/init/update and `checkpoint_segments=isqrt(L)`, `depth_rung` and
its own `STREAM_LR_LADDER` box, `run_pilot` writing `results.json` +
`appendix.md`, `_measure` as the one cell loop, `RegistrationBox` /
`AS_REGISTERED` / `STREAM_BOX`, `run_registration(box)`, `--re-register`, and
`learning_control_gate` with `LEARNING_FLOOR=0.25`), the owned free pass
(`CreditAssignment.free_activations`; the pipeline skips the pre-forward, the
FREE settle, and the free-metrics settle, and its tripwire lock), the atlas
(`validation/estimator_atlas.py`: `_build_arm` reads each credit's identity
card, `_reference_delta` is the exact arm's one-step reference, `_train` takes
the per-arm LR, `_run_cell`/`_refusal_cell` write the kill-safe log, and
`replay_estimator_atlas` recomputes the table without training; the per-arm LR
ladder is 1e-3/1e-2/1e-1 at seed 59 with confirmation 60 and claim seeds
61/62/63), the substrate ladder (`validation/substrate_ladder.py`: `_build_system`
composes one rule per arm with `EnergyMinimizationDynamics(compiled=False)` and
`ThermodynamicContrast`, `device_state` prices the device width (0.25 / 2 / 4
B/weight + 4 B/scale per ternary layer), `_run_ladders` is the per-arm LR
ladder then the settle ladder, `_verdict`/`_arm_parity` is the two-seed parity
gate, and `replay_substrate_ladder` recomputes the table; the LR ladder is
1e-3/3e-3/1e-2 at seed 59 with confirmation 60), the matched comparison
(`validation/matched_substrate.py`: `_pair`/`_gate` is the paired 95% interval
plus the walltime and QDQ rulers, `_screen_adopts` is the settle-20/40 screen,
`QuantizedSubstrate` is the int8 QDQ control at 8 bits/weight, and
`replay_matched_comparison` recomputes the gate; the box is 784-64-10, seeds
57/58 for the screen and 71-75 paired, LR 1e-2), the composition ladder
(`validation/composition_ladder.py`: `_single_axis_arms` is the 41-arm
single-axis reference, `_sample_screen` is the seeded 50-cell reservoir,
`_ladder_coordinates` is the family's 2/4/6 width ladder, `_gate` is the
pre-registered screen/ladder predicate with its confirmation seed, and
`replay_composition_ladder` recomputes it; the box is `digits` at 57
forward-equivalents with δ=1 pp and a 50k parameter ceiling), or the refusal list
(FF/SNN contrastive are unavailable with triggers; hybrid refuses
non-feedforward geometry; PC-ALM's card validates depth 100, so a shallow chance
cell is a regime-mismatch, not a refusal; ternary refuses at width 32, so a wider
header or a learnable α per layer is its re-open trigger).
---
## 9. Locks (the plan's culture, applied to itself)
1. **Memory-truth lock** — measured peak per backend matches its declared
   complexity class on a seeded depth ladder (constant vs monotone).
   **FF/PEPITA (`ff_kernels.py`) pass it (flat 66.3 / 58.5 MB); every other
   backend still declares `False`.**
2. **Stub detector** — for every contrastive backend: if the target error is
   non-zero, `nudged_phase` must differ from `free_phase` by more than tol. Kills
   the `pass` stubs at `contrastive_kernels.py:507` and `:747` permanently.
3. **Lockstep exactness** — `max|ΔW_lockstep − ΔW_reference| < tol` per layer on
   a seeded fixture. **Landed: `tol = 0` for FF/PEPITA; the hybrid trunk holds
   the same equality against the store-all hybrid at measured max|Δ| = 0.0
   (locked at `atol=1e-7`).**
4. **Checkpoint parity** — checkpointed gradients ≡ plain backprop under dropout
   with RNG preservation.
5. **Binding gate** — the **plain `backprop`** arm's activation share of peak
   ≥50%, else `[regime-mismatch]`, not evidence. The recovered
   `backprop+ckpt` share is reported, never gated. Enforced by a test over the
   claim table.
6. **Memory calibration** — measured activation bytes match `c·L·B·W·4` within
   10%, with **c measured on the declared geometry** (not hardcoded 1) and locked
   with tolerance. The guard rejects a deliberately non-binding cell. A lock
   whose fixture cannot fail is a comment.
7. **Positive controls** — instrument (calibration) **and** learning (plain
   backprop at L=8 reaches the pilot floor). A failed control invalidates the
   run, not the arm.
8. **State ruler** — the device state is a declared width per substrate (2/16/32
   bits per weight), the train state is the fp32 latent set (equal for every
   arm), and the test asserts the ordering `ternary < memristive < digital` and
   a non-zero byte count. A ruler reported as zero is a fabricated measurement,
   not a saving.
8. **W2 accuracy floor** — a depth counts only if val accuracy ≥ the pre-registered
   floor; "trainable" must mean "learns".
9. **Identity completeness** — backend path, dtype, optimizer, GPU model, torch
   version, forward-equivalents, seed, command, replay hash; missing field = row
   invalid.
Every lock must fail when its mechanism is removed (TODO46 D26).

**Landed 2026-11-15:** locks 1–2 partially (the declaration, the stub detector,
and the anti-fabrication scan: `tests/property/test_kernel_truth_lock.py`), lock
5–6 (`tests/property/test_memory_binding.py`: decomposition sums to peak,
measured `c`, gate rejects a non-binding cell), lock 4
(`tests/property/test_checkpoint_parity.py`: checkpointed grads ≡ plain under
dropout, with an RNG-off negative control and the pilot-point memory budget),
and the estimator-declaration lock for §2's taxonomy
(`tests/property/test_estimator_lock.py`).

**Landed 2026-11-16 (T3):** lock 3 (`tests/property/test_lockstep_parity.py`:
per-layer deltas ≡ the store-all schedule at `atol=0` for both families and both
surfaces, plus the applied-weight check) and lock 1 for the two two-pass families
(same file: peak flat at L=4/8/16/32, with the **retained-stream negative
control** bending to 8.7×).

**Landed 2026-11-16 (T3b):** lock 3 for the hybrid
(`tests/property/test_hybrid_parity.py`: the lockstep trunk ≡ the store-all
hybrid, max|Δ| = 0.0, head ≡ plain backprop, and a no-grad probe whose first
recorded pass is the negative control), lock 1 for the hybrid trunk (peak above
the weight-gradient set flat at 81.0 MB at L=4/8/16/32, with the **store-all
control** bending 122→1018 MB), and the composed-path learning control (rung 1:
`train_step` decreases loss and every weight moves).

**Landed 2026-11-16 (D2):** the paired-gate lock
(`tests/unit/validation/test_matched_substrate.py`: the 95% interval decides
promote/coordinate/refuse, the cost ruler refuses at 1.2×, the width ruler
names the QDQ gap, the extension screen adopts only on both seeds, a control
below the floor invalidates the run, a crash is a refusal with a trigger, and
the log replays the gate). The QDQ lock proves the control quantises (256
levels, float forward, straight-through gradient) and that its 8 bits/weight
state is below the digital rule's 32, so a cast cannot pass as a control.

**Landed 2026-11-16 (F1):** the composition gate lock
(`tests/unit/validation/test_composition_ladder.py`: promote only when the
family ladder and its confirmation seed both clear the bar; a screen winner below
its ladder or confirmation is a coordinate; a flat screen is a refusal with its
trigger; a reference below the floor or a drifting control invalidates the run;
the family selector is a median and refuses a singleton; the width ladder is
2/4/6 non-default axes with the family credit kept; the screen sample is seeded,
deterministic, and multi-axis; the reference sweep varies each axis and is legal;
and the registration is written before the first cell).

**Landed 2026-11-16 (T6a):** the registration and screen locks
(`tests/unit/validation/test_memory_frontier_registration.py`: the registration
cannot be missing a field -- claim, δ, `n_max=5`, the reduced box, the measured
L=8 ladder with its frozen best per arm, the disjoint claim/data seeds, both
controls, the 30 priced cells, the binding appendix, the stop rule; the raw-JSON
loader split (`ThresholdRegistration.from_dict` ignores the extra keys, so the
claim-table test, not the loader, enforces the binding gate); the minimal claim
ladder is 3 arms × L=4/8 × 5 paired seeds and no depth ≥16; a failed control
raises and writes no file; the binding rows price `peak = activations + 2·params`
at a share ≥0.5; the screen refuses the claim when the hybrid is below the floor
or above 0.5×, and is marginal within one held-out resolution; and write/commit
never overwrites an existing registration).

**Landed 2026-11-16 (C1):** a label-channel lock and a data-order lock.
(1) The credit-facing `SystemState` carries the **global** class index
(`local_y + task_start`); the masked loss still uses the local label, so PEPITA's
second pass trains the current task. Without the offset, local scored
0.405/0.426/0.445/0.652/**0.030** per task; on task 1 alone it reached 0.964
(`test_credit_state_carries_the_global_task_target`). `_finalize_output` now stores
the loss it computes, so a FREE-only credit returns a finite loss instead of raising
(`test_local_arm_trains_through_the_continual_step`). (2) Each train loader's
`RandomSampler` owns a generator seeded `config.seed + task_id`, so a credit that
draws from the global RNG (PEPITA's feedback matrix) cannot change the data order
(`test_train_order_is_seeded_independently_of_model_rng`). Backprop read 0.926
before this fix and 0.839 after: a 9 pp data-order swing, so a single row is a
coordinate. `CLConfig.lr` and `si_xi` now reach every factory
(`test_config_lr_reaches_every_credit_arm`). The ladder gate is
`test_plasticity_ladder.py` (promote only on two seeds; a control at chance
invalidates the run).
**Landed 2026-11-16 (C2):** a retention gate (floor on two seeds, matched
per-step cost ≤1.5×, forgetting δ=0.032, saturation at the top rung), a
kill-safe cell log (`_resume_cells`/`read_cells` reuse measured cells, dedupe a
kill-race row), a replay path (`--replay` recomputes the gate without
training), and the task-start anchor lock
(`test_task_boundary_anchors_without_erasing_importance`; `anchor()` moves
`_old_params`/`_baseline` and leaves the drift Fisher intact). The ladder
closed at λ=100 (local 0.952 / 0.015 vs control 0.963 / 0.020; gain +0.005 <
δ), and CORRECTION 12 records the anchor defect the probe found before the
retention claim could be made.
**Landed 2026-11-16 (T6):** lock 7's instrument control and learning control
(`tests/property/test_memory_frontier.py`: `c` within 10 % of the declared 4.1 at
the registered width/batch, plain-backprop share ≥0.5, and L=8 at the floor),
plus lock 5 on the composed path (the checkpointed arm's activation set is
0.39× plain backprop's, so the recovered arm is reported and not gated). Lock 8
(W2 floor) stays open: **no depth rung counts until T6c makes the claim geometry
train**, and T6c refused its cheap pass (§2.10), so the LayerNorm re-open is the
next cell. The hybrid's composed-path memory is no longer an `xfail`: T6b landed
(a credit owns its free pass) and the `0.5×` property is a plain lock.
---
## 10. Baseline ladder, stated once
```
backprop
  └─ + checkpointing (√L segments)                    ← required baseline
       └─ + optimizer offload (priced; arm-neutral)   ← optional, differential = activations only
```
Routing: `STE + load-balancing/z-loss` is the required baseline; expert-choice and
dense-backprop-MoE are positioning controls. Streaming: `backprop + SI/online-EWC`
± small replay; the cheapest falsifier is plasticity before retention. **No arm
is compared against a weaker implementation of itself.**
---
## 11. Artifact-first: the deliverable that survives any measurement
The durable, citable artifact is not a single win; it is:
- `docs/BENCHMARKS.md` — published / ours / delta / σ / command;
- the **measured complexity table** — claimed vs actual per backend, with the
  `pass`-stub rows marked unavailable;
- corrections rows in `docs/CORRECTIONS.md`;
- one **Pareto figure per task** (accuracy vs peak GB at iso-walltime) via
  `computronium/experiment/analysis/pareto_analysis.py:compute_pareto_frontier`;
- a **stacked memory decomposition** (params / optimizer / activations /
  auxiliary) per arm — cheap, and the mechanism behind every verdict;
- a **state-ruler table** per substrate (device B/weight vs train B/weight),
  with the width declared, so a "less state" claim names what a device holds;
- a **composition screen table** with its `composition.registered.json` written
  before the first cell: every legal single-axis arm, 50 multi-axis cells, the
  family's 2/4/6-width ladder, and the disjoint confirmation seed, so a
  composition refusal names its reference, bar, and seed spread.
**Venue, decided now (two artifacts, one program).** **NeurIPS Datasets &
Benchmarks** for the reusable comparator suite — identity cards, measured
complexity table, stacked decomposition, Pareto harness. **TMLR** for the
frontier/negative mechanism analysis. Naming both forces the artifact spec; "decide
later" is how the suite drifts into a demo. The contribution is **rigor and the
frontier**, not terra incognita.
---
## 12. Deferred options (kept with their capability gaps)
Nothing here is discarded; each item re-enters when a task family needs it.
| Item | Why it stays | Trigger to re-enter |
|---|---|---|
| **Phase-conjugate credit** (optical) | a credit mechanism physics provides and digital cannot; `U†` realised by phase conjugation, no stored backward weights | a digital claim lands and needs a substrate contrast, or a photonics collaborator appears |
| **Memristive drift as consolidation** | turns a hardware defect into free EWC-like anchoring | P4 closes with **either** verdict — a replay-wins negative is precisely the evidence that motivates substrate anchoring — and a device model with retention exists |
| **Per-layer substrate placement** | the only way to express digital front-end + analog back-end | a substrate signal exists |
| **CSP settling (`energy_structured`)** | settling *is* the algorithm on such tasks | a digital memory/streaming result lands, or a practical CSP use case appears |
| **Composition-wide sweep** | the 6-axis generator remains the long-run idea | three pieces of evidence that composition × regime changes outcomes |
**Why deferred, plainly:** substrate and toy-regime results do not help a user
today. If a digital result needs a substrate control, the trigger fires.
---
## 13. Portfolio discipline (no artificial caps, relaxed)
1. **Every row names its capability, its price, and what stops it.** That is the
   only admission rule; there is no ticket-count quota and no serial gate.
2. **Cost is priced from a measured build**; the watchdog is 2× that price. A
   row that exceeds its watchdog is re-priced or parked, never extended by
   default.
3. **Re-rank every session** by capability gained ÷ build cost; record the
   ranking in §14. Run what the session can support; park the rest with a fix or
   a capability gap.
4. **Screening is wide; claims are rare.** Hundreds of L0 cells allowed; a claim
   freezes five seeds and a pre-registration.
5. **A low number is a defect probe first** (§0.6).
6. **Steering rules — the plan changes itself when results say so.**

| Observation | Response |
|---|---|
| W1/W2 hold | track A becomes the lead claim; B/C/D run as follow-ups |
| hybrid loses at matched memory and walltime | the split or the LR coupling is the defect; the frontier stays as the artifact |
| pure local loses but hybrid wins | expected; report the composition result, not a local-rule win |
| binding gate red at the pilot | re-pose the operating point (batch/width/dtype); never report the cell |
| STE+aux beats local on routing | narrow B's claim to the estimator that won; keep the measured bias |
| the STE gap is flat across the ladder | the missing surrogate primitive is the gap (§19 row 4) |
| plasticity at chance at C's best ladder point | the label channel or the step scale is the defect; retention is not yet tested |
| replay saturates streaming | measure the saturation point; the long-stream protocol is the capability (§19 row 7) |
| a substrate arm reaches parity with less state | promote D; it is the project's most distinctive claim |
| a substrate arm cannot train at any ladder point | the device model or the programming budget is the defect; park D as a capability gap |
| composition is flat after each family's ladder | record the defect probe; the axis space is the gap (§19 rows 4–6), and E/D carry the plan |
| an atlas row contradicts a published number | T5 defect first; no atlas claim until closed |
| a surprise cell beats its declared expectation by ≥2σ | ticket in the same session; the plan re-ranks around it |
| P1 gaps beyond tolerance | defect tickets only; no measurement claims until closed |
| nothing wins at these coordinates | the coordinates and the box are the result; the defect ledger carries the fixes and a later HPO re-tests a wider box; §12's options lead |

**Portfolio rank (rewrite each session).** List the rows by capability gained ÷
build cost, with the last build cost beside each. A primitive row is a full
session; a defect fix rides its track. A row whose next step adds no capability
is a side track.
## 14. Scoreboard (update in place; rulers mandatory)
| Date | Track | Measurement | n | Ruler | Regime | Verdict | Ticket |
|---|---|---|---|---|---|---|---|
| 2026-11-15 | P1 | complexity audit: 14 fabricated `activations_mb: 0.0` → `None`; 1 stub kernel fixed, 2 marked unavailable; 10 credit rows declare `estimator_kind` | 15 backends, 10 rows | declaration vs measured (none verified yet) | — | **defect found and fixed by failing locks** | T1 ✅ |
| 2026-11-15 | P2 | activation coefficient `c` on the claim geometry | 2 depth deltas × 1 seed | measured `c·L·B·W·4`, spread <1 % | Linear+ReLU fp32, W=256, B=2048, L=4/8/16 (CUDA) | **c = 4.1** (assumed 1 → peak 4× the appendix; pilot point re-posed, §4.1) | T4a ✅ |
| 2026-11-15 | P2 | ladder runner reachability | 2 cells | baseline + family cell returned, `results.json` written | iris, 1 epoch, 1 seed, CPU, 4.9 s | **defect found and fixed** (`batch_size` NameError blocked every campaign) | T4c ✅ |
| 2026-11-16 | P2 | lockstep two-pass rung: exactness and depth-flat peak | 2 families × 4 depths × 1 step | per-layer ΔW vs store-all (`atol=0`); CUDA peak above params | Linear+ReLU fp32, W=512, B=4096, L=4/8/16/32, RTX 3080 10 GiB | **ΔW ≡ 0; peak flat 66.3 MB (FF) / 58.5 MB (PEPITA) vs 576/568 MB retained; three live defects fixed** | T3 ✅ |
| 2026-11-16 | P2 | hybrid credit (lockstep-local trunk + exact head): parity and depth-flat peak | 2 fixtures + 4 depths × 1 step | per-layer ΔW vs store-all hybrid; head vs plain backprop; CUDA peak above gradients | Linear+ReLU fp32, W=512, B=4096, L=4/8/16/32, RTX 3080 10 GiB | **trunk Δ ≡ 0; head ≡ backprop; trunk peak flat 81.0 MB vs store-all 122→1018 MB; composed step learns** | T3b ✅ |
| 2026-11-15 | P2 | `backprop+ckpt` retained set and pilot admission | 2 depths × 1 forward + 1 epoch | forward peak and epoch peak vs the 6554 MB budget | W=1024, B=8192, L=16/64, fp32, RTX 3080 10 GiB | **ckpt fwd 480 MB at L=64 vs plain 2080 MB; epoch peak 3894 MB < budget; grads bit-exact under dropout** | T4b ✅ |
| 2026-11-16 | P2 | composed pilot at the registered point: controls, four arms, decomposition | 3 seeds × 4 arms + 3 calibration + 2 control cells | c at the point (10 %); learning floor at L=8; binding share; activations/peak; fwd-eq | L=32, B=8192, W=1024, fp32, CIFAR-10 10k/10k, 200 steps, RTX 3080 10 GiB | **c=4.125 (0.0 % spread), gate green (0.941), learning PASS (0.419 vs 0.409); four arms at chance at L=32** | T6 ✅ |
| 2026-11-16 | P2 | composed-path memory of the hybrid | 1 cell at the lock point + 1 at the claim point | activation set vs the checkpointed arm | L=32, W=512/B=4096 and W=1024/B=8192 | **defect found and fixed**: hybrid 3249 → 611 MB vs ckpt 1637 MB (0.37×) at the claim point, 210 vs 437 MB (0.48×) at the lock point; mechanism = the pipeline's eager store-all forward; CORRECTION 18 | T6b ✅ |
| 2026-11-16 | P2 | depth rung: plain plateau vs the stream-normalized pass | 9 cells (2 plain, 3-LR ladder, shallow, edge, 2 confirmation) + a claim-point screen | val_acc vs the learning control's floor (0.375); the ladder's own LR box | L=8/32, W=512, B=2048, 200 steps, seed 21/23 | **refused at this box**: plain 0.100, normalized 0.314/0.326 vs floor 0.375; edge 1e-1 collapses to 0.100; 3× steps 0.360; 1.45× bytes → trigger = LayerNorm (c≈2) or Innocenti init | T6c ⛔ |
| 2026-11-16 | B | routing ladder: STE gap vs its smoothed reference over stacked hard selections | 9 cells (3 τ + 4 depths + 2 confirmation) | relative norm gap on 512 probes; reference FD ≤0.10; floor 0.40; δ = 0.05 | blobs 4-class, 8 experts k=2, W=256, LR 1e-3, RTX 3080 10 GiB | **gap 0.819 → 0.660 (−0.159) at τ=0.25; confirmation −0.037; reference FD 0.013; both ends trained (0.933/1.000) → verdict: refuse** (the depth axis is not where the surrogate is wrong; B2 not run, trigger in §14) | B1 ⛔ |
| 2026-11-16 | P2 | C1 apparatus defects: credit label channel and data-order seed | 2 cells + 2 defect probes | task-1 accuracy and backprop at LR 1e-3 | SplitMNIST batch 1, W=256, 30k steps/5 tasks, 1 seed | **defects found and fixed** — local scored 0.030 on task 4 under task-local labels (0.964 on task 1 alone after); backprop swung 0.926→0.839 under the data-order seed | C1 ✅ |
| 2026-11-16 | C | batch-1 plasticity ladder: local (PEPITA) vs exact gradient | 8 cells (2 arms × 3 LR + 2 seeds) | 2000 held-out samples/task (1 σ = 0.011); floor 0.55 | SplitMNIST, batch 1, 1 epoch/task, W=256, RTX 3080 10 GiB | **local 0.945 / 0.947 at LR 1e-3 on two seeds**; control 0.839 / 0.893; forgetting 0.038/0.036 vs 0.145/0.091; **verdict: promote** (coordinate, n=1; best at the lower edge) | C1 ✅ |
| 2026-11-16 | C | consolidation-strength ladder: local × EWC vs backprop × EWC | 8 cells (2 arms × 3 λ + 2 confirmation seeds) | 2000 held-out samples/task (1 σ = 0.011; forgetting σ = 0.016; δ = 0.032); floor 0.55; per-step cost ≤1.5× | SplitMNIST, batch 1, 1 epoch/task, W=256, frozen LR 1e-3, λ=1/10/100, RTX 3080 10 GiB | **at λ=100: local 0.952 / 0.015 vs control 0.963 / 0.020** (gain +0.005 < δ; accuracy −1.1 pp); confirmation 0.951 / 0.016 vs 0.958 / 0.024; cost 1.07×; λ ladder moves 0.6 / 2.2 pp (< δ) → **verdict: close at the saturation point** (coordinate, n=1 + confirmation) | C2 ✅ |
| 2026-11-16 | E | estimator atlas: bias/variance/compute per kind | 18 claim cells (6 arms × 3 seeds) + 22 ladder/confirmation cells | full MNIST test split (1 σ = 0.3 pp); chance 0.1; floor 0.25; probe 256; FD tol 0.99 | MNIST quick, feedforward 784-32-10, batch 32, 600 batches, 1 epoch, per-arm LR 1e-3/1e-2/1e-1, CPU | **controls pass** (FD 1.0000; exact 0.914 ± 0.006); PEPITA 0.972 ± 0.001 / 1.60×, 0.923 ± 0.003; FA 0.125 ± 0.079 / 0.002×, 0.821 ± 0.007; hybrid 0.185 ± 0.007 / 0.395×, 0.827 ± 0.007; FF 0.143 ± 0.109 / 1.211 ± 0.308, 0.816 ± 0.089; PC-ALM depth-2 regime mismatch/refusal (0.105 ± 0.013, one seed refused) → **verdict: atlas, not a winner**; CORRECTION 16 | E1 ✅ |
| 2026-11-16 | D | substrate ladder: ternary/memristive + `energy_min` at settle 5/10/20, per-arm LR | 24 cells (3 arms × 3 LR + 3 settle + 5 confirmation) + 1 control | full 10k test split (1σ = 0.3 pp); chance 0.1; floor 0.55; δ = 0.01; device B/weight | MNIST quick, 784-32-10, B=32, 600 batches, 1 epoch, β=0.5, CPU | **memristive 0.9097 vs digital 0.9097 at settle 20 on the confirmation seed, 2 vs 4 B/weight → promote D2**; ternary 0.861 vs 0.913, 2 bits/weight → refused; control 0.9234; CORRECTION 17 | D1 ✅ |
| 2026-11-16 | D | matched substrate comparison: memristive vs the digital rule at matched settle compute, backprop control, int8 QDQ control | 5 paired seeds × 4 arms + 4 extension-screen cells | paired 95% interval on the accuracy gap (1σ = 0.3 pp); floor 0.55; parity 1 pp; cost 1.2×; device B/weight | MNIST quick, 784-64-10, B=32, 600 batches, 1 epoch, β=0.5, settle 20/40, CPU | **refused at the walltime box**: gap −0.31 pp (CI [−0.41, −0.22]) at **2.09× walltime**; QDQ −0.01 pp (width harmless), forward-equivalents 1.00×, 2 vs 4 B/weight; control 0.9366 → the programming budget binds; D3 parked; CORRECTION 19 (QDQ cast ≠ quantisation) | D2 ⛔ |
| 2026-11-16 | F | composition screen: 50 legal multi-axis cells vs the best legal single-axis default, then the family ladder | 41 single-axis arms + 1 reference control + 50 screen + 3 ladder + 1 confirmation (96 cells) | accuracy on the full `digits` split; matched forward-equivalents (57); δ=1 pp; floor 0.55; control band 10 pp; param ceiling 50k | `digits` quick, 1797×64, 10 classes, B=32, 57 batches, 1 epoch, 1 seed, CPU, 50k params | **refused at this box**: reference 0.797 (`update`), screen best 0.669 (4 axes), `random_projections` ladder 0.092/0.783/refused at width 6 vs bar 0.807; confirmation 0.814 (3.1 pp seed spread > δ); control 0.867 (drift 6.9 pp, inside the 10 pp band); 50/50 measured | F1 ⛔ |
| — | P1 | published-parity (3 publishables + hybrid trunk rule) | — | published ±1 pp / σ | — | — | T5 |
| 2026-11-17 | A | T6a triage: the ratio is depth-declared and the claim's bars never meet | 18 cells (6 memory + 12 accuracy) | hybrid/ckpt ratio at L=8/16/32 × B=2048/4096; val_acc at L=16 (2 seeds, 2 batches); floor 0.375 | CIFAR-10 10k/10k, W=512, 200 steps where accuracy is read, RTX 3080 10 GiB (≤600 MB/cell) | **`invalid-box`**: ratio 1.22 / 0.75 / 0.53 and 0.48 at L=32; L=16/32 all arms 0.100 on both seeds → the refusal holds only at L=4→8, where the claim was never stated; re-registration at a pass-carrying box | T6a ⚠️ |
| 2026-11-16 | A | memory-frontier registration and its rung-2 screen (reduced L=4→8 box per the OOM guard) | 12 ladder + 4 screen + 3 calibration + 2 control cells | val_acc vs the learning floor (0.375); activation ratio vs 0.5×; δ=1 pp; c vs 4.1 (10%) | CIFAR-10 10k/10k, W=512, B=2048, L=4/8/16, 200 steps, seed 11/21/22, RTX 3080 10 GiB | **registered; screen refused the claim**: hybrid 0.167 / 103 MB vs ckpt 0.385 / 85 MB (1.22×), confirmation 0.154 vs 0.363; controls PASS (c=4.25, spread 0.0%; 0.385 vs 0.375); 30 priced cells; trigger T6c | T6a ✅ |
| 2026-11-17 | A | T6d update diagnostic at the pilot box: bias flag, gamma ladder, head-only, and the sibling whole-stack control | 12 measured cells (14 planned) (2 mechanism rows + 2 head-only/sibling ladders) | val_acc vs the ckpt's minus δ (floor 0.408 = 0.418 - 1 pp); the ladder's collapse to 1/classes; activation ratio vs 1.0 | CIFAR-10 10k/10k, L=8, W=1024, B=8192, 200 steps, LR 0.3, seed 21/22, RTX 3080 10 GiB (516-1037 MB) | **refused**: baseline 0.163/0.169; `train_biases` 0.167/0.175 (+0.5 pp); gamma 0.05/0.3/1.0 → 0.163/0.100/0.100; head-only 0.149; sibling (`local`, same rule whole stack) 0.400/0.405/0.384; hybrid activations 1.06× the ckpt's → **the split is the mechanism** (CORRECTION 24); T6e next | T6d ⛔ |
| 2026-11-17 | A | T6a re-registration at the pass-carrying box: the memory bar is met, the accuracy bar is not | 12 ladder + 4 screen + 3 calibration + 2 control cells | val_acc vs the ckpt's minus δ at the same box (floor 0.354); activation ratio vs 0.5×; c vs 4.1 (10%) | CIFAR-10 10k/10k, L=8→32, W=512, B=4096, stream-norm, 200 steps, seed 21/22, RTX 3080 10 GiB | **refused**: hybrid 0.184 / 210 MB vs ckpt 0.364 / 453 MB (**0.46×**, memory met), confirmation 0.201 vs 0.357; controls PASS (c=4.125; learning 0.409 vs 0.399); 30 priced cells; the hybrid's own update binds → T6d | T6a₂ ⛔ |
| — | A | memory frontier (2 budgets, dominance/hypervolume) | — | acc @ matched memory / iso-walltime; binding share; forward-eq; δ | — | claim run parked: T6d refused the update at the pilot box and the mechanism is the split; T6e (the split's position) is the defect fix, T6c's re-open is a side track | T6e |
| — | C | plasticity + retention (SI/cascade baselines) | — | final-task acc; BWT; avg_forgetting; buffer size; k×params | — | — | C1 |
| — | D | substrate-native training at matched accuracy | 5 paired seeds | state per step; accuracy; dtype constraints | D2 refused the path at its walltime box (2.09×); D3's drift rung is a trigger | — | D3 |
| — | F | composition vs the best single-axis default | 41 arms + 50 screen + 3 ladder + 1 confirmation (96 cells) | ≥δ at matched forward-equivalents; δ=1 pp | F1 refused (0.669 / 0.783 vs 0.797; bar 0.807; confirmation 0.814 > δ as seed spread) | F2's five seeds; no run | F2 |
**Progress is one of:** a new primitive that trains a task family; a defect
found and fixed by a failing test; a capability card (task, memory, steps, what
stops it); a published-parity reference (P1); a promoted claim; a **measured
coordinate at a declared box**; **a surprise that opens a new question
(§0.2)**. **Not progress:** more cells of the same box, more prose, a knob
swept to pass, a verdict that closes a mechanism.

**Portfolio position, 2026-11-17 (rewrite each session).**

| Rank | Track | Capability at stake | Next rung cost | Evidence today |
|---|---|---|---|---|
| 1 | **P0** estimator family | can the system train through forward-mode, sampling, and gradient-free paths? | 1 session (3 primitives) | none yet — the three credits do not exist (§19 row 1; E1's empty cells are the gap) |
| 2 | **P0b** routing | does a hard top-k train without a soft relaxation? | 2 sessions | `SurrogateCredit` absent; B1's STE gap is the defect probe, not a verdict |
| 3 | **P0c** depth fix | does the plain stack train at L≥16 with normalization and a decoupled LR? | 1 session | T6c/T6d are defect probes (T6d localized the split; the sibling rule reads 0.405) |
| 4 | **P0d** temporal | does a sequence axis exist and train? | 2–3 sessions | the axis does not exist; three credits are absent |
| 5 | **A/F/D** defect rows | the split, the composition, the programming budget | trigger-gated fixes | measurements stand, verdicts do not (CORRECTION 25) |

**Why the track words change.** E1's atlas is a **capability map**: its three
empty unbiased cells (score-function, forward-mode, zeroth order) are the first
three rows of §19. C2's closure is a **measured capability**: local learning
holds at batch 1, and the missing SI lift and cascade are §19 row 7 — the
long-stream protocol is the capability, not the verdict. B1's gap, D2's budget,
and F1's screen are **defect probes** with named fixes (§0.6); their numbers
stand, their verdict words do not.

**Capability ledger (append-only; a defect probe is not a deletion).**

| Ticket | What was measured | Defect / gap | Fix | Capability unlocked | Command |
|---|---|---|---|---|---|
| T6c | plain L=32 at 0.100; normalized 0.314 / 0.326 vs floor 0.375 | no depth normalization; a fixed `sqrt(W)` stream scale; one LR | LayerNorm + a per-depth LR box | deep training at L≥16 | `... memory_frontier --rung --depth 32 --width 512 --batch 2048 --steps 200` |
| T6a/T6a₂ | hybrid 0.184 / 0.201 at 0.46× memory | two step scales on one LR; the head split at the boundary | a decoupled trunk LR; the split's position | deep local learning at parity | `... memory_frontier --re-register` |
| T6d | no trunk knob reaches 0.408; sibling 0.405 | the split's position and the head/trunk LR coupling | a readout-only head; a decoupled trunk LR | the trunk rule at parity | `... hybrid_update --replay` |
| D2 | memristive −0.31 pp at 2.09× walltime | no programming-budget model; per-step conductance writes | a device-level or compiled quantisation of the pair | substrate-native training with a priced budget | `... matched_substrate --replay` |
| B1 | STE gap 0.819 → 0.660 over depth | `SurrogateCredit` absent; no load-balance term | the surrogate primitive + z-loss | hard top-k training at variable k | §19 row 4 |
| F1 | screen 0.669 / ladder 0.783 vs bar 0.807 | the composition is measured on an untrainable deep box; the axis space is narrow | the depth fix + the routing and temporal axes | a real multi-axis search | §19 rows 4–6 |
| C2 | EWC +0.005 < δ at λ=100 | SI lift and cascade absent; no ≥20-task stream | lift SI; a long-stream protocol | replay-free long-horizon CL | §19 row 7 |
| E1 | atlas: 6 arms × 3 seeds | three estimator cells empty | the estimator family | three new credits | §19 row 1 |
| ternary (D1) | 0.861 vs 0.913 at 2 bits/weight | the TWN threshold and a fixed α | a learnable α per layer or a delta-ternary scale | 16× less device state at parity | `... substrate_ladder --replay` |
| PC-ALM (E1) | depth-2 regime mismatch | the card's depth is 100 | run at its declared box | a deep objective-local credit | `... estimator_atlas --full --replay` |

New defect probes are appended here by the session that measures them, with the
box, the fix, and the capability it unlocks. The surprise budget may pick one
per session.

## 15. Rules and guardrails
- **A claim names its budget.** Memory, walltime, forward-equivalents, or params
  — never an unstated swap.
- **The baseline is the strongest one**, not the most convenient.
- **Every number carries its ruler, its command, and its σ.**
- **Every run carries a positive control.** A failed control invalidates the run,
  not the arm. Never skip it (SEC: the control is the cheapest falsifier).
- **A primitive row is the unit.** One new primitive per session: class,
  identity card, primitive row, registry entry, parity test, lock. A defect fix
  rides the session that owns the defect; a second primitive waits for the next
  session unless the first lands early.
- **A new kernel path is a new identity, never a silent replacement.** Old rows
  stay valid under their old identity card.
- **Lift, do not duplicate.** A mechanism that already lives inside another
  module (STE in `core/utils/surrogate.py`, REINFORCE in `training/rl.py:196`,
  Lion at `primitives/parameter_update/lion`) becomes a first-class primitive by
  wrapping it, never by a second implementation.
- **Tune to find the best point; never tune to win a comparison.** A knob
  inside a declared box is the method (the ladder). A knob chosen to make a
  comparison look good, or turned after seeing the rival's number, is a defect.
- **Rules are defaults.** Every rule here yields to a named reason and a working
  capability; write the reason where the number lives.
- **Exploration is parallel by default.** A claim run is serial and
  pre-registered; capability work is not.
- **A park needs a ladder.** A mechanism is parked only after §0.4's 4-cell
  rung 2, and only as a capability gap with the primitive that closes it; a
  one-cell low result is a defect probe or a coordinate, never a verdict.
- **Cheap screens before claims, not before exploration.** A claim follows a
  cheaper screen; a primitive needs no screen to start. The portfolio rank
  carries the last measured build cost.
- **Every track spends 10 % on the unexpected** (§0.2); a surprise is a result,
  not noise, and it enters §14 the session it appears.
- **Pre-register claims only**; exploration runs freely and stops cheaply. Reuse
  `configs/preregistrations/` (`r92_memory_budget_registered.json` is the shape).
- **Watchdog = 2× pilot price.** Kill or re-price; never extend.
- **If a ticket does not name a decision and a falsifier, it does not land.**
- **Rewrite §0/§14 in the same commit as the result.**
- **The plan's job is to shrink work.** The repo is ~3,000 files and 50 TODOs
  deep; a ticket that adds surface without removing a question is rejected.
---
## 16. Handoff contract
- TODO92 stays closed: gate, rulers, registrations, and ledger unchanged.
- **Start order is the capability program (§19 row 1), not a DAG.** The next
  session lands the estimator family (`ForwardTangentCredit`,
  `ScoreFunctionCredit`, `ZerothOrderCredit`). The prior measurements are
  defect probes, not gates: T6c/T6d localized the split, B1 the missing
  surrogate, D2 the unpriced programming budget, F1 the untrainable deep box.
  C1 promoted and C2 measured its saturation point; E1's atlas is the capability
  map; D1 promoted memristive. T5 runs in parallel as credibility work. No claim
  run is scheduled; a claim is optional until a mechanism reaches its floor.
- Every ticket lands with its measurement recorded where the mechanism lives, not
  only in the log.
- **Live from 2026-11-16:** C2 closed at the saturation point (λ=100): local
  0.952 / 0.015 vs control 0.963 / 0.020, gain +0.005 < δ=0.032, cost ratio
  1.07×; its re-open probes are a 5-seed retention protocol (rung 3), a
  matched-byte replay composition, or SI/cascade at the frozen LR. B1
  landed and **refused** (gap 0.819 → 0.660, −0.159 on the ladder seed and
  −0.037 on the confirmation seed, vs δ=0.05; reference FD 0.013; B2 not run;
  trigger in §14). E1 landed and closed as an atlas: controls pass (FD
  1.0000; exact 0.914 ± 0.006), the table is the artifact, and PC-ALM's
  depth-2 chance is a regime mismatch with a depth-100 trigger. D1 landed:
  **promoted memristive** (0.9097 vs 0.9097 at settle 20, 2 vs 4 B/weight) and
  refused ternary (0.861 vs 0.913) with a re-open trigger. **D2 landed and
  refused the path at its walltime box**: −0.31 pp (CI [−0.41, −0.22]) at
  2.09× walltime; the QDQ control is −0.01 pp, so the programming budget
  binds and D3 does not fire. T6b landed (a credit owns its free pass; the
  hybrid reads 0.37× the checkpointed arm's activation set at the claim point)
  and T6c refused its cheap pass at the box (0.314/0.326 vs floor 0.375; 1.45×
  bytes) with the LayerNorm re-open as its trigger. **F1 landed and refused
  composition at its box**: reference 0.797, screen 0.669, family ladder 0.783
  vs bar 0.807, confirmation 0.814 (3.1 pp > δ); F2's five seeds are the
  trigger. **T6a₂ landed and its rung-2 screen refused the claim** at the
  pass-carrying box (hybrid 0.184/210 MB vs ckpt 0.364/453 MB, 0.46× — memory
  met, accuracy 17 pp below). **T6d then landed and refused its update
  diagnostic** (no trunk knob reaches the floor; the sibling shows the same
  trunk rule as a whole stack reading 0.405, so the split is the mechanism),
  so the defect fix is **T6e (the split's position)**, not a claim run; the
  session order is the estimator family (§19 row 1).
- If a steering rule fires, rewrite §0 and §14 in the same commit that records the
  result.
---
## 17. Review answers (resolved)
| Q | Answer |
|---|---|
| 1. Order | **Capability order, rewritten every session (§14)**, not a DAG. v26 start: **the estimator family** (`ForwardTangentCredit`, `ScoreFunctionCredit`, `ZerothOrderCredit`, §19 row 1), then routing (`SurrogateCredit` + hard top-k), then the depth fix (normalization + a decoupled trunk LR), then the temporal axis, then the streaming lifts. Every earlier "refusal" is a defect probe (CORRECTION 25): T6c/T6d localized the split, B1 the missing surrogate, D2 the unpriced programming budget, F1 the untrainable deep box. Memory is an instrument: T6a₂'s 0.46× bar and T6d's 1.06× at L=8 are measurements, not the queue. No claim run is scheduled; the primitives are the work. |
| 2. Task | CIFAR-10, **fixed 10k-image train subset + full test** (`CostClass.EXPENSIVE`; data cached at `data/cifar-10-batches-py`). Depth/width/batch are hyperparameters and run settings, not registry axes. Synthetic depth task only for instrument acceptance. Normalization fixed across arms: LayerNorm or none — BatchNorm is non-local and breaks batch-1 streaming. W1/W2 are relative claims; the absolute vision bar does not apply. |
| 3. Checkpointing | **Landed (T4b).** `core/gradient_checkpointing.py` + `FeedforwardGeometry.set_gradient_checkpointing`, √L segments split at Linear starts, `use_reentrant=False`, `preserve_rng_state=True`, geometry forward only; grads bit-exact under dropout and the arm fits L=64 at W=1024/B=8192. |
| 4. P1 scope | Three publishables first, then any credit the new primitives add. The complexity-audit column is part of every row; reproduce the published protocol and record σ. |
| 5. D1/D2 timing | **Landed 2026-11-16** (D1: 24 cells, 617 s; D2: 24 cells, 915 s, CPU): D1 promoted memristive and refused ternary; D2 refused the path at the walltime box (−0.31 pp at 2.09× walltime; the programming budget binds). D3 is a trigger; no continuous surrogate is needed for a parity coordinate. |
| 6. Triggers | Event triggers, no fixed dates. D3 stays parked: D2 held parity but missed the 1.2× walltime. A device-level/compiled quantisation of the pair is its re-open. Ternary re-opens on a wider width or a learnable α per layer. |
| 7. Headline | **Frontier, not depth:** "accuracy per GB at iso-walltime", ε-dominance with a pre-registered δ (or baseline accuracy at ≤0.5× **activation bytes**), with a stacked memory decomposition. "2× depth" is reported only with the accuracy floor. |
---
## 18. Code-change appendix (what each ticket touches)
**T1 — complexity truth.**
- `acceleration/kernel_backend.py:143` — `memory_complexity` gains a
  `complexity_verified: bool` (or `None`) so an unmeasured claim is distinguishable.
- Every `get_memory_stats()` returning `activations_mb: 0.0` — return `None`
  until measured, or compute from captured tensors. Files: `backprop_kernels.py`
  (:181), `ff_kernels.py` (:240, :576), `pc_kernels.py` (:294), `tp_kernels.py`
  (:505), `fa_kernels.py` (:328), `mep_kernels.py` (:308), `dfa_kernels.py`
  (:299), `hebbian_kernels.py` (:237), `contrastive_kernels.py` (:235),
  `snn_kernels.py` (:351), `tile_kernels.py` (:478, :1028),
  `eqprop_kernel_backend.py` (:342, :350).
- `acceleration/export.py:191` — identity card carries `complexity_verified`,
  backend path, dtype, optimizer, GPU model, torch version, forward-equivalents.
**T2 — stub fixes.**
- `acceleration/contrastive_kernels.py:498–510` `PEPITAContrastiveKernel.nudged_phase`
  — replace `pass` with error modulation via `_feedback_matrix` (the faithful
  `ff_kernels.PEPITAKernelBackend` is the reference); until fixed, mark the kernel
  `available=False` with `unavailable_reason`.
- `:747` `SNNContrastiveKernel._simulate` — same, or mark unavailable.
- `:410` `FFContrastiveKernel` — verify label-change semantics; `nudged` returning
  free otherwise yields a zero update.
**T3 — lockstep recompute (✅ landed 2026-11-16).**
- `acceleration/ff_kernels.py` — a two-pass path: pass 1 computes the error and
  discards intermediates; pass 2 recomputes standard and perturbed activations
  layer-by-layer in lockstep and updates W_ℓ immediately. Exact because each
  W_ℓ is used once per pass before its update.
- **What the code does.** `lockstep_contrasts` is one generator for both
  families — FF contrasts its positive and negative chains, PEPITA its standard
  and error-modulated ones, and both reduce to
  `postᵀpre/B` on each chain (`contrast_delta`, the Triton twin's tested
  equation). `apply_contrast` writes the layer before the next one is produced.
  `train_step` and `kernel_train_step` both run it under `no_grad`; the
  activation lists are gone from the step paths.
- **Where the lock came from.** The plan said "lock against the `algorithms/`
  path". That path's rule is **not** this rule: `PepitaCredit` takes the exact
  autograd gradient of the modulated loss, the kernel rung is the closed-form
  per-layer contrast (`estimator_kind` differs by design, §2). Numeric parity
  there would have been a tolerance chosen to pass. The lock is therefore
  **lockstep ≡ store-all of the same equations**, per layer, at `atol=0`, with
  the store-all rung retained as production reference code and the expected
  delta recomputed from the definition inside the test. The `algorithms/` parity
  question belongs to T5/P1 and is unchanged.
- **Three live defects it killed.** (1) `FFKernelBackend.train_step` called
  `self.backward_contrastive(...)`, which does not exist — every FF system-path
  step raised `AttributeError`. (2) `PEPITAKernelBackend.train_step` called
  `self.backward(std_acts, err_acts)` against a signature that required a third
  `error` argument — same outcome. (3) The bespoke PEPITA step multiplied the
  standard pre-activation into both chains while the Triton twin (its tested
  specification) uses each chain's own — the step and its own kernel disagreed.
  Also removed: `feedback_matrix_scale` was applied a second time to the update
  (it already scales the modulation) and the now-dead `compute_goodness`.
**T4a — decomposition and guard (hours, not sessions).**
- `core/system_trainer/_resources.py:62` `EpochResource` — add
  `params_mb`, `optimizer_mb`, `activations_mb`, `auxiliary_mb`, `cpu_rss_mb`;
  `EpochResources.stop` already reads CUDA peak, so subtract the known terms and
  record the remainder as auxiliary (never assert 0.0).
- `experiment/kernel/_trainer_utils.py:194-207` — emit the decomposition and
  `activation_share` beside `memory_usage`.
- new lock/test `tests/property/test_memory_binding.py` — calibration within 10%
  of `c·L·B·W·4` with **c measured on the declared geometry** (Linear+ReLU c≈1;
  LayerNorm c≈2), the gate computed on **plain `backprop`**, and a deliberately
  non-binding cell rejected.
- CPU RSS: `psutil` is already a declared dependency (`pyproject.toml:100`);
  read `Process().memory_info().rss`. No new dependency.
**T4b — activation checkpointing (✅ landed).**
- `core/gradient_checkpointing.py` — `segments_for_depth` (√L over Linears),
  `GradientCheckpointing.to_identity()` (`grad_checkpointing_segments`,
  `compiled=False`), and `enable_gradient_checkpointing(system, segments=None)`,
  which refuses a geometry with no measured path instead of silently running
  plain. `FeedforwardGeometry.set_gradient_checkpointing` splits the stack at
  **Linear starts** (a mid-block split would resume with the wrong residual skip
  tensor) and wraps each chunk with `checkpoint(..., use_reentrant=False,
  preserve_rng_state=True)`. The wrapped unit is the geometry forward, never
  `system.train_step` (which contains the update). Under checkpointing,
  `forward_with_intermediates` returns segment boundaries, so the retained set
  is O(√L·B·W), not O(L·B·W). `torch.compile` is not on this path; the identity
  card records `compiled=False`, and a compiled ckpt cell would need both
  variants measured and named.
**T4c — reuse the existing ladder runner.**
- `validation/backprop_parity.py:729` `run_parity` — add `batch_size`, and add
  `pepita`/`local_goodness` to `_COMPUTE_MATCHED_PORTFOLIO`; the depth loop,
  per-depth baseline, seeds, bootstrap CI, peak memory and FLOPs already exist.
**T3b — hybrid (declare the step semantics; no hand-waving). ✅ Landed
2026-11-16.**
- `HybridCredit` in `ontology/credit/_hybrid.py`, wrapped by
  `primitives/credit_assignment/hybrid/`; owns `trunk_credit` (`PepitaTrunk`
  contrast) + `head_credit` (`GradientCredit`) + `split_layer`; dispatches by
  layer index. One registry row in `_CREDIT_PRIMS`, one `estimator_kind="hybrid"`,
  a feedforward-geometry refusal (constraint row + `SystemConfig` validator), and
  a bottom-level `GradientCredit.gradient_of` shared with the head.
- **Semantics, fixed before the code:**
  1. **standard pass**: trunk forward under `torch.no_grad()`; at the boundary
     `h = h.detach().requires_grad_(True)`; head forward records the graph →
     logits → CE;
  2. head backward on the standard pass → boundary error
     `δ = ∂L/∂h_trunk_out` (the head's input gradient);
  3. **trunk error-modulated pass** under `torch.no_grad()` with `e_out = δ`,
     propagated by the trunk's feedback matrices; this is the PEPITA trunk's
     second pass;
  4. compute trunk and head gradients from the **same pre-update weights**; apply
     trunk then head. No second head forward, no head update before the boundary
     error is formed.
  The `no_grad` trunk and the `detach` boundary are what make the memory claim
  true; without them the trunk graph is retained and the hybrid is just backprop.
- **Reference fixture (correctness, not speed):** a *store-all* hybrid — two-pass
  PEPITA trunk + backprop head, no lockstep — is the reference. Lock the lockstep
  trunk against it (`max|ΔW| < tol` per layer), exactly as T3 does. "Composes" is
  not acceptance; parity is.
- **Acceptance:** hybrid loss decreases, trunk gets non-zero updates, head gets
  true gradients, parity with the store-all reference on a seeded synthetic task,
  and the measured trunk activation set is **flat in depth**. Budget the upper
  2 sessions; on watchdog, fall back to pure-local and record the composition
  refusal.
- the head's autograd graph is the only stored activation set; the trunk's
  working set is O(B·W) per layer. Record both in the decomposition, or the
  hybrid's advantage is unmeasured.
- no `System` schema change: `credit` stays a single protocol object.
- **What the code actually did.** `FeedforwardGeometry.step_layer` is the
  one-layer advance that threads the last Linear's *input* across the following
  activation (the residual skip reads it); `_apply_layers` now loops over it, so
  the lockstep and the store-all reference cannot disagree about a skip.
  `split_layer` is a stack index and must land on a Linear (a split between a
  Linear and its activation would lose the skip input); `-1` puts the head on
  the last two Linears. The trunk's first pass and second pass both run under
  `torch.no_grad()`; the head graph is the only retained set. The measured peak
  above the weight-gradient set is flat at **81.0 MB** (L=4→32, W=512, B=4096)
  against the store-all control's **122→1018 MB**; the per-layer trunk delta is
  bit-exact (max|Δ| = 0.0) and the head's gradient equals plain backprop's at
  the same boundary. `tests/property/test_hybrid_parity.py` (8 tests, 16 s,
  2 s CUDA) is the lock; the composed path's 40-step loss decreases and every
  weight moves. A measured defect was found and fixed by the depth lock: the
  second pass originally ran outside `no_grad`, so each stored contrast's
  `grad_fn` pinned the whole activation chain and the "flat" peak grew
  101→577 MB — the lock's first measurement caught it.
**T6a — the registration (✅ landed 2026-11-16).**
- `configs/preregistrations/t93_memory_frontier_registered.json` —
  `MemoryFrontierRegistration` (in `validation/memory_frontier.py`) keeps the
  claim, the meta-threshold (`metric`, `threshold=δ`, `min_seeds=5`, `alpha`),
  the reduced box (L=4→8, W=512, B=2048, 200 steps, fp32, SGD+momentum), the
  measured L=8 LR ladder (12 rows, best per arm frozen), the claim seeds
  (101–105, disjoint from pilot 11–13 and ladder 21–23), the data-order seed
  (7), both controls, the 30 priced claim cells, the binding appendix, and the
  stop rule. `ThresholdRegistration.from_dict` ignores extra keys, so a
  claim-table test reads the raw JSON; the loader does not enforce the binding
  gate. The registration's claim is W1's **≤0.5× activation-bytes** form, so no
  hypervolume reference point is registered.
- register the **LR viability ladder** (3 points per arm at L=8, best frozen,
  **seeds disjoint from the claim**), the fixed epochs/`batches_per_epoch`, the
  claim seed list and data-order seed, the **minimal ladder** (§4: ~30 cells, not
  the grid), and the **hypervolume reference point** `(floor−5 pp, max_peak×1.1)`
  with δ — or the ≤0.5× **activation** rule.
- register **both positive controls**: instrument (calibration cell reads
  `c·L·B·W·4` within tol) and learning (plain backprop at L=8 reaches the pilot
  floor). A failed control invalidates the run.
- the ε-dominance claim is computed from the registered budgets after the run;
  the budgets, δ, and the reference point are fixed before it, so this is not
  post-hoc.
**D1 — substrate ladder (✅ landed 2026-11-16).**
- `validation/substrate_ladder.py` — the runner, the `SubstrateCell` row, the
  `SubstrateReport` table, `device_state` (width arithmetic), `_run_ladders`
  (per-arm LR then settle ladder), `_arm_parity`/`_verdict` (two-seed 1 pp gate,
  then state saving), `read_cells`/`replay_substrate_ladder` (kill-safe replay),
  and `write_report` (`substrate.json` + `substrate.md`).
- the substrate models are the ontology ones, not the adapters:
  `ontology.TernarySubstrate` (TWN + STE, 2 bits/weight) and
  `MemristiveSubstrate` (differential int8 pair, 16 bits/weight); the digital
  control is `DigitalSubstrate(SubstrateConfig.digital())`.
- **D2 — matched substrate comparison (✅ landed 2026-11-16).**
  `validation/matched_substrate.py` reuses the D1 runner
  (`_cell_or_measure`, `_resume_cells`, `read_cells`), adds the paired gate
  (`_pair`, `_gate`, `replay_matched_comparison`) and the int8 QDQ control;
  `_build_system`/`_box` in the D1 runner take `hidden_dims`, so the 2× box
  needs no second runner. The memory arm and the digital rule run at **matched
  settle compute**; the walltime, forward-equivalents, and device state are
  rulers beside the accuracy. 5 paired seeds; no new
  primitive. **CORRECTION 19:** `QuantizedSubstrate` claimed int8 precision
  but its forward cast operands to int8 and never quantised; it now uses the
  float forward with asymmetric per-tensor int8 QDQ and a straight-through
  gradient, and `DEVICE_BITS` gains `qdq = 8` bits/weight.
**T8 — lift, do not rewrite.**
- `core/continual/losses.py:84` `SynapticIntelligence` already implements the
  mechanism; lift it to `ontology/update/` as a U row and reuse
  `create_si_arm` (`core/continual/arms.py:238`). `create_replay_arm` and
  `create_ewc_arm` already exist for P4's baselines.
**T6 — frontier figure.**
- reuse `experiment/analysis/pareto_analysis.py:compute_pareto_frontier`
  (objectives `["accuracy", "peak_bytes"]`, `maximize=[True, False]`).
- the cell loop is `validation/memory_frontier.py` (`run_pilot` writes
  `results.json` + `appendix.md`); the Pareto aggregation reads its `arms` rows,
  so no second ladder exists. T6b has landed and T6a₂ priced the pass-carrying
  box; the hybrid's update (T6d) has landed and refused, so the figure's points
  are the pilot box's until T6e prices the split's position.
**T1 (cont.) — estimator coordinate.**
- `experiment/schema/axis.py:116` — add
  `estimator_kind: Literal["exact","surrogate","gradient_approx","objective_local","local_supervised","score_function","forward_mode","zeroth_order","temporal_local","hybrid"]`
  and `bias_reference: Literal["none","exact_tractable","smoothed_objective"]`
  beside `target_kind`.
- `experiment/schema/seed_registries.py:186` `_CREDIT_PRIMS` — each row declares
  its kind; add the declaration lock. The lock applies to **CREDIT rows only**
  (`AxisSpec` is shared across all six axes; other axes default `unspecified`).
  Initial mapping: `gradient=exact`; `random_projections`, `target_inversion`,
  `thermodynamic_contrast`, `pc_alm` = **`gradient_approx`**;
  `pepita`, `local_goodness`, `local_contrastive`, `homeostatic` =
  **`objective_local`**; `temporal_trace` = `temporal_local`.
  `bias_reference="none"` for `objective_local`/`local_supervised`/
  `temporal_local`; `"exact_tractable"` for the gradient-estimator rows. Confirm
  per implementation before locking; do not label a local objective as a biased
  gradient.
**T7 — estimator credits (E1's atlas is the capability map: the three are §19 row 1).**
- new `primitives/credit_assignment/surrogate/` — lift the STE/Gumbel machinery
  already in `core/utils/surrogate.py` and `benchmarks/joint/z3_fixed_weights.py`;
  do not reimplement.
- new `primitives/credit_assignment/forward_tangent/` — `torch.func.jvp`,
  random and antithetic tangents; declare `forward_mode`.
- new `primitives/credit_assignment/score_function/` — lift REINFORCE from
  `training/rl.py:196`; add a moving-average or value baseline; declare
  `score_function`.
- new `primitives/credit_assignment/zeroth_order/` — SPSA (2 evals), antithetic
  ES, blockwise perturbations; declare `zeroth_order`.
- `experiment/kernel/search_space.py:288` — compatibility predicates:
  `score_function` requires stochastic selection in geometry; `forward_mode`
  requires jvp-capable ops; `temporal_local` requires recurrent dynamics.
**T8 — streaming baselines (C1 promoted; the lift is §19 row 7).**
- `SynapticIntelligence` already exists at `core/continual/losses.py:84` and
  `create_si_arm` at `core/continual/arms.py:238`; **lift** it into
  `ontology/update/` as a U row. Do not write a second implementation.
- new `primitives/plasticity/cascade/` — Benna–Fusi k hidden states; price
  `k×params` in the memory ruler before the first cell.
- `primitives/parameter_update/lion/` already exists — reuse it; do not add a
  sign-momentum primitive.
**T9 — temporal (the sequence axis is §19 row 6).**
- new `primitives/credit_assignment/eligibility_prop/`,
  `.../unbiased_rtrl/`; the exact RTRL reference is a fixture under
  `tests/`, never a registered arm.
**Deferred T0.**
- `experiment/schema/axis.py:116` — `regime: frozenset[Regime]` beside
  `target_kind`, only when §12's search trigger fires; until then the manual tag
  lives on the cell record.
---
### Landed 2026-11-16 (T3 — what the code actually did)
- **One stream, two families.** `lockstep_contrasts(layers, chain_a, chain_b,
  activation, final_activation=...)` yields `LayerContrast(layer, post_a,
  post_b, weight, bias)`; both rules reduce to `postᵀpre/B` on each chain, so
  Forward-Forward and PEPITA share the kernel instead of owning two copies.
  `apply_contrast(contrast, lr)` writes `W_l` before layer `l+1` is produced.
- **The step paths are the rung; the reference is production code.** `train_step`
  and `kernel_train_step` run the stream under `no_grad`;
  `forward_positive`/`forward_negative`/`forward_standard`/
  `forward_error_modulated`/`backward`/`update_weights` are retained as the
  store-all rung the lock compares against — a live reference, not a test copy.
- **Every step superscript is now measured.** `complexity_verified=True` on both
  backends with the ladder in `docs/BENCHMARKS.md` §2.2; `activations_mb` stays
  `None` per instance because a kernel does not self-measure.
- **`feedback_matrix_scale` is applied once, to the modulation.** It had also
  been multiplying the update in the store-all `backward`, so a non-unit scale
  scaled the rule twice.

### Landed 2026-11-16 (T3b — what the code actually did)
- **One layer advance, two readers.** `FeedforwardGeometry.step_layer` advances
  one layer and returns the threaded `h_in` (the last Linear's input, which the
  following activation's residual skip reads); `_apply_layers` now loops over it.
  A hybrid that advanced the stack itself would add the wrong skip tensor on a
  residual geometry — the parity lock covers the residual fixture.
- **The boundary is a stack index, not a width.** `split_layer` indexes
  `geometry._layers` and must land on a Linear; the head's first layer reads the
  detached boundary, so a split between a Linear and its activation would lose
  the skip input. `-1` selects the last two Linears (the readout and the last
  hidden layer), clamped so the trunk keeps at least one Linear.
- **The head delegates, it does not reimplement.** `GradientCredit.gradient_of`
  is the single exact-autograd choke point (fail-loud on a missing gradient);
  `GradientCredit.compute_pseudo_gradient` and `HybridCredit`'s head both call
  it, so the head's gradient is backprop by construction.
- **The first measured defect was the lock itself.** The second pass initially
  ran outside `no_grad`; each stored contrast's `grad_fn` pinned the trunk's
  activation chain, and the "flat" peak grew 101→577 MB with depth. The depth
  lock caught it on its first run; with `no_grad` the peak is flat at 81.0 MB
  above the weight-gradient set (the O(L·W²) parameter-sized tensor set every
  pseudo-gradient credit returns), and the store-all control is 122→1018 MB.
- **Composition and refusal are both declared.** One `_CREDIT_PRIMS` row, one
  `estimator_kind="hybrid"` card, a `system.py` validator plus a constraint row
  refusing non-feedforward geometry; `tests/property/test_hybrid_parity.py`
  (8 tests, 16 s, 2 s CUDA) is the lock.

### Landed 2026-11-16 (T6 — what the code actually did)
- **One point, four arms, one builder.** `validation/memory_frontier.py` owns the
  operating point as `PilotPoint` (depth/width/batch/steps), the arithmetic
  (`activation_mb = c·L·B·W·4`, `peak_mb = activations + 2·params`,
  `affordable` against 80 % of the card), and `build_arm`, which composes all
  four arms from one geometry/init/update so only the credit and the
  checkpointing differ. `claim_ladder` prices the registered cells and marks the
  two that cannot run: L=64 is unaffordable (8.2 GiB activations) and B=16k
  cannot fill the fixed 10k-image subset.
- **The controls are the deliverable.** The instrument control re-measures `c`
  at the pilot width and batch from two depth deltas (8→16→32): **c = 4.125,
  spread 0.0 %**, so the appendix's 4.1 is not a W=256 artifact. The learning
  control freezes the floor at `ckpt(L=8) − 1 pp` and requires plain backprop to
  reach it: both measure **0.419** (checkpointing parity at real scale), floor
  0.409 → PASS. The LR ladder `(0.1, 0.3, 1.0)` at L=8 picks 0.3 for every arm;
  a fourth point at 1.0 was measured and rejected (0.170/0.188), so the best
  point is interior, not an edge.
- **The pilot's job is to find what a claim would have hidden.** Two blockers,
  both measured: **T6b** — the hybrid's composed activation set is 3249 MB
  against the checkpointed arm's 1637 MB although its credit-level trunk is flat
  at 81 MB, because `core/pipeline.py` materialises `forward_pass` before the
  credit runs (and does so with autograd enabled for a credit that declares
  `requires_autograd=False`); **T6c** — at L=32 every arm sits at val_acc 0.100
  with the backprop loss pinned at 2.2132 from step 200 to 1000, so the plain
  Linear+ReLU stack at the claim depth is not trainable and §4's LayerNorm
  fallback must be taken before any depth rung is registered.
- **The registration was committed, and the screen refused the claim.** T6a
  wrote the registration at the reduced L=4→8 box (W=512/B=2048/200 steps) per
  the OOM guard: the instrument control measures c=4.25 from L=8/16/32 standard
  deltas (spread 0.0%, within 10 % of the declared 4.1), and the learning
  control reads backprop 0.385 vs floor 0.375 (PASS). The rung-2 screen then
  measured the hybrid at 0.167 and 103 MB against the checkpointed arm's 0.385
  and 85 MB (1.22×), with the confirmation seed at 0.154 vs 0.363, so the
  claim is refused at this box and no claim run is scheduled. **T6a₂ then
  re-registered at the pass-carrying L=8→32/B=4096 box and refused again: the
  memory bar is met (0.184/210 MB vs 0.364/453 MB, 0.46×) and the baseline
  trains (0.364 vs floor 0.354), so the refusal is the hybrid's own update.**
  The trigger was **T6d** (`train_biases`, `feedback_scale`, a head-only
  control at the pilot box) — landed 2026-11-17 and refused; the split is the
  mechanism (CORRECTION 24); T6c's LayerNorm re-open is a side track.
- **Locks.** `tests/property/test_memory_frontier.py` (8 tests, 21 s CUDA) holds
  the coefficient, the gate, the checkpointed arm's 0.39× activation set, and
  the arm wiring; the hybrid's composed-path property is a **strict xfail**
  (843 MB vs 437 MB at the smaller lock point) so T6b cannot be forgotten.

### Landed 2026-11-15 (T1/T4a/T4c/T4b — what the code actually did)
- **Estimator coordinate lives on the identity card, not on `axis.py` alone.**
  `AlgorithmIdentityCard` gained `estimator_kind`/`bias_reference`; each of the
  10 credit classes declares them, `spec.estimator_coordinate()` reads the card,
  and `_seed_axis_primitives` stamps `AxisSpec` (which gained the two fields,
  defaulting `unspecified` for the other five axes). One declaration, three
  readers — the same shape as `error_blind_credit`.
- **Complexity truth is a protocol-level declaration.** `KernelBackend` gained
  `complexity_verified`, `available`, `unavailable_reason`; `get_memory_stats()`
  returns `dict[str, float | None]` and `activations_mb` is `None` at all 14
  former zero sites; `KernelRegistry.get` refuses an unavailable backend;
  `export._build_manifest` carries `complexity_verified`, `available`,
  `unavailable_reason`, `backend_path`, `gpu_model`, `torch_version`.
- **The PEPITA contrastive nudge is a real second pass.** `free_phase` caches the
  logits; `nudged_phase` backprojects `one_hot(target) − logits` through the
  fixed feedback matrix and replays the stack. FF and SNN contrastive are
  `available=False` with reversal triggers (no label channel; the nudge branch
  ignores its target).
- **T4a is a decomposition, not a counter.** `EpochResources._decomposition`
  reads geometry params, the update rule's `state_tensors()` (a new non-cloning
  accessor on `StateSnapshotMixin`/`AdamStateMixin`/`LionStateMixin`/
  `BaseParameterUpdate`) and the CUDA peak; `activations = peak − params −
  optimizer − auxiliary`, `None` when the optimizer cannot be enumerated.
  `auxiliary_mb` stays `None` until a mechanism declares state outside both.
- **T4c's real defect:** `backprop_baseline` referenced a `batch_size` it never
  received, so `run_parity` raised `NameError` before training a cell. Fixed and
  locked; `batch_size` is now a campaign parameter (the binding gate is `B·W·L`).
- **T4b is a recovered-arm instrument, not a flag.** Segments count Linears
  (127 modules at L=64, so √L=8 is only correct because the count is depth);
  chunks start at Linears so a residual block never splits; non-reentrant
  checkpoint with `preserve_rng_state=True` gives bit-exact gradients under
  dropout, and the negative control re-runs the fixture with the flag off to
  prove the lock can fail. Measured at W=1024, B=8192: forward peak 480 MB at
  L=64 (plain 2080 MB) and epoch peak 3894 MB against the 6554 MB 8 GB-card
  budget (§4.1). The epoch peak keeps a param-sized gradient floor (~2.1 GB at
  L=64) that checkpointing cannot remove — that is the activation term's bend,
  not the whole peak's.

### Landed 2026-11-16 (E1 — what the code actually did)
- `validation/estimator_atlas.py` — the E1 runner. `EstimatorCell` carries the
  arm, its declared `(estimator_kind, bias_reference)`, the selected LR, the
  one-step angle/magnitude, val/train accuracy, steps, forward-equivalents and
  walltime; `EstimatorReport` carries the claim cells, the viability ladder,
  the FD control and the verdict. `read_cells`/`replay_estimator_atlas` replay
  from the kill-safe log without training; `_resume_cells` reuses a measured
  cell, keyed by `(arm, seed, lr, stage)`, so a kill costs only the cell in
  flight.
- **The reference is the exact arm, not a second model.**
  `_reference_delta` builds `BackpropCredit` at the same `(seed, lr)` and reads
  its one-step displacement; `_reference_control` validates autograd against
  `finite_diff_gradient` on a small net (cos 1.0000). `_build_arm` reads the
  coordinate from the credit's identity card, so no second taxonomy table
  exists.
- **The fair chance is a per-arm LR ladder.** `LR_LADDER = (1e-3, 1e-2, 1e-1)`
  at `LADDER_SEED = 59`, a confirmation at the best point (`CONFIRM_SEED = 60`),
  and claim seeds `61/62/63`; the best point is chosen by held-out accuracy,
  so the ladder's tuning is not a claim. `_train` reseeds before each build so
  every LR sees the same initialization and data order; `_CappedLoader` caps
  the 600-batch epoch so compute stays matched.
- **The box.** MNIST quick mode, feedforward 784-32-10 Linear+ReLU, batch 32,
  600 batches, one epoch, `EuclideanUpdate(step_size=lr, grad_clip=1e9)`;
  `EnergyMinimization(max_steps=3, beta=0.5)` for every arm except PC-ALM,
  which uses `PCALMDynamics(max_steps=3, step_size=0.02)` as its declared
  dynamics. The held-out ruler is the full test split (10k, 1σ = 0.3 pp).
- **The measured table (3 seeds; mean ± σ).** Exact **0.914 ± 0.006**, angle
  1.000, scale 1.000. PEPITA **0.923 ± 0.003**, angle **0.972 ± 0.001**, scale
  **1.604 ± 0.110**. FA **0.821 ± 0.007**, angle **0.125 ± 0.079**, scale
  **0.002**. Hybrid **0.827 ± 0.007**, angle **0.185 ± 0.007**, scale
  **0.395 ± 0.020**. Forward-Forward **0.816 ± 0.089**, angle **0.143 ± 0.109**,
  scale **1.211 ± 0.308**. PC-ALM **0.105 ± 0.013** on two seeds (seed 61
  refused), angle 0.071 ± 0.029, scale 0.040 ± 0.006.
- **One refusal row, one honest gap.** PC-ALM at depth 2 diverges in the settle
  at LR 1e-2/1e-1 (NaN at step 1/2) and is chance at 1e-3; its card validates
  depth 100, so the row is a `regime-mismatch`/refusal with a depth-100 trigger,
  not an algorithm verdict. Its forward-equivalents are `None` because the FLOP
  counter fell back to parameter counting (1.0) — the structural 2×`max_steps`
  value is not fabricated into a matched budget.
- **One apparatus defect fixed (CORRECTION 16).** A shared LR is not a fair
  box: at 1e-3 FA collapses (0.093) and at 1e-1 the hybrid diverges (0.097).
  The per-arm ladder is the corrected apparatus; the single-LR cells are the
  defect probe, not a table.
- **Locks.** `tests/unit/validation/test_estimator_atlas.py` (12 tests) pins the
  six declared coordinates, the lite/full subset, the seed variance (`None` at
  n=1, sample σ at n=3), the control/defect/refusal verdicts, the PC-ALM
  regime note, and the replay/dedup rules. The table is in
  `results/t93_e1/estimator.md` and `docs/BENCHMARKS.md` §2.8.

### Landed 2026-11-16 (D1 — what the code actually did)
- `validation/substrate_ladder.py` — the D1 runner. `SubstrateCell` carries the
  arm, stage, seed, LR, settle length, device, val/train accuracy, device state
  (bytes and bytes/weight), train state, steps, walltime and
  forward-equivalents; `SubstrateReport` carries the box, cell log, control and
  verdict. `read_cells`/`replay_substrate_ladder` recompute the gate from the
  kill-safe log without training; `_resume_cells` reuses a measured cell keyed by
  `(arm, stage, seed, lr, max_steps)` and the in-memory `done` map dedupes
  within a launch, so a kill costs only the cell in flight.
- **One rule, three substrates, one learning control.** The three substrate arms
  share `ThermodynamicContrast(beta=0.5)` + `EnergyMinimization(max_steps,
  beta=0.5, compiled=False)` + `EuclideanUpdate(step_size=lr, grad_clip=1e9)`;
  the digital control is `DigitalSubstrate`, and the learning control is
  `InstantaneousDynamics` + `BackpropCredit` on the same architecture. No second
  rule was written: parity is measured against the same rule on a digital
  substrate, which isolates the substrate from the rule's own weakness.
- **The state ruler is arithmetic, not a measurement.** `device_state` prices the
  device width (32 bits/weight digital, 2 bits/weight ternary + one fp32 scale
  per layer, 16 bits/weight for a differential int8 pair). `train_state_bytes`
  is the fp32 latent set + optimizer buffer from `EpochResource` (0.2 MB, equal
  for every arm) and is declared, never claimed: an in-situ device would hold
  the weights, not a second fp32 copy. A test pins the widths and their
  ordering, so a fabricated zero cannot pass.
- **The fair chance is a per-arm LR ladder (CORRECTION 17).** A shared LR is
  not a fair box: at 1e-2 ternary reads 0.381 while digital and memristive read
  0.909/0.905, and ternary's best point is 3e-3. The ladder therefore sweeps
  `LR_LADDER = (1e-3, 3e-3, 1e-2)` at seed 59 and settle 10, freezes each
  arm's best LR, and then sweeps `MAX_STEPS_LADDER = (5, 10, 20)` at that LR;
  the confirmation seed is 60. A moving-scale probe rejected a frozen-α "fix"
  (the cell moves ≤2 pp where it is alive), so CORRECTION 17 is an apparatus
  fix, not a substrate verdict.
- **The measured table (24 cells, 617 s, CPU).** Learning control **0.9234**;
  digital rule 0.913/0.914/0.916 at settle 5/10/20 (LR 1e-2); memristive
  0.893/0.911/**0.915**; ternary 0.821/0.835/0.796 (LR 3e-3). Confirmation
  at settle 20: memristive **0.9097** vs digital **0.9097** (0.05 pp) at 2 vs
  4 B/weight → **promote D2**. Confirmation at settle 10: ternary **0.861** vs
  digital **0.913** (5.2 pp) at 2 bits/weight (16× less state) → **refuse at
  this box** with a wider-width/learnable-α trigger.
- **Locks.** `tests/unit/validation/test_substrate_ladder.py` (9 tests) pins the
  device-width arithmetic and ordering, the two-seed parity margin (the registered
  1 pp), the confirmation failure, the no-state-saving case, the
  invalid-learning-control case, the park-with-trigger case, and the
  cell-log round trip + replay. The table is in `results/t93_d1/substrate.md`
  and `results/t93_d1/substrate.json`.
- **Two probe scripts** price the ladder before it runs:
  `scripts/probes/t93_d1_substrate_pilot.py` (the LR/settle box) and
  `scripts/probes/t93_d1_ternary_defect.py` (the rejected frozen-α fix).

### C1/C2 — batch-1 ladders (✅ landed 2026-11-16)
- `validation/plasticity_ladder.py` — the C1/C2 runner. `LadderCell` carries
  metric, BWT, forgetting, consolidation state and walltime; `LadderReport` the
  box, rulers and verdict. Stage 1 sweeps LR over `local`/`backprop`; stage 2
  sweeps EWC λ over `local_ewc`/`backprop_ewc` at the frozen LR. `_emit` appends
  every finished cell to `*.cells.jsonl`, so a kill keeps evidence. The verdict
  is a predicate (`_verdict`), not prose: promote only when local clears the
  floor on the ladder seed **and** the confirmation seed; a control below the
  floor is `invalid-control`. Stage 2's predicate is `_retention_verdict`:
  floor on both seeds, then a matched per-step cost (≤1.5×), then a
  pre-registered forgetting margin δ = 2√2σ ≈ 3.2 pp; a top rung that reduces
  local forgetting by less than δ closes C at the saturation point. The cell log
  is idempotent: `_resume_cells` reuses measured cells, `read_cells` dedupes a
  kill-race row, and `--replay` recomputes the gate without training.
- `core/continual/arms.py` — `create_local_arm` (PEPITA + Euclidean),
  `create_local_ewc_arm` (PEPITA + EWC), `create_backprop_ewc_arm` (exact
  gradient + EWC). Every factory takes `lr`; `create_si_arm` also takes `xi`.
  `_mlp_stack` is the one substrate/geometry source, so arms differ only in
  credit/update.
- `core/continual/runner.py` — a builder table (`_ARM_BUILDERS`) replaces the
  arm-name chain; consolidation, SI, LwF and replay dispatch on the `extra`
  components, so any credit composes with any consolidation. Train loaders own
  a `RandomSampler` generator seeded `config.seed + task_id`; eval loaders use
  256 so the 2000-sample ruler is not paid at batch 1. `_finalize_metrics`
  reads `state_bytes()` from the update/SI object.
- `core/continual/training.py` — the credit-facing `SystemState.y` is the
  **global** class index; the masked loss still uses the local label.
  `_finalize_output` stores the loss it computes.
- **What the code actually did.** The first ladder run was a defect probe: local
  scored 0.405/0.426/0.445/0.652/0.030 per task because PEPITA's second pass read
  task-local labels and trained the task-0 logits for every task. With the
  global offset, task 1 alone reached 0.964. The second run exposed a
  data-order confound: PEPITA's lazy feedback draw advanced the global RNG, so
  the control saw a different order (backprop 0.926 → 0.839 after the sampler
  seed). The third run is the recorded result: **local 0.945 / 0.947 at LR 1e-3
  on two seeds**, control 0.839 / 0.893, floor 0.55 → promote. Cost 220–287 s
  per cell at batch 1. The best local point is the ladder's lower edge; the
  recorded optimum is therefore a bound, not an interior optimum.

**What the C2 ladder actually did.** Its first launch measured the task-start
anchor defect (CORRECTION 12): two cells are kept as the defect probe in
`consolidation.inert.cells.jsonl`, never as a ladder. With the anchor fixed,
the eight-cell ladder closed at the saturation point λ=100: local 0.952 / 0.015
vs control 0.963 / 0.020 (gain +0.005 < δ=0.032; accuracy −1.1 pp), the
confirmation seed repeating it (0.951 / 0.016 vs 0.958 / 0.024) at a 1.07×
per-step cost. The second launch was killed after seven cells; the resumed run
reused them, and a cell written in the kill window left one duplicate row,
deduped on read by `(arm, knob, seed)`. The task-start `anchor()` and the
`test_task_boundary_anchors_without_erasing_importance` lock are the defect's
permanent fix.

### Landed 2026-11-16 (B1 — what the code actually did)
- **One screen, two surrogates.** `validation/routing_ladder.py` trains a
  shared trunk feeding `depth` parallel hard top-k selections (8 experts,
  k=2), averaged before the head. `GatedBlock.selection` returns the STE
  weights (`mask + masked_softmax − masked_softmax.detach()`) or the
  temperature-smoothed mixture over all experts; `RoutingNet.set_mode` flips
  them at matched weights.
- **The gap is a relative norm, per selection.** `_gradient_gap` reads each
  block's router gradient in both modes, averages the per-block relative gap,
  and validates the smoothed reference with a central difference along its own
  gradient (`FD_EPS = 1e-2`, tolerance 0.10). The probe runs at declared
  optimiser steps (8/16/32) and averages, because the end-of-training probe
  measures the saturated one-hot limit (CORRECTION 14).
- **Rulers.** `_blobs(task_seed, n, seed)` draws the task's centers once and
  only the samples move, so the held-out split reads the same task
  (CORRECTION 15); router accuracy is the last block's top-k agreement with
  the head's per-expert argmin loss, chance k/n = 0.25.
- **Measured 9 cells** (`results/t93_b1/routing.json`, 1.5–9.1 s each):
  gap 0.819 → 0.660 at τ=0.25 from depth 1 to 8, confirmation 0.681 → 0.644;
  reference FD ≤0.013; end-task accuracy 0.933–1.000 at every depth. The
  chained/end-of-training/instrument cells (`results/t93_b1/defect_probe/`) are
  kept as the defect probe, never a ladder.
- **Gate.** `tests/unit/validation/test_routing_ladder.py` (14 tests, 13 s)
  locks the growth/refusal predicate, the stub detector (a soft relaxation in
  place of STE reads a zero gap), the reference's FD agreement, and the
  kill-safe log (resume reuses, replay recomputes). **Verdict: refuse** at
  this box; B2 is not run and the trigger is in §14.

### Landed 2026-11-16 (T6b — what the code actually did)
- **One capability, three call sites.** `credit.free_activations(substrate,
  geometry, x)` is the optional free pass (`_FreePassOwner` /
  `_is_free_pass_owner`, the same callable-shape declaration as the bias
  hook). The pipeline calls it once for the FREE phase and once for the
  post-update free metrics, and skips the pre-forward, the FREE settle, and
  the free-metrics settle: `_owned_free_state` is the one constructor, so the
  owned set is built in one place.
- **The hybrid's own pass is one tensor.** `HybridCredit.free_activations`
  runs the full stack under `no_grad` and returns the logits, which the head
  and trunk recompute from `x` anyway; the free phase's state is
  `[logits]`, flat in depth. Arithmetic is unchanged (the loss is the same
  forward's logits; the credit reads only `x`/`y`), so the lockstep parity
  lock still passes.
- **Measured.** At the claim point (L=32/B=8192/W=1024) the hybrid's
  activation set moves **3249 → 611 MB** against the checkpointed arm's 1637
  (0.37×), forward-equivalents 5.50 → 4.27, walltime 45.5 → 34.6 s; at the
  lock point 210 vs 437 MB (0.48×). The `≤0.5×` property is live, no
  `xfail`.
- **Locks.** `test_the_hybrid_activation_set_is_half_the_checkpointed_arms`
  (no `xfail`), `test_the_hybrid_owns_its_free_pass` (tripwire: the
  pipeline's `forward_pass` must not run), and
  `test_the_plain_arm_reads_the_pipeline_forward` (the tripwire's positive
  control — without it the first test is a comment).

### Landed 2026-11-16 (T6c — what the code actually did)
- **The pass is a point coordinate.** `PilotPoint.stream_norm` (carried by
  `scaled`) flips `GeometryConfig.feedforward(stream_norm=...)`; the cell's
  coordinate is the point, so no argument can be silently dropped, and the
  plain cells stay bit-identical (`PilotPoint.stream_norm=False`).
- **`depth_rung` is the rung, not a second ladder.** It reuses `_measure`,
  takes its floor from `_learning_control` (one source for the bar), and runs
  the plain L=8/L=32 cells, the normalized pass's own `STREAM_LR_LADDER`
  (3e-3/1e-2/3e-2 — the plain box diverges under unit-scale streams), the
  shallow cell at the best LR, and a confirmation seed at the best point.
  `DepthCell` carries `lr`, so a cell states its own LR (`ArmCell.lr` added;
  the results JSON now names it per cell).
- **Measured and refused** (§2.10): plain L=32 0.100, normalized 0.314 /
  0.326 against floor 0.375; the edge LR 1e-1 collapses to 0.100, so the best
  point is interior; 3× steps reach 0.360, still 3.2 pp below the shallow
  cell; the pass costs 1.45× the plain activation bytes. The trigger is
  LayerNorm (c≈2, appendix recomputed) or the Innocenti init on a residual
  geometry.
- **One coordinate for the registration.** The plain stack stops learning
  between depth 4 (0.399) and depth 16 (0.100) at W=512/B=2048/200 steps, so
  T6a's depth rung is L=4→8 until T6c re-opens. The registration's measured
  rows: backprop 0.343/0.385/0.139 and backprop+ckpt the same; hybrid
  0.100/0.167/0.100; local 0.340/0.350/0.145 at LR 0.1/0.3/1.0, all on seed 21.
- **Locks.** `test_the_depth_rung_verdict_reads_the_floor_and_the_confirmation`
  (the verdict function: plateau, lift, floor, and the second seed) and
  `test_the_rung_point_carries_its_pass_into_the_geometry` (the coordinate
  reaches the geometry; removing the pass silently measures the plain arm).

### Landed 2026-11-16 (T6a — what the code actually did)
- **One registration, one screen, no claim run.** `validation/memory_frontier.py`
  gained `_learning_ladder`, `_screen`/`run_screen`, `InstrumentControl`,
  `ClaimCell`, `BindingRow`/`BindingAppendix`, `ScreenVerdict`,
  `MemoryFrontierRegistration`, `build_registration`, and
  `register_memory_frontier` (`--register`). The registration is written and
  committed to `configs/preregistrations/t93_memory_frontier_registered.json`
  before any claim; its 30 claim cells are priced with the measured coefficient
  and never run.
- **The OOM guard re-posed the box, and that is recorded.** The pilot point is
  L=16/W=512/B=2048 (two depth deltas, c=4.25, spread 0.0 %) and the claim point
  is the L=4→8 depth rung at the same width/batch, not the 4.5 GiB
  L=32/W=1024/B=8192 allocation. The coefficient still cancels the cuBLAS
  floor in the deltas, and the claim cells fit with a measured binding share
  of 0.81/0.85.
- **Measured and refused by the rung-2 screen.** The 12 ladder cells at L=8
  (seed 21) read backprop 0.343/0.385/0.139, the same for `backprop+ckpt`,
  hybrid 0.100/0.167/0.100, and local 0.340/0.350/0.145 at LR 0.1/0.3/1.0; the
  best per arm freezes at 0.3. The screen then reads the hybrid at 0.167/103 MB
  against the checkpointed arm's 0.385/85 MB (1.22×) and the confirmation seed
  at 0.154 vs 0.363, so `verdict=refuse`: the claim run is not scheduled.
- **Both controls pass.** Instrument c=4.25 from two deltas within 10 % of the
  declared 4.1; learning backprop 0.385 against floor 0.375. A failed control
  raises `ValueError` and writes no registration.
- **No hypervolume reference point.** The registered claim is W1's ≤0.5×
  activation-bytes form, so the sharper alternative is pre-registered and the
  hypervolume form is deliberately absent.
- **Locks.** `tests/unit/validation/test_memory_frontier_registration.py`
  (11 tests, 11 s, no model trained: the essentials and the raw-JSON loader
  split, disjoint seeds, the 30-cell minimal ladder, the frozen best point with
  the smaller-LR tie, a failed control, the binding arithmetic, the screen's
  refuse/candidate/coordinate verdicts, and the write-then-commit no-overwrite
  rule). Replay: `uv run python -m computronium.validation.memory_frontier
  --register --device cuda --registration-dir results/t93_a`.
- **No defect in the mechanism; one serialization defect found and fixed.** The
  first write dropped `ScreenVerdict`'s derived `verdict`/`reason`/`trigger`
  because they are properties, not fields; `to_dict` now emits them explicitly
  and the screen test fails when that line is removed.

### Landed 2026-11-17 (T6d — what the code actually did)
- **One module, one box, two knobs, and the sibling control.**
  `validation/hybrid_update.py` reuses `memory_frontier.measure_cell` (now
  public, with `gamma`/`train_biases` keywords) at the trigger's box
  (L=8/W=1024/B=8192, 200 steps, LR 0.3): 12 measured cells (14 planned), ~200 s, 516-1037 MB
  peak, seeds 21/22 and the ladder seed 21. The cell log
  (`hybrid_update.cells.jsonl`) is appended per cell, so a rerun reuses a
  measured cell and `--replay` rebuilds the report without training.
- **The knobs move nothing.** `train_biases=True` reads 0.167/0.175
  (+0.5 pp over 0.163/0.169); `feedback_scale` 0.05/0.3/1.0 reads
  0.163/0.100/0.100 -- the ladder peaks at the registered scale and
  collapses to chance above it; head-only (gamma=0, zero trunk contrast)
  reads 0.149. The floor is 0.408 (the checkpointed reference 0.419/0.416
  minus 1 pp).
- **The sibling control names the mechanism.** The same trunk rule as a whole
  stack (`local`) reads 0.400/0.405/0.384 at the same box, LR, and seed --
  within 1.5 pp of the reference and 24 pp above the hybrid -- and it does not
  collapse where the hybrid does. The exact-gradient split, not the trunk's
  rule, its bias path, or its scale, is the mechanism (CORRECTION 24). The
  hybrid's activation set is 516 MB against the reference's 485 MB
  (**1.06×**), so the pilot box cannot decide the memory half: L=32/stream is
  the memory box (§2.14).
- **One API change, no new primitive.** `memory_frontier._credit`,
  `build_arm`, and `_measure` take `gamma`/`train_biases` (defaults keep the
  registered arms bit-identical); `_measure` -> `measure_cell` and
  `_cifar` -> `cifar_splits` are public for the diagnostic. No schema and no
  registry row changed.
- **Locks.** `tests/unit/validation/test_hybrid_update.py` (16 tests, 9 s, no
  model trained): the gate's six branches, the floor from the reference, the
  ladder's confirmation seed, the sibling branch, the head-only branches, the
  assembly's 12 measured cells, the JSON's rulers, and the log's reuse/dedup. The
  property suite's `frontier._cifar`/`_measure` calls moved to the public
  names.

### Landed 2026-11-16 (D2 — what the code actually did)
- **One runner, one box, one screen.** `validation/matched_substrate.py`
  reuses the D1 cell runner at **2×** D1's width (784-64-10; `_build_system`
  and `_box` gained `hidden_dims`) with the frozen LR 1e-2. It screens settle
  40 against 20 on seeds 57/58 (4 cells), adopts 20 when the memory arm does
  not gain 0.5 pp on both seeds, then runs 5 paired seeds at 4 arms each
  (digital rule, memristive, QDQ, backprop): 24 cells, 915 s on CPU.
- **The verdict is a paired interval, not a point.** `_gate` reads the paired
  accuracy gap's 95% interval (from `compute_confidence_interval`), the
  walltime ratio at matched settle compute, and the constraint that binds
  (the int8 width at the QDQ gap, the programming budget at the walltime,
  or drift). A shared gate proves the verdict is a predicate, and
  `replay_matched_comparison` recomputes it from `matched.cells.jsonl`.
- **Measured and refused** (§2.11): −0.43/−0.24/−0.29/−0.34/−0.26 pp, mean
  **−0.31 pp, CI [−0.41, −0.22]**, at **2.18/2.21/1.35/2.26/2.44× walltime**
  (mean 2.09×), forward-equivalents **1.00×**, 2 vs 4 B/weight; QDQ −0.01 pp
  mean; control 0.9367/0.9351/0.9277/0.9377/0.9376. The screen's extension
  gain is +0.17/−0.05 pp, so settle 20 stays. **D3 does not fire**; the
  re-open is a device-level or compiled quantisation of the pair.
- **One apparatus correction.** `QuantizedSubstrate` now quantises (the old
  forward cast to int8 without rounding weights; CORRECTION 19), and the QDQ
  arm prices 8 bits/weight with no device model. Its QDQ gap isolates the
  representation, so a parity claim cannot be attributed to the width.
- **Locks.** `tests/unit/validation/test_matched_substrate.py` (13 tests):
  the paired interval, the cost and width rulers, the QDQ forward/STE and
  device width, the extension screen, the 2× box, the crash refusal, and the
  kill-safe replay.

### Landed 2026-11-16 (F1 — what the code actually did)
- **One generator, one cheap task, one matched ruler.**
  `validation/composition_ladder.py` reuses `iter_candidates` and the legality
  filter (2,000 candidates examined in 18 s yielded 321 composable cells) and
  evaluates through `experiment/kernel/evaluate.evaluate_cell`. The box is
  `digits` quick mode (1797×64, 10 classes) at B=32, 57 batches — one epoch,
  so 57 forward-equivalents per cell — with one seed, CPU, and a 50k parameter
  ceiling. `composition.registered.json` is written before the first cell.
- **The reference is every legal single-axis arm, not a composition.** 41 arms
  (the default plus 40 variations over the six axes; `plasticity:
  conflict_adaptive` refused training and is recorded). The best is **0.797**
  (`update`, `ortho_adam`), then 0.792 (`geometry`, `attention`), 0.769
  (`tile_mesh`), 0.764 (`muon`, `riemannian_orthogonal`), 0.456
  (`causal_transformer`); the learning control reads 0.194 (the untuned default
  MLP is at chance at this box). The reference's second seed reads **0.867**
  (drift 6.9 pp; the 10 pp band was fixed from the pilot, not after the run).
- **Fifty legal compositions, no refusals.** The seeded reservoir sample has
  50/50 measured cells. The best reads **0.669** (`digital / tile_mesh /
  instantaneous / temporal_psi / random_projections /
  riemannian_orthogonal`, four non-default axes), then 0.481
  (`ternary / conv / temporal_psi / gradient / muon`), 0.328, 0.306, 0.269,
  0.189. No composition clears the bar (0.797 + 1 pp = **0.807**).
- **The family ladder.** Families are credit primitives, selected by median (n≥2);
  the best-looking is **`random_projections`**. Its widths 2/4/6 read **0.092
  / 0.783 / refused** (the width-6 cell, `tile_mesh + energy_minimization +
  random_projections + riemannian_orthogonal + analog + temporal_psi`, failed to
  train). The confirmation seed at width 4 reads **0.814**, a **3.1 pp spread**
  from the screen seed — wider than δ = 1 pp, so the point did not reproduce.
- **Measured and refused at this box** (§2.11, track F): the screen's best trails
  the single-axis default by 12.8 pp, the family ladder by 1.4 pp, and the
  confirmation's +1.7 pp is inside the seed spread. Verdict: **refuse
  composition at this box**, not "composition is false". Re-open: **F2's five
  seeds** at the same box, a matched-parameter composition, or a real task family
  (`MNIST`/`CIFAR`, wider axes). The knob box (41 + 1 + 50 + 3 + 1 = 96 cells,
  ~19 min CPU) and the 10 pp control band are pre-registered, not post-hoc.
- **Locks.** `tests/unit/validation/test_composition_ladder.py` (17 tests):
  the gate's promote/refuse/coordinate/invalid branches, the median family
  selector, the width ladder (2/4/6 non-default axes, family credit kept), the
  seeded deterministic screen sample, the reference sweep's six axes and legality,
  registration-before-first-cell ordering, the report's rulers, and replay.

## 19. Primitive work program (capability-first, ordered)
**Framing.** The primitives are the work. Each row adds something the system
cannot do today, and every row pays the same price: spec, kernel, reference,
cases, identity card, a registry row, a parity test, and a lock — the shape of
the ten credits that ship. No row is gated behind a measurement verdict
(`AGENTS.md` SEC, capability-first amendment; CORRECTION 25). *"More primitives
is not progress"* is retired: it was the rule that made capability work depend
on negative measurements.

**Inventory (2026-11-15, read from the identity cards).** Absent:
`ForwardTangentCredit`, `ScoreFunctionCredit`, `ZerothOrderCredit`,
`SurrogateCredit`, `LocalSupervisionCredit`, `CascadeSynapsePlasticity`,
`BayesianOnlineUpdate`, `EligibilityPropCredit`, `UnbiasedOnlineRTRL`,
`RTRLReference`. Present: `lion`, `adam`, `local_adam`, `ortho_adam`,
`mean_norm`, `role_split`; STE utilities; REINFORCE; EWC; SI (an arm, to lift);
replay; eight EP variants plus PC/pcalm.

**The program, ordered by capability per session.**

| # | Primitive (axis) | Capability it adds | Task family it unlocks | Cost | Depends on |
|---|---|---|---|---|---|
| 1 | `ForwardTangentCredit` (C) | unbiased pathwise gradient at O(1) activation memory | supervised tasks at O(1) memory; the unbiased reference for every biased credit | 1 session | none |
| 2 | `ScoreFunctionCredit` (C) | unbiased gradient of an expected loss | sampled computation (Gumbel selection, RL tasks) | 1 session | none |
| 3 | `ZerothOrderCredit` (C) | gradient-free update (SPSA, two forwards) | non-differentiable device paths | 1 session | none |
| 4 | `SurrogateCredit` + a hard top-k geometry (C, G) | a hard selection trains without a soft relaxation | routing/MoE at variable k | 2 sessions | #1 or #2 for the baseline |
| 5 | `LocalSupervisionCredit` (C) | deep local credit without a boundary bottleneck | layerwise deep training (greedy, DGL, InfoPro) | 1–2 sessions | none |
| 6 | `EligibilityPropCredit`, `UnbiasedOnlineRTRLCredit`, `RTRLReference` (C, G) | **temporal credit**: a sequence axis the system does not have | sequence tasks | 2–3 sessions | a sequence geometry + loader |
| 7 | `SynapticIntelligenceUpdate` (lift), `CascadeSynapsePlasticity`, `BayesianOnlineUpdate` (U, P) | long-stream consolidation without replay | ≥20-task streams | 1–2 sessions | #5 optional |
| 8 | `FactoredSecondMomentUpdate` (Adafactor), `QuantizedStateUpdate` (8-bit Adam), `ScheduleFreeUpdate` (U) | optimizer-memory and schedule capability | any task at a lower optimizer footprint | 1 session each | none |

**First session — the estimator family (build spec).**
`ontology/credit/`: three classes with identity cards — `estimator_kind` =
`forward_mode` / `score_function` / `zeroth_order`; `bias_reference` =
`unbiased_pathwise` / `unbiased_expected` / `finite_difference`;
`symmetry_requirements`; `approximation_parameters` = the variance knob and the
sample count. Config classmethods: `CreditAssignmentConfig.forward_tangent(...)`,
`.score_function(...)`, `.zeroth_order(...)`. Three primitive rows in
`primitives/credit_assignment/{forward_tangent,score_function,zeroth_order}/`:
`spec.py` (the equations), `kernel.py` (Triton where it pays, the reference
otherwise), `reference.py` (`step(case)`), `cases.py` (one tiny fixture each),
`__init__.py`. Registry rows, `ontology/__init__` exports, and the three
dispatcher entries.

**Equations.**

- **forward tangent**: `v ~ Rademacher(θ)`; `d = jvp(f, θ, v)`; `ĝ = d · v`
  (unbiased, since `E[vvᵀ] = I`); the variance falls as `1/√n` tangents.
- **score function**: `a ~ Categorical(softmax(logits))`;
  `ĝ = ∇_θ log π(a) · (R(a) − b)` with `R = −CE(a, y)` and `b = mean_batch R`
  — the unbiased gradient of the expected loss, with a graph through the logits
  only.
- **zeroth order**: `Δ ~ Rademacher(θ)`;
  `ĝ = (L(θ + cΔ) − L(θ − cΔ)) / (2c) · Δ`; two forwards, no graph.

**Locks (landed with the primitives).**

| Lock | What it proves |
|---|---|
| `test_credit_dispatch_lock` | each of the three builds through spec / factory / joint |
| `test_estimator_lock` | each declares `estimator_kind` and `bias_reference`; the axis totality holds |
| `test_forward_tangent_parity` | `ĝ · g / ‖ĝ‖‖g‖ > 0.3` at 8 tangents on a tiny fixture, and the variance falls as 1/√n |
| `test_zeroth_order_parity` | cos > 0.9 at 256 pairs against the exact gradient on a quadratic fixture |
| `test_score_function_parity` | cos > 0.9 at 1024 samples against the exact gradient of the expected loss on a two-action fixture |

Each also trains a tiny task above chance (MNIST quick, one epoch) and carries a
**capability card**: task, memory, steps, and what stops it. The capability
cards are the deliverable, not a verdict.

**Build notes per family** (mechanism variants and their prices).

| Family | Variants | Price |
|---|---|---|
| forward-mode | `jvp` random tangents; antithetic pairs; layer-blocked tangents | O(1) activation memory; one forward + tangent pass |
| score-function | REINFORCE ± baseline; Gumbel selection; leave-one-out baseline | one sample per batch; graph through the logits |
| zeroth-order | SPSA 2 evals; antithetic ES; layerwise blocks | two forwards per step, no graph |
| routing | STE; Gumbel-ST; perturbed top-k; z-loss load balance | no new state; the geometry gains a top-k gate |
| layerwise | greedy layerwise; DGL; InfoPro; periodic global guidance | aux-head params enter the ruler |
| temporal | e-prop; UORO rank-1; exact RTRL fixture | O(params) state; a sequence geometry + loader |
| streaming | SI lift; Benna–Fusi cascade; VON | SI ≈ EWC at 5 tasks — the long-stream protocol (≥20) is the capability |
| optimizer | Adafactor; 8-bit Adam; schedule-free | optimizer-state bytes enter the identity card |

**Not in this program, with reasons.** More EP/PC variants (eight plus two
ship; no task family needs another); substrate primitives (§12, deferred);
optimizer-of-the-month (arm-neutral); unsupervised rules with no regime;
lookahead/EMA/SWA unless pre-registered for both arms. Each is a scope note,
not a verdict: a task family can promote any of them.

## 20. Executability audit (2026-11-15, verified against the claim path)
| Assumption in v4 | Verified in the repo | Consequence |
|---|---|---|
| Peak memory is not measured in the claim path | `core/system_trainer/_resources.py:73,133,155` captures it; `_trainer_utils.py:194-207` emits `memory_usage` per cell | T4a is hours; only the decomposition, RSS, and guard are new |
| Backprop checkpointing is entirely absent | **Landed (T4b):** `core/gradient_checkpointing.py` wraps the geometry forward in √L segments; `torch.utils.checkpoint(use_reentrant=False)` was already used for settle steps (`core/local_learning/settling.py:403,446,760`) | proven API, and the parity lock makes the wrapped unit (forward, not step) checkable |
| The claim path is `domains/trainer.py` | The claim path is `experiment/kernel/evaluate.py` → `SystemTrainer.train_epoch` | Instrument `_resources`, never `_TaskTrainer` |
| CIFAR-10 needs a download | Cached at `data/cifar-10-batches-py`; registry marks it `EXPENSIVE` | Fixed 10k train subset + full test; price the cell |
| The hybrid is one schema field | `System.credit` is a single config (`ontology/system.py:426`); `BackpropCredit` exists (`joint.py:122`) | T3b is a wrapper primitive, not a schema change |
| A frontier runner must be built | `validation/backprop_parity.run_parity` (:729) already loops depth, baseline, seeds, CIs, memory, FLOPs | T4c extends it; no second runner |
| The composition space is enumerable (731,808 cells) | `iter_candidates` pages legal composable cells; 2,000 candidates → 321 legal in 18 s | F1 samples 50 uniformly with a seeded reservoir, no enumeration |
| Synaptic Intelligence is missing | `SynapticIntelligence` at `core/continual/losses.py:84`; `create_si_arm` at `arms.py:238` | Lift to U; do not implement |
| P4 needs a stream and arms | `run_continual_learning`, `create_ewc_arm`, `create_replay_arm`, `SplitMNIST` exist | P4 is a protocol/measurement ticket |
| A router must be built | `algorithms/routing/` exists | Reuse; do not rebuild |
| Depth/width/batch are registry axes | They are hyperparameters/run settings (`num_layers` integer, `batch_size` run config) | Fix the ladder vocabulary; no axis work |
| Lion/sign-momentum is missing | `primitives/parameter_update/lion/` exists | No admission; reuse |
| PC-ALM trains at the shallow atlas box | `PCALMDynamics` step 1e-1 NaNs at depth 2; 0.02 is stable but chance; its card validates depth 100 | The PC-ALM row is a regime mismatch/refusal with a depth-100 trigger, not a verdict |
| The atlas needs a second trainer | `SystemTrainer` + `estimator_atlas._run_cell`; one train loop, `_CappedLoader` | Reuse; no second trainer |
| A "gate" can be a sentence | Locks and claim-table assertions are runnable predicates | Binding guard is a test, not a CLI |
**v6 arithmetic corrections (B1–B6, applied).**
| Bug | Correction | Where |
|---|---|---|
| B1: gate on `backprop+ckpt` self-defeats (Adam share 41%) | gate on **plain backprop** (89% SGD / 73% Adam); ckpt reported only; optimizer named per table | §4, §9.5 |
| B2: ≤0.5× *peak* is unreachable (params+optimizer floor) | ≤0.5× **activation bytes**, or ε-dominance with a pre-registered HV anchor | §2 W1 |
| B3: calibration hardcodes c=1; LN gives c≈2 | measure and lock **c** on the declared geometry | §4, §9.6 |
| B4: hybrid step semantics undefined | explicit four-step order + **store-all hybrid reference** lock | §18 T3b, §9.3 |
| B5: W4 "matched memory" contradicts §6 | pre-registered **analytic byte cap** in the GPU runner | §2 W4, §6 |
| B6: local objectives labelled "biased gradients" | `gradient_approx` vs `objective_local`; alignment, not bias, for local objectives | §2, §18 T1 |
**Cost-critical refs, confirmed 2026-11-15.** `_resources.py:73,133,155` +
`_trainer_utils.py:194-207` (peak → `memory_usage`); `backprop_parity.py:729`
(`run_parity`; portfolio :121; `batch_size` hardcoded 64 at :778, so T4c must add
the parameter); `core/continual/losses.py:84` (SI), `arms.py:90,238` (EWC, SI
arm), `runner.py:412` (`run_continual_learning`); `core/utils/surrogate.py:8` +
`z3_fixed_weights.py`; `ontology/system.py:426` (single credit) +
`core/system_trainer/joint.py:122` (`BackpropCredit`); `settling.py:403,446,760`
(checkpoint precedent); `primitives/parameter_update/lion/`; `psutil` at
`pyproject.toml:100`. **Costs hold.**
**Remaining execution risks, priced.**
1. **Hybrid integration — closed.** It did share one `train_step`: the credit
   re-runs the stack from the free state (like PEPITA), so `System.train_step`
   needed no change. The measured split is a stack index on a Linear, and the
   composed-path learning control passes. Residual geometry required one
   geometry helper (`step_layer`) so the lockstep's per-layer advance threads the
   same skip input the full pass does; the parity lock covers it.
2. **`torch.func.jvp` on a composed system.** Many primitives mutate state.
   Scope the forward-mode reference to a pure `nn.Sequential`; if the composed
   system fails, it is a reference, not an arm.
3. **A 64-layer fp32 MLP may not train.** LayerNorm and residual connections are
   the fallback; if the floor is unreachable at L=32, cap the ladder and report
   the measured ceiling rather than forcing depth.
4. **CIFAR-10 flat-MLP accuracy is low.** W1/W2 are relative; say so in the
   pre-registration so a 45–60% row is not read as a capability failure.
5. **`psutil` availability.** Confirmed: declared at `pyproject.toml:100`; read
   `Process().memory_info().rss`. No new dependency. **Landed in T4a:**
   `EpochResource.cpu_rss_mb`, `None` only if the import fails.
6. **The pilot point does not fit the card at the measured coefficient.**
   c=4.1 puts L=64/B=8192/W=1024 at ≈8.7 GiB (SGD+momentum). Re-posed to B=8192
   at L≤32 or B=16k at L≤16 (§4.1). This is arithmetic, not a risk: the ladder
   is bounded by the card, and the checkpointed arm (≈1.0 GiB) is what buys
   depth. Price the claim cells from these coordinates, not the v6 appendix.
7. **A verified memory class is claimed for two backends, not twelve.**
   T3 measured FF and PEPITA (`complexity_verified=True`, flat at L=4→32, §2.2 of
   `BENCHMARKS.md`); the other eight rungs still declare `False`, so their rows
   are honest gaps rather than claims. Filling them is T5 work, not a defect.
**Net effect.** The truth pass and the decomposition are one day, not three. The
**implementation** falsifier (the lockstep and the hybrid both work) cost ~6
sessions and is closed; the first **research** falsifier (hybrid vs ckpt at a
binding point) now has two registered boxes and two rung-2 refusals: L=4→8
(0.167/103 MB vs 0.385/85 MB, 1.22×) and L=8→32/B=4096 (0.184/210 MB vs
0.364/453 MB, **0.46×** — the memory bar is met and the baseline trains, so
the accuracy gap is the split, not the trunk's rule or its scale). The next
defect fix is **T6e**, not a claim run; the session order is the estimator
family (§19 row 1). T6/T6a is no longer the critical path to a
positive result: the
hybrid has a landed wrapper, measured parity, a store-all reference fixture,
and a depth-flat peak, but its accuracy is 17 pp below the baseline at the
pass-carrying box.
