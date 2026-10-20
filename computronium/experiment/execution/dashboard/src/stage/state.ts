/** The state the stage shares (TODO69 Phase 5).

    The main view area is a stage, and every view that stands on it reads the
    same picture: the run the dashboard shows, the axes the reader picked, the
    space the backend declares and the records the run measured. The state
    holds those once, so the map, the terrain, the frontier and the charts
    cannot disagree about what the run found.

    The space is asked for again only when it could have changed: a new run, a
    new set of axes, or a new value measured on one of them.
*/

import {
  AXIS_NAMES,
  type AxisName,
  type CellCoordinate,
  type CurvePoint,
  type SpaceCell,
  type SpacePayload,
} from "../cell-data.js";
import {
  runSelection,
  type GateThresholds,
  type RunMetrics,
} from "../run-selection.js";
import { router } from "../ws-client.js";

/** The three axes the stage shows, and the three it holds. */
export interface AxisSelection {
  x: AxisName;
  y: AxisName;
  z: AxisName;
}

/** One thing that happened, as the dashboard saw it. */
export interface StageEvent {
  stage: string;
  message: string;
  level: string;
  sentence: string;
  at: number;
}

/** One stage of the run, and the time it took. */
export interface StageSpan {
  stage: string;
  action: string;
  events: number;
  first: number;
  last: number;
  offset: number;
  duration: number;
}

/** The run's stages, as they happened. */
export interface RunTimeline {
  run_id: string | null;
  start: number;
  seconds: number;
  events: StageEvent[];
  stages: StageSpan[];
}

/** One arm of the run, with its evidence and the gate's standing on it. */
export interface LedgerArm {
  axis: string;
  value: string;
  mean: number;
  sd: number;
  n: number;
  cells: number;
  verdict: string;
}

/** An axis that did not vary: one value, and the whole run behind it. */
export interface FixedAxis {
  axis: string;
  value: string;
  mean: number;
  n: number;
  cells: number;
}

/** What the run can say. */
export interface Ledger {
  run_id: string;
  metric: string;
  claims: LedgerArm[];
  fixed: FixedAxis[];
  /** How many arms stand each way: the ledger's headline. */
  standings: Record<string, number>;
  limitations: { kind: string; detail: string; count: number }[];
  significance: string;
  min_seeds: number;
  chance: number | null;
}

/** One arm, as the contrast sees it. */
export interface ContrastArm {
  value: string;
  mean: number;
  sd: number;
  n: number;
  cells: number;
}

/** One pair of arms, and what separates them. */
export interface ContrastPair {
  a: string;
  b: string;
  difference: number | null;
  shared_cells: number;
}

/** The test the run could or could not run. */
export interface ContrastTest {
  tested: boolean;
  significant: boolean;
  p_value: number | null;
  ci_lower: number | null;
  ci_upper: number | null;
  cohens_dz: number | null;
  mean_diff: number | null;
  shared_cells: number;
  required_cells: number;
  alpha: number;
}

/** The run's arms against one another. */
export interface Contrast {
  run_id: string;
  axis: string;
  metric: string;
  arms: ContrastArm[];
  pairs: ContrastPair[];
  test: ContrastTest;
}

/** The run's account of itself: what it can say, and how it compares. */
export interface RunAccount {
  run_id: string;
  ledger: Ledger;
  contrast: Contrast;
}

/** One stage of the run, and what it handled. */
export interface FlowStage {
  stage: string;
  action: string;
  count: number;
  kind: string;
  refused: number;
  events: number;
}

/** The run's cells, from the space to the evidence. */
export interface RunFlow {
  run_id: string | null;
  stages: FlowStage[];
  cells: number;
  refused: number;
  measured: number;
  records: number;
  summary: string;
}

/** One arm of one axis, as the attribution reads it. */
export interface AttributionArm {
  value: string;
  mean: number;
  sd: number;
  n: number;
  cells: number;
  verdict: string;
}

/** One axis of the run, and whether it varied. */
export interface AttributionAxis {
  axis: string;
  varied: boolean;
  spread: number;
  values: AttributionArm[];
}

/** What the run can attribute, and what its design cannot say. */
export interface RunAttribution {
  run_id: string;
  metric: string;
  records: number;
  axes: AttributionAxis[];
  varied_axes: string[];
  held_axes: string[];
  attributable: boolean;
  reason: string;
  summary: string;
}


