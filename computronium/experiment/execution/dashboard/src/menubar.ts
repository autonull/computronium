/** Menubar — Top-level application menu (TODO71 Phase 3).
 *
 *  Fixed at the top of the screen, provides system-wide controls:
 *  - File: Database management (switch, create, open)
 *  - View: Presets, panel visibility
 *  - Run: Start, stop, control
 *  - Tools: Palette, help, settings
 *  - Window: Layout management
 */

import { registry } from "./components/registry.js";
import { panels } from "./panels.js";
import { layoutManager, registerLayoutComponent } from "./layout-manager.js";
import { viewSwitcher } from "./stage/switcher.js";
import { wsClient } from "./ws-client.js";
import { applyPreset, getCurrentPreset } from "./layout.js";
import { openPalette } from "./palette.js";
import { helpOverlay } from "./help-overlay.js";
import { runSelection } from "./run-selection.js";
import type { Component } from "./components/registry.js";

function getLegacyControlPanel(): any {
  return (window as any).__DASHBOARD__?.controlPanel ?? null;
}
function getLegacyControlBar(): any {
  return (window as any).__DASHBOARD__?.controlBar ?? null;
}
function getLegacyCellDrawer(): any {
  return (window as any).__DASHBOARD__?.cellDrawer ?? null;
}

interface DatabaseInfo {
  path: string;
  name: string;
  size: number;
  modified: string;
  runs: number;
}

