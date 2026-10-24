/** The timeline — the run's stages, and the time each of them held it (TODO69).

    A run is a process before it is an evidence. This draws the process: one
    lane per stage, in the order the run reached it, and the marks on the
    clock the stage left. The stretch between the lanes is the time the run
    spent doing the work, and it is shaded and named: the pause is the
    biggest thing in the picture, and a picture that leaves it empty says
    the run did nothing.
*/

import { PALETTE } from "../colors.js";
import { stageCanvas } from "./canvas2d.js";
import { drawNote, drawRowFrame } from "./plot2d.js";
import { stageState } from "./store.js";
import type { StageSpan } from "./payloads.js";
import type { StageView, ViewGroup } from "./views.js";

export class TimelineView implements StageView {
  id = "timeline";
  name = "The timeline";
  group = "the process" as ViewGroup;
  caption =
    "The run's stages, in the order it reached them, and the time each held it.";
  key = "t";

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
    const timeline = stageState.timeline;
    const spans = timeline?.stages ?? [];
    if (!timeline || spans.length === 0) {
      this.drawn = false;
      return;
    }

    const ctx = stageCanvas.begin();
    const area = stageCanvas.area();
    const seconds = Math.max(timeline.seconds, 0.001);

    const frame = drawRowFrame(ctx, area, {
      xMin: 0,
      xMax: seconds,
      rows: spans.map((span: StageSpan) => span.action),
      title: "The timeline",
      subtitle: "the run's stages, and the time each of them held it",
      xLabel: "seconds",
    });

    const toX = (value: number): number =>
      frame.rect.x + (value / seconds) * frame.rect.width;

    // The events of each stage: the marks it left on the clock.
    const byStage = new Map<string, number[]>();
    timeline.events.forEach((event) => {
      const times = byStage.get(event.stage) ?? [];
      times.push(event.at - timeline.start);
      byStage.set(event.stage, times);
    });

    // The gap between one stage's last word and the next stage's first: the
    // run's shape, from one stage to the next. A stage that spoke twice —
    // in two rounds — is measured from the word that came first.
    const gaps = spans.slice(0, -1).map((span, index) => {
      const next = spans[index + 1];
      const mine = (byStage.get(span.stage) ?? []).filter(
        (at) => at <= next.offset,
      );
      const from = mine.length > 0 ? mine[mine.length - 1] : span.offset;
      return { index, from, to: next.offset, seconds: next.offset - from };
    });
    const longest = gaps.reduce(
      (widest, gap) => (gap.seconds > widest.seconds ? gap : widest),
      { index: -1, from: 0, to: 0, seconds: 0 },
    );

    // The silence, shaded: the time the run spent working rather than
    // talking. It is the biggest thing in the picture, so it is drawn first
    // and the marks are drawn over it.
    const silence = longest.seconds > 0.5 ? longest : null;
    if (silence) {
      const from = toX(silence.from);
      const to = toX(silence.to);
      ctx.fillStyle = `${PALETTE.warn}18`;
      ctx.fillRect(
        from,
        frame.rect.y,
        Math.max(2, to - from),
        frame.rect.height,
      );
    }

    // The connectors: the run's shape, from one stage to the next.
    gaps.forEach((gap) => {
      const isLongest = gap.index === longest.index;
      ctx.strokeStyle = isLongest ? PALETTE.warn : PALETTE.border;
      ctx.lineWidth = isLongest ? 2 : 1;
      ctx.beginPath();
      ctx.moveTo(toX(gap.from), frame.rowY(gap.index));
      ctx.lineTo(toX(gap.to), frame.rowY(gap.index + 1));
      ctx.stroke();
    });

    spans.forEach((span, index) => {
      const y = frame.rowY(index);

      // Its words, each one a mark on the clock.
      ctx.fillStyle = PALETTE.gradient;
      (byStage.get(span.stage) ?? []).forEach((at) => {
        const x = toX(at);
        ctx.fillRect(x - 1.5, y - 9, 3, 18);
      });

      ctx.font = "12px 'JetBrains Mono', monospace";
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      ctx.fillStyle = PALETTE.text_secondary;
      ctx.fillText(`${span.events}`, frame.rect.x + frame.rect.width + 12, y);
    });

    // The silence, named: the time between two stages that the run spent
    // working rather than talking.
    if (silence) {
      ctx.font = "13px 'JetBrains Mono', monospace";
      ctx.textAlign = "center";
      ctx.textBaseline = "alphabetic";
      ctx.fillStyle = PALETTE.warn;
      ctx.fillText(
        `${silence.seconds.toFixed(1)} s of silence`,
        (toX(silence.from) + toX(silence.to)) / 2,
        frame.rect.y + 22,
      );
    }

    drawNote(
      ctx,
      area,
      `${spans.length} stages · ${timeline.events.length} events · ` +
        `${seconds.toFixed(1)} s from the first word to the last`,
    );

    this.drawn = true;
  }
}
