# TODO27 — Discovery Round: The Rescue Matrix + Lean Autopoiesis

**Status:** PLANNED 2026-09-14 (rev 3: complete task-space view —
registered + candidate problem classes; certification space = product of
mechanisms × problem classes × tiers × substrates × interventions).
Course-corrects the program from infrastructure rounds (TODO23–26) to
**general-purpose ML discovery and invention**: axis-level interventions
evaluated across the full mechanism catalog on the full registered task
space under certified matched-compute rules, plus the lean Autopoiesis
self-modification probe. **Builds on:** TODO26 (all phases + Phase S).
**Explicit exclusions:** PyPI publishing; physical hardware; LLM-scale
claims; new substrate models.

---

## 0. The Course Correction

### 0.1 The drift, stated plainly

TODO23–26 spent four consecutive rounds mostly on measurement and
governance infrastructure (synthesis layer, evolution, corpus, CEEC
kernel) plus one P-axis thread (temporal ψ on synthetic gaussian
blobs). RESEARCH4's credit-channel agenda — the unifying diagnosis that
**local-learning defects are credit-fidelity failures that compound
with depth/width** — has zero executed experiments. Infrastructure was
reproducing itself: TODO25→TODO26 was largely CEEC refactoring CEEC.

**TODO27 freezes infrastructure work.** Rule for the whole round: *no
CEEC/lab architectural change is in scope unless it unblocks a named
discovery experiment below.* Instrument quality is a multiplier; this
round multiplies.

### 0.2 Design principle: interventions on axes, subjects from the catalog, the full task space is the arena

The rev-2 draft anchored on RESEARCH4's worked examples (PEPITA, ePC)
and a single synthetic problem class. That under-uses the platform: the
zoo ships ~13 factories and a catalog of mechanism coordinates spanning
every credit × update family, and the corpus already registers **7
problem classes** across classification, sequence, state-prediction,
and continual learning. The fix is structural:

1. **Implement each intervention once, on its axis**, as a drop-in
   primitive — a `ParameterUpdate` (per-layer magnitude normalization),
   a credit-path option (propagation normalization), a credit-rule
   variant (learnable feedback), a ψ-warm-start arm (continual arm).
   Every catalog mechanism that composes that axis inherits the
   intervention for free. No per-algorithm patching.
2. **Let the catalog supply the mechanisms; let the corpus supply the
   tasks.** The question is never "does this fix PEPITA" but
   "**which mechanisms does each intervention rescue, on which problem
   classes, at which width/depth regimes, and which families are
   immune?**" — answered by a grid over the full certified product
   space: `{Mechanisms} × {ProblemClasses} × {Tiers} × {Substrates}
   × {Interventions}`.
3. **Let the AutoScientist schedule it.** The proposer/campaign stack
   (which has never completed a commissioned run — RESEARCH3 PR-9)
   prioritizes which grid cells earn certified-tier budget. The
   campaign stack finally consumes real work; the sweep avoids
   hand-picked ordering.
4. **Tier the cost.** Screen the whole grid at smoke tier (seconds per
   cell), promote only the top contrasts to certified quick tier — the
   E-1 ladder, which the corpus already institutionalizes. Maximum
   benefit per certified GPU-minute.

### 0.3 What the last four rounds actually bought (the justification)

The infrastructure is not the program — it is what makes the program's
own protocol (RESEARCH3 E-1..E-11, PR-2/PR-4/PR-6) executable instead
of aspirational. Each protocol rule now has an operational counterpart:

| RESEARCH3 requirement | Instrument that now executes it |
|---|---|
| E-1 smoke→pilot→full ladder | corpus tiers + `Lab.research_report` dry runs |
| E-3 reproducibility contract | CEEC ledger: append-only sha256 artifacts + execution provenance (code commit, seed policy, config hash — TODO26 F.2) |
| E-4 baseline protection | corpus matched-compute arms (matched-θ control, capacity-matched control, frozen floor) |
| E-10 minimum-viable controls | continual benchmark arm structure |
| E-11 decision log | `policy_version` stamping + decision-recorded-before-probe (`run_experiment`) |
| PR-2 θ-invariance audit | `FrozenThetaAudit` + `theta_digest` (bitwise, adversarially tested) |
| PR-4 statistics kit | `permutation_test_p`, paired comparisons in corpus/continual reports |
| PR-6 fairness contract | profile-bound budgets, keyword-only record APIs, gate families |
| PR-9 campaign commissioning | **open — this round finally exercises it (T27.B.3)** |

