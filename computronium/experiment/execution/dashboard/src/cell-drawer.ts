/** Cell Drawer — Slide-in Detail Panel (TODO68 Phase 2). */

import { registry } from "./components/registry.js";
import { registerPanel } from "./panels.js";
import { PALETTE, ARM_COLORS } from "./palette.js";
import type { CellData } from "./cell-data.js";
import type { Component } from "./components/registry.js";

export class CellDrawer implements Component {
  name = "CellDrawer";

  private panel: HTMLElement | null = null;
  private content: HTMLElement | null = null;
  private sparklineCanvas: HTMLCanvasElement | null = null;
  private currentData: CellData | null = null;

  async init(): Promise<void> {
    this.createPanel();
    this.setupEvents();
    registerPanel(
      "cell-drawer",
      "cell drawer",
      "◧",
      () => this.hide(),
      () => this.isOpen(),
    );
    console.log("[CellDrawer] Initialized");
  }

  async destroy(): Promise<void> {
    this.stopSparkline();
    this.panel?.remove();
    window.removeEventListener(
      "cell-selected",
      this.onCellSelected as EventListener,
    );
    window.removeEventListener("keydown", this.onKeyDown);
  }

  private createPanel(): void {
    const overlay = document.getElementById("ui-overlay");
    if (!overlay) return;

    this.panel = document.createElement("div");
    this.panel.id = "cell-drawer";
    this.panel.style.cssText = `
      position: fixed;
      top: 0;
      right: 0;
      width: 380px;
      height: 100%;
      background: var(--bg-secondary);
      border-left: 1px solid var(--border);
      transform: translateX(100%);
      transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      z-index: 200;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    `;

    this.panel.innerHTML = `
      <div id="drawer-header" style="
        padding: 16px;
        border-bottom: 1px solid var(--border);
        display: flex;
        align-items: center;
        justify-content: space-between;
      ">
        <h3 style="margin: 0; font-size: 14px; font-weight: 600;">Cell Details</h3>
        <button id="drawer-close" style="
          background: none;
          border: none;
          color: var(--text-secondary);
          font-size: 20px;
          cursor: pointer;
          padding: 4px;
          line-height: 1;
        ">&times;</button>
      </div>
      <div id="drawer-content" style="
        flex: 1;
        overflow-y: auto;
        padding: 16px;
      "></div>
    `;

    overlay.appendChild(this.panel);
    this.content = this.panel.querySelector("#drawer-content")!;

    this.panel
      .querySelector("#drawer-close")!
      .addEventListener("click", () => this.hide());
  }

  private setupEvents(): void {
    window.addEventListener(
      "cell-selected",
      this.onCellSelected as EventListener,
    );
    window.addEventListener("keydown", this.onKeyDown);
  }

  private onKeyDown = (event: KeyboardEvent): void => {
    if (event.key === "Escape" && this.currentData) {
      this.hide();
    }
  };

  /** The drawer covers the right-hand panels; they step aside for it. */
  private shiftPanels(open: boolean): void {
    const right = open ? 400 : 44;
    ["hud", "chart-column"].forEach((id) => {
      document.getElementById(id)?.style.setProperty("right", `${right}px`);
    });
  }

  /** Whether the drawer is showing. */
  isOpen(): boolean {
    if (!this.panel) return false;
    return this.panel.style.transform === "translateX(0)";
  }

  private onCellSelected = (event: CustomEvent): void => {
    this.show(event.detail);
  };

  show(data: CellData): void {
    this.currentData = data;
    this.renderContent(data);
    this.panel!.style.transform = "translateX(0)";
    this.shiftPanels(true);
    this.startSparkline(data);
  }

