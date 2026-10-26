/** Pareto chart definition with per-instance state. */

import { createParetoChartView, PARETO_CHART_SPEC, createPerInstanceChartPanelBody } from "../../plotter.js";
import { registerDefinition } from "../definitions.js";
import type {
  ComponentContext,
  ComponentDefinition,
  ComponentHandle,
  JsonValue,
} from "../types.js";
import { metricsStore } from "../../stores/metrics.js";
import { workspaceStore } from "../../stores/workspace.js";
import type { AxisSelection } from "../../layout/types.js";

interface ChartState {
  metric?: string;
  runId?: string | null;
  axes?: AxisSelection;
}

export const paretoChartDefinition: ComponentDefinition =
  registerDefinition<JsonValue>({
    type: "pareto-chart",
    title: PARETO_CHART_SPEC.title,
    icon: PARETO_CHART_SPEC.glyph,
    defaultSize: { width: 400, height: 300 },
    defaultState: { metric: "pareto", runId: null, axes: null } as unknown as JsonValue,
    create(
      host: HTMLElement,
      state: JsonValue,
      ctx: ComponentContext,
    ): ComponentHandle<JsonValue> {
      const chartState = state as unknown as ChartState;
      // Resolve effective runId and axes from state or workspace
      const effectiveRunId = chartState.runId ?? ctx.workspace.getSelectedRunId();
      const effectiveAxes = chartState.axes ?? ctx.workspace.getAxes();

      host.innerHTML = createPerInstanceChartPanelBody(PARETO_CHART_SPEC);
      const view = createParetoChartView(host, {
        runId: effectiveRunId,
        axes: effectiveAxes,
        metricsStore,
        workspace: ctx.workspace,
      });
      return {
        element: host,
        update(next: JsonValue): void {
          const nextState = next as unknown as ChartState;
          const newRunId = nextState.runId ?? ctx.workspace.getSelectedRunId();
          const newAxes = nextState.axes ?? ctx.workspace.getAxes();
          view.updateRunAndAxes(newRunId, newAxes);
        },
        dispose(): void {
          view.dispose();
          host.remove();
        },
      };
    },
  });
