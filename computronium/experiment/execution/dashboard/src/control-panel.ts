/** Control Panel — the dashboard's command center, one view per instance. */

import { wsClient } from "./ws-client.js";
import { runSelection } from "./run-selection.js";
import { PALETTE } from "./colors.js";
import { workspaceStore } from "./stores/workspace.js";
import { metricsStore } from "./stores/metrics.js";
import type { JsonValue } from "./layout/types.js";

/** One profile, as the server offers it. */
interface Profile {
  name: string;
  description: string;
  stages: string[];
  fidelity: string;
  task: string;
  n_seeds: number;
  epochs: number;
  batch_limit: number;
  budget_seconds: number | null;
  param_budget: number;
  objectives: string[];
  policy: string;
  axes: { axis: string; primitives: string[] }[];
}

/** One axis, as the server offers it. */
interface Axis {
  axis: string;
  primitives: { name: string; description: string; available: boolean; unavailable_reason: string | null }[];
}

/** One campaign, as the queue holds it. */
interface Campaign {
  campaign_id: string;
  name: string;
  status: string;
  priority: string;
}

/** The six axes a cell names, in the order the ontology declares them. */
const CELL_AXES = ["substrate", "geometry", "dynamics", "plasticity", "credit", "update"] as const;

const SECTIONS = [
  { id: "new-run", title: "New Run", key: "1" },
  { id: "this-run", title: "This Run", key: "2" },
  { id: "queue", title: "The Queue", key: "3" },
  { id: "cells", title: "Cells", key: "4" },
  { id: "exports", title: "Exports", key: "5" },
] as const;

