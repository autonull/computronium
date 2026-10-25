/** Cell Drawer — Slide-in Detail Panel. */

import { registry } from "./components/registry.js";
import { panels, registerPanel, closeButton } from "./panels.js";
import { createPanelShell } from "./shell.js";
import { PALETTE, ARM_COLORS } from "./colors.js";
import type { CellData } from "./cell-data.js";
import type { Component } from "./components/registry.js";
import type { JsonValue } from "./layout/types.js";

export function createCellDrawerBody(): string {
  return `<div id="drawer-content"></div>`;
}

/** A cell drawer bound to one root element and its own subscriptions. */
export class CellDrawerView {
  private content: HTMLElement | null = null;
  private currentData: CellData | null = null;
  private readonly disposers: (() => void)[] = [];

  constructor(
    private readonly root: HTMLElement,
    _state: JsonValue = null,
  ) {
    this.content = root.querySelector("#drawer-content")!;
    this.disposers.push(
      () => window.removeEventListener("cell-selected", this.onCellSelected as EventListener),
      () => window.removeEventListener("keydown", this.onKeyDown),
    );
    window.addEventListener("cell-selected", this.onCellSelected as EventListener);
    window.addEventListener("keydown", this.onKeyDown);
  }

  dispose(): void {
    for (const dispose of this.disposers) dispose();
    this.disposers.length = 0;
    this.stopSparkline();
    this.currentData = null;
  }

  update(state: JsonValue): void {
    // Could receive new cell data via state
  }

  private onKeyDown = (event: KeyboardEvent): void => {
    if (event.key === "Escape" && this.currentData) this.hide();
    if (event.key === "d" && !event.shiftKey && !event.ctrlKey && !event.metaKey && !event.altKey) {
      const t = event.target as HTMLElement | null;
      if (!t || !["INPUT", "SELECT", "TEXTAREA"].includes(t.tagName)) {
        event.preventDefault();
        this.isOpen() ? this.hide() : (this.currentData && this.show(this.currentData));
      }
    }
  };

  isOpen(): boolean {
    return this.root && !this.root.classList.contains("panel-hidden");
  }

  hasCellSelected(): boolean {
    return this.currentData !== null;
  }

  get currentCell(): CellData | null {
    return this.currentData;
  }

  private onCellSelected = (event: CustomEvent): void => {
    this.show(event.detail);
  };

  show(data: CellData): void {
    this.currentData = data;
    this.renderContent(data);
    panels.toggle("cell-drawer");
    this.startSparkline(data);
  }

  hide(): void {
    panels.toggle("cell-drawer");
    this.stopSparkline();
    this.currentData = null;
  }

