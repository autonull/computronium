/** Frontier stage view — every measured cell in (accuracy, speed, parameters) (TODO72 P6). */

import * as THREE from "three";
import { ARM_COLORS, PALETTE } from "../../../colors.js";
import { frameBox } from "../../../stores/framing.js";
import { createDotTexture, createRingSprite, createTextSprite } from "../../../stores/sprites.js";
import { metricsStore } from "../../../stores/metrics.js";
import { workspaceStore } from "../../../stores/workspace.js";
import type {
  StageViewDefinition,
  StageViewInstance,
  StageViewContext,
  StageChange,
  Size,
} from "../../../layout/types.js";

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

/** Create a StageViewInstance for the "frontier" view. */
export function createFrontierView(context: StageViewContext): StageViewInstance {
  const { surface, workspace, state } = context;

  // Per-instance state derived from state + workspace
  let runId = (state as any).runId ?? workspace.getSelectedRunId();
  let axes = (state as any).axes ?? workspace.getAxes();

  // Three.js objects owned by this view instance
  const scene = surface.three.scene;
  const camera = surface.three.camera;
  const controls = surface.three.controls;
  const sceneGroup = new THREE.Group();

  // View state
  let visible = false;
  let drawn = false;
  let framed = false;
  let accuracy: Extent = { min: 0, max: 0, span: 0 };

  // Subscriptions
  let workspaceUnsub: (() => void) | null = null;
  let metricsUnsub: (() => void) | null = null;

  async function init(): Promise<void> {
    scene.add(sceneGroup);

    // Subscribe to workspace changes
    workspaceUnsub = workspace.onChange(() => {
      const newRunId = workspace.getSelectedRunId();
      const newAxes = workspace.getAxes();
      if (newRunId !== runId || newAxes.x !== axes.x || newAxes.y !== axes.y || newAxes.z !== axes.z) {
        runId = newRunId;
        axes = newAxes;
        redraw();
      }
    });

    // Subscribe to metrics for this run
    if (runId) {
      metricsUnsub = metricsStore.subscribe(runId, () => {
        redraw();
      });
    }

    visible = true;
    await redraw();
  }

  function redraw(): void {
    if (!visible) return;
    draw(true);
  }

  function draw(force: boolean): void {
    const points = computePoints();
    if (points.length === 0) {
      drawn = false;
      clear();
      return;
    }

    clear();
    addPoints(points);
    addFront(points);
    addChanceFloor();
    addLabels();

    drawn = true;
    if (force || !framed) {
      frame();
      framed = true;
    }
  }

  function computePoints(): Point[] {
    const metrics = runId ? metricsStore.get(runId) : null;
    const records = metrics?.records ?? [];
    const flags = metrics?.pareto ?? [];
    const chance = metrics?.chance ?? 0.1;

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
    accuracy = accRange;
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

  function addPoints(points: Point[]): void {
    const positions: number[] = [];
    const colors: number[] = [];
    points.forEach((point) => {
      positions.push(point.x, point.y, point.z);
      const color = new THREE.Color(ARM_COLORS[point.arm] || PALETTE.gradient);
      colors.push(color.r, color.g, color.b);
    });

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
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
    sceneGroup.add(new THREE.Points(geometry, material));

    // The frontier's points are ringed.
    const front = points.filter((point) => point.pareto);
    if (front.length === 0) return;
    front.forEach((point) => {
      const ring = createRingSprite(PALETTE.pareto, 0.26);
      ring.position.set(point.x, point.y, point.z);
      sceneGroup.add(ring);
    });
  }

  function addFront(points: Point[]): void {
    const front = points
      .filter((point) => point.pareto)
      .sort((a, b) => a.y - b.y);
    if (front.length < 2) return;

    const positions: number[] = [];
    front.forEach((point) => positions.push(point.x, point.y, point.z));
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
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
    sceneGroup.add(line);
  }

  function addChanceFloor(): void {
    const metrics = runId ? metricsStore.get(runId) : null;
    const chance = metrics?.chance ?? 0.1;
    const accRange = accuracy;
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
    sceneGroup.add(floor);

    const label = createTextSprite(
      "chance",
      0.24,
      new THREE.SpriteMaterial({
        color: PALETTE.chance_line,
        sizeAttenuation: true,
      }),
    );
    label.position.set(WIDTH / 2 + 0.3, height, DEPTH / 2 + 0.3);
    sceneGroup.add(label);
  }

  function addLabels(): void {
    const nameMaterial = new THREE.SpriteMaterial({
      color: 0xc9d4e0,
      sizeAttenuation: true,
    });
    const speed = createTextSprite("speed 1/s", 0.26, nameMaterial);
    speed.position.set(WIDTH / 2 + 0.6, 0.1, 0);
    sceneGroup.add(speed);

    const accuracyLabel = createTextSprite("accuracy", 0.26, nameMaterial);
    accuracyLabel.position.set(0, HEIGHT + 0.4, 0);
    sceneGroup.add(accuracyLabel);

    const params = createTextSprite("parameters", 0.26, nameMaterial);
    params.position.set(0, 0.1, DEPTH / 2 + 0.7);
    sceneGroup.add(params);
  }

  function frame(): void {
    frameBox(
      { camera, controls } as any,
      new THREE.Vector3(-WIDTH / 2 - 0.6, -0.2, -DEPTH / 2 - 0.6),
      new THREE.Vector3(WIDTH / 2 + 0.6, HEIGHT + 0.6, DEPTH / 2 + 0.6),
      new THREE.Vector3(0, HEIGHT / 2, 0),
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
    surface.three.renderer.setSize(size.width, size.height);
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

/** Register the frontier view definition. */
export const frontierViewDefinition: StageViewDefinition = {
  view: "frontier",
  title: "Frontier",
  key: "shift+g",
  group: "the run",
  create: createFrontierView,
};