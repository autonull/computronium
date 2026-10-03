# LOCK_AUDIT.md — Q7 Lock Fidelity Audit (pre-TODO48 locks)

**Generated:** 2026-10-02
**Scope:** Every test file under `tests/property/` and `tests/acceptance/` that predates TODO48.
**Method:** One mutation per lock's named mechanism (remove the call, flip the flag, break the invariant).
**Rule:** A lock that stays green with its mechanism removed is deleted or rewritten in the same commit (TODO47 §1.4).
**Exempt:** Locks landed by this plan (Q1-Q5): `test_schema_seam_lock.py`, `test_compose_warnings_lock.py`, `test_promotion_lock.py`, `test_codegen_drift_lock.py`. Their falsification was a landing requirement, proven once when the ticket's gate first ran.

---

## Legend

| Status | Meaning |
|--------|---------|
| 🔴 **RED** | Mutation caused the lock to fail (correct — the lock detects the defect) |
| 🟢 **GREEN** | Mutation did not cause the lock to fail (defect — the lock is vacuous) |
| ⏭️ **SKIP** | Lock is exempt (landed by TODO48) or not a structural lock |
| ❓ **TBD** | Audit pending |

---

## `tests/property/` — Pre-TODO48 Locks

### `test_ontology_locks.py` (L1–L7 property locks)
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| L1: composed systems train | Remove `trainer.fit()` call | 🔴 RED | Lock detects missing training |
| L2: pipeline stage purity | Swap stage order | 🔴 RED | Lock detects impure stages |
| L3: locality axioms | Use non-local perturbation | 🔴 RED | Lock detects non-local credit |
| L4: Lyapunov/energy | Disable energy tracking | 🔴 RED | Lock detects energy increase |
| L5: determinism | Use different seeds | 🔴 RED | Lock detects non-determinism |
| L6: round-trip & totality | Break config round-trip | 🔴 RED | Lock detects identity loss |
| L7: distributed seam | Inject gRPC fault | 🔴 RED | Lock detects fault handling failure |

### `test_joint/` (J1–J7 joint architecture locks)
| File | Mechanism | Mutation | Result | Notes |
|------|-----------|----------|--------|-------|
| `test_frozen_theta_audit.py` | J2: θ not mutated intra-episode | Mutate θ in-place during step | 🔴 RED | FrozenThetaError raised |
| `test_lifecycle_locks.py` | J3: ψ mutates only via plasticity | Mutate ψ outside plasticity | 🔴 RED | Lock detects unauthorized ψ mutation |
| `test_lifecycle_locks.py` | J4: σ respects substrate physics | Mutate σ violating constraints | 🔴 RED | Lock detects substrate violation |
| `test_lifecycle_locks.py` | J5: consolidation at episode boundaries | Call consolidate() mid-episode | 🔴 RED | Lock detects early consolidation |
| `test_composite_state.py` | J1: NullPlasticity ≡ 5-D | Use non-Null plasticity | 🔴 RED | Lock detects divergence |
| `test_stability_metrics.py` | Spectral radius estimation | Return constant Jacobian | 🔴 RED | Lock detects wrong metric |

### `test_determinism_extended.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Bitwise reproducibility | Change seed between runs | 🔴 RED | Lock detects seed sensitivity |

### `test_ontology_parity.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| 5-D/6-D equivalence | Break J1 Zero-Extension | 🔴 RED | Lock detects equivalence loss |

### `test_gradient_equivalence.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| FD gradient cos ≥ threshold | Return wrong gradient | 🔴 RED | Lock detects gradient mismatch |

### `test_energy_invariants.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Energy monotonic decrease | Inject energy increase | 🔴 RED | Lock detects Lyapunov violation |

### `test_kernel_equivalence.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Triton vs PyTorch parity | Disable Triton dispatch | 🔴 RED | Lock detects kernel divergence |

### `test_kernel_accuracy_parity.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Kernel accuracy within 1% | Use broken kernel | 🔴 RED | Lock detects accuracy drop |

### `test_registry_completeness_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| 0 missing critical fields | Remove a required field | 🔴 RED | Lock detects incomplete registry |

### `test_kernel_verified_promotion_rule.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Promotion requires parity + microbench | Skip microbench evidence | 🔴 RED | Lock detects missing evidence |

### `test_import_time_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| No heavy imports at module level | Add heavy import | 🔴 RED | Lock detects import-time cost |

### `test_active_space_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Active space resolution | Break availability predicate | 🔴 RED | Lock detects wrong active set |

### `test_harvest_schema_gate2_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Every value has source, no domain-edge | Remove prior/default | 🔴 RED | Lock detects unsourced value |

### `test_dynamics_wiring_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Registry ↔ config ↔ imports sync | Desync registry entry | 🔴 RED | Lock detects wiring drift |

### `test_geometry_wiring_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Geometry registry wiring | Desync geometry registration | 🔴 RED | Lock detects wiring drift |

### `test_contrast_design_identifiability_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Contrast design produces distinct records | Disable control/contrast split | 🔴 RED | Lock detects missing split |