function createMenubarBody(): string {
  return `
    <style>
      .menubar {
        display: flex;
        align-items: center;
        gap: 0;
        height: 28px;
        background: var(--bg-tertiary);
        border-bottom: 1px solid var(--border);
        font-size: 12px;
        color: var(--text-primary);
        user-select: none;
        -webkit-app-region: drag;
      }
      .menubar-menu {
        position: relative;
      }
      .menubar-menu > button {
        padding: 0 12px;
        height: 100%;
        background: transparent;
        border: none;
        color: var(--text-primary);
        font-size: 12px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 4px;
        -webkit-app-region: no-drag;
      }
      .menubar-menu > button:hover,
      .menubar-menu > button:focus {
        background: var(--bg-primary);
      }
      .menubar-menu.open > button {
        background: var(--bg-primary);
        color: var(--gradient);
      }
      .menubar-divider {
        width: 1px;
        height: 16px;
        background: var(--border);
        margin: 0 4px;
      }
      .menubar-dropdown {
        position: absolute;
        top: 100%;
        left: 0;
        min-width: 220px;
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 0 0 6px 6px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        z-index: 1000;
        display: none;
        flex-direction: column;
        padding: 4px 0;
      }
      .menubar-menu.open .menubar-dropdown {
        display: flex;
      }
      .menubar-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 12px;
        color: var(--text-primary);
        font-size: 11px;
        cursor: pointer;
        white-space: nowrap;
        -webkit-app-region: no-drag;
      }
      .menubar-item:hover,
      .menubar-item:focus {
        background: var(--bg-tertiary);
        color: var(--gradient);
      }
      .menubar-item.disabled {
        color: var(--text-muted);
        cursor: not-allowed;
      }
      .menubar-item.disabled:hover {
        background: transparent;
        color: var(--text-muted);
      }
      .menubar-item .shortcut {
        margin-left: auto;
        font-family: monospace;
        font-size: 9px;
        padding: 1px 4px;
        background: var(--bg);
        border: 1px solid var(--border);
        border-radius: 3px;
        color: var(--text-muted);
      }
      .menubar-separator {
        height: 1px;
        background: var(--border);
        margin: 4px 8px;
      }
      .menubar-submenu {
        position: relative;
      }
      .menubar-submenu > .menubar-dropdown {
        left: 100%;
        top: 0;
        border-radius: 0 6px 6px 6px;
      }
      .menubar-submenu.open > .menubar-dropdown {
        display: flex;
      }
      .menubar-checkbox {
        width: 14px;
        height: 14px;
        accent-color: var(--gradient);
      }
      .menubar-section-title {
        padding: 6px 12px 2px;
        font-size: 9px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        font-weight: 600;
      }
      .menubar-db-item {
        display: flex;
        flex-direction: column;
        gap: 2px;
        padding: 8px 12px;
      }
      .menubar-db-name {
        font-weight: 500;
        color: var(--text-primary);
      }
      .menubar-db-meta {
        font-size: 9px;
        color: var(--text-muted);
      }
      .menubar-db-item.active .menubar-db-name {
        color: var(--gradient);
      }
      .menubar-input {
        width: 100%;
        padding: 4px 8px;
        background: var(--bg);
        border: 1px solid var(--border);
        border-radius: 4px;
        color: var(--text-primary);
        font-size: 11px;
        font-family: monospace;
      }
      .menubar-input:focus {
        outline: none;
        border-color: var(--gradient);
      }
      .menubar-dialog {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: var(--bg-secondary);
        border: 1px solid var(--border-bright);
        border-radius: 8px;
        padding: 16px;
        min-width: 360px;
        box-shadow: 0 16px 48px rgba(0,0,0,0.5);
        z-index: 2000;
      }
      .menubar-dialog-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.5);
        backdrop-filter: blur(2px);
        z-index: 1999;
      }
      .menubar-dialog-title {
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 12px;
      }
      .menubar-dialog-buttons {
        display: flex;
        justify-content: flex-end;
        gap: 8px;
        margin-top: 16px;
      }
      .menubar-btn {
        padding: 6px 12px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 4px;
        color: var(--text-primary);
        font-size: 11px;
        cursor: pointer;
      }
      .menubar-btn:hover {
        background: var(--border);
      }
      .menubar-btn.primary {
        background: var(--gradient)22;
        border-color: var(--gradient)66;
        color: var(--gradient);
      }
      .menubar-btn.primary:hover {
        background: var(--gradient)33;
        border-color: var(--gradient);
      }
      .menubar-btn.danger {
        background: var(--error)22;
        border-color: var(--error)66;
        color: var(--error);
      }
      .menubar-btn.danger:hover {
        background: var(--error)33;
        border-color: var(--error);
      }
    </style>
    <div class="menubar" id="menubar">
      <!-- File Menu -->
      <div class="menubar-menu" id="menu-file">
        <button>File ▾</button>
        <div class="menubar-dropdown" id="dropdown-file">
          <div class="menubar-section-title">Database</div>
          <div id="db-list" class="menubar-db-list"></div>
          <div class="menubar-separator"></div>
          <div class="menubar-item" data-action="new-db">
            <span>New Database…</span>
            <kbd class="shortcut">⌘N</kbd>
          </div>
          <div class="menubar-item" data-action="open-db">
            <span>Open Database…</span>
            <kbd class="shortcut">⌘O</kbd>
          </div>
          <div class="menubar-separator"></div>
          <div class="menubar-item" data-action="export-db">
            <span>Export Database…</span>
          </div>
          <div class="menubar-item" data-action="import-db">
            <span>Import Database…</span>
          </div>
        </div>
      </div>

      <!-- View Menu -->
      <div class="menubar-menu" id="menu-view">
        <button>View ▾</button>
        <div class="menubar-dropdown" id="dropdown-view">
          <div class="menubar-section-title">Workspaces</div>
          <div class="menubar-item" data-preset="watch">
            <span>Watch — Campaigns</span>
            <kbd class="shortcut">1</kbd>
          </div>
          <div class="menubar-item" data-preset="audit">
            <span>Audit — Evidence</span>
            <kbd class="shortcut">2</kbd>
          </div>
          <div class="menubar-item" data-preset="drive">
            <span>Drive — Instrument</span>
            <kbd class="shortcut">3</kbd>
          </div>
          <div class="menubar-separator"></div>
          <div class="menubar-section-title">Panels</div>
          <div id="panel-toggles"></div>
          <div class="menubar-separator"></div>
          <div class="menubar-item" data-action="reset-layout">
            <span>Reset Layout</span>
          </div>
          <div class="menubar-item" data-action="save-layout">
            <span>Save Layout</span>
          </div>
        </div>
      </div>

      <!-- Run Menu -->
      <div class="menubar-menu" id="menu-run">
        <button>Run ▾</button>
        <div class="menubar-dropdown" id="dropdown-run">
          <div class="menubar-section-title">Control</div>
          <div class="menubar-item" data-action="start-run">
            <span>Start Run…</span>
            <kbd class="shortcut">Z</kbd>
          </div>
          <div class="menubar-item" data-action="pause-run">
            <span>Pause</span>
            <kbd class="shortcut">Space</kbd>
          </div>
          <div class="menubar-item" data-action="step-run">
            <span>Step</span>
            <kbd class="shortcut">⏭</kbd>
          </div>
          <div class="menubar-item" data-action="stop-run">
            <span>Stop</span>
            <kbd class="shortcut">⏹</kbd>
          </div>
          <div class="menubar-separator"></div>
          <div class="menubar-section-title">Cell Actions</div>
          <div class="menubar-item" data-action="replicate-cell">
            <span>Replicate Cell</span>
            <kbd class="shortcut">⇧R</kbd>
          </div>
          <div class="menubar-item" data-action="preregister-cell">
            <span>Preregister Claim</span>
            <kbd class="shortcut">⇧P</kbd>
          </div>
          <div class="menubar-item" data-action="adopt-quest">
            <span>Adopt as Quest</span>
            <kbd class="shortcut">⇧Q</kbd>
          </div>
        </div>
      </div>

      <!-- Tools Menu -->
      <div class="menubar-menu" id="menu-tools">
        <button>Tools ▾</button>
        <div class="menubar-dropdown" id="dropdown-tools">
          <div class="menubar-section-title">Utilities</div>
          <div class="menubar-item" data-action="palette">
            <span>Command Palette…</span>
            <kbd class="shortcut">⇧;</kbd>
          </div>
          <div class="menubar-item" data-action="help">
            <span>Keyboard Shortcuts</span>
            <kbd class="shortcut">?</kbd>
          </div>
          <div class="menubar-separator"></div>
          <div class="menubar-section-title">Views</div>
          <div id="view-toggles"></div>
        </div>
      </div>

      <!-- Window Menu -->
      <div class="menubar-menu" id="menu-window">
        <button>Window ▾</button>
        <div class="menubar-dropdown" id="dropdown-window">
          <div class="menubar-section-title">Layout</div>
          <div class="menubar-item" data-action="minimize-all">
            <span>Minimize All Panels</span>
          </div>
          <div class="menubar-item" data-action="restore-all">
            <span>Restore All Panels</span>
          </div>
          <div class="menubar-separator"></div>
          <div class="menubar-item" data-action="toggle-fullscreen">
            <span>Toggle Fullscreen</span>
            <kbd class="shortcut">F11</kbd>
          </div>
        </div>
      </div>

      <!-- Connection Status (right side) -->
      <div style="flex: 1;"></div>
      <div class="menubar-connection" style="display: flex; align-items: center; gap: 8px; padding: 0 12px; font-size: 10px; color: var(--text-secondary);">
        <span class="dot" id="menubar-conn-dot" style="width: 8px; height: 8px; border-radius: 50%; background: var(--error);"></span>
        <span id="menubar-conn-label">Disconnected</span>
        <span id="menubar-db-label" style="margin-left: 12px; font-family: monospace; color: var(--text-muted);"></span>
      </div>
    </div>
    <div id="menubar-dialog-root"></div>
  `;
}

