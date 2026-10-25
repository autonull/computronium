/** The stage's sources — the eight `sync*` fetchers (TODO71 Phase 5).
 *
 *  These are the only code that knows how to ask the server. The store
 *  calls them, writes their results into its state, and notifies listeners.
 *  Views never import them; they only read from the store.
 */

import { AXIS_NAMES, type AxisName } from "../cell-data.js";
import { type GateThresholds, type RunMetrics } from "../run-selection.js";
import { router } from "../ws-client.js";
export type {
  CellDynamics,
  MultiRunSpace,
  RunAccount,
  RunAttribution,
  RunFlow,
  RunTimeline,
  SpacePayload,
} from "./payloads.js";

import {
  type CellDynamics,
  type MultiRunSpace,
  type RunAccount,
  type RunAttribution,
  type RunFlow,
  type RunTimeline,
  type SpacePayload,
  indexSpaceCells,
  measuredValues,
} from "./payloads.js";

/** The declared space, from the server. */
export async function fetchSpace(
  runId: string,
  axes: AxisSelection,
  values: Record<AxisName, string[]>,
): Promise<SpacePayload | null> {
  try {
    const response = await fetch(`/api/cells/${runId}/space`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ axes: [axes.x, axes.y, axes.z] }),
    });
    if (!response.ok) {
      console.warn("[StageState] The space was refused", response.status);
      return null;
    }
    return (await response.json()) as SpacePayload;
  } catch (error) {
    console.warn("[StageState] The space could not be read", error);
    return null;
  }
}

/** The run's account: what it can say, and how its arms compare. */
export async function fetchAccount(
  runId: string,
  measured: number,
): Promise<RunAccount | null> {
  try {
    const response = await fetch(
      `/api/runs/${encodeURIComponent(runId)}/account`,
    );
    if (!response.ok) {
      console.warn("[StageState] The account was refused", response.status);
      return null;
    }
    return (await response.json()) as RunAccount;
  } catch (error) {
    console.warn("[StageState] The account could not be read", error);
    return null;
  }
}

/** The run's stages, as they happened. */
export async function fetchTimeline(
  runId: string,
): Promise<RunTimeline | null> {
  try {
    const response = await fetch(
      `/api/events?run_id=${encodeURIComponent(runId)}`,
    );
    if (!response.ok) {
      console.warn("[StageState] The timeline was refused", response.status);
      return null;
    }
    return (await response.json()) as RunTimeline;
  } catch (error) {
    console.warn("[StageState] The timeline could not be read", error);
    return null;
  }
}

/** The run's cells, from the space to the evidence. */
export async function fetchFlow(runId: string): Promise<RunFlow | null> {
  try {
    const response = await fetch(`/api/runs/${encodeURIComponent(runId)}/flow`);
    if (!response.ok) {
      console.warn("[StageState] The flow was refused", response.status);
      return null;
    }
    return (await response.json()) as RunFlow;
  } catch (error) {
    console.warn("[StageState] The flow could not be read", error);
    return null;
  }
}

/** What the run can attribute, and what its design cannot say. */
export async function fetchAttribution(
  runId: string,
  measured: number,
): Promise<RunAttribution | null> {
  try {
    const response = await fetch(
      `/api/runs/${encodeURIComponent(runId)}/attribution`,
    );
    if (!response.ok) {
      console.warn("[StageState] The attribution was refused", response.status);
      return null;
    }
    return (await response.json()) as RunAttribution;
  } catch (error) {
    console.warn("[StageState] The attribution could not be read", error);
    return null;
  }
}

/** The cell's own dynamics, measured on the server. */
export async function fetchDynamics(
  runId: string,
): Promise<CellDynamics | null> {
  try {
    const response = await fetch(
      `/api/runs/${encodeURIComponent(runId)}/dynamics`,
    );
    if (!response.ok) {
      console.warn("[StageState] The dynamics were refused", response.status);
      return null;
    }
    return (await response.json()) as CellDynamics;
  } catch (error) {
    console.warn("[StageState] The dynamics could not be read", error);
    return null;
  }
}

/** The cell's own dynamics after training, measured on the server. */
export async function fetchTrainedDynamics(
  runId: string,
): Promise<CellDynamics | null> {
  try {
    const response = await fetch(
      `/api/runs/${encodeURIComponent(runId)}/dynamics/trained`,
    );
    if (!response.ok) {
      console.warn(
        "[StageState] The trained dynamics were refused",
        response.status,
      );
      return null;
    }
    return (await response.json()) as CellDynamics;
  } catch (error) {
    console.warn("[StageState] The trained dynamics could not be read", error);
    return null;
  }
}

/** Several runs' evidence in one space. */
export async function fetchMultirun(
  axes: AxisSelection,
): Promise<MultiRunSpace | null> {
  try {
    const response = await fetch("/api/spaces", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ axes: [axes.x, axes.y, axes.z] }),
    });
    if (!response.ok) {
      console.warn("[StageState] The runs' space was refused", response.status);
      return null;
    }
    return (await response.json()) as MultiRunSpace;
  } catch (error) {
    console.warn("[StageState] The runs' space could not be read", error);
    return null;
  }
}

/** A live event: the run's story has moved, so the timeline is read again. */
export function scheduleTimeline(store: {
  timelineStale: boolean;
  timelineTimer: number | null;
  syncTimeline: () => Promise<void>;
}): void {
  store.timelineStale = true;
  if (store.timelineTimer !== null) return;
  store.timelineTimer = window.setTimeout(() => {
    store.timelineTimer = null;
    void store.syncTimeline();
  }, 300);
}

/** The axes selection type (re-exported for sources). */
export type AxisSelection = {
  x: AxisName;
  y: AxisName;
  z: AxisName;
};
