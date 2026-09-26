"""Rung Benchmark: measure each rung of the acceleration ladder against the rung below it.

Every rung a spec declares is a claim about speed. This module times the claim on
the box it runs on, at three input sizes, and writes the result beside the rung
below it so the two can be read as a pair (TODO36 §4.1).

A row records the *rung* (``rung``/``backend``: ``reference``, ``kernel``) and
the rung's *technology* (``technology``: ``torch``, ``torch_compile``, ``triton``)
separately, because the two are different facts and the existing
``artifacts/benchmarks`` schema is keyed on the first.

Nothing here deletes or demotes a rung. A rung that loses is a ranked rung.
"""

from __future__ import annotations

import argparse
import importlib
import json
import pathlib
import subprocess  # ruff: ignore[suspicious-subprocess-import]
import time
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, fields, is_dataclass
from typing import Any

import torch

__all__ = ["Rung", "RungSite", "main", "measure", "rung_sites"]

DEFAULT_SCALES: tuple[int, ...] = (1, 8, 32)
OUTPUT_DIR = pathlib.Path("artifacts/benchmarks/rungs")

type Case = Any
type Step = Callable[[Case], object]

#: Packages whose ``kernel`` module reaches a triton or compiled rung. Each entry
#: is (spec id, package) and is the unit §1.2 counted as a "triton call site".
_RUNG_PACKAGES: tuple[tuple[str, str], ...] = (
    ("algorithm.pcalm", "computronium.algorithms.pcalm"),
    (
        "primitive.credit_assignment.local_goodness",
        "computronium.primitives.credit_assignment.local_goodness",
    ),
    (
        "primitive.credit_assignment.random_projections",
        "computronium.primitives.credit_assignment.random_projections",
    ),
    ("primitive.geometry.tile_mesh", "computronium.primitives.geometry.tile_mesh"),
    (
        "primitive.state_dynamics.energy_minimization",
        "computronium.primitives.state_dynamics.energy_minimization",
    ),
    (
        "primitive.state_dynamics.pc_alm_settling",
        "computronium.primitives.state_dynamics.pc_alm_settling",
    ),
    (
        "primitive.state_dynamics.predictive_settling",
        "computronium.primitives.state_dynamics.predictive_settling",
    ),
)


@dataclass(frozen=True, slots=True)
class Rung:
    """One rung of the ladder for one site.

    Attributes:
        label: rung name — ``reference`` or ``kernel``.
        technology: what the rung is implemented in.
        step: callable taking the site case and returning the output.
        available: whether the rung can run here; measured, not declared.
    """

    label: str
    technology: str
    step: Step
    available: Callable[[], bool] = lambda: True


@dataclass(frozen=True, slots=True)
class RungSite:
    """A unit of work with more than one implementation of it."""

    id: str
    make_case: Callable[..., Case]
    rungs: tuple[Rung, ...]
    shape: Callable[[Case], str]

    def case(self, *, device: str, dtype: torch.dtype, seed: int, scale: int) -> Case:
        return self.make_case(device=device, dtype=dtype, seed=seed, scale=scale)


def _always() -> bool:
    return True


def _git_sha() -> str | None:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],  # ruff: ignore[start-process-with-partial-path]
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except OSError:
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None


def _members(obj: object) -> Iterable[object]:
    if is_dataclass(obj):
        return [getattr(obj, f.name, None) for f in fields(obj)]
    return list(getattr(obj, "__dict__", {}).values())


def _tensor_bytes(case: Case) -> int:
    total = 0
    stack = [case]
    while stack:
        obj = stack.pop()
        if isinstance(obj, torch.Tensor):
            total += obj.numel() * obj.element_size()
        elif isinstance(obj, dict):
            stack.extend(obj.values())
        elif isinstance(obj, (list, tuple, set, frozenset)):
            stack.extend(obj)
        else:
            stack.extend(_members(obj))
    return total


def _shape(case: Case) -> str:
    dims: list[str] = []
    stack = [case]
    while stack:
        obj = stack.pop()
        if isinstance(obj, torch.Tensor):
            dims.extend(str(d) for d in obj.shape)
        elif isinstance(obj, dict):
            stack.extend(obj.values())
        elif isinstance(obj, (list, tuple, set, frozenset)):
            stack.extend(obj)
        else:
            stack.extend(_members(obj))
    return "x".join(dims[:4]) or "scalar"


