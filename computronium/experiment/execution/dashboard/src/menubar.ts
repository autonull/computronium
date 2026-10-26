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
import { listDefinitions } from "./layout/definitions.js";
import { listStageViews } from "./components/stage/registry.js";
import { wsClient } from "./ws-client.js";
import { applyPreset, getCurrentPreset } from "./layout.js";
import { openPalette } from "./palette.js";
import { helpOverlay } from "./help-overlay.js";
import { dockviewHost } from "./layout/dockview-host.js";
import { commands, layoutCommands } from "./layout/commands.js";
import type { Component } from "./components/registry.js";

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

/** Inject menubar styles once. */
function injectMenubarStyles(): void {
  if (document.getElementById("menubar-styles")) return;
  const style = document.createElement("style");
  style.id = "menubar-styles";
  style.textContent = `
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
  `;
  document.head.appendChild(style);
}

/** Create a menu button with dropdown. */
function createMenu(label: string, dropdownId: string, onToggle: (menu: HTMLElement) => void): HTMLElement {
  const menu = document.createElement("div");
  menu.className = "menubar-menu";
  menu.id = `menu-${label.toLowerCase()}`;

  const button = document.createElement("button");
  button.textContent = `${label} ▾`;
  menu.appendChild(button);

  const dropdown = document.createElement("div");
  dropdown.className = "menubar-dropdown";
  dropdown.id = dropdownId;
  menu.appendChild(dropdown);

  button.addEventListener("click", (e) => {
    e.stopPropagation();
    onToggle(menu);
  });

  return menu;
}

/** Create a menu item. */
function createMenuItem(
  label: string,
  options: {
    action?: string;
    preset?: string;
    panel?: string;
    view?: string;
    shortcut?: string;
    disabled?: boolean;
    checkbox?: boolean;
    checked?: boolean;
  } = {},
): HTMLElement {
  const item = document.createElement("div");
  item.className = "menubar-item";
  if (options.disabled) item.classList.add("disabled");

  if (options.checkbox) {
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "menubar-checkbox";
    checkbox.checked = options.checked ?? false;
    item.appendChild(checkbox);
  }

  const span = document.createElement("span");
  span.textContent = label;
  item.appendChild(span);

  if (options.shortcut) {
    const kbd = document.createElement("kbd");
    kbd.className = "shortcut";
    kbd.textContent = options.shortcut;
    item.appendChild(kbd);
  }

  if (options.action) item.dataset.action = options.action;
  if (options.preset) item.dataset.preset = options.preset;
  if (options.panel) item.dataset.panel = options.panel;
  if (options.view) item.dataset.view = options.view;

  return item;
}

/** Create a section title. */
function createSectionTitle(text: string): HTMLElement {
  const div = document.createElement("div");
  div.className = "menubar-section-title";
  div.textContent = text;
  return div;
}

/** Create a separator. */
function createSeparator(): HTMLElement {
  const div = document.createElement("div");
  div.className = "menubar-separator";
  return div;
}

