# TODO13b.md — Execution Plan: Compose the Winners

> **Opened 2026-09-07 (rev 2).** Distills [TODO13.md](TODO13.md) §6 into an
> ordered execution plan. The asset inventory, dead-item ledger, and findings
> record live in TODO13/TODO11 — this document is **what to build, in what
> order, what lands, and what we do in each branch.**
>
> **Thesis:** the repair era made the instrument honest. TODO13b spends that
> honesty on capability. Four moves, each ending in something you can show:
> (1) verify or kill the bombshell, (2) put OrthoAdam on everything,
> (3) build the per-layer local-contrastive credit (the flagship),
> (4) land closed-form ψ adaptation (the thing backprop cannot do).
>
> **Posture (carried):** optimism with a probe budget, not a mood. The
> empirical grounds: *the algorithms kept being better than the measurements
> said* — every pessimistic verdict that got a defect audit either dissolved
> or got sharper. That cuts both ways: **optimistic verdicts get the same
> matched-step / multi-seed / defect-audit treatment** (R11.5.5a applies to
> wins too). Every session ends in a pinned demo, a killed speculation, or a
> promoted probe. Audit-only sessions are retired.

---

## ⚠️ §0 — Read First: The Bombshell Is Almost Certainly a Sick Baseline

If walltime was a factor, the computer may have been spuriously busy affecting results.

Set the expectation now, before anyone falls in love with a number.

**The D17 seed-0 headline — transformer/ff_hybrid/muon 5.05 vs
transformer/bp/adam 27.55 (5.5× better, 7× fewer steps) — is almost
certainly inflated by a broken backprop denominator, not a real 5.5×
algorithmic win.** The ff_hybrid number may well be strong, but the
*comparison* is suspect.

**The smoking gun is already in the data:** a healthy baseline gets *better*
with more training. bp/adam got **dramatically worse**:

| Timepoint | Shape | Steps | bp/adam val_ppl |
|---|---|---|---|
| 2.5 min smoke | 156k params | — | **5.82** |
| 15 min registered | 7.4M params | 15,217 | **27.55** |

~6× the parameters, ~6× the walltime, ~7× the steps → **5× worse**, landing
near unigram entropy (~22–30 ppl; chance = 65). Meanwhile ff_hybrid improved
monotonically (6.74 → 5.05) — what a healthy run looks like. **More training
making the baseline worse is the signature of collapse or mis-measurement,
not a fair backprop run.**

**Most likely culprits (diagnostic order, all free-to-cheap):**
1. **Registered-scale lr mismatch** — bp/adam's lr 1e-3 was tuned on the 156k
   smoke shape; at 7.4M it may overshoot/collapse. (H1/H4 lesson: never trust
   a baseline at an unverified lr.)
2. **The `_val_sets` mixed-ctx defect** — fixed *en route* on 2026-09-06
   (windows were cut at max(ctx)). If bp/adam ran pre-fix, its val windows
   were mis-cut and its ppl is inflated. **Confirm pre/post-fix provenance.**
3. **Adam depth/second-moment collapse** — Adam is depth-fragile in this repo
   (D15: BP×Adam 0.303 at depth 16 where Muon hits 0.834). 7.4M/6L may
   trigger it.
4. **Throughput asymmetry masking an accounting artifact** — the 7× step gap
   (2,200 vs 15,217) needs a per-step cost explanation before any walltime
   comparison is quoted.

**What this means:** "verify the bombshell" is operationally **"diagnose the
baseline."** This is not pessimism — it is the defect-hunt posture applied to
a positive result.

**The reframe that keeps this ambitious:** even if the 5.5× collapses to
parity, *"hybrid local-credit rule matches backprop on a transformer LM"* is
still the best local-learning number in the repo. **The plan captures that win
in every branch.** We are not deflating the bombshell; we are making sure
whatever we promote is true. The headline only exists if it survives a healthy
baseline.

---

## §1 — The Priority Stack (ranked by cross-the-room value × cost)

| Rank | Item | Source | Why it's here | Cost to first signal |
|---|---|---|---|---|
| **0** | Bombshell regime reconciliation + per-step instrumentation | TODO13 §1 steps 0–1 | Biggest number in the repo sitting unverified; anomalies load-bearing (§0). Free-to-cheap until step 3. | **Free** (read the JSON) |
| **1** | **SP6 — OrthoAdam on LM** | TODO13 §6 SP6 | OrthoAdam dominates mlp/attention/lattice/jpc but has **never run on LM**. Two 2.5-min cells upgrade the bombshell arm for free. Highest value-per-cost in the portfolio. | ~5 min |
| **2** | **S3 — `local_contrastive` credit (flagship build)** | TODO13 §6 S3, §2e | The only artifact realizing Claim A (true locality) + Claim B (physical advantage) + competitive learning together. Flips F5's pinned miss. B4 mechanisms probe-confirmed. | 2–3 sessions |
| **3** | **S4 — closed-form ψ adaptation** | TODO13 §6 S4, §4c | "LoRA without gradients." Structurally impossible for backprop — the most *novel* capability. D22 named both the exact boundary and the exact lever. | 1–2 sessions |
| **4** | S1 — depth frontier + zero-shot LR transfer | TODO13 §6 S1 | Cheap CPU. "Local learning scales to 100 layers; tune once, run anywhere." | interstitial |
| **5** | SP2 — does OrthoAdam make weak credit strong? | TODO13 §6 SP2 | A profound reframing if it holds: "the optimizer, not the credit rule, is the learning." Cheap, uses existing credits. Rides W1. | interstitial |

**Deferred to Tier-2 (do not start until Tier-1 lands):** C1 contrastive-LM
parity (mechanical fallback only), reward-modulated STDP (F2 closer, not the
frontier), registered-scale P-axis campaign, P2 untried jpc cells,
transformer-ePC settle extension, SP3 inference-time settling (slack-only),
all demo-API roadmap items, all as-touch hygiene.

---

## Workstream W0 — Verify or Kill the Bombshell (priority zero)

**Anchor:** TODO13 §1 + §0 above. ff_hybrid/muon 5.05 vs bp/adam 27.55,
single seed, 15-min arms, registered shape.

**This is a performance claim, never a locality claim.** The Claim A scope
audit stands: ff_hybrid's autograd chain IS a backward sweep through hidden
layers. Locality is W2's job.

