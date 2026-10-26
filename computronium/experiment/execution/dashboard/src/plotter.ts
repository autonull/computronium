/** Plotter — uPlot Charts (Pareto, Ablation, Variability) (TODO68 Phase 3, refactored for TODO71 Phase 1).
 *
 * The three charts are three panels, not one tabbed container (TODO70):
 * closing the Pareto chart must leave the ablation chart alone. They sit in
 * a column under the HUD, each with its own title, its own ×, and its own
 * download button.
 */

import uPlot from "uplot";
import "uplot/dist/uPlot.min.css";
import { registry } from "./components/registry.js";
import { createEmptyState, createChartEmptyState } from "./components/EmptyState.js";
import { TAB_KEYS } from "./keys.js";
import { router } from "./ws-client.js";
import { PALETTE, ARM_COLORS } from "./colors.js";
import { runSelection, type RunMetrics } from "./run-selection.js";
import { metricsStore } from "./stores/metrics.js";
import { workspaceStore } from "./stores/workspace.js";
import type { Component } from "./components/registry.js";
import type { JsonValue } from "./layout/types.js";
import type { AxisSelection } from "./layout/types.js";
import type { MetricsStore as MetricsStoreInterface } from "./layout/types.js";
import type { WorkspaceStore as WorkspaceStoreInterface } from "./layout/types.js";

/** The chart is what the panel leaves once the title has taken its line. */
function chartHeight(panel: HTMLElement): number {
  return Math.max(120, panel.clientHeight - 30);
}

/** One chart's panel: what it is called, and where it lives on the page. */
interface ChartSpec {
  /** The chart's name, as the reader knows it. */
  id: "pareto" | "ablation" | "variability";
  /** The panel's dom id: what the reader, and the tour, name it by. */
  panelId: string;
  /** The host the plot is drawn into. */
  hostId: string;
  /** The panel's title. */
  title: string;
  /** The glyph on the rail's button. */
  glyph: string;
  /** The key that shows the chart. */
  key: string;
}

/** The three charts, in the order they are listed. */
export const CHARTS: ChartSpec[] = [
  {
    id: "pareto",
    panelId: "plotter-pareto",
    hostId: "plotter-pareto-chart",
    title: "Pareto frontier",
    glyph: "◭",
    key: TAB_KEYS.pareto,
  },
  {
    id: "ablation",
    panelId: "plotter-ablation",
    hostId: "plotter-ablation-chart",
    title: "Ablation",
    glyph: "▥",
    key: TAB_KEYS.ablation,
  },
  {
    id: "variability",
    panelId: "plotter-variability",
    hostId: "plotter-variability-chart",
    title: "Variability",
    glyph: "◇",
    key: TAB_KEYS.variability,
  },
];

interface RecordData {
  record_id: string;
  coordinate: {
    credit: string;
    geometry: string;
    dynamics: string;
    substrate?: string;
    plasticity?: string;
    update?: string;
  };
  payload: Record<string, number>;
  schedule: {
    fidelity: string;
    seed: number;
    n_seeds: number;
  };
}

interface AblationGroup {
  axis: string;
  group_index: number;
  fixed_axes: string;
  metrics: Array<{
    metric: string;
    arms: Array<{
      value: string;
      mean: number;
      std: number;
      count: number;
      at_chance: boolean;
    }>;
  }>;
}

export function createChartPanelBody(chart: ChartSpec): string {
  return `
    <div id="${chart.hostId}" style="flex: 1; position: relative; overflow: hidden;"></div>
    <div class="chart-empty-state"></div>
    <div class="chart-toolbar" style="display: flex; align-items: center; justify-content: space-between; padding: 6px 10px; border-top: 1px solid var(--border); background: var(--bg-tertiary); font-size: 10px;">
      <span class="chart-status" style="color: var(--text-secondary);">No data</span>
      <button class="chart-download" title="Download chart as PNG" style="background: none; border: 1px solid var(--border); border-radius: 4px; padding: 2px 8px; color: var(--text-secondary); font-size: 10px; cursor: pointer;">↓ PNG</button>
    </div>
  `;
}

function getEmptyHint(chartId: string): string {
  switch (chartId) {
    case "pareto":
      return "Run with multiple credit arms to populate the frontier. Pick a profile with credit axis variety.";
    case "ablation":
      return "Add credit-axis groups to see ablation. Profiles with credit axis variety enable this chart.";
    case "variability":
      return "Add seeds in the control panel (seeds > 1) to see seed-to-seed spread.";
    default:
      return "Select a run from the legend to populate this chart.";
  }
}

function initEmptyState(chartId: "pareto" | "ablation" | "variability", root: HTMLElement, glyph: string, title: string, key: string): void {
  const emptyStateEl = root.querySelector<HTMLElement>(".chart-empty-state");
  if (!emptyStateEl) return;

  const hints: Record<string, string> = {
    pareto: "Run with multiple credit arms to populate the frontier. Pick a profile with credit axis variety.",
    ablation: "Add credit-axis groups to see ablation. Profiles with credit axis variety enable this chart.",
    variability: "Add seeds in the control panel (seeds > 1) to see seed-to-seed spread.",
  };

  const emptyState = createChartEmptyState(
    chartId,
    glyph,
    title,
    key
  );
  emptyStateEl.innerHTML = "";
  emptyStateEl.appendChild(emptyState);
}

/** Base view class shared by the three chart views. */
abstract class PlotterChartView {
  protected plot: uPlot | null = null;
  protected tooltip: HTMLElement | null = null;
  protected records: RecordData[] = [];
  protected ablationGroups: AblationGroup[] = [];
  protected paretoFlags: boolean[] = [];
  protected chance = 0.1;
  protected paretoRecordIndices: number[] = [];
  protected paretoXData: number[] = [];
  protected paretoYData: number[] = [];
  protected categoryLabels: string[] = [];
  protected ablationFixedAxes = "";
  protected paretoAutoOpened = false;
  private readonly disposers: (() => void)[] = [];

  constructor(protected readonly root: HTMLElement, _state: JsonValue = null) {
    this.tooltip = document.createElement("div");
    this.tooltip.id = "plotter-tooltip";
    this.tooltip.style.cssText = `
      position: absolute;
      display: none;
      pointer-events: none;
      padding: 6px 10px;
      background: var(--bg-secondary);
      border: 1px solid var(--border-bright);
      border-radius: 6px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--text-primary);
      white-space: nowrap;
      z-index: 10;
      box-shadow: 0 4px 16px rgba(0,0,0,0.5);
    `;
    root.appendChild(this.tooltip);

    // Subscribe to metrics for the currently selected run
    this.disposers.push(
      runSelection.onChange(() => {
        const runId = runSelection.selectedId;
        if (runId) {
          void this.subscribeToRun(runId);
        }
      }),
      // Initial subscription
      (() => {
        const runId = runSelection.selectedId;
        if (runId) void this.subscribeToRun(runId);
        return () => {}; // Return empty unsubscribe function
      })(),
    );
  }

  private subscribeToRun(runId: string): void {
    // Unsubscribe from previous run if any
    if (this.currentRunUnsubscribe) {
      this.currentRunUnsubscribe();
    }
    this.currentRunUnsubscribe = metricsStore.subscribe(runId, () => {
      const metrics = metricsStore.get(runId);
      if (metrics) {
        this.onRunChanged(runId, metrics);
      }
    });
  }

  private currentRunUnsubscribe: (() => void) | null = null;

  dispose(): void {
    for (const dispose of this.disposers) dispose();
    this.disposers.length = 0;
    this.currentRunUnsubscribe?.();
    this.currentRunUnsubscribe = null;
    this.plot?.destroy();
    this.plot = null;
    this.tooltip?.remove();
    this.tooltip = null;
  }

  protected abstract initPlot(): void;

