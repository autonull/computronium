/** Slices stage view — the space, cut three ways, side by side (TODO72 P6). */

import { PALETTE } from "../../../colors.js";
import { rampColor } from "../../../stage/ramp.js";
import { drawNote, type Area } from "../../../stage/plot2d.js";
import { metricsStore } from "../../../stores/metrics.js";
import { spaceStore } from "../../../stores/space.js";
import { workspaceStore } from "../../../stores/workspace.js";
import { aggregateRecords, cellKey, mean, type AxisSelection } from "../../../stage/payloads.js";
import { wrapLabel } from "../../../stage/sprites.js";
import type {
  StageViewDefinition,
  StageViewInstance,
  StageViewContext,
  StageChange,
  Size,
} from "../../../layout/types.js";

/** Which axis plays which part in one cut. */
type Axis = "x" | "y" | "z";

/** One cut of the space: two axes free, one collapsed over. */
interface Cut {
  across: Axis;
  down: Axis;
  held: Axis;
}

/** The three cuts, in the order they are drawn. */
const CUTS: Cut[] = [
  { across: "x", down: "y", held: "z" },
  { across: "x", down: "z", held: "y" },
  { across: "y", down: "z", held: "x" },
];

/** One cell of a cut: what the space holds there. */
interface SliceCell {
  status: "measured" | "gap" | "void";
  accuracy: number;
}

