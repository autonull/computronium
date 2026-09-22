"""Fog-of-war — KB coverage derived map overlay (M2.6).

Coverage % from KB alone. "You've charted X% of planned regions".
Derivable from KB only — no new measurement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from computronium.autoscientist.broad_map import _load_measured_cells

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True, slots=True)
class FogRegion:
    """A region on the discovery map."""

    key: str  # e.g., "dynamics=EnergyMinimization,credit=ThermodynamicContrast,..."
    label: str  # Human-readable label
    charted: bool
    cell_count: int
    dominant_primitives: dict[str, str]  # axis -> primitive


@dataclass(frozen=True, slots=True)
class FogOfWar:
    """Complete fog-of-war state for the discovery map."""

    regions: tuple[FogRegion, ...]
    total_planned: int
    total_charted: int
    coverage_pct: float

    @property
    def explorer_summary(self) -> str:
        return f"You've charted {self.total_charted} of {self.total_planned} regions ({self.coverage_pct:.0f}%)"

    @property
    def lab_summary(self) -> str:
        return f"KB coverage: {self.total_charted}/{self.total_planned} regions ({self.coverage_pct:.1f}%)"


def _generate_region_key(row: object) -> str:
    """Generate a region key from a cell row (axis primitives)."""
    # Use the 4 main axes that define the search space
    axes = ("dynamics", "credit", "update", "topology")
    parts = []
    for axis in axes:
        val = getattr(row, axis, "unknown")
        parts.append(f"{axis}={val}")
    return ",".join(parts)


def _generate_region_label(row: object) -> str:
    """Generate a human-readable label for a region."""
    axes = ("dynamics", "credit", "update", "topology")
    parts = []
    for axis in axes:
        val = getattr(row, axis, "unknown")
        # Shorten common names
        short = {
            "EnergyMinimization": "EnergyMin",
            "PredictiveSettling": "PredSettle",
            "InstantaneousPass": "Instant",
            "SpikeIntegration": "Spike",
            "ThermodynamicContrast": "Thermo",
            "RandomProjectionsCredit": "RandProj",
            "LocalGoodnessCredit": "LocalGood",
            "TargetInversionCredit": "TargetInv",
            "TemporalTraceCredit": "TempTrace",
            "HomeostaticCredit": "Homeo",
            "EuclideanUpdate": "Euclid",
            "RiemannianOrthogonalUpdate": "Riemann",
            "SpectralConstrainedUpdate": "Spectral",
            "NaturalGradientUpdate": "NatGrad",
            "ElasticConsolidationUpdate": "Elastic",
            "FeedforwardDAG": "FF",
            "RecurrentAttractor": "Recurrent",
            "TileMesh": "Tile",
            "FabricPC": "Fabric",
            "SpatialLattice3D": "Lattice3D",
            "NTM": "NTM",
            "NCA": "NCA",
        }.get(val, val)
        parts.append(f"{short}")
    return " × ".join(parts)


def _get_dominant_primitives(row: object) -> dict[str, str]:
    """Get the primitive for each axis from a cell row."""
    axes = ("dynamics", "credit", "update", "topology", "substrate", "plasticity")
    return {axis: str(getattr(row, axis, "unknown")) for axis in axes}


def compute_fog_of_war(root: Path) -> FogOfWar:  # noqa: C901
    """Compute fog-of-war from KB (read-only).

    Args:
        root: Campaign root path (contains kb.sqlite)

    Returns:
        FogOfWar with all regions and coverage stats
    """
    kb_path = root / "kb.sqlite"
    if not kb_path.exists():
        return FogOfWar(regions=(), total_planned=0, total_charted=0, coverage_pct=0.0)

    cells = _load_measured_cells(kb_path)
    if not cells:
        return FogOfWar(regions=(), total_planned=0, total_charted=0, coverage_pct=0.0)

    # Group cells by region (dynamics × credit × update × topology)
    from collections import Counter, defaultdict

    region_cells: dict[str, list] = defaultdict(list)
    region_primitives: dict[str, dict[str, Counter]] = defaultdict(
        lambda: defaultdict(Counter)
    )

    for row in cells:
        key = _generate_region_key(row)
        region_cells[key].append(row)

        # Track primitive distribution per axis for this region
        for axis in (
            "dynamics",
            "credit",
            "update",
            "topology",
            "substrate",
            "plasticity",
        ):
            val = str(getattr(row, axis, "unknown"))
            region_primitives[key][axis][val] += 1

    # Build fog regions
    regions = []
    for key, cell_list in region_cells.items():
        # Get dominant primitive per axis
        dominant = {}
        for axis, counter in region_primitives[key].items():
            dominant[axis] = counter.most_common(1)[0][0]

        regions.append(
            FogRegion(
                key=key,
                label=_generate_region_label(cell_list[0]),
                charted=True,
                cell_count=len(cell_list),
                dominant_primitives=dominant,
            )
        )

    # Also include planned but uncharted regions from structural_voids.jsonl
    voids_path = root / "structural_voids.jsonl"
    if voids_path.exists():
        import json

        voids_by_region: dict[str, int] = defaultdict(int)
        for line in voids_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            void = json.loads(line)
            key = ",".join(
                f"{axis}={void.get(axis, 'unknown')}"
                for axis in ("dynamics", "credit", "update", "topology")
            )
            voids_by_region[key] += 1

        for key, count in voids_by_region.items():
            if key not in region_cells:
                # This is a planned but uncharted region
                parts = key.split(",")
                dominant = {p.split("=")[0]: p.split("=")[1] for p in parts}
                label = " × ".join(
                    {
                        "EnergyMinimization": "EnergyMin",
                        "PredictiveSettling": "PredSettle",
                        "InstantaneousPass": "Instant",
                        "SpikeIntegration": "Spike",
                        "ThermodynamicContrast": "Thermo",
                        "RandomProjectionsCredit": "RandProj",
                        "LocalGoodnessCredit": "LocalGood",
                        "TargetInversionCredit": "TargetInv",
                        "TemporalTraceCredit": "TempTrace",
                        "HomeostaticCredit": "Homeo",
                        "EuclideanUpdate": "Euclid",
                        "RiemannianOrthogonalUpdate": "Riemann",
                        "SpectralConstrainedUpdate": "Spectral",
                        "NaturalGradientUpdate": "NatGrad",
                        "ElasticConsolidationUpdate": "Elastic",
                        "FeedforwardDAG": "FF",
                        "RecurrentAttractor": "Recurrent",
                        "TileMesh": "Tile",
                        "FabricPC": "Fabric",
                        "SpatialLattice3D": "Lattice3D",
                        "NTM": "NTM",
                        "NCA": "NCA",
                    }.get(p.split("=")[1], p.split("=")[1])
                    for p in parts
                )
                regions.append(
                    FogRegion(
                        key=key,
                        label=label,
                        charted=False,
                        cell_count=0,
                        dominant_primitives=dominant,
                    )
                )

    total_planned = len(regions)
    total_charted = sum(1 for r in regions if r.charted)
    coverage_pct = (100.0 * total_charted / total_planned) if total_planned > 0 else 0.0

    return FogOfWar(
        regions=tuple(regions),
        total_planned=total_planned,
        total_charted=total_charted,
        coverage_pct=coverage_pct,
    )


def get_charted_regions(root: Path) -> list[str]:
    """Get list of charted region keys (for recognition projector)."""
    fog = compute_fog_of_war(root)
    return [r.key for r in fog.regions if r.charted]


def get_fog_overlay_data(root: Path) -> list[dict]:
    """Get fog-of-war data formatted for map overlay rendering."""
    fog = compute_fog_of_war(root)
    return [
        {
            "key": r.key,
            "label": r.label,
            "charted": r.charted,
            "cell_count": r.cell_count,
            "opacity": 1.0 if r.charted else 0.3,  # Fogged regions are semi-transparent
            "color": None if r.charted else "#999999",  # Fogged = grey
        }
        for r in fog.regions
    ]
