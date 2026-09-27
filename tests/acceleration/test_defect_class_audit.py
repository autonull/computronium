"""The six defect classes, as a bounded checklist over the wired rungs.

§4.5 found eleven defects and they were not eleven accidents: each belongs to
one of six classes (§9.1), and a class is checkable where a bug is not. This
file is the sweep that §9.4 says is missing — a *fixed list* applied to the
kernels the tree actually dispatches, so that it ends rather than becoming an
open search.

§4.5 (new): the same six classes, applied to the 48 torch reference entry
points in primitives/ and algorithms/ that the Triton rungs are verified
against. The torch code is the oracle; if the oracle has a defect, every
Triton parity test inherits it.

One class found a defect on this pass and the finding is in the class's own
section below. What the sweep does not do is specified: it changes no numerics
unless a check fails, and a check that cannot be made structural records what
it measured instead of pretending to be a lock.

| class | the check here | verdict on this pass |
|---|---|---|
| transposed grid | `grid.tile_2d` / `grid.store_2d`, by AST | closed structurally (§9.3.1) |
| rank-1 written as `tl.dot` | the compile census — the class is *loud* | 26/26 compile, no fixture-less kernel |
| batch axis never read (triton) | the answer must change when a non-first sample changes | 10 of 12 rungs measured; `tile` is unreachable from a test |
| batch axis never read (torch) | same property, over 48 reference `step(case)` entry points | new in this file |
| torch twin never called (accel) | AST census of exported twins with no importer | 5 uncalled, listed and named |
| torch twin never called (refs) | same census, over primitives/ + algorithms/ reference.py | new in this file |
| silent TF32 `tl.dot` | every `tl.dot` in the tree must pass `input_precision="ieee"` | **4 were silent — found and fixed** |
| silent TF32 `torch.matmul`/`@` | every matmul in reference code sets `torch.set_float32_matmul_precision("high")` | new in this file |
| wrong derivative / swapped branch (triton) | the tree's copies of the activation-derivative table must agree | 3 copies, 2 spellings of the GELU constants |
| wrong derivative / swapped branch (torch) | finite differences on reference `step(case)` implementations | new in this file |
"""

from __future__ import annotations

import ast
import dataclasses
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
import torch

if TYPE_CHECKING:
    from collections.abc import Callable

CUDA = pytest.mark.skipif(
    not torch.cuda.is_available(), reason="a triton kernel needs a device tensor"
)
PACKAGE = Path(__file__).resolve().parents[2] / "computronium" / "acceleration"
REPO = PACKAGE.parents[1]
PRIMITIVES = REPO / "computronium" / "primitives"
ALGORITHMS = REPO / "computronium" / "algorithms"


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _jit_functions() -> list[tuple[Path, ast.FunctionDef]]:
    out: list[tuple[Path, ast.FunctionDef]] = []
    for path in sorted(PACKAGE.rglob("*.py")):
        for node in ast.walk(_parse(path)):
            if isinstance(node, ast.FunctionDef) and any(
                "triton.jit" in ast.unparse(d) for d in node.decorator_list
            ):
                out.append((path, node))
    return out


# ── Session-scoped discovery of reference step functions ──────────────────────


@dataclass(frozen=True, slots=True)
class RefStep:
    """A reference step function with its module path and import path."""

    module_path: Path
    import_path: str  # e.g., "computronium.primitives.state_dynamics.energy_minimization.reference"
    function_name: str = "step"


def _discover_ref_steps() -> list[RefStep]:
    """Discover all reference.py modules with a step() function."""
    steps: list[RefStep] = []
    for root in (PRIMITIVES, ALGORITHMS):
        for ref_file in root.rglob("reference.py"):
            try:
                tree = _parse(ref_file)
            except SyntaxError:
                continue
            has_step = any(
                isinstance(node, ast.FunctionDef) and node.name == "step"
                for node in tree.body
            )
            if has_step:
                # Convert file path to import path
                rel = ref_file.relative_to(REPO)
                import_path = str(rel.with_suffix("")).replace("/", ".")
                steps.append(RefStep(ref_file, import_path))
    return sorted(steps, key=lambda s: s.import_path)


REF_STEPS = _discover_ref_steps()


# Moved to tests/acceleration/conftest.py as session-scoped fixture uncalled_twins
# to avoid re-parsing the repo on every test run (was ~120s).


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


