/** Layout presets as LayoutSpec (TODO72 P2 / TODO74 P11.1). */

import { dockviewHost } from "./layout/dockview-host.js";
import type { LayoutNode, LayoutSpec, Size } from "./layout/types.js";

export type Preset = "watch" | "audit" | "drive" | "free";

/** Stage panel with ratio-based sizing (centre pane ≥ 55% × 55%). */
const stage = (view = "space"): LayoutNode => ({
  kind: "panel",
  type: "stage",
  title: "3D Stage",
  state: { view },
  // At 1920px: 1300px = 67.7% (leaving 300+320 for sides)
  // At 1080px main row (86%): stage height = 55% of 1080 = 594px = 64% of main row
  size: { ratio: 0.677, width: 1280, height: 720 },
});

/** Left column: legend + control-panel (clamped 280–420px).
 * Ratio 0.293 gives ~300px at 1024, ~422px at 1440, ~562px at 1920.
 * Panel minPx constrains the column width in Dockview's grid. */
const leftColumn = (): LayoutNode => ({
  kind: "split",
  direction: "column",
  size: { ratio: 0.293, minPx: 280, maxPx: 420, width: 1920, height: 1080 },
  children: [
    { kind: "panel", type: "discovery-legend", title: "Discovery Map", size: { ratio: 0.5, minPx: 280, width: 300, height: 540 } },
    { kind: "panel", type: "control-panel", title: "Control Panel", size: { ratio: 0.5, minPx: 280, width: 300, height: 540 } },
  ],
});

/** Right column for Audit: HUD only (clamped 280–420px).
 * Ratio 0.195 gives ~200px at 1024, ~280px at 1440, ~374px at 1920. */
const rightColumnAudit = (): LayoutNode => ({
  kind: "split",
  direction: "column",
  size: { ratio: 0.195, minPx: 280, maxPx: 420, width: 1920, height: 1080 },
  children: [
    { kind: "panel", type: "hud", title: "Mission Control", size: { ratio: 1, minPx: 280, width: 320, height: 1080 } },
  ],
});

/** Right column for Drive: HUD + Charts (clamped 280–420px). */
const rightColumnDrive = (): LayoutNode => ({
  kind: "split",
  direction: "column",
  size: { ratio: 0.195, minPx: 280, maxPx: 420, width: 1920, height: 1080 },
  children: [
    { kind: "panel", type: "hud", title: "Mission Control", size: { ratio: 0.25, minPx: 280, width: 320, height: 270 } },
    { kind: "panel", type: "pareto-chart", title: "Pareto", size: { ratio: 0.25, minPx: 280, width: 320, height: 270 } },
    { kind: "panel", type: "ablation-chart", title: "Ablation", size: { ratio: 0.25, minPx: 280, width: 320, height: 270 } },
    { kind: "panel", type: "variability-chart", title: "Variability", size: { ratio: 0.25, minPx: 280, width: 320, height: 270 } },
  ],
});

/** Right column for Free: HUD + Charts (same as Drive). */
const rightColumn = (): LayoutNode => rightColumnDrive();

/** Bottom row: control-bar + caption + live-rail (clamped 110–180px). */
const bottomRow = (): LayoutNode => ({
  kind: "split",
  direction: "row",
  size: { ratio: 0.135, minPx: 110, maxPx: 180, width: 1920, height: 1080 },
  children: [
    { kind: "panel", type: "control-bar", title: "Control Bar", size: { ratio: 0.33, minPx: 110, width: 640, height: 140 } },
    { kind: "panel", type: "caption", title: "Caption", size: { ratio: 0.34, minPx: 110, width: 640, height: 140 } },
    { kind: "panel", type: "live-rail", title: "Live Rail", size: { ratio: 0.33, minPx: 110, width: 640, height: 140 } },
  ],
});

const mainRow = (rightCol: LayoutNode): LayoutNode => ({
  kind: "split",
  direction: "row",
  size: { ratio: 0.87, width: 1920, height: 940 },
  children: [leftColumn(), stage(), rightCol],
});

const fullLayout = (rightCol: LayoutNode): LayoutNode[] => [
  {
    kind: "split",
    direction: "column",
    size: { ratio: 1, width: 1920, height: 1080 },
    children: [mainRow(rightCol), bottomRow()],
  },
];

const PRESET_SPECS: Record<Preset, LayoutSpec> = {
  watch: {
    version: 1,
    // Stage + Legend + Control Panel (left), NO right column
    // Control Bar + Caption + Live Rail (bottom)
    nodes: [
      {
        kind: "split",
        direction: "column",
        size: { ratio: 1, width: 1920, height: 1080 },
        children: [
          {
            kind: "split",
            direction: "row",
            size: { ratio: 0.87, width: 1920, height: 940 },
            children: [
              leftColumn(),
              stage(),
            ],
          },
          bottomRow(),
        ],
      },
    ],
  },
  audit: {
    version: 1,
    // Watch + HUD (right column)
    nodes: fullLayout(rightColumnAudit()),
  },
  drive: {
    version: 1,
    // Audit + Charts (Pareto, Ablation, Variability) in right column
    nodes: fullLayout(rightColumnDrive()),
  },
  free: {
    version: 1,
    // Everything: left + stage + right (HUD + charts) + bottom + floating legend
    nodes: [
      ...fullLayout(rightColumn()),
      {
        kind: "float",
        panel: { kind: "panel", type: "discovery-legend", title: "Discovery Map" },
        rect: { x: 1200, y: 120, width: 420, height: 360 },
      },
    ],
  },
};

let currentPreset: Preset = "watch";

export function applyPreset(preset: Preset): void {
  const spec = PRESET_SPECS[preset];
  if (!spec) return;
  currentPreset = preset;
  dockviewHost.applySpec(spec);
}

export function getCurrentPreset(): Preset {
  return currentPreset;
}

export function cyclePreset(): void {
  const presets: Preset[] = ["watch", "audit", "drive", "free"];
  const idx = presets.findIndex((p) => p === currentPreset);
  applyPreset(presets[(idx + 1) % presets.length]);
}

export function reset(): void {
  applyPreset("watch");
}

export function applyWorkspace(id: string): void {
  applyPreset(id as Preset);
}

export function buildPresetSwitcher(): HTMLElement {
  const container = document.createElement("div");
  container.style.cssText = `display: flex; gap: 2px;`;
  for (const p of ["watch", "audit", "drive"] as Preset[]) {
    const btn = document.createElement("button");
    btn.textContent = p[0].toUpperCase();
    btn.title = p;
    btn.style.cssText = `
      flex: 1; padding: 4px 8px; background: var(--bg-tertiary);
      border: 1px solid var(--border); border-radius: 4px;
      color: var(--text-secondary); font-size: 11px; cursor: pointer;
    `;
    if (p === currentPreset) {
      btn.style.background = "var(--bg-primary)";
      btn.style.color = "var(--text-primary)";
      btn.style.borderColor = "var(--border-bright)";
    }
    btn.addEventListener("click", () => { applyPreset(p); buildPresetSwitcher(); });
    container.appendChild(btn);
  }
  return container;
}