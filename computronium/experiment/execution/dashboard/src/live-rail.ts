/** Live Rail — Scrolling Pipeline Event Log (TODO68 Phase 4, refactored for TODO71 Phase 1). */

import { registry } from "./components/registry.js";
import { PANEL_KEYS } from "./keys.js";
import { panels, registerDisplayPanel, getPanelElement } from "./panels.js";
import { createPanelShell } from "./shell.js";
import { router, wsClient } from "./ws-client.js";
import { PALETTE } from "./palette.js";
import type { Component } from "./components/registry.js";

interface PipelineEvent {
  stage: string;
  message: string;
  level: "ok" | "warn" | "error";
  timestamp: string;
  run_id?: string;
}

function createLiveRailBody(): string {
  return `
    <div id="rail-header" class="rail-header-inner">
      <span class="rail-connection" id="rail-connection">
        <span class="dot"></span>
        <span class="rail-label">Disconnected</span>
      </span>
      <div style="flex: 1;"></div>
      <span id="rail-queue" class="rail-queue">0 running · 0 queued</span>
      <span id="rail-count" class="rail-count">0 events</span>
    </div>
    <div id="rail-log"></div>
    <!-- Scroll hint -->
    <div id="rail-scroll-hint"></div>
  `;
}

export class LiveRail implements Component {
  name = "LiveRail";

  private container: HTMLElement | null = null;
  private logContainer: HTMLElement | null = null;
  private scrollHint: HTMLElement | null = null;
  private events: PipelineEvent[] = [];
  private maxEvents = 50;

  constructor() {
    // Register WebSocket handlers IMMEDIATELY in constructor
    router.register("pipeline_event", this.onPipelineEvent);
    router.register("status_update", this.onStatusUpdate);
  }

  async init(): Promise<void> {
    this.container = createPanelShell({
      id: "live-rail",
      title: "LIVE RAIL",
      glyph: "≡",
      key: PANEL_KEYS.rail,
      body: createLiveRailBody(),
      dock: "bottom",
      defaultOpen: true,
      className: "live-rail-panel",
    });

    this.logContainer = this.container.querySelector("#rail-log")!;
    this.scrollHint = this.container.querySelector("#rail-scroll-hint") as HTMLElement;

    registerDisplayPanel(
      "live-rail",
      "live rail",
      "≡",
      () => this.container,
      PANEL_KEYS.rail,
    );
    wsClient.onStateChange((state) => this.setConnected(state === "connected"));
    console.log("[LiveRail] Initialized");
  }

  async destroy(): Promise<void> {
    router.unregister("pipeline_event", this.onPipelineEvent);
    router.unregister("status_update", this.onStatusUpdate);
    this.container?.remove();
  }

  private onPipelineEvent = (data: PipelineEvent): void => {
    this.events.unshift(data);
    if (this.events.length > this.maxEvents) this.events.pop();
    this.render();
  };

  private onStatusUpdate = (data: any): void => {
    const running = data?.data?.running_campaigns ?? 0;
    const queued = data?.data?.queued_campaigns ?? 0;
    const countEl = this.container?.querySelector(
      "#rail-queue",
    ) as HTMLElement | null;
    if (countEl) {
      countEl.textContent = `${running} running · ${queued} queued`;
    }
  };

  /** The pill reports the socket, not the campaign: one says "connected",
      the other says "idle". */
  private setConnected(connected: boolean): void {
    const connEl = this.container?.querySelector(
      "#rail-connection",
    ) as HTMLElement | null;
    if (!connEl) return;

    const dot = connEl.querySelector(".dot") as HTMLElement | null;
    const text = connEl.querySelector(".rail-label") as HTMLElement | null;
    if (!dot || !text) return;

    const color = connected ? PALETTE.ok : PALETTE.error;
    dot.style.background = color;
    connEl.style.background = color + "22";
    connEl.style.borderColor = color + "88";
    connEl.style.color = color;
    text.textContent = connected ? "Connected" : "Disconnected";
  }

  private render(): void {
    if (!this.logContainer) return;

    this.logContainer.innerHTML = this.events
      .map((event, index) => {
        const time = new Date(event.timestamp).toLocaleTimeString();
        const levelColors: Record<string, string> = {
          ok: PALETTE.ok,
          warn: PALETTE.warn,
          error: PALETTE.error,
        };
        const color = levelColors[event.level] || PALETTE.text_secondary;
        const icons: Record<string, string> = {
          ok: "✓",
          warn: "⚠",
          error: "✗",
        };
        const isLatest = index === 0;

        return `
          <span class="rail-event ${isLatest ? "latest" : ""}">
            <span class="rail-time">${time}</span>
            <span class="rail-icon" style="color: ${color};">${icons[event.level] ?? "•"}</span>
            <span class="rail-stage">${event.stage}</span>
            <span class="rail-message">${event.message}</span>
          </span>
        `;
      })
      .join("");

    const countEl = this.container?.querySelector(
      "#rail-count",
    ) as HTMLElement | null;
    if (countEl) countEl.textContent = `${this.events.length} events`;

    // Auto-scroll to latest (left side)
    this.logContainer.scrollLeft = 0;

    // Update scroll hint
    if (this.scrollHint) {
      const canScroll = this.logContainer!.scrollWidth > this.logContainer!.clientWidth;
      this.scrollHint.style.opacity = canScroll ? "1" : "0";
    }
  }
}

export const liveRail = new LiveRail();
registry.register(liveRail);