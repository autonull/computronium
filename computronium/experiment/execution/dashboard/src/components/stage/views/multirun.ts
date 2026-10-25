/** Multirun stage view — several runs' evidence in one space (TODO72 P6). */

import * as THREE from "three";
import { PALETTE } from "../../../colors.js";
import { frameBox } from "../../../stage/framing.js"
import { multiRunStore } from "../../../stores/multirun.js";
import { workspaceStore } from "../../../stores/workspace.js";
import { cellKey, type AxisSelection } from "../../../stage/payloads.js";
import { createTextSprite } from "../../../stage/sprites.js";
import type {
  StageViewDefinition,
  StageViewInstance,
  StageViewContext,
  StageChange,
  Size,
} from "../../../layout/types.js";
import type { MultiRunSpace } from "../../../stage/payloads.js";

/** The colours the runs are told apart by. */
const RUN_COLORS = ["#58a6ff", "#d4a843", "#3fb950", "#f78166"];
/** The distance between two cells of the space. */
const SPACING = 1.15;
/** The side of one cell. */
const CELL = 1.0;
/** How tall the best cell stands. */
const MAX_HEIGHT = 1.5;
/** The angle the space is seen from: low enough for the runs' cells to stand up. */
const VIEW_DIRECTION = new THREE.Vector3(0.34, 0.4, 0.85);

