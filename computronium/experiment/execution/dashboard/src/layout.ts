/** Layout presets as LayoutSpec (TODO72 P2). */

import { dockviewHost } from "./layout/dockview-host.js";
import type { LayoutNode, LayoutSpec } from "./layout/types.js";

export type Preset = "watch" | "audit" | "drive" | "free";

const stage = (view = "space"): LayoutNode => ({
  kind: "panel",
  type: "stage",
  title: "3D Stage",
  state: { view },
  size: { width: 1280, height: 720 },
});

const PRESET_SPECS: Record<Preset, LayoutSpec> = {
  watch: {
    version: 1,
    nodes: [
      {
        kind: "split",
        direction: "row",
        children: [
          {
            kind: "split",
            direction: "column",
            children: [stage(), { kind: "panel", type: "caption", title: "Caption" }],
          },
          {
            kind: "tabs",
            panels: [
              { kind: "panel", type: "hud", title: "Mission Control" },
              { kind: "panel", type: "discovery-legend", title: "Discovery Map" },
              { kind: "panel", type: "live-rail", title: "Live Rail" },
            ],
          },
        ],
      },
    ],
  },
  audit: {
    version: 1,
    nodes: [
      {
        kind: "split",
        direction: "row",
        children: [
          stage(),
          {
            kind: "tabs",
            panels: [
              { kind: "panel", type: "pareto-chart", title: "Pareto" },
              { kind: "panel", type: "ablation-chart", title: "Ablation" },
              { kind: "panel", type: "variability-chart", title: "Variability" },
              { kind: "panel", type: "discovery-legend", title: "Discovery Map" },
            ],
          },
        ],
      },
    ],
  },
  drive: {
    version: 1,
    nodes: [
      {
        kind: "split",
        direction: "row",
        children: [
          {
            kind: "split",
            direction: "column",
            children: [stage(), { kind: "panel", type: "control-bar", title: "Control Bar" }],
          },
          {
            kind: "tabs",
            panels: [
              { kind: "panel", type: "control-panel", title: "Control Panel" },
              { kind: "panel", type: "hud", title: "Mission Control" },
              { kind: "panel", type: "live-rail", title: "Live Rail" },
            ],
          },
        ],
      },
    ],
  },
  free: {
    version: 1,
    nodes: [
      {
        kind: "split",
        direction: "row",
        children: [
          stage(),
          {
            kind: "tabs",
            panels: [
              { kind: "panel", type: "hud", title: "Mission Control" },
              { kind: "panel", type: "live-rail", title: "Live Rail" },
            ],
          },
        ],
      },
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