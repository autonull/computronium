/** Dockview layout host — the only file that imports Dockview (TODO72 P2). */

import { createDockview, type DockviewApi, type IDockviewPanel, type IContentRenderer, type ITabRenderer, type IWatermarkRenderer, type AddPanelOptions, type DockviewComponentOptions, type SerializedDockview, type Parameters, type DockviewPanelApi, type GroupPanelPartInitParameters, type TabPartInitParameters, type WatermarkRendererInitParameters, themeDark, type DockviewOptions } from "dockview-core";

import { getDefinition, resolveState, listDefinitions, definitionTypes } from "./definitions.js";
import { commands } from "./commands.js";
import { workspaceStore } from "../stores/workspace.js";
import { metricsStore } from "../stores/metrics.js";
import { spaceStore } from "../stores/space.js";
import type {
  ComponentContext,
  ComponentHandle,
  DropLocation,
  JsonValue,
  LayoutDocument,
  LayoutHost,
  LayoutNode,
  LayoutSpec,
  OpenOptions,
  PanelInstanceMeta,
  Rect,
  Size,
  StageViewInstance,
} from "./types.js";

function context(instanceId: string): ComponentContext {
  return {
    instanceId,
    workspace: workspaceStore,
    metrics: metricsStore,
    spaces: spaceStore,
    commands: {
      register: (id, run, title) => commands.register(id, run, title),
      execute: (id) => commands.execute(id),
    },
  };
}

interface InternalInstance {
  panel: IDockviewPanel | null;
  panelApi: DockviewPanelApi | null;
  handle: ComponentHandle<JsonValue>;
  meta: PanelInstanceMeta;
  readyPromise: Promise<void>;
  readyResolve: () => void;
  /** For stage panels, the handle to query measured cells. */
  stageHandle?: {
    getMeasuredCells: () => number;
  };
}

function toRect(instance: InternalInstance): Rect {
  const panel = instance.panel;
  const panelApi = instance.panelApi;
  const element = panel?.api.group.element ?? panelApi?.group.element;
  if (!element) return { x: 0, y: 0, width: 0, height: 0 };
  const rect = element.getBoundingClientRect();
  const container = element.closest(".dv-container") as HTMLElement | null;
  if (container) {
    const containerRect = container.getBoundingClientRect();
    return {
      x: rect.left - containerRect.left,
      y: rect.top - containerRect.top,
      width: rect.width,
      height: rect.height,
    };
  }
  return { x: 0, y: 0, width: rect.width, height: rect.height };
}

function toSize(instance: InternalInstance): Size {
  const panel = instance.panel;
  const panelApi = instance.panelApi;
  const element = panel?.api.group.element ?? panelApi?.group.element;
  if (!element) return { width: 320, height: 240 };
  return { width: element.clientWidth, height: element.clientHeight };
}

function jsonToParams(value: JsonValue): Parameters {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return value as Parameters;
  }
  return {};
}

function paramsToJson(params: Parameters | undefined): JsonValue {
  return (params ?? {}) as unknown as JsonValue;
}

/** Custom tab renderer for stage panels — shows view/run badges. */
class StageTabRenderer implements ITabRenderer {
  readonly element: HTMLElement;
  private panelApi: DockviewPanelApi | null = null;

  constructor() {
    this.element = document.createElement("div");
    this.element.className = "dv-tab dv-stage-tab";
    this.element.setAttribute("role", "tab");
    this.element.setAttribute("aria-selected", "false");
    this.element.style.cssText = `
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      height: 28px;
      min-width: 120px;
      max-width: 280px;
      background: var(--bg-tertiary);
      border: 1px solid var(--border);
      border-bottom: none;
      border-radius: 4px 4px 0 0;
      font-size: 11px;
      color: var(--text-primary);
      white-space: nowrap;
      overflow: hidden;
      outline: none;
    `;
    this.element.addEventListener("focus", () => this.updateFocusStyle(true));
    this.element.addEventListener("blur", () => this.updateFocusStyle(false));
  }

  init(params: TabPartInitParameters): void {
    this.panelApi = params.api;
    this.render(params);
    params.api.onDidTitleChange(() => this.render(params));
    params.api.onDidParametersChange(() => this.render(params));
  }

  private updateFocusStyle(focused: boolean): void {
    if (focused) {
      this.element.style.boxShadow = "0 0 0 2px var(--gradient)";
      this.element.style.zIndex = "2";
    } else {
      this.element.style.boxShadow = "none";
      const group = this.panelApi?.group;
      const isActive = group?.activePanel?.id === this.panelApi?.id;
      this.element.style.zIndex = isActive ? "1" : "0";
    }
  }