/** Create a StageViewInstance for the "multirun" view. */
export function createMultirunView(context: StageViewContext): StageViewInstance {
  const { surface, workspace, state } = context;

  // Per-instance state derived from state + workspace
  let axes = (state as any).axes ?? workspace.getAxes();

  // Three.js objects owned by this view instance
  const scene = surface.three.scene;
  const camera = surface.three.camera;
  const controls = surface.three.controls;
  const renderer = surface.three.renderer;
  const sceneGroup = new THREE.Group();

  let legendElement: HTMLElement | null = null;

  // Subscriptions
  let workspaceUnsub: (() => void) | null = null;
  let multirunUnsub: (() => void) | null = null;

  // View state
  let visible = false;
  let drawn = false;
  let framed = false;

  async function init(): Promise<void> {
    scene.add(sceneGroup);

    // Subscribe to workspace changes (axes)
    workspaceUnsub = workspace.onChange(() => {
      const newAxes = workspace.getAxes();
      if (newAxes.x !== axes.x || newAxes.y !== axes.y || newAxes.z !== axes.z) {
        axes = newAxes;
        load();
      }
    });

    // Subscribe to multirun space
    await load();

    visible = true;
  }

  async function load(): Promise<void> {
    // The store fetches when subscribed
    const space = multiRunStore.get(axes);
    if (!space || space.runs.length === 0) {
      drawn = false;
      clear();
      return;
    }
    draw(true);
  }

  function draw(force: boolean): void {
    const space = multiRunStore.get(axes);
    if (!space || space.runs.length === 0) {
      drawn = false;
      clear();
      return;
    }

    clear();
    const { tiles, blocks, xValues, yValues, zValues, labelled } = computeCells(space);

    addGround(tiles);
    addBlocks(blocks);
    addLabels(xValues, yValues.length, zValues.length, labelled);

    drawn = blocks.length > 0;
    buildLegend(space);
    if (force || !framed) {
      frame(xValues.length, yValues.length, zValues.length);
      framed = true;
    }
  }

  function clear(): void {
    [...sceneGroup.children].forEach((child) => {
      sceneGroup.remove(child);
      disposeObject(child);
    });
    legendElement?.remove();
    legendElement = null;
    // Show the arms block again
    const arms = document.getElementById("legend-arms-block");
    if (arms) arms.style.display = "";
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

  function computeCells(space: MultiRunSpace): {
    tiles: { x: number; y: number; z: number }[];
    blocks: {
      x: number;
      y: number;
      z: number;
      color: string;
      height: number;
    }[];
    xValues: string[];
    yValues: string[];
    zValues: string[];
    labelled: Set<string>;
  } {
    const [xAxis, yAxis, zAxis] = space.axes;
    const xValues = space.values[xAxis] ?? [];
    const yValues = space.values[yAxis] ?? [];
    const zValues = space.values[zAxis] ?? [];

    // Where each run's cells sit, and how well they did.
    const placements: {
      xi: number;
      yi: number;
      zi: number;
      runIndex: number;
      accuracy: number;
    }[] = [];
    const labelled = new Set<string>();
    let best = 0.0001;
    space.runs.forEach((run, runIndex) => {
      Object.entries(run.measured).forEach(([key, cell]) => {
        const [x, y, z] = key.split("|");
        const xi = xValues.indexOf(x);
        const yi = yValues.indexOf(y);
        const zi = zValues.indexOf(z);
        if (xi < 0 || yi < 0 || zi < 0) return;
        placements.push({ xi, yi, zi, runIndex, accuracy: cell.accuracy });
        labelled.add(x);
        if (cell.accuracy > best) best = cell.accuracy;
      });
    });

    // Two runs that measured the same cell stand side by side in it.
    const totals = new Map<string, number>();
    placements.forEach((placement) => {
      const key = `${placement.xi}|${placement.yi}|${placement.zi}`;
      totals.set(key, (totals.get(key) ?? 0) + 1);
    });
    const seen = new Map<string, number>();
    const blocks = placements.map((placement) => {
      const key = `${placement.xi}|${placement.yi}|${placement.zi}`;
      const index = seen.get(key) ?? 0;
      seen.set(key, index + 1);
      const total = totals.get(key) ?? 1;
      const offset = (index - (total - 1) / 2) * (CELL * 0.5);
      return {
        x: (placement.xi - (xValues.length - 1) / 2) * SPACING + offset,
        y: placement.yi * SPACING,
        z: (placement.zi - (zValues.length - 1) / 2) * SPACING,
        color: RUN_COLORS[placement.runIndex % RUN_COLORS.length],
        height: (placement.accuracy / best) * MAX_HEIGHT,
      };
    });

    // The ground is the union of the runs' windows.
    const allowed = new Set<string>();
    space.runs.forEach((run) => {
      const runValues = [xAxis, yAxis, zAxis].map(
        (axis) => run.values[axis] ?? [],
      );
      const refused = new Set(run.refused);
      xValues.forEach((x) => {
        if (!runValues[0].includes(x)) return;
        runValues[1].forEach((y) => {
          runValues[2].forEach((z) => {
            if (refused.has(cellKey(x, y, z))) return;
            allowed.add(cellKey(x, y, z));
          });
        });
      });
    });

    const tiles: { x: number; y: number; z: number }[] = [];
    xValues.forEach((x, xi) => {
      yValues.forEach((y, yi) => {
        zValues.forEach((z, zi) => {
          if (!allowed.has(cellKey(x, y, z))) return;
          tiles.push({
            x: (xi - (xValues.length - 1) / 2) * SPACING,
            y: yi * SPACING,
            z: (zi - (zValues.length - 1) / 2) * SPACING,
          });
        });
      });
    });

    return { tiles, blocks, xValues, yValues, zValues, labelled };
  }

  function addGround(tiles: { x: number; y: number; z: number }[]): void {
    if (tiles.length === 0) return;
    const half = CELL / 2;
    const positions: number[] = [];
    const indices: number[] = [];
    tiles.forEach((tile, index) => {
      positions.push(
        tile.x - half,
        tile.y,
        tile.z - half,
        tile.x + half,
        tile.y,
        tile.z - half,
        tile.x + half,
        tile.y,
        tile.z + half,
        tile.x - half,
        tile.y,
        tile.z + half,
      );
      const base = index * 4;
      indices.push(base, base + 2, base + 1, base, base + 3, base + 2);
    });

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(positions, 3),
    );
    geometry.setIndex(indices);
    geometry.computeVertexNormals();

    sceneGroup.add(
      new THREE.Mesh(
        geometry,
        new THREE.MeshBasicMaterial({
          color: new THREE.Color(PALETTE.border),
          side: THREE.DoubleSide,
        }),
      ),
    );
  }

  function addBlocks(
    blocks: {
      x: number;
      y: number;
      z: number;
      color: string;
      height: number;
    }[],
  ): void {
    const perCell = new Map<string, number>();
    blocks.forEach((block) => {
      const key = `${block.x}|${block.y}|${block.z}`;
      const index = perCell.get(key) ?? 0;
      perCell.set(key, index + 1);
      const total = perCell.size;
      const offset = (index - (total - 1) / 2) * (CELL * 0.5);
      const height = Math.max(block.height, 0.12);
      const geometry = new THREE.BoxGeometry(CELL * 0.45, height, CELL * 0.45);
      geometry.translate(0, height / 2, 0);
      const material = new THREE.MeshStandardMaterial({
        color: new THREE.Color(block.color),
        emissive: new THREE.Color(block.color),
        emissiveIntensity: 0.45,
        transparent: true,
        opacity: 0.95,
        metalness: 0.2,
        roughness: 0.4,
      });
      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.set(block.x + offset, block.y, block.z);
      sceneGroup.add(mesh);
    });
  }

  function addLabels(
    xValues: string[],
    yCount: number,
    zCount: number,
    labelled: Set<string>,
  ): void {
    const nameMaterial = new THREE.SpriteMaterial({
      color: 0xc9d4e0,
      sizeAttenuation: true,
    });
    const valueMaterial = new THREE.SpriteMaterial({
      color: 0x8b98a8,
      sizeAttenuation: true,
    });

    const halfX = ((xValues.length - 1) * SPACING) / 2;
    const halfZ = ((zCount - 1) * SPACING) / 2;

    // Only the values a run measured are named.
    xValues.forEach((value, index) => {
      if (!labelled.has(value)) return;
      const sprite = createTextSprite(
        value,
        0.26,
        valueMaterial,
        SPACING * 0.9,
      );
      sprite.position.set(
        (index - (xValues.length - 1) / 2) * SPACING,
        -0.45,
        halfZ + 1.1,
      );
      sceneGroup.add(sprite);
    });

    const space = multiRunStore.get(axes);
    const [xAxis, yAxis, zAxis] = space?.axes ?? ["", "", ""];

    const xSprite = createTextSprite(xAxis, 0.24, nameMaterial);
    xSprite.position.set(halfX + 1.0, -0.4, halfZ + 1.1);
    sceneGroup.add(xSprite);

    const zSprite = createTextSprite(zAxis, 0.24, nameMaterial);
    zSprite.position.set(0, -0.4, halfZ + 2.0);
    sceneGroup.add(zSprite);

    const ySprite = createTextSprite(yAxis, 0.24, nameMaterial);
    ySprite.position.set(-halfX - 1.3, (yCount - 1) * SPACING * 0.5, 0);
    sceneGroup.add(ySprite);
  }

  function buildLegend(space: MultiRunSpace): void {
    const host = document.getElementById("discovery-legend");
    if (!host) return;
    legendElement?.remove();

    // Hide the map's own arms block.
    const arms = document.getElementById("legend-arms-block");
    if (arms) arms.style.display = "none";

    const block = document.createElement("div");
    block.id = "legend-runs";
    block.style.cssText =
      "margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border);";

    const heading = document.createElement("div");
    heading.textContent = "Runs";
    heading.style.cssText = "font-weight: 600; margin-bottom: 8px;";
    block.appendChild(heading);

    space.runs.forEach((run, index) => {
      const color = RUN_COLORS[index % RUN_COLORS.length];
      const cells = Object.keys(run.measured).length;
      const row = document.createElement("div");
      row.style.cssText =
        "display: flex; align-items: center; gap: 8px; margin-bottom: 6px; font-size: 11px;";
      const swatch = document.createElement("span");
      swatch.style.cssText = `width: 14px; height: 14px; background: ${color}; border-radius: 3px;`;
      const label = document.createElement("span");
      label.style.color = "var(--text-secondary)";
      label.textContent = `${run.profile ?? run.run_id.slice(0, 8)} · ${cells} cells · ${run.records} records`;
      row.appendChild(swatch);
      row.appendChild(label);
      block.appendChild(row);
    });

    const note = document.createElement("div");
    note.textContent = space.summary;
    note.style.cssText =
      "font-size: 11px; color: var(--text-muted); margin-top: 6px;";
    block.appendChild(note);

    host.appendChild(block);
    legendElement = block;
  }

  function frame(xCount: number, yCount: number, zCount: number): void {
    if (!scene || xCount === 0) return;

    const halfX = ((xCount - 1) * SPACING) / 2 + 0.6;
    const halfZ = ((zCount - 1) * SPACING) / 2 + 0.6;
    const top = (yCount - 1) * SPACING + 0.8;

    frameBox(
      { controls } as any,
      new THREE.Vector3(-halfX, -0.8, -halfZ),
      new THREE.Vector3(halfX, top, halfZ + 1.8),
      new THREE.Vector3(0, top / 3, 0),
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
    if (change.kind === "data" || change.kind === "resize" || change.kind === "selection" || change.kind === "view") {
      // For multirun, axes changes are handled via workspace subscription
      load();
    }
  }

  function ready(): boolean {
    return drawn;
  }

  // Dispose
  function dispose(): void {
    workspaceUnsub?.();
    multirunUnsub?.();
    scene.remove(sceneGroup);
    disposeObject(sceneGroup);
    legendElement?.remove();
    const arms = document.getElementById("legend-arms-block");
    if (arms) arms.style.display = "";
  }

  // Initialize
  init();

  return {
    mount,
    resize,
    refresh,
    ready,
    dispose,
  };
}

/** Register the multirun view definition. */
export const multirunViewDefinition: StageViewDefinition = {
  view: "multirun",
  title: "The multi-run space",
  key: "u",
  group: "the space",
  create: createMultirunView,
};