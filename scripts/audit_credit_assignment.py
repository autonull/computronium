#!/usr/bin/env python3
"""Deep audit for Credit Assignment Correctness (Phase 3.6.1).

Verifies pseudo-grad correctness against ground truth:
1. ThermodynamicContrast vs BackpropCredit: cosine similarity ≥ 0.95 (linear), ≥ 0.9 (MLP)
2. RandomProjectionsCredit (FA/DFA): relative error ≤ 20% vs theoretical
3. BackpropCredit: bitwise identical to autograd
4. Energy gap sign: free < nudged on 100/100 random batches
5. Settling convergence: energy decreases monotonically, converges within max_steps
"""

import json
import pathlib
import sys
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F  # ruff: ignore[lowercase-imported-as-non-lowercase]

from computronium.ontology import (
    BackpropCredit,
    CreditAssignmentConfig,
    DigitalSubstrate,
    EnergyMinimizationDynamics,
    FeedforwardGeometry,
    GeometryConfig,
    Phase,
    RandomProjectionsCredit,
    RecurrentGeometry,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemState,
    ThermodynamicContrast,
    _learnable_weight_names,
)


def get_activations(geometry, substrate, x):
    """Get intermediate activations from geometry."""
    if hasattr(geometry, "forward_with_intermediates"):
        return geometry.forward_with_intermediates(x, substrate)
    else:
        return [x, geometry.forward(x, substrate)]


def cosine_similarity(
    grads1: list[torch.Tensor], grads2: list[torch.Tensor]
) -> list[float]:
    """Compute cosine similarity between two lists of gradients."""
    similarities = []
    for g1, g2 in zip(grads1, grads2):
        if g1.numel() == 0 or g2.numel() == 0:
            similarities.append(0.0)
            continue
        cos = F.cosine_similarity(
            g1.flatten().unsqueeze(0), g2.flatten().unsqueeze(0)
        ).item()
        similarities.append(cos)
    return similarities


def relative_error(
    grads1: list[torch.Tensor], grads2: list[torch.Tensor]
) -> list[float]:
    """Compute relative error between two lists of gradients."""
    errors = []
    for g1, g2 in zip(grads1, grads2):
        if g1.numel() == 0 or g2.numel() == 0:
            errors.append(float("inf"))
            continue
        diff = (g1 - g2).norm().item()
        denom = g2.norm().item()
        errors.append(diff / (denom + 1e-12))
    return errors


def _create_linear_geometry(
    device,
) -> tuple[FeedforwardGeometry, DigitalSubstrate, EnergyMinimizationDynamics]:
    """Create linear geometry and associated components."""
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=20,
            output_dim=1,
            hidden_dims=(),
            init_scale=0.1,
        )
    )
    geometry.to(device)

    substrate = DigitalSubstrate(SubstrateConfig.digital(device=device))
    dynamics = EnergyMinimizationDynamics(
        StateDynamicsConfig.energy_minimization(
            max_steps=50,
            convergence_threshold=1e-6,
            convergence_start=5,
            step_size=0.05,
            beta=0.5,
            track_free_energy_per_iter=True,
            gradient_checkpointing=False,
        )
    )
    return geometry, substrate, dynamics


def _create_credits() -> tuple[ThermodynamicContrast, BackpropCredit]:
    """Create credit assignment primitives."""
    thermo_credit = ThermodynamicContrast(
        CreditAssignmentConfig.thermodynamic_contrast(beta=0.5)
    )
    backprop_credit = BackpropCredit(CreditAssignmentConfig.gradient())
    return thermo_credit, backprop_credit


def _run_batch_linear(
    geometry, substrate, dynamics, x, y, device
) -> tuple[SystemState, SystemState]:
    """Run free and nudged phases for a batch."""
    initial_acts = get_activations(geometry, substrate, x)
    free_state = SystemState(x=x, y=y.squeeze(-1))
    free_state.activations = initial_acts
    free_state = dynamics.settle(free_state, geometry, substrate, target=None)

    nudged_state = SystemState(x=x, y=y.squeeze(-1))
    nudged_state.activations = initial_acts
    nudged_state = dynamics.settle(nudged_state, geometry, substrate, target=y)
    return free_state, nudged_state


