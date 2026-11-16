"""Locks for the memory-truth pass (TODO93 §9.1, §9.2).

Two claims are inadmissible without a lock. A declared memory class is not a
measurement, so a backend that has not been measured must report ``None``
rather than a fabricated zero. And a kernel whose nudged phase reproduces its
free phase produces a zero update, so it must be unavailable with a reason --
a ``pass`` where error modulation belongs is a stub, not an algorithm.

Both locks fail on the pre-TODO93 code: every backend returned
``activations_mb: 0.0`` and two contrastive kernels silenced their nudge.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import torch

from computronium.acceleration import get_algorithm_kernels
from computronium.acceleration.backprop_kernels import BackpropKernelBackend
from computronium.acceleration.contrastive_kernels import (
    ContrastiveConfig,
    PEPITAContrastiveKernel,
    get_contrastive_kernels,
)
from computronium.acceleration.kernel_backend import (
    AlgorithmFamily,
    HardwareTarget,
    KernelConfig,
    KernelRegistry,
)

_ACCELERATION = Path(__file__).resolve().parents[2] / "computronium" / "acceleration"


def _all_backend_classes() -> list[tuple[str, type]]:
    classes: dict[str, type] = dict(get_algorithm_kernels())
    classes.update(get_contrastive_kernels())
    return sorted(classes.items())


def _instantiate(cls: type) -> object:
    instance = cls()
    if hasattr(instance, "initialize"):
        instance.initialize(
            KernelConfig(
                algorithm=AlgorithmFamily.BACKPROP,
                hardware=HardwareTarget.CPU,
                extra={"input_dim": 8, "output_dim": 3},
            )
        )
    return instance


@pytest.mark.parametrize(("name", "cls"), _all_backend_classes())
def test_every_backend_declares_its_capabilities(name: str, cls: type) -> None:
    """``available`` and ``complexity_verified`` are declarations, not defaults."""
    assert hasattr(cls, "available"), f"{name} does not declare availability"
    assert hasattr(cls, "complexity_verified"), (
        f"{name} does not declare whether its memory class is measured"
    )
    if not cls.available:
        assert cls.unavailable_reason, f"{name} is unavailable without a reason"


def test_no_backend_hands_back_a_fabricated_activation_measurement() -> None:
    """The static half of the lock: the zero literal is gone from the package.

    A per-instance check cannot reach every backend (several need a bound layer
    stack before their stats dict exists), so the source scan pins the pattern
    that was the defect: a hardcoded ``activations_mb: 0.0`` in any kernel.
    """
    offenders = [
        path.name
        for path in _ACCELERATION.glob("*.py")
        if '"activations_mb": 0.0' in path.read_text()
    ]
    assert not offenders, (
        "kernels report a fabricated activation measurement rather than "
        f"None: {offenders}"
    )


def test_an_unbound_reading_of_a_verified_backend_is_none() -> None:
    """The dynamic half: an unmeasured term travels as ``None``, not zero."""
    kernel = BackpropKernelBackend()
    kernel.initialize(
        KernelConfig(
            algorithm=AlgorithmFamily.BACKPROP,
            hardware=HardwareTarget.CPU,
            extra={"input_dim": 8, "output_dim": 3},
        )
    )
    kernel.set_model_ref([torch.nn.Linear(8, 6), torch.nn.Linear(6, 3)])
    stats = kernel.get_memory_stats()
    assert stats["activations_mb"] is None
    params_mb = stats["params_mb"]
    assert params_mb is not None and params_mb > 0.0


def test_registry_refuses_an_unavailable_backend() -> None:
    """The stub declaration binds: no cell can route to a zero-update kernel."""
    for family in (
        AlgorithmFamily.FF_CONTRASTIVE,
        AlgorithmFamily.SNN_CONTRASTIVE,
    ):
        backend_cls = KernelRegistry._backends.get(family, {}).get(HardwareTarget.CPU)
        assert backend_cls is not None, f"{family} is not registered"
        assert backend_cls.available is False
        assert KernelRegistry.get(family, HardwareTarget.CPU) is None


def test_pepita_nudged_pass_moves_the_update() -> None:
    """The stub detector: a non-zero target error must change the update.

    Before TODO93 the nudged pass was a ``pass``, so the contrastive delta was
    identically zero and the kernel trained nothing.
    """
    torch.manual_seed(0)
    layers = [torch.nn.Linear(8, 16), torch.nn.Linear(16, 4)]
    kernel = PEPITAContrastiveKernel()
    kernel.initialize(
        ContrastiveConfig(
            algorithm=AlgorithmFamily.PEPITA_CONTRASTIVE,
            hardware=HardwareTarget.CPU,
            lr=0.1,
        )
    )
    kernel.set_model_ref(layers, torch.nn.ReLU())

    x = torch.randn(5, 8)
    y = torch.randint(0, 4, (5,))
    before = [layer.weight.detach().clone() for layer in layers]
    kernel.contrastive_step(x, y)

    deltas = [
        float((layer.weight - start).abs().max())
        for layer, start in zip(layers, before, strict=True)
    ]
    assert all(delta > 1e-6 for delta in deltas), f"zero update: {deltas}"


def test_free_and_nudged_phases_differ_under_error() -> None:
    """The modulated pass is a second pass, not a second copy of the first."""
    torch.manual_seed(0)
    layers = [torch.nn.Linear(8, 16), torch.nn.Linear(16, 4)]
    kernel = PEPITAContrastiveKernel()
    kernel.initialize(
        ContrastiveConfig(
            algorithm=AlgorithmFamily.PEPITA_CONTRASTIVE,
            hardware=HardwareTarget.CPU,
        )
    )
    kernel.set_model_ref(layers, torch.nn.ReLU())

    x = torch.randn(5, 8)
    free = kernel.free_phase(x)
    nudged = kernel.nudged_phase(x, torch.randint(0, 4, (5,)))
    gap = max(float((f - n).abs().max()) for f, n in zip(free, nudged, strict=True))
    assert gap > 1e-6, "nudged phase reproduces the free phase"


def test_snn_contrastive_declares_why_it_cannot_train() -> None:
    cls = get_contrastive_kernels()["snn_contrastive"]
    assert cls.available is False
    assert "target" in (cls.unavailable_reason or "")
