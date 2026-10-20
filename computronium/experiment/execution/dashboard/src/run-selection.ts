/** Which run the dashboard shows (TODO68).

A store holds several runs — the run, and the runs its own answers spawned —
and every one of them reports its own metrics. A picture can only show one at
a time, so the choice is made once, here: the run that started last until the
reader picks another, and every component that draws a run's evidence reads
the same answer. Without it, the map, the charts and the panel each showed
whichever run reported last, and the reader was never told which.
*/

export interface RunSummary {
  run_id?: string;
  profile?: string;
  tasks?: string[];
  fidelity?: string;
  mode?: string;
  started_at?: string;
}

export interface RunMetrics {
  records?: any[];
  pareto?: boolean[];
  ablation_groups?: any[];
  chance?: number;
  required_seeds?: number;
  resources?: Record<string, number | string | undefined>;
  store?: { source?: string; published_at?: string };
  run?: RunSummary;
}

export type RunListener = (runId: string | null, metrics: RunMetrics | null) => void;

class RunSelection {
  private metricsByRun: Map<string, RunMetrics> = new Map();
  private selectedRunId: string | null = null;
  /** Whether the reader has chosen, or the newest run still leads. */
  private chosenByReader = false;
  private listeners: RunListener[] = [];

  /** A run reported its metrics. */
  observe(runId: string, metrics: RunMetrics): void {
    this.metricsByRun.set(runId, metrics);
    if (!this.chosenByReader) {
      this.selectedRunId = this.newestRunId();
    }
    this.notify();
  }

  /** The reader chose the run the dashboard shows. */
  select(runId: string | null): void {
    this.chosenByReader = true;
    this.selectedRunId = runId;
    this.notify();
  }

  get selectedId(): string | null {
    return this.selectedRunId;
  }

  get selected(): RunMetrics | null {
    if (!this.selectedRunId) return null;
    return this.metricsByRun.get(this.selectedRunId) ?? null;
  }

  /** Every run the dashboard has heard about, with its metrics. */
  get runs(): [string, RunMetrics][] {
    return Array.from(this.metricsByRun.entries());
  }

  onChange(listener: RunListener): void {
    this.listeners.push(listener);
  }

  private notify(): void {
    this.listeners.forEach((listener) => listener(this.selectedRunId, this.selected));
  }

  /** The run that started last: the one in progress, when there is one. */
  private newestRunId(): string | null {
    let newest: string | null = null;
    let newestAt = -Infinity;
    this.metricsByRun.forEach((metrics, runId) => {
      const started = metrics.run?.started_at;
      const at = started ? Date.parse(started) : Number.NaN;
      if (Number.isNaN(at)) return;
      if (at >= newestAt) {
        newestAt = at;
        newest = runId;
      }
    });
    if (newest) return newest;
    const first = this.metricsByRun.keys().next();
    return first.done ? null : first.value;
  }
}

export const runSelection = new RunSelection();
