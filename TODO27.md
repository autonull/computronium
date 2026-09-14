# TODO27 — Discovery Round: Credit-Channel Inventions + Lean Autopoiesis

**Status:** PLANNED 2026-09-14. Course-corrects the program from
infrastructure rounds (TODO23–26) to **general-purpose ML discovery and
invention**: falsifiable experiments on the credit channel (RESEARCH4's
six levers) and the lean Autopoiesis self-modification probe
(AUTOTILE.md), both riding the certification spine we just finished.
**Builds on:** TODO26 (all phases + Phase S; H24.3 carries two
certified verdicts). **Explicit exclusions:** PyPI publishing; physical
hardware; LLM-scale claims.

---

## 0. The Course Correction

### 0.1 The drift, stated plainly

TODO23–26 spent four consecutive rounds mostly on measurement and
governance infrastructure (synthesis layer, evolution, corpus, CEEC
kernel) plus one P-axis thread (temporal ψ on synthetic gaussian
blobs). RESEARCH4's credit-channel agenda — the unifying diagnosis that
**every local-algorithm defect is a credit-fidelity failure that
compounds with depth** — has zero executed experiments. The six-axis
substrate story, the benchmark paper, and Z3/ICL are likewise idle.
Infrastructure was reproducing itself: TODO25→TODO26 was largely CEEC
refactoring CEEC.

**TODO27 freezes infrastructure work.** Rule for the whole round: *no
CEEC/lab architectural change is in scope unless it unblocks a named
discovery experiment below.* Instrument quality is a multiplier; this
round multiplies.

### 0.2 What the last four rounds actually bought (the justification)

The infrastructure is not the program — it is what makes the program's
own protocol (RESEARCH3 E-1..E-11, PR-2/PR-4/PR-6) executable instead
of aspirational. Concretely, each RESEARCH3 protocol rule now has an
operational counterpart:

| RESEARCH3 requirement | Instrument that now executes it |
|---|---|
| E-1 smoke→pilot→full ladder | corpus tiers + `Lab.research_report` dry runs |
| E-3 reproducibility contract | CEEC ledger: append-only artifacts with sha256 + execution provenance (code commit, seed policy, config hash — TODO26 F.2) |
| E-4 baseline protection | corpus matched-compute arms (`theta_finetune_matched_compute`, capacity-matched controls) |
| E-10 minimum-viable controls | continual benchmark arm structure (frozen floor + matched-θ control + mechanism) |
| E-11 decision log | CEEC `policy_version` stamping + pre-registration-before-probe (`run_experiment` records the §22 decision strictly before measurement) |
| PR-2 θ-invariance audit | `FrozenThetaAudit` + `theta_digest` (bitwise, adversarially tested) |
| PR-4 statistics kit | `permutation_test_p`, paired comparisons in corpus/continual reports |
| PR-6 fairness contract | profile-bound budgets (`Profile.tier_budget`), keyword-only record APIs, gate families |

And the round-trip proof that the spine works end-to-end: **H24.3**
moved from instrument-blocked → certified AGAINST (accuracy rule) →
certified FOR (speed rule) inside one session, with the instrument
defect root-caused (ψ statistics discarded between episodes) and fixed
in place. A blocked instrument no longer silently produces misleading
evidence. Negative results are first-class: both H24.3 verdicts and the
round-1 caveat are ledger-persistent, machine-readable, and citeable.

**Justification verdict:** the four rounds are justified as the
precondition for this one — *if and only if* TODO27 spends them on
discovery. That is the round's whole design.

### 0.3 The best we can honestly hope for

With a CPU-tier certified loop costing ~a session per round-trip, the
realistic ceiling of this round:

1. **A new local learning rule candidate** — if RESEARCH4 levers 1+2
   compose (learned, orthogonally-normalized feedback), that is a
   publishable mechanism claim with certified width/depth sweeps behind
   it: "credit direction was right; magnitude was broken; here is the
   rule that fixes magnitude locally."
2. **A falsification with teeth** — if the levers fail their
   pre-registered predictions, we hold certified boundaries (width
   windows, decay profiles) that prune the search space for everyone,
   recorded in the failure manifesto.
3. **The first honest three-tier self-modification measurement** —
   lean Autopoiesis (Tier 1+2, fixed menu) with oracle-rescue pilots;
   if Tier 2 passes, the catalog's "which credit family can use depth"
   question becomes an *autonomous search result* rather than a manual
   sweep.
4. **Generalization beyond the operating point** — the ψ speed result
   (1-episode acquisition) replicated on a second curriculum; width
   sweeps on a real-data tier (MNIST quick) instead of gaussian blobs.

What we cannot hope for and do not claim: hardware measurements,
LLM-scale validation, or Level 1–3 formal claims. Quick/standard-tier
certified mechanisms are the ceiling — stated up front, per the
verification taxonomy.

---

## 1. The discovery agenda (two tracks, one spine)

**Track 1 — Credit-channel inventions (RESEARCH4).** The measured
defect map (RESEARCH4 §Unifying Diagnosis) already tells us what to
engineer: a local credit channel that is *aligned, non-attenuating,
gain-normalized, task-coupled, well-conditioned*. Execute its phases in
impact order with certified gates.

