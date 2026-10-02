# Axes Registry

Generated: 2026-10-02T07:45:32.450590
Total: 57 axes

| Structural Axis | Name | Axis Kind | Available | Prior | Override Scope | Topology Params |
|-----------------|------|-----------|-----------|-------|----------------|-----------------|
| substrate | analog | substrate | always | None | coordinate | - |
| substrate | complex | substrate | always | None | coordinate | - |
| substrate | digital | substrate | always | None | coordinate | - |
| substrate | memristive | substrate | always | None | coordinate | - |
| substrate | neuromorphic | substrate | always | None | coordinate | - |
| substrate | optical | substrate | always | None | coordinate | - |
| substrate | quantum | substrate | always | None | coordinate | - |
| substrate | sparse | substrate | always | None | coordinate | - |
| substrate | ternary | substrate | always | None | coordinate | - |
| geometry | attention | geometry | always | None | coordinate | input_dim, output_dim, num_heads |
| geometry | causal_transformer | geometry | always | None | coordinate | input_dim, output_dim, hidden_dim, num_heads, seq_len |
| geometry | conv | geometry | always | None | coordinate | input_dim, output_dim, conv_channels, kernel_size |
| geometry | feedforward | geometry | always | None | coordinate | input_dim, output_dim, hidden_dim, num_layers |
| geometry | graph | geometry | always | None | coordinate | input_dim, output_dim, hidden_dim |
| geometry | nca | geometry | always | None | coordinate | input_dim, output_dim, grid_hw |
| geometry | ntm | geometry | always | None | coordinate | input_dim, output_dim, mem_slots, mem_width |
| geometry | recurrent | geometry | always | None | coordinate | input_dim, output_dim, hidden_dim, num_layers |
| geometry | spatial_lattice | geometry | always | None | coordinate | input_dim, output_dim, lattice_dims |
| geometry | tile | geometry | always | None | coordinate | input_dim, output_dim, neurons_per_tile, tiles_per_layer |
| geometry | tile_mesh | geometry | always | None | coordinate | input_dim, output_dim, neurons_per_tile, tiles_per_layer |
| dynamics | diffusion | dynamics | always | None | coordinate | max_steps |
| dynamics | energy_minimization | dynamics | always | None | coordinate | max_steps, convergence_threshold |
| dynamics | error_predictive_coding | dynamics | always | None | coordinate | max_steps, convergence_threshold |
| dynamics | instantaneous | dynamics | always | None | coordinate | - |
| dynamics | lazy | dynamics | always | None | coordinate | - |
| dynamics | pc_alm | dynamics | always | None | coordinate | max_steps |
| dynamics | predictive_settling | dynamics | always | None | coordinate | max_steps, convergence_threshold |
| dynamics | spike_integration | dynamics | always | None | coordinate | max_steps |
| plasticity | conflict_adaptive | plasticity | always | None | coordinate | trace_decay, conflict_threshold |
| plasticity | fast_weights | plasticity | always | None | coordinate | fast_weight_dim |
| plasticity | null | plasticity | always | None | coordinate | - |
| plasticity | routing | plasticity | always | None | coordinate | gate_dim |
| plasticity | rule_state | plasticity | always | None | coordinate | num_operators |
| plasticity | substrate_coupled | plasticity | always | None | coordinate | - |
| plasticity | temporal_psi | plasticity | always | None | coordinate | trace_decay |
| credit | gradient | credit | always | None | coordinate | - |
| credit | homeostatic | credit | always | None | coordinate | - |
| credit | local_contrastive | credit | always | None | coordinate | ema_beta, contrast_threshold, contrast_objective |
| credit | local_goodness | credit | always | None | coordinate | - |
| credit | pc_alm | credit | always | None | coordinate | - |
| credit | pepita | credit | always | None | coordinate | feedback_scale |
| credit | random_projections | credit | always | None | coordinate | feedback_scale |
| credit | target_inversion | credit | always | None | coordinate | - |
| credit | temporal_trace | credit | always | None | coordinate | a_plus, a_minus, tau_pre, tau_post |
| credit | thermodynamic_contrast | credit | always | None | coordinate | - |
| update | adam | update | always | None | coordinate | beta2, eps |
| update | elastic_consolidation | update | always | None | coordinate | ewc_lambda, fisher_damping |
| update | euclidean | update | always | None | coordinate | - |
| update | lion | update | always | None | coordinate | beta2, eps |
| update | local_adam | update | always | None | coordinate | beta2, eps |
| update | mean_norm | update | always | None | coordinate | - |
| update | muon | update | always | None | coordinate | ortho_steps, momentum |
| update | natural_gradient | update | always | None | coordinate | fisher_damping |
| update | ortho_adam | update | always | None | coordinate | beta2, eps, ortho_lr |
| update | riemannian_orthogonal | update | always | None | coordinate | ortho_steps |
| update | role_split | update | always | None | coordinate | - |
| update | spectral_constrained | update | always | None | coordinate | spectral_norm |