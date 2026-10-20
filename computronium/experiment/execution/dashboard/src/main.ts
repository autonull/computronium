/** Three.js Dashboard Main Entry Point (TODO68 Phase 0). */

import * as THREE from "three";
import { OrbitControls } from "three-stdlib";
import { router, wsClient } from "./ws-client.js";
import { setSceneContext } from "./components/context.js";
import { discoveryMap } from "./discovery-map.js";
import { cellDrawer } from "./cell-drawer.js";
import { plotter } from "./plotter.js";
import { liveRail } from "./live-rail.js";
import { caption } from "./caption.js";
import { hud } from "./hud.js";
import { viewSwitcher } from "./stage/switcher.js";
import { PALETTE } from "./palette.js";
import { PANEL_KEYS, TAB_KEYS } from "./keys.js";
import { detectRenderProfile } from "./render-profile.js";

// Global error handler
window.addEventListener("error", (event) => {
  console.error("[Global Error]", event.error);
  showError(event.error?.message || "Unknown error");
});

window.addEventListener("unhandledrejection", (event) => {
  console.error("[Unhandled Rejection]", event.reason);
  showError(event.reason?.message || "Unhandled promise rejection");
});

// Loading state
let loadingElement: HTMLElement | null = null;
let errorElement: HTMLElement | null = null;

function showLoading(message = "Initializing dashboard..."): void {
  const overlay = document.getElementById("ui-overlay");
  if (!overlay) return;
  loadingElement = document.createElement("div");
  loadingElement.id = "global-loading";
  loadingElement.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 32px 48px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    z-index: 1000;
    box-shadow: 0 16px 48px rgba(0,0,0,0.5);
  `;
  loadingElement.innerHTML = `
    <div style="
      width: 48px;
      height: 48px;
      border: 3px solid var(--border);
      border-top-color: ${PALETTE.gradient};
      border-radius: 50%;
      animation: spin 1s linear infinite;
    "></div>
    <div style="font-size: 14px; color: var(--text-primary);">${message}</div>
    <style>
      @keyframes spin { to { transform: rotate(360deg); } }
    </style>
  `;
  overlay.appendChild(loadingElement);
}

function hideLoading(): void {
  loadingElement?.remove();
  loadingElement = null;
}

function showError(message: string): void {
  const overlay = document.getElementById("ui-overlay");
  if (!overlay) return;
  errorElement = document.createElement("div");
  errorElement.id = "global-error";
  errorElement.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${PALETTE.error}22;
    border: 1px solid ${PALETTE.error}88;
    border-radius: 8px;
    padding: 16px 24px;
    color: ${PALETTE.error};
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    z-index: 1000;
    max-width: 400px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    display: flex;
    align-items: center;
    gap: 12px;
  `;
  errorElement.innerHTML = `
    <span>✗</span>
    <span>${message}</span>
    <button onclick="this.parentElement.remove()" style="
      background: none;
      border: none;
      color: ${PALETTE.error};
      font-size: 18px;
      cursor: pointer;
      line-height: 1;
      padding: 0 4px;
    ">&times;</button>
  `;
  overlay.appendChild(errorElement);
  // Auto-dismiss after 10 seconds
  setTimeout(() => errorElement?.remove(), 10000);
}

// Initialize WebSocket client (uses shared instance from ws-client.ts)
wsClient.connect();

// Show loading state
showLoading("Connecting to dashboard...");

// Wait for WebSocket connection, then hide loading
wsClient.waitForConnection(15000).then((connected) => {
  if (connected) {
    hideLoading();
  } else {
    showLoading("Connection timeout — retrying...");
    // Keep trying
    wsClient.onStateChange((state) => {
      if (state === "connected") hideLoading();
    });
  }
});

// Components self-register with the registry on import; the registry
// initializes them on DOMContentLoaded (after __DASHBOARD__ is published).

