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

/** The three axes the stage shows, and the three it holds. */
export interface AxisSelection {
  x: AxisName;
  y: AxisName;
  z: AxisName;
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
export type StageChange = "axes" | "space" | "evidence";

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
  /** What the space was last asked for, so it is only asked again when it changes. */
  private spaceRequest = "";
  private listeners: ((change: StageChange) => void)[] = [];

  constructor() {
    // The run the picture is of is chosen once, in the shared selection, so
    // every view reads the same answer without asking for it.
    runSelection.onChange((runId, metrics) => {
      void this.absorb(runId, metrics);
    });
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
}

export const stageState = new StageState();
