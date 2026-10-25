/** CommandBus — decoupled command execution (TODO72 P1/P4).

Components register command handlers; UI (menubar, palette, bindings) invokes
commands by ID. No singleton component imports in UI code.
*/

type CommandHandler = (payload: any) => void | Promise<void>;

interface CommandRegistration {
  id: string;
  handler: CommandHandler;
  description?: string;
}

export class CommandBus {
  private commands = new Map<string, CommandRegistration>();

  /** Register a command handler. Returns unregister function. */
  register(id: string, handler: CommandHandler, description?: string): () => void {
    if (this.commands.has(id)) {
      console.warn(`[CommandBus] Command "${id}" already registered, replacing`);
    }
    this.commands.set(id, { id, handler, description });
    return () => this.unregister(id);
  }

  /** Unregister a command. */
  unregister(id: string): void {
    this.commands.delete(id);
  }

  /** Execute a command by ID. Returns true if handler existed. */
  async execute(id: string, payload: any = {}): Promise<boolean> {
    const registration = this.commands.get(id);
    if (!registration) {
      console.warn(`[CommandBus] No handler for command "${id}"`);
      return false;
    }
    try {
      await Promise.resolve(registration.handler(payload));
      return true;
    } catch (error) {
      console.error(`[CommandBus] Command "${id}" failed:`, error);
      return false;
    }
  }

  /** Get all registered command IDs and descriptions. */
  list(): { id: string; description?: string }[] {
    return Array.from(this.commands.values()).map((c) => ({
      id: c.id,
      description: c.description,
    }));
  }

  /** Check if a command is registered. */
  has(id: string): boolean {
    return this.commands.has(id);
  }

  dispose(): void {
    this.commands.clear();
  }
}

export const commandBus = new CommandBus();