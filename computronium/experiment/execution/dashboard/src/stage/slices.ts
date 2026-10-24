/** The slices — the space, cut three ways, side by side (TODO70 Phase 7).

    One picture of the space is one cut of it: three axes free, three held at
    one value each. A reader who has seen one cut has seen one third of the
    space, and the space is six axes' worth of pictures. This view puts three
    cuts side by side, so a reader sees that the space is not one picture.

    It needs no new data: the space and the records are already on the stage,
    and the same cell is looked at three ways.
*/

import { PALETTE } from "../colors.js";
import { stageCanvas } from "./canvas2d.js";
import { rampColor } from "./ramp.js";
import { cellKey, mean, stageState } from "./state.js";
import { wrapLabel } from "./sprites.js";
import type { StageView, ViewGroup } from "./views.js";

/** Which axis plays which part in one cut. */
type Axis = "x" | "y" | "z";

/** One cut of the space: two axes free, one collapsed over. */
interface Cut {
  /** The axis the columns run along. */
  across: Axis;
  /** The axis the rows run down. */
  down: Axis;
  /** The axis the cut collapses over. */
  held: Axis;
}

/** The three cuts, in the order they are drawn. */
const CUTS: Cut[] = [
  { across: "x", down: "y", held: "z" },
  { across: "x", down: "z", held: "y" },
  { across: "y", down: "z", held: "x" },
];

/** One cell of a cut: what the space holds there. */
interface SliceCell {
  status: "measured" | "gap" | "void";
  accuracy: number;
}

export class SlicesView implements StageView {
  id = "slices";
  name = "The slices";
  group = "analysis" as ViewGroup;
  /** The letters are gone; the next view takes a punctuation key. */
  key = ",";
  caption =
    "The same space, cut three ways: three pairs of axes, side by side, so the space is not one picture.";

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

  /** One cut: the cells of the space, seen through two of its axes. */
  private cut(cut: Cut): {
    cells: SliceCell[];
    across: string[];
    down: string[];
  } {
    const space = stageState.space;
    if (!space) return { cells: [], across: [], down: [] };

    const axes = stageState.axes;
    const acrossValues = space.values[axes[cut.across]] ?? [];
    const downValues = space.values[axes[cut.down]] ?? [];
    const heldValues = space.values[axes[cut.held]] ?? [];

    const cells: SliceCell[] = [];
    acrossValues.forEach((across) => {
      downValues.forEach((down) => {
        let voidCells = 0;
        let legalCells = 0;
        let best = -Infinity;
        heldValues.forEach((held) => {
          const key = this.keyOf(axes, cut, across, down, held);
          const cell = stageState.spaceCells.get(key);
          if (cell?.status === "void") {
            voidCells += 1;
            return;
          }
          legalCells += 1;
          const aggregate = stageState.aggregates.get(key);
          if (!aggregate || aggregate.acc.length === 0) return;
          best = Math.max(best, mean(aggregate.acc));
        });
        cells.push({
          status:
            voidCells > 0 && legalCells === 0
              ? "void"
              : best > -Infinity
                ? "measured"
                : "gap",
          accuracy: best > -Infinity ? best : 0,
        });
      });
    });
    return { cells, across: acrossValues, down: downValues };
  }

  /** The key a cell has in the stage's own axis order. */
  private keyOf(
    axes: { x: string; y: string; z: string },
    cut: Cut,
    across: string,
    down: string,
    held: string,
  ): string {
    const value = { x: "", y: "", z: "" };
    value[cut.across] = across;
    value[cut.down] = down;
    value[cut.held] = held;
    return cellKey(value.x, value.y, value.z);
  }

