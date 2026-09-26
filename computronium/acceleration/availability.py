"""One meaning for "the triton rung is available here, now".

Four names in this tree used to answer that question — ``kernel_available("triton")``
(a CUDA check), the ``HAS_TRITON_*`` flags (an import check), ``KERNEL_TECHNOLOGY``
(a string), and a spec's ``supported_backends`` (does a torch implementation exist) —
and none of them meant it. TODO36 §4.2 replaces them with one function whose answer
is measured: *the kernel imports and compiles*. Triton's ``.warmup()`` compiles
without launching, so this is a real compilation, not a presence check.

Three things live here, in this order:

1. :class:`KernelFixture` — a kernel plus the concrete arguments that make it
   compile. A ``@triton.jit`` function's shape constraints are semantic (equal
   reduction dimensions, ``K >= 8`` for ``tl.dot``), so fixtures are written by
   hand from each kernel's own signature. There is no way to synthesise them: a
   name-and-annotation-driven synthesiser was measured against this population and
   produced 13 false failures out of 18, because a wrong-but-well-typed argument
   is a compile error, not a no-op.
2. :func:`compile_state` / :func:`triton_rung_available` — the answer, cached per
   process because compilation is not free.
3. :func:`regressions` — the standing check. It compares the measured compile
   state of every fixture against ``triton_compile_baseline.json`` and reports a
   problem **only when a kernel that compiled stops compiling**. The kernels that
   do not compile are a recorded, named state, not a red gate (TODO36 §4.2: a
   check that is red on arrival is a check whose fastest fix is deletion, and
   TODO36 §3 exists to prevent exactly that).

:func:`discover_kernels` enumerates the whole module-level ``@triton.jit``
population so that a new kernel cannot join the family without either a fixture
(checked here) or a GPU test that compiles it.
"""

from __future__ import annotations

import argparse
import importlib
import json
from dataclasses import dataclass
from enum import StrEnum
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

import torch

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

__all__ = [
    "BASELINE_PATH",
    "CompileState",
    "KernelFixture",
    "KernelReport",
    "Regression",
    "compile_report",
    "compile_state",
    "discover_kernels",
    "main",
    "record_baseline",
    "regressions",
    "triton_rung_available",
    "triton_stack_available",
    "unfixtured_kernels",
]

BASELINE_PATH = Path(__file__).with_name("triton_compile_baseline.json")

#: The kernel :func:`triton_stack_available` compiles to answer the global
#: question. Chosen because it is in the baseline as ``compiles``.
_CANARY = "fa_kernels._fa_batched_outer_kernel"

#: Modules searched for module-level ``@triton.jit`` functions. The complex
#: substrate keeps its kernels outside ``acceleration/``, so it is named here.
_KERNEL_MODULES: tuple[str, ...] = (
    "computronium.acceleration.fa_kernels",
    "computronium.acceleration.ff_kernels",
    "computronium.acceleration.hebbian_kernels",
    "computronium.acceleration.pcalm_kernels",
    "computronium.acceleration.pc_kernels",
    "computronium.acceleration.snn_kernels",
    "computronium.acceleration.tile_kernels",
    "computronium.acceleration.tp_kernels",
    "computronium.acceleration.triton_kernels",
    "computronium.core.substrates.complex_substrate",
)

# Argument shapes for the fixtures. Small, aligned, and satisfying each kernel's
# own constraints; the values are the point of the fixture, not the throughput.
_B, _D, _D_IN, _D_OUT, _PRE, _POST, _T = 32, 48, 64, 48, 32, 32, 8


class CompileState(StrEnum):
    """What happened when a kernel was asked to compile."""

    COMPILES = "compiles"
    FAILS = "fails"
    NO_TRITON = "no_triton"


@dataclass(frozen=True, slots=True)
class KernelFixture:
    """A triton kernel and the arguments that make it compile.

    Attributes:
        family: the group the kernel serves — an
            :class:`~computronium.acceleration.kernel_backend.AlgorithmFamily`
            value, or a named kernel group such as ``complex_substrate``.
        name: ``module.kernel`` — the identity the baseline records.
        module: importable module path.
        attr: attribute holding the ``JITFunction``.
        args: positional arguments in signature order, built fresh per call
            (tensors must be live for the call).
    """

    family: str
    name: str
    module: str
    attr: str
    args: Callable[[], tuple[Any, ...]]


@dataclass(frozen=True, slots=True)
class KernelReport:
    """One kernel's measured compile state."""

    name: str
    family: str
    state: CompileState
    detail: str = ""


@dataclass(frozen=True, slots=True)
class Regression:
    """A kernel whose compile state is worse than the recorded baseline."""

    name: str
    was: CompileState
    now: CompileState
    detail: str = ""


def _t(*shape: int) -> Callable[[], torch.Tensor]:
    return lambda: torch.randn(*shape, device="cuda")


