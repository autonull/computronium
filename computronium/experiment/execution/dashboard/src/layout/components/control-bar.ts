/** Control-bar definition: instances share one poller, never one element. */

import { ControlBarView, createControlBarBody } from "../../control-bar.js";
import { registerDefinition } from "../definitions.js";
import type {
  ComponentContext,
  ComponentDefinition,
  ComponentHandle,
  JsonValue,
} from "../types.js";

export const controlBarDefinition: ComponentDefinition =
  registerDefinition<JsonValue>({
    type: "control-bar",
    title: "Control Bar",
    icon: "⏯",
    defaultSize: { width: 720, height: 100 },
    create(
      host: HTMLElement,
      _state: JsonValue,
      ctx: ComponentContext,
    ): ComponentHandle<JsonValue> {
      host.innerHTML = createControlBarBody();
      const view = new ControlBarView(host, () => {
        ctx.commands.execute("control-panel");
      });
      return {
        element: host,
        dispose(): void {
          view.dispose();
          host.remove();
        },
      };
    },
  });