  private draw(): void {
    const space = stageState.space;
    if (!space) {
      this.drawn = false;
      return;
    }

    const ctx = stageCanvas.begin();
    const area = stageCanvas.area();
    const axes = stageState.axes;

    ctx.fillStyle = PALETTE.text_primary;
    ctx.font = "600 22px 'JetBrains Mono', monospace";
    ctx.textAlign = "left";
    ctx.textBaseline = "alphabetic";
    ctx.fillText("The slices", area.x, area.y + 14);

    ctx.fillStyle = PALETTE.text_secondary;
    ctx.font = "13px 'JetBrains Mono', monospace";
    ctx.fillText(
      "One space, three cuts: the axes a reader sees are a choice, and every choice hides an axis.",
      area.x,
      area.y + 40,
    );

    const gap = 28;
    const sliceWidth = (area.width - gap * 2) / 3;
    let measured = 0;
    let gaps = 0;
    let refused = 0;

    CUTS.forEach((cut, index) => {
      const { cells, across, down } = this.cut(cut);
      const left = area.x + index * (sliceWidth + gap);
      const top = area.y + 70;
      const labelWidth = 96;
      const labelHeight = 54;
      const plot = {
        x: left + labelWidth,
        y: top,
        width: Math.max(60, sliceWidth - labelWidth - 12),
        height: Math.max(60, area.height - 70 - labelHeight),
      };
      const cellWidth = across.length ? plot.width / across.length : 0;
      const cellHeight = down.length ? plot.height / down.length : 0;
      const maxAccuracy = Math.max(
        ...cells.map((cell) => cell.accuracy),
        0.0001,
      );

      // The cut's own name: the two axes it shows, and the one it hides.
      ctx.fillStyle = PALETTE.text_primary;
      ctx.font = "600 13px 'JetBrains Mono', monospace";
      ctx.textAlign = "left";
      ctx.textBaseline = "alphabetic";
      ctx.fillText(
        `${axes[cut.across]} × ${axes[cut.down]}`,
        left,
        top - 12,
      );
      ctx.fillStyle = PALETTE.text_muted;
      ctx.font = "11px 'JetBrains Mono', monospace";
      ctx.fillText(`${axes[cut.held]} collapsed`, left, top - 30);

      cells.forEach((cell, index2) => {
        const xi = Math.floor(index2 / down.length);
        const yi = index2 % down.length;
        const x = plot.x + xi * cellWidth;
        const y = plot.y + yi * cellHeight;

        if (cell.status === "void") {
          refused += 1;
          ctx.fillStyle = `${PALETTE.void}22`;
          ctx.fillRect(x, y, cellWidth, cellHeight);
        } else if (cell.status === "gap") {
          gaps += 1;
          ctx.fillStyle = PALETTE.bg_tertiary;
          ctx.fillRect(x, y, cellWidth, cellHeight);
        } else {
          measured += 1;
          ctx.fillStyle = rampColor(cell.accuracy / maxAccuracy);
          ctx.fillRect(x, y, cellWidth, cellHeight);
        }

        ctx.strokeStyle = PALETTE.bg;
        ctx.lineWidth = 1;
        ctx.strokeRect(x + 0.5, y + 0.5, cellWidth - 1, cellHeight - 1);
      });

      // The values the columns and the rows name.
      ctx.fillStyle = PALETTE.text_secondary;
      ctx.font = "11px 'JetBrains Mono', monospace";
      across.forEach((value, xi) => {
        const lines = wrapLabel(value, 12);
        ctx.textAlign = "center";
        ctx.textBaseline = "top";
        lines.forEach((line, index3) => {
          ctx.fillText(
            line,
            plot.x + xi * cellWidth + cellWidth / 2,
            plot.y + plot.height + 8 + index3 * 14,
          );
        });
      });
      down.forEach((value, yi) => {
        const lines = wrapLabel(value, 14);
        ctx.textAlign = "right";
        ctx.textBaseline = "middle";
        lines.forEach((line, index3) => {
          ctx.fillText(
            line,
            plot.x - 8,
            plot.y +
              yi * cellHeight +
              cellHeight / 2 -
              (lines.length - 1) * 7 +
              index3 * 14,
          );
        });
      });
    });

    ctx.fillStyle = PALETTE.text_secondary;
    ctx.font = "12px 'JetBrains Mono', monospace";
    ctx.textAlign = "left";
    ctx.textBaseline = "alphabetic";
    ctx.fillText(
      `${measured} measured · ${gaps} gaps · ${refused} refused`,
      area.x,
      area.y + area.height + 24,
    );

    this.drawn = measured > 0;
  }
}
