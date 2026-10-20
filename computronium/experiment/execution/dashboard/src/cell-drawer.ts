/** Cell Drawer — Slide-in Detail Panel (TODO68 Phase 2). */

import * as THREE from "three";
import { registry } from "./components/registry.js";
import { PALETTE, ARM_COLORS } from "./palette.js";
import type { Component } from "./components/registry.js";

interface CellData {
  coordinate: {
    credit: string;
    geometry: string;
    dynamics: string;
    substrate?: string;
    plasticity?: string;
    update?: string;
  };
  status: "measured" | "legal" | "void";
  metrics?: {
    val_acc?: number;
    val_acc_std?: number;
    walltime_s?: number;
    param_count?: number;
    n_seeds?: number;
  };
  requiredSeeds?: number;
  price?: number;
}

export class CellDrawer implements Component {
  name = "CellDrawer";

  private panel: HTMLElement | null = null;
  private content: HTMLElement | null = null;
  private sparklineScene: THREE.Scene | null = null;
  private sparklineRenderer: THREE.WebGLRenderer | null = null;
  private sparklineCamera: THREE.OrthographicCamera | null = null;
  private sparklineAnimationId: number | null = null;
  private currentData: CellData | null = null;

  async init(): Promise<void> {
    this.createPanel();
    this.setupEvents();
    console.log("[CellDrawer] Initialized");
  }

  async destroy(): Promise<void> {
    this.stopSparkline();
    this.panel?.remove();
    window.removeEventListener(
      "cell-selected",
      this.onCellSelected as EventListener,
    );
  }

  private createPanel(): void {
    const overlay = document.getElementById("ui-overlay");
    if (!overlay) return;

    this.panel = document.createElement("div");
    this.panel.id = "cell-drawer";
    this.panel.style.cssText = `
      position: fixed;
      top: 0;
      right: 0;
      width: 380px;
      height: 100%;
      background: var(--bg-secondary);
      border-left: 1px solid var(--border);
      transform: translateX(100%);
      transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      z-index: 200;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    `;

    this.panel.innerHTML = `
      <div id="drawer-header" style="
        padding: 16px;
        border-bottom: 1px solid var(--border);
        display: flex;
        align-items: center;
        justify-content: space-between;
      ">
        <h3 style="margin: 0; font-size: 14px; font-weight: 600;">Cell Details</h3>
        <button id="drawer-close" style="
          background: none;
          border: none;
          color: var(--text-secondary);
          font-size: 20px;
          cursor: pointer;
          padding: 4px;
          line-height: 1;
        ">&times;</button>
      </div>
      <div id="drawer-content" style="
        flex: 1;
        overflow-y: auto;
        padding: 16px;
      "></div>
    `;

    overlay.appendChild(this.panel);
    this.content = this.panel.querySelector("#drawer-content")!;

    this.panel
      .querySelector("#drawer-close")!
      .addEventListener("click", () => this.hide());
  }

  private setupEvents(): void {
    window.addEventListener(
      "cell-selected",
      this.onCellSelected as EventListener,
    );
  }

  private onCellSelected = (event: CustomEvent): void => {
    this.show(event.detail);
  };

  show(data: CellData): void {
    this.currentData = data;
    this.renderContent(data);
    this.panel!.style.transform = "translateX(0)";
    this.startSparkline(data);
  }

  hide(): void {
    this.panel!.style.transform = "translateX(100%)";
    this.stopSparkline();
    this.currentData = null;
  }

