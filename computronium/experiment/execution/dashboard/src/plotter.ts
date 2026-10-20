/** Plotter — uPlot Charts (Pareto, Ablation, Variability) (TODO68 Phase 3). */

import uPlot from "uplot";
import "uplot/dist/uPlot.min.css";
import { registry } from "./components/registry.js";
import { router } from "./ws-client.js";
import { PALETTE, ARM_COLORS } from "./palette.js";
import { runSelection, type RunMetrics } from "./run-selection.js";
import type { Component } from "./components/registry.js";

/** The chart is what the panel leaves once the title has taken its line. */
function chartHeight(panel: HTMLElement): number {
  return Math.max(120, panel.clientHeight - 30);
}

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

export class Plotter implements Component {
  name = "Plotter";

  private container: HTMLElement | null = null;
  private tabsContainer: HTMLElement | null = null;
  private contentContainer: HTMLElement | null = null;
  private tooltip: HTMLElement | null = null;
  private paretoPlot: uPlot | null = null;
  private ablationPlot: uPlot | null = null;
  private variabilityPlot: uPlot | null = null;
  private currentTab = "pareto";
  private records: RecordData[] = [];
  private ablationGroups: AblationGroup[] = [];
  private paretoFlags: boolean[] = [];
  private chance = 0.1;
  /** Data index → record index: a record without a wall time is still plotted
      as a gap, so the two indices are not the same. */
  private paretoRecordIndices: number[] = [];
  private paretoXData: number[] = [];
  private paretoYData: number[] = [];
  /** The category labels the current chart's x axis names. */
  private categoryLabels: string[] = [];
  /** The axes the ablation chart holds fixed. */
  private ablationFixedAxes = "";

  constructor() {
    // Register WebSocket handlers IMMEDIATELY in constructor
    router.register("campaign_metrics", this.onCampaignMetrics);
    runSelection.onChange(this.onRunChanged);
  }

  async init(): Promise<void> {
    this.createUI();
    console.log("[Plotter] Initialized");
  }

  async destroy(): Promise<void> {
    router.unregister("campaign_metrics", this.onCampaignMetrics);
    this.paretoPlot?.destroy();
    this.ablationPlot?.destroy();
    this.variabilityPlot?.destroy();
    this.container?.remove();
  }

  private createUI(): void {
    const overlay = document.getElementById("ui-overlay");
    if (!overlay) return;

    this.container = document.createElement("div");
    this.container.id = "plotter";
    this.container.style.cssText = `
      position: fixed;
      bottom: 140px;
      right: 20px;
      width: 520px;
      height: 430px;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      z-index: 150;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
      transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    `;

    this.container.innerHTML = `
      <div id="plotter-tabs" style="
        display: flex;
        border-bottom: 1px solid var(--border);
        background: var(--bg-tertiary);
        border-radius: 8px 8px 0 0;
      ">
        <button class="plotter-tab active" data-tab="pareto" style="flex: 1;">Pareto</button>
        <button class="plotter-tab" data-tab="ablation" style="flex: 1;">Ablation</button>
        <button class="plotter-tab" data-tab="variability" style="flex: 1;">Variability</button>
      </div>
      <div id="plotter-content" style="flex: 1; position: relative; overflow: hidden;">
        <div id="plotter-pareto" style="width: 100%; height: 100%; display: block;"></div>
        <div id="plotter-ablation" style="width: 100%; height: 100%; display: none;"></div>
        <div id="plotter-variability" style="width: 100%; height: 100%; display: none;"></div>
      </div>
      <div id="plotter-toolbar" style="
        padding: 8px 12px;
        border-top: 1px solid var(--border);
        display: flex;
        gap: 8px;
        align-items: center;
        font-size: 11px;
        color: var(--text-secondary);
      ">
        <span id="plotter-status" style="
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        ">No data</span>
        <div style="flex: 1;"></div>
        <button id="plotter-download" style="
          padding: 4px 10px;
          background: var(--bg-tertiary);
          border: 1px solid var(--border);
          border-radius: 4px;
          color: var(--text-primary);
          font-size: 11px;
          cursor: pointer;
        ">Download PNG</button>
      </div>
    `;

    overlay.appendChild(this.container);
    this.tabsContainer = this.container.querySelector("#plotter-tabs")!;
    this.contentContainer = this.container.querySelector("#plotter-content")!;

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
    this.container.appendChild(this.tooltip);

    // Tab switching
    this.tabsContainer.querySelectorAll(".plotter-tab").forEach((btn) => {
      btn.addEventListener("click", () =>
        this.switchTab(btn.getAttribute("data-tab")!),
      );
    });

    // Download button
    this.container
      .querySelector("#plotter-download")!
      .addEventListener("click", () => this.downloadCurrent());

    // Render the initially active tab
    this.switchTab(this.currentTab);
  }

