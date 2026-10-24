/** The panel shell — every panel declares what it is; the shell says how it
 *  looks (TODO71 Phase 1).
 *
 *  The DOM ids do not change (the tour's compatibility contract). Static
 *  styling lives in dashboard.css; only genuinely dynamic values — meter
 *  levels, trace points, per-frame colours — touch element.style.
 *
 *  The shell sets the chrome's accessibility once: a panel's title is its
 *  aria-label, its close button carries its own, and focus moves to the
 *  panel's header when it opens.
 */

import { closeButton, panels, setPanelHidden } from "./panels.js";
import { layout } from "./layout.js";

export interface PanelShellOptions {
  /** The panel's dom id: what the reader, and the tour, name it by. */
  id: string;
  /** The word on the rail's tooltip and the panel's header. */
  title: string;
  /** The glyph on the rail's button. */
  glyph: string;
  /** The key that toggles this panel, when it has one. */
  key?: string;
  /** The panel's body, as a template literal. */
  body: string;
  /** Dock preference for Phase 2 layout manager. */
  dock?: "top" | "bottom" | "left" | "right" | "floating";
  /** Whether the panel opens by default. */
  defaultOpen?: boolean;
  /** Extra CSS classes for the panel element. */
  className?: string;
  /** Callback when the panel opens/closes. */
  onToggle?: (open: boolean) => void;
}

/** Create a panel with the shared chrome: header (title + ×), body, and
 *  register it with the panel registry so the rail works unchanged.
 *  Also registers with the layout manager for dock management.
 */
export function createPanelShell(options: PanelShellOptions): HTMLElement {
  const { id, title, glyph, key, body, className = "", dock, defaultOpen = false, onToggle } = options;

  const overlay = document.getElementById("ui-overlay");
  if (!overlay) {
    throw new Error("ui-overlay not found — panels must init after DOM ready");
  }

  const panel = document.createElement("div");
  panel.id = id;
  panel.className = `panel ${className}`.trim();
  panel.dataset.dock = dock ?? "floating";
  panel.setAttribute("role", "dialog");
  panel.setAttribute("aria-label", title);
  panel.setAttribute("aria-modal", "false");

  // The panel's chrome: header with title, key hint, and close button
  panel.innerHTML = `
    <header class="panel-header">
      <span class="panel-title">${title}</span>
      ${key ? `<kbd class="panel-key-hint">${key.toUpperCase()}</kbd>` : `<span class="panel-key-hint"></span>`}
    </header>
    <div class="panel-body">${body}</div>
  `;

  const header = panel.querySelector<HTMLElement>(".panel-header")!;
  const close = closeButton(() => {
    panels.toggle(id);
  });
  close.style.position = "absolute";
  close.style.top = "8px";
  close.style.right = "8px";
  header.appendChild(close);

  overlay.appendChild(panel);

  // Hide by default unless defaultOpen
  setPanelHidden(panel, !defaultOpen);

  // Register with layout manager for dock management
  if (dock) {
    layout.registerPanel(id, { dock, defaultOpen });
  }

  // Wire the registry toggle to also notify shell
  const originalToggle = () => {
    const isOpen = !panel.classList.contains("panel-hidden");
    panels.toggle(id);
  };

  // Listen for registry changes to sync hidden state
  const unsubscribe = panels.onChange(() => {
    const panelObj = panels.get(id);
    if (panelObj) {
      const shouldBeHidden = !panelObj.isOpen();
      const currentlyHidden = panel.classList.contains("panel-hidden");
      if (shouldBeHidden !== currentlyHidden) {
        setPanelHidden(panel, shouldBeHidden);
        // Notify layout manager of open/close state change
        layout.setPanelOpen(id, !shouldBeHidden);
        onToggle?.(!shouldBeHidden);
      }
    }
  });

  // Store unsubscribe for cleanup
  (panel as any).__panelShellUnsubscribe = unsubscribe;

  // Focus management: when panel opens, focus the header
  const observer = new MutationObserver(() => {
    if (!panel.classList.contains("panel-hidden")) {
      header.focus();
    }
  });
  observer.observe(panel, { attributes: true, attributeFilter: ["class"] });
  (panel as any).__panelShellObserver = observer;

  return panel;
}

/** Get the panel element by id (for panels that need to query their internals). */
export function getPanelElement(id: string): HTMLElement | null {
  return document.getElementById(id);
}

/** Remove a panel created by the shell. */
export function destroyPanelShell(panel: HTMLElement): void {
  const unsubscribe = (panel as any).__panelShellUnsubscribe;
  if (unsubscribe) unsubscribe();
  const observer = (panel as any).__panelShellObserver;
  if (observer) observer.disconnect();
  panel.remove();
}