Round-trip proof: **H24.3** moved from instrument-blocked → certified
AGAINST (accuracy rule) → certified FOR (speed rule) inside one
session, with the instrument defect root-caused (ψ statistics discarded
between episodes) and fixed in place. Negative results are first-class
and ledger-persistent.

**Justification verdict:** the four rounds are justified as the
precondition for this one — *if and only if* TODO27 spends them on
discovery. The infrastructure-freeze gate (§Gates) makes that binding.

### 0.4 The best we can honestly hope for

1. **A certified rescue map** — machine-readable: which mechanisms fail
   on which problem classes at which width/depth regimes, and which
   axis-level intervention rescues which failure. Even all-negative
   cells are pruning results.
2. **A new general-purpose rule candidate** — if normalization and/or
   learned-feedback compose across *multiple* families (not one
   algorithm), that is a mechanism claim with certified sweeps behind
   it, family-coverage being the credibility multiplier.
3. **The first honest three-tier self-modification measurement** —
   lean Autopoiesis with oracle-rescue pilots; a pass on Tier 2 makes
   "which interventions help" an autonomous search result.
4. **A commissioned AutoScientist loop** — the campaign stack
   completing real iterate → measure → frontier cycles on discovery
   work, unblocking RESEARCH3's frontier campaign and discovery items.
5. **Generalization checks** — findings re-tested off their discovery
   task (second curriculum, real-data tier, new substrate).

Not claimed: hardware measurements, LLM-scale validation, Level 1–3
formal claims. Quick/standard-tier certified mechanisms are the ceiling.

---

## 1. The Task Space — Registered + Candidate

The corpus currently registers **7 problem classes** via
`register_problem_class()` in `corpus.py`:

| Problem Class | Tier | Type | Example Tasks |
|---|---|---|---|
| `flat_classification` | quick/standard | Static → class | Gaussian blobs, MNIST, CIFAR-10/100 (if wired) |
| `flat_classification_hard` | quick/standard | Static → class, harder | Harder blobs, higher dimension |
| `continual_switch` | quick/standard | Task A → B | Synthetic A→B switch (current), real curricula (candidate) |
| `sequence_last_symbol` | quick/standard | Sequence → class | Last symbol recall |
| `sequence_threshold` | quick/standard | Sequence → class | Threshold counting |
| `sequence_parity` | quick/standard | Sequence → class | Parity over sequence |
| `nca_state_prediction` | quick | Grid t→t+1 | NCA rollout, label-free |

**Candidate problem classes** (not yet registered, but part of the
certification space the framework is designed for):

| Candidate | Tier | Type | Why it matters |
|---|---|---|---|
| `image_classification` | standard/nightly | Image → class | CIFAR-10/100, ImageNet subset — the canonical "local vs backprop" claim space |
| `language_modeling` | standard/nightly | Next-token | WikiText, TinyStories — LM is the dominant workload; local rules need to prove here |
| `reinforcement_learning` | standard | Policy/value | Minigrid, Procgen — local credit + ψ adaptation is a natural fit for RL |
| `generative_modeling` | standard | Density/sample | VAE/GAN-style — local rules on generation is an open question |
| `regression` | quick/standard | Continuous target | Physical dynamics, control — local rules on continuous targets |
| `anomaly_detection` | quick | Binary/ood | Security, monitoring — local rules' error-blindness is tested here |
| `multi_task` | standard | Multi-head | MTL/continual — ψ-swap and routing are designed for this |

