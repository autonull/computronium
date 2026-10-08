# Analyzing Results

Comprehensive guide to analyzing experiment results with computronium's analysis tools.

## Overview

After running experiments, use these commands to analyze results:

| Command | Purpose |
|---------|---------|
| `comp stats` | Summary statistics, bootstrap CI, effect sizes |
| `comp pareto` | Multi-objective Pareto frontiers |
| `comp diff` | Compare two runs/configurations |
| `comp report` | Generate HTML/PDF reports |
| `comp export` | Export for reproducibility |

## Basic Statistics

```bash
# Summary table (default)
uv run comp stats --store results.db

# Specific metrics
uv run comp stats --store results.db \
  --metrics validation_accuracy,walltime_total,spectral_radius,lyapunov_exponent

# All metrics
uv run comp stats --store results.db --all-metrics

# JSON output for scripting
uv run comp stats --store results.db --format json > stats.json

# CSV for spreadsheet
uv run comp stats --store results.db --format csv > stats.csv
```

## Bootstrap Confidence Intervals

```bash
# 95% CI with 1000 bootstrap samples
uv run comp stats --store results.db \
  --bootstrap 1000 \
  --ci 0.95 \
  --metrics validation_accuracy,walltime_total

# Custom CI level
uv run comp stats --store results.db --bootstrap 5000 --ci 0.99
```

Output:
```
Metric              Mean     Std      CI95_Low  CI95_High
validation_accuracy 0.923    0.012    0.901     0.945
walltime_total     145.2    12.3     124.1     168.7
```

## Effect Sizes

```bash
# Cohen's d between two configurations
uv run comp stats --store results.db \
  --effect-size \
  --group-by substrate \
  --metric validation_accuracy

# Cliff's delta (non-parametric)
uv run comp stats --store results.db \
  --effect-size cliff \
  --group-by model \
  --metric validation_accuracy
```

Output:
```
Comparison              Cohen's d   Interpretation
digital vs memristive   0.82        Large
digital vs photonic     0.45        Medium
digital vs quantum      1.20        Very Large
```

## Pareto Frontier Analysis

### 2D Pareto (Standard)

```bash
# Accuracy vs walltime
uv run comp pareto \
  --store results.db \
  --x walltime_total \
  --y validation_accuracy \
  --format table

# Save Pareto points
uv run comp pareto \
  --store results.db \
  --x walltime_total \
  --y validation_accuracy \
  --format json > pareto.json
```

### 3D Pareto (Three Objectives)

```bash
# Accuracy, walltime, stability
uv run comp pareto \
  --store results.db \
  --x walltime_total \
  --y validation_accuracy \
  --z spectral_radius \
  --format json
```

### Visualize Pareto

```bash
# Generate Pareto plot (requires matplotlib)
uv run comp pareto \
  --store results.db \
  --x walltime_total \
  --y validation_accuracy \
  --plot pareto.png

# Interactive HTML plot
uv run comp pareto \
  --store results.db \
  --x walltime_total \
  --y validation_accuracy \
  --plot pareto.html --interactive
```

## Diff Analysis

### Compare Two Runs

```bash
# Full diff
uv run comp diff \
  --store results.db \
  --run-id RUN_ID_A \
  --run-id RUN_ID_B

# Diff specific metrics
uv run comp diff \
  --store results.db \
  --run-id RUN_ID_A \
  --run-id RUN_ID_B \
  --metrics validation_accuracy,walltime_total,spectral_radius
```

Output:
```
Metric              Run A    Run B    Diff     %Change   Significance
validation_accuracy 0.923    0.945    +0.022   +2.4%     p=0.03 *
walltime_total     145.2    120.1    -25.1    -17.3%    p=0.01 *
spectral_radius    0.98     0.85     -0.13    -13.3%    p=0.05 *
```

### Compare Groups

```bash
# Compare all digital vs all memristive runs
uv run comp diff \
  --store results.db \
  --group-by substrate \
  --group-values digital,memristic \
  --metric validation_accuracy
```

## Statistical Significance Testing

