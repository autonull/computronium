# Pareto Analysis

Multi-objective optimization and Pareto frontier analysis.

## Overview

Pareto analysis identifies configurations that are not dominated by any other configuration across multiple objectives.

## Basic Usage

```bash
# 2D Pareto frontier
uv run comp pareto --store results.db \
  --x walltime_total \
  --y validation_accuracy \
  --format table

# 3D Pareto frontier
uv run comp pareto --store results.db \
  --x walltime_total \
  --y validation_accuracy \
  --z spectral_radius \
  --format json
```

## Understanding Output

### Table Format

```
Run ID    Model      Substrate   Walltime    Val Acc    Spectral Rad   Pareto
abc123    backprop   digital     45.2        0.97       0.98           ✓
def456    eqprop     digital     120.1       0.94       0.85           ✓
ghi789    fa         digital     80.3        0.91       0.95           ✓
jkl012    tp         digital     150.5       0.82       1.05           ✗
```

- ✓ = Pareto optimal (not dominated)
- ✗ = Dominated (another config is better in all objectives)

### JSON Format

```json
{
  "pareto_points": [
    {"run_id": "abc123", "walltime_total": 45.2, "validation_accuracy": 0.97, "spectral_radius": 0.98},
    {"run_id": "def456", "walltime_total": 120.1, "validation_accuracy": 0.94, "spectral_radius": 0.85}
  ],
  "dominated_points": [...],
  "objectives": ["walltime_total", "validation_accuracy", "spectral_radius"],
  "dimensions": 3
}
```

## Advanced Options

### Minimize/Maximize Direction

```bash
# Explicit direction (auto-detected from objective registry)
uv run comp pareto \
  --store results.db \
  --x walltime_total --x-dir minimize \
  --y validation_accuracy --y-dir maximize \
  --z spectral_radius --z-dir minimize
```

### Filter Before Pareto

```bash
# Only consider digital substrate
uv run comp pareto \
  --store results.db \
  --filter 'substrate=digital' \
  --x walltime_total \
  --y validation_accuracy

# Only specific models
uv run comp pareto \
  --store results.db \
  --filter 'model=backprop,eqprop,fa' \
  --x walltime_total \
  --y validation_accuracy
```

### Custom Reference Point (Hypervolume)

```bash
# Compute hypervolume indicator
uv run comp pareto \
  --store results.db \
  --x walltime_total \
  --y validation_accuracy \
  --ref-point 300,0.5 \
  --hypervolume
```

Output:
```
Hypervolume: 0.0234 (reference: walltime=300, accuracy=0.5)
Pareto front covers 23.4% of objective space
```

## Visualization

### Static Plot

```bash
# Save as PNG
uv run comp pareto \
  --store results.db \
  -x walltime_total -y validation_accuracy \
  --plot pareto.png
```

### Interactive HTML

```bash
# Interactive Plotly plot
uv run comp pareto \
  --store results.db \
  -x walltime_total -y validation_accuracy \
  --plot pareto.html --interactive
```

Interactive features:
- Hover for run details
- Zoom/pan
- Select/deselect points
- Export as PNG/SVG

### 3D Interactive

```bash
# 3D interactive Pareto
uv run comp pareto \
  --store results.db \
  -x walltime_total -y validation_accuracy -z spectral_radius \
  --plot pareto_3d.html --interactive
```

## Multi-Objective Decision Making

### Knee Point Detection

```bash
# Find knee point (best trade-off)
uv run comp pareto \
  --store results.db \
  -x walltime_total -y validation_accuracy \
  --knee-point
```

Output:
```
Knee point: run_id=def456 (eqprop, digital)
  Walltime: 120.1s, Accuracy: 0.94
  Marginal rate: -0.0003 accuracy/sec
  Interpretation: Best accuracy per additional second
```

### Weighted Sum

```bash
# Scalarize with weights
uv run comp pareto \
  --store results.db \
  -x walltime_total -y validation_accuracy \
  --weights 0.6,0.4 \
  --scalarize
```

Output:
```
Weighted scores (walltime*0.6 + accuracy*0.4):
1. abc123 (backprop): 27.1 + 0.39 = 27.49
2. def456 (eqprop): 72.1 + 0.38 = 72.48
3. ghi789 (fa): 48.2 + 0.36 = 48.56
Best: backprop (lowest weighted score)
```

## Pareto Over Time

```bash
# Track Pareto frontier evolution across epochs
uv run comp pareto \
  --store results.db \
  -x walltime_total -y validation_accuracy \
  --by-epoch \
  --plot pareto_evolution.gif
```

## Export for Analysis

```bash
# Export Pareto points for custom analysis
uv run comp pareto \
  --store results.db \
  -x walltime_total -y validation_accuracy \
  --format json > pareto_points.json

# Export all points with Pareto rank
uv run comp pareto \
  --store results.db \
  -x walltime_total -y validation_accuracy \
  --format csv --include-dominated > all_points.csv
```

## Common Patterns

### Pattern 1: Accuracy vs Speed

```bash
uv run comp pareto \
  --store results.db \
  -x walltime_total -y validation_accuracy \
  --filter 'task=digits'
```

**Interpretation**: Points on the frontier offer best accuracy for given time budget.

### Pattern 2: Accuracy vs Stability

```bash
uv run comp pareto \
  --store results.db \
  -x spectral_radius -y validation_accuracy \
  --filter 'model=eqprop'
```

**Interpretation**: Trade-off between performance and dynamical stability.

### Pattern 3: Energy vs Accuracy (Substrate)

```bash
uv run comp pareto \
  --store results.db \
  -x energy_per_step -y validation_accuracy \
  --filter 'model=eqprop'
```

**Interpretation**: Substrate efficiency frontier.

### Pattern 4: Three-Way Trade-off

```bash
uv run comp pareto \
  --store results.db \
  -x walltime_total -y validation_accuracy -z spectral_radius \
  --filter 'task=digits'
```

**Interpretation**: Joint optimization of speed, accuracy, and stability.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No Pareto points | Check filter criteria, ensure data exists |
| All points dominated | Objectives may be correlated; try different pair |
| 3D plot not rendering | Use `--interactive` for Plotly, ensure browser supports WebGL |
| Hypervolume = 0 | Reference point dominates all points; use worse reference |

## Next Steps

- [Analysis Index](../analysis/index.md) - Other analysis recipes
- [Ablation Studies](ablation.md) - Component contribution
- [Experiments](../experiments/index.md) - Running experiments for Pareto