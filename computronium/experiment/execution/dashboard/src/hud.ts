/** HUD — Mission Control Panel, one view per instance. */

import { router, wsClient } from "./ws-client.js";
import { PALETTE } from "./colors.js";
import { runSelection, type RunMetrics } from "./run-selection.js";
import type { JsonValue } from "./layout/types.js";

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

export function createHudBody(): string {
  return `
    <style>
      .hud-header { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
      .hud-mode { display: flex; align-items: center; gap: 8px; }
      .hud-mode-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; padding: 3px 8px; border-radius: 4px; color: var(--text-primary); }
      .hud-mode-detail { font-size: 10px; color: var(--text-secondary); }
      .hud-connection { display: flex; align-items: center; gap: 6px; font-size: 10px; }
      .hud-connection .dot { width: 8px; height: 8px; border-radius: 50%; }
      .hud-meters { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 8px; }
      .hud-meter { background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 6px; padding: 8px 10px; }
      .hud-meter-row { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px; }
      .hud-meter-label { font-size: 9px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); }
      .hud-meter-value { font-size: 13px; font-weight: 600; color: var(--text-primary); font-variant-numeric: tabular-nums; }
      .hud-meter-bar { height: 5px; background: var(--bg); border-radius: 2px; overflow: hidden; }
      .hud-meter-fill { height: 100%; width: 0%; border-radius: 2px; }
      .hud-claim { background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 6px; padding: 8px 10px; }
      .hud-claim-row { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px; }
      .hud-claim-label { font-size: 9px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); }
      .hud-claim-value { font-size: 13px; font-weight: 600; color: var(--text-primary); }
      .hud-claim-bar { height: 5px; background: var(--bg); border-radius: 2px; overflow: hidden; }
      .hud-claim-fill { height: 100%; width: 0%; border-radius: 2px; background: var(--promoted); }
      .hud-source { display: flex; justify-content: space-between; align-items: center; font-size: 10px; color: var(--text-secondary); padding-top: 6px; border-top: 1px solid var(--border); }
    </style>
    <div class="hud-header">
      <div class="hud-mode">
        <span class="hud-mode-label">NO RUN</span>
        <span class="hud-mode-detail"></span>
      </div>
      <div class="hud-connection">
        <span class="dot"></span>
        <span class="hud-conn-label">Disconnected</span>
      </div>
    </div>
    <div class="hud-meters"></div>
    <div class="hud-claim">
      <div class="hud-claim-row">
        <span class="hud-claim-label">SEEDS TO CLAIM</span>
        <span class="hud-claim-value">—</span>
      </div>
      <div class="hud-claim-bar"><div class="hud-claim-fill"></div></div>
    </div>
    <div class="hud-source">
      <span>PICTURE</span>
      <span class="hud-source-value">—</span>
    </div>
  `;
}

/** A HUD bound to one root element and its own subscriptions. */
function readRunId(state: JsonValue): string | null {
  if (!state || Array.isArray(state) || typeof state !== "object") return null;
  const runId = state["runId"];
  return typeof runId === "string" ? runId : null;
}

export class HudView {
  private runId: string | null;
  private rows = new Map<string, MeterRow>();
  private rowElements = new Map<
    string,
    { fill: HTMLElement; value: HTMLElement }
  >();
  private claimValue: HTMLElement;
  private claimFill: HTMLElement;
  private sourceValue: HTMLElement;
  private modeLabel: HTMLElement;
  private modeDetail: HTMLElement;
  private dot: HTMLElement;
  private connLabel: HTMLElement;
  private statusData: StatusData = {};
  private resources: CampaignResources = {};
  private requiredSeeds = 0;
  private measuredSeeds = 0;
  private connected = false;
  private readonly disposers: (() => void)[] = [];

  constructor(
    private readonly root: HTMLElement,
    state: JsonValue = null,
  ) {
    this.runId = readRunId(state);
    this.modeLabel = this.query(".hud-mode-label");
    this.modeDetail = this.query(".hud-mode-detail");
    this.dot = this.query(".hud-connection .dot");
    this.connLabel = this.query(".hud-conn-label");
    this.claimValue = this.query(".hud-claim-value");
    this.claimFill = this.query(".hud-claim-fill");
    this.sourceValue = this.query(".hud-source-value");

    const meters = this.query(".hud-meters");
    this.addMeter(meters, "device", "DEVICE", "var(--gradient)");
    this.addMeter(meters, "memory", "MEMORY", "var(--memory)");
    this.addMeter(meters, "walltime", "WALLTIME", "var(--cpu)");
    this.addMeter(meters, "gpu", "GPU", "var(--gpu)");
    this.addMeter(meters, "cpu", "CPU", "var(--cpu)");
    this.addMeter(meters, "records", "RECORDS", "var(--promoted)");

    this.disposers.push(
      router.register("status_update", this.onStatusUpdate),
      router.register("campaign_metrics", this.onCampaignMetrics),
      runSelection.onChange(this.onRunChanged),
      wsClient.onStateChange((state) => {
        this.connected = state === "connected";
        this.updateConnection();
      }),
    );
    this.renderMeters();
  }

  update(state: JsonValue): void {
    this.runId = readRunId(state);
    this.onRunChanged(runSelection.selectedId, runSelection.selected);
  }