  abstract refresh(): void;

  private onRunChanged = (
    _runId: string,
    metrics: RunMetrics,
  ): void => {
    this.records = metrics.records ?? [];
    this.paretoFlags = metrics.pareto ?? [];
    this.ablationGroups = metrics.ablation_groups ?? [];
    if (typeof metrics.chance === "number") this.chance = metrics.chance;
    this.refresh();
    this.updateStatus();
  };

  protected updateStatus(): void {
    const hasData = this.records.length > 0;
    const counts = `${this.records.length} records | ${this.paretoFlags.filter((f) => f).length} Pareto`;
    const fixed = this.ablationFixedAxes
      ? ` | fixed: ${this.ablationFixedAxes}`
      : "";
    const statusEl = this.root.querySelector<HTMLElement>(".chart-status");
    const emptyState = this.root.querySelector<HTMLElement>(".chart-empty-state");
    if (statusEl) {
      statusEl.textContent = hasData ? counts + fixed : "No run selected";
      statusEl.title = statusEl.textContent;
    }
    if (emptyState) {
      emptyState.style.display = hasData ? "none" : "flex";
    }
  }

  download(): void {
    if (!this.plot) return;
    const link = document.createElement("a");
    link.download = `computronium-chart-${Date.now()}.png`;
    link.href = this.exportImage(this.plot);
    link.click();
  }

  /** The chart with its axes, not just the plot area. */
  protected exportImage(plot: uPlot): string {
    const canvases = Array.from(
      plot.root.querySelectorAll("canvas"),
    ) as HTMLCanvasElement[];
    const rootRect = plot.root.getBoundingClientRect();

    const width = Math.max(...canvases.map((c) => c.width), 1);
    const height = Math.max(...canvases.map((c) => c.height), 1);
    const output = document.createElement("canvas");
    output.width = width;
    output.height = height;
    const ctx = output.getContext("2d");
    if (!ctx) return plot.ctx.canvas.toDataURL("image/png");

    ctx.fillStyle = PALETTE.bg;
    ctx.fillRect(0, 0, width, height);
    canvases.forEach((canvas) => {
      const rect = canvas.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) return;
      const ratio = canvas.width / rect.width;
      ctx.drawImage(
        canvas,
        (rect.left - rootRect.left) * ratio,
        (rect.top - rootRect.top) * ratio,
        canvas.width,
        canvas.height,
      );
    });
    return output.toDataURL("image/png");
  }

  protected showTooltip(plot: uPlot, content: string): void {
    if (!this.tooltip) return;
    const cursor = plot.cursor;
    if (!cursor || cursor.left == null || cursor.top == null) {
      this.hideTooltip();
      return;
    }
    const canvasRect = plot.ctx.canvas.getBoundingClientRect();
    const panelRect = this.root.getBoundingClientRect();
    this.tooltip.innerHTML = content;
    this.tooltip.style.display = "block";
    this.tooltip.style.left = `${canvasRect.left - panelRect.left + plot.bbox.left + cursor.left + 14}px`;
    this.tooltip.style.top = `${canvasRect.top - panelRect.top + plot.bbox.top + cursor.top + 14}px`;
  }

  protected hideTooltip(): void {
    if (this.tooltip) this.tooltip.style.display = "none";
  }

  /** The banded charts' tooltip names the arm and its spread. */
  protected showCategoryTooltip(
    plot: uPlot,
    kind: "ablation" | "variability",
  ): void {
    const cursor = plot.cursor;
    if (!cursor || cursor.left == null || cursor.top == null) {
      this.hideTooltip();
      return;
    }

    const index = Math.round(plot.posToVal(cursor.left, "x"));
    if (index < 0 || index >= this.categoryLabels.length) {
      this.hideTooltip();
      return;
    }
    const arm = this.categoryLabels[index];

    if (kind === "ablation") {
      const group = this.ablationGroups.find((g) => g.axis === "credit");
      const metric = group?.metrics.find((m) => m.metric === "val_acc");
      const stats = metric?.arms[index];
      if (!stats) {
        this.hideTooltip();
        return;
      }
      this.showTooltip(
        plot,
        `${arm} · ${stats.mean.toFixed(3)} ± ${stats.std.toFixed(3)} (n=${stats.count})${stats.at_chance ? " · at chance" : ""}`,
      );
      return;
    }

    const values = this.records
      .filter((r) => r.coordinate.credit === arm)
      .map((r) => r.payload.val_acc)
      .filter((v): v is number => typeof v === "number")
      .sort((a, b) => a - b);
    if (values.length === 0) {
      this.hideTooltip();
      return;
    }
    const median = values[Math.floor(values.length * 0.5)];
    const q1 = values[Math.floor(values.length * 0.25)];
    const q3 = values[Math.floor(values.length * 0.75)];
    this.showTooltip(
      plot,
      `${arm} · median ${median.toFixed(3)} · IQR ${(q3 - q1).toFixed(3)} · n=${values.length}`,
    );
  }

  protected fitScale(
    plot: uPlot,
    key: "x" | "y",
    min: number,
    max: number,
  ): void {
    if (!Number.isFinite(min) || !Number.isFinite(max)) return;
    if (min === max) {
      min -= 0.01;
      max += 0.01;
    }
    const pad = (max - min) * 0.05;
    plot.setScale(key, { min: min - pad, max: max + pad });
  }

  protected categoryIndices(): number[] {
    return this.categoryLabels.map((_, i) => i);
  }
}

/** Pareto Chart View. */
export class PlotterParetoView extends PlotterChartView {
  constructor(host: HTMLElement, _state: JsonValue = null) {
    super(host);
    initEmptyState("pareto", host, "◭", "Pareto frontier", "p");
    this.initPlot();
  }

  protected initPlot(): void {
    const panel = document.getElementById("plotter-pareto-chart") as HTMLDivElement;
    if (!panel) return;

    const opts: uPlot.Options = {
      width: panel.clientWidth,
      height: chartHeight(panel),
      title: "Pareto Frontier: validation accuracy vs speed",
      axes: [
        {
          label: "1 / walltime_s   (faster →)",
          grid: { stroke: PALETTE.border },
        },
        {
          label: "accuracy",
          grid: { stroke: PALETTE.border },
          side: 1,
        },
      ],
      scales: {
        x: { time: false },
        y: { time: false },
      },
      series: [
        {}, // x: 1/walltime_s
        {
          label: "val_acc",
          stroke: PALETTE.gradient,
          width: 0,
          points: {
            show: true,
            size: 8,
            stroke: "white",
            width: 1,
            fill: (u: uPlot, i: number) => {
              const recordIndex = this.paretoRecordIndices[i];
              const record =
                recordIndex === undefined ? undefined : this.records[recordIndex];
              if (!record) return PALETTE.gradient;
              return ARM_COLORS[record.coordinate?.credit] || PALETTE.gradient;
            },
          },
        },
      ],
      hooks: {
        draw: [
          (u: uPlot) => {
            const ctx = u.ctx;

            // The Pareto frontier: the cells that are not beaten on both axes.
            if (this.paretoFlags.some((f) => f)) {
              const paretoPoints: [number, number][] = [];
              this.records.forEach((r, recordIdx) => {
                if (
                  this.paretoFlags[recordIdx] &&
                  r.payload.walltime_s &&
                  r.payload.val_acc
                ) {
                  paretoPoints.push([
                    1 / r.payload.walltime_s,
                    r.payload.val_acc,
                  ]);
                }
              });
              paretoPoints.sort((a, b) => a[0] - b[0]);

              if (paretoPoints.length > 1) {
                ctx.beginPath();
                ctx.strokeStyle = PALETTE.pareto;
                ctx.lineWidth = 2;
                ctx.setLineDash([5, 5]);

                paretoPoints.forEach((p, i) => {
                  const pxCanvas = u.valToPos(p[0], "x");
                  const pyCanvas = u.valToPos(p[1], "y");
                  if (i === 0) ctx.moveTo(pxCanvas, pyCanvas);
                  else ctx.lineTo(pxCanvas, pyCanvas);
                });
                ctx.stroke();
                ctx.setLineDash([]);
              }

              paretoPoints.forEach((p) => {
                const pxCanvas = u.valToPos(p[0], "x");
                const pyCanvas = u.valToPos(p[1], "y");
                ctx.beginPath();
                ctx.arc(pxCanvas, pyCanvas, 7, 0, Math.PI * 2);
                ctx.strokeStyle = PALETTE.pareto;
                ctx.lineWidth = 1.5;
                ctx.stroke();
              });
            }

            // Chance line: what every point is measured against.
            const chanceY = u.valToPos(this.chance, "y");
            ctx.strokeStyle = PALETTE.chance_line;
            ctx.lineWidth = 1.5;
            ctx.setLineDash([4, 4]);
            ctx.beginPath();
            ctx.moveTo(u.bbox.left, chanceY);
            ctx.lineTo(u.bbox.width, chanceY);
            ctx.stroke();
            ctx.setLineDash([]);
          },
        ],
        setCursor: [
          (u: uPlot) => {
            this.showScatterTooltip(u);
          },
        ],
      },
      cursor: {
        show: true,
        drag: { setScale: true },
        focus: { prox: 16 },
      },
    };

    this.plot = new uPlot(opts, [[], []], panel);

    // Wire download button
    this.root.querySelector<HTMLElement>(".chart-download")!.addEventListener("click", () => this.download());
  }

