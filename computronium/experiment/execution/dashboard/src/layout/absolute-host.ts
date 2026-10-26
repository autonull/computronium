/** A floating fallback host for the P1 instance model.
 *
 * It has no docking and no trees: each instance is an absolutely positioned
 * card. It exists so definitions can be opened twice, resized, reloaded and
 * destroyed before Dockview lands, and it implements the same `LayoutHost`
 * seam the real engine will.
 */

import { commands } from "./commands.js";
import { getDefinition, resolveState } from "./definitions.js";
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
} from "./types.js";

interface Instance {
  meta: PanelInstanceMeta;
  element: HTMLElement;
  handle: ComponentHandle<JsonValue>;
  rect: Rect;
}

const CASCADE = 26;

function context(instanceId: string, host: AbsoluteHost): ComponentContext {
  return {
    instanceId,
    workspace: workspaceStore,
    metrics: metricsStore,
    spaces: spaceStore,
    commands: {
      register: (id, run, title) => commands.register(id, run, title),
      execute: (id) => commands.execute(id),
    },
    setState: (next) => host.setState(instanceId, next),
  };
}

export class AbsoluteHost implements LayoutHost {
  private layer: HTMLElement | null = null;
  private readonly instances = new Map<string, Instance>();
  private readonly listeners = new Set<(doc: LayoutDocument) => void>();
  private sequence = 0;
  private activeId: string | null = null;
  private z = 1;

  async mount(root: HTMLElement): Promise<void> {
    this.layer = document.createElement("div");
    this.layer.id = "absolute-layout-layer";
    this.layer.style.cssText =
      "position:fixed; inset:0; pointer-events:none; z-index:1200;";
    root.appendChild(this.layer);
  }

  async open(type: string, state?: JsonValue, opts: OpenOptions = {}): Promise<string> {
    const definition = getDefinition(type);
    if (!definition) throw new Error(`unknown component type: ${type}`);
    const layer = this.ensureLayer();
    const id = `${type}-${++this.sequence}`;
    const resolved = resolveState(definition, state);
    const size = opts.size ?? definition.defaultSize ?? { width: 320, height: 240 };
    const index = this.instances.size;
    const rect: Rect = {
      x: 24 + (index % 8) * CASCADE,
      y: 24 + (index % 8) * CASCADE,
      width: size.width,
      height: size.height,
    };

    const element = document.createElement("section");
    element.className = "layout-instance";
    element.dataset.instanceId = id;
    element.dataset.component = type;
    element.style.cssText = `
      position:absolute;
      display:flex; flex-direction:column;
      background: var(--bg-secondary);
      border:1px solid var(--border);
      border-radius:6px; overflow:hidden;
      pointer-events:auto;
      box-shadow:0 8px 24px rgb(0 0 0 / 35%);
      left:${rect.x}px; top:${rect.y}px;
      width:${rect.width}px; height:${rect.height}px;
      z-index:${++this.z};
    `;

    const header = document.createElement("header");
    header.className = "layout-instance-header";
    header.style.cssText = `
      display:flex; align-items:center; justify-content:space-between;
      padding:6px 10px; font-size:11px; letter-spacing:.04em;
      text-transform:uppercase; color:var(--text-secondary);
      background:var(--bg-tertiary); border-bottom:1px solid var(--border);
      cursor:grab;
    `;
    const title = document.createElement("span");
    title.textContent = opts.title ?? definition.title;
    const close = document.createElement("button");
    close.className = "panel-close";
    close.setAttribute("aria-label", "close");
    close.textContent = "×";
    close.style.cssText =
      "background:none;border:none;color:inherit;font-size:16px;cursor:pointer;";
    close.addEventListener("click", () => this.close(id));
    header.append(title, close);

    const body = document.createElement("div");
    body.className = "layout-instance-body";
    body.style.cssText =
      "flex:1; min-height:0; overflow:auto; padding:10px; position:relative;";
    element.append(header, body);

    this.makeDraggable(element, header);
    layer.appendChild(element);

    const handle = definition.create(body, resolved, context(id, this));
    this.instances.set(id, {
      meta: {
        id,
        type,
        title: opts.title ?? definition.title,
        state: resolved,
      },
      element,
      handle,
      rect,
    });
    this.focus(id);
    this.emit();
    return id;
  }

  async openAt(type: string, location: DropLocation, state?: JsonValue): Promise<string> {
    const opts: OpenOptions = {};
    if (location.kind === "float" && location.rect) {
      opts.size = {
        width: location.rect.width,
        height: location.rect.height,
      };
    }
    const id = await this.open(type, state, opts);
    if (location.kind === "float" && location.rect) {
      this.place(id, location.rect);
    }
    return id;
  }

  async duplicate(instanceId: string): Promise<string> {
    const source = this.instances.get(instanceId);
    if (!source) throw new Error(`unknown instance: ${instanceId}`);
    return this.open(source.meta.type, source.meta.state, {
      title: source.meta.title,
      size: {
        width: source.rect.width,
        height: source.rect.height,
      },
    });
  }

  close(instanceId: string): void {
    const instance = this.instances.get(instanceId);
    if (!instance) return;
    instance.handle.dispose();
    instance.element.remove();
    this.instances.delete(instanceId);
    if (this.activeId === instanceId) this.activeId = null;
    this.emit();
  }

  focus(instanceId: string): void {
    const instance = this.instances.get(instanceId);
    if (!instance) return;
    instance.element.style.zIndex = String(++this.z);
    this.activeId = instanceId;
  }

  setState(instanceId: string, state: JsonValue): void {
    const instance = this.instances.get(instanceId);
    if (!instance) return;
    instance.meta.state = state;
    instance.handle.update?.(state);
    this.emit();
  }

