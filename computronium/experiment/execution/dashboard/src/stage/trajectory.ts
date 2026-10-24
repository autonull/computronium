/** The trajectory — the state's own path through the state space (TODO71 Phase 4).
 *
 *  One of the eight dynamics views. The server composes the cell, steps its
 *  own relaxation, and says what it found. A cell with no state that moves —
 *  a feedforward cell with an instantaneous pass — has no picture here, and
 *  the views say so rather than drawing an empty stage.
 */

import { PALETTE } from "../colors.js";
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
import { registerView } from "./registry.js";
import type { StageView, ViewGroup } from "./views.js";

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

/** The trajectory — the state's own path through the state space. */
export class TrajectoryView implements StageView {
  id = "trajectory";
  name = "The trajectory";
  group = "the system" as ViewGroup;
  caption =
    "Where the cell's own state went, step by step: the path it took through the space it moves in.";
  key = "j";

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
        base - ((value - lowest) / ((highest - lowest) || 1)) * band * 0.5;
      ctx.strokeStyle = PALETTE.thermodynamic_contrast;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      errors.forEach((value, index) => {
        const x =
          frame.rect.x + (index / (errors.length - 1)) * frame.rect.width;
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
    this.drawn = true;
  }
}

registerView(new TrajectoryView());