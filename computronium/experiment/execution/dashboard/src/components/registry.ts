/** Component registry for auto-discovery and lifecycle management (TODO68). */

export interface Component {
  /** Initialize the component (called once on startup). */
  init(): Promise<void>;

  /** Clean up the component (called on shutdown). */
  destroy(): Promise<void>;

  /** Optional: unique component name for debugging. */
  name?: string;
}

/**
 * ComponentRegistry - Auto-discovery and lifecycle management.
 * Components are registered via `register()` and auto-initialized.
 */
export class ComponentRegistry {
  private components: Map<string, Component> = new Map();
  private initialized = false;

  /** Register a component. */
  register(component: Component): void {
    const name = component.name || component.constructor.name;
    if (this.components.has(name)) {
      console.warn(
        `[ComponentRegistry] Component "${name}" already registered, replacing`,
      );
    }
    this.components.set(name, component);
    if (this.initialized) {
      component.init().catch(console.error);
    }
  }

  /** Unregister a component. */
  unregister(name: string): void {
    const component = this.components.get(name);
    if (component) {
      component.destroy().catch(console.error);
      this.components.delete(name);
    }
  }

  /** Initialize all registered components. */
  async initAll(): Promise<void> {
    this.initialized = true;
    for (const [name, component] of this.components) {
      try {
        await component.init();
        console.log(`[ComponentRegistry] Initialized: ${name}`);
      } catch (e) {
        console.error(`[ComponentRegistry] Failed to initialize ${name}:`, e);
      }
    }
  }

  /** Destroy all registered components. */
  async destroyAll(): Promise<void> {
    for (const [name, component] of this.components) {
      try {
        await component.destroy();
        console.log(`[ComponentRegistry] Destroyed: ${name}`);
      } catch (e) {
        console.error(`[ComponentRegistry] Failed to destroy ${name}:`, e);
      }
    }
    this.components.clear();
    this.initialized = false;
  }

  /** Get a component by name. */
  get(name: string): Component | undefined {
    return this.components.get(name);
  }

  /** Get all registered component names. */
  list(): string[] {
    return Array.from(this.components.keys());
  }
}

// Global registry instance
export const registry = new ComponentRegistry();

// Auto-initialize on module load (for components that import this)
if (typeof window !== "undefined") {
  // Defer to after DOM ready
  document.addEventListener("DOMContentLoaded", () => {
    registry.initAll().catch(console.error);
  });

  // Cleanup on page unload
  window.addEventListener("beforeunload", () => {
    registry.destroyAll().catch(console.error);
  });
}
