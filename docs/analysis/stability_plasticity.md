# Stability-Plasticity Analysis

Dynamical systems analysis of the stability-plasticity trade-off.

## Overview

The stability-plasticity dilemma: systems must be stable enough to retain knowledge but plastic enough to learn new tasks. Computronium provides dynamical metrics to quantify this trade-off.

## Key Metrics

| Metric | Description | Stability/Plasticity | Ideal |
|--------|-------------|---------------------|-------|
| `spectral_radius` | ρ(J_F) - asymptotic stability margin | Stability | < 1.0 |
| `max_singular_value` | σ_max(J_F) - transient amplification bound | Stability | Low |
| `lyapunov_exponent` | Largest Lyapunov exponent - chaos indicator | Stability | < 0 |
| `stability_margin` | 1 - ρ(J_F) - distance to instability | Stability | High |
| `nonnormality` | σ_max/ρ - transient amplification per contraction | Stability | Low |
| `settle_steps` | Iterations to convergence | Stability | Low |
| `psi_capacity` | Plastic state dimensionality | Plasticity | High |
| `consolidation_cost` | ψ→θ consolidation compute cost | Plasticity | Low |
| `rewrite_rate` | Rate of ψ rewriting | Plasticity | High |

## Computing Metrics

Metrics are automatically computed during probe runs:

```bash
# Run with stability metrics
uv run comp run eqprop --task digits --epochs 30 --store stability.db

# Check metrics
uv run comp stats --store stability.db \
  --metrics spectral_radius,max_singular_value,lyapunov_exponent,stability_margin,nonnormality,settle_steps,psi_capacity,consolidation_cost,rewrite_rate
```

## Stability Analysis

### Spectral Radius Tracking

```bash
# Track ρ(J) across training
uv run comp stats --store stability.db \
  --metrics spectral_radius \
  --by-epoch \
  --plot spectral_radius_evolution.png
```

### Lyapunov Spectrum

```bash
# Full Lyapunov spectrum (requires trajectory)
uv run comp stats --store stability.db \
  --lyapunov-spectrum \
  --plot lyapunov_spectrum.png
```

### Transient Amplification

```bash
# Nonnormality analysis
uv run comp stats --store stability.db \
  --metrics max_singular_value,nonnormality \
  --by-epoch \
  --plot transient_amplification.png
```

## Plasticity Analysis

### Plastic State Capacity

```bash
# Track ψ capacity across training
uv run comp stats --store stability.db \
  --metrics psi_capacity \
  --by-epoch \
  --plot psi_capacity_evolution.png
```

### Consolidation Cost

```bash
# ψ→θ consolidation cost
uv run comp stats --store stability.db \
  --metrics consolidation_cost \
  --by-epoch \
  --plot consolidation_cost.png
```

### Rewrite Rate

```bash
# Adaptation speed
uv run comp stats --store stability.db \
  --metrics rewrite_rate \
  --by-epoch \
  --plot rewrite_rate.png
```

## Stability-Plasticity Trade-off

### Pareto Frontier

```bash
# Accuracy vs stability
uv run comp pareto --store stability.db \
  -x spectral_radius -y validation_accuracy

# Accuracy vs plasticity
uv run comp pareto --store stability.db \
  -x psi_capacity -y validation_accuracy

# Three-way: accuracy, stability, plasticity
uv run comp pareto --store stability.db \
  -x spectral_radius -y validation_accuracy -z psi_capacity
```

### Stability-Plasticity Ratio

```bash
# Compute ratio
uv run comp stats --store stability.db \
  --compute-ratio spectral_radius/psi_capacity \
  --as stability_plasticity_ratio \
  --plot spr_evolution.png
```

### Beta Sweep (EqProp)

```bash
# Sweep β to trace trade-off curve
uv run comp campaign --model eqprop --task digits \
  --sweep 'beta=0.1,0.2,0.5,1.0,2.0,5.0' \
  --epochs 30 \
  --seeds 42,123,456 \
  --store beta_sweep.db

# Analyze trade-off
uv run comp stats --store beta_sweep.db \
  --metrics spectral_radius,psi_capacity,validation_accuracy \
  --group-by beta

# Plot trade-off curve
uv run comp pareto --store beta_sweep.db \
  -x spectral_radius -y validation_accuracy \
  --color-by beta \
  --plot beta_tradeoff.html
```