export function createControlPanelBody(): string {
  return `
    <style>
      .control-panel h4 { margin: 14px 0 6px; font-size: 10px; letter-spacing: 0.08em; color: var(--text-secondary); text-transform: uppercase; }
      .control-panel table.kv, .control-panel table.list { width: 100%; border-collapse: collapse; font-size: 11px; }
      .control-panel table.kv th, .control-panel table.list th { text-align: left; font-weight: 500; color: var(--text-secondary); padding: 2px 6px 2px 0; vertical-align: top; }
      .control-panel table.kv td, .control-panel table.list td { color: var(--text-primary); padding: 2px 6px 2px 0; vertical-align: top; }
      .control-panel .note { color: var(--text-secondary); margin: 4px 0 8px; line-height: 1.4; font-size: 11px; }
      .control-panel .row { display: flex; gap: 8px; align-items: center; margin: 4px 0; }
      .control-panel input, .control-panel select { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border); border-radius: 4px; font-size: 11px; padding: 2px 4px; min-width: 0; }
      .control-panel button.mini { background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 4px; color: var(--text-primary); font-size: 11px; padding: 2px 8px; cursor: pointer; }
      .control-panel button.action { background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 4px; color: var(--text-primary); font-size: 11px; padding: 6px 12px; cursor: pointer; font-weight: 500; display: flex; align-items: center; gap: 6px; }
      .control-panel button.action:hover:not(:disabled) { background: var(--bg-primary); border-color: var(--border-bright); }
      .control-panel button.action:disabled { opacity: 0.4; cursor: not-allowed; }
      .control-panel button.action.primary { background: var(--gradient)22; border-color: var(--gradient)66; color: var(--gradient); }
      .control-panel button.action.primary:hover:not(:disabled) { background: var(--gradient)33; border-color: var(--gradient); }
      .control-panel button.action.danger { background: var(--error)22; border-color: var(--error)66; color: var(--error); }
      .control-panel button.action.danger:hover:not(:disabled) { background: var(--error)33; border-color: var(--error); }
      .control-panel .cell-row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
      .control-panel .cell-row label { display: flex; flex-direction: column; gap: 2px; font-size: 10px; color: var(--text-secondary); white-space: nowrap; }
      .control-panel .cell-row select { font-size: 10px; padding: 2px 6px; }
      .control-panel .section-tabs { display: flex; gap: 2px; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid var(--border); flex-wrap: wrap; }
      .control-panel .tab { padding: 6px 10px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 4px 4px 0 0; color: var(--text-secondary); font-size: 11px; font-weight: 500; cursor: pointer; white-space: nowrap; position: relative; margin-bottom: -1px; }
      .control-panel .tab:hover { background: var(--border); color: var(--text-primary); }
      .control-panel .tab.active { background: var(--bg-secondary); border-color: var(--border-bright); color: var(--text-primary); }
      .control-panel .tab .kbd { font-family: monospace; font-size: 9px; padding: 1px 4px; background: var(--bg); border: 1px solid var(--border); border-radius: 3px; color: var(--text-muted); margin-left: 4px; }
      .control-panel .tab-content { display: none; }
      .control-panel .tab-content.active { display: block; animation: fadeIn 0.1s ease; }
      @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: none; } }
      .control-panel .kbd-hint { font-family: monospace; font-size: 9px; padding: 1px 4px; background: var(--bg); border: 1px solid var(--border); border-radius: 3px; color: var(--text-muted); margin-left: 6px; }
      .empty-state { text-align: center; padding: 24px 12px; color: var(--text-muted); font-size: 11px; }
      .empty-state .icon { font-size: 24px; margin-bottom: 8px; opacity: 0.5; }
    </style>
    <div class="control-panel-header" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
      <span style="font-weight: 600; color: var(--text-primary); letter-spacing: 0.08em;">CONTROL</span>
      <div style="flex: 1;"></div>
    </div>

    <div class="section-tabs" id="section-tabs">
      ${SECTIONS.map((s) => `
        <button class="tab${s.id === "new-run" ? " active" : ""}" data-section="${s.id}" title="Switch to ${s.title} (${s.key})">
          ${s.title}<span class="kbd">${s.key}</span>
        </button>
      `).join("")}
    </div>

    <div class="tab-content active" data-tab="new-run">
      <h4>NEW RUN</h4>
      <div class="row">
        <select class="profile" style="flex: 1;"></select>
        <select class="device">
          <option value="auto">auto</option>
          <option value="cpu">cpu</option>
          <option value="cuda">cuda</option>
        </select>
      </div>
      <div class="note profile-note"></div>
      <div class="row">
        <label>seeds</label><input class="seeds" type="number" min="1" />
        <label>epochs</label><input class="epochs" type="number" min="1" />
        <label>budget (s)</label><input class="budget" type="number" min="1" />
        <select class="fidelity">
          <option value="L0">L0</option>
          <option value="L1">L1</option>
          <option value="L2">L2</option>
        </select>
      </div>
      <div class="row">
        <button class="action start primary">Start run <span class="kbd">Z</span></button>
      </div>
      <div class="note new-run-note"></div>
    </div>

    <div class="tab-content" data-tab="this-run">
      <h4>THIS RUN</h4>
      <div class="run-section empty-state">
        <div class="icon">📋</div>
        <div>No run selected</div>
        <div style="margin-top: 4px; font-size: 10px;">Pick a run in the legend</div>
      </div>
    </div>

    <div class="tab-content" data-tab="queue">
      <h4>THE QUEUE</h4>
      <div class="queue-section empty-state">
        <div class="icon">📦</div>
        <div>No campaigns queued</div>
        <div style="margin-top: 4px; font-size: 10px;">Start a run to see queue</div>
      </div>
    </div>

    <div class="tab-content" data-tab="cells">
      <h4>CELLS</h4>
      <div class="row cell-row"></div>
      <div class="row">
        <button class="action replicate">Replicate <span class="kbd">⇧R</span></button>
        <button class="action preregister">Preregister <span class="kbd">⇧P</span></button>
        <button class="action quest primary">Adopt as Quest <span class="kbd">⇧Q</span></button>
      </div>
      <div class="note cell-note">Select a cell on the map or in the drawer to enable actions.</div>
    </div>

    <div class="tab-content" data-tab="exports">
      <h4>EXPORTS</h4>
      <div class="row">
        <button class="action export-script">Narration script <span class="kbd">E S</span></button>
        <button class="action export-report">Run report <span class="kbd">E R</span></button>
        <button class="action export-records">Records as JSON <span class="kbd">E J</span></button>
      </div>
      <div class="note export-note">Exports download immediately.</div>
    </div>
  `;
}

/** A control panel bound to one root element and its own subscriptions. */
export class ControlPanelView {
  private profiles: Profile[] = [];
  private axes: Axis[] = [];
  private profileSelect: HTMLSelectElement | null = null;
  private seedsInput: HTMLInputElement | null = null;
  private epochsInput: HTMLInputElement | null = null;
  private budgetInput: HTMLInputElement | null = null;
  private deviceSelect: HTMLSelectElement | null = null;
  private fidelitySelect: HTMLSelectElement | null = null;
  private profileNote: HTMLElement | null = null;
  private newRunNote: HTMLElement | null = null;
  private runSection: HTMLElement | null = null;
  private queueSection: HTMLElement | null = null;
  private cellSelects = new Map<string, HTMLSelectElement>();
  private cellNote: HTMLElement | null = null;
  private exportNote: HTMLElement | null = null;
  private activeTab = "new-run";
  private readonly disposers: (() => void)[] = [];

  constructor(
    private readonly root: HTMLElement,
    _state: JsonValue = null,
  ) {
    this.bindElements();
    this.bindEvents();
    this.disposers.push(runSelection.onChange(() => this.renderRun()));
    this.loadCatalogue();
  }

