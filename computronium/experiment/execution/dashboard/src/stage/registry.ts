/** The view registry — views self-register; the switcher consumes (TODO71 Phase 4).
 *
 *  A view is its own file + one registry row. The next view is one file plus
 *  its row, and nothing else moves. The switcher's 25-constructor list dies;
 *  the toolbar's six groups are the README's own section names.
 */

import type { StageView } from "./views.js";

/** The registry of all stage views. */
const viewRegistry: StageView[] = [];

/** Register a view. Called by the view's module on import. */
export function registerView(view: StageView): void {
  if (viewRegistry.some((v) => v.id === view.id)) {
    throw new Error(`View with id "${view.id}" already registered`);
  }
  viewRegistry.push(view);
}

/** Get all registered views, in registration order. */
export function getViews(): StageView[] {
  return [...viewRegistry];
}

/** Get a view by id. */
export function getView(id: string): StageView | undefined {
  return viewRegistry.find((v) => v.id === id);
}

/** Get views by group. */
export function getViewsByGroup(group: string): StageView[] {
  return viewRegistry.filter((v) => v.group === group);
}

/** The six README groups, in order. */
export const VIEW_GROUPS: readonly string[] = [
  "the space",
  "the run",
  "the evidence",
  "the process",
  "the judgement",
  "the system",
] as const;

/** Group label for display (matches README section titles). */
export function groupLabel(group: string): string {
  return group;
}