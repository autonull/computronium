/** The layout grammar — docks, a manager, and workspaces (TODO71 Phase 2).
 *
 *  Five docks — top strip, bottom strip, left column, right column, and
 *  floating — and one LayoutManager that owns coordinates, z-order, and
 *  membership. A panel declares its preferred dock and its default openness;
 *  the default placement table reproduces today's screen exactly.
 *
 *  A workspace is one row of layout data — {the view on the stage, the
 *  panels that are open, their dock order} — read by the same manager.
 *  Three ship, plus the reader's own:
 *    watch  — today's default screen
 *    audit  — ledger view + three charts open
 *    drive  — flow view + control panel open
 *    free   — whatever the reader arranged (any manual change moves here)
 *
 *  Persistence is localStorage, versioned (computronium.layout.v1). A
 *  version bump clears it; the tour calls layout.reset() before every shot set.
 */

import { panels, type Panel } from "./panels.js";
import { viewSwitcher } from "./stage/switcher.js";

/** Dock regions. */
export type Dock = "top" | "bottom" | "left" | "right" | "floating";

/** Where a panel prefers to live. */
export interface DockPreference {
  /** The dock this panel belongs in. */
  dock: Dock;
  /** Default z-index within the dock (higher = on top). */
  zIndex?: number;
  /** Whether this panel opens by default in the watch workspace. */
  defaultOpen?: boolean;
  /** Minimum size for the dock (pixels or fraction). */
  minSize?: number;
  /** Maximum size for the dock. */
  maxSize?: number;
}

/** A panel's current placement. */
export interface PanelPlacement {
  id: string;
  dock: Dock;
  order: number;
  isOpen: boolean;
  bounds?: DOMRect;
}

/** A saved workspace arrangement. */
export interface WorkspaceData {
  /** Workspace identifier. */
  id: "watch" | "audit" | "drive" | "free";
  /** The view showing on the stage. */
  viewId: string;
  /** Panel placements in this workspace. */
  placements: PanelPlacement[];
  /** When this workspace was last active (for persistence). */
  updatedAt: number;
}

/** The built-in workspaces. */
export const WORKSPACES: Record<string, Omit<WorkspaceData, "updatedAt">> = {
  watch: {
    id: "watch",
    viewId: "space",
    placements: [
      { id: "control-bar", dock: "bottom", order: 0, isOpen: true },
      { id: "live-rail", dock: "right", order: 0, isOpen: true },
      { id: "caption", dock: "bottom", order: 1, isOpen: true },
      { id: "legend", dock: "bottom", order: 2, isOpen: true },
      { id: "hud", dock: "top", order: 0, isOpen: false },
      { id: "plotter-pareto", dock: "right", order: 1, isOpen: true },
      { id: "plotter-ablation", dock: "right", order: 2, isOpen: false },
      { id: "plotter-variability", dock: "right", order: 3, isOpen: false },
      { id: "cell-drawer", dock: "floating", order: 0, isOpen: false },
      { id: "control-panel", dock: "floating", order: 1, isOpen: false },
      { id: "help-overlay", dock: "floating", order: 2, isOpen: false },
    ],
  },
  audit: {
    id: "audit",
    viewId: "ledger",
    placements: [
      { id: "control-bar", dock: "bottom", order: 0, isOpen: true },
      { id: "live-rail", dock: "right", order: 0, isOpen: true },
      { id: "caption", dock: "bottom", order: 1, isOpen: true },
      { id: "legend", dock: "bottom", order: 2, isOpen: true },
      { id: "hud", dock: "top", order: 0, isOpen: false },
      { id: "plotter-pareto", dock: "right", order: 1, isOpen: true },
      { id: "plotter-ablation", dock: "right", order: 2, isOpen: true },
      { id: "plotter-variability", dock: "right", order: 3, isOpen: true },
      { id: "cell-drawer", dock: "floating", order: 0, isOpen: false },
      { id: "control-panel", dock: "floating", order: 1, isOpen: false },
      { id: "help-overlay", dock: "floating", order: 2, isOpen: false },
    ],
  },
  drive: {
    id: "drive",
    viewId: "flow",
    placements: [
      { id: "control-bar", dock: "bottom", order: 0, isOpen: true },
      { id: "live-rail", dock: "right", order: 0, isOpen: true },
      { id: "caption", dock: "bottom", order: 1, isOpen: true },
      { id: "legend", dock: "bottom", order: 2, isOpen: true },
      { id: "hud", dock: "top", order: 0, isOpen: false },
      { id: "plotter-pareto", dock: "right", order: 1, isOpen: false },
      { id: "plotter-ablation", dock: "right", order: 2, isOpen: false },
      { id: "plotter-variability", dock: "right", order: 3, isOpen: false },
      { id: "cell-drawer", dock: "floating", order: 0, isOpen: false },
      { id: "control-panel", dock: "floating", order: 1, isOpen: true },
      { id: "help-overlay", dock: "floating", order: 2, isOpen: false },
    ],
  },
  free: {
    id: "free",
    viewId: "space",
    placements: [],
  },
};

