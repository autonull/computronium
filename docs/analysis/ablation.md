# Ablation Studies

Component contribution analysis through systematic ablation.

## Overview

Ablation studies quantify the contribution of each component by comparing full system performance against variants with components removed.

## Basic Usage

```bash
# Run ablation sweep
uv run comp campaign --model eqprop --task digits \
  --sweep 'use_feedback=True,False' \
  --sweep 'use_homeostatic=True,False' \
  --sweep 'use_weight_decay=True,False' \
  --epochs 20 \
  --seeds 42,123,456 \
  --store ablation.db
```

## Analyzing Ablation Results

### Main Effect Analysis

```bash
# Compare each component's contribution
uv run comp diff --store ablation.db \
  --group-by use_feedback \
  --metric validation_accuracy

# All components at once
uv run comp stats --store ablation.db \
  --ablation \
  --metrics validation_accuracy,walltime_total,spectral_radius
```

Output:
```
Component          Δ Accuracy    Δ Walltime    Δ Spectral Rad   p-value
use_feedback       +0.045***    +15.2s        -0.08*           0.001
use_homeostatic    +0.012*      +3.1s         -0.03            0.023
use_weight_decay   +0.008       +0.5s         -0.01            0.156
```

### Interaction Effects

```bash
# Two-way interactions
uv run comp stats --store ablation.db \
  --interaction use_feedback,use_homeostatic \
  --metric validation_accuracy
```

Output:
```
Interaction                    Effect Size    p-value
use_feedback × use_homeostatic +0.006         0.041*
```

### Waterfall Chart

```bash
# Visualize component contributions
uv run comp stats --store ablation.db \
  --waterfall \
  --metric validation_accuracy \
  --output ablation_waterfall.png
```

## Experimental Design

### Full Factorial (Recommended)

```bash
# All combinations (2^k for k binary components)
uv run comp campaign --model eqprop --task digits \
  --sweep 'use_feedback=True,False' \
  --sweep 'use_homeostatic=True,False' \
  --sweep 'use_weight_decay=True,False' \
  --sweep 'beta=0.5,1.0' \
  --epochs 20 \
  --seeds 42,123,456 \
  --store ablation_full.db
```

Runs: 2^4 × 3 seeds = 48 runs

### Fractional Factorial (Fewer Runs)

```bash
# Resolution IV design (8 runs instead of 16)
uv run comp campaign --model eqprop --task digits \
  --sweep 'use_feedback=True,False' \
  --sweep 'use_homeostatic=True,False' \
  --sweep 'use_weight_decay=True,False' \
  --sweep 'beta=0.5,1.0' \
  --fractional 0.5 \
  --epochs 20 \
  --seeds 42,123 \
  --store ablation_frac.db
```

Runs: 8 × 2 seeds = 16 runs

### One-at-a-Time (Fastest, Less Rigorous)

```bash
# Baseline + each component removed
uv run comp campaign --model eqprop --task digits \
  --config 'use_feedback=True,use_homeostatic=True,use_weight_decay=True,beta=1.0' \
  --epochs 20 --seeds 42 --store baseline.db

uv run comp campaign --model eqprop --task digits \
  --config 'use_feedback=False,use_homeostatic=True,use_weight_decay=True,beta=1.0' \
  --epochs 20 --seeds 42 --store no_feedback.db

uv run comp campaign --model eqprop --task digits \
  --config 'use_feedback=True,use_homeostatic=False,use_weight_decay=True,beta=1.0' \
  --epochs 20 --seeds 42 --store no_homeostatic.db
```

## Statistical Analysis

### ANOVA

```bash
# Main effects ANOVA
uv run comp stats --store ablation.db \
  --test anova \
  --group-by use_feedback,use_homeostatic,use_weight_decay \
  --metric validation_accuracy
```

### Effect Size (Cohen's d)

