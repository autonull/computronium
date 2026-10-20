/** Objects on the stage (TODO69 Phase 5).

    The scene is shared: every view puts its objects on the same stage. A
    view that is not active must leave nothing of itself there, so the
    objects it built are freed when it goes.
*/

import * as THREE from "three";

/** Free an object and everything hanging off it. */
export function disposeObject(object: THREE.Object3D): void {
  object.traverse((child) => {
    const mesh = child as THREE.Mesh;
    mesh.geometry?.dispose();
    const material = mesh.material;
    if (Array.isArray(material)) {
      material.forEach((entry) => entry.dispose());
    } else {
      material?.dispose();
    }
  });
}