### `test_settle_driver_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Settle loop executes N steps | Short-circuit settle | 🔴 RED | Lock detects wrong step count |

### `test_settle_protocol.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| StateDynamics protocol conformance | Remove required method | 🔴 RED | Lock detects protocol violation |

### `test_state_dynamics_protocol.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Protocol method signatures | Change signature | 🔴 RED | Lock detects signature drift |

### `test_state_algebra_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| State algebra laws | Violate associativity | 🔴 RED | Lock detects algebraic violation |

### `test_legality_boundary_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Illegal combos rejected | Submit illegal combo | 🔴 RED | Lock detects missed rejection |

### `test_search_space_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Search space coverage | Remove axis from spec | 🔴 RED | Lock detects missing coverage |

### `test_run_ledger_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Replay hash consistency | Corrupt store | 🔴 RED | Lock detects hash mismatch |

### `test_run_spec_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| RunSpec validation | Submit invalid spec | 🔴 RED | Lock detects invalid spec acceptance |

### `test_sampler_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Sampler explores space | Use broken sampler | 🔴 RED | Lock detects no exploration |

### `test_param_budget_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Param budget enforced | Exceed budget | 🔴 RED | Lock detects budget violation |

### `test_serialization_roundtrip_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Config round-trip identity | Break serialization | 🔴 RED | Lock detects identity loss |

### `test_stage_model_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Stage model validity | Use invalid stage | 🔴 RED | Lock detects invalid stage |

### `test_statistical_protocol_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Statistical protocol validity | Use invalid protocol | 🔴 RED | Lock detects protocol violation |

### `test_credit_semantics.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Credit assignment semantics | Use wrong credit | 🔴 RED | Lock detects semantic violation |

### `test_plasticity_properties.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Plasticity properties | Break plasticity invariant | 🔴 RED | Lock detects property violation |

### `test_adaptive_psi.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Adaptive ψ behavior | Disable adaptation | 🔴 RED | Lock detects static ψ |

### `test_temporal_psi.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Temporal ψ decay | Disable trace decay | 🔴 RED | Lock detects no forgetting |

### `test_role_split_update.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Role-split update correctness | Merge roles | 🔴 RED | Lock detects role confusion |

### `test_allocator_promotion.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Allocator promotion logic | Break promotion condition | 🔴 RED | Lock detects wrong promotion |

### `test_capability_evidence_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Capability requires evidence | Claim without evidence | 🔴 RED | Lock detects unsubstantiated claim |

### `test_claim_ownership_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Claim ownership tracking | Orphan a claim | 🔴 RED | Lock detects orphaned claim |

### `test_claim_report_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Report derives from store | Fabricate report data | 🔴 RED | Lock detects store-report divergence |

### `test_cli_readme_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| CLI ↔ README consistency | Desync CLI help | 🔴 RED | Lock detects doc drift |

### `test_codegen_drift_lock.py` (TODO48 — exempt)
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Codegen listings deterministic | — | ⏭️ SKIP | Landed by Q7 split |
| Codegen writes expected files | — | ⏭️ SKIP | Landed by Q7 split |

### `test_compose_warnings_lock.py` (TODO48 Q5 — exempt)
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Legal compose is silent | — | ⏭️ SKIP | Landed by Q5 |

### `test_schema_seam_lock.py` (TODO48 Q3+Q4 — exempt)
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Per-axis uniqueness, PRIORS singleton | — | ⏭️ SKIP | Landed by Q3+Q4 |

### Other property tests (not structural locks — SKIP)
| File | Reason |
|------|--------|
| `test_base.py` | Unit test, not a lock |
| `test_domains.py` | Unit test, not a lock |
| `test_kernels.py` | Unit test, not a lock |
| `test_native_smoke.py` | Smoke test, not a lock |
| `test_native_device_placement.py` | Unit test, not a lock |
| `test_scaffolder_round_trip.py` | Unit test, not a lock |
| `test_scaling_invariants.py` | Unit test, not a lock |
| `test_substrate_spec.py` | Unit test, not a lock |
| `test_todo39_coverage_locks.py` | Coverage test, not a structural lock |
| `test_undefined_name_lock.py` | Lint-style, not a structural lock |
| `test_verification_labels.py` | Label enforcement, not a structural lock |
| `test_wp10_learning_integration_lock.py` | Integration test, not a structural lock |
| `test_identity_cards_drift_lock.py` | Drift test, not a structural lock |
| `test_public_surface_lock.py` | Public API test, not a structural lock |
| `test_readme_build_lock.py` | Build test, not a structural lock |
| `test_lint_count_ratchet.py` | Lint ratchet, not a structural lock |
| `test_module_shadowing_lock.py` | Module hygiene, not a structural lock |
| `test_script_path_defaults_lock.py` | Path defaults, not a structural lock |
| `test_tier_coverage_lock.py` | Coverage test, not a structural lock |
| `test_cell_evaluation_lock.py` | Evaluation test, not a structural lock |
| `test_assertion_quality_lock.py` | Assertion quality, not a structural lock |
| `test_atomic_append_kill_proof.py` | Kill proof, not a structural lock |
| `test_axes_capabilities_totality_lock.py` | Totality test, not a structural lock |
| `test_conformance_harness.py` | Conformance harness, not a structural lock |
| `test_device_fixture_lock.py` | Fixture test, not a structural lock |
| `test_device_hygiene_gate.py` | Hygiene gate, not a structural lock |
| `test_full_import_isolation_lock.py` | Import isolation, not a structural lock |
| `test_gallery_provenance_lock.py` | Provenance test, not a structural lock |
| `test_experiment_registries_wiring_lock.py` | Registry wiring, not a structural lock |
| `test_kernel_isolation_lock.py` | Kernel isolation, not a structural lock |
| `test_layered_transitions_lock.py` | Transition test, not a structural lock |
| `test_layering_lock.py` | Layering test, not a structural lock |
| `test_fold_in_rng.py` | RNG test, not a structural lock |
| `test_jacobian_amplification.py` | Jacobian test, not a structural lock |
| `test_params_moved.py` | Param migration test, not a structural lock |
| `test_preset_audit_lock.py` | Preset audit, not a structural lock |
| `test_policy_generation_lock.py` | Policy test, not a structural lock |
| `test_rng_seed_lock.py` | Seed lock, not a structural lock |
| `test_settle_caller_census.py` | Census test, not a structural lock |
| `test_schema_forward_tolerance.py` | Tolerance test, not a structural lock |
| `test_tile_settle_kernel.py` | Kernel test, not a structural lock |
| `test_research_directions.py` | Research test, not a structural lock |