/** What the run measured at one cell, folded over its seeds. */
export interface CellAggregate {
  acc: number[];
  walltime: number[];
  params: number[];
  curves: CurvePoint[][];
  pareto: boolean;
  coordinate: CellCoordinate;
  /** The seeds the run measured at this cell. */
  seeds: number;
}

/** What changed, so a view knows how much of itself to redraw. */
export type StageChange = "axes" | "space" | "evidence" | "events";

export function cellKey(x: string, y: string, z: string): string {
  return `${x}|${y}|${z}`;
}

export function mean(values: number[]): number {
  if (values.length === 0) return 0;
  return values.reduce((sum, v) => sum + v, 0) / values.length;
}

export function stddev(values: number[]): number {
  if (values.length < 2) return 0;
  const m = mean(values);
  const variance =
    values.reduce((sum, v) => sum + (v - m) ** 2, 0) / (values.length - 1);
  return Math.sqrt(variance);
}

/** The per-epoch accuracy of every seed that recorded a curve, averaged. */
export function meanCurve(curves: CurvePoint[][]): CurvePoint[] {
  const byEpoch = new Map<number, number[]>();
  for (const curve of curves) {
    for (const point of curve) {
      const values = byEpoch.get(point.epoch) ?? [];
      values.push(point.val_acc);
      byEpoch.set(point.epoch, values);
    }
  }
  return Array.from(byEpoch.entries())
    .sort((a, b) => a[0] - b[0])
    .map(([epoch, values]) => ({ epoch, val_acc: mean(values) }));
}

/** The backend's verdict per cell, by the key the stage knows the cell by. */
export function indexSpaceCells(
  space: SpacePayload,
  axes: AxisSelection,
): Map<string, SpaceCell> {
  const indexed = new Map<string, SpaceCell>();
  space.cells.forEach((cell) => {
    indexed.set(
      cellKey(
        cell.coordinate[axes.x],
        cell.coordinate[axes.y],
        cell.coordinate[axes.z],
      ),
      cell,
    );
  });
  return indexed;
}

/** Fold the records into one aggregate per cell. */
export function aggregateRecords(
  metrics: RunMetrics | null,
  axes: AxisSelection,
): Map<string, CellAggregate> {
  const aggregates = new Map<string, CellAggregate>();
  const records = metrics?.records ?? [];

  records.forEach((record: any, idx: number) => {
    const coord = record?.coordinate;
    if (!coord) return;
    const key = cellKey(coord[axes.x], coord[axes.y], coord[axes.z]);
    let aggregate = aggregates.get(key);
    if (!aggregate) {
      aggregate = {
        acc: [],
        walltime: [],
        params: [],
        curves: [],
        pareto: false,
        coordinate: { ...coord },
        seeds: 0,
      };
      aggregates.set(key, aggregate);
    }
    aggregate.seeds += 1;
    const payload = record.payload ?? {};
    if (typeof payload.val_acc === "number") aggregate.acc.push(payload.val_acc);
    if (typeof payload.walltime_s === "number") {
      aggregate.walltime.push(payload.walltime_s);
    }
    if (typeof payload.param_count === "number") {
      aggregate.params.push(payload.param_count);
    }
    if (Array.isArray(payload.convergence_curve)) {
      const curve = payload.convergence_curve
        .filter(
          (point: any) =>
            typeof point?.epoch === "number" &&
            typeof point?.val_acc === "number",
        )
        .map((point: any) => ({ epoch: point.epoch, val_acc: point.val_acc }));
      if (curve.length > 0) aggregate.curves.push(curve);
    }
    if (metrics?.pareto?.[idx]) aggregate.pareto = true;
  });

  return aggregates;
}

/** The cells the run measured, in the order a reader reads them. */
export function measuredCells(
  aggregates: Map<string, CellAggregate>,
  axes: AxisSelection,
): CellAggregate[] {
  const cells = Array.from(aggregates.values());
  const varying = varyingAxes(cells, axes);
  return cells.sort((left, right) =>
    cellLabel(left, axes, varying).localeCompare(
      cellLabel(right, axes, varying),
    ),
  );
}

/** The axes the cells differ along: the ones a reader has to be told. */
export function varyingAxes(
  cells: CellAggregate[],
  axes: AxisSelection,
): AxisName[] {
  const names: AxisName[] = [axes.x, axes.y, axes.z];
  return names.filter((name) => {
    const values = new Set(cells.map((cell) => cell.coordinate[name]));
    return values.size > 1;
  });
}

