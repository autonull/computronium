/** The glyphs the view toolbar wears (TODO70).

    Twenty-four views, twenty-four glyphs: a reader learns the grammar once
    and reads the toolbar without reading the words. The kinds are told
    apart by their marks — solids for the 3D views, marks for the flat ones,
    bars for the process, curves for the dynamics — so the strip says what
    kind of picture a view is before the reader presses it.
*/

/** What kind of picture a view shows. */
export type ViewKind = "solid" | "mark" | "bar" | "curve";

/** One view's glyph, and the kind of picture it shows. */
export interface ViewGlyph {
  glyph: string;
  kind: ViewKind;
}

/** Every view's glyph. A view with no entry here is drawn with a dot. */
export const VIEW_GLYPHS: Record<string, ViewGlyph> = {
  // The 3D views: solids.
  space: { glyph: "▦", kind: "solid" },
  terrain: { glyph: "▲", kind: "solid" },
  frontier: { glyph: "◭", kind: "solid" },
  layers: { glyph: "▤", kind: "solid" },
  multirun: { glyph: "▣", kind: "solid" },

  // The flat views that show marks.
  matrix: { glyph: "▩", kind: "mark" },
  multiples: { glyph: "⊞", kind: "mark" },
  uncertainty: { glyph: "◌", kind: "mark" },
  ledger: { glyph: "☰", kind: "mark" },
  contrast: { glyph: "◐", kind: "mark" },
  basin: { glyph: "◡", kind: "mark" },
  "trained-basin": { glyph: "◠", kind: "mark" },

  // The process views: bars.
  cost: { glyph: "▮", kind: "bar" },
  flow: { glyph: "⇉", kind: "bar" },
  effect: { glyph: "▯", kind: "bar" },
  spread: { glyph: "▬", kind: "bar" },

  // The dynamics views: curves.
  convergence: { glyph: "∿", kind: "curve" },
  timeline: { glyph: "↦", kind: "curve" },
  trajectory: { glyph: "⟿", kind: "curve" },
  spectrum: { glyph: "〜", kind: "curve" },
  landscape: { glyph: "∿", kind: "curve" },
  "trained-trajectory": { glyph: "⟿", kind: "curve" },
  "trained-spectrum": { glyph: "〜", kind: "curve" },
  "trained-landscape": { glyph: "∿", kind: "curve" },
  slices: { glyph: "⁙", kind: "mark" },
};

/** The glyph of a view, and the kind of picture it shows. */
export function viewGlyph(id: string): ViewGlyph {
  return VIEW_GLYPHS[id] ?? { glyph: "•", kind: "mark" };
}