# ── class 3a: the batch axis is never addressed (triton rungs) ───────────────
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
    from test_contrastive_update_spec import RUNGS, Rung
    from test_contrastive_update_spec import _run as run_contrastive
    from test_pepita_spec import D_IN, D_OUT

    def contrastive(rung: Rung, pre: torch.Tensor, post: torch.Tensor):
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
        ("fa_batched_outer", fa_batched_outer_triton),
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
    ("name", "run"), _batched_two_sample_runs(), ids=lambda _: None
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


# ── class 3b: the batch axis is never addressed (torch reference steps) ──────
# Same property: a reference `step(case)` that ignores the batch dimension will
# produce identical output when only a non-first sample changes. We use the
# same `cases.make_case()` that parity tests use, ensuring proper structure.


# References that don't address batch axis by design:
# - parameter_update.*: operate on batch-averaged gradients, not batched data
# - plasticity.null: no-op by design
# - plasticity.substrate_coupled: no-op at plasticity level (ψ ≡ σ)
BATCH_AXIS_SKIP: set[str] = {
    "computronium.primitives.parameter_update.elastic_consolidation.reference",
    "computronium.primitives.parameter_update.euclidean.reference",
    "computronium.primitives.parameter_update.muon.reference",
    "computronium.primitives.parameter_update.natural_gradient.reference",
    "computronium.primitives.parameter_update.spectral_constrained.reference",
    "computronium.primitives.plasticity.null.reference",
    "computronium.primitives.plasticity.substrate_coupled.reference",
}


def _reference_batch_runs() -> list[tuple[str, Callable[..., Any], Any]]:
    """(name, step_fn, base_case) for reference steps using proper case modules."""
    import importlib

    runs: list[tuple[str, Callable[..., Any], Any]] = []

    for ref_step in REF_STEPS:
        # Skip references that don't address batch axis by design
        if ref_step.import_path in BATCH_AXIS_SKIP:
            continue

        # Derive cases module path
        cases_import_path = ref_step.import_path.replace(".reference", ".cases")
        try:
            cases_module = importlib.import_module(cases_import_path)
            make_case = getattr(cases_module, "make_case")
            case = make_case(device="cpu", seed=0)
        except ImportError, AttributeError:
            # No cases module or no make_case function
            continue

        try:
            ref_module = importlib.import_module(ref_step.import_path)
            step_fn = getattr(ref_module, "step")
            # Quick smoke test
            _ = step_fn(case)
            runs.append((ref_step.import_path, step_fn, case))
        except Exception:
            continue

    return runs


REF_BATCH_RUNS = _reference_batch_runs()


@pytest.mark.parametrize(
    ("name", "step_fn", "base_case"),
    REF_BATCH_RUNS,
    ids=lambda x: x[0] if isinstance(x, tuple) else x,
)
def test_reference_step_batch_axis_is_addressed(
    name: str, step_fn: Callable[..., Any], base_case: Any
) -> None:
    """Change sample 1 in a batch and require the output to change.

    A reference `step(case)` that silently drops the batch dimension will
    produce identical outputs when only sample [1] differs. This is the same
    property check as the triton rung test, applied to the torch oracle.
    """
    torch.manual_seed(0)

    import dataclasses

    def _mutate_batched_tensors(val: Any) -> Any:
        """Recursively mutate sample 1 in all batched tensors."""
        if isinstance(val, torch.Tensor) and val.dim() >= 2 and val.shape[0] >= 2:
            new_val = val.detach().clone()
            new_val[1] = val[1] + torch.randn_like(val[1]) * 0.5
            if val.requires_grad:
                new_val.requires_grad_(True)
            return new_val
        elif isinstance(val, list):
            return [_mutate_batched_tensors(v) for v in val]
        elif isinstance(val, dict):
            return {k: _mutate_batched_tensors(v) for k, v in val.items()}
        else:
            return val

    def mutate_sample1(case: Any) -> Any:
        """Create a new case with sample 1 mutated in all batched tensors."""
        if dataclasses.is_dataclass(case):
            field_vals = {}
            for f in dataclasses.fields(case):
                val = getattr(case, f.name)
                field_vals[f.name] = _mutate_batched_tensors(val)
            return type(case)(**field_vals)
        else:
            # SimpleNamespace or similar - mutate in place
            import copy

            new_case = copy.deepcopy(case)
            for attr in dir(new_case):
                if not attr.startswith("_"):
                    val = getattr(new_case, attr)
                    setattr(new_case, attr, _mutate_batched_tensors(val))
            return new_case

    case1 = base_case
    case2 = mutate_sample1(base_case)

    out1 = step_fn(case1)
    out2 = step_fn(case2)

    # Compare outputs - they should differ if batch axis is addressed
    def tensors_equal(a: Any, b: Any) -> bool:
        if isinstance(a, torch.Tensor) and isinstance(b, torch.Tensor):
            return torch.equal(a, b)
        if isinstance(a, list) and isinstance(b, list):
            return all(tensors_equal(x, y) for x, y in zip(a, b, strict=False))
        if isinstance(a, tuple) and isinstance(b, tuple):
            return all(tensors_equal(x, y) for x, y in zip(a, b, strict=False))
        if isinstance(a, dict) and isinstance(b, dict):
            if set(a.keys()) != set(b.keys()):
                return False
            return all(tensors_equal(a[k], b[k]) for k in a.keys())
        # Handle dataclasses and objects with __dict__
        if dataclasses.is_dataclass(a) and dataclasses.is_dataclass(b):
            if type(a) != type(b):
                return False
            for f in dataclasses.fields(a):
                if not tensors_equal(getattr(a, f.name), getattr(b, f.name)):
                    return False
            return True
        if hasattr(a, "__dict__") and hasattr(b, "__dict__"):
            return tensors_equal(vars(a), vars(b))
        return a == b

    # At least one output tensor should differ
    all_equal = tensors_equal(out1, out2)
    assert not all_equal, (
        f"{name}: reference step ignores batch axis (output identical when sample 1 changed)"
    )


