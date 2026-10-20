/** Drawing a flat picture (TODO69 Phase 5).

    The frames, the ticks and the labels a 2D view needs, so the matrix and
    the convergence are drawn the same way and read as two pictures of one
    system rather than two drawings.
*/

import { PALETTE } from "../palette.js";
import type { Area } from "./canvas2d.js";

/** The margins a frame leaves for its labels. */
const MARGIN = { top: 64, right: 36, bottom: 62, left: 78 };

/** The rectangle the data is drawn in, inside the area the panels leave. */
export interface PlotFrame {
  rect: Area;
  xMin: number;
  xMax: number;
  yMin: number;
  yMax: number;
}

/** Round tick values that cover a range, evenly. */
export function niceTicks(min: number, max: number, count = 5): number[] {
  if (!Number.isFinite(min) || !Number.isFinite(max)) return [min];
  if (min === max) return [min];
  const span = max - min;
  const raw = span / Math.max(1, count);
  const magnitude = 10 ** Math.floor(Math.log10(raw));
  const normalized = raw / magnitude;
  const step =
    (normalized >= 5 ? 10 : normalized >= 2 ? 5 : normalized >= 1 ? 2 : 1) *
    magnitude;
  const first = Math.ceil(min / step) * step;
  const ticks: number[] = [];
  for (let value = first; value <= max + step * 1e-6; value += step) {
    ticks.push(Number(value.toFixed(10)));
  }
  return ticks;
}

/** A tick's own number, in the fewest digits that tell it apart. */
export function formatTick(value: number): string {
  const abs = Math.abs(value);
  if (abs === 0) return "0";
  if (abs >= 1000) return value.toFixed(0);
  if (abs >= 10) return value.toFixed(0);
  if (abs >= 1) return value.toFixed(1);
  if (abs >= 0.01) return value.toFixed(2);
  return value.toExponential(1);
}

export function scaleX(
  value: number,
  frame: PlotFrame,
): number {
  const span = frame.xMax - frame.xMin;
  if (span === 0) return frame.rect.x;
  return frame.rect.x + ((value - frame.xMin) / span) * frame.rect.width;
}

export function scaleY(value: number, frame: PlotFrame): number {
  const span = frame.yMax - frame.yMin;
  if (span === 0) return frame.rect.y + frame.rect.height;
  return (
    frame.rect.y + frame.rect.height - ((value - frame.yMin) / span) * frame.rect.height
  );
}

/** The frame of a picture: its box, its ticks, its labels and its title. */
export function drawFrame(
  ctx: CanvasRenderingContext2D,
  area: Area,
  options: {
    xMin: number;
    xMax: number;
    yMin: number;
    yMax: number;
    xLabel: string;
    yLabel: string;
    title: string;
    subtitle?: string;
    xTicks?: number[];
    yTicks?: number[];
  },
): PlotFrame {
  const rect: Area = {
    x: area.x + MARGIN.left,
    y: area.y + MARGIN.top,
    width: Math.max(40, area.width - MARGIN.left - MARGIN.right),
    height: Math.max(40, area.height - MARGIN.top - MARGIN.bottom),
  };
  const frame: PlotFrame = {
    rect,
    xMin: options.xMin,
    xMax: options.xMax,
    yMin: options.yMin,
    yMax: options.yMax,
  };

  ctx.fillStyle = PALETTE.text_primary;
  ctx.font = "600 22px 'JetBrains Mono', monospace";
  ctx.textAlign = "left";
  ctx.textBaseline = "alphabetic";
  ctx.fillText(options.title, area.x, area.y + 14);

  if (options.subtitle) {
    ctx.fillStyle = PALETTE.text_secondary;
    ctx.font = "13px 'JetBrains Mono', monospace";
    ctx.fillText(options.subtitle, area.x, area.y + 40);
  }

  const xTicks = options.xTicks ?? niceTicks(options.xMin, options.xMax, 6);
  const yTicks = options.yTicks ?? niceTicks(options.yMin, options.yMax, 5);

  ctx.strokeStyle = PALETTE.border;
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.rect(rect.x, rect.y, rect.width, rect.height);
  ctx.stroke();

  ctx.font = "12px 'JetBrains Mono', monospace";
  ctx.fillStyle = PALETTE.text_secondary;

  xTicks.forEach((tick) => {
    const x = scaleX(tick, frame);
    if (x < rect.x - 1 || x > rect.x + rect.width + 1) return;
    ctx.strokeStyle = PALETTE.border;
    ctx.beginPath();
    ctx.moveTo(x, rect.y);
    ctx.lineTo(x, rect.y + rect.height);
    ctx.stroke();
    ctx.textAlign = "center";
    ctx.fillText(formatTick(tick), x, rect.y + rect.height + 20);
  });

  yTicks.forEach((tick) => {
    const y = scaleY(tick, frame);
    if (y < rect.y - 1 || y > rect.y + rect.height + 1) return;
    ctx.strokeStyle = PALETTE.border;
    ctx.beginPath();
    ctx.moveTo(rect.x, y);
    ctx.lineTo(rect.x + rect.width, y);
    ctx.stroke();
    ctx.textAlign = "right";
    ctx.fillText(formatTick(tick), rect.x - 10, y + 4);
  });

  ctx.fillStyle = PALETTE.text_secondary;
  ctx.font = "13px 'JetBrains Mono', monospace";
  ctx.textAlign = "center";
  ctx.fillText(options.xLabel, rect.x + rect.width / 2, rect.y + rect.height + 46);
  ctx.save();
  ctx.translate(rect.x - 56, rect.y + rect.height / 2);
  ctx.rotate(-Math.PI / 2);
  ctx.textAlign = "center";
  ctx.fillText(options.yLabel, 0, 0);
  ctx.restore();

  return frame;
}

/** A line of text under the picture: what the reader is looking at. */
export function drawNote(
  ctx: CanvasRenderingContext2D,
  area: Area,
  text: string,
): void {
  ctx.fillStyle = PALETTE.text_secondary;
  ctx.font = "12px 'JetBrains Mono', monospace";
  ctx.textAlign = "left";
  ctx.textBaseline = "alphabetic";
  ctx.fillText(text, area.x, area.y + area.height + 40);
}
