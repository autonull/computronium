/** The command palette — every verb reachable without a memorized letter.
 *
 *  Opens on `:` (shift+;). Fuzzy-matches the binding table, views, panels,
 *  cell verbs, and workspaces. Enter runs; Esc closes. Focus-trapped,
 *  arrow-navigable. A cell verb without a selected cell is disabled with
 *  the reason. The loop's five verbs sit in *the next question* group first.
 *
 *  The empty store names the door: the palette's top entry on an empty store
 *  is *start a run*, pointing at the control panel's New run section.
 */

import { BINDINGS, allBindings, getAction, setAction } from "./bindings.js";
import { panels } from "./panels.js";
import { layout, getLayout } from "./layout.js";
import { viewSwitcher } from "./stage/switcher.js";
import { cellDrawer } from "./cell-drawer.js";
import { controlPanel } from "./control-panel.js";
import { controlBar } from "./control-bar.js";
import { helpOverlay } from "./help-overlay.js";
import { wsClient } from "./ws-client.js";

/** A palette entry — one action the reader can invoke. */
export interface PaletteEntry {
  /** Unique identifier. */
  id: string;
  /** Display label. */
  label: string;
  /** Logical group for sectioning. */
  group: string;
  /** Key or chord hint (e.g., "h", "shift+r", "v"). */
  hint?: string;
  /** Whether this entry is currently available. */
  enabled: boolean;
  /** Reason if disabled (shown as subtitle). */
  disabledReason?: string;
  /** The action to run when selected. */
  run: () => void;
  /** Optional metadata for sorting. */
  sortOrder?: number;
}

/** The palette's group order — the loop first. */
const GROUP_ORDER: readonly string[] = [
  "the next question",
  "workspaces",
  "views",
  "panels",
  "verbs",
  "general",
] as const;

/** The palette instance. */
class CommandPalette {
  private container: HTMLElement | null = null;
  private input: HTMLInputElement | null = null;
  private list: HTMLElement | null = null;
  private entries: PaletteEntry[] = [];
  private filtered: PaletteEntry[] = [];
  private selectedIndex = 0;
  private isOpen = false;
  private previousFocus: HTMLElement | null = null;
  private focusTrapCleanup: (() => void) | null = null;
  private unsubscribeLayout: (() => void) | null = null;
  private unsubscribePanels: (() => void) | null = null;
  private unsubscribeCellDrawer: (() => void) | null = null;

  /** Initialize the palette DOM and key binding. */
  async init(): Promise<void> {
    // Build the palette container (hidden initially)
    this.buildContainer();
    document.body.appendChild(this.container!);

    // Rebuild entries when layout/workspaces/cell selection changes
    this.unsubscribeLayout = getLayout().onChange(() => this.rebuildEntries());
    this.unsubscribePanels = panels.onChange(() => this.rebuildEntries());
    this.unsubscribeCellDrawer = cellDrawer.onChange?.(() => this.rebuildEntries());

    // Initial build
    this.rebuildEntries();

    // Global key binding: shift+; (which is ":")
    document.addEventListener("keydown", this.onGlobalKeyDown);

    console.log("[CommandPalette] Initialized");
  }

