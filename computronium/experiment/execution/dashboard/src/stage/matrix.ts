/** The evidence matrix — the space, flat (TODO69 Phase 5).

    The same space the map draws in three dimensions, seen from above: one
    axis against another, every column a number, the cells the system
    refuses in the void's colour. It needs no new data at all — the space
    and the records are already on the stage.
*/

import { PALETTE } from "../colors.js";
import { stageCanvas } from "./canvas2d.js";
import { rampColor } from "./ramp.js";
import { cellKey, mean, stageState } from "./state.js";
import { wrapLabel } from "./sprites.js";
import type { StageView, ViewGroup } from "./views.js";

type ColumnStatus = "measured" | "gap" | "void";

interface Column {
  status: ColumnStatus;
  accuracy: number;
  arm: string;
}

export class MatrixView implements StageView {
  id = "matrix";
  name = "Evidence matrix";
  group = "analysis" as ViewGroup;
  caption =
    "The space seen from above: one axis against another, every column a number, the refusals in the void colour.";

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

  /** The columns of the matrix: one per (x, y) pair, collapsed over z. */
  private columns(): {
    columns: Column[];
    xValues: string[];
    yValues: string[];
  } {
    const space = stageState.space;
    if (!space) return { columns: [], xValues: [], yValues: [] };

    const axes = stageState.axes;
    const xValues = space.values[axes.x] ?? [];
    const yValues = space.values[axes.y] ?? [];
    const zValues = space.values[axes.z] ?? [];

    const columns: Column[] = [];
    xValues.forEach((x) => {
      yValues.forEach((y) => {
        let voidCells = 0;
        let legalCells = 0;
        let best = -Infinity;
        let arm = "";
        zValues.forEach((z) => {
          const key = cellKey(x, y, z);
          const cell = stageState.spaceCells.get(key);
          if (cell?.status === "void") {
            voidCells += 1;
            return;
          }
          legalCells += 1;
          const aggregate = stageState.aggregates.get(key);
          if (!aggregate || aggregate.acc.length === 0) return;
          const accuracy = mean(aggregate.acc);
          if (accuracy > best) {
            best = accuracy;
            arm = aggregate.coordinate.credit ?? "";
          }
        });
        const status: ColumnStatus =
          voidCells > 0 && legalCells === 0
            ? "void"
            : best > -Infinity
              ? "measured"
              : "gap";
        columns.push({
          status,
          accuracy: best > -Infinity ? best : 0,
          arm,
        });
      });
    });
    return { columns, xValues, yValues };
  }

