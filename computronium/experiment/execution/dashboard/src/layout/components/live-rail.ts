/** Live-rail definition: every instance keeps its own event history. */

import { createRailBody, LiveRailView } from "../../live-rail.js";
import { registerDefinition } from "../definitions.js";
import type {
  ComponentContext,
  ComponentDefinition,
  ComponentHandle,
  JsonValue,
} from "../types.js";

export const liveRailDefinition: ComponentDefinition =
  registerDefinition<JsonValue>({
    type: "live-rail",
    title: "Live Rail",
    icon: "≡",
    defaultSize: { width: 320, height: 240 },
    create(
      host: HTMLElement,
      _state: JsonValue,
      _ctx: ComponentContext,
    ): ComponentHandle<JsonValue> {
      host.innerHTML = createRailBody();
      const view = new LiveRailView(host);
      return {
        element: host,
        dispose(): void {
          view.dispose();
          host.remove();
        },
      };
    },
  });
