/** Simple layout — three preset arrangements, no persistence. */

import { panels } from "./panels.js";
import { viewSwitcher } from "./stage/switcher.js";

export type Preset = "watch" | "audit" | "drive";

interface PresetDef {
  id: Preset;
  viewId: string;
  openPanels: string[];
}

const PRESETS: PresetDef[] = [
  { id: "watch", viewId: "space", openPanels: ["control-bar", "live-rail", "caption", "legend"] },
  { id: "audit", viewId: "ledger", openPanels: ["control-bar", "live-rail", "caption", "legend", "plotter-pareto", "plotter-ablation", "plotter-variability"] },
  { id: "drive", viewId: "flow", openPanels: ["control-bar", "live-rail", "caption", "legend", "control-panel"] },
];

let currentPreset: Preset = "watch";

export function applyPreset(preset: Preset): void {
  const def = PRESETS.find((p) => p.id === preset);
  if (!def) return;
  currentPreset = preset;
  viewSwitcher.show(def.viewId);
  for (const panel of panels.list()) {
    const shouldOpen = def.openPanels.includes(panel.id);
    if (panel.isOpen() !== shouldOpen) panel.toggle();
  }
}

export function getCurrentPreset(): Preset {
  return currentPreset;
}

export function cyclePreset(): void {
  const idx = PRESETS.findIndex((p) => p.id === currentPreset);
  applyPreset(PRESETS[(idx + 1) % PRESETS.length].id);
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
  for (const p of PRESETS) {
    const btn = document.createElement("button");
    btn.textContent = p.id[0].toUpperCase();
    btn.title = p.id;
    btn.style.cssText = `
      flex: 1; padding: 4px 8px; background: var(--bg-tertiary);
      border: 1px solid var(--border); border-radius: 4px;
      color: var(--text-secondary); font-size: 11px; cursor: pointer;
    `;
    if (p.id === currentPreset) {
      btn.style.background = "var(--bg-primary)";
      btn.style.color = "var(--text-primary)";
      btn.style.borderColor = "var(--border-bright)";
    }
    btn.addEventListener("click", () => { applyPreset(p.id); buildPresetSwitcher(); });
    container.appendChild(btn);
  }
  return container;
}