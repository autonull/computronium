/** Caption — the closed-caption overlay (TODO69 Phase 1).
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
    this.createUI();
    this.render();
  }

  async destroy(): Promise<void> {
    router.unregister("narration", this.onNarration);
    router.unregister("pipeline_event", this.onEvent);
    if (this.holdTimer !== null) window.clearTimeout(this.holdTimer);
    this.container?.remove();
  }

  /** Hide or show the caption. */
  toggle(): void {
    if (!this.container) return;
    this.container.style.display =
      this.container.style.display === "none" ? "" : "none";
  }

  /** Say a sentence, in the server's words, for a few seconds.

      The text is never composed here: it comes from the narration, and the
      caller only decides when to show it again. */
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

  private createUI(): void {
    const overlay = document.getElementById("ui-overlay");
    if (!overlay) return;

    this.container = document.createElement("div");
    this.container.id = "caption";
    this.container.style.cssText = `
      position: fixed;
      bottom: 132px;
      left: 50%;
      transform: translateX(-50%);
      width: 820px;
      max-width: calc(100vw - 80px);
      padding: 12px 20px;
      background: rgba(10, 14, 20, 0.82);
      border: 1px solid var(--border);
      border-radius: 10px;
      text-align: center;
      z-index: 160;
      pointer-events: none;
      box-shadow: 0 8px 32px rgba(0,0,0,0.45);
    `;

    this.container.innerHTML = `
      <div id="caption-headline" style="
        font-size: 22px;
        line-height: 1.3;
        color: var(--text-primary);
        text-shadow: 0 2px 6px rgba(0,0,0,0.8);
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      ">The dashboard is starting.</div>
      <div id="caption-context" style="
        margin-top: 6px;
        font-size: 14px;
        line-height: 1.35;
        color: var(--text-secondary);
      "></div>
    `;

    overlay.appendChild(this.container);
    this.headline = this.container.querySelector("#caption-headline");
    this.context = this.container.querySelector("#caption-context");
  }

  private render(): void {
    if (!this.headline || !this.context) return;

    if (this.spoken) {
      this.headline.textContent = this.spoken.text;
      this.headline.style.color = this.colorOf(this.spoken.level);
      this.context.textContent = this.state.join(" ");
      return;
    }

    if (this.state.length > 0) {
      this.headline.textContent = this.state[0];
      this.headline.style.color = PALETTE.text_primary;
      this.context.textContent = this.state.slice(1).join(" ");
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
