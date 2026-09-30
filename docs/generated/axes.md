# Axes Registry

Generated: 2026-09-30T13:23:50.134074
Total: 57 axes

| Structural Axis | Name | Axis Kind | Available | Prior | Override Scope | Topology Params |
|-----------------|------|-----------|-----------|-------|----------------|-----------------|
| substrate | analog | substrate | None | None | coordinate | - |
| substrate | complex | substrate | None | None | coordinate | - |
| substrate | digital | substrate | None | None | coordinate | - |
| substrate | memristive | substrate | None | None | coordinate | - |
| substrate | neuromorphic | substrate | None | None | coordinate | - |
| substrate | optical | substrate | None | None | coordinate | - |
| substrate | quantum | substrate | None | None | coordinate | - |
| substrate | sparse | substrate | None | None | coordinate | - |
| substrate | ternary | substrate | None | None | coordinate | - |
| geometry | attention | geometry | None | None | coordinate | input_dim, output_dim, num_heads |
| geometry | causal_transformer | geometry | None | None | coordinate | input_dim, output_dim, hidden_dim, num_heads, seq_len |
| geometry | conv | geometry | None | None | coordinate | input_dim, output_dim, conv_channels, kernel_size |
| geometry | feedforward | geometry | None | None | coordinate | input_dim, output_dim, hidden_dim, num_layers |
| geometry | graph | geometry | None | None | coordinate | input_dim, output_dim, hidden_dim |
| geometry | nca | geometry | None | None | coordinate | input_dim, output_dim, grid_hw |
| geometry | ntm | geometry | None | None | coordinate | input_dim, output_dim, mem_slots, mem_width |
| geometry | recurrent | geometry | None | None | coordinate | input_dim, output_dim, hidden_dim, num_layers |
| geometry | spatial_lattice | geometry | None | None | coordinate | input_dim, output_dim, lattice_dims |
| geometry | tile | geometry | None | None | coordinate | input_dim, output_dim, neurons_per_tile, tiles_per_layer |
| geometry | tile_mesh | geometry | None | None | coordinate | input_dim, output_dim, neurons_per_tile, tiles_per_layer |
| dynamics | diffusion | dynamics | None | None | coordinate | max_steps |
| dynamics | energy_minimization | dynamics | None | None | coordinate | max_steps, convergence_threshold |
| dynamics | error_predictive_coding | dynamics | None | None | coordinate | max_steps, convergence_threshold |
| dynamics | instantaneous | dynamics | None | None | coordinate | - |
| dynamics | lazy | dynamics | None | None | coordinate | - |
| dynamics | pc_alm | dynamics | None | None | coordinate | max_steps |
| dynamics | predictive_settling | dynamics | None | None | coordinate | max_steps, convergence_threshold |
| dynamics | spike_integration | dynamics | None | None | coordinate | max_steps |
| plasticity | conflict_adaptive | plasticity | None | None | coordinate | trace_decay, conflict_threshold |
| plasticity | fast_weights | plasticity | None | None | coordinate | fast_weight_dim |
| plasticity | null | plasticity | None | None | coordinate | - |
| plasticity | routing | plasticity | None | None | coordinate | gate_dim |
| plasticity | rule_state | plasticity | None | None | coordinate | num_operators |
| plasticity | substrate_coupled | plasticity | None | None | coordinate | - |
| plasticity | temporal_psi | plasticity | None | None | coordinate | trace_decay |
| credit | gradient | credit | None | None | coordinate | - |
| credit | homeostatic | credit | None | None | coordinate | - |
| credit | local_contrastive | credit | None | None | coordinate | ema_beta, contrast_threshold, contrast_objective |
| credit | local_goodness | credit | None | None | coordinate | - |
| credit | pc_alm | credit | None | None | coordinate | - |
| credit | pepita | credit | None | None | coordinate | feedback_scale |
| credit | random_projections | credit | None | None | coordinate | feedback_scale |
| credit | target_inversion | credit | None | None | coordinate | - |
| credit | temporal_trace | credit | None | None | coordinate | a_plus, a_minus, tau_pre, tau_post |
| credit | thermodynamic_contrast | credit | None | None | coordinate | - |
| update | adam | update | None | None | coordinate | beta2, eps |
| update | elastic_consolidation | update | None | None | coordinate | ewc_lambda, fisher_damping |
| update | euclidean | update | None | None | coordinate | - |
| update | lion | update | None | None | coordinate | beta2, eps |
| update | local_adam | update | None | None | coordinate | beta2, eps |
| update | mean_norm | update | None | None | coordinate | - |
| update | muon | update | None | None | coordinate | ortho_steps, momentum |
| update | natural_gradient | update | None | None | coordinate | fisher_damping |
| update | ortho_adam | update | None | None | coordinate | beta2, eps, ortho_lr |
| update | riemannian_orthogonal | update | None | None | coordinate | ortho_steps |
| update | role_split | update | None | None | coordinate | - |
| update | spectral_constrained | update | None | None | coordinate | spectral_norm |