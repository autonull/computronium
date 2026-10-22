/** The control bar: the verbs, always visible (TODO70).

    The dashboard is an instrument: these are the buttons that act on the run,
    and they act on the run itself — through the control plane, which a run
    in another process reads. Nothing here is decorative, and nothing here is
    a control the server does not offer: a verb the server cannot honour is
    disabled, with the reason in its tooltip.

    The bar polls the control endpoint at 2 Hz. The dashboard's own update
    loop runs every two seconds, which is far too slow for a meter that is
    meant to move.

    The ceiling and the use are two different numbers, and the bar shows
    both: the slider sets the ceiling, the meter shows the cells in flight
    now, and the machine's own CPU is a third mark. Collapsing them into
    one number would be a lie about which is which.
*/

import { registry } from "./components/registry.js";
import { closeButton, panels, registerDisplayPanel } from "./panels.js";
import type { Component } from "./components/registry.js";

/** How often the bar asks the server what the run is doing. */
const POLL_MS = 500;

/** How many samples the trace keeps: a minute at two hertz. */
const TRACE_SAMPLES = 60;

/** The control section of the plane. */
interface ControlState {
  paused: boolean;
  step_budget: number;
  max_workers: number | null;
  cancel: boolean;
  revision: number;
  updated_at: number;
}

/** What the run says about itself. */
interface RunStatus {
  run_id: string;
  stage: string;
  in_flight: number;
  cells_done: number;
  ceiling: number;
  at: number;
}

/** What the control endpoint answers. */
interface ControlPayload {
  control: ControlState;
  status: RunStatus | null;
  readable: boolean;
  error: string | null;
  machine: { cpu_percent: number; cpu_count: number | null };
}

/** One sample of the trace: the cells in flight and the machine's use. */
interface Sample {
  level: number;
  cpu: number;
}

export class ControlBar implements Component {
  name = "ControlBar";

  private container: HTMLElement | null = null;
  private playButton: HTMLButtonElement | null = null;
  private stepButton: HTMLButtonElement | null = null;
  private stopButton: HTMLButtonElement | null = null;
  private slider: HTMLInputElement | null = null;
  private ceilingValue: HTMLElement | null = null;
  private levelFill: HTMLElement | null = null;
  private levelText: HTMLElement | null = null;
  private cpuFill: HTMLElement | null = null;
  private cpuText: HTMLElement | null = null;
  private trace: HTMLCanvasElement | null = null;
  private statusText: HTMLElement | null = null;
  private timer: number | null = null;

  private payload: ControlPayload | null = null;
  private samples: Sample[] = [];

  async init(): Promise<void> {
    this.createBar();
    registerDisplayPanel(
      "control-bar",
      "control bar",
      "⏯",
      () => this.container,
    );
    this.timer = window.setInterval(() => {
      void this.poll();
    }, POLL_MS);
    void this.poll();
  }

  async destroy(): Promise<void> {
    if (this.timer !== null) window.clearInterval(this.timer);
    this.timer = null;
    this.container?.remove();
  }

  /** Play or pause: the button shows what the server says, and the browser
   * never decides. */
  togglePlay(): void {
    void this.command({ paused: !this.payload?.control.paused });
  }

  /** Release exactly one more batch. */
  step(): void {
    void this.command({ step: true });
  }

  /** Stop the run. The reader confirms it. */
  stop(): void {
    if (!window.confirm("Stop the run? The run ends at its next boundary.")) {
      return;
    }
    void this.command({ cancel: true });
  }

  /** Ask the server what the run is doing, and show it. */
  private async poll(): Promise<void> {
    try {
      const response = await fetch("/api/control");
      if (!response.ok) return;
      const payload = (await response.json()) as ControlPayload;
      this.payload = payload;
      this.samples.push({
        level: payload.status?.in_flight ?? 0,
        cpu: payload.machine?.cpu_percent ?? 0,
      });
      while (this.samples.length > TRACE_SAMPLES) this.samples.shift();
      this.render();
    } catch {
      // The server is away: the bar keeps its last reading rather than
      // pretending the run stopped.
    }
  }

