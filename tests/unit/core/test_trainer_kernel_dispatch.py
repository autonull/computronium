"""Kernel-backend dispatch in ``dispatch_train_step`` (TODO35 §12).

The contrastive branch of the kernel path imported
``_run_contrastive_kernel_step`` / ``_run_kernel_train_step`` from
``computronium.core.trainer`` — names the module did not define and nothing
else in the tree defines either, so the branch raised ``ImportError`` the
first time a kernel backend exposed ``contrastive_step`` and nothing else.
The fix routes to the backend's own methods, whose signatures the helpers
were thin wrappers around.

Both branches are asserted because the class of defect is a name that
resolves to nothing: a passing bespoke-branch test says nothing about the
sibling branch.
"""

from typing import Any, ClassVar

import torch
from torch import nn

from computronium.core.trainer import dispatch_train_step


class _BespokeBackend:
    """A backend with the bespoke ``kernel_train_step`` contract."""

    def __init__(self) -> None:
        self.calls: list[tuple[Any, ...]] = []

    def kernel_train_step(
        self,
        model: nn.Module,
        config: Any,
        x: torch.Tensor,
        y: torch.Tensor,
        optimizer: object | None = None,
    ) -> dict[str, object]:
        self.calls.append((x, y, optimizer))
        return {"loss": 0.5, "route": "bespoke"}


class _ContrastiveBackend:
    """A backend with only the contrastive ``contrastive_step`` contract."""

    def __init__(self) -> None:
        self.calls: list[tuple[torch.Tensor, torch.Tensor]] = []

    def contrastive_step(
        self, x: torch.Tensor, target: torch.Tensor
    ) -> dict[str, float]:
        self.calls.append((x, target))
        return {"loss": 0.25, "route": 1.0}


class _BareBackend:
    """A backend with neither step contract: dispatch must fall through."""


class _KernelModel(nn.Module):
    def __init__(self, backend: object) -> None:
        super().__init__()
        self.lin = nn.Linear(4, 3)
        self._kernel_backend = backend

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.lin(x)


def _config() -> Any:
    from computronium.core.trainer import _TrainerConfigProtocol

    class _Config(_TrainerConfigProtocol):
        optimizer_kwargs: ClassVar[dict[str, object]] = {}
        extra: ClassVar[dict[str, object]] = {}
        grad_clip: ClassVar[float | None] = None

    return _Config()


def _dispatch(
    backend: object, config: object | None
) -> tuple[dict[str, object], list[str]]:
    recorded: list[str] = []
    model = _KernelModel(backend)
    x = torch.randn(2, 4)
    y = torch.randint(0, 3, (2,))
    metrics = dispatch_train_step(
        model,
        x,
        y,
        adapt_input=lambda t: t,
        propagator=None,
        optimizer=torch.optim.SGD(model.parameters(), lr=0.01),
        config=config,  # type: ignore[arg-type]
        record_path=recorded.append,
    )
    return metrics, recorded


def test_bespoke_kernel_step_is_reached() -> None:
    backend = _BespokeBackend()
    metrics, recorded = _dispatch(backend, _config())
    assert len(backend.calls) == 1
    assert metrics["route"] == "bespoke"
    assert recorded == ["kernel"]


def test_contrastive_kernel_step_is_reached() -> None:
    backend = _ContrastiveBackend()
    metrics, recorded = _dispatch(backend, _config())
    assert len(backend.calls) == 1
    assert metrics["route"] == 1.0
    assert recorded == ["kernel"]


def test_a_backend_with_no_step_contract_falls_through() -> None:
    """No step method means the kernel path yields, not raises."""
    metrics, recorded = _dispatch(_BareBackend(), _config())
    assert recorded == ["kernel", "bptt"]
    assert "logits" in metrics


def test_kernel_path_is_skipped_without_config() -> None:
    """``config is None`` leaves the backend untouched, as before."""
    backend = _BespokeBackend()
    _, recorded = _dispatch(backend, None)
    assert not backend.calls
    assert recorded == ["bptt"]
