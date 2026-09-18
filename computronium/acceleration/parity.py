"""Parity Comparison Utilities.

Compare reference and kernel outputs with configurable tolerances.
Must remain generic - no knowledge of specific algorithms.
"""

from typing import TYPE_CHECKING, Any

import torch

if TYPE_CHECKING:
    from computronium.acceleration.spec import ParityTolerance


def _is_composite_state(obj: Any) -> bool:
    """Check if object is a CompositeState (duck typing)."""
    return (
        hasattr(obj, "activity")
        and hasattr(obj, "plastic")
        and hasattr(obj, "substrate")
    )


def _flatten_composite_state(value: Any) -> torch.Tensor:
    """Flatten a CompositeState to 1D tensor."""
    parts = []
    for attr_name in ("activity", "plastic", "substrate"):
        attr = getattr(value, attr_name, None)
        if not isinstance(attr, dict):
            continue
        for v in attr.values():
            if isinstance(v, torch.Tensor):
                parts.append(v.detach().reshape(-1).float())
            elif isinstance(v, list):
                parts.extend(
                    t.detach().reshape(-1).float()
                    for t in v
                    if isinstance(t, torch.Tensor)
                )
    return torch.cat(parts) if parts else torch.tensor([])


def _flatten(value: Any) -> torch.Tensor:
    """Flatten arbitrary nested structures to 1D tensor for comparison."""
    if isinstance(value, torch.Tensor):
        return value.detach().reshape(-1).float()

    if isinstance(value, dict):
        parts = [_flatten(v) for v in value.values()]
        return torch.cat(parts) if parts else torch.tensor([])

    if isinstance(value, tuple | list):
        parts = [_flatten(v) for v in value]
        return torch.cat(parts) if parts else torch.tensor([])

    if _is_composite_state(value):
        return _flatten_composite_state(value)

    return torch.as_tensor(value).detach().reshape(-1).float()


def compare(reference: Any, kernel: Any) -> dict[str, float]:
    """Compare reference and kernel outputs.

    Returns a report with max absolute difference, max relative difference,
    and cosine similarity.
    """
    ref = _flatten(reference)
    acc = _flatten(kernel)

    abs_diff = torch.abs(ref - acc)
    max_abs_diff = abs_diff.max().item()

    rel_diff = abs_diff / (torch.abs(ref) + 1e-8)
    max_rel_diff = rel_diff.max().item()

    if ref.numel() == 0:
        cosine = 1.0
    elif torch.allclose(ref, torch.zeros_like(ref)) and torch.allclose(
        acc, torch.zeros_like(acc)
    ):
        # Both are all zeros - they are identical
        cosine = 1.0
    else:
        cosine = torch.nn.functional.cosine_similarity(
            ref.unsqueeze(0),
            acc.unsqueeze(0),
        ).item()

    return {
        "max_abs_diff": max_abs_diff,
        "max_rel_diff": max_rel_diff,
        "cosine": cosine,
    }


def assert_parity(
    reference: Any, kernel: Any, tolerance: ParityTolerance
) -> dict[str, float]:
    """Assert that reference and kernel outputs match within tolerance.

    Raises AssertionError with the report if any threshold is violated.
    """
    report = compare(reference, kernel)

    if report["max_abs_diff"] > tolerance.max_abs_diff:
        raise AssertionError(report)
    if report["max_rel_diff"] > tolerance.max_rel_diff:
        raise AssertionError(report)
    if report["cosine"] < tolerance.min_cosine:
        raise AssertionError(report)

    return report
