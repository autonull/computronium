/** The stage's store — holds state, notifies views, does not fetch (TODO71 Phase 5).
 *
 *  Views subscribe to this; the fetchers (in sources.ts) write into it.
 *  No view imports a fetcher; the store knows nothing of fetch.
 */

import { AXIS_NAMES, type AxisName } from "../cell-data.js";
import {
  runSelection,
  type GateThresholds,
  type RunMetrics,
} from "../run-selection.js";
import { router } from "../ws-client.js";
import {
  type AxisSelection,
  type CellAggregate,
  type CellDynamics,
  type FixedAxis,
  type FlowStage,
  type LedgerArm,
  type MultiRunSpace,
  type RunAccount,
  type RunAttribution,
  type RunFlow,
  type RunTimeline,
  type SpaceCell,
  type SpacePayload,
  type StageChange,
  aggregateRecords,
  cellKey,
  indexSpaceCells,
  measuredCells,
  measuredValues,
  varyingAxes,
} from "./payloads.js";
import {
  fetchSpace,
  fetchAccount,
  fetchTimeline,
  fetchFlow,
  fetchAttribution,
  fetchDynamics,
  fetchTrainedDynamics,
  fetchMultirun,
  scheduleTimeline,
  type AxisSelection as SourceAxisSelection,
} from "./sources.js";

/** The store that every view reads. */
export class StageState {
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
  /** The cell's own dynamics, measured on the server. */
  dynamics: CellDynamics | null = null;
  /** Several runs' evidence in one space, read from the server. */
  multirun: MultiRunSpace | null = null;
  /** The cell's own dynamics after training, measured on the server. */
  trainedDynamics: CellDynamics | null = null;

  /** What the space was last asked for, so it is only asked again when it changes. */
  spaceRequest = "";
  /** What the account was last asked for: the run, and how much it measured. */
  accountRequest = "";
  /** What the attribution was last asked for: the run, and how much it measured. */
  attributionRequest = "";
  /** What the flow was last asked for: the run, and how many events it has. */
  flowRequest = "";
  /** The run the dynamics were measured for. */
  dynamicsRun = "";
  /** Whether the dynamics are being asked for right now. */
  dynamicsAsking = false;
  /** The run the trained dynamics were measured for. */
  trainedDynamicsRun = "";
  /** Whether the trained dynamics are being asked for right now. */
  trainedDynamicsAsking = false;
  /** The axes the runs' space was last asked for. */
  multirunRequest = "";
  /** Whether the runs' space is being asked for right now. */
  multirunAsking = false;
  /** The run the timeline belongs to, and whether it is out of date. */
  timelineRun = "";
  timelineStale = true;
  timelineTimer: number | null = null;
  private listeners: ((change: StageChange) => void)[] = [];

  constructor() {
    // The run the picture is of is chosen once, in the shared selection, so
    // every view reads the same answer without asking for it.
    runSelection.onChange((runId, metrics) => {
      void this.absorb(runId, metrics);
    });
    // A live event means the run's story has moved.
    router.register("pipeline_event", () => scheduleTimeline(this));
  }

  /** Subscribe to state changes. */
  onChange(listener: (change: StageChange) => void): void {
    this.listeners.push(listener);
  }

  private notify(change: StageChange): void {
    this.listeners.forEach((listener) => listener(change));
  }

  /** The run the picture is of, and everything it has measured. */
  async absorb(
    runId: string | null,
    metrics: RunMetrics | null,
  ): Promise<void> {
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
    void this.syncDynamics();
    void this.syncTrainedDynamics();
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

    const space = await fetchSpace(this.runId, this.axes, this.values);
    if (!space) return;
    this.spaceRequest = request;
    this.space = space;
    this.spaceCells = indexSpaceCells(space, this.axes);
    this.notify("space");
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

    const account = await fetchAccount(this.runId, measured);
    if (!account) return;
    this.account = account;
    this.accountRequest = request;
    this.notify("evidence");
  }

