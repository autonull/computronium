/** The keys the dashboard has already given away (TODO69, TODO70).

    The panels, the charts and the stage's views all answer to the keyboard,
    so the keys they hold are one list: a view that claimed a key another
    panel already held would steal it, and the reader would find that the
    caption no longer toggles.

    TODO69 left four letters free. TODO70's controls took all four, and took
    the spacebar for play/pause besides. The next view takes a punctuation
    key from the list below — the letters are gone.

    The authoritative source is now src/bindings.ts. This module derives its
    exported objects from the binding table so there is one list and no drift.
*/

import {
  panelKeys as _panelKeys,
  tabKeys as _tabKeys,
  controlKeys as _controlKeys,
  cycleKey as _cycleKey,
  claimedKeys as _claimedKeys,
} from "./bindings.js";

/** The panels that can be hidden, and the key that hides each. */
export const PANEL_KEYS = _panelKeys();

/** The charts, and the key that shows each. */
export const TAB_KEYS = _tabKeys();

/** The control bar's verbs: play and pause, stop, step, and the panel. */
export const CONTROL_KEYS = _controlKeys();

/** The key that cycles the stage's views. */
export const CYCLE_KEY = _cycleKey();

/** The punctuation a new view takes, in the order it is offered.

    The letters ran out at exactly the moment a new surface wanted one, so
    the next view takes a punctuation key — and the list that says which
    lives here, beside the others, rather than in a plan that will be
    forgotten.
*/
export const PUNCTUATION_KEYS: readonly string[] = [",", ".", "/", ";", "'"];

/** Every key that belongs to something else (derived from bindings + views). */
export const RESERVED_KEYS: ReadonlySet<string> = _claimedKeys();

/** The letters no key has taken. */
export const FREE_KEYS: ReadonlySet<string> = new Set(
  "abcdefghijklmnopqrstuvwxyz".split("").filter((key) => !RESERVED_KEYS.has(key)),
);