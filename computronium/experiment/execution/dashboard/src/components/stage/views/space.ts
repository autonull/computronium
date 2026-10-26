/** Space stage view — the discovery map as a per-instance view (TODO72 P5). */

import * as THREE from "three";
import { AXIS_NAMES, type AxisName, type CellData } from "../../../cell-data.js";
import { frameBox } from "../../../stores/framing.js";
import { createTextSprite } from "../../../stores/sprites.js";
import { ARM_COLORS, PALETTE } from "../../../colors.js";
import { workspaceStore } from "../../../stores/workspace.js";
import { metricsStore } from "../../../stores/metrics.js";
import { spaceStore } from "../../../stores/space.js";
import { cellKey, type AxisSelection } from "../../../stores/payloads.js";
import type {
  StageViewDefinition,
  StageViewInstance,
  StageViewContext,
  StageChange,
  Size,
} from "../../../layout/types.js";

interface AxisMeta {
  display_name: string;
  description: string;
  primitives: { name: string }[];
}

const STATUS_LABELS: Record<CellData["status"], string> = {
  measured: "Measured — the run has evidence here",
  legal: "Legal — a gap nobody has measured",
  void: "Void — the system refuses this cell",
};

/** Create a StageViewInstance for the "space" view. */
export function createSpaceView(context: StageViewContext): StageViewInstance {
  const { surface, flat, workspace, state, instanceId } = context;

  // Per-instance state derived from state + workspace
  let runId = (state as any).runId ?? workspace.getSelectedRunId();
  let axes: AxisSelection = (state as any).axes ?? {
    x: workspace.getAxes().x as AxisName,
    y: workspace.getAxes().y as AxisName,
    z: workspace.getAxes().z as AxisName,
  };

  // Three.js objects owned by this view instance
  const scene = surface.three.scene;
  const camera = surface.three.camera;
  const renderer = surface.three.renderer;
  const controls = surface.three.controls;

  // Grid state
  const cells = new Map<string, THREE.Mesh | THREE.LineSegments | THREE.Line>();
  const cellDataMap = new Map<string, CellData>();
  const cellHeights = new Map<string, number>();
  let xValues: string[] = [];
  let yValues: string[] = [];
  let zValues: string[] = [];
  const cellSize = 0.8;
  const spacing = 1.1;
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();
  let hoveredCell: string | null = null;
  let selectedCell: string | null = null;
  let pointerX = 0;
  let pointerY = 0;
  const axisLabelMeshes: THREE.Object3D[] = [];
  let voidMesh: THREE.LineSegments | null = null;
  let visible = false;

  // Readout element (shared overlay, but per-instance content)
  let readoutElement: HTMLElement | null = null;

  // Subscriptions
  let workspaceUnsub: (() => void) | null = null;
  let metricsUnsub: (() => void) | null = null;
  let spaceUnsub: (() => void) | null = null;
  let frameUnsub: (() => void) | null = null;

  // Space store values key (empty initially, updated when space loads)
  let spaceValues: Record<AxisName, string[]> = {
    credit: [],
    geometry: [],
    dynamics: [],
    substrate: [],
    plasticity: [],
    update: [],
  };
  let heldValues: Record<AxisName, string> = {
    credit: "",
    geometry: "",
    dynamics: "",
    substrate: "",
    plasticity: "",
    update: "",
  };

  function resubscribe(): void {
    metricsUnsub?.();
    spaceUnsub?.();
    if (!runId) return;
    metricsUnsub = metricsStore.subscribe(runId, () => {
      applyAggregates();
    });
    spaceUnsub = spaceStore.subscribe(runId, axes, spaceValues, () => {
      applyAxes();
    });
  }

  async function init(): Promise<void> {
    // Create readout overlay
    createReadout();

    // Create empty state CTA (hidden by default)
    createEmptyCta();

    // Subscribe to workspace changes (run selection, axes)
    workspaceUnsub = workspace.onChange(() => {
      const newRunId = workspace.getSelectedRunId();
      const newAxesRaw = workspace.getAxes();
      const newAxes: AxisSelection = {
        x: newAxesRaw.x as AxisName,
        y: newAxesRaw.y as AxisName,
        z: newAxesRaw.z as AxisName,
      };
      if (newRunId !== runId || newAxes.x !== axes.x || newAxes.y !== axes.y || newAxes.z !== axes.z) {
        runId = newRunId;
        axes = newAxes;
        resubscribe();
        applyAxes();
      }
    });

    resubscribe();

    // Register per-frame update
    frameUnsub = surface.onFrame(update);

    // Initial draw; space data may still be in flight
    applyAxes();
  }

  function createReadout(): void {
    const overlay = document.getElementById("ui-overlay");
    if (!overlay) return;

    readoutElement = document.createElement("div");
    readoutElement.id = `cell-readout-${instanceId}`;
    readoutElement.style.cssText = `
      position: fixed;
      pointer-events: none;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 12px;
      font-size: 11px;
      line-height: 1.5;
      z-index: 300;
      display: none;
      max-width: 360px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.5);
      backdrop-filter: blur(8px);
    `;
    overlay.appendChild(readoutElement);
  }

  function showReadout(cell: CellData): void {
    const element = readoutElement;
    if (!element) return;

    element.innerHTML = "";

    const coordRow = document.createElement("div");
    coordRow.style.cssText = "display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px;";
    Object.entries(cell.coordinate)
      .filter(([, value]) => value)
      .forEach(([axis, value]) => {
        const isCredit = axis === "credit";
        const armColor = ARM_COLORS[value as string];
        const color = isCredit ? (armColor ?? PALETTE.gradient) : "var(--text-secondary)";
        const chip = document.createElement("span");
        chip.style.cssText = `
          padding: 2px 8px;
          background: ${isCredit ? color + "22" : "var(--bg-tertiary)"};
          border: 1px solid ${isCredit ? color + "88" : "var(--border)"};
          border-radius: 10px;
          font-size: 10px;
          color: ${color};
          font-weight: ${isCredit ? "600" : "400"};
        `;
        chip.textContent = `${axis}=${value}`;
        coordRow.appendChild(chip);
      });
    element.appendChild(coordRow);

    const statusRow = document.createElement("div");
    statusRow.style.cssText = "display: flex; align-items: center; gap: 8px; margin-bottom: 6px;";
    const statusColors: Record<CellData["status"], string> = {
      measured: PALETTE.measured,
      legal: PALETTE.legal_unmeasured,
      void: PALETTE.void,
    };
    const statusIcons: Record<CellData["status"], string> = {
      measured: "●",
      legal: "○",
      void: "✕",
    };
    const icon = document.createElement("span");
    icon.style.cssText = `font-size: 14px; color: ${statusColors[cell.status]};`;
    icon.textContent = statusIcons[cell.status];
    statusRow.appendChild(icon);

    const statusText = document.createElement("span");
    statusText.style.cssText = `font-weight: 600; color: ${statusColors[cell.status]}; font-size: 12px;`;
    statusText.textContent = STATUS_LABELS[cell.status];
    statusRow.appendChild(statusText);
    element.appendChild(statusRow);

    if (cell.status === "measured" && cell.metrics) {
      const m = cell.metrics;
      const metricsRow = document.createElement("div");
      metricsRow.style.cssText = "display: flex; gap: 16px; font-size: 11px; color: var(--text-secondary);";
      const acc = m.val_acc ?? 0;
      const std = m.val_acc_std ?? 0;
      const seeds = m.n_seeds ?? 0;
      const wt = m.walltime_s;
      metricsRow.innerHTML = `
        <span>acc <strong style="color: var(--text-primary);">${acc.toFixed(3)}</strong> ± ${std.toFixed(3)}</span>
        <span>n=<strong style="color: var(--text-primary);">${seeds}</strong></span>
        <span>${wt !== undefined ? `${wt.toFixed(1)}s` : ""}</span>
        ${cell.pareto ? `<span style="color: var(--pareto);">● PARETO</span>` : ""}
      `;
      element.appendChild(metricsRow);
    }

    if (cell.status === "legal") {
      const hint = document.createElement("div");
      hint.style.cssText = "margin-top: 6px; padding: 6px 8px; background: var(--bg-tertiary); border-radius: 4px; font-size: 10px; color: var(--text-muted);";
      const seeds = cell.requiredSeeds ?? 0;
      hint.textContent = `Click to queue ${seeds} seeds →`;
      element.appendChild(hint);
    }

    if (cell.voidReason) {
      const reason = document.createElement("div");
      reason.style.cssText = "margin-top: 6px; padding: 6px 8px; background: var(--void)11; border: 1px solid var(--void)44; border-radius: 4px; font-size: 10px; color: var(--void);";
      reason.textContent = cell.voidReason;
      element.appendChild(reason);
    }

    element.style.display = "block";
    const box = element.getBoundingClientRect();
    const left = Math.min(pointerX + 16, window.innerWidth - box.width - 8);
    const top = Math.min(pointerY + 16, window.innerHeight - box.height - 8);
    element.style.left = `${Math.max(8, left)}px`;
    element.style.top = `${Math.max(8, top)}px`;
  }

  function hideReadout(): void {
    if (readoutElement) readoutElement.style.display = "none";
  }

  let emptyCtaElement: HTMLElement | null = null;

  function createEmptyCta(): void {
    const overlayEl = document.getElementById("ui-overlay");
    if (!overlayEl) return;
    emptyCtaElement = document.createElement("div");
    emptyCtaElement.className = "ui-empty-cta";
    emptyCtaElement.innerHTML = `
      <div class="icon">🚀</div>
      <div class="title">Welcome to Computronium</div>
      <div class="message">No run selected. Start a quick run to explore the discovery map.</div>
      <button class="cta-btn" data-act="start-run">Start a Run</button>
    `;
    const btn = emptyCtaElement.querySelector<HTMLButtonElement>("[data-act=start-run]");
    btn?.addEventListener("click", () => {
      // Open control panel and focus the New Run section
      const panelBtn = document.querySelector<HTMLButtonElement>('.ctrl [data-act="panel"]');
      panelBtn?.click();
      // Focus the quick run button in control panel
      setTimeout(() => {
        const quickRunBtn = document.querySelector<HTMLButtonElement>('.ctrl [data-act="quick-run"]');
        quickRunBtn?.focus();
      }, 100);
    });
    overlayEl?.appendChild(emptyCtaElement);
  }

  function showEmptyCta(): void {
    if (!emptyCtaElement) createEmptyCta();
    emptyCtaElement?.classList.add("visible");
  }

  function hideEmptyCta(): void {
    emptyCtaElement?.classList.remove("visible");
  }

  function applyAxes(): void {
    if (!runId) {
      visible = false;
      clearGrid();
      showEmptyCta();
      return;
    }
    hideEmptyCta();

    const space = spaceStore.get(runId, axes, spaceValues);
    if (!space) {
      visible = false;
      clearGrid();
      showEmptyCta();
      return;
    }

    // spaceValues no longer used for cache key (fixed in SpaceStore), but keep for compatibility
    spaceValues = { ...spaceValues, ...space.values };
    // Cache held values for coordinateFor()
    heldValues = { ...space.held ?? {} };

    xValues = space.values[axes.x] ?? [];
    yValues = space.values[axes.y] ?? [];
    zValues = space.values[axes.z] ?? [];
    visible = true;
    buildGrid();
    applyAggregates();
  }

  function buildGrid(): void {
    clearGrid();
    if (!visible) return;

    createAxisLabels();

    const space = spaceStore.get(runId!, axes, spaceValues);
    const cellsByCoord = new Map<string, any>();
    space?.cells.forEach((c) => {
      const coordKey = `${c.coordinate[axes.x]}|${c.coordinate[axes.y]}|${c.coordinate[axes.z]}`;
      cellsByCoord.set(coordKey, c);
    });

    const voidMarkers: number[] = [];

    yValues.forEach((yVal: string, yIdx: number) => {
      zValues.forEach((zVal: string, zIdx: number) => {
        xValues.forEach((xVal: string, xIdx: number) => {
          const key = cellKey(xVal, yVal, zVal);
          const coordKey = `${xVal}|${yVal}|${zVal}`;
          const spaceCell = cellsByCoord.get(coordKey);
          const status = spaceCell?.status ?? "legal";
          const cellData: CellData = {
            coordinate: coordinateFor(xVal, yVal, zVal),
            status,
            chance: 0.1,
            requiredSeeds: 0,
            runId,
            voidReason: spaceCell?.reason,
            inDeclaration: spaceCell?.in_declaration,
          };
          cellDataMap.set(key, cellData);
          if (status === "void") {
            voidMarkers.push(...voidMarkerPositions(xIdx, yIdx, zIdx));
            return;
          }
          createCell(key, cellData, xIdx, yIdx, zIdx);
        });
      });
    });

    if (voidMarkers.length > 0) createVoidMarkers(voidMarkers);
    frameGrid();
  }

  function coordinateFor(xVal: string, yVal: string, zVal: string): CellData["coordinate"] {
    const coordinate: CellData["coordinate"] = {
      credit: "",
      geometry: "",
      dynamics: "",
      substrate: "",
      plasticity: "",
      update: "",
    };
    coordinate[axes.x] = xVal;
    coordinate[axes.y] = yVal;
    coordinate[axes.z] = zVal;
    AXIS_NAMES.forEach((axis: AxisName) => {
      if (coordinate[axis]) return;
      const held = heldValues[axis];
      if (held) coordinate[axis] = held;
    });
    return coordinate;
  }

  function createAxisLabels(): void {
    axisLabelMeshes.forEach((mesh) => scene.remove(mesh));
    axisLabelMeshes.length = 0;

    const valueMaterial = new THREE.SpriteMaterial({
      color: 0x8b98a8,
      sizeAttenuation: true,
    });
    const nameMaterial = new THREE.SpriteMaterial({
      color: 0xc9d4e0,
      sizeAttenuation: true,
    });

    const gridWidth = (xValues.length - 1) * spacing;
    const gridDepth = (zValues.length - 1) * spacing;
    const labelZ = gridDepth / 2 + 1.2;
    const labelY = -0.45;

    xValues.forEach((val, idx) => {
      const x = (idx - (xValues.length - 1) / 2) * spacing;
      const sprite = createTextSprite(val, 0.3, valueMaterial, spacing * 0.95);
      sprite.position.set(x, labelY, labelZ);
      scene.add(sprite);
      axisLabelMeshes.push(sprite);
    });

    const xSprite = createTextSprite(axes.x, 0.3, nameMaterial);
    xSprite.position.set(gridWidth / 2 + 1.15, labelY, labelZ);
    scene.add(xSprite);
    axisLabelMeshes.push(xSprite);

    const zSprite = createTextSprite(axes.z, 0.3, nameMaterial);
    zSprite.position.set(0, labelY, labelZ + 1.1);
    scene.add(zSprite);
    axisLabelMeshes.push(zSprite);

    const ySprite = createTextSprite(axes.y, 0.3, nameMaterial);
    ySprite.position.set(-(gridWidth / 2) - 1.5, 1.3, 0);
    scene.add(ySprite);
    axisLabelMeshes.push(ySprite);
  }

  function createCell(key: string, data: CellData, xIdx: number, yIdx: number, zIdx: number): void {
    const x = (xIdx - (xValues.length - 1) / 2) * spacing;
    const y = yIdx * spacing;
    const z = (zIdx - (zValues.length - 1) / 2) * spacing;

    const mesh = data.status === "measured" ? createMeasuredCell(data) : createLegalCell();

    mesh.position.set(x, y, z);
    mesh.userData = { ...mesh.userData, cellKey: key };
    scene.add(mesh);
    cells.set(key, mesh);
  }

  function createMeasuredCell(data: CellData): THREE.Mesh {
    const height = pillarHeight(data);
    const color = ARM_COLORS[data.coordinate.credit] || PALETTE.gradient;

    const geometry = new THREE.BoxGeometry(cellSize, height, cellSize);
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

    const glowGeometry = new THREE.BoxGeometry(cellSize * 1.1, height * 1.1, cellSize * 1.1);
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

  function createLegalCell(): THREE.LineSegments {
    const geometry = new THREE.BoxGeometry(cellSize, cellSize, cellSize);
    const edges = new THREE.EdgesGeometry(geometry);
    edges.translate(0, cellSize / 2, 0);
    const material = new THREE.LineBasicMaterial({
      color: PALETTE.legal_unmeasured,
      transparent: true,
      opacity: 0.55,
    });
    const mesh = new THREE.LineSegments(edges, material);

    const pick = new THREE.Mesh(new THREE.BoxGeometry(cellSize, cellSize, cellSize), new THREE.MeshBasicMaterial());
    pick.position.y = cellSize / 2;
    pick.visible = false;
    mesh.add(pick);

    return mesh;
  }

  function disposeMesh(mesh: THREE.Object3D): void {
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

  function voidMarkerPositions(xIdx: number, yIdx: number, zIdx: number): number[] {
    const x = (xIdx - (xValues.length - 1) / 2) * spacing;
    const y = yIdx * spacing;
    const z = (zIdx - (zValues.length - 1) / 2) * spacing;
    const size = cellSize * 0.6;
    const lift = 0.1;
    return [
      x - size, y + lift, z - size,
      x + size, y + lift, z + size,
      x + size, y + lift, z - size,
      x - size, y + lift, z + size,
    ];
  }

  function createVoidMarkers(positions: number[]): void {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    const material = new THREE.LineBasicMaterial({
      color: PALETTE.void,
      transparent: true,
      opacity: 0.32,
    });
    voidMesh = new THREE.LineSegments(geometry, material);
    scene.add(voidMesh);
  }

  function frameGrid(): void {
    if (xValues.length === 0 || zValues.length === 0) return;

    const halfX = ((xValues.length - 1) * spacing) / 2 + cellSize;
    const halfZ = ((zValues.length - 1) * spacing) / 2 + cellSize;
    const top = (yValues.length - 1) * spacing + cellSize;
    const front = halfZ + 1.8;
    const floor = -0.8;

    frameBox(
      { camera, controls } as any,
      new THREE.Vector3(-halfX, floor, -halfZ),
      new THREE.Vector3(halfX, top, front),
      new THREE.Vector3(0, top / 2, 0),
    );
  }

  function clearGrid(): void {
    cells.forEach((mesh) => {
      scene.remove(mesh);
      disposeMesh(mesh);
    });
    cells.clear();
    cellDataMap.clear();
    cellHeights.clear();

    axisLabelMeshes.forEach((mesh) => {
      scene.remove(mesh);
      disposeMesh(mesh);
    });
    axisLabelMeshes.length = 0;

    if (voidMesh) {
      scene.remove(voidMesh);
      voidMesh.geometry.dispose();
      if (Array.isArray(voidMesh.material)) {
        voidMesh.material.forEach((m) => m.dispose());
      } else {
        voidMesh.material.dispose();
      }
      voidMesh = null;
    }
  }

  function applyAggregates(): void {
    if (!visible || !runId) return;

    const metrics = metricsStore.get(runId);
    if (!metrics) return;

    // Re-aggregate from metrics records
    const aggregates = new Map<string, any>();
    const records = metrics.records ?? [];
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
      if (typeof payload.walltime_s === "number") aggregate.walltime.push(payload.walltime_s);
      if (typeof payload.param_count === "number") aggregate.params.push(payload.param_count);
      if (Array.isArray(payload.convergence_curve)) {
        const curve = payload.convergence_curve
          .filter(
            (point: any) =>
              typeof point?.epoch === "number" && typeof point?.val_acc === "number",
          )
          .map((point: any) => ({ epoch: point.epoch, val_acc: point.val_acc }));
        if (curve.length > 0) aggregate.curves.push(curve);
      }
      if (metrics.pareto?.[idx]) aggregate.pareto = true;
    });

    aggregates.forEach((aggregate, key) => {
      const cellData = cellDataMap.get(key);
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
      cellData.chance = 0.1;
      cellData.requiredSeeds = 0;
      cellData.runId = runId;
      updateCellVisual(key, cellData, aggregate.pareto);
    });
  }

  function mean(values: number[]): number {
    if (values.length === 0) return 0;
    return values.reduce((sum, v) => sum + v, 0) / values.length;
  }

  function stddev(values: number[]): number {
    if (values.length < 2) return 0;
    const m = mean(values);
    const variance = values.reduce((sum, v) => sum + (v - m) ** 2, 0) / (values.length - 1);
    return Math.sqrt(variance);
  }

  function meanCurve(curves: any[][]): any[] {
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

  function pillarHeight(data: CellData): number {
    return THREE.MathUtils.lerp(0.4, 3.4, data.metrics?.val_acc ?? 0);
  }

  function updateCellVisual(key: string, data: CellData, isPareto: boolean): void {
    const oldMesh = cells.get(key);
    if (!oldMesh) return;

    const position = oldMesh.position.clone();
    const glow = oldMesh.userData.glow;
    if (glow) oldMesh.remove(glow);

    scene.remove(oldMesh);
    disposeMesh(oldMesh);

    const newMesh = createMeasuredCell(data);
    newMesh.position.copy(position);
    newMesh.userData.cellKey = key;

    const target = pillarHeight(data);
    const previous = cellHeights.get(key) ?? 0;
    cellHeights.set(key, target);
    newMesh.scale.y = target > 0 ? Math.min(1, Math.max(previous / target, 0.001)) : 1;

    if (isPareto) {
      const ringGeometry = new THREE.RingGeometry(cellSize * 0.6, cellSize * 0.8, 32);
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

    scene.add(newMesh);
    cells.set(key, newMesh);
  }

  function selectCell(key: string): void {
    selectedCell = key;
    const data = cellDataMap.get(key);
    if (data) {
      window.dispatchEvent(new CustomEvent("cell-selected", { detail: data }));
    }
  }

  function update(delta: number): void {
    if (!visible) {
      hideReadout();
      return;
    }

    const ease = 1 - Math.exp(-delta * 8);
    cells.forEach((mesh, key) => {
      const data = cellDataMap.get(key);
      if (data?.status === "measured" && mesh instanceof THREE.Mesh && mesh.material instanceof THREE.MeshStandardMaterial) {
        if (mesh.scale.y < 1) {
          mesh.scale.y = Math.min(1, mesh.scale.y + (1 - mesh.scale.y) * ease);
        }
        const glow = mesh.userData.glow;
        if (glow) {
          glow.material.opacity = 0.1 + 0.1 * Math.sin(Date.now() * 0.003);
        }
        const ring = mesh.userData.paretoRing;
        if (ring) {
          ring.material.opacity = 0.4 + 0.2 * Math.sin(Date.now() * 0.005);
        }
      }
    });

    // Raycast for hover
    const canvas = renderer.domElement;
    const rect = canvas.getBoundingClientRect();
    mouse.x = ((pointerX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((pointerY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    raycaster.params.Line.threshold = cellSize * 0.2;
    const intersects = raycaster.intersectObjects(Array.from(cells.values()), true);

    let key: string | null = null;
    if (intersects.length > 0) {
      key = pickCell(intersects);
    }
    if (!key) {
      key = voidCellUnderCursor();
    }

    if (key !== hoveredCell) {
      if (hoveredCell) highlightCell(hoveredCell, false);
      hoveredCell = key;
      if (key) highlightCell(key, true);
    }

    const hovered = key ? cellDataMap.get(key) : undefined;
    if (hovered) {
      showReadout(hovered);
    } else {
      hideReadout();
    }
  }

  function pickCell(intersects: THREE.Intersection[]): string | null {
    let nearest: string | null = null;
    for (const hit of intersects) {
      const key = hit.object.userData.cellKey || hit.object.parent?.userData.cellKey;
      if (!key) continue;
      nearest ??= key;
      if (cellDataMap.get(key)?.status === "measured") {
        return key;
      }
    }
    return nearest;
  }

  function voidCellUnderCursor(): string | null {
    if (!voidMesh) return null;
    const threshold = raycaster.params.Line.threshold;
    raycaster.params.Line.threshold = cellSize * 0.3;
    try {
      const hits = raycaster.intersectObject(voidMesh, false);
      if (hits.length === 0) return null;
      return cellAt(hits[0].point);
    } finally {
      raycaster.params.Line.threshold = threshold;
    }
  }

  function cellAt(point: THREE.Vector3): string | null {
    const xIdx = Math.round(point.x / spacing + (xValues.length - 1) / 2);
    const yIdx = Math.round(point.y / spacing);
    const zIdx = Math.round(point.z / spacing + (zValues.length - 1) / 2);
    if (xIdx < 0 || xIdx >= xValues.length) return null;
    if (yIdx < 0 || yIdx >= yValues.length) return null;
    if (zIdx < 0 || zIdx >= zValues.length) return null;
    return cellKey(xValues[xIdx], yValues[yIdx], zValues[zIdx]);
  }

  function highlightCell(key: string, highlight: boolean): void {
    const mesh = cells.get(key);
    if (!mesh) return;

    const canvas = renderer.domElement;
    if (canvas) {
      canvas.style.cursor = highlight && isCellActionable(key) ? "pointer" : "grab";
    }

    if (mesh instanceof THREE.Mesh && mesh.material instanceof THREE.MeshStandardMaterial) {
      if (highlight) {
        mesh.userData.originalEmissive = mesh.material.emissiveIntensity;
        mesh.userData.originalScale = mesh.scale.y;
        mesh.material.emissiveIntensity = (mesh.userData.originalEmissive || 0.5) + 0.5;
        mesh.scale.y = Math.min(1.05, mesh.scale.y * 1.08);
      } else {
        if (mesh.userData.originalEmissive !== undefined) {
          mesh.material.emissiveIntensity = mesh.userData.originalEmissive;
        }
        if (mesh.userData.originalScale !== undefined) {
          mesh.scale.y = mesh.userData.originalScale;
        }
      }
      return;
    }

    if (mesh instanceof THREE.LineSegments && mesh.material instanceof THREE.LineBasicMaterial) {
      if (highlight) {
        mesh.userData.originalOpacity = mesh.material.opacity;
        mesh.material.opacity = 0.95;
        mesh.material.linewidth = 2;
      } else if (mesh.userData.originalOpacity !== undefined) {
        mesh.material.opacity = mesh.userData.originalOpacity;
        mesh.material.linewidth = 1;
      }
    }
  }

  function isCellActionable(key: string): boolean {
    const data = cellDataMap.get(key);
    if (!data) return false;
    return data.status === "legal" || data.status === "measured";
  }

  // Event handlers for mouse interaction
  function onMouseMove(event: MouseEvent): void {
    pointerX = event.clientX;
    pointerY = event.clientY;
  }

  function onMouseLeave(): void {
    hideReadout();
  }

  function onClick(): void {
    if (hoveredCell) {
      selectCell(hoveredCell);
    }
  }

  // Mount: attach event listeners
  function mount(): void {
    const canvas = renderer.domElement;
    canvas.addEventListener("mousemove", onMouseMove);
    canvas.addEventListener("mouseleave", onMouseLeave);
    canvas.addEventListener("click", onClick);
  }

  // Resize: update camera aspect and renderer size
  function resize(size: Size): void {
    camera.aspect = size.width / size.height;
    camera.updateProjectionMatrix();
    renderer.setSize(size.width, size.height);
    flat.resize(size);
  }

  // Refresh: handle data/view/resize changes
  function refresh(change: StageChange): void {
    if (change.runId && change.runId !== runId) {
      runId = change.runId;
      resubscribe();
    }
    if (change.kind === "data" || change.kind === "resize") {
      applyAxes();
    }
  }

  function ready(): boolean {
    // Consider ready once grid is built; cellHeights populated after metrics arrive
    return cells.size > 0;
  }

  // Dispose: clean up everything
  function dispose(): void {
    frameUnsub?.();
    workspaceUnsub?.();
    metricsUnsub?.();
    spaceUnsub?.();

    const canvas = renderer.domElement;
    canvas.removeEventListener("mousemove", onMouseMove);
    canvas.removeEventListener("mouseleave", onMouseLeave);
    canvas.removeEventListener("click", onClick);

    clearGrid();
    readoutElement?.remove();
  }

  return {
    mount,
    init,
    resize,
    refresh,
    ready,
    dispose,
    getMeasuredCells(): number {
      let measuredCount = 0;
      let legalCount = 0;
      cellDataMap.forEach((data) => {
        if (data.status === "measured" && data.metrics?.n_seeds) {
          measuredCount++;
        } else if (data.status === "legal" && data.metrics) {
          // Count legal cells that have metrics (transitional state)
          measuredCount++;
        } else if (data.status === "legal") {
          legalCount++;
        }
      });
      // Fallback to legal count if no measured cells yet (for probe compatibility)
      return measuredCount > 0 ? measuredCount : legalCount;
    },
    cells(): unknown[] {
      return Array.from(cellDataMap.values());
    },
  };
}

/** Register the space view definition. */
export const spaceViewDefinition: StageViewDefinition = {
  view: "space",
  title: "Space",
  key: "1",
  group: "the space",
  create: createSpaceView,
};