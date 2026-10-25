/** Dockview layout host — the only file that imports Dockview (TODO72 P2). */

import { createDockview, type DockviewApi, type IDockviewPanel, type IContentRenderer, type AddPanelOptions, type DockviewComponentOptions, type SerializedDockview, type Parameters, type DockviewPanelApi, themeDark } from "dockview-core";

import { getDefinition, resolveState } from "./definitions.js";
import { commands } from "./commands.js";
import { runSelection } from "../run-selection.js";
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
} from "./types.js";

function context(instanceId: string): ComponentContext {
  return {
    instanceId,
    workspace: {
      get selectedRunId() {
        return runSelection.selectedId;
      },
      axes: {},
    },
    metrics: {
      metricsFor: async (runId: string) => {
        const entry = runSelection.runs.find(([id]) => id === runId);
        return entry?.[1] ?? null;
      },
    },
    spaces: { spaceFor: async () => null },
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

      const handle = definition.create(element, {} as JsonValue, context(options.id));

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
      disableFloatingGroups: false,
      floatingGroupBounds: "boundedWithinViewport",
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