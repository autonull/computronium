/** TimelineStore — shared cache for run timeline and flow data (TODO72 P6).
 *
 * One fetch per runId for timeline; flow depends on timeline events count.
 * Deduplicates in-flight promises so simultaneous views don't trigger parallel fetches.
 */

import { fetchTimeline, fetchFlow, type RunTimeline, type RunFlow } from "./sources.js";

type TimelineKey = string; // "runId"
type FlowKey = string; // "runId|events"

interface CacheEntry<T> {
  data: T | null;
  promise: Promise<T | null> | null;
  listeners: Set<() => void>;
}

export class TimelineStore {
  private timelineCache = new Map<TimelineKey, CacheEntry<RunTimeline>>();
  private flowCache = new Map<FlowKey, CacheEntry<RunFlow>>();

  constructor() {}

  // Timeline methods

  /** Get timeline for a run, returning cached data immediately if available. */
  getTimeline(runId: string): RunTimeline | null {
    const entry = this.timelineCache.get(runId);
    return entry?.data ?? null;
  }

  /** Subscribe to timeline changes for a run. Returns unsubscribe function. */
  subscribeTimeline(runId: string, listener: () => void): () => void {
    let entry = this.timelineCache.get(runId);
    if (!entry) {
      entry = { data: null, promise: null, listeners: new Set() };
      this.timelineCache.set(runId, entry);
    }
    entry.listeners.add(listener);
    if (!entry.data && !entry.promise) {
      void this.fetchTimeline(runId);
    }
    return () => {
      entry!.listeners.delete(listener);
    };
  }

  /** Set timeline directly (e.g., from WebSocket push if we add one). */
  setTimeline(runId: string, payload: RunTimeline): void {
    let entry = this.timelineCache.get(runId);
    if (!entry) {
      entry = { data: null, promise: null, listeners: new Set() };
      this.timelineCache.set(runId, entry);
    }
    entry.data = payload;
    entry.promise = null;
    entry.listeners.forEach((listener) => listener());
  }

  /** Fetch timeline from the server, deduplicating in-flight requests. */
  private async fetchTimeline(runId: string): Promise<RunTimeline | null> {
    let entry = this.timelineCache.get(runId);
    if (!entry) {
      entry = { data: null, promise: null, listeners: new Set() };
      this.timelineCache.set(runId, entry);
    }
    if (entry.promise) {
      return entry.promise;
    }
    entry.promise = this.doFetchTimeline(runId);
    try {
      const data = await entry.promise;
      entry.data = data;
      entry.promise = null;
      entry.listeners.forEach((listener) => listener());
      return data;
    } catch (error) {
      entry.promise = null;
      console.warn(`[TimelineStore] Timeline fetch failed for ${runId}:`, error);
      return null;
    }
  }

  private async doFetchTimeline(runId: string): Promise<RunTimeline | null> {
    return fetchTimeline(runId);
  }

  // Flow methods

  /** Get flow for a run, returning cached data immediately if available. */
  getFlow(runId: string, events: number): RunFlow | null {
    const key = `${runId}|${events}`;
    const entry = this.flowCache.get(key);
    return entry?.data ?? null;
  }

  /** Subscribe to flow changes for a run. Returns unsubscribe function. */
  subscribeFlow(runId: string, events: number, listener: () => void): () => void {
    const key = `${runId}|${events}`;
    let entry = this.flowCache.get(key);
    if (!entry) {
      entry = { data: null, promise: null, listeners: new Set() };
      this.flowCache.set(key, entry);
    }
    entry.listeners.add(listener);
    if (!entry.data && !entry.promise) {
      void this.fetchFlow(runId);
    }
    return () => {
      entry!.listeners.delete(listener);
    };
  }

  /** Set flow directly. */
  setFlow(runId: string, events: number, payload: RunFlow): void {
    const key = `${runId}|${events}`;
    let entry = this.flowCache.get(key);
    if (!entry) {
      entry = { data: null, promise: null, listeners: new Set() };
      this.flowCache.set(key, entry);
    }
    entry.data = payload;
    entry.promise = null;
    entry.listeners.forEach((listener) => listener());
  }

  /** Fetch flow from the server, deduplicating in-flight requests. */
  private async fetchFlow(runId: string): Promise<RunFlow | null> {
    const key = `${runId}|0`; // will be updated after timeline loads
    let entry = this.flowCache.get(key);
    if (!entry) {
      entry = { data: null, promise: null, listeners: new Set() };
      this.flowCache.set(key, entry);
    }
    if (entry.promise) {
      return entry.promise;
    }
    entry.promise = this.doFetchFlow(runId);
    try {
      const data = await entry.promise;
      entry.data = data;
      entry.promise = null;
      entry.listeners.forEach((listener) => listener());
      return data;
    } catch (error) {
      entry.promise = null;
      console.warn(`[TimelineStore] Flow fetch failed for ${runId}:`, error);
      return null;
    }
  }

  private async doFetchFlow(runId: string): Promise<RunFlow | null> {
    return fetchFlow(runId);
  }

  /** Clear the cache (e.g., on disconnect). */
  clear(): void {
    this.timelineCache.clear();
    this.flowCache.clear();
  }

  dispose(): void {
    this.clear();
  }
}

export const timelineStore = new TimelineStore();