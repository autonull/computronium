/** Component registry for auto-discovery and lifecycle management (TODO68). */

export interface Component {
  /** Initialize the component (called once on startup). */
  init(): Promise<void>;

  /** Clean up the component (called on shutdown). */
  destroy(): Promise<void>;

  /** Optional: unique component name for debugging. */
  name?: string;

  /** Optional: dependencies - names of components that must be initialized first. */
  dependencies?: string[];

  /** Optional: health check - returns true if component is healthy. */
  healthCheck?(): Promise<boolean> | boolean;
}

/**
 * ComponentRegistry - Auto-discovery and lifecycle management.
 * Components are registered via `register()` and auto-initialized.
 * Supports dependency ordering and health checks.
 */
export class ComponentRegistry {
  private components: Map<string, Component> = new Map();
  private initialized = false;
  private initOrder: string[] = [];

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

  /** Compute initialization order based on dependencies. */
  private computeInitOrder(): string[] {
    const visited = new Set<string>();
    const visiting = new Set<string>();
    const order: string[] = [];

    const visit = (name: string): void => {
      if (visited.has(name)) return;
      if (visiting.has(name)) {
        console.warn(
          `[ComponentRegistry] Circular dependency detected: ${name}`,
        );
        return;
      }
      visiting.add(name);

      const component = this.components.get(name);
      if (component?.dependencies) {
        for (const dep of component.dependencies) {
          if (this.components.has(dep)) {
            visit(dep);
          }
        }
      }

      visiting.delete(name);
      visited.add(name);
      order.push(name);
    };

    for (const name of this.components.keys()) {
      visit(name);
    }

    return order;
  }

  /** Initialize all registered components in dependency order. */
  async initAll(): Promise<void> {
    if (this.initialized) return;
    this.initOrder = this.computeInitOrder();
    this.initialized = true;

    for (const name of this.initOrder) {
      const component = this.components.get(name);
      if (!component) continue;
      try {
        await component.init();
        console.log(`[ComponentRegistry] Initialized: ${name}`);
      } catch (e) {
        console.error(`[ComponentRegistry] Failed to initialize ${name}:`, e);
      }
    }
  }

  /** Destroy all registered components in reverse initialization order. */
  async destroyAll(): Promise<void> {
    for (const name of [...this.initOrder].reverse()) {
      const component = this.components.get(name);
      if (!component) continue;
      try {
        await component.destroy();
        console.log(`[ComponentRegistry] Destroyed: ${name}`);
      } catch (e) {
        console.error(`[ComponentRegistry] Failed to destroy ${name}:`, e);
      }
    }
    this.components.clear();
    this.initialized = false;
    this.initOrder = [];
  }

  /** Get a component by name. */
  get<T extends Component = Component>(name: string): T | undefined {
    return this.components.get(name) as T | undefined;
  }

  /** Get all registered component names in init order. */
  list(): string[] {
    return this.initOrder.length > 0
      ? this.initOrder
      : Array.from(this.components.keys());
  }

  /** Run health checks on all components. */
  async healthCheck(): Promise<Record<string, boolean>> {
    const results: Record<string, boolean> = {};
    for (const [name, component] of this.components) {
      if (component.healthCheck) {
        try {
          results[name] = await Promise.resolve(component.healthCheck());
        } catch {
          results[name] = false;
        }
      } else {
        results[name] = true;
      }
    }
    return results;
  }

  /** Check if all components are healthy. */
  async isHealthy(): Promise<boolean> {
    const results = await this.healthCheck();
    return Object.values(results).every((v) => v);
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