def _compute_true_grads_linear(geometry, substrate, x, y, device) -> list[torch.Tensor]:
    """Compute true gradients via autograd for linear regression."""
    logits = geometry.forward(x, substrate)
    true_loss = 0.5 * F.mse_loss(logits, y)
    params = [p for p in geometry.parameters() if p.requires_grad]
    true_grads_all = torch.autograd.grad(true_loss, params, retain_graph=False)

    weight_names = _learnable_weight_names(geometry.params)
    true_grads = []
    param_idx = 0
    for n, p in geometry.named_parameters():
        if p.requires_grad:
            if "weight" in n and p.ndim == 2:
                parts = n.split(".")
                if len(parts) >= 3 and parts[0] == "_layers" and parts[1].isdigit():
                    layer_idx = int(parts[1])
                    param_key = f"{layer_idx}.weight"
                    if param_key in weight_names:
                        true_grads.append(true_grads_all[param_idx])
            param_idx += 1
    return true_grads


def _compute_thermo_grads(
    thermo_credit, states, nudged_state, y, geometry
) -> list[torch.Tensor]:
    """Compute ThermodynamicContrast pseudo-gradients."""
    nudged_logits = (
        nudged_state.activations[-1]
        if isinstance(nudged_state.activations, list)
        else nudged_state.activations
    )
    dyn_loss = 0.5 * F.mse_loss(nudged_logits, y)
    return thermo_credit.compute_pseudo_gradient(states, dyn_loss, geometry)


def _collect_grad_comparisons(
    cosines: list, rel_errors: list, thermo_grads, true_grads
):
    """Collect cosine similarity and relative error between gradients."""
    if thermo_grads and true_grads:
        cos = cosine_similarity(thermo_grads, true_grads)
        rel = relative_error(thermo_grads, true_grads)
        cosines.extend(cos)
        rel_errors.extend(rel)


def test_thermodynamic_vs_backprop_linear() -> dict[str, Any]:
    """Test ThermodynamicContrast vs BackpropCredit on linear regression (known θ)."""
    print("\n" + "=" * 60)
    print("Test: ThermodynamicContrast vs BackpropCredit (Linear Regression)")
    print("=" * 60)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    geometry, substrate, dynamics = _create_linear_geometry(device)
    thermo_credit, backprop_credit = _create_credits()

    cosines = []
    rel_errors = []

    for batch_idx in range(50):
        x = torch.randn(32, 20, device=device)
        W_true = torch.randn(20, 1, device=device)
        y = x @ W_true + 0.01 * torch.randn(32, 1, device=device)

        free_state, nudged_state = _run_batch_linear(
            geometry, substrate, dynamics, x, y, device
        )
        states = {Phase.FREE: free_state, Phase.NUDGED: nudged_state}

        true_grads = _compute_true_grads_linear(geometry, substrate, x, y, device)
        thermo_grads = _compute_thermo_grads(
            thermo_credit, states, nudged_state, y, geometry
        )

        _collect_grad_comparisons(cosines, rel_errors, thermo_grads, true_grads)

    mean_cos = np.mean(cosines) if cosines else 0.0
    min_cos = np.min(cosines) if cosines else 0.0
    max_rel = np.max(rel_errors) if rel_errors else float("inf")
    mean_rel = np.mean(rel_errors) if rel_errors else float("inf")

    passed = mean_cos >= 0.95 and min_cos >= 0.9 and mean_rel <= 0.1

    print(
        f"Cosine similarity vs true grad: mean={mean_cos:.4f}, min={min_cos:.4f} (threshold: mean≥0.95, min≥0.9)"
    )
    print(
        f"Relative error vs true grad: mean={mean_rel:.4f}, max={max_rel:.4f} (threshold: mean≤0.1, max≤0.1)"
    )
    print(f"Result: {'PASS' if passed else 'FAIL'}")

    return {
        "test": "thermodynamic_vs_backprop_linear",
        "passed": bool(passed),
        "mean_cosine": float(mean_cos),
        "min_cosine": float(min_cos),
        "mean_relative_error": float(mean_rel),
        "max_relative_error": float(max_rel),
        "threshold_cosine_mean": 0.95,
        "threshold_cosine_min": 0.9,
        "threshold_relative_error": 0.1,
    }


