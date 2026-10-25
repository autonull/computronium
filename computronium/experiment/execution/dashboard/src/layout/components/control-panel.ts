/** Control-panel definition: every instance owns its nodes and subscriptions. */

import { ControlPanelView, createControlPanelBody } from "../../control-panel.js";
import { registerDefinition } from "../definitions.js";
import type {
  ComponentContext,
  ComponentDefinition,
  ComponentHandle,
  JsonValue,
} from "../types.js";

export const controlPanelDefinition: ComponentDefinition =
  registerDefinition<JsonValue>({
    type: "control-panel",
    title: "Control Panel",
    icon: "⚙",
    defaultSize: { width: 400, height: 500 },
    create(
      host: HTMLElement,
      _state: JsonValue,
      ctx: ComponentContext,
    ): ComponentHandle<JsonValue> {
      host.innerHTML = createControlPanelBody();
      const view = new ControlPanelView(host);
      return {
        element: host,
        update(next: JsonValue): void {
          view.update(next);
        },
        dispose(): void {
          view.dispose();
          host.remove();
        },
      };
    },
  });