  refresh(): void {
    if (!this.plot || this.records.length === 0) return;

    const xData: number[] = [];
    const yData: number[] = [];
    this.paretoRecordIndices = [];

    this.records.forEach((r, recordIndex) => {
      const wt = r.payload.walltime_s;
      const acc = r.payload.val_acc;
      this.paretoRecordIndices.push(recordIndex);
      if (wt && acc) {
        xData.push(1 / wt);
        yData.push(acc);
      } else {
        xData.push(NaN);
        yData.push(NaN);
      }
    });

    this.plot.setData([xData, yData]);
    this.paretoXData = xData;
    this.paretoYData = yData;

    const xs = xData.filter(Number.isFinite);
    const ys = yData.filter(Number.isFinite);
    if (xs.length > 0) {
      this.fitScale(this.plot, "x", Math.min(...xs), Math.max(...xs));
    }
    if (ys.length > 0) {
      this.fitScale(
        this.plot,
        "y",
        Math.min(Math.min(...ys), this.chance),
        Math.max(...ys),
      );
    }
  }

  /** The record behind a plotted point: a gap holds no record. */
  private recordAt(dataIndex: number): RecordData | undefined {
    const recordIndex = this.paretoRecordIndices[dataIndex];
    return recordIndex === undefined ? undefined : this.records[recordIndex];
  }

  /** The scatter's tooltip names the record behind the point. */
  private showScatterTooltip(plot: uPlot): void {
    const cursor = plot.cursor;
    if (!cursor || cursor.left == null || cursor.top == null) {
      this.hideTooltip();
      return;
    }

    let bestIndex = -1;
    let bestDistance = Infinity;
    this.paretoXData.forEach((x, i) => {
      const y = this.paretoYData[i];
      if (!Number.isFinite(x) || !Number.isFinite(y)) return;
      const px = plot.valToPos(x, "x");
      const py = plot.valToPos(y, "y");
      if (!Number.isFinite(px) || !Number.isFinite(py)) return;
      const distance = (px - cursor.left!) ** 2 + (py - cursor.top!) ** 2;
      if (distance < bestDistance) {
        bestDistance = distance;
        bestIndex = i;
      }
    });

    if (bestIndex < 0 || bestDistance > 400) {
      this.hideTooltip();
      return;
    }

    const record = this.recordAt(bestIndex);
    if (!record) {
      this.hideTooltip();
      return;
    }
    const recordIndex = this.paretoRecordIndices[bestIndex];
    const arm = record.coordinate?.credit ?? "?";
    const acc = record.payload.val_acc ?? 0;
    const walltime = record.payload.walltime_s ?? 0;
    const seed = record.schedule?.seed ?? "?";
    const pareto = this.paretoFlags[recordIndex] ? " · PARETO" : "";
    this.showTooltip(
      plot,
      `${arm} · val_acc ${acc.toFixed(3)} · ${walltime.toFixed(1)}s · seed ${seed}${pareto}`,
    );
  }
}

/** Ablation Chart View. */
export class PlotterAblationView extends PlotterChartView {
  constructor(host: HTMLElement, _state: JsonValue = null) {
    super(host);
    initEmptyState("ablation", host, "▥", "Ablation", "a");
    this.initPlot();
  }

  protected initPlot(): void {
    const panel = document.getElementById(
      "plotter-ablation-chart",
    ) as HTMLDivElement;
    if (!panel) return;

    const opts: uPlot.Options = {
      width: panel.clientWidth,
      height: chartHeight(panel),
      title: "Ablation: credit arm → validation accuracy",
      axes: [
        {
          label: "credit arm",
          splits: () => this.categoryIndices(),
          values: (_u, splits) =>
            splits.map((i) => this.categoryLabels[i] ?? String(i)),
          grid: { stroke: PALETTE.border },
        },
        {
          label: "accuracy",
          grid: { stroke: PALETTE.border },
          side: 1,
        },
      ],
      scales: { x: { time: false }, y: { time: false } },
      series: [
        {},
        { label: "val_acc", width: 0, points: { show: false } },
      ],
      hooks: {
        draw: [
          (u: uPlot) => {
            if (!this.ablationGroups.length) return;
            const ctx = u.ctx;
            const group = this.ablationGroups.find((g) => g.axis === "credit");
            if (!group) return;

            const metricData = group.metrics.find(
              (m) => m.metric === "val_acc",
            );
            if (!metricData) return;

            const arms = metricData.arms;
            const barW = u.bbox.width / (arms.length * 1.5);

            arms.forEach((arm, i) => {
              const x = u.valToPos(i, "x");
              const y0 = u.valToPos(0, "y");
              const y1 = u.valToPos(arm.mean, "y");
              const h = y0 - y1;

              ctx.fillStyle = ARM_COLORS[arm.value] || PALETTE.gradient;
              ctx.fillRect(x - barW / 2, y1, barW, h);

              // Error bar
              if (arm.std > 0) {
                const yErr = u.valToPos(arm.mean + arm.std, "y");
                ctx.strokeStyle = PALETTE.text_muted;
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(x, yErr);
                ctx.lineTo(x, y0);
                ctx.stroke();
                // Caps
                ctx.moveTo(x - 3, yErr);
                ctx.lineTo(x + 3, yErr);
                ctx.stroke();
              }
            });

            // Chance line
            const chanceY = u.valToPos(this.chance, "y");
            ctx.strokeStyle = PALETTE.chance_line;
            ctx.lineWidth = 2;
            ctx.setLineDash([5, 5]);
            ctx.beginPath();
            ctx.moveTo(u.bbox.left, chanceY);
            ctx.lineTo(u.bbox.width, chanceY);
            ctx.stroke();
            ctx.setLineDash([]);
          },
        ],
        setCursor: [
          (u: uPlot) => {
            this.showCategoryTooltip(u, "ablation");
          },
        ],
      },
      cursor: { show: true, drag: { setScale: true } },
    };

    this.plot = new uPlot(opts, [[], []], panel);
    this.root.querySelector<HTMLElement>(".chart-download")!.addEventListener("click", () => this.download());
  }

