#!/usr/bin/env python3
"""Generate color palette from single source for Python, TypeScript, and CSS.

Single source of truth for dashboard colors. Run to regenerate all three outputs.
"""

from __future__ import annotations

from pathlib import Path

# ─── Single Source: PALETTE_SOURCE ──────────────────────────────────────
# Edit this dict to add/change colors. Keys are semantic names used everywhere.

PALETTE_SOURCE: dict[str, str] = {
    # ── Background & UI ────────────────────────────────────────────────
    "bg": "#0a0e14",
    "bg_secondary": "#111820",
    "bg_tertiary": "#1a2330",
    "border": "#2a3a4a",
    "border_bright": "#3a4a5a",
    "text_primary": "#e8ecf0",
    "text_secondary": "#8b98a8",
    "text_muted": "#5a6a7a",
    # ── Credit Arm Colors ──────────────────────────────────────────────
    "gradient": "#58a6ff",
    "pepita": "#d4a843",
    "random_projections": "#f78166",
    "local_goodness": "#a371f7",
    "thermodynamic_contrast": "#3fb950",
    "contrastive": "#ff7b72",
    "hebbian": "#79c0ff",
    "predictive": "#d2a8ff",
    # ── Substrate Colors ───────────────────────────────────────────────
    "digital": "#58a6ff",
    "memristive": "#d4a843",
    "neuromorphic": "#f78166",
    "photonic": "#a371f7",
    "complex": "#3fb950",
    "analog": "#ff7b72",
    "quantum": "#79c0ff",
    "spiking": "#d2a8ff",
    # ── Geometry Colors ────────────────────────────────────────────────
    "feedforward": "#58a6ff",
    "recurrent": "#d4a843",
    "ntm": "#f78166",
    "nca": "#a371f7",
    "spatial_lattice_3d": "#3fb950",
    "liquid": "#ff7b72",
    "modular": "#79c0ff",
    # ── Dynamics Colors ────────────────────────────────────────────────
    "instantaneous": "#58a6ff",
    "energy_minimization": "#d4a843",
    "predictive_settling": "#f78166",
    "lazy": "#a371f7",
    "homeostatic": "#3fb950",
    "oscillatory": "#ff7b72",
    # ── Plasticity Colors ─────────────────────────────────────────────
    "null": "#8b98a8",
    "routing": "#58a6ff",
    "fast_weights": "#d4a843",
    "substrate_coupled": "#f78166",
    "hebbian_plasticity": "#a371f7",
    "stdp": "#3fb950",
    # ── Update Rule Colors ────────────────────────────────────────────
    "euclidean": "#58a6ff",
    "adam": "#d4a843",
    "muon": "#f78166",
    "rmsprop": "#a371f7",
    "sgd": "#3fb950",
    "lars": "#ff7b72",
    # ── Semantic Status Colors ────────────────────────────────────────
    "measured": "#d4a843",  # glowing pillars
    "legal_unmeasured": "#58a6ff",  # wireframe cubes
    "void": "#f85149",  # red X markers
    "pareto": "#e8ecf0",  # Pareto frontier highlight (white: no arm is white)
    "chance_line": "#f85149",  # chance level line
    "gpu": "#58a6ff",
    "cpu": "#3fb950",
    "memory": "#d29922",
    "ok": "#3fb950",
    "warn": "#d29922",
    "error": "#f85149",
    # ── Cell States ────────────────────────────────────────────────────
    "passed": "#3fb950",
    "insufficient": "#d29922",
    "rejected": "#f85149",
    "promoted": "#a371f7",
    # ── Value Ramp (low → mid → high) ──────────────────────────────────
    "ramp_low": "#1f3a5f",
    "ramp_mid": "#58a6ff",
    "ramp_high": "#d4a843",
}

# ─── Derived Computed Values ──────────────────────────────────────────
# CSS variables (kebab-case)
CSS_VARS = {k.replace("_", "-"): v for k, v in PALETTE_SOURCE.items()}

# Arm color map for quick lookup
ARM_COLORS = {
    "gradient": PALETTE_SOURCE["gradient"],
    "pepita": PALETTE_SOURCE["pepita"],
    "random_projections": PALETTE_SOURCE["random_projections"],
    "local_goodness": PALETTE_SOURCE["local_goodness"],
    "thermodynamic_contrast": PALETTE_SOURCE["thermodynamic_contrast"],
    "contrastive": PALETTE_SOURCE["contrastive"],
    "hebbian": PALETTE_SOURCE["hebbian"],
    "predictive": PALETTE_SOURCE["predictive"],
}