  private renderContent(data: CellData): void {
    if (!this.content) return;

    const { coordinate, metrics, status } = data;
    const armColor = ARM_COLORS[coordinate.credit] || PALETTE.gradient;
    const valAcc = metrics?.val_acc ?? 0;
    const nSeeds = metrics?.n_seeds ?? 0;
    const chance = 0.1; // digits task = 10 classes
    const requiredSeeds = data.requiredSeeds ?? 0;

    // Verdict logic
    let verdict = "UNKNOWN";
    let verdictColor = PALETTE.text_secondary;
    if (status === "measured") {
      if (valAcc > chance + 0.1) {
        verdict = "PASSED";
        verdictColor = PALETTE.passed;
      } else if (valAcc > chance) {
        verdict = "INSUFFICIENT";
        verdictColor = PALETTE.insufficient;
      } else {
        verdict = "REJECTED";
        verdictColor = PALETTE.rejected;
      }
    }

    // Seeds to claim: the power analysis asks for a fixed seed count
    const seedsToClaim =
      status === "measured" && requiredSeeds > 0
        ? Math.max(0, requiredSeeds - nSeeds)
        : "N/A";

    this.content.innerHTML = `
      <div style="margin-bottom: 20px;">
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;">
          ${Object.entries(coordinate)
            .filter(([, v]) => v)
            .map(
              ([axis, value]) => `
              <span style="
                padding: 4px 10px;
                background: ${axis === "credit" ? armColor + "22" : "var(--bg-tertiary)"};
                border: 1px solid ${axis === "credit" ? armColor + "88" : "var(--border)"};
                border-radius: 12px;
                font-size: 11px;
                color: ${axis === "credit" ? armColor : "var(--text-primary)"};
              ">
                ${axis}=${value}
              </span>
            `,
            )
            .join("")}
        </div>
      </div>

      ${
        metrics
          ? `
        <div style="margin-bottom: 20px;">
          <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 4px;">VALIDATION ACCURACY</div>
          <div style="
            font-size: 42px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            color: var(--text-primary);
            line-height: 1;
          ">${valAcc.toFixed(3)}</div>
          <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">
            ± ${(metrics.val_acc_std ?? 0).toFixed(3)} (n=${nSeeds})
          </div>
        </div>
      `
          : ""
      }

      <div style="margin-bottom: 20px; padding: 12px; background: var(--bg-tertiary); border-radius: 6px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
          <span style="
            padding: 4px 10px;
            background: ${verdictColor}22;
            border: 1px solid ${verdictColor}88;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            color: ${verdictColor};
            text-transform: uppercase;
          ">${verdict}</span>
          <span style="font-size: 12px; color: var(--text-secondary);">Chance level: ${chance}</span>
        </div>
        <div style="height: 4px; background: var(--bg); border-radius: 2px; overflow: hidden;">
          <div style="
            width: ${Math.min(100, (valAcc / (chance * 2)) * 100)}%;
            height: 100%;
            background: linear-gradient(90deg, ${PALETTE.rejected}, ${PALETTE.insufficient}, ${PALETTE.passed});
            border-radius: 2px;
          "></div>
        </div>
      </div>

      ${
        status === "measured"
          ? `
        <div style="margin-bottom: 20px;">
          <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px;">SEEDS TO CLAIM</div>
          <div style="font-size: 24px; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: ${PALETTE.insufficient};">
            ${seedsToClaim}
          </div>
          <div style="font-size: 11px; color: var(--text-secondary);">(d=0.5, α=0.05)</div>
        </div>
      `
          : ""
      }

      ${
        metrics?.walltime_s
          ? `
        <div style="margin-bottom: 20px; padding: 12px; background: var(--bg-tertiary); border-radius: 6px;">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 12px;">
            <div>
              <div style="color: var(--text-secondary);">Wall Time</div>
              <div style="font-family: 'JetBrains Mono', monospace; font-weight: 600;">${metrics.walltime_s.toFixed(1)}s</div>
            </div>
            <div>
              <div style="color: var(--text-secondary);">Parameters</div>
              <div style="font-family: 'JetBrains Mono', monospace; font-weight: 600;">${((metrics.param_count ?? 0) / 1000).toFixed(1)}K</div>
            </div>
          </div>
        </div>
      `
          : ""
      }

      <!-- Mini 3D Sparkline Container -->
      <div style="margin-bottom: 20px;">
        <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px;">TRAINING CURVE</div>
        <div id="sparkline-container" style="
          width: 100%;
          height: 120px;
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: 6px;
          overflow: hidden;
        "></div>
      </div>

      <!-- Actions (visual only for v1) -->
      <div style="
        display: flex;
        gap: 8px;
        padding-top: 16px;
        border-top: 1px solid var(--border);
      ">
        <button class="drawer-btn" style="flex: 1;" disabled>Queue Rest</button>
        <button class="drawer-btn" style="flex: 1;" disabled>Preregister</button>
        <button class="drawer-btn" style="flex: 1;" disabled>Adopt as Quest</button>
      </div>
    `;

    // Add button styles
    const style = document.createElement("style");
    style.textContent = `
      .drawer-btn {
        padding: 10px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 6px;
        color: var(--text-secondary);
        font-size: 11px;
        cursor: not-allowed;
        transition: all 0.15s;
      }
      .drawer-btn:not(:disabled):hover {
        background: var(--border);
        color: var(--text-primary);
        border-color: var(--border-bright);
      }
    `;
    this.content.appendChild(style);
  }

