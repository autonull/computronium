/** The ledger — every arm the run measured, and where it stands (TODO69).

    The evidence views say what the run found. This says what the run *can
    say*: every arm it measured, the evidence behind it, and the gate's
    standing on it — PASSED, INSUFFICIENT or REJECTED. Underneath are the
    limitations the report derived, and the report's own test.

    The arms that fell short are here too. A ledger that lists only the
    claims hides the hole the claims leave.
*/

import { ARM_COLORS, PALETTE } from "../colors.js";
import { stageCanvas } from "./canvas2d.js";
import { drawNote, drawTitle, wrapText } from "./plot2d.js";
import { stageState, type LedgerArm } from "./state.js";
import type { StageView, ViewGroup } from "./views.js";

/** The colour a verdict is written in. */
const VERDICT_COLORS: Record<string, string> = {
  PASSED: PALETTE.passed,
  INSUFFICIENT: PALETTE.insufficient,
  REJECTED: PALETTE.rejected,
};

export class LedgerView implements StageView {
  id = "ledger";
  name = "The ledger";
  group = "the judgement" as ViewGroup;
  caption =
    "Every arm the run measured, its evidence, and the gate's standing on it.";
  key = "l";

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

  /** The gate's verdict, written in its own colour. */
  private chip(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    text: string,
  ): void {
    const color = VERDICT_COLORS[text] ?? PALETTE.text_secondary;
    ctx.font = "11px 'JetBrains Mono', monospace";
    const width = ctx.measureText(text).width + 18;
    ctx.fillStyle = `${color}22`;
    ctx.strokeStyle = `${color}88`;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(x, y - 9, width, 18, 9);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = color;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(text, x + width / 2, y);
  }

  /** The gate's standing on every arm, as one bar. */
  private standingBar(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    width: number,
    standings: Record<string, number>,
    arms: number,
  ): void {
    const total = Object.values(standings).reduce((sum, count) => sum + count, 0);
    if (total === 0) return;

    const height = 18;
    let cursor = x;
    Object.entries(standings).forEach(([verdict, count]) => {
      if (count <= 0) return;
      const segment = (count / total) * width;
      ctx.fillStyle = VERDICT_COLORS[verdict] ?? PALETTE.text_secondary;
      ctx.fillRect(cursor, y, Math.max(2, segment - 2), height);
      if (segment > 52) {
        ctx.fillStyle = PALETTE.bg;
        ctx.font = "11px 'JetBrains Mono', monospace";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(`${count}`, cursor + (segment - 2) / 2, y + height / 2);
      }
      cursor += segment;
    });

    ctx.font = "12px 'JetBrains Mono', monospace";
    ctx.textAlign = "left";
    ctx.textBaseline = "alphabetic";
    ctx.fillStyle = PALETTE.text_secondary;
    ctx.fillText(
      `${arms} arm${arms === 1 ? "" : "s"}, and where each one stands`,
      x,
      y - 10,
    );
  }

  private draw(): void {
    const ledger = stageState.account?.ledger;
    if (!ledger || ledger.claims.length === 0) {
      this.drawn = false;
      return;
    }

    const ctx = stageCanvas.begin();
    const area = stageCanvas.area();

    drawTitle(
      ctx,
      area,
      "The ledger",
      "every arm the run measured, its evidence, and the gate's standing on it",
    );

    let y = area.y + 96;
    this.standingBar(
      ctx,
      area.x,
      y,
      Math.min(560, area.width * 0.55),
      ledger.standings,
      ledger.claims.length,
    );
    y += 66;

    // The arms: what each one measured, and what the gate made of it.
    ledger.claims.forEach((arm: LedgerArm) => {
      const color = ARM_COLORS[arm.value] ?? PALETTE.gradient;
      ctx.font = "14px 'JetBrains Mono', monospace";
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      ctx.fillStyle = color;
      ctx.fillText(`${arm.axis} = ${arm.value}`, area.x, y);

      ctx.font = "13px 'JetBrains Mono', monospace";
      ctx.fillStyle = PALETTE.text_primary;
      ctx.fillText(
        `${arm.mean.toFixed(3)} ± ${arm.sd.toFixed(3)}`,
        area.x + 300,
        y,
      );
      ctx.font = "12px 'JetBrains Mono', monospace";
      ctx.fillStyle = PALETTE.text_secondary;
      ctx.fillText(
        `${arm.n} seeds · ${arm.cells} cell${arm.cells === 1 ? "" : "s"}`,
        area.x + 460,
        y,
      );
      this.chip(ctx, area.x + 640, y, arm.verdict);
      y += 42;
    });

    // What was held fixed: the axes the run did not vary.
    if (ledger.fixed.length > 0) {
      y += 22;
      ctx.font = "600 14px 'JetBrains Mono', monospace";
      ctx.textAlign = "left";
      ctx.textBaseline = "alphabetic";
      ctx.fillStyle = PALETTE.text_primary;
      ctx.fillText("What was held fixed", area.x, y);
      y += 24;

      ctx.font = "12px 'JetBrains Mono', monospace";
      ledger.fixed.forEach((axis) => {
        ctx.textAlign = "left";
        ctx.textBaseline = "middle";
        ctx.fillStyle = PALETTE.text_secondary;
        ctx.fillText(`${axis.axis} = ${axis.value}`, area.x, y);
        ctx.fillText(
          `${axis.mean.toFixed(3)}`,
          area.x + 300,
          y,
        );
        ctx.fillText(
          `${axis.n} measurements · ${axis.cells} cells`,
          area.x + 460,
          y,
        );
        y += 26;
      });
    }

    // What holds the claims back: the report's own limitations.
    y += 22;
    ctx.font = "600 14px 'JetBrains Mono', monospace";
    ctx.textAlign = "left";
    ctx.textBaseline = "alphabetic";
    ctx.fillStyle = PALETTE.text_primary;
    ctx.fillText("What holds it back", area.x, y);
    y += 24;

    ctx.font = "13px 'JetBrains Mono', monospace";
    ledger.limitations.forEach((limitation) => {
      wrapText(ctx, `· ${limitation.detail}`, area.width).forEach((line) => {
        ctx.fillStyle = PALETTE.text_secondary;
        ctx.fillText(line, area.x, y);
        y += 20;
      });
    });

    if (ledger.significance) {
      y += 14;
      wrapText(ctx, `the report's test — ${ledger.significance}`, area.width).forEach(
        (line) => {
          ctx.fillStyle = PALETTE.text_secondary;
          ctx.fillText(line, area.x, y);
          y += 20;
        },
      );
    }

    drawNote(
      ctx,
      area,
      `a claim needs ${ledger.min_seeds} seeds per cell`
        + (ledger.chance !== null ? ` · the chance level is ${ledger.chance.toFixed(3)}` : ""),
    );

    this.drawn = true;
  }
}