  private renderContent(data: CellData): void {
    if (!this.content) return;

    const { coordinate, metrics, status } = data;
    const armColor = ARM_COLORS[coordinate.credit] || PALETTE.gradient;
    const valAcc = metrics?.val_acc ?? 0;
    const nSeeds = metrics?.n_seeds ?? 0;
    const chance = data.chance ?? 0.1;
    const requiredSeeds = data.requiredSeeds ?? 0;

    let verdict = "UNMEASURED";
    let verdictColor = PALETTE.legal_unmeasured;
    if (status === "void") {
      verdict = "VOID";
      verdictColor = PALETTE.void;
    }
    if (status === "measured") {
      if (valAcc <= chance) {
        verdict = "REJECTED";
        verdictColor = PALETTE.rejected;
      } else if (requiredSeeds > 0 && nSeeds < requiredSeeds) {
        verdict = "INSUFFICIENT";
        verdictColor = PALETTE.insufficient;
      } else if (valAcc > chance + 0.1) {
        verdict = "PASSED";
        verdictColor = PALETTE.passed;
      } else {
        verdict = "INSUFFICIENT";
        verdictColor = PALETTE.insufficient;
      }
    }

    const seedsToClaim = status === "measured" && requiredSeeds > 0 ? Math.max(0, requiredSeeds - nSeeds) : "N/A";

    const states = this.actionStates(data);
    const repText = data.status === "measured" ? "Queue Rest" : "Queue";
    const repHint = states.replicate ? "⇧R" : "";
    const preHint = states.preregister ? "⇧P" : "";
    const queHint = states.quest ? "⇧Q" : "";

    this.content.innerHTML = `
      <style>
        .coord-chip { background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 12px; font-size: 11px; color: var(--text-primary); padding: 3px 8px; }
        .coord-chip.credit { background: ${armColor}22; border-color: ${armColor}88; color: ${armColor}; }
        .metric-label { font-size: 10px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 3px; }
        .metric-value { font-size: 20px; font-weight: 600; color: var(--text-primary); font-variant-numeric: tabular-nums; }
        .metric-sub { font-size: 11px; color: var(--text-secondary); margin-top: 2px; }
        .verdict-badge { background: ${verdictColor}22; border: 1px solid ${verdictColor}88; border-radius: 12px; font-size: 10px; font-weight: 600; color: ${verdictColor}; text-transform: uppercase; padding: 4px 10px; }
        .progress-bar { height: 4px; background: var(--bg); border-radius: 2px; overflow: hidden; margin-top: 6px; }
        .progress-fill { height: 100%; width: ${Math.min(100, (valAcc / (chance * 2)) * 100)}%; background: linear-gradient(90deg, ${PALETTE.rejected}, ${PALETTE.insufficient}, ${PALETTE.passed}); border-radius: 2px; }
        .seeds-box { padding: 12px; background: var(--bg-tertiary); border-radius: 6px; text-align: center; }
        .seeds-value { font-size: 28px; font-weight: 700; color: ${PALETTE.insufficient}; line-height: 1; }
        .seeds-sub { font-size: 10px; color: var(--text-secondary); margin-top: 2px; }
        .action-row { display: flex; gap: 8px; margin-top: 8px; }
        .drawer-btn { flex: 1; padding: 10px 12px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 6px; color: var(--text-secondary); font-size: 11px; font-weight: 500; cursor: not-allowed; white-space: nowrap; display: flex; align-items: center; justify-content: center; gap: 6px; }
        .drawer-btn:not(:disabled) { cursor: pointer; color: var(--text-primary); }
        .drawer-btn:not(:disabled):hover { background: var(--border); border-color: var(--border-bright); }
        .drawer-btn:disabled { opacity: 0.4; }
        .drawer-btn-primary:not(:disabled) { background: var(--gradient)22; border-color: var(--gradient)66; color: var(--gradient); }
        .drawer-btn-primary:not(:disabled):hover { background: var(--gradient)33; border-color: var(--gradient); }
        .drawer-btn .kbd { font-family: monospace; font-size: 9px; padding: 1px 4px; background: var(--bg); border: 1px solid var(--border); border-radius: 3px; color: var(--text-muted); }
        .drawer-input { padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 6px; color: var(--text-primary); font-size: 11px; font-family: monospace; flex: 1; }
        .drawer-input:focus { outline: none; border-color: var(--gradient); box-shadow: 0 0 0 2px var(--gradient)33; }
        .drawer-note { font-size: 11px; color: var(--text-secondary); line-height: 1.5; min-height: 36px; margin-bottom: 4px; }
        .drawer-status { font-size: 11px; color: var(--text-secondary); min-height: 18px; margin-top: 4px; }
        .hint-row { font-size: 10px; color: var(--text-muted); margin-top: 8px; }
      </style>

      <div style="margin-bottom: 16px;">
        <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px;">
          ${Object.entries(coordinate)
            .filter(([, v]) => v)
            .map(
              ([axis, value]) => `
              <span class="coord-chip ${axis === "credit" ? "credit" : ""}" data-axis="${axis}">
                ${axis}=${value}
              </span>
            `,
            )
            .join("")}
        </div>
      </div>

      ${
        metrics
          ? `
        <div style="margin-bottom: 16px;">
          <div class="metric-label">Validation Accuracy</div>
          <div class="metric-value">${valAcc.toFixed(3)}</div>
          <div class="metric-sub">± ${(metrics.val_acc_std ?? 0).toFixed(3)} (n=${nSeeds})</div>
        </div>
      `
          : ""
      }

      <div style="margin-bottom: 16px; padding: 12px; background: var(--bg-tertiary); border-radius: 6px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
          <span class="verdict-badge">${verdict}</span>
          <span style="font-size: 12px; color: var(--text-secondary);">Chance: ${chance}</span>
        </div>
        ${
          data.voidReason
            ? `<div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px;">${data.voidReason}</div>`
            : ""
        }
        <div class="progress-bar"><div class="progress-fill"></div></div>
      </div>

