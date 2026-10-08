# Quickstart: Running Your First Experiment

This guide walks you through running a complete experiment with computronium, from installation to analysis.

## Prerequisites

- Python 3.14+
- `uv` package manager
- CUDA-enabled GPU (optional, CPU fallback available)

```bash
# Install computronium
git clone https://github.com/your-org/computronium
cd computronium
uv sync --dev --all-extras
```

## 1. Run a Quick Verification

```bash
# Run quick verification (digits task, backprop, 1 epoch)
uv run comp run quick-verify --device cpu --seed 42 --iterations 1

# Expected output: probe result with accuracy, walltime, and stability metrics
```

## 2. Run a Full Training Experiment

```bash
# Train SGD on MNIST digits for 10 epochs
uv run comp run sgd --device cpu --seed 42 --iterations 10 --store results.db

# With GPU (if available)
uv run comp run sgd --device cuda --seed 42 --iterations 10 --store results.db
```

## 3. Run Multiple Configurations (Campaign)

```bash
# Run a campaign sweeping learning rate and hidden dim
uv run comp campaign \
  --model sgd \
  --task digits \
  --sweep 'learning_rate=0.001,0.01,0.1' \
  --sweep 'hidden_dim=32,64,128' \
  --seeds 42,123,456 \
  --epochs 5 \
  --store campaign.db
```

## 4. Analyze Results

```bash
# Basic statistics
uv run comp stats --store results.db --format table

# Pareto frontier (accuracy vs walltime)
uv run comp pareto --store results.db --x walltime_total --y validation_accuracy

# Compare two runs
uv run comp diff --store results.db --run-id RUN_ID_1 --run-id RUN_ID_2

# Export for reproducibility
uv run comp export --store results.db --run-id RUN_ID --format json --output ./repro
```

## 5. View Generated Reports

```bash
# Generate HTML report
uv run comp report --store results.db --output report.html

# Open in browser
open report.html
```

## 6. Reproduce a Run (Docker)

```bash
# Export Docker environment
uv run comp export --store results.db --run-id RUN_ID --format docker --output ./docker_repro

# Build and run (requires Docker)
cd docker_repro
docker build -t comp-repro .
docker run --rm comp-repro
```

## Next Steps

- [Benchmark Suites](../benchmarks/index.md) - Run standardized benchmark suites
- [Analysis Recipes](../analysis/index.md) - Pareto, ablation, stability-plasticity analysis
- [GPU Optimization](../gpu_guide/index.md) - Mixed precision, multi-GPU, memory optimization
- [CLI Reference](../cli_reference.md) - Complete command reference