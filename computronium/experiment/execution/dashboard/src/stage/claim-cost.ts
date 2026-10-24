/** The claim's cost — the seeds measured against the seeds a claim needs (TODO69 Phase 5).

    The run measured what it could and stopped. This draws the bill: for every
    cell, the seeds that were measured beside the seeds a claim is measured
    against, and the gap between them. It is the picture behind the sentence
    "the claim cannot be made yet: too few seeds".
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
} from "./state.js";
import type { StageView, ViewGroup } from "./views.js";

interface Cost {
  cell: CellAggregate;
  label: string;
  color: string;
  measured: number;
  required: number;
}

export class ClaimCostView implements StageView {
  id = "cost";
  name = "The claim's cost";
  group = "process" as ViewGroup;
  caption =
    "The seeds each cell measured, against the seeds a claim is measured against.";

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

  /** The cells, and what each of them owes the claim. */
  private costs(): Cost[] {
    const axes = stageState.axes;
    const required = stageState.requiredSeeds;
    const cells = measuredCells(stageState.aggregates, axes);
    const varying = varyingAxes(cells, axes);
    return cells
      .map((cell) => ({
        cell,
        label: cellLabel(cell, axes, varying),
        color: ARM_COLORS[cell.coordinate.credit] ?? PALETTE.gradient,
        measured: cell.seeds,
        required,
      }))
      .sort(
        (left, right) =>
          right.required - right.measured - (left.required - left.measured),
      );
  }

  private draw(): void {
    const costs = this.costs();
    if (costs.length === 0) {
      this.drawn = false;
      return;
    }

    const ctx = stageCanvas.begin();
    const area = stageCanvas.area();
    const required = Math.max(
      stageState.requiredSeeds,
      ...costs.map((cost) => cost.measured),
    );

    const frame = drawRowFrame(ctx, area, {
      xMin: 0,
      xMax: required,
      rows: costs.map((cost) => cost.label),
      title: "The claim's cost",
      subtitle: "the seeds measured, and the seeds a claim still needs",
      xLabel: "seeds",
    });

    const toX = (value: number): number =>
      frame.rect.x + (value / (frame.xMax || 1)) * frame.rect.width;

    costs.forEach((cost, index) => {
      const y = frame.rowY(index);
      const barHeight = Math.min(26, frame.rowHeight * 0.5);

      // The cost of the claim: the channel the seeds would have to fill.
      ctx.fillStyle = PALETTE.bg_tertiary;
      ctx.fillRect(
        frame.rect.x,
        y - barHeight / 2,
        toX(cost.required) - frame.rect.x,
        barHeight,
      );

      // The seeds that were measured.
      const measured = toX(cost.measured) - frame.rect.x;
      ctx.fillStyle = cost.color;
      ctx.fillRect(frame.rect.x, y - barHeight / 2, measured, barHeight);

      // The gap: what is missing, marked as the space it leaves.
      const short = Math.max(0, cost.required - cost.measured);
      if (short > 0) {
        ctx.strokeStyle = PALETTE.warn;
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 4]);
        ctx.beginPath();
        ctx.moveTo(toX(cost.measured) + 4, y);
        ctx.lineTo(toX(cost.required) - 4, y);
        ctx.stroke();
        ctx.setLineDash([]);
      }

      ctx.strokeStyle = PALETTE.border;
      ctx.lineWidth = 1;
      ctx.strokeRect(
        frame.rect.x + 0.5,
        y - barHeight / 2,
        toX(cost.required) - frame.rect.x - 1,
        barHeight - 1,
      );

      // The counts, beside the bar.
      ctx.font = "12px 'JetBrains Mono', monospace";
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      ctx.fillStyle = PALETTE.text_secondary;
      ctx.fillText(
        `${cost.measured} of ${cost.required}`,
        frame.rect.x + frame.rect.width + 12,
        y - 8,
      );
      if (short > 0) {
        ctx.fillStyle = PALETTE.warn;
        ctx.fillText(
          `${short} short`,
          frame.rect.x + frame.rect.width + 12,
          y + 9,
        );
      }
    });

    // The requirement, drawn across every row: the line the run has not reached.
    const requiredX = toX(stageState.requiredSeeds);
    if (requiredX > frame.rect.x && requiredX < frame.rect.x + frame.rect.width) {
      ctx.strokeStyle = PALETTE.text_secondary;
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 4]);
      ctx.beginPath();
      ctx.moveTo(requiredX, frame.rect.y);
      ctx.lineTo(requiredX, frame.rect.y + frame.rect.height);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    const short = costs.reduce(
      (sum, cost) => sum + Math.max(0, cost.required - cost.measured),
      0,
    );
    drawNote(
      ctx,
      area,
      `the claim is ${short} seeds short over ${costs.length} cells`,
    );

    this.drawn = true;
  }
}
