/** Discovery Map — 3D Fog-of-War Grid (TODO68 Phase 1). */

import * as THREE from "three";
import { Line2 } from "three-stdlib";
import { LineGeometry, LineMaterial } from "three-stdlib";
import { registry } from "./components/registry.js";
import { getSceneContext } from "./components/context.js";
import { router } from "./ws-client.js";
import { ARM_COLORS, PALETTE } from "./palette.js";
import type { Component } from "./components/registry.js";

interface CellData {
  coordinate: {
    credit: string;
    geometry: string;
    dynamics: string;
    substrate?: string;
    plasticity?: string;
    update?: string;
  };
  status: "measured" | "legal" | "void";
  metrics?: {
    val_acc?: number;
    val_acc_std?: number;
    walltime_s?: number;
    param_count?: number;
    n_seeds?: number;
  };
  requiredSeeds?: number;
  price?: number; // for legal/unmeasured cells
}

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

interface GridAxes {
  x: string; // credit
  y: string; // geometry
  z: string; // dynamics
}

export class DiscoveryMap implements Component {
  name = "DiscoveryMap";

  private scene: THREE.Scene = new THREE.Scene();
  private camera: THREE.Camera = new THREE.Camera();
  private renderer: THREE.WebGLRenderer | null = null;
  private cells: Map<string, THREE.Mesh | THREE.LineSegments | THREE.Line> =
    new Map();
  cellDataMap: Map<string, CellData> = new Map();
  private axes: GridAxes = { x: "credit", y: "geometry", z: "dynamics" };
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
  private initialized = false;

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

    // Setup mouse interaction
    this.setupInteraction();

    // Default axes values (from demo campaign)
    this.xValues = [
      "gradient",
      "random_projections",
      "pepita",
      "local_goodness",
    ];
    this.yValues = ["feedforward"];
    this.zValues = ["instantaneous"];

    // Create legend once the axes it names are known
    this.createLegend();

