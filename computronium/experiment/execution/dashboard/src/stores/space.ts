/** SpaceStore — shared cache for space payloads (TODO72 P4).

One fetch per (runId, axes, values) key; multiple subscribers per key.
Deduplicates in-flight promises so simultaneous views don't trigger parallel fetches.
*/

import { AXIS_NAMES, type AxisName } from "../cell-data.js";
import type { AxisSelection } from "../stage/payloads.js";

export interface SpacePayload {
  cells: any[];
  axes: { x: AxisName; y: AxisName; z: AxisName };
  values: Record<AxisName, string[]>;
}

type SpaceKey = string; // "runId|x|y|z|values..."

interface CacheEntry {
  data: SpacePayload | null;
  promise: Promise<SpacePayload | null> | null;
  listeners: Set<() => void>;
}

export class SpaceStore {
  private cache = new Map<SpaceKey, CacheEntry>();

  constructor() {}

  /** Build a cache key from the request parameters. */
  private makeKey(
    runId: string,
    axes: AxisSelection,
    values: Record<AxisName, string[]>,
  ): SpaceKey {
    const valueStr = AXIS_NAMES.map((axis) => values[axis].join(",")).join("|");
    return `${runId}|${axes.x}|${axes.y}|${axes.z}|${valueStr}`;
  }

  /** Get space payload for a key, returning cached data immediately if available. */
  get(runId: string, axes: AxisSelection, values: Record<AxisName, string[]>): SpacePayload | null {
    const key = this.makeKey(runId, axes, values);
    const entry = this.cache.get(key);
    return entry?.data ?? null;
  }

  /** Subscribe to space payload changes for a key. Returns unsubscribe function. */
  subscribe(
    runId: string,
    axes: AxisSelection,
    values: Record<AxisName, string[]>,
    listener: () => void,
  ): () => void {
    const key = this.makeKey(runId, axes, values);
    let entry = this.cache.get(key);
    if (!entry) {
      entry = { data: null, promise: null, listeners: new Set() };
      this.cache.set(key, entry);
    }
    entry.listeners.add(listener);
    // Trigger fetch if we don't have data yet
    if (!entry.data && !entry.promise) {
      void this.fetch(runId, axes, values);
    }
    return () => {
      entry!.listeners.delete(listener);
    };
  }

  /** Set space payload directly (e.g., from WebSocket push if we add one). */
  set(runId: string, axes: AxisSelection, values: Record<AxisName, string[]>, payload: SpacePayload): void {
    const key = this.makeKey(runId, axes, values);
    let entry = this.cache.get(key);
    if (!entry) {
      entry = { data: null, promise: null, listeners: new Set() };
      this.cache.set(key, entry);
    }
    entry.data = payload;
    entry.promise = null;
    entry.listeners.forEach((listener) => listener());
  }

  /** Fetch space payload from the server, deduplicating in-flight requests. */
  private async fetch(
    runId: string,
    axes: AxisSelection,
    values: Record<AxisName, string[]>,
  ): Promise<SpacePayload | null> {
    const key = this.makeKey(runId, axes, values);
    let entry = this.cache.get(key);
    if (!entry) {
      entry = { data: null, promise: null, listeners: new Set() };
      this.cache.set(key, entry);
    }
    if (entry.promise) {
      return entry.promise;
    }
    entry.promise = this.doFetch(runId, axes, values);
    try {
      const data = await entry.promise;
      entry.data = data;
      entry.promise = null;
      entry.listeners.forEach((listener) => listener());
      return data;
    } catch (error) {
      entry.promise = null;
      console.warn(`[SpaceStore] Fetch failed for ${key}:`, error);
      return null;
    }
  }

  private async doFetch(
    runId: string,
    axes: AxisSelection,
    values: Record<AxisName, string[]>,
  ): Promise<SpacePayload | null> {
    try {
      const response = await fetch(`/api/cells/${encodeURIComponent(runId)}/space`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ axes: [axes.x, axes.y, axes.z] }),
      });
      if (!response.ok) {
        console.warn(`[SpaceStore] Space refused for ${runId}: ${response.status}`);
        return null;
      }
      return (await response.json()) as SpacePayload;
    } catch (error) {
      console.warn(`[SpaceStore] Space could not be read for ${runId}:`, error);
      return null;
    }
  }

  /** Clear the cache (e.g., on disconnect). */
  clear(): void {
    this.cache.clear();
  }

  dispose(): void {
    this.cache.clear();
  }
}

export const spaceStore = new SpaceStore();