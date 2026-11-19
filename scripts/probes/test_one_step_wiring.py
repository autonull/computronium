#!/usr/bin/env python
"""One-step wiring probes for TODO97 S4.

Tests the four cheap wiring probes:
1. geometry.graph - batch node rows with edge_index/batch
2. geometry.conv - one-step gradient vs feedforward
3. credit.pc_alm - one-step pseudo-gradient vs gradient
4. dynamics.error_predictive_coding - one-step settle vs predictive_settling
"""

import torch
from computronium.ontology import (
    CreditAssignmentConfig,
    DigitalSubstrate,
    EuclideanUpdate,
    FeedforwardGeometry,
    GeometryConfig,
    InstantaneousDynamics,
    ParameterUpdateConfig,
    PCALMCredit,
    PCALMDynamics,
    StateDynamicsConfig,
    SubstrateConfig,
    ErrorPredictiveCodingDynamics,
    PredictiveSettlingDynamics,
    ConvGeometry,
)
from computronium.core.system_trainer import compose_system
from computronium.ontology.credit import BackpropCredit


def test_graph_batching():
    """Test graph geometry with batched input."""
    print("Testing graph batching...")
    
    from computronium.ontology.geometry import GraphGeometry
    
    substrate = DigitalSubstrate(SubstrateConfig.digital(device="cpu"))
    geometry = GraphGeometry(
        GeometryConfig.graph(
            input_dim=16,
            output_dim=5,
            edge_index=[[0, 1, 2, 3], [1, 2, 3, 0]],
            hidden_dims=(32,),
            pooling="mean",
        )
    )
    dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    credit = BackpropCredit(CreditAssignmentConfig.gradient())
    update = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.01))
    
    system = compose_system(substrate, geometry, dynamics, credit, update)
    
    # Create batched graph input: 4 nodes, 2 graphs
    x = torch.randn(4, 16)
    edge_index = torch.tensor([[0, 1, 2, 3], [1, 2, 3, 0]], dtype=torch.long)
    batch = torch.tensor([0, 0, 1, 1], dtype=torch.long)
    y = torch.randint(0, 5, (2,))  # 2 graphs, 5 classes
    
    # Forward pass with batched graph
    logits = system.forward(x, edge_index=edge_index, batch=batch)
    assert logits.shape == (2, 5), f"Expected (2, 5), got {logits.shape}"
    
    # Compute loss and backward
    loss = torch.nn.functional.cross_entropy(logits, y)
    loss.backward()
    
    # Check gradients exist
    for name, param in system.named_parameters():
        if param.grad is not None:
            assert torch.isfinite(param.grad).all(), f"Non-finite gradient in {name}"
    
    print("  ✓ Graph batching works")
    return True


def test_conv_vs_feedforward():
    """Test conv geometry one-step gradient vs feedforward."""
    print("Testing conv vs feedforward...")
    
    # Create conv system
    substrate = DigitalSubstrate(SubstrateConfig.digital(device="cpu"))
    geometry_conv = ConvGeometry(
        GeometryConfig.conv(
            input_dim=784,
            output_dim=10,
            conv_channels=(8, 16),
            kernel_size=3,
            in_channels=1,
            input_hw=(28, 28),
            pool_hw=(4, 4),
        )
    )
    dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    credit = BackpropCredit(CreditAssignmentConfig.gradient())
    update = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.01))
    
    system_conv = compose_system(substrate, geometry_conv, dynamics, credit, update)
    
    # Create feedforward system with same parameters
    geometry_ff = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=784,
            output_dim=10,
            hidden_dims=(128, 64),
        )
    )
    system_ff = compose_system(substrate, geometry_ff, dynamics, credit, update)
    
    # Same input
    x = torch.randn(4, 1, 28, 28)
    y = torch.randint(0, 10, (4,))
    
    # Forward conv
    logits_conv = system_conv.forward(x)
    loss_conv = torch.nn.functional.cross_entropy(logits_conv, y)
    
    # Forward feedforward (flatten input)
    x_flat = x.view(4, 784)
    logits_ff = system_ff.forward(x_flat)
    loss_ff = torch.nn.functional.cross_entropy(logits_ff, y)
    
    # Both should produce finite losses
    assert torch.isfinite(loss_conv), "Conv loss is not finite"
    assert torch.isfinite(loss_ff), "Feedforward loss is not finite"
    
    # Backward both
    loss_conv.backward()
    loss_ff.backward()
    
    # Check gradients
    for name, param in system_conv.named_parameters():
        if param.grad is not None:
            assert torch.isfinite(param.grad).all(), f"Non-finite gradient in conv {name}"
    
    for name, param in system_ff.named_parameters():
        if param.grad is not None:
            assert torch.isfinite(param.grad).all(), f"Non-finite gradient in ff {name}"
    
    print("  ✓ Conv vs feedforward works")
    return True