  /** Show one of the charts: "pareto", "ablation" or "variability". */
  showTab(tab: string): void {
    if (tab === this.currentTab) return;
    this.switchTab(tab);
  }

  private switchTab(tab: string): void {
    this.currentTab = tab;

    // Update tab buttons
    this.tabsContainer!.querySelectorAll(".plotter-tab").forEach((btn) => {
      btn.classList.toggle("active", btn.getAttribute("data-tab") === tab);
    });

    // Show/hide the chart panels
    const panels = {
      pareto: "plotter-pareto",
      ablation: "plotter-ablation",
      variability: "plotter-variability",
    };

    Object.entries(panels).forEach(([key, id]) => {
      const panel = document.getElementById(id);
      if (panel) panel.style.display = key === tab ? "block" : "none";
    });

    // Initialize plot if needed
    if (tab === "pareto" && !this.paretoPlot) this.initParetoPlot();
    if (tab === "ablation" && !this.ablationPlot) this.initAblationPlot();
    if (tab === "variability" && !this.variabilityPlot)
      this.initVariabilityPlot();

    // Update plots with current data
    this.updatePlots();
  }

  private onCampaignMetrics = (data: any): void => {
    const { data: metricsData } = data;
    if (!metricsData?.records) return;

    // The charts show the run the dashboard shows, not whichever run
    // reported last.
    runSelection.observe(data?.campaign_id, metricsData);
  };

  /** The run the reader picked, or the newest one. */
  private onRunChanged = (_runId: string | null, metrics: RunMetrics | null): void => {
    if (!metrics) return;
    this.records = metrics.records ?? [];
    this.paretoFlags = metrics.pareto ?? [];
    this.ablationGroups = metrics.ablation_groups ?? [];
    if (typeof metrics.chance === "number") this.chance = metrics.chance;
    this.updatePlots();
    this.updateStatus();
  };

  private updateStatus(): void {
    const statusEl = this.container?.querySelector<HTMLElement>("#plotter-status");
    if (!statusEl) return;
    const counts = `${this.records.length} records | ${this.paretoFlags.filter((f) => f).length} Pareto`;
    // The ablation chart is only about the arms that share every other
    // axis; saying which ones is what makes its bars comparable.
    const fixed = this.ablationFixedAxes
      ? ` | fixed: ${this.ablationFixedAxes}`
      : "";
    statusEl.textContent = counts + fixed;
    statusEl.title = statusEl.textContent;
  }

  private updatePlots(): void {
    if (this.currentTab === "pareto" && this.paretoPlot)
      this.updateParetoPlot();
    if (this.currentTab === "ablation" && this.ablationPlot)
      this.updateAblationPlot();
    if (this.currentTab === "variability" && this.variabilityPlot)
      this.updateVariabilityPlot();
  }

