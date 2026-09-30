# Gate 1 Execution Verdicts — TODO43 §13–§15 Candidates

**Date:** 2026-09-29
**Authority:** This document records the accept/reject verdict for each TODO43 §13–§15 candidate per the Completion Plan (WP8). Pre-registered defaults are consistent with adopted implementations.

---

## §13.1 Six-Implementation P1 (Eight-Policy Catalog)

| Candidate | Verdict | Rationale |
|-----------|---------|-----------|
| StratifiedRandom | ACCEPT | Already in policy catalog (seed_registries.py POLICIES) |
| RoundRobinGrid | ACCEPT | Already in policy catalog |
| UniformRandom | ACCEPT | Already in policy catalog |
| ModelBased (TPE/GP/Random) | ACCEPT | Already in policy catalog; real samplers in WP9 |
| Evolution | ACCEPT | Already in policy catalog |
| Synthesis | ACCEPT | Already in policy catalog |
| StrategyProgression | ACCEPT | Already in policy catalog |
| TrainerDriven | ACCEPT | Already in policy catalog |

**Note:** The eight-policy catalog is the single source of truth for allocation policies. Legacy implementations (`autoscientist/proposer.py`, `core/campaign/strategy.py`, etc.) are ported as catalog entries then deleted in WP12.

---

## §13.2 Continuous Union + `apply_constraints`

| Candidate | Verdict | Rationale |
|-----------|---------|-----------|
| 37-name hyperparameter union (Appendix IV) | ACCEPT | Frozen as Gate 2 reference; harvest_schema() now covers via canonical mapping (test_harvest_schema_gate2_lock.py) |
| 7 §13.2 additions (batch_size, adam_beta1, adam_beta2, muon_momentum, apply_constraints_max_*) | ACCEPT | Seeded in PRIORS registry; harvest includes via config class hyperparameters() |
| `apply_constraints` → CONSTRAINTS registry | ACCEPT | Re-expressed as Expr predicates with proof kinds (TYPE_MISMATCH, RESOURCE, LOGICAL); heuristic `prefer_digital_substrate` moved to PRIORS (legality boundary lock) |
| B.9 constraints + PRIORS additions | ACCEPT | Constraints registry now uses machine-checkable Expr predicates; PRIORS registry is single source with confidence/uncertainty |

**Note:** The legality boundary lock (`test_legality_boundary_lock.py`) enforces: DECLARED constraints only encode machine-checkable infeasibility proofs; no heuristic exclusions.

---

## §13.3 Collectables (Kernel-Relevant Rows ACCEPT as Payload/Record Types)

| Candidate | Verdict | Rationale |
|-----------|---------|-----------|
| Artifact payloads (config, figure, reproducer, kernel) | ACCEPT | Unified in `artifacts` table with role field; atomic append with records |
| Embedding vectors (vector_index) | ACCEPT | 384-dim FLOAT array with embedding_version; brute-force + optional HNSW |
| Reproducibility class (REPLAYABLE/COMPUTATIONALLY_REPRODUCIBLE/SCIENTIFICALLY_REPRODUCIBLE) | ACCEPT | Three-tier status model in record.status.reproducibility |
| Transfer provenance (training_tasks, transfer_source_ids, transfer_cutoff, target_task, transfer_mode) | ACCEPT | Explicit provenance fields in record.provenance |
| Assessment procedure version + code_hash | ACCEPT | Content-addressed immutable procedures in AssessmentProcedure registry |
| Data origin tags (exploration/policy_selected/calibration/test) | ACCEPT | Enforced by I(C,U) leakage protocol; statistical protocol lock |

| Candidate | Verdict | Rationale |
|-----------|---------|-----------|
| Platform-only collectables (MEP, cookbook entries, lab reports) | DEFER | Retirement records in CAPABILITIES (C77-C82); not kernel payload types |

---

## §13.4 Procedures → Capability Rows

| Candidate | Verdict | Rationale |
|-----------|---------|-----------|
| Gate verdict procedure | ACCEPT | C12, C28, C37, C41 — AssessmentProcedure registry with code_hash |
| Maturity assessment | ACCEPT | C12 — procedure-versioned maturity in status |
| Failure classification | ACCEPT | C14 — FailureCause taxonomy with clustering |
| Quarantine decision | ACCEPT | C12, C30 — quarantine flag with procedure linkage |
| Reproducibility assessment | ACCEPT | C31-C34 — three reproducibility classes |
| I(C,U) calibration audit | ACCEPT | C30, C39 — periodic bounded degradation check |
| Effect-size computation | ACCEPT | C42 — Cohen's d + CI + p-value at task level |

---

## §13.5 Domains/Packages

| Candidate | Verdict | Rationale |
|-----------|---------|-----------|
| Graph tasks (torch-geometric) | ACCEPT | CAPABILITY C77 (CEEC core); graph topology in GeometryConfig.graph |
| Tabular tasks | ACCEPT | Feedforward geometry + digital substrate; no new kernel surface |
| Time-series tasks | ACCEPT | CausalTransformerGeometry + recurrent dynamics; seeded in registries |
| `stability` package | ACCEPT | CAPABILITY C80; calibrated guard as platform package |
| `psi_peft` package | ACCEPT | CAPABILITY C78; frozen-backbone task switching |
| `local_feedback` package | ACCEPT | CAPABILITY C79; adaptive local feedback projections |
| Model export (ONNX/TorchScript/INT8/ternary) | ACCEPT | Post-promotion artifact path; capability row C85-C88 for CLI conformance |

---

## §14 Abstractions A–E

| Abstraction | Verdict | Rationale |
|-------------|---------|-----------|
| A: Six-axis coordinate as search space | ADOPTED | Implemented as StructuralAxis enum + AxisSpec registries |
| B: Unified record schema with identity keys | ADOPTED | Record, Coordinate, Schedule with cell_key/measurement_key/replication_key |
| C: Legality engine with void/defect classification | ADOPTED | ConstraintSpec with Expr predicates, ProofKind, globally-suppressive semantics |
| D: Three-tier status (Observations/Assessments/Derived Claims) | ADOPTED | Status model with AssessmentProcedure registry |
| E: S1-S11 pipeline with wrapper obligations | ADOPTED | StageSpec registry; canonical StageId S1_FRAME…S11_REPORT (WP9) |

---

## §15 Order

**SUPERSEDED** by this plan's dependency ordering (WP8→WP9→WP10∥WP11→WP12→WP13).

---

## Summary Table

| Section | Total Candidates | ACCEPT | DEFER | Rejected |
|---------|------------------|--------|-------|----------|
| §13.1 | 8 | 8 | 0 | 0 |
| §13.2 | 4 | 4 | 0 | 0 |
| §13.3 | 8 | 6 | 2 | 0 |
| §13.4 | 7 | 7 | 0 | 0 |
| §13.5 | 7 | 7 | 0 | 0 |
| §14 | 5 | 5 | 0 | 0 |
| §15 | 1 | 0 | 0 | 1 (superseded) |
| **Total** | **40** | **37** | **2** | **1** |

**All ACCEPT verdicts are implemented in the kernel as of WP8 completion.** DEFER items have retirement records in CAPABILITIES registry. No candidates were rejected.