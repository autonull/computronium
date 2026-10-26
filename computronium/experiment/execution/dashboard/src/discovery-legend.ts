/** Discovery Legend — the map's key, one view per instance. */

import { workspaceStore } from "./stores/workspace.js";
import { metricsStore } from "./stores/metrics.js";
import { runSelection, type RunMetrics } from "./run-selection.js";
import { PALETTE } from "./colors.js";
import { cellKey } from "./stores/payloads.js";
import type { AxisSelection, WorkspaceStore as WorkspaceStoreInterface } from "./layout/types.js";

interface LegendOptions {
  runId: string | null;
  axes: AxisSelection;
  workspace: WorkspaceStoreInterface;
}

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
    <div class="legend-title" style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
      <span style="font-weight: 600; color: var(--text-primary);">Discovery Map</span>
      <span class="legend-cell-count" style="font-size: 11px; color: var(--text-muted);"></span>
    </div>
    <div class="legend-empty-state empty-state" style="display: none; text-align: center; padding: 24px 12px; color: var(--text-muted); font-size: 11px;">
      <div class="empty-state-icon" style="font-size: 24px; margin-bottom: 8px; opacity: 0.5;">▦</div>
      <div class="empty-state-title">No run selected</div>
      <div class="empty-state-message">Pick a run from the dropdown below to see its declared space</div>
    </div>
    <div class="legend-view" style="display: none;"></div>
    <div class="legend-marks" style="display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px;">
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
    <div class="legend-axes"></div>
    <div class="legend-arms" style="display: flex; flex-direction: column; gap: 4px; margin-bottom: 8px;"></div>
    <div class="legend-actions">
      <button class="legend-btn primary" data-act="replicate" title="Replicate (Shift+R)">Replicate</button>
      <button class="legend-btn" data-act="preregister" title="Preregister (Shift+P)">Preregister</button>
      <button class="legend-btn" data-act="quest" title="Quest (Shift+Q)">Quest</button>
    </div>
  `;
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
    this.emptyState = this.query(".legend-empty-state");
    this.view = this.query(".legend-view");
    this.marks = this.query(".legend-marks");
    this.arms = this.query(".legend-arms");
    this.cellCount = this.query(".legend-cell-count");
    this.axesContainer = this.query(".legend-axes");
    this.replicanteBtn = this.query("[data-act=replicate]");
    this.preregisterBtn = this.query("[data-act=preregister]");
    this.questBtn = this.query("[data-act=quest]");

    this.disposers.push(
      this.options.workspace.onChange(() => this.render()),
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
    const availableAxes = ["credit", "geometry", "dynamics", "substrate", "plasticity", "update"] as const;
    type AxisName = typeof availableAxes[number];
    this.axesContainer.innerHTML = axesNames.map((axisKey) => `
      <div class="legend-axis-group" style="display: flex; align-items: center; gap: 4px; min-width: 120px; flex-wrap: wrap;">
        <span style="font-size: 9px; text-transform: uppercase; color: var(--text-muted);">${axisKey.toUpperCase()}</span>
        <div class="legend-axis-chips" data-axis-key="${axisKey}" style="display: flex; gap: 2px; flex-wrap: wrap;">
          ${availableAxes.map((axis) => `
            <button class="legend-axis-chip${this.options.axes[axisKey] === axis ? " active" : ""}" 
                    data-axis-key="${axisKey}" data-axis-value="${axis}"
                    title="Click to cycle ${axisKey} axis"
                    style="display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 12px; font-size: 10px; color: var(--text-secondary); cursor: pointer; white-space: nowrap;"
                    ${this.options.axes[axisKey] === axis ? 'style="background: var(--gradient)22; border-color: var(--gradient)66; color: var(--gradient);"' : ""}>
              ${axis}
            </button>
          `).join("")}
        </div>
      </div>
    `).join("");

    for (const chip of this.axesContainer.querySelectorAll<HTMLButtonElement>(".legend-axis-chip")) {
      chip.addEventListener("click", () => {
        const key = chip.dataset.axisKey as keyof AxisSelection;
        const currentIdx = availableAxes.indexOf(this.options.axes[key]);
        const nextIdx = (currentIdx + 1) % availableAxes.length;
        const nextAxis = availableAxes[nextIdx];
        this.options.axes[key] = nextAxis;
        this.renderAxesPicker();
        this.options.workspace.setAxes(this.options.axes);
      });
    }
  }

  private render(): void {
    const runId = this.options.runId ?? this.options.workspace.getSelectedRunId();
    const axes = this.options.axes;

    if (!runId) {
      this.emptyState.style.display = "";
      this.view.style.display = "none";
      this.marks.style.display = "none";
      this.cellCount.textContent = "";
      this.arms.innerHTML = "";
      return;
    }

    this.emptyState.style.display = "none";
    this.view.style.display = "";
    this.marks.style.display = "";

    const metrics = runSelection.getMetrics(runId);
    if (!metrics) {
      this.cellCount.textContent = "Loading…";
      return;
    }

    const records = metrics.records ?? [];
    const measured = records.filter((r: any) => r.status === "measured").length;
    const insufficient = records.filter((r: any) => r.status === "insufficient").length;
    const rejected = records.filter((r: any) => r.status === "rejected").length;
    const voidCount = records.filter((r: any) => r.status === "void").length;
    const total = measured + insufficient + rejected + voidCount;

    this.cellCount.textContent = `${measured} measured · ${insufficient} insufficient · ${rejected} rejected · ${voidCount} void · ${total} total`;

    // Render arms
    const armColors: Record<string, string> = {
      credit: "#3b82f6",
      geometry: "#22c55e",
      dynamics: "#f59e0b",
      substrate: "#a855f7",
      plasticity: "#ec4899",
      update: "#06b6d4",
    };
    this.arms.innerHTML = "";
    for (const axis of ["credit", "geometry", "dynamics", "substrate", "plasticity", "update"] as const) {
      const primitives = metrics.primitives?.[axis] ?? [];
      if (!primitives.length) continue;
      const chip = document.createElement("span");
      chip.className = "legend-chip";
      chip.style.borderColor = armColors[axis] + "88";
      chip.innerHTML = `<span class="dot" style="background:${armColors[axis]}"></span>${axis}: ${primitives.join(", ")}`;
      this.arms.appendChild(chip);
    }
  }
}