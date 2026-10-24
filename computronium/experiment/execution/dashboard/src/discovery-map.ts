/** Discovery Map — 3D Fog-of-War Grid (TODO68 Phase 1).

    The grid is a slice of the ontology's declared space: three axes are free
    and the other three are held at one value each, so every cell on the grid
    is a whole coordinate and the system can judge it. The backend judges
    each cell — measured (the run has evidence there), legal (the system
    would measure it and nobody has) or void (the system's own rules refuse
    it) — and the map draws what it is told.

    A cell with no record is not an empty cell: it is a gap the researcher
    can see, queue or register.
*/

import * as THREE from "three";
import { registry } from "./components/registry.js";
import { getSceneContext } from "./components/context.js";
import { PANEL_KEYS } from "./keys.js";
import { registerDisplayPanel } from "./panels.js";
import { createPanelShell } from "./shell.js";
import { router } from "./ws-client.js";
import { ARM_COLORS, PALETTE } from "./palette.js";
import { runSelection } from "./run-selection.js";
import axisMetadata from "./axis-metadata.json";
import { frameBox } from "./stage/framing.js";
import {
  cellKey,
  mean,
  meanCurve,
  stageState,
  stddev,
  type AxisSelection,
  type StageChange,
} from "./stage/state.js";
import { createTextSprite } from "./stage/sprites.js";
import {
  AXIS_NAMES,
  type AxisName,
  type CellData,
} from "./cell-data.js";
import type { Component } from "./components/registry.js";

interface AxisMeta {
  display_name: string;
  description: string;
  primitives: { name: string }[];
}

const AXIS_META = axisMetadata.axes as unknown as Record<AxisName, AxisMeta>;

/** What a cell's status reads as, under the cursor. */
const STATUS_LABELS: Record<CellData["status"], string> = {
  measured: "Measured — the run has evidence here",
  legal: "Legal — a gap nobody has measured",
  void: "Void — the system refuses this cell",
};

export class DiscoveryMap implements Component {
  name = "DiscoveryMap";

  private scene: THREE.Scene = new THREE.Scene();
  private camera: THREE.PerspectiveCamera = new THREE.PerspectiveCamera();
  private renderer: THREE.WebGLRenderer | null = null;
  private cells: Map<string, THREE.Mesh | THREE.LineSegments | THREE.Line> =
    new Map();
  cellDataMap: Map<string, CellData> = new Map();
  /** The height each cell's pillar currently stands at. */
  private cellHeights: Map<string, number> = new Map();
  private xValues: string[] = [];
  private yValues: string[] = [];
  private zValues: string[] = [];
  private cellSize = 0.8;
  private spacing = 1.1;
  private raycaster = new THREE.Raycaster();
  private mouse = new THREE.Vector2();
  private selectedCell: string | null = null;
  private hoveredCell: string | null = null;
  private legendElement: HTMLElement | null = null;
  /** The readout that names the cell under the cursor. */
  private readoutElement: HTMLElement | null = null;
  private pointerX = 0;
  private pointerY = 0;
  private axisLabelMeshes: THREE.Object3D[] = [];
  /** Every void marker, in one mesh: they are never picked, only drawn. */
  private voidMesh: THREE.LineSegments | null = null;
  /** Whether the grid stands on the stage: a view that is not active
      leaves nothing of itself there. */
  private visible = false;

  constructor() {
    // Register WebSocket handlers IMMEDIATELY in constructor
    // This ensures handlers are ready before any WebSocket messages arrive
    router.register("queue_update", this.onQueueUpdate);
    router.register("campaign_metrics", this.onCampaignMetrics);
  }

  async init(): Promise<void> {
    const context = getSceneContext();
    if (context) {
      this.scene = context.scene;
      this.camera = context.camera;
      this.renderer = context.renderer;
    }

    this.setupInteraction();
    this.createLegend();
    this.createReadout();

    // The stage's state is the map's state: the space, the records and the
    // axes the reader picked are shared with the other views. The legend
    // follows it; the grid is drawn by whoever stands on the stage.
    stageState.onChange(() => this.updateLegend());
    runSelection.onChange(() => this.updateRunPicker());

    console.log("[DiscoveryMap] Initialized");
  }

  async destroy(): Promise<void> {
    router.unregister("queue_update", this.onQueueUpdate);
    router.unregister("campaign_metrics", this.onCampaignMetrics);
    this.clearGrid();
    this.legendElement?.remove();
    this.readoutElement?.remove();
  }

  /** The grid is one of the stage's views: it stands on it when it is chosen. */
  show(): void {
    this.visible = true;
    this.applyAxes();
  }

  /** The grid leaves the stage: nothing of it may remain. */
  hide(): void {
    this.visible = false;
    this.clearGrid();
  }

  /** Re-read the shared state and redraw the grid. */
  refreshView(change: StageChange): void {
    if (!this.visible) return;
    if (change === "space") {
      // The space carries the grid's shape: the values it shows and the
      // verdict on every cell.
      this.applyAxes();
      return;
    }
    if (change === "evidence") {
      this.applyAggregates();
    }
  }

  /** Whether the grid holds a cell the run measured. */
  hasMeasured(): boolean {
    return this.cellDataMap.size > 0 && this.cellHeights.size > 0;
  }

