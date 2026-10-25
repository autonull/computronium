/** StageViewDefinition registry — views self-register; stage panels consume (TODO72 P5/P6). */

import type { StageViewDefinition, StageViewInstance, StageViewContext, StageChange } from "../../layout/types.js";

const viewDefinitions = new Map<string, StageViewDefinition>();

/** Register a stage view definition. Called by the view's module on import. */
export function registerStageView(definition: StageViewDefinition): void {
  if (viewDefinitions.has(definition.view)) {
    throw new Error(`Stage view "${definition.view}" already registered`);
  }
  viewDefinitions.set(definition.view, definition);
}

/** Get a stage view definition by id. */
export function getStageView(view: string): StageViewDefinition | undefined {
  return viewDefinitions.get(view);
}

/** Get all registered stage view definitions. */
export function listStageViews(): StageViewDefinition[] {
  return [...viewDefinitions.values()];
}

/** Create a StageViewInstance for the given view name. */
export function createStageViewInstance(
  view: string,
  context: StageViewContext,
): StageViewInstance | null {
  const definition = getStageView(view);
  if (!definition) return null;
  return definition.create(context);
}

/** Get the default view (first registered, or "space"). */
export function getDefaultStageView(): string {
  return listStageViews()[0]?.view ?? "space";
}