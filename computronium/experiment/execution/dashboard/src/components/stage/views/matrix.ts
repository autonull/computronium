/** Matrix stage view — the evidence matrix, the space seen from above (TODO72 P6). */

import { PALETTE } from "../../../colors.js";
import { rampColor } from "../../../stores/ramp.js";
import { drawNote, type Area } from "../../../stores/plot2d.js";
import { metricsStore } from "../../../stores/metrics.js";
import { spaceStore } from "../../../stores/space.js";
import { workspaceStore } from "../../../stores/workspace.js";
import { aggregateRecords, cellKey, mean, type AxisSelection } from "../../../stores/payloads.js";
import { wrapLabel } from "../../../stores/sprites.js";
import type {
  StageViewDefinition,
  StageViewInstance,
  StageViewContext,
  StageChange,
  Size,
} from "../../../layout/types.js";

type ColumnStatus = "measured" | "gap" | "void";

interface Column {
  status: ColumnStatus;
  accuracy: number;
  arm: string;
}

/** Create a StageViewInstance for the "matrix" view. */
export function createMatrixView(context: StageViewContext): StageViewInstance {
  const { flat, workspace, state } = context;

  // Per-instance state derived from state + workspace
  let runId = (state as any).runId ?? workspace.getSelectedRunId();
  let axes = (state as any).axes ?? workspace.getAxes();

  // Subscriptions
  let workspaceUnsub: (() => void) | null = null;
  let metricsUnsub: (() => void) | null = null;
  let spaceUnsub: (() => void) | null = null;

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
        updateSubscriptions();
        redraw();
      }
    });

    // Subscribe to metrics for this run
    if (runId) {
      metricsUnsub = metricsStore.subscribe(runId, () => {
        redraw();
      });
    }

    // Subscribe to space
    await updateSubscriptions();

    visible = true;
    await redraw();
  }

  async function updateSubscriptions(): Promise<void> {
    spaceUnsub?.();
    if (!runId) return;

    const spaceValues: Record<AxisSelection["x"], string[]> = {
      credit: [],
      geometry: [],
      dynamics: [],
      substrate: [],
      plasticity: [],
      update: [],
    };
    spaceUnsub = spaceStore.subscribe(runId, axes, spaceValues, () => {
      redraw();
    });
  }

  function redraw(): void {
    if (!visible) return;
    draw();
  }

  function draw(): void {
    const { columns, xValues, yValues } = computeColumns();
    if (columns.length === 0) {
      drawn = false;
      flat.clear();
      return;
    }

    const ctx = flat.begin();
    const area = flat.area();
    const axesData = workspace.getAxes();

    const nx = xValues.length;
    const ny = yValues.length;
    const labelWidth = 150;
    const labelHeight = 96;
    const plot = {
      x: area.x + labelWidth,
      y: area.y + 70,
      width: Math.max(80, area.width - labelWidth - 40),
      height: Math.max(80, area.height - 70 - labelHeight),
    };
    const cellWidth = plot.width / nx;
    const cellHeight = plot.height / ny;

    const maxAccuracy = Math.max(
      ...columns.map((column) => column.accuracy),
      0.0001,
    );

    ctx.fillStyle = PALETTE.text_primary;
    ctx.font = "600 22px 'JetBrains Mono', monospace";
    ctx.textAlign = "left";
    ctx.textBaseline = "alphabetic";
    ctx.fillText("Evidence matrix", area.x, area.y + 14);

    ctx.fillStyle = PALETTE.text_secondary;
    ctx.font = "13px 'JetBrains Mono', monospace";
    ctx.fillText(
      `${axesData.x} against ${axesData.y} — the best cell of each column`,
      area.x,
      area.y + 40,
    );

    let measured = 0;
    let gaps = 0;
    let refused = 0;

    columns.forEach((column, index) => {
      const xi = Math.floor(index / ny);
      const yi = index % ny;
      const x = plot.x + xi * cellWidth;
      const y = plot.y + yi * cellHeight;

      if (column.status === "void") {
        refused += 1;
        ctx.fillStyle = `${PALETTE.void}22`;
        ctx.fillRect(x, y, cellWidth, cellHeight);
        drawCross(ctx, x, y, cellWidth, cellHeight);
      } else if (column.status === "gap") {
        gaps += 1;
        ctx.fillStyle = PALETTE.bg_tertiary;
        ctx.fillRect(x, y, cellWidth, cellHeight);
      } else {
        measured += 1;
        ctx.fillStyle = rampColor(column.accuracy / maxAccuracy);
        ctx.fillRect(x, y, cellWidth, cellHeight);
        if (cellWidth > 44 && cellHeight > 26) {
          ctx.fillStyle = textOn(column.accuracy / maxAccuracy);
          ctx.font = "600 15px 'JetBrains Mono', monospace";
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillText(
            column.accuracy.toFixed(2),
            x + cellWidth / 2,
            y + cellHeight / 2,
          );
        }
      }

      ctx.strokeStyle = PALETTE.bg;
      ctx.lineWidth = 1;
      ctx.strokeRect(x + 0.5, y + 0.5, cellWidth - 1, cellHeight - 1);
    });

    // The values the columns and the rows name.
    ctx.fillStyle = PALETTE.text_secondary;
    ctx.font = "12px 'JetBrains Mono', monospace";
    xValues.forEach((value, xi) => {
      const lines = wrapLabel(value, 14);
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      lines.forEach((line, index) => {
        ctx.fillText(
          line,
          plot.x + xi * cellWidth + cellWidth / 2,
          plot.y + plot.height + 12 + index * 16,
        );
      });
    });
    yValues.forEach((value, yi) => {
      const lines = wrapLabel(value, 16);
      ctx.textAlign = "right";
      ctx.textBaseline = "middle";
      lines.forEach((line, index) => {
        ctx.fillText(
          line,
          plot.x - 12,
          plot.y +
            yi * cellHeight +
            cellHeight / 2 -
            (lines.length - 1) * 8 +
            index * 16,
        );
      });
    });

    // The colour key: what the colours of the cells mean.
    const keyWidth = 180;
    const keyX = plot.x + plot.width - keyWidth;
    const keyY = area.y + 16;
    const gradient = ctx.createLinearGradient(keyX, 0, keyX + keyWidth, 0);
    gradient.addColorStop(0, rampColor(0));
    gradient.addColorStop(0.5, rampColor(0.5));
    gradient.addColorStop(1, rampColor(1));
    ctx.fillStyle = gradient;
    ctx.fillRect(keyX, keyY, keyWidth, 12);
    ctx.strokeStyle = PALETTE.border;
    ctx.strokeRect(keyX + 0.5, keyY + 0.5, keyWidth - 1, 11);
    ctx.fillStyle = PALETTE.text_secondary;
    ctx.font = "11px 'JetBrains Mono', monospace";
    ctx.textAlign = "left";
    ctx.textBaseline = "top";
    ctx.fillText("0", keyX, keyY + 18);
    ctx.textAlign = "right";
    ctx.fillText(maxAccuracy.toFixed(2), keyX + keyWidth, keyY + 18);

    ctx.textAlign = "left";
    ctx.fillText(
      `${measured} measured · ${gaps} gaps · ${refused} refused`,
      area.x,
      area.y + area.height + 30,
    );

    drawn = measured > 0;
  }

  function computeColumns(): { columns: Column[]; xValues: string[]; yValues: string[] } {
    const metrics = runId ? metricsStore.get(runId) : null;
    const space = runId ? spaceStore.get(runId, axes, {
      credit: [],
      geometry: [],
      dynamics: [],
      substrate: [],
      plasticity: [],
      update: [],
    }) : null;
    if (!space) return { columns: [], xValues: [], yValues: [] };

    const axesData = axes;
    const spaceValues = space.values as Record<string, string[]>;
    const xValues = spaceValues[axesData.x] ?? [];
    const yValues = spaceValues[axesData.y] ?? [];
    const zValues = spaceValues[axesData.z] ?? [];

    // We need aggregates from metrics
    let aggregates = new Map<string, any>();
    if (metrics) {
      aggregates = aggregateRecords(metrics, axesData);
    }

    const columns: Column[] = [];
    xValues.forEach((x) => {
      yValues.forEach((y) => {
        let voidCells = 0;
        let legalCells = 0;
        let best = -Infinity;
        let arm = "";
        zValues.forEach((z) => {
          const key = cellKey(x, y, z);
          const cell = space.cells.find((c: any) => {
            const coord = c.coordinate;
            return coord[axesData.x] === x && coord[axesData.y] === y && coord[axesData.z] === z;
          });
          if (cell?.status === "void") {
            voidCells += 1;
            return;
          }
          legalCells += 1;
          const aggregate = aggregates.get(key);
          if (!aggregate || aggregate.acc.length === 0) return;
          const accuracy = mean(aggregate.acc);
          if (accuracy > best) {
            best = accuracy;
            arm = aggregate.coordinate.credit ?? "";
          }
        });
        const status: ColumnStatus =
          voidCells > 0 && legalCells === 0
            ? "void"
            : best > -Infinity
              ? "measured"
              : "gap";
        columns.push({
          status,
          accuracy: best > -Infinity ? best : 0,
          arm,
        });
      });
    });
    return { columns, xValues, yValues };
  }

  function drawCross(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    width: number,
    height: number,
  ): void {
    const size = Math.min(width, height) * 0.28;
    const cx = x + width / 2;
    const cy = y + height / 2;
    ctx.strokeStyle = PALETTE.void;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(cx - size, cy - size);
    ctx.lineTo(cx + size, cy + size);
    ctx.moveTo(cx + size, cy - size);
    ctx.lineTo(cx - size, cy + size);
    ctx.stroke();
  }

  function textOn(fraction: number): string {
    return fraction > 0.62 ? PALETTE.bg : PALETTE.text_primary;
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
    spaceUnsub?.();
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

/** Register the matrix view definition. */
export const matrixViewDefinition: StageViewDefinition = {
  view: "matrix",
  title: "Evidence matrix",
  key: "shift+x",
  group: "the run",
  create: createMatrixView,
};