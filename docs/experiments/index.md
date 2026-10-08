# Experiment Tutorials

End-to-end tutorials for running experiments with computronium.

## Tutorials

- [Quickstart](quickstart.md) - Run your first experiment in 5 minutes
- [Training a Custom Model](custom_model.md) - Define and train a new primitive
- [Running a Hyperparameter Sweep](hyperparameter_sweep.md) - Campaign automation
- [Analyzing Results](analyzing_results.md) - Statistics, Pareto, diff, export
- [Reproducibility](reproducibility.md) - Docker export, bitwise verification
- [Distributed Experiments](distributed.md) - Multi-GPU, multi-node training

## Quick Reference

| Task | Command |
|------|---------|
| Quick verify | `comp run quick-verify` |
| Single run | `comp run <model> --task <task>` |
| Campaign | `comp campaign --model <model> --sweep ...` |
| Stats | `comp stats --store <db>` |
| Pareto | `comp pareto --store <db>` |
| Diff | `comp diff --store <db> --run-id A --run-id B` |
| Report | `comp report --store <db>` |
| Export | `comp export --store <db> --run-id <id>` |
| Reproduce | `comp repro --store <db> --run-id <id> --docker` |

## Common Workflows

### Quick Exploration
```bash
# Test a new algorithm on digits
uv run comp run backprop --task digits --epochs 10 --store exp.db
uv run comp stats --store exp.db
```

### Systematic Comparison
```bash
# Compare all algorithms on digits
uv run comp campaign \
  --model sgd,fa,hebbian,ff,tp,pc,eqprop \
  --task digits \
  --epochs 20 \
  --seeds 42,123,456 \
  --store comparison.db
uv run comp pareto --store comparison.db --x walltime_total --y validation_accuracy
```

### Stability Analysis
```bash
# Run with stability metrics
uv run comp run eqprop --task digits --epochs 30 --store stability.db
uv run comp stats --store stability.db --metrics spectral_radius,lyapunov_exponent,settle_steps
```