/** Contrast stage view — the arms against one another, and the test (TODO72 P6). */

import { ARM_COLORS, PALETTE } from "../../../colors.js";
import { drawNote, drawRowFrame, type RowFrame } from "../../../stage/plot2d.js";
import { accountStore } from "../../../stores/account.js";
import { metricsStore } from "../../../stores/metrics.js"
import { workspaceStore } from "../../../stores/workspace.js";
import type { ContrastArm, ContrastPair } from "../../../stage/payloads.js";
import type {
  StageViewDefinition,
  StageViewInstance,
  StageViewContext,
  StageChange,
  Size,
} from "../../../layout/types.js";

/** Create a StageViewInstance for the "contrast" view. */
export function createContrastView(context: StageViewContext): StageViewInstance {
  const { flat, workspace, state } = context;

  // Per-instance state derived from state + workspace
  let runId = (state as any).runId ?? workspace.getSelectedRunId();
  let axes = (state as any).axes ?? workspace.getAxes();

  // Subscriptions
  let workspaceUnsub: (() => void) | null = null;
  let metricsUnsub: (() => void) | null = null;
  let accountUnsub: (() => void) | null = null;

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
        updateAccountSubscription();
        redraw();
      }
    });

    // Subscribe to metrics for this run
    if (runId) {
      metricsUnsub = metricsStore.subscribe(runId, () => {
        updateAccountSubscription();
        redraw();
      });
    }

    // Subscribe to account
    await updateAccountSubscription();

    visible = true;
    await redraw();
  }

  async function updateAccountSubscription(): Promise<void> {
    accountUnsub?.();
    if (!runId) return;

    const metrics = metricsStore.get(runId);
    const measured = metrics?.records?.length ?? 0;
    accountUnsub = accountStore.subscribe(runId, measured, () => {
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
    const account = runId ? accountStore.get(runId, measured) : null;
    const contrast = account?.contrast;

    if (!contrast || contrast.pairs.length === 0) {
      drawn = false;
      flat.clear();
      return;
    }

    const means = new Map<string, number>();
    const spreads = new Map<string, number>();
    contrast.arms.forEach((arm: ContrastArm) => {
      means.set(arm.value, arm.mean);
      spreads.set(arm.value, arm.sd);
    });
    const highest = Math.max(...contrast.arms.map((arm) => arm.mean), 0.001);

    const ctx = flat.begin();
    const area = flat.area();

    const frame = drawRowFrame(ctx, area, {
      xMin: 0,
      xMax: highest * 1.15,
      rows: contrast.pairs.map((pair: ContrastPair) => `${pair.a} vs ${pair.b}`),
      title: "The contrast",
      subtitle: `the ${contrast.axis} arms on ${contrast.metric}, and what separates them`,
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
      ctx.fillRect(Math.min(left, right), y - 11, Math.abs(right - left), 22);

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
        ? `the test ran: p=${test.p_value?.toFixed(4)} (alpha=${test.alpha})` +
            ` · dz=${test.cohens_dz?.toFixed(2)}` +
            ` · ${test.shared_cells} shared cells`
        : `no test ran: ${test.shared_cells} shared cell` +
            `${test.shared_cells === 1 ? "" : "s"}, ${test.required_cells} required`,
    );

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
    accountUnsub?.();
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

/** Register the contrast view definition. */
export const contrastViewDefinition: StageViewDefinition = {
  view: "contrast",
  title: "The contrast",
  key: "d",
  group: "the judgement",
  create: createContrastView,
};