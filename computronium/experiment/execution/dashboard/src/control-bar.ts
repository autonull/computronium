/** Simple control bar — play/step/stop, ceiling slider, status, quick run. */

import { controlStore, type ControlPayload } from "./stores/control.js";

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
      .ctrl .quick-run { padding: 6px 12px; font-size: 11px; background: var(--gradient)22; border: 1px solid var(--gradient)66; border-radius: 4px; color: var(--gradient); cursor: pointer; position: relative; }
      .ctrl .quick-run:hover { background: var(--gradient)33; }
      .ctrl .quick-run:disabled { opacity: 0.4; cursor: not-allowed; }
      .ctrl .quick-run:hover .quick-run-inline,
      .ctrl .quick-run:focus-within .quick-run-inline { display: block; }
      .ctrl .quick-run-inline { display: none; position: absolute; bottom: 100%; right: 0; margin-bottom: 6px; padding: 10px 12px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 6px; font-size: 10px; color: var(--text-secondary); white-space: nowrap; box-shadow: 0 -4px 16px rgba(0,0,0,0.4); z-index: 10; }
      .ctrl .quick-run-inline .summary-row { display: flex; gap: 16px; margin: 4px 0; }
      .ctrl .quick-run-inline .summary-label { color: var(--text-muted); font-size: 9px; text-transform: uppercase; letter-spacing: 0.05em; }
      .ctrl .quick-run-inline .summary-value { color: var(--text-primary); font-weight: 600; font-size: 10px; }
      
      /* Responsive: <1200px */
      @media (max-width: 1199px) {
        .ctrl .meter-label { display: none; }
        .ctrl .slider { width: 80px; }
        .ctrl .status { min-width: 60px; font-size: 10px; }
        .ctrl .quick-run { padding: 6px 8px; font-size: 10px; }
        .ctrl .verb-group { display: flex; gap: 2px; }
      }
    </style>
    <div class="ctrl" style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
      <div class="verb-group" style="display: flex; gap: 2px;">
        <button class="verb primary" data-act="play" title="Play">▶</button>
        <button class="verb" data-act="step" title="Step one batch" disabled>⏭</button>
        <button class="verb danger" data-act="stop" title="Stop run">⏹</button>
      </div>
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
      <button class="quick-run" data-act="quick-run" title="Start quick run (diverse cells in ~30s)" disabled>
        Quick Run
        <div class="quick-run-inline">
          <div class="summary-row"><span class="summary-label">Profile</span><span class="summary-value">quick-run</span></div>
          <div class="summary-row"><span class="summary-label">Fidelity</span><span class="summary-value">L0</span></div>
          <div class="summary-row"><span class="summary-label">Seeds</span><span class="summary-value">1</span></div>
          <div class="summary-row"><span class="summary-label">Arms</span><span class="summary-value">6</span></div>
          <div class="summary-row"><span class="summary-label">Est. time</span><span class="summary-value">~30s</span></div>
        </div>
      </button>
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
  private readonly quickRunBtn: HTMLButtonElement;
  private readonly unsubscribe: () => void;

  constructor(
    private readonly root: HTMLElement,
    openControlPanel: () => void = () => {},
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
    this.quickRunBtn = this.query("[data-act=quick-run]");

    this.playBtn.addEventListener("click", () => controlStore.togglePlay());
    this.stepBtn.addEventListener("click", () => controlStore.step());
    this.stopBtn.addEventListener("click", () => {
      if (confirm("Stop the run?")) controlStore.stop();
    });
    this.slider.addEventListener("change", () =>
      controlStore.setCeiling(Number(this.slider.value)),
    );
    this.quickRunBtn.addEventListener("click", () => this.startQuickRun());
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

  private async startQuickRun(): Promise<void> {
    this.quickRunBtn.disabled = true;
    this.quickRunBtn.innerHTML = `<span class="ctrl-spinner" style="display:inline-block;width:14px;height:14px;border:2px solid currentColor;border-right-color:transparent;border-radius:50%;animation:ctrl-spin 0.8s linear infinite;margin-right:6px;vertical-align:middle;"></span>Starting...`;
    if (!document.getElementById("ctrl-spinner-style")) {
      const style = document.createElement("style");
      style.id = "ctrl-spinner-style";
      style.textContent = "@keyframes ctrl-spin{to{transform:rotate(360deg)}}";
      document.head.appendChild(style);
    }
    try {
      const response = await fetch("/api/runs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profile: "quick-run" }),
      });
      const result = await response.json();
      if (result.started) {
        this.showToast("Run complete — tracking cells…");
        this.quickRunBtn.textContent = "Started";
        setTimeout(() => {
          this.quickRunBtn.textContent = "Quick Run";
          this.quickRunBtn.disabled = false;
        }, 2000);
      } else {
        this.quickRunBtn.textContent = "No Queue";
        this.quickRunBtn.title = result.error || "No campaign queue attached";
        setTimeout(() => {
          this.quickRunBtn.textContent = "Quick Run";
          this.quickRunBtn.disabled = false;
        }, 3000);
      }
    } catch {
      this.quickRunBtn.textContent = "Error";
      setTimeout(() => {
        this.quickRunBtn.textContent = "Quick Run";
        this.quickRunBtn.disabled = false;
      }, 2000);
    }
  }

  private showToast(message: string): void {
    const overlay = document.getElementById("ui-overlay");
    if (!overlay) return;
    const toast = document.createElement("div");
    toast.style.cssText = `
      position: fixed; bottom: 24px; right: 24px; z-index: 1000; pointer-events: auto;
      padding: 12px 20px; background: var(--bg-secondary); border: 1px solid var(--border);
      border-radius: 8px; box-shadow: 0 8px 32px rgba(0,0,0,0.5); font-size: 12px;
      color: var(--text-primary); animation: ctrl-toast-in 0.2s ease-out;
    `;
    toast.textContent = message;
    if (!document.getElementById("ctrl-toast-style")) {
      const style = document.createElement("style");
      style.id = "ctrl-toast-style";
      style.textContent = "@keyframes ctrl-toast-in{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}";
      document.head.appendChild(style);
    }
    overlay.appendChild(toast);
    setTimeout(() => {
      toast.style.animation = "ctrl-toast-in 0.2s ease-out reverse";
      setTimeout(() => toast.remove(), 200);
    }, 3000);
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

    // Enable quick-run button when no run is active or when run is paused
    const hasActiveRun = p.readable && !!s && !s.stage.includes("idle");
    this.quickRunBtn.disabled = hasActiveRun && !c.paused;
    this.quickRunBtn.title = hasActiveRun && !c.paused
      ? "Pause current run first"
      : "Start quick run (diverse cells in ~30s)";
  }
}