/** Layers stage view — the space cut into sheets (TODO72 P6). */

import * as THREE from "three";
import { ARM_COLORS, PALETTE } from "../../../colors.js";
import { frameBox } from "../../../stage/framing.js"
import { metricsStore } from "../../../stores/metrics.js";
import { spaceStore } from "../../../stores/space.js";
import { workspaceStore } from "../../../stores/workspace.js";
import { aggregateRecords, cellKey, mean, type AxisSelection } from "../../../stage/payloads.js";
import { wrapLabel } from "../../../stage/sprites.js";
import { createTextSprite } from "../../../stage/sprites.js";
import type {
  StageViewDefinition,
  StageViewInstance,
  StageViewContext,
  StageChange,
  Size,
} from "../../../layout/types.js";

/** The distance between two sheets: enough to see them apart. */
const LAYER_GAP = 1.7;
/** The side of one cell. */
const CELL = 1.0;
/** How far a measured cell stands up off its sheet. */
const PIN_HEIGHT = 0.9;
/** The angle the stack is seen from: from the side, so the layers read. */
const VIEW_DIRECTION = new THREE.Vector3(0.72, 0.24, 0.65);

type CellStatus = "measured" | "gap" | "void";

interface SheetCell {
  status: CellStatus;
  accuracy: number;
  arm: string;
  x: number;
  y: number;
}

interface Sheet {
  value: string;
  height: number;
  cells: SheetCell[];
  measured: number;
}

