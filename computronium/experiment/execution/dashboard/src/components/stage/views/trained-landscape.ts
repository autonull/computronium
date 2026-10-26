/** Trained landscape stage view — the cell's own energy over the slice its trajectory crosses, after training (TODO72 P6). */

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

/** Create a StageViewInstance for the "trained-landscape" view. */
export function createTrainedLandscapeView(context: StageViewContext): StageViewInstance {
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
    const landscape = payload?.landscape;
    const trajectory = payload?.trajectory;

    if (!payload || !landscape || landscape.grid.length === 0) {
      drawn = false;
      flat.clear();
      return;
    }

    const ctx = flat.begin();
    const area = flat.area();
    const grid = landscape.grid;
    const flatGrid = grid.flat();
    const lowest = Math.min(...flatGrid);
    const highest = Math.max(...flatGrid);

    const frame = drawFrame(ctx, area, {
      xMin: landscape.x[0],
      xMax: landscape.x[landscape.x.length - 1],
      yMin: landscape.y[0],
      yMax: landscape.y[landscape.y.length - 1],
      xLabel: "along the trajectory",
      yLabel: "across it",
      title: "The trained landscape",
      subtitle: trainedNote(payload),
    });

    const cellWidth = frame.rect.width / (landscape.x.length - 1 || 1);
    const cellHeight = frame.rect.height / (landscape.y.length - 1 || 1);
    ctx.save();
    ctx.beginPath();
    ctx.rect(frame.rect.x, frame.rect.y, frame.rect.width, frame.rect.height);
    ctx.clip();
    grid.forEach((row, i) => {
      row.forEach((value, j) => {
        const t = (value - lowest) / (highest - lowest || 1);
        ctx.fillStyle = rampColor(1 - t);
        const x = frame.rect.x + cellWidth * i;
        const y = frame.rect.y + frame.rect.height - cellHeight * (j + 1);
        ctx.fillRect(x, y, cellWidth + 1, cellHeight + 1);
      });
    });
    ctx.restore();

    if (trajectory && trajectory.path.length > 1) {
      ctx.strokeStyle = PALETTE.text_primary;
      ctx.lineWidth = 2;
      ctx.beginPath();
      trajectory.path.forEach((point, index) => {
        const x = scaleX(point[0], frame);
        const y = scaleY(point[1], frame);
        if (index === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
    }

    let bestX = 0;
    let bestY = 0;
    let bestValue = Number.POSITIVE_INFINITY;
    grid.forEach((row, i) =>
      row.forEach((value, j) => {
        if (value < bestValue) {
          bestValue = value;
          bestX = i;
          bestY = j;
        }
      }),
    );
    const bx = scaleX(landscape.x[bestX], frame);
    const by = scaleY(landscape.y[bestY], frame);
    ctx.strokeStyle = PALETTE.ok;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(bx, by, 7, 0, Math.PI * 2);
    ctx.stroke();
    ctx.font = "12px 'JetBrains Mono', monospace";
    ctx.fillStyle = PALETTE.ok;
    ctx.textAlign = "left";
    ctx.textBaseline = "bottom";
    ctx.fillText("the lowest ground", bx + 11, by - 6);

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

/** Register the trained landscape view definition. */
export const trainedLandscapeViewDefinition: StageViewDefinition = {
  view: "trained-landscape",
  title: "The trained landscape",
  key: "shift+o",
  group: "the system",
  create: createTrainedLandscapeView,
};