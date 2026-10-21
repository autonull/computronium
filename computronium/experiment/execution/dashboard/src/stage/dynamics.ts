/** The cell's own dynamics (TODO69 Phase 5).

    Every other view on the stage draws the *bookkeeping* of a run: what was
    measured, what was refused, what it cost. These four draw the system
    being measured — where its state goes, whether it settles, how much of
    the neighbourhood comes back, and what its energy looks like over the
    slice its own trajectory crosses.

    They share one payload, because they are four readings of one
    measurement: the server composes the cell, steps its own relaxation,
    and says what it found. A cell with no state that moves — a feedforward
    cell with an instantaneous pass — has no picture here, and the views
    say so rather than drawing an empty stage.
*/

import { PALETTE } from "../palette.js";
import { stageCanvas } from "./canvas2d.js";
import {
  drawFrame,
  drawNote,
  formatTick,
  niceTicks,
  scaleX,
  scaleY,
} from "./plot2d.js";
import { rampColor } from "./ramp.js";
import { stageState, type CellDynamics } from "./state.js";
import type { StageView } from "./views.js";

/** The payload, or nothing: a view with nothing to draw leaves an empty stage. */
function dynamics(): CellDynamics | null {
  const payload = stageState.dynamics;
  if (!payload || !payload.stateful) return null;
  return payload;
}

/** The cell the server measured, named the way a reader would say it. */
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

/** The note under a picture: the server's own sentence about the cell. */
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

/** The base of a class: the four views differ only in what they draw. */
abstract class DynamicsView implements StageView {
  abstract id: string;
  abstract name: string;
  abstract caption: string;
  key?: string;

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

  protected abstract draw(): void;
}

/** The trajectory — the state's own path through the state space. */
export class TrajectoryView extends DynamicsView {
  id = "trajectory";
  name = "The trajectory";
  caption =
    "Where the cell's own state went, step by step: the path it took through the space it moves in.";
  key = "j";

  protected draw(): void {
    const payload = dynamics();
    const trajectory = payload?.trajectory;
    if (!payload || !trajectory || trajectory.path.length < 2) {
      this.drawn = false;
      return;
    }

    const ctx = stageCanvas.begin();
    const area = stageCanvas.area();
    const path = trajectory.path;
    const xs = path.map((point) => point[0]);
    const ys = path.map((point) => point[1]);
    const pad = 0.08;
    const xMin = Math.min(...xs);
    const xMax = Math.max(...xs);
    const yMin = Math.min(...ys);
    const yMax = Math.max(...ys);
    const xSpan = (xMax - xMin) || 1;
    const ySpan = (yMax - yMin) || 1;

    const frame = drawFrame(ctx, area, {
      xMin: xMin - xSpan * pad,
      xMax: xMax + xSpan * pad,
      yMin: yMin - ySpan * pad,
      yMax: yMax + ySpan * pad,
      xLabel: trajectory.axes[0] ?? "the direction the state moved",
      yLabel: trajectory.axes[1] ?? "the direction across it",
      title: "The trajectory",
      subtitle: note(payload),
    });

    // The path, coloured by time: where the state was, and when.
    for (let index = 1; index < path.length; index += 1) {
      const t = index / (path.length - 1);
      ctx.strokeStyle = rampColor(t);
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(scaleX(path[index - 1][0], frame), scaleY(path[index - 1][1], frame));
      ctx.lineTo(scaleX(path[index][0], frame), scaleY(path[index][1], frame));
      ctx.stroke();
    }

    // Where it started, and where it stopped.
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

    // The error the relaxation was driving down, along the bottom.
    const errors = trajectory.error ?? [];
    if (errors.length > 1) {
      const lowest = Math.min(...errors);
      const highest = Math.max(...errors);
      const band = frame.rect.height * 0.16;
      const base = frame.rect.y + frame.rect.height - band * 0.5;
      const toY = (value: number): number =>
        base -
        ((value - lowest) / ((highest - lowest) || 1)) * band * 0.5;
      ctx.strokeStyle = PALETTE.thermodynamic_contrast;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      errors.forEach((value, index) => {
        const x =
          frame.rect.x +
          (index / (errors.length - 1)) * frame.rect.width;
        if (index === 0) ctx.moveTo(x, toY(value));
        else ctx.lineTo(x, toY(value));
      });
      ctx.stroke();
      ctx.font = "11px 'JetBrains Mono', monospace";
      ctx.fillStyle = PALETTE.thermodynamic_contrast;
      ctx.textAlign = "right";
      ctx.textBaseline = "bottom";
      ctx.fillText("the prediction error", frame.rect.x + frame.rect.width, base - band * 0.6);
    }

    drawNote(ctx, area, payload.verdict ?? "");
    this.drawn = true;
  }
}