**Track 2 — Lean Autopoiesis (AUTOTILE.md as amended).** Constitutional
self-modification reduced to its load-bearing core: neutral birth +
slope-based selection on forked-copy adaptation probes, Tier 1+2 only,
no Tier 3, single organism, paired statistical acceptance with a genome
size penalty. The corpus catalog (trainable_on, mechanism rows, CEEC
ledger) *is* its registry and constitution bookkeeping.

Tracks share the spine: pre-register on Session → certified corpus arm
→ gates → calibration → failure-manifesto on nulls.

---

## Phase A — Kill the Optimizer Crutch (RESEARCH4 Phase 1)

| Task | Deliverable | Depends On |
|---|---|---|
| **T27.A.1 `LocalAdamUpdate`** | New U-axis primitive: per-layer Adam normalization (per-layer m/v state, `EuclideanUpdate`-drop-in). Identity card required (`AlgorithmIdentityCard`), registry row + config classmethod per the ontology checklist | — |
| **T27.A.2 PEPITA width sweep, certified** | Arms: PEPITA × {Muon, Euclidean, LocalAdam} at widths {32, 64, 128, 256}; pre-registered prediction: LocalAdam trains at w128 where Euclidean collapses and matches Muon within noise | A.1 |
| **T27.A.3 ePC width sweep, certified** | Arms: ePC × {OrthoAdam, Euclidean, LocalAdam} same widths; prediction: LocalAdam does not explode at w32 (activity compounding 0.93→2028 under Euclid is contained) | A.1 |

**Decision rule (pre-registered at A.1 landing, before any sweep):**
"Credit direction is approximately right; magnitude is broken" is
confirmed iff **both** A.2 and A.3 predictions hold at ≥2 seeds;
falsified if either fails. Confirmed → Track 1 proceeds on magnitude
levers only. Falsified → direction levers (B/C) get priority instead.
Either outcome is a certified result.