export class Menubar implements Component {
  name = "Menubar";
  private container: HTMLElement | null = null;
  private dbLabel: HTMLElement | null = null;
  private connDot: HTMLElement | null = null;
  private connLabel: HTMLElement | null = null;
  private dialogRoot: HTMLElement | null = null;
  private currentDbPath: string | null = null;
  private databases: DatabaseInfo[] = [];
  private closeOnClickOutside = (e: MouseEvent) => this.handleClickOutside(e);

  constructor() {
    wsClient.onStateChange((state) => this.updateConnection(state));
  }

  async init(): Promise<void> {
    this.container = document.createElement("div");
    this.container.id = "menubar-container";
    this.container.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: 28px;
      z-index: 1000;
      pointer-events: auto;
      -webkit-app-region: drag;
    `;
    this.container.innerHTML = createMenubarBody();
    document.body.appendChild(this.container);

    this.dialogRoot = document.getElementById("menubar-dialog-root");
    this.dbLabel = this.container.querySelector("#menubar-db-label");
    this.connDot = this.container.querySelector("#menubar-conn-dot");
    this.connLabel = this.container.querySelector("#menubar-conn-label");

    this.bindMenuEvents();
    this.bindPanelToggles();
    this.bindViewToggles();
    await this.loadDatabases();
    this.renderDatabaseList();
    this.renderPanelToggles();
    this.renderViewToggles();

    document.addEventListener("click", this.closeOnClickOutside);
    console.log("[Menubar] Initialized");
  }

  async destroy(): Promise<void> {
    document.removeEventListener("click", this.closeOnClickOutside);
    this.container?.remove();
    this.dialogRoot?.remove();
  }

  private bindMenuEvents(): void {
    if (!this.container) return;

    // Menu open/close on click
    for (const menu of this.container.querySelectorAll<HTMLElement>(".menubar-menu")) {
      const button = menu.querySelector("button");
      button?.addEventListener("click", (e) => {
        e.stopPropagation();
        this.toggleMenu(menu);
      });
    }

    // Close menus on escape
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") this.closeAllMenus();
    });

    // Menu item actions
    this.container.addEventListener("click", async (e) => {
      const item = (e.target as HTMLElement).closest(".menubar-item") as HTMLElement;
      if (!item || item.classList.contains("disabled")) return;

      const action = item.dataset.action;
      const preset = item.dataset.preset;
      const panelId = item.dataset.panel;
      const viewId = item.dataset.view;

      this.closeAllMenus();

      if (preset) {
        applyPreset(preset as any);
      } else if (panelId) {
        panels.toggle(panelId);
      } else if (viewId) {
        viewSwitcher.show(viewId);
      } else if (action) {
        await this.handleAction(action, item as HTMLElement);
      }
    });
  }

  private toggleMenu(menu: HTMLElement): void {
    const isOpen = menu.classList.contains("open");
    this.closeAllMenus();
    if (!isOpen) menu.classList.add("open");
  }

  private closeAllMenus(): void {
    this.container?.querySelectorAll(".menubar-menu").forEach((m) => m.classList.remove("open"));
    this.container?.querySelectorAll(".menubar-submenu").forEach((m) => m.classList.remove("open"));
  }

  private handleClickOutside(e: MouseEvent): void {
    if (!(e.target as HTMLElement).closest(".menubar-menu")) {
      this.closeAllMenus();
    }
    if (!(e.target as HTMLElement).closest(".menubar-dialog") && !(e.target as HTMLElement).closest(".menubar-item")) {
      this.closeDialogs();
    }
  }

  private closeDialogs(): void {
    this.dialogRoot?.querySelectorAll(".menubar-dialog-overlay").forEach((o) => o.remove());
    this.dialogRoot?.querySelectorAll(".menubar-dialog").forEach((d) => d.remove());
  }

  private async handleAction(action: string, item: HTMLElement): Promise<void> {
    switch (action) {
      case "start-run":
        panels.toggle("control-panel");
        getLegacyControlPanel()?.showSection("new-run");
        break;
      case "pause-run":
        getLegacyControlBar()?.togglePlay();
        break;
      case "step-run":
        getLegacyControlBar()?.step();
        break;
      case "stop-run":
        getLegacyControlBar()?.stop();
        break;
      case "replicate-cell":
        getLegacyCellDrawer()?.replicateSelected?.();
        break;
      case "preregister-cell":
        getLegacyCellDrawer()?.preregisterSelected?.();
        break;
      case "adopt-quest":
        getLegacyCellDrawer()?.adoptQuestSelected?.();
        break;
      case "palette":
        openPalette();
        break;
      case "help":
        helpOverlay.toggle();
        break;
      case "reset-layout":
        layoutManager.reset();
        break;
      case "save-layout":
        localStorage.setItem("computronium-dashboard-layout", JSON.stringify(layoutManager.getConfig()));
        break;
      case "minimize-all":
        for (const p of panels.list()) { if (p.isOpen()) p.toggle(); }
        break;
      case "restore-all":
        for (const p of panels.list()) { if (!p.isOpen()) p.toggle(); }
        break;
      case "toggle-fullscreen":
        if (!document.fullscreenElement) {
          document.documentElement.requestFullscreen().catch(() => {});
        } else {
          document.exitFullscreen().catch(() => {});
        }
        break;
      case "new-db":
        this.showNewDatabaseDialog();
        break;
      case "open-db":
        this.showOpenDatabaseDialog();
        break;
      case "switch-db":
        const dbItem = item.closest(".menubar-db-item") as HTMLElement | null;
        const dbPath = dbItem?.dataset.path;
        if (dbPath) await this.switchDatabase(dbPath);
        break;
      case "export-db":
        this.exportDatabase();
        break;
      case "import-db":
        this.importDatabase();
        break;
    }
  }

  private bindPanelToggles(): void {
    panels.onChange(() => this.renderPanelToggles());
  }

  private renderPanelToggles(): void {
    const container = this.container?.querySelector("#panel-toggles");
    if (!container) return;

    const panelOrder = ["control-bar", "live-rail", "caption", "discovery-legend", "hud", "control-panel", "cell-drawer", "pareto-chart", "ablation-chart", "variability-chart", "help-overlay"];
    container.innerHTML = panelOrder
      .map((id) => {
        const panel = panels.get(id);
        if (!panel) return "";
        const open = panel.isOpen();
        const key = panel.key ? `<kbd class="shortcut">${panel.key.toUpperCase()}</kbd>` : "";
        return `
          <div class="menubar-item${open ? " active" : ""}" data-panel="${id}">
            <input type="checkbox" class="menubar-checkbox" ${open ? "checked" : ""}>
            <span>${panel.label}</span>
            ${key}
          </div>
        `;
      })
      .join("");
  }

  private bindViewToggles(): void {
    viewSwitcher.getViews().forEach((v) => {
      // Views don't have a change event, but we can rebuild on layout change
    });
    layoutManager.getGoldenLayout()?.on("stateChanged", () => this.renderViewToggles());
  }

  private renderViewToggles(): void {
    const container = this.container?.querySelector("#view-toggles");
    if (!container) return;

    const views = viewSwitcher.getViews();
    const activeId = viewSwitcher.activeId;
    container.innerHTML = views
      .map((v) => {
        const active = v.id === activeId;
        const key = v.key ? `<kbd class="shortcut">${v.key.toUpperCase()}</kbd>` : "";
        return `
          <div class="menubar-item${active ? " active" : ""}" data-view="${v.id}">
            <input type="checkbox" class="menubar-checkbox" ${active ? "checked" : ""}>
            <span>${v.name}</span>
            ${key}
          </div>
        `;
      })
      .join("");
  }

  private updateConnection(state: string): void {
    if (!this.connDot || !this.connLabel) return;
    const connected = state === "connected";
    this.connDot.style.background = connected ? "var(--ok)" : "var(--error)";
    this.connLabel.textContent = connected ? "Connected" : "Disconnected";
  }

  private async loadDatabases(): Promise<void> {
    try {
      const res = await fetch("/api/databases");
      if (res.ok) {
        const data = await res.json();
        this.databases = data.databases ?? [];
        this.currentDbPath = data.current ?? null;
      }
    } catch {
      // Fallback to default
      this.databases = [{
        path: "experiment.duckdb",
        name: "experiment.duckdb",
        size: 0,
        modified: new Date().toISOString(),
        runs: 0,
      }];
      this.currentDbPath = "experiment.duckdb";
    }
  }

  private renderDatabaseList(): void {
    const container = this.container?.querySelector("#db-list");
    const label = this.dbLabel;
    if (!container) return;

    if (this.databases.length === 0) {
      container.innerHTML = '<div class="menubar-item disabled">No databases found</div>';
      return;
    }

    container.innerHTML = this.databases.map((db) => {
      const active = db.path === this.currentDbPath;
      const sizeMb = (db.size / 1024 / 1024).toFixed(1);
      return `
        <div class="menubar-db-item${active ? " active" : ""}" data-path="${db.path}" data-action="switch-db">
          <span class="menubar-db-name">${db.name}${active ? " ●" : ""}</span>
          <span class="menubar-db-meta">${sizeMb} MB · ${db.runs} runs · ${new Date(db.modified).toLocaleString()}</span>
        </div>
      `;
    }).join("");

    if (label && this.currentDbPath) {
      const current = this.databases.find((d) => d.path === this.currentDbPath);
      label.textContent = current ? current.name : this.currentDbPath;
    }
  }

  private showNewDatabaseDialog(): void {
    this.closeDialogs();
    if (!this.dialogRoot) return;

    const overlay = document.createElement("div");
    overlay.className = "menubar-dialog-overlay";
    overlay.addEventListener("click", () => this.closeDialogs());

    const dialog = document.createElement("div");
    dialog.className = "menubar-dialog";
    dialog.innerHTML = `
      <div class="menubar-dialog-title">New Database</div>
      <div style="margin-bottom: 12px;">
        <label style="display: block; margin-bottom: 4px; font-size: 11px; color: var(--text-secondary);">Database name</label>
        <input type="text" class="menubar-input" id="new-db-name" placeholder="my-experiment" value="experiment">
      </div>
      <div style="margin-bottom: 12px;">
        <label style="display: block; margin-bottom: 4px; font-size: 11px; color: var(--text-secondary);">Path (relative to workspace)</label>
        <input type="text" class="menubar-input" id="new-db-path" placeholder="experiment.duckdb">
      </div>
      <div class="menubar-dialog-buttons">
        <button class="menubar-btn" data-cancel>Cancel</button>
        <button class="menubar-btn primary" data-create>Create</button>
      </div>
    `;

    dialog.querySelector("[data-cancel]")?.addEventListener("click", () => this.closeDialogs());
    dialog.querySelector("[data-create]")?.addEventListener("click", () => this.createDatabase(dialog));

    overlay.appendChild(dialog);
    this.dialogRoot.appendChild(overlay);
    this.dialogRoot.appendChild(dialog);
    (dialog.querySelector("#new-db-name") as HTMLInputElement)?.focus();
  }

  private showOpenDatabaseDialog(): void {
    this.closeDialogs();
    if (!this.dialogRoot) return;

    const overlay = document.createElement("div");
    overlay.className = "menubar-dialog-overlay";
    overlay.addEventListener("click", () => this.closeDialogs());

    const dialog = document.createElement("div");
    dialog.className = "menubar-dialog";
    dialog.style.maxHeight = "60vh";
    dialog.style.overflow = "auto";
    dialog.innerHTML = `
      <div class="menubar-dialog-title">Open Database</div>
      <div style="margin-bottom: 12px;">
        <input type="text" class="menubar-input" id="open-db-search" placeholder="Search databases…">
      </div>
      <div id="open-db-list" style="max-height: 300px; overflow: auto;"></div>
      <div class="menubar-dialog-buttons">
        <button class="menubar-btn" data-cancel>Cancel</button>
      </div>
    `;

    const list = dialog.querySelector("#open-db-list")!;
    list.innerHTML = this.databases.map((db) => `
      <div class="menubar-db-item" data-path="${db.path}" style="cursor: pointer; padding: 8px 12px; border-radius: 4px;">
        <span class="menubar-db-name">${db.name}</span>
        <span class="menubar-db-meta">${(db.size / 1024 / 1024).toFixed(1)} MB · ${db.runs} runs</span>
      </div>
    `).join("");

    list.addEventListener("click", (e) => {
      const item = (e.target as HTMLElement).closest(".menubar-db-item") as HTMLElement | null;
      if (item) {
        this.switchDatabase(item.dataset.path!);
        this.closeDialogs();
      }
    });

    dialog.querySelector("[data-cancel]")?.addEventListener("click", () => this.closeDialogs());
    overlay.appendChild(dialog);
    this.dialogRoot.appendChild(overlay);
    this.dialogRoot.appendChild(dialog);
    (dialog.querySelector("#open-db-search") as HTMLInputElement)?.focus();
  }

  private async createDatabase(dialog: HTMLElement): Promise<void> {
    const nameInput = dialog.querySelector("#new-db-name") as HTMLInputElement;
    const pathInput = dialog.querySelector("#new-db-path") as HTMLInputElement;
    const name = nameInput?.value.trim() || "experiment";
    const path = pathInput?.value.trim() || `${name}.duckdb`;

    try {
      const res = await fetch("/api/databases/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, path }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to create database");

      this.closeDialogs();
      await this.loadDatabases();
      this.renderDatabaseList();
      await this.switchDatabase(data.path);
    } catch (e) {
      alert(`Failed to create database: ${(e as Error).message}`);
    }
  }

  private async switchDatabase(path: string): Promise<void> {
    try {
      const res = await fetch("/api/databases/switch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to switch database");

      this.currentDbPath = path;
      await this.loadDatabases();
      this.renderDatabaseList();

      // Reload the dashboard's store
      location.reload();
    } catch (e) {
      alert(`Failed to switch database: ${(e as Error).message}`);
    }
  }

  private exportDatabase(): void {
    if (!this.currentDbPath) return;
    window.open(`/api/databases/export?path=${encodeURIComponent(this.currentDbPath)}`, "_blank");
  }

  private importDatabase(): void {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".duckdb,.db,.sqlite";
    input.addEventListener("change", async () => {
      const file = input.files?.[0];
      if (!file) return;
      const formData = new FormData();
      formData.append("file", file);
      try {
        const res = await fetch("/api/databases/import", { method: "POST", body: formData });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Failed to import database");
        await this.loadDatabases();
        this.renderDatabaseList();
      } catch (e) {
        alert(`Failed to import database: ${(e as Error).message}`);
      }
    });
    input.click();
  }
}

export const menubar = new Menubar();
registry.register(menubar);