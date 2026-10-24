/** The landscape — the cell's own energy over the slice its trajectory crosses (TODO71 Phase 4).
 *
 *  One of the eight dynamics views.
 */

import { PALETTE } from "../colors.js";
import { stageCanvas } from "./canvas2d.js";
import { drawFrame, drawNote, scaleX, scaleY } from "./plot2d.js";
import { rampColor } from "./ramp.js";
import { stageState, type CellDynamics } from "./state.js";
import { registerView } from "./registry.js";
import type { StageView, ViewGroup } from "./views.js";

/** The payload, or nothing: a view with nothing to draw leaves an empty stage. */
function dynamics(): CellDynamics | null {
  const payload = stageState.dynamics;
  if (!payload || !payload.stateful) return null;
  return payload;
}

function cellName(payload: CellDynamics): string {
  const coordinate = payload.cell?.coordinate ?? {};
  return [
    coordinate.geometry,
    coordinate.dynamics,
    coordinate.credit,
  ]
    .filter((part) => typeof part === "string" && part.length > 0)
    .join(" · ");
}

function note(payload: CellDynamics): string {
  const parts: string[] = [];
  const cell = cellName(payload);
  if (cell) parts.push(cell);
  if (payload.cell?.measured_by_run === false) {
    parts.push("a cell of the space, not one the run measured");
  }
  if (payload.trained === false) parts.push("the weights are untrained");
  return parts.join(" · ");
}

/** The landscape — the cell's own energy over the slice its trajectory crosses. */
export class LandscapeView implements StageView {
  id = "landscape";
  name = "The landscape";
  group = "the system" as ViewGroup;
  caption =
    "The cell's own energy over the ground its trajectory crossed, and the path it took across it.";
  key = "n";

  protected visible = false;
  protected drawn = false;

  enter(): void {
    this.visible = true;
    stageCanvas.show();
    this.draw();
  }

  exit(): void {
    this.visible = false;
    stageCanvas.hide();
    this.drawn = false;
  }

  refresh(): void {
    if (!this.visible) return;
    this.draw();
  }

  ready(): boolean {
    return this.drawn;
  }

  protected draw(): void {
    const payload = dynamics();
    const landscape = payload?.landscape;
    const trajectory = payload?.trajectory;
    if (!payload || !landscape || landscape.grid.length === 0) {
      this.drawn = false;
      return;
    }

    const ctx = stageCanvas.begin();
    const area = stageCanvas.area();
    const grid = landscape.grid;
    const flat = grid.flat();
    const lowest = Math.min(...flat);
    const highest = Math.max(...flat);

    const frame = drawFrame(ctx, area, {
      xMin: landscape.x[0],
      xMax: landscape.x[landscape.x.length - 1],
      yMin: landscape.y[0],
      yMax: landscape.y[landscape.y.length - 1],
      xLabel: "along the trajectory",
      yLabel: "across it",
      title: "The landscape",
      subtitle: note(payload),
    });

    // The energy, as a field: the ground the cell's own path crossed. The
    // grid is indexed by x then y, and it is clipped to the frame so that
    // it cannot paint over the picture's own title.
    const cellWidth = frame.rect.width / (landscape.x.length - 1 || 1);
    const cellHeight = frame.rect.height / (landscape.y.length - 1 || 1);
    ctx.save();
    ctx.beginPath();
    ctx.rect(frame.rect.x, frame.rect.y, frame.rect.width, frame.rect.height);
    ctx.clip();
    grid.forEach((row, i) => {
      row.forEach((value, j) => {
        const t = (value - lowest) / ((highest - lowest) || 1);
        ctx.fillStyle = rampColor(1 - t);
        const x = frame.rect.x + cellWidth * i;
        const y = frame.rect.y + frame.rect.height - cellHeight * (j + 1);
        ctx.fillRect(x, y, cellWidth + 1, cellHeight + 1);
      });
    });
    ctx.restore();

    // The trajectory, over the ground.
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

    // The low ground, named: where the energy is smallest.
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
    this.drawn = true;
  }
}

registerView(new LandscapeView());