  private render(params: TabPartInitParameters): void {
    const title = params.title || "Stage";
    const view = params.params?.view as string | undefined;
    const runId = params.params?.runId as string | undefined;

    this.element.innerHTML = "";

    // Icon
    const icon = document.createElement("span");
    icon.textContent = "⬢";
    icon.style.fontSize = "12px";
    this.element.appendChild(icon);

    // Title
    const titleEl = document.createElement("span");
    titleEl.textContent = title;
    titleEl.style.flex = "1";
    titleEl.style.overflow = "hidden";
    titleEl.style.textOverflow = "ellipsis";
    this.element.appendChild(titleEl);

    // View badge
    if (view) {
      const viewBadge = document.createElement("span");
      viewBadge.textContent = view;
      viewBadge.style.cssText = `
        font-size: 9px;
        padding: 1px 6px;
        background: var(--bg-primary);
        border: 1px solid var(--border);
        border-radius: 3px;
        color: var(--text-secondary);
        font-variant-numeric: tabular-nums;
      `;
      this.element.appendChild(viewBadge);
    }

    // Run badge (shortened)
    if (runId) {
      const runBadge = document.createElement("span");
      const shortId = runId.slice(0, 8);
      runBadge.textContent = shortId;
      runBadge.title = runId;
      runBadge.style.cssText = `
        font-size: 9px;
        padding: 1px 6px;
        background: var(--gradient)22;
        border: 1px solid var(--gradient)66;
        border-radius: 3px;
        color: var(--gradient);
        font-family: monospace;
      `;
      this.element.appendChild(runBadge);
    }

    // Active state styling
    const group = params.api.group;
    const isActive = group?.activePanel?.id === params.api.id;
    this.element.setAttribute("aria-selected", isActive ? "true" : "false");
    if (isActive) {
      this.element.style.background = "var(--bg-primary)";
      this.element.style.borderColor = "var(--border-bright)";
      this.element.style.zIndex = "1";
    } else {
      this.element.style.background = "var(--bg-tertiary)";
      this.element.style.borderColor = "var(--border)";
      this.element.style.zIndex = "0";
    }
  }

  dispose(): void {
    this.element.remove();
  }
}

/** Custom tab renderer for regular panels. */
class DefaultTabRenderer implements ITabRenderer {
  readonly element: HTMLElement;
  private panelApi: DockviewPanelApi | null = null;

  constructor() {
    this.element = document.createElement("div");
    this.element.className = "dv-tab dv-default-tab";
    this.element.setAttribute("role", "tab");
    this.element.setAttribute("aria-selected", "false");
    this.element.style.cssText = `
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      height: 28px;
      min-width: 100px;
      max-width: 240px;
      background: var(--bg-tertiary);
      border: 1px solid var(--border);
      border-bottom: none;
      border-radius: 4px 4px 0 0;
      font-size: 11px;
      color: var(--text-primary);
      white-space: nowrap;
      overflow: hidden;
      outline: none;
    `;
    this.element.addEventListener("focus", () => this.updateFocusStyle(true));
    this.element.addEventListener("blur", () => this.updateFocusStyle(false));
  }

  init(params: TabPartInitParameters): void {
    this.panelApi = params.api;
    this.render(params);
    params.api.onDidTitleChange(() => this.render(params));
  }

  private updateFocusStyle(focused: boolean): void {
    if (focused) {
      this.element.style.boxShadow = "0 0 0 2px var(--gradient)";
      this.element.style.zIndex = "2";
    } else {
      this.element.style.boxShadow = "none";
      const group = this.panelApi?.group;
      const isActive = group?.activePanel?.id === this.panelApi?.id;
      this.element.style.zIndex = isActive ? "1" : "0";
    }
  }

  private render(params: TabPartInitParameters): void {
    const title = params.title || "Panel";

    this.element.innerHTML = "";
    const titleEl = document.createElement("span");
    titleEl.textContent = title;
    titleEl.style.flex = "1";
    titleEl.style.overflow = "hidden";
    titleEl.style.textOverflow = "ellipsis";
    this.element.appendChild(titleEl);

    const group = params.api.group;
    const isActive = group?.activePanel?.id === params.api.id;
    this.element.setAttribute("aria-selected", isActive ? "true" : "false");
    if (isActive) {
      this.element.style.background = "var(--bg-primary)";
      this.element.style.borderColor = "var(--border-bright)";
      this.element.style.zIndex = "1";
    } else {
      this.element.style.background = "var(--bg-tertiary)";
      this.element.style.borderColor = "var(--border)";
      this.element.style.zIndex = "0";
    }
  }