  // ─── Pareto Plot (scatter: val_acc vs 1/walltime_s) ───
  private initParetoPlot(): void {
    const panel = document.getElementById("plotter-pareto") as HTMLDivElement;
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
                  // Use valToPos for canvas coordinates
                  const pxCanvas = u.valToPos(p[0], "x");
                  const pyCanvas = u.valToPos(p[1], "y");
                  if (i === 0) ctx.moveTo(pxCanvas, pyCanvas);
                  else ctx.lineTo(pxCanvas, pyCanvas);
                });
                ctx.stroke();
                ctx.setLineDash([]);
              }

              // A ring marks the frontier's points without taking their arm's
              // colour away from them.
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

    this.paretoPlot = new uPlot(opts, [[], []], panel);
  }

  /** The record behind a plotted point: a gap holds no record. */
  private recordAt(dataIndex: number): RecordData | undefined {
    const recordIndex = this.paretoRecordIndices[dataIndex];
    return recordIndex === undefined ? undefined : this.records[recordIndex];
  }

  private updateParetoPlot(): void {
    if (!this.paretoPlot || this.records.length === 0) return;

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

    this.paretoPlot.setData([xData, yData]);
    this.paretoXData = xData;
    this.paretoYData = yData;

    const xs = xData.filter(Number.isFinite);
    const ys = yData.filter(Number.isFinite);
    if (xs.length > 0) {
      this.fitScale(this.paretoPlot, "x", Math.min(...xs), Math.max(...xs));
    }
    if (ys.length > 0) {
      // The chance line is part of what the chart is about: it stays in view.
      this.fitScale(
        this.paretoPlot,
        "y",
        Math.min(Math.min(...ys), this.chance),
        Math.max(...ys),
      );
    }
  }

  /**
   * Fit an axis to the data it shows.
   *
   * uPlot's automatic range only ever widens, so a chart that first saw a
   * partial dataset keeps that window forever — and a chart fed placeholder
   * data keeps the placeholder's. The range is therefore stated explicitly,
   * after every set of data.
   */
  private fitScale(plot: uPlot, key: "x" | "y", min: number, max: number): void {
    if (!Number.isFinite(min) || !Number.isFinite(max)) return;
    if (min === max) {
      min -= 0.01;
      max += 0.01;
    }
    const pad = (max - min) * 0.05;
    plot.setScale(key, { min: min - pad, max: max + pad });
  }

  // ─── Ablation Plot (grouped bars) ───
  private initAblationPlot(): void {
    const panel = document.getElementById("plotter-ablation") as HTMLDivElement;
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
        // The draw hook draws the bars; uPlot must not draw a series over
        // them.
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
            const x0 = u.bbox.left;

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

    this.ablationPlot = new uPlot(opts, [[], []], panel);
  }

  private updateAblationPlot(): void {
    if (!this.ablationPlot || !this.ablationGroups.length) return;

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

    this.ablationPlot.setData([xData, yData]);
    this.fitScale(this.ablationPlot, "x", -0.5, Math.max(xData.length - 0.5, 0.5));

    const values = metricData.arms.flatMap((arm) => [
      arm.mean - arm.std,
      arm.mean + arm.std,
    ]);
    if (values.length > 0) {
      this.fitScale(
        this.ablationPlot,
        "y",
        Math.min(Math.min(...values), this.chance),
        Math.max(...values),
      );
    }
    // uPlot has no setTitle: the title is a div it made.
    const title = this.ablationPlot.root.querySelector(".u-title");
    if (title) {
      title.textContent = `Ablation: ${group.axis} vs val_acc`;
    }
    // uPlot's redraw() re-sets the x scale from the scale's own (empty)
    // range, which throws away the range this chart states. setScale has
    // already scheduled the redraw.
  }

  // ─── Variability Plot (box plots per arm) ───
  private initVariabilityPlot(): void {
    const panel = document.getElementById(
      "plotter-variability",
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
        // The draw hook draws the bars; uPlot must not draw a series over
        // them.
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

    this.variabilityPlot = new uPlot(opts, [[], []], panel);
  }

  private updateVariabilityPlot(): void {
    if (!this.variabilityPlot || !this.records.length) return;

    // The boxes are drawn by the hook from this.records; the series only
    // carries the arm positions and the axis range.
    const arms = Array.from(
      new Set(this.records.map((r) => r.coordinate.credit)),
    ).sort();
    const xData = arms.map((_, i) => i);
    const yData = arms.map(() => 0);
    this.categoryLabels = arms;
    this.variabilityPlot.setData([xData, yData]);
    this.fitScale(
      this.variabilityPlot,
      "x",
      -0.5,
      Math.max(arms.length - 0.5, 0.5),
    );

    const values = this.records
      .map((r) => r.payload.val_acc)
      .filter((v): v is number => typeof v === "number");
    if (values.length > 0) {
      this.fitScale(
        this.variabilityPlot,
        "y",
        Math.min(Math.min(...values), this.chance),
        Math.max(...values),
      );
    }
  }

  /** The category positions the x axis splits on. */
  private categoryIndices(): number[] {
    return this.categoryLabels.map((_, i) => i);
  }

  /** The tooltip follows the cursor and says what the point is. */
  private showTooltip(plot: uPlot, content: string): void {
    if (!this.tooltip || !this.container) return;
    const cursor = plot.cursor;
    if (!cursor || cursor.left == null || cursor.top == null) {
      this.hideTooltip();
      return;
    }
    const canvasRect = plot.ctx.canvas.getBoundingClientRect();
    const containerRect = this.container.getBoundingClientRect();
    this.tooltip.innerHTML = content;
    this.tooltip.style.display = "block";
    this.tooltip.style.left = `${canvasRect.left - containerRect.left + plot.bbox.left + cursor.left + 14}px`;
    this.tooltip.style.top = `${canvasRect.top - containerRect.top + plot.bbox.top + cursor.top + 14}px`;
  }

  private hideTooltip(): void {
    if (this.tooltip) this.tooltip.style.display = "none";
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

  /** The banded charts' tooltip names the arm and its spread. */
  private showCategoryTooltip(plot: uPlot, kind: "ablation" | "variability"): void {
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

  private downloadCurrent(): void {
    const plotMap: Record<string, uPlot | null> = {
      pareto: this.paretoPlot,
      ablation: this.ablationPlot,
      variability: this.variabilityPlot,
    };
    const plot = plotMap[this.currentTab];
    if (!plot) return;

    const link = document.createElement("a");
    link.download = `computronium-${this.currentTab}-${Date.now()}.png`;
    link.href = this.exportImage(plot);
    link.click();
  }

  /** The chart with its axes, not just the plot area.

    uPlot draws the axes on their own canvases; the plot area alone is a
    rectangle of points with no labels on it.
  */
  private exportImage(plot: uPlot): string {
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
}

export const plotter = new Plotter();
registry.register(plotter);