# Substrate color map
SUBSTRATE_COLORS = {
    "digital": PALETTE_SOURCE["digital"],
    "memristive": PALETTE_SOURCE["memristive"],
    "neuromorphic": PALETTE_SOURCE["neuromorphic"],
    "photonic": PALETTE_SOURCE["photonic"],
    "complex": PALETTE_SOURCE["complex"],
    "analog": PALETTE_SOURCE["analog"],
    "quantum": PALETTE_SOURCE["quantum"],
    "spiking": PALETTE_SOURCE["spiking"],
}


def generate_python() -> str:
    """Generate Python palette module."""
    lines = [
        '"""Generated color palette — DO NOT EDIT. Run scripts/generate_palette.py."""',
        "",
        "# ─── Semantic Colors ───────────────────────────────────────────",
    ]
    for key, value in PALETTE_SOURCE.items():
        lines.append(f'{key.upper()} = "{value}"')
    lines.append("")
    lines.append("# ─── Arm Color Map ────────────────────────────────────────────")
    lines.append("ARM_COLORS: dict[str, str] = {")
    for k, v in ARM_COLORS.items():
        lines.append(f'    "{k}": "{v}",')
    lines.append("}")
    lines.append("")
    lines.append("# ─── Substrate Color Map ──────────────────────────────────────")
    lines.append("SUBSTRATE_COLORS: dict[str, str] = {")
    for k, v in SUBSTRATE_COLORS.items():
        lines.append(f'    "{k}": "{v}",')
    lines.append("}")
    lines.append("")
    lines.append("# ─── Full Palette Dict ─────────────────────────────────────────")
    lines.append("PALETTE: dict[str, str] = {")
    for k, v in PALETTE_SOURCE.items():
        lines.append(f'    "{k}": "{v}",')
    lines.append("}")
    return "\n".join(lines)


def generate_typescript() -> str:
    """Generate TypeScript palette module."""
    lines = [
        "// Generated color palette — DO NOT EDIT. Run scripts/generate_palette.py.",
        "",
        "// ─── Semantic Colors ───────────────────────────────────────────",
    ]
    for key, value in PALETTE_SOURCE.items():
        lines.append(f'export const {key.upper()} = "{value}";')
    lines.append("")
    lines.append("// ─── Arm Color Map ────────────────────────────────────────────")
    lines.append("export const ARM_COLORS: Record<string, string> = {")
    for k, v in ARM_COLORS.items():
        lines.append(f'  "{k}": "{v}",')
    lines.append("};")
    lines.append("")
    lines.append("// ─── Substrate Color Map ──────────────────────────────────────")
    lines.append("export const SUBSTRATE_COLORS: Record<string, string> = {")
    for k, v in SUBSTRATE_COLORS.items():
        lines.append(f'  "{k}": "{v}",')
    lines.append("};")
    lines.append("")
    lines.append("// ─── Full Palette Object ───────────────────────────────────────")
    lines.append("export const PALETTE: Record<string, string> = {")
    for k, v in PALETTE_SOURCE.items():
        lines.append(f'  "{k}": "{v}",')
    lines.append("};")
    lines.append("")
    lines.append("// Type helper for arm names")
    lines.append("export type ArmName = keyof typeof ARM_COLORS;")
    lines.append("export type SubstrateName = keyof typeof SUBSTRATE_COLORS;")
    return "\n".join(lines)


def generate_css() -> str:
    """Generate CSS variables."""
    lines = [
        "/* Generated color palette — DO NOT EDIT. Run scripts/generate_palette.py. */",
        "",
        ":root {",
    ]
    for key, value in CSS_VARS.items():
        lines.append(f"  --{key}: {value};")
    lines.append("}")
    return "\n".join(lines)


def main() -> None:
    root = Path(__file__).resolve().parents[1]

    # Python output
    py_out = root / "computronium" / "visualization" / "_palette.py"
    py_out.parent.mkdir(parents=True, exist_ok=True)
    py_out.write_text(generate_python(), encoding="utf-8")
    print(f"✓ Generated {py_out}")

    # TypeScript output
    ts_out = (
        root
        / "computronium"
        / "experiment"
        / "execution"
        / "dashboard"
        / "src"
        / "palette.ts"
    )
    ts_out.parent.mkdir(parents=True, exist_ok=True)
    ts_out.write_text(generate_typescript(), encoding="utf-8")
    print(f"✓ Generated {ts_out}")

    # CSS output
    css_out = (
        root
        / "computronium"
        / "experiment"
        / "execution"
        / "dashboard"
        / "templates"
        / "static"
        / "css"
        / "palette.css"
    )
    css_out.parent.mkdir(parents=True, exist_ok=True)
    css_out.write_text(generate_css(), encoding="utf-8")
    print(f"✓ Generated {css_out}")

    print("✓ Palette generation complete")


if __name__ == "__main__":
    main()
