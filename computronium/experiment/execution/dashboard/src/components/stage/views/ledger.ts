/** Ledger stage view — every arm the run measured, and where it stands (TODO72 P6). */

import { ARM_COLORS, PALETTE } from "../../../colors.js";
import { drawTitle, drawFrame, drawNote, wrapText, type PlotFrame } from "../../../stores/plot2d.js";
import { accountStore } from "../../../stores/account.js";
import { metricsStore } from "../../../stores/metrics.js";
import { workspaceStore } from "../../../stores/workspace.js";
import type {
  StageViewDefinition,
  StageViewInstance,
  StageViewContext,
  StageChange,
  Size,
} from "../../../layout/types.js";

const VERDICT_COLORS: Record<string, string> = {
  PASSED: PALETTE.passed,
  INSUFFICIENT: PALETTE.insufficient,
  REJECTED: PALETTE.rejected,
};

/** Create a StageViewInstance for the "ledger" view. */
export function createLedgerView(context: StageViewContext): StageViewInstance {
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
    // Subscribe to workspace changes (run selection, axes)
    workspaceUnsub = workspace.onChange(() => {
      const newRunId = workspace.getSelectedRunId();
      const newAxes = workspace.getAxes();
      if (newRunId !== runId || newAxes.x !== axes.x || newAxes.y !== axes.y || newAxes.z !== axes.z) {
        runId = newRunId;
        axes = newAxes;
        redraw();
      }
    });

    // Subscribe to metrics for this run (to get measured count)
    if (runId) {
      metricsUnsub = metricsStore.subscribe(runId, () => {
        redraw();
      });
    }

    // Subscribe to account for this run
    if (runId) {
      // We'll re-subscribe when measured count changes
      await updateAccountSubscription();
    }

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
    const ledger = account?.ledger;

    if (!ledger || ledger.claims.length === 0) {
      drawn = true;
      flat.clear();
      return;
    }

    const ctx = flat.begin();
    const area = flat.area();

    drawTitle(ctx, area, "The ledger", "every arm the run measured, its evidence, and the gate's standing on it");

    let y = area.y + 96;
    drawStandingBar(ctx, area, ledger.standings, ledger.claims.length);
    y += 66;

    // The arms: what each one measured, and what the gate made of it.
    ledger.claims.forEach((arm: any) => {
      const color = ARM_COLORS[arm.value] ?? PALETTE.gradient;
      ctx.font = "14px 'JetBrains Mono', monospace";
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      ctx.fillStyle = color;
      ctx.fillText(`${arm.axis} = ${arm.value}`, area.x, y);

      ctx.font = "13px 'JetBrains Mono', monospace";
      ctx.fillStyle = PALETTE.text_primary;
      ctx.fillText(`${arm.mean.toFixed(3)} ± ${arm.sd.toFixed(3)}`, area.x + 300, y);

      ctx.font = "12px 'JetBrains Mono', monospace";
      ctx.fillStyle = PALETTE.text_secondary;
      ctx.fillText(`${arm.n} seeds · ${arm.cells} cell${arm.cells === 1 ? "" : "s"}`, area.x + 460, y);

      drawChip(ctx, area.x + 640, y, arm.verdict);
      y += 42;
    });

    // What was held fixed: the axes the run did not vary.
    if (ledger.fixed.length > 0) {
      y += 22;
      ctx.font = "600 14px 'JetBrains Mono', monospace";
      ctx.textAlign = "left";
      ctx.textBaseline = "alphabetic";
      ctx.fillStyle = PALETTE.text_primary;
      ctx.fillText("What was held fixed", area.x, y);
      y += 24;

      ctx.font = "12px 'JetBrains Mono', monospace";
      ledger.fixed.forEach((axis: any) => {
        ctx.textAlign = "left";
        ctx.textBaseline = "middle";
        ctx.fillStyle = PALETTE.text_secondary;
        ctx.fillText(`${axis.axis} = ${axis.value}`, area.x, y);
        ctx.fillText(`${axis.mean.toFixed(3)}`, area.x + 300, y);
        ctx.fillText(`${axis.n} measurements · ${axis.cells} cells`, area.x + 460, y);
        y += 26;
      });
    }

    // What holds the claims back: the report's own limitations.
    y += 22;
    ctx.font = "600 14px 'JetBrains Mono', monospace";
    ctx.textAlign = "left";
    ctx.textBaseline = "alphabetic";
    ctx.fillStyle = PALETTE.text_primary;
    ctx.fillText("What holds it back", area.x, y);
    y += 24;

    ctx.font = "13px 'JetBrains Mono', monospace";
    ledger.limitations.forEach((limitation: any) => {
      wrapText(ctx, `· ${limitation.detail}`, area.width).forEach((line) => {
        ctx.fillStyle = PALETTE.text_secondary;
        ctx.fillText(line, area.x, y);
        y += 20;
      });
    });

    if (ledger.significance) {
      y += 14;
      wrapText(ctx, `the report's test — ${ledger.significance}`, area.width).forEach((line) => {
        ctx.fillStyle = PALETTE.text_secondary;
        ctx.fillText(line, area.x, y);
        y += 20;
      });
    }

    drawNote(ctx, area, `a claim needs ${ledger.min_seeds} seeds per cell` + (ledger.chance !== null ? ` · the chance level is ${ledger.chance.toFixed(3)}` : ""));

    drawn = true;
  }

  function drawStandingBar(
    ctx: CanvasRenderingContext2D,
    area: { x: number; y: number; width: number; height: number },
    standings: Record<string, number>,
    arms: number,
  ): void {
    const total = Object.values(standings).reduce((sum, count) => sum + count, 0);
    if (total === 0) return;

    const height = 18;
    const width = Math.min(560, area.width * 0.55);
    const y = area.y + 96; // Add y position
    let cursor = area.x;
    Object.entries(standings).forEach(([verdict, count]) => {
      if (count <= 0) return;
      const segment = (count / total) * width;
      ctx.fillStyle = VERDICT_COLORS[verdict] ?? PALETTE.text_secondary;
      ctx.fillRect(cursor, y, Math.max(2, segment - 2), height);
      if (segment > 52) {
        ctx.fillStyle = PALETTE.bg;
        ctx.font = "11px 'JetBrains Mono', monospace";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(`${count}`, cursor + (segment - 2) / 2, y + height / 2);
      }
      cursor += segment;
    });

    ctx.font = "12px 'JetBrains Mono', monospace";
    ctx.textAlign = "left";
    ctx.textBaseline = "alphabetic";
    ctx.fillStyle = PALETTE.text_secondary;
    ctx.fillText(`${arms} arm${arms === 1 ? "" : "s"}, and where each one stands`, area.x, y - 10);
  }

  function drawChip(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    text: string,
  ): void {
    const color = VERDICT_COLORS[text] ?? PALETTE.text_secondary;
    ctx.font = "11px 'JetBrains Mono', monospace";
    const width = ctx.measureText(text).width + 18;
    ctx.fillStyle = `${color}22`;
    ctx.strokeStyle = `${color}88`;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(x, y - 9, width, 18, 9);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = color;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(text, x + width / 2, y);
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

/** Register the ledger view definition. */
export const ledgerViewDefinition: StageViewDefinition = {
  view: "ledger",
  title: "The ledger",
  key: "l",
  group: "the judgement",
  create: createLedgerView,
};