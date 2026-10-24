/** The control bar: the verbs, always visible (TODO70, refactored for TODO71 Phase 1).
 *
 * The dashboard is an instrument: these are the buttons that act on the run,
 * and they act on the run itself — through the control plane, which a run
 * in another process reads. Nothing here is decorative, and nothing here is
 * a control the server does not offer: a verb the server cannot honour is
 * disabled, with the reason in its tooltip.
 *
 * The bar polls the control endpoint at 2 Hz. The dashboard's own update
 * loop runs every two seconds, which is far too slow for a meter that is
 * meant to move.
 *
 * The ceiling and the use are two different numbers, and the bar shows
 * both: the slider sets the ceiling, the meter shows the cells in flight
 * now, and the machine's own CPU is a third mark. Collapsing them into
 * one number would be a lie about which is which.
 */

import { registry } from "./components/registry.js";
import { panels, registerDisplayPanel } from "./panels.js";
import { createPanelShell } from "./shell.js";
import { layout, getLayout } from "./layout.js";
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

function createControlBarBody(): string {
  return `
    <style>
      .control-bar .verb {
        width: 36px;
        height: 32px;
        font-size: 16px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 6px;
        color: var(--text-primary);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all var(--motion-fast) var(--ease-out);
      }
      .control-bar .verb:not(:disabled):hover {
        background: var(--border);
        border-color: var(--border-bright);
        transform: translateY(-1px);
      }
      .control-bar .verb:not(:disabled):active {
        transform: translateY(0) scale(0.95);
      }
      .control-bar .verb:disabled {
        opacity: 0.4;
        cursor: not-allowed;
      }
      .control-bar .verb-primary:not(:disabled) {
        background: var(--gradient)22;
        border-color: var(--gradient)66;
        color: var(--gradient);
      }
      .control-bar .verb-primary:not(:disabled):hover {
        background: var(--gradient)33;
        border-color: var(--gradient);
      }
      .control-bar .verb-danger:not(:disabled) {
        background: var(--error)22;
        border-color: var(--error)66;
        color: var(--error);
      }
      .control-bar .verb-danger:not(:disabled):hover {
        background: var(--error)33;
        border-color: var(--error);
      }
      .control-bar .separator {
        width: 1px;
        height: 24px;
        background: var(--border);
      }
      .control-bar .meter-group {
        display: flex;
        flex-direction: column;
        gap: 3px;
        min-width: 150px;
      }
      .control-bar .meter-label-row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
      }
      .control-bar .meter-label {
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-secondary);
      }
      .control-bar .meter-value {
        color: var(--text-primary);
        font-weight: 600;
        font-variant-numeric: tabular-nums;
      }
      .control-bar .meter-bar {
        height: 6px;
        background: var(--bg);
        border-radius: 3px;
        overflow: hidden;
      }
      .control-bar .meter-fill {
        height: 100%;
        width: 0%;
        border-radius: 3px;
        transition: width var(--motion-normal) var(--ease-out), background-color var(--motion-fast);
      }
      .control-bar .ceiling-slider {
        width: 150px;
        accent-color: var(--gradient);
      }
      .control-bar .trace-canvas {
        border: 1px solid var(--border);
        border-radius: 6px;
        background: var(--bg);
      }
      .control-bar .status-text {
        min-width: 120px;
        color: var(--text-secondary);
        font-variant-numeric: tabular-nums;
      }
      .control-bar .door-btn {
        width: 30px;
        height: 30px;
        font-size: 15px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 6px;
        color: var(--text-primary);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all var(--motion-fast) var(--ease-out);
      }
      .control-bar .door-btn:hover {
        background: var(--border);
        border-color: var(--border-bright);
      }
      .control-bar .workspace-switcher {
        margin-left: 8px;
      }
    </style>
    <button class="verb verb-primary" data-action="play" title="Play — release the run">▶</button>
    <button class="verb" data-action="step" title="Step — release exactly one more batch" disabled>⏭</button>
    <button class="verb verb-danger" data-action="stop" title="Stop — end the run at its next boundary">⏹</button>
    <div class="separator"></div>
    <div class="meter-group">
      <div class="meter-label-row">
        <span class="meter-label">CEILING</span>
        <span class="meter-value ceiling-value">—</span>
      </div>
      <input class="ceiling-slider" type="range" min="1" max="8" value="4" />
    </div>
    <div class="meter-group">
      <div class="meter-label-row">
        <span class="meter-label">CELLS</span>
        <span class="meter-value level-text">—</span>
      </div>
      <div class="meter-bar"><div class="meter-fill level-fill" style="background: var(--promoted);"></div></div>
      <div class="meter-label-row">
        <span class="meter-label">CPU</span>
        <span class="meter-value cpu-text">—</span>
      </div>
      <div class="meter-bar"><div class="meter-fill cpu-fill" style="background: var(--cpu);"></div></div>
    </div>
    <canvas class="trace-canvas" width="130" height="42"></canvas>
    <div class="separator"></div>
    <span class="status-text">no run is reporting</span>
    <div class="workspace-switcher"></div>
    <button class="door-btn" data-action="panel" title="Open control panel">⚙</button>
  `;
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

  private layoutUnsubscribe: (() => void) | null = null;

  async init(): Promise<void> {
    this.container = createPanelShell({
      id: "control-bar",
      title: "Control Bar",
      glyph: "⏯",
      body: createControlBarBody(),
      dock: "bottom",
      defaultOpen: true,
      className: "control-bar-panel",
    });

    this.bindElements();
    this.bindEvents();

    registerDisplayPanel(
      "control-bar",
      "control bar",
      "⏯",
      () => this.container,
    );

    // Listen for layout changes to refresh workspace switcher
    this.layoutUnsubscribe = getLayout().onChange(() => this.refreshWorkspaceSwitcher());

    this.timer = window.setInterval(() => {
      void this.poll();
    }, POLL_MS);
    void this.poll();
  }

  async destroy(): Promise<void> {
    if (this.timer !== null) window.clearInterval(this.timer);
    this.timer = null;
    this.layoutUnsubscribe?.();
    this.layoutUnsubscribe = null;
    this.container?.remove();
  }

  private refreshWorkspaceSwitcher(): void {
    if (!this.workspaceSwitcherContainer) return;
    const switcher = this.workspaceSwitcherContainer.querySelector(".workspace-switcher");
    if (switcher) {
      getLayout().refreshSwitcher(switcher as HTMLElement);
    }
  }

  private workspaceSwitcherContainer: HTMLElement | null = null;

  private bindElements(): void {
    if (!this.container) return;
    const verbs = this.container.querySelectorAll<HTMLButtonElement>(".verb");
    this.playButton = verbs[0];
    this.stepButton = verbs[1];
    this.stopButton = verbs[2];

    this.slider = this.container.querySelector<HTMLInputElement>(".ceiling-slider");
    this.ceilingValue = this.container.querySelector(".ceiling-value");
    this.levelFill = this.container.querySelector(".level-fill");
    this.levelText = this.container.querySelector(".level-text");
    this.cpuFill = this.container.querySelector(".cpu-fill");
    this.cpuText = this.container.querySelector(".cpu-text");
    this.trace = this.container.querySelector("canvas.trace-canvas");
    this.statusText = this.container.querySelector(".status-text");

    // Initialize workspace switcher
    this.workspaceSwitcherContainer = this.container.querySelector(".workspace-switcher");
    if (this.workspaceSwitcherContainer) {
      const switcher = getLayout().buildWorkspaceSwitcher();
      this.workspaceSwitcherContainer.appendChild(switcher);
    }
  }

  private bindEvents(): void {
    if (!this.container) return;
    this.playButton?.addEventListener("click", () => this.togglePlay());
    this.stepButton?.addEventListener("click", () => this.step());
    this.stopButton?.addEventListener("click", () => this.stop());
    this.slider?.addEventListener("input", (e) => {
      const target = e.target as HTMLInputElement;
      const value = Number(target.value);
      if (this.ceilingValue) this.ceilingValue.textContent = String(value);
    });
    this.slider?.addEventListener("change", () => {
      const value = Number(this.slider?.value ?? 1);
      void this.command({ max_workers: value });
    });
    this.container
      .querySelector<HTMLButtonElement>(".door-btn")!
      .addEventListener("click", () => panels.toggle("control-panel"));
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
      const isPaused = control.paused;
      this.playButton.textContent = isPaused ? "▶" : "⏸";
      this.playButton.classList.toggle("verb-primary", isPaused);
      this.playButton.classList.toggle("verb-danger", !isPaused);
      this.playButton.title = isPaused
        ? "Play — release the run"
        : "Pause — hold the run at its next boundary";
      this.playButton.setAttribute("aria-label", isPaused ? "play" : "pause");
    }
    if (this.stepButton) {
      const canStep = control.paused && payload.readable;
      this.stepButton.disabled = !canStep;
      this.stepButton.title = canStep
        ? "Step — release exactly one more batch"
        : control.paused
          ? "Step — control plane not readable"
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
      // Color transitions: green when idle, amber when busy, red when saturated
      if (fraction === 0) this.levelFill.style.background = "var(--promoted)";
      else if (fraction < 0.5) this.levelFill.style.background = "var(--promoted)";
      else if (fraction < 0.85) this.levelFill.style.background = "var(--warn)";
      else this.levelFill.style.background = "var(--error)";
    }
    if (this.levelText) {
      this.levelText.textContent = `${inFlight}${ceiling ? ` / ${ceiling}` : ""}`;
    }
    if (this.cpuFill) {
      const cpuClamped = Math.min(100, Math.max(0, cpu));
      this.cpuFill.style.width = `${cpuClamped}%`;
      if (cpuClamped < 30) this.cpuFill.style.background = "var(--cpu)";
      else if (cpuClamped < 70) this.cpuFill.style.background = "var(--warn)";
      else this.cpuFill.style.background = "var(--error)";
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

    // Subtle grid lines
    ctx.strokeStyle = "var(--border)";
    ctx.lineWidth = 0.5;
    [0.25, 0.5, 0.75].forEach((frac) => {
      const y = height * frac;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    });

    // CPU trace (machine use) - blue line
    ctx.beginPath();
    ctx.strokeStyle = "var(--cpu)";
    ctx.globalAlpha = 0.7;
    ctx.lineWidth = 1;
    this.samples.forEach((sample, index) => {
      const x = offset + index * step;
      const y = height - (Math.min(100, sample.cpu) / 100) * height;
      if (index === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
    ctx.globalAlpha = 1;

    // Level trace (cells in flight) - green/amber/red gradient based on level
    const gradient = ctx.createLinearGradient(0, height, 0, 0);
    gradient.addColorStop(0, "var(--promoted)");
    gradient.addColorStop(0.5, "var(--warn)");
    gradient.addColorStop(1, "var(--error)");
    ctx.strokeStyle = gradient;
    ctx.lineWidth = 1.5;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    this.samples.forEach((sample, index) => {
      const x = offset + index * step;
      const y = height - Math.min(1, sample.level / ceiling) * height;
      if (index === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Current value indicators (small dots at the right edge)
    if (this.samples.length > 0) {
      const latest = this.samples[this.samples.length - 1];
      const x = width - 2;
      // CPU dot
      const cpuY = height - (Math.min(100, latest.cpu) / 100) * height;
      ctx.fillStyle = "var(--cpu)";
      ctx.beginPath();
      ctx.arc(x, cpuY, 2.5, 0, Math.PI * 2);
      ctx.fill();
      // Level dot
      const levelY = height - Math.min(1, latest.level / ceiling) * height;
      const levelFrac = latest.level / ceiling;
      ctx.fillStyle = levelFrac < 0.5 ? "var(--promoted)" : levelFrac < 0.85 ? "var(--warn)" : "var(--error)";
      ctx.beginPath();
      ctx.arc(x - 6, levelY, 2.5, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  /** Say why a command did not land. */
  private setStatus(text: string): void {
    if (this.statusText) this.statusText.textContent = text;
  }
}

export const controlBar = new ControlBar();
registry.register(controlBar);