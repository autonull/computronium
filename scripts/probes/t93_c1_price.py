"""Price one batch-1 PEPITA step for track C's plasticity ladder (TODO93 C1).

Measures per-step walltime for a local (PEPITA) and a backprop arm on the
SplitMNIST geometry at batch 1, so the ladder watchdog is priced from a
measured cell rather than a guess. Prints only; the number lives in the
ladder module once C1 lands.

uv run python scripts/probes/t93_c1_price.py
"""

from __future__ import annotations

import time

import torch

from computronium.core.continual.arms import (
    _get_compose_joint_system,
    create_backprop_arm,
)
from computronium.core.continual.system import ContinualJointSystem
from computronium.core.joint.transition import NullPlasticity
from computronium.ontology import (
    CreditAssignmentConfig,
    DigitalSubstrate,
    EuclideanUpdate,
    FeedforwardGeometry,
    GeometryConfig,
    InstantaneousDynamics,
    ParameterUpdateConfig,
    PepitaCredit,
    StateDynamicsConfig,
    SubstrateConfig,
)


def _local_arm(device: str) -> ContinualJointSystem:
    substrate = DigitalSubstrate(
        SubstrateConfig.digital(precision="float32", noise_level=0.0, device=device)
    )
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=784,
            output_dim=10,
            hidden_dims=(256, 256),
            init_scale=0.1,
        )
    )
    joint = _get_compose_joint_system()(
        substrate,
        geometry,
        InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
        NullPlasticity(),
        PepitaCredit(CreditAssignmentConfig.pepita()),
        EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.01)),
    )
    return ContinualJointSystem.from_joint_system(joint).to(device)


def main() -> None:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    x = torch.randn(1, 784, device=device)
    y = torch.tensor([1], device=device)
    for name, build in (("local", _local_arm), ("backprop", create_backprop_arm)):
        model = build("cuda") if build is _local_arm else build(device=device)
        for _ in range(20):
            model.train_step(x, y, task_id=0)
        torch.cuda.synchronize() if device == "cuda" else None
        start = time.perf_counter()
        for _ in range(200):
            model.train_step(x, y, task_id=0)
        torch.cuda.synchronize() if device == "cuda" else None
        elapsed = time.perf_counter() - start
        print(f"{name}: {elapsed / 200 * 1e3:.3f} ms/step")


if __name__ == "__main__":
    main()