**The certification space is the full product:**
`{Mechanisms from CATALOG} × {Registered + Candidate Problem Classes} ×
{Tiers} × {Substrates} × {Interventions}`

**This round's scope:** we certify on the **registered 7** (smoke
screen) and promote the top cells on the **highest-practitioner-
relevance** candidates (`image_classification`, `language_modeling`) to
standard tier. The candidate classes are not blockers — they are the
next-round expansion targets.

---

## 1. The Unified Stack — How It All Fits Together

- **Ontology (6 axes)** — the space; every intervention below is a new
  primitive on one axis, so the whole compatible region inherits it.
- **Catalog + synthesis** — the roster of mechanisms and the validity
  screen (`trainable_on`, `SystemConfig.validate()`) that keeps the
  grid honest.
- **Corpus + MeasurementRunner** — the arenas: 7 registered problem
  classes, budget tiers, matched-compute controls, manifests.
- **CEEC** — the referee: pre-registration, artifacts, evidence, gates,
  calibration, audit, failure manifesto. Zero kernel changes planned
  (§Phase F); one new lab profile.
- **AutoScientist** — the scheduler: proposes which grid cells deserve
  certified budget, records lineages, renders frontiers.
- **Lean Autopoiesis** — search internalized: the same
  propose→probe→accept loop running inside a single organism at episode
  boundaries, using the catalog as its registry and the stability guard
  as its constitution.

The phases are deliberately redundant: B (external, exhaustive sweep)
and D (internal, autonomous) attack the same question by different
mechanisms — agreement makes the conclusion robust, disagreement is
itself the finding.

---

## Phase A — Axis-level interventions (build once, inherit everywhere)

| Task | Deliverable | Depends On |
|---|---|---|
| **T27.A.1 `LocalAdamUpdate`** | New U-axis primitive: per-layer Adam-style magnitude normalization (per-layer m/v state; `EuclideanUpdate` drop-in). Identity card, registry row, config classmethod per the ontology checklist | — |
| **T27.A.2 `credit_norm` propagation option** | Credit-path option normalizing the pseudo-gradient per layer as it propagates (spectral/RMS), composable with any C-axis primitive | — |
| **T27.A.3 Trainable feedback variant** | `LocalGoodnessCredit` gains learnable B (autograd-trained with θ; fixed-random-B preserved as control) | — |
| **T27.A.4 ψ warm-start arm** | `LocalAdamUpdate`-style composition on the continual side: ψ-acquire (1-episode) → θ-consolidate from the warm readout — the H24.3 frontier-closing arm as a catalog-level option | — |

Each intervention carries its falsifiable story from RESEARCH4 (A.1:
magnitude-broken-not-direction; A.2: attenuating-channel; A.3:
misaligned-channel) — but the stories are tested across the catalog,
not on one algorithm.

---

## Phase B — The Rescue Matrix (screen wide, certify narrow)

| Task | Deliverable | Depends On |
|---|---|---|
| **T27.B.1 Full-product smoke screen** | Grid: `{Mechanisms from CATALOG} × {7 Registered Problem Classes} × {Regimes: width {32,64,128,256}, depth {4,8,16,20}} × {Interventions {none, A.1, A.2, A.3, A.1+A.2}}`. Output: which cells fail today (reproduces F1/P3/P4 boundaries cheaply) and which interventions flip them. Machine-readable matrix artifact | A.1–A.3 |
| **T27.B.2 Certified promotions (standard tier)** | Top-k contrasting cells promoted through Session closed loops with pre-registered decision rules — e.g. "intervention X rescues family Y on `image_classification` at width 128 with matched compute and ≥2 seeds". Both rescues and refusals certify | B.1 |
| **T27.B.3 AutoScientist scheduling + commissioning (PR-9)** | The proposer prioritizes promotion order from screen slopes, weighted by `PractitionerRelevance` (image_classification > language_modeling > continual > sequence > state_prediction > synthetic). One full campaign iterate → measure → frontier → resume cycle runs on this real workload (finally discharges RESEARCH3 PR-9); frontier rendered via `comp frontier` | B.1 |
| **T27.B.4 The rescue map** | Certified rescue map + frontier: which families are magnitude-limited vs direction-limited vs immune, on which problem classes — the round's headline deliverable either way | B.2, B.3 |

