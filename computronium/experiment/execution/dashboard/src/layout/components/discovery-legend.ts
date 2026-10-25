/** Discovery-legend definition: every instance owns its nodes and subscriptions. */

import { DiscoveryLegendView, createLegendBody } from "../../discovery-legend.js";
import { registerDefinition } from "../definitions.js";
import type {
  ComponentContext,
  ComponentDefinition,
  ComponentHandle,
  JsonValue,
} from "../types.js";

export const discoveryLegendDefinition: ComponentDefinition =
  registerDefinition<JsonValue>({
    type: "discovery-legend",
    title: "Discovery Map",
    icon: "▦",
    defaultSize: { width: 360, height: 280 },
    create(
      host: HTMLElement,
      _state: JsonValue,
      _ctx: ComponentContext,
    ): ComponentHandle<JsonValue> {
      host.innerHTML = createLegendBody();
      const view = new DiscoveryLegendView(host);
      return {
        element: host,
        dispose(): void {
          view.dispose();
          host.remove();
        },
      };
    },
  });