  refresh(): void {
    if (!this.plot || !this.ablationGroups.length) return;

    const group = this.ablationGroups.find((g) => g.axis === "credit");
    if (!group) return;

    const metricData = group.metrics.find((m) => m.metric === "val_acc");
    if (!metricData) return;

    const xData = metricData.arms.map((_, i) => i);
    const yData = metricData.arms.map((a) => a.mean);
    this.categoryLabels = metricData.arms.map((arm) => arm.value);
    this.ablationFixedAxes = group.fixed_axes
      .split(",")
      .map((entry) => entry.split("=").pop() ?? entry)
      .join(", ");

    this.plot.setData([xData, yData]);
    this.fitScale(this.plot, "x", -0.5, Math.max(xData.length - 0.5, 0.5));

    const values = metricData.arms.flatMap((arm) => [
      arm.mean - arm.std,
      arm.mean + arm.std,
    ]);
    if (values.length > 0) {
      this.fitScale(
        this.plot,
        "y",
        Math.min(Math.min(...values), this.chance),
        Math.max(...values),
      );
    }
    const title = this.plot.root.querySelector(".u-title");
    if (title) {
      title.textContent = `Ablation: ${group.axis} vs val_acc`;
    }
  }

  /** The banded charts' tooltip names the arm and its spread. */
  showCategoryTooltip(
    plot: uPlot,
    kind: "ablation" | "variability",
  ): void {
    const cursor = plot.cursor;
    if (!cursor || cursor.left == null || cursor.top == null) {
      this.hideTooltip();
      return;
    }

    const index = Math.round(plot.posToVal(cursor.left, "x"));
    if (index < 0 || index >= this.categoryLabels.length) {
      this.hideTooltip();
      return;
    }
    const arm = this.categoryLabels[index];

    if (kind === "ablation") {
      const group = this.ablationGroups.find((g) => g.axis === "credit");
      const metric = group?.metrics.find((m) => m.metric === "val_acc");
      const stats = metric?.arms[index];
      if (!stats) {
        this.hideTooltip();
        return;
      }
      this.showTooltip(
        plot,
        `${arm} · ${stats.mean.toFixed(3)} ± ${stats.std.toFixed(3)} (n=${stats.count})${stats.at_chance ? " · at chance" : ""}`,
      );
      return;
    }

    const values = this.records
      .filter((r) => r.coordinate.credit === arm)
      .map((r) => r.payload.val_acc)
      .filter((v): v is number => typeof v === "number")
      .sort((a, b) => a - b);
    if (values.length === 0) {
      this.hideTooltip();
      return;
    }
    const median = values[Math.floor(values.length * 0.5)];
    const q1 = values[Math.floor(values.length * 0.25)];
    const q3 = values[Math.floor(values.length * 0.75)];
    this.showTooltip(
      plot,
      `${arm} · median ${median.toFixed(3)} · IQR ${(q3 - q1).toFixed(3)} · n=${values.length}`,
    );
  }
}

/** Variability Chart View. */
export class PlotterVariabilityView extends PlotterChartView {
  constructor(host: HTMLElement, _state: JsonValue = null) {
    super(host);
    initEmptyState("variability", host, "◇", "Variability", "s");
    this.initPlot();
  }

  protected initPlot(): void {
    const panel = document.getElementById(
      "plotter-variability-chart",
    ) as HTMLDivElement;
    if (!panel) return;

    const opts: uPlot.Options = {
      width: panel.clientWidth,
      height: chartHeight(panel),
      title: "Seed variability: validation accuracy per arm",
      axes: [
        {
          label: "credit arm",
          splits: () => this.categoryIndices(),
          values: (_u, splits) =>
            splits.map((i) => this.categoryLabels[i] ?? String(i)),
          grid: { stroke: PALETTE.border },
        },
        {
          label: "accuracy",
          grid: { stroke: PALETTE.border },
          side: 1,
        },
      ],
      scales: { x: { time: false }, y: { time: false } },
      series: [
        {},
        { label: "val_acc", width: 0, points: { show: false } },
      ],
      hooks: {
        draw: [
          (u: uPlot) => {
            if (!this.records.length) return;
            const ctx = u.ctx;

            // Group records by credit arm
            const byArm: Record<string, number[]> = {};
            this.records.forEach((r) => {
              const arm = r.coordinate.credit;
              const acc = r.payload.val_acc;
              if (acc !== undefined) {
                (byArm[arm] ||= []).push(acc);
              }
            });

            const arms = Object.keys(byArm).sort();
            const boxW = u.bbox.width / (arms.length * 2);

            arms.forEach((arm, i) => {
              const values = byArm[arm].sort((a, b) => a - b);
              const n = values.length;
              if (n === 0) return;

              const q1 = values[Math.floor(n * 0.25)];
              const median = values[Math.floor(n * 0.5)];
              const q3 = values[Math.floor(n * 0.75)];
              const iqr = q3 - q1;
              const min = Math.max(values[0], q1 - 1.5 * iqr);
              const max = Math.min(values[n - 1], q3 + 1.5 * iqr);

              const x = u.valToPos(i, "x");
              const yMin = u.valToPos(min, "y");
              const yQ1 = u.valToPos(q1, "y");
              const yMed = u.valToPos(median, "y");
              const yQ3 = u.valToPos(q3, "y");
              const yMax = u.valToPos(max, "y");

              const color = ARM_COLORS[arm] || PALETTE.gradient;

              // Whiskers
              ctx.strokeStyle = color;
              ctx.lineWidth = 1.5;
              ctx.beginPath();
              ctx.moveTo(x, yMin);
              ctx.lineTo(x, yQ1);
              ctx.moveTo(x, yQ3);
              ctx.lineTo(x, yMax);
              ctx.stroke();

              // Box
              ctx.fillStyle = color + "44";
              ctx.strokeStyle = color;
              ctx.lineWidth = 1.5;
              ctx.fillRect(x - boxW / 2, yQ3, boxW, yQ1 - yQ3);
              ctx.strokeRect(x - boxW / 2, yQ3, boxW, yQ1 - yQ3);

              // Median line
              ctx.strokeStyle = "white";
              ctx.lineWidth = 2;
              ctx.beginPath();
              ctx.moveTo(x - boxW / 2, yMed);
              ctx.lineTo(x + boxW / 2, yMed);
              ctx.stroke();

              // Outliers
              values.forEach((v) => {
                if (v < min || v > max) {
                  const y = u.valToPos(v, "y");
                  ctx.fillStyle = color;
                  ctx.beginPath();
                  ctx.arc(x, y, 2, 0, Math.PI * 2);
                  ctx.fill();
                }
              });
            });

            // Chance line
            const chanceY = u.valToPos(this.chance, "y");
            ctx.strokeStyle = PALETTE.chance_line;
            ctx.lineWidth = 2;
            ctx.setLineDash([5, 5]);
            ctx.beginPath();
            ctx.moveTo(u.bbox.left, chanceY);
            ctx.lineTo(u.bbox.width, chanceY);
            ctx.stroke();
            ctx.setLineDash([]);
          },
        ],
        setCursor: [
          (u: uPlot) => {
            this.showCategoryTooltip(u, "variability");
          },
        ],
      },
      cursor: { show: true, drag: { setScale: true } },
    };

    this.plot = new uPlot(opts, [[], []], panel);
    this.root.querySelector<HTMLElement>(".chart-download")!.addEventListener("click", () => this.download());
  }