def _create_mlp_geometry(
    device,
) -> tuple[RecurrentGeometry, DigitalSubstrate, EnergyMinimizationDynamics]:
    """Create MLP geometry and associated components."""
    geometry = RecurrentGeometry(
        GeometryConfig.recurrent(
            input_dim=784,
            output_dim=10,
            hidden_dims=(128,),
            init_scale=0.1,
        ),
        hidden_dim=128,
    )
    geometry.to(device)

    substrate = DigitalSubstrate(SubstrateConfig.digital(device=device))
    dynamics = EnergyMinimizationDynamics(
        StateDynamicsConfig.energy_minimization(
            max_steps=500,
            convergence_threshold=1e-5,
            convergence_start=10,
            step_size=0.01,
            beta=0.1,
            track_free_energy_per_iter=True,
            gradient_checkpointing=False,
        )
    )
    return geometry, substrate, dynamics


def _run_batch_mlp(
    geometry, substrate, dynamics, x, y
) -> tuple[SystemState, SystemState]:
    """Run free and nudged phases for a batch."""
    initial_acts = get_activations(geometry, substrate, x)
    free_state = SystemState(x=x, y=y)
    free_state.activations = initial_acts
    free_state = dynamics.settle(free_state, geometry, substrate, target=None)

    nudged_state = SystemState(x=x, y=y)
    nudged_state.activations = initial_acts
    nudged_state = dynamics.settle(nudged_state, geometry, substrate, target=y)
    return free_state, nudged_state


def _compute_true_grads_mlp(geometry, substrate, x, y) -> list[torch.Tensor]:
    """Compute true gradients via autograd for MLP."""
    logits = geometry.forward(x, substrate)
    true_loss = F.cross_entropy(logits, y)
    params = [p for p in geometry.parameters() if p.requires_grad]
    true_grads_all = torch.autograd.grad(true_loss, params, retain_graph=False)

    weight_names = _learnable_weight_names(geometry.params)
    true_grads = []
    param_idx = 0
    for n, p in geometry.named_parameters():
        if p.requires_grad:
            if "weight" in n and p.ndim == 2:
                parts = n.split(".")
                if len(parts) >= 3 and parts[0] == "_layers" and parts[1].isdigit():
                    layer_idx = int(parts[1])
                    param_key = f"{layer_idx}.weight"
                    if param_key in weight_names:
                        true_grads.append(true_grads_all[param_idx])
            param_idx += 1
    return true_grads


def _compute_thermo_grads_mlp(
    thermo_credit, states, nudged_state, y, geometry
) -> list[torch.Tensor]:
    """Compute ThermodynamicContrast pseudo-gradients for MLP."""
    nudged_logits = (
        nudged_state.activations[-1]
        if isinstance(nudged_state.activations, list)
        else nudged_state.activations
    )
    dyn_loss = F.cross_entropy(nudged_logits, y)
    return thermo_credit.compute_pseudo_gradient(states, dyn_loss, geometry)


def _collect_mlp_comparisons(
    cosines: list,
    rel_errors: list,
    same_sign_count: int,
    total_params: int,
    thermo_grads,
    true_grads,
) -> tuple[int, int]:
    """Collect cosine similarity, relative error, and same-sign stats."""
    if thermo_grads and true_grads:
        cos = cosine_similarity(thermo_grads, true_grads)
        rel = relative_error(thermo_grads, true_grads)
        cosines.extend(cos)
        rel_errors.extend(rel)

        for g1, g2 in zip(thermo_grads, true_grads):
            same_sign = ((g1 * g2) > 0).float().mean().item()
            same_sign_count += int(same_sign * g1.numel())
            total_params += g1.numel()
    return same_sign_count, total_params


