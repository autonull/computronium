/** Three.js Dashboard Main Entry Point (TODO73 P10 — Dockview migration). */

import "dockview/dist/styles/dockview.css";
import "./palette.css";
import "./dashboard.css";
import { router, wsClient } from "./ws-client.js";
import { registry } from "./components/registry.js";
import { helpOverlay } from "./help-overlay.js";
import { initPalette, openPalette } from "./palette.js";
import { applyPreset, reset, applyWorkspace } from "./layout.js";
import { BINDINGS, allBindings, setAction } from "./bindings.js";
import { initHints } from "./hints.js";
import "./menubar.js";
import { dockviewHost, DockviewHost } from "./layout/dockview-host.js";
import { spaceStore } from "./stores/space.js";
import { controlStore } from "./stores/control.js";
import { metricsStore } from "./stores/metrics.js";
import { workspaceStore } from "./stores/workspace.js";
import { commands, registerLayoutCommands } from "./layout/commands.js";
import { listDefinitions } from "./layout/definitions.js";
import "./layout/components/hud.js";
import "./layout/components/caption.js";
import "./layout/components/live-rail.js";
import "./layout/components/control-bar.js";
import "./layout/components/discovery-legend.js";
import "./layout/components/control-panel.js";
import "./layout/components/new-run-panel.js";
import "./layout/components/this-run-panel.js";
import "./layout/components/queue-panel.js";
import "./layout/components/cells-panel.js";
import "./layout/components/exports-panel.js";
import "./layout/components/cell-drawer.js";
import "./layout/components/pareto-chart.js";
import "./layout/components/ablation-chart.js";
import "./layout/components/variability-chart.js";
import "./layout/components/stage.js";
import type { Binding } from "./bindings.js";
import type { LayoutHost } from "./layout/types.js";

// Global error handler
window.addEventListener("error", (event) => {
  console.error("[Global Error]", event.error);
  showError(event.error?.message || "Unknown error");
});

window.addEventListener("unhandledrejection", (event) => {
  console.error("[Unhandled Rejection]", event.reason);
  showError(event.reason?.message || "Unhandled promise rejection");
});

// Loading state - uses .global-loading CSS class
let loadingElement: HTMLElement | null = null;

function showLoading(message = "Initializing dashboard..."): void {
  const overlay = document.getElementById("ui-overlay");
  if (!overlay) return;
  loadingElement = document.createElement("div");
  loadingElement.id = "global-loading";
  loadingElement.className = "global-loading";
  loadingElement.innerHTML = `
    <div class="global-loading-spinner"></div>
    <div class="global-loading-text">${message}</div>
  `;
  overlay.appendChild(loadingElement);
}

function hideLoading(): void {
  loadingElement?.remove();
  loadingElement = null;
}

function showError(message: string): void {
  const overlay = document.getElementById("ui-overlay");
  if (!overlay) return;
  const errorElement = document.createElement("div");
  errorElement.id = "global-error-unique";
  errorElement.className = "global-error";
  errorElement.innerHTML = `
    <span>✗</span>
    <span>${message}</span>
    <button class="global-error-close">&times;</button>
  `;
  errorElement
    .querySelector(".global-error-close")
    ?.addEventListener("click", () => {
      errorElement.remove();
    });
  overlay.appendChild(errorElement);
  setTimeout(() => errorElement?.remove(), 10000);
}

// Initialize WebSocket client (uses shared instance from ws-client.ts)
wsClient.connect();

// Show loading state
showLoading("Connecting to dashboard...");

// Wait for WebSocket connection, then hide loading
wsClient.waitForConnection(15000).then((connected) => {
  if (connected) {
    hideLoading();
  } else {
    showLoading("Connection timeout — retrying...");
    wsClient.onStateChange((state) => {
      if (state === "connected") hideLoading();
    });
  }
});

