/** Trained spectrum stage view — the Lyapunov exponents after training (TODO72 P6). */

import { PALETTE } from "../../../colors.js";
import { drawFrame, drawNote, formatTick, niceTicks, scaleX, scaleY, type PlotFrame } from "../../../stage/plot2d.js";
import { dynamicsStore } from "../../../stores/dynamics.js";
import { workspaceStore } from "../../../stores/workspace.js";
import type {
  StageViewDefinition,
  StageViewInstance,
  StageViewContext,
  StageChange,
  Size,
} from "../../../layout/types.js";

/** Create a StageViewInstance for the "trained-spectrum" view. */
export function createTrainedSpectrumView(context: StageViewContext): StageViewInstance {
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
    const spectrum = payload?.spectrum;

    if (!payload || !spectrum || spectrum.length === 0) {
      drawn = false;
      flat.clear();
      return;
    }

    const ctx = flat.begin();
    const area = flat.area();
    const largest = Math.max(...spectrum.map((value) => Math.abs(value)), 1e-6);
    const top = largest * 1.25;

    const frame = drawFrame(ctx, area, {
      xMin: 0,
      xMax: spectrum.length,
      yMin: -top,
      yMax: top,
      xLabel: "direction",
      yLabel: "growth per step",
      title: "The trained spectrum",
      subtitle: trainedNote(payload),
      xTicks: niceTicks(0, spectrum.length, 6).filter((tick) => Number.isInteger(tick)),
    });

    const zero = scaleY(0, frame);
    ctx.strokeStyle = PALETTE.text_muted;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(frame.rect.x, zero);
    ctx.lineTo(frame.rect.x + frame.rect.width, zero);
    ctx.stroke();

    const band = frame.rect.width / spectrum.length;
    spectrum.forEach((value, index) => {
      const centre = frame.rect.x + band * (index + 0.5);
      const width = Math.min(46, band * 0.5);
      const y = scaleY(value, frame);
      const growing = value > 0;
      ctx.fillStyle = growing ? PALETTE.warn : PALETTE.ok;
      ctx.fillRect(centre - width / 2, Math.min(y, zero), width, Math.abs(y - zero));
      ctx.font = "11px 'JetBrains Mono', monospace";
      ctx.fillStyle = growing ? PALETTE.warn : PALETTE.ok;
      ctx.textAlign = "center";
      ctx.textBaseline = growing ? "bottom" : "top";
      ctx.fillText(formatTick(value), centre, growing ? y - 5 : y + 5);
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

/** Register the trained spectrum view definition. */
export const trainedSpectrumViewDefinition: StageViewDefinition = {
  view: "trained-spectrum",
  title: "The trained spectrum",
  key: "i",
  group: "the system",
  create: createTrainedSpectrumView,
};