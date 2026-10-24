/** The frontier — every measured cell in (accuracy, speed, parameters) (TODO69 Phase 5).

    The picture every reader of a run actually wants: what the run found, and
    what nothing else beat. The records are points in three measures at once,
    the frontier the run computed is drawn through them, and the chance level
    is the floor under them all.
*/

import * as THREE from "three";
import { getSceneContext } from "../components/context.js";
import { ARM_COLORS, PALETTE } from "../colors.js";
import { frameBox } from "./framing.js";
import { disposeObject } from "./scene.js";
import { stageState } from "./state.js";
import { createDotTexture, createRingSprite, createTextSprite } from "./sprites.js";
import type { StageView, ViewGroup } from "./views.js";

/** The size of the plot the points are drawn in. */
const WIDTH = 6.4;
const HEIGHT = 4.0;
const DEPTH = 5.0;

interface Point {
  x: number;
  y: number;
  z: number;
  arm: string;
  pareto: boolean;
}

export class FrontierView implements StageView {
  id = "frontier";
  name = "Frontier";
  group = "the run" as ViewGroup;
  caption =
    "Every measured cell in accuracy, speed and parameters; the frontier is the line nothing beat.";

  private sceneGroup = new THREE.Group();
  private visible = false;
  private drawn = false;
  private framed = false;
  /** The accuracy the points were scaled against. */
  private accuracy: Extent = { min: 0, max: 0, span: 0 };

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

  /** The records as points: accuracy up, speed across, parameters back. */
  private points(): Point[] {
    const records = stageState.metrics?.records ?? [];
    const flags = stageState.metrics?.pareto ?? [];
    const chance = stageState.chance;

    const accuracies: number[] = [];
    const speeds: number[] = [];
    const params: number[] = [];
    records.forEach((record: any) => {
      const payload = record?.payload ?? {};
      if (typeof payload.val_acc === "number") {
        accuracies.push(payload.val_acc);
      }
      if (typeof payload.walltime_s === "number" && payload.walltime_s > 0) {
        speeds.push(1 / payload.walltime_s);
      }
      if (typeof payload.param_count === "number" && payload.param_count > 0) {
        params.push(Math.log10(payload.param_count));
      }
    });

    const accRange = range([...accuracies, chance]);
    this.accuracy = accRange;
    const speedRange = range(speeds);
    const paramRange = range(params);

    const points: Point[] = [];
    records.forEach((record: any, index: number) => {
      const payload = record?.payload ?? {};
      if (typeof payload.val_acc !== "number") return;
      const speed =
        typeof payload.walltime_s === "number" && payload.walltime_s > 0
          ? 1 / payload.walltime_s
          : null;
      const param =
        typeof payload.param_count === "number" && payload.param_count > 0
          ? Math.log10(payload.param_count)
          : null;

      points.push({
        x:
          speed === null || speedRange.span === 0
            ? 0
            : ((speed - speedRange.min) / speedRange.span - 0.5) * WIDTH,
        y:
          accRange.span === 0
            ? 0
            : ((payload.val_acc - accRange.min) / accRange.span) * HEIGHT,
        z:
          param === null || paramRange.span === 0
            ? 0
            : ((param - paramRange.min) / paramRange.span - 0.5) * DEPTH,
        arm: record?.coordinate?.credit ?? "",
        pareto: flags[index] === true,
      });
    });
    return points;
  }

  private draw(force: boolean): void {
    const points = this.points();
    if (points.length === 0) {
      this.drawn = false;
      return;
    }

    this.clear();
    this.addPoints(points);
    this.addFront(points);
    this.addChanceFloor();
    this.addLabels();

    this.drawn = true;
    if (force || !this.framed) {
      this.frame();
      this.framed = true;
    }
  }

  private clear(): void {
    [...this.sceneGroup.children].forEach((child) => {
      this.sceneGroup.remove(child);
      disposeObject(child);
    });
  }

