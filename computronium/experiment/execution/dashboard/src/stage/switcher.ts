/** The switcher — the main view area, and the choice of what stands on it (TODO69 Phase 5).

    The canvas is a stage, and a view is what stands on it. The switcher is
    what turns "a picture" into "a canvas that can show more than one thing":
    a key that cycles the views, the number keys that pick one, and a
    selector in the legend, so the choice is visible where it is made.
*/

import { registry } from "../components/registry.js";
import { discoveryMap } from "../discovery-map.js";
import { ClaimCostView } from "./claim-cost.js";
import { ConvergenceView } from "./convergence.js";
import { FrontierView } from "./frontier.js";
import { MatrixView } from "./matrix.js";
import { SmallMultiplesView } from "./small-multiples.js";
import { SpreadView } from "./spread.js";
import { stageState, type StageChange } from "./state.js";
import { TerrainView } from "./terrain.js";
import { UncertaintyView } from "./uncertainty.js";
import type { StageView } from "./views.js";
import type { Component } from "../components/registry.js";

/** The discovery map, as one of the stage's views. */
class SpaceView implements StageView {
  id = "space";
  name = "Space";
  caption =
    "The declared space: the gaps as cages, the measured cells as pillars, the refusals as crosses.";

  enter(): void {
    discoveryMap.show();
  }

  exit(): void {
    discoveryMap.hide();
  }

  refresh(change: StageChange): void {
    discoveryMap.refreshView(change);
  }

  ready(): boolean {
    return discoveryMap.hasMeasured();
  }
}

export class ViewSwitcher implements Component {
  name = "ViewSwitcher";

  private views: StageView[] = [];
  private active: StageView | null = null;
  private selector: HTMLSelectElement | null = null;
  private captionElement: HTMLElement | null = null;
  private section: HTMLElement | null = null;

  constructor() {
    this.views = [
      new SpaceView(),
      new TerrainView(),
      new FrontierView(),
      new MatrixView(),
      new ConvergenceView(),
      new SmallMultiplesView(),
      new SpreadView(),
      new ClaimCostView(),
      new UncertaintyView(),
    ];
  }

  async init(): Promise<void> {
    window.addEventListener("keydown", this.onKeyDown);
    stageState.onChange((change) => this.active?.refresh(change));
    this.buildSection();
    this.attachSection();
    this.show(this.views[0].id);
    console.log("[ViewSwitcher] Initialized");
  }

  async destroy(): Promise<void> {
    window.removeEventListener("keydown", this.onKeyDown);
    this.active?.exit();
    this.active = null;
    this.section?.remove();
    this.section = null;
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

  /** The next view, in the order the number keys pick them. */
  cycle(): void {
    if (this.views.length === 0) return;
    const index = this.views.findIndex((view) => view === this.active);
    const next = this.views[(index + 1) % this.views.length];
    this.show(next.id);
  }

  private onKeyDown = (event: KeyboardEvent): void => {
    if (event.metaKey || event.ctrlKey || event.altKey) return;
    const target = event.target as HTMLElement | null;
    if (
      target &&
      ["INPUT", "SELECT", "TEXTAREA"].includes(target.tagName)
    ) {
      return;
    }

    const key = event.key.toLowerCase();
    if (key === "v") {
      this.cycle();
      return;
    }
    const index = Number.parseInt(event.key, 10) - 1;
    if (!Number.isNaN(index) && index >= 0 && index < this.views.length) {
      this.show(this.views[index].id);
    }
  };

  /** The selector, and what the active view says about itself. */
  private buildSection(): void {
    const section = document.createElement("div");
    section.id = "legend-view-section";
    section.style.cssText = "margin-bottom: 12px;";

    const heading = document.createElement("div");
    heading.textContent = "View";
    heading.style.cssText = "font-weight: 600; margin-bottom: 8px;";
    section.appendChild(heading);

    const select = document.createElement("select");
    select.id = "view-picker";
    select.style.cssText = `
      width: 100%;
      background: var(--bg-tertiary);
      color: var(--text-primary);
      border: 1px solid var(--border);
      border-radius: 4px;
      font-size: 11px;
      padding: 2px 4px;
    `;
    this.views.forEach((view) => {
      const option = document.createElement("option");
      option.value = view.id;
      option.textContent = view.name;
      select.appendChild(option);
    });
    select.addEventListener("change", () => this.show(select.value));
    section.appendChild(select);
    this.selector = select;

    const caption = document.createElement("div");
    caption.id = "view-caption";
    caption.style.cssText =
      "font-size: 11px; color: var(--text-secondary); margin-top: 8px;";
    section.appendChild(caption);
    this.captionElement = caption;

    const keys = document.createElement("div");
    keys.textContent = `V cycles · 1–${this.views.length} pick`;
    keys.style.cssText = "font-size: 10px; color: var(--text-muted); margin-top: 6px;";
    section.appendChild(keys);

    this.section = section;
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

  private updateSelector(): void {
    if (!this.selector || !this.active) return;
    this.selector.value = this.active.id;
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