/** Create a StageViewInstance for the "slices" view. */
export function createSlicesView(context: StageViewContext): StageViewInstance {
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
    const metrics = runId ? metricsStore.get(runId) : null;
    const space = runId ? spaceStore.get(runId, axes, {
      credit: [],
      geometry: [],
      dynamics: [],
      substrate: [],
      plasticity: [],
      update: [],
    }) : null;
    if (!space) {
      drawn = false;
      flat.clear();
      return;
    }

    const ctx = flat.begin();
    const area = flat.area();
    const axesData = axes;

    ctx.fillStyle = PALETTE.text_primary;
    ctx.font = "600 22px 'JetBrains Mono', monospace";
    ctx.textAlign = "left";
    ctx.textBaseline = "alphabetic";
    ctx.fillText("The slices", area.x, area.y + 14);

    ctx.fillStyle = PALETTE.text_secondary;
    ctx.font = "13px 'JetBrains Mono', monospace";
    ctx.fillText(
      "One space, three cuts: the axes a reader sees are a choice, and every choice hides an axis.",
      area.x,
      area.y + 40,
    );

    const gap = 28;
    const sliceWidth = (area.width - gap * 2) / 3;
    let measured = 0;
    let gaps = 0;
    let refused = 0;

    CUTS.forEach((cut, index) => {
      const { cells, across, down } = computeCut(cut);
      const left = area.x + index * (sliceWidth + gap);
      const top = area.y + 70;
      const labelWidth = 96;
      const labelHeight = 54;
      const plot = {
        x: left + labelWidth,
        y: top,
        width: Math.max(60, sliceWidth - labelWidth - 12),
        height: Math.max(60, area.height - 70 - labelHeight),
      };
      const cellWidth = across.length ? plot.width / across.length : 0;
      const cellHeight = down.length ? plot.height / down.length : 0;
      const maxAccuracy = Math.max(
        ...cells.map((cell) => cell.accuracy),
        0.0001,
      );

      // The cut's own name: the two axes it shows, and the one it hides.
      ctx.fillStyle = PALETTE.text_primary;
      ctx.font = "600 13px 'JetBrains Mono', monospace";
      ctx.textAlign = "left";
      ctx.textBaseline = "alphabetic";
      ctx.fillText(`${axesData[cut.across]} × ${axesData[cut.down]}`, left, top - 12);
      ctx.fillStyle = PALETTE.text_muted;
      ctx.font = "11px 'JetBrains Mono', monospace";
      ctx.fillText(`${axesData[cut.held]} collapsed`, left, top - 30);

      cells.forEach((cell, index2) => {
        const xi = Math.floor(index2 / down.length);
        const yi = index2 % down.length;
        const x = plot.x + xi * cellWidth;
        const y = plot.y + yi * cellHeight;

        if (cell.status === "void") {
          refused += 1;
          ctx.fillStyle = `${PALETTE.void}22`;
          ctx.fillRect(x, y, cellWidth, cellHeight);
        } else if (cell.status === "gap") {
          gaps += 1;
          ctx.fillStyle = PALETTE.bg_tertiary;
          ctx.fillRect(x, y, cellWidth, cellHeight);
        } else {
          measured += 1;
          ctx.fillStyle = rampColor(cell.accuracy / maxAccuracy);
          ctx.fillRect(x, y, cellWidth, cellHeight);
        }

        ctx.strokeStyle = PALETTE.bg;
        ctx.lineWidth = 1;
        ctx.strokeRect(x + 0.5, y + 0.5, cellWidth - 1, cellHeight - 1);
      });

      // The values the columns and the rows name.
      ctx.fillStyle = PALETTE.text_secondary;
      ctx.font = "11px 'JetBrains Mono', monospace";
      across.forEach((value, xi) => {
        const lines = wrapLabel(value, 12);
        ctx.textAlign = "center";
        ctx.textBaseline = "top";
        lines.forEach((line, index3) => {
          ctx.fillText(
            line,
            plot.x + xi * cellWidth + cellWidth / 2,
            plot.y + plot.height + 8 + index3 * 14,
          );
        });
      });
      down.forEach((value, yi) => {
        const lines = wrapLabel(value, 14);
        ctx.textAlign = "right";
        ctx.textBaseline = "middle";
        lines.forEach((line, index3) => {
          ctx.fillText(
            line,
            plot.x - 8,
            plot.y +
              yi * cellHeight +
              cellHeight / 2 -
              (lines.length - 1) * 7 +
              index3 * 14,
          );
        });
      });
    });

    ctx.fillStyle = PALETTE.text_secondary;
    ctx.font = "12px 'JetBrains Mono', monospace";
    ctx.textAlign = "left";
    ctx.textBaseline = "alphabetic";
    ctx.fillText(
      `${measured} measured · ${gaps} gaps · ${refused} refused`,
      area.x,
      area.y + area.height + 24,
    );

    drawn = measured > 0;
  }

  function computeCut(cut: Cut): {
    cells: SliceCell[];
    across: string[];
    down: string[];
  } {
    const metrics = runId ? metricsStore.get(runId) : null;
    const space = runId ? spaceStore.get(runId, axes, {
      credit: [],
      geometry: [],
      dynamics: [],
      substrate: [],
      plasticity: [],
      update: [],
    }) : null;
    if (!space) return { cells: [], across: [], down: [] };

    const axesData = axes;
    const spaceValues = space.values as Record<string, string[]>;
    const acrossValues = spaceValues[axesData[cut.across]] ?? [];
    const downValues = spaceValues[axesData[cut.down]] ?? [];
    const heldValues = spaceValues[axesData[cut.held]] ?? [];

    // We need aggregates from metrics
    let aggregates = new Map<string, any>();
    if (metrics) {
      aggregates = aggregateRecords(metrics, axesData);
    }

    const cells: SliceCell[] = [];
    acrossValues.forEach((across) => {
      downValues.forEach((down) => {
        let voidCells = 0;
        let legalCells = 0;
        let best = -Infinity;
        heldValues.forEach((held) => {
          const key = keyOf(axesData, cut, across, down, held);
          const cell = space.cells.find((c: any) => {
            const coord = c.coordinate;
            return coord[axesData.x] === key.split("|")[0] &&
              coord[axesData.y] === key.split("|")[1] &&
              coord[axesData.z] === key.split("|")[2];
          });
          if (cell?.status === "void") {
            voidCells += 1;
            return;
          }
          legalCells += 1;
          const aggregate = aggregates.get(key);
          if (!aggregate || aggregate.acc.length === 0) return;
          best = Math.max(best, mean(aggregate.acc));
        });
        cells.push({
          status:
            voidCells > 0 && legalCells === 0
              ? "void"
              : best > -Infinity
                ? "measured"
                : "gap",
          accuracy: best > -Infinity ? best : 0,
        });
      });
    });
    return { cells, across: acrossValues, down: downValues };
  }

  function keyOf(
    axesData: { x: string; y: string; z: string },
    cut: Cut,
    across: string,
    down: string,
    held: string,
  ): string {
    const value = { x: "", y: "", z: "" };
    value[cut.across] = across;
    value[cut.down] = down;
    value[cut.held] = held;
    return cellKey(value.x, value.y, value.z);
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

/** Register the slices view definition. */
export const slicesViewDefinition: StageViewDefinition = {
  view: "slices",
  title: "The slices",
  key: ",",
  group: "the space",
  create: createSlicesView,
};