/** This Run Panel — shows details of the currently selected run. */

import { runSelection } from "../../run-selection.js";
import { registerDefinition } from "../definitions.js";
import type {
  ComponentContext,
  ComponentDefinition,
  ComponentHandle,
  JsonValue,
} from "../types.js";

function createThisRunPanelBody(): string {
  return `
    <style>
      .this-run-panel h4 { margin: 14px 0 6px; font-size: 10px; letter-spacing: 0.08em; color: var(--text-secondary); text-transform: uppercase; }
      .this-run-panel table.kv { width: 100%; border-collapse: collapse; font-size: 11px; }
      .this-run-panel table.kv th { text-align: left; font-weight: 500; color: var(--text-secondary); padding: 2px 6px 2px 0; vertical-align: top; }
      .this-run-panel table.kv td { color: var(--text-primary); padding: 2px 6px 2px 0; vertical-align: top; }
      .this-run-panel .note { color: var(--text-secondary); margin: 4px 0 8px; line-height: 1.4; font-size: 11px; }
      .this-run-panel .empty-state { text-align: center; padding: 24px 12px; color: var(--text-muted); font-size: 11px; }
      .this-run-panel .empty-state .icon { font-size: 24px; margin-bottom: 8px; opacity: 0.5; }
    </style>
    <div class="this-run-panel-header" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
      <span style="font-weight: 600; color: var(--text-primary); letter-spacing: 0.08em;">THIS RUN</span>
    </div>
    <div class="run-section empty-state">
      <div class="icon">📋</div>
      <div>No run selected</div>
      <div style="margin-top: 4px; font-size: 10px;">Pick a run in the legend</div>
    </div>
  `;
}

export class ThisRunPanelView {
  private runSection: HTMLElement | null = null;
  private readonly disposers: (() => void)[] = [];

  constructor(
    private readonly root: HTMLElement,
    _state: JsonValue = null,
  ) {
    this.bindElements();
    this.disposers.push(runSelection.onChange(() => this.renderRun()));
    this.renderRun();
  }

  dispose(): void {
    for (const dispose of this.disposers) dispose();
    this.disposers.length = 0;
  }

  update(_state: JsonValue): void {
    this.renderRun();
  }

  private bindElements(): void {
    this.runSection = this.root.querySelector(".run-section");
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
}

export const thisRunPanelDefinition: ComponentDefinition = registerDefinition<JsonValue>({
  type: "this-run-panel",
  title: "This Run",
  icon: "📋",
  defaultSize: { width: 400, height: 300 },
  create(
    host: HTMLElement,
    _state: JsonValue,
    _ctx: ComponentContext,
  ): ComponentHandle<JsonValue> {
    host.innerHTML = createThisRunPanelBody();
    const view = new ThisRunPanelView(host);
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