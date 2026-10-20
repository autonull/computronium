/** Three.js Dashboard Main Entry Point (TODO68 Phase 0). */

import * as THREE from "three";
import { OrbitControls } from "three-stdlib";
import { registry } from "./components/registry.js";
import { router } from "./ws-client.js";
import { WSClient } from "./ws-client.js";
import { DiscoveryMap } from "./discovery-map.js";
import { CellDrawer } from "./cell-drawer.js";
import { Plotter } from "./plotter.js";
import { LiveRail } from "./live-rail.js";
import { HUD } from "./hud.js";

// Initialize WebSocket client
const wsClient = new WSClient("/ws", router);
wsClient.connect();

// Create and register core components
const discoveryMap = new DiscoveryMap();
const cellDrawer = new CellDrawer();
const plotter = new Plotter();
const liveRail = new LiveRail();
const hud = new HUD();

registry.register(discoveryMap);
registry.register(cellDrawer);
registry.register(plotter);
registry.register(liveRail);
registry.register(hud);

// Three.js scene setup (shared by DiscoveryMap and HUD)
const canvas = document.getElementById("dashboard-canvas") as HTMLCanvasElement;
const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  alpha: true,
  powerPreference: "high-performance",
});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
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
camera.position.set(15, 12, 15);
camera.lookAt(0, 0, 0);

// Orbit controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.enablePan = true;
controls.minDistance = 5;
controls.maxDistance = 80;
controls.maxPolarAngle = Math.PI / 2 - 0.05;

// Lights
const ambientLight = new THREE.AmbientLight(0x444466, 0.6);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2);
directionalLight.position.set(10, 20, 10);
directionalLight.castShadow = true;
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

// Grid helper (subtle)
const gridHelper = new THREE.GridHelper(40, 40, 0x2a3a4a, 0x1a2330);
gridHelper.position.y = -0.01;
scene.add(gridHelper);

// Axis labels (will be updated by DiscoveryMap)
const axisLabels: THREE.Mesh[] = [];

// Resize handler
function onResize(): void {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
}
window.addEventListener("resize", onResize);

// Animation loop
let lastTime = 0;
function animate(time: number): void {
  requestAnimationFrame(animate);

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
  hud,
  wsClient,
  router,
};

console.log("🚀 Computronium Dashboard initialized");
