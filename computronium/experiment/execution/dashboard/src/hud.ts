/** HUD — 3D Resource Bars & Mission Control (TODO68 Phase 4). */

import * as THREE from "three";
import { registry } from "./components/registry.js";
import { router } from "./ws-client.js";
import { PALETTE } from "./palette.js";
import type { Component } from "./components/registry.js";

interface StatusData {
  gpu_utilization?: number;
  cpu_utilization?: number;
  memory_utilization?: number;
  used_gpus?: number;
  max_gpus?: number;
  used_cpus?: number;
  max_cpus?: number;
  used_memory_gb?: number;
  max_memory_gb?: number;
  running_campaigns?: number;
  queued_campaigns?: number;
}

interface ResourceBarData {
  key: string;
  label: string;
  color: string;
  max: number;
}

export class HUD implements Component {
  name = "HUD";

  private scene: THREE.Scene;
  private camera: THREE.Camera;
  private renderer: THREE.WebGLRenderer;
  private resourceBars: Map<string, THREE.Group> = new Map();
  private burnRateMesh: THREE.Sprite | null = null;
  private claimPriceMesh: THREE.Sprite | null = null;
  private modeChipMesh: THREE.Sprite | null = null;
  private statusData: StatusData = {};
  private animationTime = 0;

  constructor() {
    this.scene = new THREE.Scene();
    this.camera = new THREE.Camera();
    this.renderer = new THREE.WebGLRenderer();
  }

  async init(): Promise<void> {
    const dashboard = (window as any).__DASHBOARD__;
    if (dashboard) {
      this.scene = dashboard.scene;
      this.camera = dashboard.camera;
      this.renderer = dashboard.renderer;
    }

    router.register("status_update", this.onStatusUpdate.bind(this));

    this.createHUD();
    console.log("[HUD] Initialized");
  }

  async destroy(): Promise<void> {
    router.unregister("status_update", this.onStatusUpdate.bind(this));
    this.resourceBars.forEach((group) => {
      this.scene.remove(group);
      group.traverse((obj) => {
        if (obj instanceof THREE.Mesh) {
          obj.geometry.dispose();
          if (Array.isArray(obj.material)) {
            obj.material.forEach((m) => m.dispose());
          } else {
            obj.material.dispose();
          }
        } else if (obj instanceof THREE.Sprite) {
          obj.material.map?.dispose();
          obj.material.dispose();
        }
      });
    });
    this.resourceBars.clear();
    this.burnRateMesh?.material.map?.dispose();
    this.burnRateMesh?.material.dispose();
    this.claimPriceMesh?.material.map?.dispose();
    this.claimPriceMesh?.material.dispose();
    this.modeChipMesh?.material.map?.dispose();
    this.modeChipMesh?.material.dispose();
  }

  private createHUD(): void {
    // Create 3D resource bars (GPU, CPU, Memory)
    const resources = [
      { key: "gpu", label: "GPU", color: PALETTE.gpu, max: 8 },
      { key: "cpu", label: "CPU", color: PALETTE.cpu, max: 64 },
      { key: "memory", label: "MEM", color: PALETTE.memory, max: 512 },
    ];

    const startX = 18;
    const startY = 8;
    const spacing = -1.8;

    resources.forEach((res, i) => {
      const group = new THREE.Group();
      group.position.set(startX, startY + i * spacing, 0);
      this.createResourceBar(group, res);
      this.scene.add(group);
      this.resourceBars.set(res.key, group);
    });

    // Burn rate display
    this.createBurnRate();

    // Claim price display
    this.createClaimPrice();

    // Mode chip (top-left)
    this.createModeChip();
  }

