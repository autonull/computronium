/** The convergence — accuracy against epoch (TODO69 Phase 5).

    The picture of the run as a process rather than as evidence: every arm's
    curve, the chance level under them, and the epoch in which they part.
    The curves are already in the records, so this view needs nothing the
    dashboard does not have.
*/

import { ARM_COLORS, PALETTE } from "../colors.js";
import { stageCanvas } from "./canvas2d.js";
import { drawFrame, drawNote, scaleX, scaleY } from "./plot2d.js";
import { registerView } from "./registry.js";
import { stageState } from "./store.js";
import type { StageView, ViewGroup } from "./views.js";

interface ArmCurve {
  arm: string;
  points: { epoch: number; val_acc: number }[];
}

export class ConvergenceView implements StageView {
  id = "convergence";
  name = "Convergence";
  group = "the run" as ViewGroup;
  caption =
    "Accuracy against epoch, one curve per arm, with the chance level under them.";

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

  /** One curve per arm: the mean accuracy of that arm, epoch by epoch. */
  private curves(): ArmCurve[] {
    const records = stageState.metrics?.records ?? [];
    const byArm = new Map<string, Map<number, number[]>>();

    records.forEach((record: any) => {
      const curve = record?.payload?.convergence_curve;
      if (!Array.isArray(curve) || curve.length === 0) return;
      const arm = record?.coordinate?.credit ?? "";
      const epochs = byArm.get(arm) ?? new Map<number, number[]>();
      curve.forEach((point: any) => {
        if (typeof point?.epoch !== "number") return;
        if (typeof point?.val_acc !== "number") return;
        const values = epochs.get(point.epoch) ?? [];
        values.push(point.val_acc);
        epochs.set(point.epoch, values);
      });
      byArm.set(arm, epochs);
    });

    return Array.from(byArm.entries()).map(([arm, epochs]) => ({
      arm,
      points: Array.from(epochs.entries())
        .sort((a, b) => a[0] - b[0])
        .map(([epoch, values]) => ({
          epoch,
          val_acc: values.reduce((sum, v) => sum + v, 0) / values.length,
        })),
    }));
  }

  private draw(): void {
    const curves = this.curves();
    if (curves.length === 0) {
      this.drawn = false;
      return;
    }

    const ctx = stageCanvas.begin();
    const area = stageCanvas.area();
    const chance = stageState.chance;

    const maxEpoch = Math.max(
      ...curves.flatMap((curve) => curve.points.map((point) => point.epoch)),
    );
    const maxAccuracy = Math.max(
      chance,
      ...curves.flatMap((curve) => curve.points.map((point) => point.val_acc)),
    );

    const frame = drawFrame(ctx, area, {
      xMin: 0,
      xMax: maxEpoch,
      yMin: 0,
      yMax: maxAccuracy,
      xLabel: "epoch",
      yLabel: "accuracy",
      title: "Convergence",
      subtitle: "the mean accuracy of each arm, epoch by epoch",
      xTicks: undefined,
      yTicks: undefined,
    });

    // The chance level: what every curve is measured against.
    const chanceY = scaleY(chance, frame);
    ctx.strokeStyle = PALETTE.chance_line;
    ctx.lineWidth = 1.5;
    ctx.setLineDash([6, 5]);
    ctx.beginPath();
    ctx.moveTo(frame.rect.x, chanceY);
    ctx.lineTo(frame.rect.x + frame.rect.width, chanceY);
    ctx.stroke();
    ctx.setLineDash([]);

    curves.forEach((curve) => {
      const color = ARM_COLORS[curve.arm] || PALETTE.gradient;
      ctx.strokeStyle = color;
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      curve.points.forEach((point, index) => {
        const x = scaleX(point.epoch, frame);
        const y = scaleY(point.val_acc, frame);
        if (index === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();

      curve.points.forEach((point) => {
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(
          scaleX(point.epoch, frame),
          scaleY(point.val_acc, frame),
          3,
          0,
          Math.PI * 2,
        );
        ctx.fill();
      });
    });

    // The arms, named.
    ctx.font = "12px 'JetBrains Mono', monospace";
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    let legendY = frame.rect.y + 10;
    curves.forEach((curve) => {
      const color = ARM_COLORS[curve.arm] || PALETTE.gradient;
      ctx.fillStyle = color;
      ctx.fillRect(frame.rect.x + frame.rect.width + 18, legendY - 5, 10, 10);
      ctx.fillStyle = PALETTE.text_secondary;
      ctx.fillText(curve.arm, frame.rect.x + frame.rect.width + 34, legendY);
      legendY += 20;
    });

    drawNote(
      ctx,
      area,
      `${curves.length} arms · the dashed line is the chance level (${chance.toFixed(2)})`,
    );

    this.drawn = true;
  }
}

registerView(new ConvergenceView());
