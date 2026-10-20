/** Shared three.js scene context — populated by main.ts, consumed by components. */

import type * as THREE from "three";

export interface SceneContext {
  scene: THREE.Scene;
  camera: THREE.Camera;
  renderer: THREE.WebGLRenderer;
}

let context: SceneContext | null = null;

export function setSceneContext(next: SceneContext): void {
  context = next;
}

export function getSceneContext(): SceneContext | null {
  return context;
}
