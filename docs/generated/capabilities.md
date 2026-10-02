# Capabilities Registry

Generated: 2026-10-02T11:30:28.628004
Total: 88 capabilities

| ID | Name | Kind | Required | Stage | Owner | Verifying Test | Evidence | Flags | Status |
|----|------|------|----------|-------|-------|----------------|----------|-------|--------|
| C1 | Six-axis coordinate space | core | ✓ | S1_FRAME | schema | tests/property/test_experiment_registries_wiring_lock.py::test_all_registries_dict_completeness | mechanism | axis, coordinate | active |
| C10 | Evidence-driven allocation | core | ✓ | S10_DECIDE | allocator | tests/property/test_allocator_promotion.py::TestEvidenceDrivenAllocation::test_first_observation_nominates_next_fidelity | mechanism | allocation, evidence_driven | active |
| C11 | Replay and resume | core | ✓ | S6_TRAIN | replay | tests/property/test_atomic_append_kill_proof.py::TestAtomicAppendKillProof::test_monotonic_seq_across_concurrent_writes | mechanism | replay, resume | active |
| C12 | Three-tier status model | core | ✓ | S7_MEASURE | evidence | tests/property/test_statistical_protocol_lock.py::TestClaimPredicates::test_claim_eligible_requires_l2_fidelity | mechanism | status, three_tier | active |
| C13 | Claim eligibility predicates | core | ✓ | S7_MEASURE | evidence | tests/property/test_statistical_protocol_lock.py::TestClaimPredicates::test_claim_eligible_requires_pass_verdict | mechanism | claims, predicates | active |
| C14 | Failure intelligence | core | ✓ | S7_MEASURE | evidence | tests/property/test_statistical_protocol_lock.py::TestAlertPredicates::test_alert_on_divergence | mechanism | failure, clustering | active |
| C15 | Unified artifact storage | core | ✓ | S8_RECORD | artifacts | tests/property/test_atomic_append_kill_proof.py::TestAtomicAppendKillProof::test_kill_during_atomic_append_no_partial_state | mechanism | artifacts, atomic | active |
| C16 | Vector retrieval | core | ✓ | S8_RECORD | store | tests/property/test_statistical_protocol_lock.py::TestStoreIntegration::test_store_supports_vector_index | mechanism | vector, vss_optional | active |
| C17 | Prior registry | core | ✓ | S1_FRAME | priors | tests/property/test_active_space_lock.py::test_every_declared_prior_resolves | mechanism | priors, ruler_lr | active |
| C18 | Surrogate policy wrapper | core | ✓ | S5_COMPOSE | learning | tests/property/test_wp10_learning_integration_lock.py::TestSurrogateStoreWiring::test_training_split_excludes_calibration_test | mechanism | surrogate, acquisition | active |
| C19 | I(C,U) metamodel | core | ✓ | S5_COMPOSE | learning | tests/property/test_statistical_protocol_lock.py::TestDataSplitProtocol::test_leakage_detection_calibration_in_training | mechanism | icu, leakage_guard | active |
| C2 | Unified record schema | core | ✓ | S2_SPACE | schema | tests/property/test_dynamics_wiring_lock.py::test_registry_classes_round_trip_to_spec_from_spec | mechanism | schema, record | active |
| C20 | Reasoning records | core | ✓ | S1_FRAME | learning | tests/property/test_scientific_validity_protocol_lock.py::TestDataOriginAndTransferProvenance::test_provenance_roundtrip | mechanism | reasoning, provenance | active |
| C21 | torch.compile settle loop | acceleration | ✗ | S6_TRAIN | dynamics | tests/integration/test_compiled_settle.py | mechanism | compilation, experimental | active |
| C22 | Gradient checkpointing | acceleration | ✗ | S6_TRAIN | dynamics | tests/property/test_settle_driver_lock.py::test_gradient_checkpointing_memory | shape | checkpointing, memory | unverified |
| C23 | Gain control homeostasis | acceleration | ✗ | S6_TRAIN | dynamics | tests/property/test_settle_driver_lock.py::test_gain_control_unit_rms | shape | gain_control, homeostasis | unverified |
| C24 | KV cache for transformer | acceleration | ✗ | S6_TRAIN | geometry | tests/property/test_geometry_wiring_lock.py::test_transformer_kv_cache | shape | kv_cache, transformer | unverified |
| C25 | Async orchestration | acceleration | ✗ | S6_TRAIN | backends | tests/property/test_experiment_registries_wiring_lock.py::test_async_backend_works | shape | async, taskgroup | unverified |
| C26 | Multiprocess backend | scaling | ✗ | S6_TRAIN | backends | tests/property/test_experiment_registries_wiring_lock.py::test_multiprocess_backend | shape | multiprocess, parallel | unverified |
| C27 | Multi-GPU DDP/FSDP | scaling | ✗ | S6_TRAIN | backends | tests/property/test_experiment_registries_wiring_lock.py::test_ddp_fsdp_works | shape | ddp, fsdp, gpu_only | unverified |
| C28 | P2P gossip cluster | scaling | ✗ | S6_TRAIN | backends | tests/property/test_experiment_registries_wiring_lock.py::test_p2p_cluster_works | shape | p2p, kademlia | unverified |
| C29 | Batch vectorization | scaling | ✗ | S6_TRAIN | backends | tests/property/test_experiment_registries_wiring_lock.py::test_batch_vectorization | shape | vectorization, batch | unverified |
| C3 | Content-addressed records | core | ✓ | S8_RECORD | store | tests/property/test_atomic_append_kill_proof.py::TestAtomicAppendKillProof::test_append_with_artifacts_atomic_on_exception | mechanism | content_addressed, dedup | active |
| C30 | Pipeline parallelism | scaling | ✗ | S6_TRAIN | backends | tests/property/test_experiment_registries_wiring_lock.py::test_pipeline_parallelism | shape | pipeline_parallel, experimental | unverified |
| C31 | Computational reproducibility | reproducibility | ✓ | S11_REPORT | replay | tests/property/test_scientific_validity_protocol_lock.py::TestReproducibilityClasses::test_reproducibility_class_enum | shape | replayable, computational | active |
| C32 | Scientific reproducibility | reproducibility | ✗ | S11_REPORT | benchmarks | tests/property/test_scientific_validity_protocol_lock.py::test_scientific_reproducibility | shape | scientific, independent_env | unverified |
| C33 | Reproducibility class tracking | reproducibility | ✓ | S7_MEASURE | evidence | tests/property/test_scientific_validity_protocol_lock.py::TestReproducibilityClasses::test_status_requires_reproducibility_class | mechanism | reproducibility, tracking | active |
| C34 | Data origin tags | reproducibility | ✓ | S3_SCHEDULE | evidence | tests/property/test_statistical_protocol_lock.py::TestDataSplitProtocol::test_no_leakage_clean_split | mechanism | data_origin, i_cu | active |
| C35 | Transfer provenance | reproducibility | ✓ | S1_FRAME | evidence | tests/property/test_scientific_validity_protocol_lock.py::TestDataOriginAndTransferProvenance::test_transfer_mode_enum | shape | transfer, provenance | active |
| C36 | Assessment procedure versioning | reproducibility | ✓ | S7_MEASURE | evidence | tests/property/test_scientific_validity_protocol_lock.py::TestReproducibilityClasses::test_status_requires_assessment_procedure_version | mechanism | assessment, procedure | active |
| C37 | Comparison guard | governance | ✓ | S10_DECIDE | evidence | tests/property/test_statistical_protocol_lock.py::TestComparisonGuards::test_matched_cost_comparison | mechanism | comparison, guard | active |
| C38 | Stratification guard | governance | ✓ | S10_DECIDE | evidence | tests/property/test_statistical_protocol_lock.py::TestComparisonGuards::test_same_hardware_class_for_walltime | mechanism | stratification, hardware_class | active |
| C39 | ICU calibration audit | governance | ✓ | S10_DECIDE | learning | tests/property/test_wp10_learning_integration_lock.py::TestSurrogateStoreWiring::test_effect_size_guards | mechanism | icu, calibration | active |
| C4 | Measurement key deduplication | core | ✓ | S8_RECORD | store | tests/property/test_atomic_append_kill_proof.py::TestAtomicAppendKillProof::test_append_with_artifacts_atomic_on_duplicate_measurement | mechanism | dedup, measurement_key | active |
| C40 | Alert predicates | governance | ✓ | S7_MEASURE | evidence | tests/property/test_statistical_protocol_lock.py::TestAlertPredicates::test_alert_on_resource_exhaustion | mechanism | alerts, predicates | active |
| C41 | Promotion predicates | governance | ✓ | S10_DECIDE | evidence | tests/property/test_statistical_protocol_lock.py::TestClaimPredicates::test_promoted_requires_l2_maturity | mechanism | promotion, maturity | active |
| C42 | Effect size protocol | governance | ✓ | S10_DECIDE | evidence | tests/property/test_statistical_protocol_lock.py::TestEffectSizeProtocol::test_effect_size_reports_cohens_d_with_ci | mechanism | effect_size, cohens_d | active |
| C43 | Budget tier system | governance | ✓ | S3_SCHEDULE | evidence | tests/property/test_statistical_protocol_lock.py::TestEffectSizeProtocol::test_budget_tier_matching_required | mechanism | budget_tier, comparison | active |
| C44 | Surface CLI profiles | governance | ✓ | S1_FRAME | surface | tests/property/test_wp11_surface_lock.py::TestDocumentedCommands::test_run_profiles_canonical_stages | shape | cli, profiles | active |
| C45 | Service manager | governance | ✗ | S9_ATTRIBUTE | operations | tests/property/test_public_surface_lock.py::test_service_manager_webhooks | shape | service, webhooks | unverified |
| C46 | Conformance harness gate | governance | ✓ | S11_REPORT | surface | tests/property/test_conformance_harness.py::TestConformanceHarness::test_required_capabilities_have_verifying_tests | mechanism | conformance, ci_gate | active |
| C47 | Currency lock flags | governance | ✓ | S11_REPORT | surface | tests/property/test_conformance_harness.py::TestFlagProjectionLock::test_flag_projection_totality | mechanism | currency_lock, flags | active |
| C48 | Synthesis policy question-first | governance | ✓ | S1_FRAME | surface | tests/property/test_wp11_surface_lock.py::TestQuestionFirst::test_spec_shape | mechanism | synthesis, question_first | active |
| C49 | Surrogate-driven acquisition | learning | ✗ | S5_COMPOSE | learning | tests/property/test_statistical_protocol_lock.py::test_surrogate_acquisition_ei | shape | surrogate, ei | unverified |
| C5 | Cell key grouping | core | ✓ | S2_SPACE | schema | tests/property/test_atomic_append_kill_proof.py::TestAtomicAppendKillProof::test_concurrent_append_dedup_by_measurement_key | mechanism | cell_key, replication | active |
| C50 | Cross-task transfer | learning | ✗ | S1_FRAME | learning | tests/property/test_statistical_protocol_lock.py::test_cross_task_transfer | shape | transfer, cross_task | unverified |
| C51 | Prior single source | learning | ✓ | S1_FRAME | priors | tests/property/test_wp10_learning_integration_lock.py::TestPriorSingleSource::test_ruler_tasks_resolve_via_registry | mechanism | priors, single_source | active |
| C52 | No global singletons | learning | ✓ | S1_FRAME | kernel | tests/property/test_kernel_isolation_lock.py::TestRunScopedState::test_engine_singleton_removed | shape | k10, singletons | active |
| C53 | Reasoning persistence | learning | ✓ | S1_FRAME | learning | tests/property/test_scientific_validity_protocol_lock.py::TestDataOriginAndTransferProvenance::test_provenance_with_data_origin | mechanism | reasoning, persistence | active |
| C54 | Warm-start from prior runs | learning | ✗ | S5_COMPOSE | learning | tests/property/test_statistical_protocol_lock.py::test_warm_start_prior_runs | shape | warm_start, transfer | unverified |
| C55 | Coordinate-wide surrogate | learning | ✗ | S5_COMPOSE | learning | tests/property/test_statistical_protocol_lock.py::test_coordinate_wide_surrogate | shape | surrogate, coordinate_wide | unverified |
| C56 | I(C,U) feature encoder | learning | ✗ | S5_COMPOSE | learning | tests/property/test_statistical_protocol_lock.py::test_icu_feature_encoder | shape | icu, feature_encoder | unverified |
| C57 | Achieved seed claim | learning | ✓ | S10_DECIDE | evidence | tests/property/test_statistical_protocol_lock.py::TestClaimPredicates::test_claim_eligible_requires_min_seeds | mechanism | claims, achieved_seeds | active |
| C58 | Multi-objective Pareto | learning | ✓ | S7_MEASURE | learning | tests/property/test_wp10_learning_integration_lock.py::TestSurrogateStoreWiring::test_effect_size_guards | mechanism | pareto, multi_objective | unverified |
| C59 | Substrate-aware objectives | learning | ✗ | S7_MEASURE | substrate | tests/property/test_statistical_protocol_lock.py::test_substrate_aware_objectives | shape | substrate, objectives | unverified |
| C6 | Schema versioning | core | ✓ | S1_FRAME | schema | tests/property/test_experiment_registries_wiring_lock.py::test_registry_integrity_checks_pass | mechanism | versioning, unknown_field | active |
| C60 | Frozen-θ ψ adaptation | learning | ✗ | S10_DECIDE | update | tests/property/test_statistical_protocol_lock.py::test_frozen_theta_psi_adapt | shape | frozen_theta, psi | unverified |
| C61 | NTM geometry | core | ✗ | S5_COMPOSE | geometry | tests/unit/core/test_ntm_geometry.py | mechanism | ntm, gate1_accepted, experimental | active |
| C62 | NCA geometry | core | ✗ | S5_COMPOSE | geometry | tests/unit/core/test_nca_geometry.py | mechanism | nca, gate1_accepted, experimental | active |
| C63 | PEPITA/LEMMA credit | core | ✗ | S5_COMPOSE | credit | tests/property/generated/test_algorithm_pepita_invariants.py | mechanism | pepita, lemma, gate1_accepted | active |
| C64 | Holomorphic EP | core | ✗ | S5_COMPOSE | models_native | tests/property/generated/test_algorithm_holomorphic_ep_invariants.py | mechanism | holomorphic, gate1_accepted | active |
| C65 | Directed EP | core | ✗ | S5_COMPOSE | models_native | tests/property/generated/test_algorithm_directed_ep_invariants.py | mechanism | directed_ep, gate1_accepted | active |
| C66 | Finite-nudge EP | core | ✗ | S5_COMPOSE | models_native | tests/property/generated/test_algorithm_finite_nudge_ep_invariants.py | mechanism | finite_nudge, gate1_accepted | active |
| C67 | Ternary EqProp | core | ✗ | S5_COMPOSE | models_native | tests/property/generated/test_algorithm_ternary_eqprop_invariants.py | mechanism | ternary, eqprop, gate1_accepted | active |
| C68 | Momentum EqProp | core | ✗ | S5_COMPOSE | models_native | tests/property/generated/test_algorithm_momentum_eqprop_invariants.py | mechanism | momentum, eqprop, gate1_accepted | active |
| C69 | Sparse EqProp | core | ✗ | S5_COMPOSE | models_native | tests/property/generated/test_algorithm_sparse_eqprop_invariants.py | mechanism | sparse, eqprop, gate1_accepted | active |
| C7 | Legality engine | core | ✓ | S4_GATE | legality | tests/property/test_legality_boundary_lock.py | mechanism | legality, void, defect | active |
| C70 | Diffusion EqProp | core | ✗ | S5_COMPOSE | models_native | tests/property/generated/test_algorithm_diffusion_eqprop_invariants.py | mechanism | diffusion, eqprop, gate1_accepted | active |
| C71 | Routing plasticity | core | ✗ | S5_COMPOSE | plasticity | tests/property/generated/test_primitive_plasticity_routing_invariants.py | mechanism | routing, plasticity, gate1_accepted | active |
| C72 | Fast-weight plasticity | core | ✗ | S5_COMPOSE | plasticity | tests/property/generated/test_primitive_plasticity_fast_weight_invariants.py | mechanism | fast_weight, plasticity, gate1_accepted | active |
| C73 | Substrate-coupled plasticity | core | ✗ | S5_COMPOSE | plasticity | tests/property/generated/test_primitive_plasticity_substrate_coupled_invariants.py | mechanism | substrate_coupled, plasticity, gate1_accepted | active |
| C74 | Rule-state plasticity (Z3) | core | ✗ | S5_COMPOSE | plasticity | tests/property/generated/test_primitive_plasticity_rule_state_invariants.py | mechanism | z3, rule_state, gate1_accepted | active |
| C75 | Closed-form ridge plasticity | core | ✗ | S5_COMPOSE | plasticity | tests/property/generated/test_primitive_plasticity_closed_form_ridge_invariants.py | mechanism | closed_form, ridge, gate1_accepted | active |
| C76 | Temporal ψ plasticity | core | ✗ | S5_COMPOSE | plasticity | tests/property/generated/test_primitive_plasticity_temporal_psi_invariants.py | mechanism | temporal_psi, plasticity, gate1_accepted | active |
| C77 | CEEC core ledger | core | ✗ | S8_RECORD | ceec_core | packages/ceec-core/tests/test_ceec_store.py | mechanism | ceec, ledger, platform | active |
| C78 | Psi-PEFT | core | ✗ | S10_DECIDE | psi_peft | packages/psi-peft/tests/test_psi_adaptive.py | mechanism | psi_peft, platform | active |
| C79 | Local feedback projections | core | ✗ | S5_COMPOSE | local_feedback | packages/local-feedback/tests/test_lf_adaptive.py | mechanism | local_feedback, platform | active |
| C8 | S1-S11 pipeline | core | ✓ | S1_FRAME | pipeline | tests/acceptance/test_unified_kernel.py::TestU1_SynthesisPolicyPipeline::test_u1_synthesis_policy_end_to_end | mechanism | pipeline, stages | active |
| C80 | Stability guard | core | ✗ | S6_TRAIN | stability | packages/stability/tests/test_stability_guard.py | mechanism | stability, guard, platform | active |
| C81 | Computronium Lab synthesis | core | ✗ | S1_FRAME | lab | packages/computronium-lab/tests/test_synthesis.py | mechanism | lab, synthesis, platform | active |
| C82 | Computronium Lab evolution | core | ✗ | S10_DECIDE | lab | packages/computronium-lab/tests/test_lab_integration_loop.py | mechanism | lab, evolution, platform | active |
| C83 | Surface CLI dispatcher | core | ✓ | S11_REPORT | surface | tests/property/test_cli_readme_lock.py::TestTierZeroIsReal::test_dry_run_prints_a_plan_and_writes_nothing | mechanism | cli, surface | active |
| C84 | Report generator | core | ✓ | S11_REPORT | surface | tests/property/test_wp11_surface_lock.py::TestPublicExports::test_handoff_mentions_intents | mechanism | report, export | active |
| C85 | Codegen from registries | core | ✗ | S11_REPORT | surface | tests/property/test_codegen_drift_lock.py | mechanism | codegen, drift_lock | active |
| C86 | Documented-command conformance | core | ✓ | S11_REPORT | surface | tests/property/test_wp11_surface_lock.py::TestDocumentedCommands::test_commands_parse[argv0] | mechanism | conformance, cli | active |
| C87 | Gallery lock | core | ✓ | S11_REPORT | visualization | tests/integration/test_gallery_lock.py::test_figure_lock | mechanism | gallery, manifest | active |
| C88 | Probe conventions | core | ✓ | S11_REPORT | probes | tests/property/test_wp11_surface_lock.py::TestAlertsAndControl::test_operator_intent_factory | mechanism | probes, conventions | active |
| C9 | Eight-policy catalog | core | ✓ | S3_SCHEDULE | policy | tests/property/test_sampler_lock.py::TestTheRunReachesThePolicy::test_the_spec_reaches_a_learning_policy | mechanism | policy, catalog | active |