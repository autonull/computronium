/** Simple live rail — scrolling event log. */

import { registry } from "./components/registry.js";
import { panels, registerDisplayPanel } from "./panels.js";
import { createPanelShell } from "./shell.js";
import { wsClient } from "./ws-client.js";
import { PALETTE } from "./colors.js";
import type { Component } from "./components/registry.js";

interface Event { stage: string; message: string; level: "ok" | "warn" | "error"; timestamp: string; }

function createBody(): string {
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
    </style>
    <div class="rail-header">
      <span class="rail-conn"><span class="rail-dot" id="rail-dot"></span><span id="rail-label">Disconnected</span></span>
      <span style="flex: 1;"></span>
      <span id="rail-queue" style="color: var(--text-secondary); font-variant-numeric: tabular-nums;">0 running · 0 queued</span>
    </div>
    <div class="rail-log" id="rail-log"></div>
  `;
}

export class LiveRail implements Component {
  name = "LiveRail";
  private container: HTMLElement | null = null;
  private log: HTMLElement | null = null;
  private dot: HTMLElement | null = null;
  private label: HTMLElement | null = null;
  private queue: HTMLElement | null = null;
  private events: Event[] = [];
  private maxEvents = 100;

  async init(): Promise<void> {
    this.container = createPanelShell({ id: "live-rail", title: "Live Rail", glyph: "≡", body: createBody(), dock: "right", defaultOpen: true, className: "live-rail-panel" });
    this.log = this.container.querySelector("#rail-log")!;
    this.dot = this.container.querySelector("#rail-dot")!;
    this.label = this.container.querySelector("#rail-label")!;
    this.queue = this.container.querySelector("#rail-queue")!;
    registerDisplayPanel("live-rail", "live rail", "≡", () => this.container);
    wsClient.onStateChange((s) => this.setConn(s === "connected"));
    console.log("[LiveRail] Ready");
  }

  async destroy(): Promise<void> { this.container?.remove(); }

  private setConn(connected: boolean): void {
    if (!this.dot || !this.label) return;
    this.dot.style.background = connected ? "var(--ok)" : "var(--error)";
    this.label.textContent = connected ? "Connected" : "Disconnected";
  }

  add(stage: string, message: string, level: "ok" | "warn" | "error" = "ok"): void {
    this.events.unshift({ stage, message, level, timestamp: new Date().toISOString() });
    if (this.events.length > this.maxEvents) this.events.pop();
    this.render();
  }

  private render(): void {
    if (!this.log) return;
    this.log.innerHTML = this.events.map((e) => {
      const time = new Date(e.timestamp).toLocaleTimeString();
      const icons = { ok: "✓", warn: "⚠", error: "✗" };
      const colors = { ok: PALETTE.ok, warn: PALETTE.warn, error: PALETTE.error };
      return `<div class="rail-event ${e.level}"><span class="rail-time">${time}</span><span style="color:${colors[e.level]}">${icons[e.level]}</span><span class="rail-stage">${e.stage}</span><span class="rail-msg">${e.message}</span></div>`;
    }).join("");
    this.log.scrollTop = 0;
  }

  setQueue(running: number, queued: number): void {
    if (this.queue) this.queue.textContent = `${running} running · ${queued} queued`;
  }
}

export const liveRail = new LiveRail();
registry.register(liveRail);