// Synchronous flag to track DOMContentLoaded handler execution
(window as any).__DASHBOARD_DOMCONTENTLOADED__ = false;
document.addEventListener("DOMContentLoaded", async () => {
  (window as any).__DASHBOARD_DOMCONTENTLOADED__ = true;

  // Initialize all registered components via the registry (menubar, etc.)
  await registry.initAll();

  // Mount the Dockview layout host below the menubar
  const workspace = document.createElement("div");
  workspace.id = "workspace";
  workspace.style.cssText = `
    position: fixed;
    top: var(--menubar-height, 28px);
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 200;
    pointer-events: auto;
  `;
  document.body.appendChild(workspace);
  await dockviewHost.mount(workspace);

  // Register layout commands (panel opens, chart opens, layout verbs)
  registerLayoutCommands();

  // Apply default watch preset via LayoutSpec
  applyPreset("watch");

  // Initialize command palette
  await initPalette();

  // Initialize keyboard hints (Shift to show)
  initHints();

  // Wire binding actions to the command bus
  // Chart commands
  setAction("chart-pareto", () => commands.execute("chart-pareto"));
  setAction("chart-ablation", () => commands.execute("chart-ablation"));
  setAction("chart-variability", () => commands.execute("chart-variability"));

  // Control bar verbs
  setAction("control-play", () => { const cs = (window as any).__DASHBOARD__?.controlStore; cs?.togglePlay?.(); });
  setAction("control-step", () => { const cs = (window as any).__DASHBOARD__?.controlStore; cs?.step?.(); });
  setAction("control-stop", () => { const cs = (window as any).__DASHBOARD__?.controlStore; cs?.stop?.(); });
  setAction("control-panel", () => commands.execute("panel-control-bar"));

  // Panel commands
  setAction("panel-hud", () => commands.execute("panel-hud"));
  setAction("panel-rail", () => commands.execute("panel-rail"));
  setAction("panel-caption", () => commands.execute("panel-caption"));
  setAction("panel-legend", () => commands.execute("panel-legend"));

  setAction("view-cycle", () => commands.execute("view-cycle"));

  // Stage view commands — set view on focused stage panel
  const stageViews = ["space", "ledger", "timeline", "landscape", "basin", "spectrum", "trajectory", "flow", "frontier", "contrast", "convergence", "uncertainty", "effect", "spread", "matrix", "layers", "slices", "small-multiples", "ramp", "terrain", "claim-cost", "plot2d", "multirun", "trained-trajectory", "trained-basin", "trained-landscape", "trained-spectrum"];
  for (const view of stageViews) {
    setAction(`view-${view}`, () => commands.execute(`view-${view}`));
  }

  // Register view commands — target first stage panel (or all if multiple)
  for (const view of stageViews) {
    if (commands.has(`view-${view}`)) continue;
    commands.register(`view-${view}`, () => {
      const api = dockviewHost.getApi();
      if (!api) return;
      // Find first stage panel (not just active panel)
      const panel = api.panels.find((candidate) => candidate.view.contentComponent === "stage");
      if (!panel) return;
      dockviewHost.setState(panel.id, { view });
    }, `View: ${view}`);
  }
  if (!commands.has("view-cycle")) {
    commands.register("view-cycle", () => {
      const api = dockviewHost.getApi();
      if (!api) return;
      const panel = api.panels.find((candidate) => candidate.view.contentComponent === "stage");
      if (!panel) return;
      const views = stageViews;
      const currentView = (panel.api.getParameters()?.view as string) || "space";
      const currentIndex = views.indexOf(currentView);
      const nextView = views[(currentIndex + 1) % views.length];
      dockviewHost.setState(panel.id, { view: nextView });
    }, "Cycle Stage View");
  }

  // Preset workspace commands
  setAction("preset-watch", () => applyPreset("watch"));
  setAction("preset-audit", () => applyPreset("audit"));
  setAction("preset-drive", () => applyPreset("drive"));
  setAction("preset-free", () => applyPreset("free"));

  setAction("cell-replicate", () =>
    window.dispatchEvent(new CustomEvent("cell-action-replicate")),
  );
  setAction("cell-preregister", () =>
    window.dispatchEvent(new CustomEvent("cell-action-preregister")),
  );
  setAction("cell-quest", () =>
    window.dispatchEvent(new CustomEvent("cell-action-quest")),
  );

  setAction("help", () => helpOverlay.toggle());
  setAction("palette", () => openPalette());
  setAction("collapse-all", () => {
    for (const instance of dockviewHost.list()) dockviewHost.close(instance.id);
  });
  setAction("escape", () => helpOverlay.hide());
});

// Keyboard shortcuts: the binding layer is the single source of truth.

const bindingsByKey = new Map<string, Binding>();
const bindingsByChord = new Map<string, Binding>();
for (const binding of BINDINGS) {
  if (binding.key) bindingsByKey.set(binding.key.toLowerCase(), binding);
  if (binding.chord) bindingsByChord.set(binding.chord.toLowerCase(), binding);
}

