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
}

export function isAxisName(value: string): value is AxisName {
  return (AXIS_NAMES as readonly string[]).includes(value);
}
