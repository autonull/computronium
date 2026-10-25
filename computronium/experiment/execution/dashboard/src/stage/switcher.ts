/** The switcher — the main view area, and the choice of what stands on it (TODO69 Phase 5).

    The canvas is a stage, and a view is what stands on it. The switcher is
    what turns "a picture" into "a canvas that can show more than one thing":
    a key that cycles the views, the number keys that pick one, a letter for
    the views that do not fit in the numbers, and a toolbar in the legend, so
    the choice is visible where it is made.
*/

import { registry } from "../components/registry.js";
import { viewGlyph } from "../icons.js";
import { CYCLE_KEY, RESERVED_KEYS } from "../keys.js";
import { getViews, VIEW_GROUPS, registerView } from "./registry.js";
import "./basin.js";
import "./claim-cost.js";
import "./contrast.js";
import "./convergence.js";
import "./effect.js";
import "./flow.js";
import "./frontier.js";
import "./landscape.js";
import "./layers.js";
import "./ledger.js";
import "./matrix.js";
import "./multirun.js";
import "./slices.js";
import "./small-multiples.js";
import "./spread.js";
import "./spectrum.js";
import "./terrain.js";
import "./timeline.js";
import "./trained-basin.js";
import "./trained-landscape.js";
import "./trained-spectrum.js";
import "./trained-trajectory.js";
import "./trajectory.js";
import "./uncertainty.js";
import { stageState } from "./store.js";
import type { StageChange } from "./payloads.js";
import type { StageView, ViewGroup } from "./views.js";
import type { Component } from "../components/registry.js";

function getLegacyDiscoveryMap(): any {
  return (window as any).__DASHBOARD__?.discoveryMap ?? null;
}

/** The discovery map, as one of the stage's views. */
class SpaceView implements StageView {
  id = "space";
  name = "Space";
  group = "the space" as ViewGroup;
  caption =
    "The declared space: the gaps as cages, the measured cells as pillars, the refusals as crosses.";

  enter(): void {
    getLegacyDiscoveryMap()?.show();
  }

  exit(): void {
    getLegacyDiscoveryMap()?.hide();
  }

  refresh(change: StageChange): void {
    getLegacyDiscoveryMap()?.refreshView(change);
  }

  ready(): boolean {
    return getLegacyDiscoveryMap()?.hasMeasured?.() ?? false;
  }
}

// Register the SpaceView so it appears in the view switcher
registerView(new SpaceView());

export class ViewSwitcher implements Component {
  name = "ViewSwitcher";

  private views: StageView[] = [];
  private active: StageView | null = null;
  private track: HTMLElement | null = null;
  private viewButtons = new Map<string, HTMLButtonElement>();
  private captionElement: HTMLElement | null = null;
  private section: HTMLElement | null = null;
  /** The key that picks each view: the numbers first, then the letters. */
  private keys = new Map<string, StageView>();
  /** The key each view is picked by, so the legend can name it. */
  private keyOf = new Map<string, string>();

  constructor() {
    // Views are loaded via registry.ts imports; getViews() returns them in registration order
    this.views = getViews();
  }

  async init(): Promise<void> {
    window.addEventListener("keydown", this.onKeyDown);
    stageState.onChange((change) => this.active?.refresh(change));
    this.buildKeys();
    this.buildSection();
    this.attachSection();
    this.show("space");
    console.log("[ViewSwitcher] Initialized");
  }

  async destroy(): Promise<void> {
    window.removeEventListener("keydown", this.onKeyDown);
    this.active?.exit();
    this.active = null;
    this.section?.remove();
    this.section = null;
  }

  /** Get all registered views (for palette). */
  getViews(): StageView[] {
    return this.views;
  }

  /** The view that stands on the stage. */
  get activeId(): string | null {
    return this.active?.id ?? null;
  }

  /** Whether the active view has something to show. */
  isReady(id: string): boolean {
    const view = this.views.find((candidate) => candidate.id === id);
    return view ? view.ready() : false;
  }

  /** Put a view on the stage, and take the last one off it. */
  show(id: string): void {
    const view = this.views.find((candidate) => candidate.id === id);
    if (!view || view === this.active) return;
    this.active?.exit();
    this.active = view;
    view.enter();
    this.updateSelector();
    this.updateLegend();
  }

  /** The next view, in the order they are listed. */
  cycle(): void {
    if (this.views.length === 0) return;
    const index = this.views.findIndex((view) => view === this.active);
    const next = this.views[(index + 1) % this.views.length];
    this.show(next.id);
  }