  refresh(): void {
    if (!this.plot || !this.records.length) return;

    // The boxes are drawn by the hook from this.records; the series only
    // carries the arm positions and the axis range.
    const arms = Array.from(
      new Set(this.records.map((r) => r.coordinate.credit)),
    ).sort();
    const xData = arms.map((_, i) => i);
    const yData = arms.map(() => 0);
    this.categoryLabels = arms;
    this.plot.setData([xData, yData]);
    this.fitScale(
      this.plot,
      "x",
      -0.5,
      Math.max(arms.length - 0.5, 0.5),
    );

    const values = this.records
      .map((r) => r.payload.val_acc)
      .filter((v): v is number => typeof v === "number");
    if (values.length > 0) {
      this.fitScale(
        this.plot,
        "y",
        Math.min(Math.min(...values), this.chance),
        Math.max(...values),
      );
    }
  }
}

/** Options for per-instance chart views. */
export interface PerInstanceChartViewOptions {
  runId: string | null;
  axes: AxisSelection;
  metricsStore: MetricsStoreInterface;
  workspace: WorkspaceStoreInterface;
}

/** Base class for per-instance chart views using shared stores. */
abstract class PerInstanceChartView {
  protected plot: uPlot | null = null;
  protected tooltip: HTMLElement | null = null;
  protected records: RecordData[] = [];
  protected ablationGroups: AblationGroup[] = [];
  protected paretoFlags: boolean[] = [];
  protected chance = 0.1;
  protected paretoRecordIndices: number[] = [];
  protected paretoXData: number[] = [];
  protected paretoYData: number[] = [];
  protected categoryLabels: string[] = [];
  protected ablationFixedAxes = "";
  private readonly disposers: (() => void)[] = [];
  private currentRunUnsubscribe: (() => void) | null = null;

  constructor(
    protected readonly root: HTMLElement,
    protected readonly options: PerInstanceChartViewOptions,
  ) {
    this.tooltip = document.createElement("div");
    this.tooltip.id = `plotter-tooltip-${Math.random().toString(36).slice(2)}`;
    this.tooltip.style.cssText = `
      position: absolute;
      display: none;
      pointer-events: none;
      padding: 6px 10px;
      background: var(--bg-secondary);
      border: 1px solid var(--border-bright);
      border-radius: 6px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--text-primary);
      white-space: nowrap;
      z-index: 10;
      box-shadow: 0 4px 16px rgba(0,0,0,0.5);
    `;
    root.appendChild(this.tooltip);

    this.initPlot();
    this.subscribeToRun();
  }

  protected abstract initPlot(): void;

  protected abstract onMetricsChange(metrics: RunMetrics): void;

  protected updateStatus(): void {
    const hasData = this.records.length > 0;
    const counts = `${this.records.length} records | ${this.paretoFlags.filter((f) => f).length} Pareto`;
    const fixed = this.ablationFixedAxes
      ? ` | fixed: ${this.ablationFixedAxes}`
      : "";
    const statusEl = this.root.querySelector<HTMLElement>(".chart-status");
    const emptyState = this.root.querySelector<HTMLElement>(".chart-empty-state");
    if (statusEl) {
      statusEl.textContent = hasData ? counts + fixed : "No run selected";
      statusEl.title = statusEl.textContent;
    }
    if (emptyState) {
      emptyState.style.display = hasData ? "none" : "flex";
    }
  }

  private subscribeToRun(): void {
    if (this.currentRunUnsubscribe) {
      this.currentRunUnsubscribe();
    }
    const { runId, metricsStore } = this.options;
    if (runId) {
      this.currentRunUnsubscribe = metricsStore.subscribe(runId, () => {
        const metrics = metricsStore.get(runId);
        if (metrics) {
          this.onMetricsChange(metrics);
        }
      });
    }
  }

  updateRunAndAxes(runId: string | null, axes: AxisSelection): void {
    this.options.runId = runId;
    this.options.axes = axes;
    this.subscribeToRun();
  }

  download(): void {
    if (!this.plot) return;
    const link = document.createElement("a");
    link.download = `computronium-chart-${Date.now()}.png`;
    link.href = this.exportImage(this.plot);
    link.click();
  }

  /** The chart with its axes, not just the plot area. */
  protected exportImage(plot: uPlot): string {
    const canvases = Array.from(
      plot.root.querySelectorAll("canvas"),
    ) as HTMLCanvasElement[];
    const rootRect = plot.root.getBoundingClientRect();

    const width = Math.max(...canvases.map((c) => c.width), 1);
    const height = Math.max(...canvases.map((c) => c.height), 1);
    const output = document.createElement("canvas");
    output.width = width;
    output.height = height;
    const ctx = output.getContext("2d");
    if (!ctx) return plot.ctx.canvas.toDataURL("image/png");

    ctx.fillStyle = PALETTE.bg;
    ctx.fillRect(0, 0, width, height);
    canvases.forEach((canvas) => {
      const rect = canvas.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) return;
      const ratio = canvas.width / rect.width;
      ctx.drawImage(
        canvas,
        (rect.left - rootRect.left) * ratio,
        (rect.top - rootRect.top) * ratio,
        canvas.width,
        canvas.height,
      );
    });
    return output.toDataURL("image/png");
  }

  protected showTooltip(plot: uPlot, content: string): void {
    if (!this.tooltip) return;
    const cursor = plot.cursor;
    if (!cursor || cursor.left == null || cursor.top == null) {
      this.hideTooltip();
      return;
    }
    const canvasRect = plot.ctx.canvas.getBoundingClientRect();
    const panelRect = this.root.getBoundingClientRect();
    this.tooltip.innerHTML = content;
    this.tooltip.style.display = "block";
    this.tooltip.style.left = `${canvasRect.left - panelRect.left + plot.bbox.left + cursor.left + 14}px`;
    this.tooltip.style.top = `${canvasRect.top - panelRect.top + plot.bbox.top + cursor.top + 14}px`;
  }

  protected hideTooltip(): void {
    if (this.tooltip) this.tooltip.style.display = "none";
  }

  protected fitScale(
    plot: uPlot,
    key: "x" | "y",
    min: number,
    max: number,
  ): void {
    if (!Number.isFinite(min) || !Number.isFinite(max)) return;
    if (min === max) {
      min -= 0.01;
      max += 0.01;
    }
    const pad = (max - min) * 0.05;
    plot.setScale(key, { min: min - pad, max: max + pad });
  }

  protected categoryIndices(): number[] {
    return this.categoryLabels.map((_, i) => i);
  }

  /** The banded charts' tooltip names the arm and its spread. */
  protected showCategoryTooltip(
    plot: uPlot,
    kind: "ablation" | "variability",
  ): void {
    const cursor = plot.cursor;
    if (!cursor || cursor.left == null || cursor.top == null) {
      this.hideTooltip();
      return;
    }

    const index = Math.round(plot.posToVal(cursor.left, "x"));
    if (index < 0 || index >= this.categoryLabels.length) {
      this.hideTooltip();
      return;
    }
    const arm = this.categoryLabels[index];

    if (kind === "ablation") {
      const group = this.ablationGroups.find((g) => g.axis === "credit");
      const metric = group?.metrics.find((m) => m.metric === "val_acc");
      const stats = metric?.arms[index];
      if (!stats) {
        this.hideTooltip();
        return;
      }
      this.showTooltip(
        plot,
        `${arm} · ${stats.mean.toFixed(3)} ± ${stats.std.toFixed(3)} (n=${stats.count})${stats.at_chance ? " · at chance" : ""}`,
      );
      return;
    }

    const values = this.records
      .filter((r) => r.coordinate.credit === arm)
      .map((r) => r.payload.val_acc)
      .filter((v): v is number => typeof v === "number")
      .sort((a, b) => a - b);
    if (values.length === 0) {
      this.hideTooltip();
      return;
    }
    const median = values[Math.floor(values.length * 0.5)];
    const q1 = values[Math.floor(values.length * 0.25)];
    const q3 = values[Math.floor(values.length * 0.75)];
    this.showTooltip(
      plot,
      `${arm} · median ${median.toFixed(3)} · IQR ${(q3 - q1).toFixed(3)} · n=${values.length}`,
    );
  }

  dispose(): void {
    for (const dispose of this.disposers) dispose();
    this.disposers.length = 0;
    this.currentRunUnsubscribe?.();
    this.currentRunUnsubscribe = null;
    this.plot?.destroy();
    this.plot = null;
    this.tooltip?.remove();
    this.tooltip = null;
  }
}