  hide(): void {
    this.panel!.style.transform = "translateX(100%)";
    this.shiftPanels(false);
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

    // Verdict: what the cell's own evidence supports. A cell with fewer
    // seeds than the gate asks for cannot support a claim, however good its
    // mean looks — the run's verdict is INSUFFICIENT, and so is the cell's.
    // A cell nobody measured has no verdict: it is a gap, not a result.
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

    // Seeds to claim: the power analysis asks for a fixed seed count
    const seedsToClaim =
      status === "measured" && requiredSeeds > 0
        ? Math.max(0, requiredSeeds - nSeeds)
        : "N/A";

    this.content.innerHTML = `
      <div style="margin-bottom: 20px;">
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;">
          ${Object.entries(coordinate)
            .filter(([, v]) => v)
            .map(
              ([axis, value]) => `
              <span style="
                padding: 4px 10px;
                background: ${axis === "credit" ? armColor + "22" : "var(--bg-tertiary)"};
                border: 1px solid ${axis === "credit" ? armColor + "88" : "var(--border)"};
                border-radius: 12px;
                font-size: 11px;
                color: ${axis === "credit" ? armColor : "var(--text-primary)"};
              ">
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
        <div style="margin-bottom: 20px;">
          <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 4px;">VALIDATION ACCURACY</div>
          <div style="
            font-size: 42px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            color: var(--text-primary);
            line-height: 1;
          ">${valAcc.toFixed(3)}</div>
          <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">
            ± ${(metrics.val_acc_std ?? 0).toFixed(3)} (n=${nSeeds})
          </div>
        </div>
      `
          : ""
      }

      <div style="margin-bottom: 20px; padding: 12px; background: var(--bg-tertiary); border-radius: 6px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
          <span style="
            padding: 4px 10px;
            background: ${verdictColor}22;
            border: 1px solid ${verdictColor}88;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            color: ${verdictColor};
            text-transform: uppercase;
          ">${verdict}</span>
          <span style="font-size: 12px; color: var(--text-secondary);">Chance level: ${chance}</span>
        </div>
        ${
          data.voidReason
            ? `<div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">${data.voidReason}</div>`
            : ""
        }
        <div style="height: 4px; background: var(--bg); border-radius: 2px; overflow: hidden;">
          <div style="
            width: ${Math.min(100, (valAcc / (chance * 2)) * 100)}%;
            height: 100%;
            background: linear-gradient(90deg, ${PALETTE.rejected}, ${PALETTE.insufficient}, ${PALETTE.passed});
            border-radius: 2px;
          "></div>
        </div>
      </div>

      ${
        status === "measured"
          ? `
        <div style="margin-bottom: 20px;">
          <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px;">SEEDS TO CLAIM</div>
          <div style="font-size: 24px; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: ${PALETTE.insufficient};">
            ${seedsToClaim}
          </div>
          <div style="font-size: 11px; color: var(--text-secondary);">(d=0.5, α=0.05)</div>
        </div>
      `
          : ""
      }

      ${
        metrics?.walltime_s
          ? `
        <div style="margin-bottom: 20px; padding: 12px; background: var(--bg-tertiary); border-radius: 6px;">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 12px;">
            <div>
              <div style="color: var(--text-secondary);">Wall Time</div>
              <div style="font-family: 'JetBrains Mono', monospace; font-weight: 600;">${metrics.walltime_s.toFixed(1)}s</div>
            </div>
            <div>
              <div style="color: var(--text-secondary);">Parameters</div>
              <div style="font-family: 'JetBrains Mono', monospace; font-weight: 600;">${((metrics.param_count ?? 0) / 1000).toFixed(1)}K</div>
            </div>
          </div>
        </div>
      `
          : ""
      }

      <!-- Mini 3D Sparkline Container -->
      <div style="margin-bottom: 20px;">
        <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px;">TRAINING CURVE</div>
        <div id="sparkline-container" style="
          width: 100%;
          height: 120px;
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: 6px;
          overflow: hidden;
        "></div>
      </div>