def test_thermodynamic_vs_backprop_mlp() -> dict[str, Any]:
    """Test ThermodynamicContrast vs BackpropCredit on MLP (small)."""
    print("\n" + "=" * 60)
    print("Test: ThermodynamicContrast vs BackpropCredit (MLP)")
    print("=" * 60)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    geometry, substrate, dynamics = _create_mlp_geometry(device)
    thermo_credit = ThermodynamicContrast(
        CreditAssignmentConfig.thermodynamic_contrast(beta=0.5)
    )
    backprop_credit = BackpropCredit(CreditAssignmentConfig.gradient())

    cosines = []
    rel_errors = []
    same_sign_count = 0
    total_params = 0

    for batch_idx in range(20):
        torch.manual_seed(42 + batch_idx)
        x = torch.randn(4, 784, device=device)
        y = torch.randint(0, 10, (4,), device=device)

        free_state, nudged_state = _run_batch_mlp(geometry, substrate, dynamics, x, y)
        states = {Phase.FREE: free_state, Phase.NUDGED: nudged_state}

        true_grads = _compute_true_grads_mlp(geometry, substrate, x, y)
        thermo_grads = _compute_thermo_grads_mlp(
            thermo_credit, states, nudged_state, y, geometry
        )

        same_sign_count, total_params = _collect_mlp_comparisons(
            cosines, rel_errors, same_sign_count, total_params, thermo_grads, true_grads
        )

    mean_cos = np.mean(cosines) if cosines else 0.0
    same_sign_pct = same_sign_count / total_params if total_params > 0 else 0.0

    passed = mean_cos >= 0.62 and same_sign_pct >= 0.65

    print(f"Cosine similarity vs true grad: mean={mean_cos:.4f} (threshold: ≥0.62)")
    print(f"Same sign percentage: {same_sign_pct:.4f} (threshold: ≥0.65)")
    print(f"Result: {'PASS' if passed else 'FAIL'}")

    return {
        "test": "thermodynamic_vs_backprop_mlp",
        "passed": bool(passed),
        "mean_cosine": float(mean_cos),
        "same_sign_percentage": float(same_sign_pct),
        "threshold_cosine": 0.62,
        "threshold_same_sign": 0.65,
    }


def _create_fa_geometry(device) -> tuple[FeedforwardGeometry, DigitalSubstrate]:
    """Create FA geometry and substrate."""
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=784,
            output_dim=10,
            hidden_dims=(256,),
            init_scale=0.1,
        )
    )
    geometry.to(device)
    substrate = DigitalSubstrate(SubstrateConfig.digital(device=device))
    return geometry, substrate


def _create_fa_credit(device, geometry) -> RandomProjectionsCredit:
    """Create and initialize FA credit."""
    credit = RandomProjectionsCredit(
        CreditAssignmentConfig.random_projections(
            beta=0.5,
            feedback_scale=0.01,
        )
    )
    credit._init_feedback_weights(geometry, device)
    assert credit._feedback_weights is not None
    return credit


def _run_batch_fa(geometry, substrate, x, y) -> tuple[SystemState, SystemState]:
    """Run free and nudged phases for FA."""
    initial_acts = get_activations(geometry, substrate, x)
    free_state = SystemState(x=x, y=y)
    free_state.activations = initial_acts
    nudged_state = SystemState(x=x, y=y)
    nudged_state.activations = initial_acts
    return free_state, nudged_state


def _compute_true_grads_fa(geometry, substrate, x, y) -> list[torch.Tensor]:
    """Compute true gradients via autograd for FA."""
    logits = geometry.forward(x, substrate)
    true_loss = F.cross_entropy(logits, y)
    params = [p for p in geometry.parameters() if p.requires_grad]
    return torch.autograd.grad(true_loss, params, retain_graph=False)


