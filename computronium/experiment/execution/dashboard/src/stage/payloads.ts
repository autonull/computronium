/** The payloads the stage shares — interfaces and utilities (TODO71 Phase 5).
 *
 *  Views and the store read from these; the fetchers write to them.
 *  No view imports a fetcher; no interface knows how it is filled.
 */

import {
  AXIS_NAMES,
  type AxisName,
  type CellCoordinate,
  type CurvePoint,
  type SpaceCell,
  type SpacePayload,
} from "../cell-data.js";
import { type GateThresholds, type RunMetrics } from "../run-selection.js";

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

/** One cell's own dynamics, measured on the server. */
export interface CellDynamics {
  run_id?: string;
  /** Whether the cell has a state that moves at all. */
  stateful: boolean;
  /** Why it does or does not. */
  reason?: string;
  /** What the measurements say together, in the server's words. */
  verdict?: string;
  /** Whether the weights were trained before the measurement. */
  trained?: boolean;
  task?: string;
  cell?: {
    coordinate: Record<string, string>;
    params?: number;
    /** The axes the server swapped to find a cell with a state. */
    repairs?: string[];
    /** Whether the run itself measured this cell. */
    measured_by_run?: boolean;
    run_cell?: Record<string, string>;
  };
  trajectory?: {
    steps: number;
    path: number[][];
    norm: number[];
    error: number[];
    span: number;
    axes: string[];
  };
  spectrum?: number[];
  basin?: {
    radii: number[];
    stability: number[];
    paths: {
      radius: number;
      sample: number;
      distances: number[];
      returned: boolean;
    }[];
  };
  landscape?: {
    grid: number[][];
    x: number[];
    y: number[];
    span: number;
  };
  settles?: boolean;
  largest_exponent?: number;
  widest_basin?: number;
}

/** What one run measured at one cell of the space, folded over its seeds. */
export interface MultiRunCell {
  accuracy: number;
  seeds: number;
  arm: string;
}

/** One run's own window on the space, and what it measured in it. */
export interface MultiRunSlice {
  run_id: string;
  profile: string | null;
  status: string | null;
  started_at: string | null;
  records: number;
  values: Record<string, string[]>;
  held: Record<string, string>;
  declared: Record<string, string[]>;
  /** The cells the system refuses, by the name the axes give them. */
  refused: string[];
  measured: Record<string, MultiRunCell>;
}

/** Several runs' evidence in one space. */
export interface MultiRunSpace {
  axes: string[];
  values: Record<string, string[]>;
  runs: MultiRunSlice[];
  counts: {
    runs: number;
    measured: number;
    shared: number;
    cells: number;
  };
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

/** Re-export the types from cell-data and run-selection that views need. */
export type {
  AxisName,
  CellCoordinate,
  CurvePoint,
  SpaceCell,
  SpacePayload,
  GateThresholds,
  RunMetrics,
};

/** A unique key for a cell in the space. */
export function cellKey(x: string, y: string, z: string): string {
  return `${x}|${y}|${z}`;
}

/** The arithmetic mean of a list of numbers. */
export function mean(values: number[]): number {
  if (values.length === 0) return 0;
  return values.reduce((sum, v) => sum + v, 0) / values.length;
}

/** The sample standard deviation of a list of numbers. */
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
    if (typeof payload.val_acc === "number")
      aggregate.acc.push(payload.val_acc);
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
export function measuredValues(records: any[]): Record<AxisName, string[]> {
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