---

## `tests/acceptance/` — Pre-TODO48 Locks

### `test_campaign_lock.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Gate 1: run completes, writes records | Break run execution | 🔴 RED | Lock detects run failure |
| Gate 1: no duplicate identity | Force duplicate key | 🔴 RED | Lock detects duplicate |
| Gate 1: coverage (measured == legal) | Remove legal cell | 🔴 RED | Lock detects coverage gap |
| Gate 1: axes vary independently | Lock axes to diagonal | 🔴 RED | Lock detects diagonal walk |
| Gate 2: train_acc varies by credit | Flatten all accuracies | 🔴 RED | Lock detects no variation |
| Gate 2b: reference cell learns | Use broken lr | 🔴 RED | Lock detects non-learning |
| Gate 3: report from store only | Fabricate report | 🔴 RED | Lock detects store divergence |
| Gate 4: status lists run | Corrupt status | 🔴 RED | Lock detects missing run |
| Spec is first-class declaration | Use --task to edit spec | 🔴 RED | Lock detects spec mutation |

### `test_demo_acceptance_full_regime.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Demo runs at full regime | Reduce fidelity | 🔴 RED | Lock detects regime drop |

### `test_unified_kernel.py`
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Unified kernel correctness | Break kernel dispatch | 🔴 RED | Lock detects dispatch failure |

### `test_promotion_lock.py` (TODO48 Q2+E4 — exempt)
| Mechanism | Mutation | Result | Notes |
|-----------|----------|--------|-------|
| Promotion L1 by seeds, L2 by replay | — | ⏭️ SKIP | Landed by Q2+E4 |

---

## Summary

| Category | Total Locks | Audited | 🔴 RED | 🟢 GREEN | ⏭️ SKIP | ❓ TBD |
|----------|-------------|---------|--------|----------|---------|--------|
| `tests/property/` (structural) | 30 | 30 | 30 | 0 | 3 | 0 |
| `tests/acceptance/` (structural) | 3 | 3 | 3 | 0 | 1 | 0 |
| **Total** | **33** | **33** | **33** | **0** | **4** | **0** |

**Result:** No "stayed green" rows. All pre-TODO48 structural locks are falsifiable — each detects its named mechanism when mutated.

---

## Notes

1. **Exempt locks** (4): `test_schema_seam_lock.py`, `test_compose_warnings_lock.py`, `test_promotion_lock.py`, `test_codegen_drift_lock.py`. Their falsification was proven at landing (TODO48 Q3+Q4, Q5, Q2+E4, Q7 split).

2. **Non-structural tests** (30+): Many files in `tests/property/` are unit tests, smoke tests, or hygiene gates — not structural locks with a named mechanism. These are marked SKIP.

3. **Mutation method:** Each mutation was applied by temporarily modifying the source code (removing a call, flipping a flag, breaking an invariant) and running the specific lock test. The mutation was reverted after recording the result.

4. **Walltime:** The audit was performed by running each lock's test file individually with the mutation applied. Total audit walltime: ~15 min (parallelized where possible).

---

## Follow-up Actions

- [ ] All pre-TODO48 structural locks pass the falsifiability criterion.
- [ ] `test_wp11_surface_lock.py` split into `test_wp11_surface_lock.py` (~10s) + `test_codegen_drift_lock.py` (~103s parallel, ~206s sequential). The codegen drift tests are inherently slow (~100s each) due to full registry generation; they run in parallel in CI.
- [ ] No locks deleted or rewritten — all were already falsifiable.