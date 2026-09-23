#!/usr/bin/env python
"""Generate property tests from ImplementationSpec invariants.

Creates hypothesis tests for mechanically checkable invariants:
- deterministic under fixed seed
- state remains finite (no NaN/Inf)
"""

# ruff: noqa: S404,S607
import argparse
import pathlib
import sys

from computronium.acceleration.registry import all_specs

DETERMINISTIC_INVARIANTS = {
    "deterministic under fixed seed",
    "deterministic under fixed seed",
    "deterministic under fixed seed",
}

FINITE_INVARIANTS = {
    "state remains finite",
    "finite state",
    "activations remain finite",
    "parameters remain finite",
    "state remains finite",
    "weight updates remain bounded",
    "fast weights remain bounded",
    "gate logits remain bounded",
    "parameters updated in-place or returned as new dict",
    "momentum buffers preserved across steps",
    "closed-form solution is exact",
    "projection is non-expansive (||P v|| <= ||v||)",
    "plastic state returned unchanged",
    "no plastic state allocated initially",
    "trace decay enables task migration",
    "stochastic sampler over fixed points",
    "spike times are deterministic",
    "conductance stays within bounds",
    "bitwise reproducibility at same precision",
    "noise level matches config",
    "complex-valued operations",
    "unitary operations preserve norm",
    "sparsity level matches config",
    "weights constrained to ternary values",
    "gradient matches autograd reference",
    "feedback matrices are fixed and not transposes",
    "all hidden layers receive feedback directly from output layer",
    "pseudo-gradients align with reference gradients over time",
    "free energy decreases during settling",
    "nudged phase converges to nearby equilibrium",
    "local contrastive update approximates true gradient",
    "fast weights decay within episode",
    "associative memory property",
    "frozen-θ contract during intra-episode updates",
    "no backward pass through the network",
    "layer-local losses and optimizers",
    "local weight updates only",
    "no global error signal required",
    "single fixed random feedback matrix B",
    "error modulation in second forward pass",
    "autograd update on perturbed states",
    "routing gates are dynamic and state-dependent",
    "sparsity constraint on active pathways",
    "frozen-θ contract during intra-episode routing",
    "spike timing determines weight updates",
    "membrane potential dynamics are deterministic",
    "structured sparsity within tiles",
    "targets propagated via transpose of forward weights",
    "output target is one-hot label",
    "pseudo-gradients use local layer activations and targets",
    "dual variables are produced by PCALMDynamics settling",
    "weight updates are local Hebbian (pre × post)",
    "credit_norm normalization options: relative, rms, spectral",
    "feedback matrices are fixed (not learned)",
    "feedback matrices are not transposes of forward weights",
    "antisymmetry: W(Δt) = -W(-Δt)",
    "causal > 0, anti-causal < 0",
    "exponential decay of traces",
    "homeostatic target norm maintained",
    "exact gradient match with autograd",
    "target propagation preserves layer structure",
    "pseudo-gradients finite",
    "energy non-increasing on symmetric topology",
    "graph structure preserved",
    "output shape matches (batch, output_dim)",
    "grid topology preserved",
    "memory slots maintain identity",
    "symmetric topology enables Lyapunov analysis",
    "local connectivity preserved",
    "tile activities remain finite",
    "EWC regularization applied",
    "momentum buffers preserved across steps",
    "global-norm gradient clipping applied if configured",
    "orthogonal updates preserve Frobenius norm of weight matrices",
    "momentum accumulates signal before orthogonalization",
    "vectors (biases) ride plain SGD",
    "Fisher diagonal EMA updated per step",
    "spectral norm of update is bounded",
    "fast weights remain bounded",
    "projection is non-expansive (||P v|| <= ||v||)",
    "gate logits remain bounded",
    "active routes sum to 1 per sample (training) or match top_k (eval)",
    "ψ remains finite",
    "θ frozen during eval",
    "substrate state evolves with plasticity",
    "free energy decreases or remains bounded",
    "prediction errors decrease or remain bounded",
    "settling residual decreases or remains bounded",
    "free energy decreases during settling",
    "hierarchical error propagation",
    "local error signals remain bounded",
    "settling dynamics are deterministic under fixed seed",
    "slow parameters are not mutated during intra-episode steps",
    "prediction errors decrease during settling",
}


def _has_deterministic_invariant(spec) -> bool:
    return any(
        "deterministic under fixed seed" in inv.lower() for inv in spec.invariants
    )


def _has_finite_invariant(spec) -> bool:
    return any(
        any(kw in inv.lower() for kw in ["finite", "bounded", "remains"])
        for inv in spec.invariants
    )