/** The name of a cell: the values of the axes the cells differ along. */
export function cellLabel(
  cell: CellAggregate,
  axes: AxisSelection,
  varying: AxisName[],
): string {
  const names = varying.length > 0 ? varying : [axes.x, axes.y, axes.z];
  return names.map((name) => cell.coordinate[name] ?? "").join(" · ");
}

/** Which values each axis takes, learned from the records themselves. */
export function measuredValues(
  records: any[],
): Record<AxisName, string[]> {
  const observed: Record<AxisName, Set<string>> = {
    credit: new Set(),
    geometry: new Set(),
    dynamics: new Set(),
    substrate: new Set(),
    plasticity: new Set(),
    update: new Set(),
  };

  records.forEach((record) => {
    const coord = record?.coordinate;
    if (!coord) return;
    AXIS_NAMES.forEach((axis) => {
      const value = coord[axis];
      if (typeof value === "string" && value.length > 0) {
        observed[axis].add(value);
      }
    });
  });

  const values = {} as Record<AxisName, string[]>;
  AXIS_NAMES.forEach((axis) => {
    values[axis] = Array.from(observed[axis]).sort();
  });
  return values;
}

class StageState {
  runId: string | null = null;
  metrics: RunMetrics | null = null;
  axes: AxisSelection = { x: "credit", y: "geometry", z: "dynamics" };
  space: SpacePayload | null = null;
  spaceCells = new Map<string, SpaceCell>();
  aggregates = new Map<string, CellAggregate>();
  values: Record<AxisName, string[]> = measuredValues([]);
  chance = 0.1;
  requiredSeeds = 0;
  /** The gate's thresholds: the rules a claim is measured against. */
  gate: GateThresholds | null = null;
  /** The run's stages, as they happened. */
  timeline: RunTimeline | null = null;
  /** The run's account of itself: what it can say, and how it compares. */
  account: RunAccount | null = null;
  /** The run's cells, from the space to the evidence. */
  flow: RunFlow | null = null;
  /** What the run can attribute, and what its design cannot say. */
  attribution: RunAttribution | null = null;
  /** What the space was last asked for, so it is only asked again when it changes. */
  private spaceRequest = "";
  /** What the account was last asked for: the run, and how much it measured. */
  private accountRequest = "";
  /** What the attribution was last asked for: the run, and how much it measured. */
  private attributionRequest = "";
  /** What the flow was last asked for: the run, and how many events it has. */
  private flowRequest = "";
  /** The run the timeline belongs to, and whether it is out of date. */
  private timelineRun = "";
  private timelineStale = true;
  private timelineTimer: number | null = null;
  private listeners: ((change: StageChange) => void)[] = [];

  constructor() {
    // The run the picture is of is chosen once, in the shared selection, so
    // every view reads the same answer without asking for it.
    runSelection.onChange((runId, metrics) => {
      void this.absorb(runId, metrics);
    });
    // A live event means the run's story has moved: the timeline is read
    // again, a moment after the burst.
    router.register("pipeline_event", () => this.scheduleTimeline());
  }

  onChange(listener: (change: StageChange) => void): void {
    this.listeners.push(listener);
  }

  private notify(change: StageChange): void {
    this.listeners.forEach((listener) => listener(change));
  }

  /** The run the picture is of, and everything it has measured. */
  async absorb(runId: string | null, metrics: RunMetrics | null): Promise<void> {
    this.runId = runId;
    this.metrics = metrics;
    if (metrics) {
      if (typeof metrics.chance === "number") this.chance = metrics.chance;
      if (typeof metrics.required_seeds === "number") {
        this.requiredSeeds = metrics.required_seeds;
      }
      if (metrics.gate) {
        this.gate = metrics.gate;
        if (typeof metrics.gate.required_seeds_per_group === "number") {
          this.requiredSeeds = metrics.gate.required_seeds_per_group;
        }
      }
      this.values = measuredValues(metrics.records ?? []);
    }
    this.recomputeEvidence();
    await this.syncSpace();
    void this.syncAccount();
    void this.syncAttribution();
    void this.syncTimeline();
  }

  /** The axes the reader picked: another slice of the same space. */
  setAxes(axes: AxisSelection): void {
    this.axes = axes;
    this.notify("axes");
    this.recomputeEvidence();
    void this.syncSpace();
  }

