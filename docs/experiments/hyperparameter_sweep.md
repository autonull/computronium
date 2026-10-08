# Running Hyperparameter Sweeps

Learn how to run systematic hyperparameter sweeps using computronium's campaign automation.

## Basic Sweep

```bash
# Sweep a single parameter
uv run comp campaign \
  --model backprop \
  --task digits \
  --sweep 'learning_rate=0.001,0.01,0.1' \
  --epochs 20 \
  --seeds 42,123,456 \
  --store sweep_lr.db
```

## Multi-Parameter Sweep

```bash
# Sweep multiple parameters (cartesian product)
uv run comp campaign \
  --model backprop \
  --task digits \
  --sweep 'learning_rate=0.001,0.01,0.1' \
  --sweep 'hidden_dim=64,128,256' \
  --sweep 'num_layers=2,3,4' \
  --epochs 20 \
  --seeds 42 \
  --store sweep_multi.db
```

## Model Comparison Sweep

```bash
# Compare multiple algorithms
uv run comp campaign \
  --model sgd,fa,hebbian,ff,tp,pc,eqprop,backprop \
  --task digits \
  --sweep 'learning_rate=0.01' \
  --epochs 30 \
  --seeds 42,123,456 \
  --store model_comparison.db
```

## Substrate Comparison Sweep

```bash
# Compare substrates for the same algorithm
uv run comp campaign \
  --model eqprop \
  --task digits \
  --sweep 'substrate=digital,memristive,photonic,quantum' \
  --epochs 20 \
  --seeds 42,123 \
  --store substrate_comparison.db
```

## Advanced: Using RunSpec Builder

For complex sweeps, use the Python API:

```python
"""Advanced sweep with custom RunSpec."""
from computronium.experiment.schema.builder import RunSpecBuilder
from computronium.experiment.schema.run_spec import RunSpec

# Build custom RunSpec
spec = (
    RunSpecBuilder()
    .model("eqprop")
    .task("digits")
    .objectives("validation_accuracy", "walltime_total", "spectral_radius")
    .axis("substrate", ["digital", "memristive", "photonic"])
    .axis("learning_rate", [0.001, 0.01, 0.1])
    .axis("beta", [0.1, 0.5, 1.0])
    .seeds([42, 123, 456])
    .epochs(30)
    .device("cuda")
    .build()
)

# Run via CLI
# comp run --spec sweep_spec.json --store advanced.db
```

## Running the Campaign

```bash
# Run with default settings (parallel workers = CPU count)
uv run comp campaign --spec sweep_spec.json --store results.db

# Control parallelism
uv run comp campaign --spec sweep_spec.json --store results.db --workers 4

# Resume interrupted campaign
uv run comp campaign --spec sweep_spec.json --store results.db --resume
```

## Monitoring Progress

```bash
# Watch live stats
uv run comp stats --store results.db --watch

# Check specific run status
uv run comp status --store results.db --run-id RUN_ID
```

## Analyzing Sweep Results

### Basic Statistics

```bash
# Summary table
uv run comp stats --store results.db --format table

# JSON for programmatic analysis
uv run comp stats --store results.db --format json > stats.json
```

### Pareto Frontier

```bash
# Accuracy vs walltime Pareto frontier
uv run comp pareto \
  --store results.db \
  --x walltime_total \
  --y validation_accuracy \
  --format table

# Multi-objective Pareto (3D)
uv run comp pareto \
  --store results.db \
  --x walltime_total \
  --y validation_accuracy \
  --z spectral_radius \
  --format json
```

### Diff Between Configurations

```bash
# Compare two specific runs
uv run comp diff \
  --store results.db \
  --run-id RUN_ID_A \
  --run-id RUN_ID_B

# Compare best vs worst
uv run comp diff \
  --store results.db \
  --run-id $(comp stats --store results.db --best validation_accuracy --format json | jq -r .run_id) \
  --run-id $(comp stats --store results.db --worst validation_accuracy --format json | jq -r .run_id)
```

### Bootstrap Confidence Intervals

```bash
# Bootstrap statistics with 95% CI
uv run comp stats \
  --store results.db \
  --bootstrap 1000 \
  --ci 0.95 \
  --metrics validation_accuracy,walltime_total,spectral_radius
```

## Expected Results

For the model comparison sweep on digits (10 epochs, 3 seeds):

| Model | Val Acc (mean±std) | Walltime (s) | Spectral Radius |
|-------|-------------------|--------------|-----------------|
| backprop | 0.95±0.01 | 120±10 | 0.98±0.02 |
| eqprop | 0.92±0.02 | 180±15 | 0.85±0.05 |
| fa | 0.88±0.03 | 150±12 | 0.95±0.03 |
| hebbian | 0.85±0.02 | 100±8 | 0.92±0.04 |
| ff | 0.82±0.03 | 110±9 | 0.88±0.06 |
| tp | 0.78±0.04 | 200±20 | 1.05±0.08 |
| pc | 0.80±0.03 | 250±25 | 0.90±0.07 |

*Note: Results vary by hardware and seed. Run your own sweeps for exact numbers.*

## Best Practices

1. **Start small**: Test with 1-2 seeds and few epochs first
2. **Use seeds**: Always run multiple seeds for statistical validity
3. **Log everything**: Store results in a database (`--store results.db`)
4. **Analyze incrementally**: Check stats after each batch of runs
5. **Export for reproducibility**: Use `comp export` to save exact configurations

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Campaign hangs | Check GPU memory, reduce batch size or workers |
| Out of memory | Use `--device cpu` or reduce `hidden_dim` |
| Slow sweeps | Use `--workers` to parallelize, run on GPU |
| Inconsistent results | Increase `--seeds`, check for non-determinism |

## Next Steps

- [Analyzing Results](analyzing_results.md) - Deep dive into analysis tools
- [Pareto Analysis](../analysis/pareto.md) - Multi-objective optimization
- [Ablation Studies](../analysis/ablation.md) - Component contribution analysis