**Why first:** U-axis-only change, no new credit rules, existing width
harnesses; the F1 failure-manifesto and P3/P4 audits supply the
baselines verbatim (E-4: reuse, don't rerun).

---

## Phase B — Credit-Space Normalization (RESEARCH4 lever 1)

| Task | Deliverable | Depends On |
|---|---|---|
| **T27.B.1 `credit_norm` option** | Normalization hook in the credit path: per-layer spectral/RMS normalization of the pseudo-gradient as it propagates down from layer ℓ to ℓ−1 (probe first on ePC's `ThermodynamicContrast` channel) | — |
| **T27.B.2 Decay-profile probe** | Measure ePC credit magnitude per layer at depth {4, 8, 16, 20}: does the ~4×/layer attenuation flatten toward ~1× with `credit_norm` on? Does credit at layer 1 reach non-vanishing norm at depth 20? | B.1 |
| **T27.B.3 Depth sweep, certified** | ePC ± credit_norm at depths {8, 16, 20} on the F1 harness; pre-registered: credit_norm arm trains where the unnormalized arm loses the contrastive signal | B.2 |

**Gate:** if B.2 shows the decay profile unchanged, the unifying
"attenuating channel" diagnosis is falsified for ePC — record it and
re-weight toward lever 2 (learned feedback).

---

## Phase C — Learned Feedback Projections (RESEARCH4 lever 2)

| Task | Deliverable | Depends On |
|---|---|---|
| **T27.C.1 Trainable B** | `LocalGoodnessCredit` gains a learnable projection B (autograd-trained alongside θ — PEPITA-as-inference-network); fixed-random-B path preserved as the control | — |
| **T27.C.2 Depth sweep, certified** | Learned-B vs fixed-B PEPITA at depths {4, 8, 16}; measure cos(B, Wᵀ) alignment drift over training (the known directional-collapse metric) | C.1 |
| **T27.C.3 Composition probe** | If B.3 and C.2 both positive: learned-B × credit_norm × LocalAdam — the "learned, orthogonally-normalized feedback alignment" candidate rule, one certified quick-tier round on flat_classification_hard | B.3, C.2 |

**Deliverable if C.3 lands:** a named candidate rule with a certified
operating point — the round's headline invention. If it fails its gate,
the failure modes (alignment drift? normalization insufficient?) are
the recorded result.

---

## Phase D — Lean Autopoiesis: Ouroboros Probe (AUTOTILE.md, amended)

Scope per the AUTOTILE simplification analysis — **Tier 3 deleted,
protocol stack reduced to one metric + one selection rule, asexual
mutations only.**

| Task | Deliverable | Depends On |
|---|---|---|
| **T27.D.1 Lean consolidator** | `AutopoieticConsolidator` (sleep-phase only): stagnation gate → propose (`DuplicateAndPerturb` / `SpliceOperator`) → constitution veto (stability guard) → neutral birth (zero-output edges, identity nodes; bit-identical forward at insertion — the J6 θ-projection correctness test) → paired adaptation probe on **forked copies** with held-out batches → statistical acceptance vs parent slope, penalized by `GenomeSizePenalty` | — |
| **T27.D.2 Amendment compliance** | Probes resource-budgeted (settle-step cost reported, not just step count — the E-4 confound); rollback: accepted genome checkpointed, revertible on degradation; Ω + lineage written into the E-3 manifest; prior-art gate logged (NEAT neutral birth, PBT slope-fitness, Gödel machine — delta: typed property-locked ontology, enforced constitution, slope currency, falsifiable tiers) | D.1 |
| **T27.D.3 Oracle-rescue pilot** | For each tier: hand-inject the correct mutation, verify the pressure bites (seed Tier 1 deliberately under-capacity, hidden_dim 2–4) and the probe selects the rescue. **No autonomous run before this passes** — the anti-false-negative gate | D.1, D.2 |
| **T27.D.4 Tier 1 probe** | Growing Context Parity (lag 5→50), seed Ω₀ = one under-capacity RecurrentBlock; success: \|Ω\| grows as lag increases, accuracy >90%, neutral birth verified at every insertion | D.3 |
| **T27.D.5 Tier 2 probe** | Episode-30 credit-noise injection; success: Ω swaps the Credit axis (visible **only** under slope selection — the load-bearing claim), accuracy recovers | D.4 |
| **T27.D.6 Certified recording** | The probe run (whichever tiers pass/fail) pre-registered and recorded through Session; Tier failures land in the failure manifesto as the first honest three-tier self-modification measurement | D.4 |

**Kill criterion (pre-committed):** Tier 2 fails after ≤3 tuning rounds
→ Autopoiesis shelves to a neuroevolution-tier artifact; the probe
publishes as a falsification. **Strategic upside if Tier 1 passes:**
the Tier-1 consolidator *is* a progressive-deepening operator — the
memory-wall/depth-scaling chart becomes a grown lineage rather than a
hand-picked sweep (AUTOTILE §8.7), queued as the next round's
flagship candidate.

---

## Phase E — Generalization (spine stress-test, cheap)

| Task | Deliverable | Depends On |
|---|---|---|
| **T27.E.1 Second continual curriculum** | Register a second curriculum (new offset/threshold); re-run the H24.3 speed rule — turns the 1-episode acquisition result from an operating-point finding into a (still tier-scoped) mechanism claim or a certified boundary | — |
| **T27.E.2 Real-data quick tier** | One width-sweep arm from Phase A re-run on the MNIST quick tier instead of gaussian blobs — checks that Phase A's conclusion survives leaving the synthetic tier | A.2/A.3 |

---

## Gates (whole round)

1. **Infrastructure freeze:** zero CEEC/lab architectural commits
   except those unblocking a named task above (auditable from the git
   log — enforced by review, listed in the progress log).
2. **Pre-registration discipline:** every sweep/probe has its decision
   rule registered before its data exists (Session run ordering makes
   this structural; violations are review blockers).
3. **Certified or manifesto:** every Phase lands exactly one of — a
   certified verdict, a manifesto entry with root cause, or an
   infra-failure (which restarts the round, per E-7).
4. **Suites:** repo-wide ruff clean maintained; ceec + lab suites green
   per phase; new primitives (LocalAdamUpdate, trainable-B) ship with
   identity cards + property locks.
5. **Tier honesty:** all claims stay Level 4/5 at quick/standard tier;
   no wording drift toward validated-scale claims.

---

## 17. Progress Log

### Session 2026-09-14 — PLANNED
- [x] Course-correct diagnosis verified against the session record
  (TODO23–26 infrastructure drift; RESEARCH4 unexecuted; AUTOTILE
  amendments incorporated: Tier 3 cut, single selection policy,
  resource-budgeted probes, rollback, oracle-rescue, prior-art gate)

---

## 18. Implementation notes

- **Sequencing rationale:** A is first because it is U-axis-only and
  its outcome *routes* the rest (magnitude levers vs direction levers);
  B and C are independent and can interleave; D is CPU-minutes cheap
  and runs whenever a long sweep blocks; E rides spare capacity.
- **Reuse inventory (E-4: don't rerun baselines):** F1 depth/width
  audit harness (ePC decay profile, sPC zero-credit, PEPITA collapse),
  P3 optimizer-crutch measurements (ePC gradient 400× small under
  Euclid; Muon load-bearing), P4/P5 width sweeps, `probe_campaign`
  (forked-copy paired-slope machinery already in `adaptation.py` —
  D's probe primitive), catalog `trainable_on` + campaign fitness
  (D's registry/constitution bookkeeping), corpus matched-compute
  controls (A/B/E arms).
- **Existing-ledger hygiene:** prior scratch ledgers predate
  `policy_version` 26.0; their rows read as pre-T26 semantics — new
  rounds write to fresh per-round ledgers as TODO26 S.3 did.
- **Out of scope:** Tier 3 meta-morphogenesis (deferred until Tier 1+2
  demonstrates measurable benefit — AUTOTILE's own red line);
  population/crossover; open-field self-modification; hardware;
  multi-GPU scaling; anything requiring new substrate models.