/** Pareto Chart View (per-instance). */
export class ParetoChartView extends PerInstanceChartView {
  protected initPlot(): void {
    const panel = this.root.querySelector<HTMLDivElement>("[id^='chart-']") as HTMLDivElement;
    if (!panel) return;

    const opts: uPlot.Options = {
      width: panel.clientWidth,
      height: chartHeight(panel),
      title: "Pareto Frontier: validation accuracy vs speed",
      axes: [
        {
          label: "1 / walltime_s   (faster →)",
          grid: { stroke: PALETTE.border },
        },
        {
          label: "accuracy",
          grid: { stroke: PALETTE.border },
          side: 1,
        },
      ],
      scales: {
        x: { time: false },
        y: { time: false },
      },
      series: [
        {}, // x: 1/walltime_s
        {
          label: "val_acc",
          stroke: PALETTE.gradient,
          width: 0,
          points: {
            show: true,
            size: 8,
            stroke: "white",
            width: 1,
            fill: (u: uPlot, i: number) => {
              const recordIndex = this.paretoRecordIndices[i];
              const record =
                recordIndex === undefined ? undefined : this.records[recordIndex];
              if (!record) return PALETTE.gradient;
              return ARM_COLORS[record.coordinate?.credit] || PALETTE.gradient;
            },
          },
        },
      ],
      hooks: {
        draw: [
          (u: uPlot) => {
            const ctx = u.ctx;

            // The Pareto frontier: the cells that are not beaten on both axes.
            if (this.paretoFlags.some((f) => f)) {
              const paretoPoints: [number, number][] = [];
              this.records.forEach((r, recordIdx) => {
                if (
                  this.paretoFlags[recordIdx] &&
                  r.payload.walltime_s &&
                  r.payload.val_acc
                ) {
                  paretoPoints.push([
                    1 / r.payload.walltime_s,
                    r.payload.val_acc,
                  ]);
                }
              });
              paretoPoints.sort((a, b) => a[0] - b[0]);

              if (paretoPoints.length > 1) {
                ctx.beginPath();
                ctx.strokeStyle = PALETTE.pareto;
                ctx.lineWidth = 2;
                ctx.setLineDash([5, 5]);

                paretoPoints.forEach((p, i) => {
                  const pxCanvas = u.valToPos(p[0], "x");
                  const pyCanvas = u.valToPos(p[1], "y");
                  if (i === 0) ctx.moveTo(pxCanvas, pyCanvas);
                  else ctx.lineTo(pxCanvas, pyCanvas);
                });
                ctx.stroke();
                ctx.setLineDash([]);
              }

              paretoPoints.forEach((p) => {
                const pxCanvas = u.valToPos(p[0], "x");
                const pyCanvas = u.valToPos(p[1], "y");
                ctx.beginPath();
                ctx.arc(pxCanvas, pyCanvas, 7, 0, Math.PI * 2);
                ctx.strokeStyle = PALETTE.pareto;
                ctx.lineWidth = 1.5;
                ctx.stroke();
              });
            }

            // Chance line: what every point is measured against.
            const chanceY = u.valToPos(this.chance, "y");
            ctx.strokeStyle = PALETTE.chance_line;
            ctx.lineWidth = 1.5;
            ctx.setLineDash([4, 4]);
            ctx.beginPath();
            ctx.moveTo(u.bbox.left, chanceY);
            ctx.lineTo(u.bbox.width, chanceY);
            ctx.stroke();
            ctx.setLineDash([]);
          },
        ],
        setCursor: [
          (u: uPlot) => {
            this.showScatterTooltip(u);
          },
        ],
      },
      cursor: {
        show: true,
        drag: { setScale: true },
        focus: { prox: 16 },
      },
    };

    this.plot = new uPlot(opts, [[], []], panel);

    // Wire download button
    this.root.querySelector<HTMLElement>(".chart-download")!.addEventListener("click", () => this.download());
  }

  protected onMetricsChange(metrics: RunMetrics): void {
    this.records = metrics.records ?? [];
    this.paretoFlags = metrics.pareto ?? [];
    this.ablationGroups = metrics.ablation_groups ?? [];
    if (typeof metrics.chance === "number") this.chance = metrics.chance;
    this.refresh();
    this.updateStatus();
  }

  /** Pareto is relevant when there are Pareto cells (non-dominated on accuracy + speed). */
  protected isRelevant(): boolean {
    return this.paretoFlags.some((f) => f);
  }

  protected override updateStatus(): void {
    const hasData = this.isRelevant();
    const counts = `${this.records.length} records | ${this.paretoFlags.filter((f) => f).length} Pareto`;
    const statusEl = this.root.querySelector<HTMLElement>(".chart-status");
    const emptyState = this.root.querySelector<HTMLElement>(".chart-empty-state");
    if (statusEl) {
      statusEl.textContent = hasData ? counts : "No Pareto cells yet";
      statusEl.title = statusEl.textContent;
    }
    if (emptyState) {
      emptyState.style.display = hasData ? "none" : "flex";
    }
  }

  refresh(): void {
    if (!this.plot || !this.isRelevant()) return;

    const xData: number[] = [];
    const yData: number[] = [];
    this.paretoRecordIndices = [];

    this.records.forEach((r, recordIndex) => {
      const wt = r.payload.walltime_s;
      const acc = r.payload.val_acc;
      this.paretoRecordIndices.push(recordIndex);
      if (wt && acc) {
        xData.push(1 / wt);
        yData.push(acc);
      } else {
        xData.push(NaN);
        yData.push(NaN);
      }
    });

    this.plot.setData([xData, yData]);
    this.paretoXData = xData;
    this.paretoYData = yData;

    const xs = xData.filter(Number.isFinite);
    const ys = yData.filter(Number.isFinite);
    if (xs.length > 0) {
      this.fitScale(this.plot, "x", Math.min(...xs), Math.max(...xs));
    }
    if (ys.length > 0) {
      this.fitScale(
        this.plot,
        "y",
        Math.min(Math.min(...ys), this.chance),
        Math.max(...ys),
      );
    }
  }

  /** The record behind a plotted point: a gap holds no record. */
  private recordAt(dataIndex: number): RecordData | undefined {
    const recordIndex = this.paretoRecordIndices[dataIndex];
    return recordIndex === undefined ? undefined : this.records[recordIndex];
  }

  /** The scatter's tooltip names the record behind the point. */
  private showScatterTooltip(plot: uPlot): void {
    const cursor = plot.cursor;
    if (!cursor || cursor.left == null || cursor.top == null) {
      this.hideTooltip();
      return;
    }

    let bestIndex = -1;
    let bestDistance = Infinity;
    this.paretoXData.forEach((x, i) => {
      const y = this.paretoYData[i];
      if (!Number.isFinite(x) || !Number.isFinite(y)) return;
      const px = plot.valToPos(x, "x");
      const py = plot.valToPos(y, "y");
      if (!Number.isFinite(px) || !Number.isFinite(py)) return;
      const distance = (px - cursor.left!) ** 2 + (py - cursor.top!) ** 2;
      if (distance < bestDistance) {
        bestDistance = distance;
        bestIndex = i;
      }
    });

    if (bestIndex < 0 || bestDistance > 400) {
      this.hideTooltip();
      return;
    }

    const record = this.recordAt(bestIndex);
    if (!record) {
      this.hideTooltip();
      return;
    }
    const recordIndex = this.paretoRecordIndices[bestIndex];
    const arm = record.coordinate?.credit ?? "?";
    const acc = record.payload.val_acc ?? 0;
    const walltime = record.payload.walltime_s ?? 0;
    const seed = record.schedule?.seed ?? "?";
    const pareto = this.paretoFlags[recordIndex] ? " · PARETO" : "";
    this.showTooltip(
      plot,
      `${arm} · val_acc ${acc.toFixed(3)} · ${walltime.toFixed(1)}s · seed ${seed}${pareto}`,
    );
  }
}