  dispose(): void {
    for (const dispose of this.disposers) dispose();
    this.disposers.length = 0;
    this.rows.clear();
    this.rowElements.clear();
  }

  setMeasuredSeeds(n: number): void {
    this.measuredSeeds = n;
    this.renderMeters();
  }

  private query<T extends HTMLElement>(selector: string): T {
    const el = this.root.querySelector<T>(selector);
    if (!el) throw new Error(`[HUD] missing element: ${selector}`);
    return el;
  }

  private addMeter(
    container: HTMLElement,
    key: string,
    label: string,
    color: string,
  ): void {
    const row = document.createElement("div");
    row.className = "hud-meter";
    row.innerHTML = `
      <div class="hud-meter-row">
        <span class="hud-meter-label">${label}</span>
        <span class="hud-meter-value hud-value">—</span>
      </div>
      <div class="hud-meter-bar"><div class="hud-meter-fill hud-fill" style="background: ${color};"></div></div>
    `;
    container.appendChild(row);
    this.rows.set(key, { key, label, value: "", fraction: 0, color });
    this.rowElements.set(key, {
      fill: row.querySelector<HTMLElement>(".hud-fill")!,
      value: row.querySelector<HTMLElement>(".hud-value")!,
    });
  }

  private onStatusUpdate = (data: StatusData): void => {
    this.statusData = data;
    this.renderMeters();
  };

  private onCampaignMetrics = (data: CampaignResources): void => {
    this.resources = data;
    this.renderMeters();
  };

  private onRunChanged = (
    _runId: string | null,
    metrics: RunMetrics | null,
  ): void => {
    if (!metrics) return;
    const runId = metrics.run?.run_id ?? null;
    if (this.runId && runId !== this.runId) return;
    this.requiredSeeds = metrics.required_seeds ?? 0;
    this.updateModeChip(metrics.run);
    this.updateSource(metrics);
  };

  private updateModeChip(run: RunStatus | undefined): void {
    const mode = run?.mode ?? "NO RUN";
    const color =
      mode === "PREREGISTERED"
        ? PALETTE.promoted
        : mode === "EXPLORATORY"
          ? PALETTE.insufficient
          : PALETTE.text_muted;
    this.modeLabel.textContent = mode;
    this.modeLabel.style.background = color + "22";
    this.modeLabel.style.borderColor = color + "88";
    this.modeLabel.style.color = color;
    this.modeDetail.textContent = run?.profile
      ? `${run.profile} · ${run.fidelity}`
      : "";
  }

  private updateSource(metrics: RunMetrics): void {
    const store = metrics.store;
    if (store?.source && store?.published_at) {
      const t = new Date(store.published_at).toLocaleTimeString();
      this.sourceValue.textContent = `${store.source} @ ${t}`;
    } else {
      this.sourceValue.textContent = "—";
    }
  }

  private updateConnection(): void {
    this.dot.style.background = this.connected
      ? "var(--ok)"
      : "var(--error)";
    this.connLabel.textContent = this.connected ? "Connected" : "Disconnected";
  }

  private renderMeters(): void {
    const {
      running_campaigns,
      queued_campaigns,
      used_gpus,
      max_gpus,
      used_cpus,
      max_cpus,
      used_memory_gb,
      max_memory_gb,
    } = this.statusData;
    const { device, memory_mb, walltime_s, records } = this.resources;

    this.setMeter("device", device ?? "—");
    this.setMeter(
      "memory",
      memory_mb
        ? `${(memory_mb / 1024).toFixed(1)} GB`
        : max_memory_gb
          ? `${used_memory_gb ?? 0}/${max_memory_gb} GB`
          : "—",
      max_memory_gb ? (used_memory_gb ?? 0) / max_memory_gb : 0,
    );
    this.setMeter(
      "walltime",
      walltime_s ? `${(walltime_s / 60).toFixed(1)} min` : "—",
    );
    this.setMeter(
      "gpu",
      used_gpus && max_gpus ? `${used_gpus}/${max_gpus}` : "—",
      max_gpus ? (used_gpus ?? 0) / max_gpus : 0,
    );
    this.setMeter(
      "cpu",
      used_cpus && max_cpus ? `${used_cpus}/${max_cpus}` : "—",
      max_cpus ? (used_cpus ?? 0) / max_cpus : 0,
    );
    this.setMeter(
      "records",
      records
        ? String(records)
        : running_campaigns
          ? `${running_campaigns} running, ${queued_campaigns} queued`
          : "—",
    );

    const missing =
      this.requiredSeeds > 0
        ? Math.max(0, this.requiredSeeds - this.measuredSeeds)
        : 0;
    this.claimValue.textContent =
      this.requiredSeeds > 0 ? `${missing} / ${this.requiredSeeds}` : "—";
    this.claimFill.style.width =
      this.requiredSeeds > 0
        ? `${Math.min(100, (1 - missing / this.requiredSeeds) * 100)}%`
        : "0%";
  }

  private setMeter(key: string, value: string, fraction = 0): void {
    const row = this.rows.get(key);
    const el = this.rowElements.get(key);
    if (!row || !el) return;
    row.value = value;
    row.fraction = fraction;
    el.value.textContent = value;
    el.fill.style.width = `${fraction * 100}%`;
  }
}