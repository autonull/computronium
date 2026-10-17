"""Generate the Computronium Consortium mark.

One geometry, two inks: six nodes on the six-axis hexagon around a referee at
the centre. No node is privileged, and no algorithm family appears in the mark.
The light and dark variants are the same paths, so they cannot diverge.

Usage::

    uv run python scripts/generate_consortium_mark.py
"""

from __future__ import annotations

import math
from pathlib import Path

MARK_SIZE = 192
CENTRE = MARK_SIZE / 2
RADIUS = 74
STROKE = 8
NODE_RADIUS = 8
CORE_RING_RADIUS = 21
CORE_RING_STROKE = 4
CORE_RADIUS = 8

INK: dict[str, str] = {"light": "#0f172a", "dark": "#e2e8f0"}
ASSET_DIR = Path(__file__).resolve().parents[1] / "docs" / "assets"


def _point(angle_degrees: float, radius: float) -> tuple[float, float]:
    angle = math.radians(angle_degrees)
    return CENTRE + radius * math.cos(angle), CENTRE + radius * math.sin(angle)


def _vertices() -> list[tuple[float, float]]:
    return [_point(-90 + 60 * step, RADIUS) for step in range(6)]


def render(variant: str) -> str:
    """Return the SVG source for ``variant`` (``"light"`` or ``"dark"``)."""
    ink = INK[variant]
    vertices = _vertices()
    points = " ".join(f"{x:.1f},{y:.1f}" for x, y in vertices)
    nodes = "\n".join(
        f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{NODE_RADIUS}" fill="{ink}"/>'
        for x, y in vertices
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {MARK_SIZE} {MARK_SIZE}"'
        ' role="img" aria-label="Computronium Consortium">\n'
        "  <title>Computronium Consortium</title>\n"
        f'  <polygon points="{points}" fill="none" stroke="{ink}"'
        f' stroke-width="{STROKE}" stroke-linejoin="round"/>\n'
        f"{nodes}\n"
        f'  <circle cx="{CENTRE}" cy="{CENTRE}" r="{CORE_RING_RADIUS}"'
        f' fill="none" stroke="{ink}" stroke-width="{CORE_RING_STROKE}"/>\n'
        f'  <circle cx="{CENTRE}" cy="{CENTRE}" r="{CORE_RADIUS}" fill="{ink}"/>\n'
        "</svg>\n"
    )


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    for variant in INK:
        path = ASSET_DIR / f"consortium-mark-{variant}.svg"
        path.write_text(render(variant), encoding="utf-8")
        print(path.relative_to(ASSET_DIR.parents[1]))


if __name__ == "__main__":
    main()