/** Ablation Chart View (per-instance). */
export class AblationChartView extends PerInstanceChartView {
  protected initPlot(): void {
    const panel = this.root.querySelector<HTMLDivElement>("[id^='chart-']") as HTMLDivElement;
    if (!panel) return;

    const opts: uPlot.Options = {
      width: panel.clientWidth,
      height: chartHeight(panel),
      title: "Ablation: credit arm → validation accuracy",
      axes: [
        {
          label: "credit arm",
          splits: () => this.categoryIndices(),
          values: (_u, splits) =>
            splits.map((i) => this.categoryLabels[i] ?? String(i)),
          grid: { stroke: PALETTE.border },
        },
        {
          label: "accuracy",
          grid: { stroke: PALETTE.border },
          side: 1,
        },
      ],
      scales: { x: { time: false }, y: { time: false } },
      series: [
        {},
        { label: "val_acc", width: 0, points: { show: false } },
      ],
      hooks: {
        draw: [
          (u: uPlot) => {
            if (!this.ablationGroups.length) return;
            const ctx = u.ctx;
            const group = this.ablationGroups.find((g) => g.axis === "credit");
            if (!group) return;

            const metricData = group.metrics.find(
              (m) => m.metric === "val_acc",
            );
            if (!metricData) return;

            const arms = metricData.arms;
            const barW = u.bbox.width / (arms.length * 1.5);

            arms.forEach((arm, i) => {
              const x = u.valToPos(i, "x");
              const y0 = u.valToPos(0, "y");
              const y1 = u.valToPos(arm.mean, "y");
              const h = y0 - y1;

              ctx.fillStyle = ARM_COLORS[arm.value] || PALETTE.gradient;
              ctx.fillRect(x - barW / 2, y1, barW, h);

              // Error bar
              if (arm.std > 0) {
                const yErr = u.valToPos(arm.mean + arm.std, "y");
                ctx.strokeStyle = PALETTE.text_muted;
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(x, yErr);
                ctx.lineTo(x, y0);
                ctx.stroke();
                // Caps
                ctx.moveTo(x - 3, yErr);
                ctx.lineTo(x + 3, yErr);
                ctx.stroke();
              }
            });

            // Chance line
            const chanceY = u.valToPos(this.chance, "y");
            ctx.strokeStyle = PALETTE.chance_line;
            ctx.lineWidth = 2;
            ctx.setLineDash([5, 5]);
            ctx.beginPath();
            ctx.moveTo(u.bbox.left, chanceY);
            ctx.lineTo(u.bbox.width, chanceY);
            ctx.stroke();
            ctx.setLineDash([]);
          },
        ],
        setCursor: [
          (u: uPlot) => {
            this.showCategoryTooltip(u, "ablation");
          },
        ],
      },
      cursor: { show: true, drag: { setScale: true } },
    };

    this.plot = new uPlot(opts, [[], []], panel);
    this.root.querySelector<HTMLElement>(".chart-download")!.addEventListener("click", () => this.download());
  }

  protected onMetricsChange(metrics: RunMetrics): void {
    this.records = metrics.records ?? [];
    this.paretoFlags = metrics.pareto ?? [];
    this.ablationGroups = metrics.ablation_groups ?? [];
    if (typeof metrics.chance === "number") this.chance = metrics.chance;
    this.refresh();
    this.updateStatus();
  }

  /** Ablation is relevant when there are credit-axis ablation groups. */
  protected isRelevant(): boolean {
    return this.ablationGroups.some((g) => g.axis === "credit");
  }

  protected override updateStatus(): void {
    const hasData = this.isRelevant();
    const group = this.ablationGroups.find((g) => g.axis === "credit");
    const counts = group ? `${group.metrics[0]?.arms?.length ?? 0} arms` : "no data";
    const fixed = this.ablationFixedAxes
      ? ` | fixed: ${this.ablationFixedAxes}`
      : "";
    const statusEl = this.root.querySelector<HTMLElement>(".chart-status");
    const emptyState = this.root.querySelector<HTMLElement>(".chart-empty-state");
    if (statusEl) {
      statusEl.textContent = hasData ? counts + fixed : "No ablation data yet";
      statusEl.title = statusEl.textContent;
    }
    if (emptyState) {
      emptyState.style.display = hasData ? "none" : "flex";
    }
  }

  refresh(): void {
    if (!this.plot || !this.isRelevant()) return;

    const group = this.ablationGroups.find((g) => g.axis === "credit");
    if (!group) return;

    const metricData = group.metrics.find((m) => m.metric === "val_acc");
    if (!metricData) return;

    const xData = metricData.arms.map((_, i) => i);
    const yData = metricData.arms.map((a) => a.mean);
    this.categoryLabels = metricData.arms.map((arm) => arm.value);
    this.ablationFixedAxes = group.fixed_axes
      .split(",")
      .map((entry) => entry.split("=").pop() ?? entry)
      .join(", ");

    this.plot.setData([xData, yData]);
    this.fitScale(this.plot, "x", -0.5, Math.max(xData.length - 0.5, 0.5));

    const values = metricData.arms.flatMap((arm) => [
      arm.mean - arm.std,
      arm.mean + arm.std,
    ]);
    if (values.length > 0) {
      this.fitScale(
        this.plot,
        "y",
        Math.min(Math.min(...values), this.chance),
        Math.max(...values),
      );
    }
    const title = this.plot.root.querySelector(".u-title");
    if (title) {
      title.textContent = `Ablation: ${group.axis} vs val_acc`;
    }
  }
}