def _b(*shape: int) -> Callable[[], torch.Tensor]:
    return lambda: torch.randint(0, 2, shape, device="cuda", dtype=torch.float32)


def _o(*shape: int) -> Callable[[], torch.Tensor]:
    return lambda: torch.zeros(*shape, device="cuda")


def _args(*arg_specs: Any) -> Callable[[], tuple[Any, ...]]:
    """Bind an argument list, calling every builder so tensors are freshly live."""
    return lambda: tuple(spec() if callable(spec) else spec for spec in arg_specs)


def _fixture(
    family: str,
    module: str,
    attr: str,
    args: tuple[Any, ...],
) -> KernelFixture:
    """Bind a kernel to its argument builders, in signature order."""
    return KernelFixture(
        family=family,
        name=f"{module.rsplit('.', 1)[-1]}.{attr}",
        module=module,
        attr=attr,
        args=_args(*args),
    )


def _fixtures() -> tuple[KernelFixture, ...]:
    """Every kernel with a hand-written compile fixture.

    Two tiers, both listed here so the census is one read:

    * the **unwired** rungs of TODO36 §2 — no test in the tree reaches them, so a
      fixture is the only compile evidence they have;
    * the **wired** rungs of the two families a dispatch site actually asks
      about (``fa`` and ``pcalm``) — a fixture is what makes
      :func:`triton_rung_available` an answer rather than an assumption.

    Kernels a GPU test already compiles are not listed; a fixture for them would
    be a second, weaker copy of that test. :func:`unfixtured_kernels` closes the
    census so nothing escapes the count silently.
    """
    fa = "computronium.acceleration.fa_kernels"
    pc = "computronium.acceleration.pc_kernels"
    snn = "computronium.acceleration.snn_kernels"
    ff = "computronium.acceleration.ff_kernels"
    heb = "computronium.acceleration.hebbian_kernels"
    pcalm = "computronium.acceleration.pcalm_kernels"
    cplx = "computronium.core.substrates.complex_substrate"
    return (
        _fixture(
            "fa",
            fa,
            "_fa_batched_outer_kernel",
            (
                _t(_B, _D_IN),
                _t(_B, _D_OUT),
                _o(_D_OUT, _D_IN),
                _B,
                _D_IN,
                _D_OUT,
                16,
                16,
            ),
        ),
        _fixture(
            "fa",
            fa,
            "_fa_feedback_projection_kernel",
            (
                _t(_B, _D_OUT),
                _t(_D_IN, _D_OUT),
                _o(_B, _D_IN),
                _B,
                _D_IN,
                _D_OUT,
                16,
                16,
            ),
        ),
        _fixture(
            "pcalm",
            pcalm,
            "_FUSED_UPDATE_KERNEL",
            (
                _t(256),
                _t(256),
                _t(256),
                _t(256),
                _o(256),
                _o(256),
                0.1,
                1.0,
                0.5,
                256,
                64,
            ),
        ),
        _fixture(
            "pc",
            pc,
            "_pc_prediction_kernel",
            (
                _t(_B, _D_IN),
                _t(_D_OUT, _D_IN),
                _t(_D_OUT),
                _o(_B, _D_OUT),
                _B,
                _D_IN,
                _D_OUT,
                3,
                16,
                16,
            ),
        ),
        _fixture(
            "pc",
            pc,
            "_pc_error_update_kernel",
            (_t(_B, _D), _t(_B, _D), _o(_B, _D), 0.1, 3, _B, _D, 16, 16),
        ),
        _fixture(
            "pc",
            pc,
            "_pc_contrastive_update_kernel",
            (
                _t(_B, _D_OUT),
                _t(_B, _D_OUT),
                _t(_B, _D_OUT),
                _t(_B, _D_OUT),
                _o(_D_OUT, _D_IN),
                _B,
                _D_IN,
                _D_OUT,
                0.1,
                0.01,
                16,
                16,
            ),
        ),
        _fixture(
            "snn",
            snn,
            "_lif_step_kernel",
            (_t(_B, _D), _t(_B, _D), _o(_B, _D), 20.0, 5.0, 1.0, 0.01, _B, _D, 16, 16),
        ),
        _fixture(
            "snn",
            snn,
            "_stdp_update_kernel",
            (
                _b(_B, _PRE, _T),
                _b(_B, _POST, _T),
                _o(_POST, _PRE),
                _B,
                _PRE,
                _POST,
                _T,
                0.01,
                0.01,
                16,
                16,
                8,
            ),
        ),
        _fixture(
            "snn",
            snn,
            "_contrastive_stdp_kernel",
            (
                _b(_B, _PRE, _T),
                _b(_B, _POST, _T),
                _b(_B, _PRE, _T),
                _b(_B, _POST, _T),
                _o(_POST, _PRE),
                _B,
                _PRE,
                _POST,
                _T,
                0.01,
                0.01,
                1.0,
                16,
                16,
                8,
            ),
        ),
        _fixture(
            "ff",
            ff,
            "_ff_goodness_kernel",
            (_t(_B, _D), _t(_B, _D), _o(_B), 0.5, _B, _D, 16, 16),
        ),
        _fixture(
            "ff",
            ff,
            "_ff_contrastive_update_kernel",
            (
                _t(_B, _D_OUT),
                _t(_B, _D_OUT),
                _t(_B, _D_OUT),
                _t(_B, _D_OUT),
                _o(_D_OUT, _D_IN),
                _B,
                _D_IN,
                _D_OUT,
                0.01,
                16,
                16,
            ),
        ),
        _fixture(
            "pepita",
            ff,
            "_pepita_error_modulation_kernel",
            (
                _t(_B, _D_IN),
                _t(_B, _D_OUT),
                _o(_D_OUT, _D_IN),
                0.5,
                _B,
                _D_IN,
                _D_OUT,
                16,
                16,
            ),
        ),
        _fixture(
            "pepita",
            ff,
            "_pepita_contrastive_update_kernel",
            (
                _t(_B, _D_OUT),
                _t(_B, _D_OUT),
                _t(_B, _D_OUT),
                _t(_B, _D_OUT),
                _o(_D_OUT, _D_IN),
                _B,
                _D_IN,
                _D_OUT,
                0.01,
                16,
                16,
            ),
        ),
        _fixture(
            "hebbian",
            heb,
            "_hebbian_update_kernel",
            (
                _t(_B, _D_IN),
                _t(_B, _D_OUT),
                _t(_D_OUT, _D_IN),
                _o(_D_OUT, _D_IN),
                _B,
                _D_IN,
                _D_OUT,
                0.01,
                1,
                16,
                16,
            ),
        ),
        _fixture(
            "hebbian",
            heb,
            "_three_factor_hebbian_kernel",
            (
                _t(_B, _D_IN),
                _t(_B, _D_OUT),
                _t(_B, _D_OUT),
                _o(_D_OUT, _D_IN),
                _B,
                _D_IN,
                _D_OUT,
                0.01,
                16,
                16,
            ),
        ),
        _fixture(
            "hebbian",
            heb,
            "_contrastive_hebbian_kernel",
            (
                _t(_B, _D_IN),
                _t(_B, _D_OUT),
                _t(_B, _D_IN),
                _t(_B, _D_OUT),
                _o(_D_OUT, _D_IN),
                _B,
                _D_IN,
                _D_OUT,
                0.01,
                0.5,
                16,
                16,
            ),
        ),
        _fixture(
            "complex_substrate",
            cplx,
            "_complex_tanh_kernel",
            (_t(256), _t(256), _o(256), _o(256), 256, 64),
        ),
    )


