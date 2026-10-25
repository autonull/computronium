/** Simple command palette — fuzzy search, enter to run, esc to close. */

import { BINDINGS, allBindings } from "./bindings.js";
import { panels } from "./panels.js";
import { viewSwitcher } from "./stage/switcher.js";
import { helpOverlay } from "./help-overlay.js";
import { wsClient } from "./ws-client.js";
import { applyPreset, getCurrentPreset } from "./layout.js";

function getLegacyCellDrawer(): any {
  return (window as any).__DASHBOARD__?.cellDrawer ?? null;
}
function getLegacyControlPanel(): any {
  return (window as any).__DASHBOARD__?.controlPanel ?? null;
}
function getLegacyControlBar(): any {
  return (window as any).__DASHBOARD__?.controlBar ?? null;
}

interface Entry {
  id: string;
  label: string;
  group: string;
  hint?: string;
  enabled: boolean;
  reason?: string;
  run: () => void;
  sortOrder?: number;
}

const GROUP_ORDER = ["the next question", "workspaces", "views", "panels", "verbs", "general"];

class CommandPalette {
  private container: HTMLElement | null = null;
  private input: HTMLInputElement | null = null;
  private list: HTMLElement | null = null;
  private entries: Entry[] = [];
  private filtered: Entry[] = [];
  private selected = 0;
  private open = false;
  private prevFocus: HTMLElement | null = null;
  private unsubLayout: (() => void) | null = null;
  private unsubPanels: (() => void) | null = null;
  private unsubDrawer: (() => void) | null = null;

  async init(): Promise<void> {
    this.build();
    document.body.appendChild(this.container!);
    this.unsubLayout = () => {}; // no-op, rebuild on open
    this.unsubPanels = panels.onChange(() => { if (this.open) this.rebuild(); });
    const drawer = getLegacyCellDrawer();
    this.unsubDrawer = drawer?.onChange?.(() => { if (this.open) this.rebuild(); });
    this.rebuild();
    document.addEventListener("keydown", this.onGlobalKey);
    console.log("[Palette] Ready");
  }

  private build(): void {
    this.container = document.createElement("div");
    this.container.id = "command-palette";
    this.container.style.cssText = `
      position: fixed; inset: 0; z-index: 10000; display: none;
      align-items: flex-start; justify-content: center; padding-top: 10vh;
      background: rgba(0,0,0,0.5); backdrop-filter: blur(2px);
    `;
    this.container.innerHTML = `
      <div style="
        width: min(640px, 90vw); max-height: 70vh;
        background: var(--bg-secondary); border: 1px solid var(--border-bright);
        border-radius: 8px; box-shadow: 0 16px 48px rgba(0,0,0,0.5);
        display: flex; flex-direction: column; overflow: hidden;
      ">
        <div style="display: flex; align-items: center; gap: 8px; padding: 10px 12px; border-bottom: 1px solid var(--border); background: var(--bg-tertiary);">
          <kbd style="font-size: 10px; padding: 2px 6px; background: var(--bg); border: 1px solid var(--border); border-radius: 3px; color: var(--text-muted);">⇧;</kbd>
          <input class="palette-input" type="text" placeholder="Type a command…" autocomplete="off" spellcheck="false"
            style="flex: 1; background: var(--bg); border: 1px solid var(--border); border-radius: 4px; padding: 6px 10px; font-size: 13px; color: var(--text-primary); outline: none;"/>
          <kbd style="font-size: 10px; padding: 2px 6px; background: var(--bg); border: 1px solid var(--border); border-radius: 3px; color: var(--text-muted);">Esc</kbd>
        </div>
        <div class="palette-list" style="flex: 1; overflow-y: auto; padding: 8px;"></div>
        <div style="padding: 6px 12px; border-top: 1px solid var(--border); background: var(--bg-tertiary); font-size: 10px; color: var(--text-muted);">
          ↑↓ select · ⏎ run · Esc close
        </div>
      </div>
    `;
    this.input = this.container.querySelector(".palette-input")!;
    this.list = this.container.querySelector(".palette-list")!;
    this.input.addEventListener("input", () => this.filter());
    this.input.addEventListener("keydown", this.onInputKey);
    this.container.addEventListener("click", (e) => { if (e.target === this.container) this.close(); });
  }

