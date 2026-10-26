/** MultiRunStore — shared cache for multi-run space data (TODO72 P6).
 *
 * One fetch per axes selection; multiple subscribers per key.
 * Deduplicates in-flight promises so simultaneous views don't trigger parallel fetches.
 */

import { fetchMultirun, type MultiRunSpace } from "./sources.js";
import type { AxisSelection } from "../layout/types.js";
import { AXIS_NAMES } from "../cell-data.js";

type MultiRunKey = string; // "x|y|z"

interface CacheEntry {
  data: MultiRunSpace | null;
  promise: Promise<MultiRunSpace | null> | null;
  listeners: Set<() => void>;
}

export class MultiRunStore {
  private cache = new Map<MultiRunKey, CacheEntry>();

  constructor() {}

  /** Build a cache key from the request parameters. */
  private makeKey(axes: AxisSelection): MultiRunKey {
    return `${axes.x}|${axes.y}|${axes.z}`;
  }

  /** Get multirun space for axes, returning cached data immediately if available. */
  get(axes: AxisSelection): MultiRunSpace | null {
    const key = this.makeKey(axes);
    const entry = this.cache.get(key);
    return entry?.data ?? null;
  }

  /** Subscribe to multirun space changes for axes. Returns unsubscribe function. */
  subscribe(axes: AxisSelection, listener: () => void): () => void {
    const key = this.makeKey(axes);
    let entry = this.cache.get(key);
    if (!entry) {
      entry = { data: null, promise: null, listeners: new Set() };
      this.cache.set(key, entry);
    }
    entry.listeners.add(listener);
    if (!entry.data && !entry.promise) {
      void this.fetch(axes);
    }
    return () => {
      entry!.listeners.delete(listener);
    };
  }

  /** Set multirun space directly. */
  set(axes: AxisSelection, payload: MultiRunSpace): void {
    const key = this.makeKey(axes);
    let entry = this.cache.get(key);
    if (!entry) {
      entry = { data: null, promise: null, listeners: new Set() };
      this.cache.set(key, entry);
    }
    entry.data = payload;
    entry.promise = null;
    entry.listeners.forEach((listener) => listener());
  }

  /** Fetch multirun space from the server, deduplicating in-flight requests. */
  private async fetch(axes: AxisSelection): Promise<MultiRunSpace | null> {
    const key = this.makeKey(axes);
    let entry = this.cache.get(key);
    if (!entry) {
      entry = { data: null, promise: null, listeners: new Set() };
      this.cache.set(key, entry);
    }
    if (entry.promise) {
      return entry.promise;
    }
    entry.promise = this.doFetch(axes);
    try {
      const data = await entry.promise;
      entry.data = data;
      entry.promise = null;
      entry.listeners.forEach((listener) => listener());
      return data;
    } catch (error) {
      entry.promise = null;
      console.warn(`[MultiRunStore] Fetch failed for ${key}:`, error);
      return null;
    }
  }

  private async doFetch(axes: AxisSelection): Promise<MultiRunSpace | null> {
    return fetchMultirun(axes);
  }

  /** Clear the cache (e.g., on disconnect). */
  clear(): void {
    this.cache.clear();
  }

  dispose(): void {
    this.cache.clear();
  }
}

export const multiRunStore = new MultiRunStore();