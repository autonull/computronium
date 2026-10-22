/** The keys the dashboard has already given away (TODO69, TODO70).

    The panels, the charts and the stage's views all answer to the keyboard,
    so the keys they hold are one list: a view that claimed a key another
    panel already held would steal it, and the reader would find that the
    caption no longer toggles.

    TODO69 left four letters free. TODO70's controls took all four, and took
    the spacebar for play/pause besides. The next view takes a punctuation
    key from the list below — the letters are gone.
*/

/** The panels that can be hidden, and the key that hides each. */
export const PANEL_KEYS = {
  hud: "h",
  rail: "r",
  caption: "c",
  legend: "q",
} as const;

/** The charts, and the key that shows each. */
export const TAB_KEYS = {
  pareto: "p",
  ablation: "a",
  variability: "s",
} as const;

/** The control bar's verbs: play and pause, stop, step, and the panel. */
export const CONTROL_KEYS = {
  play: " ",
  stop: "x",
  step: "w",
  panel: "z",
} as const;

/** The key that cycles the stage's views. */
export const CYCLE_KEY = "v";

/** The punctuation a new view takes, in the order it is offered.

    The letters ran out at exactly the moment a new surface wanted one, so
    the next view takes a punctuation key — and the list that says which
    lives here, beside the others, rather than in a plan that will be
    forgotten.
*/
export const PUNCTUATION_KEYS: readonly string[] = [",", ".", "/", ";", "'"];

/** Every key that belongs to something else. */
export const RESERVED_KEYS: ReadonlySet<string> = new Set([
  ...Object.values(PANEL_KEYS),
  ...Object.values(TAB_KEYS),
  ...Object.values(CONTROL_KEYS),
  CYCLE_KEY,
]);

/** The letters no key has taken. */
export const FREE_KEYS: ReadonlySet<string> = new Set(
  "abcdefghijklmnopqrstuvwxyz".split("").filter((key) => !RESERVED_KEYS.has(key)),
);
