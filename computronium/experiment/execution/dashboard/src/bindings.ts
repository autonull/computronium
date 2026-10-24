/** The binding layer — the one list of what the reader can do (TODO71 Phase 0).
 *
 *  Every key the reader can press is declared here, as data, in a stated
 *  precedence order. The dispatcher in main.ts walks this table; the rail's
 *  tooltips, the help overlay, and the command palette render it; the
 *  property lock parses it.
 *
 *  keys.ts stays as the budget's ledger — PUNCTUATION_KEYS, FREE_KEYS —
 *  but PANEL_KEYS, TAB_KEYS and CONTROL_KEYS become derived from the table
 *  rather than maintained beside it.
 */

export interface Binding {
  /** Unique id for this binding. */
  id: string;
  /** Human-readable label for the help overlay and palette. */
  label: string;
  /** Logical group for organization (help, palette). */
  group: string;
  /** Single key (e.g., "h", " ", "v"). */
  key?: string;
  /** Chord (e.g., "shift+?") — only for shifted keys. */
  chord?: string;
  /** When this binding is available. "always" | "cell-selected" | "run-active". */
  when?: "always" | "cell-selected" | "run-active";
  /** The action to run. */
  run: () => void;
}

/** Late-bound action functions, set by main.ts after components initialize. */
const actions: Record<string, () => void> = {};

/** Register an action implementation by binding id. */
export function setAction(id: string, fn: () => void): void {
  actions[id] = fn;
}

/** Get an action implementation by binding id. */
export function getAction(id: string): (() => void) | undefined {
  return actions[id];
}

/** All keyboard bindings, in precedence order (first match wins). */
export const BINDINGS: Binding[] = [
  // Chart tabs — numbers first
  { id: "chart-pareto", label: "Pareto frontier", group: "Charts", key: "p", run: () => actions["chart-pareto"]?.() },
  { id: "chart-ablation", label: "Ablation chart", group: "Charts", key: "a", run: () => actions["chart-ablation"]?.() },
  { id: "chart-variability", label: "Variability chart", group: "Charts", key: "s", run: () => actions["chart-variability"]?.() },

  // Control bar verbs
  { id: "control-play", label: "Play / Pause", group: "Run Control", key: " ", run: () => actions["control-play"]?.() },
  { id: "control-step", label: "Step one batch", group: "Run Control", key: "w", run: () => actions["control-step"]?.() },
  { id: "control-stop", label: "Stop run", group: "Run Control", key: "x", run: () => actions["control-stop"]?.() },
  { id: "control-panel", label: "Control panel", group: "Run Control", key: "z", run: () => actions["control-panel"]?.() },

  // Panels
  { id: "panel-hud", label: "Mission Control (HUD)", group: "Panels", key: "h", run: () => actions["panel-hud"]?.() },
  { id: "panel-rail", label: "Live Rail", group: "Panels", key: "r", run: () => actions["panel-rail"]?.() },
  { id: "panel-caption", label: "Caption", group: "Panels", key: "c", run: () => actions["panel-caption"]?.() },
  { id: "panel-legend", label: "Legend", group: "Panels", key: "q", run: () => actions["panel-legend"]?.() },

  // Stage views
  { id: "view-cycle", label: "Cycle stage views", group: "Stage", key: "v", run: () => actions["view-cycle"]?.() },

  // Cell actions (require a selected cell) — chords only, no direct keys
  {
    id: "cell-replicate",
    label: "Replicate (queue remaining seeds)",
    group: "Cell Actions",
    chord: "shift+r",
    when: "cell-selected",
    run: () => actions["cell-replicate"]?.(),
  },
  {
    id: "cell-preregister",
    label: "Preregister (confirm protocol)",
    group: "Cell Actions",
    chord: "shift+p",
    when: "cell-selected",
    run: () => actions["cell-preregister"]?.(),
  },
  {
    id: "cell-quest",
    label: "Adopt as Quest (new run)",
    group: "Cell Actions",
    chord: "shift+q",
    when: "cell-selected",
    run: () => actions["cell-quest"]?.(),
  },

  // General
  { id: "help", label: "Show help", group: "General", chord: "shift+/", run: () => actions["help"]?.() },
  { id: "escape", label: "Close drawer / dismiss", group: "General", key: "escape", run: () => actions["escape"]?.() },
];

/** BINDINGS grouped by group, for the help overlay and palette. */
export function bindingsByGroup(): Map<string, Binding[]> {
  const groups = new Map<string, Binding[]>();
  for (const binding of BINDINGS) {
    const group = binding.group;
    if (!groups.has(group)) groups.set(group, []);
    groups.get(group)!.push(binding);
  }
  return groups;
}

/** BINDINGS as a flat list for the lock test and tour. */
export function allBindings(): Binding[] {
  return BINDINGS;
}

/** Keys claimed by BINDINGS (for keys.ts budget). */
export function claimedKeys(): Set<string> {
  const keys = new Set<string>();
  for (const binding of BINDINGS) {
    if (binding.key) keys.add(binding.key.toLowerCase());
    if (binding.chord) {
      const match = binding.chord.match(/shift\+(.+)/);
      if (match) keys.add(match[1].toLowerCase());
    }
  }
  return keys;
}

/** Derived panel keys for keys.ts compatibility. */
export function panelKeys(): Record<string, string> {
  const result: Record<string, string> = {};
  for (const binding of BINDINGS) {
    if (binding.group === "Panels" && binding.key) {
      const id = binding.id.replace("panel-", "");
      result[id] = binding.key;
    }
  }
  return result;
}

/** Derived chart/tab keys for keys.ts compatibility. */
export function tabKeys(): Record<string, string> {
  const result: Record<string, string> = {};
  for (const binding of BINDINGS) {
    if (binding.group === "Charts" && binding.key) {
      const id = binding.id.replace("chart-", "");
      result[id] = binding.key;
    }
  }
  return result;
}

/** Derived control keys for keys.ts compatibility. */
export function controlKeys(): Record<string, string> {
  const result: Record<string, string> = {};
  for (const binding of BINDINGS) {
    if (binding.group === "Run Control" && binding.key) {
      const id = binding.id.replace("control-", "");
      result[id] = binding.key;
    }
  }
  return result;
}

/** The cycle key. */
export function cycleKey(): string {
  const binding = BINDINGS.find((b) => b.id === "view-cycle");
  return binding?.key ?? "v";
}