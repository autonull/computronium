"""TODO34 §1.5 — determinism ratchet: no *new* unseeded value assertions.

A test that draws from the global torch RNG and then asserts a number is
unreproducible, and under ``-n 4`` each worker holds its own stream, so a
failure cannot be re-run to the same inputs. Two of the defects in TODO34
§0 surfaced only because settle work shifted the global stream.

Scope is deliberately narrow, because a lock with false positives gets
switched off (the §2.5 lesson). A test is flagged only when *all* hold:

* it calls a global ``torch.<rand*|randint|randperm|normal>`` directly,
* nothing in the function or the module body seeds a generator, and
* it asserts on a *number* — an ordered comparison, ``allclose``,
  ``isclose`` or ``pytest.approx``.

Shape-only tests are exempt: whether ``torch.randn(3, 4)`` has shape
``(3, 4)`` does not depend on the draw. That exemption is why the
unflagged population is large (334 unseeded tests) while the flagged one
is not (116, across 42 files).

The lock is a ratchet, not a ban: ``_BASELINE`` records what already
exists, new entries are a failure, and shrinking it is progress. Delete an
entry from ``_BASELINE`` when you add a seed to the test it names.
"""

import ast
from pathlib import Path
from typing import Final

import pytest

TESTS_DIR: Final = Path(__file__).resolve().parents[1]

_RNG_CALLS: Final = frozenset({
    "rand",
    "rand_like",
    "randint",
    "randint_like",
    "randn",
    "randn_like",
    "randperm",
    "normal",
})
_SEED_CALLS: Final = ("manual_seed", "set_rng_state", "Generator(", "fork_rng")
_ORDERED_CMP: Final = frozenset({"Lt", "LtE", "Gt", "GtE"})
_TOLERANCE_CMP: Final = ("allclose", "isclose", "approx")

