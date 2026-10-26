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

    // Parse state
    const stageState = state as unknown as StageState;
    const viewState = { ...stageState, runId: stageState.runId ?? ctx.workspace.selectedRunId };
    let viewInstance: StageViewInstance | null = createStageViewInstance(stageState.view, {
      surface: surface as StageSurface,
      flat: surface.flat,
      workspace: ctx.workspace,
      state: viewState,
    });

    let initPromise: Promise<void> | null = null;
    if (viewInstance) {
      initPromise = viewInstance.init().then(() => {
        viewInstance?.mount();
      });
    }

    surface.start();

    // Register with DockviewHost for measured cells query
    const instanceId = ctx.instanceId;
    if (viewInstance) {
      DockviewHost.registerStageInstance(instanceId, viewInstance);
    }

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
        const runId = stageState.runId ?? ctx.workspace.getSelectedRunId();
        const axes = ctx.workspace.getAxes();
        viewInstance.refresh({ kind: "data", runId: runId ?? undefined });
      }
    });

    return {
      element: host,
      update(next: JsonValue): void {
        const nextState = next as unknown as StageState;
        // View switch
        if (nextState.view !== stageState.view) {
          viewInstance?.dispose();
          const newViewInstance = createStageViewInstance(nextState.view, {
            surface: surface as StageSurface,
            flat: surface.flat,
            workspace: ctx.workspace,
            state: { ...nextState, runId: nextState.runId ?? ctx.workspace.getSelectedRunId() },
          });
          viewInstance = newViewInstance;
          if (newViewInstance) {
            newViewInstance.init().then(() => {
              newViewInstance.mount();
              newViewInstance.resize(surface.size());
              DockviewHost.registerStageInstance(instanceId, newViewInstance);
            });
          }
        }
        // Run/axes change — refresh the view
        else if (nextState.runId !== stageState.runId || nextState.axes !== stageState.axes) {
          viewInstance?.refresh({ kind: "data", runId: nextState.runId ?? undefined });
        }
      },
      dispose(): void {
        resizeObserver.disconnect();
        workspaceUnsub();
        viewInstance?.dispose();
        DockviewHost.unregisterStageInstance(instanceId);
        surface.dispose();
      },
    };
  },
});