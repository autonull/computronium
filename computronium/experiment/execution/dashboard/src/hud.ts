/** HUD — Mission Control Panel (TODO68 Phase 4). */

import { registry } from "./components/registry.js";
import { router } from "./ws-client.js";
import { PALETTE } from "./palette.js";
import type { Component } from "./components/registry.js";

interface StatusData {
  gpu_utilization?: number;
  cpu_utilization?: number;
  memory_utilization?: number;
  used_gpus?: number;
  max_gpus?: number;
  used_cpus?: number;
  max_cpus?: number;
  used_memory_gb?: number;
  max_memory_gb?: number;
  running_campaigns?: number;
  queued_campaigns?: number;
}

interface CampaignResources {
  device?: string;
  memory_mb?: number;
  walltime_s?: number;
  records?: number;
  seeds_per_arm?: number;
}

interface MeterRow {
  key: string;
  label: string;
  value: string;
  fraction: number;
  color: string;
}

export class HUD implements Component {
  name = "HUD";

  private panel: HTMLElement | null = null;
  private modeChip: HTMLElement | null = null;
  private connectionPill: HTMLElement | null = null;
  private rows: Map<string, MeterRow> = new Map();
  private rowElements: Map<string, { fill: HTMLElement; value: HTMLElement }> =
    new Map();
  private claimValue: HTMLElement | null = null;
  private statusData: StatusData = {};
  private resources: CampaignResources = {};
  private requiredSeeds = 0;
  private measuredSeeds = 0;
  private connected = false;
  private animationTime = 0;

  constructor() {
    router.register("status_update", this.onStatusUpdate);
    router.register("campaign_metrics", this.onCampaignMetrics);
  }

  async init(): Promise<void> {
    this.createPanel();
    this.createModeChip();
    console.log("[HUD] Initialized");
  }

  async destroy(): Promise<void> {
    router.unregister("status_update", this.onStatusUpdate);
    router.unregister("campaign_metrics", this.onCampaignMetrics);
    this.panel?.remove();
    this.modeChip?.remove();
  }

