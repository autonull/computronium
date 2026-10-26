/** Discovery Legend — run picker, axis picker, arm legend, actions. */

import { workspaceStore } from "./stores/workspace.js";
import { runSelection, type RunMetrics } from "./run-selection.js";
import { stageState } from "./stage/store.js";
import { PALETTE } from "./colors.js";
import type { JsonValue } from "./layout/types.js";
import type { AxisSelection } from "./layout/types.js";
import type { WorkspaceStore as WorkspaceStoreInterface } from "./layout/types.js";
import { registry } from "./components/registry.js";
import { panels, registerDisplayPanel } from "./panels.js";
import { createPanelShell } from "./shell.js";
import { PANEL_KEYS } from "./keys.js";
import type { Component } from "./components/registry.js";

export function createLegendBody(): string {
  return `
    <style>
      .legend-chip { display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 12px; font-size: 10px; color: var(--text-secondary); }
      .legend-chip .dot { width: 8px; height: 8px; border-radius: 50%; }
      .legend-summary { display: flex; gap: 12px; flex-wrap: wrap; margin: 8px 0; padding: 8px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 6px; font-size: 10px; }
      .legend-summary-item { display: flex; align-items: center; gap: 4px; }
      .legend-actions { display: flex; gap: 6px; margin-top: 8px; }
      .legend-btn { padding: 4px 10px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 4px; font-size: 10px; color: var(--text-secondary); cursor: pointer; }
      .legend-btn:hover { background: var(--border); color: var(--text-primary); }
      .legend-btn.primary { background: var(--gradient)22; border-color: var(--gradient)66; color: var(--gradient); }
      .legend-btn.primary:hover { background: var(--gradient)33; border-color: var(--gradient); }
      .legend-axes { display: flex; gap: 4px; margin-bottom: 8px; flex-wrap: wrap; }
      .legend-axis-btn { padding: 2px 6px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 4px; font-size: 10px; color: var(--text-secondary); cursor: pointer; }
      .legend-axis-btn:hover { background: var(--border); color: var(--text-primary); }
      .legend-axis-btn.active { background: var(--gradient)22; border-color: var(--gradient)66; color: var(--gradient); }
    </style>
    <div id="legend-title" style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
      <span style="font-weight: 600; color: var(--text-primary);">Discovery Map</span>
      <span id="legend-cell-count" style="font-size: 11px; color: var(--text-muted);"></span>
    </div>
    <div id="legend-empty-state" class="empty-state" style="display: none; text-align: center; padding: 24px 12px; color: var(--text-muted); font-size: 11px;">
      <div class="empty-state-icon" style="font-size: 24px; margin-bottom: 8px; opacity: 0.5;">▦</div>
      <div class="empty-state-title">No run selected</div>
      <div class="empty-state-message">Pick a run from the dropdown below to see its declared space</div>
    </div>
    <div id="legend-view" style="display: none;"></div>
    <div id="legend-marks" style="display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px;">
      <div class="legend-item" style="display: flex; align-items: center; gap: 8px; font-size: 11px;">
        <div style="width: 14px; height: 14px; background: var(--measured); border-radius: 3px; box-shadow: 0 0 10px var(--measured);"></div>
        <span>Measured — glowing pillar</span>
      </div>
      <div class="legend-item" style="display: flex; align-items: center; gap: 8px; font-size: 11px;">
        <div style="width: 14px; height: 14px; background: var(--insufficient); border-radius: 3px;"></div>
        <span>Insufficient — translucent</span>
      </div>
      <div class="legend-item" style="display: flex; align-items: center; gap: 8px; font-size: 11px;">
        <div style="width: 14px; height: 14px; background: var(--rejected); border-radius: 3px;"></div>
        <span>Rejected — dark pillar</span>
      </div>
      <div class="legend-item" style="display: flex; align-items: center; gap: 8px; font-size: 11px;">
        <div style="width: 14px; height: 14px; background: var(--unmeasured); border: 1px dashed var(--border); border-radius: 3px;"></div>
        <span>Unmeasured — wireframe</span>
      </div>
    </div>
    <div id="legend-axes" class="legend-axes"></div>
    <div id="legend-arms" style="display: flex; flex-direction: column; gap: 4px; margin-bottom: 8px;"></div>
    <div class="legend-actions">
      <button class="legend-btn primary" data-act="replicate" title="Replicate (Shift+R)">Replicate</button>
      <button class="legend-btn" data-act="preregister" title="Preregister (Shift+P)">Preregister</button>
      <button class="legend-btn" data-act="quest" title="Quest (Shift+Q)">Quest</button>
    </div>
  `;
}