  private onKeyDown = (event: KeyboardEvent): void => {
    if (event.metaKey || event.ctrlKey || event.altKey) return;
    const target = event.target as HTMLElement | null;
    if (target && ["INPUT", "SELECT", "TEXTAREA"].includes(target.tagName)) {
      return;
    }

    const key = event.key.toLowerCase();
    if (key === CYCLE_KEY) {
      this.cycle();
      return;
    }
    const view = this.keys.get(key);
    if (view) {
      this.show(view.id);
    }
  };

  /** The key that picks each view: the numbers first, then the letters.

    A view may name a key of its own, but not one another part of the
    dashboard already holds.
  */
  private buildKeys(): void {
    this.keys.clear();
    this.keyOf.clear();

    // The space view (discovery map) always gets key "1" as the primary view
    const spaceView = this.views.find((v) => v.id === "space");
    const otherViews = this.views.filter((v) => v.id !== "space");

    if (spaceView) {
      this.keys.set("1", spaceView);
      this.keyOf.set(spaceView.id, "1");
    }

    // Assign keys 2-9 to the first 8 other views
    otherViews.forEach((view, index) => {
      const digit = index < 8 ? String(index + 2) : "";
      if (digit) {
        this.keys.set(digit, view);
        this.keyOf.set(view.id, digit);
      }
      if (view.key && !RESERVED_KEYS.has(view.key)) {
        this.keys.set(view.key, view);
        this.keyOf.set(view.id, view.key);
      }
    });
  }

  /** The name of a view, and the key that picks it. */
  private optionLabel(view: StageView): string {
    const key = this.keyOf.get(view.id);
    return key ? `${key.toUpperCase()} · ${view.name}` : view.name;
  }

  /** The keys the reader can press, as the legend names them. */
  private keyHint(): string {
    const digits: string[] = [];
    const letters: string[] = [];
    const punctuation: string[] = [];
    this.views.forEach((view, index) => {
      if (index < 9) {
        digits.push(String(index + 1));
        return;
      }
      if (!view.key || RESERVED_KEYS.has(view.key)) return;
      if (/^[a-z]$/.test(view.key)) {
        letters.push(view.key.toUpperCase());
        return;
      }
      punctuation.push(view.key);
    });
    const parts = ["V cycles"];
    if (digits.length > 0)
      parts.push(`${digits[0]}–${digits[digits.length - 1]} pick`);
    if (letters.length > 0) parts.push(`${letters.join(" ")} pick`);
    if (punctuation.length > 0) parts.push(`${punctuation.join(" ")} pick`);
    return parts.join(" · ");
  }

  /** The selector, and what the active view says about itself. */
  private buildSection(): void {
    const section = document.createElement("div");
    section.id = "legend-view-section";
    section.style.cssText = "margin-bottom: 12px;";

    const heading = document.createElement("div");
    heading.textContent = "View";
    heading.style.cssText = "font-weight: 600; margin-bottom: 8px;";
    section.appendChild(heading);

    // The toolbar: views grouped by category with separators
    const strip = document.createElement("div");
    strip.id = "view-strip";
    strip.style.cssText = `
      display: flex;
      align-items: center;
      gap: 4px;
      width: 100%;
    `;
    strip.appendChild(this.stepButton("‹", "the previous view", -1));

    const track = document.createElement("div");
    track.id = "view-track";
    track.style.cssText = `
      display: flex;
      align-items: center;
      gap: 3px;
      flex: 1;
      overflow-x: auto;
      overflow-y: hidden;
      scrollbar-width: thin;
      padding-bottom: 2px;
    `;

    // Group views by the README's six sections
    const groups: Array<{ group: string; label: string; views: StageView[] }> =
      [
        { group: "the space", label: "The space", views: [] },
        { group: "the run", label: "The run", views: [] },
        { group: "the evidence", label: "The evidence", views: [] },
        { group: "the process", label: "The process", views: [] },
        { group: "the judgement", label: "The judgement", views: [] },
        { group: "the system", label: "The system", views: [] },
      ];

    for (const view of this.views) {
      const g = groups.find((grp) => grp.group === view.group);
      if (g) g.views.push(view);
    }

    groups.forEach((g, gi) => {
      if (g.views.length === 0) return;
      if (gi > 0) {
        // Group separator
        const sep = document.createElement("div");
        sep.style.cssText = `
          width: 1px;
          height: 16px;
          background: var(--border);
          margin: 0 4px;
        `;
        track.appendChild(sep);
      }
      // Group label
      const label = document.createElement("span");
      label.textContent = g.label;
      label.style.cssText = `
        font-size: 9px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        margin-right: 4px;
        flex-shrink: 0;
      `;
      track.appendChild(label);
      // View buttons in this group
      for (const view of g.views) {
        track.appendChild(this.viewButton(view));
      }
    });

    strip.appendChild(track);
    strip.appendChild(this.stepButton("›", "the next view", 1));
    section.appendChild(strip);
    this.track = track;

    const caption = document.createElement("div");
    caption.id = "view-caption";
    caption.style.cssText =
      "font-size: 11px; color: var(--text-secondary); margin-top: 8px;";
    section.appendChild(caption);
    this.captionElement = caption;

    const keys = document.createElement("div");
    keys.textContent = this.keyHint();
    keys.style.cssText =
      "font-size: 10px; color: var(--text-muted); margin-top: 6px;";
    section.appendChild(keys);

    this.section = section;
  }

