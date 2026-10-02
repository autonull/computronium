## 60-second quickstart

Compose a 6-axis system and train it on MNIST. This block is locked verbatim against its source demo test ([`tests/integration/test_demo_compose_6axis.py`](tests/integration/test_demo_compose_6axis.py)):

<!-- lock: composition_6axis -->
```python
import torch

from computronium import (
    DigitalSubstrate,
    EnergyMinimizationDynamics,
    EuclideanUpdate,
    GeometryConfig,
    NullPlasticity,
    RecurrentGeometry,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemTrainer,
    SystemTrainerConfig,
    ThermodynamicContrast,
    compose_joint_system,
    create_task,
)


def _flatten(loader):
    for x, y in loader:
        yield x.view(x.size(0), -1), y


task = create_task("mnist", device="cpu", quick_mode=True)
task.setup()
train_loader = task.get_dataloader("train")

torch.manual_seed(0)
six_axis = compose_joint_system(
    substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
    geometry=RecurrentGeometry(
        GeometryConfig.recurrent(input_dim=784, output_dim=10, hidden_dims=(32,))
    ),
    dynamics=EnergyMinimizationDynamics(
        StateDynamicsConfig.energy_minimization(max_steps=5, beta=0.5)
    ),
    plasticity=NullPlasticity(),
    credit=ThermodynamicContrast(),
    update=EuclideanUpdate(),
)
trainer = SystemTrainer(
    system=six_axis,
    config=SystemTrainerConfig(max_epochs=1, device="cpu", seed=42),
    train_data=_flatten(train_loader),
)
history = trainer.fit()
print(f"train accuracy: {history[-1]['train_acc']:.1%}")
```

Expected result (Level 4 — sampled numerical): one CPU epoch reaches ≈ 0.9 train accuracy (chance 0.1).

---