  private createPanel(): void {
    const overlay = document.getElementById("ui-overlay");
    if (!overlay) return;

    this.panel = document.createElement("div");
    this.panel.id = "hud";
    this.panel.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      width: 260px;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px 16px;
      font-size: 11px;
      z-index: 150;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    `;

    this.panel.innerHTML = `
      <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
        <span style="font-weight: 600; color: var(--text-primary); letter-spacing: 0.08em;">MISSION CONTROL</span>
        <div style="flex: 1;"></div>
        <span id="hud-connection" style="
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
          <span>offline</span>
        </span>
      </div>
      <div id="hud-meters" style="display: flex; flex-direction: column; gap: 9px;"></div>
      <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: baseline;">
        <span style="color: var(--text-secondary);">SEEDS TO CLAIM</span>
        <span id="hud-claim" style="font-weight: 700; color: ${PALETTE.insufficient};">—</span>
      </div>
    `;

    overlay.appendChild(this.panel);

    const meters = this.panel.querySelector<HTMLElement>("#hud-meters")!;
    this.addMeter(meters, "device", "DEVICE", PALETTE.gradient);
    this.addMeter(meters, "memory", "MEMORY", PALETTE.memory);
    this.addMeter(meters, "walltime", "WALLTIME", PALETTE.cpu);
    this.addMeter(meters, "gpu", "GPU", PALETTE.gpu);
    this.addMeter(meters, "cpu", "CPU", PALETTE.cpu);
    this.addMeter(meters, "records", "RECORDS", PALETTE.pareto);

    this.claimValue = this.panel.querySelector("#hud-claim");
    this.connectionPill = this.panel.querySelector("#hud-connection");
  }

  private addMeter(
    container: HTMLElement,
    key: string,
    label: string,
    color: string,
  ): void {
    const row = document.createElement("div");
    row.style.cssText = "display: flex; flex-direction: column; gap: 3px;";
    row.innerHTML = `
      <div style="display: flex; justify-content: space-between;">
        <span style="color: var(--text-secondary);">${label}</span>
        <span class="hud-value" style="color: var(--text-primary);">—</span>
      </div>
      <div style="height: 4px; background: var(--bg); border-radius: 2px; overflow: hidden;">
        <div class="hud-fill" style="height: 100%; width: 0%; background: ${color}; border-radius: 2px; transition: width 0.4s ease;"></div>
      </div>
    `;
    container.appendChild(row);
    this.rows.set(key, { key, label, value: "", fraction: 0, color });
    this.rowElements.set(key, {
      fill: row.querySelector<HTMLElement>(".hud-fill")!,
      value: row.querySelector<HTMLElement>(".hud-value")!,
    });
  }

  private createModeChip(): void {
    const overlay = document.getElementById("ui-overlay");
    if (!overlay) return;

    this.modeChip = document.createElement("div");
    this.modeChip.id = "mode-chip";
    this.modeChip.style.cssText = `
      position: fixed;
      top: 20px;
      left: 20px;
      padding: 6px 14px;
      border-radius: 16px;
      background: ${PALETTE.insufficient}22;
      border: 1px solid ${PALETTE.insufficient}88;
      color: ${PALETTE.insufficient};
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.1em;
      z-index: 150;
    `;
    this.modeChip.textContent = "EXPLORATORY";
    overlay.appendChild(this.modeChip);
  }

  private setMeter(key: string, value: string, fraction: number): void {
    const row = this.rows.get(key);
    const elements = this.rowElements.get(key);
    if (!row || !elements) return;
    row.value = value;
    row.fraction = Math.max(0, Math.min(1, fraction));
    elements.value.textContent = value;
    elements.fill.style.width = `${(row.fraction * 100).toFixed(1)}%`;
  }

  private onStatusUpdate = (data: any): void => {
    const status = (data?.data ?? data) as StatusData;
    if (!status) return;
    this.statusData = status;
    this.connected = true;
    this.updateConnection();
    this.updateQueueRows();
  };

  private onCampaignMetrics = (data: any): void => {
    const metrics = data?.data;
    if (!metrics) return;

    this.resources = (metrics.resources ?? {}) as CampaignResources;
    if (typeof metrics.required_seeds === "number") {
      this.requiredSeeds = metrics.required_seeds;
    }
    this.measuredSeeds = this.resources.seeds_per_arm ?? metrics.records?.length ?? 0;
    this.updateResourceRows();
    this.updateClaim();
  };

  private updateQueueRows(): void {
    const status = this.statusData;
    // No queue means no quota to report: the rows stay empty rather than lie.
    this.setMeter(
      "gpu",
      status.max_gpus ? `${status.used_gpus ?? 0} / ${status.max_gpus}` : "—",
      status.max_gpus ? (status.used_gpus ?? 0) / status.max_gpus : 0,
    );
    this.setMeter(
      "cpu",
      status.max_cpus ? `${status.used_cpus ?? 0} / ${status.max_cpus}` : "—",
      status.max_cpus ? (status.used_cpus ?? 0) / status.max_cpus : 0,
    );
  }

  private updateResourceRows(): void {
    const resources = this.resources;
    this.setMeter("device", resources.device ?? "—", resources.device ? 1 : 0);
    this.setMeter(
      "memory",
      resources.memory_mb !== undefined
        ? `${resources.memory_mb.toFixed(1)} MB`
        : "—",
      resources.memory_mb !== undefined
        ? Math.min(1, resources.memory_mb / 2048)
        : 0,
    );
    this.setMeter(
      "walltime",
      resources.walltime_s !== undefined
        ? `${resources.walltime_s.toFixed(1)} s`
        : "—",
      resources.walltime_s !== undefined
        ? Math.min(1, resources.walltime_s / 120)
        : 0,
    );
    this.setMeter(
      "records",
      resources.records !== undefined ? `${resources.records}` : "—",
      resources.records !== undefined ? Math.min(1, resources.records / 20) : 0,
    );
  }

  private updateClaim(): void {
    if (!this.claimValue) return;
    if (this.requiredSeeds <= 0) {
      this.claimValue.textContent = "—";
      return;
    }
    const missing = Math.max(0, this.requiredSeeds - this.measuredSeeds);
    this.claimValue.textContent = `${missing} more (${this.requiredSeeds} needed)`;
  }

  private updateConnection(): void {
    if (!this.connectionPill) return;
    const dot = this.connectionPill.querySelector(".dot") as HTMLElement;
    const label = this.connectionPill.querySelector("span:last-child") as HTMLElement;
    const color = this.connected ? PALETTE.ok : PALETTE.error;
    dot.style.background = color;
    this.connectionPill.style.background = `${color}22`;
    this.connectionPill.style.borderColor = `${color}88`;
    this.connectionPill.style.color = color;
    label.textContent = this.connected ? "live" : "offline";
  }

  update(delta: number): void {
    this.animationTime += delta;
    const pulse = 0.5 + 0.5 * Math.sin(this.animationTime * 2);
    this.connectionPill?.style.setProperty("opacity", `${0.75 + 0.25 * pulse}`);
  }
}

export const hud = new HUD();
registry.register(hud);
