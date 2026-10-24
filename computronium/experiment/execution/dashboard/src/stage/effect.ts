/** The effect — which axis moved the objective (TODO69).

    A run can only speak about the axes it varied. This draws one column per
    axis: a band spanning the arms of an axis that varied, and a mark for an
    axis that was held fixed at one value. The columns are read against the
    run's own objective, so the picture says both what moved and what was
    pinned — and the note under it says, in the server's words, whether the
    run is big enough to attribute anything at all.
*/

import { ARM_COLORS, PALETTE } from "../colors.js";
import { stageCanvas } from "./canvas2d.js";
import { drawCategoryFrame, drawNote } from "./plot2d.js";
import { stageState, type AttributionArm, type AttributionAxis } from "./state.js";
import type { StageView, ViewGroup } from "./views.js";

export class EffectView implements StageView {
  id = "effect";
  name = "The effect";
  group = "analysis" as ViewGroup;
  caption =
    "Which axis moved the objective, and which the run held fixed: the run's attribution, and its limits.";
  key = "e";

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
    const attribution = stageState.attribution;
    const axes = attribution?.axes ?? [];
    if (!attribution || axes.length === 0) {
      this.drawn = false;
      return;
    }

    const ctx = stageCanvas.begin();
    const area = stageCanvas.area();

    const means = axes.flatMap((axis: AttributionAxis) =>
      axis.values.map((arm: AttributionArm) => arm.mean),
    );
    const highest = Math.max(...means, 0.1);

    const frame = drawCategoryFrame(ctx, area, {
      yMin: 0,
      yMax: highest * 1.15,
      categories: axes.map((axis: AttributionAxis) => axis.axis),
      title: "The effect",
      subtitle: attribution.summary,
      yLabel: attribution.metric || "the objective",
    });

    const toY = (value: number): number =>
      frame.rect.y +
      frame.rect.height -
      (value / (frame.yMax || 1)) * frame.rect.height;

    axes.forEach((axis: AttributionAxis, index: number) => {
      const centre = frame.band(index);
      const width = Math.min(46, frame.bandWidth * 0.4);

      if (axis.varied && axis.values.length > 1) {
        const lowest = Math.min(...axis.values.map((arm) => arm.mean));
        const highestMean = Math.max(...axis.values.map((arm) => arm.mean));
        const top = toY(highestMean);
        const bottom = toY(lowest);

        // The band: how far apart this axis's arms stand.
        ctx.fillStyle = `${PALETTE.gradient}33`;
        ctx.fillRect(centre - width / 2, top, width, bottom - top);
        ctx.strokeStyle = PALETTE.gradient;
        ctx.lineWidth = 1;
        ctx.strokeRect(centre - width / 2, top, width, bottom - top);

        // Each arm, where it stands.
        const placed: number[] = [];
        axis.values.forEach((arm: AttributionArm) => {
          const y = toY(arm.mean);
          const color = ARM_COLORS[arm.value] ?? PALETTE.gradient;
          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.arc(centre, y, 5, 0, Math.PI * 2);
          ctx.fill();

          // The name, beside the arm it names. Two arms that stand at the
          // same level would write their names on top of one another, so a
          // name that would collide is stepped down.
          let label = y;
          while (placed.some((other: number) => Math.abs(other - label) < 14)) {
            label += 14;
          }
          placed.push(label);

          ctx.font = "12px 'JetBrains Mono', monospace";
          ctx.textAlign = "left";
          ctx.textBaseline = "middle";
          ctx.fillStyle = color;
          ctx.fillText(arm.value, centre + width / 2 + 10, label);
        });
        return;
      }

      // An axis that was held fixed: one value, and one mark.
      const arm = axis.values[0];
      if (!arm) return;
      const y = toY(arm.mean);
      ctx.strokeStyle = PALETTE.text_muted;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(centre - 7, y);
      ctx.lineTo(centre + 7, y);
      ctx.stroke();

      ctx.font = "12px 'JetBrains Mono', monospace";
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.fillStyle = PALETTE.text_muted;
      ctx.fillText(arm.value, centre, y + 10);
    });

    drawNote(ctx, area, attribution.reason);
    this.drawn = true;
  }
}
