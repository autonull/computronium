"""One line per rung: what exists, what compiles, what is verified, what was measured.

TODO36 §6.2 named this command as the check §0.3 asks for and the tree did not
have. It exists because the questions were unanswerable together: a rung's
technology came from a spec field, its compilability from a module-level flag, its
parity from a status enum, and its speed from a file in ``artifacts/`` nobody
could tie back to a rung.

    uv run python -m computronium.acceleration.status --family fa

Every column is read from a source that can be re-derived — the spec registry,
:mod:`computronium.acceleration.availability`, and the benchmark rows — and
``none`` means *not recorded here*, never *absent*. The distinction is the point:
a missing measurement and a missing rung are different facts.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING

from computronium.acceleration.availability import compile_report
from computronium.acceleration.dispatch import resolve_rung
from computronium.acceleration.registry import all_specs

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from computronium.acceleration.spec import ImplementationSpec

__all__ = ["RungStatus", "family_of", "gpu_rungs", "main", "rows", "technology_of"]

BENCH_DIR = pathlib.Path("artifacts/benchmarks")

_NONE = "none"

#: ``acceleration/<name>_kernels`` -> the family whose rungs that module serves.
#: Derived from the kernel module's imports at query time; this table only names
#: the convention, so a module without an entry simply has no derived family.
#: Also matches ``core/substrates/complex_substrate`` for the complex substrate family.
#: Matches both module paths and import statements from acceleration kernel modules.
_KERNEL_MODULE_FAMILY = re.compile(
    r"computronium\.(?:acceleration\.(\w+?_kernels|compile)|core\.substrates\.(complex_substrate))|"
    r"from computronium\.acceleration\.(\w+?_kernels) import"
)

#: Patterns to derive kernel technology from a kernel module's imports.
#: Matched in order; first match wins. This replaces the declared
#: ``spec.kernel_technology`` with a measured value (§4.2).
_KERNEL_TECHNOLOGY_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    # Direct triton imports
    (re.compile(r"import triton\b|from triton\b"), "triton"),
    # Direct cupy imports
    (re.compile(r"import cupy\b|from cupy\b"), "cupy"),
    # Import from acceleration kernel modules (which use triton)
    (re.compile(r"from computronium\.acceleration\.\w+_kernels import"), "triton"),
    # Import from availability (triton_rung_available)
    (
        re.compile(
            r"from computronium\.acceleration\.availability import.*\btriton_rung_available\b"
        ),
        "triton",
    ),
    # Import from backends with kernel_available("triton") usage
    (re.compile(r'kernel_available\s*\(\s*["\']triton["\']'), "triton"),
    (
        re.compile(
            r"from computronium\.acceleration\.backends import.*\bkernel_available\b.*KERNEL_TECHNOLOGY"
        ),
        "triton",
    ),
    # Import from compile module -> torch_compile
    (re.compile(r"from computronium\.acceleration\.compile import"), "torch_compile"),
    # kernel_available with torch_compile
    (re.compile(r'kernel_available\s*\(\s*["\']torch_compile["\']'), "torch_compile"),
)


@dataclass(frozen=True, slots=True)
class RungStatus:
    """Everything known about one rung of one spec.

    Attributes:
        spec: the implementation id.
        family: the acceleration family derived from the kernel module's imports.
        rung: ``reference`` or ``kernel``.
        technology: what the rung is implemented in.
        compiles: ``yes``/``no``/``none`` — measured for a triton rung with a
            fixture, otherwise not recorded.
        parity: ``verified`` when the promotion status asserts it, else ``none``.
        gpu: whether a ``device: "cuda"`` benchmark row exists for this rung.
        status: the spec's promotion status.
    """

    spec: str
    family: str
    rung: str
    technology: str
    compiles: str
    parity: str
    gpu: str
    status: str


def _kernel_module_source(spec: ImplementationSpec) -> str | None:
    if spec.kernel_entrypoint is None:
        return None
    module = spec.kernel_entrypoint.rsplit(".", 1)[0]
    path = pathlib.Path(*module.split(".")).with_suffix(".py")
    return path.read_text(encoding="utf-8") if path.exists() else None


def family_of(spec: ImplementationSpec) -> str:
    """The acceleration family a spec's kernel rung belongs to.

    Derived from the kernel module's own imports — ``fa_kernels`` means the ``fa``
    family, ``compile`` means ``torch_compile`` — because §4.3's whole point is
    that a family name has one referent. ``none`` means the kernel module imports
    no acceleration kernel module at all, which for a spec that declares
    ``kernel_technology="triton"`` means the declaration is not delivered.
    """
    source = _kernel_module_source(spec)
    if source is None:
        return _NONE
    found = _KERNEL_MODULE_FAMILY.findall(source)
    if not found:
        return _NONE
    # findall returns tuples when pattern has groups; pick first non-empty group
    family = next((g for g in found[0] if g), "")
    return "torch_compile" if family == "compile" else family.removesuffix("_kernels")


def technology_of(spec: ImplementationSpec) -> str:
    """The kernel technology a spec's kernel rung uses.

    Derived from the kernel module's own imports — same "measured, not declared"
    rule as :func:`family_of`. Eliminates drift between declared
    ``kernel_technology`` and actual implementation.

    Returns:
        One of: "triton", "torch_compile", "cupy", "torch" (reference), "none".
    """
    source = _kernel_module_source(spec)
    if source is None:
        return _NONE
    for pattern, tech in _KERNEL_TECHNOLOGY_PATTERNS:
        if pattern.search(source):
            return tech
    # Check for KERNEL_TECHNOLOGY constant as fallback
    if "KERNEL_TECHNOLOGY" in source:
        # Extract the value if it's a simple string assignment
        match = re.search(r'KERNEL_TECHNOLOGY\s*=\s*["\']([^"\']+)["\']', source)
        if match:
            return match.group(1)
    return "torch"


def gpu_rungs() -> dict[tuple[str, str], float]:
    """Best (lowest) CUDA wall time per ``(spec id, rung)`` in the benchmark rows."""
    best: dict[tuple[str, str], float] = {}
    if not BENCH_DIR.exists():
        return best
    for path in sorted(BENCH_DIR.rglob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("device") != "cuda" or row.get("status") != "ok":
                continue
            key = (str(row.get("id")), str(row.get("rung", row.get("backend"))))
            millis = float(row.get("wall_time_ms", 0.0))
            if key not in best or millis < best[key]:
                best[key] = millis
    return best


def _compile_states() -> dict[str, str]:
    return {report.family: report.state.value for report in compile_report()}


def _family_compiles(family: str) -> str:
    states = {
        report.state.value for report in compile_report() if report.family == family
    }
    if not states:
        return _NONE
    return "yes" if states == {"compiles"} else "no"


def _parity(spec: ImplementationSpec, rung: str) -> str:
    if rung == "reference":
        return "n/a"
    return (
        "verified"
        if spec.status in {"kernel_verified", "microbenched", "campaign_ready"}
        else _NONE
    )


def rows(specs: Iterable[ImplementationSpec] | None = None) -> tuple[RungStatus, ...]:
    """One :class:`RungStatus` per rung of every spec, reference rung first."""
    gpu = gpu_rungs()
    out: list[RungStatus] = []
    for spec in specs if specs is not None else all_specs():
        family = family_of(spec)
        tech = technology_of(spec)
        compiles = _family_compiles(family) if tech == "triton" else _NONE
        for requested in ("reference", "kernel"):
            if requested == "kernel" and "kernel" not in spec.supported_backends:
                continue
            rung = resolve_rung(spec, requested)
            out.append(
                RungStatus(
                    spec=spec.id,
                    family=family,
                    rung=rung.rung,
                    technology=rung.technology or tech or _NONE,
                    compiles=compiles if rung.rung == "kernel" else "n/a",
                    parity=_parity(spec, rung.rung),
                    gpu=("yes" if (spec.id, rung.rung) in gpu else _NONE),
                    status=spec.status,
                )
            )
    return tuple(out)


def _spec_matches(spec: str, needle: str) -> bool:
    """Segment-aware id search: ``algorithm.fa`` is not ``algorithm.fast_weight``.

    A plain substring search on a dotted id matches at every dot, which is how
    "algorithm.fa" finds "algorithm.fast_weight" ("fast" starts with "fa"). The
    last segment is compared whole, on its word stem: "tile" finds
    "tile_mesh", "fa" does not find "fabric".
    """
    spec_parts = spec.lower().split(".")
    query_parts = needle.lower().split(".")
    if len(query_parts) > len(spec_parts):
        return False
    if spec_parts[: len(query_parts) - 1] != query_parts[:-1]:
        return False
    return spec_parts[-1].split("_")[0] == query_parts[-1]


def _matches(row: RungStatus, needle: str) -> bool:
    """Match the derived family or the technology, exactly.

    Substring matching is how ``--family fa`` ends up reporting `fabric_pc`,
    `fast_weight` and `dfa`; a name is a name. ``--spec`` is the substring search,
    for when you know the id and not the family.
    """
    needle = needle.lower()
    return needle in {row.family.lower(), row.technology.lower()}


_COLUMNS = (
    "spec",
    "family",
    "rung",
    "technology",
    "compiles",
    "parity",
    "gpu",
    "status",
)


def _render(table: Sequence[RungStatus]) -> str:
    body = [[str(value) for value in asdict(row).values()] for row in table]
    widths = [
        max(len(_COLUMNS[i]), *(len(line[i]) for line in body))
        if body
        else len(_COLUMNS[i])
        for i in range(len(_COLUMNS))
    ]
    lines = [
        "  ".join(_COLUMNS[i].ljust(widths[i]) for i in range(len(_COLUMNS))),
        "  ".join("-" * widths[i] for i in range(len(_COLUMNS))),
    ]
    lines.extend(
        "  ".join(line[i].ljust(widths[i]) for i in range(len(_COLUMNS)))
        for line in body
    )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    """Print the rung table, optionally filtered to one family.

    Returns:
        ``0`` always; the table is a report, not a gate.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--family", default=None, help="exact derived family or technology, e.g. fa"
    )
    parser.add_argument(
        "--spec", default=None, help="spec id, segment-aware: 'algorithm.fa'"
    )
    parser.add_argument(
        "--status", default=None, help="substring of the promotion status"
    )
    parser.add_argument(
        "--json", action="store_true", help="emit JSON instead of a table"
    )
    args = parser.parse_args(argv)

    table = list(rows())
    if args.family:
        table = [row for row in table if _matches(row, args.family)]
    if args.spec:
        table = [row for row in table if _spec_matches(row.spec, args.spec)]
    if args.status:
        table = [row for row in table if args.status.lower() in row.status.lower()]

    if args.json:
        print(json.dumps([asdict(row) for row in table], indent=2))  # ruff: ignore[print]
    else:
        print(_render(table) if table else "no rungs match")  # ruff: ignore[print]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
