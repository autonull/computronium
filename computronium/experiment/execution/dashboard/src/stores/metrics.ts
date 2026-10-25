/** MetricsStore — shared cache for campaign metrics (TODO72 P4).

One fetch per run_id; multiple subscribers per run. Deduplicates in-flight
promises by key so simultaneous components don't trigger parallel fetches.
*/

import { router } from "../ws-client.js";
import { runSelection } from "../run-selection.js";

export interface RunMetrics {
  records?: any[];
  pareto?: boolean[];
  ablation_groups?: any[];
  chance?: number;
  required_seeds?: number;
  gate?: any;
  resources?: Record<string, number | string | undefined>;
  store?: { source?: string; published_at?: string };
  run?: any;
}

interface CacheEntry {
  data: RunMetrics | null;
  promise: Promise<RunMetrics | null> | null;
  listeners: Set<() => void>;
}

export class MetricsStore {
  private cache = new Map<string, CacheEntry>();
  private wsUnsubscribe: (() => void) | null = null;
  private runsSummaryUnsubscribe: (() => void) | null = null;
  private runsSummary: any[] = [];

  constructor() {
    // Single ingestion point for campaign_metrics from WebSocket
    this.wsUnsubscribe = router.register("campaign_metrics", (data: any) => {
      const { campaign_id, data: metricsData } = data;
      if (!campaign_id || !metricsData) return;
      this.setMetrics(campaign_id, metricsData);
    });

    // Keep runSelection in sync for backward compatibility (legacy components)
    // The store is the source of truth; runSelection mirrors for old listeners.
    this.wsUnsubscribe = router.register("campaign_metrics", (data: any) => {
      const { campaign_id, data: metricsData } = data;
      if (!campaign_id || !metricsData) return;
      runSelection.observe(campaign_id, metricsData);
    });
  }

  /** Get metrics for a run, fetching if needed. Returns cached data immediately if available. */
  get(runId: string): RunMetrics | null {
    const entry = this.cache.get(runId);
    return entry?.data ?? null;
  }

  /** Subscribe to metrics changes for a run. Returns unsubscribe function. */
  subscribe(runId: string, listener: () => void): () => void {
    let entry = this.cache.get(runId);
    if (!entry) {
      entry = { data: null, promise: null, listeners: new Set() };
      this.cache.set(runId, entry);
    }
    entry.listeners.add(listener);
    // Trigger fetch if we don't have data yet
    if (!entry.data && !entry.promise) {
      void this.fetch(runId);
    }
    return () => {
      entry!.listeners.delete(listener);
      if (entry!.listeners.size === 0 && !entry!.promise) {
        // Optionally clean up empty entries
      }
    };
  }

  /** Set metrics directly (from WebSocket push). */
  setMetrics(runId: string, metrics: RunMetrics): void {
    let entry = this.cache.get(runId);
    if (!entry) {
      entry = { data: null, promise: null, listeners: new Set() };
      this.cache.set(runId, entry);
    }
    entry.data = metrics;
    entry.promise = null;
    entry.listeners.forEach((listener) => listener());
  }

  /** Fetch metrics from the server, deduplicating in-flight requests. */
  private async fetch(runId: string): Promise<RunMetrics | null> {
    let entry = this.cache.get(runId);
    if (!entry) {
      entry = { data: null, promise: null, listeners: new Set() };
      this.cache.set(runId, entry);
    }
    if (entry.promise) {
      return entry.promise;
    }
    entry.promise = this.doFetch(runId);
    try {
      const data = await entry.promise;
      entry.data = data;
      entry.promise = null;
      entry.listeners.forEach((listener) => listener());
      return data;
    } catch (error) {
      entry.promise = null;
      console.warn(`[MetricsStore] Fetch failed for ${runId}:`, error);
      return null;
    }
  }

  private async doFetch(runId: string): Promise<RunMetrics | null> {
    try {
      const response = await fetch(
        `/api/campaigns/${encodeURIComponent(runId)}/metrics`,
      );
      if (!response.ok) {
        console.warn(`[MetricsStore] Metrics refused for ${runId}: ${response.status}`);
        return null;
      }
      return (await response.json()) as RunMetrics;
    } catch (error) {
      console.warn(`[MetricsStore] Metrics could not be read for ${runId}:`, error);
      return null;
    }
  }

  /** Get the lightweight runs summary (catalog). */
  getRunsSummary(): any[] {
    return this.runsSummary;
  }

  /** Subscribe to runs summary changes. Returns unsubscribe function. */
  subscribeRunsSummary(listener: () => void): () => void {
    if (!this.runsSummaryUnsubscribe) {
      this.runsSummaryUnsubscribe = router.register("runs_summary", (data: any) => {
        if (data?.runs) {
          this.runsSummary = data.runs;
          this.runsSummaryListeners.forEach((l) => l());
        }
      });
      // Request initial summary
      void this.fetchRunsSummary();
    }
    this.runsSummaryListeners.add(listener);
    return () => {
      this.runsSummaryListeners.delete(listener);
    };
  }

  private runsSummaryListeners = new Set<() => void>();

  private async fetchRunsSummary(): Promise<void> {
    try {
      const response = await fetch("/api/runs/summary");
      if (!response.ok) return;
      const data = await response.json();
      if (data?.runs) {
        this.runsSummary = data.runs;
        this.runsSummaryListeners.forEach((l) => l());
      }
    } catch (error) {
      console.warn("[MetricsStore] Runs summary could not be read:", error);
    }
  }

  /** Request fresh runs summary from server (call after catalog changes). */
  async refreshRunsSummary(): Promise<void> {
    await this.fetchRunsSummary();
  }

  dispose(): void {
    this.wsUnsubscribe?.();
    this.runsSummaryUnsubscribe?.();
    this.cache.clear();
    this.runsSummary = [];
    this.runsSummaryListeners.clear();
  }
}

export const metricsStore = new MetricsStore();