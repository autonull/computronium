/** Caption — the dashboard's voice. Shows run state, selected cell, guidance. */

import { registry } from "./components/registry.js";
import { panels, registerDisplayPanel } from "./panels.js";
import { createPanelShell } from "./shell.js";
import { wsClient } from "./ws-client.js";
import { runSelection } from "./run-selection.js";
import { cellDrawer } from "./cell-drawer.js";
import { PALETTE } from "./colors.js";
import type { Component } from "./components/registry.js";

function createBody(): string {
  return `
    <div id="caption-headline" style="font-size: 13px; font-weight: 500; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"></div>
    <div id="caption-context" style="font-size: 11px; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 2px;"></div>
    <div id="caption-detail" style="font-size: 10px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 1px;"></div>
  `;
}

export class Caption implements Component {
  name = "Caption";
  private container: HTMLElement | null = null;
  private headline: HTMLElement | null = null;
  private context: HTMLElement | null = null;
  private detail: HTMLElement | null = null;
  private lastText = "";
  private unsub: (() => void) | null = null;

  async init(): Promise<void> {
    this.container = createPanelShell({ id: "caption", title: "Caption", glyph: "◈", body: createBody(), dock: "bottom", defaultOpen: true, className: "caption-panel" });
    this.headline = this.container.querySelector("#caption-headline")!;
    this.context = this.container.querySelector("#caption-context")!;
    this.detail = this.container.querySelector("#caption-detail")!;
    registerDisplayPanel("caption", "caption", "◈", () => this.container);
    this.unsub = wsClient.onStateChange((state) => { if (state === "connected") this.render(); else this.set("Connecting…", "", ""); });
    runSelection.onChange(() => this.render());
    cellDrawer.onChange?.(() => this.render());
    this.render();
  }

  async destroy(): Promise<void> { this.unsub?.(); this.container?.remove(); }

  private render(): void {
    const run = runSelection.selected;
    const cell = cellDrawer.hasCellSelected() ? cellDrawer.currentCell : null;

    if (this.lastText) {
      this.set(this.lastText, "", "");
      return;
    }

    if (!run) {
      this.set("No run yet", "Press Z or open Control Panel to start a run", "");
      return;
    }

    const mode = run.run?.mode || "UNKNOWN";
    const profile = run.run?.profile || "—";
    const fidelity = run.run?.fidelity || "—";
    const cellsDone = run.records?.length || 0;
    const requiredSeeds = run.required_seeds || 0;

    if (cell) {
      const coord = cell.coordinate;
      const status = cell.status;
      const valAcc = cell.metrics?.val_acc ?? 0;
      const chance = cell.chance ?? 0.1;
      const coordStr = Object.entries(coord).filter(([, v]) => v).map(([k, v]) => `${k}=${v}`).join(", ");
      const verdict = status === "measured" ? (valAcc > chance + 0.1 ? "PASSED" : valAcc <= chance ? "REJECTED" : "INSUFFICIENT") : status.toUpperCase();
      const verdictColor = verdict === "PASSED" ? PALETTE.promoted : verdict === "REJECTED" ? PALETTE.rejected : PALETTE.insufficient;
      this.set(`${mode} · ${cellsDone} cells · ${profile}@${fidelity}`, `Cell: ${coordStr} · ${verdict} (${valAcc.toFixed(3)} vs ${chance})`, `Shift+R replicate · Shift+P preregister · Shift+Q quest · D toggle`);
    } else {
      this.set(`${mode} · ${cellsDone} cells · ${profile}@${fidelity}`, requiredSeeds > 0 ? `Seeds to claim: ${requiredSeeds}` : "Click a cell to inspect", "V cycle views · 1-9 pick view · Z start run · Space play/pause");
    }
  }

  set(headline: string, context = "", detail = ""): void {
    if (this.headline) this.headline.textContent = headline;
    if (this.context) this.context.textContent = context;
    if (this.detail) this.detail.textContent = detail;
  }

  notify(text: string, ctx = "", det = ""): void { this.lastText = text; this.set(text, ctx, det); }
  clear(): void { this.lastText = ""; this.render(); }
}

export const caption = new Caption();
registry.register(caption);