      <!-- Actions -->
      <div style="
        display: flex;
        flex-direction: column;
        gap: 10px;
        padding-top: 16px;
        border-top: 1px solid var(--border);
      ">
        <div id="drawer-action-note" style="font-size: 11px; color: var(--text-secondary); line-height: 1.5; min-height: 36px;">
        </div>
        <div style="display: flex; gap: 8px;">
          <button class="drawer-btn drawer-btn-primary" data-action="replicate" style="flex: 1;">Queue Rest</button>
          <button class="drawer-btn" data-action="preregister" style="flex: 1;">Preregister</button>
          <button class="drawer-btn" data-action="quest" style="flex: 1;">Adopt as Quest</button>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
          <input id="drawer-threshold" class="drawer-input" type="number" step="0.001"
            placeholder="material effect (auto)" style="flex: 1;" />
          <span id="drawer-threshold-hint" style="font-size: 10px; color: var(--text-muted); white-space: nowrap;">auto = measured − chance</span>
        </div>
        <div id="drawer-status" style="font-size: 11px; color: var(--text-secondary); line-height: 1.5; min-height: 18px;"></div>
      </div>
    `;

    // Add button styles
    const style = document.createElement("style");
    style.textContent = `
      .drawer-btn {
        padding: 10px 12px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 6px;
        color: var(--text-secondary);
        font-size: 11px;
        font-weight: 500;
        cursor: not-allowed;
        transition: all var(--motion-fast) var(--ease-out);
        white-space: nowrap;
      }
      .drawer-btn:not(:disabled):hover {
        background: var(--border);
        color: var(--text-primary);
        border-color: var(--border-bright);
        transform: translateY(-1px);
      }
      .drawer-btn:not(:disabled):active {
        transform: translateY(0) scale(0.98);
      }
      .drawer-btn:not(:disabled) {
        cursor: pointer;
        color: var(--text-primary);
      }
      .drawer-btn:disabled {
        opacity: 0.4;
      }
      .drawer-btn-primary:not(:disabled) {
        background: var(--gradient)22;
        border-color: var(--gradient)66;
        color: var(--gradient);
      }
      .drawer-btn-primary:not(:disabled):hover {
        background: var(--gradient)33;
        border-color: var(--gradient);
        color: var(--gradient);
      }
      .drawer-input {
        padding: 8px 10px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 6px;
        color: var(--text-primary);
        font-size: 11px;
        font-family: 'JetBrains Mono', monospace;
        transition: border-color var(--motion-fast), box-shadow var(--motion-fast);
      }
      .drawer-input:focus-visible {
        outline: none;
        border-color: var(--gradient);
        box-shadow: 0 0 0 2px var(--gradient)33;
      }
    `;
    this.content.appendChild(style);

    this.wireActions(data);
  }

  /** What the three verbs do to this cell, and which of them apply. */
  private actionStates(data: CellData): Record<string, boolean> {
    // The system refuses a void cell, and the verbs refuse it too: the mark
    // on the picture and the behaviour of the dashboard agree.
    if (data.status === "void") {
      return { replicate: false, preregister: false, quest: false };
    }
    const measured = data.status === "measured";
    const seeds = data.metrics?.n_seeds ?? 0;
    const required = data.requiredSeeds ?? 0;
    const missing = required > 0 ? Math.max(0, required - seeds) : 0;

    return {
      replicate: missing > 0 || !measured,
      preregister: measured,
      quest: !measured,
    };
  }

  private wireActions(data: CellData): void {
    const content = this.content;
    if (!content) return;

    const states = this.actionStates(data);
    const buttons = content.querySelectorAll<HTMLButtonElement>(
      ".drawer-btn[data-action]",
    );

    buttons.forEach((button) => {
      const action = button.dataset.action ?? "";
      const enabled = states[action] === true;
      button.disabled = !enabled;
      button.addEventListener("click", () => {
        void this.runAction(action, data);
      });
    });

    const replicate = content.querySelector<HTMLButtonElement>(
      '.drawer-btn[data-action="replicate"]',
    );
    if (replicate) {
      replicate.textContent = data.status === "measured" ? "Queue Rest" : "Queue";
    }

    const note = content.querySelector("#drawer-action-note");
    if (note) note.textContent = this.actionNote(data);
  }

  private actionNote(data: CellData): string {
    if (!data.runId) {
      return "This cell belongs to no run yet — nothing to queue or register.";
    }
    if (data.status === "void") {
      return `The system refuses this cell.${data.voidReason ? ` ${data.voidReason}` : ""}`;
    }
    if (data.status === "measured") {
      const seeds = data.metrics?.n_seeds ?? 0;
      const required = data.requiredSeeds ?? 0;
      const missing = Math.max(0, required - seeds);
      if (missing > 0) {
        return `Queue Rest adds ${missing} more seeds to reach the claim threshold (${required} needed). Preregister locks in this cell's protocol for a confirmatory run.`;
      }
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
    (status as HTMLElement).style.color = isError
      ? PALETTE.rejected
      : PALETTE.text_secondary;
  }

  private async runAction(
    action: string,
    data: CellData,
  ): Promise<void> {
    if (!data.runId) {
      this.setStatus("This cell belongs to no run yet.", true);
      return;
    }

    const buttons = Array.from(
      this.content?.querySelectorAll<HTMLButtonElement>(".drawer-btn") ?? [],
    );
    buttons.forEach((button) => {
      button.disabled = true;
    });
    this.setStatus("Working…");

    const thresholdInput = this.content?.querySelector<HTMLInputElement>(
      "#drawer-threshold",
    );
    const threshold = thresholdInput?.value ? Number(thresholdInput.value) : null;
    const body: Record<string, unknown> = { coordinate: data.coordinate };
    if (threshold !== null && Number.isFinite(threshold)) {
      body.threshold = threshold;
    }

    try {
      const response = await fetch(`/api/cells/${data.runId}/${action}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const payload = await response.json();
      if (!response.ok) {
        this.setStatus(payload?.error ?? "The action failed.", true);
        return;
      }
      this.setStatus(this.actionSummary(action, payload));
    } catch (error) {
      this.setStatus(`The action failed: ${String(error)}`, true);
    } finally {
      buttons.forEach((button) => {
        button.disabled = false;
      });
    }
  }

  private actionSummary(action: string, payload: any): string {
    if (action === "replicate") {
      return `Queued campaign ${payload.campaign_id}: ${payload.measurements} measurements in a plan of ${payload.plan}.`;
    }
    const written = payload.written ? "Registered" : "Already registered";
    const registered = `${written} ${payload.path} — commit it; the run that follows it can be confirmatory.`;
    if (action !== "quest") return registered;
    if (!payload.campaign_id) {
      return `${registered} No campaign queue is attached, so nothing is scheduled.`;
    }
    return `${registered} Queued campaign ${payload.campaign_id}: ${payload.measurements} measurements in a plan of ${payload.plan}, in a new run.`;
  }

  /** Lightweight 2D canvas sparkline for the training curve. */
  private startSparkline(data: CellData): void {
    const container = document.getElementById("sparkline-container");
    if (!container) return;

    this.stopSparkline();

    const curve = data.curve ?? [];
    if (curve.length === 0) {
      container.innerHTML = `
        <div style="
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 11px;
          color: var(--text-muted);
          text-align: center;
          padding: 0 12px;
        ">No convergence curve recorded for this cell.</div>
      `;
      return;
    }

    const canvas = document.createElement("canvas");
    canvas.style.width = "100%";
    canvas.style.height = "100%";
    container.appendChild(canvas);

    const ctx = canvas.getContext("2d")!;
    const dpr = Math.min(window.devicePixelRatio, 2);
    const rect = container.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);
    const width = rect.width;
    const height = rect.height;

    const chance = data.chance ?? 0.1;
    const values = curve.map((p) => p.val_acc);
    const low = Math.min(chance, ...values);
    const high = Math.max(...values, chance);
    const span = high - low || 1;
    const pad = span * 0.1;
    const yMin = low - pad;
    const yMax = high + pad;

    const toX = (i: number) => (i / (curve.length - 1 || 1)) * (width - 20) + 10;
    const toY = (v: number) => height - 10 - ((v - yMin) / (yMax - yMin)) * (height - 20);

    // Background
    ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--bg").trim() || "#0a0e14";
    ctx.fillRect(0, 0, width, height);

    // Chance line
    const chanceY = toY(chance);
    ctx.strokeStyle = PALETTE.chance_line;
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(10, chanceY);
    ctx.lineTo(width - 10, chanceY);
    ctx.stroke();
    ctx.setLineDash([]);

    // Chance label
    ctx.fillStyle = PALETTE.chance_line;
    ctx.font = "9px 'JetBrains Mono', monospace";
    ctx.textAlign = "left";
    ctx.fillText("chance", 12, chanceY - 4);

    // Curve
    const color = ARM_COLORS[data.coordinate.credit] || PALETTE.gradient;
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.beginPath();
    curve.forEach((point, i) => {
      const x = toX(i);
      const y = toY(point.val_acc);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Points
    ctx.fillStyle = color;
    curve.forEach((point, i) => {
      const x = toX(i);
      const y = toY(point.val_acc);
      ctx.beginPath();
      ctx.arc(x, y, 3, 0, Math.PI * 2);
      ctx.fill();
    });

    // Y-axis labels (min/max)
    ctx.fillStyle = PALETTE.text_muted;
    ctx.font = "9px 'JetBrains Mono', monospace";
    ctx.textAlign = "right";
    ctx.fillText(yMax.toFixed(2), 8, 14);
    ctx.fillText(yMin.toFixed(2), 8, height - 6);

    // Store for cleanup
    this.sparklineCanvas = canvas;
  }

  private stopSparkline(): void {
    if (this.sparklineCanvas) {
      this.sparklineCanvas.remove();
      this.sparklineCanvas = null;
    }
  }
}

export const cellDrawer = new CellDrawer();
registry.register(cellDrawer);
