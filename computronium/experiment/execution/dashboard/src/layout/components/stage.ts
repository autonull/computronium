/** Stage panel definition: hosts a StageSurface and switches StageViewInstances. */

import { StageSurfaceImpl } from "../../components/stage/Surface.js";
import { createStageViewInstance, listStageViews, getDefaultStageView } from "../../components/stage/registry.js";
import { registerDefinition } from "../definitions.js";
import { dockviewHost, DockviewHost } from "../dockview-host.js";

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
  // No defaultSize — stage fills its panel via flex
  minSize: { width: 400, height: 300 },
  defaultState: defaultStageState as unknown as JsonValue,
  create(
    host: HTMLElement,
    state: JsonValue,
    ctx: ComponentContext,
  ): ComponentHandle<JsonValue> {
    host.style.display = "flex";
    host.style.flexDirection = "column";
    host.style.overflow = "hidden";
    host.style.position = "relative"; // For absolute-positioned toolbar

    // Create the surface
    const surface = new StageSurfaceImpl();
    host.appendChild(surface.root);
    // Surface root fills the host (toolbar is overlay, not flex child)
    surface.root.style.position = "absolute";
    surface.root.style.inset = "0";

    const instanceId = ctx.instanceId;
    let viewInstance: StageViewInstance | null = null;
    let viewInitPromise: Promise<void> | null = null;
    let currentView: string | null = null;
    let currentRunId: string | null = null;
    let currentAxes: { x: string; y: string; z: string } | null = null;
    let panelState: StageState = { ...defaultStageState, ...(state as unknown as StageState) };

    surface.start();

    // Overlay toolbar — never reduces canvas height
    const toolbar = document.createElement("div");
    toolbar.className = "stage-toolbar";
    toolbar.style.cssText = `
      position: absolute;
      top: 8px;
      right: 8px;
      height: 24px;
      pointer-events: none;
      display: flex;
      align-items: center;
      gap: 6px;
      opacity: 0.4;
      transition: opacity 0.2s ease;
      z-index: 10;
    `;
    // Restore opacity on hover/focus of host
    host.addEventListener("mouseenter", () => { toolbar.style.opacity = "1"; });
    host.addEventListener("mouseleave", () => { toolbar.style.opacity = "0.4"; });
    host.addEventListener("focusin", () => { toolbar.style.opacity = "1"; });
    host.addEventListener("focusout", () => { toolbar.style.opacity = "0.4"; });

    // Toolbar content (pointer-events: auto so children are interactive)
    const toolbarContent = document.createElement("div");
    toolbarContent.style.cssText = `
      pointer-events: auto;
      display: flex;
      align-items: center;
      gap: 6px;
    `;
    toolbar.appendChild(toolbarContent);

    const viewSelect = document.createElement("select");
    viewSelect.className = "stage-view-select";
    viewSelect.title = "Stage view";
    for (const definition of listStageViews()) {
      const option = document.createElement("option");
      option.value = definition.view;
      option.textContent = definition.title;
      viewSelect.appendChild(option);
    }
    viewSelect.style.cssText = "background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border); border-radius: 4px; font-size: 11px; padding: 2px 6px; height: 24px;";
    viewSelect.addEventListener("change", () => ctx.setState({ view: viewSelect.value }));

    const runSelect = document.createElement("select");
    runSelect.className = "stage-run-select";
    runSelect.title = "Run";
    runSelect.style.cssText = viewSelect.style.cssText;
    runSelect.addEventListener("change", () =>
      ctx.setState({ runId: runSelect.value || null }),
    );

    const maximizeBtn = document.createElement("button");
    maximizeBtn.title = "Maximize";
    maximizeBtn.textContent = "⛶";
    maximizeBtn.style.cssText = "width: 24px; height: 24px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 4px; color: var(--text-primary); font-size: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center;";
    maximizeBtn.addEventListener("click", () => {
      const api = dockviewHost.getApi();
      if (api) {
        const panel = api.getPanel(instanceId);
        if (panel) api.maximizeGroup(panel);
      }
    });

    toolbarContent.append(viewSelect, runSelect, maximizeBtn);
    host.appendChild(toolbar);

    const renderRuns = (): void => {
      const runs = ctx.workspace.getRuns();
      const selected = effectiveRunId();
      runSelect.innerHTML = "";
      const workspaceOption = document.createElement("option");
      workspaceOption.value = "";
      workspaceOption.textContent = "Workspace run";
      runSelect.appendChild(workspaceOption);
      for (const run of runs) {
        const option = document.createElement("option");
        option.value = run.run_id;
        option.textContent = run.run_id.slice(0, 8);
        runSelect.appendChild(option);
      }
      runSelect.value = panelState.runId ?? "";
      runSelect.title = selected ?? "No run selected";
    };

    const effectiveRunId = (): string | null =>
      panelState.runId ?? ctx.workspace.getSelectedRunId();

    const effectiveAxes = (): { x: string; y: string; z: string } => {
      const axes = panelState.axes ?? ctx.workspace.getAxes();
      return { x: axes.x, y: axes.y, z: axes.z };
    };

    const syncHeader = (): void => {
      viewSelect.value = panelState.view ?? getDefaultStageView();
      renderRuns();
    };

    // Handle resize via ResizeObserver on host
    const resizeObserver = new ResizeObserver(() => {
      surface.resize();
      if (viewInstance) {
        viewInstance.resize(surface.size());
      }
    });
    resizeObserver.observe(host);

    // Subscribe to workspace changes for run/axes updates
    const workspaceUnsub = ctx.workspace.onChange(() => {
      syncHeader();
      ensureViewInstance(panelState);
    });

    const ensureViewInstance = (st: StageState): void => {
      const view = st.view ?? getDefaultStageView();
      const runId = st.runId ?? ctx.workspace.getSelectedRunId();
      const axes = st.axes ?? ctx.workspace.getAxes();

      const viewChanged = view !== currentView;
      const runChanged = runId !== currentRunId;
      const axesChanged = axes.x !== currentAxes?.x || axes.y !== currentAxes?.y || axes.z !== currentAxes?.z;

      if (viewChanged || runChanged || axesChanged || !viewInstance) {
        // Dispose old view if switching
        if (viewInstance) {
          viewInstance.dispose();
          DockviewHost.unregisterStageInstance(instanceId);
        }

        // Create new view instance
        const viewState = { ...st, runId, axes };
        viewInstance = createStageViewInstance(view, {
          surface: surface as StageSurface,
          flat: surface.flat,
          workspace: ctx.workspace,
          state: viewState,
          instanceId,
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
      }
    };

    const handle: ComponentHandle<JsonValue> & { viewInitPromise?: Promise<void> } = {
      element: host,
      get viewInitPromise() {
        return viewInitPromise ?? undefined;
      },
      update(next: JsonValue): void {
        panelState = { ...panelState, ...(next as unknown as StageState) };
        syncHeader();
        ensureViewInstance(panelState);
      },
      dispose(): void {
        resizeObserver.disconnect();
        workspaceUnsub();
        viewInstance?.dispose();
        DockviewHost.unregisterStageInstance(instanceId);
        surface.dispose();
        toolbar.remove();
      },
    };

    // Initialize with initial state (which may be empty - update will be called again with real params)
    syncHeader();
    ensureViewInstance(panelState);

    return handle;
  },
});