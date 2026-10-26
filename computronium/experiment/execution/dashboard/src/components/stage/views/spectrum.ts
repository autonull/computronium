/** Spectrum stage view — the Lyapunov exponents, and so the system's stability (TODO72 P6). */

import { PALETTE } from "../../../colors.js";
import { rampColor } from "../../../stores/ramp.js";
import { drawFrame, drawNote, formatTick, niceTicks, scaleX, scaleY, type PlotFrame } from "../../../stores/plot2d.js";
import { dynamicsStore } from "../../../stores/dynamics.js";
import { workspaceStore } from "../../../stores/workspace.js";
import type {
  StageViewDefinition,
  StageViewInstance,
  StageViewContext,
  StageChange,
  Size,
} from "../../../layout/types.js";

/** Create a StageViewInstance for the "spectrum" view. */
export function createSpectrumView(context: StageViewContext): StageViewInstance {
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
    // Subscribe to workspace changes (run selection, axes)
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

    // Subscribe to dynamics for this run
    await updateDynamicsSubscription();

    visible = true;
    await redraw();
  }

  async function updateDynamicsSubscription(): Promise<void> {
    dynamicsUnsub?.();
    if (!runId) return;

    dynamicsUnsub = dynamicsStore.subscribe(runId, false, () => {
      redraw();
    });
  }

  function redraw(): void {
    if (!visible) return;
    draw();
  }

  function draw(): void {
    const payload = runId ? dynamicsStore.get(runId, false) : null;
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
      title: "The spectrum",
      subtitle: cellNote(payload),
      xTicks: niceTicks(0, spectrum.length, 6).filter((tick) => Number.isInteger(tick)),
    });

    // The zero line: what separates a direction that contracts from one that grows.
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

  function cellName(payload: any): string {
    const coordinate = payload.cell?.coordinate ?? {};
    return [coordinate.geometry, coordinate.dynamics, coordinate.credit]
      .filter((part) => typeof part === "string" && part.length > 0)
      .join(" · ");
  }

  function cellNote(payload: any): string {
    const parts: string[] = [];
    const cell = cellName(payload);
    if (cell) parts.push(cell);
    if (payload.cell?.measured_by_run === false) {
      parts.push("a cell of the space, not one the run measured");
    }
    if (payload.trained === false) parts.push("the weights are untrained");
    return parts.join(" · ");
  }

  // Mount: attach event listeners if needed
  function mount(): void {
    // No event listeners needed for 2D view
  }

  // Resize: update canvas size
  function resize(size: Size): void {
    flat.resize(size);
    if (visible) draw();
  }

  // Refresh: handle data/view/resize changes
  function refresh(change: StageChange): void {
    if (change.kind === "data" || change.kind === "resize") {
      redraw();
    }
  }

  function ready(): boolean {
    return drawn;
  }

  // Dispose: clean up everything
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

/** Register the spectrum view definition. */
export const spectrumViewDefinition: StageViewDefinition = {
  view: "spectrum",
  title: "The spectrum",
  key: "shift+m",
  group: "the system",
  create: createSpectrumView,
};