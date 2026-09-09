# Family Recipe Registry

Canonical constructors for each credit family — copy-paste these instead of
guessing configs. Each entry is the exact combination that reproduces the
recorded number at the operating point.

---

## FF — `LocalContrastiveCredit` (W2 flagship)

**Operating point**: d2 0.824 / d4 0.757 / d8 0.512 (3 seeds, EMA + seq-LR)

```python
geometry = FeedforwardGeometry(
    GeometryConfig.feedforward(
        input_dim=784 + 10,          # label-augmented input
        output_dim=10,
        hidden_dims=(128,) * (depth - 1),
    )
)
credit = LocalContrastiveCredit(
    CreditAssignmentConfig.local_contrastive(
        label_dim=10,
        ema_beta=0.99,
        sequential_lr=0.3,            # MUST match update.step_size
        readout_scale=1 / 3,
    )
)
update = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.3))
dynamics = InstantaneousDynamics()
```

**Input contract**: data must be label-augmented (`x ⊕ onehot(label)`);
eval uses the "good" stream (same augmentation).

---

## EqProp — `ThermodynamicContrast` + `EnergyMinimizationDynamics`

**Operating point**: 0.86 on RecurrentGeometry (32,) — swap_credit demo

```python
geometry = FeedforwardGeometry(
    GeometryConfig.feedforward(
        input_dim=784,
        output_dim=10,
        hidden_dims=(128,) * (depth - 1),
        # DEFAULT init_scale=0.1 — EqProp small-init convention!
        # Do NOT use init_scale=1.0 or μPC — collapses the family.
    )
)
credit = ThermodynamicContrast(CreditAssignmentConfig.thermodynamic_contrast(beta=0.5))
update = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.1))
dynamics = EnergyMinimizationDynamics(
    StateDynamicsConfig.energy_minimization(max_steps=30, beta=0.5)
)
```

**Depth caveat**: collapses beyond d2–d4 (harvest: peaks @batch 60, EMA → chance).

---

## ePC — `ThermodynamicContrast` + `ErrorPredictiveCodingDynamics`

**Operating point**: depth 32 0.917 / 50 0.824 mean (3 seeds, harvest)

```python
geometry = FeedforwardGeometry(
    GeometryConfig.feedforward(
        input_dim=784,
        output_dim=10,
        hidden_dims=(128,) * (depth - 1),
        init_scheme="mupc",
        residual=True,
    )
)
credit = ThermodynamicContrast(
    CreditAssignmentConfig.thermodynamic_contrast(beta=0.5)
)
update = OrthoAdamUpdate(
    ParameterUpdateConfig.ortho_adam(step_size=1e-3)
)
dynamics = ErrorPredictiveCodingDynamics(
    StateDynamicsConfig.error_predictive_coding(max_steps=depth, beta=0.5)
)
```

**Depth**: works to 32+ layers under harvest; the program's current frontier.

---

## PEPITA (published) — `PepitaCredit`

**Operating point**: MNIST 0.884 (BP 0.890, γ=0.05, Adam 1e-3)

```python
geometry = FeedforwardGeometry(
    GeometryConfig.feedforward(
        input_dim=784,
        output_dim=10,
        hidden_dims=(128,) * (depth - 1),
        init_scheme="mupc",
        residual=True,
    )
)
credit = PepitaCredit(CreditAssignmentConfig.pepita(gamma=0.05))
# Substrate hook auto-wired by compose_system; credit.set_substrate() optional
update = AdamUpdate(ParameterUpdateConfig.adam(step_size=1e-3))
dynamics = InstantaneousDynamics()
```

**Task bound**: classification only (fixed inputs). LM cell = boundary-locked.

---

## LEMMA (per-layer closed-form) — `LocalGoodnessCredit` with `local_objective="lemma"`

**Status**: boundary-locked (alignment noise, harvest-audited plateau)

```python
credit = LocalGoodnessCredit(
    CreditAssignmentConfig.local_goodness(
        feedback_scale=0.01,
        local_objective="lemma",      # NOT "pepita"
        learned_feedback=False,
    )
)
```

---

## LocalGoodness FF — `LocalGoodnessCredit` with `local_objective="ff"`

**Operating point**: Hinton FF contrast (layer-local G contrast)

```python
credit = LocalGoodnessCredit(
    CreditAssignmentConfig.local_goodness(
        feedback_scale=0.01,
        local_objective="ff",
    )
)
```

**Note**: distinct from `LocalContrastiveCredit` — uses label-injected GOOD/BAD streams, no EMA/seq-LR machinery.

---

## Random Projections (FA/DFA) — `RandomProjectionsCredit`

```python
credit = RandomProjectionsCredit(
    CreditAssignmentConfig.random_projections(
        feedback_scale=0.01,
        orthogonal_init=False,
        learned_feedback=False,
    )
)
```

---

## Backprop — `BackpropCredit` (alias for `GradientCredit`)

```python
credit = BackpropCredit(CreditAssignmentConfig.gradient())
```

---

# Geometry Notes (common pitfalls)

| family             | init_scheme | residual | init_scale | notes |
|--------------------|-------------|----------|------------|-------|
| FF                 | default     | False    | 1.0*       | manual nn.Linear stack preferred |
| EqProp             | default     | False    | **0.1**    | EqProp small-init convention |
| ePC                | **mupc**    | **True** | 1.0        | μPC + residual are ePC conventions |
| PEPITA             | mupc        | True     | 1.0        | same as ePC |
| LocalGoodness FF   | default     | False    | 1.0        | label-augmented input |

*\* FF's record used manual `nn.Linear` (kaiming uniform) — equivalent to `init_scale≈1.0`.*

---

# Quick-Reference: How to Build a System for Family X

```python
from computronium import compose_system, DigitalSubstrate, ...

system = compose_system(
    substrate=DigitalSubstrate(),
    geometry=...,
    dynamics=...,
    credit=...,
    update=...,
)
```

The `compose_system` call wires `set_substrate` (for PEPITA) and
`set_update_rule` (for sequential-LR FF) automatically.