/** Plotter — uPlot Charts (Pareto, Ablation, Variability) (TODO68 Phase 3). */

import uPlot from "uplot";
import "uplot/dist/uPlot.min.css";
import { registry } from "./components/registry.js";
import { router } from "./ws-client.js";
import { PALETTE, ARM_COLORS } from "./palette.js";
import type { Component } from "./components/registry.js";

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
  private paretoPlot: uPlot | null = null;
  private ablationPlot: uPlot | null = null;
  private variabilityPlot: uPlot | null = null;
  private currentTab = "pareto";
  private records: RecordData[] = [];
  private ablationGroups: AblationGroup[] = [];
  private paretoFlags: boolean[] = [];

  constructor() {
    // Register WebSocket handlers IMMEDIATELY in constructor
    router.register("campaign_metrics", this.onCampaignMetrics.bind(this));
  }

  async init(): Promise<void> {
    this.createUI();
    console.log("[Plotter] Initialized");
  }

  async destroy(): Promise<void> {
    router.unregister("campaign_metrics", this.onCampaignMetrics.bind(this));
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
      bottom: 20px;
      right: 20px;
      width: 520px;
      height: 380px;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      z-index: 150;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
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
        <canvas id="plotter-pareto" style="width: 100%; height: 100%; display: block;"></canvas>
        <canvas id="plotter-ablation" style="width: 100%; height: 100%; display: none;"></canvas>
        <canvas id="plotter-variability" style="width: 100%; height: 100%; display: none;"></canvas>
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
        <span id="plotter-status">No data</span>
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
  }

  private switchTab(tab: string): void {
    this.currentTab = tab;

    // Update tab buttons
    this.tabsContainer!.querySelectorAll(".plotter-tab").forEach((btn) => {
      btn.classList.toggle("active", btn.getAttribute("data-tab") === tab);
    });

    // Show/hide canvases
    const canvases = {
      pareto: "plotter-pareto",
      ablation: "plotter-ablation",
      variability: "plotter-variability",
    };

    Object.entries(canvases).forEach(([key, id]) => {
      const canvas = document.getElementById(id) as HTMLCanvasElement;
      if (canvas) canvas.style.display = key === tab ? "block" : "none";
    });

    // Initialize plot if needed
    if (tab === "pareto" && !this.paretoPlot) this.initParetoPlot();
    if (tab === "ablation" && !this.ablationPlot) this.initAblationPlot();
    if (tab === "variability" && !this.variabilityPlot)
      this.initVariabilityPlot();

    // Update plots with current data
    this.updatePlots();
  }

  private onCampaignMetrics(data: any): void {
    const { data: metricsData } = data;
    if (!metricsData?.records) return;

    this.records = metricsData.records;
    this.paretoFlags = metricsData.pareto || [];
    this.ablationGroups = metricsData.ablation_groups || [];
    this.updatePlots();
    this.updateStatus();
  }

  private updateStatus(): void {
    const statusEl = this.container?.querySelector("#plotter-status");
    if (statusEl) {
      statusEl.textContent = `${this.records.length} records | ${this.paretoFlags.filter((f) => f).length} Pareto`;
    }
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
    const canvas = document.getElementById(
      "plotter-pareto",
    ) as HTMLCanvasElement;
    if (!canvas) return;

    const opts: uPlot.Options = {
      width: canvas.clientWidth,
      height: canvas.clientHeight,
      title: "Pareto Frontier: val_acc vs 1/walltime_s",
      axes: [
        { grid: { stroke: PALETTE.border } },
        { grid: { stroke: PALETTE.border }, side: 1 },
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
          fill: PALETTE.gradient + "33",
          width: 0,
          points: {
            show: true,
            size: 6,
            stroke: "white",
            width: 1,
            fill: (u: uPlot, i: number) => {
              return this.paretoFlags[i]
                ? PALETTE.pareto
                : ARM_COLORS[this.records[i]?.coordinate?.credit] ||
                    PALETTE.gradient;
            },
          },
        },
      ],
      hooks: {
        draw: [
          (u: uPlot) => {
            // Draw Pareto frontier line
            if (this.paretoFlags.some((f) => f)) {
              const paretoPoints: [number, number][] = [];
              this.records.forEach((r, i) => {
                if (
                  this.paretoFlags[i] &&
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
                const ctx = u.ctx;
                ctx.beginPath();
                ctx.strokeStyle = PALETTE.pareto;
                ctx.lineWidth = 2;
                ctx.setLineDash([5, 5]);

                paretoPoints.forEach((p, i) => {
                  const [px, py] = [
                    u.posToVal(p[0], "x"),
                    u.posToVal(p[1], "y"),
                  ];
                  // Use valToPos for canvas coordinates
                  const pxCanvas = u.valToPos(p[0], "x");
                  const pyCanvas = u.valToPos(p[1], "y");
                  if (i === 0) ctx.moveTo(pxCanvas, pyCanvas);
                  else ctx.lineTo(pxCanvas, pyCanvas);
                });
                ctx.stroke();
                ctx.setLineDash([]);
              }
            }
          },
        ],
      },
      cursor: {
        show: true,
        drag: { setScale: true },
        focus: { prox: 16 },
      },
    };

    this.paretoPlot = new uPlot(opts, [[], []], canvas);
  }

  private updateParetoPlot(): void {
    if (!this.paretoPlot || this.records.length === 0) return;

    const xData: number[] = [];
    const yData: number[] = [];

    this.records.forEach((r) => {
      const wt = r.payload.walltime_s;
      const acc = r.payload.val_acc;
      if (wt && acc) {
        xData.push(1 / wt);
        yData.push(acc);
      } else {
        xData.push(NaN);
        yData.push(NaN);
      }
    });

    this.paretoPlot.setData([xData, yData]);
  }

  // ─── Ablation Plot (grouped bars) ───
  private initAblationPlot(): void {
    const canvas = document.getElementById(
      "plotter-ablation",
    ) as HTMLCanvasElement;
    if (!canvas) return;

    const opts: uPlot.Options = {
      width: canvas.clientWidth,
      height: canvas.clientHeight,
      title: "Ablation: Credit Arm vs val_acc",
      axes: [
        { grid: { stroke: PALETTE.border } },
        { grid: { stroke: PALETTE.border }, side: 1 },
      ],
      scales: { x: { time: false }, y: { time: false } },
      series: [
        {},
        {
          label: "val_acc",
          fill: PALETTE.gradient,
          stroke: PALETTE.gradient,
          width: 0,
        },
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
            const chanceY = u.valToPos(0.1, "y");
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
      },
      cursor: { show: true, drag: { setScale: true } },
    };

    this.ablationPlot = new uPlot(opts, [[], []], canvas);
  }

  private updateAblationPlot(): void {
    if (!this.ablationPlot || !this.ablationGroups.length) return;

    const group = this.ablationGroups.find((g) => g.axis === "credit");
    if (!group) return;

    const metricData = group.metrics.find((m) => m.metric === "val_acc");
    if (!metricData) return;

    const xData = metricData.arms.map((_, i) => i);
    const yData = metricData.arms.map((a) => a.mean);

    this.ablationPlot.setData([xData, yData]);
    // uPlot doesn't have setTitle, update title via options
    (this.ablationPlot as any).opts.title =
      `Ablation: ${group.axis} vs val_acc (fixed: ${group.fixed_axes})`;
    this.ablationPlot.redraw();
  }

  // ─── Variability Plot (box plots per arm) ───
  private initVariabilityPlot(): void {
    const canvas = document.getElementById(
      "plotter-variability",
    ) as HTMLCanvasElement;
    if (!canvas) return;

    const opts: uPlot.Options = {
      width: canvas.clientWidth,
      height: canvas.clientHeight,
      title: "Seed Variability: val_acc per Credit Arm",
      axes: [
        { grid: { stroke: PALETTE.border } },
        { grid: { stroke: PALETTE.border }, side: 1 },
      ],
      scales: { x: { time: false }, y: { time: false } },
      series: [
        {},
        {
          label: "val_acc",
          fill: PALETTE.gradient,
          stroke: PALETTE.gradient,
          width: 0,
        },
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
            const chanceY = u.valToPos(0.1, "y");
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
      },
      cursor: { show: true, drag: { setScale: true } },
    };

    this.variabilityPlot = new uPlot(opts, [[], []], canvas);
  }

  private updateVariabilityPlot(): void {
    if (!this.variabilityPlot || !this.records.length) return;

    // Trigger redraw via setData with dummy data
    const arms = Array.from(
      new Set(this.records.map((r) => r.coordinate.credit)),
    ).sort();
    const xData = arms.map((_, i) => i);
    const yData = arms.map(() => 0); // yData not directly used, draw hook reads this.records
    this.variabilityPlot.setData([xData, yData]);
  }

  private downloadCurrent(): void {
    const canvasMap: Record<string, string> = {
      pareto: "plotter-pareto",
      ablation: "plotter-ablation",
      variability: "plotter-variability",
    };
    const canvas = document.getElementById(
      canvasMap[this.currentTab],
    ) as HTMLCanvasElement;
    if (!canvas) return;

    const link = document.createElement("a");
    link.download = `computronium-${this.currentTab}-${Date.now()}.png`;
    link.href = canvas.toDataURL("image/png");
    link.click();
  }
}

registry.register(new Plotter());
