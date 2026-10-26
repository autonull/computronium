/** Three.js Dashboard Main Entry Point (TODO72 P5/P7 — StageSurface, Multi-instance). */

import "./palette.css";
import "./dashboard.css";
import { router, wsClient } from "./ws-client.js";
import { registry } from "./components/registry.js";
import { ControlBar } from "./control-bar.js";
import { ControlPanel } from "./control-panel.js";
import { CellDrawer } from "./cell-drawer.js";
import { Plotter } from "./plotter.js";
import { LiveRail } from "./live-rail.js";
import { Caption } from "./caption.js";
import { HUD } from "./hud.js";
import { viewSwitcher } from "./stage/switcher.js";
import { runSelection } from "./run-selection.js";
import { helpOverlay } from "./help-overlay.js";
import { initPalette, openPalette } from "./palette.js";
import { panels, getPanelElement } from "./panels.js";
import { applyPreset, reset, applyWorkspace } from "./layout.js";
import { BINDINGS, allBindings, setAction } from "./bindings.js";
import { initHints } from "./hints.js";
import { menubar } from "./menubar.js";
import { dockviewHost } from "./layout/dockview-host.js";
import { commands, registerLayoutCommands } from "./layout/commands.js";
import { listDefinitions } from "./layout/definitions.js";
import "./layout/components/hud.js";
import "./layout/components/caption.js";
import "./layout/components/live-rail.js";
import "./layout/components/control-bar.js";
import "./layout/components/discovery-legend.js";
import "./layout/components/control-panel.js";
import "./layout/components/cell-drawer.js";
import "./layout/components/pareto-chart.js";
import "./layout/components/ablation-chart.js";
import "./layout/components/variability-chart.js";
import "./layout/components/stage.js";
import type { Binding } from "./bindings.js";
import type { LayoutHost } from "./layout/types.js";

// Legacy component instances kept for keyboard bindings and __DASHBOARD__ debug
const legacyHud = new HUD();
const legacyPlotter = new Plotter();
const legacyLiveRail = new LiveRail();
const legacyCaption = new Caption();
const legacyControlBar = new ControlBar();
const legacyControlPanel = new ControlPanel();
const legacyCellDrawer = new CellDrawer();

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
  errorElement.id = "global-error";
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

// Initialize the registry (which initializes all registered components including
// menubar), then wire up bindings and mount the Dockview host.
// Synchronous flag to track DOMContentLoaded handler execution
(window as any).__DASHBOARD_DOMCONTENTLOADED__ = false;
document.addEventListener("DOMContentLoaded", async () => {
  (window as any).__DASHBOARD_DOMCONTENTLOADED__ = true;
  // Initialize legacy components (needed for bindings and debug)
  await legacyHud.init();
  await legacyPlotter.init();
  await legacyLiveRail.init();
  await legacyCaption.init();
  await legacyControlBar.init();
  await legacyControlPanel.init();
  await legacyCellDrawer.init();

  // Initialize all registered components via the registry (menubar, etc.)
  await registry.initAll();

  // Mount the Dockview layout host below the 28px menubar
  const workspace = document.createElement("div");
  workspace.id = "workspace";
  workspace.style.cssText = `
    position: fixed;
    top: 28px;
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
  setAction("control-play", () => commands.execute("control-play"));
  setAction("control-step", () => commands.execute("control-step"));
  setAction("control-stop", () => commands.execute("control-stop"));
  setAction("control-panel", () => commands.execute("control-panel"));

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

  // Register view commands
  for (const view of stageViews) {
    if (commands.has(`view-${view}`)) continue;
    commands.register(`view-${view}`, () => {
      const api = dockviewHost.getApi();
      if (!api) return;
      const panel = api.activePanel;
      if (!panel) return;
      // Check if it's a stage panel (use type assertion for dockview panel)
      if ((panel as any).component === "stage") {
        dockviewHost.setState(panel.id, { view });
      }
    }, `View: ${view}`);
  }
  if (!commands.has("view-cycle")) {
    commands.register("view-cycle", () => {
      const api = dockviewHost.getApi();
      if (!api) return;
      const panel = api.activePanel;
      if (!panel || (panel as any).component !== "stage") return;
      const views = stageViews;
      const currentView = (panel.api.getParameters()?.view as string) || "space";
      const currentIndex = views.indexOf(currentView);
      const nextView = views[(currentIndex + 1) % views.length];
      dockviewHost.setState(panel.id, { view: nextView });
    }, "Cycle Stage View");
  }

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
    for (const panel of panels.list()) {
      if (panel.isOpen()) panel.toggle();
    }
  });
  setAction("escape", () => {
    if (legacyCellDrawer.hasCellSelected()) legacyCellDrawer.hide();
    else helpOverlay.hide();
  });
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
      if (binding.when === "cell-selected" && !legacyCellDrawer.hasCellSelected())
        return;
      binding.run();
      return;
    }
  }

  // Direct key match
  const binding = bindingsByKey.get(key);
  if (binding) {
    if (binding.when === "cell-selected" && !legacyCellDrawer.hasCellSelected())
      return;
    binding.run();
    return;
  }
});

// Expose for debugging
(window as any).__DASHBOARD__ = {
  // Legacy scene removed — each stage panel owns its own StageSurface
  cellDrawer: legacyCellDrawer,
  plotter: legacyPlotter,
  liveRail: legacyLiveRail,
  caption: legacyCaption,
  hud: legacyHud,
  helpOverlay,
  viewSwitcher,
  controlBar: legacyControlBar,
  controlPanel: legacyControlPanel,
  panels,
  layout: { reset, applyWorkspace },
  layoutHost: dockviewHost,
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
  runSelection,
  bindings: {
    list: () =>
      allBindings().map((b) => ({
        id: b.id,
        label: b.label,
        group: b.group,
        key: b.key,
      })),
  },
  debug: {
    instances: () => dockviewHost.list(),
    measuredCells: (instanceId?: string) => {
      const instances = dockviewHost.list();
      if (instanceId) {
        const inst = instances.find((i) => i.id === instanceId);
        return inst ? 1 : 0;
      }
      return instances.length;
    },
    stageRect: (instanceId?: string) => {
      const api = dockviewHost.getApi();
      if (!api) return null;
      const panel = instanceId ? api.getPanel(instanceId) : api.activePanel;
      if (!panel) return null;
      const rect = panel.api.group.element.getBoundingClientRect();
      const container = panel.api.group.element.closest(".dv-container") as HTMLElement | null;
      if (container) {
        const containerRect = container.getBoundingClientRect();
        return { x: rect.left - containerRect.left, y: rect.top - containerRect.top, width: rect.width, height: rect.height };
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
          type: panel.component,
          rect: panel.api.group.element.getBoundingClientRect(),
        };
      });
    },
  },
};

console.log("🚀 Computronium Dashboard initialized");