  dispose(): void {
    for (const dispose of this.disposers) dispose();
    this.disposers.length = 0;
  }

  update(_state: JsonValue): void {
    this.refresh();
  }

  private bindElements(): void {
    this.runSection = this.root.querySelector(".run-section");
    this.queueSection = this.root.querySelector(".queue-section");
    this.cellNote = this.root.querySelector(".cell-note");
    this.exportNote = this.root.querySelector(".export-note");
    this.profileSelect = this.root.querySelector(".profile");
    this.profileNote = this.root.querySelector(".profile-note");
    this.newRunNote = this.root.querySelector(".new-run-note");
    this.seedsInput = this.root.querySelector(".seeds");
    this.epochsInput = this.root.querySelector(".epochs");
    this.budgetInput = this.root.querySelector(".budget");
    this.deviceSelect = this.root.querySelector(".device");
    this.fidelitySelect = this.root.querySelector(".fidelity");

    const cellRow = this.root.querySelector<HTMLElement>(".cell-row")!;
    for (const axis of CELL_AXES) {
      const label = document.createElement("label");
      label.textContent = axis;
      const select = document.createElement("select");
      select.className = `cell-${axis}`;
      label.appendChild(select);
      cellRow.appendChild(label);
      this.cellSelects.set(axis, select);
    }

    for (const tab of this.root.querySelectorAll<HTMLButtonElement>(".tab")) {
      tab.addEventListener("click", () => this.switchTab(tab.dataset.section!));
    }

    this.root.addEventListener("keydown", (e) => {
      if (e.key >= "1" && e.key <= "5" && !e.ctrlKey && !e.metaKey && !e.altKey) {
        const t = e.target as HTMLElement;
        if (!["INPUT", "SELECT", "TEXTAREA"].includes(t.tagName)) {
          e.preventDefault();
          this.switchTab(SECTIONS[Number(e.key) - 1].id);
        }
      }
    });
  }

  private switchTab(id: string): void {
    for (const tab of this.root.querySelectorAll<HTMLButtonElement>(".tab")) tab.classList.toggle("active", tab.dataset.section === id);
    for (const content of this.root.querySelectorAll<HTMLElement>(".tab-content")) content.classList.toggle("active", content.dataset.tab === id);
    this.activeTab = id;
  }

  private bindEvents(): void {
    this.profileSelect?.addEventListener("change", () => this.renderProfileNote());
    this.root.querySelector<HTMLButtonElement>(".start")!.addEventListener("click", () => void this.startRun());
    this.root.querySelector<HTMLButtonElement>(".replicate")!.addEventListener("click", () => void this.cellAction("replicate"));
    this.root.querySelector<HTMLButtonElement>(".preregister")!.addEventListener("click", () => void this.cellAction("preregister"));
    this.root.querySelector<HTMLButtonElement>(".quest")!.addEventListener("click", () => void this.cellAction("quest"));
    this.root.querySelector<HTMLButtonElement>(".export-script")!.addEventListener("click", () => void this.export("script"));
    this.root.querySelector<HTMLButtonElement>(".export-report")!.addEventListener("click", () => void this.export("report"));
    this.root.querySelector<HTMLButtonElement>(".export-records")!.addEventListener("click", () => void this.export("records"));
  }

  private async loadCatalogue(): Promise<void> {
    try {
      const [profiles, axesResponse] = await Promise.all([
        fetch("/api/profiles").then((r) => r.json()),
        fetch("/api/axes").then((r) => r.json()),
      ]);
      this.profiles = profiles ?? [];
      this.axes = axesResponse?.axes ?? [];
      if (this.profileSelect) {
        this.profileSelect.innerHTML = this.profiles.map((p) => `<option value="${p.name}">${p.name}</option>`).join("");
        this.renderProfileNote();
      }
    } catch { /* ignore */ }
  }

  private renderProfileNote(): void {
    if (!this.profileSelect || !this.profileNote) return;
    const p = this.profiles.find((x) => x.name === this.profileSelect!.value);
    if (!p) return;
    const axesStr = p.axes.map((a) => a.axis).join(", ");
    this.profileNote.innerHTML = `
      <div style="margin-bottom: 4px;"><strong>${p.description || "No description"}</strong></div>
      <div style="font-size: 10px; color: var(--text-secondary);">
        Task: ${p.task} · Fidelity: ${p.fidelity} · Axes: ${axesStr}
      </div>
      <div style="font-size: 10px; color: var(--text-muted); margin-top: 2px;">
        Seeds: ${p.n_seeds} · Epochs: ${p.epochs} · Budget: ${p.budget_seconds ? p.budget_seconds + "s" : "∞"} · Policy: ${p.policy}
      </div>
    `;
    this.seedsInput!.value = String(p.n_seeds);
    this.epochsInput!.value = String(p.epochs);
    this.budgetInput!.value = p.budget_seconds ? String(p.budget_seconds) : "";
    this.fidelitySelect!.value = p.fidelity;
  }

