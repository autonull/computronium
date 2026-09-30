# Capabilities Registry

Generated: 2026-09-30T13:23:50.133084
Total: 88 capabilities

| ID | Name | Kind | Required | Stage | Owner | Verifying Test | Flags | Status |
|----|------|------|----------|-------|-------|----------------|-------|--------|
| C1 | Six-axis coordinate space | core | ✓ | S1_FRAME | schema | tests/property/test_experiment_registries_wiring_lock.py::test_all_registries_dict_completeness | axis, coordinate | active |
| C10 | Evidence-driven allocation | core | ✓ | S10_DECIDE | allocator | tests/property/test_statistical_protocol_lock.py::test_allocation_promotion | allocation, evidence_driven | active |
| C11 | Replay and resume | core | ✓ | S6_TRAIN | replay | tests/property/test_atomic_append_kill_proof.py::test_monotonic_seq_across_concurrent | replay, resume | active |
| C12 | Three-tier status model | core | ✓ | S7_MEASURE | evidence | tests/property/test_statistical_protocol_lock.py::test_three_tier_status_model | status, three_tier | active |
| C13 | Claim eligibility predicates | core | ✓ | S7_MEASURE | evidence | tests/property/test_statistical_protocol_lock.py::test_claim_eligible_predicate | claims, predicates | active |
| C14 | Failure intelligence | core | ✓ | S7_MEASURE | evidence | tests/property/test_statistical_protocol_lock.py::test_failure_clustering | failure, clustering | active |
| C15 | Unified artifact storage | core | ✓ | S8_RECORD | artifacts | tests/property/test_atomic_append_kill_proof.py::test_atomic_append_with_artifacts | artifacts, atomic | active |
| C16 | Vector retrieval | core | ✓ | S8_RECORD | store | tests/property/test_statistical_protocol_lock.py::test_vector_retrieval_bruteforce | vector, vss_optional | active |
| C17 | Prior registry | core | ✓ | S1_FRAME | priors | tests/property/test_experiment_registries_wiring_lock.py::test_priors_registry_seeded | priors, ruler_lr | active |
| C18 | Surrogate policy wrapper | core | ✓ | S5_COMPOSE | learning | tests/property/test_statistical_protocol_lock.py::test_surrogate_policy_wrapper | surrogate, acquisition | active |
| C19 | I(C,U) metamodel | core | ✓ | S5_COMPOSE | learning | tests/property/test_statistical_protocol_lock.py::test_icu_leakage_guard | icu, leakage_guard | active |
| C2 | Unified record schema | core | ✓ | S2_SPACE | schema | tests/property/test_dynamics_wiring_lock.py::test_record_schema_valid | schema, record | active |
| C20 | Reasoning records | core | ✓ | S1_FRAME | learning | tests/property/test_statistical_protocol_lock.py::test_reasoning_provenance_linkage | reasoning, provenance | active |
| C21 | torch.compile settle loop | acceleration | ✗ | S6_TRAIN | dynamics | tests/property/test_settle_driver_lock.py::test_compiled_settle_bitwise_equal | compilation, experimental | active |
| C22 | Gradient checkpointing | acceleration | ✗ | S6_TRAIN | dynamics | tests/property/test_settle_driver_lock.py::test_gradient_checkpointing_memory | checkpointing, memory | active |
| C23 | Gain control homeostasis | acceleration | ✗ | S6_TRAIN | dynamics | tests/property/test_settle_driver_lock.py::test_gain_control_unit_rms | gain_control, homeostasis | active |
| C24 | KV cache for transformer | acceleration | ✗ | S6_TRAIN | geometry | tests/property/test_geometry_wiring_lock.py::test_transformer_kv_cache | kv_cache, transformer | active |
| C25 | Async orchestration | acceleration | ✗ | S6_TRAIN | backends | tests/property/test_experiment_registries_wiring_lock.py::test_async_backend_works | async, taskgroup | active |
| C26 | Multiprocess backend | scaling | ✗ | S6_TRAIN | backends | tests/property/test_experiment_registries_wiring_lock.py::test_multiprocess_backend | multiprocess, parallel | active |
| C27 | Multi-GPU DDP/FSDP | scaling | ✗ | S6_TRAIN | backends | tests/property/test_experiment_registries_wiring_lock.py::test_ddp_fsdp_works | ddp, fsdp, gpu_only | active |
| C28 | P2P gossip cluster | scaling | ✗ | S6_TRAIN | backends | tests/property/test_experiment_registries_wiring_lock.py::test_p2p_cluster_works | p2p, kademlia | active |
| C29 | Batch vectorization | scaling | ✗ | S6_TRAIN | backends | tests/property/test_experiment_registries_wiring_lock.py::test_batch_vectorization | vectorization, batch | active |
| C3 | Content-addressed records | core | ✓ | S8_RECORD | store | tests/property/test_atomic_append_kill_proof.py::test_atomic_transaction_rollback | content_addressed, dedup | active |
| C30 | Pipeline parallelism | scaling | ✗ | S6_TRAIN | backends | tests/property/test_experiment_registries_wiring_lock.py::test_pipeline_parallelism | pipeline_parallel, experimental | active |
| C31 | Computational reproducibility | reproducibility | ✓ | S11_REPORT | replay | tests/property/test_scientific_validity_protocol_lock.py::test_replayable_reproducibility | replayable, computational | active |
| C32 | Scientific reproducibility | reproducibility | ✗ | S11_REPORT | benchmarks | tests/property/test_scientific_validity_protocol_lock.py::test_scientific_reproducibility | scientific, independent_env | active |
| C33 | Reproducibility class tracking | reproducibility | ✓ | S7_MEASURE | evidence | tests/property/test_scientific_validity_protocol_lock.py::test_reproducibility_classes | reproducibility_class, tracking | active |
| C34 | Assessment procedure versioning | reproducibility | ✓ | S7_MEASURE | evidence | tests/property/test_statistical_protocol_lock.py::test_assessment_procedure_versioning | assessment, procedure | active |
| C35 | Data origin tagging | reproducibility | ✓ | S3_SCHEDULE | schema | tests/property/test_scientific_validity_protocol_lock.py::test_data_origin_tags | data_origin, split | active |
| C36 | Transfer provenance tracking | reproducibility | ✓ | S1_FRAME | learning | tests/property/test_statistical_protocol_lock.py::test_transfer_provenance | transfer, provenance | active |
| C37 | Matched-cost comparison guard | governance | ✓ | S7_MEASURE | evidence | tests/property/test_statistical_protocol_lock.py::test_comparison_guard_rejects_mismatched | comparison, guard | active |
| C38 | Stratification guard | governance | ✓ | S7_MEASURE | evidence | tests/property/test_statistical_protocol_lock.py::test_stratification_guard_hardware_class | stratification, hardware_class | active |
| C39 | I(C,U) leakage audit | governance | ✓ | S7_MEASURE | learning | tests/property/test_statistical_protocol_lock.py::test_icu_calibration_audit | icu, leakage, audit | active |
| C4 | Measurement key deduplication | core | ✓ | S8_RECORD | store | tests/property/test_atomic_append_kill_proof.py::test_duplicate_measurement_key_dedup | dedup, measurement_key | active |
| C40 | Alert predicates | governance | ✓ | S10_DECIDE | evidence | tests/property/test_statistical_protocol_lock.py::test_alert_predicates | alerts, predicates | active |
| C41 | Promotion predicates | governance | ✓ | S10_DECIDE | evidence | tests/property/test_statistical_protocol_lock.py::test_promotion_predicates | promotion, claims | active |
| C42 | Effect-size protocol | governance | ✓ | S7_MEASURE | evidence | tests/property/test_statistical_protocol_lock.py::test_effect_size_protocol | effect_size, cohens_d | active |
| C43 | Budget tier system | governance | ✓ | S3_SCHEDULE | budget | tests/property/test_statistical_protocol_lock.py::test_budget_tier_system | budget, tier | active |
| C44 | Run controller | governance | ✓ | S11_REPORT | operations | tests/property/test_public_surface_lock.py::test_run_controller_pause_resume | operations, control | active |
| C45 | Service manager | governance | ✗ | S9_ATTRIBUTE | operations | tests/property/test_public_surface_lock.py::test_service_manager_webhooks | service, webhooks | active |
| C46 | Conformance harness | governance | ✓ | S11_REPORT | surface | tests/property/test_public_surface_lock.py::test_conformance_harness_gate | conformance, ci | active |
| C47 | Currency lock | governance | ✓ | S11_REPORT | surface | tests/property/test_public_surface_lock.py::test_currency_lock_flags | currency, flags | active |
| C48 | Question-first entry | governance | ✓ | S1_FRAME | policy | tests/property/test_public_surface_lock.py::test_synthesis_policy_question_first | synthesis, question_first | active |
| C49 | Surrogate-driven acquisition | learning | ✗ | S5_COMPOSE | learning | tests/property/test_statistical_protocol_lock.py::test_surrogate_acquisition_ei | surrogate, ei | active |
| C5 | Cell key grouping | core | ✓ | S2_SPACE | schema | tests/property/test_scientific_validity_protocol_lock.py::test_replication_key_groups_seeds | cell_key, replication | active |
| C50 | Cross-task transfer | learning | ✗ | S1_FRAME | learning | tests/property/test_statistical_protocol_lock.py::test_cross_task_transfer | transfer, cross_task | active |
| C51 | Prior single-source accessor | learning | ✓ | S1_FRAME | priors | tests/property/test_statistical_protocol_lock.py::test_prior_single_source | priors, single_source | active |
| C52 | Run-scoped ICU/Reasoning | learning | ✓ | S1_FRAME | learning | tests/property/test_experiment_registries_wiring_lock.py::test_no_global_singletons | icu, reasoning, k10 | active |
| C53 | Reasoning persistence | learning | ✓ | S1_FRAME | learning | tests/property/test_statistical_protocol_lock.py::test_reasoning_persistence | reasoning, persistence | active |
| C54 | Warm-start from prior runs | learning | ✗ | S5_COMPOSE | learning | tests/property/test_statistical_protocol_lock.py::test_warm_start_prior_runs | warm_start, transfer | active |
| C55 | Coordinate-wide surrogate | learning | ✗ | S5_COMPOSE | learning | tests/property/test_statistical_protocol_lock.py::test_coordinate_wide_surrogate | surrogate, coordinate_wide | active |
| C56 | I(C,U) feature encoder | learning | ✗ | S5_COMPOSE | learning | tests/property/test_statistical_protocol_lock.py::test_icu_feature_encoder | icu, feature_encoder | active |
| C57 | Achieved-seed claim eligibility | learning | ✓ | S7_MEASURE | evidence | tests/property/test_statistical_protocol_lock.py::test_achieved_seed_claim | claims, achieved_seeds | active |
| C58 | Multi-objective Pareto | learning | ✓ | S7_MEASURE | objectives | tests/property/test_statistical_protocol_lock.py::test_multi_objective_pareto | pareto, multi_objective | active |
| C59 | Substrate-aware objectives | learning | ✗ | S7_MEASURE | substrate | tests/property/test_statistical_protocol_lock.py::test_substrate_aware_objectives | substrate, objectives | active |
| C6 | Schema versioning | core | ✓ | S1_FRAME | schema | tests/property/test_experiment_registries_wiring_lock.py::test_schema_versioning_fail_closed | versioning, unknown_field | active |
| C60 | Frozen-θ ψ adaptation | learning | ✗ | S10_DECIDE | update | tests/property/test_statistical_protocol_lock.py::test_frozen_theta_psi_adapt | frozen_theta, psi | active |
| C61 | NTM geometry | core | ✗ | S5_COMPOSE | geometry | tests/integration/test_demo_ntm.py | ntm, gate1_accepted, experimental | active |
| C62 | NCA geometry | core | ✗ | S5_COMPOSE | geometry | tests/integration/test_demo_nca.py | nca, gate1_accepted, experimental | active |
| C63 | PEPITA/LEMMA credit | core | ✗ | S5_COMPOSE | credit | tests/integration/test_demo_swap_credit.py | pepita, lemma, gate1_accepted | active |
| C64 | Holomorphic EP | core | ✗ | S5_COMPOSE | models_native | tests/integration/test_demo_holomorphic_ep.py | holomorphic, gate1_accepted | active |
| C65 | Directed EP | core | ✗ | S5_COMPOSE | models_native | tests/integration/test_demo_directed_ep.py | directed_ep, gate1_accepted | active |
| C66 | Finite-nudge EP | core | ✗ | S5_COMPOSE | models_native | tests/integration/test_demo_finite_nudge_ep.py | finite_nudge, gate1_accepted | active |
| C67 | Ternary EqProp | core | ✗ | S5_COMPOSE | models_native | tests/integration/test_demo_ternary_eqprop.py | ternary, eqprop, gate1_accepted | active |
| C68 | Momentum EqProp | core | ✗ | S5_COMPOSE | models_native | tests/integration/test_demo_momentum_eqprop.py | momentum, eqprop, gate1_accepted | active |
| C69 | Sparse EqProp | core | ✗ | S5_COMPOSE | models_native | tests/integration/test_demo_sparse_eqprop.py | sparse, eqprop, gate1_accepted | active |
| C7 | Legality engine | core | ✓ | S4_GATE | legality | tests/property/test_legality_boundary_lock.py::test_declared_constraints_have_proof | legality, void, defect | active |
| C70 | Diffusion EqProp | core | ✗ | S5_COMPOSE | models_native | tests/integration/test_demo_diffusion_eqprop.py | diffusion, eqprop, gate1_accepted | active |
| C71 | Routing plasticity | core | ✗ | S5_COMPOSE | plasticity | tests/integration/test_demo_swap_plasticity.py | routing, plasticity, gate1_accepted | active |
| C72 | Fast-weight plasticity | core | ✗ | S5_COMPOSE | plasticity | tests/integration/test_demo_swap_plasticity.py | fast_weight, plasticity, gate1_accepted | active |
| C73 | Substrate-coupled plasticity | core | ✗ | S5_COMPOSE | plasticity | tests/integration/test_demo_memristive.py | substrate_coupled, plasticity, gate1_accepted | active |
| C74 | Rule-state plasticity (Z3) | core | ✗ | S5_COMPOSE | plasticity | tests/integration/test_demo_z3_frozen_theta.py | z3, rule_state, gate1_accepted | active |
| C75 | Closed-form ridge plasticity | core | ✗ | S5_COMPOSE | plasticity | tests/integration/test_demo_closed_form_ridge.py | closed_form, ridge, gate1_accepted | active |
| C76 | Temporal ψ plasticity | core | ✗ | S5_COMPOSE | plasticity | tests/integration/test_demo_temporal_psi.py | temporal_psi, plasticity, gate1_accepted | active |
| C77 | CEEC core ledger | core | ✗ | S8_RECORD | ceec_core | packages/ceec-core/tests/test_ceec_ledger.py | ceec, ledger, platform | active |
| C78 | Psi-PEFT | core | ✗ | S10_DECIDE | psi_peft | packages/psi-peft/tests/test_psi_peft.py | psi_peft, platform | active |
| C79 | Local feedback projections | core | ✗ | S5_COMPOSE | local_feedback | packages/local-feedback/tests/test_local_feedback.py | local_feedback, platform | active |
| C8 | S1-S11 pipeline | core | ✓ | S1_FRAME | pipeline | tests/property/test_experiment_registries_wiring_lock.py::test_stage_registry_completeness | pipeline, stages | active |
| C80 | Stability guard | core | ✗ | S6_TRAIN | stability | packages/stability/tests/test_stability_guard.py | stability, guard, platform | active |
| C81 | Computronium Lab synthesis | core | ✗ | S1_FRAME | lab | packages/computronium-lab/tests/test_lab_synthesize.py | lab, synthesis, platform | active |
| C82 | Computronium Lab evolution | core | ✗ | S10_DECIDE | lab | packages/computronium-lab/tests/test_lab_evolution.py | lab, evolution, platform | active |
| C83 | Surface CLI dispatcher | core | ✓ | S11_REPORT | surface | tests/property/test_public_surface_lock.py::test_surface_cli_profiles | cli, surface | active |
| C84 | Report generator | core | ✓ | S11_REPORT | surface | tests/property/test_public_surface_lock.py::test_report_generator | report, export | active |
| C85 | Codegen from registries | core | ✗ | S11_REPORT | surface | tests/property/test_public_surface_lock.py::test_codegen_drift_lock | codegen, drift_lock | active |
| C86 | Documented-command conformance | core | ✓ | S11_REPORT | surface | tests/property/test_public_surface_lock.py::test_documented_command_conformance | conformance, cli | active |
| C87 | Gallery lock | core | ✓ | S11_REPORT | visualization | tests/integration/test_gallery_lock.py | gallery, manifest | active |
| C88 | Probe conventions | core | ✓ | S11_REPORT | probes | tests/property/test_public_surface_lock.py::test_probe_conventions | probes, conventions | active |
| C9 | Eight-policy catalog | core | ✓ | S3_SCHEDULE | policy | tests/property/test_experiment_registries_wiring_lock.py::test_policy_registry_has_eight | policy, catalog | active |