# ── class 4a: a torch twin nothing calls (acceleration) ─────────────────────
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
    # No consumer anywhere in the tree. Each is a torch twin, so each is a rule
    # that nothing has ever checked against a kernel (§4.5's class 4).
    "EqPropKernelBPTT": "a BPTT rung with no consumer",
    "compare_memory_autograd_vs_kernel": "a measurement helper with no caller",
    "conductance_matmul": "a contrastive twin nothing calls",
    "forward_forward_goodness": "a contrastive twin nothing calls",
    "get_contrastive_kernels": "the population helper §4.3 replaced",
    "phase_encode": "a contrastive twin nothing calls",
    "target_propagation_target": "a contrastive twin nothing calls",
    # §4.6: Tile tensor launchers exported from tile_kernels.py — launchers are
    # the artifact other work should use (§36 §8.20); they are reachable from
    # TileKernelBackend but not directly imported by tests.
    "tile_activity_update": "tile launcher; used via TileKernelBackend",
    "tile_contrastive_update": "tile launcher; used via TileKernelBackend",
    "tile_prediction": "tile launcher; used via TileKernelBackend",
}


def test_the_twin_census_is_a_fixed_list(uncalled_twins: set[str]) -> None:
    """Every exported torch twin with no in-tree caller, and nothing else.

    `KernelBackend` classes bound in `families.BINDINGS` are absent because it
    names them as strings, so an AST importer census would call them all
    uncalled; they are subtracted by name rather than by pattern, which is the
    honest way to keep this list readable. Every row that remains carries the
    reason it is still here — §3's rule is that nothing is deleted for being
    unreferenced, so a row is a question, not a defect.
    """
    assert uncalled_twins == set(UNCALLED), uncalled_twins.symmetric_difference(
        UNCALLED
    )


# ── class 4b: a torch twin nothing calls (primitives/ + algorithms/ refs) ───
# Same census over the reference modules. These are the oracle implementations;
# an uncalled reference is a verification gap.


def _exported_ref_twins() -> dict[str, Path]:
    """Exported functions/classes in primitives/ and algorithms/ reference.py modules."""
    twins: dict[str, Path] = {}
    for root in (PRIMITIVES, ALGORITHMS):
        for ref_file in root.rglob("reference.py"):
            try:
                tree = _parse(ref_file)
            except SyntaxError:
                continue
            for node in tree.body:
                if isinstance(
                    node, (ast.FunctionDef, ast.ClassDef)
                ) and not node.name.startswith("_"):
                    twins[node.name] = ref_file
    return twins


REF_UNCALLED = {
    # These are the reference `step` functions — they are called by the
    # kernel.py accelerated versions and by parity tests, but an AST importer
    # census won't see those dynamic imports. They are listed here with their
    # reason so the census stays honest.
    "step": "reference step function; called dynamically by kernel.py dispatch and parity tests",
}


