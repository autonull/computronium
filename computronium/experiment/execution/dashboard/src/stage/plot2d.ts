/** Drawing a flat picture (TODO69 Phase 5).

    The frames, the ticks and the labels a 2D view needs, so the matrix and
    the convergence are drawn the same way and read as two pictures of one
    system rather than two drawings.
*/

import { PALETTE } from "../colors.js";
import { wrapLabel } from "./sprites.js";
import type { Area } from "./canvas2d.js";

/** The margins a frame leaves for its labels. */
const MARGIN = { top: 64, right: 36, bottom: 62, left: 78 };

/** The title of a picture, and the line under it that says what it is. */
export function drawTitle(
  ctx: CanvasRenderingContext2D,
  area: Area,
  title: string,
  subtitle?: string,
): void {
  ctx.fillStyle = PALETTE.text_primary;
  ctx.font = "600 22px 'JetBrains Mono', monospace";
  ctx.textAlign = "left";
  ctx.textBaseline = "alphabetic";
  ctx.fillText(title, area.x, area.y + 14);

  if (subtitle) {
    ctx.fillStyle = PALETTE.text_secondary;
    ctx.font = "13px 'JetBrains Mono', monospace";
    ctx.fillText(subtitle, area.x, area.y + 40);
  }
}

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

  drawTitle(ctx, area, options.title, options.subtitle);

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