```bash
# t-test between groups
uv run comp stats --store results.db \
  --test ttest \
  --group-by model \
  --metric validation_accuracy

# Mann-Whitney U test (non-parametric)
uv run comp stats --store results.db \
  --test mannwhitney \
  --group-by model \
  --metric validation_accuracy

# ANOVA across multiple groups
uv run comp stats --store results.db \
  --test anova \
  --group-by model \
  --metric validation_accuracy

# Post-hoc pairwise (Tukey HSD)
uv run comp stats --store results.db \
  --test tukey \
  --group-by model \
  --metric validation_accuracy
```

## Report Generation

```bash
# HTML report
uv run comp report --store results.db --output report.html

# PDF report (requires pandoc)
uv run comp report --store results.db --output report.pdf

# Custom template
uv run comp report --store results.db --output report.html --template custom.j2
```

Report includes:
- Experiment metadata (config, seeds, hardware)
- Summary statistics table
- Pareto frontier plots
- Convergence curves
- Stability analysis
- Bootstrap confidence intervals
- Effect size comparisons

## Export for Further Analysis

```bash
# Export all runs as JSON
uv run comp export --store results.db --format json --output ./export

# Export specific run
uv run comp export --store results.db --run-id RUN_ID --format json --output ./run_export

# Export as CSV for pandas/R
uv run comp export --store results.db --format csv --output results.csv

# Export for reproducibility (Docker)
uv run comp export --store results.db --run-id RUN_ID --format docker --output ./docker
```

## Working with Exported Data

### Python/Pandas

```python
import pandas as pd

# Load exported CSV
df = pd.read_csv("results.csv")

# Filter by model
backprop_runs = df[df['model'] == 'backprop']

# Group by substrate
substrate_stats = df.groupby('substrate')['validation_accuracy'].agg(['mean', 'std'])

# Pareto frontier computation
from scipy.spatial import ConvexHull
# ... custom analysis
```

### R

```r
library(tidyverse)

results <- read_csv("results.csv")

# Summary by model
results %>%
  group_by(model) %>%
  summarise(
    mean_acc = mean(validation_accuracy),
    sd_acc = sd(validation_accuracy),
    mean_time = mean(walltime_total)
  )

# Pareto frontier
library(rPref)
pareto <- results %>% psel(low(walltime_total) * high(validation_accuracy))
```

## Common Analysis Workflows

### Workflow 1: Model Selection

```bash
# 1. Run model comparison
uv run comp campaign --model sgd,fa,eqprop,backprop --task digits --store compare.db

# 2. Get Pareto frontier
uv run comp pareto --store compare.db -x walltime_total -y validation_accuracy

# 3. Statistical test
uv run comp stats --store compare.db --test anova --group-by model --metric validation_accuracy

# 4. Effect sizes
uv run comp stats --store compare.db --effect-size --group-by model --metric validation_accuracy

# 5. Generate report
uv run comp report --store compare.db --output model_selection.html
```

### Workflow 2: Stability-Plasticity Trade-off

```bash
# 1. Run stability-focused sweep
uv run comp campaign --model eqprop --task digits \
  --sweep 'beta=0.1,0.5,1.0,2.0' \
  --store stability.db

# 2. Analyze stability metrics
uv run comp stats --store stability.db \
  --metrics spectral_radius,lyapunov_exponent,settle_steps,stability_margin

# 3. Pareto: accuracy vs stability
uv run comp pareto --store stability.db \
  -x spectral_radius -y validation_accuracy

# 4. Correlation analysis
uv run comp stats --store stability.db \
  --correlation spectral_radius,validation_accuracy
```

### Workflow 3: Substrate Efficiency

```bash
# 1. Run substrate comparison
uv run comp campaign --model eqprop --task digits \
  --sweep 'substrate=digital,memristive,photonic' \
  --store substrate.db

# 2. Energy efficiency analysis
uv run comp stats --store substrate.db \
  --metrics energy_per_step,energy_per_mac,validation_accuracy

# 3. Pareto: accuracy vs energy
uv run comp pareto --store substrate.db \
  -x energy_per_step -y validation_accuracy

# 4. Report
uv run comp report --store substrate.db --output substrate_efficiency.html
```

## Next Steps

- [Pareto Analysis](../analysis/pareto.md) - Advanced Pareto techniques
- [Ablation Studies](../analysis/ablation.md) - Component contribution
- [Stability-Plasticity Analysis](../analysis/stability_plasticity.md) - Dynamical analysis
- [Reproducibility](reproducibility.md) - Docker export and verification