/** Create a StageViewInstance for the "layers" view. */
export function createLayersView(context: StageViewContext): StageViewInstance {
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
    const { sheets, nx, ny } = computeSheets();
    if (sheets.length === 0) {
      drawn = false;
      clear();
      return;
    }

    clear();

    const structure: number[] = [];
    const structureColors: number[] = [];
    const measured: number[] = [];
    const measuredColors: number[] = [];

    let best = 0;
    sheets.forEach((sheet) => {
      sheet.cells.forEach((cell) => {
        if (cell.status === "measured") {
          best = Math.max(best, cell.accuracy);
        }
      });
    });
    const scale = best > 0 ? best : 1;

    sheets.forEach((sheet) => {
      sheet.cells.forEach((cell) => {
        const color = new THREE.Color(
          cell.status === "measured"
            ? ARM_COLORS[cell.arm] || PALETTE.gradient
            : cell.status === "void"
              ? PALETTE.void
              : PALETTE.border_bright,
        );
        if (cell.status === "measured") {
          color.multiplyScalar(0.65 + 0.35 * (cell.accuracy / scale));
        } else {
          color.multiplyScalar(0.3);
        }
        const target = cell.status === "measured" ? measured : structure;
        const targetColors =
          cell.status === "measured" ? measuredColors : structureColors;
        const half = CELL / 2;
        target.push(
          cell.x - half,
          sheet.height,
          cell.y - half,
          cell.x + half,
          sheet.height,
          cell.y - half,
          cell.x + half,
          sheet.height,
          cell.y + half,
          cell.x - half,
          sheet.height,
          cell.y + half,
        );
        for (let i = 0; i < 4; i += 1) {
          targetColors.push(color.r, color.g, color.b);
        }
      });
    });

    // The sheets the run never entered: a faint ground the lit cells stand
    // out of. They are drawn without depth so they never hide a cell.
    if (structure.length > 0) {
      sceneGroup.add(
        new THREE.Mesh(
          quadGeometry(structure, structureColors),
          new THREE.MeshBasicMaterial({
            vertexColors: true,
            transparent: true,
            opacity: 0.11,
            side: THREE.DoubleSide,
            depthWrite: false,
          }),
        ),
      );
    }

    // The cells the run measured: solid, so they read through the sheets.
    if (measured.length > 0) {
      sceneGroup.add(
        new THREE.Mesh(
          quadGeometry(measured, measuredColors),
          new THREE.MeshBasicMaterial({
            vertexColors: true,
            side: THREE.DoubleSide,
          }),
        ),
      );
    }

    addPins(sheets);
    addSheetEdges(sheets, nx, ny);
    addLabels(sheets, nx, ny);

    drawn = sheets.some((sheet) => sheet.measured > 0);
    if (force || !framed) {
      frame(sheets, nx, ny);
      framed = true;
    }
  }

  function computeSheets(): { sheets: Sheet[]; nx: number; ny: number } {
    const metrics = runId ? metricsStore.get(runId) : null;
    const space = runId ? spaceStore.get(runId, axes, {
      credit: [],
      geometry: [],
      dynamics: [],
      substrate: [],
      plasticity: [],
      update: [],
    }) : null;
    if (!space) return { sheets: [], nx: 0, ny: 0 };

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

    const sheets: Sheet[] = zValues.map((z, zi) => {
      const cells: SheetCell[] = [];
      let measured = 0;
      xValues.forEach((x, xi) => {
        yValues.forEach((y, yi) => {
          const key = cellKey(x, y, z);
          const cell = space.cells.find((c: any) => {
            const coord = c.coordinate;
            return coord[axesData.x] === x && coord[axesData.y] === y && coord[axesData.z] === z;
          });
          const aggregate = aggregates.get(key);
          const accuracy =
            aggregate && aggregate.acc.length > 0 ? mean(aggregate.acc) : 0;
          if (cell?.status === "void") {
            cells.push({
              status: "void",
              accuracy: 0,
              arm: "",
              x: (xi - (xValues.length - 1) / 2) * CELL,
              y: (yi - (yValues.length - 1) / 2) * CELL,
            });
            return;
          }
          if (accuracy > 0) {
            measured += 1;
            cells.push({
              status: "measured",
              accuracy,
              arm: aggregate?.coordinate.credit ?? "",
              x: (xi - (xValues.length - 1) / 2) * CELL,
              y: (yi - (yValues.length - 1) / 2) * CELL,
            });
            return;
          }
          cells.push({
            status: "gap",
            accuracy: 0,
            arm: "",
            x: (xi - (xValues.length - 1) / 2) * CELL,
            y: (yi - (yValues.length - 1) / 2) * CELL,
          });
        });
      });
      return {
    init,
        value: z,
        height: (zi - (zValues.length - 1) / 2) * LAYER_GAP,
        cells,
        measured,
      };
    });
    return { sheets, nx: xValues.length, ny: yValues.length };
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

  function addPins(sheets: Sheet[]): void {
    sheets.forEach((sheet) => {
      sheet.cells.forEach((cell) => {
        if (cell.status !== "measured") return;
        const color = new THREE.Color(ARM_COLORS[cell.arm] || PALETTE.gradient);
        const geometry = new THREE.BoxGeometry(0.22, PIN_HEIGHT, 0.22);
        geometry.translate(0, PIN_HEIGHT / 2, 0);
        const material = new THREE.MeshStandardMaterial({
          color,
          emissive: color,
          emissiveIntensity: 0.55,
          roughness: 0.4,
          metalness: 0.2,
        });
        const pin = new THREE.Mesh(geometry, material);
        pin.position.set(cell.x, sheet.height, cell.y);
        sceneGroup.add(pin);
      });
    });
  }

  function addSheetEdges(sheets: Sheet[], nx: number, ny: number): void {
    const positions: number[] = [];
    const halfX = (nx * CELL) / 2;
    const halfY = (ny * CELL) / 2;
    sheets.forEach((sheet) => {
      const corners: [number, number][] = [
        [-halfX, -halfY],
        [halfX, -halfY],
        [halfX, halfY],
        [-halfX, halfY],
      ];
      corners.forEach((corner, index) => {
        const next = corners[(index + 1) % corners.length];
        positions.push(
          corner[0],
          sheet.height,
          corner[1],
          next[0],
          sheet.height,
          next[1],
        );
      });
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
          color: PALETTE.border_bright,
          transparent: true,
          opacity: 0.65,
        }),
      ),
    );
  }

  function addLabels(sheets: Sheet[], nx: number, ny: number): void {
    const axesData = axes;
    const nameMaterial = new THREE.SpriteMaterial({
      color: 0xc9d4e0,
      sizeAttenuation: true,
    });
    const valueMaterial = new THREE.SpriteMaterial({
      color: 0x8b98a8,
      sizeAttenuation: true,
    });

    const halfX = (nx * CELL) / 2;
    const halfY = (ny * CELL) / 2;

    sheets.forEach((sheet) => {
      const sprite = createTextSprite(sheet.value, 0.26, valueMaterial);
      sprite.position.set(-halfX - 0.85, sheet.height, halfY);
      sceneGroup.add(sprite);
    });

    const zSprite = createTextSprite(axesData.z, 0.28, nameMaterial);
    zSprite.position.set(-halfX - 0.85, sheets.length * LAYER_GAP * 0.5, -halfY);
    sceneGroup.add(zSprite);

    const xSprite = createTextSprite(axesData.x, 0.28, nameMaterial);
    xSprite.position.set(halfX + 0.9, -LAYER_GAP, halfY);
    sceneGroup.add(xSprite);

    const ySprite = createTextSprite(axesData.y, 0.28, nameMaterial);
    ySprite.position.set(halfX + 0.9, -LAYER_GAP, -halfY - 0.6);
    sceneGroup.add(ySprite);
  }

  function frame(sheets: Sheet[], nx: number, ny: number): void {
    if (!scene || sheets.length === 0) return;

    const halfX = (nx * CELL) / 2;
    const halfY = (ny * CELL) / 2;
    const halfStack = (sheets.length * LAYER_GAP) / 2;

    frameBox(
      { camera, controls } as any,
      new THREE.Vector3(-halfX - 1.4, -halfStack - 0.4, -halfY - 0.6),
      new THREE.Vector3(halfX + 1.4, halfStack + 0.4, halfY + 0.6),
      new THREE.Vector3(0, 0, 0),
      VIEW_DIRECTION,
    );
  }

  function quadGeometry(
    positions: number[],
    colors: number[],
  ): THREE.BufferGeometry {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(positions, 3),
    );
    geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
    return geometry;
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

/** Register the layers view definition. */
export const layersViewDefinition: StageViewDefinition = {
  view: "layers",
  title: "Layers",
  key: "y",
  group: "the space",
  create: createLayersView,
};