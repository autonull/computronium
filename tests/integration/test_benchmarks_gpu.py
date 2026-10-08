"""GPU benchmarks for joint benchmark suites.

These tests run the 5 existing benchmark suites on GPU to verify
correctness and collect performance metrics. They are marked with
``@pytest.mark.gpu`` and will be skipped when CUDA is unavailable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.gpu
@pytest.mark.timeout(300)
class TestAdaptationEfficiencyGPU:
    """Adaptation Efficiency Benchmark on GPU."""

    def test_adaptation_efficiency_gpu(self, tmp_path: Path):
        """Run adaptation efficiency benchmark on GPU (quick mode)."""
        from computronium.benchmarks.joint.adaptation_efficiency import (
            run_adaptation_efficiency_suite,
        )

        coordinates = [
            "digital/recurrent/energy_minimization/null/thermodynamic_contrast/euclidean",
            "digital/recurrent/energy_minimization/routing/thermodynamic_contrast/euclidean",
        ]

        results = run_adaptation_efficiency_suite(
            coordinates=coordinates,
            output_dir=tmp_path / "adaptation_efficiency",
            epochs=3,
            batch_size=64,
            seeds=1,
            device="cuda",
        )

        assert len(results) == 2
        for r in results:
            assert "seeds" in r
            assert len(r["seeds"]) == 1
            assert "mean_adaptation_time" in r
            assert "mean_accuracy" in r


@pytest.mark.gpu
@pytest.mark.timeout(300)
class TestComputeEfficiencyGPU:
    """Compute Efficiency Benchmark on GPU."""

    def test_compute_efficiency_gpu(self, tmp_path: Path):
        """Run compute efficiency benchmark on GPU (quick mode)."""
        from computronium.benchmarks.joint.compute_efficiency import (
            run_compute_efficiency_suite,
        )

        coordinates = [
            "digital/feedforward/instantaneous/null/thermodynamic_contrast/euclidean",
            "digital/feedforward/instantaneous/routing/thermodynamic_contrast/euclidean",
        ]

        results = run_compute_efficiency_suite(
            coordinates=coordinates,
            output_dir=tmp_path / "compute_efficiency",
            epochs=3,
            batch_size=64,
            seeds=1,
            device="cuda",
        )

        assert len(results) == 2
        for r in results:
            assert "seeds" in r
            assert len(r["seeds"]) == 1
            assert "mean_accuracy" in r
            assert "mean_active_routes" in r


@pytest.mark.gpu
@pytest.mark.timeout(300)
class TestStructuralRobustnessGPU:
    """Structural Robustness Benchmark on GPU."""

    def test_structural_robustness_gpu(self, tmp_path: Path):
        """Run structural robustness benchmark on GPU (quick mode)."""
        from computronium.benchmarks.joint.structural_robustness import (
            run_structural_robustness_suite,
        )

        coordinates = [
            "digital/recurrent/energy_minimization/null/thermodynamic_contrast/euclidean",
            "digital/recurrent/energy_minimization/routing/thermodynamic_contrast/euclidean",
        ]

        results = run_structural_robustness_suite(
            coordinates=coordinates,
            output_dir=tmp_path / "structural_robustness",
            epochs=3,
            batch_size=64,
            recovery_steps=5,
            damage_severity=0.3,
            seeds=1,
            device="cuda",
        )

        assert len(results) == 2
        for r in results:
            assert "seeds" in r
            assert len(r["seeds"]) == 1
            assert "mean_recovery_ratio" in r
            assert "mean_final_accuracy" in r


@pytest.mark.gpu
@pytest.mark.timeout(300)
class TestAlgorithmMigrationGPU:
    """Algorithm Migration Benchmark on GPU."""

    def test_algorithm_migration_gpu(self, tmp_path: Path):
        """Run algorithm migration benchmark on GPU (quick mode)."""
        from computronium.benchmarks.joint.algorithm_migration import (
            run_algorithm_migration_suite,
        )

        coordinates = [
            "digital/recurrent/energy_minimization/routing/thermodynamic_contrast/euclidean",
            "digital/recurrent/energy_minimization/fast_weights/thermodynamic_contrast/euclidean",
        ]

        results = run_algorithm_migration_suite(
            coordinates=coordinates,
            output_dir=tmp_path / "algorithm_migration",
            epochs_a0=5,
            epochs_a1=5,
            batch_size=64,
            seeds=1,
            device="cuda",
        )

        assert len(results) == 2
        for r in results:
            assert "seeds" in r
            assert len(r["seeds"]) == 1
            assert "mean_a0_accuracy" in r
            assert "mean_a1_accuracy" in r
            assert "mean_migration_time" in r


@pytest.mark.gpu
@pytest.mark.timeout(120)
class TestZ3FixedWeightsGPU:
    """Z3 Fixed Weights Benchmark on GPU."""

    def test_z3_fixed_weights_gpu(self, tmp_path: Path):
        """Run Z3 fixed weights benchmark on GPU (quick mode)."""
        from computronium.benchmarks.joint.z3_fixed_weights import (
            run_z3_suite,
        )

        coordinates = [
            "digital/recurrent/energy_minimization/rule_state/thermodynamic_contrast/euclidean",
        ]

        results = run_z3_suite(
            coordinates=coordinates,
            output_dir=tmp_path / "z3_fixed_weights",
            meta_train_epochs=5,
            eval_epochs=3,
            batch_size=64,
            seeds=1,
            device="cuda",
        )

        assert len(results) == 1
        for r in results:
            assert "seeds" in r
            assert len(r["seeds"]) == 1
            # Z3 returns different structure
            assert "tasks" in r["seeds"][0]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "gpu"])


@pytest.mark.gpu
@pytest.mark.timeout(300)
class TestCreditAssignmentScalingGPU:
    """Credit Assignment Scaling Benchmark on GPU."""

    def test_credit_assignment_scaling_gpu(self, tmp_path: Path):
        """Run credit assignment scaling benchmark on GPU (quick mode)."""
        from computronium.benchmarks.joint.credit_assignment_scaling import (
            run_credit_assignment_scaling_suite,
        )

        depths = [2, 4]
        methods = ["gradient", "fa"]

        results = run_credit_assignment_scaling_suite(
            depths=depths,
            credit_methods=methods,
            output_dir=tmp_path / "credit_assignment_scaling",
            epochs=3,
            batch_size=64,
            seeds=1,
            device="cuda",
        )

        assert len(results) == len(depths) * len(methods)
        for r in results:
            assert "seeds" in r
            assert len(r["seeds"]) == 1
            assert "mean_accuracy" in r


@pytest.mark.gpu
@pytest.mark.timeout(300)
class TestSubstratePrecisionScalingGPU:
    """Substrate Precision Scaling Benchmark on GPU."""

    def test_substrate_precision_scaling_gpu(self, tmp_path: Path):
        """Run substrate precision scaling benchmark on GPU (quick mode)."""
        from computronium.benchmarks.joint.substrate_precision_scaling import (
            run_substrate_precision_scaling_suite,
        )

        substrates = ["digital", "memristive"]
        precisions = ["fp32", "fp16"]

        results = run_substrate_precision_scaling_suite(
            substrates=substrates,
            precisions=precisions,
            output_dir=tmp_path / "substrate_precision_scaling",
            epochs=3,
            batch_size=64,
            seeds=1,
            device="cuda",
        )

        assert len(results) == len(substrates) * len(precisions)
        for r in results:
            assert "seeds" in r
            assert len(r["seeds"]) == 1
            assert "mean_accuracy" in r


@pytest.mark.gpu
@pytest.mark.timeout(300)
class TestStabilityPlasticityFrontierGPU:
    """Stability-Plasticity Frontier Benchmark on GPU."""

    def test_stability_plasticity_frontier_gpu(self, tmp_path: Path):
        """Run stability-plasticity frontier benchmark on GPU (quick mode)."""
        from computronium.benchmarks.joint.stability_plasticity_frontier import (
            run_stability_plasticity_frontier_suite,
        )

        rho_values = [0.7, 0.9]
        plasticity_types = ["null", "routing"]

        results = run_stability_plasticity_frontier_suite(
            rho_values=rho_values,
            plasticity_types=plasticity_types,
            output_dir=tmp_path / "stability_plasticity_frontier",
            epochs_per_task=3,
            batch_size=64,
            seeds=1,
            device="cuda",
        )

        assert len(results) == len(rho_values) * len(plasticity_types)
        for r in results:
            assert "seeds" in r
            assert len(r["seeds"]) == 1
            assert "mean_task_a_accuracy" in r
            assert "mean_task_b_accuracy" in r
            assert "mean_retention" in r