**Decision rules are registered per promoted cell before its data
exists** (Session ordering makes this structural). The RESEARCH4
unifying hypothesis ("direction right, magnitude broken") is confirmed
iff magnitude-only interventions (A.1) rescue across ≥2 distinct credit
families *and* on ≥2 problem classes; falsified if rescues require
direction interventions (A.3) or don't replicate across families.

---

## Phase C — ψ × θ composition check (close the H24.3 frontier)

| Task | Deliverable | Depends On |
|---|---|---|
| **T27.C.1 Warm-start certified round** | On the continual benchmark: arm ψ-acquire→θ-consolidate (A.4) vs θ-cold vs ψ-only vs θ-only; pre-registered rule: warm-start reaches the θ-only ceiling in fewer epochs than cold start | A.4 |

Cheap (existing harness, one new arm); converts the certified speed/
accuracy Pareto frontier into a composition claim or a certified
boundary on it.

---

## Phase D — Lean Autopoiesis: Ouroboros Probe (AUTOTILE.md, amended)

Tier 3 deleted, protocol stack reduced to one metric + one selection
rule, asexual mutations only — per AUTOTILE's own simplification
analysis.

| Task | Deliverable | Depends On |
|---|---|---|
| **T27.D.1 Lean consolidator** | Sleep-phase-only loop: stagnation gate → propose (`DuplicateAndPerturb` / `SpliceOperator`) → constitution veto (stability guard) → neutral birth (zero-output edges, identity nodes; bit-identical forward at insertion — doubles as the θ-projection correctness test) → paired adaptation probe on **forked copies** with held-out batches → statistical acceptance vs parent slope, penalized by `GenomeSizePenalty`; rollback checkpoint on every acceptance | — |
| **T27.D.2 Amendment compliance** | Probes resource-budgeted (settle-step cost reported, not just step count — the E-4 confound); Ω + lineage in the E-3 manifest; prior-art gate logged (NEAT neutral birth, PBT slope-fitness, Gödel machine — delta: typed property-locked ontology, enforced constitution, slope currency, falsifiable tiers) | D.1 |
| **T27.D.3 Oracle-rescue pilot** | Per tier: hand-inject the correct mutation; verify pressure bites (Tier 1 seeded under-capacity, hidden_dim 2–4) and the probe selects the rescue. **No autonomous run before this passes** | D.1, D.2 |
| **T27.D.4 Tier 1 probe** | Growing Context Parity (lag 5→50); success: \|Ω\| grows with lag, accuracy >90%, neutral birth verified at every insertion | D.3 |
| **T27.D.5 Tier 2 probe** | Episode-30 credit-noise injection; success: Ω swaps the Credit axis (visible only under slope selection — the load-bearing claim), accuracy recovers | D.4 |
| **T27.D.6 Certified recording** | Whatever passes/fails is pre-registered and recorded through Session; tier failures land in the failure manifesto as the first honest three-tier self-modification measurement | D.4 |

**Kill criterion (pre-committed):** Tier 2 fails after ≤3 tuning rounds
→ Autopoiesis shelves to a neuroevolution-tier artifact; the probe
publishes as a falsification. **Strategic upside if Tier 1 passes:** the
Tier-1 consolidator *is* a progressive-deepening operator — the
depth-scaling chart becomes a grown lineage (AUTOTILE §8.7), queued as
the next round's flagship candidate.

---

## Phase E — Generalization (spine stress-test, cheap)

| Task | Deliverable | Depends On |
|---|---|---|
| **T27.E.1 Off-discovery replication** | The round's top certified claim re-tested on a problem class it was not discovered on (e.g., if rescue found on `flat_classification`, re-test on `image_classification` or `continual_switch`). Findings that don't travel get their scope narrowed in the ledger — that correction is itself a certified result | B.2 |

---

## Phase F — CEEC support (adapter-only)

