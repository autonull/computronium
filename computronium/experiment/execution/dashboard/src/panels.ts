/** The panels the dashboard can show, and the rail that says which are open (TODO70).

    Every floating panel registers here: the HUD, the live rail, the caption,
    the three charts, the legend, the cell drawer, the control bar and the
    control panel. One registry means one place answers "what is showing",
    and the rail is that answer drawn as a column of buttons down one edge.

    A panel that registers is toggled on its own: closing the Pareto chart
    must leave the ablation chart alone. The keys keep working — the key
    handler asks the registry rather than remembering a second list — and the
    registry is what the tour asks when it hides a panel for a picture.
*/

import { registry } from "./components/registry.js";
import { layout } from "./layout.js";
import type { Component } from "./components/registry.js";

/** One panel the reader can show, hide and close. */
export interface Panel {
  /** The panel's dom id: what the reader, and the tour, name it by. */
  id: string;
  /** The word on the rail's tooltip. */
  label: string;
  /** The glyph on the rail's button. */
  glyph: string;
  /** The key that toggles this panel, when it has one. */
  key?: string;
  /** Show or hide the panel. */
  toggle(): void;
  /** Whether the panel is showing now. */
  isOpen(): boolean;
}

/** The panels the dashboard knows about, and who is showing them. */
export class PanelRegistry {
  private readonly panels = new Map<string, Panel>();
  private readonly listeners = new Set<() => void>();

  /** Add a panel. A panel already registered under the same id is replaced. */
  register(panel: Panel): void {
    this.panels.set(panel.id, panel);
    this.notify();
  }

  /** The panel with this id, if there is one. */
  get(id: string): Panel | undefined {
    return this.panels.get(id);
  }

  /** Every panel, in the order they registered. */
  list(): Panel[] {
    return [...this.panels.values()];
  }

  /** Show or hide a panel by id. */
  toggle(id: string): void {
    const panel = this.panels.get(id);
    if (!panel) return;
    panel.toggle();
    // Notify layout manager of open/close state change
    layout.setPanelOpen(id, panel.isOpen());
    this.notify();
  }

  /** Whether a panel is showing now. */
  isOpen(id: string): boolean {
    const panel = this.panels.get(id);
    return panel ? panel.isOpen() : false;
  }

  /** The ids of the panels that are showing. */
  openIds(): string[] {
    return this.list()
      .filter((panel) => panel.isOpen())
      .map((panel) => panel.id);
  }

  /** The panel a key toggles, if any. */
  byKey(key: string): Panel | undefined {
    return this.list().find((panel) => panel.key === key);
  }

  /** Be told when a panel opens or closes. */
  onChange(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  private notify(): void {
    for (const listener of this.listeners) listener();
  }
}

/** The one registry every panel belongs to. */
export const panels = new PanelRegistry();

/** The class a hidden panel carries.

    Hiding a panel by clearing its inline ``display`` would flatten a flex
    panel into a stack: the control bar is a row of verbs, and a row of verbs
    that has become a column is a different control. The class hides the
    panel and leaves its own display alone.
*/
export const HIDDEN_CLASS = "panel-hidden";

/** Hide or show a panel element, keeping the display it was built with. */
export function setPanelHidden(
  element: HTMLElement | null,
  hidden: boolean,
): void {
  if (!element) return;
  element.classList.toggle(HIDDEN_CLASS, hidden);
}

/** The small × every closable panel carries.

    A panel the reader cannot close is a panel the reader is stuck with. The
    button is returned rather than appended: each panel knows where its own
    header is, and a button dropped in the wrong place covers content.
*/
export function closeButton(onClose: () => void): HTMLButtonElement {
  const button = document.createElement("button");
  button.className = "panel-close";
  button.setAttribute("aria-label", "close");
  button.textContent = "×";
  button.style.cssText = `
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 16px;
    line-height: 1;
    cursor: pointer;
    padding: 2px 4px;
    flex: 0 0 auto;
    pointer-events: auto;
  `;
  button.addEventListener("click", (event) => {
    event.stopPropagation();
    onClose();
  });
  return button;
}

/** The rail: a column of mini buttons down the right edge.

    The honest home for "toggleable individually": a reader sees the set of
    panels, not a list of keys. A lit button is a panel that is showing.
*/
export class PanelRail implements Component {
  name = "PanelRail";

