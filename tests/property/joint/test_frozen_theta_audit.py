"""J2 hardening: FrozenThetaAudit adversarial tests (TODO18 2.2).

The frozen-θ contract: across an audited episode, every persistent tensor
of the System — geometry parameters, substrate state tensors, optimizer
moment tensors — is bitwise identical, has an unchanged ``Tensor._version``
counter, and keeps its storage pointer. This catches:

- in-place value mutations (``theta.add_(1)``),
- mutate-then-restore patterns (version counter survives a ``copy_`` rollback),
- alias/storage rebinding (``data_ptr`` change),

not just the naive clone-comparison the pre-TODO18 J2 check used.
"""

import pytest
import torch

from computronium.core.frozen_theta import FrozenThetaAudit, frozen_theta_audit


class _Geometry:
    def __init__(self) -> None:
        self.params = {"w": torch.randn(4, 4), "b": torch.randn(4)}


class _System:
    def __init__(self) -> None:
        self.geometry = _Geometry()


def test_clean_episode_passes():
    system = _System()
    with FrozenThetaAudit(system) as audit:
        pass
    audit.assert_invariant()


def test_inplace_mutation_fails():
    system = _System()
    audit = FrozenThetaAudit(system)
    with audit:
        system.geometry.params["w"].add_(1.0)
    with pytest.raises(AssertionError, match="version_bumped"):
        audit.assert_invariant()
    assert audit.report is not None
    assert "geometry.w" in audit.report.mutated


def test_mutate_then_restore_fails():
    """copy_ rollback restores values but bumps _version — must be caught."""
    system = _System()
    with (
        pytest.raises(AssertionError, match="frozen-θ contract violated"),
        frozen_theta_audit(system),
    ):
        w = system.geometry.params["w"]
        orig = w.clone()
        w.add_(1.0)
        w.copy_(orig)


def test_alias_mutation_fails():
    """Mutation through an alias of the same storage must be caught."""
    system = _System()
    alias = system.geometry.params["w"]
    with pytest.raises(AssertionError, match="mutated"), frozen_theta_audit(system):
        alias.mul_(-1.0)


def test_rebinding_fails():
    """Rebinding a parameter to fresh storage must be caught via data_ptr."""
    system = _System()
    audit = FrozenThetaAudit(system)
    with audit:
        system.geometry.params["w"] = torch.randn_like(system.geometry.params["w"])
    with pytest.raises(AssertionError, match="rebound"):
        audit.assert_invariant()
    assert audit.report is not None
    assert "geometry.w" in audit.report.rebound


def test_report_available_after_exit():
    system = _System()
    audit = FrozenThetaAudit(system)
    with audit:
        pass
    assert audit.report is not None
    assert audit.report.invariant
