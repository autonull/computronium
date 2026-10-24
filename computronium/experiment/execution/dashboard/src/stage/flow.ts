/** The flow — the run's cells, from the space to the evidence (TODO69).

    A run is a process before it is an evidence. This draws the process: one
    column per stage, in the order the run reached it, and the count of what
    each stage handled. The cells the run carried are blue, the records it
    wrote are gold, and what the gate refused is drawn in the void colour on
    top of the stage that refused it.

    The counts are the run's own: the events the dashboard watched, read by
    the server. The rules that refuse a cell are the system's own, read from
    the declared space.
*/

import { PALETTE } from "../colors.js";
import { stageCanvas } from "./canvas2d.js";
import { drawNote, drawTitle, wrapText } from "./plot2d.js";
import { stageState, type FlowStage } from "./state.js";
import type { StageView, ViewGroup } from "./views.js";

/** The space between the title and the columns. */
const TOP = 84;

/** The room the stage labels take under the columns. */
const LABEL_ROOM = 92;

export class FlowView implements StageView {
  id = "flow";
  name = "The flow";
  group = "process" as ViewGroup;
  caption =
    "The run's cells, stage by stage: what each one handled, and what the gate refused.";
  key = "f";

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
    const flow = stageState.flow;
    const stages = flow?.stages ?? [];
    if (!flow || stages.length === 0) {
      this.drawn = false;
      return;
    }

    const ctx = stageCanvas.begin();
    const area = stageCanvas.area();

    drawTitle(
      ctx,
      area,
      "The flow",
      "the run's cells, from the space to the evidence",
    );

    const bottom = area.y + area.height - LABEL_ROOM;
    const height = Math.max(120, bottom - (area.y + TOP));
    const largest = Math.max(
      1,
      ...stages.map((stage: FlowStage) => stage.count + stage.refused),
    );
    const band = area.width / stages.length;

    // The baseline: the run's own line, and the count it is read against.
    ctx.strokeStyle = PALETTE.border;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(area.x, bottom + 0.5);
    ctx.lineTo(area.x + area.width, bottom + 0.5);
    ctx.stroke();

    stages.forEach((stage: FlowStage, index: number) => {
      const centre = area.x + band * (index + 0.5);
      const width = band * 0.56;
      const heightOf = (count: number): number => (count / largest) * height;

      // What the stage handled: the cells it carried, or the records it wrote.
      const carried = heightOf(stage.count);
      const top = bottom - carried;
      ctx.fillStyle =
        stage.kind === "records" ? PALETTE.measured : PALETTE.gradient;
      ctx.fillRect(centre - width / 2, top, width, Math.max(carried, 2));

      // What the gate refused: drawn on top of the stage that refused it.
      if (stage.refused > 0) {
        const refused = heightOf(stage.refused);
        ctx.fillStyle = PALETTE.void;
        ctx.fillRect(centre - width / 2, top - refused, width, refused);
        ctx.font = "12px 'JetBrains Mono', monospace";
        ctx.textAlign = "center";
        ctx.textBaseline = "bottom";
        ctx.fillStyle = PALETTE.void;
        ctx.fillText(`${stage.refused} refused`, centre, top - refused - 6);
      }

      // The count the stage handled.
      if (stage.count > 0) {
        ctx.font = "600 15px 'JetBrains Mono', monospace";
        ctx.textAlign = "center";
        ctx.textBaseline = "bottom";
        ctx.fillStyle = PALETTE.text_primary;
        ctx.fillText(`${stage.count}`, centre, top - 6);
      }

      // The stage's own name: what it did, in the pipeline's own words.
      ctx.font = "12px 'JetBrains Mono', monospace";
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.fillStyle =
        stage.count > 0 ? PALETTE.text_secondary : PALETTE.text_muted;
      wrapText(ctx, stage.action, band - 8)
        .slice(0, 2)
        .forEach((line: string, lineIndex: number) => {
          ctx.fillText(line, centre, bottom + 10 + lineIndex * 16);
        });
    });

    this.drawRefusals(ctx, area);
    drawNote(ctx, area, flow.summary);
    this.drawn = true;
  }

  /** The rules that refuse a cell, in the slice the reader is looking at. */
  private drawRefusals(
    ctx: CanvasRenderingContext2D,
    area: { x: number; y: number; width: number; height: number },
  ): void {
    const space = stageState.space;
    const rules = space?.void_rules ?? {};
    const names = Object.keys(rules);
    const x = area.x;

    ctx.textAlign = "left";
    ctx.textBaseline = "alphabetic";
    ctx.font = "600 13px 'JetBrains Mono', monospace";
    ctx.fillStyle = PALETTE.text_secondary;
    ctx.fillText("the rules that refuse", x, area.y + 80);

    if (names.length === 0) {
      ctx.font = "12px 'JetBrains Mono', monospace";
      ctx.fillStyle = PALETTE.text_muted;
      ctx.fillText("no cell of this slice is refused", x, area.y + 102);
      return;
    }

    ctx.font = "12px 'JetBrains Mono', monospace";
    names.slice(0, 6).forEach((rule: string, index: number) => {
      const y = area.y + 102 + index * 18;
      ctx.fillStyle = PALETTE.void;
      ctx.fillText(rule, x, y);
      ctx.fillStyle = PALETTE.text_secondary;
      ctx.textAlign = "right";
      ctx.fillText(`${rules[rule]} cells`, x + 280, y);
      ctx.textAlign = "left";
    });
  }
}
