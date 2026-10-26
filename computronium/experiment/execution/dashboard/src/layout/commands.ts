/** Commands are the only verbs the chrome calls (TODO72 P1/P7).
 *
 * Menubars, palettes and key bindings look up a command by id. They never
 * import a panel singleton, and layout verbs go through the host seam.
 */

import { dockviewHost } from "./dockview-host.js";
import type { JsonValue, LayoutHost, LayoutSpec, OpenOptions, PanelInstanceMeta, LayoutDocument } from "./types.js";

export interface Command {
  id: string;
  title: string;
  run: () => void | Promise<void>;
}

export class CommandRegistry {
  private readonly commands = new Map<string, Command>();

  register(
    id: string,
    run: () => void | Promise<void>,
    title = id,
  ): void {
    if (this.commands.has(id)) {
      throw new Error(`duplicate command: ${id}`);
    }
    this.commands.set(id, { id, title, run });
  }

  has(id: string): boolean {
    return this.commands.has(id);
  }

  tryExecute(id: string): boolean {
    if (!this.commands.has(id)) return false;
    this.execute(id);
    return true;
  }

  replace(id: string, run: () => void | Promise<void>, title = id): void {
    this.commands.set(id, { id, title, run });
  }

  execute(id: string): void {
    const command = this.commands.get(id);
    if (!command) throw new Error(`unknown command: ${id}`);
    const result = command.run();
    if (result instanceof Promise) {
      result.catch((error: unknown) => {
        console.error(`[commands] ${id} failed`, error);
      });
    }
  }

  list(): Command[] {
    return [...this.commands.values()];
  }
}

export const commands = new CommandRegistry();

const presets = new Map<string, LayoutSpec>();

export function registerPreset(id: string, spec: LayoutSpec): void {
  presets.set(id, spec);
}

export function getPreset(id: string): LayoutSpec | undefined {
  return presets.get(id);
}

export function listPresets(): string[] {
  return [...presets.keys()];
}

/** Layout verbs bound to the Dockview host. */
export class LayoutCommands {
  constructor(private readonly host: () => LayoutHost | null) {}

  async open(type: string, state?: JsonValue, opts?: OpenOptions): Promise<void> {
    await this.host()?.open(type, state, opts);
  }

  async duplicate(instanceId: string): Promise<void> {
    await this.host()?.duplicate(instanceId);
  }

  close(instanceId: string): void {
    this.host()?.close(instanceId);
  }

  focus(instanceId: string): void {
    this.host()?.focus(instanceId);
  }

  setState(instanceId: string, state: JsonValue): void {
    this.host()?.setState(instanceId, state);
  }

  applyPreset(id: string): boolean {
    const spec = presets.get(id);
    if (!spec) return false;
    this.host()?.applySpec(spec);
    return true;
  }

  /** Save current layout as a LayoutDocument. */
  save(): LayoutDocument | null {
    return this.host()?.save() ?? null;
  }

  /** Load a LayoutDocument. */
  async load(doc: LayoutDocument): Promise<void> {
    await this.host()?.load(doc);
  }

  /** Undo last layout change. */
  undo(): void {
    const api = dockviewHost.getApi();
    api?.undo();
  }

  /** Redo last undone layout change. */
  redo(): void {
    const api = dockviewHost.getApi();
    api?.redo();
  }

  /** Whether undo is available. */
  canUndo(): boolean {
    const api = dockviewHost.getApi();
    return api?.canUndo ?? false;
  }

  /** Whether redo is available. */
  canRedo(): boolean {
    const api = dockviewHost.getApi();
    return api?.canRedo ?? false;
  }
}

/** Singleton layout commands bound to the Dockview host. */
export const layoutCommands = new LayoutCommands(() => dockviewHost);

/** Register all built-in layout commands. */
export function registerLayoutCommands(): void {
  // Panel open commands
  commands.register("panel-hud", () => layoutCommands.open("hud"), "Open HUD");
  commands.register("panel-rail", () => layoutCommands.open("live-rail"), "Open Live Rail");
  commands.register("panel-caption", () => layoutCommands.open("caption"), "Open Caption");
  commands.register("panel-legend", () => layoutCommands.open("discovery-legend"), "Open Discovery Legend");
  commands.register("panel-control-bar", () => layoutCommands.open("control-bar"), "Open Control Bar");
  commands.register("panel-control-panel", () => layoutCommands.open("control-panel"), "Open Control Panel (legacy)");
  commands.register("panel-new-run", () => layoutCommands.open("new-run-panel"), "Open New Run Panel");
  commands.register("panel-this-run", () => layoutCommands.open("this-run-panel"), "Open This Run Panel");
  commands.register("panel-queue", () => layoutCommands.open("queue-panel"), "Open Queue Panel");
  commands.register("panel-cells", () => layoutCommands.open("cells-panel"), "Open Cells Panel");
  commands.register("panel-exports", () => layoutCommands.open("exports-panel"), "Open Exports Panel");
  commands.register("panel-cell-drawer", () => layoutCommands.open("cell-drawer"), "Open Cell Drawer");
  commands.register("panel-pareto-chart", () => layoutCommands.open("pareto-chart"), "Open Pareto Chart");
  commands.register("panel-ablation-chart", () => layoutCommands.open("ablation-chart"), "Open Ablation Chart");
  commands.register("panel-variability-chart", () => layoutCommands.open("variability-chart"), "Open Variability Chart");
  commands.register("panel-stage", () => layoutCommands.open("stage"), "Open Stage");

  // Chart commands with per-instance state (metric, runId, axes)
  commands.register("chart-pareto", () => layoutCommands.open("pareto-chart", { metric: "pareto" }), "Pareto Frontier");
  commands.register("chart-ablation", () => layoutCommands.open("ablation-chart", { metric: "ablation" }), "Ablation Chart");
  commands.register("chart-variability", () => layoutCommands.open("variability-chart", { metric: "variability" }), "Variability Chart");

  // Layout verbs
  commands.register("layout-duplicate", () => {
    const api = dockviewHost.getApi();
    const panel = api?.activePanel;
    if (panel) layoutCommands.duplicate(panel.id);
  }, "Duplicate Active Panel");

  commands.register("layout-close", () => {
    const api = dockviewHost.getApi();
    const panel = api?.activePanel;
    if (panel) layoutCommands.close(panel.id);
  }, "Close Active Panel");

  commands.register("layout-maximize", () => {
    const api = dockviewHost.getApi();
    const panel = api?.activePanel;
    if (panel) api.maximizeGroup(panel);
  }, "Maximize Active Group");

  commands.register("layout-float", () => {
    const api = dockviewHost.getApi();
    const panel = api?.activePanel;
    if (panel) api.addFloatingGroup(panel);
  }, "Float Active Panel");

  commands.register("layout-undo", () => layoutCommands.undo(), "Undo Layout Change");
  commands.register("layout-redo", () => layoutCommands.redo(), "Redo Layout Change");

  commands.register("layout-save", () => {
    const doc = layoutCommands.save();
    if (doc) {
      localStorage.setItem("computronium-dashboard-layout", JSON.stringify(doc));
    }
  }, "Save Layout");

  commands.register("layout-load", () => {
    const saved = localStorage.getItem("computronium-dashboard-layout");
    if (saved) {
      try {
        const doc = JSON.parse(saved);
        layoutCommands.load(doc);
      } catch (e) {
        console.error("[commands] Failed to load layout:", e);
      }
    }
  }, "Load Layout");

  commands.register("layout-reset", () => { layoutCommands.applyPreset("watch"); }, "Reset to Watch Preset");
}