```bash
# Standardized effect sizes
uv run comp stats --store ablation.db \
  --effect-size \
  --group-by use_feedback,use_homeostatic,use_weight_decay \
  --metric validation_accuracy
```

### Bootstrap CI

```bash
# Confidence intervals for effects
uv run comp stats --store ablation.db \
  --bootstrap 5000 \
  --ci 0.95 \
  --ablation \
  --metric validation_accuracy
```

## Visualization

### Ablation Waterfall

```bash
uv run comp stats --store ablation.db \
  --waterfall \
  --metric validation_accuracy \
  --baseline 'use_feedback=True,use_homeostatic=True,use_weight_decay=True' \
  --output ablation_waterfall.html
```

### Interaction Heatmap

```bash
uv run comp stats --store ablation.db \
  --interaction-heatmap \
  --metric validation_accuracy \
  --output interaction_heatmap.png
```

### Component Importance Bar Chart

```bash
uv run comp stats --store ablation.db \
  --importance \
  --metric validation_accuracy \
  --output importance.png
```

## Reporting

```bash
# Full ablation report
uv run comp report --store ablation.db \
  --ablation \
  --output ablation_report.html
```

Report includes:
- Main effects table with significance
- Interaction effects
- Waterfall chart
- Interaction heatmap
- Component importance ranking
- Bootstrap confidence intervals
- Effect size interpretation

## Common Ablation Targets

### For EqProp
- `use_feedback`: Backward pass feedback weights
- `use_homeostatic`: Homeostatic plasticity
- `use_weight_decay`: L2 regularization
- `beta`: Nudging strength (sweep continuous)
- `num_nudged_steps`: Inference iterations

### For Backprop
- `use_batch_norm`: Batch normalization
- `use_dropout`: Dropout layers
- `use_weight_decay`: L2 regularization
- `learning_rate_schedule`: Constant vs cosine vs step

### For FA/TP/PC
- `use_feedback_alignment`: Fixed random feedback
- `use_direct_feedback`: Direct output feedback
- `feedback_sparsity`: Sparse feedback matrix
- `weight_mirror`: Mirror forward weights

### For Substrates
- `noise_level`: Substrate noise injection
- `quantization_bits`: Weight precision
- `nonlinearity`: Device nonlinearity model

## Best Practices

1. **Use factorial designs** - Capture interactions, not just main effects
2. **Multiple seeds** - At least 3 seeds for statistical validity
3. **Control for walltime** - Some ablations change compute time
4. **Report effect sizes** - Statistical significance ≠ practical importance
5. **Visualize interactions** - Heatmaps reveal non-additive effects

## Example: EqProp Ablation

```bash
# 1. Run full factorial
uv run comp campaign --model eqprop --task digits \
  --sweep 'use_feedback=True,False' \
  --sweep 'use_homeostatic=True,False' \
  --sweep 'use_weight_decay=True,False' \
  --sweep 'beta=0.5,1.0,2.0' \
  --epochs 30 \
  --seeds 42,123,456 \
  --store eqprop_ablation.db

# 2. Analyze
uv run comp stats --store eqprop_ablation.db --ablation

# 3. Visualize
uv run comp stats --store eqprop_ablation.db --waterfall --output figs/
uv run comp stats --store eqprop_ablation.db --interaction-heatmap --output figs/

# 4. Report
uv run comp report --store eqprop_ablation.db --ablation --output eqprop_ablation.html
```

Expected findings:
- `use_feedback`: Large effect (essential for credit assignment)
- `use_homeostatic`: Medium effect (stabilizes learning)
- `use_weight_decay`: Small effect (regularization)
- `beta`: Strong interaction with `use_feedback`

## Next Steps

- [Analysis Index](../analysis/index.md) - Other analysis recipes
- [Pareto Analysis](pareto.md) - Multi-objective optimization
- [Stability-Plasticity](stability_plasticity.md) - Dynamical analysis
- [Experiments](../experiments/index.md) - Running experiments