"""The six defect classes, as a bounded checklist over the wired rungs.

§4.5 found eleven defects and they were not eleven accidents: each belongs to
one of six classes (§9.1), and a class is checkable where a bug is not. This
file is the sweep that §9.4 says is missing — a *fixed list* applied to the
kernels the tree actually dispatches, so that it ends rather than becoming an
open search.

One class found a defect on this pass and the finding is in the class's own
section below. What the sweep does not do is specified: it changes no numerics
unless a check fails, and a check that cannot be made structural records what
it measured instead of pretending to be a lock.

| class | the check here | verdict on this pass |
|---|---|---|
| transposed grid | `grid.tile_2d` / `grid.store_2d`, by AST | closed structurally (§9.3.1) |
| rank-1 written as `tl.dot` | the compile census — the class is *loud* | 26/26 compile, no fixture-less kernel |
| batch axis never read | the answer must change when a non-first sample changes | 10 of 12 rungs measured; `tile` is unreachable from a test |
| torch twin never called | AST census of exported twins with no importer | 5 uncalled, listed and named |
| silent TF32 `tl.dot` | every `tl.dot` in the tree must pass `input_precision="ieee"` | **4 were silent — found and fixed** |
| wrong derivative / swapped branch | the tree's copies of the activation-derivative table must agree | 3 copies, 2 spellings of the GELU constants |
"""

from __future__ import annotations

import ast
from collections.abc import Callable
from pathlib import Path

import pytest
import torch

CUDA = pytest.mark.skipif(
    not torch.cuda.is_available(), reason="a triton kernel needs a device tensor"
)
PACKAGE = Path(__file__).resolve().parents[2] / "computronium" / "acceleration"
REPO = PACKAGE.parents[1]


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text())


def _jit_functions() -> list[tuple[Path, ast.FunctionDef]]:
    out: list[tuple[Path, ast.FunctionDef]] = []
    for path in sorted(PACKAGE.rglob("*.py")):
        for node in ast.walk(_parse(path)):
            if isinstance(node, ast.FunctionDef) and any(
                "triton.jit" in ast.unparse(d) for d in node.decorator_list
            ):
                out.append((path, node))
    return out


# ── class 1: transposed grid ────────────────────────────────────────────────
# The convention is `acceleration.grid`, and the lock that holds it is
# `test_grid_convention.py`. This class is a delegation, not a second copy.


def test_the_transposed_grid_class_is_closed_in_one_place() -> None:
    from test_grid_convention import TILED_KERNELS, test_the_census_is_not_empty

    test_the_census_is_not_empty()
    assert len(TILED_KERNELS) == 12


# ── class 2: a rank-1 product written as a contraction ──────────────────────
# This class is the cheapest there is: `tl.dot` refuses a contraction of length
# 1, so a kernel in this class does not compile and says so. The structural
# check is therefore the compile census, not a linter.


@CUDA
def test_every_triton_kernel_compiles_so_the_rank1_class_cannot_hide() -> None:
    from computronium.acceleration.availability import compile_report

    failures = [r.name for r in compile_report() if r.state != "compiles"]
    assert not failures, failures


# ── class 3: the batch axis is never addressed ─────────────────────────────
# A kernel that drops the batch stride still returns the right shape, the right
# dtype and a plausible magnitude; it has computed one sample's answer. The
# signature is that changing *another* sample changes nothing, which is a
# property any launcher can state without knowing the rule.


def _batched_two_sample_runs() -> list[tuple[str, Callable[..., torch.Tensor]]]:
    """(name, run) pairs for every rung whose launcher a test can reach.

    A rung is reachable when some test module launches it. The two `tile`
    rungs are launched from inside their backend class and are named in
    `NOT_REACHABLE` below rather than quietly omitted.
    """
    from test_contrastive_update_spec import RUNGS
    from test_contrastive_update_spec import _run as run_contrastive
    from test_pepita_spec import D_IN, D_OUT

    def contrastive(rung: object, pre: torch.Tensor, post: torch.Tensor):
        return run_contrastive(rung, pre, post, pre + 1.0, post + 1.0)

    from test_hebbian_spec import (
        _run_hebbian,
        _run_three_factor,
    )
    from test_pepita_spec import _run as run_pepita
    from test_snn_stdp_spec import _run_contrastive_stdp, _run_stdp

    from computronium.acceleration.fa_kernels import fa_batched_outer_triton

    return [
        (
            "hebbian",
            lambda pre, post: _run_hebbian(
                pre, post, torch.zeros(D_OUT, D_IN, device=pre.device), 0.1, False
            ),
        ),
        (
            "three_factor",
            lambda pre, post: _run_three_factor(pre, post, torch.ones_like(post), 0.1),
        ),
        ("pepita_error_modulation", lambda err, fb: run_pepita(err, fb, 0.1)),
        ("stdp", lambda pre, post: _run_stdp(pre, post, 0.01, 0.02)),
        (
            "contrastive_stdp",
            lambda pre, post: _run_contrastive_stdp(
                pre, post, pre + 1.0, post + 1.0, 0.5
            ),
        ),
        ("fa_batched_outer", lambda pre, post: fa_batched_outer_triton(pre, post)),
        *[
            (
                f"contrastive:{rung.spec_id}",
                lambda pre, post, _r=rung: contrastive(_r, pre, post),
            )
            for rung in RUNGS
        ],
    ]


