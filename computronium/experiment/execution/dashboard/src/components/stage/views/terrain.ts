/** Terrain stage view — the space as a heightfield (TODO72 P6). */

import * as THREE from "three";
import { ARM_COLORS, PALETTE } from "../../../colors.js";
import { frameBox } from "../../../stores/framing.js"
import { metricsStore } from "../../../stores/metrics.js";
import { spaceStore } from "../../../stores/space.js";
import { workspaceStore } from "../../../stores/workspace.js";
import { aggregateRecords, cellKey, mean, type AxisSelection } from "../../../stores/payloads.js";
import { createTextSprite } from "../../../stores/sprites.js";
import type {
  StageViewDefinition,
  StageViewInstance,
  StageViewContext,
  StageChange,
  Size,
} from "../../../layout/types.js";

/** How tall the best cell stands. */
const MAX_HEIGHT = 3.4;
/** How deep a crater the system's refusals dig. */
const PIT_DEPTH = 1.1;
/** The distance between two columns of the surface. */
const SPACING = 1.15;
/** The angle the terrain is seen from: low enough for the relief to read. */
const VIEW_DIRECTION = new THREE.Vector3(0.34, 0.4, 0.85);

type ColumnStatus = "measured" | "gap" | "void";

interface Column {
  status: ColumnStatus;
  accuracy: number;
  arm: string;
  x: number;
  y: number;
}

