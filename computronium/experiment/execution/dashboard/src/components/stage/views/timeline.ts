/** Timeline stage view — the run's stages, and the time each of them held it (TODO72 P6). */

import { PALETTE } from "../../../colors.js";
import { drawNote, drawRowFrame, type RowFrame } from "../../../stores/plot2d.js";
import { metricsStore } from "../../../stores/metrics.js";
import { timelineStore } from "../../../stores/timeline.js";
import { workspaceStore } from "../../../stores/workspace.js";
import type { StageSpan } from "../../../stores/payloads.js";
import type {
  StageViewDefinition,
  StageViewInstance,
  StageViewContext,
  StageChange,
  Size,
} from "../../../layout/types.js";

/** Create a StageViewInstance for the "timeline" view. */
export function createTimelineView(context: StageViewContext): StageViewInstance {
  const { flat, workspace, state } = context;

  // Per-instance state derived from state + workspace
  let runId = (state as any).runId ?? workspace.getSelectedRunId();
  let axes = (state as any).axes ?? workspace.getAxes();

  // Subscriptions
  let workspaceUnsub: (() => void) | null = null;
  let metricsUnsub: (() => void) | null = null;
  let timelineUnsub: (() => void) | null = null;
  let flowUnsub: (() => void) | null = null;

  // View state
  let drawn = false;
  let visible = false;

  async function init(): Promise<void> {
    // Subscribe to workspace changes (run selection, axes)
    workspaceUnsub = workspace.onChange(() => {
      const newRunId = workspace.getSelectedRunId();
      const newAxes = workspace.getAxes();
      if (newRunId !== runId || newAxes.x !== axes.x || newAxes.y !== axes.y || newAxes.z !== axes.z) {
        runId = newRunId;
        axes = newAxes;
        updateSubscriptions();
        redraw();
      }
    });

    // Subscribe to metrics for this run (to get measured count for timeline)
    if (runId) {
      metricsUnsub = metricsStore.subscribe(runId, () => {
        updateSubscriptions();
        redraw();
      });
    }

    // Subscribe to timeline and flow
    await updateSubscriptions();

    visible = true;
    await redraw();
  }

  async function updateSubscriptions(): Promise<void> {
    timelineUnsub?.();
    flowUnsub?.();
    if (!runId) return;

    timelineUnsub = timelineStore.subscribeTimeline(runId, () => {
      // When timeline updates, also update flow subscription
      updateFlowSubscription();
      redraw();
    });

    // Also fetch timeline to trigger flow subscription
    const timeline = timelineStore.getTimeline(runId);
    if (timeline) {
      updateFlowSubscription(timeline.events.length);
    }
  }

  function updateFlowSubscription(events?: number): void {
    flowUnsub?.();
    if (!runId) return;

    const timeline = timelineStore.getTimeline(runId);
    const eventCount = events ?? timeline?.events.length ?? 0;
    flowUnsub = timelineStore.subscribeFlow(runId, eventCount, () => {
      redraw();
    });
  }

  function redraw(): void {
    if (!visible) return;
    draw();
  }

  function draw(): void {
    const timeline = runId ? timelineStore.getTimeline(runId) : null;
    const spans = timeline?.stages ?? [];
    if (!timeline || spans.length === 0) {
      drawn = false;
      flat.clear();
      return;
    }

    const ctx = flat.begin();
    const area = flat.area();
    const seconds = Math.max(timeline.seconds, 0.001);

    const frame = drawRowFrame(ctx, area, {
      xMin: 0,
      xMax: seconds,
      rows: spans.map((span: StageSpan) => span.action),
      title: "The timeline",
      subtitle: "the run's stages, in the order it reached them, and the time each held it",
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

    // The gap between one stage's last word and the next stage's first.
    const gaps = spans.slice(0, -1).map((span, index) => {
      const next = spans[index + 1];
      const mine = (byStage.get(span.stage) ?? []).filter((at) => at <= next.offset);
      const from = mine.length > 0 ? mine[mine.length - 1] : span.offset;
      return { index, from, to: next.offset, seconds: next.offset - from };
    });
    const longest = gaps.reduce(
      (widest, gap) => (gap.seconds > widest.seconds ? gap : widest),
      { index: -1, from: 0, to: 0, seconds: 0 },
    );

    // The silence, shaded: the time the run spent working rather than talking.
    const silence = longest.seconds > 0.5 ? longest : null;
    if (silence) {
      const from = toX(silence.from);
      const to = toX(silence.to);
      ctx.fillStyle = `${PALETTE.warn}18`;
      ctx.fillRect(from, frame.rect.y, Math.max(2, to - from), frame.rect.height);
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

    // The silence, named.
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
      `${spans.length} stages · ${timeline.events.length} events · ` + `${seconds.toFixed(1)} s from the first word to the last`,
    );

    drawn = true;
  }

  // Mount: attach event listeners if needed
  function mount(): void {
    // No event listeners needed for 2D view
  }

  // Resize: update canvas size
  function resize(size: Size): void {
    flat.resize(size);
    if (visible) draw();
  }

  // Refresh: handle data/view/resize changes
  function refresh(change: StageChange): void {
    if (change.kind === "data" || change.kind === "resize") {
      redraw();
    }
  }

  function ready(): boolean {
    return drawn;
  }

  // Dispose: clean up everything
  function dispose(): void {
    workspaceUnsub?.();
    metricsUnsub?.();
    timelineUnsub?.();
    flowUnsub?.();
  }

  // Initialize
  init();

  return {
    init,
    mount,
    resize,
    refresh,
    ready,
    dispose,
  };
}

/** Register the timeline view definition. */
export const timelineViewDefinition: StageViewDefinition = {
  view: "timeline",
  title: "The timeline",
  key: "t",
  group: "the process",
  create: createTimelineView,
};