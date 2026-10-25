/** The component type registry (TODO72 P1).
 *
 * A definition is a type, not an element. Adding a panel is one definition
 * file plus one row here; every surface that lists components reads this
 * registry instead of importing panel singletons.
 */

import type { ComponentDefinition, JsonValue } from "./types.js";

const definitions = new Map<string, ComponentDefinition<JsonValue>>();

export function registerDefinition<S extends JsonValue>(
  definition: ComponentDefinition<S>,
): ComponentDefinition<S> {
  if (definitions.has(definition.type)) {
    throw new Error(`duplicate component definition: ${definition.type}`);
  }
  definitions.set(
    definition.type,
    definition as unknown as ComponentDefinition<JsonValue>,
  );
  return definition;
}

export function getDefinition(
  type: string,
): ComponentDefinition<JsonValue> | undefined {
  return definitions.get(type);
}

export function hasDefinition(type: string): boolean {
  return definitions.has(type);
}

export function listDefinitions(): ComponentDefinition<JsonValue>[] {
  return [...definitions.values()];
}

export function definitionTypes(): string[] {
  return [...definitions.keys()];
}

export function resolveState(
  definition: ComponentDefinition<JsonValue>,
  state: JsonValue | undefined,
): JsonValue {
  return state ?? definition.defaultState ?? null;
}