/** Variability Chart View (per-instance). */
export class VariabilityChartView extends PerInstanceChartView {
  protected initPlot(): void {
    const panel = this.root.querySelector<HTMLDivElement>("[id^='chart-']") as HTMLDivElement;
    if (!panel) return;

    const opts: uPlot.Options = {
      width: panel.clientWidth,
      height: chartHeight(panel),
      title: "Seed variability: validation accuracy per arm",
      axes: [
        {
          label: "credit arm",
          splits: () => this.categoryIndices(),
          values: (_u, splits) =>
            splits.map((i) => this.categoryLabels[i] ?? String(i)),
          grid: { stroke: PALETTE.border },
        },
        {
          label: "accuracy",
          grid: { stroke: PALETTE.border },
          side: 1,
        },
      ],
      scales: { x: { time: false }, y: { time: false } },
      series: [
        {},
        { label: "val_acc", width: 0, points: { show: false } },
      ],
      hooks: {
        draw: [
          (u: uPlot) => {
            if (!this.records.length) return;
            const ctx = u.ctx;

            // Group records by credit arm
            const byArm: Record<string, number[]> = {};
            this.records.forEach((r) => {
              const arm = r.coordinate.credit;
              const acc = r.payload.val_acc;
              if (acc !== undefined) {
                (byArm[arm] ||= []).push(acc);
              }
            });

            const arms = Object.keys(byArm).sort();
            const boxW = u.bbox.width / (arms.length * 2);

            arms.forEach((arm, i) => {
              const values = byArm[arm].sort((a, b) => a - b);
              const n = values.length;
              if (n === 0) return;

              const q1 = values[Math.floor(n * 0.25)];
              const median = values[Math.floor(n * 0.5)];
              const q3 = values[Math.floor(n * 0.75)];
              const iqr = q3 - q1;
              const min = Math.max(values[0], q1 - 1.5 * iqr);
              const max = Math.min(values[n - 1], q3 + 1.5 * iqr);

              const x = u.valToPos(i, "x");
              const yMin = u.valToPos(min, "y");
              const yQ1 = u.valToPos(q1, "y");
              const yMed = u.valToPos(median, "y");
              const yQ3 = u.valToPos(q3, "y");
              const yMax = u.valToPos(max, "y");

              const color = ARM_COLORS[arm] || PALETTE.gradient;

              // Whiskers
              ctx.strokeStyle = color;
              ctx.lineWidth = 1.5;
              ctx.beginPath();
              ctx.moveTo(x, yMin);
              ctx.lineTo(x, yQ1);
              ctx.moveTo(x, yQ3);
              ctx.lineTo(x, yMax);
              ctx.stroke();

              // Box
              ctx.fillStyle = color + "44";
              ctx.strokeStyle = color;
              ctx.lineWidth = 1.5;
              ctx.fillRect(x - boxW / 2, yQ3, boxW, yQ1 - yQ3);
              ctx.strokeRect(x - boxW / 2, yQ3, boxW, yQ1 - yQ3);

              // Median line
              ctx.strokeStyle = "white";
              ctx.lineWidth = 2;
              ctx.beginPath();
              ctx.moveTo(x - boxW / 2, yMed);
              ctx.lineTo(x + boxW / 2, yMed);
              ctx.stroke();

              // Outliers
              values.forEach((v) => {
                if (v < min || v > max) {
                  const y = u.valToPos(v, "y");
                  ctx.fillStyle = color;
                  ctx.beginPath();
                  ctx.arc(x, y, 2, 0, Math.PI * 2);
                  ctx.fill();
                }
              });
            });

            // Chance line
            const chanceY = u.valToPos(this.chance, "y");
            ctx.strokeStyle = PALETTE.chance_line;
            ctx.lineWidth = 2;
            ctx.setLineDash([5, 5]);
            ctx.beginPath();
            ctx.moveTo(u.bbox.left, chanceY);
            ctx.lineTo(u.bbox.width, chanceY);
            ctx.stroke();
            ctx.setLineDash([]);
          },
        ],
        setCursor: [
          (u: uPlot) => {
            this.showCategoryTooltip(u, "variability");
          },
        ],
      },
      cursor: { show: true, drag: { setScale: true } },
    };

    this.plot = new uPlot(opts, [[], []], panel);
    this.root.querySelector<HTMLElement>(".chart-download")!.addEventListener("click", () => this.download());
  }

  protected onMetricsChange(metrics: RunMetrics): void {
    this.records = metrics.records ?? [];
    this.paretoFlags = metrics.pareto ?? [];
    this.ablationGroups = metrics.ablation_groups ?? [];
    if (typeof metrics.chance === "number") this.chance = metrics.chance;
    this.refresh();
    this.updateStatus();
  }

  /** Variability is relevant when any credit arm has >1 seed (multi-seed spread). */
  protected isRelevant(): boolean {
    const byArm: Record<string, number> = {};
    for (const r of this.records) {
      const arm = r.coordinate.credit;
      const acc = r.payload.val_acc;
      if (acc !== undefined) {
        byArm[arm] = (byArm[arm] ?? 0) + 1;
      }
    }
    return Object.values(byArm).some((count) => count > 1);
  }

  protected override updateStatus(): void {
    const hasData = this.isRelevant();
    const byArm: Record<string, number> = {};
    for (const r of this.records) {
      const arm = r.coordinate.credit;
      const acc = r.payload.val_acc;
      if (acc !== undefined) {
        byArm[arm] = (byArm[arm] ?? 0) + 1;
      }
    }
    const counts = Object.entries(byArm)
      .map(([arm, count]) => `${arm}:${count}`)
      .join(", ");
    const statusEl = this.root.querySelector<HTMLElement>(".chart-status");
    const emptyState = this.root.querySelector<HTMLElement>(".chart-empty-state");
    if (statusEl) {
      statusEl.textContent = hasData ? `${counts} (multi-seed)` : "No multi-seed data yet";
      statusEl.title = statusEl.textContent;
    }
    if (emptyState) {
      emptyState.style.display = hasData ? "none" : "flex";
    }
  }

  refresh(): void {
    if (!this.plot || !this.isRelevant()) return;

    // The boxes are drawn by the hook from this.records; the series only
    // carries the arm positions and the axis range.
    const arms = Array.from(
      new Set(this.records.map((r) => r.coordinate.credit)),
    ).sort();
    const xData = arms.map((_, i) => i);
    const yData = arms.map(() => 0);
    this.categoryLabels = arms;
    this.plot.setData([xData, yData]);
    this.fitScale(
      this.plot,
      "x",
      -0.5,
      Math.max(arms.length - 0.5, 0.5),
    );

    const values = this.records
      .map((r) => r.payload.val_acc)
      .filter((v): v is number => typeof v === "number");
    if (values.length > 0) {
      this.fitScale(
        this.plot,
        "y",
        Math.min(Math.min(...values), this.chance),
        Math.max(...values),
      );
    }
  }
}

/** Factory functions for per-instance chart views. */
export function createParetoChartView(
  host: HTMLElement,
  options: PerInstanceChartViewOptions,
): ParetoChartView {
  return new ParetoChartView(host, options);
}

export function createAblationChartView(
  host: HTMLElement,
  options: PerInstanceChartViewOptions,
): AblationChartView {
  return new AblationChartView(host, options);
}

export function createVariabilityChartView(
  host: HTMLElement,
  options: PerInstanceChartViewOptions,
): VariabilityChartView {
  return new VariabilityChartView(host, options);
}

/** Chart specs for the new per-instance definitions. */
export const PARETO_CHART_SPEC = { title: "Pareto frontier", glyph: "◭", hostId: "chart-pareto" };
export const ABLATION_CHART_SPEC = { title: "Ablation", glyph: "▥", hostId: "chart-ablation" };
export const VARIABILITY_CHART_SPEC = { title: "Variability", glyph: "◇", hostId: "chart-variability" };

/** Create chart panel body for per-instance views. */
export function createPerInstanceChartPanelBody(spec: { hostId: string; glyph: string; title: string }): string {
  return `
    <div id="${spec.hostId}" style="flex: 1; position: relative; overflow: hidden;"></div>
    <div class="chart-empty-state" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 20px; text-align: center;">
      <div class="empty-icon" style="font-size: 32px; margin-bottom: 12px; opacity: 0.5;">${spec.glyph}</div>
      <div style="font-size: 13px; font-weight: 600; color: var(--text-primary);">${spec.title}</div>
      <div style="font-size: 11px; color: var(--text-secondary); max-width: 280px; line-height: 1.5; margin-top: 6px;">Select a run from the legend to populate this chart.</div>
      <div style="margin-top: 12px; padding: 8px 12px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 6px; font-size: 10px; color: var(--text-muted);">
        Pick a run in the legend · Press <kbd style="font-family: monospace; padding: 1px 5px; background: var(--bg); border: 1px solid var(--border-bright); border-radius: 3px;">P/A/S</kbd> for charts
      </div>
    </div>
    <div class="chart-toolbar" style="display: flex; align-items: center; justify-content: space-between; padding: 6px 10px; border-top: 1px solid var(--border); background: var(--bg-tertiary); font-size: 10px;">
      <span class="chart-status" style="color: var(--text-secondary);">No data</span>
      <button class="chart-download" title="Download chart as PNG" style="background: none; border: 1px solid var(--border); border-radius: 4px; padding: 2px 8px; color: var(--text-secondary); font-size: 10px; cursor: pointer;">↓ PNG</button>
    </div>
  `;
}