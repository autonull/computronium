"""One line per rung: what exists, what compiles, what is verified, what was measured.

TODO36 §6.2 named this command as the check §0.3 asks for and the tree did not
have. It exists because the questions were unanswerable together: a rung's
technology came from a spec field, its compilability from a module-level flag, its
parity from a status enum, and its speed from a file in ``artifacts/`` nobody
could tie back to a rung.

    uv run python -m computronium.acceleration.status --credit thermodynamic_contrast

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

__all__ = [
    "RungStatus",
    "coordinate_of",
    "gpu_rungs",
    "main",
    "rows",
    "technology_of",
]

BENCH_DIR = pathlib.Path("artifacts/benchmarks")

_NONE = "none"

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
        coordinate: the coordinate (geometry, dynamics, credit, update, plasticity) derived from uses_primitives.
        rung: ``reference`` or ``kernel``.
        technology: what the rung is implemented in.
        compiles: ``yes``/``no``/``none`` — measured for a triton rung with a
            fixture, otherwise not recorded.
        parity: ``verified`` when the promotion status asserts it, else ``none``.
        gpu: whether a ``device: "cuda"`` benchmark row exists for this rung.
        status: the spec's promotion status.
    """

    spec: str
    coordinate: str
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


def _primitive_to_axis(primitive: str) -> tuple[str, str] | None:
    """Map a primitive name to its axis and value."""
    # Extract the primitive name from full ID like "primitive.state_dynamics.instantaneous_pass"
    prim_name = primitive.split(".")[-1]

    # credit_assignment primitives
    credit_primitives = {
        "thermodynamic_contrast": ("credit", "thermodynamic_contrast"),
        "equilibrium": ("credit", "equilibrium"),
        "random_projections": ("credit", "random_projections"),
        "local_goodness": ("credit", "local_goodness"),
        "pepita": ("credit", "pepita"),
        "temporal_trace": ("credit", "temporal_trace"),
        "target_inversion": ("credit", "target_inversion"),
        "gradient": ("credit", "gradient"),
        "backprop": ("credit", "gradient"),
        "reverse_mode": ("credit", "gradient"),
        "pc_alm": ("credit", "pc_alm"),
    }
    # state_dynamics primitives
    dynamics_primitives = {
        "energy_minimization": ("dynamics", "energy_minimization"),
        "predictive_settling": ("dynamics", "predictive_settling"),
        "spike_integration": ("dynamics", "spike_integration"),
        "instantaneous_pass": ("dynamics", "instantaneous"),
        "instantaneous": ("dynamics", "instantaneous"),
        "diffusion": ("dynamics", "diffusion"),
        "pc_alm": ("dynamics", "pc_alm"),
        "pc_alm_settling": ("dynamics", "pc_alm"),
    }
    # geometry primitives
    geometry_primitives = {
        "feedforward": ("geometry", "feedforward"),
        "recurrent": ("geometry", "recurrent"),
        "recurrent_attractor": ("geometry", "recurrent_attractor"),
        "tile_mesh": ("geometry", "tile_mesh"),
        "tile": ("geometry", "tile_mesh"),
        "attention": ("geometry", "attention"),
        "spatial_lattice": ("geometry", "spatial_lattice"),
        "graph": ("geometry", "graph"),
        "conv": ("geometry", "conv"),
        "nca": ("geometry", "nca"),
        "ntm": ("geometry", "ntm"),
        "causal_transformer": ("geometry", "causal_transformer"),
    }
    # update primitives
    update_primitives = {
        "euclidean": ("update", "euclidean"),
        "adam": ("update", "adam"),
        "ortho_adam": ("update", "ortho_adam"),
        "lion": ("update", "lion"),
        "riemannian_orthogonal": ("update", "riemannian_orthogonal"),
        "spectral_constrained": ("update", "spectral_constrained"),
        "mean_norm": ("update", "mean_norm"),
        "elastic_consolidation": ("update", "elastic_consolidation"),
    }
    # plasticity primitives
    plasticity_primitives = {
        "null_plasticity": ("plasticity", "null"),
        "routing": ("plasticity", "routing"),
        "fast_weight": ("plasticity", "fast_weight"),
        "substrate_coupled": ("plasticity", "substrate_coupled"),
    }

    if prim_name in credit_primitives:
        return credit_primitives[prim_name]
    if prim_name in dynamics_primitives:
        return dynamics_primitives[prim_name]
    if prim_name in geometry_primitives:
        return geometry_primitives[prim_name]
    if prim_name in update_primitives:
        return update_primitives[prim_name]
    if prim_name in plasticity_primitives:
        return plasticity_primitives[prim_name]
    return None


