/** Live Rail — Scrolling Pipeline Event Log (TODO68 Phase 4). */

import { registry } from "./components/registry.js";
import { PANEL_KEYS } from "./keys.js";
import {
  closeButton,
  panels,
  registerDisplayPanel,
} from "./panels.js";
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

export class LiveRail implements Component {
  name = "LiveRail";

  private container: HTMLElement | null = null;
  private logContainer: HTMLElement | null = null;
  private events: PipelineEvent[] = [];
  private maxEvents = 50;

  constructor() {
    // Register WebSocket handlers IMMEDIATELY in constructor
    router.register("pipeline_event", this.onPipelineEvent);
    router.register("status_update", this.onStatusUpdate);
  }

  async init(): Promise<void> {
    this.createUI();
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

  private createUI(): void {
    const overlay = document.getElementById("ui-overlay");
    if (!overlay) return;

    this.container = document.createElement("div");
    this.container.id = "live-rail";
    this.container.style.cssText = `
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      height: 120px;
      background: linear-gradient(to top, var(--bg), transparent);
      border-top: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      z-index: 100;
      pointer-events: none;
    `;

    this.container.innerHTML = `
      <div id="rail-header" style="
        padding: 8px 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 11px;
        color: var(--text-secondary);
        border-bottom: 1px solid var(--border);
        background: var(--bg-secondary);
      ">
        <span style="font-weight: 600; color: var(--text-primary);">LIVE RAIL</span>
        <span id="rail-connection" style="
          display: inline-flex;
          align-items: center;
          gap: 4px;
          padding: 2px 8px;
          border-radius: 12px;
          background: var(--error)22;
          border: 1px solid var(--error)88;
          color: var(--error);
        ">
          <span class="dot" style="width: 6px; height: 6px; border-radius: 50%; background: var(--error);"></span>
          <span class="rail-label">Disconnected</span>
        </span>
        <div style="flex: 1;"></div>
        <span id="rail-queue" style="color: var(--text-secondary);">0 running · 0 queued</span>
        <span id="rail-count">0 events</span>
      </div>
      <div id="rail-log" style="
        flex: 1;
        overflow-x: auto;
        overflow-y: hidden;
        display: flex;
        gap: 24px;
        padding: 8px 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        white-space: nowrap;
      "></div>
    `;

    overlay.appendChild(this.container);
    this.container
      .querySelector<HTMLElement>("#rail-header")!
      .appendChild(closeButton(() => panels.toggle("live-rail")));
    this.logContainer = this.container.querySelector("#rail-log")!;
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
      .map((event) => {
        const time = new Date(event.timestamp).toLocaleTimeString();
        const levelColors: Record<string, string> = {
          ok: PALETTE.ok,
          warn: PALETTE.warn,
          error: PALETTE.error,
        };
        const color = levelColors[event.level] || PALETTE.text_secondary;
        const icon =
          event.level === "ok" ? "✓" : event.level === "warn" ? "⚠" : "✗";

        return `
          <span style="
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 16px;
            color: var(--text-primary);
          ">
            <span style="color: var(--text-secondary);">${time}</span>
            <span style="color: ${color};">${icon}</span>
            <span style="color: var(--text-muted);">[${event.stage}]</span>
            <span>${event.message}</span>
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
  }
}

export const liveRail = new LiveRail();
registry.register(liveRail);