/** Default dock preferences for each panel (used when no workspace is loaded). */
export const DEFAULT_DOCK_PREFS: Record<string, DockPreference> = {
  "control-bar": { dock: "bottom", zIndex: 100, defaultOpen: true },
  "live-rail": { dock: "right", zIndex: 90, defaultOpen: true },
  "caption": { dock: "bottom", zIndex: 80, defaultOpen: true },
  "legend": { dock: "bottom", zIndex: 70, defaultOpen: true },
  "hud": { dock: "top", zIndex: 60, defaultOpen: false },
  "plotter-pareto": { dock: "right", zIndex: 50, defaultOpen: true },
  "plotter-ablation": { dock: "right", zIndex: 40, defaultOpen: false },
  "plotter-variability": { dock: "right", zIndex: 30, defaultOpen: false },
  "cell-drawer": { dock: "floating", zIndex: 200, defaultOpen: false },
  "control-panel": { dock: "floating", zIndex: 190, defaultOpen: false },
  "help-overlay": { dock: "floating", zIndex: 1000, defaultOpen: false },
};

/** Storage key and version. */
const STORAGE_KEY = "computronium.layout.v1";
const STORAGE_VERSION = 1;

/** The layout manager — owns docks, coordinates, z-order, and workspaces. */
export class LayoutManager {
  private dockElements = new Map<Dock, HTMLElement>();
  private panelPlacements = new Map<string, PanelPlacement>();
  private currentWorkspace: "watch" | "audit" | "drive" | "free" = "watch";
  private isManualOverride = false;
  private listeners = new Set<() => void>();
  private initialized = false;

  /** Initialize the dock containers in the DOM. */
  async init(): Promise<void> {
    if (this.initialized) return;

    const overlay = document.getElementById("ui-overlay");
    if (!overlay) {
      throw new Error("ui-overlay not found — layout must init after DOM ready");
    }

    // Create dock containers
    for (const dock of ["top", "bottom", "left", "right", "floating"] as Dock[]) {
      const element = document.createElement("div");
      element.id = `dock-${dock}`;
      element.className = `dock dock-${dock}`;
      element.dataset.dock = dock;
      element.style.cssText = this.dockStyles(dock);
      overlay.appendChild(element);
      this.dockElements.set(dock, element);
    }

    // Restore persisted layout or apply default (watch) workspace
    this.restoreOrDefault();

    this.initialized = true;
    console.log("[LayoutManager] Initialized");
  }

  /** CSS styles for each dock type. */
  private dockStyles(dock: Dock): string {
    const base = `
      position: fixed;
      pointer-events: none;
      z-index: 140;
      display: flex;
      flex-direction: column;
      gap: 4px;
    `;
    switch (dock) {
      case "top":
        return `${base}
          top: 0;
          left: 0;
          right: 0;
          padding: 4px;
          align-items: center;
          justify-content: flex-start;
        `;
      case "bottom":
        return `${base}
          bottom: 0;
          left: 0;
          right: 0;
          padding: 4px;
          align-items: center;
          justify-content: flex-end;
        `;
      case "left":
        return `${base}
          top: 0;
          bottom: 0;
          left: 0;
          padding: 4px;
          width: 320px;
          align-items: flex-start;
          justify-content: flex-start;
          overflow-y: auto;
        `;
      case "right":
        return `${base}
          top: 0;
          bottom: 0;
          right: 0;
          padding: 4px;
          width: 520px;
          align-items: flex-end;
          justify-content: flex-start;
          overflow-y: auto;
        `;
      case "floating":
        return `${base}
          inset: 0;
          align-items: flex-start;
          justify-content: flex-start;
          overflow: auto;
        `;
    }
  }

  /** Register a panel's dock preference (called by panel initialization). */
  registerPanel(panelId: string, preference: DockPreference): void {
    const panel = panels.get(panelId);
    if (!panel) return;

    const existing = this.panelPlacements.get(panelId);
    const placement: PanelPlacement = {
      id: panelId,
      dock: preference.dock,
      order: existing?.order ?? 0,
      isOpen: existing?.isOpen ?? preference.defaultOpen ?? false,
    };
    this.panelPlacements.set(panelId, placement);

    // Move the panel element to its dock
    this.movePanelToDock(panelId, preference.dock);

    // Apply open/closed state
    if (placement.isOpen) {
      panel.toggle(); // ensures it's open
    } else {
      // Panel starts closed
    }

    this.notify();
  }