  private draw(): void {
    const { columns, xValues, yValues } = this.columns();
    if (columns.length === 0) {
      this.drawn = false;
      return;
    }

    const ctx = stageCanvas.begin();
    const area = stageCanvas.area();
    const axes = stageState.axes;

    const nx = xValues.length;
    const ny = yValues.length;
    const labelWidth = 150;
    const labelHeight = 96;
    const plot = {
      x: area.x + labelWidth,
      y: area.y + 70,
      width: Math.max(80, area.width - labelWidth - 40),
      height: Math.max(80, area.height - 70 - labelHeight),
    };
    const cellWidth = plot.width / nx;
    const cellHeight = plot.height / ny;

    const maxAccuracy = Math.max(
      ...columns.map((column) => column.accuracy),
      0.0001,
    );

    ctx.fillStyle = PALETTE.text_primary;
    ctx.font = "600 22px 'JetBrains Mono', monospace";
    ctx.textAlign = "left";
    ctx.textBaseline = "alphabetic";
    ctx.fillText("Evidence matrix", area.x, area.y + 14);

    ctx.fillStyle = PALETTE.text_secondary;
    ctx.font = "13px 'JetBrains Mono', monospace";
    ctx.fillText(
      `${axes.x} against ${axes.y} — the best cell of each column`,
      area.x,
      area.y + 40,
    );

    let measured = 0;
    let gaps = 0;
    let refused = 0;

    columns.forEach((column, index) => {
      const xi = Math.floor(index / ny);
      const yi = index % ny;
      const x = plot.x + xi * cellWidth;
      const y = plot.y + yi * cellHeight;

      if (column.status === "void") {
        refused += 1;
        ctx.fillStyle = `${PALETTE.void}22`;
        ctx.fillRect(x, y, cellWidth, cellHeight);
        this.drawCross(ctx, x, y, cellWidth, cellHeight);
      } else if (column.status === "gap") {
        gaps += 1;
        ctx.fillStyle = PALETTE.bg_tertiary;
        ctx.fillRect(x, y, cellWidth, cellHeight);
      } else {
        measured += 1;
        ctx.fillStyle = rampColor(column.accuracy / maxAccuracy);
        ctx.fillRect(x, y, cellWidth, cellHeight);
        if (cellWidth > 44 && cellHeight > 26) {
          ctx.fillStyle = textOn(column.accuracy / maxAccuracy);
          ctx.font = "600 15px 'JetBrains Mono', monospace";
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillText(
            column.accuracy.toFixed(2),
            x + cellWidth / 2,
            y + cellHeight / 2,
          );
        }
      }

      ctx.strokeStyle = PALETTE.bg;
      ctx.lineWidth = 1;
      ctx.strokeRect(x + 0.5, y + 0.5, cellWidth - 1, cellHeight - 1);
    });

    // The values the columns and the rows name.
    ctx.fillStyle = PALETTE.text_secondary;
    ctx.font = "12px 'JetBrains Mono', monospace";
    xValues.forEach((value, xi) => {
      const lines = wrapLabel(value, 14);
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      lines.forEach((line, index) => {
        ctx.fillText(
          line,
          plot.x + xi * cellWidth + cellWidth / 2,
          plot.y + plot.height + 12 + index * 16,
        );
      });
    });
    yValues.forEach((value, yi) => {
      const lines = wrapLabel(value, 16);
      ctx.textAlign = "right";
      ctx.textBaseline = "middle";
      lines.forEach((line, index) => {
        ctx.fillText(
          line,
          plot.x - 12,
          plot.y + yi * cellHeight + cellHeight / 2 - (lines.length - 1) * 8 + index * 16,
        );
      });
    });

    // The colour key: what the colours of the cells mean.
    const keyWidth = 180;
    const keyX = plot.x + plot.width - keyWidth;
    const keyY = area.y + 16;
    const gradient = ctx.createLinearGradient(keyX, 0, keyX + keyWidth, 0);
    gradient.addColorStop(0, rampColor(0));
    gradient.addColorStop(0.5, rampColor(0.5));
    gradient.addColorStop(1, rampColor(1));
    ctx.fillStyle = gradient;
    ctx.fillRect(keyX, keyY, keyWidth, 12);
    ctx.strokeStyle = PALETTE.border;
    ctx.strokeRect(keyX + 0.5, keyY + 0.5, keyWidth - 1, 11);
    ctx.fillStyle = PALETTE.text_secondary;
    ctx.font = "11px 'JetBrains Mono', monospace";
    ctx.textAlign = "left";
    ctx.textBaseline = "top";
    ctx.fillText("0", keyX, keyY + 18);
    ctx.textAlign = "right";
    ctx.fillText(maxAccuracy.toFixed(2), keyX + keyWidth, keyY + 18);

    ctx.textAlign = "left";
    ctx.fillText(
      `${measured} measured · ${gaps} gaps · ${refused} refused`,
      area.x,
      area.y + area.height + 30,
    );

    this.drawn = measured > 0;
  }

  /** The cross that marks a column the system refuses. */
  private drawCross(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    width: number,
    height: number,
  ): void {
    const size = Math.min(width, height) * 0.28;
    const cx = x + width / 2;
    const cy = y + height / 2;
    ctx.strokeStyle = PALETTE.void;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(cx - size, cy - size);
    ctx.lineTo(cx + size, cy + size);
    ctx.moveTo(cx + size, cy - size);
    ctx.lineTo(cx - size, cy + size);
    ctx.stroke();
  }
}

/** The colour a number is written in: dark on a bright cell, light on a dark one. */
function textOn(fraction: number): string {
  return fraction > 0.62 ? PALETTE.bg : PALETTE.text_primary;
}