  // Mini 3D sparkline (training curve in panel)
  private startSparkline(data: CellData): void {
    const container = document.getElementById("sparkline-container");
    if (!container) return;

    // Create mini three.js scene
    this.sparklineScene = new THREE.Scene();
    this.sparklineCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 10);
    this.sparklineCamera.position.z = 2;

    this.sparklineRenderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
    });
    this.sparklineRenderer.setSize(
      container.clientWidth,
      container.clientHeight,
    );
    this.sparklineRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(this.sparklineRenderer.domElement);

    // Generate mock training curve data
    const epochs = 10;
    const curveData = Array.from({ length: epochs }, (_, i) => {
      const progress = i / (epochs - 1);
      const baseAcc = 0.1 + progress * 0.3; // 0.1 to 0.4
      const noise = (Math.random() - 0.5) * 0.05;
      return Math.max(0.1, Math.min(0.95, baseAcc + noise));
    });

    // Create line geometry
    const points = curveData.map((val, i) => {
      const x = THREE.MathUtils.lerp(-0.9, 0.9, i / (epochs - 1));
      const y = THREE.MathUtils.lerp(-0.7, 0.7, (val - 0.1) / 0.85);
      return new THREE.Vector3(x, y, 0);
    });

    const curveGeometry = new THREE.BufferGeometry().setFromPoints(points);
    const curveMaterial = new THREE.LineBasicMaterial({
      color: ARM_COLORS[data.coordinate.credit] || PALETTE.gradient,
      linewidth: 2,
    });
    const curve = new THREE.Line(curveGeometry, curveMaterial);
    this.sparklineScene.add(curve);

    // Add chance line
    const chanceY = THREE.MathUtils.lerp(-0.7, 0.7, (0.1 - 0.1) / 0.85);
    const chanceGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-0.9, chanceY, 0),
      new THREE.Vector3(0.9, chanceY, 0),
    ]);
    const chanceMaterial = new THREE.LineDashedMaterial({
      color: PALETTE.chance_line,
      dashSize: 0.05,
      gapSize: 0.03,
      linewidth: 1,
    });
    const chanceLine = new THREE.Line(chanceGeometry, chanceMaterial);
    chanceLine.computeLineDistances();
    this.sparklineScene.add(chanceLine);

    // Add axis lines
    const axisGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-0.9, -0.7, 0),
      new THREE.Vector3(0.9, -0.7, 0),
      new THREE.Vector3(-0.9, -0.7, 0),
      new THREE.Vector3(-0.9, 0.7, 0),
    ]);
    const axisMaterial = new THREE.LineBasicMaterial({
      color: PALETTE.border,
      linewidth: 1,
    });
    const axes = new THREE.LineSegments(axisGeometry, axisMaterial);
    this.sparklineScene.add(axes);

    // Animate
    const animate = () => {
      if (
        !this.sparklineRenderer ||
        !this.sparklineScene ||
        !this.sparklineCamera
      )
        return;
      this.sparklineRenderer.render(this.sparklineScene, this.sparklineCamera);
      this.sparklineAnimationId = requestAnimationFrame(animate);
    };
    animate();
  }

  private stopSparkline(): void {
    if (this.sparklineAnimationId) {
      cancelAnimationFrame(this.sparklineAnimationId);
      this.sparklineAnimationId = null;
    }
    if (this.sparklineRenderer) {
      this.sparklineRenderer.dispose();
      this.sparklineRenderer = null;
    }
    this.sparklineScene = null;
    this.sparklineCamera = null;
  }
}

export const cellDrawer = new CellDrawer();
registry.register(cellDrawer);