def coordinate_of(spec: ImplementationSpec) -> str:
    """The coordinate a spec's kernel rung targets.

    Derived from the spec's ``uses_primitives`` which names the exact axes.
    For primitive specs, uses the ``axis`` field. Returns a compact string
    like "feedforward/instantaneous/gradient/euclidean/null".
    """
    axes = {
        "geometry": "unknown",
        "dynamics": "unknown",
        "credit": "unknown",
        "update": "unknown",
        "plasticity": "null",
    }

    # For primitive specs, use the axis field
    if spec.kind == "primitive" and spec.axis:
        axis_map = {
            "substrate": "substrate",
            "geometry": "geometry",
            "state_dynamics": "dynamics",
            "plasticity": "plasticity",
            "credit_assignment": "credit",
            "parameter_update": "update",
        }
        axis_key = axis_map.get(spec.axis)
        if axis_key and axis_key != "substrate":
            # For primitives, we only know one axis
            axes[axis_key] = spec.id.split(".")[-1]
        return f"{axes['geometry']}/{axes['dynamics']}/{axes['credit']}/{axes['update']}/{axes['plasticity']}"

    # For algorithm specs, use uses_primitives
    for prim in spec.uses_primitives:
        mapped = _primitive_to_axis(prim)
        if mapped:
            axis, value = mapped
            axes[axis] = value

    # Infer geometry from algorithm ID if not specified
    if axes["geometry"] == "unknown":
        spec_id = spec.id.lower()
        if "tile" in spec_id:
            axes["geometry"] = "tile_mesh"
        elif any(
            x in spec_id
            for x in [
                "eqprop",
                "directed_ep",
                "diffusion_eqprop",
                "finite_nudge",
                "momentum_eqprop",
                "ternary_eqprop",
                "sparse_eqprop",
                "pc",
                "pcalm",
                "hebbian",
                "snn",
                "fast_weight",
                "routing",
            ]
        ):
            axes["geometry"] = "recurrent"
        elif any(
            x in spec_id
            for x in ["fa", "dfa", "ff", "pepita", "tp", "backprop", "holomorphic_ep"]
        ):
            axes["geometry"] = "feedforward"

    return f"{axes['geometry']}/{axes['dynamics']}/{axes['credit']}/{axes['update']}/{axes['plasticity']}"


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


def _coordinate_compiles(coord: str) -> str:
    """Check if any kernel for this coordinate compiles."""
    # Map coordinate to compile report family
    coord_to_family = {
        "feedforward/instantaneous/gradient/euclidean/null": "backprop",
        "recurrent/energy_minimization/thermodynamic_contrast/euclidean/null": "pc",
        "feedforward/instantaneous/random_projections/euclidean/null": "fa",
        "feedforward/instantaneous/local_goodness/euclidean/null": "ff",
        "feedforward/instantaneous/pepita/euclidean/null": "pepita",
        "feedforward/instantaneous/temporal_trace/euclidean/null": "hebbian",
        "feedforward/instantaneous/target_inversion/euclidean/null": "tp",
        "feedforward/predictive_settling/thermodynamic_contrast/euclidean/null": "pc",
        "feedforward/spike_integration/temporal_trace/euclidean/null": "snn",
        "tile_mesh/instantaneous/gradient/euclidean/null": "tile",
    }
    family = coord_to_family.get(coord)
    if family is None:
        return _NONE
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
        coord = coordinate_of(spec)
        tech = technology_of(spec)
        compiles = _coordinate_compiles(coord) if tech == "triton" else _NONE
        for requested in ("reference", "kernel"):
            if requested == "kernel" and "kernel" not in spec.supported_backends:
                continue
            rung = resolve_rung(spec, requested)
            out.append(
                RungStatus(
                    spec=spec.id,
                    coordinate=coord,
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
    """Match the coordinate or the technology, exactly.

    Substring matching on coordinate axes. ``--credit thermodynamic_contrast`` matches
    all specs using thermodynamic contrast credit.
    """
    needle = needle.lower()
    # Check if needle matches any coordinate axis
    coord_parts = row.coordinate.lower().split("/")
    return needle in coord_parts or needle == row.technology.lower()


_COLUMNS = (
    "spec",
    "coordinate",
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
    """Print the rung table, optionally filtered to one coordinate axis.

    Returns:
        ``0`` always; the table is a report, not a gate.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--credit",
        default=None,
        help="exact credit assignment type, e.g. thermodynamic_contrast",
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
    if args.credit:
        table = [row for row in table if _matches(row, args.credit)]
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
