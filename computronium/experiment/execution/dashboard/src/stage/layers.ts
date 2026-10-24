/** The layers — the space cut into sheets (TODO69 Phase 5).

    The map draws the space as a field of cubes and the terrain draws it
    as a surface. The layers draw it as what it is: a stack of sheets, one
    for each value of the third axis. The sheets the run measured are lit;
    the rest are the space it declared and never entered. A reader sees
    which slab of the space the run filled, and how thin it was.
*/

import * as THREE from "three";
import { getSceneContext } from "../components/context.js";
import { ARM_COLORS, PALETTE } from "../colors.js";
import { frameBox } from "./framing.js";
import { disposeObject } from "./scene.js";
import { cellKey, mean, stageState } from "./store.js";
import { createTextSprite } from "./sprites.js";
import type { StageView, ViewGroup } from "./views.js";

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

/** One sheet: the cells of one value of the stacked axis. */
interface Sheet {
  value: string;
  height: number;
  cells: SheetCell[];
  measured: number;
}

export class LayersView implements StageView {
  id = "layers";
  name = "Layers";
  group = "the space" as ViewGroup;
  key = "y";
  caption =
    "The space cut into sheets: the lit ones are the cells the run measured.";

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

  /** The space, one sheet per value of the stacked axis. */
  private sheets(): { sheets: Sheet[]; nx: number; ny: number } {
    const space = stageState.space;
    if (!space) return { sheets: [], nx: 0, ny: 0 };

    const axes = stageState.axes;
    const xValues = space.values[axes.x] ?? [];
    const yValues = space.values[axes.y] ?? [];
    const zValues = space.values[axes.z] ?? [];

    const sheets: Sheet[] = zValues.map((z, zi) => {
      const cells: SheetCell[] = [];
      let measured = 0;
      xValues.forEach((x, xi) => {
        yValues.forEach((y, yi) => {
          const key = cellKey(x, y, z);
          const cell = stageState.spaceCells.get(key);
          const aggregate = stageState.aggregates.get(key);
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
        value: z,
        height: (zi - (zValues.length - 1) / 2) * LAYER_GAP,
        cells,
        measured,
      };
    });
    return { sheets, nx: xValues.length, ny: yValues.length };
  }

  private draw(force: boolean): void {
    const { sheets, nx, ny } = this.sheets();
    if (sheets.length === 0) {
      this.drawn = false;
      return;
    }

    this.clear();

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
          // The brighter the cell, the better it did.
          color.multiplyScalar(0.65 + 0.35 * (cell.accuracy / scale));
        } else {
          // The space the run did not enter: the ground the lit cells
          // stand out of.
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
      this.sceneGroup.add(
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
      this.sceneGroup.add(
        new THREE.Mesh(
          quadGeometry(measured, measuredColors),
          new THREE.MeshBasicMaterial({
            vertexColors: true,
            side: THREE.DoubleSide,
          }),
        ),
      );
    }

    this.addPins(sheets);
    this.addSheetEdges(sheets, nx, ny);
    this.addLabels(sheets, nx, ny);

    this.drawn = sheets.some((sheet) => sheet.measured > 0);
    if (force || !this.framed) {
      this.frame(sheets, nx, ny);
      this.framed = true;
    }
  }

  /** A pin on every cell the run measured.

      The measured cells are a handful of squares in a field of hundreds:
      flat, they disappear into their own sheet. A pin standing off its
      sheet says which sheet the run entered, and how few cells it took.
  */
  private addPins(sheets: Sheet[]): void {
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
        this.sceneGroup.add(pin);
      });
    });
  }

  /** The edge of every sheet, so the stack reads as a stack. */
  private addSheetEdges(sheets: Sheet[], nx: number, ny: number): void {
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
    this.sceneGroup.add(
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

  /** The name of each sheet, and the axes the stack is built on. */
  private addLabels(sheets: Sheet[], nx: number, ny: number): void {
    const axes = stageState.axes;
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
      this.sceneGroup.add(sprite);
    });

    const zSprite = createTextSprite(axes.z, 0.28, nameMaterial);
    zSprite.position.set(
      -halfX - 0.85,
      sheets.length * LAYER_GAP * 0.5,
      -halfY,
    );
    this.sceneGroup.add(zSprite);

    const xSprite = createTextSprite(axes.x, 0.28, nameMaterial);
    xSprite.position.set(halfX + 0.9, -LAYER_GAP, halfY);
    this.sceneGroup.add(xSprite);

    const ySprite = createTextSprite(axes.y, 0.28, nameMaterial);
    ySprite.position.set(halfX + 0.9, -LAYER_GAP, -halfY - 0.6);
    this.sceneGroup.add(ySprite);
  }

  private frame(sheets: Sheet[], nx: number, ny: number): void {
    const context = getSceneContext();
    if (!context || sheets.length === 0) return;

    const halfX = (nx * CELL) / 2;
    const halfY = (ny * CELL) / 2;
    const halfStack = (sheets.length * LAYER_GAP) / 2;

    frameBox(
      context,
      new THREE.Vector3(-halfX - 1.4, -halfStack - 0.4, -halfY - 0.6),
      new THREE.Vector3(halfX + 1.4, halfStack + 0.4, halfY + 0.6),
      new THREE.Vector3(0, 0, 0),
      VIEW_DIRECTION,
    );
  }

  /** Take the old sheets off the stage before the new ones go on. */
  private clear(): void {
    [...this.sceneGroup.children].forEach((child) => {
      this.sceneGroup.remove(child);
      disposeObject(child);
    });
  }
}

/** The quads of a sheet, as one geometry. */
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
