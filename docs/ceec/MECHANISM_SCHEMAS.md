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
| local-credit-adaptive-inverse | B-H1-ADAPTIVE-LOCAL-INVERSES | awaiting X-ALI-001 |
| temporal-psi-credit | B-H2-TEMPORAL-PSI-CREDIT | awaiting X-TPC-001 |
| stable-transient-amplification | B-H3-STABLE-TRANSIENT-AMPLIFICATION | awaiting X-STA-001 |
| routing-sparsity-efficiency | B-H4-ROUTING-SPARSITY-EFFICIENCY | awaiting X-RSE-001 |
| update-rule-specialization | B-H5-UPDATE-RULE-SPECIALIZATION | awaiting X-USU-001 |

Schemas will be emitted as `derived` objects of type `mechanism_schema` by
the reporting pipeline once the first gated belief updates land.