  list(): PanelInstanceMeta[] {
    return [...this.instances.values()].map((instance) => instance.meta);
  }

  active(): string | null {
    return this.activeId;
  }

  save(): LayoutDocument {
    return {
      version: 1,
      engine: "absolute",
      engineVersion: 1,
      data: {
        instances: [...this.instances.values()].map((instance) => ({
          id: instance.meta.id,
          x: instance.rect.x,
          y: instance.rect.y,
          width: instance.rect.width,
          height: instance.rect.height,
        })),
      },
      instances: this.list(),
    };
  }

  async load(doc: LayoutDocument): Promise<void> {
    if (doc.engine !== "absolute") {
      throw new Error(`absolute host cannot load ${doc.engine} layouts`);
    }
    this.clear();
    const data = doc.data;
    const saved =
      data && !Array.isArray(data) && typeof data === "object"
        ? data["instances"]
        : null;
    const rects = new Map<string, Rect>();
    if (Array.isArray(saved)) {
      for (const row of saved) {
        if (!row || Array.isArray(row) || typeof row !== "object") continue;
        const id = row["id"];
        const x = row["x"];
        const y = row["y"];
        const width = row["width"];
        const height = row["height"];
        if (
          typeof id === "string" &&
          typeof x === "number" &&
          typeof y === "number" &&
          typeof width === "number" &&
          typeof height === "number"
        ) {
          rects.set(id, { x, y, width, height });
        }
      }
    }
    for (const meta of doc.instances) {
      const id = await this.open(meta.type, meta.state, {
        title: meta.title,
        size: rects.get(meta.id)
          ? {
              width: rects.get(meta.id)!.width,
              height: rects.get(meta.id)!.height,
            }
          : undefined,
      });
      const rect = rects.get(meta.id);
      if (rect) this.place(id, rect);
    }
  }

  async applySpec(spec: LayoutSpec): Promise<void> {
    this.clear();
    const layer = this.ensureLayer();
    const rect = layer.getBoundingClientRect();
    await this.applyNodes(spec.nodes, { x: 0, y: 0, width: rect.width, height: rect.height });
  }

  onChange(cb: (doc: LayoutDocument) => void): () => void {
    this.listeners.add(cb);
    return () => this.listeners.delete(cb);
  }

  private async applyNodes(nodes: LayoutNode[], area: Rect): Promise<void> {
    if (nodes.length === 0) return;
    const each = area.height / nodes.length;
    for (let index = 0; index < nodes.length; index++) {
      const node = nodes[index];
      const slot = { ...area, y: area.y + each * index, height: each };
      await this.applyNode(node, slot);
    }
  }

  private async applyNode(node: LayoutNode, area: Rect): Promise<void> {
    switch (node.kind) {
      case "panel": {
        const id = await this.open(node.type, node.state, {
          title: node.title,
          size: { width: area.width, height: area.height },
        });
        this.place(id, area);
        break;
      }
      case "float": {
        const id = await this.open(node.panel.kind === "panel" ? node.panel.type : "hud", undefined, {
          size: { width: node.rect.width, height: node.rect.height },
        });
        this.place(id, node.rect);
        break;
      }
      case "tabs": {
        for (const [index, panel] of node.panels.entries()) {
          await this.applyNode(panel, {
            ...area,
            x: area.x + index * 12,
            y: area.y + index * 12,
          });
        }
        break;
      }
      case "split": {
        const horizontal = node.direction === "row";
        const count = node.children.length;
        const weights = node.sizes ?? node.children.map(() => 1);
        const total = weights.reduce((sum, weight) => sum + weight, 0) || 1;
        let offset = 0;
        for (const [index, child] of node.children.entries()) {
          const span = ((horizontal ? area.width : area.height) * weights[index]) / total;
          const slot = horizontal
            ? { ...area, x: area.x + offset, width: span }
            : { ...area, y: area.y + offset, height: span };
          await this.applyNode(child, slot);
          offset += span;
        }
        break;
      }
    }
  }

  private place(instanceId: string, rect: Rect): void {
    const instance = this.instances.get(instanceId);
    if (!instance) return;
    instance.rect = rect;
    Object.assign(instance.element.style, {
      left: `${rect.x}px`,
      top: `${rect.y}px`,
      width: `${rect.width}px`,
      height: `${rect.height}px`,
    });
    this.emit();
  }

  private makeDraggable(element: HTMLElement, header: HTMLElement): void {
    let startX = 0;
    let startY = 0;
    let originX = 0;
    let originY = 0;
    let dragging = false;

    header.addEventListener("pointerdown", (event) => {
      if ((event.target as HTMLElement).closest("button")) return;
      dragging = true;
      startX = event.clientX;
      startY = event.clientY;
      originX = element.offsetLeft;
      originY = element.offsetTop;
      header.setPointerCapture(event.pointerId);
      this.focus(element.dataset.instanceId ?? "");
    });
    header.addEventListener("pointermove", (event) => {
      if (!dragging) return;
      const rect = {
        x: originX + event.clientX - startX,
        y: Math.max(0, originY + event.clientY - startY),
        width: element.offsetWidth,
        height: element.offsetHeight,
      };
      this.place(element.dataset.instanceId ?? "", rect);
    });
    header.addEventListener("pointerup", () => {
      dragging = false;
    });
  }

  private ensureLayer(): HTMLElement {
    if (!this.layer) {
      void this.mount(document.body);
    }
    return this.layer!;
  }

  private clear(): void {
    for (const id of [...this.instances.keys()]) this.close(id);
    this.activeId = null;
  }

  private emit(): void {
    if (this.listeners.size === 0) return;
    const doc = this.save();
    for (const listener of this.listeners) listener(doc);
  }
}

export const absoluteHost = new AbsoluteHost();
