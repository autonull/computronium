/** Shared control-plane state: one poller for every control-bar instance. */

const POLL_MS = 500;

export interface ControlState {
  paused: boolean;
  step_budget: number;
  max_workers: number | null;
  cancel: boolean;
  revision: number;
}

export interface RunStatus {
  run_id: string;
  stage: string;
  in_flight: number;
  cells_done: number;
  ceiling: number;
}

export interface ControlPayload {
  control: ControlState;
  status: RunStatus | null;
  readable: boolean;
  error: string | null;
  machine: { cpu_percent: number; cpu_count: number | null };
}

type Listener = (payload: ControlPayload | null) => void;

export class ControlStore {
  private payload: ControlPayload | null = null;
  private readonly listeners = new Set<Listener>();
  private timer: number | null = null;

  subscribe(listener: Listener): () => void {
    this.listeners.add(listener);
    listener(this.payload);
    this.ensurePolling();
    return () => {
      this.listeners.delete(listener);
      if (this.listeners.size === 0) this.stopPolling();
    };
  }

  get current(): ControlPayload | null {
    return this.payload;
  }

  async command(changes: Record<string, unknown>): Promise<string | null> {
    const revision = this.payload?.control.revision;
    try {
      const response = await fetch("/api/control", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...changes, revision }),
      });
      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        return typeof body.error === "string" ? body.error : "command refused";
      }
      await this.poll();
      return null;
    } catch {
      return "cannot reach server";
    }
  }

  togglePlay(): void {
    void this.command({ paused: !this.payload?.control.paused });
  }

  step(): void {
    void this.command({ step: true });
  }

  stop(): void {
    void this.command({ cancel: true });
  }

  setCeiling(maxWorkers: number): void {
    void this.command({ max_workers: maxWorkers });
  }

  private ensurePolling(): void {
    if (this.timer !== null) return;
    this.timer = window.setInterval(() => void this.poll(), POLL_MS);
    void this.poll();
  }

  private stopPolling(): void {
    if (this.timer === null) return;
    clearInterval(this.timer);
    this.timer = null;
  }

  private async poll(): Promise<void> {
    try {
      const response = await fetch("/api/control");
      if (!response.ok) return;
      this.payload = (await response.json()) as ControlPayload;
      for (const listener of this.listeners) listener(this.payload);
    } catch {
      /* keep last state */
    }
  }
}

export const controlStore = new ControlStore();
