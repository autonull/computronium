/** Pareto chart definition. */

import { PlotterParetoView, createChartPanelBody, CHARTS } from "../../plotter.js";
import { registerDefinition } from "../definitions.js";
import type {
  ComponentContext,
  ComponentDefinition,
  ComponentHandle,
  JsonValue,
} from "../types.js";

const paretoSpec = CHARTS.find((c) => c.id === "pareto")!;

export const paretoChartDefinition: ComponentDefinition =
  registerDefinition<JsonValue>({
    type: "pareto-chart",
    title: paretoSpec.title,
    icon: paretoSpec.glyph,
    defaultSize: { width: 400, height: 300 },
    create(
      host: HTMLElement,
      _state: JsonValue,
      _ctx: ComponentContext,
    ): ComponentHandle<JsonValue> {
      host.innerHTML = createChartPanelBody(paretoSpec);
      const view = new PlotterParetoView(host);
      return {
        element: host,
        dispose(): void {
          view.dispose();
          host.remove();
        },
      };
    },
  });