window.addEventListener("keydown", (event) => {
  // Ignore if modifier keys pressed (except Shift for chords)
  if (event.metaKey || event.ctrlKey || event.altKey) return;

  const target = event.target as HTMLElement | null;
  if (target && ["INPUT", "SELECT", "TEXTAREA"].includes(target.tagName)) {
    return;
  }

  const key = event.key.toLowerCase();

  // Check for shifted chords first (e.g., shift+r)
  if (event.shiftKey) {
    const chord = `shift+${key}`;
    const binding = bindingsByChord.get(chord);
    if (binding) {
      binding.run();
      return;
    }
  }

  // Direct key match
  const binding = bindingsByKey.get(key);
  if (binding) {
    binding.run();
    return;
  }
});

// Expose for debugging
(window as any).__DASHBOARD__ = {
  helpOverlay,
  layoutHost: dockviewHost,
  registry,
  commands,
  definitions: {
    list: () =>
      listDefinitions().map((definition) => ({
        type: definition.type,
        title: definition.title,
        icon: definition.icon,
      })),
    },
  wsClient,
  router,
  bindings: {
    list: () =>
      allBindings().map((b) => ({
        id: b.id,
        label: b.label,
        group: b.group,
        key: b.key,
      })),
  },
  layout: {
    applyPreset,
    reset,
    applyWorkspace,
    presets: ["watch", "audit", "drive", "free"],
  },
  debug: {
    controlStore,
    instances: () => dockviewHost.list(),
    measuredCells: (instanceId?: string) => {
      return DockviewHost.getMeasuredCells(instanceId);
    },
    stage: (instanceId?: string) => {
      const api = dockviewHost.getApi();
      if (!api) return null;
      const panel = instanceId
        ? api.getPanel(instanceId)
        : api.panels.find((candidate) => candidate.view.contentComponent === "stage");
      if (!panel) return null;
      const params = (panel.api.getParameters() ?? {}) as Record<string, unknown>;
      return {
        id: panel.id,
        view: params.view ?? null,
        runId: params.runId ?? null,
        axes: params.axes ?? null,
        ready: DockviewHost.isStageReady(panel.id),
        measured: DockviewHost.getMeasuredCells(panel.id),
        cells: DockviewHost.getStageCells(panel.id),
      };
    },
    setStageView: (view: string, instanceId?: string) => {
      const api = dockviewHost.getApi();
      if (!api) return null;
      const panel = instanceId
        ? api.getPanel(instanceId)
        : api.panels.find((candidate) => candidate.view.contentComponent === "stage");
      if (!panel) return null;
      dockviewHost.setState(panel.id, { view });
      return panel.id;
    },
    getStageDebug: (instanceId: string) => {
      return dockviewHost.getStageDebug(instanceId);
    },
    maximize: (instanceId: string) => {
      const panel = dockviewHost.getApi()?.getPanel(instanceId);
      if (panel) dockviewHost.getApi()?.maximizeGroup(panel);
    },
    metricsStore: () => metricsStore,
    workspaceStore: () => workspaceStore,
    spaceStore: () => spaceStore,
    stageRect: (instanceId?: string) => {
      const api = dockviewHost.getApi();
      if (!api) return null;
      const panel = instanceId ? api.getPanel(instanceId) : api.activePanel;
      if (!panel) return null;
      const contentEl = panel.view.content.element;
      const rect = contentEl.getBoundingClientRect();
      // Find the workspace container for relative positioning
      const workspace = document.getElementById("workspace");
      if (workspace) {
        const wsRect = workspace.getBoundingClientRect();
        return { x: rect.left - wsRect.left, y: rect.top - wsRect.top, width: rect.width, height: rect.height };
      }
      return { x: rect.left, y: rect.top, width: rect.width, height: rect.height };
    },
    stageSurfaces: (instanceId?: string) => {
      const api = dockviewHost.getApi();
      if (!api) return [];
      const panels = instanceId
        ? [api.getPanel(instanceId)].filter(Boolean)
        : api.panels;
      return panels.map((panel: any) => {
        const handle = panel?.api?.contentRenderer?.init?.toString();
        return {
          id: panel.id,
          type: panel.view.contentComponent,
          rect: panel.view.content.element.getBoundingClientRect(),
        };
      });
    },
  },
};

console.log("🚀 Computronium Dashboard initialized");