_BASELINE: dict[str, tuple[str, ...]] = {
    "tests/integration/test_compiled_settle.py": (
        "test_compiled_settle_matches_eager",
    ),
    "tests/integration/test_energy_invariants.py": (
        "TestGradientEquivalence::test_thermodynamic_contrast_limit",
    ),
    "tests/integration/test_equitile_domains.py": (
        "TestVision::test_conv_equitile_train_step",
        "TestVision::test_vision_augmentation",
    ),
    "tests/integration/test_grpc_seam_subprocess.py": ("test_various_geometries",),
    "tests/integration/test_lazy_dynamics.py": (
        "test_lazy_settle_monotone_and_nudges",
    ),
    "tests/integration/test_pc_alm_validation.py": (
        "TestPCALMAdaptiveBudget::test_adaptive_stops_early",
        "TestPCALMAdaptiveBudget::test_convergence_threshold_zero_uses_full_budget",
        "TestPCALMAdaptiveBudget::test_fixed_vs_adaptive_steps",
        "TestPCALMEnergyTracking::test_augmented_lagrangian_decreases",
        "TestPCALMEnergyTracking::test_free_energy_history_recorded",
        "TestPCALMGradientEquivalence::test_pcalm_depth_4_trains",
        "TestPCALMGradientEquivalence::test_pcalm_produces_pseudo_gradients",
    ),
    "tests/integration/test_settle_protocol_models.py": (
        "TestSettleProtocolMultiEpochLearning::test_multi_epoch_learning",
        "TestTileAlgorithmSettleProtocol::test_get_settle_telemetry",
        "TestTileAlgorithmSettleProtocol::test_loose_threshold_early_convergence",
        "TestTileAlgorithmSettleProtocol::test_settle_universal_returns_telemetry",
    ),
    "tests/integration/test_settling_memory.py": (
        "test_sequential_settling_bounded_memory",
    ),
    "tests/integration/test_substrate_settle_equivalence.py": (
        "TestProductionPathEquivalence::test_dynamics_settle_matches_reference",
        "TestProductionPathEquivalence::test_dynamics_settle_nudged_matches_reference",
        "TestSubstrateSettleEquivalence::test_nudged_phase_equivalence",
        "TestSubstrateSettlePseudoGradient::test_pseudo_gradient_matches_thermodynamic_contrast",
        "TestSubstrateSettleWeightUpdateOperator::test_digital_update_operator_is_sgd",
    ),
    "tests/property/joint/test_adapter_projections.py": (
        "test_joint_transition_with_null_plasticity",
    ),
    "tests/property/joint/test_composability.py": (
        "test_null_plasticity_reproduces_5d_behavior",
    ),
    "tests/property/joint/test_composite_state.py": (
        "test_composite_state_mutability",
    ),
    "tests/property/joint/test_consolidation.py": (
        "test_consolidation_promotes_consolidatable",
        "test_consolidation_resets_plastic",
        "test_consolidation_scale",
    ),
    "tests/property/joint/test_lifecycle_locks.py": (
        "test_j1_null_plasticity_zero_extension",
        "test_j3_fast_plastic_only_via_plasticity",
        "test_j5_consolidation_only_at_episode_boundary",
        "test_j7_trajectory_records_full_joint_state",
    ),
    "tests/property/joint/test_null_equivalence.py": (
        "test_null_plasticity_equivalence",
    ),
    "tests/property/joint/test_plasticity_axis_certifications.py": (
        "test_consolidation_with_plasticity_config",
        "test_fast_weight_plasticity_axis_certification",
        "test_null_plasticity_preserves_joint_invariants",
        "test_routing_plasticity_axis_certification",
        "test_rule_state_plasticity_axis_certification",
        "test_zero_extension_null_plasticity",
        "test_zero_extension_null_vs_non_null",
    ),
    "tests/property/joint/test_state_registry.py": ("test_composite_state_clone",),
    "tests/property/test_axis_certifications.py": (
        "TestCAxisLocalGoodnessCredit::test_local_goodness_surrogate_alignment",
        "TestCAxisTargetInversionCredit::test_target_inversion_surrogate_alignment",
        "TestDAxisSpikeIntegration::test_membrane_boundedness",
        "TestDAxisSpikeIntegration::test_spike_counts_bounded_per_step",
        "TestUAxisElasticConsolidationUpdate::test_protected_parameter_immobility",
        "TestUAxisMeanNormUpdate::test_fisher_whitening_direction_preserved",
        "TestUAxisRiemannianOrthogonalUpdate::test_orthogonality_preservation",
        "TestUAxisSpectralConstrainedUpdate::test_spectral_norm_bound",
    ),
    "tests/property/test_campaign_fidelity.py": (
        "TestMetricHonesty::test_free_accuracy_is_not_supervision_leaked",
    ),
    "tests/property/test_gradient_equivalence.py": (
        "TestGradientEquivalence::test_thermodynamic_contrast_local_gradients",
        "TestGradientEquivalence::test_thermodynamic_contrast_no_weight_transport",
    ),
    "tests/property/test_jacobian_amplification.py": (
        "test_estimator_is_not_sigma_max_on_nonnormal",
        "test_nonnormal_jordan_block_not_conflated",
        "test_normal_matrix_rho_equals_sigma_max",
    ),
    "tests/property/test_psi_engagement.py": ("test_modulate_reaches_activations",),
    "tests/property/test_role_split_update.py": (
        "TestPartitionExactness::test_bias_grads_routed_to_owner",
    ),
    "tests/property/test_scaling_invariants.py": (
        "TestDeepNetworkCreditAssignment::test_deep_network_gradient_flow",
        "TestMemoryScalingO1::test_backprop_memory_grows_with_depth",
        "TestMemoryScalingO1::test_eqprop_activation_memory_constant",
        "TestNoiseDampingSelfHealing::test_noise_damping",
    ),
    "tests/property/test_settle_driver_lock.py": (
        "TestDriverUniquenessLock::test_every_dynamics_class_reports_its_horizon",
    ),
    "tests/property/test_settle_protocol.py": (
        "test_forward_trajectory_path_still_works",
    ),
    "tests/property/test_state_dynamics_protocol.py": (
        "TestActivationLayout::test_settle_returns_layered_activations",
        "TestMutationContract::test_caller_must_use_returned_state",
    ),
    "tests/property/test_tile_settle_kernel.py": (
        "test_block_vs_per_edge_equivalence",
        "test_free_vs_nudged_contrast",
    ),
    "tests/slow/test_continual_learning.py": (
        "TestArmLearningRegression::test_lwf_distillation_is_active",
        "TestCLMetrics::test_compute_cl_metrics_backward_transfer",
        "TestCLMetrics::test_compute_cl_metrics_forgetting",
        "TestContinualJointSystem::test_forward_with_psi_modulates_output",
        "TestOtherArms::test_lwf_loss_computation",
        "TestOtherArms::test_synaptic_intelligence_tracking",
    ),
    "tests/unit/core/test_buffers.py": (
        "TestReplayBuffer::test_balanced_eviction",
        "TestReplayBuffer::test_task_id_preserved",
    ),
    "tests/unit/core/test_checkpoint.py": ("test_load_checkpoint_into_model",),
    "tests/unit/core/test_cl_pipeline.py": (
        "TestPlasticStateManagement::test_psi_updated_across_steps",
        "TestTaskMasking::test_different_tasks_different_slices",
        "TestTaskMasking::test_loss_computed_on_task_slice",
    ),
    "tests/unit/core/test_credit.py": (
        "TestBackpropIdentity::test_bitwise_identical",
        "TestFATheoretical::test_feedback_propagated_error_signal",
        "TestThermodynamicVsBackpropLinear::test_cosine_similarity_high",
    ),
    "tests/unit/core/test_credit_norm.py": (
        "test_beta_adaptive_is_unit_rms_error_reference",
        "test_spectral_radius_one",
    ),
    "tests/unit/core/test_energies.py": (
        "TestHybridEnergy::test_non_negative",
        "TestHybridEnergy::test_supervised_weight_scales",
        "TestHybridEnergy::test_supervised_weight_zero",
        "TestMSEEnergy::test_non_negative",
        "TestMSEEnergy::test_zero_for_perfect_match",
        "TestNodeEnergy::test_non_negative",
        "TestNodeEnergy::test_scales_with_reg_weight",
        "TestNodeEnergy::test_zero_reg_weight",
        "TestPredictionErrorEnergy::test_non_negative",
        "TestPredictionErrorEnergy::test_single_layer",
        "TestPredictionErrorEnergy::test_with_weights",
        "TestPredictionErrorEnergy::test_zero_for_exact_match",
        "TestSupervisedEnergy::test_default_loss_is_ce",
        "TestSupervisedEnergy::test_non_negative",
    ),
    "tests/unit/core/test_energy_model.py": ("test_ebm_fallback_metrics_valid",),
    "tests/unit/core/test_energy_sparsity.py": (
        "TestActivationSparsity::test_no_matching_modules_returns_zero",
        "TestActivationSparsity::test_relu_gives_moderate_sparsity",
        "TestActivationSparsity::test_returns_float_in_range",
        "TestEnergyTracker::test_conv_model_activation_sparsity",
        "TestEnergyTracker::test_gelu_model",
        "TestEnergyTracker::test_tracker_sets_profile",
    ),
    "tests/unit/core/test_gradient_strategies.py": (
        "TestHebbianGradient::test_local_hebbian_update",
    ),
    "tests/unit/core/test_latency_proxy.py": (
        "test_proxy_ordering_matches_measured_walltime",
    ),
    "tests/unit/core/test_plasticity.py": (
        "TestFastWeightPlasticity::test_decay_property_zero_activity",
        "TestFastWeightPlasticity::test_forward_modulation_changes_output",
        "TestFastWeightPlasticity::test_step_updates_fast_weights",
        "TestRoutingPlasticity::test_step_updates_gate_logits",
        "TestRuleStatePlasticity::test_step_updates_operator_logits",
    ),
    "tests/unit/nn/test_computronium_linear.py": (
        "TestComputroniumLinearFastWeights::test_fast_weights_modulates_output",
        "TestComputroniumLinearFastWeights::test_fast_weights_reset_psi",
    ),
    "tests/unit/stability/test_stability_api.py": (
        "TestDeviceManagement::test_cuda_consistency",
    ),
}


