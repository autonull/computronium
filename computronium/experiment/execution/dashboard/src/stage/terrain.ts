/** The terrain — the space as a heightfield (TODO69 Phase 5).

    The discovery map draws the space as a field of cubes: a gap is a
    wireframe box, a measured cell is a glowing pillar. The terrain draws
    the same space as a surface — accuracy is the height, the gaps are flat
    ground, and the cells the system refuses are craters in it. The
    arithmetic is the map's; only the geometry is different.
*/

import * as THREE from "three";
import { getSceneContext } from "../components/context.js";
import { ARM_COLORS, PALETTE } from "../colors.js";
import { frameBox } from "./framing.js";
import { disposeObject } from "./scene.js";
import { cellKey, mean, stageState } from "./store.js";
import { createTextSprite } from "./sprites.js";
import type { StageView, ViewGroup } from "./views.js";

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

export class TerrainView implements StageView {
  id = "terrain";
  name = "Terrain";
  group = "the run" as ViewGroup;
  caption =
    "The space as a heightfield: accuracy is the height, the gaps are flat, the refusals are craters.";

  private sceneGroup = new THREE.Group();
  private visible = false;
  private drawn = false;
  private framed = false;

  enter(): void {
    this.visible = true;
    const context = getSceneContext();
    if (context) context.scene.add(this.sceneGroup);
    this.draw(true);
  }

  exit(): void {
    this.visible = false;
    this.sceneGroup.parent?.remove(this.sceneGroup);
    disposeObject(this.sceneGroup);
    this.sceneGroup = new THREE.Group();
    this.drawn = false;
    this.framed = false;
  }

  refresh(): void {
    if (!this.visible) return;
    this.draw(false);
  }

  ready(): boolean {
    return this.drawn;
  }

  /** The surface's columns: one per (x, y) pair, collapsed over z. */
  private columns(): {
    columns: Column[];
    xValues: string[];
    yValues: string[];
  } {
    const space = stageState.space;
    if (!space) return { columns: [], xValues: [], yValues: [] };

    const axes = stageState.axes;
    const xValues = space.values[axes.x] ?? [];
    const yValues = space.values[axes.y] ?? [];
    const zValues = space.values[axes.z] ?? [];

    const columns: Column[] = [];
    xValues.forEach((x, xi) => {
      yValues.forEach((y, yi) => {
        let voidCells = 0;
        let legalCells = 0;
        let best = -Infinity;
        let arm = "";
        zValues.forEach((z) => {
          const key = cellKey(x, y, z);
          const cell = stageState.spaceCells.get(key);
          if (cell?.status === "void") {
            voidCells += 1;
            return;
          }
          legalCells += 1;
          const aggregate = stageState.aggregates.get(key);
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

  private draw(force: boolean): void {
    const { columns, xValues, yValues } = this.columns();
    if (columns.length === 0) {
      this.drawn = false;
      return;
    }

    this.clear();

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
        // Wound so that the surface faces up: a normal that points into the
        // ground is a surface the light never reaches.
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

    const surface = new THREE.Mesh(
      geometry,
      new THREE.MeshStandardMaterial({
        vertexColors: true,
        roughness: 0.7,
        metalness: 0.1,
        side: THREE.DoubleSide,
      }),
    );
    this.sceneGroup.add(surface);

    this.addVoidMarkers(columns);
    this.addLabels(xValues, yValues);

    // The terrain is only worth looking at when the run measured something:
    // a plain of gaps is a picture of nothing.
    this.drawn = columns.some((column) => column.status === "measured");
    if (force || !this.framed) {
      this.frame(columns, xValues, yValues);
      this.framed = true;
    }
  }

  /** Take the old surface off the stage before the new one goes on. */
  private clear(): void {
    [...this.sceneGroup.children].forEach((child) => {
      this.sceneGroup.remove(child);
      disposeObject(child);
    });
  }

  /** The red cross that marks a column the system refuses. */
  private addVoidMarkers(columns: Column[]): void {
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
    this.sceneGroup.add(
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

  /** The axes, named where they run. The values are the matrix's business. */
  private addLabels(xValues: string[], yValues: string[]): void {
    const nameMaterial = new THREE.SpriteMaterial({
      color: 0xc9d4e0,
      sizeAttenuation: true,
    });

    const halfX = ((xValues.length - 1) * SPACING) / 2;
    const halfZ = ((yValues.length - 1) * SPACING) / 2;

    const xSprite = createTextSprite(stageState.axes.x, 0.22, nameMaterial);
    xSprite.position.set(halfX + 1.0, -0.2, halfZ + 0.9);
    this.sceneGroup.add(xSprite);

    const zSprite = createTextSprite(stageState.axes.y, 0.22, nameMaterial);
    zSprite.position.set(-halfX - 1.0, 0.2, -halfZ);
    this.sceneGroup.add(zSprite);
  }

  private frame(columns: Column[], xValues: string[], yValues: string[]): void {
    const context = getSceneContext();
    if (!context) return;
    if (columns.length === 0) return;

    const halfX = ((xValues.length - 1) * SPACING) / 2;
    const halfZ = ((yValues.length - 1) * SPACING) / 2;
    // The labels stand in front of the surface: the frame has to hold them
    // too, or they end up in the reader's face.
    frameBox(
      context,
      new THREE.Vector3(-halfX - 1.2, -PIT_DEPTH - 0.3, -halfZ),
      new THREE.Vector3(halfX + 1.2, MAX_HEIGHT, halfZ + 1.4),
      new THREE.Vector3(0, MAX_HEIGHT / 3, 0),
      VIEW_DIRECTION,
    );
  }
}