  /** The legend follows the stage: the arms the run measured, the axes it
      shows, and the tally of what it declared. */
  private updateLegend(): void {
    const space = stageState.space;
    const hasSpace = !!space;
    const arms = stageState.values.credit;
    const hasArms = arms.length > 0;

    // Toggle empty state
    const emptyState = this.legendElement?.querySelector("#legend-empty-state") as HTMLElement;
    const view = this.legendElement?.querySelector("#legend-view") as HTMLElement;
    const armsBlock = this.legendElement?.querySelector("#legend-arms-block") as HTMLElement;
    const axesBlock = this.legendElement?.querySelector("#legend-axes-block") as HTMLElement;

    if (emptyState) emptyState.style.display = hasSpace ? "none" : "flex";
    if (view) view.style.display = hasSpace ? "block" : "none";
    if (armsBlock) armsBlock.style.display = hasArms ? "block" : "none";
    if (axesBlock) axesBlock.style.display = hasSpace ? "block" : "none";

    // Update cell count in title
    const countEl = this.legendElement?.querySelector("#legend-cell-count") as HTMLElement;
    if (countEl && space) {
      const counts = {
        measured: Array.from(stageState.aggregates.keys()).filter((key) =>
          stageState.spaceCells.has(key),
        ).length,
        legal: space.counts.legal,
        void: space.counts.void,
      };
      countEl.textContent = `${counts.measured + counts.legal + counts.void} cells`;
    }

    this.refreshAxisOptions();
    this.updateLegendArms();
    this.updateLegendAxes();
  }

  private setupInteraction(): void {
    const canvas = this.renderer?.domElement;
    if (!canvas) return;

    // A line is picked within a threshold of the ray, and the default
    // threshold is a whole cell: the cursor would name a cell it is nowhere
    // near. The cells that matter are solid — a pillar, or a pick target
    // behind the wireframe — so the threshold can be tight.
    this.raycaster.params.Line.threshold = this.cellSize * 0.2;

    canvas.addEventListener("mousemove", (event) => {
      const rect = canvas.getBoundingClientRect();
      this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      this.pointerX = event.clientX;
      this.pointerY = event.clientY;
    });

    canvas.addEventListener("mouseleave", () => {
      this.hideReadout();
    });

    canvas.addEventListener("click", () => {
      if (this.hoveredCell) {
        this.selectCell(this.hoveredCell);
      }
    });
  }

  /** The readout that names the cell under the cursor. */
  private createReadout(): void {
    const overlay = document.getElementById("ui-overlay");
    if (!overlay) return;

    this.readoutElement = document.createElement("div");
    this.readoutElement.id = "cell-readout";
    this.readoutElement.style.cssText = `
      position: fixed;
      pointer-events: none;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 12px;
      font-size: 11px;
      line-height: 1.5;
      z-index: 300;
      display: none;
      max-width: 360px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.5);
      backdrop-filter: blur(8px);
    `;
    overlay.appendChild(this.readoutElement);
  }

  private showReadout(cell: CellData): void {
    const element = this.readoutElement;
    if (!element) return;

    element.innerHTML = "";

    // Coordinate chips
    const coordRow = document.createElement("div");
    coordRow.style.cssText = "display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px;";
    Object.entries(cell.coordinate)
      .filter(([, value]) => value)
      .forEach(([axis, value]) => {
        const isCredit = axis === "credit";
        const color = isCredit ? (ARM_COLORS[value] || PALETTE.gradient) : "var(--text-secondary)";
        const chip = document.createElement("span");
        chip.style.cssText = `
          padding: 2px 8px;
          background: ${isCredit ? color + "22" : "var(--bg-tertiary)"};
          border: 1px solid ${isCredit ? color + "88" : "var(--border)"};
          border-radius: 10px;
          font-size: 10px;
          color: ${color};
          font-weight: ${isCredit ? "600" : "400"};
        `;
        chip.textContent = `${axis}=${value}`;
        coordRow.appendChild(chip);
      });
    element.appendChild(coordRow);

    // Status with icon
    const statusRow = document.createElement("div");
    statusRow.style.cssText = "display: flex; align-items: center; gap: 8px; margin-bottom: 6px;";
    const statusColors: Record<CellData["status"], string> = {
      measured: PALETTE.measured,
      legal: PALETTE.legal_unmeasured,
      void: PALETTE.void,
    };
    const statusIcons: Record<CellData["status"], string> = {
      measured: "●",
      legal: "○",
      void: "✕",
    };
    const icon = document.createElement("span");
    icon.style.cssText = `font-size: 14px; color: ${statusColors[cell.status]};`;
    icon.textContent = statusIcons[cell.status];
    statusRow.appendChild(icon);

    const statusText = document.createElement("span");
    statusText.style.cssText = `font-weight: 600; color: ${statusColors[cell.status]}; font-size: 12px;`;
    statusText.textContent = STATUS_LABELS[cell.status];
    statusRow.appendChild(statusText);
    element.appendChild(statusRow);

    // Measured cell: show key metrics inline
    if (cell.status === "measured" && cell.metrics) {
      const m = cell.metrics;
      const metricsRow = document.createElement("div");
      metricsRow.style.cssText = "display: flex; gap: 16px; font-size: 11px; color: var(--text-secondary);";
      const acc = m.val_acc ?? 0;
      const std = m.val_acc_std ?? 0;
      const seeds = m.n_seeds ?? 0;
      const wt = m.walltime_s;
      metricsRow.innerHTML = `
        <span>acc <strong style="color: var(--text-primary);">${acc.toFixed(3)}</strong> ± ${std.toFixed(3)}</span>
        <span>n=<strong style="color: var(--text-primary);">${seeds}</strong></span>
        <span>${wt !== undefined ? `${wt.toFixed(1)}s` : ""}</span>
        ${cell.pareto ? `<span style="color: var(--pareto);">● PARETO</span>` : ""}
      `;
      element.appendChild(metricsRow);
    }

    // Legal cell: show actionable hint
    if (cell.status === "legal") {
      const hint = document.createElement("div");
      hint.style.cssText = "margin-top: 6px; padding: 6px 8px; background: var(--bg-tertiary); border-radius: 4px; font-size: 10px; color: var(--text-muted);";
      const seeds = cell.requiredSeeds ?? 0;
      hint.textContent = `Click to queue ${seeds} seeds →`;
      element.appendChild(hint);
    }

    // Void cell: show reason
    if (cell.voidReason) {
      const reason = document.createElement("div");
      reason.style.cssText = "margin-top: 6px; padding: 6px 8px; background: var(--void)11; border: 1px solid var(--void)44; border-radius: 4px; font-size: 10px; color: var(--void);";
      reason.textContent = cell.voidReason;
      element.appendChild(reason);
    }

    element.style.display = "block";
    const box = element.getBoundingClientRect();
    const left = Math.min(
      this.pointerX + 16,
      window.innerWidth - box.width - 8,
    );
    const top = Math.min(this.pointerY + 16, window.innerHeight - box.height - 8);
    element.style.left = `${Math.max(8, left)}px`;
    element.style.top = `${Math.max(8, top)}px`;
  }