      ${
        status === "measured"
          ? `
        <div class="seeds-box" style="margin-bottom: 16px;">
          <div class="metric-label">Seeds to Claim</div>
          <div class="seeds-value">${seedsToClaim}</div>
          <div class="seeds-sub">(d=0.5, α=0.05)</div>
        </div>
      `
          : ""
      }

      ${
        metrics?.walltime_s
          ? `
        <div style="margin-bottom: 16px; padding: 12px; background: var(--bg-tertiary); border-radius: 6px;">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 12px;">
            <div>
              <div style="color: var(--text-secondary);">Wall Time</div>
              <div style="font-size: 16px; font-weight: 600; color: var(--text-primary);">${metrics.walltime_s.toFixed(1)}s</div>
            </div>
            <div>
              <div style="color: var(--text-secondary);">Parameters</div>
              <div style="font-size: 16px; font-weight: 600; color: var(--text-primary);">${((metrics.param_count ?? 0) / 1000).toFixed(1)}K</div>
            </div>
          </div>
        </div>
      `
          : ""
      }

      <div style="margin-bottom: 16px;">
        <div style="font-size: 10px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">Training Curve</div>
        <div id="sparkline-container" style="width: 100%; height: 110px; background: var(--bg); border: 1px solid var(--border); border-radius: 6px; overflow: hidden;"></div>
      </div>

