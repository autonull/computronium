/** Caption — the closed-caption overlay (TODO69 Phase 1, refactored for TODO71 Phase 1).
 *
 * The words come from the server. The `narration` frame carries the state —
 * what the system is doing now — and every `pipeline_event` frame carries the
 * sentence for the thing that just happened. The browser renders them and
 * writes none of its own, so the caption, the live rail and an agent reading
 * `/api/narration` all say the same thing in the same words.
 *
 * A sentence holds the headline for a few seconds; then the state summary
 * comes back, so a reader who looks up at any moment sees where the system
 * stands rather than a line that has gone stale.
 */

import { registry } from "./components/registry.js";
import { PANEL_KEYS } from "./keys.js";
import { panels, registerDisplayPanel } from "./panels.js";
import { createPanelShell } from "./shell.js";
import { router } from "./ws-client.js";
import { PALETTE } from "./palette.js";
import type { Component } from "./components/registry.js";

interface NarrationFrame {
  state?: string[];
}

interface EventFrame {
  sentence?: string;
  level?: string;
}

/** How long a sentence holds the headline before the summary returns. */
const HOLD_MS = 4000;

const LEVEL_COLORS: Record<string, string> = {
  ok: PALETTE.text_primary,
  warn: PALETTE.warn,
  error: PALETTE.error,
};

function createCaptionBody(): string {
  return `
    <div id="caption-headline">The dashboard is starting.</div>
    <div id="caption-context"></div>
  `;
}

export class Caption implements Component {
  name = "Caption";

  private container: HTMLElement | null = null;
  private headline: HTMLElement | null = null;
  private context: HTMLElement | null = null;
  private state: string[] = [];
  private spoken: { text: string; level: string } | null = null;
  private last: { text: string; level: string } | null = null;
  private holdTimer: number | null = null;

  constructor() {
    router.register("narration", this.onNarration);
    router.register("pipeline_event", this.onEvent);
  }

  async init(): Promise<void> {
    this.container = createPanelShell({
      id: "caption",
      title: "Caption",
      glyph: "▤",
      key: PANEL_KEYS.caption,
      body: createCaptionBody(),
      dock: "bottom",
      defaultOpen: true,
      className: "caption-panel",
    });

    this.headline = this.container.querySelector("#caption-headline");
    this.context = this.container.querySelector("#caption-context");

    registerDisplayPanel(
      "caption",
      "caption",
      "▤",
      () => this.container,
      PANEL_KEYS.caption,
    );
    this.render();
  }

  async destroy(): Promise<void> {
    router.unregister("narration", this.onNarration);
    router.unregister("pipeline_event", this.onEvent);
    if (this.holdTimer !== null) window.clearTimeout(this.holdTimer);
    this.container?.remove();
  }

  /** Say a sentence, in the server's words, for a few seconds.
   *
   * The text is never composed here: it comes from the narration, and the
   * caller only decides when to show it again. */
  say(text: string, level = "ok"): void {
    if (!text) return;
    this.spoken = { text, level };
    this.last = { text, level };
    this.render();
    if (this.holdTimer !== null) window.clearTimeout(this.holdTimer);
    this.holdTimer = window.setTimeout(() => {
      this.spoken = null;
      this.holdTimer = null;
      this.render();
    }, HOLD_MS);
  }

  private onNarration = (data: NarrationFrame): void => {
    this.state = data?.state ?? [];
    this.render();
  };

  private onEvent = (data: EventFrame): void => {
    if (!data?.sentence) return;
    this.say(data.sentence, data.level ?? "ok");
  };

  private render(): void {
    if (!this.headline || !this.context) return;

    if (this.spoken) {
      this.headline.textContent = this.spoken.text;
      this.headline.style.color = this.colorOf(this.spoken.level);
      this.context.textContent = this.state.join(" · ");
      return;
    }

    if (this.state.length > 0) {
      this.headline.textContent = this.state[0];
      this.headline.style.color = PALETTE.text_primary;
      this.context.textContent = this.state.slice(1).join(" · ");
      return;
    }

    // No run has reported yet, so there is no state to fall back to. The
    // last thing that happened is still the truest thing to say.
    if (this.last) {
      this.headline.textContent = this.last.text;
      this.headline.style.color = this.colorOf(this.last.level);
      this.context.textContent = "";
      return;
    }

    this.headline.textContent = "The dashboard is starting.";
    this.headline.style.color = PALETTE.text_primary;
    this.context.textContent = "";
  }

  private colorOf(level: string): string {
    return LEVEL_COLORS[level] ?? PALETTE.text_primary;
  }
}

export const caption = new Caption();
registry.register(caption);