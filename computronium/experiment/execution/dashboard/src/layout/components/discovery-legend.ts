/** Discovery-legend definition: every instance owns its nodes and subscriptions with per-instance axes. */

import { DiscoveryLegendView, createLegendBody } from "../../discovery-legend.js";
import { registerDefinition } from "../definitions.js";
import type {
  ComponentContext,
  ComponentDefinition,
  ComponentHandle,
  JsonValue,
} from "../types.js";
import type { AxisSelection } from "../../layout/types.js";

interface LegendState {
  runId?: string | null;
  axes?: AxisSelection;
}

export const discoveryLegendDefinition: ComponentDefinition =
  registerDefinition<JsonValue>({
    type: "discovery-legend",
    title: "Discovery Map",
    icon: "▦",
    defaultSize: { width: 360, height: 280 },
    defaultState: { runId: null, axes: null } as unknown as JsonValue,
    create(
      host: HTMLElement,
      state: JsonValue,
      ctx: ComponentContext,
    ): ComponentHandle<JsonValue> {
      const legendState = state as unknown as LegendState;
      // Resolve effective runId and axes from state or workspace
      const effectiveRunId = legendState.runId ?? ctx.workspace.getSelectedRunId();
      const effectiveAxes = legendState.axes ?? ctx.workspace.getAxes();

      host.innerHTML = createLegendBody();
      const view = new DiscoveryLegendView(host, {
        runId: effectiveRunId,
        axes: effectiveAxes,
        workspace: ctx.workspace,
      });
      return {
        element: host,
        update(next: JsonValue): void {
          const nextState = next as unknown as LegendState;
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
