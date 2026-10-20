/** Discovery Map — 3D Fog-of-War Grid (TODO68 Phase 1).

    The grid is a slice of the ontology's declared space: three axes are free
    and the other three are held at one value each, so every cell on the grid
    is a whole coordinate and the system can judge it. The backend judges
    each cell — measured (the run has evidence there), legal (the system
    would measure it and nobody has) or void (the system's own rules refuse
    it) — and the map draws what it is told.

    A cell with no record is not an empty cell: it is a gap the researcher
    can see, queue or register.
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
  type SpaceCell,
  type SpacePayload,
} from "./cell-data.js";
import type { Component } from "./components/registry.js";

interface AxisMeta {
  display_name: string;
  description: string;
  primitives: { name: string }[];
}

const AXIS_META = axisMetadata.axes as unknown as Record<AxisName, AxisMeta>;

/** What a cell's status reads as, under the cursor. */
const STATUS_LABELS: Record<CellData["status"], string> = {
  measured: "Measured — the run has evidence here",
  legal: "Legal — a gap nobody has measured",
  void: "Void — the system refuses this cell",
};

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

/** The part of the window the panels leave free: the map is framed into it.

    The legend sits at the bottom left and the plotter at the bottom right, so
    a map framed into the whole window would be half hidden behind them.
*/
const FREE_WIDTH = 0.72;
const FREE_HEIGHT = 0.86;

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
  private camera: THREE.PerspectiveCamera = new THREE.PerspectiveCamera();
  private renderer: THREE.WebGLRenderer | null = null;
  private cells: Map<string, THREE.Mesh | THREE.LineSegments | THREE.Line> =
    new Map();
  cellDataMap: Map<string, CellData> = new Map();
  /** The height each cell's pillar currently stands at. */
  private cellHeights: Map<string, number> = new Map();
  private axes: GridAxes = { x: "credit", y: "geometry", z: "dynamics" };
  private xValues: string[] = [];
  private yValues: string[] = [];
  private zValues: string[] = [];
  /** The declared space the grid shows, as the backend judges it. */
  private space: SpacePayload | null = null;
  /** The backend's verdict per cell, by the cell's key. */
  private spaceCells: Map<string, SpaceCell> = new Map();
  /** The values the run actually measured, per axis. */
  private measuredValues: Record<AxisName, string[]> = {
    credit: [],
    geometry: [],
    dynamics: [],
    substrate: [],
    plasticity: [],
    update: [],
  };
  /** What the space was last asked for, so it is only asked again when it changes. */
  private spaceRequest = "";
  private cellSize = 0.8;
  private spacing = 1.1;
  private raycaster = new THREE.Raycaster();
  private mouse = new THREE.Vector2();
  private selectedCell: string | null = null;
  private hoveredCell: string | null = null;
  private legendElement: HTMLElement | null = null;
  /** The readout that names the cell under the cursor. */
  private readoutElement: HTMLElement | null = null;
  private pointerX = 0;
  private pointerY = 0;
  private axisLabelMeshes: THREE.Object3D[] = [];
  /** Every void marker, in one mesh: they are never picked, only drawn. */
  private voidMesh: THREE.LineSegments | null = null;
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
    this.createReadout();
    this.buildGrid();

    console.log("[DiscoveryMap] Initialized");
  }

  async destroy(): Promise<void> {
    router.unregister("queue_update", this.onQueueUpdate);
    router.unregister("campaign_metrics", this.onCampaignMetrics);
    this.clearGrid();
    this.legendElement?.remove();
    this.readoutElement?.remove();
  }

  private setupInteraction(): void {
    const canvas = this.renderer?.domElement;
    if (!canvas) return;

    // A line is picked within a threshold of the ray, and the default
    // threshold is a whole cell: the cursor would name a cell it is nowhere
    // near. The cells that matter are solid — a pillar, or a pick target
    // behind the wireframe — so the threshold can be tight.
    this.raycaster.params.Line.threshold = this.cellSize * 0.2;

    canvas.addEventListener("mousemove", (event) => {
      const rect = canvas.getBoundingClientRect();
      this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      this.pointerX = event.clientX;
      this.pointerY = event.clientY;
    });

    canvas.addEventListener("mouseleave", () => {
      this.hideReadout();
    });

    canvas.addEventListener("click", () => {
      if (this.hoveredCell) {
        this.selectCell(this.hoveredCell);
      }
    });
  }

  /** The readout that names the cell under the cursor. */
  private createReadout(): void {
    const overlay = document.getElementById("ui-overlay");
    if (!overlay) return;

    this.readoutElement = document.createElement("div");
    this.readoutElement.id = "cell-readout";
    this.readoutElement.style.cssText = `
      position: fixed;
      pointer-events: none;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 8px 10px;
      font-size: 11px;
      line-height: 1.5;
      z-index: 300;
      display: none;
      max-width: 340px;
    `;
    overlay.appendChild(this.readoutElement);
  }

  private showReadout(cell: CellData): void {
    const element = this.readoutElement;
    if (!element) return;

    const coordinate = document.createElement("div");
    coordinate.style.color = "var(--text-secondary)";
    coordinate.textContent = Object.entries(cell.coordinate)
      .filter(([, value]) => value)
      .map(([axis, value]) => `${axis}=${value}`)
      .join("  ");
    element.replaceChildren(coordinate);

    const status = document.createElement("div");
    status.style.marginTop = "4px";
    status.style.fontWeight = "600";
    status.style.color =
      cell.status === "void"
        ? PALETTE.void
        : cell.status === "measured"
          ? PALETTE.measured
          : PALETTE.legal_unmeasured;
    status.textContent = STATUS_LABELS[cell.status];
    element.appendChild(status);

    if (cell.voidReason) {
      const reason = document.createElement("div");
      reason.style.marginTop = "4px";
      reason.style.color = "var(--text-secondary)";
      reason.textContent = cell.voidReason;
      element.appendChild(reason);
    }

    element.style.display = "block";
    const box = element.getBoundingClientRect();
    const left = Math.min(
      this.pointerX + 16,
      window.innerWidth - box.width - 8,
    );
    const top = Math.min(this.pointerY + 16, window.innerHeight - box.height - 8);
    element.style.left = `${Math.max(8, left)}px`;
    element.style.top = `${Math.max(8, top)}px`;
  }

  private hideReadout(): void {
    if (this.readoutElement) this.readoutElement.style.display = "none";
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
      max-width: 340px;
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
          <span>Legal / unmeasured — a gap</span>
        </div>
        <div class="legend-item" style="display: flex; align-items: center; gap: 8px;">
          <svg width="16" height="16" viewBox="0 0 16 16"><line x1="3" y1="3" x2="13" y2="13" stroke="var(--void)" stroke-width="2"/><line x1="13" y1="3" x2="3" y2="13" stroke="var(--void)" stroke-width="2"/></svg>
          <span>Void (the system refuses it)</span>
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
        void this.syncSpace();
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

    const arms = this.measuredValues.credit;
    if (arms.length === 0) {
      container.innerHTML =
        '<span style="color: var(--text-muted); font-size: 11px;">No arm measured yet.</span>';
      return;
    }

    container.innerHTML = arms
      .map((arm) => {
        const color = ARM_COLORS[arm] || PALETTE.gradient;
        return `<span style="display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; background: ${color}22; border: 1px solid ${color}88; border-radius: 12px; color: ${color}; font-size: 11px;">${arm}</span>`;
      })
      .join("");
  }

  private updateLegendAxes(): void {
    const container = this.legendElement?.querySelector("#legend-axes");
    if (!container) return;

    const space = this.space;
    if (!space) {
      container.textContent =
        "Waiting for the run's declared space — the axes come from the ontology.";
      return;
    }

    const axisLine = (axis: AxisName, values: string[]): string => {
      const available = space.available[axis] ?? values.length;
      const trimmed =
        available > values.length ? ` (${values.length} of ${available})` : "";
      const name = AXIS_META[axis]?.display_name ?? axis;
      return `${name}${trimmed}`;
    };

    const held = Object.entries(space.held).map(
      ([axis, value]) => `${axis}=${value}`,
    );
    const counts = { measured: 0, legal: 0, void: 0 };
    this.cellDataMap.forEach((cell) => {
      counts[cell.status] += 1;
    });
    const total = space.cells.length;

    const rules = Object.entries(space.void_rules ?? {})
      .sort((a, b) => b[1] - a[1])
      .slice(0, 2)
      .map(([rule, count]) => `${rule.replace(/_/g, " ")} (${count})`);

    container.innerHTML = [
      `<div>X: ${axisLine(this.axes.x, space.values[this.axes.x] ?? [])}</div>`,
      `<div>Y: ${axisLine(this.axes.y, space.values[this.axes.y] ?? [])}</div>`,
      `<div>Z: ${axisLine(this.axes.z, space.values[this.axes.z] ?? [])}</div>`,
      `<div style="margin-top: 6px;">held: ${held.join(" · ") || "—"}</div>`,
      `<div style="margin-top: 6px;">${counts.measured} measured · ${counts.legal} legal · ${counts.void} void (of ${total})</div>`,
      rules.length > 0
        ? `<div style="margin-top: 6px;">refused by: ${rules.join(", ")}</div>`
        : "",
    ].join("");
  }

  /** Re-read the selected axes from the declared space and rebuild the grid. */
  private applyAxes(): void {
    const space = this.space;
    this.xValues = space?.values[this.axes.x] ?? [];
    this.yValues = space?.values[this.axes.y] ?? [];
    this.zValues = space?.values[this.axes.z] ?? [];
    this.buildGrid();
    this.refreshAxisOptions();
    this.updateLegendArms();
    this.updateLegendAxes();
  }

  private buildGrid(): void {
    this.clearGrid();

    this.createAxisLabels();

    const voidMarkers: number[] = [];

    this.yValues.forEach((yVal, yIdx) => {
      this.zValues.forEach((zVal, zIdx) => {
        this.xValues.forEach((xVal, xIdx) => {
          const key = this.cellKey(xVal, yVal, zVal);
          const spaceCell = this.spaceCells.get(key);
          const status = spaceCell?.status ?? "legal";
          const cellData: CellData = {
            coordinate: this.coordinateFor(xVal, yVal, zVal),
            status,
            chance: this.chance,
            requiredSeeds: this.requiredSeeds,
            runId: this.runId,
            voidReason: spaceCell?.reason,
            inDeclaration: spaceCell?.in_declaration,
          };
          this.cellDataMap.set(key, cellData);
          if (status === "void") {
            // The void markers are drawn together: they are never picked.
            voidMarkers.push(...this.voidMarkerPositions(xIdx, yIdx, zIdx));
            return;
          }
          this.createCell(key, cellData, xIdx, yIdx, zIdx);
        });
      });
    });

    if (voidMarkers.length > 0) this.createVoidMarkers(voidMarkers);
    this.frameGrid();
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
      const held = this.space?.held?.[axis];
      if (held) coordinate[axis] = held;
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
    // label on the grid's own plane is painted across the pillars. They also
    // sit below the floor, so the near ones do not stand on the front row.
    const labelZ = gridDepth / 2 + 1.2;
    const labelY = -0.45;

    // The values the row names, under the cells.
    this.xValues.forEach((val, idx) => {
      const x = (idx - (this.xValues.length - 1) / 2) * this.spacing;
      const sprite = this.createTextSprite(
        val,
        0.3,
        valueMaterial,
        this.spacing * 0.95,
      );
      sprite.position.set(x, labelY, labelZ);
      this.scene.add(sprite);
      this.axisLabelMeshes.push(sprite);
    });

    // The axis the row runs along, at the row's end.
    const xSprite = this.createTextSprite(this.axes.x, 0.3, nameMaterial);
    xSprite.position.set(gridWidth / 2 + 1.15, labelY, labelZ);
    this.scene.add(xSprite);
    this.axisLabelMeshes.push(xSprite);

    // The axis that comes at the camera, on its own line in front.
    const zSprite = this.createTextSprite(this.axes.z, 0.3, nameMaterial);
    zSprite.position.set(0, labelY, labelZ + 1.1);
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

    const mesh =
      data.status === "measured"
        ? this.createMeasuredCell(data)
        : this.createLegalCell();

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
      opacity: 0.55,
    });
    const mesh = new THREE.LineSegments(edges, material);

    // A wireframe cube is hollow: a ray through its middle hits nothing, and
    // a gap nobody can click is a gap nobody can act on. The pick target is
    // the solid cell, drawn never and picked always.
    const pick = new THREE.Mesh(
      new THREE.BoxGeometry(this.cellSize, this.cellSize, this.cellSize),
      new THREE.MeshBasicMaterial(),
    );
    pick.position.y = this.cellSize / 2;
    pick.visible = false;
    mesh.add(pick);

    return mesh;
  }

  /** Free a mesh and everything hanging off it. */
  private disposeMesh(mesh: THREE.Object3D): void {
    mesh.traverse((child) => {
      const geometry = (child as THREE.Mesh).geometry;
      if (geometry) geometry.dispose();
      const material = (child as THREE.Mesh).material;
      if (Array.isArray(material)) {
        material.forEach((m) => m.dispose());
      } else if (material) {
        material.dispose();
      }
    });
  }

  /** The red cross that marks a cell the system refuses. */
  private voidMarkerPositions(
    xIdx: number,
    yIdx: number,
    zIdx: number,
  ): number[] {
    const x = (xIdx - (this.xValues.length - 1) / 2) * this.spacing;
    const y = yIdx * this.spacing;
    const z = (zIdx - (this.zValues.length - 1) / 2) * this.spacing;
    const size = this.cellSize * 0.6;
    const lift = 0.1;
    return [
      x - size,
      y + lift,
      z - size,
      x + size,
      y + lift,
      z + size,
      x + size,
      y + lift,
      z - size,
      x - size,
      y + lift,
      z + size,
    ];
  }

  /** Every void marker in one mesh: they are drawn, never picked. */
  private createVoidMarkers(positions: number[]): void {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(positions, 3),
    );
    const material = new THREE.LineBasicMaterial({
      color: PALETTE.void,
      transparent: true,
      opacity: 0.32,
    });
    this.voidMesh = new THREE.LineSegments(geometry, material);
    this.scene.add(this.voidMesh);
  }

  /** Frame the grid the map just built: a bigger grid needs a wider view.

      The grid is a slab, not a ball, and it is seen at an angle, so the
      camera is placed where every corner of the slab — and the labels that
      stand in front of it — falls inside the frustum, rather than where a
      bounding sphere would fit.
  */
  private frameGrid(): void {
    const context = getSceneContext();
    if (!context?.controls) return;
    if (this.xValues.length === 0 || this.zValues.length === 0) return;

    const halfX = ((this.xValues.length - 1) * this.spacing) / 2 + this.cellSize;
    const halfZ = ((this.zValues.length - 1) * this.spacing) / 2 + this.cellSize;
    const top = (this.yValues.length - 1) * this.spacing + this.cellSize;
    const front = halfZ + 1.8;
    const floor = -0.8;

    const target = new THREE.Vector3(0, top / 2, 0);
    const direction = this.camera.position.clone().sub(context.controls.target);
    if (direction.lengthSq() === 0) direction.set(0.4, 0.5, 0.8);
    direction.normalize();

    const view = direction.clone().negate();
    const right = new THREE.Vector3()
      .crossVectors(view, new THREE.Vector3(0, 1, 0))
      .normalize();
    const up = new THREE.Vector3().crossVectors(right, view).normalize();

    const tanV = Math.tan(((this.camera.fov ?? 60) * Math.PI) / 360);
    const tanH = tanV * (this.camera.aspect || 1);
    // The map is framed into the part of the window the panels leave free.
    const freeTanV = tanV * FREE_HEIGHT;
    const freeTanH = tanH * FREE_WIDTH;

    let distance = 0;
    [-1, 1].forEach((sx) => {
      [floor, top].forEach((y) => {
        [-halfZ, front].forEach((z) => {
          const corner = new THREE.Vector3(sx * halfX, y, z);
          const need =
            Math.max(
              Math.abs(corner.dot(right)) / freeTanH,
              Math.abs(corner.dot(up)) / freeTanV,
            ) + corner.dot(direction);
          distance = Math.max(distance, need);
        });
      });
    });
    distance *= 1.06;

    // The free area is not the middle of the window, so the camera looks
    // beside the grid's centre rather than at it.
    const ndcX = FREE_WIDTH - 1;
    const ndcY = 1 - FREE_HEIGHT;
    target
      .add(right.clone().multiplyScalar(-ndcX * tanH * distance))
      .add(up.clone().multiplyScalar(-ndcY * tanV * distance));

    context.controls.target.copy(target);
    this.camera.position
      .copy(target)
      .add(direction.clone().multiplyScalar(distance));
    context.controls.update();
  }

  private clearGrid(): void {
    this.cells.forEach((mesh) => {
      this.scene.remove(mesh);
      this.disposeMesh(mesh);
    });
    this.cells.clear();
    this.cellDataMap.clear();
    this.cellHeights.clear();

    if (this.voidMesh) {
      this.scene.remove(this.voidMesh);
      this.voidMesh.geometry.dispose();
      if (Array.isArray(this.voidMesh.material)) {
        this.voidMesh.material.forEach((m) => m.dispose());
      } else {
        this.voidMesh.material.dispose();
      }
      this.voidMesh = null;
    }
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

    this.absorbMeasuredValues(metricsData.records);
    void this.syncSpace();
  };

  /** Ask for the declared space, and redraw the grid when it arrives.

      The space is asked for again only when it could have changed: a new run,
      a new set of axes, or a new value measured on one of them.
  */
  private async syncSpace(): Promise<void> {
    if (!this.runId) {
      this.applyAggregates(this.aggregate(this.lastMetrics));
      return;
    }

    const request = [
      this.runId,
      this.axes.x,
      this.axes.y,
      this.axes.z,
      ...AXIS_NAMES.map((axis) => this.measuredValues[axis].join(",")),
    ].join("|");
    if (request !== this.spaceRequest) {
      const space = await this.fetchSpace();
      // The request is only remembered once it has been answered: a space
      // that failed to arrive is asked for again, not waited for.
      if (!space) return;
      this.spaceRequest = request;
      this.space = space;
      this.spaceCells = this.indexSpaceCells(space);
      this.applyAxes();
    }

    this.applyAggregates(this.aggregate(this.lastMetrics));
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
        console.warn("[DiscoveryMap] The space was refused", response.status);
        return null;
      }
      return (await response.json()) as SpacePayload;
    } catch (error) {
      console.warn("[DiscoveryMap] The space could not be read", error);
      return null;
    }
  }

  /** The backend's verdict per cell, by the key the grid knows the cell by. */
  private indexSpaceCells(space: SpacePayload): Map<string, SpaceCell> {
    const indexed = new Map<string, SpaceCell>();
    space.cells.forEach((cell) => {
      const key = this.cellKey(
        cell.coordinate[this.axes.x],
        cell.coordinate[this.axes.y],
        cell.coordinate[this.axes.z],
      );
      indexed.set(key, cell);
    });
    return indexed;
  }

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
    this.updateLegendAxes();
  }

  /** Fold the records into one aggregate per cell. */
  private aggregate(metricsData: any): Map<string, CellAggregate> {
    const aggregates = new Map<string, CellAggregate>();
    if (!metricsData?.records) return aggregates;

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
  private absorbMeasuredValues(records: any[]): void {
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

    AXIS_NAMES.forEach((axis) => {
      this.measuredValues[axis] = Array.from(observed[axis]).sort();
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
    this.disposeMesh(oldMesh);

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

    let key: string | null = null;
    if (intersects.length > 0) {
      key = this.pickCell(intersects);
    }
    if (!key) {
      key = this.voidCellUnderCursor();
    }

    if (key !== this.hoveredCell) {
      if (this.hoveredCell) this.highlightCell(this.hoveredCell, false);
      this.hoveredCell = key;
      if (key) this.highlightCell(key, true);
    }

    const hovered = key ? this.cellDataMap.get(key) : undefined;
    if (hovered) {
      this.showReadout(hovered);
    } else {
      this.hideReadout();
    }
  }

  /** The cell a click means.

      The grid is dense, and every gap carries an invisible pick target so it
      can be acted on — which means the nearest cell along the ray is often a
      gap standing in front of a pillar. The evidence wins: a measured cell
      the ray met is what the researcher was aiming at, glowing and
      unmistakable, and a gap is picked when nothing measured is in the way.
  */
  private pickCell(intersects: THREE.Intersection[]): string | null {
    let nearest: string | null = null;
    for (const hit of intersects) {
      const key =
        hit.object.userData.cellKey || hit.object.parent?.userData.cellKey;
      if (!key) continue;
      nearest ??= key;
      if (this.cellDataMap.get(key)?.status === "measured") {
        return key;
      }
    }
    return nearest;
  }

  /** The void cell under the cursor, if any.

      The void markers are one mesh, drawn and never picked, so the cursor
      cannot name one of them by picking it: the point the ray met says which
      cell the marker belongs to.
  */
  private voidCellUnderCursor(): string | null {
    if (!this.voidMesh) return null;
    const threshold = this.raycaster.params.Line.threshold;
    this.raycaster.params.Line.threshold = this.cellSize * 0.3;
    try {
      const hits = this.raycaster.intersectObject(this.voidMesh, false);
      if (hits.length === 0) return null;
      return this.cellAt(hits[0].point);
    } finally {
      this.raycaster.params.Line.threshold = threshold;
    }
  }

  /** The cell a point in the world belongs to. */
  private cellAt(point: THREE.Vector3): string | null {
    const xIdx = Math.round(point.x / this.spacing + (this.xValues.length - 1) / 2);
    const yIdx = Math.round(point.y / this.spacing);
    const zIdx = Math.round(point.z / this.spacing + (this.zValues.length - 1) / 2);
    if (xIdx < 0 || xIdx >= this.xValues.length) return null;
    if (yIdx < 0 || yIdx >= this.yValues.length) return null;
    if (zIdx < 0 || zIdx >= this.zValues.length) return null;
    return this.cellKey(
      this.xValues[xIdx],
      this.yValues[yIdx],
      this.zValues[zIdx],
    );
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
      return;
    }

    // A legal cell is a wireframe cube: it brightens rather than glows.
    if (
      mesh instanceof THREE.LineSegments &&
      mesh.material instanceof THREE.LineBasicMaterial
    ) {
      if (highlight) {
        mesh.userData.originalOpacity = mesh.material.opacity;
        mesh.material.opacity = 0.95;
      } else if (mesh.userData.originalOpacity !== undefined) {
        mesh.material.opacity = mesh.userData.originalOpacity;
      }
    }
  }
}

// Register with global registry
export const discoveryMap = new DiscoveryMap();
registry.register(discoveryMap);
