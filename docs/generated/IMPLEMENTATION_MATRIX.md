| ID | KIND | AXIS | BACKENDS | STATUS | KERNEL TECH | SUMMARY |
|----|------|------|----------|--------|-------------|---------|
| primitive.credit_assignment.local_goodness | primitive | credit_assignment | reference,kernel | reference_only | triton | Layer-local contrastive credit assignment (Forward-Forward a |
| primitive.credit_assignment.pc_alm | primitive | credit_assignment | reference,kernel | kernel_unverified | triton | Local Hebbian credit assignment using dual variables from PC |
| primitive.credit_assignment.random_projections | primitive | credit_assignment | reference,kernel | kernel_unverified | triton | Fixed random feedback matrix credit assignment (Feedback Ali |
| primitive.credit_assignment.temporal_trace | primitive | credit_assignment | reference,kernel | kernel_unverified | triton | Spike-timing correlations (STDP) for credit assignment. |
| primitive.credit_assignment.homeostatic | primitive | credit_assignment | reference,kernel | reference_only | triton | Homeostatic synaptic scaling with timing-asymmetric STDP |
| primitive.credit_assignment.reverse_mode | primitive | credit_assignment | reference,kernel | reference_only | triton | Reverse-mode autograd credit (backprop baseline). |
| primitive.credit_assignment.target_inversion | primitive | credit_assignment | reference,kernel | reference_only | triton | Target Propagation with transpose feedback for local target  |
| primitive.credit_assignment.thermodynamic_contrast | primitive | credit_assignment | reference,kernel | reference_only | triton | Equilibrium Propagation contrastive credit assignment using  |
| primitive.geometry.fabric_pc | primitive | geometry | reference,kernel | reference_only | triton | Arbitrary node-edge graph topology for predictive coding (ad |
| primitive.geometry.feedforward_dag | primitive | geometry | reference,kernel | reference_only | triton | Standard feedforward DAG topology (MLP/CNN) with configurabl |
| primitive.geometry.nca | primitive | geometry | reference,kernel | reference_only | triton | Neural Cellular Automaton: shared cell MLP on 2D grid with l |
| primitive.geometry.ntm | primitive | geometry | reference,kernel | reference_only | triton | Neural Turing Machine with LSTM controller and content-addre |
| primitive.geometry.recurrent_attractor | primitive | geometry | reference,kernel | reference_only | triton | Recurrent attractor geometry for energy-based models like Eq |
| primitive.geometry.spatial_lattice_3d | primitive | geometry | reference,kernel | reference_only | triton | 3D spatial lattice topology with local connectivity for neur |
| primitive.geometry.tile_mesh | primitive | geometry | reference,kernel | kernel_unverified | triton | TileNet mesh topology with modular independent tiles and loc |
| primitive.parameter_update.elastic_consolidation | primitive | parameter_update | reference,kernel | reference_only | triton | Elastic Weight Consolidation (EWC) with Fisher information |
| primitive.parameter_update.euclidean | primitive | parameter_update | reference,kernel | reference_only | triton | Standard Euclidean parameter update (SGD with optional momen |
| primitive.parameter_update.muon | primitive | parameter_update | reference,kernel | kernel_unverified | triton | Orthogonal parameter updates via Riemannian optimization on  |
| primitive.parameter_update.natural_gradient | primitive | parameter_update | reference,kernel | reference_only | triton | Natural gradient parameter update with Fisher geometry preco |
| primitive.parameter_update.spectral_constrained | primitive | parameter_update | reference,kernel | reference_only | triton | Spectral-constrained parameter update. |
| primitive.plasticity.closed_form_ridge | primitive | plasticity | reference,kernel | reference_only | triton | Closed-form ridge regression plasticity for supervised fast- |
| primitive.plasticity.fast_weight | primitive | plasticity | reference,kernel | kernel_unverified | triton | Episode-local associative memory via Hebbian outer-product w |
| primitive.plasticity.null | primitive | plasticity | reference,kernel | reference_only | triton | Null plasticity (zero-extension): plastic state unchanged, m |
| primitive.plasticity.routing | primitive | plasticity | reference,kernel | kernel_unverified | triton | State-dependent pathway gating with Gumbel-Softmax routing a |
| primitive.plasticity.rule_state | primitive | plasticity | reference,kernel | reference_only | triton | Rule State Plasticity (Z3): frozen-θ algorithm switching via |
| primitive.plasticity.substrate_coupled | primitive | plasticity | reference,kernel | reference_only | triton | Substrate-coupled plasticity. |
| primitive.plasticity.temporal_psi | primitive | plasticity | reference,kernel | reference_only | triton | Trace-decayed ridge regression plasticity for task-switching |
| primitive.state_dynamics.diffusion | primitive | state_dynamics | reference,kernel | reference_only | triton | Langevin dynamics over the geometry's Hopfield energy with s |
| primitive.state_dynamics.energy_minimization | primitive | state_dynamics | reference,kernel | kernel_verified | torch_compile | Energy-based settling (Equilibrium Propagation, Hopfield, CH |
| primitive.state_dynamics.instantaneous_pass | primitive | state_dynamics | reference,kernel | reference_only | triton | Single-pass feedforward dynamics for Backprop and Forward-Fo |
| primitive.state_dynamics.lazy_state_dynamics | primitive | state_dynamics | reference,kernel | reference_only | triton | Sequential (Gauss-Seidel) EqProp settle with lazy per-layer  |
| primitive.state_dynamics.pc_alm_settling | primitive | state_dynamics | reference,kernel | kernel_unverified | triton | Primal-dual settling dynamics for PC-ALM. |
| primitive.state_dynamics.predictive_settling | primitive | state_dynamics | reference,kernel | kernel_verified | torch_compile | Predictive coding settling dynamics (PCN). |
| primitive.state_dynamics.spike_integration | primitive | state_dynamics | reference,kernel | reference_only | triton | Spike integration dynamics (LIF/Izhikevich). |
| primitive.substrate.complex | primitive | substrate | reference,kernel | reference_only | triton | Digital substrate with complex-valued state space for holomo |
| primitive.substrate.digital | primitive | substrate | reference,kernel | reference_only | triton | Digital substrate with configurable precision, noise, and sp |
| primitive.substrate.memristive | primitive | substrate | reference,kernel | reference_only | triton | Memristive substrate with IR-drop and conductance bounds. |
| primitive.substrate.neuromorphic | primitive | substrate | reference,kernel | reference_only | triton | Neuromorphic substrate with async spikes. |
| primitive.substrate.noisy | primitive | substrate | reference,kernel | reference_only | triton | Digital substrate with configurable additive Gaussian noise  |
| primitive.substrate.photonic | primitive | substrate | reference,kernel | reference_only | triton | Optical/photonic substrate with phase/amplitude encoding |
| primitive.substrate.quantum | primitive | substrate | reference,kernel | reference_only | triton | Quantum substrate with unitary gate operations |
| primitive.substrate.sparse | primitive | substrate | reference,kernel | reference_only | triton | Digital substrate with configurable sparsity constraints for |
| primitive.substrate.ternary | primitive | substrate | reference,kernel | reference_only | triton | Digital substrate with ternary weight quantization {-α, 0, + |
| algorithm.backprop | algorithm |  | reference,kernel | kernel_verified | torch_compile | Standard backpropagation with automatic differentiation. |
| algorithm.dfa | algorithm |  | reference,kernel | kernel_unverified | triton | Direct Feedback Alignment with output-to-all-layers fixed ra |
| algorithm.diffusion_eqprop | algorithm |  | reference,kernel | reference_only | torch_compile | Diffusion Equilibrium Propagation with continuous-time dynam |
| algorithm.directed_ep | algorithm |  | reference,kernel | reference_only | torch_compile | Directed Equilibrium Propagation with Feedback Alignment cre |
| algorithm.eqprop | algorithm |  | reference,kernel | kernel_unverified | triton | Equilibrium Propagation: energy-based local contrastive lear |
| algorithm.fa | algorithm |  | reference,kernel | kernel_unverified | triton | Feedback Alignment with fixed random feedback matrices. |
| algorithm.fast_weight | algorithm |  | reference,kernel | kernel_unverified | triton | 6-D Joint: episode-local associative memory via fast-weight  |
| algorithm.ff | algorithm |  | reference,kernel | kernel_unverified | triton | Forward-Forward: layer-local objectives, no backward pass. |
| algorithm.finite_nudge_ep | algorithm |  | reference,kernel | reference_only | torch_compile | Finite-Nudge Equilibrium Propagation with large β |
| algorithm.hebbian | algorithm |  | reference,kernel | kernel_unverified | triton | Hebbian learning: neurons that fire together, wire together. |
| algorithm.holomorphic_ep | algorithm |  | reference,kernel | reference_only | torch_compile | Holomorphic Equilibrium Propagation with complex-valued dyna |
| algorithm.momentum_eqprop | algorithm |  | reference,kernel | reference_only | torch_compile | Momentum Equilibrium Propagation with heavy-ball dynamics |
| algorithm.pc | algorithm |  | reference,kernel | kernel_unverified | triton | Predictive Coding: hierarchical prediction error minimizatio |
| algorithm.pcalm | algorithm |  | reference,kernel | kernel_unverified | triton | Augmented Lagrangian Predictive Coding. |
| algorithm.pepita | algorithm |  | reference,kernel | kernel_unverified | triton | PEPITA: fixed random B, error-modulated second forward pass, |
| algorithm.routing | algorithm |  | reference,kernel | kernel_unverified | triton | 6-D Joint: state-dependent gating with RoutingPlasticity. |
| algorithm.sparse_eqprop | algorithm |  | reference,kernel | reference_only | torch_compile | Sparse Equilibrium Propagation with dynamic sparsity |
| algorithm.spiking_snn | algorithm |  | reference,kernel | kernel_unverified | triton | Spiking Neural Network: LIF neurons with STDP credit assignm |
| algorithm.ternary_eqprop | algorithm |  | reference,kernel | reference_only | torch_compile | Ternary-Weight Equilibrium Propagation with STE quantization |
| algorithm.tile | algorithm |  | reference,kernel | kernel_unverified | triton | TileNet: modular tiled architecture with local connectivity. |
| algorithm.tp | algorithm |  | reference,kernel | kernel_unverified | triton | Target Propagation with transpose feedback and predictive se |