  private async refresh(): Promise<void> {
    this.renderRun();
    await this.renderQueue();
    this.renderAxes();
  }

  private renderRun(): void {
    if (!this.runSection) return;
    const metrics = runSelection.selected;
    if (!metrics?.run) {
      this.runSection.innerHTML = `<div class="empty-state"><div class="icon">📋</div><div>No run selected</div><div style="margin-top: 4px; font-size: 10px;">Pick a run in the legend</div></div>`;
      return;
    }
    const r = metrics.run;
    this.runSection.innerHTML = `
      <table class="kv">
        <tr><th>Run ID</th><td>${r.run_id?.slice(0, 12)}…</td></tr>
        <tr><th>Profile</th><td>${r.profile}</td></tr>
        <tr><th>Fidelity</th><td>${r.fidelity}</td></tr>
        <tr><th>Mode</th><td>${r.mode}</td></tr>
        <tr><th>Started</th><td>${r.started_at ? new Date(r.started_at).toLocaleString() : "—"}</td></tr>
      </table>
      <div class="note">This run's declaration is frozen.</div>
    `;
  }

  private async renderQueue(): Promise<void> {
    if (!this.queueSection) return;
    try {
      const res = await fetch("/api/queue");
      if (!res.ok) throw new Error();
      const data = await res.json();
      const campaigns = data.campaigns ?? [];
      if (!campaigns.length) {
        this.queueSection.innerHTML = `<div class="empty-state"><div class="icon">📦</div><div>No campaigns queued</div></div>`;
        return;
      }
      this.queueSection.innerHTML = `
        <table class="list">
          <thead><tr><th>Campaign</th><th>Status</th><th>Priority</th><th></th></tr></thead>
          <tbody>
            ${campaigns.map((c: Campaign) => `
              <tr>
                <td>${c.name}</td>
                <td>${c.status}</td>
                <td>${c.priority}</td>
                <td><button class="mini" data-cancel="${c.campaign_id}">Cancel</button></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      `;
      for (const btn of this.queueSection.querySelectorAll<HTMLButtonElement>("[data-cancel]")) {
        btn.addEventListener("click", async () => {
          btn.disabled = true;
          await fetch(`/api/campaign/${btn.dataset.cancel}`, { method: "DELETE" });
          this.renderQueue();
        });
      }
    } catch {
      this.queueSection.innerHTML = `<div class="empty-state"><div class="icon">📦</div><div>Queue unavailable</div></div>`;
    }
  }

  private renderAxes(): void {
    if (!this.cellNote) return;
    const metrics = runSelection.selected;
    if (!metrics) return;
    // Update cell axis dropdowns from run metrics
    const records = metrics.records ?? [];
    if (!records.length) return;
    for (const axis of CELL_AXES) {
      const select = this.cellSelects.get(axis);
      if (!select) continue;
      const values = [...new Set(records.map((r: any) => r.coordinate?.[axis]).filter(Boolean))].sort();
      select.innerHTML = values.map((v) => `<option value="${v}">${v}</option>`).join("");
    }
  }

  private async startRun(): Promise<void> {
    if (!this.profileSelect) return;
    const profile = this.profileSelect.value;
    const seeds = Number(this.seedsInput?.value ?? 1);
    const epochs = Number(this.epochsInput?.value ?? 1);
    const budget = this.budgetInput?.value ? Number(this.budgetInput.value) : null;
    const fidelity = this.fidelitySelect?.value ?? "L0";
    const device = this.deviceSelect?.value ?? "auto";

    this.setStatus("Starting run…");
    try {
      const res = await fetch("/api/runs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profile, seeds, epochs, budget_seconds: budget, fidelity, device }),
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(body.error || "Failed to start run");
      this.setStatus(body.message || "Run started");
      runSelection.select(body.run_id ?? null);
    } catch (e) {
      this.setStatus(e instanceof Error ? e.message : "Failed to start run", true);
    }
  }

  private cellAction(action: "replicate" | "preregister" | "quest"): void {
    window.dispatchEvent(new CustomEvent(`cell-action-${action}`));
  }

  private export(type: "script" | "report" | "records"): void {
    window.dispatchEvent(new CustomEvent(`export-${type}`));
  }

  private setStatus(message: string, isError = false): void {
    if (this.newRunNote) {
      this.newRunNote.textContent = message;
      this.newRunNote.style.color = isError ? "var(--error)" : "var(--text-secondary)";
    }
  }
}