  dispose(): void {
    this.element.remove();
  }
}

/** Custom watermark renderer — empty state component picker. */
class EmptyStatePickerRenderer implements IWatermarkRenderer {
  readonly element: HTMLElement;
  private containerApi: DockviewApi | null = null;

  constructor() {
    this.element = document.createElement("div");
    this.element.className = "dv-watermark dv-empty-picker";
    this.element.style.cssText = `
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      width: 100%;
      background: var(--bg);
      color: var(--text-muted);
      font-size: 13px;
      padding: 24px;
    `;
  }

  init(params: WatermarkRendererInitParameters): void {
    this.containerApi = params.containerApi;
    this.render();
  }

  private render(): void {
    if (!this.containerApi) return;

    const definitions = listDefinitions();
    if (definitions.length === 0) {
      this.element.innerHTML = `
        <div style="text-align: center;">
          <div style="font-size: 48px; margin-bottom: 16px; opacity: 0.3;">📦</div>
          <div>No panel types registered</div>
        </div>
      `;
      return;
    }

    const groups = new Map<string, typeof definitions>();
    for (const def of definitions) {
      const group = def.type === "stage" ? "3D Views" : "Panels";
      if (!groups.has(group)) groups.set(group, []);
      groups.get(group)!.push(def);
    }

    let html = `<div style="text-align: center; width: 100%; max-width: 480px;">`;
    html += `<div style="font-size: 48px; margin-bottom: 8px; opacity: 0.4;">🔧</div>`;
    html += `<h3 style="margin: 0 0 8px; color: var(--text-primary); font-size: 16px; font-weight: 500;">Add a Panel</h3>`;
    html += `<p style="margin: 0 0 16px; font-size: 12px;">Choose a panel type to start building your workspace</p>`;

    for (const [groupName, defs] of groups) {
      html += `<div style="margin-bottom: 16px; text-align: left;">`;
      html += `<div style="font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 8px; font-weight: 600;">${groupName}</div>`;
      html += `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 8px;">`;
      for (const def of defs) {
        const icon = def.icon || "◻";
        html += `
          <button
            data-type="${def.type}"
            style="
              display: flex; flex-direction: column; align-items: center; gap: 6px;
              padding: 12px 8px; background: var(--bg-tertiary); border: 1px solid var(--border);
              border-radius: 6px; color: var(--text-primary); font-size: 11px; cursor: pointer;
              transition: background 0.1s, border-color 0.1s, transform 0.1s;
            "
            onmouseover="this.style.background='var(--bg-primary)'; this.style.borderColor='var(--border-bright)'; this.style.transform='translateY(-1px)'"
            onmouseout="this.style.background='var(--bg-tertiary)'; this.style.borderColor='var(--border)'; this.style.transform='none'"
          >
            <span style="font-size: 20px;">${icon}</span>
            <span style="font-weight: 500;">${def.title}</span>
          </button>
        `;
      }
      html += `</div></div>`;
    }
    html += `</div>`;

    this.element.innerHTML = html;

    // Attach click handlers
    for (const btn of this.element.querySelectorAll<HTMLButtonElement>("button[data-type]")) {
      btn.addEventListener("click", () => {
        const type = btn.dataset.type!;
        this.containerApi?.addPanel({
          id: `${type}-${Date.now()}`,
          component: type,
          title: getDefinition(type)?.title ?? type,
        });
      });
    }
  }

  layout(_width: number, _height: number): void {
    // No-op for watermark
  }

  dispose(): void {
    this.element.remove();
  }
}

/** Map of stage instance IDs to their view instances for measured cells query. */
const stageInstances = new Map<string, StageViewInstance>();

export class DockviewHost implements LayoutHost {
  private api: DockviewApi | null = null;
  private readonly instances = new Map<string, InternalInstance>();
  private readonly listeners = new Set<(doc: LayoutDocument) => void>();
  private sequence = 0;
  private mountPromise: Promise<void> | null = null;
  /** Whether the host has been mounted. */
  mounted = false;
  /** Whether the mount has completed (async operations finished). */
  mountComplete = false;

  /** Register a stage instance's view for measured cells queries. */
  static registerStageInstance(instanceId: string, viewInstance: StageViewInstance): void {
    stageInstances.set(instanceId, viewInstance);
  }

  /** Unregister a stage instance. */
  static unregisterStageInstance(instanceId: string): void {
    stageInstances.delete(instanceId);
  }