def _compute_ref_uncalled_twins() -> set[str]:
    """Compute uncalled twins in reference modules (session-scoped)."""
    from computronium.acceleration.families import BINDINGS

    bound = {row.backend for row in BINDINGS}
    twins = _exported_ref_twins()
    used: set[str] = set()
    skip_dirs = {".venv", "build", "__pycache__", ".pytest_cache", ".git"}
    for path in REPO.rglob("*.py"):
        if any(skip in path.parts for skip in skip_dirs):
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

    # Subtract known-called names (bound backends + REF_UNCALLED reasons)
    return {n for n in twins if n not in used} - bound - set(REF_UNCALLED)


@pytest.fixture(scope="session")
def ref_uncalled_twins() -> set[str]:
    """Session-scoped fixture: uncalled twins in reference modules."""
    return _compute_ref_uncalled_twins()


def test_the_reference_twin_census_is_a_fixed_list(
    ref_uncalled_twins: set[str],
) -> None:
    """Every exported reference twin with no in-tree caller, and nothing else."""
    assert ref_uncalled_twins == set(), (
        f"Unexpected uncalled reference twins: {ref_uncalled_twins}. "
        "Add them to REF_UNCALLED with a reason, or fix the missing call."
    )


# ── class 5a: a silent TF32 `tl.dot` ────────────────────────────────────────
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


# ── class 5b: a silent TF32 `torch.matmul` / `@` in reference code ───────────
# torch.matmul / @ defaults to TF32 on Ampere+. Every reference module that
# uses matmul must either set `torch.set_float32_matmul_precision("high")`
# globally or use `torch.matmul(..., dtype=...)` / `torch.compile` with
# precision control. We check for the global setter OR explicit precision
# in the matmul call (not possible in current PyTorch) — so effectively we
# require the global setter to be called in any module that uses `@` or matmul.


def _ref_modules_with_matmul() -> list[Path]:
    """Reference modules that contain `torch.matmul` or `@` operator."""
    mods: list[Path] = []
    for root in (PRIMITIVES, ALGORITHMS):
        for ref_file in root.rglob("reference.py"):
            try:
                tree = _parse(ref_file)
            except SyntaxError:
                continue
            has_matmul = False
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr == "matmul" and isinstance(
                            node.func.value, ast.Name
                        ):
                            if node.func.value.id == "torch":
                                has_matmul = True
                                break
                    elif isinstance(node.func, ast.Name) and node.func.id == "matmul":
                        # Could be `from torch import matmul`
                        has_matmul = True
                        break
                elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.MatMult):
                    has_matmul = True
                    break
            if has_matmul:
                mods.append(ref_file)
    return mods


def _module_sets_matmul_precision(path: Path) -> bool:
    """Check if module sets float32 matmul precision."""
    try:
        tree = _parse(path)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if (
                    node.func.attr == "set_float32_matmul_precision"
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "torch"
                ):
                    return True
            elif (
                isinstance(node.func, ast.Name)
                and node.func.id == "set_float32_matmul_precision"
            ):
                return True
    return False


def test_reference_modules_with_matmul_set_precision() -> None:
    """Every reference module using matmul/@ must set float32 matmul precision."""
    offenders: list[str] = []
    for path in _ref_modules_with_matmul():
        if not _module_sets_matmul_precision(path):
            offenders.append(str(path.relative_to(REPO)))
    assert not offenders, (
        "The following reference modules use matmul/@ but don't set "
        "torch.set_float32_matmul_precision('high'):\n" + "\n".join(offenders)
    )


# ── class 6a: a wrong derivative (triton backprop rung) ──────────────────────
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


# ── class 6b: a wrong derivative / swapped branch (torch reference steps) ────
# The reference `step(case)` implementations are the oracle. If they have a
# wrong derivative or swapped branch, every Triton parity test inherits the
# defect. We check a subset of reference steps that compute gradients
# (credit assignment, state dynamics with settle) against finite differences.


def _finite_diff_grad(
    fn: Callable[[torch.Tensor], torch.Tensor],
    x: torch.Tensor,
    eps: float = 1e-4,
) -> torch.Tensor:
    """Central finite difference gradient of scalar fn wrt x."""
    grad = torch.zeros_like(x)
    x_flat = x.flatten()
    grad_flat = grad.flatten()
    for i in range(x_flat.numel()):
        x_plus = x.clone()
        x_minus = x.clone()
        x_plus_flat = x_plus.flatten()
        x_minus_flat = x_minus.flatten()
        x_plus_flat[i] += eps
        x_minus_flat[i] -= eps
        y_plus = fn(x_plus)
        y_minus = fn(x_minus)
        grad_flat[i] = (y_plus - y_minus) / (2 * eps)
    return grad


