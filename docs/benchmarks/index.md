# Benchmark Suites

Standardized benchmark suites for evaluating algorithms and substrates.

## Available Suites

| Suite | Description | Models | Tasks | Seeds | Runtime |
|-------|-------------|--------|-------|-------|---------|
| `quick` | Fast smoke test | 3 | 1 | 1 | ~30s |
| `standard` | Full algorithm comparison | 8 | 3 | 3 | ~15m |
| `substrate` | Substrate efficiency | 3 | 2 | 3 | ~20m |
| `stability` | Stability-plasticity | 4 | 1 | 5 | ~30m |
| `scaling` | Scaling laws | 2 | 2 | 3 | ~45m |
| `full` | Complete regression | 8 | 5 | 5 | ~2h |

## Running Benchmarks

```bash
# Quick smoke test
uv run comp benchmark --suite quick --store bench_quick.db

# Standard comparison
uv run comp benchmark --suite standard --store bench_standard.db

# Substrate efficiency
uv run comp benchmark --suite substrate --store bench_substrate.db

# Stability-plasticity trade-off
uv run comp benchmark --suite stability --store bench_stability.db

# Full regression (nightly)
uv run comp benchmark --suite full --store bench_full.db
```

## Suite Definitions

### Quick Suite (`quick`)

Fast validation that everything works.

```yaml
models: [backprop, eqprop, fa]
tasks: [digits]
seeds: [42]
epochs: 5
objectives: [validation_accuracy, walltime_total]
```

**Expected runtime**: ~30 seconds on CPU

**Pass criteria**: All models complete without error, accuracy > 0.5

### Standard Suite (`standard`)

Comprehensive algorithm comparison.

```yaml
models: [sgd, fa, hebbian, ff, tp, pc, eqprop, backprop]
tasks: [digits, fashion_mnist, cifar10]
seeds: [42, 123, 456]
epochs: 20
objectives: [validation_accuracy, walltime_total, spectral_radius, lyapunov_exponent, settle_steps, flops, memory_usage]
```

**Expected runtime**: ~15 minutes on GPU

**Expected Results** (digits, 20 epochs, 3 seeds):

| Model | Val Acc | Walltime (s) | Spectral Radius | Lyapunov Exp | Settle Steps |
|-------|---------|--------------|-----------------|--------------|--------------|
| backprop | 0.97±0.01 | 45±3 | 0.98±0.01 | -0.02±0.01 | 12±2 |
| eqprop | 0.94±0.02 | 120±10 | 0.85±0.03 | -0.15±0.02 | 25±3 |
| fa | 0.91±0.02 | 80±5 | 0.95±0.02 | -0.05±0.01 | 18±2 |
| hebbian | 0.88±0.02 | 60±4 | 0.92±0.02 | -0.08±0.01 | 15±2 |
| ff | 0.85±0.03 | 70±6 | 0.88±0.04 | -0.12±0.02 | 20±3 |
| tp | 0.82±0.03 | 150±15 | 1.05±0.05 | 0.02±0.03 | 35±5 |
| pc | 0.84±0.03 | 200±20 | 0.90±0.03 | -0.10±0.02 | 30±4 |
| sgd | 0.95±0.01 | 50±4 | 0.97±0.01 | -0.03±0.01 | 14±2 |

### Substrate Suite (`substrate`)

Substrate efficiency comparison.

```yaml
models: [eqprop, backprop, pc]
tasks: [digits, fashion_mnist]
seeds: [42, 123, 456]
epochs: 20
substrate: [digital, memristive, photonic]
objectives: [validation_accuracy, energy_per_step, energy_per_mac, latency_ms, spike_rate, ir_drop_variance, phase_noise, gate_fidelity, coherence_time]
```

**Expected Results** (eqprop, digits, 20 epochs):