interface LegendOptions {
  runId: string | null;
  axes: AxisSelection;
  workspace: WorkspaceStoreInterface;
}

/** A legend bound to one root element and its own subscriptions. */
export class DiscoveryLegendView {
  private readonly emptyState: HTMLElement;
  private readonly view: HTMLElement;
  private readonly marks: HTMLElement;
  private readonly arms: HTMLElement;
  private readonly cellCount: HTMLElement;
  private readonly axesContainer: HTMLElement;
  private readonly replicanteBtn: HTMLButtonElement;
  private readonly preregisterBtn: HTMLButtonElement;
  private readonly questBtn: HTMLButtonElement;
  private readonly disposers: (() => void)[] = [];
  private options: LegendOptions;

  constructor(
    private readonly root: HTMLElement,
    options?: LegendOptions,
  ) {
    this.options = options ?? {
      runId: null,
      axes: { x: "credit", y: "geometry", z: "dynamics" },
      workspace: workspaceStore,
    };
    this.emptyState = this.query("#legend-empty-state");
    this.view = this.query("#legend-view");
    this.marks = this.query("#legend-marks");
    this.arms = this.query("#legend-arms");
    this.cellCount = this.query("#legend-cell-count");
    this.axesContainer = this.query("#legend-axes");
    this.replicanteBtn = this.query("[data-act=replicate]");
    this.preregisterBtn = this.query("[data-act=preregister]");
    this.questBtn = this.query("[data-act=quest]");

    this.disposers.push(
      this.options.workspace.onChange(() => this.render()),
      stageState.onChange((_change) => this.render()),
    );
    this.renderAxesPicker();
    this.render();
  }

  dispose(): void {
    for (const dispose of this.disposers) dispose();
    this.disposers.length = 0;
  }

  updateRunAndAxes(runId: string | null, axes: AxisSelection): void {
    this.options.runId = runId;
    this.options.axes = axes;
    this.renderAxesPicker();
    this.render();
  }

  private query<T extends HTMLElement>(selector: string): T {
    const el = this.root.querySelector<T>(selector);
    if (!el) throw new Error(`[DiscoveryLegend] missing element: ${selector}`);
    return el;
  }

  private renderAxesPicker(): void {
    const axesNames: Array<keyof AxisSelection> = ["x", "y", "z"];
    const availableAxes = ["credit", "geometry", "dynamics", "substrate", "plasticity", "update"];
    this.axesContainer.innerHTML = axesNames.map((axisKey) => `
      <div style="display: flex; flex-direction: column; gap: 2px; min-width: 80px;">
        <div style="font-size: 9px; text-transform: uppercase; color: var(--text-muted);">${axisKey.toUpperCase()}</div>
        <div style="display: flex; gap: 2px; flex-wrap: wrap;">
          ${availableAxes.map((axis) => `
            <button class="legend-axis-btn${this.options.axes[axisKey] === axis ? " active" : ""}" 
                    data-axis-key="${axisKey}" data-axis-value="${axis}"
                    title="Set ${axisKey} axis to ${axis}">
              ${axis}
            </button>
          `).join("")}
        </div>
      </div>
    `).join("");

    for (const btn of this.axesContainer.querySelectorAll<HTMLButtonElement>(".legend-axis-btn")) {
      btn.addEventListener("click", () => {
        const axisKey = btn.dataset.axisKey as keyof AxisSelection;
        const axisValue = btn.dataset.axisValue as AxisSelection[keyof AxisSelection];
        if (axisKey && axisValue) {
          this.options.workspace.setAxes({ ...this.options.axes, [axisKey]: axisValue });
        }
      });
    }
  }

