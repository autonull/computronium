"""Preset Factory Functions for Common Bioplausible Systems.

Provides one-line system construction for common 5-D and 6-D coordinates.
Instead of 20 lines of config, users can call:
    system = create_backprop_mlp(input_dim=784, hidden_dims=(256, 128), output_dim=10)
    system = create_eqprop_mlp(input_dim=784, hidden_dims=(256, 128), output_dim=10, beta=0.5, n_iters=20)
    system = create_fa_mlp(input_dim=784, hidden_dims=(256, 128), output_dim=10)
    system = create_routing_mlp(input_dim=784, hidden_dims=(256, 128), output_dim=10)
    system = create_fast_weight_mlp(input_dim=784, hidden_dims=(256, 128), output_dim=10)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.core.plasticity import (
    FastWeightPlasticity,
    RoutingPlasticity,
)
from computronium.core.system_trainer import (
    compose_joint_system,
    compose_system,
)
from computronium.ontology import (
    BackpropCredit,
    CreditAssignmentConfig,
    DiffusionDynamics,
    DigitalSubstrate,
    EnergyMinimizationDynamics,
    EuclideanUpdate,
    FeedforwardGeometry,
    GeometryConfig,
    InstantaneousDynamics,
    LemmaCredit,
    LocalGoodnessCredit,
    MemristiveSubstrate,
    NeuromorphicSubstrate,
    ParameterUpdateConfig,
    PepitaCredit,
    PredictiveSettlingDynamics,
    RandomProjectionsCredit,
    RecurrentGeometry,
    SpikeIntegrationDynamics,
    StateDynamicsConfig,
    SubstrateConfig,
    TargetInversionCredit,
    TemporalTraceCredit,
    ThermodynamicContrast,
)

if TYPE_CHECKING:
    from computronium.core.system_trainer import JointSystem
    from computronium.ontology import System


def _default_substrate(device: str = "cpu") -> DigitalSubstrate:
    """Create a default digital substrate."""
    return DigitalSubstrate(
        SubstrateConfig(
            precision="float32",
            noise_level=0.0,
            weight_bounds=None,
            sparsity=0.0,
            device=device,
        )
    )


def _mlp_geometry(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    init_scale: float = 0.1,
) -> FeedforwardGeometry:
    """Create a standard MLP feedforward geometry."""
    return FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=input_dim,
            output_dim=output_dim,
            hidden_dims=hidden_dims,
            init_scale=init_scale,
        )
    )


def _recurrent_geometry(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    init_scale: float = 0.1,
) -> RecurrentGeometry:
    """Create a recurrent geometry for EqProp."""
    # Use the last hidden dim as the recurrent state dimension
    hidden_dim = hidden_dims[-1] if hidden_dims else output_dim
    return RecurrentGeometry(
        GeometryConfig.recurrent(
            input_dim=input_dim,
            output_dim=output_dim,
            hidden_dims=hidden_dims,
            init_scale=init_scale,
        ),
        hidden_dim=hidden_dim,
    )


def _default_credit() -> BackpropCredit:
    """Create default backprop credit assignment."""
    return BackpropCredit(CreditAssignmentConfig.gradient())


def _eqprop_credit(beta: float = 0.5) -> ThermodynamicContrast:
    """Create EqProp thermodynamic contrast credit assignment."""
    return ThermodynamicContrast(
        CreditAssignmentConfig.thermodynamic_contrast(beta=beta)
    )


def _default_update(lr: float = 0.001) -> EuclideanUpdate:
    """Create default Euclidean update."""
    return EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=lr))


def _instant_backprop_system(
    substrate: DigitalSubstrate | MemristiveSubstrate | NeuromorphicSubstrate,
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    lr: float,
    init_scale: float,
) -> System:
    """Compose a Digital/Memristive × Feedforward backprop MLP (5-D)."""
    geometry = _mlp_geometry(input_dim, hidden_dims, output_dim, init_scale)
    dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    return compose_system(
        substrate, geometry, dynamics, _default_credit(), _default_update(lr)
    )


# ============================================================
# 5-D System Factories (Standard Ontology)
# ============================================================


def create_backprop_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    lr: float = 0.001,
    init_scale: float = 0.1,
    device: str = "cpu",
    checkpoint_segments: int | None = None,
) -> System:
    """Create a standard Backprop MLP system (5-D coordinate).

    Args:
        input_dim: Input dimension (e.g., 784 for MNIST)
        hidden_dims: Tuple of hidden layer dimensions (e.g., (256, 128))
        output_dim: Output dimension (e.g., 10 for MNIST)
        lr: Learning rate
        init_scale: Weight initialization scale
        device: Target device ("cpu" or "cuda")
        checkpoint_segments: Activation-checkpointing segment count for the
            geometry forward; ``None`` runs plain (every layer activation
            retained). This is the ``backprop+checkpointing`` ladder arm
            (TODO93 T4b).

    Returns:
        A composed 5-D System with Backprop credit assignment.
    """
    system = _instant_backprop_system(
        _default_substrate(device), input_dim, hidden_dims, output_dim, lr, init_scale
    )
    if checkpoint_segments is not None:
        from computronium.core.gradient_checkpointing import (
            enable_gradient_checkpointing,
        )

        enable_gradient_checkpointing(system, checkpoint_segments)
    return system


def create_memristive_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    lr: float = 0.001,
    noise_level: float = 0.05,
    init_scale: float = 0.1,
    device: str = "cpu",
) -> System:
    """Create a memristive-substrate Backprop MLP system (5-D coordinate).

    Same coordinate as :func:`create_backprop_mlp` with the S-axis swapped:
    weights are realized as differential-pair conductances — every device
    non-negative and bounded in [0, 1] with int8 quantization, the pair
    difference carrying the signed weight — and activations carry IR-drop
    noise of ``noise_level`` standard deviations.

    Args:
        input_dim: Input dimension (e.g., 784 for MNIST)
        hidden_dims: Tuple of hidden layer dimensions (e.g., (256, 128))
        output_dim: Output dimension (e.g., 10 for MNIST)
        lr: Learning rate
        noise_level: IR-drop noise standard deviation on activations
        init_scale: Weight initialization scale
        device: Target device ("cpu" or "cuda")

    Returns:
        A composed 5-D System on the memristive substrate.
    """
    substrate = MemristiveSubstrate(
        SubstrateConfig.memristive(noise_level=noise_level, device=device)
    )
    return _instant_backprop_system(
        substrate, input_dim, hidden_dims, output_dim, lr, init_scale
    )


def create_neuromorphic_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    lr: float = 0.001,
    noise_level: float = 0.0,
    sparsity: float = 0.95,
    init_scale: float = 0.1,
    device: str = "cpu",
) -> System:
    """Create a neuromorphic-substrate Backprop MLP system (5-D coordinate).

    Same coordinate as :func:`create_backprop_mlp` with the S-axis swapped:
    the state is thinned to the active spike set each forward step — every
    activation element survives with probability ``1 - sparsity`` — plus
    additive state noise of ``noise_level`` standard deviations. At the
    default ``sparsity`` the thinning walls learning at chance.

    Args:
        input_dim: Input dimension (e.g. 784 for MNIST)
        hidden_dims: Tuple of hidden layer dimensions
        output_dim: Output dimension
        lr: Learning rate
        noise_level: Additive state-noise standard deviation
        sparsity: Target spike sparsity ratio [0, 1) (fraction dropped per step)
        init_scale: Weight initialization scale
        device: Target device ("cpu" or "cuda")

    Returns:
        A composed 5-D System on the neuromorphic substrate.
    """
    substrate = NeuromorphicSubstrate(
        SubstrateConfig.neuromorphic(
            noise_level=noise_level, sparsity=sparsity, device=device
        )
    )
    return _instant_backprop_system(
        substrate, input_dim, hidden_dims, output_dim, lr, init_scale
    )


def create_eqprop_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...] = (512, 512, 512),
    output_dim: int = 10,
    beta: float = 0.1,
    inference_steps: int = 20,
    lr: float = 0.001,
    init_scale: float = 0.1,
    device: str = "cpu",
) -> System:
    """Create an Equilibrium Propagation MLP system (5-D coordinate).

    Args:
        input_dim: Input dimension (e.g., 784 for MNIST)
        hidden_dims: Tuple of hidden layer dimensions (default: 3 layers of 512)
        output_dim: Output dimension (e.g., 10 for MNIST)
        beta: Nudge strength for EqProp (default: 0.1, matches vision parity)
        inference_steps: Number of settling iterations (default: 20)
        lr: Learning rate (default: 0.001, matches vision parity)
        init_scale: Weight initialization scale
        device: Target device ("cpu" or "cuda")

    Returns:
        A composed 5-D System with ThermodynamicContrast credit assignment
        and EnergyMinimization dynamics.
    """
    substrate = _default_substrate(device)
    geometry = _recurrent_geometry(input_dim, hidden_dims, output_dim, init_scale)
    dynamics = EnergyMinimizationDynamics(
        StateDynamicsConfig.energy_minimization(
            max_steps=inference_steps,
            convergence_threshold=1e-4,
            convergence_start=5,
            step_size=0.1,
            beta=beta,
            track_free_energy_per_iter=False,
        )
    )
    credit = _eqprop_credit(beta)
    update = _default_update(lr)

    return compose_system(substrate, geometry, dynamics, credit, update)


def create_fa_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    lr: float = 0.001,
    init_scale: float = 0.1,
    feedback_scale: float = 0.01,
    device: str = "cpu",
) -> System:
    """Create a Feedback Alignment MLP system (5-D coordinate).

    Args:
        input_dim: Input dimension (e.g., 784 for MNIST)
        hidden_dims: Tuple of hidden layer dimensions (e.g., (256, 128))
        output_dim: Output dimension (e.g., 10 for MNIST)
        lr: Learning rate
        init_scale: Weight initialization scale
        feedback_scale: Scale for random feedback matrix initialization
        device: Target device ("cpu" or "cuda")

    Returns:
        A composed 5-D System with RandomProjections (FA) credit assignment.
    """
    substrate = _default_substrate(device)
    geometry = _mlp_geometry(input_dim, hidden_dims, output_dim, init_scale)
    dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    credit = RandomProjectionsCredit(
        CreditAssignmentConfig.random_projections(
            beta=0.5,
            feedback_scale=feedback_scale,
        )
    )
    update = _default_update(lr)

    return compose_system(substrate, geometry, dynamics, credit, update)


def create_ff_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    layer_lr: float = 0.03,
    init_scale: float = 0.1,
    device: str = "cpu",
) -> System:
    """Create a Forward-Forward MLP system (5-D coordinate, native ontology).

    The reference rung is the pipeline's layer-local goodness contrast
    (``LocalGoodnessCredit``); the kernel rung binds ``FFKernelBackend`` to the
    same geometry. Composing the axes is this function's whole job: a preset
    that also owns a private layer stack trains weights the system never reads.
    """
    substrate = _default_substrate(device)
    geometry = _mlp_geometry(input_dim, hidden_dims, output_dim, init_scale)
    dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    credit = LocalGoodnessCredit(CreditAssignmentConfig.local_goodness())
    update = _default_update(layer_lr)
    return compose_system(substrate, geometry, dynamics, credit, update)


def create_lemma_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    lr: float = 0.01,
    init_scale: float = 0.1,
    device: str = "cpu",
) -> System:
    """Create a LEMMA MLP system (5-D coordinate).

    Per-layer closed-form error-modulated credit
    (:class:`LemmaCredit`) — NOT the published PEPITA rule (TODO18 2.4).

    Args:
        input_dim: Input dimension
        hidden_dims: Tuple of hidden layer dimensions
        output_dim: Output dimension
        lr: Learning rate
        init_scale: Weight initialization scale
        device: Target device

    Returns:
        A composed 5-D System with FeedforwardGeometry + InstantaneousDynamics
        + LemmaCredit + EuclideanUpdate
    """
    substrate = _default_substrate(device)
    geometry = _mlp_geometry(input_dim, hidden_dims, output_dim, init_scale)
    dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    credit = LemmaCredit()
    update = _default_update(lr)

    return compose_system(substrate, geometry, dynamics, credit, update)


def create_pepita_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    lr: float = 0.01,
    init_scale: float = 0.1,
    device: str = "cpu",
) -> System:
    """Create a PEPITA MLP system (5-D coordinate).

    Published PEPITA (arXiv 2201.11665): one input-space fixed random B,
    error-modulated second forward pass, autograd update
    (:class:`PepitaCredit`). Memory is backprop-class.

    Args:
        input_dim: Input dimension
        hidden_dims: Tuple of hidden layer dimensions
        output_dim: Output dimension
        lr: Learning rate
        init_scale: Weight initialization scale
        device: Target device

    Returns:
        A composed 5-D System with FeedforwardGeometry + InstantaneousDynamics
        + PepitaCredit + EuclideanUpdate
    """
    substrate = _default_substrate(device)
    geometry = _mlp_geometry(input_dim, hidden_dims, output_dim, init_scale)
    dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    credit = PepitaCredit()
    update = _default_update(lr)

    return compose_system(substrate, geometry, dynamics, credit, update)


def create_tp_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    lr: float = 0.001,
    init_scale: float = 0.1,
    beta: float = 0.1,
    settle_steps: int = 30,
    device: str = "cpu",
) -> System:
    """Create a Target Propagation MLP system (5-D coordinate).

    Target Propagation uses learned inverse mappings to propagate targets
    backwards through the network instead of gradients.

    Args:
        input_dim: Input dimension
        hidden_dims: Tuple of hidden layer dimensions
        output_dim: Output dimension
        lr: Learning rate
        init_scale: Weight initialization scale
        beta: Nudge strength for target propagation
        settle_steps: Number of settling iterations for predictive dynamics
        device: Target device

    Returns:
        A composed 5-D System with FeedforwardGeometry + PredictiveSettlingDynamics
        + TargetInversionCredit + EuclideanUpdate
    """
    substrate = _default_substrate(device)
    geometry = _mlp_geometry(input_dim, hidden_dims, output_dim, init_scale)
    dynamics = PredictiveSettlingDynamics(
        StateDynamicsConfig.predictive_settling(
            max_steps=settle_steps,
            beta=beta,
        )
    )
    credit = TargetInversionCredit(
        CreditAssignmentConfig.target_inversion(
            beta=beta,
            feedback_scale=0.01,
        )
    )
    update = _default_update(lr)

    return compose_system(substrate, geometry, dynamics, credit, update)


def create_pc_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    lr: float = 0.001,
    init_scale: float = 0.1,
    beta: float = 0.5,
    settle_steps: int = 30,
    device: str = "cpu",
) -> System:
    """Create a Predictive Coding MLP system (5-D coordinate).

    Predictive Coding minimizes prediction errors through a hierarchy of
    top-down predictions and bottom-up error signals.

    Args:
        input_dim: Input dimension
        hidden_dims: Tuple of hidden layer dimensions
        output_dim: Output dimension
        lr: Learning rate
        init_scale: Weight initialization scale
        beta: Nudge strength for predictive coding
        settle_steps: Number of settling iterations
        device: Target device

    Returns:
        A composed 5-D System with RecurrentGeometry + PredictiveSettlingDynamics
        + LocalGoodnessCredit + EuclideanUpdate
    """
    substrate = _default_substrate(device)
    geometry = _recurrent_geometry(input_dim, hidden_dims, output_dim, init_scale)
    dynamics = PredictiveSettlingDynamics(
        StateDynamicsConfig.predictive_settling(
            max_steps=settle_steps,
            beta=beta,
        )
    )
    credit = LocalGoodnessCredit(CreditAssignmentConfig.local_goodness())
    update = _default_update(lr)

    return compose_system(substrate, geometry, dynamics, credit, update)


def create_hebbian_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    lr: float = 0.001,
    init_scale: float = 0.1,
    device: str = "cpu",
) -> System:
    """Create a Hebbian/STDP MLP system (5-D coordinate).

    Hebbian learning uses spike-timing correlations (STDP):
    neurons that fire together, wire together.

    Args:
        input_dim: Input dimension
        hidden_dims: Tuple of hidden layer dimensions
        output_dim: Output dimension
        lr: Learning rate
        init_scale: Weight initialization scale
        device: Target device

    Returns:
        A composed 5-D System with FeedforwardGeometry + InstantaneousDynamics
        + TemporalTraceCredit + EuclideanUpdate
    """
    substrate = _default_substrate(device)
    geometry = _mlp_geometry(input_dim, hidden_dims, output_dim, init_scale)
    dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    credit = TemporalTraceCredit(CreditAssignmentConfig.temporal_trace())
    update = _default_update(lr)

    return compose_system(substrate, geometry, dynamics, credit, update)


def create_snn_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    lr: float = 0.001,
    init_scale: float = 0.1,
    device: str = "cpu",
) -> System:
    """Create a Spiking Neural Network MLP system (5-D coordinate).

    SNNs use spike-based computation with temporal integration dynamics
    and temporal trace credit assignment.

    This factory now aligns with the working YAML preset (snn_mnist.yaml)
    which uses InstantaneousDynamics + LocalGoodnessCredit for compatibility
    with SystemTrainer. For true spiking dynamics, use create_spiking_snn_mlp.

    Args:
        input_dim: Input dimension
        hidden_dims: Tuple of hidden layer dimensions
        output_dim: Output dimension
        lr: Learning rate
        init_scale: Weight initialization scale
        device: Target device

    Returns:
        A composed 5-D System with FeedforwardGeometry + InstantaneousDynamics
        + LocalGoodnessCredit + EuclideanUpdate
    """
    substrate = _default_substrate(device)
    geometry = _mlp_geometry(input_dim, hidden_dims, output_dim, init_scale)
    dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    credit = LocalGoodnessCredit(CreditAssignmentConfig.local_goodness())
    update = _default_update(lr)

    return compose_system(substrate, geometry, dynamics, credit, update)


def create_spiking_snn_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    lr: float = 0.001,
    init_scale: float = 0.1,
    device: str = "cpu",
    max_steps: int = 30,
    beta: float = 0.1,
    threshold: float = 0.5,
) -> System:
    """Create a true Spiking Neural Network MLP with SpikeIntegrationDynamics and TemporalTraceCredit.

    This factory uses:
    - SpikeIntegrationDynamics: LIF membrane potential integration with thresholding
    - TemporalTraceCredit: STDP-based credit assignment using spike timing
    - FeedforwardGeometry: Standard MLP topology

    Requires SystemTrainer with spiking support (implemented in compose_system).

    Args:
        input_dim: Input dimension
        hidden_dims: Tuple of hidden layer dimensions
        output_dim: Output dimension
        lr: Learning rate
        init_scale: Weight initialization scale
        device: Target device
        max_steps: Number of simulation time steps
        beta: Nudge strength for nudged phase
        threshold: Spike threshold (lower = more spikes)

    Returns:
        A composed 5-D System with FeedforwardGeometry + SpikeIntegrationDynamics
        + TemporalTraceCredit + EuclideanUpdate
    """
    substrate = _default_substrate(device)
    geometry = _mlp_geometry(input_dim, hidden_dims, output_dim, init_scale)
    dynamics = SpikeIntegrationDynamics(
        StateDynamicsConfig.spike_integration(
            max_steps=max_steps,
            beta=beta,
            threshold=threshold,
        )
    )
    credit = TemporalTraceCredit(
        CreditAssignmentConfig.temporal_trace(
            tau_pre=0.9,
            tau_post=0.9,
        )
    )
    update = _default_update(lr)

    return compose_system(substrate, geometry, dynamics, credit, update)


def create_directed_ep_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...] = (512, 512, 512),
    output_dim: int = 10,
    beta: float = 0.5,
    inference_steps: int = 20,
    lr: float = 0.001,
    feedback_scale: float = 0.01,
    init_scale: float = 0.1,
    device: str = "cpu",
) -> System:
    """Create a Directed Equilibrium Propagation MLP system (5-D coordinate).

    Directed EP uses Feedback Alignment within the energy-based framework:
    fixed random feedback matrices (no transport shortcut) with thermodynamic
    settling dynamics.

    Args:
        input_dim: Input dimension (e.g., 784 for MNIST)
        hidden_dims: Tuple of hidden layer dimensions (default: 3 layers of 512)
        output_dim: Output dimension (e.g., 10 for MNIST)
        beta: Nudge strength for EqProp (default: 0.5)
        inference_steps: Number of settling iterations (default: 20)
        lr: Learning rate (default: 0.001)
        feedback_scale: Scale for random feedback matrix initialization
        init_scale: Weight initialization scale
        device: Target device ("cpu" or "cuda")

    Returns:
        A composed 5-D System with RandomProjections (FA) credit assignment
        and EnergyMinimization dynamics.
    """
    substrate = _default_substrate(device)
    geometry = _recurrent_geometry(input_dim, hidden_dims, output_dim, init_scale)
    dynamics = EnergyMinimizationDynamics(
        StateDynamicsConfig.energy_minimization(
            max_steps=inference_steps,
            convergence_threshold=1e-4,
            convergence_start=5,
            step_size=0.1,
            beta=beta,
            track_free_energy_per_iter=False,
        )
    )
    credit = RandomProjectionsCredit(
        CreditAssignmentConfig.random_projections(
            beta=beta,
            feedback_scale=feedback_scale,
        )
    )
    update = _default_update(lr)

    return compose_system(substrate, geometry, dynamics, credit, update)


def create_finite_nudge_ep_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...] = (512, 512, 512),
    output_dim: int = 10,
    beta: float = 1.0,
    inference_steps: int = 20,
    lr: float = 0.001,
    init_scale: float = 0.1,
    device: str = "cpu",
) -> System:
    """Create a Finite-Nudge Equilibrium Propagation MLP system (5-D coordinate).

    Finite-Nudge EP uses large β (finite nudge) instead of infinitesimal limit.
    Stronger supervision signals while maintaining equilibrium dynamics.

    Args:
        input_dim: Input dimension (e.g., 784 for MNIST)
        hidden_dims: Tuple of hidden layer dimensions (default: 3 layers of 512)
        output_dim: Output dimension (e.g., 10 for MNIST)
        beta: Nudge strength for EqProp (default: 1.0, finite nudge)
        inference_steps: Number of settling iterations (default: 20)
        lr: Learning rate (default: 0.001)
        init_scale: Weight initialization scale
        device: Target device ("cpu" or "cuda")

    Returns:
        A composed 5-D System with ThermodynamicContrast credit assignment
        and EnergyMinimization dynamics with finite β.
    """
    substrate = _default_substrate(device)
    geometry = _recurrent_geometry(input_dim, hidden_dims, output_dim, init_scale)
    dynamics = EnergyMinimizationDynamics(
        StateDynamicsConfig.energy_minimization(
            max_steps=inference_steps,
            convergence_threshold=1e-4,
            convergence_start=5,
            step_size=0.1,
            beta=beta,
            track_free_energy_per_iter=False,
        )
    )
    credit = ThermodynamicContrast(
        CreditAssignmentConfig.thermodynamic_contrast(beta=beta)
    )
    update = _default_update(lr)

    return compose_system(substrate, geometry, dynamics, credit, update)


def create_ternary_eqprop_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...] = (512, 512, 512),
    output_dim: int = 10,
    beta: float = 0.5,
    inference_steps: int = 20,
    lr: float = 0.001,
    init_scale: float = 0.1,
    weight_bounds: tuple[float, float] = (-1.0, 1.0),
    device: str = "cpu",
) -> System:
    """Create a Ternary-Weight Equilibrium Propagation MLP system (5-D coordinate).

    Ternary EP constrains weights to {-α, 0, +α} using STE-based quantization.

    Args:
        input_dim: Input dimension (e.g., 784 for MNIST)
        hidden_dims: Tuple of hidden layer dimensions (default: 3 layers of 512)
        output_dim: Output dimension (e.g., 10 for MNIST)
        beta: Nudge strength for EqProp (default: 0.5)
        inference_steps: Number of settling iterations (default: 20)
        lr: Learning rate (default: 0.001)
        init_scale: Weight initialization scale
        weight_bounds: Ternary weight bounds (default: (-1.0, 1.0))
        device: Target device ("cpu" or "cuda")

    Returns:
        A composed 5-D System on TernarySubstrate with ThermodynamicContrast
        credit assignment and EnergyMinimization dynamics.
    """
    from computronium.ontology import SubstrateConfig, TernarySubstrate

    substrate = TernarySubstrate(
        SubstrateConfig.ternary(weight_bounds=weight_bounds, device=device)
    )
    geometry = _recurrent_geometry(input_dim, hidden_dims, output_dim, init_scale)
    dynamics = EnergyMinimizationDynamics(
        StateDynamicsConfig.energy_minimization(
            max_steps=inference_steps,
            convergence_threshold=1e-4,
            convergence_start=5,
            step_size=0.1,
            beta=beta,
            track_free_energy_per_iter=False,
        )
    )
    credit = ThermodynamicContrast(
        CreditAssignmentConfig.thermodynamic_contrast(beta=beta)
    )
    update = _default_update(lr)

    return compose_system(substrate, geometry, dynamics, credit, update)


def create_momentum_eqprop_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...] = (512, 512, 512),
    output_dim: int = 10,
    beta: float = 0.5,
    momentum: float = 0.9,
    inference_steps: int = 20,
    lr: float = 0.001,
    init_scale: float = 0.1,
    device: str = "cpu",
) -> System:
    """Create a Momentum Equilibrium Propagation MLP system (5-D coordinate).

    Momentum EP uses heavy-ball settling dynamics for faster equilibrium convergence.

    Args:
        input_dim: Input dimension (e.g., 784 for MNIST)
        hidden_dims: Tuple of hidden layer dimensions (default: 3 layers of 512)
        output_dim: Output dimension (e.g., 10 for MNIST)
        beta: Nudge strength for EqProp (default: 0.5)
        momentum: Heavy-ball momentum coefficient (default: 0.9)
        inference_steps: Number of settling iterations (default: 20)
        lr: Learning rate (default: 0.001)
        init_scale: Weight initialization scale
        device: Target device ("cpu" or "cuda")

    Returns:
        A composed 5-D System with EnergyMinimization(momentum) dynamics
        and ThermodynamicContrast credit assignment.
    """
    substrate = _default_substrate(device)
    geometry = _recurrent_geometry(input_dim, hidden_dims, output_dim, init_scale)
    dynamics = EnergyMinimizationDynamics(
        StateDynamicsConfig.energy_minimization(
            max_steps=inference_steps,
            convergence_threshold=1e-4,
            convergence_start=5,
            step_size=0.1,
            beta=beta,
            momentum=momentum,
            track_free_energy_per_iter=False,
        )
    )
    credit = ThermodynamicContrast(
        CreditAssignmentConfig.thermodynamic_contrast(beta=beta)
    )
    update = _default_update(lr)

    return compose_system(substrate, geometry, dynamics, credit, update)


def create_sparse_eqprop_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...] = (512, 512, 512),
    output_dim: int = 10,
    beta: float = 0.5,
    inference_steps: int = 20,
    lr: float = 0.001,
    sparsity: float = 0.9,
    init_scale: float = 0.1,
    device: str = "cpu",
) -> System:
    """Create a Sparse Equilibrium Propagation MLP system (5-D coordinate).

    Sparse EP uses dynamic sparsity masks with efficient sparse matmul.

    Args:
        input_dim: Input dimension (e.g., 784 for MNIST)
        hidden_dims: Tuple of hidden layer dimensions (default: 3 layers of 512)
        output_dim: Output dimension (e.g., 10 for MNIST)
        beta: Nudge strength for EqProp (default: 0.5)
        inference_steps: Number of settling iterations (default: 20)
        lr: Learning rate (default: 0.001)
        sparsity: Target sparsity ratio (default: 0.9)
        init_scale: Weight initialization scale
        device: Target device ("cpu" or "cuda")

    Returns:
        A composed 5-D System on SparseSubstrate with ThermodynamicContrast
        credit assignment and EnergyMinimization dynamics.
    """
    from computronium.ontology import SparseSubstrate, SubstrateConfig

    substrate = SparseSubstrate(
        SubstrateConfig.sparse(sparsity=sparsity, device=device)
    )
    geometry = _recurrent_geometry(input_dim, hidden_dims, output_dim, init_scale)
    dynamics = EnergyMinimizationDynamics(
        StateDynamicsConfig.energy_minimization(
            max_steps=inference_steps,
            convergence_threshold=1e-4,
            convergence_start=5,
            step_size=0.1,
            beta=beta,
            track_free_energy_per_iter=False,
        )
    )
    credit = ThermodynamicContrast(
        CreditAssignmentConfig.thermodynamic_contrast(beta=beta)
    )
    update = _default_update(lr)

    return compose_system(substrate, geometry, dynamics, credit, update)


def create_diffusion_eqprop_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...] = (512, 512, 512),
    output_dim: int = 10,
    beta: float = 0.5,
    inference_steps: int = 20,
    lr: float = 0.001,
    init_scale: float = 0.1,
    device: str = "cpu",
) -> System:
    """Create a Diffusion Equilibrium Propagation MLP system (5-D coordinate).

    Diffusion EP uses continuous-time diffusion settling dynamics.

    Args:
        input_dim: Input dimension (e.g., 784 for MNIST)
        hidden_dims: Tuple of hidden layer dimensions (default: 3 layers of 512)
        output_dim: Output dimension (e.g., 10 for MNIST)
        beta: Nudge strength for EqProp (default: 0.5)
        inference_steps: Number of settling iterations (default: 20)
        lr: Learning rate (default: 0.001)
        init_scale: Weight initialization scale
        device: Target device ("cpu" or "cuda")

    Returns:
        A composed 5-D System with DiffusionDynamics and ThermodynamicContrast
        credit assignment.
    """
    substrate = _default_substrate(device)
    geometry = _recurrent_geometry(input_dim, hidden_dims, output_dim, init_scale)
    dynamics = DiffusionDynamics(
        StateDynamicsConfig.diffusion(
            max_steps=inference_steps,
            step_size=0.1,
            beta=beta,
        )
    )
    credit = ThermodynamicContrast(
        CreditAssignmentConfig.thermodynamic_contrast(beta=beta)
    )
    update = _default_update(lr)

    return compose_system(substrate, geometry, dynamics, credit, update)


def create_holomorphic_ep_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...] = (512, 512, 512),
    output_dim: int = 10,
    beta: float = 0.5,
    inference_steps: int = 20,
    lr: float = 0.001,
    init_scale: float = 0.1,
    device: str = "cpu",
) -> System:
    """Create a Holomorphic Equilibrium Propagation MLP system (5-D coordinate).

    Holomorphic EP uses complex-valued Equilibrium Propagation with holomorphic
    (analytic) activation functions and conjugate-transpose feedback pathways.
    Note: complex-valued, not quantum — the quantum label applies only when
    running on the specific simulated unitary-gate substrate.

    Args:
        input_dim: Input dimension (e.g., 784 for MNIST)
        hidden_dims: Tuple of hidden layer dimensions (default: 3 layers of 512)
        output_dim: Output dimension (e.g., 10 for MNIST)
        beta: Nudge strength for EqProp (default: 0.5)
        inference_steps: Number of settling iterations (default: 20)
        lr: Learning rate (default: 0.001)
        init_scale: Weight initialization scale
        device: Target device ("cpu" or "cuda")

    Returns:
        A composed 5-D System on QuantumSubstrate with ThermodynamicContrast
        credit assignment and EnergyMinimization dynamics.
    """
    from computronium.ontology import QuantumSubstrate, SubstrateConfig

    substrate = QuantumSubstrate(SubstrateConfig.quantum(device=device))
    geometry = _recurrent_geometry(input_dim, hidden_dims, output_dim, init_scale)
    dynamics = EnergyMinimizationDynamics(
        StateDynamicsConfig.energy_minimization(
            max_steps=inference_steps,
            convergence_threshold=1e-4,
            convergence_start=5,
            step_size=0.1,
            beta=beta,
            track_free_energy_per_iter=False,
        )
    )
    credit = ThermodynamicContrast(
        CreditAssignmentConfig.thermodynamic_contrast(beta=beta)
    )
    update = _default_update(lr)

    return compose_system(substrate, geometry, dynamics, credit, update)


# ============================================================
# 6-D Joint System Factories (Extended Ontology with Plasticity)
# ============================================================


def create_routing_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    lr: float = 0.001,
    init_scale: float = 0.1,
    gate_dim: int = 64,
    gate_init_scale: float = 0.1,
    device: str = "cpu",
) -> JointSystem:
    """Create an MLP with RoutingPlasticity (6-D coordinate).

    Args:
        input_dim: Input dimension
        hidden_dims: Tuple of hidden layer dimensions
        output_dim: Output dimension
        lr: Learning rate
        init_scale: Weight initialization scale
        gate_dim: Dimension of routing gates
        gate_init_scale: Initial scale for gate logits
        device: Target device

    Returns:
        A composed 6-D JointSystem with RoutingPlasticity.
    """
    substrate = _default_substrate(device)
    geometry = _mlp_geometry(input_dim, hidden_dims, output_dim, init_scale)
    dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    credit = _default_credit()
    update = _default_update(lr)

    plasticity = RoutingPlasticity(
        gate_dim=gate_dim,
        temperature=1.0,
        decay=0.99,
        learning_rate=0.01,
    )

    return compose_joint_system(
        substrate, geometry, dynamics, plasticity, credit, update
    )


def create_fast_weight_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    lr: float = 0.001,
    init_scale: float = 0.1,
    fast_weight_dim: int = 512,
    decay: float = 0.9,
    learning_rate: float = 0.1,
    device: str = "cpu",
) -> JointSystem:
    """Create an MLP with FastWeightPlasticity (6-D coordinate).

    Args:
        input_dim: Input dimension
        hidden_dims: Tuple of hidden layer dimensions
        output_dim: Output dimension
        lr: Learning rate
        init_scale: Weight initialization scale
        fast_weight_dim: Dimension of fast weight matrix
        decay: Decay factor for fast weights
        learning_rate: Hebbian learning rate for fast weights
        device: Target device

    Returns:
        A composed 6-D JointSystem with FastWeightPlasticity.
    """
    substrate = _default_substrate(device)
    geometry = _mlp_geometry(input_dim, hidden_dims, output_dim, init_scale)
    dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    credit = _default_credit()
    update = _default_update(lr)

    plasticity = FastWeightPlasticity(
        fast_weight_dim=fast_weight_dim,
        decay=decay,
        learning_rate=learning_rate,
        outer_product_scale=1.0,
    )

    return compose_joint_system(
        substrate, geometry, dynamics, plasticity, credit, update
    )


def create_tile_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    lr: float = 0.001,
    init_scale: float = 0.1,
    neurons_per_tile: int = 8,
    tiles_per_layer: int = 2,
    device: str = "cpu",
) -> System:
    """Create a Tile MLP system (5-D coordinate with TileGeometry).

    TileGeometry organizes neurons into tiles with local connectivity,
    enabling structured sparsity and efficient computation.

    Args:
        input_dim: Input dimension
        hidden_dims: Tuple of hidden layer dimensions
        output_dim: Output dimension
        lr: Learning rate
        init_scale: Weight initialization scale
        neurons_per_tile: Number of neurons per tile
        tiles_per_layer: Number of tiles per layer
        device: Target device ("cpu" or "cuda")

    Returns:
        A composed 5-D System with TileGeometry + InstantaneousDynamics
        + BackpropCredit + EuclideanUpdate
    """
    substrate = _default_substrate(device)
    geometry = _mlp_geometry(input_dim, hidden_dims, output_dim, init_scale)
    # Replace with TileGeometry
    from computronium.ontology import GeometryConfig, TileGeometry

    tile_cfg = GeometryConfig(
        input_dim=input_dim,
        output_dim=output_dim,
        hidden_dims=hidden_dims,
        num_layers=len(hidden_dims) + 1,
        topology_type="tile_mesh",
        connectivity=None,
        recurrent_weight=None,
        init_scale=init_scale,
        neurons_per_tile=neurons_per_tile,
        tiles_per_layer=tiles_per_layer,
    )
    geometry = TileGeometry(
        tile_cfg,
        neurons_per_tile=neurons_per_tile,
        tiles_per_layer=tiles_per_layer,
    )
    dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    credit = _default_credit()
    update = _default_update(lr)

    return compose_system(substrate, geometry, dynamics, credit, update)


__all__ = [  # ruff: ignore[unsorted-dunder-all]
    # 5-D factories
    "create_backprop_mlp",
    "create_eqprop_mlp",
    "create_fa_mlp",
    "create_ff_mlp",
    "create_lemma_mlp",
    "create_pepita_mlp",
    "create_tp_mlp",
    "create_pc_mlp",
    "create_hebbian_mlp",
    "create_snn_mlp",
    "create_spiking_snn_mlp",
    "create_tile_mlp",
    # Phase 7: EqProp variants
    "create_directed_ep_mlp",
    "create_finite_nudge_ep_mlp",
    "create_ternary_eqprop_mlp",
    "create_momentum_eqprop_mlp",
    "create_sparse_eqprop_mlp",
    "create_diffusion_eqprop_mlp",
    "create_holomorphic_ep_mlp",
    # 6-D factories
    "create_routing_mlp",
    "create_fast_weight_mlp",
]
