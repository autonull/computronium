/** Claim cost stage view — the seeds measured against the seeds a claim needs (TODO72 P6). */

import { ARM_COLORS, PALETTE } from "../../../colors.js";
import { drawNote, drawRowFrame, type RowFrame } from "../../../stage/plot2d.js";
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

interface Cost {
  cell: CellAggregate;
  label: string;
  color: string;
  measured: number;
  required: number;
}

/** Create a StageViewInstance for the "claim-cost" view. */
export function createClaimCostView(context: StageViewContext): StageViewInstance {
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
    const costs = computeCosts();
    if (costs.length === 0) {
      drawn = false;
      flat.clear();
      return;
    }

    const ctx = flat.begin();
    const area = flat.area();
    const metrics = runId ? metricsStore.get(runId) : null;
    const required = Math.max(
      metrics?.required_seeds ?? 0,
      ...costs.map((cost) => cost.measured),
    );

    const frame = drawRowFrame(ctx, area, {
      xMin: 0,
      xMax: required,
      rows: costs.map((cost) => cost.label),
      title: "The claim's cost",
      subtitle: "the seeds measured, and the seeds a claim still needs",
      xLabel: "seeds",
    });

    const toX = (value: number): number =>
      frame.rect.x + (value / (frame.xMax || 1)) * frame.rect.width;

    costs.forEach((cost, index) => {
      const y = frame.rowY(index);
      const barHeight = Math.min(26, frame.rowHeight * 0.5);

      // The cost of the claim: the channel the seeds would have to fill.
      ctx.fillStyle = PALETTE.bg_tertiary;
      ctx.fillRect(
        frame.rect.x,
        y - barHeight / 2,
        toX(cost.required) - frame.rect.x,
        barHeight,
      );

      // The seeds that were measured.
      const measured = toX(cost.measured) - frame.rect.x;
      ctx.fillStyle = cost.color;
      ctx.fillRect(frame.rect.x, y - barHeight / 2, measured, barHeight);

      // The gap: what is missing, marked as the space it leaves.
      const short = Math.max(0, cost.required - cost.measured);
      if (short > 0) {
        ctx.strokeStyle = PALETTE.warn;
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 4]);
        ctx.beginPath();
        ctx.moveTo(toX(cost.measured) + 4, y);
        ctx.lineTo(toX(cost.required) - 4, y);
        ctx.stroke();
        ctx.setLineDash([]);
      }

      ctx.strokeStyle = PALETTE.border;
      ctx.lineWidth = 1;
      ctx.strokeRect(
        frame.rect.x + 0.5,
        y - barHeight / 2,
        toX(cost.required) - frame.rect.x - 1,
        barHeight - 1,
      );

      // The counts, beside the bar.
      ctx.font = "12px 'JetBrains Mono', monospace";
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      ctx.fillStyle = PALETTE.text_secondary;
      ctx.fillText(
        `${cost.measured} of ${cost.required}`,
        frame.rect.x + frame.rect.width + 12,
        y - 8,
      );
      if (short > 0) {
        ctx.fillStyle = PALETTE.warn;
        ctx.fillText(
          `${short} short`,
          frame.rect.x + frame.rect.width + 12,
          y + 9,
        );
      }
    });

    // The requirement, drawn across every row: the line the run has not reached.
    const requiredSeeds = metrics?.required_seeds ?? 0;
    const requiredX = toX(requiredSeeds);
    if (
      requiredX > frame.rect.x &&
      requiredX < frame.rect.x + frame.rect.width
    ) {
      ctx.strokeStyle = PALETTE.text_secondary;
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 4]);
      ctx.beginPath();
      ctx.moveTo(requiredX, frame.rect.y);
      ctx.lineTo(requiredX, frame.rect.y + frame.rect.height);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    const short = costs.reduce(
      (sum, cost) => sum + Math.max(0, cost.required - cost.measured),
      0,
    );
    drawNote(
      ctx,
      area,
      `the claim is ${short} seeds short over ${costs.length} cells`,
    );

    drawn = true;
  }

  function computeCosts(): Cost[] {
    const metrics = runId ? metricsStore.get(runId) : null;
    const required = metrics?.required_seeds ?? 0;
    const cells = runId ? measuredCellsFromMetrics(metrics, axes) : [];
    const varying = varyingAxes(cells, axes);

    return cells
      .map((cell) => ({
        cell,
        label: cellLabel(cell, axes, varying),
        color: ARM_COLORS[cell.coordinate.credit] ?? PALETTE.gradient,
        measured: cell.seeds,
        required,
      }))
      .sort(
        (left, right) =>
          right.required - right.measured - (left.required - left.measured),
      );
  }

  function cellLabel(cell: CellAggregate, axes: any, varying: any): string {
    const names = varying.length > 0 ? varying : [axes.x, axes.y, axes.z];
    return names.map((name: string) => cell.coordinate[name] ?? "").join(" · ");
  }

  function measuredCellsFromMetrics(metrics: any, axes: any): CellAggregate[] {
    if (!metrics) return [];
    const { aggregateRecords, measuredCells: mc, varyingAxes: va } = require("../../../stage/payloads.js") as any;
    const aggregates = aggregateRecords(metrics, axes);
    const cells = mc(aggregates, axes);
    const varying = va(cells, axes);
    return cells;
  }

  function varyingAxes(cells: CellAggregate[], axes: any): any[] {
    const names: any[] = [axes.x, axes.y, axes.z];
    return names.filter((name) => {
      const values = new Set(cells.map((cell) => cell.coordinate[name]));
      return values.size > 1;
    });
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

/** Register the claim-cost view definition. */
export const claimCostViewDefinition: StageViewDefinition = {
  view: "claim-cost",
  title: "The claim's cost",
  key: "c",
  group: "the evidence",
  create: createClaimCostView,
};