def _spec_site(spec_id: str, package: str) -> RungSite:
    """Bind both rungs of a spec site: ``reference.step`` and ``kernel.step``."""
    from computronium.acceleration.registry import get

    spec = get(spec_id)
    if spec.kernel_entrypoint is None:
        raise ValueError(f"{spec_id} declares no kernel rung")
    reference = importlib.import_module(f"{package}.reference")
    kernel = importlib.import_module(f"{package}.kernel")
    cases = importlib.import_module(f"{package}.cases")

    kernel_call = getattr(kernel, spec.kernel_entrypoint.rsplit(".", 1)[1])
    return RungSite(
        id=spec_id,
        make_case=cases.make_case,
        rungs=(
            Rung("reference", "torch", reference.step),
            Rung(
                "kernel",
                spec.kernel_technology or "torch",
                kernel_call,
                available=kernel.is_available,
            ),
        ),
        shape=_shape,
    )


def _muon_site() -> RungSite:
    """Muon orthogonalisation: the torch rung against the triton rung."""
    from computronium.acceleration.triton_kernels import HAS_TRITON, MEP_TritonOps
    from computronium.core.optimization.strategies import MuonUpdate

    torch_rung = MuonUpdate()
    return RungSite(
        id="acceleration.muon_newton_schulz",
        make_case=lambda *, device, dtype, seed, scale: torch.randn(
            64 * scale,
            64 * scale,
            device=device,
            dtype=dtype,
            generator=torch.Generator(device=device).manual_seed(seed),
        ),
        rungs=(
            Rung("reference", "torch", lambda g: torch_rung._newton_schulz(g, 5)),
            Rung(
                "kernel",
                "triton",
                lambda g: MEP_TritonOps.muon_orthogonalize(g, ns_steps=5),
                available=lambda: HAS_TRITON,
            ),
        ),
        shape=lambda g: f"{g.shape[0]}x{g.shape[1]}",
    )


def _eqprop_site() -> RungSite:
    """EqProp forward step: the torch expression against the triton kernel."""
    from computronium.acceleration.triton_kernels import TritonEqPropOps

    def _torch_step(case: tuple[torch.Tensor, torch.Tensor, torch.Tensor | None]):
        h, pre_act, bias = case
        bias_val = bias if bias is not None else 0.0
        return 0.5 * h + 0.5 * torch.tanh(pre_act + bias_val)

    def _make_case(*, device, dtype, seed, scale):
        gen = torch.Generator(device=device).manual_seed(seed)
        n = 1024 * scale
        h = torch.randn(n, device=device, dtype=dtype, generator=gen)
        pre_act = torch.randn(n, device=device, dtype=dtype, generator=gen)
        bias = torch.randn(n, device=device, dtype=dtype, generator=gen)
        return h, pre_act, bias

    return RungSite(
        id="acceleration.eqprop_forward_step",
        make_case=_make_case,
        rungs=(
            Rung("reference", "torch", _torch_step),
            Rung(
                "kernel",
                "triton",
                lambda case: TritonEqPropOps.step(case[0], case[1], 0.5, case[2]),
                available=TritonEqPropOps.is_available,
            ),
        ),
        shape=lambda case: f"{case[0].numel()}",
    )


def rung_sites() -> tuple[RungSite, ...]:
    """Every site that has a triton rung to measure, in a stable order."""
    return tuple(
        [_spec_site(spec_id, package) for spec_id, package in _RUNG_PACKAGES]
        + [_muon_site(), _eqprop_site()]
    )


def _time_rung(
    rung: Rung, case: Case, *, device: str, warmup: int, iterations: int
) -> list[dict[str, Any]]:
    cuda = device != "cpu" and torch.cuda.is_available()

    def _sync() -> None:
        if cuda:
            torch.cuda.synchronize()

    for _ in range(warmup):
        rung.step(case)
    _sync()

    rows: list[dict[str, Any]] = []
    for iteration in range(iterations):
        if cuda:
            torch.cuda.reset_peak_memory_stats()
        start = time.perf_counter()
        rung.step(case)
        _sync()
        elapsed = time.perf_counter() - start
        rows.append({
            "wall_time_s": elapsed,
            "wall_time_ms": elapsed * 1000,
            "peak_mem_mb": (
                torch.cuda.max_memory_allocated() / (1024 * 1024)
                if cuda
                else _tensor_bytes(case) / (1024 * 1024)
            ),
            "iteration": iteration,
        })
    return rows


