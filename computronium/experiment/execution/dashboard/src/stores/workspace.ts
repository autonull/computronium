/** WorkspaceStore — shared workspace state (TODO72 P4).

Holds the run catalog, selected run, default axes, and cell selection.
Components subscribe to the parts they need.
*/

import { metricsStore } from "./metrics.js";
import type { AxisSelection } from "../layout/types.js";
import type { WorkspaceStore as WorkspaceStoreInterface } from "../layout/types.js";

export interface RunSummary {
  run_id: string;
  status: string;
  record_count: number;
  started_at: string | null;
  profile: string | null;
  task: string | null;
  fidelity: string | null;
}

export interface WorkspaceState {
  runs: RunSummary[];
  selectedRunId: string | null;
  axes: AxisSelection;
  cellSelection: string | null; // cell key
}

type Listener = () => void;

export class WorkspaceStore implements WorkspaceStoreInterface {
  private state: WorkspaceState = {
    runs: [],
    selectedRunId: null,
    axes: { x: "credit", y: "geometry", z: "dynamics" },
    cellSelection: null,
  };
  private listeners = new Set<Listener>();
  private runsSummaryUnsubscribe: (() => void) | null = null;

  get selectedRunId(): string | null {
    return this.state.selectedRunId;
  }

  get axes(): AxisSelection {
    return this.state.axes;
  }

  constructor() {
    // Subscribe to metrics store's runs summary
    this.runsSummaryUnsubscribe = metricsStore.subscribeRunsSummary(() => {
      const summary = metricsStore.getRunsSummary();
      this.state.runs = summary.map((r: any) => ({
        run_id: r.run_id,
        status: r.status,
        record_count: r.record_count,
        started_at: r.started_at,
        profile: r.profile,
        task: r.task,
        fidelity: r.fidelity,
      }));
      // Auto-select newest running run if none chosen
      if (!this.state.selectedRunId) {
        const running = this.state.runs
          .filter((r) => r.status === "running" || r.record_count > 0)
          .sort((a, b) => {
            const ta = a.started_at ? Date.parse(a.started_at) : 0;
            const tb = b.started_at ? Date.parse(b.started_at) : 0;
            return tb - ta; // newest first
          });
        if (running.length > 0) {
          this.state.selectedRunId = running[0].run_id;
        }
      }
      this.notify();
    });
  }

  /** Get current runs catalog. */
  getRuns(): RunSummary[] {
    return this.state.runs;
  }

  /** Get currently selected run ID. */
  getSelectedRunId(): string | null {
    return this.state.selectedRunId;
  }

  /** Select a run by ID. */
  selectRun(runId: string | null): void {
    if (this.state.selectedRunId !== runId) {
      this.state.selectedRunId = runId;
      this.notify();
    }
  }

  /** Get current axes selection. */
  getAxes(): AxisSelection {
    return this.state.axes;
  }

  /** Set axes selection. */
  setAxes(axes: AxisSelection): void {
    this.state.axes = axes;
    this.notify();
  }

  /** Get current cell selection. */
  getCellSelection(): string | null {
    return this.state.cellSelection;
  }

  /** Set cell selection. */
  setCellSelection(key: string | null): void {
    if (this.state.cellSelection !== key) {
      this.state.cellSelection = key;
      this.notify();
    }
  }

  /** Subscribe to any workspace state change. Returns unsubscribe function. */
  onChange(listener: Listener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  /** Subscribe only to run catalog changes. */
  onRunsChange(listener: Listener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  /** Subscribe only to selected run changes. */
  onSelectionChange(listener: Listener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  /** Subscribe only to axes changes. */
  onAxesChange(listener: Listener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  /** Subscribe only to cell selection changes. */
  onCellSelectionChange(listener: Listener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify(): void {
    this.listeners.forEach((listener) => listener());
  }

  /** Request fresh runs summary from server. */
  async refreshRuns(): Promise<void> {
    await metricsStore.refreshRunsSummary();
  }

  dispose(): void {
    this.runsSummaryUnsubscribe?.();
    this.listeners.clear();
  }
}

export const workspaceStore = new WorkspaceStore();