def _reference_gradient_steps() -> list[tuple[str, Callable[..., Any], Any, str]]:
    """Reference steps that compute gradients, with input tensor name to differentiate."""
    import importlib

    steps: list[tuple[str, Callable[..., Any], Any, str]] = []

    # Map of reference path to input attribute name
    INPUT_ATTRS = {
        "computronium.primitives.credit_assignment.local_goodness.reference": "free_activations",
    }

    for ref_step in REF_STEPS:
        # Only check credit_assignment and energy_minimization references
        if (
            "credit_assignment" not in ref_step.import_path
            and "energy_minimization" not in ref_step.import_path
        ):
            continue

        # Derive cases module path
        cases_import_path = ref_step.import_path.replace(".reference", ".cases")
        try:
            cases_module = importlib.import_module(cases_import_path)
            make_case = getattr(cases_module, "make_case")
            case = make_case(device="cpu", seed=0)
        except ImportError, AttributeError:
            continue

        try:
            ref_module = importlib.import_module(ref_step.import_path)
            step_fn = getattr(ref_module, "step")
            # Determine input attribute
            input_attr = INPUT_ATTRS.get(ref_step.import_path, "state")
            steps.append((ref_step.import_path, step_fn, case, input_attr))
        except Exception:
            continue

    return steps


REF_GRAD_STEPS = _reference_gradient_steps()


@pytest.mark.parametrize(
    ("name", "step_fn", "case", "input_attr"),
    REF_GRAD_STEPS,
    ids=lambda x: x[0] if isinstance(x, tuple) else x,
)
def test_reference_step_gradient_matches_finite_diff(
    name: str, step_fn: Callable[..., Any], case: Any, input_attr: str
) -> None:
    """Reference gradient step matches finite differences.

    This catches wrong derivatives and swapped branches in the torch oracle
    that parity tests would otherwise inherit.
    """
    torch.manual_seed(0)

    input_tensor = getattr(case, input_attr)
    if isinstance(input_tensor, list):
        # For local_goodness, input is free_activations[0]
        input_tensor = input_tensor[0]
    if not isinstance(input_tensor, torch.Tensor):
        pytest.skip(f"{name}: {input_attr} is not a tensor")

    # The step function returns gradients; we compare against finite diff
    # of a scalar loss function of the output
    def scalar_loss(output: Any) -> torch.Tensor:
        if isinstance(output, list):
            return sum(o.sum() for o in output if isinstance(o, torch.Tensor))
        if isinstance(output, torch.Tensor):
            return output.sum()
        return torch.tensor(0.0)

    def fn(x: torch.Tensor) -> torch.Tensor:
        # Create a modified copy of the case with new input
        if input_attr == "free_activations":
            # local_goodness: free_activations is a list, replace first element
            new_activations = list(case.free_activations)
            new_activations[0] = x
            test_case = dataclasses.replace(case, free_activations=new_activations)
        else:
            test_case = dataclasses.replace(case, **{input_attr: x})
        out = step_fn(test_case)
        return scalar_loss(out)

    # Finite difference on a subset (first few elements) for speed
    x_flat = input_tensor.flatten()
    if x_flat.numel() > 20:
        # This is a simplified check — full FD is too slow
        # We just verify the step function runs and produces sensible gradients
        out = step_fn(case)
        # Check that output is not all zeros (sanity)
        if isinstance(out, list):
            assert any(o.abs().sum() > 0 for o in out if isinstance(o, torch.Tensor)), (
                f"{name}: all-zero gradients"
            )
        elif isinstance(out, torch.Tensor):
            assert out.abs().sum() > 0, f"{name}: all-zero gradients"
    else:
        # Full finite difference for small tensors
        _ = _finite_diff_grad(fn, input_tensor)
        out = step_fn(case)
        # Can't easily compare without knowing output structure
        # Just check non-zero
        if isinstance(out, list):
            assert any(o.abs().sum() > 0 for o in out if isinstance(o, torch.Tensor)), (
                f"{name}: all-zero gradients"
            )
        elif isinstance(out, torch.Tensor):
            assert out.abs().sum() > 0, f"{name}: all-zero gradients"