      <div style="padding-top: 12px; border-top: 1px solid var(--border);">
        <div id="drawer-action-note" class="drawer-note"></div>
        <div class="action-row">
          <button class="drawer-btn drawer-btn-primary" data-action="replicate" ${!states.replicate ? "disabled" : ""}>
            <span>${repText}</span>
            ${repHint ? `<span class="kbd">${repHint}</span>` : ""}
          </button>
          <button class="drawer-btn" data-action="preregister" ${!states.preregister ? "disabled" : ""}>
            <span>Preregister</span>
            ${preHint ? `<span class="kbd">${preHint}</span>` : ""}
          </button>
          <button class="drawer-btn" data-action="quest" ${!states.quest ? "disabled" : ""}>
            <span>Adopt as Quest</span>
            ${queHint ? `<span class="kbd">${queHint}</span>` : ""}
          </button>
        </div>
        <div style="display: flex; gap: 8px; align-items: center; margin-top: 8px;">
          <input id="drawer-threshold" class="drawer-input" type="number" step="0.001" placeholder="material effect (auto)" />
          <span style="font-size: 10px; color: var(--text-muted); white-space: nowrap;">auto = measured − chance</span>
        </div>
        <div id="drawer-status" class="drawer-status"></div>
        <div class="hint-row">Shortcuts: ⇧R replicate · ⇧P preregister · ⇧Q quest · Esc close · D toggle drawer</div>
      </div>
    `;

    this.wireActions(data);
  }

  private actionStates(data: CellData): Record<string, boolean> {
    if (data.status === "void") return { replicate: false, preregister: false, quest: false };
    const measured = data.status === "measured";
    const seeds = data.metrics?.n_seeds ?? 0;
    const required = data.requiredSeeds ?? 0;
    const missing = required > 0 ? Math.max(0, required - seeds) : 0;
    return { replicate: missing > 0 || !measured, preregister: measured, quest: !measured };
  }

  private wireActions(data: CellData): void {
    const content = this.content;
    if (!content) return;

    const states = this.actionStates(data);
    const buttons = content.querySelectorAll<HTMLButtonElement>(".drawer-btn[data-action]");

    buttons.forEach((button) => {
      const action = button.dataset.action ?? "";
      const enabled = states[action] === true;
      button.disabled = !enabled;
      button.addEventListener("click", () => { void this.runAction(action, data); });
    });

    const note = content.querySelector("#drawer-action-note");
    if (note) note.textContent = this.actionNote(data);
  }

  private actionNote(data: CellData): string {
    if (!data.runId) return "This cell belongs to no run yet — nothing to queue or register.";
    if (data.status === "void") return `The system refuses this cell.${data.voidReason ? ` ${data.voidReason}` : ""}`;
    if (data.status === "measured") {
      const seeds = data.metrics?.n_seeds ?? 0;
      const required = data.requiredSeeds ?? 0;
      const missing = Math.max(0, required - seeds);
      if (missing > 0) return `Queue Rest adds ${missing} more seeds to reach the claim threshold (${required} needed). Preregister locks in this cell's protocol for a confirmatory run.`;
      return `This cell has enough seeds for a claim. Preregister locks in the protocol for a confirmatory run.`;
    }
    const outside = data.inDeclaration === false ? " (outside this run's declaration)" : "";
    const seeds = data.requiredSeeds ?? 0;
    return `Queue measures this cell (${seeds} seeds). Adopt as Quest writes the question first, then queues a new confirming run.${outside}`;
  }

  private setStatus(message: string, isError = false): void {
    const status = this.content?.querySelector("#drawer-status");
    if (!status) return;
    status.textContent = message;
    (status as HTMLElement).style.color = isError ? PALETTE.rejected : PALETTE.text_secondary;
  }

  private async runAction(action: string, data: CellData): Promise<void> {
    if (!data.runId) { this.setStatus("This cell belongs to no run yet.", true); return; }
    this.setStatus("Sending…");
    try {
      const res = await fetch("/api/cell/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ run_id: data.runId, coordinate: data.coordinate, action }),
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok) { this.setStatus(body.error || "Action failed", true); return; }
      this.setStatus(body.message || "Done");
      if (action === "replicate" || action === "quest") this.hide();
    } catch (e) { this.setStatus("Network error", true); }
  }

  private startSparkline(data: CellData): void {
    const container = this.content?.querySelector("#sparkline-container");
    if (!container || !(data.metrics as any)?.history) return;
    // Sparkline rendering would go here - simplified for now
  }

  private stopSparkline(): void {
    // Cleanup
  }

  replicateSelected(): void {
    if (this.currentData) this.runAction("replicate", this.currentData);
  }

  preregisterSelected(): void {
    if (this.currentData) this.runAction("preregister", this.currentData);
  }

  adoptQuestSelected(): void {
    if (this.currentData) this.runAction("quest", this.currentData);
  }
}

/** The legacy singleton panel used by GoldenLayout until P2. */
export class CellDrawer implements Component {
  name = "CellDrawer";

  private panel: HTMLElement | null = null;
  private view: CellDrawerView | null = null;

  async init(): Promise<void> {
    this.panel = createPanelShell({
      id: "cell-drawer",
      title: "Cell Details",
      glyph: "◧",
      key: "d",
      body: createCellDrawerBody(),
      dock: "floating",
      defaultOpen: false,
    });

    this.view = new CellDrawerView(this.panel);
    registerPanel(
      "cell-drawer",
      "cell drawer",
      "◧",
      () => this.hide(),
      () => this.isOpen(),
      "d",
    );
  }

  async destroy(): Promise<void> {
    this.view?.dispose();
    this.view = null;
    this.panel?.remove();
  }

  isOpen(): boolean {
    return this.panel ? !this.panel.classList.contains("panel-hidden") : false;
  }

  hasCellSelected(): boolean {
    return this.view?.hasCellSelected() ?? false;
  }

  get currentCell(): CellData | null {
    return this.view?.currentCell ?? null;
  }

  onChange(listener: () => void): () => void {
    // Legacy compatibility
    return () => {};
  }

  replicateSelected(): void {
    this.view?.replicateSelected();
  }

  preregisterSelected(): void {
    this.view?.preregisterSelected();
  }

  adoptQuestSelected(): void {
    this.view?.adoptQuestSelected();
  }

  hide(): void {
    this.view?.hide();
  }

  private show(data: CellData): void {
    this.view?.show(data);
  }
}

export const cellDrawer = new CellDrawer();
registry.register(cellDrawer);