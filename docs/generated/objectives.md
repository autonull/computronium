# Objectives Registry

Generated: 2026-10-08T18:43:30.291034
Total: 48 objectives

| Name | Direction | Weight | Normalizer | Axis Tag | Metric |
|------|-----------|--------|------------|----------|--------|
| augmented_lagrangian | minimize | 1.0 | minmax | stability | augmented_lagrangian |
| bleu_score | maximize | 1.0 | minmax | task | unmeasured |
| bp_deficit | minimize | 1.0 | minmax | ruler | unmeasured |
| coherence_time | maximize | 1.0 | minmax | substrate | coherence_time_us |
| consolidation_cost | minimize | 1.0 | log | plasticity | consolidation_cost |
| contraction_rate | maximize | 1.0 | minmax | stability | contraction_rate |
| convergence_steps | minimize | 1.0 | minmax | task | unmeasured |
| credit_efficiency | maximize | 1.0 | minmax | composite | unmeasured |
| drift_max_singular_value | minimize | 1.0 | minmax | stability | drift_max_singular_value |
| drift_spectral_radius | minimize | 1.0 | minmax | stability | drift_spectral_radius |
| energy_efficiency | maximize | 1.0 | minmax | cost | energy_efficiency |
| energy_per_mac | minimize | 1.0 | log | cost | energy_per_mac |
| energy_per_step | minimize | 1.0 | log | cost | energy_per_step |
| f1_score | maximize | 1.0 | minmax | task | unmeasured |
| flops | minimize | 1.0 | log | cost | flops |
| free_energy | minimize | 1.0 | minmax | stability | hopfield_energy |
| gate_fidelity | maximize | 1.0 | minmax | substrate | gate_fidelity |
| generalization_gap | minimize | 1.0 | minmax | task | unmeasured |
| hopfield_energy | minimize | 1.0 | minmax | stability | hopfield_energy |
| instantaneous_proxy_energy | minimize | 1.0 | minmax | stability | instantaneous_proxy_energy |
| ir_drop_variance | minimize | 1.0 | minmax | substrate | ir_drop_variance |
| latency_ms | minimize | 1.0 | minmax | cost | latency_ms |
| lyapunov_exponent | minimize | 1.0 | minmax | stability | lyapunov_exponent |
| macs_per_step | minimize | 1.0 | log | cost | macs_per_step |
| max_singular_value | minimize | 1.0 | minmax | stability | max_singular_value |
| memory_usage | minimize | 1.0 | minmax | cost | memory_usage |
| nonnormality | minimize | 1.0 | minmax | stability | nonnormality |
| param_count | minimize | 1.0 | log | cost | param_count |
| pc_free_energy | minimize | 1.0 | minmax | stability | pc_free_energy |
| perplexity | minimize | 1.0 | log | task | unmeasured |
| phase_noise | minimize | 1.0 | minmax | substrate | phase_noise |
| psi_capacity | maximize | 1.0 | minmax | plasticity | psi_capacity |
| rewrite_rate | maximize | 1.0 | minmax | plasticity | rewrite_rate |
| ruler_energy_ratio | minimize | 1.0 | log | ruler | unmeasured |
| ruler_param_ratio | minimize | 1.0 | log | ruler | unmeasured |
| ruler_walltime_ratio | minimize | 1.0 | log | ruler | unmeasured |
| settle_steps | minimize | 1.0 | minmax | stability | settle_steps |
| spectral_radius | minimize | 1.0 | minmax | stability | spectral_radius |
| spike_proxy_energy | minimize | 1.0 | minmax | stability | spike_proxy_energy |
| spike_rate | minimize | 1.0 | minmax | substrate | spike_rate |
| stability_margin | maximize | 1.0 | minmax | stability | stability_margin |
| stability_plasticity_ratio | minimize | 1.0 | log | composite | unmeasured |
| test_accuracy | maximize | 1.0 | minmax | task | unmeasured |
| test_loss | minimize | 1.0 | minmax | task | unmeasured |
| training_time | minimize | 1.0 | minmax | cost | unmeasured |
| validation_accuracy | maximize | 1.0 | minmax | task | val_acc |
| validation_loss | minimize | 1.0 | minmax | task | val_loss |
| walltime_total | minimize | 1.0 | minmax | cost | walltime_s |