@cache
def fixtures() -> tuple[KernelFixture, ...]:
    """The fixture table, built once; the argument builders are reusable."""
    return _fixtures()


def _cause(exc: BaseException) -> str:
    """The last non-empty line of an exception message — where triton puts the cause."""
    lines = [line for line in str(exc).splitlines() if line.strip()]
    return lines[-1] if lines else str(exc)


def _triton() -> Any | None:
    try:
        import triton
    except ImportError:
        return None
    return triton


_STATE_CACHE: dict[str, KernelReport] = {}


def compile_state(fixture: KernelFixture) -> KernelReport:
    """Compile one kernel and report what happened. Cached per process."""
    if (cached := _STATE_CACHE.get(fixture.name)) is not None:
        return cached

    triton = _triton()
    if triton is None or not torch.cuda.is_available():
        report = KernelReport(fixture.name, fixture.family, CompileState.NO_TRITON)
    else:
        try:
            kernel = getattr(importlib.import_module(fixture.module), fixture.attr)
        except (ImportError, AttributeError) as exc:
            report = KernelReport(
                fixture.name,
                fixture.family,
                CompileState.FAILS,
                f"{type(exc).__name__}: {exc}",
            )
        else:
            try:
                kernel.warmup(*fixture.args(), grid=(1,))
            except Exception as exc:  # ruff: ignore[blind-except]  (any failure is a result)
                report = KernelReport(
                    fixture.name,
                    fixture.family,
                    CompileState.FAILS,
                    f"{type(exc).__name__}: {_cause(exc)[:120]}",
                )
            else:
                report = KernelReport(
                    fixture.name, fixture.family, CompileState.COMPILES
                )

    _STATE_CACHE[fixture.name] = report
    return report


def compile_report() -> tuple[KernelReport, ...]:
    """Every fixture's compile state, in table order."""
    return tuple(compile_state(fixture) for fixture in fixtures())


