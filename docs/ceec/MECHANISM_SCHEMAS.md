# Mechanism Schemas

Mechanism schemas are derived objects and generality beliefs extracted from
gated evidence. At bootstrap round 1 none have been earned: schemas require
at least one promoted claim or one boundary with defect hunt in the target
scope.

## Schema template

Each schema records:

- **supporting scopes** — the Scope objects of promoting/bounding evidence
- **evidence refs** — `E-` ids feeding the schema
- **failure boundaries** — scopes where the mechanism is known to fail or is
  untested
- **verification levels** — evidence strength per supporting record

## Reserved schema slots (pending evidence)

| Schema | Source belief | Status |
|---|---|---|
| local-credit-adaptive-inverse | B-H1-ADAPTIVE-LOCAL-INVERSES | evidence partial (X-ALI-001); schema emission pending |
| temporal-psi-credit | B-H2-TEMPORAL-PSI-CREDIT | **emitted** (D-000013, round 5) |
| stable-transient-amplification | B-H3-STABLE-TRANSIENT-AMPLIFICATION | evidence partial (X-STA-001); schema emission pending |
| routing-sparsity-efficiency | B-H4-ROUTING-SPARSITY-EFFICIENCY | evidence partial (X-RSE-001, negative at operating point); schema emission pending |
| update-rule-specialization | B-H5-UPDATE-RULE-SPECIALIZATION | evidence partial (X-USU-001); schema emission pending |

First schema emitted round 5 (temporal-psi-credit, D-000013) — see below.
Re-emitted round 7 with X-TPC-003 evidence (D-000015 superseded by
D-000016 for complete verification levels) and round 8 with X-TAC-001
evidence (D-000017 superseded by D-000018; D-000017 missed the adaptive
clause).

Schemas are emitted as `derived` objects of type `mechanism_schema` via
`computronium.ceec.schemas.emit_mechanism_schema` (CLI: `emit-schema`).

## Emitted schemas

### temporal-psi-credit (D-000013, belief B-H2-TEMPORAL-PSI-CREDIT)

- **Statement:** temporal (trace-decayed, ρ<1) ψ credit beats forget-free
  closed-form ridge accumulation (ρ=1) when task fits conflict on the same
  frozen h; at non-conflicting coordinates the two are statistically tied,
  and ρ<1 trades old-task retention for new-task acquisition.
  Supervised-ψ acquisition (nudged-phase target consumption) is necessary
  in both cases.
- **Supporting evidence:** E-000010 (bootstrap provenance), E-000022
  (X-TPC-001, non-conflicting), E-000024 (X-TPC-002, conflicting; canonical
  of the duplicated E-000023 — supersedes relation D-000012).
- **Failure boundaries:** quick budget / digital feedforward / 2-class toy
  switch; temporal advantage absent at non-conflicting coordinates;
  old-task retention degrades with forgetting.
- **Verification levels:** E-000022: 4, E-000024: 4 (sampled numerical).
- **Checks:** θ bitwise-frozen on all arms/seeds (both probes); matched
  controls (closed-form ρ=1 + frozen-null); ρ ∈ {0.5, 0.7, 0.9} all
  support the conflict advantage 3/3 seeds.
- **Belief interval at emission:** [0.35, 0.55], status open.

### temporal-psi-credit — round-7 update (D-000016, belief B-H2-TEMPORAL-PSI-CREDIT; supersedes D-000015, which had incomplete verification levels)

- **Statement:** as D-000013, plus the real-scale clause: the advantage
  holds on MNIST with conflicting label geometry (backbone trained on
  digit≥5, ψ migration parity → INVERTED parity, θ bitwise frozen), and
  the temporal arm matches a fresh SGD re-trained linear readout (0.91–0.94)
  at the same total adaptation budget — frozen-backbone switching without
  re-training buys readout migration for free.
- **Supporting evidence:** E-000010 (bootstrap provenance), E-000022
  (X-TPC-001, non-conflicting), E-000024 (X-TPC-002, conflicting toy),
  E-000025 (X-TPC-003, conflicting MNIST + retrain_sgd control).
- **Failure boundaries:** quick budget / digital feedforward; temporal
  advantage absent at non-conflicting coordinates; old-task retention
  degrades with forgetting (B retention 0.06–0.10 at ρ=0.9); temporal is
  NOT faster per-episode than SGD re-training at this scale (0.6 s vs
  0.3 s) — the win is θ-untouched switching at matched accuracy, not speed.
- **Verification levels:** E-000022: 4, E-000024: 4, E-000025: 4.
- **Checks:** θ bitwise-frozen on all arms/seeds (all three probes);
  matched controls (closed-form ρ=1 + frozen-null; X-TPC-003 adds
  retrain_sgd); ρ ∈ {0.5, 0.7, 0.9} support the conflict advantage 3/3;
  X-TPC-003 P1/P2/P3 all supported 3/3 seeds.
- **Belief interval at emission:** [0.40, 0.65], status open.

### temporal-psi-credit — round-8 update (D-000018, belief B-H2-TEMPORAL-PSI-CREDIT; supersedes D-000017)

- **Statement:** as D-000016, plus the oracle-boundary clause: the task
  boundaries and ρ are no longer oracle-supplied.
  ConflictAdaptivePsiPlasticity detects conflict from its own readout
  agreement and self-switches trace decay on an UNLABELED alternating
  parity stream (MNIST, θ frozen): switch lag 1 episode at every flip,
  false-conflict rate ~1.5% of steady episodes, end-of-phase accuracy
  matching hand-tuned ρ=0.9 (0.92–0.95) while closed-form collapses to
  ~0.5 on inverted phases.
- **Supporting evidence:** E-000010 (bootstrap provenance), E-000022
  (X-TPC-001, non-conflicting), E-000024 (X-TPC-002, conflicting toy),
  E-000025 (X-TPC-003, conflicting MNIST + retrain_sgd control), E-000026
  (X-TAC-001, self-switching on unlabeled stream).
- **Failure boundaries:** as D-000016, plus: adaptive self-switching
  validated only on binary parity streams with clean label flips; no
  gradual-drift or multi-class stream tested.
- **Verification levels:** E-000022: 4, E-000024: 4, E-000025: 4,
  E-000026: 4.
- **Checks:** θ bitwise-frozen on all arms/seeds (all four probes);
  matched controls (closed-form ρ=1, fixed ρ=0.9, frozen-null,
  retrain_sgd); P1/P2/P3 of X-TAC-001 supported 3/3 seeds.
- **Belief interval at emission:** [0.45, 0.70], status open.
