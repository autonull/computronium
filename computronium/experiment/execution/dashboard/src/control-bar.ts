/** Simple control bar — play/step/stop, ceiling slider, status. */

import { registry } from "./components/registry.js";
import { panels, registerDisplayPanel } from "./panels.js";
import { createPanelShell } from "./shell.js";
import type { Component } from "./components/registry.js";

const POLL_MS = 500;

interface ControlState { paused: boolean; step_budget: number; max_workers: number | null; cancel: boolean; revision: number; }
interface RunStatus { run_id: string; stage: string; in_flight: number; cells_done: number; ceiling: number; }
interface ControlPayload { control: ControlState; status: RunStatus | null; readable: boolean; error: string | null; machine: { cpu_percent: number; cpu_count: number | null }; }

function createBody(): string {
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

export class ControlBar implements Component {
  name = "ControlBar";
  private container: HTMLElement | null = null;
  private playBtn: HTMLButtonElement | null = null;
  private stepBtn: HTMLButtonElement | null = null;
  private stopBtn: HTMLButtonElement | null = null;
  private slider: HTMLInputElement | null = null;
  private ceilEl: HTMLElement | null = null;
  private cellsFill: HTMLElement | null = null;
  private cellsEl: HTMLElement | null = null;
  private cpuFill: HTMLElement | null = null;
  private cpuEl: HTMLElement | null = null;
  private statusEl: HTMLElement | null = null;
  private timer: number | null = null;
  private payload: ControlPayload | null = null;

  async init(): Promise<void> {
    this.container = createPanelShell({ id: "control-bar", title: "Control Bar", glyph: "⏯", body: createBody(), dock: "bottom", defaultOpen: true, className: "control-bar-panel" });
    this.bind();
    registerDisplayPanel("control-bar", "control bar", "⏯", () => this.container);
    this.timer = window.setInterval(() => this.poll(), POLL_MS);
    await this.poll();
  }

  async destroy(): Promise<void> { if (this.timer) clearInterval(this.timer); this.container?.remove(); }

  private bind(): void {
    if (!this.container) return;
    const root = this.container;
    this.playBtn = root.querySelector("[data-act=play]")!;
    this.stepBtn = root.querySelector("[data-act=step]")!;
    this.stopBtn = root.querySelector("[data-act=stop]")!;
    this.slider = root.querySelector(".slider")!;
    this.ceilEl = root.querySelector(".ceil")!;
    this.cellsFill = root.querySelector(".cells-fill")!;
    this.cellsEl = root.querySelector(".cells")!;
    this.cpuFill = root.querySelector(".cpu-fill")!;
    this.cpuEl = root.querySelector(".cpu")!;
    this.statusEl = root.querySelector(".status")!;

    this.playBtn?.addEventListener("click", () => this.cmd({ paused: !this.payload?.control.paused }));
    this.stepBtn?.addEventListener("click", () => this.cmd({ step: true }));
    this.stopBtn?.addEventListener("click", () => { if (confirm("Stop the run?")) this.cmd({ cancel: true }); });
    this.slider?.addEventListener("change", () => this.cmd({ max_workers: Number(this.slider!.value) }));
    root.querySelector("[data-act=panel]")!.addEventListener("click", () => panels.toggle("control-panel"));
  }

  private async poll(): Promise<void> {
    try {
      const res = await fetch("/api/control");
      if (!res.ok) return;
      this.payload = await res.json();
      this.render();
    } catch { /* keep last state */ }
  }

  private async cmd(changes: Record<string, unknown>): Promise<void> {
    const rev = this.payload?.control.revision;
    try {
      const res = await fetch("/api/control", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...changes, revision: rev }) });
      if (!res.ok) { const b = await res.json().catch(() => ({})); this.setStatus(b.error || "command refused"); return; }
      await this.poll();
    } catch { this.setStatus("cannot reach server"); }
  }

  private render(): void {
    const p = this.payload; if (!p) return;
    const c = p.control, s = p.status;
    const inFlight = s?.in_flight ?? 0, ceiling = c.max_workers ?? s?.ceiling ?? 0, cpu = p.machine?.cpu_percent ?? 0;

    if (this.playBtn) {
      const paused = c.paused;
      this.playBtn.textContent = paused ? "▶" : "⏸";
      this.playBtn.classList.toggle("primary", paused);
      this.playBtn.classList.toggle("danger", !paused);
      this.playBtn.title = paused ? "Play" : "Pause";
    }
    if (this.stepBtn) {
      const can = c.paused && p.readable;
      this.stepBtn.disabled = !can;
      this.stepBtn.title = can ? "Step" : c.paused ? "Control plane not readable" : "Run not paused";
    }
    if (this.stopBtn) { this.stopBtn.disabled = !p.readable; }
    if (this.playBtn) { this.playBtn.disabled = !p.readable; if (!p.readable) this.playBtn.title = p.error || "control plane unreadable"; }

    if (this.slider) {
      const max = Math.max(1, p.machine?.cpu_count ?? 1, ceiling || 1);
      this.slider.max = String(max);
      this.slider.value = String(Math.max(1, ceiling || 1));
      this.slider.disabled = !p.readable;
    }
    if (this.ceilEl) this.ceilEl.textContent = ceiling ? String(ceiling) : "—";

    if (this.cellsFill) {
      const frac = ceiling ? Math.min(1, inFlight / ceiling) : 0;
      this.cellsFill.style.width = `${frac * 100}%`;
      this.cellsFill.style.background = frac === 0 ? "var(--promoted)" : frac < 0.5 ? "var(--promoted)" : frac < 0.85 ? "var(--warn)" : "var(--error)";
    }
    if (this.cellsEl) this.cellsEl.textContent = `${inFlight}${ceiling ? ` / ${ceiling}` : ""}`;

    if (this.cpuFill) {
      const cpc = Math.min(100, Math.max(0, cpu));
      this.cpuFill.style.width = `${cpc}%`;
      this.cpuFill.style.background = cpc < 30 ? "var(--cpu)" : cpc < 70 ? "var(--warn)" : "var(--error)";
    }
    if (this.cpuEl) this.cpuEl.textContent = `${cpu.toFixed(0)}%`;

    if (this.statusEl && p.readable) {
      this.statusEl.textContent = s ? `${s.stage.replace("s","S")} · ${s.cells_done} cells` : "no run";
    }
  }

  private setStatus(t: string): void { if (this.statusEl) this.statusEl.textContent = t; }

  togglePlay(): void { this.cmd({ paused: !this.payload?.control.paused }); }
  step(): void { this.cmd({ step: true }); }
  stop(): void { this.cmd({ cancel: true }); }
}

export const controlBar = new ControlBar();
registry.register(controlBar);