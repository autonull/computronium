/** The keys the dashboard has already given away (TODO69).

    The panels, the charts and the stage's views all answer to the keyboard,
    so the keys they hold are one list: a view that claimed a key another
    panel already held would steal it, and the reader would find that the
    caption no longer toggles.
*/

/** The panels that can be hidden, and the key that hides each. */
export const PANEL_KEYS = {
  hud: "h",
  rail: "r",
  caption: "c",
} as const;

/** The charts, and the key that shows each. */
export const TAB_KEYS = {
  pareto: "p",
  ablation: "a",
  variability: "s",
} as const;

/** The key that cycles the stage's views. */
export const CYCLE_KEY = "v";

/** Every key that belongs to something else. */
export const RESERVED_KEYS: ReadonlySet<string> = new Set([
  ...Object.values(PANEL_KEYS),
  ...Object.values(TAB_KEYS),
  CYCLE_KEY,
]);