  private hideReadout(): void {
    if (this.readoutElement) this.readoutElement.style.display = "none";
  }

  private createLegend(): void {
    this.legendElement = createPanelShell({
      id: "discovery-legend",
      title: "Discovery Map",
      glyph: "▦",
      key: PANEL_KEYS.legend,
      body: this.legendBody(),
      dock: "bottom",
      defaultOpen: true,
    });

    this.createRunPicker();
    this.createAxisPicker();
    this.updateLegendArms();
    this.updateLegendAxes();
  }

  private legendBody(): string {
    return `
      <div id="legend-title" style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
        <span style="font-weight: 600; color: var(--text-primary);">Discovery Map</span>
        <span id="legend-cell-count" style="font-size: 11px; color: var(--text-muted);"></span>
      </div>
      <div id="legend-empty-state" class="empty-state" style="display: none;">
        <div class="empty-state-icon">▦</div>
        <div class="empty-state-title">No run selected</div>
        <div class="empty-state-message">Pick a run from the dropdown below to see its declared space</div>
      </div>
      <div id="legend-view" style="display: none;"></div>
      <div id="legend-marks" style="display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px;">
        <div class="legend-item">
          <div style="width: 14px; height: 14px; background: var(--measured); border-radius: 3px; box-shadow: 0 0 10px var(--measured);"></div>
          <span style="font-size: 11px;">Measured — glowing pillar</span>
        </div>
        <div class="legend-item">
          <div style="width: 14px; height: 14px; background: transparent; border: 2px solid var(--legal-unmeasured); border-radius: 3px;"></div>
          <span style="font-size: 11px;">Legal gap — click to queue</span>
        </div>
        <div class="legend-item">
          <svg width="14" height="14" viewBox="0 0 14 14"><line x1="2" y1="2" x2="12" y2="12" stroke="var(--void)" stroke-width="2"/><line x1="12" y1="2" x2="2" y2="12" stroke="var(--void)" stroke-width="2"/></svg>
          <span style="font-size: 11px;">Void — system refuses</span>
        </div>
      </div>
      <div id="legend-arms-block" style="margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border); display: none;">
        <div style="font-weight: 600; margin-bottom: 6px; font-size: 11px;">Credit Arms</div>
        <div id="legend-arms" style="display: flex; flex-wrap: wrap; gap: 5px;"></div>
      </div>
      <div id="legend-run-block" style="margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border);">
        <div style="font-weight: 600; margin-bottom: 6px; font-size: 11px;">Run</div>
        <select id="legend-run-picker"></select>
        <div id="legend-run" style="font-size: 11px; color: var(--text-secondary); margin-top: 6px; min-height: 16px;"></div>
      </div>
      <div id="legend-axes-block" style="margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border); display: none;">
        <div style="font-weight: 600; margin-bottom: 6px; font-size: 11px;">Axes (click to change)</div>
        <div id="legend-axis-picker" style="display: flex; flex-direction: column; gap: 5px;"></div>
        <div id="legend-axes" style="font-size: 10px; color: var(--text-muted); margin-top: 6px;"></div>
      </div>
    `;
  }

  /** The run the grid shows, chosen by the reader. */
  private createRunPicker(): void {
    const select = this.legendElement?.querySelector<HTMLSelectElement>(
      "#legend-run-picker",
    );
    if (!select) return;

    select.addEventListener("change", () => {
      runSelection.select(select.value || null);
    });
  }