def triton_stack_available() -> bool:
    """Whether triton can compile anything at all on this box.

    The strongest honest *global* claim: a known-good kernel — one that compiles
    in the recorded baseline — is compiled here, now. A triton import and a CUDA
    device are necessary and not sufficient; this is the check that says so, and
    it is what ``kernel_available("triton")`` now reports.
    """
    canary = next((f for f in fixtures() if f.name == _CANARY), None)
    if canary is None or _triton() is None or not torch.cuda.is_available():
        return False
    return compile_state(canary).state is CompileState.COMPILES


def triton_rung_available(family: str) -> bool:
    """Whether the triton rung for ``family`` can run here, now.

    The answer is measured: the family's fixture kernels must import and compile.
    A family with no fixtures has nothing to compile, so the answer degrades to
    "triton imports and a driver is active" — stated here rather than implied,
    because that fallback is the weaker claim this function exists to replace.

    Args:
        family: an :class:`~computronium.acceleration.kernel_backend.AlgorithmFamily`
            value, as a string.

    Returns:
        ``True`` when the triton rung is usable on this box.
    """
    triton = _triton()
    if triton is None or not torch.cuda.is_available():
        return False
    family_reports = [r for r in compile_report() if r.family == family]
    if not family_reports:
        return True
    return all(r.state is CompileState.COMPILES for r in family_reports)


def discover_kernels() -> tuple[str, ...]:
    """Every module-level ``@triton.jit`` in the acceleration package.

    Kernels defined inside a function body (the classes that build their kernels
    lazily) are not module-level and are not enumerated; the GPU tests are their
    evidence.
    """
    triton = _triton()
    if triton is None:
        return ()
    found: list[str] = []
    for module_name in _KERNEL_MODULES:
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            continue
        for attr, obj in vars(module).items():
            if isinstance(obj, triton.runtime.jit.JITFunction):
                found.append(f"{module_name.rsplit('.', 1)[-1]}.{attr}")
    return tuple(sorted(found))


def unfixtured_kernels() -> tuple[str, ...]:
    """Discovered kernels with no compile fixture and so no compile evidence here."""
    known = {fixture.name for fixture in fixtures()}
    return tuple(name for name in discover_kernels() if name not in known)


def _baseline() -> dict[str, str]:
    if not BASELINE_PATH.exists():
        return {}
    return {
        str(name): str(state)
        for name, state in json.loads(BASELINE_PATH.read_text(encoding="utf-8")).items()
    }


def record_baseline(path: Path = BASELINE_PATH) -> dict[str, str]:
    """Measure every fixture and write the baseline. Returns what was written."""
    baseline = {report.name: report.state.value for report in compile_report()}
    path.write_text(
        json.dumps(baseline, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return baseline


def regressions() -> tuple[Regression, ...]:
    """Kernels whose compile state is worse than the recorded baseline.

    A kernel that newly compiles is progress, not a regression, and is not
    reported. A kernel with no baseline entry is new, and is not a regression
    either — recording it is ``record_baseline``'s job.
    """
    baseline = _baseline()
    found: list[Regression] = []
    for report in compile_report():
        was = baseline.get(report.name)
        if was is None or was == report.state.value:
            continue
        if was == CompileState.FAILS.value and report.state is CompileState.COMPILES:
            continue
        found.append(
            Regression(report.name, CompileState(was), report.state, report.detail)
        )
    return tuple(found)


def _render(reports: Sequence[KernelReport]) -> str:
    width = max((len(r.name) for r in reports), default=4)
    lines = [
        f"{r.name:{width}}  {r.family:8} {r.state.value:9} {r.detail}" for r in reports
    ]
    counts = {
        state: sum(1 for r in reports if r.state is state) for state in CompileState
    }
    lines.append(
        f"{sum(1 for r in reports if r.state is CompileState.COMPILES)}/{len(reports)} compile"
        f"  ({', '.join(f'{n} {state.value}' for state, n in counts.items() if n)})"
    )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    """Report the triton compile state, or check it against the baseline.

    Returns:
        ``1`` when a kernel regressed, else ``0``.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="fail on a regression")
    group.add_argument(
        "--record", action="store_true", help="rewrite the baseline from measurement"
    )
    parser.add_argument("--families", nargs="*", default=None)
    args = parser.parse_args(argv)

    if args.record:
        baseline = record_baseline()
        print(f"recorded {len(baseline)} kernels -> {BASELINE_PATH}")  # ruff: ignore[print]
        return 0

    reports = [
        r for r in compile_report() if not args.families or r.family in args.families
    ]
    print(_render(reports))  # ruff: ignore[print]

    if not args.check:
        return 0
    found = regressions()
    for regression in found:
        print(  # ruff: ignore[print]
            f"REGRESSION {regression.name}: {regression.was.value} -> "
            f"{regression.now.value} {regression.detail}"
        )
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
