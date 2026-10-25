/** Simple control bar — play/step/stop, ceiling slider, status. */

import { registry } from "./components/registry.js";
import { panels, registerDisplayPanel } from "./panels.js";
import { createPanelShell } from "./shell.js";
import { controlStore, type ControlPayload } from "./stores/control.js";
import type { Component } from "./components/registry.js";

export function createControlBarBody(): string {
  return `
    <style>
      .ctrl .verb { width: 36px; height: 32px; font-size: 16px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 6px; color: var(--text-primary); cursor: pointer; display: flex; align-items: center; justify-content: center; }
      .ctrl .verb:not(:disabled):hover { background: var(--border); border-color: var(--border-bright); }
      .ctrl .verb:disabled { opacity: 0.4; cursor: not-allowed; }
      .ctrl .verb.primary:not(:disabled) { background: var(--gradient)22; border-color: var(--gradient)66; color: var(--gradient); }
      .ctrl .verb.danger:not(:disabled) { background: var(--error)22; border-color: var(--error)66; color: var(--error); }
      .ctrl .sep { width: 1px; height: 24px; background: var(--border); }
      .ctrl .meter { display: flex; flex-direction: column; gap: 2px; min-width: 120px; }
      .ctrl .meter-row { display: flex; justify-content: space-between; align-items: baseline; font-size: 10px; }
      .ctrl .meter-label { text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); }
      .ctrl .meter-value { color: var(--text-primary); font-weight: 600; }
      .ctrl .bar { height: 5px; background: var(--bg); border-radius: 2px; overflow: hidden; }
      .ctrl .fill { height: 100%; width: 0%; border-radius: 2px; }
      .ctrl .slider { width: 120px; accent-color: var(--gradient); }
      .ctrl .status { min-width: 100px; color: var(--text-secondary); font-variant-numeric: tabular-nums; font-size: 12px; }
      .ctrl .door { width: 30px; height: 30px; font-size: 14px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 6px; color: var(--text-primary); cursor: pointer; display: flex; align-items: center; justify-content: center; }
      .ctrl .door:hover { background: var(--border); }
    </style>
    <div class="ctrl" style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
      <button class="verb primary" data-act="play" title="Play">▶</button>
      <button class="verb" data-act="step" title="Step one batch" disabled>⏭</button>
      <button class="verb danger" data-act="stop" title="Stop run">⏹</button>
      <div class="sep"></div>
      <div class="meter">
        <div class="meter-row"><span class="meter-label">Ceiling</span><span class="meter-value ceil">—</span></div>
        <input class="slider" type="range" min="1" max="8" value="4" />
      </div>
      <div class="meter">
        <div class="meter-row"><span class="meter-label">Cells</span><span class="meter-value cells">—</span></div>
        <div class="bar"><div class="fill cells-fill" style="background: var(--promoted);"></div></div>
        <div class="meter-row"><span class="meter-label">CPU</span><span class="meter-value cpu">—</span></div>
        <div class="bar"><div class="fill cpu-fill" style="background: var(--cpu);"></div></div>
      </div>
      <div class="sep"></div>
      <span class="status">no run</span>
      <button class="door" data-act="panel" title="Control panel">⚙</button>
    </div>
  `;
}

/** A control bar bound to one root element and the shared control store. */
export class ControlBarView {
  private readonly playBtn: HTMLButtonElement;
  private readonly stepBtn: HTMLButtonElement;
  private readonly stopBtn: HTMLButtonElement;
  private readonly slider: HTMLInputElement;
  private readonly ceilEl: HTMLElement;
  private readonly cellsFill: HTMLElement;
  private readonly cellsEl: HTMLElement;
  private readonly cpuFill: HTMLElement;
  private readonly cpuEl: HTMLElement;
  private readonly statusEl: HTMLElement;
  private readonly unsubscribe: () => void;