  private updateRunPicker(): void {
    const select = this.legendElement?.querySelector<HTMLSelectElement>(
      "#legend-run-picker",
    );
    const detail = this.legendElement?.querySelector("#legend-run");
    if (!select) return;

    const runs = runSelection.runs;
    select.innerHTML = "";
    runs.forEach(([runId, metrics]) => {
      const option = document.createElement("option");
      const profile = metrics?.run?.profile ?? "run";
      const records = metrics?.records?.length ?? 0;
      option.value = runId;
      option.textContent = `${runId.slice(0, 8)} · ${profile} · ${records}`;
      option.selected = runId === runSelection.selectedId;
      select.appendChild(option);
    });
    if (runs.length === 0) {
      select.disabled = true;
      if (detail) {
        detail.textContent = "No run has reported yet.";
      }
      return;
    }
    select.disabled = false;

    const metrics = runSelection.selected;
    if (!detail) return;
    if (!metrics) {
      detail.textContent = "";
      return;
    }
    const run = metrics.run ?? {};
    detail.textContent = [
      `run ${(runSelection.selectedId ?? "").slice(0, 8)}`,
      run.mode,
      `${metrics.records?.length ?? 0} records`,
    ]
      .filter(Boolean)
      .join(" · ");
  }

  private createAxisPicker(): void {
    const container = this.legendElement?.querySelector("#legend-axis-picker");
    if (!container) return;

    const dimensions: (keyof AxisSelection)[] = ["x", "y", "z"];
    dimensions.forEach((dimension) => {
      const row = document.createElement("div");
      row.className = "axis-row";
      row.dataset.dimension = dimension;
      row.style.cssText = `
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 3px;
        font-size: 11px;
        margin-bottom: 3px;
      `;

      const label = document.createElement("span");
      label.textContent = dimension.toUpperCase();
      label.style.cssText = "color: var(--text-secondary); width: 12px;";

      row.appendChild(label);
      container.appendChild(row);
    });

    this.refreshAxisOptions();
  }

  /** The axis picker's buttons: one per axis, for each of the three cuts.

    A dropdown hid the six axes behind one line of text; a row of buttons
    shows them, and the ones another cut already holds are dimmed.
  */
  private refreshAxisOptions(): void {
    const rows = this.legendElement?.querySelectorAll(
      "#legend-axis-picker .axis-row",
    );
    if (!rows) return;

    rows.forEach((row) => {
      const dimension = (row as HTMLElement).dataset
        .dimension as keyof AxisSelection;
      const taken = new Set<AxisName>(
        (["x", "y", "z"] as (keyof AxisSelection)[])
          .filter((other) => other !== dimension)
          .map((other) => stageState.axes[other]),
      );

      row.innerHTML = "";
      const label = document.createElement("span");
      label.textContent = dimension.toUpperCase();
      label.style.cssText = "color: var(--text-secondary); width: 12px;";
      row.appendChild(label);

      AXIS_NAMES.forEach((axis) => {
        const active = stageState.axes[dimension] === axis;
        const button = document.createElement("button");
        button.className = "axis-button";
        button.dataset.axis = axis;
        button.textContent = AXIS_META[axis]?.display_name ?? axis;
        button.disabled = taken.has(axis);
        button.style.cssText = `
          flex: 0 0 auto;
          padding: 1px 5px;
          background: ${active ? "var(--bg-primary)" : "var(--bg-tertiary)"};
          border: 1px solid ${active ? "var(--border-bright)" : "var(--border)"};
          border-radius: 4px;
          color: ${active ? "var(--text-primary)" : "var(--text-secondary)"};
          font-size: 10px;
          cursor: pointer;
          opacity: ${taken.has(axis) ? 0.4 : 1};
        `;
        button.addEventListener("click", () => {
          stageState.setAxes({
            ...stageState.axes,
            [dimension]: axis,
          });
        });
        row.appendChild(button);
      });
    });
  }

  private updateLegendArms(): void {
    const container = this.legendElement?.querySelector("#legend-arms");
    if (!container) return;

    const arms = stageState.values.credit;
    if (arms.length === 0) {
      container.innerHTML =
        '<span style="color: var(--text-muted); font-size: 11px;">No arm measured yet.</span>';
      return;
    }

    container.innerHTML = arms
      .map((arm) => {
        const color = ARM_COLORS[arm] || PALETTE.gradient;
        return `<span style="display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; background: ${color}22; border: 1px solid ${color}88; border-radius: 12px; color: ${color}; font-size: 11px;">${arm}</span>`;
      })
      .join("");
  }

  private updateLegendAxes(): void {
    const container = this.legendElement?.querySelector("#legend-axes");
    if (!container) return;

    const space = stageState.space;
    if (!space) {
      container.textContent =
        "Waiting for the run's declared space — the axes come from the ontology.";
      return;
    }

    const axisLine = (axis: AxisName, values: string[]): string => {
      const available = space.available[axis] ?? values.length;
      const trimmed =
        available > values.length ? ` (${values.length} of ${available})` : "";
      const name = AXIS_META[axis]?.display_name ?? axis;
      return `${name}${trimmed}`;
    };

    const held = Object.entries(space.held).map(
      ([axis, value]) => `${axis}=${value}`,
    );
    // The tally is the space's, not the grid's: the grid is off the stage
    // when another view is on, and a legend that counted an empty grid
    // would say the run measured nothing.
    const counts = {
      measured: Array.from(stageState.aggregates.keys()).filter((key) =>
        stageState.spaceCells.has(key),
      ).length,
      legal: space.counts.legal,
      void: space.counts.void,
    };
    const total = space.cells.length;

    const rules = Object.entries(space.void_rules ?? {})
      .sort((a, b) => b[1] - a[1])
      .slice(0, 2)
      .map(([rule, count]) => `${rule.replace(/_/g, " ")} (${count})`);

    container.innerHTML = [
      `<div>X: ${axisLine(stageState.axes.x, space.values[stageState.axes.x] ?? [])}</div>`,
      `<div>Y: ${axisLine(stageState.axes.y, space.values[stageState.axes.y] ?? [])}</div>`,
      `<div>Z: ${axisLine(stageState.axes.z, space.values[stageState.axes.z] ?? [])}</div>`,
      `<div style="margin-top: 6px;">held: ${held.join(" · ") || "—"}</div>`,
      `<div style="margin-top: 6px;">${counts.measured} measured · ${counts.legal} legal · ${counts.void} void (of ${total})</div>`,
      rules.length > 0
        ? `<div style="margin-top: 6px;">refused by: ${rules.join(", ")}</div>`
        : "",
    ].join("");
  }

