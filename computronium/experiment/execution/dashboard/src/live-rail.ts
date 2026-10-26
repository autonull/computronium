/** Live rail — scrolling event log, one view per instance. */

import { registry } from "./components/registry.js";
import { panels, registerDisplayPanel } from "./panels.js";
import { createPanelShell } from "./shell.js";
import { wsClient } from "./ws-client.js";
import { PALETTE } from "./colors.js";
import { dockviewHost } from "./layout/dockview-host.js";
import type { Component } from "./components/registry.js";

type EventLevel = "ok" | "warn" | "error";

interface Event {
  stage: string;
  message: string;
  level: EventLevel;
  timestamp: string;
}

export function createRailBody(): string {
  return `
    <style>
      .rail-header { display: flex; align-items: center; gap: 8px; padding: 4px 8px; margin-bottom: 4px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 4px; font-size: 11px; }
      .rail-dot { width: 8px; height: 8px; border-radius: 50%; }
      .rail-log { max-height: 180px; overflow-y: auto; padding: 4px; display: flex; flex-direction: column; gap: 2px; }
      .rail-event { display: flex; align-items: center; gap: 6px; padding: 3px 6px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 3px; font-size: 10px; }
      .rail-time { color: var(--text-muted); font-variant-numeric: tabular-nums; white-space: nowrap; }
      .rail-stage { color: var(--text-secondary); font-weight: 500; min-width: 70px; }
      .rail-msg { color: var(--text-primary); flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
      .rail-event.warn .rail-msg { color: var(--warn); }
      .rail-event.error .rail-msg { color: var(--error); }
      /* Collapsed state - only header visible */
      .rail-collapsed .rail-log { display: none; }
      .rail-collapsed .rail-header { margin-bottom: 0; }
    </style>
    <div class="rail-header">
      <span class="rail-conn"><span class="rail-dot"></span><span class="rail-label">Disconnected</span></span>
      <span style="flex: 1;"></span>
      <span class="rail-queue" style="color: var(--text-secondary); font-variant-numeric: tabular-nums;">0 running · 0 queued</span>
    </div>
    <div class="rail-log"></div>
  `;
}

/** A rail bound to one root element and its own event history. */
export class LiveRailView {
  private readonly log: HTMLElement;
  private readonly dot: HTMLElement;
  private readonly label: HTMLElement;
  private readonly queue: HTMLElement;
  private readonly header: HTMLElement;
  private events: Event[] = [];
  private readonly disposers: (() => void)[] = [];
  private instanceId: string | null = null;

  constructor(private readonly root: HTMLElement) {
    this.log = this.query(".rail-log");
    this.header = this.query(".rail-header");
    this.dot = this.query(".rail-dot");
    this.label = this.query(".rail-label");
    this.queue = this.query(".rail-queue");
    this.disposers.push(
      wsClient.onStateChange((state) => this.setConn(state === "connected")),
    );
    // Start collapsed (no events)
    this.updateCollapsedState();
  }

  /** Set the Dockview instance ID for collapse/expand operations. */
  setInstanceId(instanceId: string): void {
    this.instanceId = instanceId;
  }

  dispose(): void {
    for (const dispose of this.disposers) dispose();
    this.disposers.length = 0;
    this.events = [];
  }

  add(stage: string, message: string, level: EventLevel = "ok"): void {
    const wasEmpty = this.events.length === 0;
    this.events.unshift({
      stage,
      message,
      level,
      timestamp: new Date().toISOString(),
    });
    if (this.events.length > 100) this.events.pop();
    this.render();
    if (wasEmpty) this.updateCollapsedState();
  }

  setQueue(running: number, queued: number): void {
    this.queue.textContent = `${running} running · ${queued} queued`;
  }

  private query<T extends HTMLElement>(selector: string): T {
    const el = this.root.querySelector<T>(selector);
    if (!el) throw new Error(`[LiveRail] missing element: ${selector}`);
    return el;
  }

  private setConn(connected: boolean): void {
    this.dot.style.background = connected ? "var(--ok)" : "var(--error)";
    this.label.textContent = connected ? "Connected" : "Disconnected";
  }

  private render(): void {
    const icons = { ok: "✓", warn: "⚠", error: "✗" };
    const colors = { ok: PALETTE.ok, warn: PALETTE.warn, error: PALETTE.error };
    this.log.innerHTML = this.events
      .map((event) => {
        const time = new Date(event.timestamp).toLocaleTimeString();
        return `<div class="rail-event ${event.level}"><span class="rail-time">${time}</span><span style="color:${colors[event.level]}">${icons[event.level]}</span><span class="rail-stage">${event.stage}</span><span class="rail-msg">${event.message}</span></div>`;
      })
      .join("");
    this.log.scrollTop = 0;
  }

  /** Collapse or expand the rail based on whether it has events. */
  private updateCollapsedState(): void {
    const isEmpty = this.events.length === 0;
    if (isEmpty) {
      this.root.classList.add("rail-collapsed");
    } else {
      this.root.classList.remove("rail-collapsed");
    }
    // The CSS handles the collapsed state; Dockview will respect the minSize on next layout
  }
}

/** Legacy panel class for GoldenLayout (until P2). Not auto-registered. */
export class LiveRail implements Component {
  name = "LiveRail";
  private container: HTMLElement | null = null;
  private view: LiveRailView | null = null;

  async init(): Promise<void> {
    this.container = createPanelShell({
      id: "live-rail",
      title: "Live Rail",
      glyph: "≡",
      body: createRailBody(),
      dock: "right",
      defaultOpen: true,
      className: "live-rail-panel",
    });
    this.view = new LiveRailView(this.container);
    registerDisplayPanel("live-rail", "live rail", "≡", () => this.container);
  }

  async destroy(): Promise<void> {
    this.view?.dispose();
    this.view = null;
    this.container?.remove();
  }

  add(stage: string, message: string, level: EventLevel = "ok"): void {
    this.view?.add(stage, message, level);
  }

  setQueue(running: number, queued: number): void {
    this.view?.setQueue(running, queued);
  }
}
