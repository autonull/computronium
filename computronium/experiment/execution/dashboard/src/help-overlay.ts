/** Simple help overlay — keyboard shortcuts from bindings. */

import { registry } from "./components/registry.js";
import { allBindings } from "./bindings.js";
import type { Component } from "./components/registry.js";

function buildGroups() {
  const groups = new Map<string, { key: string; desc: string }[]>();
  for (const b of allBindings()) {
    const k = b.chord ? `Shift+${b.chord.split("+")[1].toUpperCase()}` : b.key?.toUpperCase();
    if (!k) continue;
    const g = b.group;
    if (!groups.has(g)) groups.set(g, []);
    groups.get(g)!.push({ key: k, desc: b.label });
  }
  const order = ["Navigation", "Panels", "Charts", "Run Control", "Cell Actions", "Stage", "General"];
  return order.map((t) => ({ title: t, items: groups.get(t) ?? [] })).filter((g) => g.items.length);
}

const GROUPS = buildGroups();

export class HelpOverlay {
  name = "HelpOverlay";
  private container: HTMLElement | null = null;
  private open = false;

  constructor() { window.addEventListener("keydown", this.onKey); }

  async init(): Promise<void> {
    const overlay = document.getElementById("ui-overlay");
    if (!overlay) return;
    this.container = document.createElement("div");
    this.container.id = "help-overlay";
    this.container.style.cssText = `position: fixed; inset: 0; background: rgba(10,14,20,0.92); z-index: 1000; display: none; align-items: center; justify-content: center;`;
    this.container.innerHTML = `
      <div style="width: 90%; max-width: 800px; max-height: 85vh; overflow: auto; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; padding: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--border);">
          <h2 style="margin: 0; font-size: 16px;">Keyboard Shortcuts</h2>
          <span style="font-size: 11px; color: var(--text-muted);">Press ? or Esc to close</span>
        </div>
        ${GROUPS.map((g) => `
          <div style="margin-bottom: 16px;">
            <div style="font-size: 10px; font-weight: 600; letter-spacing: 0.08em; color: var(--text-secondary); margin-bottom: 8px; text-transform: uppercase;">${g.title}</div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 6px;">
              ${g.items.map((i) => `
                <div style="display: flex; align-items: center; gap: 10px; padding: 6px 10px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 4px;">
                  <kbd style="font-family: monospace; font-size: 10px; padding: 2px 6px; background: var(--bg); border: 1px solid var(--border-bright); border-radius: 3px; color: var(--text-primary); min-width: 40px; text-align: center;">${i.key}</kbd>
                  <span style="font-size: 11px; color: var(--text-primary);">${i.desc}</span>
                </div>
              `).join("")}
            </div>
          </div>
        `).join("")}
      </div>
    `;
    overlay.appendChild(this.container);
    this.container.addEventListener("click", (e) => { if (e.target === this.container) this.hide(); });
    console.log("[HelpOverlay] Ready");
  }

  async destroy(): Promise<void> { window.removeEventListener("keydown", this.onKey); this.container?.remove(); }

  private onKey = (e: KeyboardEvent): void => {
    const t = e.target as HTMLElement | null;
    if (t && ["INPUT", "SELECT", "TEXTAREA"].includes(t.tagName)) return;
    if (e.key === "?" && !e.shiftKey && !e.ctrlKey && !e.metaKey && !e.altKey) { e.preventDefault(); this.toggle(); }
    if (e.key === "Escape" && this.open) this.hide();
  };

  toggle(): void { this.open ? this.hide() : this.show(); }
  show(): void { if (!this.container) return; this.container.style.display = "flex"; this.open = true; }
  hide(): void { if (!this.container) return; this.container.style.display = "none"; this.open = false; }
}

export const helpOverlay = new HelpOverlay();
registry.register(helpOverlay);