"""Parity Comparison Utilities.

Compare reference and kernel outputs with configurable tolerances.
Must remain generic - no knowledge of specific algorithms.
"""

import dataclasses
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


def digest(value: Any) -> str:
    """A total, structure-preserving digest of a reference output.

    ``compare`` needs tensor-shaped outputs; a substrate factory returns an
    object, and a composite state need not be a tensor. Two calls under one seed
    must agree on *all* of it, so this digests tensors by content, containers in
    order, dataclasses by field, and other objects by their public attributes —
    never by ``repr``, which carries an address.

    Args:
        value: Any reference output.

    Returns:
        A string that is equal for two structurally identical outputs.
    """
    parts: list[str] = []
    _digest_into(value, "out", parts)
    return "|".join(parts)


def _digest_into(node: Any, path: str, parts: list[str]) -> None:
    """Append ``node``'s structure to ``parts`` under ``path``."""
    if isinstance(node, torch.Tensor):
        flat = node.detach().reshape(-1).float()
        parts.append(
            f"{path}:{tuple(node.shape)}:{flat.sum().item():.17g}"
            f":{flat.abs().sum().item():.17g}"
        )
    elif isinstance(node, dict):
        for key in sorted(node, key=str):
            _digest_into(node[key], f"{path}.{key}", parts)
    elif isinstance(node, list | tuple):
        for index, item in enumerate(node):
            _digest_into(item, f"{path}[{index}]", parts)
    else:
        _digest_leaf(node, path, parts)


def _digest_leaf(node: Any, path: str, parts: list[str]) -> None:
    """Append a non-container value, never through ``repr`` on an object."""
    if dataclasses.is_dataclass(node) and not isinstance(node, type):
        for field in dataclasses.fields(node):
            _digest_into(getattr(node, field.name), f"{path}.{field.name}", parts)
    elif hasattr(node, "__dict__") and not isinstance(node, type):
        for key in sorted(vars(node)):
            if not key.startswith("_"):
                _digest_into(vars(node)[key], f"{path}.{key}", parts)
    else:
        parts.append(f"{path}={node!r}")


def compare(reference: Any, kernel: Any) -> dict[str, float]:
    """Compare reference and kernel outputs.

    Returns a report with max absolute difference, max relative difference,
    and cosine similarity.
    """
    ref = _flatten(reference)
    acc = _flatten(kernel)

    if ref.numel() == 0 and acc.numel() == 0:
        # Both empty - perfect match
        return {
            "max_abs_diff": 0.0,
            "max_rel_diff": 0.0,
            "cosine": 1.0,
        }

    abs_diff = torch.abs(ref - acc)
    max_abs_diff = abs_diff.max().item()

    # Relative difference with epsilon to avoid division by zero
    # Use combined tolerance approach: rel_diff = abs_diff / (abs_ref + eps)
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

    Uses combined absolute + relative tolerance per element:
        abs_diff <= atol + rtol * abs_ref

    This is the same convention as numpy.allclose and torch.allclose.
    Raises AssertionError with the report if any threshold is violated.

    If rtol is infinite (e.g., for activations crossing zero), only atol and cosine are checked.
    """
    report = compare(reference, kernel)

    ref = _flatten(reference)
    acc = _flatten(kernel)
    abs_diff = torch.abs(ref - acc)

    atol = tolerance.max_abs_diff
    rtol = tolerance.max_rel_diff

    # Handle infinite rtol (e.g., for GELU where relative diff is meaningless near zero)
    if rtol == float("inf") or (
        isinstance(rtol, float) and not torch.isfinite(torch.tensor(rtol))
    ):
        # Only check atol and cosine
        if report["max_abs_diff"] > atol:
            raise AssertionError(report)
    else:
        # Combined tolerance check (per-element, like numpy/torch allclose)
        combined_ok = (abs_diff <= atol + rtol * torch.abs(ref)).all().item()

        if not combined_ok:
            # Find the worst violation for the error message
            violation = (abs_diff - (atol + rtol * torch.abs(ref))).max().item()
            report["combined_violation"] = violation
            raise AssertionError(report)

    if report["cosine"] < tolerance.min_cosine:
        raise AssertionError(report)

    return report
