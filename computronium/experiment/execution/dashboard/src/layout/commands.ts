/** Commands are the only verbs the chrome calls (TODO72 P1).
 *
 * Menubars, palettes and key bindings look up a command by id. They never
 * import a panel singleton, and layout verbs go through the host seam.
 */

import type { JsonValue, LayoutHost, LayoutSpec, OpenOptions } from "./types.js";

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

/** Layout verbs bound to a host that may not be mounted yet. */
export class LayoutCommands {
  constructor(private readonly host: () => LayoutHost | null) {}

  open(type: string, state?: JsonValue, opts?: OpenOptions): string | null {
    return this.host()?.open(type, state, opts) ?? null;
  }

  duplicate(instanceId: string): string | null {
    return this.host()?.duplicate(instanceId) ?? null;
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
}
