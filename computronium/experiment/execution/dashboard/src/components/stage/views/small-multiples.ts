/** Small multiples stage view — one panel per cell, every seed's curve (TODO72 P6). */

import { ARM_COLORS, PALETTE } from "../../../colors.js";
import { drawNote, drawTitle, type Area } from "../../../stage/plot2d.js";
import { metricsStore } from "../../../stores/metrics.js";
import { workspaceStore } from "../../../stores/workspace.js";
import { cellLabel, measuredCells, varyingAxes, type CellAggregate } from "../../../stage/payloads.js";
import type {
  StageViewDefinition,
  StageViewInstance,
  StageViewContext,
  StageChange,
  Size,
} from "../../../layout/types.js";

interface Panel {
  cell: CellAggregate;
  label: string;
  color: string;
  curves: { epoch: number; val_acc: number }[][];
}

/** Create a StageViewInstance for the "multiples" view. */
export function createSmallMultiplesView(context: StageViewContext): StageViewInstance {
  const { flat, workspace, state } = context;

  // Per-instance state derived from state + workspace
  let runId = (state as any).runId ?? workspace.getSelectedRunId();
  let axes = (state as any).axes ?? workspace.getAxes();

  // Subscriptions
  let workspaceUnsub: (() => void) | null = null;
  let metricsUnsub: (() => void) | null = null;

  // View state
  let drawn = false;
  let visible = false;

  async function init(): Promise<void> {
    // Subscribe to workspace changes
    workspaceUnsub = workspace.onChange(() => {
      const newRunId = workspace.getSelectedRunId();
      const newAxes = workspace.getAxes();
      if (newRunId !== runId || newAxes.x !== axes.x || newAxes.y !== axes.y || newAxes.z !== axes.z) {
        runId = newRunId;
        axes = newAxes;
        redraw();
      }
    });

    // Subscribe to metrics for this run
    if (runId) {
      metricsUnsub = metricsStore.subscribe(runId, () => {
        redraw();
      });
    }

    visible = true;
    await redraw();
  }

  function redraw(): void {
    if (!visible) return;
    draw();
  }

  function draw(): void {
    const panels = computePanels();
    if (panels.length === 0) {
      drawn = false;
      flat.clear();
      return;
    }

    const ctx = flat.begin();
    const area = flat.area();
    const metrics = runId ? metricsStore.get(runId) : null;
    const chance = metrics?.chance ?? 0.1;

    const values = panels.flatMap((panel) =>
      panel.curves.flatMap((curve) => curve.map((point) => point.val_acc)),
    );
    const epochs = panels.flatMap((panel) =>
      panel.curves.flatMap((curve) => curve.map((point) => point.epoch)),
    );
    let yMin = Math.min(chance, ...values);
    let yMax = Math.max(chance, ...values);
    if (yMax - yMin < 1e-6) {
      yMin -= 0.05;
      yMax += 0.05;
    }
    const pad = (yMax - yMin) * 0.14;
    yMin -= pad;
    yMax += pad;
    const maxEpoch = Math.max(1, ...epochs);

    const columns = Math.ceil(Math.sqrt(panels.length));
    const rows = Math.ceil(panels.length / columns);
    const gap = 18;
    const gridWidth = area.width - gap * (columns - 1);
    const gridHeight = area.height - 64 - 44 - gap * (rows - 1);
    const panelWidth = gridWidth / columns;
    const panelHeight = gridHeight / rows;

    drawTitle(
      ctx,
      area,
      "Small multiples",
      "every seed of every cell, on one accuracy scale",
    );

    panels.forEach((panel, index) => {
      const column = index % columns;
      const row = Math.floor(index / columns);
      const left = area.x + column * (panelWidth + gap);
      const top = area.y + 64 + row * (panelHeight + gap);

      // The panel's title: the cell, in the arm's colour.
      ctx.fillStyle = panel.color;
      ctx.font = "600 13px 'JetBrains Mono', monospace";
      ctx.textAlign = "left";
      ctx.textBaseline = "alphabetic";
      ctx.fillText(panel.label, left, top + 12);

      const plot = {
        x: left + (column === 0 ? 44 : 10),
        y: top + 30,
        width: panelWidth - (column === 0 ? 54 : 20),
        height: panelHeight - 56,
      };

      ctx.strokeStyle = PALETTE.border;
      ctx.lineWidth = 1;
      ctx.strokeRect(
        plot.x + 0.5,
        plot.y + 0.5,
        plot.width - 1,
        plot.height - 1,
      );

      // The chance level, under every panel: what every seed is measured against.
      const chanceY =
        plot.y + plot.height * (1 - (chance - yMin) / (yMax - yMin));
      ctx.strokeStyle = PALETTE.chance_line;
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(plot.x, chanceY);
      ctx.lineTo(plot.x + plot.width, chanceY);
      ctx.stroke();
      ctx.setLineDash([]);

      // The seeds: one curve each, over the epochs they measured.
      panel.curves.forEach((curve) => {
        ctx.strokeStyle = panel.color;
        ctx.lineWidth = 1.8;
        ctx.beginPath();
        curve.forEach((point, pointIndex) => {
          const x = plot.x + (point.epoch / maxEpoch) * plot.width;
          const y =
            plot.y + plot.height * (1 - (point.val_acc - yMin) / (yMax - yMin));
          if (pointIndex === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        });
        ctx.stroke();
      });

      // The scale, on the first column and the last row only.
      ctx.fillStyle = PALETTE.text_muted;
      ctx.font = "9px 'JetBrains Mono', monospace";
      if (column === 0) {
        ctx.textAlign = "right";
        ctx.textBaseline = "middle";
        [yMax, (yMax + yMin) / 2, yMin].forEach((tick) => {
          const y = plot.y + plot.height * (1 - (tick - yMin) / (yMax - yMin));
          ctx.fillText(tick.toFixed(2), plot.x - 6, y);
        });
      }
      if (row === rows - 1) {
        ctx.textAlign = "left";
        ctx.textBaseline = "top";
        ctx.fillText("epoch 0", plot.x, plot.y + plot.height + 6);
        ctx.textAlign = "right";
        ctx.fillText(
          `epoch ${maxEpoch}`,
          plot.x + plot.width,
          plot.y + plot.height + 6,
        );
      }
    });

    const seeds = panels.reduce((sum, panel) => sum + panel.curves.length, 0);
    drawNote(
      ctx,
      area,
      `${panels.length} cells · ${seeds} seeds` +
        ` · the dashed line is the chance level (${chance.toFixed(2)})`,
    );

    drawn = true;
  }

  function computePanels(): Panel[] {
    const metrics = runId ? metricsStore.get(runId) : null;
    if (!metrics) return [];

    // We need to reconstruct aggregates from metrics
    const { aggregateRecords } = require("../../../stage/payloads.js") as any;
    const aggregates = aggregateRecords(metrics, axes);
    const cells = measuredCells(aggregates, axes);
    const varying = varyingAxes(cells, axes);

    return cells
      .filter((cell) => cell.curves.length > 0)
      .map((cell) => ({
        cell,
        label: cellLabel(cell, axes, varying),
        color: ARM_COLORS[cell.coordinate.credit] ?? PALETTE.gradient,
        curves: cell.curves,
      }));
  }

  // Mount
  function mount(): void {
    // No event listeners needed
  }

  // Resize
  function resize(size: Size): void {
    flat.resize(size);
    if (visible) draw();
  }

  // Refresh
  function refresh(change: StageChange): void {
    if (change.kind === "data" || change.kind === "resize") {
      redraw();
    }
  }

  function ready(): boolean {
    return drawn;
  }

  // Dispose
  function dispose(): void {
    workspaceUnsub?.();
    metricsUnsub?.();
  }

  // Initialize
  init();

  return {
    mount,
    resize,
    refresh,
    ready,
    dispose,
  };
}

/** Register the small multiples view definition. */
export const smallMultiplesViewDefinition: StageViewDefinition = {
  view: "small-multiples",
  title: "Small multiples",
  key: "m",
  group: "the evidence",
  create: createSmallMultiplesView,
};