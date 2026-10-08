"""Session-scoped fixtures for state_dynamics kernel parity tests.

This module provides shared fixtures to accelerate kernel parity tests by:
1. Pre-computing reference outputs once per session
2. Providing reduced-dimension test cases for fast suite
3. Triton warmup for CUDA tests
"""

from __future__ import annotations

from typing import Any

import pytest
import torch

# Import reference steps and case makers for all dynamics
from computronium.primitives.state_dynamics.energy_minimization import (
    make_case as make_case_em,
)
from computronium.primitives.state_dynamics.energy_minimization import (
    reference_step as reference_step_em,
)
from computronium.primitives.state_dynamics.pc_alm_settling import (
    make_case as make_case_pcalm,
)
from computronium.primitives.state_dynamics.pc_alm_settling import (
    reference_step as reference_step_pcalm,
)
from computronium.primitives.state_dynamics.predictive_settling import (
    make_case as make_case_ps,
)
from computronium.primitives.state_dynamics.predictive_settling import (
    reference_step as reference_step_ps,
)

# ============================================================
# Reduced-dimension test cases for fast suite
# ============================================================


@pytest.fixture(scope="session")
def fast_case_config() -> dict[str, Any]:
    """Configuration for fast parity tests: reduced dimensions."""
    return {
        "device": "cpu",
        "dtype": torch.float32,
        "scale": 1,  # batch=2, width=4
    }


@pytest.fixture(scope="session")
def full_case_config() -> dict[str, Any]:
    """Configuration for full parity tests (opt-in via --full-parity)."""
    return {
        "device": "cpu",
        "dtype": torch.float32,
        "scale": 8,  # batch=16, width=32
    }


# ============================================================
# Session-scoped pre-computed reference outputs
# ============================================================


def _precompute_reference_outputs(
    dynamics_name: str, seeds: list[int], case_config: dict[str, Any]
) -> dict[int, Any]:
    """Pre-compute reference outputs for given seeds and dynamics."""
    if dynamics_name == "energy_minimization":
        make_case = make_case_em
        reference_step = reference_step_em
    elif dynamics_name == "predictive_settling":
        make_case = make_case_ps
        reference_step = reference_step_ps
    elif dynamics_name == "pc_alm":
        make_case = make_case_pcalm
        reference_step = reference_step_pcalm
    else:
        raise ValueError(f"Unknown dynamics: {dynamics_name}")

    outputs = {}
    for seed in seeds:
        case = make_case(seed=seed, **case_config)
        outputs[seed] = reference_step(case)
    return outputs


@pytest.fixture(scope="session")
def energy_minimization_ref_outputs(fast_case_config: dict[str, Any]) -> dict[int, Any]:
    """Pre-computed reference outputs for energy_minimization (seeds 0, 1, 2, 42)."""
    return _precompute_reference_outputs(
        "energy_minimization", [0, 1, 2, 42], fast_case_config
    )


@pytest.fixture(scope="session")
def predictive_settling_ref_outputs(fast_case_config: dict[str, Any]) -> dict[int, Any]:
    """Pre-computed reference outputs for predictive_settling (seeds 0, 1, 2, 42)."""
    return _precompute_reference_outputs(
        "predictive_settling", [0, 1, 2, 42], fast_case_config
    )


@pytest.fixture(scope="session")
def pc_alm_ref_outputs(fast_case_config: dict[str, Any]) -> dict[int, Any]:
    """Pre-computed reference outputs for pc_alm (seeds 0, 1, 2, 42)."""
    return _precompute_reference_outputs("pc_alm", [0, 1, 2, 42], fast_case_config)


# ============================================================
# Pre-computed test cases (cases themselves, not just outputs)
# ============================================================


@pytest.fixture(scope="session")
def energy_minimization_cases(fast_case_config: dict[str, Any]) -> dict[int, Any]:
    """Pre-computed test cases for energy_minimization."""
    return {seed: make_case_em(seed=seed, **fast_case_config) for seed in [0, 1, 2, 42]}


@pytest.fixture(scope="session")
def predictive_settling_cases(fast_case_config: dict[str, Any]) -> dict[int, Any]:
    """Pre-computed test cases for predictive_settling."""
    return {seed: make_case_ps(seed=seed, **fast_case_config) for seed in [0, 1, 2, 42]}


@pytest.fixture(scope="session")
def pc_alm_cases(fast_case_config: dict[str, Any]) -> dict[int, Any]:
    """Pre-computed test cases for pc_alm."""
    return {
        seed: make_case_pcalm(seed=seed, **fast_case_config) for seed in [0, 1, 2, 42]
    }


# ============================================================
# Kernel compilation warmup fixtures
# ============================================================


def _warmup_energy_minimization() -> None:
    try:
        from computronium.acceleration.compile import compile_model
        from computronium.primitives.state_dynamics.energy_minimization import (
            make_case,
            reference_step,
        )

        case = make_case(device="cpu", seed=0)
        compiled = compile_model(reference_step, mode="reduce-overhead")
        _ = compiled(case)
    except Exception as exc:
        import logging

        logging.getLogger(__name__).debug("EnergyMinimization warmup failed: %s", exc)


def _warmup_predictive_settling() -> None:
    try:
        from computronium.acceleration.compile import compile_model
        from computronium.primitives.state_dynamics.predictive_settling import (
            make_case,
            reference_step,
        )

        case = make_case(device="cpu", seed=0)
        compiled = compile_model(reference_step, mode="reduce-overhead")
        _ = compiled(case)
    except Exception as exc:
        import logging

        logging.getLogger(__name__).debug("PredictiveSettling warmup failed: %s", exc)


def _warmup_pc_alm() -> None:
    try:
        from computronium.acceleration.compile import compile_model
        from computronium.primitives.state_dynamics.pc_alm_settling import (
            make_case,
            reference_step,
        )

        case = make_case(device="cpu", seed=0)
        compiled = compile_model(reference_step, mode="reduce-overhead")
        _ = compiled(case)
    except Exception as exc:
        import logging

        logging.getLogger(__name__).debug("PCALM warmup failed: %s", exc)


@pytest.fixture(scope="session")
def energy_minimization_kernel_warmup() -> None:
    """Pre-compile energy_minimization torch.compile kernel."""
    _warmup_energy_minimization()


@pytest.fixture(scope="session")
def predictive_settling_kernel_warmup() -> None:
    """Pre-compile predictive_settling torch.compile kernel."""
    _warmup_predictive_settling()


@pytest.fixture(scope="session")
def pc_alm_kernel_warmup() -> None:
    """Pre-compile pc_alm torch.compile kernel."""
    _warmup_pc_alm()


@pytest.fixture(scope="session", autouse=True)
def triton_warmup() -> None:
    """Warm up Triton kernels once per session to avoid JIT compilation in tests."""
    if torch.cuda.is_available():
        try:
            # Import inside to avoid circular imports
            import importlib

            accel = importlib.import_module("computronium.acceleration")
            if hasattr(accel, "get_available_kernels"):
                for kernel in accel.get_available_kernels():
                    # Run a dummy forward/backward to trigger compilation
                    if hasattr(kernel, "warmup"):
                        kernel.warmup()
        except Exception as exc:
            import logging

            logging.getLogger(__name__).debug("Triton warmup failed: %s", exc)