  /** One view's button: its glyph, its name on hover, its key. */
  private viewButton(view: StageView): HTMLButtonElement {
    const glyph = viewGlyph(view.id);
    const key = this.keyOf.get(view.id);
    const button = document.createElement("button");
    button.className = "view-button";
    button.dataset.view = view.id;
    button.textContent = glyph.glyph;
    button.title = key ? `${key.toUpperCase()} · ${view.name}` : view.name;
    button.style.cssText = `
      flex: 0 0 auto;
      width: 22px;
      height: 22px;
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
      transition: all var(--motion-fast) var(--ease-out);
    `;
    // Kind-based border color hint
    const kindColors: Record<string, string> = {
      solid: "var(--promoted)",
      mark: "var(--gradient)",
      bar: "var(--cpu)",
      curve: "var(--warn)",
    };
    button.style.borderColor = kindColors[glyph.kind] + "44";

    button.addEventListener("mouseenter", () => {
      if (!button.classList.contains("active")) {
        button.style.background = "var(--bg-primary)";
        button.style.borderColor = kindColors[glyph.kind] + "88";
        button.style.color = "var(--text-primary)";
      }
    });
    button.addEventListener("mouseleave", () => {
      if (!button.classList.contains("active")) {
        button.style.background = "var(--bg-tertiary)";
        button.style.borderColor = kindColors[glyph.kind] + "44";
        button.style.color = "var(--text-secondary)";
      }
    });
    button.addEventListener("click", () => this.show(view.id));
    this.viewButtons.set(view.id, button);
    return button;
  }

  /** The ‹ and › pair: they step the sequence and scroll the strip. */
  private stepButton(
    glyph: string,
    label: string,
    direction: number,
  ): HTMLButtonElement {
    const button = document.createElement("button");
    button.className = "view-step";
    button.textContent = glyph;
    button.title = label;
    button.style.cssText = `
      flex: 0 0 auto;
      width: 20px;
      height: 22px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--bg-tertiary);
      border: 1px solid var(--border);
      border-radius: 4px;
      color: var(--text-secondary);
      font-size: 13px;
      cursor: pointer;
      padding: 0;
    `;
    button.addEventListener("click", () => this.step(direction));
    return button;
  }

  /** The next view, or the one before it, and the strip follows. */
  private step(direction: number): void {
    if (this.views.length === 0) return;
    const index = this.views.findIndex((view) => view.id === this.active?.id);
    const from = index < 0 ? 0 : index;
    const next = (from + direction + this.views.length) % this.views.length;
    this.show(this.views[next].id);
  }

  /** Put the selector in the legend, once the legend is there. */
  private attachSection(attempt = 0): void {
    const host = document.getElementById("legend-view");
    if (!host) {
      if (attempt < 50) {
        window.setTimeout(() => this.attachSection(attempt + 1), 100);
      }
      return;
    }
    if (this.section && this.section.parentElement !== host) {
      host.appendChild(this.section);
    }
    this.updateSelector();
    this.updateLegend();
  }

  /** Light the active view's button, and bring it into the strip. */
  private updateSelector(): void {
    if (!this.active) return;
    for (const [id, button] of this.viewButtons) {
      const on = id === this.active.id;
      button.classList.toggle("active", on);
      if (on) {
        button.style.color = "var(--text-primary)";
        button.style.borderColor = "var(--border-bright)";
        button.style.background = "var(--bg-primary)";
      }
    }
    this.scrollToActive();
  }

  /** The strip is longer than the screen, so the lit button follows it. */
  private scrollToActive(): void {
    const button = this.active ? this.viewButtons.get(this.active.id) : null;
    if (!button || !this.track) return;
    button.scrollIntoView({ block: "nearest", inline: "nearest" });
  }

  /** The legend names the view, and shows the marks only where they mean. */
  private updateLegend(): void {
    if (!this.active) return;
    const title = document.getElementById("legend-title");
    if (title) title.textContent = this.active.name;
    const marks = document.getElementById("legend-marks");
    if (marks) {
      marks.style.display = this.active.id === "space" ? "" : "none";
    }
    if (this.captionElement) {
      this.captionElement.textContent = this.active.caption;
    }
  }
}

export const viewSwitcher = new ViewSwitcher();
registry.register(viewSwitcher);
