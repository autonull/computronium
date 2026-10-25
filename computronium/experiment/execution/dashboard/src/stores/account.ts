/** AccountStore — shared cache for run account data (TODO72 P6).
 *
 * One fetch per (runId, measured) key; multiple subscribers per key.
 * Deduplicates in-flight promises so simultaneous views don't trigger parallel fetches.
 */

import { fetchAccount, type RunAccount } from "../stage/sources.js";

type AccountKey = string; // "runId|measured"

interface CacheEntry {
  data: RunAccount | null;
  promise: Promise<RunAccount | null> | null;
  listeners: Set<() => void>;
}

export class AccountStore {
  private cache = new Map<AccountKey, CacheEntry>();

  constructor() {}

  /** Build a cache key from the request parameters. */
  private makeKey(runId: string, measured: number): AccountKey {
    return `${runId}|${measured}`;
  }

  /** Get account for a key, returning cached data immediately if available. */
  get(runId: string, measured: number): RunAccount | null {
    const key = this.makeKey(runId, measured);
    const entry = this.cache.get(key);
    return entry?.data ?? null;
  }

  /** Subscribe to account changes for a key. Returns unsubscribe function. */
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

  /** Set account directly (e.g., from WebSocket push if we add one). */
  set(runId: string, measured: number, payload: RunAccount): void {
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

  /** Fetch account from the server, deduplicating in-flight requests. */
  private async fetch(
    runId: string,
    measured: number,
  ): Promise<RunAccount | null> {
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
      console.warn(`[AccountStore] Fetch failed for ${key}:`, error);
      return null;
    }
  }

  private async doFetch(runId: string, measured: number): Promise<RunAccount | null> {
    return fetchAccount(runId, measured);
  }

  /** Clear the cache (e.g., on disconnect). */
  clear(): void {
    this.cache.clear();
  }

  dispose(): void {
    this.cache.clear();
  }
}

export const accountStore = new AccountStore();