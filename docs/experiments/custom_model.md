# Training a Custom Model

This tutorial shows how to define and train a new primitive (algorithm) with computronium.

## Overview

Computronium uses a registry-based architecture where algorithms are registered as **primitives**. Each primitive implements a `StateDynamics` protocol with `settle` and `compute_energy` methods.

## 1. Define Your Primitive

Create a new file `my_primitive.py`:

```python
"""Custom primitive: Simple Gradient Descent with Momentum."""

from dataclasses import dataclass
from typing import Protocol
import torch
from torch import Tensor

from computronium.ontology.dynamics import StateDynamics, StateDynamicsConfig
from computronium.ontology.system import System


# Configuration
@dataclass(frozen=True, slots=True)
class MomentumSGDConfig(StateDynamicsConfig):
    dynamics_type: str = "momentum_sgd"
    learning_rate: float = 0.01
    momentum: float = 0.9


# Implementation
class MomentumSGDDynamics(StateDynamics):
    """SGD with momentum dynamics."""

    def __init__(self, config: MomentumSGDConfig):
        self.config = config
        self.velocity: dict[str, Tensor] = {}

    def settle(
        self,
        system: System,
        inputs: Tensor,
        targets: Tensor | None = None,
        *,
        free: bool = True,
        nudged: bool = False,
        beta: float = 0.0,
    ) -> Tensor:
        """Run one forward/backward step with momentum."""
        params = dict(system.named_parameters())

        if free:
            # Free phase: standard forward pass
            with torch.no_grad():
                for name, p in params.items():
                    if p.grad is not None:
                        # Momentum update
                        if name not in self.velocity:
                            self.velocity[name] = torch.zeros_like(p)
                        self.velocity[name].mul_(self.config.momentum).add_(p.grad)
                        p.sub_(self.velocity[name] * self.config.learning_rate)

        elif nudged:
            # Nudged phase: target propagation (simplified)
            with torch.no_grad():
                for name, p in params.items():
                    if p.grad is not None:
                        if name not in self.velocity:
                            self.velocity[name] = torch.zeros_like(p)
                        self.velocity[name].mul_(self.config.momentum).add_(p.grad * beta)
                        p.sub_(self.velocity[name] * self.config.learning_rate)

        # Return activations for next layer
        return system(inputs)

    def compute_energy(self, system: System, activations: Tensor) -> Tensor:
        """Compute loss as energy."""
        return torch.nn.functional.cross_entropy(activations, system.targets)
```

## 2. Register the Primitive

Add to `computronium/ontology/dynamics/__init__.py`:

```python
from .my_primitive import MomentumSGDDynamics, MomentumSGDConfig

DYNAMICS_REGISTRY["momentum_sgd"] = MomentumSGDDynamics
StateDynamicsConfig.register_dynamics("momentum_sgd", MomentumSGDConfig)
```

## 3. Add to Root Exports

In `computronium/__init__.py`:

```python
from computronium.ontology.dynamics.my_primitive import MomentumSGDDynamics
__all__ = [..., "MomentumSGDDynamics", "MomentumSGDConfig"]
```

## 4. Run Your Primitive

```bash
# Test with quick-verify
uv run comp run momentum_sgd --task digits --epochs 5 --store test.db

# Run campaign
uv run comp campaign \
  --model momentum_sgd \
  --task digits \
  --sweep 'learning_rate=0.001,0.01,0.1' \
  --sweep 'momentum=0.8,0.9,0.99' \
  --store sweep.db
```

## 5. Verify It Works

```bash
# Check probe results include your dynamics
uv run comp stats --store test.db --format json
```

Expected output should include:
- `validation_accuracy`
- `walltime_total`
- `spectral_radius`, `lyapunov_exponent`, `settle_steps` (stability metrics)

## Adding Configuration Options

Use the config class to add algorithm-specific hyperparameters:

```python
@dataclass(frozen=True, slots=True)
class MyConfig(StateDynamicsConfig):
    dynamics_type: str = "my_algorithm"
    learning_rate: float = 0.01
    custom_param: float = 1.0  # Your custom parameter
    custom_bool: bool = True
```

The CLI will automatically expose these as flags:
```bash
comp run my_algorithm --custom-param 2.0 --no-custom-bool
```

## Testing Your Primitive

```python
# test_my_primitive.py
import pytest
from computronium.experiment.probe import run_probe, CoreTrainerDriver

def test_my_primitive_runs():
    driver = CoreTrainerDriver(record_results=False)
    result = run_probe(
        driver,
        model="momentum_sgd",
        task="digits",
        config={"learning_rate": 0.01, "momentum": 0.9},
        seed=42,
        epochs=2,
        device="cpu",
    )
    assert result.status == "ok"
    assert result.final_acc > 0.0
    assert result.spectral_radius >= 0.0  # Stability metrics populated
```

Run with:
```bash
uv run pytest test_my_primitive.py -v
```

## Resources

- [Dynamics Protocol](../reference/dynamics_protocol.md) - Full StateDynamics API
- [Primitive Registry](../reference/primitive_registry.md) - Registry internals
- [System Composition](../reference/system_composition.md) - Building systems