/** The spectrum — the Lyapunov exponents, and so the system's stability. */
export class SpectrumView extends DynamicsView {
  id = "spectrum";
  name = "The spectrum";
  caption =
    "How fast a nudge grows along each direction: the exponents that say whether this dynamics settles.";
  key = "m";

  protected draw(): void {
    const payload = dynamics();
    const spectrum = payload?.spectrum;
    if (!payload || !spectrum || spectrum.length === 0) {
      this.drawn = false;
      return;
    }

    const ctx = stageCanvas.begin();
    const area = stageCanvas.area();
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
      subtitle: note(payload),
      xTicks: niceTicks(0, spectrum.length, 6).filter(
        (tick) => Number.isInteger(tick),
      ),
    });

    // The zero line: what separates a direction that contracts from one
    // that grows.
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
      ctx.fillText(
        formatTick(value),
        centre,
        growing ? y - 5 : y + 5,
      );
    });

    drawNote(ctx, area, payload.verdict ?? "");
    this.drawn = true;
  }
}

/** The basin — how much of the neighbourhood comes back, and where the strays went. */
export class BasinView extends DynamicsView {
  id = "basin";
  name = "The basin";
  caption =
    "The states near the cell's own: how many come back, and how far the ones that do not stray.";
  key = "b";

  protected draw(): void {
    const payload = dynamics();
    const basin = payload?.basin;
    if (!payload || !basin || basin.paths.length === 0) {
      this.drawn = false;
      return;
    }

    const ctx = stageCanvas.begin();
    const area = stageCanvas.area();
    const paths = basin.paths;
    const farthest = Math.max(
      ...paths.flatMap((path) => path.distances),
      1e-6,
    );

    const frame = drawFrame(ctx, area, {
      xMin: 0,
      xMax: paths[0].distances.length,
      yMin: 0,
      yMax: farthest * 1.1,
      xLabel: "steps after the nudge",
      yLabel: "distance from the attractor",
      title: "The basin",
      subtitle: note(payload),
    });

    const radii = basin.radii;
    paths.forEach((path) => {
      const index = radii.indexOf(path.radius);
      const t = radii.length > 1 ? index / (radii.length - 1) : 0.5;
      ctx.strokeStyle = path.returned ? PALETTE.ok : rampColor(t);
      ctx.lineWidth = 2;
      ctx.beginPath();
      path.distances.forEach((distance, step) => {
        const x = scaleX(step, frame);
        const y = scaleY(distance, frame);
        if (step === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
    });

    // The share that came back, over each radius: the number the picture
    // is about. It is written inside the frame, where the curves are not.
    ctx.font = "12px 'JetBrains Mono', monospace";
    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    basin.stability.forEach((share, index) => {
      const x = frame.rect.x + (frame.rect.width / radii.length) * (index + 0.5);
      ctx.fillStyle = share > 0 ? PALETTE.ok : PALETTE.warn;
      ctx.fillText(`${Math.round(share * 100)}% back`, x, frame.rect.y + 12);
      ctx.fillStyle = PALETTE.text_secondary;
      ctx.fillText(`nudge ${radii[index]}`, x, frame.rect.y + 28);
    });

    drawNote(ctx, area, payload.verdict ?? "");
    this.drawn = true;
  }
}

/** The landscape — the cell's own energy over the slice its trajectory crosses. */
export class LandscapeView extends DynamicsView {
  id = "landscape";
  name = "The landscape";
  caption =
    "The cell's own energy over the ground its trajectory crossed, and the path it took across it.";
  key = "n";

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
