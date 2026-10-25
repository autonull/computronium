/** Engine-neutral layout vocabulary (TODO72 P1).
 *
 * Nothing here knows Dockview exists. Presets are written as `LayoutSpec`,
 * saved layouts travel as `LayoutDocument`, and every panel is a
 * `ComponentDefinition` that owns the nodes it creates.
 */

export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue };

export interface Size {
  width: number;
  height: number;
}

export interface Rect {
  x: number;
  y: number;
  width: number;
  height: number;
}

export type DropLocation =
  | { kind: "edge"; edge: "left" | "right" | "top" | "bottom" }
  | { kind: "tab"; instanceId: string }
  | { kind: "float"; rect?: Rect };

export type LayoutNode =
  | {
      kind: "panel";
      type: string;
      state?: JsonValue;
      title?: string;
      size?: Size;
    }
  | { kind: "tabs"; panels: LayoutNode[]; active?: number }
  | {
      kind: "split";
      direction: "row" | "column";
      children: LayoutNode[];
      sizes?: number[];
    }
  | { kind: "float"; panel: LayoutNode; rect: Rect };

export interface LayoutSpec {
  version: 1;
  nodes: LayoutNode[];
}

export interface PanelInstanceMeta {
  id: string;
  type: string;
  title: string;
  state: JsonValue;
}

export interface LayoutDocument {
  version: 1;
  engine: string;
  engineVersion: number;
  data: JsonValue;
  instances: PanelInstanceMeta[];
}

export interface OpenOptions {
  float?: boolean;
  size?: Size;
  title?: string;
  location?: DropLocation;
}

export interface LayoutHost {
  mount(root: HTMLElement): Promise<void>;
  open(type: string, state?: JsonValue, opts?: OpenOptions): Promise<string>;
  openAt(type: string, location: DropLocation, state?: JsonValue): Promise<string>;
  duplicate(instanceId: string): Promise<string>;
  close(instanceId: string): void;
  focus(instanceId: string): void;
  setState(instanceId: string, state: JsonValue): void;
  list(): PanelInstanceMeta[];
  active(): string | null;
  save(): LayoutDocument;
  load(doc: LayoutDocument): Promise<void>;
  applySpec(spec: LayoutSpec): Promise<void>;
  onChange(cb: (doc: LayoutDocument) => void): () => void;
}

export interface WorkspaceStore {
  selectedRunId: string | null;
  axes: Record<string, string>;
}

export interface MetricsStore {
  metricsFor(runId: string): Promise<unknown>;
}

export interface SpaceStore {
  spaceFor(key: string): Promise<unknown>;
}

export interface CommandBus {
  register(id: string, run: () => void | Promise<void>, title?: string): void;
  execute(id: string): void;
}

export interface ComponentContext {
  instanceId: string;
  workspace: WorkspaceStore;
  metrics: MetricsStore;
  spaces: SpaceStore;
  commands: CommandBus;
}

export interface ComponentHandle<S extends JsonValue = JsonValue> {
  element: HTMLElement;
  update?(state: S): void;
  dispose(): void;
}

export interface ComponentDefinition<S extends JsonValue = JsonValue> {
  type: string;
  title: string;
  icon?: string;
  singleton?: boolean;
  defaultState?: S;
  defaultSize?: Size;
  minSize?: Size;
  create(
    host: HTMLElement,
    state: S,
    ctx: ComponentContext,
  ): ComponentHandle<S>;
}

export interface StageCanvas {
  readonly canvas: HTMLCanvasElement;
  clear(): void;
}

export interface StageSurface {
  readonly root: HTMLElement;
  readonly three: {
    scene: unknown;
    camera: unknown;
    renderer: unknown;
    controls: unknown;
  };
  readonly flat: StageCanvas;
  size(): Size;
  resize(): void;
  dispose(): void;
}

export interface StageViewContext {
  surface: StageSurface;
  flat: StageCanvas;
  workspace: WorkspaceStore;
  state: JsonValue;
}

export interface StageChange {
  kind: "data" | "selection" | "view" | "resize";
  runId?: string;
}

export interface StageViewInstance {
  mount(): void;
  resize(size: Size): void;
  refresh(change: StageChange): void;
  ready(): boolean;
  dispose(): void;
}

export interface StageViewDefinition {
  view: string;
  title: string;
  key?: string;
  create(ctx: StageViewContext): StageViewInstance;
}
