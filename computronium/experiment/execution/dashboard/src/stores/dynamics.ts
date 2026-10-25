/** DynamicsStore — shared cache for cell dynamics data (TODO72 P6).
 *
 * One fetch per runId for dynamics; trained dynamics are separate.
 * Deduplicates in-flight promises so simultaneous views don't trigger parallel fetches.
 */

import { fetchDynamics, fetchTrainedDynamics, type CellDynamics } from "../stage/sources.js";

type DynamicsKey = string; // "runId" or "runId|trained"

interface CacheEntry {
  data: CellDynamics | null;
  promise: Promise<CellDynamics | null> | null;
  listeners: Set<() => void>;
}

export class DynamicsStore {
  private cache = new Map<DynamicsKey, CacheEntry>();

  constructor() {}

  /** Build a cache key from the request parameters. */
  private makeKey(runId: string, trained: boolean): DynamicsKey {
    return trained ? `${runId}|trained` : runId;
  }

  /** Get dynamics for a run, returning cached data immediately if available. */
  get(runId: string, trained: boolean): CellDynamics | null {
    const key = this.makeKey(runId, trained);
    const entry = this.cache.get(key);
    return entry?.data ?? null;
  }

  /** Subscribe to dynamics changes for a run. Returns unsubscribe function. */
  subscribe(runId: string, trained: boolean, listener: () => void): () => void {
    const key = this.makeKey(runId, trained);
    let entry = this.cache.get(key);
    if (!entry) {
      entry = { data: null, promise: null, listeners: new Set() };
      this.cache.set(key, entry);
    }
    entry.listeners.add(listener);
    if (!entry.data && !entry.promise) {
      void this.fetch(runId, trained);
    }
    return () => {
      entry!.listeners.delete(listener);
    };
  }

  /** Set dynamics directly (e.g., from WebSocket push if we add one). */
  set(runId: string, trained: boolean, payload: CellDynamics): void {
    const key = this.makeKey(runId, trained);
    let entry = this.cache.get(key);
    if (!entry) {
      entry = { data: null, promise: null, listeners: new Set() };
      this.cache.set(key, entry);
    }
    entry.data = payload;
    entry.promise = null;
    entry.listeners.forEach((listener) => listener());
  }

  /** Fetch dynamics from the server, deduplicating in-flight requests. */
  private async fetch(
    runId: string,
    trained: boolean,
  ): Promise<CellDynamics | null> {
    const key = this.makeKey(runId, trained);
    let entry = this.cache.get(key);
    if (!entry) {
      entry = { data: null, promise: null, listeners: new Set() };
      this.cache.set(key, entry);
    }
    if (entry.promise) {
      return entry.promise;
    }
    entry.promise = this.doFetch(runId, trained);
    try {
      const data = await entry.promise;
      entry.data = data;
      entry.promise = null;
      entry.listeners.forEach((listener) => listener());
      return data;
    } catch (error) {
      entry.promise = null;
      console.warn(`[DynamicsStore] Fetch failed for ${key}:`, error);
      return null;
    }
  }

  private async doFetch(runId: string, trained: boolean): Promise<CellDynamics | null> {
    return trained ? fetchTrainedDynamics(runId) : fetchDynamics(runId);
  }

  /** Clear the cache (e.g., on disconnect). */
  clear(): void {
    this.cache.clear();
  }

  dispose(): void {
    this.cache.clear();
  }
}

export const dynamicsStore = new DynamicsStore();