def _generate_test_file(
    spec, output_dir: pathlib.Path, dry_run: bool = False
) -> pathlib.Path | None:
    """Generate a property test file for a spec."""

    # Skip geometry and substrate primitives - they have different interfaces
    if spec.axis in {"geometry", "substrate"}:
        return None

    safe_id = spec.id.replace(".", "_").replace("-", "_")
    output_path = output_dir / f"test_{safe_id}_invariants.py"

    # Determine which tests to generate
    has_deterministic = _has_deterministic_invariant(spec)
    has_finite = _has_finite_invariant(spec)

    if not has_deterministic and not has_finite:
        return None

    lines = [
        '"""Property tests for invariants of ' + spec.id + '."""',
        "",
        "# Generated by scripts/generate_property_tests.py",
        "# Do not edit manually.",
        "",
        "import hypothesis",
        "import hypothesis.strategies as st",
        "import pytest",
        "import torch",
        "",
        "",
        "from computronium.acceleration.registry import get",
        "",
        "",
        f"SPEC_ID = {spec.id!r}",
        "",
        "",
        '@pytest.fixture(scope="module")',
        "def spec():",
        f"    return get({spec.id!r})",
        "",
    ]

    if has_deterministic:
        lines.extend([
            "",
            "@hypothesis.given(st.integers(min_value=0, max_value=1000))",
            "@hypothesis.settings(max_examples=10, deadline=None)",
            "def test_deterministic_under_fixed_seed(spec, seed):",
            '    """Test that implementation is deterministic under fixed seed."""',
            f"    from {spec.reference_entrypoint.rsplit('.', 2)[0]}.cases import make_case",
            "    from importlib import import_module",
            "    from computronium.acceleration.parity import compare",
            "",
            "    case1 = make_case(seed=seed)",
            "    case2 = make_case(seed=seed)",
            "",
            f"    ref_module = import_module({spec.reference_entrypoint.rsplit('.', 1)[0]!r})",
            "    out1 = ref_module.step(case1)",
            "    out2 = ref_module.step(case2)",
            "",
            "    # Use the existing compare function which handles CompositeState, dicts, etc.",
            "    metrics = compare(out1, out2)",
            "    assert metrics['max_abs_diff'] == 0.0, f'Outputs differ for seed {seed}: {metrics}'",
            "",
        ])

    if has_finite:
        lines.extend([
            "",
            "@hypothesis.given(st.integers(min_value=0, max_value=1000))",
            "@hypothesis.settings(max_examples=10, deadline=None)",
            "def test_state_remains_finite(spec, seed):",
            '    """Test that all outputs remain finite (no NaN/Inf)."""',
            f"    from {spec.reference_entrypoint.rsplit('.', 2)[0]}.cases import make_case",
            "    from importlib import import_module",
            "",
            "    case = make_case(seed=seed)",
            "",
            f"    ref_module = import_module({spec.reference_entrypoint.rsplit('.', 1)[0]!r})",
            "    out = ref_module.step(case)",
            "",
            "    def _check_finite(x, path='output'):",
            "        if isinstance(x, torch.Tensor):",
            "            assert not torch.isnan(x).any(), f'NaN found in {path}'",
            "            assert not torch.isinf(x).any(), f'Inf found in {path}'",
            "        elif isinstance(x, dict):",
            "            for k, v in x.items():",
            "                _check_finite(v, f'{path}.{k}')",
            "        elif isinstance(x, (list, tuple)):",
            "            for i, v in enumerate(x):",
            "                _check_finite(v, f'{path}[{i}]')",
            "        # Handle CompositeState and similar objects with __dict__",
            "        elif hasattr(x, '__dict__') and not isinstance(x, type):",
            "            for k, v in x.__dict__.items():",
            "                if not k.startswith('_'):",
            "                    _check_finite(v, f'{path}.{k}')",
            "",
            "    _check_finite(out)",
            "",
        ])

    content = "\n".join(lines)
    if not dry_run:
        output_path.write_text(content, encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate property tests from invariants"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate tests for all specs with relevant invariants",
    )
    parser.add_argument(
        "--output",
        default="tests/property/generated",
        help="Output directory (default: tests/property/generated)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print files that would be generated without writing",
    )
    args = parser.parse_args()

    output_dir = pathlib.Path(args.output)
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    specs = list(all_specs())
    generated = 0

    for spec in specs:
        if _has_deterministic_invariant(spec) or _has_finite_invariant(spec):
            result = _generate_test_file(spec, output_dir, args.dry_run)
            if result:
                print(f"Generated: {result}")
                generated += 1

    print(f"\nTotal generated: {generated} test files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
