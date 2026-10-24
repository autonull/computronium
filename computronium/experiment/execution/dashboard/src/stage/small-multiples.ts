/** The small multiples — one panel per cell, every seed's curve (TODO69 Phase 5).

    The convergence draws one curve per arm, averaged over the seeds, and the
    average is what hides a lottery. This draws what the average hides: every
    seed of every cell, in a panel of its own, on the same axes, so a reader
    can see which cells are steady and which are a toss of the coin.
*/

import { ARM_COLORS, PALETTE } from "../colors.js";
import { stageCanvas } from "./canvas2d.js";
import { drawNote, drawTitle } from "./plot2d.js";
import {
  cellLabel,
  measuredCells,
  stageState,
  varyingAxes,
  type CellAggregate,
} from "./state.js";
import type { StageView, ViewGroup } from "./views.js";

interface Panel {
  cell: CellAggregate;
  label: string;
  color: string;
  curves: { epoch: number; val_acc: number }[][];
}

export class SmallMultiplesView implements StageView {
  id = "multiples";
  name = "Small multiples";
  group = "analysis" as ViewGroup;
  caption =
    "One panel per cell: every seed's own curve, on the same accuracy scale.";

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

  /** The panels: one per cell that measured a curve. */
  private panels(): Panel[] {
    const axes = stageState.axes;
    const cells = measuredCells(stageState.aggregates, axes);
    const varying = varyingAxes(cells, axes);
    return cells
      .filter((cell) => cell.curves.length > 0)
      .map((cell) => ({
        cell,
        label: cellLabel(cell, axes, varying),
        color: ARM_COLORS[cell.coordinate.credit] ?? PALETTE.gradient,
        curves: cell.curves,
      }));
  }

  private draw(): void {
    const panels = this.panels();
    if (panels.length === 0) {
      this.drawn = false;
      return;
    }

    const ctx = stageCanvas.begin();
    const area = stageCanvas.area();
    const chance = stageState.chance;

    const values = panels.flatMap((panel) =>
      panel.curves.flatMap((curve) => curve.map((point) => point.val_acc)),
    );
    const epochs = panels.flatMap((panel) =>
      panel.curves.flatMap((curve) => curve.map((point) => point.epoch)),
    );
    let yMin = Math.min(chance, ...values);
    let yMax = Math.max(chance, ...values);
    if (yMax - yMin < 1e-6) {
      yMin -= 0.05;
      yMax += 0.05;
    }
    const pad = (yMax - yMin) * 0.14;
    yMin -= pad;
    yMax += pad;
    const maxEpoch = Math.max(1, ...epochs);

    const columns = Math.ceil(Math.sqrt(panels.length));
    const rows = Math.ceil(panels.length / columns);
    const gap = 18;
    const gridWidth = area.width - gap * (columns - 1);
    const gridHeight = area.height - 64 - 44 - gap * (rows - 1);
    const panelWidth = gridWidth / columns;
    const panelHeight = gridHeight / rows;

    drawTitle(
      ctx,
      area,
      "Small multiples",
      "every seed of every cell, on one accuracy scale",
    );

    panels.forEach((panel, index) => {
      const column = index % columns;
      const row = Math.floor(index / columns);
      const left = area.x + column * (panelWidth + gap);
      const top = area.y + 64 + row * (panelHeight + gap);

      // The panel's title: the cell, in the arm's colour.
      ctx.fillStyle = panel.color;
      ctx.font = "600 13px 'JetBrains Mono', monospace";
      ctx.textAlign = "left";
      ctx.textBaseline = "alphabetic";
      ctx.fillText(panel.label, left, top + 12);

      const plot = {
        x: left + (column === 0 ? 44 : 10),
        y: top + 30,
        width: panelWidth - (column === 0 ? 54 : 20),
        height: panelHeight - 56,
      };

      ctx.strokeStyle = PALETTE.border;
      ctx.lineWidth = 1;
      ctx.strokeRect(plot.x + 0.5, plot.y + 0.5, plot.width - 1, plot.height - 1);

      // The chance level, under every panel: what every seed is measured against.
      const chanceY = plot.y + plot.height * (1 - (chance - yMin) / (yMax - yMin));
      ctx.strokeStyle = PALETTE.chance_line;
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(plot.x, chanceY);
      ctx.lineTo(plot.x + plot.width, chanceY);
      ctx.stroke();
      ctx.setLineDash([]);

      // The seeds: one curve each, over the epochs they measured.
      panel.curves.forEach((curve) => {
        ctx.strokeStyle = panel.color;
        ctx.lineWidth = 1.8;
        ctx.beginPath();
        curve.forEach((point, pointIndex) => {
          const x =
            plot.x + (point.epoch / maxEpoch) * plot.width;
          const y =
            plot.y + plot.height * (1 - (point.val_acc - yMin) / (yMax - yMin));
          if (pointIndex === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        });
        ctx.stroke();
      });

      // The scale, on the first column and the last row only.
      ctx.fillStyle = PALETTE.text_muted;
      ctx.font = "9px 'JetBrains Mono', monospace";
      if (column === 0) {
        ctx.textAlign = "right";
        ctx.textBaseline = "middle";
        [yMax, (yMax + yMin) / 2, yMin].forEach((tick) => {
          const y =
            plot.y + plot.height * (1 - (tick - yMin) / (yMax - yMin));
          ctx.fillText(tick.toFixed(2), plot.x - 6, y);
        });
      }
      if (row === rows - 1) {
        ctx.textAlign = "left";
        ctx.textBaseline = "top";
        ctx.fillText("epoch 0", plot.x, plot.y + plot.height + 6);
        ctx.textAlign = "right";
        ctx.fillText(
          `epoch ${maxEpoch}`,
          plot.x + plot.width,
          plot.y + plot.height + 6,
        );
      }
    });

    const seeds = panels.reduce((sum, panel) => sum + panel.curves.length, 0);
    drawNote(
      ctx,
      area,
      `${panels.length} cells · ${seeds} seeds`
        + ` · the dashed line is the chance level (${chance.toFixed(2)})`,
    );

    this.drawn = true;
  }
}