/** Break a sentence into lines that fit the width it has.

    The other label helper breaks a name at its underscores, which is right for
    a cell and wrong for a sentence: a limitation is prose, and prose breaks
    at its spaces.
*/
export function wrapText(
  ctx: CanvasRenderingContext2D,
  text: string,
  maxWidth: number,
): string[] {
  const words = text.split(/\s+/).filter((word) => word.length > 0);
  const lines: string[] = [];
  let current = "";
  words.forEach((word) => {
    const candidate = current ? `${current} ${word}` : word;
    if (current && ctx.measureText(candidate).width > maxWidth) {
      lines.push(current);
      current = word;
      return;
    }
    current = candidate;
  });
  if (current) lines.push(current);
  return lines;
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

/** A frame whose x is a set of categories rather than a number. */
export interface CategoryFrame {
  rect: Area;
  yMin: number;
  yMax: number;
  categories: string[];
  /** The width of one category's band. */
  bandWidth: number;
  /** The middle of a category's band. */
  band(index: number): number;
}

/** The frame of a picture whose x is a set of categories.

    A violin's arm, a cell's seeds: both are named things rather than
    numbers, so the frame gives each one a band of its own.
*/
export function drawCategoryFrame(
  ctx: CanvasRenderingContext2D,
  area: Area,
  options: {
    yMin: number;
    yMax: number;
    categories: string[];
    title: string;
    subtitle?: string;
    yLabel: string;
    yTicks?: number[];
  },
): CategoryFrame {
  const rect: Area = {
    x: area.x + MARGIN.left,
    y: area.y + MARGIN.top,
    width: Math.max(40, area.width - MARGIN.left - MARGIN.right),
    height: Math.max(40, area.height - MARGIN.top - MARGIN.bottom),
  };
  const bandWidth = rect.width / Math.max(1, options.categories.length);
  const frame: CategoryFrame = {
    rect,
    yMin: options.yMin,
    yMax: options.yMax,
    categories: options.categories,
    bandWidth,
    band: (index: number) => rect.x + bandWidth * (index + 0.5),
  };
  const scale: PlotFrame = {
    rect,
    xMin: 0,
    xMax: 1,
    yMin: options.yMin,
    yMax: options.yMax,
  };

  drawTitle(ctx, area, options.title, options.subtitle);

  ctx.strokeStyle = PALETTE.border;
  ctx.lineWidth = 1;
  ctx.strokeRect(rect.x + 0.5, rect.y + 0.5, rect.width - 1, rect.height - 1);

  ctx.font = "12px 'JetBrains Mono', monospace";
  ctx.fillStyle = PALETTE.text_secondary;
  const yTicks = options.yTicks ?? niceTicks(options.yMin, options.yMax, 5);
  yTicks.forEach((tick) => {
    const y = scaleY(tick, scale);
    if (y < rect.y - 1 || y > rect.y + rect.height + 1) return;
    ctx.strokeStyle = PALETTE.border;
    ctx.beginPath();
    ctx.moveTo(rect.x, y);
    ctx.lineTo(rect.x + rect.width, y);
    ctx.stroke();
    ctx.textAlign = "right";
    ctx.fillText(formatTick(tick), rect.x - 10, y + 4);
  });

  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  options.categories.forEach((category, index) => {
    wrapLabel(category, 14).forEach((line, lineIndex) => {
      ctx.fillText(
        line,
        frame.band(index),
        rect.y + rect.height + 12 + lineIndex * 16,
      );
    });
  });

  ctx.fillStyle = PALETTE.text_secondary;
  ctx.font = "13px 'JetBrains Mono', monospace";
  ctx.save();
  ctx.translate(rect.x - 56, rect.y + rect.height / 2);
  ctx.rotate(-Math.PI / 2);
  ctx.textAlign = "center";
  ctx.textBaseline = "alphabetic";
  ctx.fillText(options.yLabel, 0, 0);
  ctx.restore();

  return frame;
}

/** A frame whose y is a set of categories rather than a number. */
export interface RowFrame {
  rect: Area;
  xMin: number;
  xMax: number;
  rows: string[];
  /** The height of one row. */
  rowHeight: number;
  /** The middle of a row. */
  rowY(index: number): number;
}

/** The frame of a picture whose y is a set of categories.

    A cell's seeds, a cell's interval: both are named things, so the frame
    gives each one a row of its own.
*/
export function drawRowFrame(
  ctx: CanvasRenderingContext2D,
  area: Area,
  options: {
    xMin: number;
    xMax: number;
    rows: string[];
    title: string;
    subtitle?: string;
    xLabel: string;
    xTicks?: number[];
  },
): RowFrame {
  // The rows are named, and a name is as long as it is: the frame gives the
  // labels the room they need rather than letting them run under the panels.
  ctx.font = "12px 'JetBrains Mono', monospace";
  const labelWidth = options.rows.reduce(
    (widest, row) => Math.max(widest, ctx.measureText(row).width),
    0,
  );
  const left = Math.min(
    area.width * 0.45,
    Math.max(MARGIN.left, labelWidth + 24),
  );
  const rect: Area = {
    x: area.x + left,
    y: area.y + MARGIN.top,
    width: Math.max(40, area.width - left - MARGIN.right),
    height: Math.max(40, area.height - MARGIN.top - MARGIN.bottom),
  };
  const rowHeight = rect.height / Math.max(1, options.rows.length);
  const frame: RowFrame = {
    rect,
    xMin: options.xMin,
    xMax: options.xMax,
    rows: options.rows,
    rowHeight,
    rowY: (index: number) => rect.y + rowHeight * (index + 0.5),
  };
  const scale: PlotFrame = {
    rect,
    xMin: options.xMin,
    xMax: options.xMax,
    yMin: 0,
    yMax: 1,
  };

  drawTitle(ctx, area, options.title, options.subtitle);

  ctx.strokeStyle = PALETTE.border;
  ctx.lineWidth = 1;
  ctx.strokeRect(rect.x + 0.5, rect.y + 0.5, rect.width - 1, rect.height - 1);

  ctx.font = "12px 'JetBrains Mono', monospace";
  ctx.fillStyle = PALETTE.text_secondary;
  const xTicks = options.xTicks ?? niceTicks(options.xMin, options.xMax, 6);
  xTicks.forEach((tick) => {
    const x = scaleX(tick, scale);
    if (x < rect.x - 1 || x > rect.x + rect.width + 1) return;
    ctx.strokeStyle = PALETTE.border;
    ctx.beginPath();
    ctx.moveTo(x, rect.y);
    ctx.lineTo(x, rect.y + rect.height);
    ctx.stroke();
    ctx.textAlign = "center";
    ctx.textBaseline = "alphabetic";
    ctx.fillText(formatTick(tick), x, rect.y + rect.height + 20);
  });

  ctx.textAlign = "right";
  ctx.textBaseline = "middle";
  options.rows.forEach((row, index) => {
    ctx.fillText(row, rect.x - 12, frame.rowY(index));
  });

  ctx.fillStyle = PALETTE.text_secondary;
  ctx.font = "13px 'JetBrains Mono', monospace";
  ctx.textAlign = "center";
  ctx.textBaseline = "alphabetic";
  ctx.fillText(options.xLabel, rect.x + rect.width / 2, rect.y + rect.height + 46);

  return frame;
}
