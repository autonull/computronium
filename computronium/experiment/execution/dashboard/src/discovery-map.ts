/** Discovery Map — 3D Fog-of-War Grid (TODO68 Phase 1).

    The grid's axes come from the data: every coordinate axis the records
    carry, with the values the records actually used. A cell is measured when
    records landed in it and legal-but-unmeasured when the axis space says the
    combination exists but nothing ran there.
*/

import * as THREE from "three";
import { registry } from "./components/registry.js";
import { getSceneContext } from "./components/context.js";
import { router } from "./ws-client.js";
import { ARM_COLORS, PALETTE } from "./palette.js";
import axisMetadata from "./axis-metadata.json";
import {
  AXIS_NAMES,
  type AxisName,
  type CellData,
  type CurvePoint,
} from "./cell-data.js";
import type { Component } from "./components/registry.js";

interface AxisMeta {
  display_name: string;
  description: string;
  primitives: { name: string }[];
}

const AXIS_META = axisMetadata.axes as unknown as Record<AxisName, AxisMeta>;

/** Beyond this the grid stops being readable, so it says so instead.
    Eight values per axis is 512 cells — the most a scene can carry legibly. */
const MAX_VALUES_PER_AXIS = 8;

function mean(values: number[]): number {
  if (values.length === 0) return 0;
  return values.reduce((sum, v) => sum + v, 0) / values.length;
}

function stddev(values: number[]): number {
  if (values.length < 2) return 0;
  const m = mean(values);
  const variance =
    values.reduce((sum, v) => sum + (v - m) ** 2, 0) / (values.length - 1);
  return Math.sqrt(variance);
}