  /** Public render for external sync (e.g., DiscoveryMap). */
  render(): void {
    const runId = this.options.runId ?? this.options.workspace.getSelectedRunId();
    const run = runSelection.selected;
    const space = stageState.space;
    const hasRun = run !== null;
    const hasSpace = space !== null;

    if (!hasRun || !hasSpace || !runId) {
      this.emptyState.style.display = "block";
      this.view.style.display = "none";
      this.marks.style.display = "none";
      this.arms.style.display = "none";
      this.cellCount.textContent = "";
      return;
    }

    this.emptyState.style.display = "none";
    this.view.style.display = "block";
    this.marks.style.display = "flex";
    this.arms.style.display = "flex";

    const records = run.records ?? [];
    const measured = records.filter((r) => r.status === "measured").length;
    this.cellCount.textContent = `${measured} / ${records.length} cells measured`;

    this.renderArms(space, run);
    this.updateActionButtons(run);
  }

  private renderArms(space: any, run: RunMetrics): void {
    const creditAxes = space.axes?.credit;
    if (!creditAxes || !Array.isArray(creditAxes) || creditAxes.length === 0) {
      this.arms.innerHTML = '<div style="font-size: 10px; color: var(--text-muted);">No credit arms</div>';
      return;
    }

    const records = run.records ?? [];
    const armData = new Map<string, { measured: number; total: number; color: string }>();

    creditAxes.forEach((arm: string) => {
      const color = (PALETTE as any)[`credit_${arm}`] || PALETTE.gradient;
      armData.set(arm, { measured: 0, total: 0, color });
    });

    records.forEach((r) => {
      const arm = r.coordinate?.credit;
      if (arm && armData.has(arm)) {
        const data = armData.get(arm)!;
        data.total++;
        if (r.status === "measured") data.measured++;
      }
    });

    this.arms.innerHTML = creditAxes
      .map((arm: string) => {
        const data = armData.get(arm)!;
        return `
          <div class="legend-chip">
            <span class="dot" style="background: ${data.color};"></span>
            <span>${arm}</span>
            <span style="color: var(--text-muted);">${data.measured}/${data.total}</span>
          </div>
        `;
      })
      .join("");
  }

  private updateActionButtons(run: RunMetrics): void {
    const hasSelection = runSelection.selected !== null;
    this.replicanteBtn.disabled = !hasSelection;
    this.preregisterBtn.disabled = !hasSelection;
    this.questBtn.disabled = !hasSelection;
  }
}

/** Legacy panel class for GoldenLayout (until P2). Not auto-registered. */
export class DiscoveryLegend implements Component {
  name = "DiscoveryLegend";
  private container: HTMLElement | null = null;
  private view: DiscoveryLegendView | null = null;

  async init(): Promise<void> {
    this.container = createPanelShell({
      id: "discovery-legend",
      title: "Discovery Map",
      glyph: "▦",
      key: PANEL_KEYS.legend,
      body: createLegendBody(),
      dock: "bottom",
      defaultOpen: true,
    });
    this.view = new DiscoveryLegendView(this.container);
    registerDisplayPanel(
      "discovery-legend",
      "Discovery Map",
      "▦",
      () => this.container,
      PANEL_KEYS.legend,
    );
  }

  async destroy(): Promise<void> {
    this.view?.dispose();
    this.view = null;
    this.container?.remove();
  }

  /** Called by DiscoveryMap when the run changes. */
  updateLegend(): void {
    this.view?.render();
  }
}