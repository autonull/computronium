/** Caption — the dashboard's voice, one view per instance. */

import { wsClient } from "./ws-client.js";
import { runSelection } from "./run-selection.js";
import { PALETTE } from "./colors.js";
import type { CellData } from "./cell-data.js";

interface CellDrawerLike {
  hasCellSelected(): boolean;
  readonly currentCell: CellData | null;
  onChange(listener: () => void): () => void;
}

export function createCaptionBody(): string {
  return `
    <div class="caption-headline" style="font-size: 13px; font-weight: 500; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"></div>
    <div class="caption-context" style="font-size: 11px; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 2px;"></div>
    <div class="caption-detail" style="font-size: 10px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 1px;"></div>
  `;
}

/** A caption bound to one root element and its own subscriptions. */
export class CaptionView {
  private readonly headline: HTMLElement;
  private readonly context: HTMLElement;
  private readonly detail: HTMLElement;
  private lastText = "";
  private readonly disposers: (() => void)[] = [];

  constructor(
    private readonly root: HTMLElement,
    private readonly cellDrawer: CellDrawerLike | null = null,
  ) {
    this.headline = this.query(".caption-headline");
    this.context = this.query(".caption-context");
    this.detail = this.query(".caption-detail");
    this.disposers.push(
      wsClient.onStateChange((state) => {
        if (state === "connected") this.render();
        else this.set("Connecting…", "", "");
      }),
      runSelection.onChange(() => this.render()),
    );
    if (this.cellDrawer) {
      this.disposers.push(this.cellDrawer.onChange(() => this.render()));
    }
    this.render();
  }

  dispose(): void {
    for (const dispose of this.disposers) dispose();
    this.disposers.length = 0;
  }

  set(headline: string, context = "", detail = ""): void {
    this.headline.textContent = headline;
    this.context.textContent = context;
    this.detail.textContent = detail;
  }

  notify(text: string, ctx = "", det = ""): void {
    this.lastText = text;
    this.set(text, ctx, det);
  }

  clear(): void {
    this.lastText = "";
    this.render();
  }

  private query<T extends HTMLElement>(selector: string): T {
    const el = this.root.querySelector<T>(selector);
    if (!el) throw new Error(`[Caption] missing element: ${selector}`);
    return el;
  }

  private render(): void {
    const run = runSelection.selected;
    const drawer = this.cellDrawer;
    const cell = drawer?.hasCellSelected() ? drawer.currentCell : null;

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
      const coordStr = Object.entries(coord)
        .filter(([, v]) => v)
        .map(([k, v]) => `${k}=${v}`)
        .join(", ");
      const verdict =
        status === "measured"
          ? valAcc > chance + 0.1
            ? "PASSED"
            : valAcc <= chance
              ? "REJECTED"
              : "INSUFFICIENT"
          : status.toUpperCase();
      const verdictColor =
        verdict === "PASSED"
          ? PALETTE.promoted
          : verdict === "REJECTED"
            ? PALETTE.rejected
            : PALETTE.insufficient;
      this.set(
        `${mode} · ${cellsDone} cells · ${profile}@${fidelity}`,
        `Cell: ${coordStr} · ${verdict} (${valAcc.toFixed(3)} vs ${chance})`,
        `Shift+R replicate · Shift+P preregister · Shift+Q quest · D toggle`,
      );
      this.detail.style.color = verdictColor;
    } else {
      this.set(
        `${mode} · ${cellsDone} cells · ${profile}@${fidelity}`,
        requiredSeeds > 0 ? `Seeds to claim: ${requiredSeeds}` : "Click a cell to inspect",
        "V cycle views · 1-9 pick view · Z start run · Space play/pause",
      );
      this.detail.style.color = "var(--text-muted)";
    }
  }
}
