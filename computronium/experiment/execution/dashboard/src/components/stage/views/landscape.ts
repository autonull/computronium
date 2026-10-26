/** Landscape stage view — the cell's own energy over the slice its trajectory crosses (TODO72 P6). */

import * as THREE from "three";
import { PALETTE } from "../../../colors.js";
import { rampColor } from "../../../stores/ramp.js";
import { dynamicsStore } from "../../../stores/dynamics.js";
import { workspaceStore } from "../../../stores/workspace.js";
import type {
  StageViewDefinition,
  StageViewInstance,
  StageViewContext,
  StageChange,
  Size,
} from "../../../layout/types.js";

/** Create a StageViewInstance for the "landscape" view. */
export function createLandscapeView(context: StageViewContext): StageViewInstance {
  const { surface, flat, workspace, state } = context;

  // Per-instance state derived from state + workspace
  let runId = (state as any).runId ?? workspace.getSelectedRunId();
  let axes = (state as any).axes ?? workspace.getAxes();

  // Three.js objects owned by this view instance
  const scene = surface.three.scene;
  const camera = surface.three.camera;
  const renderer = surface.three.renderer;
  const controls = surface.three.controls;

  // Grid state
  const meshes = new Map<string, THREE.Mesh>();
  let landscapeMesh: THREE.Mesh | null = null;
  let trajectoryLine: THREE.Line | null = null;
  let lowestMarker: THREE.Mesh | null = null;
  let visible = false;
  let drawn = false;

  // Subscriptions
  let workspaceUnsub: (() => void) | null = null;
  let dynamicsUnsub: (() => void) | null = null;

  async function init(): Promise<void> {
    // Subscribe to workspace changes (run selection, axes)
    workspaceUnsub = workspace.onChange(() => {
      const newRunId = workspace.getSelectedRunId();
      const newAxes = workspace.getAxes();
      if (newRunId !== runId || newAxes.x !== axes.x || newAxes.y !== axes.y || newAxes.z !== axes.z) {
        runId = newRunId;
        axes = newAxes;
        updateDynamicsSubscription();
        redraw();
      }
    });

    // Subscribe to dynamics for this run
    await updateDynamicsSubscription();

    visible = true;
    await redraw();
  }

  async function updateDynamicsSubscription(): Promise<void> {
    dynamicsUnsub?.();
    if (!runId) return;

    dynamicsUnsub = dynamicsStore.subscribe(runId, false, () => {
      redraw();
    });
  }

  function redraw(): void {
    if (!visible) return;
    draw();
  }

  function draw(): void {
    const payload = runId ? dynamicsStore.get(runId, false) : null;
    const landscape = payload?.landscape;
    const trajectory = payload?.trajectory;

    if (!payload || !landscape || landscape.grid.length === 0) {
      drawn = false;
      clearScene();
      return;
    }

    clearScene();

    const grid = landscape.grid;
    const flatGrid = grid.flat();
    const lowest = Math.min(...flatGrid);
    const highest = Math.max(...flatGrid);

    // Create landscape mesh
    const geometry = new THREE.PlaneGeometry(
      landscape.x[landscape.x.length - 1] - landscape.x[0] || 1,
      landscape.y[landscape.y.length - 1] - landscape.y[0] || 1,
      landscape.x.length - 1,
      landscape.y.length - 1,
    );
    geometry.rotateX(-Math.PI / 2);

    const positionAttribute = geometry.getAttribute("position");
    const colors = new Float32Array(positionAttribute.count * 3);

    for (let i = 0; i < positionAttribute.count; i++) {
      const x = positionAttribute.getX(i);
      const z = positionAttribute.getZ(i);

      // Find grid cell
      const xIdx = Math.floor((x - landscape.x[0]) / ((landscape.x[landscape.x.length - 1] - landscape.x[0]) / (landscape.x.length - 1 || 1)));
      const yIdx = Math.floor((-z - landscape.y[0]) / ((landscape.y[landscape.y.length - 1] - landscape.y[0]) / (landscape.y.length - 1 || 1)));

      let value = 0;
      if (xIdx >= 0 && xIdx < landscape.x.length - 1 && yIdx >= 0 && yIdx < landscape.y.length - 1) {
        value = grid[xIdx][yIdx];
      }

      const t = (value - lowest) / (highest - lowest || 1);
      const color = new THREE.Color(rampColor(1 - t));
      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
    }

    geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));

    const material = new THREE.MeshBasicMaterial({
      vertexColors: true,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.9,
    });

    landscapeMesh = new THREE.Mesh(geometry, material);
    landscapeMesh.position.set(
      (landscape.x[0] + landscape.x[landscape.x.length - 1]) / 2,
      0.01,
      -(landscape.y[0] + landscape.y[landscape.y.length - 1]) / 2,
    );
    scene.add(landscapeMesh);
    meshes.set("landscape", landscapeMesh);

    // The trajectory, over the ground.
    if (trajectory && trajectory.path.length > 1) {
      const points = trajectory.path.map((p) => new THREE.Vector3(p[0], 0.05, -p[1]));
      const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
      const lineMaterial = new THREE.LineBasicMaterial({
        color: PALETTE.text_primary,
        linewidth: 2,
      });
      trajectoryLine = new THREE.Line(lineGeometry, lineMaterial);
      scene.add(trajectoryLine);
      meshes.set("trajectory", trajectoryLine as any);
    }

    // The low ground, named: where the energy is smallest.
    let bestX = 0;
    let bestY = 0;
    let bestValue = Number.POSITIVE_INFINITY;
    grid.forEach((row, i) =>
      row.forEach((value, j) => {
        if (value < bestValue) {
          bestValue = value;
          bestX = i;
          bestY = j;
        }
      }),
    );

    const markerGeometry = new THREE.RingGeometry(0.15, 0.25, 32);
    const markerMaterial = new THREE.MeshBasicMaterial({
      color: PALETTE.ok,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.8,
    });
    lowestMarker = new THREE.Mesh(markerGeometry, markerMaterial);
    lowestMarker.rotation.x = -Math.PI / 2;
    lowestMarker.position.set(
      landscape.x[bestX],
      0.06,
      -landscape.y[bestY],
    );
    scene.add(lowestMarker);
    meshes.set("lowestMarker", lowestMarker);

    // Frame the camera to the landscape
    frameCamera();

    drawn = true;
  }

  function frameCamera(): void {
    if (!landscapeMesh) return;

    const box = new THREE.Box3().setFromObject(landscapeMesh);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.z);
    const distance = maxDim * 1.5;

    controls.target.copy(center);
    camera.position.set(center.x, distance * 0.7, center.z + distance);
    camera.lookAt(center);
    controls.update();
  }

  function clearScene(): void {
    meshes.forEach((mesh) => {
      scene.remove(mesh);
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
    });
    meshes.clear();
    landscapeMesh = null;
    trajectoryLine = null;
    lowestMarker = null;
  }

  // Mount: attach event listeners if needed
  function mount(): void {
    // No event listeners needed for this view
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
    if (change.kind === "data" || change.kind === "resize") {
      redraw();
    }
  }

  function ready(): boolean {
    return drawn;
  }

  // Dispose: clean up everything
  function dispose(): void {
    workspaceUnsub?.();
    dynamicsUnsub?.();
    clearScene();
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

/** Register the landscape view definition. */
export const landscapeViewDefinition: StageViewDefinition = {
  view: "landscape",
  title: "The landscape",
  key: "shift+n",
  group: "the system",
  create: createLandscapeView,
};