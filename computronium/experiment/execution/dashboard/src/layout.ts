/** Layout presets as LayoutSpec (TODO72 P2). */

import { dockviewHost } from "./layout/dockview-host.js";
import type { LayoutNode, LayoutSpec, Size } from "./layout/types.js";

export type Preset = "watch" | "audit" | "drive" | "free";

/** Stage panel with ratio-based sizing (centre pane ≥ 55% × 55%). */
const stage = (view = "space"): LayoutNode => ({
  kind: "panel",
  type: "stage",
  title: "3D Stage",
  state: { view },
  // No absolute size — stage claims remaining space via flex
  size: { ratio: 1, width: 1280, height: 720 },
});

/** Left column: legend + control-panel (clamped 300–360px). */
const leftColumn = (): LayoutNode => ({
  kind: "split",
  direction: "column",
  size: { ratio: 0.175, minPx: 300, maxPx: 360, width: 300, height: 1080 },
  children: [
    { kind: "panel", type: "discovery-legend", title: "Discovery Map", size: { ratio: 0.5, width: 300, height: 540 } },
    { kind: "panel", type: "control-panel", title: "Control Panel", size: { ratio: 0.5, width: 300, height: 540 } },
  ],
});

/** Right column: hud + pareto + ablation + variability (clamped 320–400px). */
const rightColumn = (): LayoutNode => ({
  kind: "split",
  direction: "column",
  size: { ratio: 0.18, minPx: 320, maxPx: 400, width: 320, height: 1080 },
  children: [
    { kind: "panel", type: "hud", title: "Mission Control", size: { ratio: 0.25, width: 320, height: 270 } },
    { kind: "panel", type: "pareto-chart", title: "Pareto", size: { ratio: 0.25, width: 320, height: 270 } },
    { kind: "panel", type: "ablation-chart", title: "Ablation", size: { ratio: 0.25, width: 320, height: 270 } },
    { kind: "panel", type: "variability-chart", title: "Variability", size: { ratio: 0.25, width: 320, height: 270 } },
  ],
});

/** Bottom row: control-bar + caption + live-rail (clamped 120–160px). */
const bottomRow = (): LayoutNode => ({
  kind: "split",
  direction: "row",
  size: { ratio: 0.14, minPx: 120, maxPx: 160, width: 1920, height: 120 },
  children: [
    { kind: "panel", type: "control-bar", title: "Control Bar", size: { ratio: 0.33, width: 640, height: 120 } },
    { kind: "panel", type: "caption", title: "Caption", size: { ratio: 0.34, width: 640, height: 120 } },
    { kind: "panel", type: "live-rail", title: "Live Rail", size: { ratio: 0.33, width: 640, height: 120 } },
  ],
});

const PRESET_SPECS: Record<Preset, LayoutSpec> = {
  watch: {
    version: 1,
    nodes: [
      {
        kind: "split",
        direction: "row",
        size: { ratio: 1, width: 1920, height: 1080 },
        children: [
          leftColumn(),
          stage(),
          rightColumn(),
        ],
      },
      bottomRow(),
    ],
  },
  audit: {
    version: 1,
    nodes: [
      {
        kind: "split",
        direction: "row",
        size: { ratio: 1, width: 1920, height: 1080 },
        children: [
          leftColumn(),
          stage(),
          rightColumn(),
        ],
      },
      bottomRow(),
    ],
  },
  drive: {
    version: 1,
    nodes: [
      {
        kind: "split",
        direction: "row",
        size: { ratio: 1, width: 1920, height: 1080 },
        children: [
          leftColumn(),
          stage(),
          {
            kind: "split",
            direction: "column",
            size: { ratio: 0.18, minPx: 320, maxPx: 400, width: 320, height: 1080 },
            children: [
              { kind: "panel", type: "control-panel", title: "Control Panel", size: { ratio: 0.5, width: 320, height: 540 } },
              { kind: "panel", type: "hud", title: "Mission Control", size: { ratio: 0.25, width: 320, height: 270 } },
              { kind: "panel", type: "live-rail", title: "Live Rail", size: { ratio: 0.25, width: 320, height: 270 } },
            ],
          },
        ],
      },
      bottomRow(),
    ],
  },
  free: {
    version: 1,
    nodes: [
      {
        kind: "split",
        direction: "row",
        size: { ratio: 1, width: 1920, height: 1080 },
        children: [
          leftColumn(),
          stage(),
          rightColumn(),
        ],
      },
      bottomRow(),
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