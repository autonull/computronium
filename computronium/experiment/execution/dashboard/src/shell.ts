/** Simple panel shell — header with title and close button. */

import { closeButton, panels, setPanelHidden, HIDDEN_CLASS } from "./panels.js";

export interface PanelShellOptions {
  id: string;
  title: string;
  glyph: string;
  key?: string;
  body: string;
  className?: string;
  defaultOpen?: boolean;
  dock?: "top" | "bottom" | "left" | "right" | "floating";
  onToggle?: (open: boolean) => void;
}

const panelElementRegistry = new Map<string, HTMLElement>();

export function createPanelShell(options: PanelShellOptions): HTMLElement {
  const { id, title, glyph, key, body, className = "", defaultOpen = false, onToggle } = options;

  const panel = document.createElement("div");
  panel.id = id;
  panel.className = `panel ${className}`.trim();
  panel.setAttribute("role", "dialog");
  panel.setAttribute("aria-label", title);

  panel.innerHTML = `
    <header class="panel-header">
      <span class="panel-title">${title}</span>
      ${key ? `<kbd class="panel-key-hint">${key.toUpperCase()}</kbd>` : ""}
    </header>
    <div class="panel-body">${body}</div>
  `;

  const header = panel.querySelector<HTMLElement>(".panel-header")!;
  header.appendChild(closeButton(() => panels.toggle(id)));

  // Don't append to overlay - GoldenLayout will handle positioning
  // The panel will be added to the DOM when the layout component is created
  setPanelHidden(panel, !defaultOpen);

  // Register the element so factory functions can find it before GoldenLayout appends it
  panelElementRegistry.set(id, panel);

  const unsubscribe = panels.onChange(() => {
    const p = panels.get(id);
    if (p) {
      const hidden = !p.isOpen();
      if (panel.classList.contains(HIDDEN_CLASS) !== hidden) {
        setPanelHidden(panel, hidden);
        onToggle?.(!hidden);
      }
    }
  });
  (panel as any).__unsub = unsubscribe;

  return panel;
}

export function getPanelElement(id: string): HTMLElement | null {
  return panelElementRegistry.get(id) ?? document.getElementById(id);
}

export function unregisterPanelElement(id: string): void {
  panelElementRegistry.delete(id);
}

export function destroyPanelShell(panel: HTMLElement): void {
  const unsub = (panel as any).__unsub;
  if (unsub) unsub();
  unregisterPanelElement(panel.id);
  panel.remove();
}