  private createResourceBar(
    group: THREE.Group,
    res: { key: string; label: string; color: string; max: number },
  ): void {
    const barWidth = 3.5;
    const barHeight = 0.6;
    const barDepth = 0.4;

    // Background bar
    const bgGeometry = new THREE.BoxGeometry(barWidth, barHeight, barDepth);
    const bgMaterial = new THREE.MeshStandardMaterial({
      color: 0x1a2330,
      metalness: 0.2,
      roughness: 0.8,
    });
    const bgMesh = new THREE.Mesh(bgGeometry, bgMaterial);
    bgMesh.position.x = barWidth / 2;
    group.add(bgMesh);

    // Fill bar (animated)
    const fillGeometry = new THREE.BoxGeometry(
      0.01,
      barHeight * 0.8,
      barDepth * 0.8,
    );
    const fillMaterial = new THREE.MeshStandardMaterial({
      color: res.color,
      emissive: res.color,
      emissiveIntensity: 0.4,
      metalness: 0.5,
      roughness: 0.3,
    });
    const fillMesh = new THREE.Mesh(fillGeometry, fillMaterial);
    fillMesh.position.x = 0.005;
    fillMesh.userData = { maxWidth: barWidth, baseWidth: 0.01 };
    group.add(fillMesh);
    group.userData.fillMesh = fillMesh;

    // Label
    const labelCanvas = document.createElement("canvas");
    const ctx = labelCanvas.getContext("2d")!;
    labelCanvas.width = 128;
    labelCanvas.height = 48;
    ctx.font = "bold 28px 'JetBrains Mono', monospace";
    ctx.fillStyle = res.color;
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";
    ctx.fillText(res.label, 120, 24);

    const labelTexture = new THREE.CanvasTexture(labelCanvas);
    const labelMaterial = new THREE.SpriteMaterial({
      map: labelTexture,
      transparent: true,
      depthTest: false,
    });
    const labelSprite = new THREE.Sprite(labelMaterial);
    labelSprite.scale.set(2.5, 0.9, 1);
    labelSprite.position.set(-0.3, 0, 0);
    labelSprite.renderOrder = 1;
    group.add(labelSprite);

    // Value text (updated dynamically)
    const valueCanvas = document.createElement("canvas");
    const vctx = valueCanvas.getContext("2d")!;
    valueCanvas.width = 128;
    valueCanvas.height = 48;
    vctx.font = "bold 24px 'JetBrains Mono', monospace";
    vctx.fillStyle = "#8b98a8";
    vctx.textAlign = "left";
    vctx.textBaseline = "middle";
    vctx.fillText("0%", 4, 24);

    const valueTexture = new THREE.CanvasTexture(valueCanvas);
    const valueMaterial = new THREE.SpriteMaterial({
      map: valueTexture,
      transparent: true,
      depthTest: false,
    });
    const valueSprite = new THREE.Sprite(valueMaterial);
    valueSprite.scale.set(2.5, 0.9, 1);
    valueSprite.position.set(barWidth + 0.5, 0, 0);
    valueSprite.renderOrder = 1;
    group.add(valueSprite);
    group.userData.valueSprite = valueSprite;
    group.userData.valueCanvas = valueCanvas;
    group.userData.valueContext = vctx;
  }

  private createBurnRate(): void {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d")!;
    canvas.width = 256;
    canvas.height = 64;
    ctx.font = "bold 32px 'JetBrains Mono', monospace";
    ctx.fillStyle = PALETTE.text_primary;
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";
    ctx.fillText("34s / 120s", 250, 32);

    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({
      map: texture,
      transparent: true,
      depthTest: false,
    });
    this.burnRateMesh = new THREE.Sprite(material);
    this.burnRateMesh.scale.set(5, 1.2, 1);
    this.burnRateMesh.position.set(18, 8 - 3 * 1.8 - 1.2, 0);
    this.burnRateMesh.renderOrder = 1;
    this.scene.add(this.burnRateMesh);
    this.burnRateMesh.userData.canvas = canvas;
    this.burnRateMesh.userData.context = ctx;
  }

  private createClaimPrice(): void {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d")!;
    canvas.width = 256;
    canvas.height = 48;
    ctx.font = "bold 24px 'JetBrains Mono', monospace";
    ctx.fillStyle = PALETTE.pareto;
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";
    ctx.fillText("63 seeds/arm", 250, 24);

    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({
      map: texture,
      transparent: true,
      depthTest: false,
    });
    this.claimPriceMesh = new THREE.Sprite(material);
    this.claimPriceMesh.scale.set(5, 0.9, 1);
    this.claimPriceMesh.position.set(18, 8 - 3 * 1.8 - 2.2, 0);
    this.claimPriceMesh.renderOrder = 1;
    this.scene.add(this.claimPriceMesh);
    this.claimPriceMesh.userData.canvas = canvas;
    this.claimPriceMesh.userData.context = ctx;
  }

  private createModeChip(): void {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d")!;
    canvas.width = 256;
    canvas.height = 64;
    ctx.font = "bold 28px 'JetBrains Mono', monospace";
    // Rounded rect background
    ctx.fillStyle = PALETTE.insufficient + "44";
    ctx.beginPath();
    ctx.roundRect(32, 8, 192, 48, 16);
    ctx.fill();
    ctx.fillStyle = PALETTE.insufficient;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("EXPLORATORY", 128, 32);

    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({
      map: texture,
      transparent: true,
      depthTest: false,
    });
    this.modeChipMesh = new THREE.Sprite(material);
    this.modeChipMesh.scale.set(5, 1.2, 1);
    this.modeChipMesh.position.set(-18, 8, 0);
    this.modeChipMesh.renderOrder = 1;
    this.scene.add(this.modeChipMesh);
    this.modeChipMesh.userData.canvas = canvas;
    this.modeChipMesh.userData.context = ctx;
  }

