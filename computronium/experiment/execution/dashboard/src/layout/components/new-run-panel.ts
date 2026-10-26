/** New Run Panel — configure and start runs. */

import { wsClient } from "../../ws-client.js";
import { runSelection } from "../../run-selection.js";
import { workspaceStore } from "../../stores/workspace.js";
import { metricsStore } from "../../stores/metrics.js";
import { registerDefinition } from "../definitions.js";
import type {
  ComponentContext,
  ComponentDefinition,
  ComponentHandle,
  JsonValue,
} from "../types.js";

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

interface Axis {
  axis: string;
  primitives: { name: string; description: string; available: boolean; unavailable_reason: string | null }[];
}

const CELL_AXES = ["substrate", "geometry", "dynamics", "plasticity", "credit", "update"] as const;

function createNewRunPanelBody(): string {
  return `
    <style>
      .new-run-panel h4 { margin: 14px 0 6px; font-size: 10px; letter-spacing: 0.08em; color: var(--text-secondary); text-transform: uppercase; }
      .new-run-panel table.kv { width: 100%; border-collapse: collapse; font-size: 11px; }
      .new-run-panel table.kv th { text-align: left; font-weight: 500; color: var(--text-secondary); padding: 2px 6px 2px 0; vertical-align: top; }
      .new-run-panel table.kv td { color: var(--text-primary); padding: 2px 6px 2px 0; vertical-align: top; }
      .new-run-panel .note { color: var(--text-secondary); margin: 4px 0 8px; line-height: 1.4; font-size: 11px; }
      .new-run-panel .row { display: flex; gap: 8px; align-items: center; margin: 4px 0; }
      .new-run-panel input, .new-run-panel select { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border); border-radius: 4px; font-size: 11px; padding: 2px 4px; min-width: 0; }
      .new-run-panel button.action { background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 4px; color: var(--text-primary); font-size: 11px; padding: 6px 12px; cursor: pointer; font-weight: 500; display: flex; align-items: center; gap: 6px; }
      .new-run-panel button.action:hover:not(:disabled) { background: var(--bg-primary); border-color: var(--border-bright); }
      .new-run-panel button.action:disabled { opacity: 0.4; cursor: not-allowed; }
      .new-run-panel button.action.primary { background: var(--gradient)22; border-color: var(--gradient)66; color: var(--gradient); }
      .new-run-panel button.action.primary:hover:not(:disabled) { background: var(--gradient)33; border-color: var(--gradient); }
      .new-run-panel .kbd { font-family: monospace; font-size: 9px; padding: 1px 4px; background: var(--bg); border: 1px solid var(--border); border-radius: 3px; color: var(--text-muted); margin-left: 6px; }
      .new-run-panel .empty-state { text-align: center; padding: 24px 12px; color: var(--text-muted); font-size: 11px; }
      .new-run-panel .empty-state .icon { font-size: 24px; margin-bottom: 8px; opacity: 0.5; }
    </style>
    <div class="new-run-panel-header" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
      <span style="font-weight: 600; color: var(--text-primary); letter-spacing: 0.08em;">NEW RUN</span>
    </div>
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
  `;
}

export class NewRunPanelView {
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
    this.newRunNote = this.root.querySelector(".new-run-note");
    this.profileSelect = this.root.querySelector(".profile");
    this.profileNote = this.root.querySelector(".profile-note");
    this.seedsInput = this.root.querySelector(".seeds");
    this.epochsInput = this.root.querySelector(".epochs");
    this.budgetInput = this.root.querySelector(".budget");
    this.deviceSelect = this.root.querySelector(".device");
    this.fidelitySelect = this.root.querySelector(".fidelity");
  }

  private bindEvents(): void {
    this.profileSelect?.addEventListener("change", () => this.renderProfileNote());
    this.root.querySelector<HTMLButtonElement>(".start")!.addEventListener("click", () => void this.startRun());
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

  private refresh(): void {
    this.renderRun();
  }

  private renderRun(): void {
    // New Run panel doesn't show the selected run - that's in This Run panel
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

  private setStatus(message: string, isError = false): void {
    if (this.newRunNote) {
      this.newRunNote.textContent = message;
      this.newRunNote.style.color = isError ? "var(--error)" : "var(--text-secondary)";
    }
  }
}

export const newRunPanelDefinition: ComponentDefinition = registerDefinition<JsonValue>({
  type: "new-run-panel",
  title: "New Run",
  icon: "▶",
  defaultSize: { width: 400, height: 300 },
  create(
    host: HTMLElement,
    _state: JsonValue,
    _ctx: ComponentContext,
  ): ComponentHandle<JsonValue> {
    host.innerHTML = createNewRunPanelBody();
    const view = new NewRunPanelView(host);
    return {
      element: host,
      update(next: JsonValue): void {
        view.update(next);
      },
      dispose(): void {
        view.dispose();
        host.remove();
      },
    };
  },
});