  /** Re-read the selected axes from the declared space and rebuild the grid. */
  private applyAxes(): void {
    const space = stageState.space;
    const axes = stageState.axes;
    this.xValues = space?.values[axes.x] ?? [];
    this.yValues = space?.values[axes.y] ?? [];
    this.zValues = space?.values[axes.z] ?? [];
    this.buildGrid();
    this.updateLegend();
  }

  private buildGrid(): void {
    this.clearGrid();
    if (!this.visible) return;

    this.createAxisLabels();

    const voidMarkers: number[] = [];

    this.yValues.forEach((yVal, yIdx) => {
      this.zValues.forEach((zVal, zIdx) => {
        this.xValues.forEach((xVal, xIdx) => {
          const key = cellKey(xVal, yVal, zVal);
          const spaceCell = stageState.spaceCells.get(key);
          const status = spaceCell?.status ?? "legal";
          const cellData: CellData = {
            coordinate: this.coordinateFor(xVal, yVal, zVal),
            status,
            chance: stageState.chance,
            requiredSeeds: stageState.requiredSeeds,
            runId: stageState.runId ?? undefined,
            voidReason: spaceCell?.reason,
            inDeclaration: spaceCell?.in_declaration,
          };
          this.cellDataMap.set(key, cellData);
          if (status === "void") {
            // The void markers are drawn together: they are never picked.
            voidMarkers.push(...this.voidMarkerPositions(xIdx, yIdx, zIdx));
            return;
          }
          this.createCell(key, cellData, xIdx, yIdx, zIdx);
        });
      });
    });

    if (voidMarkers.length > 0) this.createVoidMarkers(voidMarkers);
    this.frameGrid();
  }

  /** The cell's whole coordinate: the axes on screen, and the ones held fixed.

      An axis the run never varied has one value, and that value belongs to
      every cell of the grid: a cell that names only three of the six axes
      cannot be measured, queued or registered. */
  private coordinateFor(
    xVal: string,
    yVal: string,
    zVal: string,
  ): CellData["coordinate"] {
    const coordinate: CellData["coordinate"] = {
      credit: "",
      geometry: "",
      dynamics: "",
      substrate: "",
      plasticity: "",
      update: "",
    };
    coordinate[stageState.axes.x] = xVal;
    coordinate[stageState.axes.y] = yVal;
    coordinate[stageState.axes.z] = zVal;
    AXIS_NAMES.forEach((axis) => {
      if (coordinate[axis]) return;
      const held = stageState.space?.held?.[axis];
      if (held) coordinate[axis] = held;
    });
    return coordinate;
  }

  private createAxisLabels(): void {
    this.axisLabelMeshes.forEach((mesh) => this.scene.remove(mesh));
    this.axisLabelMeshes = [];

    const valueMaterial = new THREE.SpriteMaterial({
      color: 0x8b98a8,
      sizeAttenuation: true,
    });
    const nameMaterial = new THREE.SpriteMaterial({
      color: 0xc9d4e0,
      sizeAttenuation: true,
    });

    const gridWidth = (this.xValues.length - 1) * this.spacing;
    const gridDepth = (this.zValues.length - 1) * this.spacing;
    // The labels stand clear in front of the cells: from the camera's angle a
    // label on the grid's own plane is painted across the pillars. They also
    // sit below the floor, so the near ones do not stand on the front row.
    const labelZ = gridDepth / 2 + 1.2;
    const labelY = -0.45;

    // The values the row names, under the cells.
    this.xValues.forEach((val, idx) => {
      const x = (idx - (this.xValues.length - 1) / 2) * this.spacing;
      const sprite = createTextSprite(
        val,
        0.3,
        valueMaterial,
        this.spacing * 0.95,
      );
      sprite.position.set(x, labelY, labelZ);
      this.scene.add(sprite);
      this.axisLabelMeshes.push(sprite);
    });

    // The axis the row runs along, at the row's end.
    const xSprite = createTextSprite(stageState.axes.x, 0.3, nameMaterial);
    xSprite.position.set(gridWidth / 2 + 1.15, labelY, labelZ);
    this.scene.add(xSprite);
    this.axisLabelMeshes.push(xSprite);

    // The axis that comes at the camera, on its own line in front.
    const zSprite = createTextSprite(stageState.axes.z, 0.3, nameMaterial);
    zSprite.position.set(0, labelY, labelZ + 1.1);
    this.scene.add(zSprite);
    this.axisLabelMeshes.push(zSprite);

    // The axis the rows stack along, beside the rows it stacks.
    const ySprite = createTextSprite(stageState.axes.y, 0.3, nameMaterial);
    ySprite.position.set(-(gridWidth / 2) - 1.5, 1.3, 0);
    this.scene.add(ySprite);
    this.axisLabelMeshes.push(ySprite);
  }