  /** Ask the run to do something. */
  private async command(changes: Record<string, unknown>): Promise<void> {
    const revision = this.payload?.control.revision;
    try {
      const response = await fetch("/api/control", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...changes, revision }),
      });
      if (!response.ok) {
        const body = (await response.json().catch(() => ({}))) as {
          error?: string;
        };
        this.setStatus(body.error ?? "the control plane refused the command");
        return;
      }
      await this.poll();
    } catch {
      this.setStatus("the dashboard could not reach the server");
    }
  }

  /** Draw everything the bar knows. */
  private render(): void {
    const payload = this.payload;
    if (!payload) return;
    const control = payload.control;
    const status = payload.status;
    const inFlight = status?.in_flight ?? 0;
    const ceiling = control.max_workers ?? status?.ceiling ?? 0;
    const cpu = payload.machine?.cpu_percent ?? 0;

    // The button shows what the server says, and the browser never decides.
    if (this.playButton) {
      this.playButton.textContent = control.paused ? "▶" : "⏸";
      this.playButton.title = control.paused
        ? "Play — release the run"
        : "Pause — hold the run at its next boundary";
      this.playButton.setAttribute(
        "aria-label",
        control.paused ? "play" : "pause",
      );
    }
    if (this.stepButton) {
      // Stepping is only a thing a paused run can do.
      this.stepButton.disabled = !control.paused || !payload.readable;
      this.stepButton.title = control.paused
        ? "Step — release exactly one more batch"
        : "Step — the run is not paused";
    }
    if (this.stopButton) {
      this.stopButton.disabled = !payload.readable;
      this.stopButton.title = "Stop — end the run at its next boundary";
    }

    const reason = payload.readable
      ? ""
      : payload.error ?? "the control plane could not be read";
    if (this.playButton) this.playButton.disabled = !payload.readable;
    if (this.playButton && reason) this.playButton.title = reason;

    if (this.slider) {
      const max = Math.max(
        1,
        payload.machine?.cpu_count ?? 1,
        ceiling || 1,
      );
      this.slider.max = String(max);
      this.slider.value = String(Math.max(1, ceiling || 1));
      this.slider.disabled = !payload.readable;
      this.slider.title = reason
        ? reason
        : `The ceiling on cells in flight — ${ceiling || "the run's own"}`;
    }
    if (this.ceilingValue) {
      this.ceilingValue.textContent = ceiling ? String(ceiling) : "—";
    }

    if (this.levelFill) {
      const fraction = ceiling ? Math.min(1, inFlight / ceiling) : 0;
      this.levelFill.style.width = `${fraction * 100}%`;
    }
    if (this.levelText) {
      this.levelText.textContent = `${inFlight}${ceiling ? ` / ${ceiling}` : ""}`;
    }
    if (this.cpuFill) {
      this.cpuFill.style.width = `${Math.min(100, Math.max(0, cpu))}%`;
    }
    if (this.cpuText) {
      this.cpuText.textContent = `${cpu.toFixed(0)}%`;
    }

    this.drawTrace();

    if (this.statusText && !reason) {
      const stage = status?.stage ? status.stage.replace("s", "S") : "";
      this.statusText.textContent = status
        ? `${stage} · ${status.cells_done} cells`
        : "no run is reporting";
    }
  }

  /** The trace: the level over the last minute, and the machine's use. */
  private drawTrace(): void {
    const canvas = this.trace;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);

    const ceiling = Math.max(
      1,
      this.payload?.control.max_workers ??
        this.payload?.status?.ceiling ??
        1,
    );
    const step = width / Math.max(1, TRACE_SAMPLES - 1);
    const offset = width - (this.samples.length - 1) * step;

    // The machine's use: the line that says whether the run is starved.
    ctx.beginPath();
    ctx.strokeStyle = "rgba(120, 160, 220, 0.75)";
    ctx.lineWidth = 1;
    this.samples.forEach((sample, index) => {
      const x = offset + index * step;
      const y = height - (Math.min(100, sample.cpu) / 100) * height;
      if (index === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // The level: the cells in flight, over the ceiling.
    ctx.beginPath();
    ctx.strokeStyle = "rgba(120, 230, 180, 0.95)";
    ctx.lineWidth = 1.5;
    this.samples.forEach((sample, index) => {
      const x = offset + index * step;
      const y = height - Math.min(1, sample.level / ceiling) * height;
      if (index === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
  }

  /** Say why a command did not land. */
  private setStatus(text: string): void {
    if (this.statusText) this.statusText.textContent = text;
  }

  private createBar(): void {
    const overlay = document.getElementById("ui-overlay");
    if (!overlay) return;

    this.container = document.createElement("div");
    this.container.id = "control-bar";
    this.container.style.cssText = `
      position: fixed;
      bottom: 126px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 14px;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 10px;
      font-size: 11px;
      color: var(--text-secondary);
      z-index: 165;
      box-shadow: 0 8px 32px rgba(0,0,0,0.45);
    `;

    this.container.innerHTML = `
      <button class="verb" style="
        width: 34px;
        height: 30px;
        font-size: 15px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 6px;
        color: var(--text-primary);
        cursor: pointer;
      ">⏸</button>
      <button class="verb" style="
        width: 34px;
        height: 30px;
        font-size: 15px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 6px;
        color: var(--text-primary);
        cursor: pointer;
      ">⏭</button>
      <button class="verb" style="
        width: 34px;
        height: 30px;
        font-size: 15px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 6px;
        color: var(--text-primary);
        cursor: pointer;
      ">⏹</button>
      <div style="width: 1px; height: 26px; background: var(--border);"></div>
      <div style="display: flex; flex-direction: column; gap: 3px; min-width: 150px;">
        <div style="display: flex; justify-content: space-between; align-items: baseline;">
          <span>CEILING</span>
          <span class="ceiling-value" style="color: var(--text-primary); font-weight: 600;">—</span>
        </div>
        <input class="ceiling-slider" type="range" min="1" max="8" value="4" style="width: 150px;" />
      </div>
      <div style="display: flex; flex-direction: column; gap: 3px; min-width: 150px;">
        <div style="display: flex; justify-content: space-between; align-items: baseline;">
          <span>CELLS</span>
          <span class="level-text" style="color: var(--text-primary); font-weight: 600;">—</span>
        </div>
        <div style="height: 6px; background: var(--bg); border-radius: 3px; overflow: hidden;">
          <div class="level-fill" style="height: 100%; width: 0%; background: var(--promoted); border-radius: 3px; transition: width 0.2s linear;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: baseline;">
          <span>CPU</span>
          <span class="cpu-text" style="color: var(--text-primary); font-weight: 600;">—</span>
        </div>
        <div style="height: 6px; background: var(--bg); border-radius: 3px; overflow: hidden;">
          <div class="cpu-fill" style="height: 100%; width: 0%; background: var(--cpu); border-radius: 3px; transition: width 0.4s ease;"></div>
        </div>
      </div>
      <canvas class="trace" width="130" height="42" style="
        border: 1px solid var(--border);
        border-radius: 6px;
        background: var(--bg);
      "></canvas>
      <div style="width: 1px; height: 26px; background: var(--border);"></div>
      <span class="status" style="min-width: 120px; color: var(--text-secondary);">—</span>
      <button class="door" style="
        width: 30px;
        height: 30px;
        font-size: 15px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 6px;
        color: var(--text-primary);
        cursor: pointer;
      ">⚙</button>
    `;

    overlay.appendChild(this.container);

    const verbs = this.container.querySelectorAll<HTMLButtonElement>(".verb");
    this.playButton = verbs[0];
    this.stepButton = verbs[1];
    this.stopButton = verbs[2];
    this.playButton.addEventListener("click", () => this.togglePlay());
    this.stepButton.addEventListener("click", () => this.step());
    this.stopButton.addEventListener("click", () => this.stop());

    this.slider = this.container.querySelector<HTMLInputElement>(
      ".ceiling-slider",
    );
    this.slider?.addEventListener("change", () => {
      const value = Number(this.slider?.value ?? 1);
      void this.command({ max_workers: value });
    });
    this.ceilingValue = this.container.querySelector(".ceiling-value");
    this.levelFill = this.container.querySelector(".level-fill");
    this.levelText = this.container.querySelector(".level-text");
    this.cpuFill = this.container.querySelector(".cpu-fill");
    this.cpuText = this.container.querySelector(".cpu-text");
    this.trace = this.container.querySelector("canvas.trace");
    this.statusText = this.container.querySelector(".status");
    this.container
      .querySelector<HTMLButtonElement>(".door")!
      .addEventListener("click", () => panels.toggle("control-panel"));

    const close = closeButton(() => panels.toggle("control-bar"));
    close.style.position = "absolute";
    close.style.top = "-10px";
    close.style.right = "-8px";
    this.container.appendChild(close);
  }
}

export const controlBar = new ControlBar();
registry.register(controlBar);