  /** Every record is a point; the arm's colour says which arm it was. */
  private addPoints(points: Point[]): void {
    const positions: number[] = [];
    const colors: number[] = [];
    points.forEach((point) => {
      positions.push(point.x, point.y, point.z);
      const color = new THREE.Color(ARM_COLORS[point.arm] || PALETTE.gradient);
      colors.push(color.r, color.g, color.b);
    });

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(positions, 3),
    );
    geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 0.26,
      sizeAttenuation: true,
      vertexColors: true,
      map: createDotTexture(),
      alphaTest: 0.4,
      transparent: true,
      opacity: 0.95,
    });
    this.sceneGroup.add(new THREE.Points(geometry, material));

    // The frontier's points are ringed: a ring does not take the arm's
    // colour away from the point it marks.
    const front = points.filter((point) => point.pareto);
    if (front.length === 0) return;
    front.forEach((point) => {
      const ring = createRingSprite(PALETTE.pareto, 0.26);
      ring.position.set(point.x, point.y, point.z);
      this.sceneGroup.add(ring);
    });
  }

  /** The front itself: the line through the points nothing beat. */
  private addFront(points: Point[]): void {
    const front = points
      .filter((point) => point.pareto)
      .sort((a, b) => a.y - b.y);
    if (front.length < 2) return;

    const positions: number[] = [];
    front.forEach((point) => positions.push(point.x, point.y, point.z));
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(positions, 3),
    );
    const line = new THREE.Line(
      geometry,
      new THREE.LineDashedMaterial({
        color: PALETTE.pareto,
        dashSize: 0.22,
        gapSize: 0.16,
        transparent: true,
        opacity: 0.85,
      }),
    );
    line.computeLineDistances();
    this.sceneGroup.add(line);
  }

  /** The chance level, as the floor under everything the run measured. */
  private addChanceFloor(): void {
    const chance = stageState.chance;
    const accRange = this.accuracy;
    if (accRange.span === 0) return;
    const height = ((chance - accRange.min) / accRange.span) * HEIGHT;

    const geometry = new THREE.PlaneGeometry(WIDTH * 1.02, DEPTH * 1.02);
    geometry.rotateX(-Math.PI / 2);
    const floor = new THREE.Mesh(
      geometry,
      new THREE.MeshBasicMaterial({
        color: PALETTE.chance_line,
        transparent: true,
        opacity: 0.07,
        side: THREE.DoubleSide,
        depthWrite: false,
      }),
    );
    floor.position.y = height;
    this.sceneGroup.add(floor);

    const label = createTextSprite(
      "chance",
      0.24,
      new THREE.SpriteMaterial({
        color: PALETTE.chance_line,
        sizeAttenuation: true,
      }),
    );
    label.position.set(WIDTH / 2 + 0.3, height, DEPTH / 2 + 0.3);
    this.sceneGroup.add(label);
  }

  /** The three measures, named where they are. */
  private addLabels(): void {
    const nameMaterial = new THREE.SpriteMaterial({
      color: 0xc9d4e0,
      sizeAttenuation: true,
    });
    const speed = createTextSprite("speed 1/s", 0.26, nameMaterial);
    speed.position.set(WIDTH / 2 + 0.6, 0.1, 0);
    this.sceneGroup.add(speed);

    const accuracy = createTextSprite("accuracy", 0.26, nameMaterial);
    accuracy.position.set(0, HEIGHT + 0.4, 0);
    this.sceneGroup.add(accuracy);

    const params = createTextSprite("parameters", 0.26, nameMaterial);
    params.position.set(0, 0.1, DEPTH / 2 + 0.7);
    this.sceneGroup.add(params);
  }

  private frame(): void {
    const context = getSceneContext();
    if (!context) return;
    frameBox(
      context,
      new THREE.Vector3(-WIDTH / 2 - 0.6, -0.2, -DEPTH / 2 - 0.6),
      new THREE.Vector3(WIDTH / 2 + 0.6, HEIGHT + 0.6, DEPTH / 2 + 0.6),
      new THREE.Vector3(0, HEIGHT / 2, 0),
    );
  }
}

interface Extent {
  min: number;
  max: number;
  span: number;
}

function range(values: number[]): Extent {
  const finite = values.filter((value) => Number.isFinite(value));
  if (finite.length === 0) return { min: 0, max: 0, span: 0 };
  const min = Math.min(...finite);
  const max = Math.max(...finite);
  return { min, max, span: max - min };
}