  private createCell(
    key: string,
    data: CellData,
    xIdx: number,
    yIdx: number,
    zIdx: number,
  ): void {
    const x = (xIdx - (this.xValues.length - 1) / 2) * this.spacing;
    const y = yIdx * this.spacing;
    const z = (zIdx - (this.zValues.length - 1) / 2) * this.spacing;

    const mesh =
      data.status === "measured"
        ? this.createMeasuredCell(data)
        : this.createLegalCell();

    mesh.position.set(x, y, z);
    mesh.userData = { ...mesh.userData, cellKey: key };
    this.scene.add(mesh);
    this.cells.set(key, mesh);
  }

  private createMeasuredCell(data: CellData): THREE.Mesh {
    const height = this.pillarHeight(data);
    const color = ARM_COLORS[data.coordinate.credit] || PALETTE.gradient;

    const geometry = new THREE.BoxGeometry(
      this.cellSize,
      height,
      this.cellSize,
    );
    geometry.translate(0, height / 2, 0);
    const material = new THREE.MeshStandardMaterial({
      color: new THREE.Color(color),
      emissive: new THREE.Color(color),
      emissiveIntensity: 0.5,
      transparent: true,
      opacity: 0.9,
      metalness: 0.3,
      roughness: 0.4,
    });

    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;

    // Add glow effect
    const glowGeometry = new THREE.BoxGeometry(
      this.cellSize * 1.1,
      height * 1.1,
      this.cellSize * 1.1,
    );
    glowGeometry.translate(0, height / 2, 0);
    const glowMaterial = new THREE.MeshBasicMaterial({
      color: new THREE.Color(color),
      transparent: true,
      opacity: 0.15,
      depthWrite: false,
    });
    const glow = new THREE.Mesh(glowGeometry, glowMaterial);
    mesh.add(glow);
    mesh.userData.glow = glow;

    return mesh;
  }

  private createLegalCell(): THREE.LineSegments {
    const geometry = new THREE.BoxGeometry(
      this.cellSize,
      this.cellSize,
      this.cellSize,
    );
    const edges = new THREE.EdgesGeometry(geometry);
    edges.translate(0, this.cellSize / 2, 0);
    const material = new THREE.LineBasicMaterial({
      color: PALETTE["legal_unmeasured"],
      transparent: true,
      opacity: 0.55,
    });
    const mesh = new THREE.LineSegments(edges, material);

    // A wireframe cube is hollow: a ray through its middle hits nothing, and
    // a gap nobody can click is a gap nobody can act on. The pick target is
    // the solid cell, drawn never and picked always.
    const pick = new THREE.Mesh(
      new THREE.BoxGeometry(this.cellSize, this.cellSize, this.cellSize),
      new THREE.MeshBasicMaterial(),
    );
    pick.position.y = this.cellSize / 2;
    pick.visible = false;
    mesh.add(pick);

    return mesh;
  }

  /** Free a mesh and everything hanging off it. */
  private disposeMesh(mesh: THREE.Object3D): void {
    mesh.traverse((child) => {
      const geometry = (child as THREE.Mesh).geometry;
      if (geometry) geometry.dispose();
      const material = (child as THREE.Mesh).material;
      if (Array.isArray(material)) {
        material.forEach((m) => m.dispose());
      } else if (material) {
        material.dispose();
      }
    });
  }

  /** The red cross that marks a cell the system refuses. */
  private voidMarkerPositions(
    xIdx: number,
    yIdx: number,
    zIdx: number,
  ): number[] {
    const x = (xIdx - (this.xValues.length - 1) / 2) * this.spacing;
    const y = yIdx * this.spacing;
    const z = (zIdx - (this.zValues.length - 1) / 2) * this.spacing;
    const size = this.cellSize * 0.6;
    const lift = 0.1;
    return [
      x - size,
      y + lift,
      z - size,
      x + size,
      y + lift,
      z + size,
      x + size,
      y + lift,
      z - size,
      x - size,
      y + lift,
      z + size,
    ];
  }