| Substrate | Val Acc | Energy/Step (μJ) | Energy/MAC (pJ) | Latency (ms) |
|-----------|---------|------------------|-----------------|--------------|
| digital | 0.94±0.02 | 150±10 | 2.5±0.2 | 1.2±0.1 |
| memristive | 0.92±0.03 | 80±8 | 1.2±0.1 | 0.8±0.1 |
| photonic | 0.90±0.02 | 200±15 | 5.0±0.5 | 0.5±0.05 |

### Stability Suite (`stability`)

Stability-plasticity trade-off analysis.

```yaml
models: [eqprop, pc, diffusion, lazy]
tasks: [digits]
seeds: [42, 123, 456, 789, 999]
epochs: 30
sweep:
  beta: [0.1, 0.5, 1.0, 2.0]
objectives: [validation_accuracy, spectral_radius, lyapunov_exponent, stability_margin, psi_capacity, consolidation_cost, rewrite_rate]
```

**Expected Results**:

| Model | Beta | Val Acc | Spectral Radius | Lyapunov | Psi Capacity |
|-------|------|---------|-----------------|----------|--------------|
| eqprop | 0.1 | 0.88 | 0.75 | -0.28 | 0.65 |
| eqprop | 0.5 | 0.92 | 0.85 | -0.15 | 0.78 |
| eqprop | 1.0 | 0.94 | 0.90 | -0.10 | 0.82 |
| eqprop | 2.0 | 0.93 | 0.95 | -0.05 | 0.85 |

### Scaling Suite (`scaling`)

Scaling laws investigation.

```yaml
models: [backprop, eqprop]
tasks: [digits, fashion_mnist]
seeds: [42, 123, 456]
epochs: [10, 20, 30, 40, 50]
sweep:
  hidden_dim: [64, 128, 256, 512]
objectives: [validation_accuracy, walltime_total, flops, param_count, spectral_radius]
```

## Running Custom Benchmarks

```bash
# Define custom benchmark YAML
cat > my_benchmark.yaml << 'EOF'
suite: custom
models: [backprop, eqprop]
tasks: [digits]
seeds: [42, 123]
epochs: 30
objectives: [validation_accuracy, walltime_total, energy_per_step]
EOF

# Run custom benchmark
uv run comp benchmark --config my_benchmark.yaml --store custom.db
```

## Analyzing Benchmark Results

```bash
# Compare against expected results
uv run comp stats --store bench_standard.db --format table

# Pareto frontier
uv run comp pareto --store bench_standard.db -x walltime_total -y validation_accuracy

# Regression check (vs stored baselines)
uv run comp benchmark --suite standard --store bench_standard.db --check-regression
```

## Regression Testing

```bash
# Check for regressions against stored baselines
uv run comp benchmark --suite standard --store bench_standard.db --check-regression

# Update baselines (after verified improvements)
uv run comp benchmark --suite standard --store bench_standard.db --update-baselines
```

## CI Integration

```yaml
# .github/workflows/benchmarks.yml
name: Benchmarks
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  standard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --dev --all-extras
      - run: uv run comp benchmark --suite standard --store bench.db --check-regression
```

## Expected Baselines

Baselines are stored in `benchmarks/baselines/` and updated after verified improvements.

| Suite | Baseline File | Updated |
|-------|---------------|---------|
| quick | baselines/quick.json | Every PR |
| standard | baselines/standard.json | Weekly |
| substrate | baselines/substrate.json | Monthly |
| stability | baselines/stability.json | Monthly |
| scaling | baselines/scaling.json | Quarterly |
| full | baselines/full.json | Release |

## Contributing New Benchmarks

1. Add suite definition to `computronium/experiment/benchmarks/`
2. Add expected results to `benchmarks/baselines/`
3. Add CI test in `.github/workflows/`
4. Document in this file

## Next Steps

- [Quickstart](../experiments/quickstart.md) - Run your first benchmark
- [Analysis Recipes](../analysis/index.md) - Pareto, ablation, stability analysis
- [GPU Optimization](../gpu_guide/index.md) - Faster benchmark runs