| Step | Action | Cost | Lands as |
|---|---|---|---|
| **0 — reconcile from disk** | Read `benchmark_results/d17_seed0.json` curves. **(a)** Where is bp/adam at step 2,200? Where is ff_hybrid extrapolated? **(b)** Is bp/adam's *train loss* descending (lr collapse if it stalls high) or low-train/high-val (overfit or eval defect)? **(c)** Tokens seen per arm. **(d)** Check registered lrs against the `step_semantics` guard. **(e)** Confirm which arms ran pre/post the `_val_sets` mixed-ctx fix. | **free** | Regime verdict in the probe docstring: which failure class the baseline is in |
| **1 — instrument** | Per-step cost + per-step val_ppl on both arms at ~1 min. Explain the 7× throughput asymmetry (is ff_hybrid paying bp's cost + goodness overhead, per the Claim A audit?). If bp/adam's lr is suspect, micro-sweep it on its own axis. | ~10 min | Throughput accounting; healthy-or-sick baseline call |
| **2 — smoke-verify** | Re-run every registered arm end-to-end at ~1 min with the healthy baseline config (the D17 lesson: 1-min arms before minute-scale arms). | ~15 min | Clean harness |
| **3 — resume seeds 1–2** | **Gated, per-batch approval.** Only on *verified* arms: `uv run python scripts/probes/lm_comparison.py --minutes 15 --arms transformer/ff_hybrid/muon,transformer/bp/adam,mlp/ff_hybrid/muon --seed 1` (then `--seed 2`); copy JSON → `d17_seed<N>.json` after each. **If W1 upgraded the arm, run the upgraded version.** | ~90 min GPU, user-gated | Seed means |
| **4 — render verdict** | Apply pre-registered band mechanically; promote to **fixed-step** D17 demo + gallery lock (walltime arms never pinnable). | 1 session | D17 pinned, or killed with mechanism |

**Pre-registered band (carried from TODO12, unchanged):** reported = mean
val_ppl over seeds 0–2; gap = (ff_hybrid − bp)/bp. **<15% parity · 15–25%
competitive-with-caveat · >25% MISS → C1 fallback triggers mechanically.**
If step 0/1 shows the baseline was sick, recompute the band against a healthy
baseline — same mechanical rule, honest denominator.

**Kill criterion:** if step 0/1 shows bp/adam collapsed to unigram *and* the
registered lr / mixed-ctx defect explains it, the "5×" framing is dead; the
ff_hybrid story reverts to the 2.5-min anchor (~15% behind bp, still the best
local rule). Nothing was quoted, nothing lost.

---

## Workstream W1 — OrthoAdam on Everything (the cheap multiplier)

**Anchor:** OrthoAdam beats both parents on 3/4 geometries (mlp 0.930 /
attention 0.911 / lattice 0.924; graph stays with Muon 0.433), repairs Adam's
depth collapse (0.878 vs 0.303 at depth 16), partially substitutes μPC.
**It has never run on LM.**

**SP6 cells (run first, parallel with W0 steps 0–1):**

| Cell | Pre-registered prediction |
|---|---|
| `transformer/ff_hybrid/ortho_adam` (2.5-min smoke, registered shape) | OrthoAdam ≥ Muon (5.05-equivalent or better) |
| `mlp/epc_thermo/ortho_adam` (2.5-min smoke) | OrthoAdam ≥ Muon (~21 ppl or better) |

**⚠ step_semantics discipline (binding):** `ortho_lr` goes on OrthoAdam's
OWN axis — **1e-3** (the measured plateau 5e-4–1e-3), NOT borrowed from
Muon's 0.01. The jpc regime proved `ortho_lr` is sharp (3e-3 degraded μPC to
0.52 — a step-size artifact). `validate()` warns >0.05; trust it. Never sweep
a borrowed euclid/muon grid.

**NS variant note:** Newton–Schulz (5-step quintic) is statistically identical
to SVD for OrthoAdam and ~40% cheaper — use NS for any deep sweep. But NS
*collapses FF×Muon* (different mechanism: FF×Muon's update IS the raw polar
factor). Keep SVD default for FF×Muon; NS fine for OrthoAdam.

**Lands as:** two new cells in the D16-style coverage map + a RESULTS.md line.
If OrthoAdam upgrades the bombshell arm, W0 step 3 re-runs the *upgraded* arm
— the headline improves for free.

**SP2 follow-up (interstitial, once W1 lands):** run existing weak credits
(FA, ff, pepita) under OrthoAdam vs Euclid on MNIST-quick.
**Pre-registered question:** does OrthoAdam close the gap between weak and
strong credit? If FA×OrthoAdam ≈ BP×OrthoAdam, the finding is *"the optimizer
is doing the learning; credit only needs a good-enough direction."* Cheap,
uses existing infra, potentially profound.

---

## Workstream W2 — `local_contrastive` Credit (the flagship build)

**Anchor:** TODO13 §2e (B4 probe), §5 (F5 miss), and two pre-falsified traps
(instantaneous normalization destroys contrastive learning; detached-carry
keeps all graphs alive). The only artifact composing Claim A + Claim B +
learning.

### Build spec (dependency order)

1. **Per-layer recompute pattern** — O(1) peak memory. Detached/recomputed
   inter-layer inputs, per-layer local backward, **no-grad recompute** (NOT
   detached-carry — that keeps all graphs alive and measures *worse* than bp).
   Reuse `scripts/probes/b4_per_layer_ff.py` verbatim as the reference.
2. **Per-layer stream normalization** — load-bearing at depth ≥ 3 (layers die
   without it; G contrast → 0). Share A5's vocabulary (`unit_rms`/`spectral`).
3. **EMA-based magnitude normalization** on the credit gradient — the untried
   rung. **Never instantaneous** (gradient magnitude carries information in
   goodness-contrast objectives via softplus gating; instantaneous norm
   collapses learning at every depth). This EMA rung is the one untried repair
   for the class's depth wall.
4. **Full registry wiring** per the TODO12 wiring checklist (credit dispatch
   `_CREDIT_FACTORIES`/`_CREDIT_ALIASES`, config classmethod, wiring-lockstep
   lock, root + ontology exports, `SystemConfig.validate` whitelist,
   snapshot/resume if it holds state). **Credit-semantics change → gates the
   full property suite.**

### Pre-registered predictions (falsifiable, in order)

| # | Prediction | Falsified → |
|---|---|---|
| P1 | `local_contrastive` trains depth-2 MNIST > 0.80 (B4 hit 0.827) | re-audit recompute pattern |
| P2 | Per-layer peak saved bytes < bp's whole graph at depth 4 (B4: 268.8 vs 569.3 KiB) | F5's ratchet stays; recompute is wrong |
| P3 | **EMA rung lifts depth-4 accuracy above the instantaneous-collapse floor** (depth wall is the known boundary: 0.827→0.764 d2→d4) | depth wall survives the last untried repair — name it honestly |
| P4 | Learns LM without global CE (top-1 > 15% vs unigram 9.4%, leak-controlled) | per-layer targets don't transfer to transformer at probe scale |

**Leak-control discipline (rev-17 lesson):** FF-style readouts are leak-prone
two ways — never append the true label at eval; never report 1/acc as "ppl."
Argmax over per-candidate goodness, top-1 accuracy primary, CE only with a
stated posterior calibration.

### Then: compose with TransformerGeometry (SP4)

Per-layer targets on a transformer with **zero global signals** — absolute
locality. This is the Claim A repair made real. Then **re-run F5's
resource-accounting** on it: if per-layer peak < bp holds, **F5's pinned miss
flips into the ~10× memory headline** (this absorbs SP1 + SP5). Sweep depth
(4/8/16) — never quote depth-2 cells (input layer's own graph ≈ bp's whole
graph at depth 2).

**Lands as:** `local_contrastive` library primitive + a D-table demo + F5
re-pin. The artifact that justifies the whole physical-advantage thesis.

---

## Workstream W3 — Closed-Form ψ Adaptation (the novel capability)

**Anchor:** D22 (ψ-only impossible — no ψ law consumes a loss term; ‖Δθ‖=0
is bitwise-assertable; fine-tune 0.984 is the bar) + B1 (closed-form ridge
solver — settled activities, no gradients, one shot, transport-free,
snapshot-captured).

**The clever speculation:** B1 proved feedback matrices can be *computed*,
not trained. Generalize: **a ψ set in closed form from a handful of examples
— "LoRA without gradients."** Instant, forget-free adaptation that backprop
structurally cannot do (backprop must edit θ, which forgets).

### Build spec