  /** Build the palette DOM structure. */
  private buildContainer(): void {
    this.container = document.createElement("div");
    this.container.id = "command-palette";
    this.container.className = "command-palette";
    this.container.setAttribute("role", "dialog");
    this.container.setAttribute("aria-modal", "true");
    this.container.setAttribute("aria-label", "Command palette");
    this.container.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      z-index: 10000;
      display: none;
      align-items: flex-start;
      justify-content: center;
      padding-top: 12vh;
      pointer-events: none;
    `;

    this.container.innerHTML = `
      <div class="palette-backdrop" style="
        position: absolute;
        inset: 0;
        background: rgba(0,0,0,0.6);
        backdrop-filter: blur(4px);
      "></div>
      <div class="palette-window" style="
        position: relative;
        width: min(720px, 90vw);
        max-height: 70vh;
        background: var(--bg-secondary);
        border: 1px solid var(--border-bright);
        border-radius: 12px;
        box-shadow: 0 24px 48px rgba(0,0,0,0.6), 0 0 0 1px var(--border);
        overflow: hidden;
        display: flex;
        flex-direction: column;
        pointer-events: auto;
      ">
        <div class="palette-header" style="
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 16px;
          border-bottom: 1px solid var(--border);
          background: var(--bg-tertiary);
        ">
          <kbd class="palette-trigger-hint" style="
            font-size: 11px;
            padding: 2px 6px;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 4px;
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
          ">⇧;</kbd>
          <input
            class="palette-input"
            type="text"
            placeholder="Type a command…"
            autocomplete="off"
            spellcheck="false"
            style="
              flex: 1;
              background: var(--bg);
              border: 1px solid var(--border);
              border-radius: 6px;
              padding: 8px 12px;
              font-size: 14px;
              color: var(--text-primary);
              font-family: inherit;
              outline: none;
            "
            aria-label="Search commands"
          />
          <kbd class="palette-close-hint" style="
            font-size: 11px;
            padding: 2px 6px;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 4px;
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
          ">Esc</kbd>
        </div>
        <div class="palette-list" style="
          flex: 1;
          overflow-y: auto;
          padding: 8px;
        "></div>
        <div class="palette-footer" style="
          padding: 8px 16px;
          border-top: 1px solid var(--border);
          background: var(--bg-tertiary);
          font-size: 11px;
          color: var(--text-muted);
          display: flex;
          justify-content: space-between;
        ">
          <span class="palette-count"></span>
          <span>↑↓ navigate · ⏎ run · Esc close</span>
        </div>
      </div>
    `;

    this.input = this.container.querySelector(".palette-input");
    this.list = this.container.querySelector(".palette-list");

    this.input!.addEventListener("input", () => this.filter());
    this.input!.addEventListener("keydown", this.onInputKeyDown);
    this.container!.querySelector(".palette-backdrop")!.addEventListener("click", () => this.close());
  }

  /** Rebuild all palette entries from current state. */
  private rebuildEntries(): void {
    const entries: PaletteEntry[] = [];
    let sortOrder = 0;

    // 1. THE NEXT QUESTION — the research loop verbs
    const hasRun = wsClient.isConnected; // proxy for "run exists"
    const hasCellSelected = cellDrawer.hasCellSelected();

    // Start a run — top entry when no run, always available
    entries.push({
      id: "start-run",
      label: hasRun ? "Start a new run" : "Start a run",
      group: "the next question",
      hint: "z",
      enabled: true,
      sortOrder: sortOrder++,
      run: () => {
        this.close();
        controlPanel.showSection("new-run");
        panels.toggle("control-panel");
      },
    });

    // Replicate selected cell
    entries.push({
      id: "replicate-cell",
      label: "Replicate selected cell",
      group: "the next question",
      hint: "⇧R",
      enabled: hasCellSelected,
      disabledReason: hasCellSelected ? undefined : "No cell selected — click a cell on the map",
      sortOrder: sortOrder++,
      run: () => {
        this.close();
        cellDrawer.replicateSelected();
      },
    });

    // Preregister claim
    entries.push({
      id: "preregister-claim",
      label: "Preregister claim",
      group: "the next question",
      hint: "⇧P",
      enabled: hasCellSelected,
      disabledReason: hasCellSelected ? undefined : "No cell selected — click a cell on the map",
      sortOrder: sortOrder++,
      run: () => {
        this.close();
        cellDrawer.preregisterSelected();
      },
    });

    // Adopt as quest
    entries.push({
      id: "adopt-quest",
      label: "Adopt as quest (new run)",
      group: "the next question",
      hint: "⇧Q",
      enabled: hasCellSelected,
      disabledReason: hasCellSelected ? undefined : "No cell selected — click a cell on the map",
      sortOrder: sortOrder++,
      run: () => {
        this.close();
        cellDrawer.adoptQuestSelected();
      },
    });

    // Show queue
    entries.push({
      id: "show-queue",
      label: "Show run queue",
      group: "the next question",
      hint: "z → Queue",
      enabled: true,
      sortOrder: sortOrder++,
      run: () => {
        this.close();
        controlPanel.showSection("queue");
        panels.toggle("control-panel");
      },
    });

    // 2. WORKSPACES
    const currentWorkspace = getLayout().getCurrentWorkspace();
    for (const [id, label, hint] of [
      ["watch", "Watch — campaigns in real time", ""],
      ["audit", "Audit — evidence and judgement", ""],
      ["drive", "Drive — the instrument", ""],
      ["free", "Free — your arrangement", ""],
      ["reset", "Reset to Watch workspace", "↺"],
    ] as const) {
      const isReset = id === "reset";
      const wsMatches = !isReset && currentWorkspace === id;
      entries.push({
        id: `workspace-${id}`,
        label,
        group: "workspaces",
        hint,
        enabled: isReset || !wsMatches,
        disabledReason: wsMatches ? "Already active" : undefined,
        sortOrder: sortOrder++,
        run: () => {
          this.close();
          if (isReset) {
            getLayout().reset();
          } else {
            getLayout().applyWorkspace(id as "watch" | "audit" | "drive" | "free");
          }
        },
      });
    }

    // 3. VIEWS — all stage views from the switcher
    const views = viewSwitcher.getViews();
    for (const view of views) {
      const binding = BINDINGS.find((b) => b.id === `view-${view.id}`);
      entries.push({
        id: `view-${view.id}`,
        label: view.name,
        group: "views",
        hint: binding?.key ?? binding?.chord ?? "",
        enabled: true,
        sortOrder: sortOrder++,
        run: () => {
          this.close();
          viewSwitcher.show(view.id);
        },
      });
    }

    // 4. PANELS
    for (const panel of panels.list()) {
      const binding = BINDINGS.find((b) => b.id === `panel-${panel.id.replace("panel-", "")}`);
      entries.push({
        id: `panel-${panel.id}`,
        label: panel.label,
        group: "panels",
        hint: binding?.key ?? "",
        enabled: true,
        sortOrder: sortOrder++,
        run: () => {
          this.close();
          panels.toggle(panel.id);
        },
      });
    }

    // 5. VERBS (control bar actions)
    for (const binding of BINDINGS) {
      if (binding.group === "Run Control" || binding.group === "General") {
        entries.push({
          id: binding.id,
          label: binding.label,
          group: binding.group === "Run Control" ? "verbs" : "general",
          hint: binding.key ? binding.key === " " ? "Space" : binding.key : (binding.chord ?? ""),
          enabled: binding.when ? this.checkWhen(binding.when) : true,
          disabledReason: binding.when && !this.checkWhen(binding.when) ? this.whenReason(binding.when) : undefined,
          sortOrder: sortOrder++,
          run: () => {
            this.close();
            binding.run();
          },
        });
      }
    }

    // Sort by group order, then sortOrder
    this.entries = entries.sort((a, b) => {
      const ga = GROUP_ORDER.indexOf(a.group);
      const gb = GROUP_ORDER.indexOf(b.group);
      if (ga !== gb) return ga - gb;
      return (a.sortOrder ?? 0) - (b.sortOrder ?? 0);
    });

    // If palette is open, re-filter
    if (this.isOpen) {
      this.filter();
    }
  }

  /** Check a when condition. */
  private checkWhen(when: "always" | "cell-selected" | "run-active"): boolean {
    switch (when) {
      case "always":
        return true;
      case "cell-selected":
        return cellDrawer.hasCellSelected();
      case "run-active":
        return wsClient.isConnected; // approximation
      default:
        return true;
    }
  }

  /** Get disabled reason for a when condition. */
  private whenReason(when: "always" | "cell-selected" | "run-active"): string {
    switch (when) {
      case "always":
        return "";
      case "cell-selected":
        return "No cell selected — click a cell on the map";
      case "run-active":
        return "No active run";
      default:
        return "";
    }
  }

  /** Filter entries by input text (fuzzy match). */
  private filter(): void {
    const query = this.input!.value.toLowerCase().trim();
    if (!query) {
      this.filtered = [...this.entries];
    } else {
      this.filtered = this.entries
        .map((entry) => ({
          entry,
          score: this.fuzzyScore(entry.label.toLowerCase(), query),
        }))
        .filter((r) => r.score > 0)
        .sort((a, b) => b.score - a.score)
        .map((r) => r.entry);
    }
    this.selectedIndex = 0;
    this.render();
  }

  /** Simple fuzzy match score (higher = better). */
  private fuzzyScore(text: string, query: string): number {
    if (text === query) return 1000;
    if (text.startsWith(query)) return 800;
    if (text.includes(query)) return 600;

    // Subsequence match
    let ti = 0;
    let qi = 0;
    let score = 0;
    while (ti < text.length && qi < query.length) {
      if (text[ti] === query[qi]) {
        score += 10;
        qi++;
      }
      ti++;
    }
    if (qi === query.length) return score + 100;
    return 0;
  }

  /** Render the filtered list. */
  private render(): void {
    if (!this.list) return;

    this.list.innerHTML = "";

    if (this.filtered.length === 0) {
      const empty = document.createElement("div");
      empty.className = "palette-empty";
      empty.style.cssText = `
        padding: 24px;
        text-align: center;
        color: var(--text-muted);
        font-size: 13px;
      `;
      empty.textContent = this.input!.value ? "No matches" : "No commands available";
      this.list.appendChild(empty);
      this.updateCount(0);
      return;
    }

    let currentGroup = "";
    for (let i = 0; i < this.filtered.length; i++) {
      const entry = this.filtered[i];

      // Group header
      if (entry.group !== currentGroup) {
        currentGroup = entry.group;
        const header = document.createElement("div");
        header.className = "palette-group-header";
        header.style.cssText = `
          padding: 8px 12px 4px;
          font-size: 10px;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          color: var(--text-muted);
          font-weight: 600;
        `;
        header.textContent = entry.group;
        this.list.appendChild(header);
      }

      const item = document.createElement("div");
      item.className = "palette-item" + (entry.enabled ? "" : " palette-item-disabled") + (i === this.selectedIndex ? " palette-item-selected" : "");
      item.style.cssText = `
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 12px;
        border-radius: 6px;
        cursor: ${entry.enabled ? "pointer" : "not-allowed"};
        transition: background var(--motion-fast);
        ${entry.enabled ? "" : "opacity: 0.5;"}
      `;
      item.dataset.id = entry.id;

      if (i === this.selectedIndex) {
        item.style.background = "var(--gradient)1a";
      }

      item.innerHTML = `
        <span class="palette-item-label" style="flex: 1; min-width: 0; font-size: 13px; color: var(--text-primary);">${this.highlightMatch(entry.label)}</span>
        ${entry.hint ? `<kbd class="palette-item-hint" style="
          font-size: 10px;
          padding: 2px 6px;
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: 4px;
          color: var(--text-secondary);
          font-family: 'JetBrains Mono', monospace;
          white-space: nowrap;
          flex-shrink: 0;
        ">${this.escapeHtml(entry.hint)}</kbd>` : ""}
        ${entry.disabledReason ? `<span class="palette-item-reason" style="
          font-size: 11px;
          color: var(--text-muted);
          flex-shrink: 0;
        ">${this.escapeHtml(entry.disabledReason)}</span>` : ""}
      `;

      if (entry.enabled) {
        item.addEventListener("click", () => {
          this.selectedIndex = i;
          entry.run();
        });
        item.addEventListener("mouseenter", () => (this.selectedIndex = i));
      }

      this.list.appendChild(item);
    }

    // Scroll selected into view
    const selectedEl = this.list.querySelector(".palette-item-selected");
    selectedEl?.scrollIntoView({ block: "nearest" });

    this.updateCount(this.filtered.length);
  }

  /** Highlight matching substring in label. */
  private highlightMatch(label: string): string {
    const query = this.input!.value.toLowerCase().trim();
    if (!query) return this.escapeHtml(label);

    const lower = label.toLowerCase();
    const idx = lower.indexOf(query);
    if (idx === -1) return this.escapeHtml(label);

    const before = label.slice(0, idx);
    const match = label.slice(idx, idx + query.length);
    const after = label.slice(idx + query.length);
    return `${this.escapeHtml(before)}<mark style="background: var(--gradient)33; color: var(--gradient); padding: 0 2px; border-radius: 2px;">${this.escapeHtml(match)}</mark>${this.escapeHtml(after)}`;
  }

  /** Escape HTML. */
  private escapeHtml(text: string): string {
    return text
      .replace(/&/g, "\u0026amp;")
      .replace(/</g, "\u0026lt;")
      .replace(/>/g, "\u0026gt;")
      .replace(/"/g, "\u0026quot;")
      .replace(/'/g, "\u0026#39;");
  }

  /** Update the result count in footer. */
  private updateCount(count: number): void {
    const countEl = this.container!.querySelector(".palette-count");
    if (countEl) {
      countEl.textContent = `${count} command${count === 1 ? "" : "s"}`;
    }
  }

  /** Global keydown: shift+; opens palette. */
  private onGlobalKeyDown = (event: KeyboardEvent): void => {
    // shift+; = ":" (colon)
    if (event.shiftKey && event.key === ";") {
      event.preventDefault();
      this.open();
    }
    // Also allow Escape to close if palette is open (handled by focus trap)
  };

  /** Input keydown: arrows, enter, escape. */
  private onInputKeyDown = (event: KeyboardEvent): void => {
    switch (event.key) {
      case "ArrowDown":
        event.preventDefault();
        this.selectedIndex = Math.min(this.selectedIndex + 1, this.filtered.length - 1);
        this.render();
        break;
      case "ArrowUp":
        event.preventDefault();
        this.selectedIndex = Math.max(this.selectedIndex - 1, 0);
        this.render();
        break;
      case "Enter":
        event.preventDefault();
        const entry = this.filtered[this.selectedIndex];
        if (entry?.enabled) {
          entry.run();
        }
        break;
      case "Escape":
        event.preventDefault();
        this.close();
        break;
      case "Tab":
        // Let focus trap handle it
        break;
    }
  };

  /** Open the palette. */
  open(): void {
    if (this.isOpen) return;

    this.previousFocus = document.activeElement as HTMLElement;
    this.isOpen = true;
    this.container!.style.display = "flex";

    // Rebuild entries for current state
    this.rebuildEntries();
    this.filter();

    // Focus input
    requestAnimationFrame(() => {
      this.input!.focus();
      this.setupFocusTrap();
    });

    // Announce to screen readers
    this.announce("Command palette opened");
  }

  /** Close the palette. */
  close(): void {
    if (!this.isOpen) return;

    this.isOpen = false;
    this.container!.style.display = "none";
    this.input!.value = "";
    this.teardownFocusTrap();

    // Restore focus
    if (this.previousFocus) {
      this.previousFocus.focus();
      this.previousFocus = null;
    }

    this.announce("Command palette closed");
  }

  /** Set up focus trap within palette. */
  private setupFocusTrap(): void {
    const focusableElements = this.container!.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"]), .palette-item:not(.palette-item-disabled)'
    );

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleTab = (event: KeyboardEvent): void => {
      if (event.key !== "Tab") return;

      if (event.shiftKey) {
        if (document.activeElement === firstElement) {
          event.preventDefault();
          lastElement?.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          event.preventDefault();
          firstElement?.focus();
        }
      }
    };

    this.container!.addEventListener("keydown", handleTab);
    this.focusTrapCleanup = () => this.container!.removeEventListener("keydown", handleTab);
  }

  /** Remove focus trap. */
  private teardownFocusTrap(): void {
    this.focusTrapCleanup?.();
    this.focusTrapCleanup = null;
  }

  /** Announce to screen readers. */
  private announce(message: string): void {
    const announcer = document.createElement("div");
    announcer.setAttribute("role", "status");
    announcer.setAttribute("aria-live", "polite");
    announcer.style.cssText = "position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0;";
    announcer.textContent = message;
    document.body.appendChild(announcer);
    setTimeout(() => announcer.remove(), 1000);
  }

  /** Check if palette is open. */
  isOpenState(): boolean {
    return this.isOpen;
  }

  /** Destroy the palette. */
  destroy(): void {
    document.removeEventListener("keydown", this.onGlobalKeyDown);
    this.unsubscribeLayout?.();
    this.unsubscribePanels?.();
    this.unsubscribeCellDrawer?.();
    this.container?.remove();
  }
}

/** The singleton command palette. */
export const palette = new CommandPalette();

/** Initialize the palette (called from main.ts). */
export async function initPalette(): Promise<void> {
  await palette.init();
}

/** Open the palette programmatically. */
export function openPalette(): void {
  palette.open();
}

/** Close the palette programmatically. */
export function closePalette(): void {
  palette.close();
}