  /** Move a panel element to its assigned dock container. */
  private movePanelToDock(panelId: string, dock: Dock): void {
    const panelEl = document.getElementById(panelId);
    const dockEl = this.dockElements.get(dock);
    if (!panelEl || !dockEl) return;

    // Enable pointer events on the panel (dock has pointer-events: none)
    panelEl.style.pointerEvents = "auto";

    // Remove from current parent
    if (panelEl.parentElement) {
      panelEl.parentElement.removeChild(panelEl);
    }

    // Insert at the correct order position
    const placementsInDock = this.getPlacementsInDock(dock);
    const insertIndex = placementsInDock.findIndex((p) => p.order > this.panelPlacements.get(panelId)!.order);
    const children = Array.from(dockEl.children) as HTMLElement[];
    const refEl = insertIndex >= 0 && insertIndex < children.length ? children[insertIndex] : null;
    dockEl.insertBefore(panelEl, refEl);
  }

  /** Get all placements for a dock, sorted by order. */
  private getPlacementsInDock(dock: Dock): PanelPlacement[] {
    return Array.from(this.panelPlacements.values())
      .filter((p) => p.dock === dock)
      .sort((a, b) => a.order - b.order);
  }

  /** Open or close a panel (called by panel registry toggle). */
  setPanelOpen(panelId: string, open: boolean): void {
    const placement = this.panelPlacements.get(panelId);
    if (!placement) return;

    if (placement.isOpen !== open) {
      placement.isOpen = open;
      this.isManualOverride = true;
      if (this.currentWorkspace !== "free") {
        this.currentWorkspace = "free";
      }
      this.persist();
      this.notify();
    }
  }

  /** Reorder a panel within its dock. */
  setPanelOrder(panelId: string, order: number): void {
    const placement = this.panelPlacements.get(panelId);
    if (!placement) return;
    placement.order = order;
    this.isManualOverride = true;
    if (this.currentWorkspace !== "free") this.currentWorkspace = "free";
    this.movePanelToDock(panelId, placement.dock);
    this.persist();
    this.notify();
  }

  /** Move a panel to a different dock. */
  setPanelDock(panelId: string, dock: Dock): void {
    const placement = this.panelPlacements.get(panelId);
    if (!placement) return;
    if (placement.dock !== dock) {
      placement.dock = dock;
      placement.order = this.getPlacementsInDock(dock).length;
      this.isManualOverride = true;
      if (this.currentWorkspace !== "free") this.currentWorkspace = "free";
      this.movePanelToDock(panelId, dock);
      this.persist();
      this.notify();
    }
  }

  /** Apply a workspace arrangement. */
  applyWorkspace(workspaceId: "watch" | "audit" | "drive" | "free"): void {
    const workspace = WORKSPACES[workspaceId];
    if (!workspace) return;

    this.currentWorkspace = workspaceId;
    this.isManualOverride = false;

    // Switch the stage view
    viewSwitcher.show(workspace.viewId);

    // Apply panel placements
    for (const placement of workspace.placements) {
      const panel = panels.get(placement.id);
      if (!panel) continue;

      // Update placement
      const existing = this.panelPlacements.get(placement.id);
      const updatedPlacement: PanelPlacement = {
        id: placement.id,
        dock: placement.dock,
        order: placement.order,
        isOpen: placement.isOpen,
      };
      this.panelPlacements.set(placement.id, updatedPlacement);

      // Move to dock
      this.movePanelToDock(placement.id, placement.dock);

      // Apply open/closed state
      const isOpen = panel.isOpen();
      if (isOpen !== placement.isOpen) {
        panel.toggle();
      }
    }

    // Close any panels not in the workspace (except floating utility panels)
    for (const [id, panel] of panels.list().map((p) => [p.id, p] as const)) {
      if (!workspace.placements.some((p) => p.id === id)) {
        if (panel.isOpen() && !["cell-drawer", "help-overlay"].includes(id)) {
          panel.toggle();
        }
      }
    }

    this.persist();
    this.notify();
  }

  /** Reset to the watch workspace (called by tour before shot sets). */
  reset(): void {
    this.applyWorkspace("watch");
    // Clear persistence so fresh load gets watch
    this.clearPersisted();
  }

  /** Get the current workspace id. */
  getCurrentWorkspace(): "watch" | "audit" | "drive" | "free" {
    return this.currentWorkspace;
  }

  /** Whether the current arrangement is a manual override (free workspace). */
  isFree(): boolean {
    return this.currentWorkspace === "free" || this.isManualOverride;
  }

  /** Get all panel placements. */
  getPlacements(): PanelPlacement[] {
    return Array.from(this.panelPlacements.values());
  }