def measure(
    site: RungSite,
    *,
    device: str = "cuda",
    dtype: str = "float32",
    seed: int = 0,
    scales: Sequence[int] = DEFAULT_SCALES,
    warmup: int = 3,
    iterations: int = 5,
) -> list[dict[str, Any]]:
    """Time every available rung of one site at each scale.

    Returns:
        One row per (scale, rung, iteration) in the ``artifacts/benchmarks``
        schema, with ``technology`` naming the rung's implementation.
    """
    torch_dtype = getattr(torch, dtype)
    git_sha = _git_sha()
    rows: list[dict[str, Any]] = []

    for scale in scales:
        case = site.case(device=device, dtype=torch_dtype, seed=seed, scale=scale)
        for rung in site.rungs:
            available = bool(rung.available())
            try:
                timings = (
                    _time_rung(
                        rung, case, device=device, warmup=warmup, iterations=iterations
                    )
                    if available
                    else [{"status": "unavailable"}]
                )
            except Exception as exc:  # ruff: ignore[blind-except]  (a broken rung is a result)
                timings = [{"status": f"error: {type(exc).__name__}: {exc}"}]

            for timing in timings:
                row: dict[str, Any] = {
                    "id": site.id,
                    "rung": rung.label,
                    "backend": rung.label,
                    "technology": rung.technology,
                    "device": device,
                    "dtype": dtype,
                    "seed": seed,
                    "scale": scale,
                    "shape": site.shape(case),
                    "status": timing.get("status", "ok"),
                }
                row.update({k: v for k, v in timing.items() if k != "status"})
                if git_sha:
                    row["git_sha"] = git_sha
                rows.append(row)

    return rows


def _write(
    rows: Iterable[dict[str, Any]], output_dir: pathlib.Path
) -> list[pathlib.Path]:
    by_site: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_site.setdefault(str(row["id"]), []).append(row)

    written: list[pathlib.Path] = []
    for site_id, site_rows in by_site.items():
        path = output_dir / f"{site_id.replace('.', '_')}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        with path.open("a", encoding="utf-8") as handle:
            if existing and not existing.endswith("\n"):
                handle.write("\n")
            for row in site_rows:
                handle.write(json.dumps(row) + "\n")
        written.append(path)
    return written


def _summary(rows: Sequence[dict[str, Any]]) -> str:
    lines = [
        "site                                   rung       tech          n  median_ms  ratio"
    ]
    for site_id in dict.fromkeys(str(r["id"]) for r in rows):
        site_rows = [r for r in rows if r["id"] == site_id]
        by_rung: dict[tuple[str, str], list[float]] = {}
        for row in site_rows:
            if row["status"] == "ok":
                by_rung.setdefault(
                    (str(row["rung"]), str(row["technology"])), []
                ).append(float(row["wall_time_ms"]))
        base = next(
            (sorted(v)[len(v) // 2] for k, v in by_rung.items() if k[0] == "reference"),
            None,
        )
        for (rung, tech), values in by_rung.items():
            values.sort()
            median = values[len(values) // 2]
            ratio = f"{median / base:.3f}" if base else "-"
            lines.append(
                f"{site_id[:38]:38}  {rung:9}  {tech:12}  {len(values):2}  "
                f"{median:9.3f}  {ratio:>6}"
            )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the rung benchmark and append rows to ``artifacts/benchmarks/rungs``."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--dtype", default="float32")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--scales", type=int, nargs="+", default=list(DEFAULT_SCALES))
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--site", action="append", default=None)
    parser.add_argument("--output-dir", type=pathlib.Path, default=OUTPUT_DIR)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.device != "cpu" and not torch.cuda.is_available():
        parser.error("no CUDA device; pass --device cpu to measure the torch rungs")

    sites = [
        site
        for site in rung_sites()
        if not args.site or any(key in site.id for key in args.site)
    ]
    rows: list[dict[str, Any]] = []
    for site in sites:
        rows.extend(
            measure(
                site,
                device=args.device,
                dtype=args.dtype,
                seed=args.seed,
                scales=args.scales,
                warmup=args.warmup,
                iterations=args.iterations,
            )
        )

    print(_summary(rows))  # ruff: ignore[print]  (CLI output)
    if not args.dry_run:
        for path in _write(rows, args.output_dir):
            print(f"wrote {path}")  # ruff: ignore[print]  (CLI output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
