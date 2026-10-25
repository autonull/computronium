/** Variability chart definition. */

import { PlotterVariabilityView, createChartPanelBody, CHARTS } from "../../plotter.js";
import { registerDefinition } from "../definitions.js";
import type {
  ComponentContext,
  ComponentDefinition,
  ComponentHandle,
  JsonValue,
} from "../types.js";

const variabilitySpec = CHARTS.find((c) => c.id === "variability")!;

export const variabilityChartDefinition: ComponentDefinition =
  registerDefinition<JsonValue>({
    type: "variability-chart",
    title: variabilitySpec.title,
    icon: variabilitySpec.glyph,
    defaultSize: { width: 400, height: 300 },
    create(
      host: HTMLElement,
      _state: JsonValue,
      _ctx: ComponentContext,
    ): ComponentHandle<JsonValue> {
      host.innerHTML = createChartPanelBody(variabilitySpec);
      const view = new PlotterVariabilityView(host);
      return {
        element: host,
        dispose(): void {
          view.dispose();
          host.remove();
        },
      };
    },
  });
