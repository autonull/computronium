/** Sprites on the stage (TODO69 Phase 5).

    A label in the scene is a sprite with a canvas behind it: the same words
    the panels carry, drawn in the picture itself. The stage's views share
    them, so a label looks the same wherever it stands.
*/

import * as THREE from "three";

/** Break a label into lines that fit the gap between two cells.

    A long name written on one line is wider than the space it has, and the
    labels then read as a smear; breaking it at its underscores keeps every
    word whole.
*/
export function wrapLabel(text: string, maxChars = 10): string[] {
  if (text.length <= maxChars) return [text];

  const lines: string[] = [];
  let current = "";
  for (const part of text.split("_")) {
    const candidate = current ? `${current}_${part}` : part;
    if (candidate.length > maxChars && current) {
      lines.push(current);
      current = part;
    } else {
      current = candidate;
    }
  }
  if (current) lines.push(current);
  return lines;
}

/** A label that fits the space it has: wrapped, and never wider than the gap. */
export function createTextSprite(
  text: string,
  worldHeight: number,
  material: THREE.SpriteMaterial,
  maxWidth?: number,
): THREE.Sprite {
  const lines = wrapLabel(text);
  const canvas = document.createElement("canvas");
  const context = canvas.getContext("2d")!;
  const fontSize = 64;
  const lineHeight = 72;

  context.font = `bold ${fontSize}px "JetBrains Mono", monospace`;
  const textWidth =
    Math.max(...lines.map((line) => context.measureText(line).width)) + 16;
  canvas.width = Math.max(64, Math.ceil(textWidth));
  canvas.height = lines.length * lineHeight + 16;

  // Resizing the canvas resets the context, so the font is set after.
  context.font = `bold ${fontSize}px "JetBrains Mono", monospace`;
  context.fillStyle = "#ffffff";
  context.textAlign = "center";
  context.textBaseline = "middle";
  lines.forEach((line, i) => {
    context.fillText(
      line,
      canvas.width / 2,
      lineHeight * i + lineHeight / 2 + 8,
    );
  });

  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;

  const spriteMaterial = material.clone();
  spriteMaterial.map = texture;
  spriteMaterial.transparent = true;

  const sprite = new THREE.Sprite(spriteMaterial);
  const aspect = canvas.width / canvas.height;
  let height = worldHeight * lines.length;
  if (maxWidth !== undefined) {
    height = Math.min(height, maxWidth / aspect);
  }
  sprite.scale.set(height * aspect, height, 1);
  return sprite;
}

/** A round dot, for a point in a scatter. */
export function createDotTexture(): THREE.CanvasTexture {
  const size = 64;
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const context = canvas.getContext("2d")!;
  context.fillStyle = "#ffffff";
  context.beginPath();
  context.arc(size / 2, size / 2, size / 2 - 2, 0, Math.PI * 2);
  context.fill();
  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;
  return texture;
}

/** A ring that marks a point without taking the point's colour away.

    A sprite always faces the camera, so the ring around a point is seen as a
    ring from every angle — which a flat disc in the scene is not.
*/
export function createRingSprite(
  color: string,
  worldRadius: number,
  lineWidth = 0.14,
): THREE.Sprite {
  const size = 128;
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const context = canvas.getContext("2d")!;
  context.strokeStyle = color;
  context.lineWidth = size * lineWidth;
  context.beginPath();
  context.arc(size / 2, size / 2, size / 2 - context.lineWidth, 0, Math.PI * 2);
  context.stroke();

  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;

  const material = new THREE.SpriteMaterial({
    map: texture,
    transparent: true,
    depthWrite: false,
  });
  const sprite = new THREE.Sprite(material);
  sprite.scale.set(worldRadius * 2, worldRadius * 2, 1);
  return sprite;
}