function meanCurve(curves: CurvePoint[][]): CurvePoint[] {
  // Average the per-epoch accuracy of every seed that recorded a curve.
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

/** Break a label into lines that fit the gap between two cells.

    A long name written on one line is wider than the space it has, and the
    labels then read as a smear; breaking it at its underscores keeps every
    word whole.
*/
function wrapLabel(text: string, maxChars = 10): string[] {
  if (text.length <= maxChars) return [text];

  const lines: string[] = [];
  let current = "";
  for (const part of text.split("_")) {
    const candidate = current ? `${current}_${part}` : part;
    if (candidate.length > maxChars && current) {
      lines.push(current);
      current = part;
    } else {
      current = candidate;
    }
  }
  if (current) lines.push(current);
  return lines;
}

interface GridAxes {
  x: AxisName;
  y: AxisName;
  z: AxisName;
}

interface CellAggregate {
  acc: number[];
  walltime: number[];
  params: number[];
  curves: CurvePoint[][];
  pareto: boolean;
  coordinate: CellData["coordinate"];
}

export class DiscoveryMap implements Component {
  name = "DiscoveryMap";

  private scene: THREE.Scene = new THREE.Scene();
  private camera: THREE.Camera = new THREE.Camera();
  private renderer: THREE.WebGLRenderer | null = null;
  private cells: Map<string, THREE.Mesh | THREE.LineSegments | THREE.Line> =
    new Map();
  cellDataMap: Map<string, CellData> = new Map();
  /** The height each cell's pillar currently stands at. */
  private cellHeights: Map<string, number> = new Map();
  private axes: GridAxes = { x: "credit", y: "geometry", z: "dynamics" };
  private axisValues: Record<AxisName, string[]> = {
    credit: [],
    geometry: [],
    dynamics: [],
    substrate: [],
    plasticity: [],
    update: [],
  };
  private xValues: string[] = [];
  private yValues: string[] = [];
  private zValues: string[] = [];
  private cellSize = 0.8;
  private spacing = 1.1;
  private raycaster = new THREE.Raycaster();
  private mouse = new THREE.Vector2();
  private selectedCell: string | null = null;
  private hoveredCell: string | null = null;
  private legendElement: HTMLElement | null = null;
  private axisLabelMeshes: THREE.Object3D[] = [];
  private chance = 0.1;
  private requiredSeeds = 0;
  /** The run the grid's evidence comes from. */
  private runId: string | undefined = undefined;
  private lastMetrics: any = null;

  constructor() {
    // Register WebSocket handlers IMMEDIATELY in constructor
    // This ensures handlers are ready before any WebSocket messages arrive
    router.register("queue_update", this.onQueueUpdate);
    router.register("campaign_metrics", this.onCampaignMetrics);
  }

  async init(): Promise<void> {
    const context = getSceneContext();
    if (context) {
      this.scene = context.scene;
      this.camera = context.camera;
      this.renderer = context.renderer;
    }

    this.setupInteraction();
    this.createLegend();
    this.buildGrid();

    console.log("[DiscoveryMap] Initialized");
  }

  async destroy(): Promise<void> {
    router.unregister("queue_update", this.onQueueUpdate);
    router.unregister("campaign_metrics", this.onCampaignMetrics);
    this.clearGrid();
    this.legendElement?.remove();
  }

  private setupInteraction(): void {
    const canvas = this.renderer?.domElement;
    if (!canvas) return;

    canvas.addEventListener("mousemove", (event) => {
      const rect = canvas.getBoundingClientRect();
      this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    });

    canvas.addEventListener("click", () => {
      if (this.hoveredCell) {
        this.selectCell(this.hoveredCell);
      }
    });
  }

  private createLegend(): void {
    const overlay = document.getElementById("ui-overlay");
    if (!overlay) return;

    this.legendElement = document.createElement("div");
    this.legendElement.id = "discovery-legend";
    this.legendElement.style.cssText = `
      position: fixed;
      bottom: 140px;
      left: 20px;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      font-size: 12px;
      z-index: 100;
      min-width: 220px;
    `;

    this.legendElement.innerHTML = `
      <div style="font-weight: 600; margin-bottom: 12px; color: var(--text-primary);">Discovery Map</div>
      <div style="display: flex; flex-direction: column; gap: 8px;">
        <div class="legend-item" style="display: flex; align-items: center; gap: 8px;">
          <div style="width: 16px; height: 16px; background: var(--measured); border-radius: 3px; box-shadow: 0 0 8px var(--measured);"></div>
          <span>Measured (glowing pillar)</span>
        </div>
        <div class="legend-item" style="display: flex; align-items: center; gap: 8px;">
          <div style="width: 16px; height: 16px; background: transparent; border: 2px solid var(--legal-unmeasured); border-radius: 3px;"></div>
          <span>Legal / Unmeasured</span>
        </div>
        <div class="legend-item" style="display: flex; align-items: center; gap: 8px;">
          <svg width="16" height="16" viewBox="0 0 16 16"><line x1="3" y1="3" x2="13" y2="13" stroke="var(--void)" stroke-width="2"/><line x1="13" y1="3" x2="3" y2="13" stroke="var(--void)" stroke-width="2"/></svg>
          <span>Void (invalid combination)</span>
        </div>
      </div>
      <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border);">
        <div style="font-weight: 600; margin-bottom: 8px;">Arms</div>
        <div id="legend-arms" style="display: flex; flex-wrap: wrap; gap: 6px;"></div>
      </div>
      <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border);">
        <div style="font-weight: 600; margin-bottom: 8px;">Axes</div>
        <div id="legend-axis-picker" style="display: flex; flex-direction: column; gap: 6px;"></div>
        <div id="legend-axes" style="font-size: 11px; color: var(--text-secondary); margin-top: 8px;"></div>
      </div>
    `;

    overlay.appendChild(this.legendElement);
    this.createAxisPicker();
    this.updateLegendArms();
    this.updateLegendAxes();
  }

  private createAxisPicker(): void {
    const container = this.legendElement?.querySelector("#legend-axis-picker");
    if (!container) return;

    const dimensions: (keyof GridAxes)[] = ["x", "y", "z"];
    dimensions.forEach((dimension) => {
      const row = document.createElement("div");
      row.style.cssText =
        "display: flex; align-items: center; gap: 6px; font-size: 11px;";

      const label = document.createElement("span");
      label.textContent = dimension.toUpperCase();
      label.style.cssText = "color: var(--text-secondary); width: 12px;";

      const select = document.createElement("select");
      select.dataset.dimension = dimension;
      select.style.cssText = `
        flex: 1;
        background: var(--bg-tertiary);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: 4px;
        font-size: 11px;
        padding: 2px 4px;
      `;
      select.addEventListener("change", () => {
        this.axes = { ...this.axes, [dimension]: select.value as AxisName };
        this.applyAxes();
        if (this.lastMetrics) {
          this.applyAggregates(this.aggregate(this.lastMetrics));
        }
      });

      row.appendChild(label);
      row.appendChild(select);
      container.appendChild(row);
    });

    this.refreshAxisOptions();
  }

  private refreshAxisOptions(): void {
    const selects = this.legendElement?.querySelectorAll(
      "#legend-axis-picker select",
    );
    if (!selects) return;

    selects.forEach((select) => {
      const dimension = (select as HTMLSelectElement).dataset
        .dimension as keyof GridAxes;
      const taken = new Set<AxisName>(
        (["x", "y", "z"] as (keyof GridAxes)[])
          .filter((other) => other !== dimension)
          .map((other) => this.axes[other]),
      );

      select.innerHTML = "";
      AXIS_NAMES.forEach((axis) => {
        const option = document.createElement("option");
        option.value = axis;
        option.textContent = AXIS_META[axis]?.display_name ?? axis;
        option.disabled = taken.has(axis);
        option.selected = this.axes[dimension] === axis;
        select.appendChild(option);
      });
    });
  }

  private updateLegendArms(): void {
    const container = this.legendElement?.querySelector("#legend-arms");
    if (!container) return;

    container.innerHTML = this.xValues
      .map((arm) => {
        const color = ARM_COLORS[arm] || PALETTE.gradient;
        return `<span style="display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; background: ${color}22; border: 1px solid ${color}88; border-radius: 12px; color: ${color}; font-size: 11px;">${arm}</span>`;
      })
      .join("");
  }

  private updateLegendAxes(): void {
    const container = this.legendElement?.querySelector("#legend-axes");
    if (!container) return;

    if (this.xValues.length === 0 && this.yValues.length === 0) {
      container.textContent = "Waiting for records — the axes come from the data.";
      return;
    }

    const known = (axis: AxisName, shown: string[]): string => {
      const observed = this.axisValues[axis]?.length ?? 0;
      const legal = AXIS_META[axis]?.primitives.length ?? observed;
      const trimmed =
        observed > shown.length ? ` (showing ${shown.length} of ${observed})` : "";
      return `${shown.join(", ") || "—"}${trimmed} · ${observed} observed / ${legal} known`;
    };

    container.innerHTML = [
      `<div>X: ${this.axes.x} — ${known(this.axes.x, this.xValues)}</div>`,
      `<div>Y: ${this.axes.y} — ${known(this.axes.y, this.yValues)}</div>`,
      `<div>Z: ${this.axes.z} — ${known(this.axes.z, this.zValues)}</div>`,
    ].join("");
  }

  /** Re-read the selected axes from the observed values and rebuild the grid. */
  private applyAxes(): void {
    this.xValues = this.trimValues(this.axisValues[this.axes.x]);
    this.yValues = this.trimValues(this.axisValues[this.axes.y]);
    this.zValues = this.trimValues(this.axisValues[this.axes.z]);
    this.buildGrid();
    this.refreshAxisOptions();
    this.updateLegendArms();
    this.updateLegendAxes();
  }

  /** Keep the grid readable: a wide axis is shown truncated, not hidden. */
  private trimValues(values: string[]): string[] {
    return values.slice(0, MAX_VALUES_PER_AXIS);
  }

  private buildGrid(): void {
    this.clearGrid();

    this.createAxisLabels();

    this.yValues.forEach((yVal, yIdx) => {
      this.zValues.forEach((zVal, zIdx) => {
        this.xValues.forEach((xVal, xIdx) => {
          const key = this.cellKey(xVal, yVal, zVal);
          const cellData: CellData = {
            coordinate: this.coordinateFor(xVal, yVal, zVal),
            status: "legal",
            chance: this.chance,
            requiredSeeds: this.requiredSeeds,
            runId: this.runId,
          };
          this.cellDataMap.set(key, cellData);
          this.createCell(key, cellData, xIdx, yIdx, zIdx);
        });
      });
    });
  }

  /** The cell's whole coordinate: the axes on screen, and the ones held fixed.

      An axis the run never varied has one value, and that value belongs to
      every cell of the grid: a cell that names only three of the six axes
      cannot be measured, queued or registered. */
  private coordinateFor(
    xVal: string,
    yVal: string,
    zVal: string,
  ): CellData["coordinate"] {
    const coordinate: CellData["coordinate"] = {
      credit: "",
      geometry: "",
      dynamics: "",
      substrate: "",
      plasticity: "",
      update: "",
    };
    coordinate[this.axes.x] = xVal;
    coordinate[this.axes.y] = yVal;
    coordinate[this.axes.z] = zVal;
    AXIS_NAMES.forEach((axis) => {
      if (coordinate[axis]) return;
      const values = this.axisValues[axis];
      if (values.length === 1) coordinate[axis] = values[0];
    });
    return coordinate;
  }

  private cellKey(x: string, y: string, z: string): string {
    return `${x}|${y}|${z}`;
  }

  private createAxisLabels(): void {
    this.axisLabelMeshes.forEach((mesh) => this.scene.remove(mesh));
    this.axisLabelMeshes = [];

    const valueMaterial = new THREE.SpriteMaterial({
      color: 0x8b98a8,
      sizeAttenuation: true,
    });
    const nameMaterial = new THREE.SpriteMaterial({
      color: 0xc9d4e0,
      sizeAttenuation: true,
    });

    const gridWidth = (this.xValues.length - 1) * this.spacing;
    const gridDepth = (this.zValues.length - 1) * this.spacing;
    // The labels stand clear in front of the cells: from the camera's angle a
    // label on the grid's own plane is painted across the pillars.
    const labelZ = gridDepth / 2 + 1.4;

    // The values the row names, under the cells.
    this.xValues.forEach((val, idx) => {
      const x = (idx - (this.xValues.length - 1) / 2) * this.spacing;
      const sprite = this.createTextSprite(
        val,
        0.3,
        valueMaterial,
        this.spacing * 0.95,
      );
      sprite.position.set(x, 0, labelZ);
      this.scene.add(sprite);
      this.axisLabelMeshes.push(sprite);
    });

    // The axis the row runs along, at the row's end.
    const xSprite = this.createTextSprite(this.axes.x, 0.3, nameMaterial);
    xSprite.position.set(gridWidth / 2 + 1.15, 0, labelZ);
    this.scene.add(xSprite);
    this.axisLabelMeshes.push(xSprite);

    // The axis that comes at the camera, on its own line in front.
    const zSprite = this.createTextSprite(this.axes.z, 0.3, nameMaterial);
    zSprite.position.set(0, 0, labelZ + 1.1);
    this.scene.add(zSprite);
    this.axisLabelMeshes.push(zSprite);

    // The axis the rows stack along, beside the rows it stacks.
    const ySprite = this.createTextSprite(this.axes.y, 0.3, nameMaterial);
    ySprite.position.set(-(gridWidth / 2) - 1.5, 1.3, 0);
    this.scene.add(ySprite);
    this.axisLabelMeshes.push(ySprite);
  }

  /** A label that fits the space it has: wrapped, and never wider than the gap. */
  private createTextSprite(
    text: string,
    worldHeight: number,
    material: THREE.SpriteMaterial,
    maxWidth?: number,
  ): THREE.Sprite {
    const lines = wrapLabel(text);
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d")!;
    const fontSize = 64;
    const lineHeight = 72;

    context.font = `bold ${fontSize}px "JetBrains Mono", monospace`;
    const textWidth =
      Math.max(...lines.map((line) => context.measureText(line).width)) + 16;
    canvas.width = Math.max(64, Math.ceil(textWidth));
    canvas.height = lines.length * lineHeight + 16;

    // Resizing the canvas resets the context, so the font is set after.
    context.font = `bold ${fontSize}px "JetBrains Mono", monospace`;
    context.fillStyle = "#ffffff";
    context.textAlign = "center";
    context.textBaseline = "middle";
    lines.forEach((line, i) => {
      context.fillText(line, canvas.width / 2, lineHeight * i + lineHeight / 2 + 8);
    });

    const texture = new THREE.CanvasTexture(canvas);
    texture.needsUpdate = true;

    const spriteMaterial = material.clone();
    spriteMaterial.map = texture;
    spriteMaterial.transparent = true;

    const sprite = new THREE.Sprite(spriteMaterial);
    const aspect = canvas.width / canvas.height;
    let height = worldHeight * lines.length;
    if (maxWidth !== undefined) {
      height = Math.min(height, maxWidth / aspect);
    }
    sprite.scale.set(height * aspect, height, 1);
    return sprite;
  }

  private createCell(
    key: string,
    data: CellData,
    xIdx: number,
    yIdx: number,
    zIdx: number,
  ): void {
    const x = (xIdx - (this.xValues.length - 1) / 2) * this.spacing;
    const y = yIdx * this.spacing;
    const z = (zIdx - (this.zValues.length - 1) / 2) * this.spacing;

    let mesh: THREE.Mesh | THREE.LineSegments | THREE.Line;

    switch (data.status) {
      case "measured":
        mesh = this.createMeasuredCell(data);
        break;
      case "legal":
        mesh = this.createLegalCell();
        break;
      case "void":
        mesh = this.createVoidCell();
        break;
      default:
        mesh = this.createLegalCell();
    }

    mesh.position.set(x, y, z);
    mesh.userData = { ...mesh.userData, cellKey: key };
    this.scene.add(mesh);
    this.cells.set(key, mesh);
  }

  private createMeasuredCell(data: CellData): THREE.Mesh {
    const height = this.pillarHeight(data);
    const color = ARM_COLORS[data.coordinate.credit] || PALETTE.gradient;

    const geometry = new THREE.BoxGeometry(
      this.cellSize,
      height,
      this.cellSize,
    );
    geometry.translate(0, height / 2, 0);
    const material = new THREE.MeshStandardMaterial({
      color: new THREE.Color(color),
      emissive: new THREE.Color(color),
      emissiveIntensity: 0.5,
      transparent: true,
      opacity: 0.9,
      metalness: 0.3,
      roughness: 0.4,
    });

    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;

    // Add glow effect
    const glowGeometry = new THREE.BoxGeometry(
      this.cellSize * 1.1,
      height * 1.1,
      this.cellSize * 1.1,
    );
    glowGeometry.translate(0, height / 2, 0);
    const glowMaterial = new THREE.MeshBasicMaterial({
      color: new THREE.Color(color),
      transparent: true,
      opacity: 0.15,
      depthWrite: false,
    });
    const glow = new THREE.Mesh(glowGeometry, glowMaterial);
    mesh.add(glow);
    mesh.userData.glow = glow;

    return mesh;
  }

  private createLegalCell(): THREE.LineSegments {
    const geometry = new THREE.BoxGeometry(
      this.cellSize,
      this.cellSize,
      this.cellSize,
    );
    const edges = new THREE.EdgesGeometry(geometry);
    edges.translate(0, this.cellSize / 2, 0);
    const material = new THREE.LineBasicMaterial({
      color: PALETTE["legal_unmeasured"],
      transparent: true,
      opacity: 0.4,
    });
    const mesh = new THREE.LineSegments(edges, material);
    return mesh;
  }

  private createVoidCell(): THREE.Line {
    const geometry = new THREE.BufferGeometry();
    const size = this.cellSize * 0.6;
    const positions = new Float32Array([
      -size,
      0,
      -size,
      size,
      0,
      size,
      size,
      0,
      -size,
      -size,
      0,
      size,
    ]);
    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));

    const material = new THREE.LineBasicMaterial({
      color: PALETTE.void,
      linewidth: 3,
    });

    const line = new THREE.Line(geometry, material);
    line.position.y = 0.1;
    return line;
  }

  private clearGrid(): void {
    this.cells.forEach((mesh) => {
      this.scene.remove(mesh);
      mesh.geometry.dispose();
      if (Array.isArray(mesh.material)) {
        mesh.material.forEach((m) => m.dispose());
      } else {
        mesh.material.dispose();
      }
    });
    this.cells.clear();
    this.cellDataMap.clear();
    this.cellHeights.clear();
  }

  private onQueueUpdate = (_data: unknown): void => {
    // The queue says what is running; the grid says what was measured.
  };

  private onCampaignMetrics = (data: any): void => {
    const metricsData = data?.data;
    if (!metricsData?.records?.length) return;

    this.lastMetrics = metricsData;
    if (typeof data?.campaign_id === "string") this.runId = data.campaign_id;

    if (typeof metricsData.chance === "number") this.chance = metricsData.chance;
    if (typeof metricsData.required_seeds === "number") {
      this.requiredSeeds = metricsData.required_seeds;
    }

    const aggregates = this.aggregate(metricsData);
    if (this.absorbAxisValues(metricsData.records)) {
      // The axes moved: the grid was rebuilt, so the cells are re-applied below.
      this.applyAxes();
    }
    this.applyAggregates(aggregates);
  };

  /** Mark the cells that have records and light them up. */
  private applyAggregates(aggregates: Map<string, CellAggregate>): void {
    aggregates.forEach((aggregate, key) => {
      const cellData = this.cellDataMap.get(key);
      if (!cellData) return;
      cellData.status = "measured";
      cellData.coordinate = { ...aggregate.coordinate };
      cellData.metrics = {
        val_acc: mean(aggregate.acc),
        val_acc_std: stddev(aggregate.acc),
        walltime_s: mean(aggregate.walltime),
        param_count: mean(aggregate.params),
        n_seeds: aggregate.acc.length,
      };
      cellData.curve = meanCurve(aggregate.curves);
      cellData.pareto = aggregate.pareto;
      cellData.chance = this.chance;
      cellData.requiredSeeds = this.requiredSeeds;
      cellData.runId = this.runId;
      this.updateCellVisual(key, cellData, aggregate.pareto);
    });
  }

  /** Fold the records into one aggregate per cell. */
  private aggregate(metricsData: any): Map<string, CellAggregate> {
    const aggregates = new Map<string, CellAggregate>();

    metricsData.records.forEach((record: any, idx: number) => {
      const coord = record.coordinate;
      if (!coord) return;
      const key = this.cellKey(
        coord[this.axes.x],
        coord[this.axes.y],
        coord[this.axes.z],
      );
      let aggregate = aggregates.get(key);
      if (!aggregate) {
        aggregate = {
          acc: [],
          walltime: [],
          params: [],
          curves: [],
          pareto: false,
          coordinate: { ...coord },
        };
        aggregates.set(key, aggregate);
      }
      const payload = record.payload ?? {};
      if (typeof payload.val_acc === "number") aggregate.acc.push(payload.val_acc);
      if (typeof payload.walltime_s === "number")
        aggregate.walltime.push(payload.walltime_s);
      if (typeof payload.param_count === "number")
        aggregate.params.push(payload.param_count);
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
      if (metricsData.pareto?.[idx]) aggregate.pareto = true;
    });

    return aggregates;
  }

  /** Learn which values each axis takes, from the records themselves. */
  private absorbAxisValues(records: any[]): boolean {
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

    const changed = AXIS_NAMES.some((axis) => {
      const values = this.sortValues(axis, Array.from(observed[axis]));
      if (values.length === this.axisValues[axis].length) {
        return values.some((value, i) => value !== this.axisValues[axis][i]);
      }
      return true;
    });

    if (!changed) return false;

    AXIS_NAMES.forEach((axis) => {
      this.axisValues[axis] = this.sortValues(axis, Array.from(observed[axis]));
    });
    return true;
  }

  /** Order values the way the primitive registry does. */
  private sortValues(axis: AxisName, values: string[]): string[] {
    const order = (AXIS_META[axis]?.primitives ?? []).map((p) => p.name);
    return [...values].sort((a, b) => {
      const ia = order.indexOf(a);
      const ib = order.indexOf(b);
      if (ia === -1 && ib === -1) return a.localeCompare(b);
      if (ia === -1) return 1;
      if (ib === -1) return -1;
      return ia - ib;
    });
  }

  /** A pillar's height: the cell's accuracy, measured. */
  private pillarHeight(data: CellData): number {
    return THREE.MathUtils.lerp(0.4, 3.4, data.metrics?.val_acc ?? 0);
  }

  private updateCellVisual(
    key: string,
    data: CellData,
    isPareto: boolean,
  ): void {
    const oldMesh = this.cells.get(key);
    if (!oldMesh) return;

    const position = oldMesh.position.clone();
    const glow = oldMesh.userData.glow;
    if (glow) oldMesh.remove(glow);

    this.scene.remove(oldMesh);
    oldMesh.geometry.dispose();
    if (Array.isArray(oldMesh.material)) {
      oldMesh.material.forEach((m) => m.dispose());
    } else {
      oldMesh.material.dispose();
    }

    const newMesh = this.createMeasuredCell(data);
    newMesh.position.copy(position);
    // The rebuilt mesh must still know which cell it is: the click finds the
    // cell by this key.
    newMesh.userData.cellKey = key;

    // The pillar grows into its measured height instead of appearing at it.
    const target = this.pillarHeight(data);
    const previous = this.cellHeights.get(key) ?? 0;
    this.cellHeights.set(key, target);
    newMesh.scale.y = target > 0 ? Math.min(1, Math.max(previous / target, 0.001)) : 1;

    if (isPareto) {
      // Add Pareto highlight ring
      const ringGeometry = new THREE.RingGeometry(
        this.cellSize * 0.6,
        this.cellSize * 0.8,
        32,
      );
      const ringMaterial = new THREE.MeshBasicMaterial({
        color: PALETTE.pareto,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.6,
      });
      const ring = new THREE.Mesh(ringGeometry, ringMaterial);
      ring.rotation.x = -Math.PI / 2;
      ring.position.y = 0.05;
      newMesh.add(ring);
      newMesh.userData.paretoRing = ring;
    }

    this.scene.add(newMesh);
    this.cells.set(key, newMesh);
  }

  private selectCell(key: string): void {
    this.selectedCell = key;
    const data = this.cellDataMap.get(key);
    if (data) {
      // Emit event for CellDrawer
      window.dispatchEvent(new CustomEvent("cell-selected", { detail: data }));
    }
  }

  update(delta: number): void {
    // Pillars ease into the height they were measured at.
    const ease = 1 - Math.exp(-delta * 8);
    this.cells.forEach((mesh, key) => {
      const data = this.cellDataMap.get(key);
      if (
        data?.status === "measured" &&
        mesh instanceof THREE.Mesh &&
        mesh.material instanceof THREE.MeshStandardMaterial
      ) {
        if (mesh.scale.y < 1) {
          mesh.scale.y = Math.min(1, mesh.scale.y + (1 - mesh.scale.y) * ease);
        }
        const glow = mesh.userData.glow;
        if (glow) {
          glow.material.opacity = 0.1 + 0.1 * Math.sin(Date.now() * 0.003);
        }
        // Pulse pareto ring
        const ring = mesh.userData.paretoRing;
        if (ring) {
          ring.material.opacity = 0.4 + 0.2 * Math.sin(Date.now() * 0.005);
        }
      }
    });

    // Raycast for hover
    this.raycaster.setFromCamera(this.mouse, this.camera);
    const intersects = this.raycaster.intersectObjects(
      Array.from(this.cells.values()),
      true,
    );

    if (intersects.length > 0) {
      const mesh = intersects[0].object;
      const key = mesh.userData.cellKey || mesh.parent?.userData.cellKey;
      if (key && key !== this.hoveredCell) {
        this.hoveredCell = key;
        this.highlightCell(key, true);
      }
    } else if (this.hoveredCell) {
      this.highlightCell(this.hoveredCell, false);
      this.hoveredCell = null;
    }
  }

  private highlightCell(key: string, highlight: boolean): void {
    const mesh = this.cells.get(key);
    if (!mesh) return;

    if (
      mesh instanceof THREE.Mesh &&
      mesh.material instanceof THREE.MeshStandardMaterial
    ) {
      if (highlight) {
        mesh.userData.originalEmissive = mesh.material.emissiveIntensity;
        mesh.material.emissiveIntensity =
          (mesh.userData.originalEmissive || 0.5) + 0.5;
      } else {
        if (mesh.userData.originalEmissive !== undefined) {
          mesh.material.emissiveIntensity = mesh.userData.originalEmissive;
        }
      }
    }
  }
}

// Register with global registry
export const discoveryMap = new DiscoveryMap();
registry.register(discoveryMap);