  constructor(
    private readonly root: HTMLElement,
    openControlPanel: () => void = () => panels.toggle("control-panel"),
  ) {
    this.playBtn = this.query("[data-act=play]");
    this.stepBtn = this.query("[data-act=step]");
    this.stopBtn = this.query("[data-act=stop]");
    this.slider = this.query(".slider");
    this.ceilEl = this.query(".ceil");
    this.cellsFill = this.query(".cells-fill");
    this.cellsEl = this.query(".cells");
    this.cpuFill = this.query(".cpu-fill");
    this.cpuEl = this.query(".cpu");
    this.statusEl = this.query(".status");

    this.playBtn.addEventListener("click", () => controlStore.togglePlay());
    this.stepBtn.addEventListener("click", () => controlStore.step());
    this.stopBtn.addEventListener("click", () => {
      if (confirm("Stop the run?")) controlStore.stop();
    });
    this.slider.addEventListener("change", () =>
      controlStore.setCeiling(Number(this.slider.value)),
    );
    this.query("[data-act=panel]").addEventListener("click", openControlPanel);
    this.unsubscribe = controlStore.subscribe((payload) => this.render(payload));
  }

  dispose(): void {
    this.unsubscribe();
  }

  private query<T extends HTMLElement>(selector: string): T {
    const el = this.root.querySelector<T>(selector);
    if (!el) throw new Error(`[ControlBar] missing element: ${selector}`);
    return el;
  }

  private render(p: ControlPayload | null): void {
    if (!p) return;
    const c = p.control;
    const s = p.status;
    const inFlight = s?.in_flight ?? 0;
    const ceiling = c.max_workers ?? s?.ceiling ?? 0;
    const cpu = p.machine?.cpu_percent ?? 0;

    const paused = c.paused;
    this.playBtn.textContent = paused ? "▶" : "⏸";
    this.playBtn.classList.toggle("primary", paused);
    this.playBtn.classList.toggle("danger", !paused);
    this.playBtn.title = paused ? "Play" : "Pause";

    const canStep = c.paused && p.readable;
    this.stepBtn.disabled = !canStep;
    this.stepBtn.title = canStep
      ? "Step"
      : c.paused
        ? "Control plane not readable"
        : "Run not paused";
    this.stopBtn.disabled = !p.readable;
    this.playBtn.disabled = !p.readable;
    if (!p.readable) this.playBtn.title = p.error || "control plane unreadable";

    const max = Math.max(1, p.machine?.cpu_count ?? 1, ceiling || 1);
    this.slider.max = String(max);
    this.slider.value = String(Math.max(1, ceiling || 1));
    this.slider.disabled = !p.readable;
    this.ceilEl.textContent = ceiling ? String(ceiling) : "—";

    const frac = ceiling ? Math.min(1, inFlight / ceiling) : 0;
    this.cellsFill.style.width = `${frac * 100}%`;
    this.cellsFill.style.background =
      frac < 0.5
        ? "var(--promoted)"
        : frac < 0.85
          ? "var(--warn)"
          : "var(--error)";
    this.cellsEl.textContent = `${inFlight}${ceiling ? ` / ${ceiling}` : ""}`;

    const cpuPercent = Math.min(100, Math.max(0, cpu));
    this.cpuFill.style.width = `${cpuPercent}%`;
    this.cpuFill.style.background =
      cpuPercent < 30
        ? "var(--cpu)"
        : cpuPercent < 70
          ? "var(--warn)"
          : "var(--error)";
    this.cpuEl.textContent = `${cpu.toFixed(0)}%`;

    if (p.readable) {
      this.statusEl.textContent = s
        ? `${s.stage.replace("s", "S")} · ${s.cells_done} cells`
        : "no run";
    }
  }
}

/** The legacy singleton panel used by GoldenLayout until P2. */
export class ControlBar implements Component {
  name = "ControlBar";
  private container: HTMLElement | null = null;
  private view: ControlBarView | null = null;

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
    this.view = new ControlBarView(this.container);
    registerDisplayPanel("control-bar", "control bar", "⏯", () => this.container);
  }

  async destroy(): Promise<void> {
    this.view?.dispose();
    this.view = null;
    this.container?.remove();
  }

  togglePlay(): void {
    controlStore.togglePlay();
  }

  step(): void {
    controlStore.step();
  }

  stop(): void {
    controlStore.stop();
  }
}

export const controlBar = new ControlBar();
registry.register(controlBar);