  /** Get the number of measured cells for a stage instance. */
  static getMeasuredCells(instanceId?: string): number {
    if (instanceId) {
      const view = stageInstances.get(instanceId);
      return view?.getMeasuredCells?.() ?? 0;
    }
    // Sum all stage instances
    let total = 0;
    for (const view of stageInstances.values()) {
      total += view.getMeasuredCells?.() ?? 0;
    }
    return total;
  }

  /** Returns a promise that resolves when the host is mounted. */
  ready(): Promise<void> {
    if (this.mounted) return Promise.resolve();
    if (this.mountPromise) return this.mountPromise;
    // If called before mount, return a promise that resolves when mount is called
    return new Promise((resolve) => {
      const check = setInterval(() => {
        if (this.mounted) {
          clearInterval(check);
          resolve();
        }
      }, 10);
    });
  }

  async mount(root: HTMLElement): Promise<void> {
    this.mountStarted = true;
    this.mountPromise = this._mount(root);
    try {
      await this.mountPromise;
      this.mountComplete = true;
    } catch (error) {
      this.mountError = error as Error;
      console.error("[DockviewHost] Mount failed:", error);
      throw error;
    }
  }

  /** Whether mount() has been called. */
  mountStarted = false;
  /** Error if mount failed. */
  mountError: Error | null = null;

  private async _mount(root: HTMLElement): Promise<void> {
    let apiRef: DockviewApi | null = null;

    const createComponent = (options: { id: string; name: string }): IContentRenderer => {
      const definition = getDefinition(options.name);
      if (!definition) {
        console.warn(`[dockview-host] unknown component type: ${options.name}`);
        const element = document.createElement("div");
        element.textContent = `Unknown component: ${options.name}`;
        return {
          element,
          init: () => {},
          dispose: () => element.remove(),
        };
      }

      const element = document.createElement("div");
      element.style.cssText = "width:100%;height:100%;overflow:auto;";

      const handle = definition.create(element, jsonToParams((options as any).params) as JsonValue, context(options.id));

      let readyResolve: () => void;
      const readyPromise = new Promise<void>((resolve) => {
        readyResolve = resolve;
      });

      const instance: InternalInstance = {
        panel: null,
        panelApi: null,
        handle,
        meta: {
          id: options.id,
          type: definition.type,
          title: definition.title,
          state: {},
        },
        readyPromise,
        readyResolve: readyResolve!,
      };

      // For stage panels, store a reference to query measured cells
      if (definition.type === "stage") {
        instance.stageHandle = {
          getMeasuredCells: () => {
            // The handle is a ComponentHandle<JsonValue> with update/dispose
            // We need to access the viewInstance from the stage component
            // The stage component doesn't expose it directly, so we'll use a different approach
            return 0; // Placeholder - will be updated by the stage component
          },
        };
      }

      this.instances.set(options.id, instance);

      return {
        element,
        init: (params: { containerApi?: DockviewApi; api: DockviewPanelApi; title: string; params: Parameters | undefined }) => {
          instance.panelApi = params.api;
          instance.meta.title = params.title ?? definition.title;
          instance.meta.state = resolveState(definition, paramsToJson(params.params));

          // Use panelApi for title changes (doesn't require containerApi)
          instance.panelApi.onDidTitleChange((event: { title: string }) => {
            instance.meta.title = event.title;
            this.emit();
          });

          // Try to get the panel for other operations (resize, etc.)
          const containerApi = params.containerApi ?? apiRef;
          if (containerApi) {
            const panel = containerApi.getPanel(options.id) as IDockviewPanel | undefined;
            if (panel) {
              instance.panel = panel;
            }
          }

          instance.readyResolve();
          this.emit();
        },
        dispose: () => {
          handle.dispose();
          element.remove();
          this.instances.delete(options.id);
          this.emit();
        },
      };
    };

    const dockviewOptions: DockviewComponentOptions = {
      theme: themeDark,
      createComponent,
      createTabComponent: (options) => {
        const definition = getDefinition(options.name);
        if (definition?.type === "stage") {
          return new StageTabRenderer();
        }
        return new DefaultTabRenderer();
      },
      createWatermarkComponent: () => new EmptyStatePickerRenderer(),
      disableFloatingGroups: false,
      floatingGroupBounds: "boundedWithinViewport",
      closeEmptyGroups: true,
    };

    this.api = createDockview(root, dockviewOptions);
    apiRef = this.api;

    this.api.onDidLayoutChange(() => this.emit());
    this.mounted = true;
  }

