/** Run selection compatibility layer using WorkspaceStore and MetricsStore. */

import { workspaceStore } from "./stores/workspace.js";
import { metricsStore } from "./stores/metrics.js";
import type { RunMetrics as MetricsRunMetrics } from "./stores/metrics.js";

export interface RunSummary {
  run_id?: string;
  profile?: string;
  tasks?: string[];
  fidelity?: string;
  mode?: string;
  started_at?: string;
}

export type RunMetrics = MetricsRunMetrics;

/** The statistical gate's thresholds, as the server holds them. */
export interface GateThresholds {
  superiority_margin: number;
  superiority_margin_sigma: number;
  ci_width_threshold: number;
  train_val_gap_threshold: number;
  rho_band: number[];
  min_seeds_for_stats: number;
  power_target: number;
  alpha: number;
  effect_size_target: number;
  required_seeds_per_group: number;
  use_confirmation_seeds_for_l2: boolean;
}

export type RunListener = (
  runId: string | null,
  metrics: RunMetrics | null,
) => void;

class RunSelection {
  private listeners: RunListener[] = [];
  private chosenByReader = false;

  get selectedId(): string | null {
    return workspaceStore.getSelectedRunId();
  }

  get selected(): RunMetrics | null {
    const runId = this.selectedId;
    if (!runId) return null;
    return metricsStore.get(runId) ?? null;
  }

  /** The reader chose the run the dashboard shows. */
  select(runId: string | null): void {
    workspaceStore.selectRun(runId);
  }

  /** Observe metrics for a run (for backward compatibility with MetricsStore). */
  observe(runId: string, metrics: RunMetrics): void {
    metricsStore.setMetrics(runId, metrics);
    if (!this.chosenByReader) {
      workspaceStore.selectRun(runId);
    }
    this.notify();
  }

  /** Get metrics for a specific run ID. */
  getMetrics(runId: string): RunMetrics | null {
    return metricsStore.get(runId) ?? null;
  }

  /** Every run the dashboard has heard about, with its metrics. */
  get runs(): [string, RunMetrics][] {
    const summary = metricsStore.getRunsSummary?.() ?? [];
    return summary.map((r: any) => [r.run_id, metricsStore.get(r.run_id)]).filter(([, m]) => m != null) as [string, RunMetrics][];
  }

  onChange(listener: RunListener): () => void {
    this.listeners.push(listener);
    const unsubWorkspace = workspaceStore.onSelectionChange(() => this.notify());
    const unsubMetrics = metricsStore.subscribe(this.selectedId ?? "", () => this.notify());
    return () => {
      const idx = this.listeners.indexOf(listener);
      if (idx >= 0) this.listeners.splice(idx, 1);
      unsubWorkspace();
      unsubMetrics();
    };
  }

  private notify(): void {
    const runId = this.selectedId;
    const metrics = this.selected;
    this.listeners.forEach((listener) => listener(runId, metrics));
  }
}

export const runSelection = new RunSelection();