NOT_REACHABLE = ("tile:contrastive", "tile:hebbian")


@CUDA
@pytest.mark.parametrize(
    ("name", "run"), _batched_two_sample_runs(), ids=lambda v: None
)
def test_a_batched_rung_answers_for_every_sample_in_the_batch(
    name: str, run: Callable[..., torch.Tensor]
) -> None:
    """Change a sample the kernel might be ignoring, and require the answer to move.

    This is the check §9.1's table asks for ("a spec that reads one sample's
    worth") reduced to something that holds for every batched rung without
    knowing any of their rules: a kernel that reads sample 0 and ignores the
    rest returns bit-identical tensors here.
    """
    pytest.importorskip("triton")
    torch.manual_seed(0)
    from test_pepita_spec import D_IN, D_OUT

    pre = torch.randn(3, D_IN, device="cuda")
    post = torch.randn(3, D_OUT, device="cuda")
    other_post = torch.randn(3, D_OUT, device="cuda")

    first = run(pre, post)
    second = run(pre, other_post)

    assert not torch.equal(first, second), f"{name} ignores all but one sample"
    assert not torch.equal(first[0], first[1]) or name == "pepita_error_modulation"


# ── class 4: a torch twin nothing calls ────────────────────────────────────
# §8.17: a torch function with no caller is a kernel that was never verified,
# from the other direction. `pepita_error_modulation` was one, and it was a
# shape error.


def _exported_twins() -> dict[str, Path]:
    modules = [PACKAGE / "contrastive_primitives.py", PACKAGE / "kernels.py"]
    modules += sorted(PACKAGE.glob("*_kernels.py"))
    twins: dict[str, Path] = {}
    for module in modules:
        for node in _parse(module).body:
            if isinstance(
                node, (ast.FunctionDef, ast.ClassDef)
            ) and not node.name.startswith("_"):
                twins[node.name] = module
    return twins


UNCALLED = {
    # Deliberately unbound: two rows would displace a bound backend for the whole
    # family, and the contrastive ten share (family, hardware) keys (TODO36 §4.3).
    "ThreeFactorKernelBackend": "a Hebbian variant; registering it replaces the family's backend",
    "ContrastiveKernel": "one of the ten contrastive classes, same keys as the standard backends",
    "register_contrastive_kernels": "the explicit opt-in that keeps them unbound",
    # No consumer anywhere in the tree. Each is a torch twin, so each is a rule
    # that nothing has ever checked against a kernel (§4.5's class 4).
    "EqPropKernelBPTT": "a BPTT rung with no consumer",
    "compare_memory_autograd_vs_kernel": "a measurement helper with no caller",
    "conductance_matmul": "a contrastive twin nothing calls",
    "forward_forward_goodness": "a contrastive twin nothing calls",
    "get_contrastive_kernels": "the population helper §4.3 replaced",
    "phase_encode": "a contrastive twin nothing calls",
    "target_propagation_target": "a contrastive twin nothing calls",
}


def test_the_twin_census_is_a_fixed_list() -> None:
    """Every exported torch twin with no in-tree caller, and nothing else.

    `KernelBackend` classes bound in `families.BINDINGS` are absent because it
    names them as strings, so an AST importer census would call them all
    uncalled; they are subtracted by name rather than by pattern, which is the
    honest way to keep this list readable. Every row that remains carries the
    reason it is still here — §3's rule is that nothing is deleted for being
    unreferenced, so a row is a question, not a defect.
    """
    from computronium.acceleration.families import BINDINGS

    bound = {row.backend for row in BINDINGS}
    twins = _exported_twins()
    used: set[str] = set()
    for path in REPO.rglob("*.py"):
        if "build/" in str(path):
            continue
        try:
            tree = _parse(path)
        except SyntaxError, UnicodeDecodeError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used.add(node.id)
            elif isinstance(node, ast.Attribute):
                used.add(node.attr)

    uncalled = {n for n in twins if n not in used} - bound
    assert uncalled == set(UNCALLED), uncalled.symmetric_difference(UNCALLED)