| Task | Deliverable | Depends On |
|---|---|---|
| **T27.F.1 Discovery profile** | ~60-line lab profile: scope dims (width/depth/credit_family/mechanism/problem_class), quality flags for the matrix (regime, intervention, replicates, problem_class), constraint "promoted cell must have its smoke-tier screen row on record". **No kernel changes** — this is the TODO26 architecture's generalization test | — |

If a kernel change starts looking necessary mid-round, that is a
course-drift signal — raise it against the freeze gate instead of
implementing it.

---

## Gates (whole round)

1. **Infrastructure freeze:** zero CEEC/lab architectural commits
   except T27.F.1 and changes unblocking a named task (auditable in
   the progress log).
2. **Pre-registration discipline:** every promoted cell and probe has
   its decision rule registered before its data exists.
3. **Certified or manifesto:** every phase lands exactly one of — a
   certified verdict, a manifesto entry with root cause, or an
   infra-failure (restarts the round, per E-7).
4. **Family coverage:** no mechanism claim ships from a single
   algorithm; the matrix reports per-family outcomes on ≥2 problem
   classes (E-4/PR-6).
5. **Suites:** repo-wide ruff clean maintained; ceec + lab suites green
   per phase; new axis primitives ship with identity cards + property
   locks.
6. **Tier honesty:** all claims stay Level 4/5 at quick/standard tier.

---

## 17. Progress Log

### Session 2026-09-14 — PLANNED (rev 3)
- [x] Course-correct diagnosis verified against the session record
  (TODO23–26 infrastructure drift; RESEARCH4 unexecuted; AUTOTILE
  amendments incorporated: Tier 3 cut, single selection policy,
  resource-budgeted probes, rollback, oracle-rescue, prior-art gate)
- [x] Rev 2: de-anchored from RESEARCH4's example algorithms —
  interventions moved to axis primitives (catalog inherits them),
  AutoScientist commissioned as scheduler (discharges PR-9), smoke-
  screen → certified-promotion tiering added for maximum benefit per
  certified GPU-minute
- [x] Rev 3: complete task-space view — 7 registered + 7 candidate
  problem classes; certification space = full product; practitioner-
  relevance weighting; smoke-screen over full product; AutoScientist
  prioritization with `PractitionerRelevance` weight

---

## 18. Implementation notes

- **Sequencing rationale:** A is first (primitives are the grid's
  columns); B is the round's core and its cost center — the smoke
  screen keeps certified spend proportional to signal; C rides the
  existing continual harness; D is CPU-minutes and runs whenever a
  sweep blocks; E and F are spillover capacity.
- **Reuse inventory (E-4: don't rerun baselines):** F1 depth/width
  audit harness, P3 optimizer-crutch measurements, P4/P5 width sweeps,
  `probe_campaign` (forked-copy paired-slope machinery already in
  `adaptation.py` — D's probe primitive), catalog `trainable_on` +
  campaign fitness (D's registry/constitution bookkeeping), corpus
  matched-compute controls, `comp scientist`/`comp frontier` (B.3's
  scheduler and renderer), presets/catalog rows (grid subjects).
- **Cost control:** the grid is M×P×R×I — combinatorial by nature.
  Smoke tier makes screening nearly free; certified promotions are
  capped per phase (k ≤ 5 cells) and chosen by screen slope weighted
  by `PractitionerRelevance`, not preference. The matrix records *why*
  unpromoted cells were left unpromoted.
- **Existing-ledger hygiene:** fresh per-round ledgers (TODO26 S.3
  pattern); prior scratch ledgers read as pre-T26 semantics.
- **Candidate expansion:** `image_classification`, `language_modeling`,
  `reinforcement_learning` are the next three registrations; they are
  not this round's scope but are explicitly called out as the
  certification space's expansion frontier.
- **Out of scope:** Tier 3 meta-morphogenesis (until Tier 1+2 shows
  measurable benefit), population/crossover, open-field
  self-modification, hardware, multi-GPU scaling, new substrate
  models, portfolio budgeting.