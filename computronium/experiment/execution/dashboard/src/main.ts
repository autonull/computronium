/** Three.js Dashboard Main Entry Point (TODO68 Phase 0). */

import * as THREE from "three";
import { OrbitControls } from "three-stdlib";
import "./dashboard.css";
import { router, wsClient } from "./ws-client.js";
import { setSceneContext } from "./components/context.js";
import { controlBar } from "./control-bar.js";
import { controlPanel } from "./control-panel.js";
import { discoveryMap } from "./discovery-map.js";
import { cellDrawer } from "./cell-drawer.js";
import { plotter } from "./plotter.js";
import { liveRail } from "./live-rail.js";
import { caption } from "./caption.js";
import { hud } from "./hud.js";
import { viewSwitcher } from "./stage/switcher.js";
import { helpOverlay } from "./help-overlay.js";
import { PALETTE } from "./palette.js";
import { panels } from "./panels.js";
import { layout } from "./layout.js";
import { BINDINGS, allBindings, setAction } from "./bindings.js";
import { detectRenderProfile } from "./render-profile.js";
import type { Binding } from "./bindings.js";

// Global error handler
window.addEventListener("error", (event) => {
  console.error("[Global Error]", event.error);
  showError(event.error?.message || "Unknown error");
});

window.addEventListener("unhandledrejection", (event) => {
  console.error("[Unhandled Rejection]", event.reason);
  showError(event.reason?.message || "Unhandled promise rejection");
});

// Loading state - uses .global-loading CSS class
let loadingElement: HTMLElement | null = null;

function showLoading(message = "Initializing dashboard..."): void {
  const overlay = document.getElementById("ui-overlay");
  if (!overlay) return;
  loadingElement = document.createElement("div");
  loadingElement.id = "global-loading";
  loadingElement.className = "global-loading";
  loadingElement.innerHTML = `
    <div class="global-loading-spinner"></div>
    <div class="global-loading-text">${message}</div>
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
  const errorElement = document.createElement("div");
  errorElement.id = "global-error";
  errorElement.className = "global-error";
  errorElement.innerHTML = `
    <span>✗</span>
    <span>${message}</span>
    <button class="global-error-close">&times;</button>
  `;
  // Add click handler for close button
  errorElement.querySelector(".global-error-close")?.addEventListener("click", () => {
    errorElement.remove();
  });
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

// Wire binding actions after components initialize
document.addEventListener("DOMContentLoaded", async () => {
  // Initialize layout manager first (sets up docks, restores workspace)
  await layout.init();

  setAction("chart-pareto", () => plotter.showTab("pareto"));
  setAction("chart-ablation", () => plotter.showTab("ablation"));
  setAction("chart-variability", () => plotter.showTab("variability"));

  setAction("control-play", () => controlBar.togglePlay());
  setAction("control-step", () => controlBar.step());
  setAction("control-stop", () => controlBar.stop());
  setAction("control-panel", () => panels.toggle("control-panel"));

  setAction("panel-hud", () => panels.toggle("hud"));
  setAction("panel-rail", () => panels.toggle("live-rail"));
  setAction("panel-caption", () => panels.toggle("caption"));
  setAction("panel-legend", () => panels.toggle("legend"));

  setAction("view-cycle", () => viewSwitcher.cycle());

  setAction("cell-replicate", () => window.dispatchEvent(new CustomEvent("cell-action-replicate")));
  setAction("cell-preregister", () => window.dispatchEvent(new CustomEvent("cell-action-preregister")));
  setAction("cell-quest", () => window.dispatchEvent(new CustomEvent("cell-action-quest")));

  setAction("help", () => helpOverlay.toggle());
  setAction("escape", () => {
    if (cellDrawer.hasCellSelected()) cellDrawer.hide();
    else helpOverlay.hide();
  });
});

// Keyboard shortcuts: the binding layer is the single source of truth.

const bindingsByKey = new Map<string, Binding>();
const bindingsByChord = new Map<string, Binding>();
for (const binding of BINDINGS) {
  if (binding.key) bindingsByKey.set(binding.key.toLowerCase(), binding);
  if (binding.chord) bindingsByChord.set(binding.chord.toLowerCase(), binding);
}

window.addEventListener("keydown", (event) => {
  // Ignore if modifier keys pressed (except Shift for chords)
  if (event.metaKey || event.ctrlKey || event.altKey) return;

  const target = event.target as HTMLElement | null;
  if (target && ["INPUT", "SELECT", "TEXTAREA"].includes(target.tagName)) {
    return;
  }

  const key = event.key.toLowerCase();

  // Check for shifted chords first (e.g., shift+r)
  if (event.shiftKey) {
    const chord = `shift+${key}`;
    const binding = bindingsByChord.get(chord);
    if (binding) {
      if (binding.when === "cell-selected" && !cellDrawer.hasCellSelected()) return;
      binding.run();
      return;
    }
  }

  // Direct key match
  const binding = bindingsByKey.get(key);
  if (binding) {
    if (binding.when === "cell-selected" && !cellDrawer.hasCellSelected()) return;
    binding.run();
    return;
  }
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
  helpOverlay,
  viewSwitcher,
  controlBar,
  controlPanel,
  panels,
  layout,
  wsClient,
  router,
  bindings: {
    list: () => allBindings().map((b) => ({ id: b.id, label: b.label, group: b.group, key: b.key })),
  },
};

console.log("🚀 Computronium Dashboard initialized");
