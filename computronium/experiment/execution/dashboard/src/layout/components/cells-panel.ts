/** Cells Panel — shows selected cell and available actions. */

import { workspaceStore } from "../../stores/workspace.js";
import { runSelection } from "../../run-selection.js";
import { registerDefinition } from "../definitions.js";
import type {
  ComponentContext,
  ComponentDefinition,
  ComponentHandle,
  JsonValue,
} from "../types.js";

const CELL_AXES = ["substrate", "geometry", "dynamics", "plasticity", "credit", "update"] as const;

function createCellsPanelBody(): string {
  return `
    <style>
      .cells-panel h4 { margin: 14px 0 6px; font-size: 10px; letter-spacing: 0.08em; color: var(--text-secondary); text-transform: uppercase; }
      .cells-panel .note { color: var(--text-secondary); margin: 4px 0 8px; line-height: 1.4; font-size: 11px; }
      .cells-panel .row { display: flex; gap: 8px; align-items: center; margin: 4px 0; }
      .cells-panel .cell-row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
      .cells-panel .cell-row label { display: flex; flex-direction: column; gap: 2px; font-size: 10px; color: var(--text-secondary); white-space: nowrap; }
      .cells-panel .cell-row select { font-size: 10px; padding: 2px 6px; }
      .cells-panel button.action { background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 4px; color: var(--text-primary); font-size: 11px; padding: 6px 12px; cursor: pointer; font-weight: 500; display: flex; align-items: center; gap: 6px; }
      .cells-panel button.action:hover:not(:disabled) { background: var(--bg-primary); border-color: var(--border-bright); }
      .cells-panel button.action:disabled { opacity: 0.4; cursor: not-allowed; }
      .cells-panel button.action.primary { background: var(--gradient)22; border-color: var(--gradient)66; color: var(--gradient); }
      .cells-panel button.action.primary:hover:not(:disabled) { background: var(--gradient)33; border-color: var(--gradient); }
      .cells-panel .kbd { font-family: monospace; font-size: 9px; padding: 1px 4px; background: var(--bg); border: 1px solid var(--border); border-radius: 3px; color: var(--text-muted); margin-left: 6px; }
      .cells-panel .empty-state { text-align: center; padding: 24px 12px; color: var(--text-muted); font-size: 11px; }
      .cells-panel .empty-state .icon { font-size: 24px; margin-bottom: 8px; opacity: 0.5; }
    </style>
    <div class="cells-panel-header" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
      <span style="font-weight: 600; color: var(--text-primary); letter-spacing: 0.08em;">CELLS</span>
    </div>
    <div class="row cell-row"></div>
    <div class="row">
      <button class="action replicate">Replicate <span class="kbd">⇧R</span></button>
      <button class="action preregister">Preregister <span class="kbd">⇧P</span></button>
      <button class="action quest primary">Adopt as Quest <span class="kbd">⇧Q</span></button>
    </div>
    <div class="note cell-note">Select a cell on the map or in the drawer to enable actions.</div>
  `;
}

export class CellsPanelView {
  private cellSelects = new Map<string, HTMLSelectElement>();
  private cellNote: HTMLElement | null = null;
  private replicateBtn: HTMLButtonElement | null = null;
  private preregisterBtn: HTMLButtonElement | null = null;
  private questBtn: HTMLButtonElement | null = null;
  private readonly disposers: (() => void)[] = [];

  constructor(
    private readonly root: HTMLElement,
    _state: JsonValue = null,
  ) {
    this.bindElements();
    this.bindEvents();
    this.disposers.push(runSelection.onChange(() => this.renderAxes()));
    this.renderAxes();
  }

  dispose(): void {
    for (const dispose of this.disposers) dispose();
    this.disposers.length = 0;
  }

  update(_state: JsonValue): void {
    this.renderAxes();
  }

  private bindElements(): void {
    this.cellNote = this.root.querySelector(".cell-note");

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

    this.replicateBtn = this.root.querySelector<HTMLButtonElement>(".replicate")!;
    this.preregisterBtn = this.root.querySelector<HTMLButtonElement>(".preregister")!;
    this.questBtn = this.root.querySelector<HTMLButtonElement>(".quest")!;
  }

  private bindEvents(): void {
    this.root.querySelector<HTMLButtonElement>(".replicate")!.addEventListener("click", () => void this.cellAction("replicate"));
    this.root.querySelector<HTMLButtonElement>(".preregister")!.addEventListener("click", () => void this.cellAction("preregister"));
    this.root.querySelector<HTMLButtonElement>(".quest")!.addEventListener("click", () => void this.cellAction("quest"));
  }

  private renderAxes(): void {
    if (!this.cellNote) return;
    const metrics = runSelection.selected;
    if (!metrics) return;
    const records = metrics.records ?? [];
    if (!records.length) return;
    for (const axis of CELL_AXES) {
      const select = this.cellSelects.get(axis);
      if (!select) continue;
      const values = [...new Set(records.map((r: any) => r.coordinate?.[axis]).filter(Boolean))].sort();
      select.innerHTML = values.map((v) => `<option value="${v}">${v}</option>`).join("");
    }
  }

  private cellAction(action: "replicate" | "preregister" | "quest"): void {
    const cellKey = workspaceStore.getCellSelection();
    if (!cellKey) {
      this.showCellNote("No cell selected");
      return;
    }
    this.hideCellNote();
    window.dispatchEvent(new CustomEvent(`cell-action-${action}`));
  }

  private showCellNote(message: string): void {
    if (this.cellNote) {
      this.cellNote.textContent = message;
      this.cellNote.style.color = "var(--warn)";
    }
    this.disableCellButtons(true);
  }

  private hideCellNote(): void {
    if (this.cellNote) {
      this.cellNote.textContent = "Select a cell on the map or in the drawer to enable actions.";
      this.cellNote.style.color = "var(--text-muted)";
    }
    this.disableCellButtons(false);
  }

  private disableCellButtons(disabled: boolean): void {
    this.replicateBtn!.disabled = disabled;
    this.preregisterBtn!.disabled = disabled;
    this.questBtn!.disabled = disabled;
  }
}

export const cellsPanelDefinition: ComponentDefinition = registerDefinition<JsonValue>({
  type: "cells-panel",
  title: "Cells",
  icon: "🔬",
  defaultSize: { width: 400, height: 300 },
  create(
    host: HTMLElement,
    _state: JsonValue,
    _ctx: ComponentContext,
  ): ComponentHandle<JsonValue> {
    host.innerHTML = createCellsPanelBody();
    const view = new CellsPanelView(host);
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