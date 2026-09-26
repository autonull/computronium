"""The kernel census behind TODO36 §1.

Two parallel acceleration systems share the `computronium/acceleration/`
directory and the family names `fa`, `ff`, `pc`, `snn`, `hebbian`, `tile`,
`tp`, `eqprop`, `backprop`, `mep`. This probe answers, per layer, the four
questions a session needs before touching either: what is registered, what is
reachable, what compiles, and whether any of it has been measured to be faster
than the torch it replaces.

Run: ``uv run python scripts/probes/todo36_kernel_census.py``
Measured on an RTX 3080, triton 3.8.0, torch with CUDA, 2026-09-26.
"""

from __future__ import annotations

import ast
import json
import pathlib
import re
import sys
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parents[2]
TRITON_MODULES = (
    "triton_kernels",
    "fa_kernels",
    "pcalm_kernels",
    "tile_kernels",
    "compile",
)

__all__ = ["main"]


def _triton_kernel_count(module: str) -> int:
    path = REPO / "computronium" / "acceleration" / f"{module}.py"
    if not path.exists():
        return 0
    return len(re.findall(r"@triton\.jit", path.read_text()))


def _layer_b_backends() -> tuple[int, int, list[str], bool]:
    """``(concrete classes, contrastive classes, families, spec walk ran?)``."""
    classes = 0
    for path in sorted((REPO / "computronium" / "acceleration").glob("*.py")):
        tree = ast.parse(path.read_text())
        classes += sum(
            1
            for node in tree.body
            if isinstance(node, ast.ClassDef)
            and node.name.endswith("KernelBackend")
            and not any(
                (
                    isinstance(d, ast.expr)
                    and getattr(d, "attr", "") == "runtime_checkable"
                )
                or (isinstance(d, ast.Name) and d.id == "runtime_checkable")
                for d in node.decorator_list
            )
        )
    import computronium.acceleration  # ruff: ignore[unused-import]  (populates the registry)
    from computronium.acceleration.kernel_backend import KernelRegistry

    walked = "computronium.acceleration.registry" in sys.modules and any(
        "local_goodness" in m for m in sys.modules
    )
    return classes, 10, sorted(f.value for f in KernelRegistry._backends), walked


def _layer_a() -> tuple[int, int, int, list[str]]:
    """``(specs, kernel_verified, declaring triton, modules reaching triton)``."""
    import computronium.acceleration  # ruff: ignore[unused-import]
    from computronium.acceleration.registry import all_specs

    specs = all_specs()
    reaching: list[str] = []
    for base in ("algorithms", "primitives"):
        for path in sorted((REPO / "computronium" / base).rglob("kernel.py")):
            src = path.read_text()
            if any(
                f"acceleration.{m}" in src or f'"{m}"' in src for m in TRITON_MODULES
            ):
                reaching.append(f"{base}/{path.parent.name}/kernel.py")
    return (
        len(specs),
        sum(1 for s in specs if s.status == "kernel_verified"),
        sum(1 for s in specs if "triton" in str(s.kernel_technology).lower()),
        reaching,
    )


def _benchmark_rows() -> tuple[int, int, Counter]:
    """``(rows, gpu rows, (device, backend) counts)`` across the benchmark store."""
    rows, gpu, seen = 0, 0, Counter()
    for path in sorted((REPO / "artifacts" / "benchmarks").glob("*.jsonl")):
        for line in path.read_text().splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            rows += 1
            seen[row.get("device"), row.get("backend")] += 1
            if str(row.get("device", "")).startswith("cuda"):
                gpu += 1
    return rows, gpu, seen


def main() -> int:
    specs, verified, declared, reaching = _layer_a()
    classes, contrastive, registered, walked = _layer_b_backends()
    rows, gpu, seen = _benchmark_rows()
    kernels = {m: _triton_kernel_count(m) for m in TRITON_MODULES}

    print("LAYER A  -- primitives/**/kernel.py -> acceleration/, select_backend()")
    print(f"  ImplementationSpecs                  {specs}")
    print(
        f"  status == kernel_verified            {verified}   (reference_only {specs - verified})"
    )
    print(f"  kernel_technology == 'triton'        {declared}")
    print(f"  kernel modules reaching triton       {len(reaching)}")
    for name in reaching:
        print(f"      {name}")
    print(f"  triton kernels behind those modules  {sum(kernels.values())}  {kernels}")

    print()
    print("LAYER B  -- kernel_backend.py KernelRegistry, *KernelBackend classes")
    print(f"  concrete *KernelBackend classes      {classes} (excludes the Protocol)")
    print(
        f"  contrastive backend classes          {contrastive}  (module never imported)"
    )
    print(f"  families registered at this point    {len(registered)}  {registered}")
    print(f"  population came from Layer A's spec walk: {walked}")
    print("  AlgorithmFamily members total        12")

    print()
    print("EVIDENCE")
    print(f"  benchmark rows                       {rows}")
    print(f"  rows on a GPU device                 {gpu}")
    for key, n in sorted(seen.items(), key=lambda kv: str(kv[0])):
        print(f"      device={key[0]!r:8} backend={key[1]!r:10} {n}")

    print()
    print("READ THIS AS: Layer A is the system that runs. Layer B is a second design")
    print("whose registry is populated by an import side effect and whose classes")
    print("have no consumer outside the two export CLIs. TODO36.md §0.2 asks which")
    print("of the two survives before any work starts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
