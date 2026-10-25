/** The cell shape the discovery map measures and the drawer reads (TODO68). */

export const AXIS_NAMES = [
  "credit",
  "geometry",
  "dynamics",
  "substrate",
  "plasticity",
  "update",
] as const;

export type AxisName = (typeof AXIS_NAMES)[number];

export interface CurvePoint {
  epoch: number;
  val_acc: number;
}

export interface CellMetrics {
  val_acc?: number;
  val_acc_std?: number;
  walltime_s?: number;
  param_count?: number;
  n_seeds?: number;
}

export interface CellCoordinate {
  credit: string;
  geometry: string;
  dynamics: string;
  substrate?: string;
  plasticity?: string;
  update?: string;
  [key: string]: string | undefined;
}

export interface CellData {
  coordinate: CellCoordinate;
  status: "measured" | "legal" | "void";
  metrics?: CellMetrics;
  curve?: CurvePoint[];
  chance?: number;
  pareto?: boolean;
  requiredSeeds?: number;
  price?: number;
  /** The run the cell's evidence belongs to. */
  runId?: string;
  /** Why the system refuses this cell, when it does. */
  voidReason?: string;
  /** Whether the run's own declaration permits this cell. */
  inDeclaration?: boolean;
}

/** One cell of the declared space, as the backend judges it. */
export interface SpaceCell {
  coordinate: Record<AxisName, string>;
  status: "legal" | "void";
  reason: string;
  in_declaration: boolean;
}

/** The slice of the declared space the grid shows. */
export interface SpacePayload {
  run_id: string;
  axes: AxisName[];
  /** The values each free axis shows. */
  values: Record<AxisName, string[]>;
  /** The value each held axis is fixed at. */
  held: Record<AxisName, string>;
  /** Where each held value came from: measured, declared or default. */
  held_source: Record<AxisName, string>;
  /** The run's own declaration, per axis. */
  declared: Record<AxisName, string[]>;
  /** How many primitives the registry declares per axis. */
  available: Record<AxisName, number>;
  /** Every cell of the slice. */
  cells: SpaceCell[];
  counts: { legal: number; void: number };
  /** Which void rules refuse how many cells. */
  void_rules?: Record<string, number>;
}

export function isAxisName(value: string): value is AxisName {
  return (AXIS_NAMES as readonly string[]).includes(value);
}
