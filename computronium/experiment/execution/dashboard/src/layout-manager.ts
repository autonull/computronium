/** Layout Manager — GoldenLayout-based panel system (TODO71 Phase 2).
 *
 *  Replaces the ad-hoc panel positioning with a proper dockable, resizable,
 *  persistable layout. Every panel is a GoldenLayout component; the layout
 *  state is saved to localStorage and restored on load.
 */

import { registry } from "./components/registry.js";
import { panels, type Panel } from "./panels.js";
import type { Component } from "./components/registry.js";
import { GoldenLayout, Config, ContentItem } from "golden-layout";
import "golden-layout/dist/css/goldenlayout-base.css";
import "golden-layout/dist/css/themes/goldenlayout-light-theme.css";

const LAYOUT_STORAGE_KEY = "computronium-dashboard-layout";

interface LayoutConfig {
  content: ContentItem[];
}

const DEFAULT_LAYOUT: ContentItem[] = [
  {
    type: "row",
    content: [
      {
        type: "column",
        width: 25,
        content: [
          { type: "component", componentName: "control-panel", title: "Control Panel", isClosable: true },
          { type: "component", componentName: "discovery-legend", title: "Discovery Legend", isClosable: true },
        ],
      },
      {
        type: "column",
        width: 50,
        content: [
          { type: "component", componentName: "space", title: "Discovery Map", isClosable: false },
        ],
      },
      {
        type: "column",
        width: 25,
        content: [
          { type: "component", componentName: "hud", title: "Mission Control", isClosable: true },
          { type: "component", componentName: "pareto-chart", title: "Pareto", isClosable: true },
          { type: "component", componentName: "ablation-chart", title: "Ablation", isClosable: true },
          { type: "component", componentName: "variability-chart", title: "Variability", isClosable: true },
        ],
      },
    ],
  },
  {
    type: "row",
    height: 30,
    content: [
      { type: "component", componentName: "control-bar", title: "Control Bar", isClosable: true },
      { type: "component", componentName: "caption", title: "Caption", isClosable: true },
      { type: "component", componentName: "live-rail", title: "Live Rail", isClosable: true },
    ],
  },
];

const PANEL_COMPONENTS: Record<string, () => HTMLElement | null> = {};

export function registerLayoutComponent(
  name: string,
  elementFactory: () => HTMLElement | null,
): void {
  PANEL_COMPONENTS[name] = elementFactory;
}

export class LayoutManager implements Component {
  name = "LayoutManager";
  private gl: GoldenLayout | null = null;
  private container: HTMLElement | null = null;
  private initialized = false;

  async init(): Promise<void> {
    this.container = document.createElement("div");
    this.container.id = "layout-container";
    this.container.style.cssText = `
      position: fixed;
      inset: 0;
      z-index: 100;
      pointer-events: auto;
    `;
    document.body.appendChild(this.container);

    const savedLayout = this.loadLayout();
    this.gl = new GoldenLayout(this.container, {
      content: savedLayout,
      settings: {
        showPopoutIcon: false,
        showMaximiseIcon: true,
        showCloseIcon: true,
        constrainDragToContainer: true,
        reorderEnabled: true,
      },
      dimensions: {
        borderWidth: 4,
        minItemHeight: 100,
        minItemWidth: 150,
        headerHeight: 28,
        dragProxyWidth: 300,
        dragProxyHeight: 200,
      },
      labels: {
        tabDropPlaceholder: "Drop tab here",
        tabDragIndicator: "Drag to reorder",
      },
    });

    // Don't register components yet - factories aren't ready
    // registerComponents() will be called from main.ts after component init
    this.setupEventHandlers();
    this.initialized = true;

    console.log("[LayoutManager] Initialized with GoldenLayout");
  }

  registerComponents(): void {
    if (!this.gl) return;

    // Register all known panel components
    for (const [name, factory] of Object.entries(PANEL_COMPONENTS)) {
      this.gl.registerComponent(name, (container: any, _state: unknown) => {
        const element = factory();
        if (element) {
          container.getElement().append(element);
          container.on("destroy", () => {
            element.remove();
          });
        }
      });
    }
  }

