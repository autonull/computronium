/** Help Overlay — Keyboard Shortcuts Reference (press ?). */

import { registry } from "./components/registry.js";
import { PANEL_KEYS } from "./keys.js";
import { TAB_KEYS } from "./keys.js";
import { CONTROL_KEYS } from "./keys.js";
import { CYCLE_KEY } from "./keys.js";
import { closeButton, panels, registerDisplayPanel } from "./panels.js";
import type { Component } from "./components/registry.js";

interface ShortcutGroup {
  title: string;
  items: Array<{ key: string; description: string }>;
}

const SHORTCUT_GROUPS: ShortcutGroup[] = [
  {
    title: "Navigation",
    items: [
      { key: CYCLE_KEY, description: "Cycle stage views" },
      { key: "Mouse drag", description: "Orbit camera" },
      { key: "Scroll", description: "Zoom camera" },
      { key: "Shift + drag", description: "Pan camera" },
    ],
  },
  {
    title: "Panels",
    items: [
      { key: PANEL_KEYS.hud, description: "Toggle Mission Control (HUD)" },
      { key: PANEL_KEYS.rail, description: "Toggle Live Rail" },
      { key: PANEL_KEYS.caption, description: "Toggle Caption" },
      { key: PANEL_KEYS.legend, description: "Toggle Legend" },
      { key: CONTROL_KEYS.panel, description: "Toggle Control Panel" },
    ],
  },
  {
    title: "Charts",
    items: [
      { key: TAB_KEYS.pareto, description: "Show Pareto frontier" },
      { key: TAB_KEYS.ablation, description: "Show Ablation chart" },
      { key: TAB_KEYS.variability, description: "Show Variability chart" },
    ],
  },
  {
    title: "Run Control",
    items: [
      { key: CONTROL_KEYS.play, description: "Play / Pause run" },
      { key: CONTROL_KEYS.step, description: "Step one batch" },
      { key: CONTROL_KEYS.stop, description: "Stop run" },
    ],
  },
  {
    title: "Cell Actions (click a cell first)",
    items: [
      { key: "R", description: "Replicate (queue remaining seeds)" },
      { key: "P", description: "Preregister (confirm protocol)" },
      { key: "Q", description: "Adopt as Quest (new run)" },
    ],
  },
  {
    title: "General",
    items: [
      { key: "?", description: "Show this help" },
      { key: "Esc", description: "Close drawer / dismiss" },
    ],
  },
];

export class HelpOverlay implements Component {
  name = "HelpOverlay";

  private container: HTMLElement | null = null;
  private isOpen = false;

  constructor() {
    window.addEventListener("keydown", this.onKeyDown);
  }

  async init(): Promise<void> {
    this.createOverlay();
    console.log("[HelpOverlay] Initialized");
  }

  async destroy(): Promise<void> {
    window.removeEventListener("keydown", this.onKeyDown);
    this.container?.remove();
  }

  private onKeyDown = (event: KeyboardEvent): void => {
    if (event.key === "?" && !event.shiftKey && !event.ctrlKey && !event.metaKey && !event.altKey) {
      const target = event.target as HTMLElement | null;
      if (target && ["INPUT", "SELECT", "TEXTAREA"].includes(target.tagName)) {
        return;
      }
      event.preventDefault();
      this.toggle();
    }
    if (event.key === "Escape" && this.isOpen) {
      this.hide();
    }
  };

  private createOverlay(): void {
    const overlay = document.getElementById("ui-overlay");
    if (!overlay) return;

    this.container = document.createElement("div");
    this.container.id = "help-overlay";
    this.container.style.cssText = `
      position: fixed;
      inset: 0;
      background: rgba(10, 14, 20, 0.92);
      z-index: 1000;
      display: none;
      align-items: center;
      justify-content: center;
      opacity: 0;
      transition: opacity 0.2s ease;
    `;

    const groupsHtml = SHORTCUT_GROUPS.map((group) => `
      <div style="margin-bottom: 24px;">
        <div style="font-size: 11px; font-weight: 600; letter-spacing: 0.08em; color: var(--text-secondary); margin-bottom: 12px; text-transform: uppercase;">${group.title}</div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 8px;">
          ${group.items.map((item) => `
            <div style="display: flex; align-items: center; gap: 12px; padding: 8px 12px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 6px;">
              <kbd style="
                font-family: 'JetBrains Mono', monospace;
                font-size: 11px;
                padding: 2px 8px;
                background: var(--bg);
                border: 1px solid var(--border-bright);
                border-radius: 4px;
                color: var(--text-primary);
                min-width: 48px;
                text-align: center;
                box-shadow: 0 1px 2px rgba(0,0,0,0.3);
              ">${item.key}</kbd>
              <span style="font-size: 12px; color: var(--text-primary);">${item.description}</span>
            </div>
          `).join("")}
        </div>
      </div>
    `).join("");

    this.container.innerHTML = `
      <div style="
        width: 90%;
        max-width: 800px;
        max-height: 85vh;
        overflow-y: auto;
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 32px;
        box-shadow: 0 24px 64px rgba(0,0,0,0.6);
        transform: scale(0.95);
        transition: transform 0.2s ease;
      ">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--border);">
          <h2 style="margin: 0; font-size: 18px; font-weight: 600; letter-spacing: 0.02em;">Keyboard Shortcuts</h2>
          <span style="font-size: 11px; color: var(--text-muted);">Press <kbd style="font-family: 'JetBrains Mono', monospace; padding: 1px 6px; background: var(--bg); border: 1px solid var(--border); border-radius: 3px;">?</kbd> again to close</span>
        </div>
        ${groupsHtml}
      </div>
    `;

    overlay.appendChild(this.container);

    // Click backdrop to close
    this.container.addEventListener("click", (event) => {
      if (event.target === this.container) {
        this.hide();
      }
    });
  }

  toggle(): void {
    if (this.isOpen) this.hide();
    else this.show();
  }

  show(): void {
    if (!this.container) return;
    this.container.style.display = "flex";
    requestAnimationFrame(() => {
      this.container!.style.opacity = "1";
      const dialog = this.container!.querySelector("div");
      if (dialog) (dialog as HTMLElement).style.transform = "scale(1)";
    });
    this.isOpen = true;
    document.body.style.overflow = "hidden";
  }

  hide(): void {
    if (!this.container) return;
    this.container.style.opacity = "0";
    const dialog = this.container.querySelector("div");
    if (dialog) (dialog as HTMLElement).style.transform = "scale(0.95)";
    setTimeout(() => {
      if (this.container) this.container.style.display = "none";
    }, 200);
    this.isOpen = false;
    document.body.style.overflow = "";
  }
}

export const helpOverlay = new HelpOverlay();
registry.register(helpOverlay);