/** Trained trajectory stage view — the state's own path through the state space after training (TODO72 P6). */

import { PALETTE } from "../../../colors.js";
import { rampColor } from "../../../stage/ramp.js";
import { drawFrame, drawNote, scaleX, scaleY, type PlotFrame } from "../../../stage/plot2d.js";
import { dynamicsStore } from "../../../stores/dynamics.js";
import { workspaceStore } from "../../../stores/workspace.js";
import type {
  StageViewDefinition,
  StageViewInstance,
  StageViewContext,
  StageChange,
  Size,
} from "../../../layout/types.js";

/** Create a StageViewInstance for the "trained-trajectory" view. */
export function createTrainedTrajectoryView(context: StageViewContext): StageViewInstance {
  const { flat, workspace, state } = context;

  // Per-instance state derived from state + workspace
  let runId = (state as any).runId ?? workspace.getSelectedRunId();
  let axes = (state as any).axes ?? workspace.getAxes();

  // Subscriptions
  let workspaceUnsub: (() => void) | null = null;
  let dynamicsUnsub: (() => void) | null = null;

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
        updateDynamicsSubscription();
        redraw();
      }
    });

    // Subscribe to trained dynamics for this run
    await updateDynamicsSubscription();

    visible = true;
    await redraw();
  }

  async function updateDynamicsSubscription(): Promise<void> {
    dynamicsUnsub?.();
    if (!runId) return;

    dynamicsUnsub = dynamicsStore.subscribe(runId, true, () => {
      redraw();
    });
  }

  function redraw(): void {
    if (!visible) return;
    draw();
  }

  function draw(): void {
    const payload = runId ? dynamicsStore.get(runId, true) : null;
    const trajectory = payload?.trajectory;

    if (!payload || !trajectory || trajectory.path.length < 2) {
      drawn = false;
      flat.clear();
      return;
    }

    const ctx = flat.begin();
    const area = flat.area();
    const path = trajectory.path;
    const xs = path.map((point) => point[0]);
    const ys = path.map((point) => point[1]);
    const pad = 0.08;
    const xMin = Math.min(...xs);
    const xMax = Math.max(...xs);
    const yMin = Math.min(...ys);
    const yMax = Math.max(...ys);
    const xSpan = xMax - xMin || 1;
    const ySpan = yMax - yMin || 1;

    const frame = drawFrame(ctx, area, {
      xMin: xMin - xSpan * pad,
      xMax: xMax + xSpan * pad,
      yMin: yMin - ySpan * pad,
      yMax: yMax + ySpan * pad,
      xLabel: trajectory.axes[0] ?? "the direction the state moved",
      yLabel: trajectory.axes[1] ?? "the direction across it",
      title: "The trained trajectory",
      subtitle: trainedNote(payload),
    });

    for (let index = 1; index < path.length; index += 1) {
      const t = index / (path.length - 1);
      ctx.strokeStyle = rampColor(t);
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(scaleX(path[index - 1][0], frame), scaleY(path[index - 1][1], frame));
      ctx.lineTo(scaleX(path[index][0], frame), scaleY(path[index][1], frame));
      ctx.stroke();
    }

    const mark = (point: number[], color: string, label: string) => {
      const x = scaleX(point[0], frame);
      const y = scaleY(point[1], frame);
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, 5, 0, Math.PI * 2);
      ctx.fill();
      ctx.font = "12px 'JetBrains Mono', monospace";
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      ctx.fillText(label, x + 10, y);
    };
    mark(path[0], PALETTE.text_primary, "where it started");
    mark(path[path.length - 1], PALETTE.warn, "where it stopped");

    const errors = trajectory.error ?? [];
    if (errors.length > 1) {
      const lowest = Math.min(...errors);
      const highest = Math.max(...errors);
      const band = frame.rect.height * 0.16;
      const base = frame.rect.y + frame.rect.height - band * 0.5;
      const toY = (value: number): number =>
        base - ((value - lowest) / (highest - lowest || 1)) * band * 0.5;
      ctx.strokeStyle = PALETTE.thermodynamic_contrast;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      errors.forEach((value, index) => {
        const x = frame.rect.x + (index / (errors.length - 1)) * frame.rect.width;
        if (index === 0) ctx.moveTo(x, toY(value));
        else ctx.lineTo(x, toY(value));
      });
      ctx.stroke();
      ctx.font = "11px 'JetBrains Mono', monospace";
      ctx.fillStyle = PALETTE.thermodynamic_contrast;
      ctx.textAlign = "right";
      ctx.textBaseline = "bottom";
      ctx.fillText(
        "the prediction error",
        frame.rect.x + frame.rect.width,
        base - band * 0.6,
      );
    }

    drawNote(ctx, area, payload.verdict ?? "");
    drawn = true;
  }

  function trainedCellName(payload: any): string {
    const coordinate = payload.cell?.coordinate ?? {};
    return [coordinate.geometry, coordinate.dynamics, coordinate.credit]
      .filter((part) => typeof part === "string" && part.length > 0)
      .join(" · ");
  }

  function trainedNote(payload: any): string {
    const parts: string[] = [];
    const cell = trainedCellName(payload);
    if (cell) parts.push(cell);
    if (payload.cell?.measured_by_run === false) {
      parts.push("a cell of the space, not one the run measured");
    }
    if (payload.trained === true) parts.push("the weights were trained first");
    return parts.join(" · ");
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
    dynamicsUnsub?.();
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

/** Register the trained trajectory view definition. */
export const trainedTrajectoryViewDefinition: StageViewDefinition = {
  view: "trained-trajectory",
  title: "The trained trajectory",
  key: "g",
  group: "the system",
  create: createTrainedTrajectoryView,
};