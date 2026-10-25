/** Ablation chart definition. */

import { PlotterAblationView, createChartPanelBody, CHARTS } from "../../plotter.js";
import { registerDefinition } from "../definitions.js";
import type {
  ComponentContext,
  ComponentDefinition,
  ComponentHandle,
  JsonValue,
} from "../types.js";

const ablationSpec = CHARTS.find((c) => c.id === "ablation")!;

export const ablationChartDefinition: ComponentDefinition =
  registerDefinition<JsonValue>({
    type: "ablation-chart",
    title: ablationSpec.title,
    icon: ablationSpec.glyph,
    defaultSize: { width: 400, height: 300 },
    create(
      host: HTMLElement,
      _state: JsonValue,
      _ctx: ComponentContext,
    ): ComponentHandle<JsonValue> {
      host.innerHTML = createChartPanelBody(ablationSpec);
      const view = new PlotterAblationView(host);
      return {
        element: host,
        dispose(): void {
          view.dispose();
          host.remove();
        },
      };
    },
  });