1. A ψ-law receiving **NUDGED-phase** settled activity (target-conditioned
   Hebbian outer product, or closed-form ridge on settled acts — B1's pattern).
2. **Pipeline contract change:** `run_train_step` steps ψ on
   `credit.phases[0]` (always FREE at HEAD). Needs a `psi_phase:
   Literal["free","nudged"]` knob or a NUDGED-first credit. **This is a
   contract change → needs its own audit** (nudged-phase ψ modulation
   interacts with contrastive credit semantics).
3. Reuse the D22 probe as the instrument (`_probe`/`_probe_modulated`/
   `_theta_sha256` + the A→B switching-task helper). Don't re-derive.

### Pre-registered predictions

| # | Prediction | Falsified → |
|---|---|---|
| P1 | ψ-only acquires Task B with θ bitwise frozen (SHA-verified ‖Δθ‖=0) | closed-form ψ still can't carry a task signal — boundary mapped |
| P2 | Acquisition speed beats θ-fine-tune on *steps-to-criterion* (fine-tune 0.984 is the accuracy bar) | ψ adaptation slower than fine-tune — honest boundary |
| P3 | Task-A retention ≈ null (zero catastrophic forgetting by construction) | retention cost exists — measure it |

**Lands as:** D22-style demo with exact ‖Δθ‖=0 assert + fine-tune comparison.
Even a bounded result is a finding — the exact boundary AND the exact lever
are already named.

---

## Workstream W4 — Depth Frontier (cheap CPU interstitial)

**Anchor:** D14 (depth 20 works under jpc regime; OrthoAdam 0.92), SGD-alone
0.528, μPC×OrthoAdam substitution (gap narrows 0.58→0.07).

- **Depth sweep** {20, 32, 50, 100} × {mupc+residual+OrthoAdam,
  mupc+jpc-Adam, jpc+OrthoAdam} on MNIST-quick (CPU).
  **Pre-register:** "the recipe reaches depth ≥ 32 at test ≥ 0.8."
- **Zero-shot LR transfer** (the clever bit): tune at depth 8, run at
  depth 20/50 *unchanged*. If it holds → **"tune once, run anywhere"** — a
  genuinely new capability and a strong μPC validation.

**Cheap-iteration note:** digits is ~28% faster than mnist per step (measured);
CPU beats CUDA for MLPs (device policy). Use NS-OrthoAdam for the deep sweeps
(~40% cheaper than SVD).

**Lands as:** S1 pinned sweep + a zero-shot-transfer cell. Interleave with
W2's longer builds (CPU, no GPU contention).

---

## §6 — Branch Logic (the plan is versatile, not fragile)

The whole plan keys off W0's verdict. Pre-commit so there's no post-hoc
rationalizing:

- **Bombshell verified real** (healthy baseline, ff_hybrid still ≫ bp):
  accelerate SP6 + W2; run matched-token scale curves; promote the 5× headline.
- **Baseline sick, ff_hybrid healthy** (the expected branch): fix the
  baseline, recompute the band honestly, promote ff_hybrid at parity/small-gap
  as "hybrid local credit matches backprop." Continue SP6 → W2 → W3. *Nothing
  lost; the win is real, just honestly sized.*
- **ff_hybrid also sick** (eval/accounting defect): fall back to the 2.5-min
  anchor (~15% behind, still the best local rule), name the mechanism, pivot
  hard to W2 + W4 where the genuinely novel capabilities live.
- **W2 P3 fails** (EMA rung doesn't lift the depth wall): the depth wall
  survives the last untried repair in this class — name it honestly, keep the
  O(1)-memory + LM-learning result (P1/P2/P4), and the boundary becomes the
  finding.

**Robustness:** W2/W3/W4 do not depend on D17. The bombshell can die without
killing the plan. Every branch still ends with a pinned artifact and an
honest number.

---

## §7 — Carried Queue Disposition (none silently dropped)

| Carried item | Disposition in TODO13b |
|---|---|
| D17 seeds 1–2 | **W0 step 3** (gated behind steps 0–2 + per-batch approval) |
| C1 contrastive-LM parity | **Mechanical fallback only**, iff W0 verdict lands >25% |
| Registered-scale P-axis campaign | **Tier-2** — parked until Tier-1 lands |
| Reward-modulated STDP (F2 closer) | **Tier-2** — not the frontier |
| TransformerGeometry × ePC settle extension | **Tier-2** prereq for transformer PC cells |
| P2 untried jpc cells | **Tier-2** — only if contrastive path stalls |
| Demo API roadmap items 3–8 | **Deferred** (research first, user directive) |
| Bias training option (`train_biases`) | as-touch (contract honesty, H2 delta 0.000) |
| learned-B `feedback_lr` 0.5 → 0.05 | as-touch (0.5 measured insane) |
| Diverged-arm sentinel hygiene | as-touch (evidence hygiene) |
| Z3 flagship | **Parked** — its minimal kernel is W3; rides CP-6 findings |

---

## §8 — Standing Directives (carried, binding)

- `benchmark_results/` untracked, gitignored — never re-add. README never
  edited; evidence lives in RESULTS.md + the gallery.
- Probe-first; pre-register predictions in the probe docstring; multi-seed
  before quoting; matched-step/lr controls before mechanism claims;
  capacity-matching on all comparisons; walltime printed never recorded.
- **Runs budget:** no multi-hour/unattended runs; per-arm 10–20 min only with
  explicit per-batch approval; smoke-verify every registered arm at ~1-min first.
- **step_semantics discipline:** per-element-displacement updates
  (unit_rms/mean_norm/muon/ortho/adam family) get lrs on their own axis;
  `validate()` warns >0.05; never sweep a borrowed euclid grid.
- **Baseline caveats:** all bp baselines are weights-only (H2, delta 0.000)
  and (1−β)-scaled target-blended CE (H8, cos ≥0.99); β=1.0 forbidden with
  autograd credit.
- Canonical locality wording, scope-honest per the Claim A audit: "forward-
  local credit with a single readout supervision term — no backward sweep
  through the hidden layers" — holds only for requires_autograd=False credits
  and the W2 per-layer class. Never "fully local."
- **Probe hygiene:** seed before every loader draw (D8 trap, confirmed 3×).
- **Gallery pinning:** fixed-step arms only; walltime printed never recorded;
  manifest re-pins additive-only; drift-immunity = 2 consecutive green runs.
- **Gates:** fast tier ~205 s (default); slow tier `pytest -m slow -k demo`
  (D14+D15+D16, ~14 min); invoke as `uv run python -m pytest`.
- R11.5.5a + TODO12b defect-hunt posture apply to **optimistic** verdicts too.

### Operational details (don't re-derive)

- **LM harness:** `scripts/probes/lm_comparison.py` — both families through
  one pipeline, capacity-matched (ratio asserted + printed), fixed shared val
  windows, JSON → `benchmark_results/lm_comparison.json`.
- **Registered shapes:** transformer d320/6L/C128 7.41M vs mlp w816×7L/C64
  7.43M (ratio 1.003). Smoke: 156,544 vs 149,889.
- **LR table (smoke-tuned):** bp/adam 1e-3; bp/muon 0.01; bp/ortho
  ortho_lr 1e-3; ff/muon 0.01; pepita 5e-4 transformer / 0.002 MLP.
  Wildcard-LR ordering: specific patterns before wildcards.
- **Registered-scale cells:** transformer {bp/adam, bp/muon, ff_hybrid/muon,
  pepita/muon}; mlp {bp/adam, ff_hybrid/muon, epc_thermo/muon, ff/muon,
  ff/ortho_adam, pepita/muon}.
- **Walltime asymmetry is structural:** transformer arms see ~9× more tokens/s
  than mlp arms (dense per-position CE vs single target) — comparisons are
  wall-clock-budgeted by directive; the asymmetry is recorded, not hidden.

---

## §9 — The Session Spine

| Session | Spine | Ends in |
|---|---|---|
| **1** | W0 steps 0–1 (free) + W1 SP6 two cells (~5 min) | Bombshell regime verdict + OrthoAdam-on-LM number |
| **2** | W2 scaffold `local_contrastive`, train depth-2, verify O(1) peak | P1+P2 probe verdicts; SP2 interstitial if slack |
| **3** | W2 add EMA rung, test depth 4 (P3) | The class's depth wall survives or breaks |
| **4** | W2 compose with TransformerGeometry (P4) + re-run F5 | F5 ratchets flip → memory headline |
| **5** | W3 closed-form ψ (P1–P3) | ψ-only adaptation demo or boundary |
| **6** | W0 step 3 (gated, only if baseline verified) → D17 promotion | The bombshell, verified and pinned |
| **interstitial** | W4 depth sweep + zero-shot transfer (CPU, any session) | S1 pinned |

Every session ends in a pinned demo, a killed speculation, or a promoted probe.
Speculative plays (SP3 inference-time settling) run only as slack interstitials
— one cheap probe, one pre-registered prediction, promote or kill.

---

## §10 — Completion Criteria for TODO13b

> **Status (2026-09-07, post Session 6):** 1 ✅ (two-sided verdict,
> confound resolved), 2 ✅ (SP6 measured; falsified at this budget —
> muon keeps the arm), 4 ✅ (ψ closed-form boundary mapped — the
> allowed branch), 5 ✅ (depth 32 @ 0.867 + zero-shot LR transfer
> confirmed), 6 ✅ (SP2 promoted, geometry-boundary revised).
> **3: BUILT and adjudicated** — the transformer composition exists,
> the O(1)-memory half holds (P4c PASS), the LM-learning half is
> FALSIFIED at probe scale (mechanism, not budget; defect trail +
> retry levers recorded, the optimizer lever the most promising).
> TODO13b's completion criteria are otherwise met; the retry is a
> successor plan's first item, not a TODO13b item.

1. **Bombshell verdict rendered** — verified against a healthy baseline,
   matched-step, multi-seed, pinned (or killed with the mechanism named).
   *(Expected, per §0: sick baseline, honest re-promotion.)*
2. **OrthoAdam on LM measured** — SP6 cells in the coverage map; the
   bombshell arm upgraded if warranted.
3. **`local_contrastive` landed** — library primitive, O(1)-peak-memory,
   learns LM without global CE; F5's ratchets flipped or the boundary named.
4. **ψ closed-form adaptation demonstrated** — exact ‖Δθ‖=0, Task B
   acquisition vs fine-tune, A-retention — or the closed-form boundary mapped.
5. **Depth frontier + zero-shot transfer pinned.**
6. **At least one speculative play promoted** (SP2 most likely) to a D/F-table
   entry.
7. **No audit-only sessions** — every session shipped something visible.

**The bar (carried):** a result someone would cross a room to see. The
instrument is honest, the winners are confirmed, and they're sitting
uncomposed. TODO13b composes them — and checks the biggest number's
denominator before building anything on top of it.

---

## Progress Log

### 2026-09-07 — Session 1: W0 steps 0–1 ✅ + W1 SP6 ✅ (one cell falsified, one underpowered)

**W0 steps 0–1 — reconciliation complete, free (read `d17_seed0.json`).**
Verdict recorded in the `lm_comparison.py` docstring (D17 REGIME
RECONCILIATION section). Findings:

- **The 5.5× bombshell is DEAD as endpoint-vs-endpoint.** bp/adam is
  healthy but **overtrained**: train_loss descends monotonically
  (1.74→0.30) while val_ppl rises (7.0→27.55) — memorization of the
  1.0M-char Shakespeare train split (62 epochs seen vs ff_hybrid's 9)
  under the matched-walltime protocol. NOT lr collapse; NOT the
  mixed-ctx val defect (transformer val windows were cut at
  max(ctx)=128 = the transformer's own ctx — provenance moot for this
  arm).
- **Matched-token reconciliation:** at bp/adam's ~9–11M-token mark
  (t≈130–160 s) val_ppl = **4.56–4.63** — better than ff_hybrid's
  best-ever 4.83. Per token, backprop wins. Per walltime:
  (5.05−4.56)/4.56 = **10.7% → parity band (<15%)**.
- **Throughput accounting:** both arms draw 4096 tokens/step; the
  7× step gap is exactly the chars/s ratio (69.2k vs 10.0k) —
  ff_hybrid's per-step cost is 6.9× bp/adam's (Claim A overhead:
  fwd + goodness + hybrid autograd). Structural, recorded.
- **Binding honest-denominator rule** (in docstring): matched-token
  budgets (`--tokens` knob added to the harness) or bp best-val
  alongside endpoint. Endpoint-vs-endpoint across the 6.9× gap
  forbidden in quoted results. **Recomputed band: parity.** Wording:
  "forward-local hybrid credit matches backprop on a transformer LM
  at matched walltime, using ~7× fewer token-passes."
- Harness changes: `--tokens` matched-token budget; SP6 cells +
  LR entries wired (`transformer/ff_hybrid/ortho_adam`,
  `mlp/epc_thermo/ortho_adam`, ortho_lr 1e-3 on OrthoAdam's own
  axis); ruff clean. Results: `benchmark_results/sp6_ortho_adam_lm.json`.

**W1 SP6 cell 1 — `transformer/ff_hybrid/ortho_adam`, 2.5-min
registered shape: val_ppl 6.37.** Pre-registered prediction
"OrthoAdam ≥ Muon (5.05-equivalent or better)" **FALSIFIED at this
budget** — ff_hybrid/muon was at ~5.7 by t=160 s on the d17 curve.
The bombshell arm is NOT upgraded; W0 step 3 runs the original
muon arm. Caveat (honest, not an excuse): Adam-family second-moment
warmup may favor longer budgets — a 15-min curve could still overtake;
only pursue as slack, never quote the 2.5-min cell as parity.

**W1 SP6 cell 2 — `mlp/epc_thermo/ortho_adam`: UNDERPOWERED, no
signal.** 16 steps in 2.5 min (3 chars/s — EP settle at w816×7
registered shape is brutally slow; ctx-64 one-hot input dominates).
Landed at chance (65.0). Also: smoke-scale (w64) epc_thermo explodes
under BOTH Muon and OrthoAdam — a known width-fragility artifact
(`p4_width_fragility.py`: "epc_thermo w64, P4: std → 2028"), not a
wiring defect. **Deferred until the epc_thermo LM throughput question
is resolved (below).**

**New improvement opportunities (surfaced this session):**

1. **epc_thermo registered-LM provenance audit (cheap, defect-hunt
   posture applies):** RESULTS.md quotes "epc_thermo×Muon ~21 ppl at
   w816×7, 1 min" — but the harness only turns 16 steps/2.5 min at
   that shape (3 chars/s). 21 ppl in ~6 steps is implausible → the
   ~21 figure likely came from a different probe shape/batch/step
   budget. Audit before C1's 21-vs-9.9 gap is ever quoted.
2. **Seed-1 OOM root cause:** prior `d17_seed1.log` died of CUDA OOM
   from concurrent processes contending for the 9.6 GB GPU. Seed runs
   must be serial, one process at a time.
3. **OrthoAdam warmup question** (slack): if Adam-family warmup is
   real on LM, OrthoAdam cells should be compared at matched *steps*,
   not matched walltime — the same honest-denominator rule as W0.

### 2026-09-07 — Session 1b: three quick locks (no long runs)

**Lock 1 — SP2 PROMOTED (`scripts/probes/sp2_ortho_weak_credit.py`,
seeds 0–2, ~25 s CPU).** Weak credit × OrthoAdam on MNIST-quick
(1 epoch, 150 batches, 784-64-64-10):

| cell | test acc |
|---|---|
| ff × euclid 0.2 | 0.825 |
| **ff × ortho 1e-3** | **0.918** |
| pepita × euclid 0.2 | 0.101 |
| pepita × ortho 1e-3 | 0.239 |
| bp × adam 1e-3 | 0.892 |
| bp × ortho 1e-3 | 0.913 |

Pre-registered P1 ✅ (ortho rescues ff: +0.093), P2 ✅ directionally
(pepita 0.10→0.24, still weak), **P3 ✅ decisively: ff/ortho ÷
bp/ortho = 1.01** — under the right optimizer, weak ff credit not only
matches backprop, it *beats* it (0.918 vs 0.892 bp/adam). Finding to
promote to a D-table entry: **"the optimizer is doing the learning;
credit only needs a good-enough direction"** — with the boundary that
pepita's rescue is partial (its credit direction is too weak for
OrthoAdam to fully repair). Scope: weights-only bp baseline (H2),
tiny-net regime.

**Lock 2 — SP6 matched-steps (free, from d17 curve + sp6 json).**
OrthoAdam's 2.5-min deficit is NOT Adam warmup: at matched ~350 steps,
muon 5.72–5.81 vs ortho 6.37, and the ortho curve lags muon uniformly
at every t (10.52 vs ~8.3 @ 60 s). SP6 falsification now holds under
all three accountings (walltime, tokens, steps). epc_thermo at
registered shape is frozen, not diverged (train 4.07 ≈ ln 65; 16
steps).

**Lock 3 — matched-token direct measurement (2.5 min GPU,
`--tokens 1000000`).** Both transformer arms at EXACTLY 245 steps /
1,003,520 tokens: **ff_hybrid/muon 6.36 vs bp/adam 8.28** — the local
arm is ~23% better per token at the 1M budget. This confirms the
Session-1 reconciliation by direct measurement and sharpens the honest
picture: **there is a cross-over budget** — ff_hybrid wins per-token
at ≤1M tokens; bp/adam overtakes by ~10M tokens (4.56 vs ff's best
4.83). Next D17 protocol decision: quote both sides of the cross-over
(matched-token at ~1M AND ~11M), never walltime endpoints.

**New opportunities from 1b:**
- D17 step-3 seeds (still user-gated) should now run under the
  matched-token protocol: `--tokens 1000000` (~2.5 min/arm, not
  90 min!) — seeds 1–2 become CHEAP. The 15-min matched-walltime arms
  are only needed for the >10M-token side of the cross-over.
- SP2 multi-geometry: does ff×OrthoAdam ≥ bp hold on attention/lattice
  geometries (the D16 map)? Cheap cells, high value.
- OrthoAdam rescue boundary: pepita partially rescued — is the
  failure in the credit direction or the magnitude normalization?
  Ties directly into W2's EMA rung.

### 2026-09-07 — Session 1c: seeds 1–2 locked + SP2 geometry boundary

**W0 step 3 UNLOCKED & DONE at matched tokens (`--tokens 1000000`,
~2.5 min/arm, serial — seeds 1 and 2).** Three-seed means at exactly
245 steps / 1,003,520 tokens:

| arm | seed 0 | seed 1 | seed 2 | mean |
|---|---|---|---|---|
| transformer/ff_hybrid/muon | 6.36 | 6.40 | 6.54 | **6.43** |
| transformer/bp/adam | 8.28 | 8.19 | 8.30 | 8.26 |

**ff_hybrid is 22% better per token at the 1M budget, multi-seed.**
Artifacts: `d17_seed{1,2}_mt1m.json`. The D17 verdict is now fully
honest and two-sided: per-token early-regime ff_hybrid ≫ bp; per-token
late-regime (≥10M) bp overtakes (4.56 vs 4.83 best); matched-walltime
= parity band. Any D17 quote must state which side of the cross-over
it's on. GPU-hygiene reminder re-confirmed: an aborted run survives as
a niced zombie and OOMs the next run — check `nvidia-smi
--query-compute-apps` before launching, kill strays first.

**SP2 geometry boundary (`sp2_ortho_weak_credit.py`, seeds 0–2).**
ff×OrthoAdam ÷ bp×OrthoAdam:

| geometry | ff/ortho | bp/ortho | ratio | verdict |
|---|---|---|---|---|
| mlp | 0.918 | 0.913 | **1.01** | parity — optimizer does the learning |
| lattice3d | 0.903 | 0.907 | **1.00** | parity |
| attention | 0.799 | 0.909 | **0.88** | bp clearly ahead — P3 falsified here |

Promotable finding, boundary named: **"the optimizer does the
learning" holds on mlp and lattice (credit needs only a good-enough
direction), fails on attention.** Candidate mechanism for the
attention gap: ff's scalar goodness signal must route through
per-head attention structure — direction insufficiency, not step
size. Cheap follow-up if pursued: ff_hybrid (readout-error variant)
× ortho on attention — is the gap a credit-magnitude issue the EMA
rung could close? Ties into W2.

**Remaining W0 step-3 work:** the ≥10M-token side of the cross-over
(ff_hybrid needs ~7 min/arm per 4M tokens — the only long-budget item
left) and any bp/muon cells. Not urgent: the seed-0 d17 curve already
brackets the cross-over; run only if a quoted headline needs it.

**2026-09-07 — LR-sensitivity audit of the overtake (user question:
"is the late-regime bp overtake just suboptimal lr?").** Answer: NO,
lr is exonerated on both arms, at two budgets:

- ff_hybrid/muon @1M tok: lr {0.01, 0.02, 0.04} → {6.42, 6.36, 6.36};
  @2M tok: 0.02 and 0.04 **bit-identical** (best 5.57, final 5.73).
  Plateau, no lr×budget interaction.
- bp/adam @1M tok: {3e-4, 3e-3} both 8.28; @3M tok: 1e-3 → 5.37,
  3e-3 → 5.33 (0.7%). Robust across a 10× range.

**Sharpened crossover (per-token, direct runs, seed 0):** ff ahead at
2M (5.57–5.73 vs bp ≈5.8–6.0), parity at 3M (bp 5.37 vs ff ≈5.4–5.5),
bp ahead at 7–11M (≈4.6–4.7 vs ff best 4.83). Crossover ≈ **3M tokens
(~700 steps)** — earlier than the endpoint-based estimate. Both sides
of the crossover are real: ff/muon's advantage is early-regime
(curvature), bp/adam's is late-regime (per-token efficiency). Open
axis (not probed): muon-vs-other-optimizer for ff_hybrid at ≥3M —
ff's late deficit could be the Muon axis rather than the credit; a
ff_hybrid/ortho_adam or adam cell at 3M+ tokens (~7 min) would
separate them if ever needed for a headline.

### 2026-09-07 — Session 1d: SP2 attention flip + W2-P3 EMA rung CONFIRMED

**SP2 attention verdict REVISED — the "geometry boundary" was an
under-tuned rung** (the user's hyperparameter suspicion, second hit):

| attention cell | ortho_lr 1e-3 | ortho_lr 3e-3 |
|---|---|---|
| ff/ortho | 0.799 | **0.860** |
| bp/ortho | 0.909 | 0.909 (rung-insensitive) |
| ratio | 0.88 | **0.95 — P3 passes** |

At the matched 3e-3 rung, ff×OrthoAdam ≈ bp×OrthoAdam on attention
too. **Revised SP2 finding: "the optimizer does the learning" holds on
mlp, lattice, AND attention at the properly-tuned rung** — bp is
rung-insensitive, weak credit is rung-sensitive (needs the bigger
step). Also: pepita/ortho 3e-3 = 0.308 (vs 0.239 @ 1e-3) — its rescue
is magnitude-limited, consistent with the same mechanism. **Wiring
defect filed:** ff_hybrid × attention throws a pseudo-gradient shape
bug in OrthoAdam apply (`update.py:697`, grad 32 vs moments 784) —
cell unmeasurable until fixed (defect-hunt queue).

**W2-P3 EMA RUNG CONFIRMED (`scripts/probes/w2_ema_rung.py`,
pre-registered, ~70 s total).** Scalar per-layer EMA of mean(gw²) as
the credit normalizer, 150-step MNIST regime, seeds 0–2:

| depth | instantaneous (unit-RMS, all lrs 1e-3–0.1) | **EMA lr 0.3** | raw ref |
|---|---|---|---|
| 2 | ~0.52 | **0.824** | 0.827 |
| 4 | ~0.19–0.20 (collapse) | **0.757** | 0.764 |
| 8 | ~0.10–0.16 (chance) | **0.512** | — |

- d4 lifted above the collapse floor (0.757 vs 0.19) and to raw parity
  — **P3 ✅**; the TODO13b §6 "wall survives" branch does NOT trigger.
- **Depth 8 trains for the first time in this class** (0.512 vs
  chance) — the wall is now a graceful slope (0.824→0.757→0.512), not
  a wall. Open: longer budgets/matrix-EMA at d8, and the EMA rung only
  pays off at lr 0.1–0.3 (at ≤0.01 normalized rungs are just slow).
- Harness lessons (in probe docstring): wrong-label negatives only
  (1−pos hybrid negative kills the contrast — whole grid at chance);
  bias-correct the EMA or the t=1 step explodes.
- Scope: standalone probe (b4 pattern), NOT library wiring — the W2
  build proper (registry wiring, TransformerGeometry composition, P4)
  still ahead. The probe de-risks the build: the normalization math is
  now known-good.

### 2026-09-07 — Session 2: W2 `local_contrastive` WIRED + in-library parity at d2

**The library primitive is LANDED** (`LocalContrastiveCredit` in
`computronium/ontology/credit.py`, full registry wiring: config
classmethod `CreditAssignmentConfig.local_contrastive()`,
`_credit_from_config` in factory.py + joint.py, campaign
`_CREDIT_FACTORIES`, ontology + root exports, EMA snapshot
`get_state`/`load_state`). ruff + pyright clean in new code; wiring
lockstep + root-export tests pass; targeted credit/compose/checkpoint
suite 123 passed.

**Two structural discoveries locked en route (both cheap, both
load-bearing for the design):**

1. **Hidden FREE/NUDGED contrast is structurally ZERO under
   instantaneous settle** (measured: hidden max|free−nudged| = 0.0
   exactly — same weights, same input, deterministic forward; only the
   output nudge differs). The library's existing "ff" credit therefore
   trains hidden layers ONLY through the readout CE's shared-graph
   backward sweep (the ff_hybrid mechanism — never O(1)). The honest
   O(1) class must own its good/bad streams: **the contrast lives in
   the input label channel, not the phases.** Design: phases =
   (FREE,); contract = label-augmented inputs (last `label_dim`
   features = one-hot target; b4 pattern); the credit builds the
   rolled-label negative itself and Hinton-normalizes BOTH streams
   internally.
2. **The b4 probe's operating point is a two-scale recipe** (hidden:
   EMA-normalized goodness × 0.3; readout: RAW CE × 0.1 — probe
   bisection showed EMA-normalized or goodness-space readout updates
   collapse to ~0.09). A single update-axis lr cannot serve both: the
   `readout_scale` config knob folds the ratio in.

**In-library results (150-step MNIST, seeds 0–2, euclid grad_clip=0):**

| depth | library local_contrastive | probe reference |
|---|---|---|
| d2 | **0.837** (lr 0.03, raw readout) | 0.824 ✅ parity |
| d4 | 0.654 (lr 0.05, ro_scale 1/3) | 0.757 — gap open |
| d8 | frozen (chance) | 0.512 — gap open |

d2 parity proves the wiring + recompute + EMA math are correct
end-to-end through the real pipeline. The d4/d8 gap traces to a
**~4%/step label-channel gradient discrepancy vs the b4 probe**
(diagnostics captured: step-0 grads bit-identical; diff concentrated
entirely in label cols 784–793, growing ~4%/step; library
destabilizes at lr ≥ 0.1 where the probe is stable at 0.3). **Queued
defect-hunt item** with the full trail — do NOT wire the EMA rung into
the LM/transformer composition (W2 P4) until this closes.

**Consumer-side gotchas (locked, do not re-derive):** euclid's default
grad_clip=1.0 crushes EMA-normalized grads ~1000× (global-norm clip vs
unit-RMS per-layer) — always `grad_clip=0` for these cells; feed RAW
data + one-hot label (pre-normalized input scales the label channel by
1/‖raw‖ and shifts the contrast); eval must use the same Hinton-normalized
stream the credit trains on (settle with `gain_control="unit_rms"` +
normalized input).

**Updated spine:** next = close the label-channel discrepancy (it
gates P3-in-library at depth and all of P4), then W2 P4
(TransformerGeometry composition) + F5 re-pin.

### 2026-09-07 — Session 3: W2 defect CLOSED — three stacked root causes; `local_contrastive` is now the class's depth frontier

**The discrepancy chase resolved into three independent findings, each
with its own fix (all in-library, `uv run pytest` targeted suite 192
passed + wiring lockstep green):**

1. **EMA recipe drift** (`credit.py::_ema_normalize`): the wired version
   was scalar (mean over the tensor), ones-warm-start, uncorrected, with
   eps OUTSIDE the sqrt — at t=1 the step was raw gw, and outside-eps
   re-amplified satisfied-gate ~0 gradients to full size. Fixed to
   **element-wise, zeros-warm-start, bias-corrected, eps-inside-sqrt** —
   verified bit-identical to the probe formula on shared weights.
2. **Ordering semantics (the load-bearing one):** b4/w2 probes update
   each hidden layer INSIDE the batch loop, so layer i+1's input stream
   is formed against layer i's post-update weights. The library computed
   all grads against pre-step weights (Jacobi). Measured: Jacobi
   collapses the recipe (probe d4 0.76→0.27, d8 0.51→0.14). Landed as
   **`sequential_lr`** on `CreditAssignmentConfig.local_contrastive()` —
   the credit keeps a detached per-step view of updated layers for
   recompute; must equal the update step_size; 0 = Jacobi.
3. **Readout bias**: probe freezes hidden biases but trains the readout
   bias via CE; the pipeline's `apply_pseudo_gradients` choke point only
   paired 2-D weights. Landed: optional **`compute_bias_pseudo_gradients`**
   hook on the credit (duck-typed in `run_train_step`), threaded through
   every `ParameterUpdate.step` as `bias_grads: dict[str, Tensor] | None`
   (Muon/spectral apply euclid fallback for ndim<2 — matrix rules must
   not orthogonalize vectors). Absent → frozen (all other credits
   unchanged; H2 weights-only bp baseline untouched).

**THE RED HERRING, named honestly: the old "probe references" (d2
0.824 / d4 0.757 / d8 0.512 @ EMA lr 0.3) are NOT reproducible from
committed code** — `w2_ema_rung.train_acc` at lr 0.3 gives 0.507
(beta 0.99) / 0.542 (0.999). Session-2's "in-library d4 0.654 /
d8 frozen" numbers were measured against a phantom. The reproducible
frontier is **b4's RAW recipe** (raw grads, lr 0.5, sequential):
d2 0.827 / d4 0.764.

**Two-regime verdict (`scripts/probes/w2_library_parity.py`, real
pipeline, seeds 0–2, 150-step MNIST-quick):**

| arm | d2 | d4 | d8 |
|---|---|---|---|
| **raw (ema_beta=0) lr 0.5 sequential** | **0.853** | **0.789** | 0.106 (chance) |
| EMA 0.99 lr 0.3 sequential | 0.751 | 0.349 | **0.220** |

- Raw+sequential BEATS the b4 frontier at d2/d4 (0.853/0.789 vs
  0.827/0.764) — the library is now the class's best shallow-depth
  instrument. **P3-in-library ✅ in its true form**: the EMA rung is the
  depth-8 repair (0.220 vs raw chance), not a d2/d4 parity tool.
- Consumer contract locked: RAW data + one-hot label (pre-normalized
  input double-normalizes and perturbs label cols); euclid
  grad_clip=0, momentum=0; `sequential_lr` = update step_size;
  `readout_scale` folds the readout lr into the single axis
  (raw lr 0.5 → ro_scale 0.2; EMA lr 0.3 → 1/3).
- Pipeline note: the composed pipeline is far less init-sensitive than
  the probe harness (0.75-stable vs 0.52–0.82 init lottery) — the
  pipeline is the more trustworthy instrument; probe-only numbers at
  this depth need an init-robustness caveat.

**New improvement opportunities (surfaced this session):**
1. **d8 headroom:** EMA 0.220 is above chance but far from useful —
   longer budgets, matrix-shaped EMA, and beta/lr co-sweep at d8 are
   the open axis (the honest next step for the depth-wall story).
2. **Sequential×Adam interaction:** `sequential_lr` assumes plain SGD;
   under OrthoAdam the view update should use the optimizer's actual
   per-layer displacement — unmodeled. Flag before any OrthoAdam×
   local_contrastive cell.
3. **D17 optimizer-confound cells (user-directed, elevated priority):**
   the D17 early-regime win may be Muon-vs-Adam, not locality — SP2's
   "optimizer does the learning" finding makes this live. Three cheap
   cells at `--tokens 1000000` (~2.5 min/arm): ff_hybrid/adam vs
   bp/adam, ff_hybrid/muon vs bp/muon, ff_hybrid/muon vs
   ff_hybrid/adam. Run before quoting any D17 headline.
4. **OrthoAdam matched-steps LM cell** (W1 gate): one cell resolves the
   warmup question before any further W1 expansion.

### 2026-09-07 — Session 4: D17 confound RESOLVED — the 22% is ~half optimizer; credit share is 12% under a shared Muon

**The user's SP2-vs-D17 tension, settled by the three pre-registered
cells at the matched-token budget (transformer 7.41M, `--tokens
1000000` = 245 steps, seeds 0–2; `benchmark_results/
d17_confound_summary.md`, per-seed json `d17_confound_seed2.json`):**

| arm (@1M tokens) | s0 | s1 | s2 | mean |
|---|---|---|---|---|
| ff_hybrid/muon | 6.36 | 6.40 | 6.54 | **6.43** |
| bp/muon *(new)* | 7.21 | 7.40 | 7.26 | **7.29** |
| bp/adam | 8.28 | 8.19 | 8.30 | **8.26** |
| ff_hybrid/adam *(new)* | 8.68 | 8.58 | 8.54 | **8.60** |

Full 2×2 factorial decomposition:

- **Credit effect @ Muon (the fair cell): ff_hybrid 11.8% better.**
- Credit effect @ Adam: ff_hybrid 4.1% *worse* — under Adam the local
  credit does NOT beat backprop on LM.
- Optimizer effect @ bp: Muon 11.7% better. Optimizer effect @
  ff_hybrid: Muon 25.2% better — **Muon rescues the local credit
  roughly twice as much as it rescues bp** (synergistic pairing, the
  mechanistically interesting residue).

**Verdict:** the D17 "22% better per token" (vs bp/adam) decomposes
into ≈ half optimizer (Muon-vs-Adam) + ≈ half credit (12% under shared
Muon). SP2 and D17 are reconciled: *the optimizer does much of the
learning, and under the right optimizer the local credit still adds a
real ~12% per-token early-regime win — but quoting the 22% figure as a
locality result is forbidden.* **Binding honest wording:** "under a
shared Muon update, the forward-local hybrid credit beats backprop by
~12% per token at the 1M-token budget; against bp/adam the gap is 22%,
but roughly half of that is the optimizer, not the credit." Also note
the asymmetric optimizer sensitivity mirrors SP2's rung-sensitivity
finding: weak/local credit is optimizer-sensitive, bp is not.

Wiring: `ff_hybrid/adam` cell + LR entry (`*/ff_hybrid/adam: 1e-3`,
smoke-plateaued: 7.34 @1e-3 vs 7.57 @3e-3) in `lm_comparison.py`;
CELLS table row added.

**New opportunities:**
1. The synergy cell (Muon × local credit) is now the mechanistic
   question: Muon's orthogonalized update may be repairing the local
   credit's direction noise — same shape as SP2's "optimizer does the
   learning" and W2's EMA story. A `local_contrastive × muon` LM cell
   is the natural follow-on (W2 P4's optimizer axis).
2. Late-regime confirmation: does the 12% credit share persist at 3M
   (the crossover) under shared Muon? One `--tokens 3000000` pair
   (~15 min) closes it if a headline ever needs it.

### 2026-09-07 — Session 4b: d8 headroom probe (slack, ~1 min CPU)

d8 EMA with 3× budget (450 steps, seeds 0–2): β=0.99 flat (0.229),
**β=0.999 → 0.284** (seeds 0.399/0.241/0.211 — high variance, one seed
at 0.40). The d8 frontier is budget-starved, not walled: longer
training + slower EMA both trend up. Proper d8 campaign = budget×β
grid with ≥3 seeds — Tier-2, not urgent.

### 2026-09-07 — Session 6: W2 P4 transformer composition BUILT; P4 FALSIFIED (mechanism, not budget); P4c memory ratchet PASS

**The build landed** (`LocalContrastiveCredit` tf path,
`computronium/ontology/credit.py`; probe
`scripts/probes/w2_p4_transformer_local.py`): per-layer targets on
`TransformerGeometry` with zero global signals — credit-owned FIXED
random label projection injected at the embedding output (pos = true
next tokens, neg = batch-rolled); every linear (embed, per-block
in_proj/out_proj/ffn1/ffn2) descends a softplus-gated goodness
contrast on its own output via no-grad prefix recompute (O(1) peak,
sequential_lr step-views by param name); head trains local
per-position CE on the LABEL-FREE stream (train/eval distribution
match — never the true label at eval). Full pipeline dispatch via
`_tf_gradient_if_applicable`; head bias-free → bias hook no-ops.
Targeted credit/compose/checkpoint suite + wiring locks green; ruff
now BELOW baseline on credit.py (7 legacy findings, none new).

**Results (d128/L2/H4, ctx 32, V 65, seeds 0–2; ~35 min CPU):**

| arm | top-1 | val CE |
|---|---|---|
| unigram anchor | 0.153 | ~3.4 |
| local_contrastive 600 steps | 0.129–0.146 | 3.40–3.43 |
| **bp reference 600 steps (same cell)** | **0.152** | **3.329** |
| **bp reference 3000 steps** | **0.219** | **2.936** |
| local_contrastive 3000 steps | 0.109 | 3.686 (drifting down) |
| shuffled-label control 600 | 0.149 | 3.354 |
| **P4c memory: local peak 0 KiB vs bp 256 KiB** | — | **PASS** |

- **Unigram anchor correction:** this vocab's unigram top-1 is 0.153,
  not the 9.4% quoted in the plan (different probe's vocab). Bar
  re-anchored; all comparisons above use 0.153.
- **P4 FALSIFIED, mechanism not budget:** at 600 steps NOTHING
  (including bp) is out of the marginal regime — parity. At 3000
  steps bp learns context (0.219) while local_contrastive drifts
  DOWN (0.109, CE rising monotonically) — the goodness dynamics
  actively destroy readout-useful features at this scale. The
  pre-registered falsification clause ("per-layer targets do not
  transfer to the transformer at probe scale") triggers; W2 P4 is
  the boundary, named with a full defect trail.
- **P4c ✅ — the F5 transformer ratchet holds:** O(1) peak is
  structural (per-layer graphs built and released; 0 saved bytes vs
  bp's 256 KiB). The memory half of criterion 3 is real; the learning
  half failed honestly.
- **Defect trail (all measured, load-bearing for any retry):**
  (1) RMS-normalizing the goodness stream pins G==1 for both phases —
  structurally zero contrast; measure on the raw stream. (2) A
  LEARNED label injection is runaway positive feedback (norm 8→349 in
  200 steps); the label projection must be FIXED. (3) pe (±1 entries)
  swamps the label contrast in G (~1.0 vs ~0.008) — exclude pe from
  the embed goodness. (4) The MLP raw-CE readout contract does not
  transfer (head raw grad RMS ~1e-5 vs hidden ~0.65 — ~5e4
  imbalance); the head rides the EMA-normalized axis. (5) Train/eval
  injection mismatch — readout trains label-free (fixed, though
  immaterial at this signal scale).
- **Surviving mechanism hypothesis:** the fixed injection (RMS 0.088)
  modulates a 0.79-RMS stream by ~1% — the contrast direction is
  noise-dominated, and unit-RMS EMA-normalized hidden steps random-
  walk features faster than the signal organizes them.

**Queued retry levers (none claimed):** (a) gain-matched per-block
label re-injection; (b) **the SP2/D17 lesson is the big one** — local
credit needed the right optimizer (Muon rescues weak credit ~2×);
a Muon/OrthoAdam update on these pseudo-gradients is the obvious
lever (per-step SVD on 128×512 matrices — GPU cell); (c) normalized
streams at matched contrast scale.

### 2026-09-07 — Session 5: W3 closed-form ψ landed — boundary EXACTLY mapped; W4 depth frontier + zero-shot LR transfer CONFIRMED

**W3 (`scripts/probes/w3_closed_form_psi.py`, ~2.6 s CPU; pre-registered).**
Two artifacts landed:

1. **Pipeline contract change (the D22 root-cause repair):**
   `run_train_step` now steps ψ on the NUDGED settle when the primitive
   declares `psi_phase = "nudged"`; z then carries the target AND the
   pre-readout stream `h` (`computronium/core/pipeline.py::_step_psi`).
   **Latent P-axis defect fixed en route:** ψ stepped inside
   `run_train_step` was never written back to the caller's dict — the
   P-axis silently reset every call. In-place sync added; 78 pipeline/
   plasticity tests + 5 z3/pareto integration tests green.
2. **`ClosedFormRidgePlasticity`** (`core/plasticity/closed_form.py`,
   exported via root `_LAZY`/`__all__` + ontology.plasticity): ridge
   sufficient statistics G=ΣHᵀH, C=ΣHᵀ(onehot−softmax(post))
   accumulated per episode; ψ = M = (G+λI)⁻¹C solved exactly
   (bias-augmented column). No gradients anywhere.

**Verdict (d22 skeleton, parity→last-symbol, stage A 0.977):**
ψ-only B 0.644→**0.699** (θ bitwise frozen, SHA-verified, through the
REAL pipeline with step_size=0); fine-tune 0.992 @112 episodes;
retention ψ 0.973 ≈ null 0.973 ≫ fine-tune 0.660.

- **P1 falsified (strong form):** 0.699 is EXACTLY the frozen-feature
  linear-probe ceiling — the ridge solve IS that probe. Closed-form ψ
  = instant optimal linear readout on frozen features; it cannot
  synthesize features. The A→B switch needs feature reorganization,
  which requires θ change.
- **P2 falsified:** ψ never reaches 0.984; bounded-instant vs
  slow-unbounded.
- **P3 ✅ decisively:** zero forgetting by construction, as predicted.
- **Promotable (bounded) finding:** "a closed-form ridge ψ recovers
  exactly the frozen-feature linear-probe ceiling — no more. It
  composes with, and cannot substitute for, θ plasticity."
- **Open lever (queued, not claimed):** hidden-layer closed-form ψ
  corrections (per-layer, W2-style recompute) — the readout-only law
  can't reorganize features; a hidden-layer ψ might.

**W4 (`scripts/probes/w4_depth_frontier.py`, ~25 min CPU; pre-registered).**
D14 jpc-faithful regime (width 128 residual, beta 10, gamma 0.1,
150 batches), mupc × OrthoAdam (SVD, ortho_lr on its own axis):

| depth | mupc×ortho (zero-shot lr 1e-3, seeds 0–2) | control |
|---|---|---|
| 8 | 0.928 (lr pick) | — |
| 20 | **0.920** | D14 mupc+Adam 0.78 |
| 32 | **0.867** | mupc+Adam 0.420; ortho lr 3e-3 0.689 |
| 50 | 0.397 (memorization, train ~0.97) | — |

- **P1 ✅ at 32** (mean 0.867 ≥ 0.8); **the frontier's real limit is
  between 32 and 50** (depth-50 collapse is memorization, not
  divergence). Depth-100 compute gate stayed closed.
- **P2 ✅ DECISIVELY — "tune once, run anywhere" is REAL:** the
  depth-8-selected lr, run unchanged, is best at 20 AND 32 — it even
  BEATS the per-depth retune at 32 (0.867 vs 0.689). S1's headline.
- **P3 ✗:** default-init × OrthoAdam at 32 = 0.450 — the D16 rescue is
  depth-bounded below 32; μPC init stays load-bearing at depth.
- Also re-confirmed: OrthoAdam lifts depth-20 0.78→0.92; Adam
  depth-fragility reproduced (0.420 at 32).

**New improvement opportunities:**
1. **Hidden-layer closed-form ψ** (W3 lever): per-layer ridge
   corrections on recomputed hidden streams — the only route to
   feature-synthesizing gradient-free adaptation. Natural W2×W3
   composition; medium build.
2. **Depth-50 frontier autopsy:** memorization under 150-batch budget;
   longer budget or stronger reg (beta sweep) at depth 50 would locate
   whether the wall is data-budget or architecture. Cheap-ish (CPU).
3. **Zero-shot transfer breadth:** does the depth-8 lr also transfer
   to width changes (64→128→256)? Same probe, one axis. Ties W4 to
   μPC's paper claim directly.
4. **W2 P4 (transformer composition) remains the main Tier-1 build
   ahead** — needs the label-channel design decision (fixed-shape
   transformer weights vs a credit-owned label-embedding matrix at the
   embedding output). F5 re-pin rides on it.
5. **D17 late-regime 3M-token cell** (gated): only if a headline needs
   the >3M side of the crossover (Session-4 open axis).

