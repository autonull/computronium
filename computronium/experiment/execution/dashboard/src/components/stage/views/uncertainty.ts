/** Uncertainty stage view — each cell's interval against the level a claim needs (TODO72 P6). */

import { ARM_COLORS, PALETTE } from "../../../colors.js";
import { drawNote, drawRowFrame, type RowFrame } from "../../../stage/plot2d.js";
import { metricsStore } from "../../../stores/metrics.js";
import { workspaceStore } from "../../../stores/workspace.js";
import { cellKey, mean, measuredCells, varyingAxes, type CellAggregate } from "../../../stage/payloads.js";
import type {
  StageViewDefinition,
  StageViewInstance,
  StageViewContext,
  StageChange,
  Size,
} from "../../../layout/types.js";

interface Interval {
  cell: CellAggregate;
  label: string;
  color: string;
  mean: number;
  margin: number;
  lower: number;
  upper: number;
  threshold: number;
}

/** Create a StageViewInstance for the "uncertainty" view. */
export function createUncertaintyView(context: StageViewContext): StageViewInstance {
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
    const intervals = computeIntervals();
    if (intervals.length === 0) {
      drawn = false;
      flat.clear();
      return;
    }

    const ctx = flat.begin();
    const area = flat.area();
    const metrics = runId ? metricsStore.get(runId) : null;
    const chance = metrics?.chance ?? 0.1;
    const sigma = computeSigma(metrics);

    const highest = Math.max(
      chance,
      ...intervals.map((interval) =>
        Math.max(interval.upper, interval.threshold),
      ),
    );

    const frame = drawRowFrame(ctx, area, {
      xMin: 0,
      xMax: highest * 1.12,
      rows: intervals.map((interval) => interval.label),
      title: "The uncertainty",
      subtitle: "each cell's mean, and the margin the gate asks for",
      xLabel: "accuracy",
    });

    const toX = (value: number): number =>
      frame.rect.x + (value / (frame.xMax || 1)) * frame.rect.width;

    // The chance level: the line every claim has to clear.
    const chanceX = toX(chance);
    ctx.strokeStyle = PALETTE.chance_line;
    ctx.lineWidth = 1.5;
    ctx.setLineDash([6, 5]);
    ctx.beginPath();
    ctx.moveTo(chanceX, frame.rect.y);
    ctx.lineTo(chanceX, frame.rect.y + frame.rect.height);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.font = "11px 'JetBrains Mono', monospace";
    ctx.textAlign = "left";
    ctx.textBaseline = "alphabetic";
    ctx.fillStyle = PALETTE.chance_line;
    ctx.fillText("chance", chanceX + 6, frame.rect.y + 14);

    intervals.forEach((interval, index) => {
      const y = frame.rowY(index);
      const clears = interval.lower > chance;

      // The margin: the cell's mean, and the error the gate allows it.
      ctx.strokeStyle = interval.color;
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(toX(interval.lower), y);
      ctx.lineTo(toX(interval.upper), y);
      ctx.stroke();

      // The threshold this cell has to clear: chance, plus its own margin.
      ctx.strokeStyle = clears ? PALETTE.ok : PALETTE.warn;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(toX(interval.threshold), y - 11);
      ctx.lineTo(toX(interval.threshold), y + 11);
      ctx.stroke();

      // The mean itself.
      ctx.fillStyle = interval.color;
      ctx.beginPath();
      ctx.arc(toX(interval.mean), y, 5, 0, Math.PI * 2);
      ctx.fill();

      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      ctx.font = "12px 'JetBrains Mono', monospace";
      ctx.fillStyle = clears ? PALETTE.ok : PALETTE.warn;
      ctx.fillText(
        clears ? "clears chance" : "not yet separable",
        frame.rect.x + frame.rect.width + 12,
        y,
      );
    });

    const requiredSeeds = metrics?.required_seeds ?? 0;
    drawNote(
      ctx,
      area,
      `the bar is ±${sigma}·SE · the tick is the threshold each cell has to clear` +
        ` · a claim needs ${requiredSeeds} seeds per cell`,
    );

    drawn = true;
  }

  function computeSigma(metrics: any): number {
    const gate = metrics?.gate;
    if (gate && typeof gate.superiority_margin_sigma === "number") {
      return gate.superiority_margin_sigma;
    }
    return 2;
  }

  function computeIntervals(): Interval[] {
    const metrics = runId ? metricsStore.get(runId) : null;
    const chance = metrics?.chance ?? 0.1;
    const sigma = computeSigma(metrics);
    const cells = runId ? measuredCells(runId, axes) : [];
    const varying = varyingAxes(cells, axes);

    return cells
      .filter((cell) => cell.acc.length > 0)
      .map((cell) => {
        const n = cell.acc.length;
        const meanVal = cell.acc.reduce((sum, v) => sum + v, 0) / n;
        const variance =
          cell.acc.reduce((sum, v) => sum + (v - meanVal) ** 2, 0) /
          Math.max(1, n - 1);
        const error = n > 1 ? Math.sqrt(variance / n) : 0;
        const margin = sigma * error;
        return {
          cell,
          label: cellLabel(cell, axes, varying),
          color: ARM_COLORS[cell.coordinate.credit] ?? PALETTE.gradient,
          mean: meanVal,
          margin,
          lower: meanVal - margin,
          upper: meanVal + margin,
          threshold: chance + margin,
        };
      })
      .sort((left, right) => right.mean - left.mean);
  }

  function cellLabel(cell: CellAggregate, axes: any, varying: any): string {
    const names = varying.length > 0 ? varying : [axes.x, axes.y, axes.z];
    return names.map((name: string) => cell.coordinate[name] ?? "").join(" · ");
  }

  function measuredCells(runId: string, axes: any): CellAggregate[] {
    const metrics = metricsStore.get(runId);
    if (!metrics) return [];
    // We need to reconstruct the aggregates from metrics
    // For simplicity, we'll use the existing utility
    const { aggregateRecords } = require("../../../stage/payloads.js") as any;
    const aggregates = aggregateRecords(metrics, axes);
    const { measuredCells: mc } = require("../../../stage/payloads.js") as any;
    return mc(aggregates, axes);
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

/** Register the uncertainty view definition. */
export const uncertaintyViewDefinition: StageViewDefinition = {
  view: "uncertainty",
  title: "The uncertainty",
  key: "x",
  group: "the evidence",
  create: createUncertaintyView,
};