    // Build initial empty grid
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
      min-width: 200px;
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
        <div id="legend-axes" style="font-size: 11px; color: var(--text-secondary);"></div>
      </div>
    `;

    overlay.appendChild(this.legendElement);
    this.updateLegendArms();
    this.updateLegendAxes();
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

    container.textContent = `X: ${this.axes.x} (${this.xValues.join(", ")}) | Y: ${this.axes.y} (${this.yValues.join(", ")}) | Z: ${this.axes.z} (${this.zValues.join(", ")})`;
  }

  private buildGrid(): void {
    this.clearGrid();

    // Create axis labels
    this.createAxisLabels();

    // Build cell grid
    this.yValues.forEach((yVal, yIdx) => {
      this.zValues.forEach((zVal, zIdx) => {
        this.xValues.forEach((xVal, xIdx) => {
          const key = `${xVal}|${yVal}|${zVal}`;
          const cellData: CellData = {
            coordinate: {
              credit: xVal,
              geometry: yVal,
              dynamics: zVal,
            },
            status: "legal",
          };
          this.cellDataMap.set(key, cellData);
          this.createCell(key, cellData, xIdx, yIdx, zIdx);
        });
      });
    });
  }

  private createAxisLabels(): void {
    // Remove old labels
    this.axisLabelMeshes.forEach((mesh) => this.scene.remove(mesh));
    this.axisLabelMeshes = [];

    const labelMaterial = new THREE.SpriteMaterial({
      color: 0x8b98a8,
      sizeAttenuation: true,
    });

    // X-axis labels (credit arms), on the ground under the cells they name
    this.xValues.forEach((val, idx) => {
      const x = (idx - (this.xValues.length - 1) / 2) * this.spacing;
      const sprite = this.createTextSprite(val, 0.3, labelMaterial);
      sprite.position.set(x, -0.06, 0.72);
      this.scene.add(sprite);
      this.axisLabelMeshes.push(sprite);
    });

    // Y-axis label, above the cells
    const ySprite = this.createTextSprite(this.axes.y, 0.28, labelMaterial);
    ySprite.position.set(0, 3.5, 0);
    this.scene.add(ySprite);
    this.axisLabelMeshes.push(ySprite);

    // Z-axis label, past the end of the row
    const zSprite = this.createTextSprite(this.axes.z, 0.28, labelMaterial);
    zSprite.position.set(
      ((this.xValues.length - 1) / 2) * this.spacing + 1.7,
      -0.06,
      0.72,
    );
    this.scene.add(zSprite);
    this.axisLabelMeshes.push(zSprite);
  }

  private createTextSprite(
    text: string,
    worldHeight: number,
    material: THREE.SpriteMaterial,
  ): THREE.Sprite {
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d")!;
    const fontSize = 64;

    context.font = `bold ${fontSize}px "JetBrains Mono", monospace`;
    const textWidth = Math.ceil(context.measureText(text).width) + 16;
    canvas.width = Math.max(64, textWidth);
    canvas.height = 96;

    // Resizing the canvas resets the context, so the font is set after.
    context.font = `bold ${fontSize}px "JetBrains Mono", monospace`;
    context.fillStyle = "#8b98a8";
    context.textAlign = "center";
    context.textBaseline = "middle";
    context.fillText(text, canvas.width / 2, canvas.height / 2);

    const texture = new THREE.CanvasTexture(canvas);
    texture.needsUpdate = true;

    const spriteMaterial = material.clone();
    spriteMaterial.map = texture;
    spriteMaterial.transparent = true;

    const sprite = new THREE.Sprite(spriteMaterial);
    const aspect = canvas.width / canvas.height;
    sprite.scale.set(worldHeight * aspect, worldHeight, 1);
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
    mesh.userData = { cellKey: key };
    this.scene.add(mesh);
    this.cells.set(key, mesh);
  }

  private createMeasuredCell(data: CellData): THREE.Mesh {
    const height = THREE.MathUtils.lerp(0.4, 3.4, data.metrics?.val_acc ?? 0);
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
  }

  private onQueueUpdate = (data: any): void => {
    // Update grid based on queue status
    // For now, just rebuild with current axes
    if (data.campaigns) {
      // Could update axes based on running campaigns
    }
  };

  private onCampaignMetrics = (data: any): void => {
    const { data: metricsData } = data;
    if (!metricsData?.records?.length) return;

    interface CellAggregate {
      acc: number[];
      walltime: number[];
      params: number[];
      pareto: boolean;
    }

    const aggregates = new Map<string, CellAggregate>();
    metricsData.records.forEach((record: any, idx: number) => {
      const coord = record.coordinate;
      if (!coord) return;
      const key = `${coord.credit}|${coord.geometry}|${coord.dynamics}`;
      let aggregate = aggregates.get(key);
      if (!aggregate) {
        aggregate = { acc: [], walltime: [], params: [], pareto: false };
        aggregates.set(key, aggregate);
      }
      const payload = record.payload ?? {};
      if (typeof payload.val_acc === "number") aggregate.acc.push(payload.val_acc);
      if (typeof payload.walltime_s === "number")
        aggregate.walltime.push(payload.walltime_s);
      if (typeof payload.param_count === "number")
        aggregate.params.push(payload.param_count);
      if (metricsData.pareto?.[idx]) aggregate.pareto = true;
    });

    const requiredSeeds = metricsData.required_seeds as number | undefined;

    aggregates.forEach((aggregate, key) => {
      const cellData = this.cellDataMap.get(key);
      if (!cellData) return;
      cellData.status = "measured";
      cellData.metrics = {
        val_acc: mean(aggregate.acc),
        val_acc_std: stddev(aggregate.acc),
        walltime_s: mean(aggregate.walltime),
        param_count: mean(aggregate.params),
        n_seeds: aggregate.acc.length,
      };
      cellData.requiredSeeds = requiredSeeds;
      this.updateCellVisual(key, cellData, aggregate.pareto);
    });
  };

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
    // Animate glow pulse for measured cells
    this.cells.forEach((mesh, key) => {
      const data = this.cellDataMap.get(key);
      if (
        data?.status === "measured" &&
        mesh instanceof THREE.Mesh &&
        mesh.material instanceof THREE.MeshStandardMaterial
      ) {
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