  /** Every void marker in one mesh: they are drawn, never picked. */
  private createVoidMarkers(positions: number[]): void {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(positions, 3),
    );
    const material = new THREE.LineBasicMaterial({
      color: PALETTE.void,
      transparent: true,
      opacity: 0.32,
    });
    this.voidMesh = new THREE.LineSegments(geometry, material);
    this.scene.add(this.voidMesh);
  }

  /** Frame the grid the map just built: a bigger grid needs a wider view.

      The grid is a slab, not a ball, and it is seen at an angle, so the
      camera is placed where every corner of the slab — and the labels that
      stand in front of it — falls inside the frustum, rather than where a
      bounding sphere would fit.
  */
  private frameGrid(): void {
    const context = getSceneContext();
    if (!context?.controls) return;
    if (this.xValues.length === 0 || this.zValues.length === 0) return;

    const halfX = ((this.xValues.length - 1) * this.spacing) / 2 + this.cellSize;
    const halfZ = ((this.zValues.length - 1) * this.spacing) / 2 + this.cellSize;
    const top = (this.yValues.length - 1) * this.spacing + this.cellSize;
    const front = halfZ + 1.8;
    const floor = -0.8;

    frameBox(
      context,
      new THREE.Vector3(-halfX, floor, -halfZ),
      new THREE.Vector3(halfX, top, front),
      new THREE.Vector3(0, top / 2, 0),
    );
  }

  private clearGrid(): void {
    this.cells.forEach((mesh) => {
      this.scene.remove(mesh);
      this.disposeMesh(mesh);
    });
    this.cells.clear();
    this.cellDataMap.clear();
    this.cellHeights.clear();

    this.axisLabelMeshes.forEach((mesh) => {
      this.scene.remove(mesh);
      this.disposeMesh(mesh);
    });
    this.axisLabelMeshes = [];

    if (this.voidMesh) {
      this.scene.remove(this.voidMesh);
      this.voidMesh.geometry.dispose();
      if (Array.isArray(this.voidMesh.material)) {
        this.voidMesh.material.forEach((m) => m.dispose());
      } else {
        this.voidMesh.material.dispose();
      }
      this.voidMesh = null;
    }
  }

  private onQueueUpdate = (_data: unknown): void => {
    // The queue says what is running; the grid says what was measured.
  };

  private onCampaignMetrics = (data: any): void => {
    const metricsData = data?.data;
    // A run that has started but not yet measured still names itself: its
    // declaration is the space the grid draws, and the empty space is the
    // truth about it. Waiting for the first record would show a blank
    // canvas for the whole of the run.
    if (!metricsData?.run) return;

    const runId = typeof data?.campaign_id === "string" ? data.campaign_id : null;
    if (!runId) return;

    // The grid shows one run at a time. A store holds several — a run, and
    // the runs its own answers spawned — so the choice is made once, in the
    // shared selection, and the legend names the run the picture shows.
    runSelection.observe(runId, metricsData);
  };

  /** Mark the cells that have records and light them up. */
  private applyAggregates(): void {
    if (!this.visible) return;
    stageState.aggregates.forEach((aggregate, key) => {
      const cellData = this.cellDataMap.get(key);
      if (!cellData) return;
      cellData.status = "measured";
      cellData.coordinate = { ...aggregate.coordinate };
      cellData.metrics = {
        val_acc: mean(aggregate.acc),
        val_acc_std: stddev(aggregate.acc),
        walltime_s: mean(aggregate.walltime),
        param_count: mean(aggregate.params),
        n_seeds: aggregate.acc.length,
      };
      cellData.curve = meanCurve(aggregate.curves);
      cellData.pareto = aggregate.pareto;
      cellData.chance = stageState.chance;
      cellData.requiredSeeds = stageState.requiredSeeds;
      cellData.runId = stageState.runId ?? undefined;
      this.updateCellVisual(key, cellData, aggregate.pareto);
    });
    this.updateLegendAxes();
  }

  /** A pillar's height: the cell's accuracy, measured. */
  private pillarHeight(data: CellData): number {
    return THREE.MathUtils.lerp(0.4, 3.4, data.metrics?.val_acc ?? 0);
  }

  private updateCellVisual(
    key: string,
    data: CellData,
    isPareto: boolean,
  ): void {
    const oldMesh = this.cells.get(key);
    if (!oldMesh) return;

    const position = oldMesh.position.clone();
    const glow = oldMesh.userData.glow;
    if (glow) oldMesh.remove(glow);

    this.scene.remove(oldMesh);
    this.disposeMesh(oldMesh);

    const newMesh = this.createMeasuredCell(data);
    newMesh.position.copy(position);
    // The rebuilt mesh must still know which cell it is: the click finds the
    // cell by this key.
    newMesh.userData.cellKey = key;

    // The pillar grows into its measured height instead of appearing at it.
    const target = this.pillarHeight(data);
    const previous = this.cellHeights.get(key) ?? 0;
    this.cellHeights.set(key, target);
    newMesh.scale.y = target > 0 ? Math.min(1, Math.max(previous / target, 0.001)) : 1;

    if (isPareto) {
      // Add Pareto highlight ring
      const ringGeometry = new THREE.RingGeometry(
        this.cellSize * 0.6,
        this.cellSize * 0.8,
        32,
      );
      const ringMaterial = new THREE.MeshBasicMaterial({
        color: PALETTE.pareto,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.6,
      });
      const ring = new THREE.Mesh(ringGeometry, ringMaterial);
      ring.rotation.x = -Math.PI / 2;
      ring.position.y = 0.05;
      newMesh.add(ring);
      newMesh.userData.paretoRing = ring;
    }

    this.scene.add(newMesh);
    this.cells.set(key, newMesh);
  }

  private selectCell(key: string): void {
    this.selectedCell = key;
    const data = this.cellDataMap.get(key);
    if (data) {
      // Emit event for CellDrawer
      window.dispatchEvent(new CustomEvent("cell-selected", { detail: data }));
    }
  }

  update(delta: number): void {
    if (!this.visible) {
      this.hideReadout();
      return;
    }
    // Pillars ease into the height they were measured at.
    const ease = 1 - Math.exp(-delta * 8);
    this.cells.forEach((mesh, key) => {
      const data = this.cellDataMap.get(key);
      if (
        data?.status === "measured" &&
        mesh instanceof THREE.Mesh &&
        mesh.material instanceof THREE.MeshStandardMaterial
      ) {
        if (mesh.scale.y < 1) {
          mesh.scale.y = Math.min(1, mesh.scale.y + (1 - mesh.scale.y) * ease);
        }
        const glow = mesh.userData.glow;
        if (glow) {
          glow.material.opacity = 0.1 + 0.1 * Math.sin(Date.now() * 0.003);
        }
        // Pulse pareto ring
        const ring = mesh.userData.paretoRing;
        if (ring) {
          ring.material.opacity = 0.4 + 0.2 * Math.sin(Date.now() * 0.005);
        }
      }
    });

    // Raycast for hover
    this.raycaster.setFromCamera(this.mouse, this.camera);
    const intersects = this.raycaster.intersectObjects(
      Array.from(this.cells.values()),
      true,
    );

    let key: string | null = null;
    if (intersects.length > 0) {
      key = this.pickCell(intersects);
    }
    if (!key) {
      key = this.voidCellUnderCursor();
    }

    if (key !== this.hoveredCell) {
      if (this.hoveredCell) this.highlightCell(this.hoveredCell, false);
      this.hoveredCell = key;
      if (key) this.highlightCell(key, true);
    }

    const hovered = key ? this.cellDataMap.get(key) : undefined;
    if (hovered) {
      this.showReadout(hovered);
    } else {
      this.hideReadout();
    }
  }

  /** The cell a click means.

      The grid is dense, and every gap carries an invisible pick target so it
      can be acted on — which means the nearest cell along the ray is often a
      gap standing in front of a pillar. The evidence wins: a measured cell
      the ray met is what the researcher was aiming at, glowing and
      unmistakable, and a gap is picked when nothing measured is in the way.
  */
  private pickCell(intersects: THREE.Intersection[]): string | null {
    let nearest: string | null = null;
    for (const hit of intersects) {
      const key =
        hit.object.userData.cellKey || hit.object.parent?.userData.cellKey;
      if (!key) continue;
      nearest ??= key;
      if (this.cellDataMap.get(key)?.status === "measured") {
        return key;
      }
    }
    return nearest;
  }

  /** The void cell under the cursor, if any.

      The void markers are one mesh, drawn and never picked, so the cursor
      cannot name one of them by picking it: the point the ray met says which
      cell the marker belongs to.
  */
  private voidCellUnderCursor(): string | null {
    if (!this.voidMesh) return null;
    const threshold = this.raycaster.params.Line.threshold;
    this.raycaster.params.Line.threshold = this.cellSize * 0.3;
    try {
      const hits = this.raycaster.intersectObject(this.voidMesh, false);
      if (hits.length === 0) return null;
      return this.cellAt(hits[0].point);
    } finally {
      this.raycaster.params.Line.threshold = threshold;
    }
  }

  /** The cell a point in the world belongs to. */
  private cellAt(point: THREE.Vector3): string | null {
    const xIdx = Math.round(point.x / this.spacing + (this.xValues.length - 1) / 2);
    const yIdx = Math.round(point.y / this.spacing);
    const zIdx = Math.round(point.z / this.spacing + (this.zValues.length - 1) / 2);
    if (xIdx < 0 || xIdx >= this.xValues.length) return null;
    if (yIdx < 0 || yIdx >= this.yValues.length) return null;
    if (zIdx < 0 || zIdx >= this.zValues.length) return null;
    return cellKey(
      this.xValues[xIdx],
      this.yValues[yIdx],
      this.zValues[zIdx],
    );
  }

  private highlightCell(key: string, highlight: boolean): void {
    const mesh = this.cells.get(key);
    if (!mesh) return;

    const canvas = this.renderer?.domElement;
    if (canvas) {
      canvas.style.cursor = highlight && this.isCellActionable(key) ? "pointer" : "grab";
    }

    if (
      mesh instanceof THREE.Mesh &&
      mesh.material instanceof THREE.MeshStandardMaterial
    ) {
      if (highlight) {
        mesh.userData.originalEmissive = mesh.material.emissiveIntensity;
        mesh.userData.originalScale = mesh.scale.y;
        mesh.material.emissiveIntensity =
          (mesh.userData.originalEmissive || 0.5) + 0.5;
        // Subtle scale pop
        mesh.scale.y = Math.min(1.05, mesh.scale.y * 1.08);
      } else {
        if (mesh.userData.originalEmissive !== undefined) {
          mesh.material.emissiveIntensity = mesh.userData.originalEmissive;
        }
        if (mesh.userData.originalScale !== undefined) {
          mesh.scale.y = mesh.userData.originalScale;
        }
      }
      return;
    }

    // A legal cell is a wireframe cube: it brightens rather than glows.
    if (
      mesh instanceof THREE.LineSegments &&
      mesh.material instanceof THREE.LineBasicMaterial
    ) {
      if (highlight) {
        mesh.userData.originalOpacity = mesh.material.opacity;
        mesh.material.opacity = 0.95;
        mesh.material.linewidth = 2;
      } else if (mesh.userData.originalOpacity !== undefined) {
        mesh.material.opacity = mesh.userData.originalOpacity;
        mesh.material.linewidth = 1;
      }
    }
  }

  /** Whether a cell can be acted on (queue, preregister, quest). */
  private isCellActionable(key: string): boolean {
    const data = this.cellDataMap.get(key);
    if (!data) return false;
    return data.status === "legal" || data.status === "measured";
  }
}

// Register with global registry
export const discoveryMap = new DiscoveryMap();
registry.register(discoveryMap);
