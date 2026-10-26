/** Framing the camera (TODO69 Phase 5).

    A view is only a picture if it can be seen: the camera has to stand where
    the whole of it fits, and it has to fit in the part of the window the
    panels leave free. The discovery map already knew how; the stage's views
    share the same rule, so every view is framed the same way.
*/

import * as THREE from "three";
import type { SceneContext } from "../components/context.js";

/** The part of the window the panels leave free: a view is framed into it.

    The legend sits at the bottom left and the plotter at the bottom right, so
    a picture framed into the whole window would be half hidden behind them.
*/
export const FREE_WIDTH = 0.72;
export const FREE_HEIGHT = 0.86;

/** Stand the camera where the whole of a box can be seen.

    The box is seen at the angle the reader left the camera at, so a view
    that is framed again keeps its point of view. The box's corners are
    projected onto the camera's own axes: the distance is the one that puts
    every corner inside the free area, and the target is then moved so the
    box sits in the middle of that area rather than the middle of the window.
*/
export function frameBox(
  context: SceneContext,
  min: THREE.Vector3,
  max: THREE.Vector3,
  target: THREE.Vector3,
  toCamera?: THREE.Vector3,
): void {
  const { camera, controls } = context;

  const direction =
    toCamera?.clone() ?? camera.position.clone().sub(controls.target);
  if (direction.lengthSq() === 0) direction.set(0.4, 0.5, 0.8);
  direction.normalize();

  const view = direction.clone().negate();
  const right = new THREE.Vector3()
    .crossVectors(view, new THREE.Vector3(0, 1, 0))
    .normalize();
  const up = new THREE.Vector3().crossVectors(right, view).normalize();

  const tanV = Math.tan(((camera.fov ?? 60) * Math.PI) / 360);
  const tanH = tanV * (camera.aspect || 1);
  // The picture is framed into the part of the window the panels leave free.
  const freeTanV = tanV * FREE_HEIGHT;
  const freeTanH = tanH * FREE_WIDTH;

  let distance = 0;
  [min.x, max.x].forEach((x) => {
    [min.y, max.y].forEach((y) => {
      [min.z, max.z].forEach((z) => {
        const corner = new THREE.Vector3(x, y, z);
        const need =
          Math.max(
            Math.abs(corner.dot(right)) / freeTanH,
            Math.abs(corner.dot(up)) / freeTanV,
          ) + corner.dot(direction);
        distance = Math.max(distance, need);
      });
    });
  });
  distance *= 1.06;

  // The free area is not the middle of the window, so the camera looks
  // beside the picture's centre rather than at it.
  const ndcX = FREE_WIDTH - 1;
  const ndcY = 1 - FREE_HEIGHT;
  target
    .add(right.clone().multiplyScalar(-ndcX * tanH * distance))
    .add(up.clone().multiplyScalar(-ndcY * tanV * distance));

  controls.target.copy(target);
  camera.position.copy(target).add(direction.clone().multiplyScalar(distance));
  controls.update();
}