  async open(type: string, state?: JsonValue, opts: OpenOptions = {}): Promise<string> {
    if (!this.api) throw new Error("DockviewHost not mounted");
    const definition = getDefinition(type);
    if (!definition) throw new Error(`unknown component type: ${type}`);

    const id = `${type}-${++this.sequence}`;
    const resolved = resolveState(definition, state);

    const panelOptions: AddPanelOptions<Parameters> = {
      id,
      component: type,
      params: jsonToParams(resolved),
      title: opts.title ?? definition.title,
      initialWidth: opts.size?.width ?? definition.defaultSize?.width,
      initialHeight: opts.size?.height ?? definition.defaultSize?.height,
    };

    if (opts.float) {
      panelOptions.floating = true;
    } else if (opts.location?.kind === "tab") {
      panelOptions.position = {
        referencePanel: opts.location.instanceId,
        direction: "within",
      };
    } else if (opts.location?.kind === "edge") {
      panelOptions.position = {
        direction: opts.location.edge,
      };
    }

    this.api.addPanel(panelOptions);

    // Wait for the panel's init to complete
    const instance = this.instances.get(id);
    if (instance) {
      await instance.readyPromise;
      // For stage panels, also wait for the view instance's init to complete
      if (definition.type === "stage") {
        const handle = instance.handle as ComponentHandle<JsonValue> & { viewInitPromise?: Promise<void> };
        if (handle.viewInitPromise) {
          await handle.viewInitPromise;
        }
      }
    }

    return id;
  }

  async openAt(type: string, location: DropLocation, state?: JsonValue): Promise<string> {
    const opts: OpenOptions = { location };
    if (location.kind === "float" && location.rect) {
      opts.size = { width: location.rect.width, height: location.rect.height };
      opts.float = true;
    }
    return this.open(type, state, opts);
  }

  async duplicate(instanceId: string): Promise<string> {
    if (!this.api) throw new Error("DockviewHost not mounted");
    const instance = this.instances.get(instanceId);
    if (!instance) throw new Error(`unknown instance: ${instanceId}`);
    return this.open(instance.meta.type, instance.meta.state, {
      title: instance.meta.title,
      size: toSize(instance),
    });
  }

  close(instanceId: string): void {
    if (!this.api) return;
    const panel = this.api.getPanel(instanceId);
    if (panel) panel.api.close();
  }

  focus(instanceId: string): void {
    if (!this.api) return;
    const panel = this.api.getPanel(instanceId);
    if (panel) panel.api.setActive?.();
  }

  setState(instanceId: string, state: JsonValue): void {
    if (!this.api) return;
    const instance = this.instances.get(instanceId);
    if (!instance) return;
    instance.meta.state = state;
    instance.panelApi?.updateParameters(jsonToParams(state));
  }

  list(): PanelInstanceMeta[] {
    return [...this.instances.values()].map((i) => i.meta);
  }

  active(): string | null {
    if (!this.api) return null;
    const panel = this.api.activePanel;
    return panel?.id ?? null;
  }

  save(): LayoutDocument {
    if (!this.api) {
      return { version: 1, engine: "dockview", engineVersion: 8, data: {}, instances: [] };
    }
    return {
      version: 1,
      engine: "dockview",
      engineVersion: 8,
      data: this.api.toJSON() as unknown as JsonValue,
      instances: this.list(),
    };
  }

  async load(doc: LayoutDocument): Promise<void> {
    if (!this.api) throw new Error("DockviewHost not mounted");
    if (doc.engine !== "dockview") {
      throw new Error(`dockview host cannot load ${doc.engine} layouts`);
    }
    this.api.fromJSON(doc.data as unknown as SerializedDockview);
  }

  async applySpec(spec: LayoutSpec): Promise<void> {
    if (!this.api) throw new Error("DockviewHost not mounted");
    this.api.closeAllGroups();
    for (const node of spec.nodes) {
      if (node.kind === "panel") {
        await this.open(node.type, node.state, { title: node.title, size: node.size });
      } else if (node.kind === "float") {
        await this.openAt(
          node.panel.kind === "panel" ? node.panel.type : "hud",
          { kind: "float", rect: node.rect },
          node.panel.kind === "panel" ? node.panel.state : undefined,
        );
      }
    }
  }

  onChange(cb: (doc: LayoutDocument) => void): () => void {
    this.listeners.add(cb);
    return () => this.listeners.delete(cb);
  }

  /** Expose API for advanced operations (picker, tab actions, maximize, undo/redo). */
  getApi(): DockviewApi | null {
    return this.api;
  }

  private emit(): void {
    if (this.listeners.size === 0) return;
    const doc = this.save();
    for (const listener of this.listeners) listener(doc);
  }
}

export const dockviewHost = new DockviewHost();