def test_pc_alm_pseudo_gradient():
    """Test PC-ALM one-step pseudo-gradient vs gradient."""
    print("Testing PC-ALM pseudo-gradient...")
    
    from computronium.core.pipeline import _PhaseContext, _run_phases, forward_pass
    from computronium.ontology.dynamics._state import state_dual_vars
    
    substrate = DigitalSubstrate(SubstrateConfig.digital(device="cpu"))
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=784,
            output_dim=10,
            hidden_dims=(128, 64),
            init_scheme="innocenti",
            residual=True,
        )
    )
    dynamics = PCALMDynamics(
        StateDynamicsConfig.pc_alm(
            max_steps=10,
            step_size=0.1,
            beta=0.5,
            rho=1.0,
        )
    )
    credit = PCALMCredit(CreditAssignmentConfig.pc_alm(beta=0.5))
    update = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.02))
    
    system = compose_system(substrate, geometry, dynamics, credit, update)
    
    x = torch.randn(4, 784)
    y = torch.randint(0, 10, (4,))
    
    # Build phase context and run phases (without applying update)
    owned_free = None
    initial_activations = forward_pass(substrate, geometry, x)
    
    phase_ctx = _PhaseContext(
        credit=credit,
        dynamics=dynamics,
        geometry=geometry,
        substrate=substrate,
        initial_activations=initial_activations,
        x=x,
        y=y,
        plasticity=None,
        psi=None,
        context=None,
        loss_fn=torch.nn.functional.cross_entropy,
        graph_kwargs=None,
        owned_free=owned_free,
    )
    states = _run_phases(phase_ctx)
    
    # Forward to get logits for loss
    logits = system.forward(x)
    loss = torch.nn.functional.cross_entropy(logits, y)
    
    # Compute pseudo-gradients
    pseudo_grads = credit.compute_pseudo_gradient(states, loss, geometry)
    
    assert pseudo_grads is not None, "PC-ALM should produce pseudo-gradients"
    assert len(pseudo_grads) > 0, "PC-ALM should produce non-empty pseudo-gradients"
    
    # Check they're finite and non-zero
    total_norm = 0.0
    for i, grad in enumerate(pseudo_grads):
        assert torch.isfinite(grad).all(), f"Non-finite pseudo-gradient at layer {i}"
        total_norm += grad.norm().item()
    
    print(f"  Total pseudo-gradient norm: {total_norm:.6f}")
    
    # Pseudo-gradients should be non-zero (wiring works)
    assert total_norm > 0.0, "PC-ALM should produce non-zero pseudo-gradients"
    
    print("  ✓ PC-ALM pseudo-gradient works (non-zero pseudo-gradients)")
    return True


def test_epc_settle():
    """Test Error-Predictive Coding one-step settle vs Predictive Settling."""
    print("Testing EPC settle...")
    
    substrate = DigitalSubstrate(SubstrateConfig.digital(device="cpu"))
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=784,
            output_dim=10,
            hidden_dims=(128, 64),
        )
    )
    
    # EPC dynamics
    epc_dynamics = ErrorPredictiveCodingDynamics(
        StateDynamicsConfig.error_predictive_coding(
            max_steps=10,
            step_size=0.1,
            beta=0.5,
        )
    )
    credit = BackpropCredit(CreditAssignmentConfig.gradient())
    update = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.01))
    
    system_epc = compose_system(substrate, geometry, epc_dynamics, credit, update)
    
    # Predictive Settling dynamics
    ps_dynamics = PredictiveSettlingDynamics(
        StateDynamicsConfig.predictive_settling(
            max_steps=10,
            step_size=0.1,
            beta=0.5,
        )
    )
    system_ps = compose_system(substrate, geometry, ps_dynamics, credit, update)
    
    x = torch.randn(4, 784)
    y = torch.randint(0, 10, (4,))
    
    # Forward EPC
    logits_epc = system_epc.forward(x)
    loss_epc = torch.nn.functional.cross_entropy(logits_epc, y)
    
    # Forward PS
    logits_ps = system_ps.forward(x)
    loss_ps = torch.nn.functional.cross_entropy(logits_ps, y)
    
    assert torch.isfinite(loss_epc), "EPC loss not finite"
    assert torch.isfinite(loss_ps), "PS loss not finite"
    
    # Both should produce valid gradients
    loss_epc.backward()
    loss_ps.backward()
    
    for name, param in system_epc.named_parameters():
        if param.grad is not None:
            assert torch.isfinite(param.grad).all(), f"Non-finite EPC gradient in {name}"
    
    for name, param in system_ps.named_parameters():
        if param.grad is not None:
            assert torch.isfinite(param.grad).all(), f"Non-finite PS gradient in {name}"
    
    print("  ✓ EPC settle works")
    return True


def main():
    """Run all one-step wiring probes."""
    print("=" * 60)
    print("TODO97 S4: One-step wiring probes")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("Graph batching", test_graph_batching()))
    except Exception as e:
        print(f"  ✗ Graph batching failed: {e}")
        results.append(("Graph batching", False))
    
    try:
        results.append(("Conv vs feedforward", test_conv_vs_feedforward()))
    except Exception as e:
        print(f"  ✗ Conv vs feedforward failed: {e}")
        results.append(("Conv vs feedforward", False))
    
    try:
        results.append(("PC-ALM pseudo-gradient", test_pc_alm_pseudo_gradient()))
    except Exception as e:
        print(f"  ✗ PC-ALM pseudo-gradient failed: {e}")
        results.append(("PC-ALM pseudo-gradient", False))
    
    try:
        results.append(("EPC settle", test_epc_settle()))
    except Exception as e:
        print(f"  ✗ EPC settle failed: {e}")
        results.append(("EPC settle", False))
    
    print("=" * 60)
    print("Summary:")
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    print("=" * 60)
    
    if all_passed:
        print("All probes PASSED")
        return 0
    else:
        print("Some probes FAILED")
        return 1


if __name__ == "__main__":
    exit(main())