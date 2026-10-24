/** The trained cell's basin — how much of the neighbourhood comes back after training (TODO71 Phase 4).
 *
 *  One of the eight dynamics views.
 */

import { PALETTE } from "../colors.js";
import { stageCanvas } from "./canvas2d.js";
import { drawFrame, drawNote, scaleX, scaleY } from "./plot2d.js";
import { rampColor } from "./ramp.js";
import { stageState, type CellDynamics } from "./store.js";
import { registerView } from "./registry.js";
import type { StageView, ViewGroup } from "./views.js";

/** The trained payload, or nothing. */
function trainedDynamics(): CellDynamics | null {
  const payload = stageState.trainedDynamics;
  if (!payload || !payload.stateful) return null;
  return payload;
}

function trainedCellName(payload: CellDynamics): string {
  const coordinate = payload.cell?.coordinate ?? {};
  return [coordinate.geometry, coordinate.dynamics, coordinate.credit]
    .filter((part) => typeof part === "string" && part.length > 0)
    .join(" · ");
}

function trainedNote(payload: CellDynamics): string {
  const parts: string[] = [];
  const cell = trainedCellName(payload);
  if (cell) parts.push(cell);
  if (payload.cell?.measured_by_run === false) {
    parts.push("a cell of the space, not one the run measured");
  }
  if (payload.trained === true) parts.push("the weights were trained first");
  return parts.join(" · ");
}

/** The trained cell's basin — how much of the neighbourhood comes back after training. */
export class TrainedBasinView implements StageView {
  id = "trained-basin";
  name = "The trained basin";
  group = "the system" as ViewGroup;
  caption =
    "The states near the trained cell's own: how many come back, and how far the ones that do not stray.";
  key = "k";

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
    const payload = trainedDynamics();
    const basin = payload?.basin;
    if (!payload || !basin || basin.paths.length === 0) {
      this.drawn = false;
      return;
    }

    const ctx = stageCanvas.begin();
    const area = stageCanvas.area();
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

    ctx.font = "12px 'JetBrains Mono', monospace";
    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    basin.stability.forEach((share, index) => {
      const x =
        frame.rect.x + (frame.rect.width / radii.length) * (index + 0.5);
      ctx.fillStyle = share > 0 ? PALETTE.ok : PALETTE.warn;
      ctx.fillText(`${Math.round(share * 100)}% back`, x, frame.rect.y + 12);
      ctx.fillStyle = PALETTE.text_secondary;
      ctx.fillText(`nudge ${radii[index]}`, x, frame.rect.y + 28);
    });

    drawNote(ctx, area, payload.verdict ?? "");
    this.drawn = true;
  }
}

registerView(new TrainedBasinView());