Expected results:
| Beta | Spectral Radius | Psi Capacity | Val Acc |
|------|-----------------|--------------|---------|
| 0.1  | 0.75            | 0.65         | 0.88    |
| 0.5  | 0.85            | 0.78         | 0.92    |
| 1.0  | 0.90            | 0.82         | 0.94    |
| 2.0  | 0.95            | 0.85         | 0.93    |
| 5.0  | 1.02            | 0.88         | 0.90    |

## Continual Learning Analysis

### Catastrophic Forgetting

```bash
# Sequential task learning
uv run comp campaign --model eqprop --task sequential_mnist \
  --sweep 'beta=0.5,1.0,2.0' \
  --epochs 20 \
  --seeds 42,123 \
  --store continual.db

# Measure forgetting
uv run comp stats --store continual.db \
  --metrics validation_accuracy,forgetting_rate \
  --by-task
```

### Forward Transfer

```bash
# Positive transfer measurement
uv run comp stats --store continual.db \
  --forward-transfer \
  --plot forward_transfer.png
```

## Dynamical Systems Visualization

### Phase Portrait

```bash
# 2D phase portrait (requires trajectory data)
uv run comp stats --store stability.db \
  --phase-portrait \
  --dims 0,1 \
  --plot phase_portrait.png
```

### Eigenvalue Distribution

```bash
# Jacobian eigenvalue spectrum
uv run comp stats --store stability.db \
  --eigenvalue-spectrum \
  --plot eigenvalue_spectrum.png
```

### Energy Landscape

```bash
# Free energy landscape (energy-based models)
uv run comp stats --store stability.db \
  --energy-landscape \
  --plot energy_landscape.png
```

## Substrate Comparison

```bash
# Compare stability metrics across substrates
uv run comp campaign --model eqprop --task digits \
  --sweep 'substrate=digital,memristive,photonic' \
  --epochs 20 \
  --seeds 42,123 \
  --store substrate_stability.db

uv run comp stats --store substrate_stability.db \
  --metrics spectral_radius,lyapunov_exponent,settle_steps,energy_per_step \
  --group-by substrate
```

Expected:
| Substrate | Spectral Radius | Lyapunov | Settle Steps | Energy/Step |
|-----------|-----------------|----------|--------------|-------------|
| digital   | 0.90±0.02       | -0.10±0.01 | 25±3       | 150μJ       |
| memristive| 0.88±0.03       | -0.12±0.02 | 22±2       | 80μJ        |
| photonic  | 0.85±0.04       | -0.15±0.02 | 18±2       | 200μJ       |

## Reporting

```bash
# Full stability-plasticity report
uv run comp report --store stability.db \
  --stability-plasticity \
  --output spr_report.html
```

Report includes:
- Stability metric evolution
- Plasticity metric evolution
- Trade-off Pareto frontiers
- Beta sweep analysis
- Substrate comparison
- Eigenvalue spectra
- Phase portraits
- Continual learning metrics

## Theoretical Background

### Spectral Radius & Stability

For a dynamical system `x_{t+1} = f(x_t)`, the Jacobian `J = ∂f/∂x` at fixed point determines local stability:

- `ρ(J) < 1`: Asymptotically stable (fixed point attracts)
- `ρ(J) > 1`: Unstable (diverges)
- `ρ(J) = 1`: Marginally stable (critical)

### Lyapunov Exponents

Measure exponential divergence of nearby trajectories:

- `λ_max < 0`: Trajectories converge (stable)
- `λ_max = 0`: Marginal (periodic/quasiperiodic)
- `λ_max > 0`: Chaos (sensitive dependence)

### Nonnormality

`σ_max(J)/ρ(J)` measures transient amplification:

- High nonnormality: Large transient growth before decay
- Can cause numerical instability in training

### Plasticity (ψ Capacity)

Dimensionality of plastic state space:

- Higher capacity = more adaptable
- But may reduce stability (interference)

## Next Steps

- [Analysis Index](../analysis/index.md) - Other analysis recipes
- [Pareto Analysis](pareto.md) - Multi-objective optimization
- [Ablation Studies](ablation.md) - Component contribution
- [Experiments](../experiments/index.md) - Running experiments