/** The uncertainty — each cell's interval against the level a claim needs (TODO69 Phase 5).

    A mean on its own says nothing about whether the run can be trusted with
    it. This draws the margin the statistical gate asks for — the cell's own
    standard error, times the gate's sigma — around every cell's mean, and
    the chance level beside it: a cell is only separable when its margin
    clears the chance.
*/

import { ARM_COLORS, PALETTE } from "../colors.js";
import { stageCanvas } from "./canvas2d.js";
import { drawNote, drawRowFrame } from "./plot2d.js";
import {
  cellLabel,
  measuredCells,
  stageState,
  varyingAxes,
  type CellAggregate,
} from "./store.js";
import type { StageView, ViewGroup } from "./views.js";

interface Interval {
  cell: CellAggregate;
  label: string;
  color: string;
  mean: number;
  margin: number;
  lower: number;
  upper: number;
  threshold: number;
}

export class UncertaintyView implements StageView {
  id = "uncertainty";
  name = "The uncertainty";
  group = "the evidence" as ViewGroup;
  caption =
    "Each cell's mean and the margin the gate asks for, against the chance level.";

  private visible = false;
  private drawn = false;

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

  /** The margin the gate asks for, in multiples of the cell's own error. */
  private sigma(): number {
    const gate = stageState.gate;
    if (gate && typeof gate.superiority_margin_sigma === "number") {
      return gate.superiority_margin_sigma;
    }
    return 2;
  }

  /** The cells, their means, and the margin around each mean. */
  private intervals(): Interval[] {
    const axes = stageState.axes;
    const chance = stageState.chance;
    const sigma = this.sigma();
    const cells = measuredCells(stageState.aggregates, axes);
    const varying = varyingAxes(cells, axes);

    return cells
      .filter((cell) => cell.acc.length > 0)
      .map((cell) => {
        const n = cell.acc.length;
        const mean = cell.acc.reduce((sum, v) => sum + v, 0) / n;
        const variance =
          cell.acc.reduce((sum, v) => sum + (v - mean) ** 2, 0) /
          Math.max(1, n - 1);
        const error = n > 1 ? Math.sqrt(variance / n) : 0;
        const margin = sigma * error;
        return {
          cell,
          label: cellLabel(cell, axes, varying),
          color: ARM_COLORS[cell.coordinate.credit] ?? PALETTE.gradient,
          mean,
          margin,
          lower: mean - margin,
          upper: mean + margin,
          threshold: chance + margin,
        };
      })
      .sort((left, right) => right.mean - left.mean);
  }

  private draw(): void {
    const intervals = this.intervals();
    if (intervals.length === 0) {
      this.drawn = false;
      return;
    }

    const ctx = stageCanvas.begin();
    const area = stageCanvas.area();
    const chance = stageState.chance;
    const sigma = this.sigma();

    const highest = Math.max(
      chance,
      ...intervals.map((interval) =>
        Math.max(interval.upper, interval.threshold),
      ),
    );

    const frame = drawRowFrame(ctx, area, {
      xMin: 0,
      xMax: highest * 1.12,
      rows: intervals.map((interval) => interval.label),
      title: "The uncertainty",
      subtitle: "each cell's mean, and the margin the gate asks for",
      xLabel: "accuracy",
    });

    const toX = (value: number): number =>
      frame.rect.x + (value / (frame.xMax || 1)) * frame.rect.width;

    // The chance level: the line every claim has to clear.
    const chanceX = toX(chance);
    ctx.strokeStyle = PALETTE.chance_line;
    ctx.lineWidth = 1.5;
    ctx.setLineDash([6, 5]);
    ctx.beginPath();
    ctx.moveTo(chanceX, frame.rect.y);
    ctx.lineTo(chanceX, frame.rect.y + frame.rect.height);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.font = "11px 'JetBrains Mono', monospace";
    ctx.textAlign = "left";
    ctx.textBaseline = "alphabetic";
    ctx.fillStyle = PALETTE.chance_line;
    ctx.fillText("chance", chanceX + 6, frame.rect.y + 14);

    intervals.forEach((interval, index) => {
      const y = frame.rowY(index);
      const clears = interval.lower > chance;

      // The margin: the cell's mean, and the error the gate allows it.
      ctx.strokeStyle = interval.color;
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(toX(interval.lower), y);
      ctx.lineTo(toX(interval.upper), y);
      ctx.stroke();

      // The threshold this cell has to clear: chance, plus its own margin.
      ctx.strokeStyle = clears ? PALETTE.ok : PALETTE.warn;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(toX(interval.threshold), y - 11);
      ctx.lineTo(toX(interval.threshold), y + 11);
      ctx.stroke();

      // The mean itself.
      ctx.fillStyle = interval.color;
      ctx.beginPath();
      ctx.arc(toX(interval.mean), y, 5, 0, Math.PI * 2);
      ctx.fill();

      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      ctx.font = "12px 'JetBrains Mono', monospace";
      ctx.fillStyle = clears ? PALETTE.ok : PALETTE.warn;
      ctx.fillText(
        clears ? "clears chance" : "not yet separable",
        frame.rect.x + frame.rect.width + 12,
        y,
      );
    });

    drawNote(
      ctx,
      area,
      `the bar is ±${sigma}·SE · the tick is the threshold each cell has to clear` +
        ` · a claim needs ${stageState.requiredSeeds} seeds per cell`,
    );

    this.drawn = true;
  }
}
