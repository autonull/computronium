/** The contrast — the arms against one another, and the test (TODO69).

    Which arm beat which, by how much, and whether the run could say so at
    all. Each row joins two arms by the cells they share, and the test's
    verdict stands underneath: a difference measured over one cell is a
    difference, but it is not yet a finding.
*/

import { ARM_COLORS, PALETTE } from "../colors.js";
import { stageCanvas } from "./canvas2d.js";
import { drawNote, drawRowFrame } from "./plot2d.js";
import { stageState, type ContrastArm, type ContrastPair } from "./state.js";
import type { StageView, ViewGroup } from "./views.js";

export class ContrastView implements StageView {
  id = "contrast";
  name = "The contrast";
  group = "analysis" as ViewGroup;
  caption =
    "The run's arms against one another, and whether the test could be run.";
  key = "d";

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

  private draw(): void {
    const contrast = stageState.account?.contrast;
    if (!contrast || contrast.pairs.length === 0) {
      this.drawn = false;
      return;
    }

    const means = new Map<string, number>();
    const spreads = new Map<string, number>();
    contrast.arms.forEach((arm: ContrastArm) => {
      means.set(arm.value, arm.mean);
      spreads.set(arm.value, arm.sd);
    });
    const highest = Math.max(...contrast.arms.map((arm) => arm.mean), 0.001);

    const ctx = stageCanvas.begin();
    const area = stageCanvas.area();

    const frame = drawRowFrame(ctx, area, {
      xMin: 0,
      xMax: highest * 1.15,
      rows: contrast.pairs.map((pair: ContrastPair) => `${pair.a} vs ${pair.b}`),
      title: "The contrast",
      subtitle:
        `the ${contrast.axis} arms on ${contrast.metric}, and what separates them`,
      xLabel: contrast.metric,
    });

    const toX = (value: number): number =>
      frame.rect.x + (value / (frame.xMax || 1)) * frame.rect.width;

    contrast.pairs.forEach((pair: ContrastPair, index) => {
      const y = frame.rowY(index);
      const left = toX(means.get(pair.a) ?? 0);
      const right = toX(means.get(pair.b) ?? 0);

      // The gap between the two arms, filled: the difference, as a distance.
      ctx.fillStyle = `${PALETTE.gradient}33`;
      ctx.fillRect(
        Math.min(left, right),
        y - 11,
        Math.abs(right - left),
        22,
      );

      // The line between the two arms: the gap they share.
      ctx.strokeStyle = PALETTE.border_bright;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(left, y);
      ctx.lineTo(right, y);
      ctx.stroke();

      [pair.a, pair.b].forEach((value) => {
        const x = toX(means.get(value) ?? 0);
        const spread = spreads.get(value) ?? 0;

        // The arm's own spread: the seeds it measured.
        ctx.strokeStyle = ARM_COLORS[value] ?? PALETTE.gradient;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(x, y - 16);
        ctx.lineTo(x, y + 16);
        ctx.stroke();

        ctx.fillStyle = ARM_COLORS[value] ?? PALETTE.gradient;
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, Math.PI * 2);
        ctx.fill();

        ctx.font = "11px 'JetBrains Mono', monospace";
        ctx.textAlign = "center";
        ctx.textBaseline = "bottom";
        ctx.fillStyle = ARM_COLORS[value] ?? PALETTE.gradient;
        ctx.fillText(value, x, y - 18);
      });

      ctx.font = "12px 'JetBrains Mono', monospace";
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      ctx.fillStyle = PALETTE.text_primary;
      const difference = pair.difference ?? 0;
      ctx.fillText(
        `${difference >= 0 ? "+" : "−"}${Math.abs(difference).toFixed(3)}`,
        frame.rect.x + frame.rect.width + 12,
        y - 9,
      );
      ctx.fillStyle = PALETTE.text_secondary;
      ctx.fillText(
        `${pair.shared_cells} shared cell${pair.shared_cells === 1 ? "" : "s"}`,
        frame.rect.x + frame.rect.width + 12,
        y + 9,
      );
    });

    const test = contrast.test;
    drawNote(
      ctx,
      area,
      test.tested
        ? `the test ran: p=${test.p_value?.toFixed(4)} (alpha=${test.alpha})`
          + ` · dz=${test.cohens_dz?.toFixed(2)}`
          + ` · ${test.shared_cells} shared cells`
        : `no test ran: ${test.shared_cells} shared cell`
          + `${test.shared_cells === 1 ? "" : "s"}, ${test.required_cells} required`,
    );

    this.drawn = true;
  }
}
