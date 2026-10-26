/** AttributionStore — shared cache for run attribution data (TODO72 P6).
 *
 * One fetch per (runId, measured) key; multiple subscribers per key.
 * Deduplicates in-flight promises so simultaneous views don't trigger parallel fetches.
 */

import { fetchAttribution, type RunAttribution } from "./sources.js";

type AttributionKey = string; // "runId|measured"

interface CacheEntry {
  data: RunAttribution | null;
  promise: Promise<RunAttribution | null> | null;
  listeners: Set<() => void>;
}

export class AttributionStore {
  private cache = new Map<AttributionKey, CacheEntry>();

  constructor() {}

  /** Build a cache key from the request parameters. */
  private makeKey(runId: string, measured: number): AttributionKey {
    return `${runId}|${measured}`;
  }

  /** Get attribution for a key, returning cached data immediately if available. */
  get(runId: string, measured: number): RunAttribution | null {
    const key = this.makeKey(runId, measured);
    const entry = this.cache.get(key);
    return entry?.data ?? null;
  }

  /** Subscribe to attribution changes for a key. Returns unsubscribe function. */
  subscribe(runId: string, measured: number, listener: () => void): () => void {
    const key = this.makeKey(runId, measured);
    let entry = this.cache.get(key);
    if (!entry) {
      entry = { data: null, promise: null, listeners: new Set() };
      this.cache.set(key, entry);
    }
    entry.listeners.add(listener);
    if (!entry.data && !entry.promise) {
      void this.fetch(runId, measured);
    }
    return () => {
      entry!.listeners.delete(listener);
    };
  }

  /** Set attribution directly (e.g., from WebSocket push if we add one). */
  set(runId: string, measured: number, payload: RunAttribution): void {
    const key = this.makeKey(runId, measured);
    let entry = this.cache.get(key);
    if (!entry) {
      entry = { data: null, promise: null, listeners: new Set() };
      this.cache.set(key, entry);
    }
    entry.data = payload;
    entry.promise = null;
    entry.listeners.forEach((listener) => listener());
  }

  /** Fetch attribution from the server, deduplicating in-flight requests. */
  private async fetch(
    runId: string,
    measured: number,
  ): Promise<RunAttribution | null> {
    const key = this.makeKey(runId, measured);
    let entry = this.cache.get(key);
    if (!entry) {
      entry = { data: null, promise: null, listeners: new Set() };
      this.cache.set(key, entry);
    }
    if (entry.promise) {
      return entry.promise;
    }
    entry.promise = this.doFetch(runId, measured);
    try {
      const data = await entry.promise;
      entry.data = data;
      entry.promise = null;
      entry.listeners.forEach((listener) => listener());
      return data;
    } catch (error) {
      entry.promise = null;
      console.warn(`[AttributionStore] Fetch failed for ${key}:`, error);
      return null;
    }
  }

  private async doFetch(runId: string, measured: number): Promise<RunAttribution | null> {
    return fetchAttribution(runId, measured);
  }

  /** Clear the cache (e.g., on disconnect). */
  clear(): void {
    this.cache.clear();
  }

  dispose(): void {
    this.cache.clear();
  }
}

export const attributionStore = new AttributionStore();