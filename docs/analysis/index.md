# Analysis Recipes

Advanced analysis techniques for computronium experiments.

## Overview

This directory contains recipes for common analysis workflows:

- [Pareto Analysis](pareto.md) - Multi-objective optimization
- [Ablation Studies](ablation.md) - Component contribution analysis
- [Stability-Plasticity](stability_plasticity.md) - Dynamical systems analysis
- [Scaling Laws](scaling_laws.md) - Power law fitting
- [Statistical Comparison](statistical_comparison.md) - Rigorous comparison

## Quick Reference

| Analysis | Command | Use Case |
|----------|---------|----------|
| Pareto 2D | `comp pareto -x A -y B` | Trade-off visualization |
| Pareto 3D | `comp pareto -x A -y B -z C` | Three-way trade-offs |
| Bootstrap CI | `comp stats --bootstrap 1000` | Uncertainty quantification |
| Effect Size | `comp stats --effect-size` | Practical significance |
| Diff | `comp diff --run-id A --run-id B` | Pairwise comparison |
| ANOVA | `comp stats --test anova` | Multi-group comparison |
| Tukey HSD | `comp stats --test tukey` | Post-hoc pairwise |
| Correlation | `comp stats --correlation` | Metric relationships |

## Common Workflows

### 1. Algorithm Selection

```bash
# Run comparison
uv run comp campaign --model sgd,fa,eqprop,backprop --task digits --store compare.db

# Pareto: accuracy vs speed
uv run comp pareto --store compare.db -x walltime_total -y validation_accuracy

# Statistical significance
uv run comp stats --store compare.db --test anova --group-by model --metric validation_accuracy

# Effect sizes
uv run comp stats --store compare.db --effect-size --group-by model --metric validation_accuracy
```

### 2. Substrate Efficiency

```bash
# Run substrate comparison
uv run comp campaign --model eqprop --task digits \
  --sweep 'substrate=digital,memristive,photonic' --store substrate.db

# Energy-accuracy Pareto
uv run comp pareto --store substrate.db -x energy_per_step -y validation_accuracy

# Cost breakdown
uv run comp stats --store substrate.db --metrics energy_per_step,energy_per_mac,latency_ms
```

### 3. Stability Analysis

```bash
# Run stability sweep
uv run comp campaign --model eqprop --task digits \
  --sweep 'beta=0.1,0.5,1.0,2.0' --store stability.db

# Stability metrics
uv run comp stats --store stability.db \
  --metrics spectral_radius,lyapunov_exponent,stability_margin,settle_steps

# Accuracy-stability trade-off
uv run comp pareto --store stability.db -x spectral_radius -y validation_accuracy
```

### 4. Ablation Study

```bash
# Run ablation (remove components)
uv run comp campaign --model eqprop --task digits \
  --sweep 'use_feedback=True,False' \
  --sweep 'use_homeostatic=True,False' \
  --store ablation.db

# Compare contributions
uv run comp diff --store ablation.db --group-by use_feedback --metric validation_accuracy
```

## Python API for Custom Analysis

```python
"""Custom analysis using computronium's Python API."""
import sqlite3
import pandas as pd
import numpy as np
from scipy import stats

# Load results
conn = sqlite3.connect("results.db")
df = pd.read_sql("SELECT * FROM probe_results", conn)

# Custom Pareto frontier
from scipy.spatial import ConvexHull

def pareto_frontier(df, x_col, y_col, maximize_y=True):
    """Compute Pareto frontier."""
    points = df[[x_col, y_col]].dropna().values
    if maximize_y:
        points[:, 1] = -points[:, 1]  # Flip for maximization
    hull = ConvexHull(points)
    pareto_idx = hull.vertices
    return df.iloc[pareto_idx]

# Bootstrap confidence intervals
def bootstrap_ci(data, n_bootstrap=1000, ci=0.95):
    """Compute bootstrap CI."""
    boot_means = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=len(data), replace=True)
        boot_means.append(sample.mean())
    alpha = (1 - ci) / 2
    return np.percentile(boot_means, [alpha*100, (1-alpha)*100])

# Effect size (Cohen's d)
def cohens_d(group1, group2):
    """Compute Cohen's d."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    return (np.mean(group1) - np.mean(group2)) / pooled_std

# Example usage
pareto_df = pareto_frontier(df, 'walltime_total', 'validation_accuracy')
print("Pareto optimal configurations:")
print(pareto_df[['model', 'substrate', 'walltime_total', 'validation_accuracy']])

# Bootstrap CI for best model
best = df[df['model'] == 'backprop']['validation_accuracy']
ci = bootstrap_ci(best)
print(f"Backprop accuracy 95% CI: {ci}")

# Effect size: digital vs memristive
digital = df[df['substrate'] == 'digital']['validation_accuracy']
memristive = df[df['substrate'] == 'memristive']['validation_accuracy']
d = cohens_d(digital, memristive)
print(f"Cohen's d (digital vs memristive): {d:.2f}")
```

## Visualization Recipes

### Convergence Curves

```bash
# Plot training curves for all runs
uv run comp report --store results.db --output curves.html --plot-type convergence
```

### Pareto Frontier

```bash
# Interactive Pareto plot
uv run comp pareto --store results.db -x walltime_total -y validation_accuracy \
  --plot pareto.html --interactive
```

### Stability Landscape

```bash
# 3D stability landscape
uv run comp pareto --store results.db \
  -x spectral_radius -y lyapunov_exponent -z validation_accuracy \
  --plot stability_landscape.html --interactive
```

### Ablation Waterfall

```bash
# Waterfall chart for ablation
uv run comp stats --store ablation.db \
  --waterfall --metric validation_accuracy \
  --group-by use_feedback,use_homeostatic \
  --output ablation_waterfall.png
```

## Export for Publications

```bash
# Export publication-ready figures
uv run comp report --store results.db \
  --format latex \
  --output paper_figures/ \
  --figures pareto,convergence,stability,ablation

# Export data tables
uv run comp export --store results.db --format csv --output paper_data/
```

## Next Steps

- [Pareto Analysis](pareto.md) - Advanced Pareto techniques
- [Ablation Studies](ablation.md) - Component contribution
- [Stability-Plasticity](stability_plasticity.md) - Dynamical analysis
- [Experiments](../experiments/index.md) - Running experiments