  /** The run's stages, as they happened. */
  async syncTimeline(): Promise<void> {
    if (!this.runId) {
      this.timeline = null;
      this.timelineRun = "";
      return;
    }
    if (!this.timelineStale && this.timelineRun === this.runId) return;

    const timeline = await fetchTimeline(this.runId);
    if (!timeline) return;
    this.timeline = timeline;
    this.timelineRun = this.runId;
    this.timelineStale = false;
    this.notify("events");
    void this.syncFlow();
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

    const flow = await fetchFlow(this.runId);
    if (!flow) return;
    this.flow = flow;
    this.flowRequest = request;
    this.notify("events");
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

    const attribution = await fetchAttribution(this.runId, measured);
    if (!attribution) return;
    this.attribution = attribution;
    this.attributionRequest = request;
    this.notify("evidence");
  }

  /** The cell's own dynamics, measured on the server.
   *
   * The measurement is expensive — the cell is composed and its own
   * relaxation is measured over hundreds of steps — so it is asked for
   * once per run, and the server keeps it.
   */
  async syncDynamics(): Promise<void> {
    if (!this.runId) {
      this.dynamics = null;
      this.dynamicsRun = "";
      return;
    }
    if (this.dynamicsRun === this.runId || this.dynamicsAsking) return;
    this.dynamicsAsking = true;
    try {
      const payload = await fetchDynamics(this.runId);
      if (!payload) return;
      this.dynamics = payload;
      if (payload.cell) this.dynamicsRun = this.runId;
      this.notify("evidence");
    } finally {
      this.dynamicsAsking = false;
    }
  }

  /** The cell's own dynamics after training, measured on the server.
   *
   * The measurement is expensive — the cell is composed, trained, and its
   * relaxation measured — so it is asked for once per run, and the server
   * keeps it.
   */
  async syncTrainedDynamics(): Promise<void> {
    if (!this.runId) {
      this.trainedDynamics = null;
      this.trainedDynamicsRun = "";
      return;
    }
    if (this.trainedDynamicsRun === this.runId || this.trainedDynamicsAsking)
      return;
    this.trainedDynamicsAsking = true;
    try {
      const payload = await fetchTrainedDynamics(this.runId);
      if (!payload) return;
      this.trainedDynamics = payload;
      if (payload.cell) this.trainedDynamicsRun = this.runId;
      this.notify("evidence");
    } finally {
      this.trainedDynamicsAsking = false;
    }
  }

  /** Several runs' evidence in one space.
   *
   * The space belongs to the store rather than to the run on screen, so it is
   * asked for when a view wants it and kept for the axes it was asked for.
   */
  async syncMultirun(force = false): Promise<void> {
    const request = [this.axes.x, this.axes.y, this.axes.z].join("|");
    if (!force && (request === this.multirunRequest || this.multirunAsking))
      return;
    this.multirunAsking = true;
    try {
      const multirun = await fetchMultirun(this.axes);
      if (!multirun) return;
      this.multirun = multirun;
      this.multirunRequest = request;
      this.notify("evidence");
    } finally {
      this.multirunAsking = false;
    }
  }

  /** The cells the run measured, in the order a reader reads them. */
  get measuredCells(): CellAggregate[] {
    return measuredCells(this.aggregates, this.axes);
  }

  /** The axes the cells differ along: the ones a reader has to be told. */
  get varyingAxes(): AxisName[] {
    return varyingAxes(this.measuredCells, this.axes);
  }

  /** The name of a cell: the values of the axes the cells differ along. */
  cellLabel(cell: CellAggregate): string {
    return measuredCells(this.aggregates, this.axes).includes(cell)
      ? this.axes.x + "|" + this.axes.y + "|" + this.axes.z
      : "";
  }
}

/** The single stage state instance. */
export const stageState = new StageState();

/** Re-export the utility functions that views need. */
export {
  cellKey,
  mean,
  stddev,
  meanCurve,
  indexSpaceCells,
  aggregateRecords,
  measuredCells,
  varyingAxes,
  cellLabel,
  measuredValues,
  type AxisSelection,
  type CellAggregate,
  type CellCoordinate,
  type CurvePoint,
  type CellDynamics,
} from "./payloads.js";