  private rebuild(): void {
    const e: Entry[] = [];
    let order = 0;
    const hasRun = wsClient.isConnected;
    const drawer = getLegacyCellDrawer();
    const hasCell = drawer?.hasCellSelected?.() ?? false;

    // The next question
    e.push({ id: "start-run", label: hasRun ? "Start a new run" : "Start a run", group: "the next question", hint: "z", enabled: true, sortOrder: order++, run: () => { this.close(); getLegacyControlPanel()?.showSection("new-run"); panels.toggle("control-panel"); } });
    e.push({ id: "replicate-cell", label: "Replicate selected cell", group: "the next question", hint: "⇧R", enabled: hasCell, reason: hasCell ? undefined : "No cell selected", sortOrder: order++, run: () => { this.close(); drawer?.replicateSelected?.(); } });
    e.push({ id: "preregister-claim", label: "Preregister claim", group: "the next question", hint: "⇧P", enabled: hasCell, reason: hasCell ? undefined : "No cell selected", sortOrder: order++, run: () => { this.close(); drawer?.preregisterSelected?.(); } });
    e.push({ id: "adopt-quest", label: "Adopt as quest (new run)", group: "the next question", hint: "⇧Q", enabled: hasCell, reason: hasCell ? undefined : "No cell selected", sortOrder: order++, run: () => { this.close(); drawer?.adoptQuestSelected?.(); } });
    e.push({ id: "show-queue", label: "Show run queue", group: "the next question", hint: "z → Queue", enabled: true, sortOrder: order++, run: () => { this.close(); getLegacyControlPanel()?.showSection("queue"); panels.toggle("control-panel"); } });

    // Workspaces
    for (const [id, label] of [["watch", "Watch — campaigns"], ["audit", "Audit — evidence"], ["drive", "Drive — instrument"], ["reset", "Reset to Watch"]] as const) {
      const active = id !== "reset" && applyPreset === undefined ? false : getCurrentPreset() === id;
      e.push({ id: `ws-${id}`, label, group: "workspaces", hint: "", enabled: id === "reset" || !active, reason: active ? "Active" : undefined, sortOrder: order++, run: () => { this.close(); if (id === "reset") applyPreset("watch"); else applyPreset(id as any); } });
    }

    // Views
    for (const v of viewSwitcher.getViews()) {
      const b = BINDINGS.find((x) => x.id === `view-${v.id}`);
      e.push({ id: `view-${v.id}`, label: v.name, group: "views", hint: b?.key ?? b?.chord ?? "", enabled: true, sortOrder: order++, run: () => { this.close(); viewSwitcher.show(v.id); } });
    }

    // Panels
    for (const p of panels.list()) {
      const b = BINDINGS.find((x) => x.id === `panel-${p.id}`);
      e.push({ id: `panel-${p.id}`, label: p.label, group: "panels", hint: b?.key ?? "", enabled: true, sortOrder: order++, run: () => { this.close(); panels.toggle(p.id); } });
    }

    // Verbs
    for (const b of BINDINGS) {
      if (b.group === "Run Control" || b.group === "General") {
        e.push({ id: b.id, label: b.label, group: b.group === "Run Control" ? "verbs" : "general", hint: b.key === " " ? "Space" : (b.key ?? b.chord ?? ""), enabled: b.when ? this.checkWhen(b.when) : true, reason: b.when && !this.checkWhen(b.when) ? this.whenReason(b.when) : undefined, sortOrder: order++, run: () => { this.close(); b.run(); } });
      }
    }

    this.entries = e.sort((a, b) => (GROUP_ORDER.indexOf(a.group) - GROUP_ORDER.indexOf(b.group)) || (a.sortOrder! - b.sortOrder!));
    if (this.open) this.filter();
  }

  private checkWhen(w: "always" | "cell-selected" | "run-active"): boolean {
    if (w === "always") return true;
    if (w === "cell-selected") return getLegacyCellDrawer()?.hasCellSelected?.() ?? false;
    return wsClient.isConnected;
  }
  private whenReason(w: "always" | "cell-selected" | "run-active"): string {
    if (w === "cell-selected") return "No cell selected";
    return "No active run";
  }