  private recomputeEvidence(): void {
    this.aggregates = aggregateRecords(this.metrics, this.axes);
    this.notify("evidence");
  }

  /** Ask for the declared space, and tell the views when it arrives. */
  async syncSpace(): Promise<void> {
    if (!this.runId) return;

    const request = [
      this.runId,
      this.axes.x,
      this.axes.y,
      this.axes.z,
      ...AXIS_NAMES.map((axis) => this.values[axis].join(",")),
    ].join("|");
    if (request === this.spaceRequest) return;

    const space = await this.fetchSpace();
    // The request is only remembered once it has been answered: a space
    // that failed to arrive is asked for again, not waited for.
    if (!space) return;
    this.spaceRequest = request;
    this.space = space;
    this.spaceCells = indexSpaceCells(space, this.axes);
    this.notify("space");
  }

  private async fetchSpace(): Promise<SpacePayload | null> {
    try {
      const response = await fetch(`/api/cells/${this.runId}/space`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          axes: [this.axes.x, this.axes.y, this.axes.z],
        }),
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
  async syncAccount(): Promise<void> {
    if (!this.runId) {
      this.account = null;
      this.accountRequest = "";
      return;
    }
    const measured = this.metrics?.records?.length ?? 0;
    const request = `${this.runId}|${measured}`;
    if (request === this.accountRequest) return;

    try {
      const response = await fetch(
        `/api/runs/${encodeURIComponent(this.runId)}/account`,
      );
      if (!response.ok) {
        console.warn("[StageState] The account was refused", response.status);
        return;
      }
      this.account = (await response.json()) as RunAccount;
      this.accountRequest = request;
      this.notify("evidence");
    } catch (error) {
      console.warn("[StageState] The account could not be read", error);
    }
  }

  /** The run's stages, as they happened. */
  async syncTimeline(): Promise<void> {
    if (!this.runId) {
      this.timeline = null;
      this.timelineRun = "";
      return;
    }
    if (!this.timelineStale && this.timelineRun === this.runId) return;

    try {
      const response = await fetch(
        `/api/events?run_id=${encodeURIComponent(this.runId)}`,
      );
      if (!response.ok) {
        console.warn("[StageState] The timeline was refused", response.status);
        return;
      }
      this.timeline = (await response.json()) as RunTimeline;
      this.timelineRun = this.runId;
      this.timelineStale = false;
      this.notify("events");
      void this.syncFlow();
    } catch (error) {
      console.warn("[StageState] The timeline could not be read", error);
    }
  }

  /** The run's cells, from the space to the evidence. */
  async syncFlow(): Promise<void> {
    if (!this.runId) {
      this.flow = null;
      this.flowRequest = "";
      return;
    }
    const events = this.timeline?.events.length ?? 0;
    const request = `${this.runId}|${events}`;
    if (request === this.flowRequest) return;

    try {
      const response = await fetch(
        `/api/runs/${encodeURIComponent(this.runId)}/flow`,
      );
      if (!response.ok) {
        console.warn("[StageState] The flow was refused", response.status);
        return;
      }
      this.flow = (await response.json()) as RunFlow;
      this.flowRequest = request;
      this.notify("events");
    } catch (error) {
      console.warn("[StageState] The flow could not be read", error);
    }
  }

  /** What the run can attribute, and what its design cannot say. */
  async syncAttribution(): Promise<void> {
    if (!this.runId) {
      this.attribution = null;
      this.attributionRequest = "";
      return;
    }
    const measured = this.metrics?.records?.length ?? 0;
    const request = `${this.runId}|${measured}`;
    if (request === this.attributionRequest) return;

    try {
      const response = await fetch(
        `/api/runs/${encodeURIComponent(this.runId)}/attribution`,
      );
      if (!response.ok) {
        console.warn("[StageState] The attribution was refused", response.status);
        return;
      }
      this.attribution = (await response.json()) as RunAttribution;
      this.attributionRequest = request;
      this.notify("evidence");
    } catch (error) {
      console.warn("[StageState] The attribution could not be read", error);
    }
  }

  /** A live event: the run's story has moved, so the timeline is read again. */
  private scheduleTimeline(): void {
    this.timelineStale = true;
    if (this.timelineTimer !== null) return;
    this.timelineTimer = window.setTimeout(() => {
      this.timelineTimer = null;
      void this.syncTimeline();
    }, 300);
  }
}

export const stageState = new StageState();