  private container: HTMLElement | null = null;
  private buttons = new Map<string, HTMLButtonElement>();
  private unsubscribe: (() => void) | null = null;

  async init(): Promise<void> {
    const overlay = document.getElementById("ui-overlay");
    if (!overlay) return;

    this.container = document.createElement("div");
    this.container.id = "panel-rail";
    this.container.style.cssText = `
      position: fixed;
      top: 50%;
      right: 0;
      transform: translateY(-50%);
      display: flex;
      flex-direction: column;
      gap: 4px;
      padding: 6px 4px;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-right: none;
      border-radius: 8px 0 0 8px;
      z-index: 170;
      box-shadow: -4px 0 16px rgba(0, 0, 0, 0.4);
    `;
    overlay.appendChild(this.container);

    this.build();
    this.unsubscribe = panels.onChange(() => this.refresh());
  }

  async destroy(): Promise<void> {
    this.unsubscribe?.();
    this.unsubscribe = null;
    this.container?.remove();
    this.container = null;
    this.buttons.clear();
  }

  /** One button per panel, in the order the panels registered. */
  private build(): void {
    if (!this.container) return;
    this.container.innerHTML = "";
    this.buttons.clear();
    for (const panel of panels.list()) {
      const button = document.createElement("button");
      button.className = "panel-rail-button";
      button.textContent = panel.glyph;
      button.title = panel.key
        ? `${panel.label} (${panel.key.toUpperCase()})`
        : panel.label;
      button.style.cssText = `
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 4px;
        color: var(--text-secondary);
        font-size: 12px;
        cursor: pointer;
        padding: 0;
      `;
      button.addEventListener("click", () => panels.toggle(panel.id));
      this.container.appendChild(button);
      this.buttons.set(panel.id, button);
    }
    this.light();
  }

  /** Rebuild when a panel arrives; light the buttons of the ones showing. */
  private refresh(): void {
    if (!this.container) return;
    const ids = panels.list().map((panel) => panel.id);
    const known = [...this.buttons.keys()];
    const changed =
      ids.length !== known.length ||
      ids.some((id, index) => id !== known[index]);
    if (changed) {
      this.build();
      return;
    }
    this.light();
  }

  /** Light the buttons of the panels that are showing. */
  private light(): void {
    for (const panel of panels.list()) {
      const button = this.buttons.get(panel.id);
      if (!button) continue;
      const open = panel.isOpen();
      button.style.color = open ? "var(--text-primary)" : "var(--text-muted)";
      button.style.borderColor = open
        ? "var(--border-bright)"
        : "var(--border)";
      button.style.background = open
        ? "var(--bg-primary)"
        : "var(--bg-tertiary)";
    }
  }
}

export const panelRail = new PanelRail();
registry.register(panelRail);

/** Register a panel, with the two things the registry needs to know. */
export function registerPanel(
  id: string,
  label: string,
  glyph: string,
  toggle: () => void,
  isOpen: () => boolean,
  key?: string,
): void {
  panels.register({ id, label, glyph, key, toggle, isOpen });
}

/** Get a panel element by its id. */
export function getPanelElement(id: string): HTMLElement | null {
  return document.getElementById(id);
}

/** Register a panel that shows and hides itself by its own display. */
export function registerDisplayPanel(
  id: string,
  label: string,
  glyph: string,
  element: () => HTMLElement | null,
  key?: string,
): void {
  registerPanel(
    id,
    label,
    glyph,
    () => {
      const panel = element();
      if (!panel) return;
      setPanelHidden(panel, !panel.classList.contains(HIDDEN_CLASS));
    },
    () => {
      const panel = element();
      if (!panel) return false;
      return !panel.classList.contains(HIDDEN_CLASS);
    },
    key,
  );
}