/** Create a divider. */
function createDivider(): HTMLElement {
  const div = document.createElement("div");
  div.className = "menubar-divider";
  return div;
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
  private dropdownFile: HTMLElement | null = null;
  private dropdownView: HTMLElement | null = null;
  private dropdownRun: HTMLElement | null = null;
  private dropdownTools: HTMLElement | null = null;
  private dropdownWindow: HTMLElement | null = null;
  private panelToggles: HTMLElement | null = null;
  private viewToggles: HTMLElement | null = null;
  private dbList: HTMLElement | null = null;

  constructor() {
    wsClient.onStateChange((state) => this.updateConnection(state));
  }

  async init(): Promise<void> {
    injectMenubarStyles();

    // Use the existing placeholder from index.html
    this.container = document.getElementById("menubar-container");
    if (!this.container) {
      console.error("[Menubar] #menubar-container not found in HTML");
      return;
    }
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

    // Build menubar structure
    const menubar = document.createElement("div");
    menubar.className = "menubar";
    menubar.id = "menubar";

    // File menu
    const menuFile = createMenu("File", "dropdown-file", (m) => this.toggleMenu(m));
    this.dropdownFile = menuFile.querySelector("#dropdown-file");
    this.buildFileDropdown();
    menubar.appendChild(menuFile);

    menubar.appendChild(createDivider());

    // View menu
    const menuView = createMenu("View", "dropdown-view", (m) => this.toggleMenu(m));
    this.dropdownView = menuView.querySelector("#dropdown-view");
    this.buildViewDropdown();
    menubar.appendChild(menuView);

    menubar.appendChild(createDivider());

    // Run menu
    const menuRun = createMenu("Run", "dropdown-run", (m) => this.toggleMenu(m));
    this.dropdownRun = menuRun.querySelector("#dropdown-run");
    this.buildRunDropdown();
    menubar.appendChild(menuRun);

    menubar.appendChild(createDivider());

    // Tools menu
    const menuTools = createMenu("Tools", "dropdown-tools", (m) => this.toggleMenu(m));
    this.dropdownTools = menuTools.querySelector("#dropdown-tools");
    this.buildToolsDropdown();
    menubar.appendChild(menuTools);

    menubar.appendChild(createDivider());

    // Window menu
    const menuWindow = createMenu("Window", "dropdown-window", (m) => this.toggleMenu(m));
    this.dropdownWindow = menuWindow.querySelector("#dropdown-window");
    this.buildWindowDropdown();
    menubar.appendChild(menuWindow);

    // Connection status (right side)
    const spacer = document.createElement("div");
    spacer.style.flex = "1";
    menubar.appendChild(spacer);

    const connStatus = document.createElement("div");
    connStatus.style.cssText = "display: flex; align-items: center; gap: 8px; padding: 0 12px; font-size: 10px; color: var(--text-secondary);";
    connStatus.innerHTML = `
      <span class="dot" id="menubar-conn-dot" style="width: 8px; height: 8px; border-radius: 50%; background: var(--error);"></span>
      <span id="menubar-conn-label">Disconnected</span>
      <span id="menubar-db-label" style="margin-left: 12px; font-family: monospace; color: var(--text-muted);"></span>
    `;
    menubar.appendChild(connStatus);

    this.container.appendChild(menubar);

    // Dialog root
    this.dialogRoot = document.createElement("div");
    this.dialogRoot.id = "menubar-dialog-root";
    this.container.appendChild(this.dialogRoot);

    // Cache elements
    this.dbLabel = this.container.querySelector("#menubar-db-label");
    this.connDot = this.container.querySelector("#menubar-conn-dot");
    this.connLabel = this.container.querySelector("#menubar-conn-label");
    this.panelToggles = this.container.querySelector("#panel-toggles");
    this.viewToggles = this.container.querySelector("#view-toggles");
    this.dbList = this.container.querySelector("#db-list");

    this.bindMenuEvents();
    await this.loadDatabases();
    this.renderDatabaseList();
    this.renderPanelToggles();
    this.renderViewToggles();

    document.addEventListener("click", this.closeOnClickOutside);
    console.log("[Menubar] Initialized");
  }

  private buildFileDropdown(): void {
    if (!this.dropdownFile) return;
    this.dropdownFile.innerHTML = "";
    this.dropdownFile.appendChild(createSectionTitle("Database"));
    this.dbList = document.createElement("div");
    this.dbList.id = "db-list";
    this.dbList.className = "menubar-db-list";
    this.dropdownFile.appendChild(this.dbList);
    this.dropdownFile.appendChild(createSeparator());
    this.dropdownFile.appendChild(createMenuItem("New Database…", { action: "new-db", shortcut: "⌘N" }));
    this.dropdownFile.appendChild(createMenuItem("Open Database…", { action: "open-db", shortcut: "⌘O" }));
    this.dropdownFile.appendChild(createSeparator());
    this.dropdownFile.appendChild(createMenuItem("Export Database…", { action: "export-db" }));
    this.dropdownFile.appendChild(createMenuItem("Import Database…", { action: "import-db" }));
  }

  private buildViewDropdown(): void {
    if (!this.dropdownView) return;
    this.dropdownView.innerHTML = "";
    this.dropdownView.appendChild(createSectionTitle("Workspaces"));
    this.dropdownView.appendChild(createMenuItem("Watch — Campaigns", { preset: "watch", shortcut: "1" }));
    this.dropdownView.appendChild(createMenuItem("Audit — Evidence", { preset: "audit", shortcut: "2" }));
    this.dropdownView.appendChild(createMenuItem("Drive — Instrument", { preset: "drive", shortcut: "3" }));
    this.dropdownView.appendChild(createSeparator());
    this.dropdownView.appendChild(createSectionTitle("Panels"));
    this.panelToggles = document.createElement("div");
    this.panelToggles.id = "panel-toggles";
    this.dropdownView.appendChild(this.panelToggles);
    this.dropdownView.appendChild(createSeparator());
    this.dropdownView.appendChild(createMenuItem("Reset Layout", { action: "reset-layout" }));
    this.dropdownView.appendChild(createMenuItem("Save Layout", { action: "save-layout" }));
  }

  private buildRunDropdown(): void {
    if (!this.dropdownRun) return;
    this.dropdownRun.innerHTML = "";
    this.dropdownRun.appendChild(createSectionTitle("Control"));
    this.dropdownRun.appendChild(createMenuItem("Start Run…", { action: "start-run", shortcut: "Z" }));
    this.dropdownRun.appendChild(createMenuItem("Pause", { action: "pause-run", shortcut: "Space" }));
    this.dropdownRun.appendChild(createMenuItem("Step", { action: "step-run", shortcut: "⏭" }));
    this.dropdownRun.appendChild(createMenuItem("Stop", { action: "stop-run", shortcut: "⏹" }));
    this.dropdownRun.appendChild(createSeparator());
    this.dropdownRun.appendChild(createSectionTitle("Cell Actions"));
    this.dropdownRun.appendChild(createMenuItem("Replicate Cell", { action: "replicate-cell", shortcut: "⇧R" }));
    this.dropdownRun.appendChild(createMenuItem("Preregister Claim", { action: "preregister-cell", shortcut: "⇧P" }));
    this.dropdownRun.appendChild(createMenuItem("Adopt as Quest", { action: "adopt-quest", shortcut: "⇧Q" }));
  }

  private buildToolsDropdown(): void {
    if (!this.dropdownTools) return;
    this.dropdownTools.innerHTML = "";
    this.dropdownTools.appendChild(createSectionTitle("Utilities"));
    this.dropdownTools.appendChild(createMenuItem("Command Palette…", { action: "palette", shortcut: "⇧;" }));
    this.dropdownTools.appendChild(createMenuItem("Keyboard Shortcuts", { action: "help", shortcut: "?" }));
    this.dropdownTools.appendChild(createSeparator());
    this.dropdownTools.appendChild(createSectionTitle("Views"));
    this.viewToggles = document.createElement("div");
    this.viewToggles.id = "view-toggles";
    this.dropdownTools.appendChild(this.viewToggles);
  }

  private buildWindowDropdown(): void {
    if (!this.dropdownWindow) return;
    this.dropdownWindow.innerHTML = "";
    this.dropdownWindow.appendChild(createSectionTitle("Layout"));
    this.dropdownWindow.appendChild(createMenuItem("Undo", { action: "layout-undo", shortcut: "⌘Z" }));
    this.dropdownWindow.appendChild(createMenuItem("Redo", { action: "layout-redo", shortcut: "⌘⇧Z" }));
    this.dropdownWindow.appendChild(createSeparator());
    this.dropdownWindow.appendChild(createMenuItem("Save Layout…", { action: "layout-save", shortcut: "⌘S" }));
    this.dropdownWindow.appendChild(createMenuItem("Load Layout…", { action: "layout-load", shortcut: "⌘O" }));
    this.dropdownWindow.appendChild(createMenuItem("Export Layout…", { action: "layout-export" }));
    this.dropdownWindow.appendChild(createMenuItem("Import Layout…", { action: "layout-import" }));
    this.dropdownWindow.appendChild(createSeparator());
    this.dropdownWindow.appendChild(createMenuItem("Reset to Watch Preset", { action: "layout-reset" }));
    this.dropdownWindow.appendChild(createSeparator());
    this.dropdownWindow.appendChild(createMenuItem("Minimize All Panels", { action: "minimize-all" }));
    this.dropdownWindow.appendChild(createMenuItem("Restore All Panels", { action: "restore-all" }));
    this.dropdownWindow.appendChild(createSeparator());
    this.dropdownWindow.appendChild(createMenuItem("Toggle Fullscreen", { action: "toggle-fullscreen", shortcut: "F11" }));
  }

  async destroy(): Promise<void> {
    document.removeEventListener("click", this.closeOnClickOutside);
    this.container?.remove();
    this.dialogRoot?.remove();
  }

  private bindMenuEvents(): void {
    if (!this.container) return;

    // Close menus on escape
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") this.closeAllMenus();
    });

    // Menu item actions (delegated)
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
        this.togglePanel(panelId);
      } else if (viewId) {
        commands.execute(`view-${viewId}`);
      } else if (action) {
        await this.handleAction(action, item as HTMLElement);
      }
    });
  }

  /** Open a panel type, or close every instance of it. */
  private togglePanel(type: string): void {
    const open = dockviewHost.list().filter((instance) => instance.type === type);
    if (open.length > 0) {
      for (const instance of open) dockviewHost.close(instance.id);
      return;
    }
    void dockviewHost.open(type);
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
        void dockviewHost.open("control-panel");
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
        layoutCommands.applyPreset("watch");
        break;
      case "save-layout":
        layoutCommands.save();
        break;
      case "minimize-all":
        for (const instance of dockviewHost.list()) dockviewHost.close(instance.id);
        break;
      case "restore-all":
        layoutCommands.applyPreset("watch");
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
      case "layout-undo":
        layoutCommands.undo();
        break;
      case "layout-redo":
        layoutCommands.redo();
        break;
      case "layout-save":
        this.saveLayoutToFile();
        break;
      case "layout-load":
        this.loadLayoutFromFile();
        break;
      case "layout-export":
        this.exportLayoutToFile();
        break;
      case "layout-import":
        this.importLayoutFromFile();
        break;
      case "layout-reset":
        layoutCommands.applyPreset("watch");
        break;
    }
  }

  private bindPanelToggles(): void {
    dockviewHost.onChange(() => this.renderPanelToggles());
  }

  private renderPanelToggles(): void {
    if (!this.panelToggles) return;

    const openTypes = new Set(dockviewHost.list().map((instance) => instance.type));
    this.panelToggles.innerHTML = listDefinitions()
      .map((definition) => {
        const open = openTypes.has(definition.type);
        return `
          <div class="menubar-item${open ? " active" : ""}" data-panel="${definition.type}">
            <input type="checkbox" class="menubar-checkbox" ${open ? "checked" : ""}>
            <span>${definition.icon ?? ""} ${definition.title}</span>
          </div>
        `;
      })
      .join("");
  }

  private bindViewToggles(): void {
    dockviewHost.onChange(() => this.renderViewToggles());
  }

  private renderViewToggles(): void {
    if (!this.viewToggles) return;

    const views = listStageViews();
    const api = dockviewHost.getApi();
    const panel = api?.activePanel;
    const activeView = panel && panel.view.contentComponent === "stage" ? (panel.api.getParameters()?.view as string) : null;

    this.viewToggles.innerHTML = views
      .map((v) => {
        const active = v.view === activeView;
        const key = v.key ? `<kbd class="shortcut">${v.key.toUpperCase()}</kbd>` : "";
        return `
          <div class="menubar-item${active ? " active" : ""}" data-view="${v.view}">
            <input type="checkbox" class="menubar-checkbox" ${active ? "checked" : ""}>
            <span>${v.title}</span>
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
    if (!this.dbList) return;

    if (this.databases.length === 0) {
      this.dbList.innerHTML = '<div class="menubar-item disabled">No databases found</div>';
      return;
    }

    this.dbList.innerHTML = this.databases.map((db) => {
      const active = db.path === this.currentDbPath;
      const sizeMb = (db.size / 1024 / 1024).toFixed(1);
      return `
        <div class="menubar-db-item${active ? " active" : ""}" data-path="${db.path}" data-action="switch-db">
          <span class="menubar-db-name">${db.name}${active ? " ●" : ""}</span>
          <span class="menubar-db-meta">${sizeMb} MB · ${db.runs} runs · ${new Date(db.modified).toLocaleString()}</span>
        </div>
      `;
    }).join("");

    if (this.dbLabel && this.currentDbPath) {
      const current = this.databases.find((d) => d.path === this.currentDbPath);
      this.dbLabel.textContent = current ? current.name : this.currentDbPath;
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

  private saveLayoutToFile(): void {
    const doc = layoutCommands.save();
    if (!doc) return;
    const blob = new Blob([JSON.stringify(doc, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `computronium-layout-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  private loadLayoutFromFile(): void {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".json";
    input.addEventListener("change", async () => {
      const file = input.files?.[0];
      if (!file) return;
      try {
        const text = await file.text();
        const doc = JSON.parse(text);
        await layoutCommands.load(doc);
      } catch (e) {
        alert(`Failed to load layout: ${(e as Error).message}`);
      }
    });
    input.click();
  }

  private exportLayoutToFile(): void {
    const doc = layoutCommands.save();
    if (!doc) return;
    const blob = new Blob([JSON.stringify(doc, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `computronium-layout-export-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  private importLayoutFromFile(): void {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".json";
    input.addEventListener("change", async () => {
      const file = input.files?.[0];
      if (!file) return;
      try {
        const text = await file.text();
        const doc = JSON.parse(text);
        await layoutCommands.load(doc);
      } catch (e) {
        alert(`Failed to import layout: ${(e as Error).message}`);
      }
    });
    input.click();
  }
}

export const menubar = new Menubar();
registry.register(menubar);