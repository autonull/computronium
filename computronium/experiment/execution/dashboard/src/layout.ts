/** Layout presets as LayoutSpec (TODO72 P2). */

import { dockviewHost } from "./layout/dockview-host.js";
import type { LayoutSpec } from "./layout/types.js";

export type Preset = "watch" | "audit" | "drive";

const PRESET_SPECS: Record<Preset, LayoutSpec> = {
  watch: {
    version: 1,
    nodes: [
      { kind: "panel", type: "control-bar", title: "Control Bar" },
      { kind: "panel", type: "live-rail", title: "Live Rail" },
      { kind: "panel", type: "caption", title: "Caption" },
      { kind: "panel", type: "discovery-legend", title: "Discovery Legend" },
      { kind: "panel", type: "hud", title: "Mission Control" },
    ],
  },
  audit: {
    version: 1,
    nodes: [
      { kind: "panel", type: "control-bar", title: "Control Bar" },
      { kind: "panel", type: "live-rail", title: "Live Rail" },
      { kind: "panel", type: "caption", title: "Caption" },
      { kind: "panel", type: "discovery-legend", title: "Discovery Legend" },
      { kind: "panel", type: "pareto-chart", title: "Pareto" },
      { kind: "panel", type: "ablation-chart", title: "Ablation" },
      { kind: "panel", type: "variability-chart", title: "Variability" },
    ],
  },
  drive: {
    version: 1,
    nodes: [
      { kind: "panel", type: "control-bar", title: "Control Bar" },
      { kind: "panel", type: "live-rail", title: "Live Rail" },
      { kind: "panel", type: "caption", title: "Caption" },
      { kind: "panel", type: "discovery-legend", title: "Discovery Legend" },
      { kind: "panel", type: "control-panel", title: "Control Panel" },
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
  const presets: Preset[] = ["watch", "audit", "drive"];
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