  /** Get placement for a specific panel. */
  getPlacement(panelId: string): PanelPlacement | undefined {
    return this.panelPlacements.get(panelId);
  }

  /** Subscribe to layout changes. */
  onChange(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify(): void {
    for (const listener of this.listeners) listener();
  }

  /** Persist current layout to localStorage. */
  persist(): void {
    try {
      const data: WorkspaceData = {
        id: this.currentWorkspace,
        viewId: viewSwitcher.activeId ?? "space",
        placements: this.getPlacements(),
        updatedAt: Date.now(),
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch {
      // Storage unavailable (private browsing, etc.) — ignore
    }
  }

  /** Restore layout from localStorage, or apply default watch workspace. */
  private restoreOrDefault(): void {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const data = JSON.parse(stored) as WorkspaceData;
        // Verify version (future-proofing)
        if (data.placements && Array.isArray(data.placements)) {
          this.applyWorkspace(data.id);
          return;
        }
      }
    } catch {
      // Corrupted or missing — fall through to default
    }
    // Default: watch workspace
    this.applyWorkspace("watch");
  }

  /** Clear persisted layout (called on version bump or reset). */
  clearPersisted(): void {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      // Ignore
    }
  }

  /** Build the workspace switcher UI (segmented control). */
  buildWorkspaceSwitcher(): HTMLElement {
    const container = document.createElement("div");
    container.className = "workspace-switcher";
    container.style.cssText = `
      display: flex;
      gap: 2px;
      background: var(--bg-tertiary);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 2px;
    `;

    const workspaceInfos: Array<{ id: "watch" | "audit" | "drive"; label: string; title: string }> = [
      { id: "watch", label: "▦", title: "Watch — campaigns in real time" },
      { id: "audit", label: "▣", title: "Audit — evidence and judgement" },
      { id: "drive", label: "▸", title: "Drive — the instrument" },
    ];

    for (const info of workspaceInfos) {
      const button = document.createElement("button");
      button.textContent = info.label;
      button.title = info.title;
      button.dataset.workspace = info.id;
      button.style.cssText = `
        flex: 1;
        min-width: 0;
        padding: 4px 8px;
        background: transparent;
        border: none;
        border-radius: 4px;
        color: var(--text-secondary);
        font-size: 12px;
        cursor: pointer;
        transition: all var(--motion-fast) var(--ease-out);
        white-space: nowrap;
      `;
      if (this.currentWorkspace === info.id) {
        button.style.background = "var(--bg-primary)";
        button.style.color = "var(--text-primary)";
        button.style.border = "1px solid var(--border-bright)";
      }
      button.addEventListener("click", () => {
        this.applyWorkspace(info.id);
        this.refreshSwitcher(container);
      });
      container.appendChild(button);
    }

    // Add reset button
    const resetBtn = document.createElement("button");
    resetBtn.textContent = "↺";
    resetBtn.title = "Reset to Watch workspace";
    resetBtn.style.cssText = `
      width: 24px;
      height: 24px;
      background: transparent;
      border: none;
      border-radius: 4px;
      color: var(--text-muted);
      font-size: 12px;
      cursor: pointer;
      transition: all var(--motion-fast) var(--ease-out);
    `;
    resetBtn.addEventListener("click", () => this.reset());
    resetBtn.addEventListener("mouseenter", () => (resetBtn.style.color = "var(--text-primary)"));
    resetBtn.addEventListener("mouseleave", () => (resetBtn.style.color = "var(--text-muted)"));
    container.appendChild(resetBtn);

    return container;
  }

  /** Refresh the switcher buttons' active state. */
  refreshSwitcher(container: HTMLElement): void {
    for (const button of container.querySelectorAll<HTMLButtonElement>("button[data-workspace]")) {
      const ws = button.dataset.workspace as "watch" | "audit" | "drive";
      const isActive = this.currentWorkspace === ws;
      button.style.background = isActive ? "var(--bg-primary)" : "transparent";
      button.style.color = isActive ? "var(--text-primary)" : "var(--text-secondary)";
      button.style.border = isActive ? "1px solid var(--border-bright)" : "none";
    }
  }
}

/** The single layout manager instance. */
export const layout = new LayoutManager();

/** Register a panel with the layout manager (convenience for panel modules). */
export function registerPanelLayout(panelId: string, preference?: Partial<DockPreference>): void {
  const defaultPref = DEFAULT_DOCK_PREFS[panelId] ?? { dock: "floating" };
  layout.registerPanel(panelId, { ...defaultPref, ...preference });
}

/** Get the layout manager (for palette, tour, etc.). */
export function getLayout(): LayoutManager {
  return layout;
}