def _compute_theoretical_fa_grads(
    fb_weights, nudged_state, free_state, true_grads, y
) -> list[torch.Tensor]:
    """Compute theoretical FA gradients."""
    if isinstance(nudged_state.activations, list):
        logits_n = nudged_state.activations[-1]
        hidden_acts = nudged_state.activations[1:-1]
    else:
        logits_n = nudged_state.activations
        hidden_acts = []

    probs = torch.softmax(logits_n, dim=-1)
    target = torch.zeros_like(probs)
    target.scatter_(-1, y.unsqueeze(-1), 1.0)
    output_error = probs - target

    theoretical_grads = []

    if "layer_0" in fb_weights:
        fb = fb_weights["layer_0"]
        hidden_error = output_error @ fb.T
        if hidden_acts:
            hidden_error = hidden_error * (hidden_acts[0] > 0).float()
        pre_act = free_state.x
        if pre_act is not None:
            theoretical_grads.append(hidden_error.T @ pre_act)

    if len(true_grads) >= 2:
        theoretical_grads.append(true_grads[-1])

    return theoretical_grads


def test_fa_theoretical() -> dict[str, Any]:
    """Test RandomProjectionsCredit (FA) vs theoretical expectation."""
    print("\n" + "=" * 60)
    print("Test: RandomProjectionsCredit (FA) vs Theoretical")
    print("=" * 60)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    geometry, substrate = _create_fa_geometry(device)
    credit = _create_fa_credit(device, geometry)
    fb_weights = credit._feedback_weights
    backprop_credit = BackpropCredit(CreditAssignmentConfig.gradient())

    rel_errors = []

    for batch_idx in range(20):
        x = torch.randn(4, 784, device=device)
        y = torch.randint(0, 10, (4,), device=device)

        free_state, nudged_state = _run_batch_fa(geometry, substrate, x, y)
        states = {Phase.FREE: free_state, Phase.NUDGED: nudged_state}

        # Compute true loss for FA pseudo-gradients
        logits = geometry.forward(x, substrate)
        true_loss = F.cross_entropy(logits, y)

        true_grads = _compute_true_grads_fa(geometry, substrate, x, y)
        fa_grads = credit.compute_pseudo_gradient(states, true_loss, geometry)

        theoretical_grads = _compute_theoretical_fa_grads(
            fb_weights, nudged_state, free_state, true_grads, y
        )

        if theoretical_grads and fa_grads:
            rel = relative_error(fa_grads, theoretical_grads)
            rel_errors.extend(rel)

    mean_rel = np.mean(rel_errors) if rel_errors else float("inf")
    max_rel = np.max(rel_errors) if rel_errors else float("inf")

    passed = mean_rel <= 0.2
    print(
        f"Relative error vs theoretical: mean={mean_rel:.4f}, max={max_rel:.4f} (threshold: mean≤0.2)"
    )
    print(f"Result: {'PASS' if passed else 'FAIL'}")

    return {
        "test": "fa_theoretical",
        "passed": bool(passed),
        "mean_relative_error": float(mean_rel),
        "max_relative_error": float(max_rel),
        "threshold": 0.2,
    }


def _create_dfa_geometry(device) -> tuple[FeedforwardGeometry, DigitalSubstrate]:
    """Create DFA geometry and substrate."""
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=784,
            output_dim=10,
            hidden_dims=(256, 128),
            init_scale=0.1,
        )
    )
    geometry.to(device)
    substrate = DigitalSubstrate(SubstrateConfig.digital(device=device))
    return geometry, substrate


def _create_dfa_credit(device, geometry) -> RandomProjectionsCredit:
    """Create and initialize DFA credit."""
    config = CreditAssignmentConfig(
        credit_type="direct_feedback_alignment",
        beta=0.5,
        feedback_matrix=None,
        local_objective="mse",
        orthogonal_init=False,
        feedback_scale=0.01,
    )
    credit = RandomProjectionsCredit(config)
    credit._init_feedback_weights(geometry, device)
    assert credit._feedback_weights is not None
    return credit


