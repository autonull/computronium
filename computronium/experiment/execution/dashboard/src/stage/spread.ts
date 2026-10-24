/** The spread — one violin per arm, across its seeds (TODO69 Phase 5).

    A mean hides a spread: two arms can carry the same average and disagree
    about everything else. The violin draws the distribution the run actually
    measured — every seed of the arm — and the seeds a claim still needs are
    written under it, because a wide arm is why the claim is not made.
*/

import { ARM_COLORS, PALETTE } from "../colors.js";
import { stageCanvas } from "./canvas2d.js";
import { drawCategoryFrame, drawNote } from "./plot2d.js";
import { stageState } from "./state.js";
import type { StageView, ViewGroup } from "./views.js";

interface Arm {
  name: string;
  values: number[];
  color: string;
}

/** The density of the values at a point, by a Gaussian kernel.

    The bandwidth is Silverman's: the spread of the data decides how wide
    the kernel is, so a tight arm is not smoothed into a wide one.
*/
function density(values: number[], at: number, bandwidth: number): number {
  let total = 0;
  values.forEach((value) => {
    const z = (at - value) / bandwidth;
    total += Math.exp(-0.5 * z * z);
  });
  return total / (values.length * bandwidth * Math.sqrt(2 * Math.PI));
}

function bandwidth(values: number[]): number {
  if (values.length < 2) return 0.02;
  const mean = values.reduce((sum, v) => sum + v, 0) / values.length;
  const variance =
    values.reduce((sum, v) => sum + (v - mean) ** 2, 0) / (values.length - 1);
  const spread = Math.sqrt(variance);
  const silverman = 1.06 * spread * values.length ** -0.2;
  return Math.max(silverman, 0.01);
}

export class SpreadView implements StageView {
  id = "spread";
  name = "The spread";
  group = "the evidence" as ViewGroup;
  caption =
    "One violin per arm, across its seeds: the width is the spread, not the mean.";

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

  /** The arms, and the seeds each of them measured. */
  private arms(): Arm[] {
    const records = stageState.metrics?.records ?? [];
    const byArm = new Map<string, number[]>();
    records.forEach((record: any) => {
      const value = record?.payload?.val_acc;
      const arm = record?.coordinate?.credit;
      if (typeof value !== "number" || !arm) return;
      const values = byArm.get(arm) ?? [];
      values.push(value);
      byArm.set(arm, values);
    });
    return Array.from(byArm.entries())
      .map(([name, values]) => ({
        name,
        values: values.slice().sort((left, right) => left - right),
        color: ARM_COLORS[name] ?? PALETTE.gradient,
      }))
      .sort((left, right) => left.name.localeCompare(right.name));
  }

  private draw(): void {
    const arms = this.arms();
    if (arms.length === 0) {
      this.drawn = false;
      return;
    }

    const ctx = stageCanvas.begin();
    const area = stageCanvas.area();
    const chance = stageState.chance;
    const required = stageState.requiredSeeds;

    // The shape of an arm reaches past its own values: the kernel is wider
    // than the data, so the frame has to hold what the violin draws.
    const extents = arms.map((arm) => {
      const h = bandwidth(arm.values);
      return {
        high: arm.values[arm.values.length - 1] + 1.5 * h,
        low: arm.values[0] - 1.5 * h,
      };
    });
    const yMax =
      Math.max(chance, ...extents.map((extent) => extent.high)) * 1.03;

    const frame = drawCategoryFrame(ctx, area, {
      yMin: 0,
      yMax,
      categories: arms.map((arm) => arm.name),
      title: "The spread",
      subtitle: "every seed of every arm, as a distribution",
      yLabel: "accuracy",
    });

    // The chance level: what every arm is measured against.
    const chanceY = frame.rect.y + frame.rect.height * (1 - chance / frame.yMax);
    ctx.strokeStyle = PALETTE.chance_line;
    ctx.lineWidth = 1.5;
    ctx.setLineDash([6, 5]);
    ctx.beginPath();
    ctx.moveTo(frame.rect.x, chanceY);
    ctx.lineTo(frame.rect.x + frame.rect.width, chanceY);
    ctx.stroke();
    ctx.setLineDash([]);

    // The violins are drawn inside the frame: a shape that reaches past the
    // frame is a shape the reader cannot read.
    ctx.save();
    ctx.beginPath();
    ctx.rect(frame.rect.x, frame.rect.y, frame.rect.width, frame.rect.height);
    ctx.clip();

    arms.forEach((arm, index) => {
      const centre = frame.band(index);
      const half = Math.min(frame.bandWidth * 0.36, 90);
      const h = bandwidth(arm.values);
      const low = arm.values[0] - 1.5 * h;
      const high = arm.values[arm.values.length - 1] + 1.5 * h;

      // The shape of the arm: the density of its seeds, mirrored.
      const samples = 48;
      const widths: number[] = [];
      let peak = 0;
      for (let step = 0; step <= samples; step += 1) {
        const at = low + ((high - low) * step) / samples;
        const value = density(arm.values, at, h);
        widths.push(value);
        peak = Math.max(peak, value);
      }
      const scale = peak > 0 ? 1 / peak : 0;

      const toY = (value: number): number =>
        frame.rect.y + frame.rect.height * (1 - value / frame.yMax);

      ctx.beginPath();
      widths.forEach((value, step) => {
        const at = low + ((high - low) * step) / samples;
        const x = centre + value * scale * half;
        const y = toY(at);
        if (step === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      for (let step = widths.length - 1; step >= 0; step -= 1) {
        const at = low + ((high - low) * step) / samples;
        const x = centre - widths[step] * scale * half;
        ctx.lineTo(x, toY(at));
      }
      ctx.closePath();
      ctx.fillStyle = `${arm.color}33`;
      ctx.fill();
      ctx.strokeStyle = arm.color;
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // The seeds themselves: the points the shape is made of.
      arm.values.forEach((value, seed) => {
        const offset = (seed - (arm.values.length - 1) / 2) * 7;
        ctx.fillStyle = arm.color;
        ctx.beginPath();
        ctx.arc(centre + offset, toY(value), 3, 0, Math.PI * 2);
        ctx.fill();
      });

      // The mean, across the arm.
      const mean = arm.values.reduce((sum, v) => sum + v, 0) / arm.values.length;
      ctx.strokeStyle = PALETTE.text_primary;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(centre - half, toY(mean));
      ctx.lineTo(centre + half, toY(mean));
      ctx.stroke();
    });

    ctx.restore();

    // The seeds a claim still needs, under each arm.
    arms.forEach((arm, index) => {
      const short = Math.max(0, required - arm.values.length);
      ctx.font = "11px 'JetBrains Mono', monospace";
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.fillStyle = PALETTE.text_secondary;
      ctx.fillText(
        `${arm.values.length} of ${required} seeds`,
        frame.band(index),
        frame.rect.y + frame.rect.height + 46,
      );
      if (short > 0) {
        ctx.fillStyle = PALETTE.warn;
        ctx.fillText(
          `${short} short`,
          frame.band(index),
          frame.rect.y + frame.rect.height + 62,
        );
      }
    });

    drawNote(
      ctx,
      area,
      `the white line is each arm's mean · a claim needs ${required} seeds per group`,
    );

    this.drawn = true;
  }
}
