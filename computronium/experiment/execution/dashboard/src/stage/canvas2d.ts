/** The 2D stage (TODO69 Phase 5).

    A view does not have to be three.js: a matrix of numbers and a family of
    curves are flat pictures, and a canvas draws them better than a mesh of
    triangles. The canvas sits over the 3D stage, in the part of the window
    the panels leave free, and the views that use it share its frame.
*/

import { FREE_HEIGHT, FREE_WIDTH } from "./framing.js";

/** A rectangle of the window, in CSS pixels. */
export interface Area {
  x: number;
  y: number;
  width: number;
  height: number;
}

export class StageCanvas {
  private readonly canvas: HTMLCanvasElement;
  private readonly context: CanvasRenderingContext2D;
  private visible = false;

  constructor(id: string) {
    this.canvas = document.createElement("canvas");
    this.canvas.id = id;
    this.canvas.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: 50;
      display: none;
      background: var(--bg);
      pointer-events: none;
    `;
    document.body.appendChild(this.canvas);
    this.context = this.canvas.getContext("2d")!;
    this.resize();
    window.addEventListener("resize", () => {
      this.resize();
    });
  }

  show(): void {
    this.visible = true;
    this.canvas.style.display = "block";
    this.resize();
  }

  hide(): void {
    this.visible = false;
    this.canvas.style.display = "none";
  }

  private resize(): void {
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    this.canvas.width = Math.floor(window.innerWidth * ratio);
    this.canvas.height = Math.floor(window.innerHeight * ratio);
    this.context.setTransform(ratio, 0, 0, ratio, 0, 0);
  }

  /** Begin a picture: the canvas is cleared, and its context is returned. */
  begin(): CanvasRenderingContext2D {
    const ctx = this.context;
    ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
    ctx.fillStyle = "#0a0e14";
    ctx.fillRect(0, 0, window.innerWidth, window.innerHeight);
    return ctx;
  }

  /** The part of the window the picture may use: the panels leave it free.

      The legend stands at the bottom left, so the picture starts to the
      right of it rather than under it.
  */
  area(): Area {
    const legend = document.getElementById("discovery-legend");
    const legendRight = legend
      ? legend.getBoundingClientRect().right
      : 0;
    const x = Math.max(40, legendRight + 24);
    const width = Math.max(200, window.innerWidth * FREE_WIDTH - x);
    return {
      x,
      y: 70,
      width,
      height: Math.max(200, window.innerHeight * FREE_HEIGHT - 70),
    };
  }
}

/** The stage's flat canvas: one at a time, because one view stands on it. */
export const stageCanvas = new StageCanvas("stage-2d");