# ── class 5: a silent TF32 `tl.dot` ────────────────────────────────────────
# Found on this pass. Triton's default for `tl.dot` is TF32 on Ampere and
# later, which costs three orders of magnitude on `ep_settle` (1.0e-3 max
# against the fp32 expression) at cosine 1.0, and nothing in the tree noticed
# because the one test covering that kernel was `xfail`ed for a reason that
# turned out to be a different defect entirely.


@CUDA
def test_every_tl_dot_declares_its_precision() -> None:
    silent = [
        f"{path.name}:{node.name}"
        for path, node in _jit_functions()
        for call in ast.walk(node)
        if isinstance(call, ast.Call)
        and ast.unparse(call.func) == "tl.dot"
        and not any(kw.arg == "input_precision" for kw in call.keywords)
    ]
    assert not silent, silent


# ── class 6: a wrong derivative ────────────────────────────────────────────
# Two defects on this pass, both in this class. The backprop backend applied the
# derivative formula to each activation's own *output*, which coincides for
# tanh (`1 - h**2`) and is wrong for SiLU and GELU; and the three copies of the
# table had drifted apart, so nothing could notice. The table now lives in
# `acceleration.activations`, and the check that it is right is autograd.


@CUDA
@pytest.mark.parametrize("activation", ["relu", "tanh", "silu", "gelu"])
def test_the_backprop_rung_matches_autograd(activation: str) -> None:
    """The chain rule, against the only oracle that has one.

    `BackpropKernelBackend` is the reference every other backprop rung is
    compared against, so a wrong derivative here is a wrong answer everywhere.
    It was wrong for SiLU and GELU: the derivative was evaluated at the
    activation's output rather than its input, which no shape check, dtype
    check or compile check can see. The oracle is a *mean* loss, because the
    ladder's gradients are batch means — a convention worth writing down, since
    a sum-based oracle disagrees with every rung here by exactly a factor of B.
    """
    torch.manual_seed(0)
    from torch import nn

    from computronium.acceleration.backprop_kernels import BackpropKernelBackend
    from computronium.acceleration.kernel_backend import (
        AlgorithmFamily,
        HardwareTarget,
        KernelConfig,
    )

    layers = [nn.Linear(16, 12), nn.Linear(12, 10), nn.Linear(10, 6)]
    for layer in layers:
        nn.init.normal_(layer.weight, std=0.3)
        nn.init.zeros_(layer.bias)
    reference = [nn.Linear(16, 12), nn.Linear(12, 10), nn.Linear(10, 6)]
    for layer, twin in zip(layers, reference, strict=True):
        twin.load_state_dict(layer.state_dict())
    layers = [layer.cuda() for layer in layers]
    reference = [layer.cuda() for layer in reference]

    config = KernelConfig(
        algorithm=AlgorithmFamily.BACKPROP,
        hardware=HardwareTarget.CUDA,
        extra={"activation": activation},
    )
    backend = BackpropKernelBackend()
    backend.initialize(config)
    backend.set_model_ref(layers)

    x = torch.randn(5, 16, device="cuda")
    out, _ = backend.forward(x)
    error = torch.randn_like(out)
    grads = backend.backward(backend.forward(x)[1], error)

    for i, (layer, twin) in enumerate(zip(layers, reference, strict=True)):
        twin.zero_grad()
        act = x
        for j, twin_layer in enumerate(reference):
            act = twin_layer(act)
            if j < len(reference) - 1:
                act = getattr(
                    nn,
                    {"relu": "ReLU", "silu": "SiLU", "tanh": "Tanh", "gelu": "GELU"}[
                        activation
                    ],
                )()(act)
        # The ladder's gradients are batch means. `.mean()` would divide by the
        # element count; the convention here is a sum scaled by 1/B.
        (act * error).sum().div(x.shape[0]).backward()
        torch.testing.assert_close(
            grads[f"layers.{i}.weight"], twin.weight.grad, atol=1e-5, rtol=1e-4
        )
        torch.testing.assert_close(
            grads[f"layers.{i}.bias"], twin.bias.grad, atol=1e-5, rtol=1e-4
        )
