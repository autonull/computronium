/** Stage panel definition: hosts a StageSurface and switches StageViewInstances. */

import { StageSurfaceImpl } from "../../components/stage/Surface.js";
import { createStageViewInstance, listStageViews, getDefaultStageView } from "../../components/stage/registry.js";
import { registerDefinition } from "../definitions.js";
import { DockviewHost } from "../dockview-host.js";

// Import stage views so they self-register
import "../../components/stage/views/index.js";
import type {
  ComponentContext,
  ComponentDefinition,
  ComponentHandle,
  JsonValue,
  Size,
  StageChange,
  StageSurface,
  StageCanvas,
  StageViewInstance,
} from "../types.js";

interface StageState {
  view: string;
  runId?: string | null;
  axes?: { x: string; y: string; z: string };
}

const defaultStageState: StageState = {
  view: getDefaultStageView(),
  runId: null,
  axes: { x: "credit", y: "geometry", z: "dynamics" },
};

export const stageDefinition: ComponentDefinition = registerDefinition<JsonValue>({
  type: "stage",
  title: "3D Stage",
  icon: "⬢",
  defaultSize: { width: 800, height: 600 },
  minSize: { width: 400, height: 300 },
  defaultState: defaultStageState as unknown as JsonValue,
  create(
    host: HTMLElement,
    state: JsonValue,
    ctx: ComponentContext,
  ): ComponentHandle<JsonValue> {
    // Create the surface
    const surface = new StageSurfaceImpl();
    host.appendChild(surface.root);

    const instanceId = ctx.instanceId;
    let viewInstance: StageViewInstance | null = null;
    let viewInitPromise: Promise<void> | null = null;
    let currentView: string | null = null;
    let currentRunId: string | null = null;
    let currentAxes: { x: string; y: string; z: string } | null = null;

    surface.start();

    // Handle resize
    const resizeObserver = new ResizeObserver(() => {
      surface.resize();
      if (viewInstance) {
        viewInstance.resize(surface.size());
      }
    });
    resizeObserver.observe(host);

    // Subscribe to workspace changes for run/axes updates
    const workspaceUnsub = ctx.workspace.onChange(() => {
      if (viewInstance) {
        const runId = currentRunId ?? ctx.workspace.getSelectedRunId();
        const axes = ctx.workspace.getAxes();
        viewInstance.refresh({ kind: "data", runId: runId ?? undefined });
      }
    });

    const ensureViewInstance = (st: StageState): void => {
      const view = st.view ?? "space";
      const runId = st.runId ?? ctx.workspace.getSelectedRunId();
      const axes = st.axes ?? ctx.workspace.getAxes();

      const viewChanged = view !== currentView;
      const runChanged = runId !== currentRunId;
      const axesChanged = axes.x !== currentAxes?.x || axes.y !== currentAxes?.y || axes.z !== currentAxes?.z;

      if (viewChanged || !viewInstance) {
        // Dispose old view if switching
        if (viewInstance) {
          viewInstance.dispose();
          DockviewHost.unregisterStageInstance(instanceId);
        }

        // Create new view instance
        const viewState = { ...st, runId };
        viewInstance = createStageViewInstance(view, {
          surface: surface as StageSurface,
          flat: surface.flat,
          workspace: ctx.workspace,
          state: viewState,
        });

        if (viewInstance) {
          const vi = viewInstance;
          viewInitPromise = vi.init().then(() => {
            vi.mount();
            vi.resize(surface.size());
            DockviewHost.registerStageInstance(instanceId, vi);
          });
        }

        currentView = view;
        currentRunId = runId;
        currentAxes = { ...axes };
      } else if (runChanged || axesChanged) {
        // Same view, different run/axes — just refresh
        currentRunId = runId;
        currentAxes = { ...axes };
        viewInstance?.refresh({ kind: "data", runId: runId ?? undefined });
      }
    };

    const handle: ComponentHandle<JsonValue> & { viewInitPromise?: Promise<void> } = {
      element: host,
      get viewInitPromise() {
        return viewInitPromise ?? undefined;
      },
      update(next: JsonValue): void {
        const nextState = next as unknown as StageState;
        ensureViewInstance(nextState);
      },
      dispose(): void {
        resizeObserver.disconnect();
        workspaceUnsub();
        viewInstance?.dispose();
        DockviewHost.unregisterStageInstance(instanceId);
        surface.dispose();
      },
    };

    // Initialize with initial state (which may be empty - update will be called again with real params)
    ensureViewInstance(state as unknown as StageState);

    return handle;
  },
});