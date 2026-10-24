/** HUD — Mission Control Panel (TODO68 Phase 4, refactored for TODO71 Phase 1). */

import { registry } from "./components/registry.js";
import { PANEL_KEYS } from "./keys.js";
import {
  panels,
  registerDisplayPanel,
  setPanelHidden,
  getPanelElement,
} from "./panels.js";
import { createPanelShell } from "./shell.js";
import { router, wsClient } from "./ws-client.js";
import { PALETTE } from "./colors.js";
import { runSelection, type RunMetrics } from "./run-selection.js";
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

interface RunStatus {
  run_id?: string;
  profile?: string;
  tasks?: string[];
  fidelity?: string;
  objectives?: string[];
  mode?: string;
  started_at?: string;
}

interface MeterRow {
  key: string;
  label: string;
  value: string;
  fraction: number;
  color: string;
}

function createHudBody(): string {
  return `
    <div id="hud-meters"></div>
    <div class="hud-source-row">
      <div class="meter-label-row">
        <span class="meter-label">PICTURE</span>
        <span id="hud-source" class="meter-value hud-source-value">—</span>
      </div>
      <div id="hud-claim-row">
        <div class="meter-label-row">
          <span class="meter-label">SEEDS TO CLAIM</span>
          <span id="hud-claim" class="meter-value hud-claim-value">—</span>
        </div>
        <div class="meter-bar"><div id="hud-claim-fill" class="meter-fill hud-claim-fill"></div></div>
      </div>
    </div>
  `;
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
  private claimFill: HTMLElement | null = null;
  private sourceValue: HTMLElement | null = null;
  private statusData: StatusData = {};
  private resources: CampaignResources = {};
  private requiredSeeds = 0;
  private measuredSeeds = 0;
  private connected = false;
  private animationTime = 0;

  constructor() {
    router.register("status_update", this.onStatusUpdate);
    router.register("campaign_metrics", this.onCampaignMetrics);
    runSelection.onChange(this.onRunChanged);
  }

  async init(): Promise<void> {
    this.panel = createPanelShell({
      id: "hud",
      title: "MISSION CONTROL",
      glyph: "◱",
      key: PANEL_KEYS.hud,
      body: createHudBody(),
      dock: "top",
      defaultOpen: true,
    });
    this.createModeChip();
    this.setupMeters();

    registerDisplayPanel(
      "hud",
      "mission control",
      "◱",
      () => this.panel,
      PANEL_KEYS.hud,
    );
    wsClient.onStateChange((state) => {
      this.connected = state === "connected";
      this.updateConnection();
    });
    console.log("[HUD] Initialized");
  }

  async destroy(): Promise<void> {
    router.unregister("status_update", this.onStatusUpdate);
    router.unregister("campaign_metrics", this.onCampaignMetrics);
    this.panel?.remove();
    this.modeChip?.remove();
  }

  private setupMeters(): void {
    if (!this.panel) return;
    const meters = this.panel.querySelector<HTMLElement>("#hud-meters")!;
    this.addMeter(meters, "device", "DEVICE", "var(--gradient)");
    this.addMeter(meters, "memory", "MEMORY", "var(--memory)");
    this.addMeter(meters, "walltime", "WALLTIME", "var(--cpu)");
    this.addMeter(meters, "gpu", "GPU", "var(--gpu)");
    this.addMeter(meters, "cpu", "CPU", "var(--cpu)");
    this.addMeter(meters, "records", "RECORDS", "var(--promoted)");

    this.claimValue = this.panel.querySelector("#hud-claim");
    this.claimFill = this.panel.querySelector("#hud-claim-fill");
    this.connectionPill = this.panel.querySelector("#hud-connection");
    this.sourceValue = this.panel.querySelector("#hud-source");
  }

  private addMeter(
    container: HTMLElement,
    key: string,
    label: string,
    color: string,
  ): void {
    const row = document.createElement("div");
    row.className = "meter-row";
    row.innerHTML = `
      <div class="meter-label-row">
        <span class="meter-label">${label}</span>
        <span class="meter-value hud-value">—</span>
      </div>
      <div class="meter-bar"><div class="meter-fill hud-fill" style="background: ${color};"></div></div>
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
    this.modeChip.className = "mode-chip";
    this.modeChip.innerHTML = `
      <div class="mode-label">NO RUN</div>
      <div class="mode-detail"></div>
    `;
    overlay.appendChild(this.modeChip);
  }

  /** The chip reports the run's own registration status, measured. */
  private updateModeChip(run: RunStatus | undefined): void {
    if (!this.modeChip) return;

    const mode = run?.mode ?? "NO RUN";
    const color =
      mode === "PREREGISTERED"
        ? PALETTE.passed
        : mode === "EXPLORATORY"
          ? PALETTE.insufficient
          : PALETTE.text_muted;

    this.modeChip.style.background = `${color}22`;
    this.modeChip.style.borderColor = `${color}88`;
    this.modeChip.style.color = color;

    const label = this.modeChip.querySelector(".mode-label");
    if (label) label.textContent = mode;

    const detail = this.modeChip.querySelector(".mode-detail");
    if (detail) {
      detail.textContent = [
        run?.profile,
        (run?.tasks ?? []).join(", "),
        run?.fidelity,
      ]
        .filter(Boolean)
        .join(" · ");
    }

    this.modeChip.title = run
      ? `run ${run.run_id ?? "?"} · objectives: ${(run.objectives ?? []).join(", ") || "none"}`
      : "No run has reported yet";
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
    this.updateQueueRows();
  };

  private onCampaignMetrics = (data: any): void => {
    const metrics = data?.data;
    if (!metrics) return;

    // The panel reports the run the dashboard shows, not whichever run
    // reported last.
    runSelection.observe(data?.campaign_id, metrics);
  };

  /** The panel reads the run the reader is looking at. */
  private onRunChanged = (
    _runId: string | null,
    metrics: RunMetrics | null,
  ): void => {
    if (!metrics) return;
    this.resources = (metrics.resources ?? {}) as CampaignResources;
    if (typeof metrics.required_seeds === "number") {
      this.requiredSeeds = metrics.required_seeds;
    }
    this.measuredSeeds =
      this.resources.seeds_per_arm ?? metrics.records?.length ?? 0;
    this.updateModeChip(metrics.run as RunStatus | undefined);
    this.updateSource(metrics.store);
    this.updateResourceRows();
    this.updateClaim();
  };

  /** Where the picture came from: the store itself, or the writer's mirror.
   *
   * A snapshot lags the run by the writer's publish interval, and a reader
   * that does not know which it is looking at cannot tell a finished run
   * from a paused one.
   */
  private updateSource(
    store: { source?: string; published_at?: string } | undefined,
  ): void {
    if (!this.sourceValue) return;
    const source = store?.source;
    if (!source) {
      this.sourceValue.textContent = "—";
      this.sourceValue.style.color = "var(--text-secondary)";
      return;
    }
    if (source === "snapshot") {
      const published = store?.published_at
        ? new Date(store.published_at).toLocaleTimeString()
        : "";
      this.sourceValue.textContent = published
        ? `snapshot ${published}`
        : "snapshot";
      this.sourceValue.style.color = "var(--insufficient)";
      this.sourceValue.title =
        "The writer published this copy; it is as fresh as its last publish.";
      return;
    }
    this.sourceValue.textContent = "live";
    this.sourceValue.style.color = "var(--passed)";
    this.sourceValue.title = "The store itself, read as it is written.";
  }

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
    if (!this.claimValue || !this.claimFill) return;
    if (this.requiredSeeds <= 0) {
      this.claimValue.textContent = "—";
      this.claimFill.style.width = "0%";
      return;
    }
    const missing = Math.max(0, this.requiredSeeds - this.measuredSeeds);
    const progress =
      this.requiredSeeds > 0 ? this.measuredSeeds / this.requiredSeeds : 0;
    this.claimValue.textContent =
      missing > 0
        ? `${missing} more (${this.requiredSeeds} needed)`
        : `Ready (${this.requiredSeeds} met)`;
    this.claimValue.style.color =
      missing > 0 ? "var(--insufficient)" : "var(--passed)";
    this.claimFill.style.width = `${Math.min(100, progress * 100)}%`;
    this.claimFill.style.background =
      missing > 0 ? "var(--insufficient)" : "var(--passed)";
  }

  private updateConnection(): void {
    if (!this.connectionPill) return;
    const dot = this.connectionPill.querySelector(".dot") as HTMLElement;
    const label = this.connectionPill.querySelector(
      "span:last-child",
    ) as HTMLElement;
    const color = this.connected ? "var(--ok)" : "var(--error)";
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
