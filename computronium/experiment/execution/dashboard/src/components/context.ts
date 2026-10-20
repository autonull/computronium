/** Shared three.js scene context — populated by main.ts, consumed by components. */

import type * as THREE from "three";
import type { OrbitControls } from "three-stdlib";

export interface SceneContext {
  scene: THREE.Scene;
  camera: THREE.PerspectiveCamera;
  renderer: THREE.WebGLRenderer;
  controls: OrbitControls;
}

let context: SceneContext | null = null;

export function setSceneContext(next: SceneContext): void {
  context = next;
}

export function getSceneContext(): SceneContext | null {
  return context;
}