  private setupEventHandlers(): void {
    if (!this.gl) return;

    // Save layout on change
    this.gl.on("stateChanged", () => this.saveLayout());

    // Handle component creation
    this.gl.on("itemCreated", (item: any) => {
      if (item.isComponent) {
        const compName = item.config.componentName;
        this.updatePanelVisibility(compName, true);
      }
    });

    // Handle component destruction
    this.gl.on("itemDestroyed", (item: any) => {
      if (item.isComponent) {
        const compName = item.config.componentName;
        this.updatePanelVisibility(compName, false);
      }
    });

    // Handle tab clicks - show the view when its tab is activated
    this.gl.on("tabCreated", (tab: any) => {
      tab.element.on("click", () => {
        const item = tab.contentItem;
        if (item.isComponent) {
          this.activateView(item.config.componentName);
        }
      });
    });
  }

  private updatePanelVisibility(componentName: string, visible: boolean): void {
    const panel = panels.get(componentName);
    if (panel) {
      // The panel registry handles visibility; we just sync state
      if (panel.isOpen() !== visible) {
        panel.toggle();
      }
    }
  }

  private activateView(componentName: string): void {
    // Map layout component names to view switcher IDs
    const viewMap: Record<string, string> = {
      space: "space",
      "pareto-chart": "pareto",
      "ablation-chart": "ablation",
      "variability-chart": "variability",
      flow: "flow",
      ledger: "ledger",
      timeline: "timeline",
      landscape: "landscape",
      terrain: "terrain",
      frontier: "frontier",
      basin: "basin",
      spectrum: "spectrum",
      convergence: "convergence",
      contrast: "contrast",
      effect: "effect",
      layers: "layers",
      slices: "slices",
      spread: "spread",
      uncertainty: "uncertainty",
      "claim-cost": "claim-cost",
      "trained-basin": "trained-basin",
      "trained-landscape": "trained-landscape",
      "trained-spectrum": "trained-spectrum",
      "trained-trajectory": "trained-trajectory",
      trajectory: "trajectory",
      multirun: "multirun",
      "small-multiples": "small-multiples",
      matrix: "matrix",
      ramp: "ramp",
      canvas2d: "canvas2d",
      plot2d: "plot2d",
    };

    const viewId = viewMap[componentName];
    if (viewId) {
      // Import viewSwitcher dynamically to avoid circular dependency
      import("./stage/switcher.js").then(({ viewSwitcher }) => {
        viewSwitcher.show(viewId);
      });
    }
  }

  private saveLayout(): void {
    if (!this.gl) return;
    try {
      const state = this.gl.toConfig();
      localStorage.setItem(LAYOUT_STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      console.warn("[LayoutManager] Failed to save layout:", e);
    }
  }

  private loadLayout(): ContentItem[] {
    try {
      const stored = localStorage.getItem(LAYOUT_STORAGE_KEY);
      if (stored) {
        const config = JSON.parse(stored);
        // Validate it's a valid GoldenLayout config
        if (config && config.content) {
          return config.content;
        }
      }
    } catch (e) {
      console.warn("[LayoutManager] Failed to load layout, using default:", e);
    }
    return DEFAULT_LAYOUT;
  }

  /** Reset to default layout. */
  reset(): void {
    if (!this.gl) return;
    this.gl.loadLayout(DEFAULT_LAYOUT);
    this.saveLayout();
  }

  /** Get current layout config. */
  getConfig(): Config | null {
    return this.gl?.toConfig() ?? null;
  }

  /** Apply a layout config. */
  applyConfig(config: Config): void {
    if (!this.gl) return;
    this.gl.loadLayout(config.content);
    this.saveLayout();
  }

  async destroy(): Promise<void> {
    this.gl?.destroy();
    this.gl = null;
    this.container?.remove();
    this.container = null;
    this.initialized = false;
  }

  /** Get the GoldenLayout instance for advanced usage. */
  getGoldenLayout(): GoldenLayout | null {
    return this.gl;
  }
}

export const layoutManager = new LayoutManager();
registry.register(layoutManager);