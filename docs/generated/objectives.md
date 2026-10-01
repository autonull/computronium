# Objectives Registry

Generated: 2026-09-30T22:15:53.370767
Total: 36 objectives

| Name | Direction | Weight | Normalizer | Axis Tag |
|------|-----------|--------|------------|----------|
| bleu_score | maximize | 1.0 | minmax | task |
| bp_deficit | minimize | 1.0 | minmax | ruler |
| coherence_time | maximize | 1.0 | minmax | substrate |
| consolidation_cost | minimize | 1.0 | log | plasticity |
| convergence_steps | minimize | 1.0 | minmax | task |
| credit_efficiency | maximize | 1.0 | minmax | composite |
| energy_efficiency | maximize | 1.0 | minmax | cost |
| energy_per_step | minimize | 1.0 | log | cost |
| f1_score | maximize | 1.0 | minmax | task |
| flops | minimize | 1.0 | log | cost |
| free_energy | minimize | 1.0 | minmax | stability |
| gate_fidelity | maximize | 1.0 | minmax | substrate |
| generalization_gap | minimize | 1.0 | minmax | task |
| ir_drop_variance | minimize | 1.0 | minmax | substrate |
| latency_ms | minimize | 1.0 | minmax | cost |
| lyapunov_exponent | minimize | 1.0 | minmax | stability |
| max_singular_value | minimize | 1.0 | minmax | stability |
| memory_usage | minimize | 1.0 | minmax | cost |
| param_count | minimize | 1.0 | log | cost |
| perplexity | minimize | 1.0 | log | task |
| phase_noise | minimize | 1.0 | minmax | substrate |
| psi_capacity | maximize | 1.0 | minmax | plasticity |
| rewrite_rate | maximize | 1.0 | minmax | plasticity |
| ruler_energy_ratio | minimize | 1.0 | log | ruler |
| ruler_param_ratio | minimize | 1.0 | log | ruler |
| ruler_walltime_ratio | minimize | 1.0 | log | ruler |
| settle_steps | minimize | 1.0 | minmax | stability |
| spectral_radius | minimize | 1.0 | minmax | stability |
| spike_rate | minimize | 1.0 | minmax | substrate |
| stability_plasticity_ratio | minimize | 1.0 | log | composite |
| test_accuracy | maximize | 1.0 | minmax | task |
| test_loss | minimize | 1.0 | minmax | task |
| training_time | minimize | 1.0 | minmax | cost |
| validation_accuracy | maximize | 1.0 | minmax | task |
| validation_loss | minimize | 1.0 | minmax | task |
| walltime_total | minimize | 1.0 | minmax | cost |