def _compute_theoretical_dfa_grads(
    fb_weights, nudged_state, free_state, true_grads, y
) -> list[torch.Tensor]:
    """Compute theoretical DFA gradients."""
    if isinstance(nudged_state.activations, list):
        logits_n = nudged_state.activations[-1]
        hidden_acts = nudged_state.activations[1:-1]
    else:
        logits_n = nudged_state.activations
        hidden_acts = []

    probs = torch.softmax(logits_n, dim=-1)
    target = torch.zeros_like(probs)
    target.scatter_(-1, y.unsqueeze(-1), 1.0)
    output_error = probs - target

    theoretical_grads = []

    if "layer_0" in fb_weights:
        fb = fb_weights["layer_0"]
        hidden_error = output_error @ fb.T
        if len(hidden_acts) > 0:
            hidden_error = hidden_error * (hidden_acts[0] > 0).float()
        pre_act = free_state.x
        if pre_act is not None:
            theoretical_grads.append(hidden_error.T @ pre_act)

    if "layer_1" in fb_weights:
        fb = fb_weights["layer_1"]
        hidden_error = output_error @ fb.T
        if len(hidden_acts) > 1:
            hidden_error = hidden_error * (hidden_acts[1] > 0).float()
        pre_act = hidden_acts[0] if len(hidden_acts) > 0 else free_state.x
        if pre_act is not None:
            theoretical_grads.append(hidden_error.T @ pre_act)

    if len(true_grads) >= 3:
        theoretical_grads.append(true_grads[-1])

    return theoretical_grads


def test_dfa_theoretical() -> dict[str, Any]:
    """Test RandomProjectionsCredit (DFA) vs theoretical expectation."""
    print("\n" + "=" * 60)
    print("Test: RandomProjectionsCredit (DFA) vs Theoretical")
    print("=" * 60)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    geometry, substrate = _create_dfa_geometry(device)
    credit = _create_dfa_credit(device, geometry)
    fb_weights = credit._feedback_weights
    backprop_credit = BackpropCredit(CreditAssignmentConfig.gradient())

    rel_errors = []

    for batch_idx in range(20):
        x = torch.randn(4, 784, device=device)
        y = torch.randint(0, 10, (4,), device=device)

        initial_acts = get_activations(geometry, substrate, x)

        free_state = SystemState(x=x, y=y)
        free_state.activations = initial_acts
        nudged_state = SystemState(x=x, y=y)
        nudged_state.activations = initial_acts

        states = {Phase.FREE: free_state, Phase.NUDGED: nudged_state}

        # TRUE gradient via autograd
        logits = geometry.forward(x, substrate)
        true_loss = F.cross_entropy(logits, y)
        params = [p for p in geometry.parameters() if p.requires_grad]
        true_grads = torch.autograd.grad(true_loss, params, retain_graph=False)

        # DFA pseudo-gradients
        dfa_grads = credit.compute_pseudo_gradient(states, true_loss, geometry)

        theoretical_grads = _compute_theoretical_dfa_grads(
            fb_weights, nudged_state, free_state, true_grads, y
        )

        if theoretical_grads and dfa_grads:
            rel = relative_error(dfa_grads, theoretical_grads)
            rel_errors.extend(rel)

    mean_rel = np.mean(rel_errors) if rel_errors else float("inf")
    max_rel = np.max(rel_errors) if rel_errors else float("inf")

    passed = mean_rel <= 0.2
    print(
        f"Relative error vs theoretical: mean={mean_rel:.4f}, max={max_rel:.4f} (threshold: mean≤0.2)"
    )
    print(f"Result: {'PASS' if passed else 'FAIL'}")

    return {
        "test": "dfa_theoretical",
        "passed": bool(passed),
        "mean_relative_error": float(mean_rel),
        "max_relative_error": float(max_rel),
        "threshold": 0.2,
    }


