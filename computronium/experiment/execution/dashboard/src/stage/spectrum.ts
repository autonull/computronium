/** The spectrum — the Lyapunov exponents, and so the system's stability (TODO71 Phase 4).
 *
 *  One of the eight dynamics views.
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
import { stageState, type CellDynamics } from "./store.js";
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
  return [coordinate.geometry, coordinate.dynamics, coordinate.credit]
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

/** The spectrum — the Lyapunov exponents, and so the system's stability. */
export class SpectrumView implements StageView {
  id = "spectrum";
  name = "The spectrum";
  group = "the system" as ViewGroup;
  caption =
    "How fast a nudge grows along each direction: the exponents that say whether this dynamics settles.";
  key = "m";

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
      xTicks: niceTicks(0, spectrum.length, 6).filter((tick) =>
        Number.isInteger(tick),
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
      ctx.fillRect(
        centre - width / 2,
        Math.min(y, zero),
        width,
        Math.abs(y - zero),
      );
      ctx.font = "11px 'JetBrains Mono', monospace";
      ctx.fillStyle = growing ? PALETTE.warn : PALETTE.ok;
      ctx.textAlign = "center";
      ctx.textBaseline = growing ? "bottom" : "top";
      ctx.fillText(formatTick(value), centre, growing ? y - 5 : y + 5);
    });

    drawNote(ctx, area, payload.verdict ?? "");
    this.drawn = true;
  }
}

registerView(new SpectrumView());
