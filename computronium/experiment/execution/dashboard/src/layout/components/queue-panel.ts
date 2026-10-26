/** Queue Panel — shows queued and running campaigns. */

import { registerDefinition } from "../definitions.js";
import type {
  ComponentContext,
  ComponentDefinition,
  ComponentHandle,
  JsonValue,
} from "../types.js";

/** One campaign, as the queue holds it. */
interface Campaign {
  campaign_id: string;
  name: string;
  status: string;
  priority: string;
}

function createQueuePanelBody(): string {
  return `
    <style>
      .queue-panel h4 { margin: 14px 0 6px; font-size: 10px; letter-spacing: 0.08em; color: var(--text-secondary); text-transform: uppercase; }
      .queue-panel table.list { width: 100%; border-collapse: collapse; font-size: 11px; }
      .queue-panel table.list th { text-align: left; font-weight: 500; color: var(--text-secondary); padding: 2px 6px 2px 0; vertical-align: top; }
      .queue-panel table.list td { color: var(--text-primary); padding: 2px 6px 2px 0; vertical-align: top; }
      .queue-panel button.mini { background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 4px; color: var(--text-primary); font-size: 11px; padding: 2px 8px; cursor: pointer; }
      .queue-panel .empty-state { text-align: center; padding: 24px 12px; color: var(--text-muted); font-size: 11px; }
      .queue-panel .empty-state .icon { font-size: 24px; margin-bottom: 8px; opacity: 0.5; }
    </style>
    <div class="queue-panel-header" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
      <span style="font-weight: 600; color: var(--text-primary); letter-spacing: 0.08em;">THE QUEUE</span>
    </div>
    <div class="queue-section empty-state">
      <div class="icon">📦</div>
      <div>No campaigns queued</div>
      <div style="margin-top: 4px; font-size: 10px;">Start a run to see queue</div>
    </div>
  `;
}

export class QueuePanelView {
  private queueSection: HTMLElement | null = null;

  constructor(
    private readonly root: HTMLElement,
    _state: JsonValue = null,
  ) {
    this.bindElements();
    this.renderQueue();
    // Auto-refresh every 5 seconds
    const interval = setInterval(() => this.renderQueue(), 5000);
    this.cleanup = () => clearInterval(interval);
  }

  private cleanup: () => void = () => {};

  dispose(): void {
    this.cleanup();
  }

  update(_state: JsonValue): void {
    this.renderQueue();
  }

  private bindElements(): void {
    this.queueSection = this.root.querySelector(".queue-section");
  }

  private async renderQueue(): Promise<void> {
    if (!this.queueSection) return;
    try {
      const res = await fetch("/api/queue");
      if (!res.ok) throw new Error();
      const data = await res.json();
      const campaigns = data.campaigns ?? [];
      if (!campaigns.length) {
        this.queueSection.innerHTML = `<div class="empty-state"><div class="icon">📦</div><div>No campaigns queued</div></div>`;
        return;
      }
      this.queueSection.innerHTML = `
        <table class="list">
          <thead><tr><th>Campaign</th><th>Status</th><th>Priority</th><th></th></tr></thead>
          <tbody>
            ${campaigns.map((c: Campaign) => `
              <tr>
                <td>${c.name}</td>
                <td>${c.status}</td>
                <td>${c.priority}</td>
                <td><button class="mini" data-cancel="${c.campaign_id}">Cancel</button></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      `;
      for (const btn of this.queueSection.querySelectorAll<HTMLButtonElement>("[data-cancel]")) {
        btn.addEventListener("click", async () => {
          btn.disabled = true;
          await fetch(`/api/campaign/${btn.dataset.cancel}`, { method: "DELETE" });
          this.renderQueue();
        });
      }
    } catch {
      this.queueSection.innerHTML = `<div class="empty-state"><div class="icon">📦</div><div>Queue unavailable</div></div>`;
    }
  }
}

export const queuePanelDefinition: ComponentDefinition = registerDefinition<JsonValue>({
  type: "queue-panel",
  title: "Queue",
  icon: "📦",
  defaultSize: { width: 400, height: 300 },
  create(
    host: HTMLElement,
    _state: JsonValue,
    _ctx: ComponentContext,
  ): ComponentHandle<JsonValue> {
    host.innerHTML = createQueuePanelBody();
    const view = new QueuePanelView(host);
    return {
      element: host,
      update(next: JsonValue): void {
        view.update(next);
      },
      dispose(): void {
        view.dispose();
        host.remove();
      },
    };
  },
});