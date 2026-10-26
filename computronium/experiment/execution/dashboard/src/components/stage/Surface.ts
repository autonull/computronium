/** StageSurface — one Three.js scene/renderer/camera/controls per stage panel (TODO72 P5). */

import * as THREE from "three";
import { OrbitControls } from "three-stdlib";
import { detectRenderProfile } from "../../render-profile.js";
import type { Size, Rect, Area, StageCanvas, StageSurface } from "../../layout/types.js";

/** Per-instance 2D canvas for overlay rendering. */
export class StageCanvasImpl implements StageCanvas {
  readonly canvas: HTMLCanvasElement;
  private context: CanvasRenderingContext2D;

  constructor() {
    this.canvas = document.createElement("canvas");
    this.canvas.style.cssText = "position:absolute;top:0;left:0;pointer-events:none;";
    const ctx = this.canvas.getContext("2d", { alpha: true });
    if (!ctx) throw new Error("2D context unavailable");
    this.context = ctx;
  }

  clear(): void {
    this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }

  /** Resize the canvas to match the surface size. */
  resize(size: Size): void {
    const dpr = Math.min(window.devicePixelRatio, 2);
    this.canvas.width = size.width * dpr;
    this.canvas.height = size.height * dpr;
    this.canvas.style.width = `${size.width}px`;
    this.canvas.style.height = `${size.height}px`;
    this.context.scale(dpr, dpr);
  }

  /** Begin a picture: the canvas is cleared, and its context is returned. */
  begin(): CanvasRenderingContext2D {
    const ctx = this.context;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    ctx.fillStyle = "#0a0e14";
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    return ctx;
  }

  /** The drawable area: the entire surface (no more FREE_WIDTH/FREE_HEIGHT). */
  area(): Area {
    return { x: 0, y: 0, width: this.canvas.clientWidth, height: this.canvas.clientHeight };
  }
}

/** One StageSurface per stage panel instance — owns its own Three.js context. */
export class StageSurfaceImpl implements StageSurface {
  readonly root: HTMLElement;
  readonly three: {
    scene: THREE.Scene;
    camera: THREE.PerspectiveCamera;
    renderer: THREE.WebGLRenderer;
    controls: OrbitControls;
  };
  readonly flat: StageCanvasImpl;
  private profile: ReturnType<typeof detectRenderProfile>;
  private animationId: number | null = null;
  private lastTime = 0;
  private frameCallbacks = new Set<(delta: number) => void>();
  private resizeObserver: ResizeObserver | null = null;
  private hasResized = false;

  constructor() {
    this.root = document.createElement("div");
    // Root is positioned absolute inset:0 by the stage component
    this.root.style.cssText = "width:100%;height:100%;position:relative;overflow:hidden;";

    this.profile = detectRenderProfile();
    this.flat = new StageCanvasImpl();

    // Three.js scene
    this.three = this.createThreeContext();
    this.root.appendChild(this.three.renderer.domElement);
    this.root.appendChild(this.flat.canvas);

    // ResizeObserver on root — ensures resize() fires before first frameBox
    this.resizeObserver = new ResizeObserver(() => {
      this.resize();
      this.hasResized = true;
    });
    this.resizeObserver.observe(this.root);
  }

  private createThreeContext() {
    const renderer = new THREE.WebGLRenderer({
      antialias: this.profile.antialias,
      alpha: true,
      powerPreference: "high-performance",
    });
    renderer.setPixelRatio(this.profile.software ? 1 : Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = this.profile.shadows;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0e14);
    scene.fog = new THREE.FogExp2(0x0a0e14, 0.015);

    const camera = new THREE.PerspectiveCamera(60, 1, 0.1, 200);
    camera.position.set(3.3, 4.4, 8.8);
    camera.lookAt(0, 1.0, 0.1);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 1.0, 0.1);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.enablePan = true;
    controls.minDistance = 5;
    controls.maxDistance = 80;
    controls.maxPolarAngle = Math.PI / 2 - 0.05;

    // Store renderer and camera on canvas for debug access
    (renderer.domElement as HTMLCanvasElement & { __three_renderer?: THREE.WebGLRenderer; __three_camera?: THREE.PerspectiveCamera }).__three_renderer = renderer;
    (renderer.domElement as HTMLCanvasElement & { __three_renderer?: THREE.WebGLRenderer; __three_camera?: THREE.PerspectiveCamera }).__three_camera = camera;

    // Lights
    const ambientLight = new THREE.AmbientLight(0x444466, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2);
    directionalLight.position.set(10, 20, 10);
    directionalLight.castShadow = this.profile.shadows;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.camera.near = 1;
    directionalLight.shadow.camera.far = 50;
    directionalLight.shadow.camera.left = -20;
    directionalLight.shadow.camera.right = 20;
    directionalLight.shadow.camera.top = 20;
    directionalLight.shadow.camera.bottom = -20;
    scene.add(directionalLight);

    const hemiLight = new THREE.HemisphereLight(0x88aaff, 0x222233, 0.5);
    scene.add(hemiLight);

    // Grid helper
    const gridHelper = new THREE.GridHelper(8, 8, 0x243040, 0x161d28);
    gridHelper.position.y = -0.01;
    const gridMaterial = gridHelper.material as THREE.Material;
    gridMaterial.transparent = true;
    gridMaterial.opacity = 0.35;
    scene.add(gridHelper);

    return { scene, camera, renderer, controls };
  }

  /** Current size of the surface. */
  size(): Size {
    return {
      width: this.root.clientWidth,
      height: this.root.clientHeight,
    };
  }

  /** Resize renderer, camera, and flat canvas to current size. */
  resize(): void {
    const { width, height } = this.size();
    if (width === 0 || height === 0) return;

    this.three.camera.aspect = width / height;
    this.three.camera.updateProjectionMatrix();
    this.three.renderer.setSize(width, height);
    this.three.renderer.setPixelRatio(
      this.profile.software ? 1 : Math.min(window.devicePixelRatio, 2),
    );
    this.flat.resize({ width, height });
  }

  /** Register a per-frame callback (e.g., for view-specific animation). Returns unsubscribe. */
  onFrame(cb: (delta: number) => void): () => void {
    this.frameCallbacks.add(cb);
    return () => this.frameCallbacks.delete(cb);
  }

  /** Start the render loop. */
  start(): void {
    if (this.animationId) return;
    // Ensure initial resize before first frame
    if (!this.hasResized) this.resize();
    this.lastTime = performance.now();
    const animate = (time: number) => {
      this.animationId = requestAnimationFrame(animate);
      const frameIntervalMs = 1000 / this.profile.fps;
      if (time - this.lastTime < frameIntervalMs) return;
      const delta = (time - this.lastTime) / 1000;
      this.lastTime = time;
      this.three.controls.update();
      for (const cb of this.frameCallbacks) cb(delta);
      this.three.renderer.render(this.three.scene, this.three.camera);
    };
    animate(performance.now());
  }

  /** Stop the render loop. */
  stop(): void {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }

  /** Dispose all resources. */
  dispose(): void {
    this.stop();
    this.resizeObserver?.disconnect();
    this.three.controls.dispose();
    this.three.renderer.dispose();
    this.three.scene.clear();
    this.flat.canvas.remove();
    this.three.renderer.domElement.remove();
    this.root.remove();
  }
}