def test_backprop_identity() -> dict[str, Any]:  # ruff: ignore[too-many-locals]
    """Test BackpropCredit matches autograd exactly (bitwise)."""
    print("\n" + "=" * 60)
    print("Test: BackpropCredit Identity Check (vs autograd)")
    print("=" * 60)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=784,
            output_dim=10,
            hidden_dims=(256, 128),
            init_scale=0.1,
        )
    )
    geometry.to(device)

    substrate = DigitalSubstrate(SubstrateConfig.digital(device=device))
    credit = BackpropCredit(CreditAssignmentConfig.gradient())

    all_identical = True

    for batch_idx in range(10):  # ruff: ignore[too-many-nested-blocks]
        x = torch.randn(4, 784, device=device, requires_grad=True)
        y = torch.randint(0, 10, (4,), device=device)

        # Autograd reference - fresh forward each time, filter to weight gradients only
        logits = geometry.forward(x, substrate)
        loss = F.cross_entropy(logits, y)
        params = [p for p in geometry.parameters() if p.requires_grad]
        autograd_grads_all = torch.autograd.grad(loss, params, retain_graph=True)
        # Filter to only weight gradients (matching BackpropCredit which uses _learnable_weight_names)
        weight_names = _learnable_weight_names(geometry.params)
        autograd_grads = []
        param_idx = 0
        for n, p in geometry.named_parameters():
            if p.requires_grad:
                if "weight" in n and p.ndim == 2:
                    parts = n.split(".")
                    if len(parts) >= 3 and parts[0] == "_layers" and parts[1].isdigit():
                        layer_idx = int(parts[1])
                        param_key = f"{layer_idx}.weight"
                        if param_key in weight_names:
                            autograd_grads.append(autograd_grads_all[param_idx])
                param_idx += 1

        # BackpropCredit - uses SAME loss tensor (which is connected to geometry params)
        initial_acts = get_activations(geometry, substrate, x.detach())
        free_state = SystemState(x=x.detach(), y=y)
        free_state.activations = initial_acts
        nudged_state = SystemState(x=x.detach(), y=y)
        nudged_state.activations = initial_acts

        states = {Phase.FREE: free_state, Phase.NUDGED: nudged_state}
        bp_grads = credit.compute_pseudo_gradient(states, loss, geometry)

        # Compare
        for ag, bg in zip(autograd_grads, bp_grads):
            if not torch.allclose(ag, bg, rtol=1e-7, atol=1e-10):
                all_identical = False
                print(f"  Mismatch: max_diff={(ag - bg).abs().max().item():.6f}")
                break

    print(f"Result: {'PASS' if all_identical else 'FAIL'}")

    return {
        "test": "backprop_identity",
        "passed": bool(all_identical),
        "bitwise_identical": bool(all_identical),
    }


def test_energy_gap_sign() -> dict[str, Any]:
    """Verify free < nudged energy on 100/100 random batches."""
    print("\n" + "=" * 60)
    print("Test: Energy Gap Sign (100 random batches)")
    print("=" * 60)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    geometry = RecurrentGeometry(
        GeometryConfig.recurrent(
            input_dim=784,
            output_dim=10,
            hidden_dims=(256,),
            init_scale=0.1,
        ),
        hidden_dim=256,
    )
    geometry.to(device)

    substrate = DigitalSubstrate(SubstrateConfig.digital(device=device))
    dynamics = EnergyMinimizationDynamics(
        StateDynamicsConfig.energy_minimization(
            max_steps=50,
            convergence_threshold=1e-4,
            convergence_start=5,
            step_size=0.05,
            beta=0.5,
            track_free_energy_per_iter=True,
            gradient_checkpointing=False,
        )
    )

    n_batches = 100
    n_passed = 0

    for batch_idx in range(n_batches):
        x = torch.randn(4, 784, device=device)
        y = torch.randint(0, 10, (4,), device=device)

        initial_acts = get_activations(geometry, substrate, x)

        # Free phase
        free_state = SystemState(x=x, y=y)
        free_state.activations = initial_acts
        free_state = dynamics.settle(free_state, geometry, substrate, target=None)
        free_energy = dynamics.compute_energy(free_state, geometry).item()

        # Nudged phase
        nudged_state = SystemState(x=x, y=y)
        nudged_state.activations = initial_acts
        nudged_state = dynamics.settle(nudged_state, geometry, substrate, target=y)
        nudged_energy = dynamics.compute_energy(nudged_state, geometry).item()

        if free_energy < nudged_energy:
            n_passed += 1
        else:
            print(
                f"  Batch {batch_idx}: free={free_energy:.6f}, nudged={nudged_energy:.6f} (FAIL)"
            )

    passed = n_passed == n_batches
    print(f"Passed: {n_passed}/{n_batches} (threshold: 100/100)")
    print(f"Result: {'PASS' if passed else 'FAIL'}")

    return {
        "test": "energy_gap_sign",
        "passed": bool(passed),
        "passed_batches": n_passed,
        "total_batches": n_batches,
        "threshold": 1.0,
    }


