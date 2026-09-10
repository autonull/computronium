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
