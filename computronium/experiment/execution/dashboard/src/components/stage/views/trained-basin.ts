/** Trained basin stage view — how much of the neighbourhood comes back after training (TODO72 P6). */

import { PALETTE } from "../../../colors.js";
import { rampColor } from "../../../stores/ramp.js";
import { drawFrame, drawNote, scaleX, scaleY, type PlotFrame } from "../../../stores/plot2d.js";
import { dynamicsStore } from "../../../stores/dynamics.js";
import { workspaceStore } from "../../../stores/workspace.js";
import type {
  StageViewDefinition,
  StageViewInstance,
  StageViewContext,
  StageChange,
  Size,
} from "../../../layout/types.js";

/** Create a StageViewInstance for the "trained-basin" view. */
export function createTrainedBasinView(context: StageViewContext): StageViewInstance {
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
    const basin = payload?.basin;

    if (!payload || !basin || basin.paths.length === 0) {
      drawn = false;
      flat.clear();
      return;
    }

    const ctx = flat.begin();
    const area = flat.area();
    const paths = basin.paths;
    const farthest = Math.max(...paths.flatMap((path) => path.distances), 1e-6);

    const frame = drawFrame(ctx, area, {
      xMin: 0,
      xMax: paths[0].distances.length,
      yMin: 0,
      yMax: farthest * 1.1,
      xLabel: "steps after the nudge",
      yLabel: "distance from the attractor",
      title: "The trained basin",
      subtitle: trainedNote(payload),
    });

    const radii = basin.radii;
    paths.forEach((path: any) => {
      const index = radii.indexOf(path.radius);
      const t = radii.length > 1 ? index / (radii.length - 1) : 0.5;
      ctx.strokeStyle = path.returned ? PALETTE.ok : rampColor(t);
      ctx.lineWidth = 2;
      ctx.beginPath();
      path.distances.forEach((distance: number, step: number) => {
        const x = scaleX(step, frame);
        const y = scaleY(distance, frame);
        if (step === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
    });

    // The share that came back, over each radius.
    ctx.font = "12px 'JetBrains Mono', monospace";
    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    basin.stability.forEach((share: number, index: number) => {
      const x = frame.rect.x + (frame.rect.width / radii.length) * (index + 0.5);
      ctx.fillStyle = share > 0 ? PALETTE.ok : PALETTE.warn;
      ctx.fillText(`${Math.round(share * 100)}% back`, x, frame.rect.y + 12);
      ctx.fillStyle = PALETTE.text_secondary;
      ctx.fillText(`nudge ${radii[index]}`, x, frame.rect.y + 28);
    });

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
    init,
    mount,
    resize,
    refresh,
    ready,
    dispose,
  };
}

/** Register the trained basin view definition. */
export const trainedBasinViewDefinition: StageViewDefinition = {
  view: "trained-basin",
  title: "The trained basin",
  key: "k",
  group: "the system",
  create: createTrainedBasinView,
};