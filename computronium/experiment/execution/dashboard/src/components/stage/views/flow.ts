/** Flow stage view — the run's cells, from the space to the evidence (TODO72 P6). */

import { PALETTE } from "../../../colors.js";
import { drawNote, drawTitle, wrapText } from "../../../stage/plot2d.js";
import { timelineStore } from "../../../stores/timeline.js";
import { spaceStore } from "../../../stores/space.js";
import { workspaceStore } from "../../../stores/workspace.js";
import type { AxisSelection } from "../../../stage/payloads.js";
import type { FlowStage } from "../../../stage/payloads.js";
import type {
  StageViewDefinition,
  StageViewInstance,
  StageViewContext,
  StageChange,
  Size,
} from "../../../layout/types.js";

/** The space between the title and the columns. */
const TOP = 84;

/** The room the stage labels take under the columns. */
const LABEL_ROOM = 92;

/** Create a StageViewInstance for the "flow" view. */
export function createFlowView(context: StageViewContext): StageViewInstance {
  const { flat, workspace, state } = context;

  // Per-instance state derived from state + workspace
  let runId = (state as any).runId ?? workspace.getSelectedRunId();
  let axes = (state as any).axes ?? workspace.getAxes();

  // Subscriptions
  let workspaceUnsub: (() => void) | null = null;
  let flowUnsub: (() => void) | null = null;
  let spaceUnsub: (() => void) | null = null;

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
        updateFlowSubscription();
        updateSpaceSubscription();
        redraw();
      }
    });

    // Subscribe to flow for this run
    await updateFlowSubscription();

    // Subscribe to space for this run+axes (for void rules)
    await updateSpaceSubscription();

    visible = true;
    await redraw();
  }

  async function updateFlowSubscription(): Promise<void> {
    flowUnsub?.();
    if (!runId) return;

    // We need the timeline to know event count for flow
    const timeline = timelineStore.getTimeline(runId);
    const events = timeline?.events.length ?? 0;
    flowUnsub = timelineStore.subscribeFlow(runId, events, () => {
      redraw();
    });
  }

  async function updateSpaceSubscription(): Promise<void> {
    spaceUnsub?.();
    if (!runId) return;

    const spaceValues: Record<AxisSelection["x"], string[]> = {
      credit: [],
      geometry: [],
      dynamics: [],
      substrate: [],
      plasticity: [],
      update: [],
    };
    spaceUnsub = spaceStore.subscribe(runId, axes, spaceValues, () => {
      redraw();
    });
  }

  function redraw(): void {
    if (!visible) return;
    draw();
  }

  function draw(): void {
    const flow = runId ? timelineStore.getFlow(runId, 0) : null; // events count not used for get
    const stages = flow?.stages ?? [];
    if (!flow || stages.length === 0) {
      drawn = false;
      flat.clear();
      return;
    }

    const ctx = flat.begin();
    const area = flat.area();

    drawTitle(ctx, area, "The flow", "the run's cells, from the space to the evidence");

    const bottom = area.y + area.height - LABEL_ROOM;
    const height = Math.max(120, bottom - (area.y + TOP));
    const largest = Math.max(1, ...stages.map((stage: FlowStage) => stage.count + stage.refused));
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
      ctx.fillStyle = stage.kind === "records" ? PALETTE.measured : PALETTE.gradient;
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
      ctx.fillStyle = stage.count > 0 ? PALETTE.text_secondary : PALETTE.text_muted;
      wrapText(ctx, stage.action, band - 8).slice(0, 2).forEach((line: string, lineIndex: number) => {
        ctx.fillText(line, centre, bottom + 10 + lineIndex * 16);
      });
    });

    drawRefusals(ctx, area);
    drawNote(ctx, area, flow.summary);
    drawn = true;
  }

  function drawRefusals(
    ctx: CanvasRenderingContext2D,
    area: { x: number; y: number; width: number; height: number },
  ): void {
    const space = runId ? spaceStore.get(runId, axes, {
      credit: [],
      geometry: [],
      dynamics: [],
      substrate: [],
      plasticity: [],
      update: [],
    }) : null;
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
    flowUnsub?.();
    spaceUnsub?.();
  }

  // Initialize
  init();

  return {
    mount,
    resize,
    refresh,
    ready,
    dispose,
  };
}

/** Register the flow view definition. */
export const flowViewDefinition: StageViewDefinition = {
  view: "flow",
  title: "The flow",
  key: "f",
  group: "the process",
  create: createFlowView,
};