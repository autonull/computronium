# Objectives Registry

Generated: 2026-10-02T11:30:28.628907
Total: 36 objectives

| Name | Direction | Weight | Normalizer | Axis Tag | Metric |
|------|-----------|--------|------------|----------|--------|
| bleu_score | maximize | 1.0 | minmax | task | unmeasured |
| bp_deficit | minimize | 1.0 | minmax | ruler | unmeasured |
| coherence_time | maximize | 1.0 | minmax | substrate | unmeasured |
| consolidation_cost | minimize | 1.0 | log | plasticity | unmeasured |
| convergence_steps | minimize | 1.0 | minmax | task | unmeasured |
| credit_efficiency | maximize | 1.0 | minmax | composite | unmeasured |
| energy_efficiency | maximize | 1.0 | minmax | cost | unmeasured |
| energy_per_step | minimize | 1.0 | log | cost | unmeasured |
| f1_score | maximize | 1.0 | minmax | task | unmeasured |
| flops | minimize | 1.0 | log | cost | unmeasured |
| free_energy | minimize | 1.0 | minmax | stability | unmeasured |
| gate_fidelity | maximize | 1.0 | minmax | substrate | unmeasured |
| generalization_gap | minimize | 1.0 | minmax | task | unmeasured |
| ir_drop_variance | minimize | 1.0 | minmax | substrate | unmeasured |
| latency_ms | minimize | 1.0 | minmax | cost | unmeasured |
| lyapunov_exponent | minimize | 1.0 | minmax | stability | unmeasured |
| max_singular_value | minimize | 1.0 | minmax | stability | unmeasured |
| memory_usage | minimize | 1.0 | minmax | cost | unmeasured |
| param_count | minimize | 1.0 | log | cost | param_count |
| perplexity | minimize | 1.0 | log | task | unmeasured |
| phase_noise | minimize | 1.0 | minmax | substrate | unmeasured |
| psi_capacity | maximize | 1.0 | minmax | plasticity | unmeasured |
| rewrite_rate | maximize | 1.0 | minmax | plasticity | unmeasured |
| ruler_energy_ratio | minimize | 1.0 | log | ruler | unmeasured |
| ruler_param_ratio | minimize | 1.0 | log | ruler | unmeasured |
| ruler_walltime_ratio | minimize | 1.0 | log | ruler | unmeasured |
| settle_steps | minimize | 1.0 | minmax | stability | unmeasured |
| spectral_radius | minimize | 1.0 | minmax | stability | unmeasured |
| spike_rate | minimize | 1.0 | minmax | substrate | unmeasured |
| stability_plasticity_ratio | minimize | 1.0 | log | composite | unmeasured |
| test_accuracy | maximize | 1.0 | minmax | task | unmeasured |
| test_loss | minimize | 1.0 | minmax | task | unmeasured |
| training_time | minimize | 1.0 | minmax | cost | unmeasured |
| validation_accuracy | maximize | 1.0 | minmax | task | val_acc |
| validation_loss | minimize | 1.0 | minmax | task | val_loss |
| walltime_total | minimize | 1.0 | minmax | cost | walltime_s |