def _callees(fn: ast.AST) -> list[str]:
    return [
        ast.unparse(node.func) for node in ast.walk(fn) if isinstance(node, ast.Call)
    ]


def _seeds(stream: str) -> bool:
    return any(marker in stream for marker in _SEED_CALLS)


def _asserts_on_numbers(fn: ast.AST) -> bool:
    for node in ast.walk(fn):
        if not isinstance(node, ast.Assert):
            continue
        if isinstance(node.test, ast.Compare) and any(
            type(op).__name__ in _ORDERED_CMP for op in node.test.ops
        ):
            return True
        if any(marker in ast.unparse(node.test) for marker in _TOLERANCE_CMP):
            return True
    return False


def _qualified(fn: ast.AST, cls: str | None) -> str:
    name = fn.name  # type: ignore[attr-defined]
    return f"{cls}::{name}" if cls else name


def _scan_tests(path: Path) -> tuple[bool, dict[str, list[str]]]:
    """Return (module_seeds, {qualified test name: unseeded RNG calls})."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    module_seeds = any(
        _seeds(ast.unparse(node))
        for node in tree.body
        if isinstance(node, (ast.Call, ast.Expr))
    )
    found: dict[str, list[str]] = {}
    for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
        for fn in cls.body:
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
                fn.name.startswith("test_")
            ):
                _record(found, _qualified(fn, cls.name), fn, module_seeds)
    for fn in (
        n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ):
        if fn.name.startswith("test_"):
            _record(found, _qualified(fn, None), fn, module_seeds)
    return module_seeds, found


def _record(
    into: dict[str, list[str]], key: str, fn: ast.AST, module_seeds: bool
) -> None:
    if module_seeds:
        return
    callees = _callees(fn)
    if _seeds(ast.unparse(fn)):
        return
    unseeded = [
        callee
        for callee in callees
        if callee.startswith("torch.") and callee.rsplit(".", 1)[-1] in _RNG_CALLS
    ]
    if unseeded and _asserts_on_numbers(fn):
        into[key] = unseeded


def _unseeded() -> dict[str, tuple[str, ...]]:
    found: dict[str, tuple[str, ...]] = {}
    for path in sorted(TESTS_DIR.rglob("test_*.py")):
        _module_seeds, per_file = _scan_tests(path)
        if per_file:
            found[str(path.relative_to(TESTS_DIR.parent))] = tuple(sorted(per_file))
    return found


def test_no_new_unseeded_value_assertions() -> None:
    unseeded = _unseeded()
    baseline = {path: set(names) for path, names in _BASELINE.items()}
    new = {
        path: sorted(set(names) - baseline.get(path, set()))
        for path, names in unseeded.items()
    }
    new = {path: names for path, names in new.items() if names}
    assert not new, (
        "unseeded value assertions added (TODO34 §1.5): seed the RNG locally, or "
        f"record them in _BASELINE: {new}"
    )
    stale = sorted(set(baseline) - set(unseeded))
    assert not stale, (
        f"baseline entries no longer flagged — delete them from _BASELINE: {stale}"
    )


def test_baseline_is_non_trivial() -> None:
    """The §0.6 lesson: a lock that silently scans nothing is not a lock."""
    unseeded = _unseeded()
    assert len(unseeded) >= 30
    assert sum(len(v) for v in unseeded.values()) >= 100


@pytest.mark.parametrize(
    ("source", "flagged"),
    [
        pytest.param(
            "def test_x():\n"
            "    torch.manual_seed(0)\n"
            "    y = torch.randn(4)\n"
            "    assert y.mean() > 0.5\n",
            False,
            id="locally_seeded",
        ),
        pytest.param(
            "def test_x():\n    y = torch.randn(4)\n    assert y.shape == (4,)\n",
            False,
            id="shape_only",
        ),
        pytest.param(
            "torch.manual_seed(0)\n\n\ndef test_x():\n"
            "    y = torch.randn(4)\n"
            "    assert y.mean() < 10\n",
            False,
            id="module_seeded",
        ),
        pytest.param(
            "def test_x():\n    y = torch.randn(4)\n    assert y.mean() < 10\n",
            True,
            id="flagged",
        ),
    ],
)
def test_scan_classifies(source: str, flagged: bool, tmp_path: Path) -> None:
    path = tmp_path / "test_probe.py"
    path.write_text(source, encoding="utf-8")
    _module_seeds, found = _scan_tests(path)
    assert bool(found) is flagged
