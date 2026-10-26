/** Exports Panel — download run data in various formats. */

import { registerDefinition } from "../definitions.js";
import type {
  ComponentContext,
  ComponentDefinition,
  ComponentHandle,
  JsonValue,
} from "../types.js";

function createExportsPanelBody(): string {
  return `
    <style>
      .exports-panel h4 { margin: 14px 0 6px; font-size: 10px; letter-spacing: 0.08em; color: var(--text-secondary); text-transform: uppercase; }
      .exports-panel .row { display: flex; gap: 8px; align-items: center; margin: 4px 0; }
      .exports-panel button.action { background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 4px; color: var(--text-primary); font-size: 11px; padding: 6px 12px; cursor: pointer; font-weight: 500; display: flex; align-items: center; gap: 6px; }
      .exports-panel button.action:hover:not(:disabled) { background: var(--bg-primary); border-color: var(--border-bright); }
      .exports-panel button.action:disabled { opacity: 0.4; cursor: not-allowed; }
      .exports-panel .kbd { font-family: monospace; font-size: 9px; padding: 1px 4px; background: var(--bg); border: 1px solid var(--border); border-radius: 3px; color: var(--text-muted); margin-left: 6px; }
      .exports-panel .note { color: var(--text-secondary); margin: 4px 0 8px; line-height: 1.4; font-size: 11px; }
    </style>
    <div class="exports-panel-header" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
      <span style="font-weight: 600; color: var(--text-primary); letter-spacing: 0.08em;">EXPORTS</span>
    </div>
    <div class="row">
      <button class="action export-script">Narration script <span class="kbd">E S</span></button>
      <button class="action export-report">Run report <span class="kbd">E R</span></button>
      <button class="action export-records">Records as JSON <span class="kbd">E J</span></button>
    </div>
    <div class="note export-note">Exports download immediately.</div>
  `;
}

export class ExportsPanelView {
  private exportNote: HTMLElement | null = null;

  constructor(
    private readonly root: HTMLElement,
    _state: JsonValue = null,
  ) {
    this.bindElements();
    this.bindEvents();
  }

  dispose(): void {}

  update(_state: JsonValue): void {}

  private bindElements(): void {
    this.exportNote = this.root.querySelector(".export-note");
  }

  private bindEvents(): void {
    this.root.querySelector<HTMLButtonElement>(".export-script")!.addEventListener("click", () => void this.export("script"));
    this.root.querySelector<HTMLButtonElement>(".export-report")!.addEventListener("click", () => void this.export("report"));
    this.root.querySelector<HTMLButtonElement>(".export-records")!.addEventListener("click", () => void this.export("records"));
  }

  private export(type: "script" | "report" | "records"): void {
    window.dispatchEvent(new CustomEvent(`export-${type}`));
  }
}

export const exportsPanelDefinition: ComponentDefinition = registerDefinition<JsonValue>({
  type: "exports-panel",
  title: "Exports",
  icon: "📥",
  defaultSize: { width: 400, height: 200 },
  create(
    host: HTMLElement,
    _state: JsonValue,
    _ctx: ComponentContext,
  ): ComponentHandle<JsonValue> {
    host.innerHTML = createExportsPanelBody();
    const view = new ExportsPanelView(host);
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