  private onStatusUpdate(data: any): void {
    this.statusData = data.data || data;
    this.updateResourceBars();
    this.updateBurnRate();
  }

  private updateResourceBars(): void {
    const mappings = [
      {
        key: "gpu",
        util: this.statusData.gpu_utilization,
        used: this.statusData.used_gpus,
        max: this.statusData.max_gpus,
      },
      {
        key: "cpu",
        util: this.statusData.cpu_utilization,
        used: this.statusData.used_cpus,
        max: this.statusData.max_cpus,
      },
      {
        key: "memory",
        util: this.statusData.memory_utilization,
        used: this.statusData.used_memory_gb,
        max: this.statusData.max_memory_gb,
      },
    ];

    mappings.forEach(({ key, util, used, max }) => {
      const group = this.resourceBars.get(key);
      if (!group) return;

      const fillMesh = group.userData.fillMesh as THREE.Mesh | undefined;
      const valueSprite = group.userData.valueSprite as
        THREE.Sprite | undefined;
      const canvas = group.userData.valueCanvas as
        HTMLCanvasElement | undefined;
      const ctx = group.userData.valueContext as
        CanvasRenderingContext2D | undefined;

      if (fillMesh) {
        const targetWidth = fillMesh.userData.maxWidth * (util || 0);
        // Animate width
        const currentWidth = fillMesh.scale.x * fillMesh.userData.baseWidth;
        fillMesh.scale.x = THREE.MathUtils.lerp(
          currentWidth / fillMesh.userData.baseWidth,
          targetWidth / fillMesh.userData.baseWidth,
          0.1,
        );
        fillMesh.position.x =
          (fillMesh.scale.x * fillMesh.userData.baseWidth) / 2;
      }

      if (valueSprite && canvas && ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.font = "bold 24px 'JetBrains Mono', monospace";
        ctx.fillStyle = "#8b98a8";
        ctx.textAlign = "left";
        ctx.textBaseline = "middle";
        const utilPct = ((util || 0) * 100).toFixed(1);
        ctx.fillText(`${utilPct}%`, 4, 24);
        valueSprite.material.map!.needsUpdate = true;
      }
    });
  }

  private updateBurnRate(): void {
    if (!this.burnRateMesh) return;
    const canvas = this.burnRateMesh.userData.canvas as
      HTMLCanvasElement | undefined;
    const ctx = this.burnRateMesh.userData.context as
      CanvasRenderingContext2D | undefined;
    if (!canvas || !ctx) return;

    const running = this.statusData.running_campaigns || 0;
    const budget = 120; // demo budget seconds
    const elapsed = Math.min(budget, (Date.now() / 1000) % budget);

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.font = "bold 32px 'JetBrains Mono', monospace";
    ctx.fillStyle = running > 0 ? PALETTE.ok : PALETTE.text_primary;
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";
    ctx.fillText(`${Math.floor(elapsed)}s / ${budget}s`, 250, 32);
    this.burnRateMesh.material.map!.needsUpdate = true;
  }

  update(delta: number): void {
    this.animationTime += delta;

    // Pulse animation for active resources
    this.resourceBars.forEach((group, key) => {
      const fillMesh = group.userData.fillMesh as THREE.Mesh | undefined;
      const util = (this.statusData as any)[`${key}_utilization`] || 0;
      if (
        fillMesh &&
        util > 0 &&
        fillMesh.material instanceof THREE.MeshStandardMaterial
      ) {
        const pulse =
          0.3 +
          0.2 *
            Math.sin(
              this.animationTime * 3 +
                (key === "gpu" ? 0 : key === "cpu" ? 2 : 4),
            );
        fillMesh.material.emissiveIntensity = pulse;
      }
    });

    // Pulse burn rate when running
    const mesh = this.burnRateMesh;
    // @ts-ignore: TypeScript narrowing issue with this.property access
    if (mesh != null && this.statusData.running_campaigns > 0) {
      const pulse = 1 + 0.1 * Math.sin(this.animationTime * 4);
      mesh.scale.x = 5 * pulse;
      mesh.scale.y = 1.2 * pulse;
    }
  }
}

registry.register(new HUD());