  private filter(): void {
    const q = this.input!.value.toLowerCase().trim();
    if (!q) this.filtered = [...this.entries];
    else this.filtered = this.entries.filter((e) => e.label.toLowerCase().includes(q) || e.hint?.toLowerCase().includes(q));
    this.selected = 0;
    this.render();
  }

  private render(): void {
    if (!this.list) return;
    this.list.innerHTML = "";
    if (!this.filtered.length) {
      this.list.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--text-muted);">${this.input!.value ? "No matches" : "No commands"}</div>`;
      return;
    }
    let currentGroup = "";
    for (let i = 0; i < this.filtered.length; i++) {
      const e = this.filtered[i];
      if (e.group !== currentGroup) {
        currentGroup = e.group;
        const h = document.createElement("div");
        h.style.cssText = `padding: 6px 10px 2px; font-size: 9px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); font-weight: 600;`;
        h.textContent = e.group;
        this.list.appendChild(h);
      }
      const item = document.createElement("div");
      item.style.cssText = `display: flex; align-items: center; gap: 8px; padding: 6px 10px; border-radius: 4px; cursor: ${e.enabled ? "pointer" : "not-allowed"}; ${!e.enabled ? "opacity: 0.5;" : ""}`;
      if (i === this.selected) item.style.background = "var(--gradient)1a";
      item.innerHTML = `<span style="flex: 1; font-size: 12px; color: var(--text-primary);">${this.highlight(e.label)}</span>${e.hint ? `<kbd style="font-size: 9px; padding: 1px 5px; background: var(--bg); border: 1px solid var(--border); border-radius: 3px; color: var(--text-secondary);">${e.hint}</kbd>` : ""}${e.reason ? `<span style="font-size: 10px; color: var(--text-muted);">${e.reason}</span>` : ""}`;
      if (e.enabled) {
        item.addEventListener("click", () => { this.selected = i; e.run(); });
        item.addEventListener("mouseenter", () => (this.selected = i));
      }
      this.list.appendChild(item);
    }
    this.list.querySelector(`:nth-child(${this.selected + 1})`)?.scrollIntoView({ block: "nearest" });
  }

  private highlight(label: string): string {
    const q = this.input!.value.toLowerCase().trim();
    if (!q) return label;
    const i = label.toLowerCase().indexOf(q);
    if (i === -1) return label;
    return label.slice(0, i) + `<mark style="background: var(--gradient)33; color: var(--gradient); padding: 0 2px; border-radius: 2px;">${label.slice(i, i + q.length)}</mark>` + label.slice(i + q.length);
  }

  private onGlobalKey = (e: KeyboardEvent): void => {
    if (e.shiftKey && e.key === ";") { e.preventDefault(); this.open ? this.close() : this.openPalette(); }
  };

  private onInputKey = (e: KeyboardEvent): void => {
    if (e.key === "ArrowDown") { e.preventDefault(); this.selected = Math.min(this.selected + 1, this.filtered.length - 1); this.render(); }
    else if (e.key === "ArrowUp") { e.preventDefault(); this.selected = Math.max(this.selected - 1, 0); this.render(); }
    else if (e.key === "Enter") { e.preventDefault(); const en = this.filtered[this.selected]; if (en?.enabled) en.run(); }
    else if (e.key === "Escape") { e.preventDefault(); this.close(); }
  };

  openPalette(): void {
    if (this.open) return;
    this.prevFocus = document.activeElement as HTMLElement;
    this.open = true;
    this.container!.style.display = "flex";
    this.rebuild();
    this.filter();
    requestAnimationFrame(() => this.input!.focus());
  }

  close(): void {
    if (!this.open) return;
    this.open = false;
    this.container!.style.display = "none";
    this.input!.value = "";
    this.prevFocus?.focus();
    this.prevFocus = null;
  }
}

export const palette = new CommandPalette();
export async function initPalette(): Promise<void> { await palette.init(); }
export function openPalette(): void { palette.openPalette(); }
export function closePalette(): void { palette.close(); }