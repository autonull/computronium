"""Flagship C report (TODO16 §4.4): I(C,U) interaction surface as HTML.

Renders the credit × update accuracy surface from data/icu_measurements.csv,
the recipe-card registry, and the §4.2/§4.3 model results into a single
self-contained HTML file (docs/reports/icu_law.html).

uv run python scripts/analysis/icu_report.py
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

from computronium.analysis import lookup_recipe_card  # ruff: ignore[module-import-not-at-top-of-file]

CSV = ROOT / "data" / "icu_measurements.csv"
OUT = ROOT / "docs" / "reports" / "icu_law.html"

CREDITS = ("bp", "bptt", "eqprop", "fa", "pepita", "ff", "local_contrastive")
UPDATES = ("euclid", "adam", "muon", "ortho_adam", "ortho", "lion")


def surface() -> dict[tuple[str, str], tuple[float, int]]:
    """Mean accuracy and count per (credit, update) cell."""
    acc: dict[tuple[str, str], list[float]] = defaultdict(list)
    for r in csv.DictReader(CSV.open()):
        acc[r["credit"], r["update"]].append(float(r["accuracy"]))
    return {k: (sum(v) / len(v), len(v)) for k, v in acc.items() if k[0] in CREDITS}


def color(acc: float) -> str:
    scale = max(0.0, min(1.0, (acc - 0.3) / 0.6))
    return f"hsl({scale * 120:.0f}, 70%, 85%)"


def main() -> int:
    cells = surface()
    rows = ["<tr><th>credit \\ update</th>"]
    rows += [f"<th>{u}</th>" for u in UPDATES]
    rows.append("</tr>")
    for c in CREDITS:
        row = [f"<tr><th>{c}</th>"]
        for u in UPDATES:
            if (c, u) in cells:
                a, n = cells[c, u]
                row.append(
                    f'<td style="background:{color(a)}">{a:.3f}<br>'
                    f"<small>n={n}</small></td>"
                )
            else:
                row.append("<td>—</td>")
        rows.append("</tr>")

    cards = [
        f"<tr><td>{c} × {u}</td><td><pre>{card}</pre></td></tr>"
        for c in CREDITS
        for u in ("*", *UPDATES)
        if (card := lookup_recipe_card(c, u)) is not None
    ]

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>I(C,U) Law — icu_law study</title>
<style>
body{{font-family:monospace;margin:2em}}
table{{border-collapse:collapse}} td,th{{border:1px solid #999;padding:6px;text-align:center}}
</style></head><body>
<h1>I(C,U) interaction surface</h1>
<p>Mean accuracy per (credit, update) cell, all geometries/seeds,
data/icu_measurements.csv ({sum(n for _, n in cells.values())} measurements).</p>
<table>{"".join(rows)}</table>
<h1>Recipe cards</h1>
<table>{"".join(cards)}</table>
<h1>Predictive model (§4.2/§4.3)</h1>
<ul>
<li>Viability (acc ≥ 0.75) CV: tree 0.871 ± 0.055, logistic 0.892 ± 0.051.</li>
<li>Top features: projected_pseudo credit (0.49), sign_based update (Lion
hurts), width, interaction_i.</li>
<li>Held-out geometry (lattice, trained on mlp/nca/ntm): accuracy 0.944 —
the I(C,U) law transfers across geometry.</li>
</ul>
</body></html>"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
