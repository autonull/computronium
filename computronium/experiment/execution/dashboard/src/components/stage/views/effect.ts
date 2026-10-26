/** Effect stage view — which axis moved the objective (TODO72 P6). */

import { ARM_COLORS, PALETTE } from "../../../colors.js";
import { drawCategoryFrame, drawNote, type CategoryFrame } from "../../../stores/plot2d.js";
import { attributionStore } from "../../../stores/attribution.js";
import { metricsStore } from "../../../stores/metrics.js";
import { workspaceStore } from "../../../stores/workspace.js";
import type { AttributionArm, AttributionAxis } from "../../../stores/payloads.js";
import type {
  StageViewDefinition,
  StageViewInstance,
  StageViewContext,
  StageChange,
  Size,
} from "../../../layout/types.js";

/** Create a StageViewInstance for the "effect" view. */
export function createEffectView(context: StageViewContext): StageViewInstance {
  const { flat, workspace, state } = context;

  // Per-instance state derived from state + workspace
  let runId = (state as any).runId ?? workspace.getSelectedRunId();
  let axes = (state as any).axes ?? workspace.getAxes();

  // Subscriptions
  let workspaceUnsub: (() => void) | null = null;
  let metricsUnsub: (() => void) | null = null;
  let attributionUnsub: (() => void) | null = null;

  // View state
  let drawn = false;
  let visible = false;

  async function init(): Promise<void> {
    // Subscribe to workspace changes
    workspaceUnsub = workspace.onChange(() => {
      const newRunId = workspace.getSelectedRunId();
      const newAxes = workspace.getAxes();
      if (newRunId !== runId || newAxes.x !== axes.x || newAxes.y !== axes.y || newAxes.z !== axes.z) {
        runId = newRunId;
        axes = newAxes;
        updateAttributionSubscription();
        redraw();
      }
    });

    // Subscribe to metrics for this run
    if (runId) {
      metricsUnsub = metricsStore.subscribe(runId, () => {
        updateAttributionSubscription();
        redraw();
      });
    }

    // Subscribe to attribution
    await updateAttributionSubscription();

    visible = true;
    await redraw();
  }

  async function updateAttributionSubscription(): Promise<void> {
    attributionUnsub?.();
    if (!runId) return;

    const metrics = metricsStore.get(runId);
    const measured = metrics?.records?.length ?? 0;
    attributionUnsub = attributionStore.subscribe(runId, measured, () => {
      redraw();
    });
  }

  function redraw(): void {
    if (!visible) return;
    draw();
  }

  function draw(): void {
    const metrics = runId ? metricsStore.get(runId) : null;
    const measured = metrics?.records?.length ?? 0;
    const attribution = runId ? attributionStore.get(runId, measured) : null;
    const attrAxes = attribution?.axes ?? [];

    if (!attribution || attrAxes.length === 0) {
      drawn = false;
      flat.clear();
      return;
    }

    const ctx = flat.begin();
    const area = flat.area();

    const means = attrAxes.flatMap((axis: AttributionAxis) =>
      axis.values.map((arm: AttributionArm) => arm.mean),
    );
    const highest = Math.max(...means, 0.1);

    const frame = drawCategoryFrame(ctx, area, {
      yMin: 0,
      yMax: highest * 1.15,
      categories: attrAxes.map((axis: AttributionAxis) => axis.axis),
      title: "The effect",
      subtitle: attribution.summary,
      yLabel: attribution.metric || "the objective",
    });

    const toY = (value: number): number =>
      frame.rect.y +
      frame.rect.height -
      (value / (frame.yMax || 1)) * frame.rect.height;

    attrAxes.forEach((axis: AttributionAxis, index: number) => {
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

          // The name, beside the arm it names.
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
    drawn = true;
  }

  // Mount
  function mount(): void {
    // No event listeners needed
  }

  // Resize
  function resize(size: Size): void {
    flat.resize(size);
    if (visible) draw();
  }

  // Refresh
  function refresh(change: StageChange): void {
    if (change.kind === "data" || change.kind === "resize") {
      redraw();
    }
  }

  function ready(): boolean {
    return drawn;
  }

  // Dispose
  function dispose(): void {
    workspaceUnsub?.();
    metricsUnsub?.();
    attributionUnsub?.();
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

/** Register the effect view definition. */
export const effectViewDefinition: StageViewDefinition = {
  view: "effect",
  title: "The effect",
  key: "shift+e",
  group: "the process",
  create: createEffectView,
};