/** Spread stage view — one violin per arm, across its seeds (TODO72 P6). */

import { ARM_COLORS, PALETTE } from "../../../colors.js";
import { drawCategoryFrame, drawNote, type CategoryFrame } from "../../../stage/plot2d.js";
import { metricsStore } from "../../../stores/metrics.js";
import { workspaceStore } from "../../../stores/workspace.js";
import type {
  StageViewDefinition,
  StageViewInstance,
  StageViewContext,
  StageChange,
  Size,
} from "../../../layout/types.js";

interface Arm {
  name: string;
  values: number[];
  color: string;
}

/** The density of the values at a point, by a Gaussian kernel. */
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

/** Create a StageViewInstance for the "spread" view. */
export function createSpreadView(context: StageViewContext): StageViewInstance {
  const { flat, workspace, state } = context;

  // Per-instance state derived from state + workspace
  let runId = (state as any).runId ?? workspace.getSelectedRunId();
  let axes = (state as any).axes ?? workspace.getAxes();

  // Subscriptions
  let workspaceUnsub: (() => void) | null = null;
  let metricsUnsub: (() => void) | null = null;

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
        redraw();
      }
    });

    // Subscribe to metrics for this run
    if (runId) {
      metricsUnsub = metricsStore.subscribe(runId, () => {
        redraw();
      });
    }

    visible = true;
    await redraw();
  }

  function redraw(): void {
    if (!visible) return;
    draw();
  }

  function draw(): void {
    const arms = computeArms();
    if (arms.length === 0) {
      drawn = false;
      flat.clear();
      return;
    }

    const ctx = flat.begin();
    const area = flat.area();
    const metrics = runId ? metricsStore.get(runId) : null;
    const chance = metrics?.chance ?? 0.1;
    const required = metrics?.required_seeds ?? 0;

    // The shape of an arm reaches past its own values: the kernel is wider
    // than the data, so the frame has to hold what the violin draws.
    const extents = arms.map((arm) => {
      const h = bandwidth(arm.values);
      return {
        high: arm.values[arm.values.length - 1] + 1.5 * h,
        low: arm.values[0] - 1.5 * h,
      };
    });
    const yMax = Math.max(chance, ...extents.map((extent) => extent.high)) * 1.03;

    const frame = drawCategoryFrame(ctx, area, {
      yMin: 0,
      yMax,
      categories: arms.map((arm) => arm.name),
      title: "The spread",
      subtitle: "every seed of every arm, as a distribution",
      yLabel: "accuracy",
    });

    // The chance level: what every arm is measured against.
    const chanceY =
      frame.rect.y + frame.rect.height * (1 - chance / frame.yMax);
    ctx.strokeStyle = PALETTE.chance_line;
    ctx.lineWidth = 1.5;
    ctx.setLineDash([6, 5]);
    ctx.beginPath();
    ctx.moveTo(frame.rect.x, chanceY);
    ctx.lineTo(frame.rect.x + frame.rect.width, chanceY);
    ctx.stroke();
    ctx.setLineDash([]);

    // The violins are drawn inside the frame.
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

    drawn = true;
  }

  function computeArms(): Arm[] {
    const metrics = runId ? metricsStore.get(runId) : null;
    const records = metrics?.records ?? [];
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

/** Register the spread view definition. */
export const spreadViewDefinition: StageViewDefinition = {
  view: "spread",
  title: "The spread",
  key: "s",
  group: "the evidence",
  create: createSpreadView,
};