// Keyboard shortcuts: the charts, the panels, and the drawer.
// The number keys belong to the stage's views (V cycles them); the charts
// are picked by the letters that name them, and the panels by their own.
const TAB_BY_KEY = new Map<string, string>(
  Object.entries(TAB_KEYS).map(([name, key]) => [key, name]),
);
window.addEventListener("keydown", (event) => {
  if (event.metaKey || event.ctrlKey || event.altKey) return;
  const key = event.key.toLowerCase();
  const tab = TAB_BY_KEY.get(key);
  if (tab) {
    plotter.showTab(tab);
    return;
  }
  if (key === PANEL_KEYS.hud) hud.toggle();
  if (key === PANEL_KEYS.rail) liveRail.toggle();
  if (key === PANEL_KEYS.caption) caption.toggle();
});

// Three.js scene setup (shared by DiscoveryMap and HUD)
const canvas = document.getElementById("dashboard-canvas") as HTMLCanvasElement;
const profile = detectRenderProfile();
const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: profile.antialias,
  alpha: true,
  powerPreference: "high-performance",
});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(profile.software ? 1 : Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = profile.shadows;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0a0e14); // var(--bg)
scene.fog = new THREE.FogExp2(0x0a0e14, 0.015);

// Camera
const camera = new THREE.PerspectiveCamera(
  60,
  window.innerWidth / window.innerHeight,
  0.1,
  200,
);
camera.position.set(3.3, 4.4, 8.8);
camera.lookAt(0, 1.0, 0.1);

// Orbit controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1.0, 0.1);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.enablePan = true;
controls.minDistance = 5;
controls.maxDistance = 80;
controls.maxPolarAngle = Math.PI / 2 - 0.05;

// Publish the shared scene so components bind to the live scene, not copies.
// The controls are part of it: the discovery map frames the grid it builds,
// and framing is a move of the camera's target.
setSceneContext({ scene, camera, renderer, controls });

// Lights
const ambientLight = new THREE.AmbientLight(0x444466, 0.6);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2);
directionalLight.position.set(10, 20, 10);
directionalLight.castShadow = profile.shadows;
directionalLight.shadow.mapSize.width = 2048;
directionalLight.shadow.mapSize.height = 2048;
directionalLight.shadow.camera.near = 1;
directionalLight.shadow.camera.far = 50;
directionalLight.shadow.camera.left = -20;
directionalLight.shadow.camera.right = 20;
directionalLight.shadow.camera.top = 20;
directionalLight.shadow.camera.bottom = -20;
scene.add(directionalLight);

// Hemisphere light for nice ambient
const hemiLight = new THREE.HemisphereLight(0x88aaff, 0x222233, 0.5);
scene.add(hemiLight);

// Grid helper (subtle, sized to the discovery map)
const gridHelper = new THREE.GridHelper(8, 8, 0x243040, 0x161d28);
gridHelper.position.y = -0.01;
const gridMaterial = gridHelper.material as THREE.Material;
gridMaterial.transparent = true;
gridMaterial.opacity = 0.35;
scene.add(gridHelper);

// Axis labels (will be updated by DiscoveryMap)
const axisLabels: THREE.Mesh[] = [];

// Resize handler
function onResize(): void {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(
    profile.software ? 1 : Math.min(window.devicePixelRatio, 2),
  );
}
window.addEventListener("resize", onResize);

// Animation loop — capped so the render never starves the event loop that
// carries the dashboard's data.
const frameIntervalMs = 1000 / profile.fps;
let lastTime = 0;
function animate(time: number): void {
  requestAnimationFrame(animate);

  if (time - lastTime < frameIntervalMs) return;

  const delta = (time - lastTime) / 1000;
  lastTime = time;

  controls.update();

  // Update components that need per-frame updates
  discoveryMap.update(delta);
  hud.update(delta);

  renderer.render(scene, camera);
}

// Start animation loop
requestAnimationFrame(animate);

// Expose for debugging
(window as any).__DASHBOARD__ = {
  scene,
  camera,
  renderer,
  controls,
  discoveryMap,
  cellDrawer,
  plotter,
  liveRail,
  caption,
  hud,
  viewSwitcher,
  wsClient,
  router,
};

console.log("🚀 Computronium Dashboard initialized");