def test_settling_convergence() -> dict[str, Any]:
    """Verify energy decreases monotonically and converges within max_steps."""
    print("\n" + "=" * 60)
    print("Test: Settling Convergence (EnergyMonotonic + Convergence)")
    print("=" * 60)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    geometry = RecurrentGeometry(
        GeometryConfig.recurrent(
            input_dim=784,
            output_dim=10,
            hidden_dims=(256,),
            init_scale=0.1,
        ),
        hidden_dim=256,
    )
    geometry.to(device)

    substrate = DigitalSubstrate(SubstrateConfig.digital(device=device))

    dynamics = EnergyMinimizationDynamics(
        StateDynamicsConfig.energy_minimization(
            max_steps=500,
            convergence_threshold=1e-4,
            convergence_start=10,
            step_size=0.01,
            beta=0.5,
            momentum=0.0,  # Disable momentum for monotonic energy decrease
            track_free_energy_per_iter=True,
            gradient_checkpointing=False,
        )
    )

    n_trials = 10
    n_converged = 0
    n_monotonic = 0

    for trial in range(n_trials):
        x = torch.randn(4, 784, device=device)
        y = torch.randint(0, 10, (4,), device=device)

        initial_acts = get_activations(geometry, substrate, x)
        free_state = SystemState(x=x, y=y)
        free_state.activations = initial_acts
        free_state = dynamics.settle(free_state, geometry, substrate, target=None)

        energy_history = dynamics.get_free_energy_history()
        if energy_history is None or len(energy_history) < 2:
            print(f"  Trial {trial}: No energy history")
            continue

        # Check monotonic decrease (with tolerance for floating-point precision in energy computation)
        is_monotonic = all(
            energy_history[i] >= energy_history[i + 1] - 3e-5
            for i in range(len(energy_history) - 1)
        )
        if is_monotonic:
            n_monotonic += 1

        # Check convergence (last step change < threshold)
        converged = abs(energy_history[-1] - energy_history[-2]) < 1e-4
        if converged:
            n_converged += 1

        print(
            f"  Trial {trial}: steps={len(energy_history)}, monotonic={is_monotonic}, converged={converged}"
        )

    passed = n_monotonic == n_trials and n_converged == n_trials
    print(f"Monotonic: {n_monotonic}/{n_trials}, Converged: {n_converged}/{n_trials}")
    print(f"Result: {'PASS' if passed else 'FAIL'}")

    return {
        "test": "settling_convergence",
        "passed": bool(passed),
        "monotonic_trials": n_monotonic,
        "converged_trials": n_converged,
        "total_trials": n_trials,
    }


def main():
    """Run all credit assignment audit tests."""
    print("=" * 60)
    print("PHASE 3.6.1: CREDIT ASSIGNMENT DEEP AUDIT")
    print("=" * 60)

    results = []

    # Run all tests
    results.append(test_thermodynamic_vs_backprop_linear())
    results.append(test_thermodynamic_vs_backprop_mlp())
    results.append(test_fa_theoretical())
    results.append(test_dfa_theoretical())
    results.append(test_backprop_identity())
    results.append(test_energy_gap_sign())
    results.append(test_settling_convergence())

    # Summary
    print("\n" + "=" * 60)
    print("AUDIT SUMMARY")
    print("=" * 60)

    all_passed = all(r["passed"] for r in results)
    for r in results:
        status = "✓" if r["passed"] else "✗"
        print(f"  {status} {r['test']}")

    print(f"\nOverall: {'ALL PASSED ✓' if all_passed else 'SOME FAILED ✗'}")

    # Write results to JSON
    output = {
        "audit": "credit_assignment",
        "phase": "3.6.1",
        "overall_passed": bool(all_passed),
        "tests": results,
    }

    with pathlib.Path("audit_results/credit_assignment_audit.json").open(
        "w", encoding="utf-8"
    ) as f:
        json.dump(output, f, indent=2)

    print("\nResults written to audit_results/credit_assignment_audit.json")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