/** Create a StageViewInstance for the "terrain" view. */
export function createTerrainView(context: StageViewContext): StageViewInstance {
  const { surface, workspace, state } = context;

  // Per-instance state derived from state + workspace
  let runId = (state as any).runId ?? workspace.getSelectedRunId();
  let axes = (state as any).axes ?? workspace.getAxes();

  // Three.js objects owned by this view instance
  const scene = surface.three.scene;
  const camera = surface.three.camera;
  const controls = surface.three.controls;
  const renderer = surface.three.renderer;
  const sceneGroup = new THREE.Group();

  // Subscriptions
  let workspaceUnsub: (() => void) | null = null;
  let metricsUnsub: (() => void) | null = null;
  let spaceUnsub: (() => void) | null = null;

  // View state
  let visible = false;
  let drawn = false;
  let framed = false;

  async function init(): Promise<void> {
    scene.add(sceneGroup);

    // Subscribe to workspace changes
    workspaceUnsub = workspace.onChange(() => {
      const newRunId = workspace.getSelectedRunId();
      const newAxes = workspace.getAxes();
      if (newRunId !== runId || newAxes.x !== axes.x || newAxes.y !== axes.y || newAxes.z !== axes.z) {
        runId = newRunId;
        axes = newAxes;
        updateSubscriptions();
        redraw();
      }
    });

    // Subscribe to metrics
    if (runId) {
      metricsUnsub = metricsStore.subscribe(runId, () => {
        redraw();
      });
    }

    // Subscribe to space
    await updateSubscriptions();

    visible = true;
    await redraw();
  }

  async function updateSubscriptions(): Promise<void> {
    spaceUnsub?.();
    if (!runId) return;

    const spaceValues: Record<AxisSelection["x"], string[]> = {
      credit: [],
      geometry: [],
      dynamics: [],
      substrate: [],
      plasticity: [],
      update: [],
    };
    spaceUnsub = spaceStore.subscribe(runId, axes, spaceValues, () => {
      redraw();
    });
  }

  function redraw(): void {
    if (!visible) return;
    draw(true);
  }

  function draw(force: boolean): void {
    const { columns, xValues, yValues } = computeColumns();
    if (columns.length === 0) {
      drawn = false;
      clear();
      return;
    }

    clear();

    const maxAccuracy = Math.max(
      ...columns.map((column) => column.accuracy),
      0.0001,
    );

    const positions: number[] = [];
    const colors: number[] = [];
    const indices: number[] = [];

    columns.forEach((column) => {
      // The height of the ground at this column: a measured cell stands up
      // by its accuracy, a gap is flat, and a refused column is a crater.
      const height =
        column.status === "measured"
          ? (column.accuracy / maxAccuracy) * MAX_HEIGHT
          : column.status === "void"
            ? -PIT_DEPTH
            : 0;
      positions.push(column.x, height, column.y);

      const color = new THREE.Color(
        column.status === "measured"
          ? ARM_COLORS[column.arm] || PALETTE.gradient
          : column.status === "void"
            ? PALETTE.void
            : PALETTE.border_bright,
      );
      if (column.status === "measured") {
        // The higher the cell, the brighter it burns.
        const shade = 0.6 + 0.4 * (column.accuracy / maxAccuracy);
        color.multiplyScalar(shade);
      } else if (column.status === "void") {
        color.multiplyScalar(0.55);
      }
      colors.push(color.r, color.g, color.b);
    });

    const nx = xValues.length;
    const ny = yValues.length;
    for (let xi = 0; xi < nx - 1; xi += 1) {
      for (let yi = 0; yi < ny - 1; yi += 1) {
        const a = xi * ny + yi;
        const b = (xi + 1) * ny + yi;
        const c = (xi + 1) * ny + yi + 1;
        const d = xi * ny + yi + 1;
        // Wound so that the surface faces up.
        indices.push(a, d, b, b, d, c);
      }
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(positions, 3),
    );
    geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
    geometry.setIndex(indices);
    geometry.computeVertexNormals();

    const surfaceMesh = new THREE.Mesh(
      geometry,
      new THREE.MeshStandardMaterial({
        vertexColors: true,
        roughness: 0.7,
        metalness: 0.1,
        side: THREE.DoubleSide,
      }),
    );
    sceneGroup.add(surfaceMesh);

    addVoidMarkers(columns);
    addLabels(xValues, yValues);

    // The terrain is only worth looking at when the run measured something.
    drawn = columns.some((column) => column.status === "measured");
    if (force || !framed) {
      frame(columns, xValues, yValues);
      framed = true;
    }
  }

  function computeColumns(): { columns: Column[]; xValues: string[]; yValues: string[] } {
    const metrics = runId ? metricsStore.get(runId) : null;
    const space = runId ? spaceStore.get(runId, axes, {
      credit: [],
      geometry: [],
      dynamics: [],
      substrate: [],
      plasticity: [],
      update: [],
    }) : null;
    if (!space) return { columns: [], xValues: [], yValues: [] };

    const axesData = axes;
    const spaceValues = space.values as Record<string, string[]>;
    const xValues = spaceValues[axesData.x] ?? [];
    const yValues = spaceValues[axesData.y] ?? [];
    const zValues = spaceValues[axesData.z] ?? [];

    // We need aggregates from metrics
    let aggregates = new Map<string, any>();
    if (metrics) {
      aggregates = aggregateRecords(metrics, axesData);
    }

    const columns: Column[] = [];
    xValues.forEach((x, xi) => {
      yValues.forEach((y, yi) => {
        let voidCells = 0;
        let legalCells = 0;
        let best = -Infinity;
        let arm = "";
        zValues.forEach((z) => {
          const key = cellKey(x, y, z);
          const cell = space.cells.find((c: any) => {
            const coord = c.coordinate;
            return coord[axesData.x] === x && coord[axesData.y] === y && coord[axesData.z] === z;
          });
          if (cell?.status === "void") {
            voidCells += 1;
            return;
          }
          legalCells += 1;
          const aggregate = aggregates.get(key);
          if (!aggregate || aggregate.acc.length === 0) return;
          const accuracy = mean(aggregate.acc);
          if (accuracy > best) {
            best = accuracy;
            arm = aggregate.coordinate.credit ?? "";
          }
        });

        const status: ColumnStatus =
          voidCells > 0 && legalCells === 0
            ? "void"
            : best > -Infinity
              ? "measured"
              : "gap";
        columns.push({
          status,
          accuracy: best > -Infinity ? best : 0,
          arm,
          x: (xi - (xValues.length - 1) / 2) * SPACING,
          y: (yi - (yValues.length - 1) / 2) * SPACING,
        });
      });
    });
    return { columns, xValues, yValues };
  }

  function clear(): void {
    [...sceneGroup.children].forEach((child) => {
      sceneGroup.remove(child);
      disposeObject(child);
    });
  }

  function disposeObject(obj: THREE.Object3D): void {
    obj.traverse((child) => {
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

  function addVoidMarkers(columns: Column[]): void {
    const positions: number[] = [];
    const size = 0.22;
    columns.forEach((column) => {
      if (column.status !== "void") return;
      positions.push(
        column.x - size,
        -PIT_DEPTH + 0.02,
        column.y - size,
        column.x + size,
        -PIT_DEPTH + 0.02,
        column.y + size,
        column.x + size,
        -PIT_DEPTH + 0.02,
        column.y - size,
        column.x - size,
        -PIT_DEPTH + 0.02,
        column.y + size,
      );
    });
    if (positions.length === 0) return;

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(positions, 3),
    );
    sceneGroup.add(
      new THREE.LineSegments(
        geometry,
        new THREE.LineBasicMaterial({
          color: PALETTE.void,
          transparent: true,
          opacity: 0.75,
        }),
      ),
    );
  }

  function addLabels(xValues: string[], yValues: string[]): void {
    const nameMaterial = new THREE.SpriteMaterial({
      color: 0xc9d4e0,
      sizeAttenuation: true,
    });

    const halfX = ((xValues.length - 1) * SPACING) / 2;
    const halfZ = ((yValues.length - 1) * SPACING) / 2;

    const xSprite = createTextSprite(axes.x, 0.22, nameMaterial);
    xSprite.position.set(halfX + 1.0, -0.2, halfZ + 0.9);
    sceneGroup.add(xSprite);

    const zSprite = createTextSprite(axes.y, 0.22, nameMaterial);
    zSprite.position.set(-halfX - 1.0, 0.2, -halfZ);
    sceneGroup.add(zSprite);
  }

  function frame(columns: Column[], xValues: string[], yValues: string[]): void {
    if (!scene || columns.length === 0) return;

    const halfX = ((xValues.length - 1) * SPACING) / 2;
    const halfZ = ((yValues.length - 1) * SPACING) / 2;

    frameBox(
      { camera, controls } as any,
      new THREE.Vector3(-halfX - 1.2, -PIT_DEPTH - 0.3, -halfZ),
      new THREE.Vector3(halfX + 1.2, MAX_HEIGHT, halfZ + 1.4),
      new THREE.Vector3(0, MAX_HEIGHT / 3, 0),
      VIEW_DIRECTION,
    );
  }

  // Mount
  function mount(): void {
    // No event listeners needed
  }

  // Resize
  function resize(size: Size): void {
    camera.aspect = size.width / size.height;
    camera.updateProjectionMatrix();
    renderer.setSize(size.width, size.height);
  }

  // Refresh
  function refresh(change: StageChange): void {
    if (change.kind === "data" || change.kind === "resize") {
      redraw();
    }
  }

  function ready(): boolean {
    return drawn;
  }

  // Dispose
  function dispose(): void {
    workspaceUnsub?.();
    metricsUnsub?.();
    spaceUnsub?.();
    scene.remove(sceneGroup);
    disposeObject(sceneGroup);
  }

  // Initialize
  init();

  return {
    init,
    mount,
    resize,
    refresh,
    ready,
    dispose,
  };
}

/** Register the terrain view definition. */
export const terrainViewDefinition: StageViewDefinition = {
  view: "terrain",
  title: "Terrain",
  key: "shift+y",
  group: "the run",
  create: createTerrainView,
};