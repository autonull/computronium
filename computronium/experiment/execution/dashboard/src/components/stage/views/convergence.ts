/** Convergence stage view — accuracy against epoch (TODO72 P6). */

import { ARM_COLORS, PALETTE } from "../../../colors.js";
import { drawFrame, drawNote, scaleX, scaleY, type PlotFrame } from "../../../stage/plot2d.js";
import { metricsStore } from "../../../stores/metrics.js";
import { workspaceStore } from "../../../stores/workspace.js";
import type {
  StageViewDefinition,
  StageViewInstance,
  StageViewContext,
  StageChange,
  Size,
} from "../../../layout/types.js";

interface ArmCurve {
  arm: string;
  points: { epoch: number; val_acc: number }[];
}

/** Create a StageViewInstance for the "convergence" view. */
export function createConvergenceView(context: StageViewContext): StageViewInstance {
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
    const curves = computeCurves();
    if (curves.length === 0) {
      drawn = false;
      flat.clear();
      return;
    }

    const ctx = flat.begin();
    const area = flat.area();
    const metrics = runId ? metricsStore.get(runId) : null;
    const chance = metrics?.chance ?? 0.1;

    const maxEpoch = Math.max(
      ...curves.flatMap((curve) => curve.points.map((point) => point.epoch)),
    );
    const maxAccuracy = Math.max(
      chance,
      ...curves.flatMap((curve) => curve.points.map((point) => point.val_acc)),
    );

    const frame = drawFrame(ctx, area, {
      xMin: 0,
      xMax: maxEpoch,
      yMin: 0,
      yMax: maxAccuracy,
      xLabel: "epoch",
      yLabel: "accuracy",
      title: "Convergence",
      subtitle: "the mean accuracy of each arm, epoch by epoch",
      xTicks: undefined,
      yTicks: undefined,
    });

    // The chance level: what every curve is measured against.
    const chanceY = scaleY(chance, frame);
    ctx.strokeStyle = PALETTE.chance_line;
    ctx.lineWidth = 1.5;
    ctx.setLineDash([6, 5]);
    ctx.beginPath();
    ctx.moveTo(frame.rect.x, chanceY);
    ctx.lineTo(frame.rect.x + frame.rect.width, chanceY);
    ctx.stroke();
    ctx.setLineDash([]);

    curves.forEach((curve) => {
      const color = ARM_COLORS[curve.arm] || PALETTE.gradient;
      ctx.strokeStyle = color;
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      curve.points.forEach((point, index) => {
        const x = scaleX(point.epoch, frame);
        const y = scaleY(point.val_acc, frame);
        if (index === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();

      curve.points.forEach((point) => {
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(scaleX(point.epoch, frame), scaleY(point.val_acc, frame), 3, 0, Math.PI * 2);
        ctx.fill();
      });
    });

    // The arms, named.
    ctx.font = "12px 'JetBrains Mono', monospace";
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    let legendY = frame.rect.y + 10;
    curves.forEach((curve) => {
      const color = ARM_COLORS[curve.arm] || PALETTE.gradient;
      ctx.fillStyle = color;
      ctx.fillRect(frame.rect.x + frame.rect.width + 18, legendY - 5, 10, 10);
      ctx.fillStyle = PALETTE.text_secondary;
      ctx.fillText(curve.arm, frame.rect.x + frame.rect.width + 34, legendY);
      legendY += 20;
    });

    drawNote(
      ctx,
      area,
      `${curves.length} arms · the dashed line is the chance level (${chance.toFixed(2)})`,
    );

    drawn = true;
  }

  function computeCurves(): ArmCurve[] {
    const metrics = runId ? metricsStore.get(runId) : null;
    const records = metrics?.records ?? [];
    const byArm = new Map<string, Map<number, number[]>>();

    records.forEach((record: any) => {
      const curve = record?.payload?.convergence_curve;
      if (!Array.isArray(curve) || curve.length === 0) return;
      const arm = record?.coordinate?.credit ?? "";
      const epochs = byArm.get(arm) ?? new Map<number, number[]>();
      curve.forEach((point: any) => {
        if (typeof point?.epoch !== "number") return;
        if (typeof point?.val_acc !== "number") return;
        const values = epochs.get(point.epoch) ?? [];
        values.push(point.val_acc);
        epochs.set(point.epoch, values);
      });
      byArm.set(arm, epochs);
    });

    return Array.from(byArm.entries()).map(([arm, epochs]) => ({
      arm,
      points: Array.from(epochs.entries())
        .sort((a, b) => a[0] - b[0])
        .map(([epoch, values]) => ({
          epoch,
          val_acc: values.reduce((sum, v) => sum + v, 0) / values.length,
        })),
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

/** Register the convergence view definition. */
export const convergenceViewDefinition: StageViewDefinition = {
  view: "convergence",
  title: "Convergence",
  key: "c",
  group: "the run",
  create: createConvergenceView,
};