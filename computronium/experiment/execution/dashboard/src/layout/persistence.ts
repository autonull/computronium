/** Versioned persistence for the layout envelope (TODO72 P1).
 *
 * The engine payload is opaque here. This module owns the version check, the
 * instance mirror, and the rule that an unknown component type is dropped
 * with one warning instead of breaking the whole restore.
 */

import { hasDefinition } from "./definitions.js";
import type {
  JsonValue,
  LayoutDocument,
  PanelInstanceMeta,
} from "./types.js";

export const LAYOUT_VERSION = 1;
export const LAYOUT_ENGINE = "dockview";
export const LAYOUT_STORAGE_KEY = "computronium-dashboard-layout-v1";

const warnedTypes = new Set<string>();

function isJsonValue(value: unknown): value is JsonValue {
  if (
    value === null ||
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return true;
  }
  if (Array.isArray(value)) return value.every(isJsonValue);
  if (typeof value === "object") {
    return Object.values(value).every(isJsonValue);
  }
  return false;
}

function isInstance(value: unknown): value is PanelInstanceMeta {
  if (!value || typeof value !== "object") return false;
  const instance = value as Record<string, unknown>;
  return (
    typeof instance.id === "string" &&
    typeof instance.type === "string" &&
    typeof instance.title === "string" &&
    isJsonValue(instance.state)
  );
}

export function isLayoutDocument(value: unknown): value is LayoutDocument {
  if (!value || typeof value !== "object") return false;
  const doc = value as Record<string, unknown>;
  return (
    doc.version === LAYOUT_VERSION &&
    doc.engine === LAYOUT_ENGINE &&
    typeof doc.engineVersion === "number" &&
    isJsonValue(doc.data) &&
    Array.isArray(doc.instances) &&
    doc.instances.every(isInstance)
  );
}

/** Drop mirror rows for component types this build does not define. */
export function sanitizeDocument(doc: LayoutDocument): LayoutDocument {
  const instances = doc.instances.filter((instance) => {
    if (hasDefinition(instance.type)) return true;
    if (!warnedTypes.has(instance.type)) {
      warnedTypes.add(instance.type);
      console.warn(`[layout] dropping unknown component type: ${instance.type}`);
    }
    return false;
  });
  return { ...doc, instances };
}

export function serializeDocument(doc: LayoutDocument): string {
  return JSON.stringify(doc);
}

export function parseDocument(raw: string): LayoutDocument | null {
  try {
    const value: unknown = JSON.parse(raw);
    if (!isLayoutDocument(value)) {
      console.warn("[layout] stored layout failed validation; using preset");
      return null;
    }
    return sanitizeDocument(value);
  } catch (error) {
    console.warn("[layout] stored layout is not JSON; using preset", error);
    return null;
  }
}

export function saveDocument(
  storage: Storage,
  doc: LayoutDocument,
  key = LAYOUT_STORAGE_KEY,
): void {
  storage.setItem(key, serializeDocument(doc));
}

export function loadDocument(
  storage: Storage,
  key = LAYOUT_STORAGE_KEY,
): LayoutDocument | null {
  const raw = storage.getItem(key);
  return raw ? parseDocument(raw) : null;
}
