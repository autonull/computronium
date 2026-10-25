/** Cell-drawer definition: every instance owns its nodes and subscriptions. */

import { CellDrawerView, createCellDrawerBody } from "../../cell-drawer.js";
import { registerDefinition } from "../definitions.js";
import type {
  ComponentContext,
  ComponentDefinition,
  ComponentHandle,
  JsonValue,
} from "../types.js";

export const cellDrawerDefinition: ComponentDefinition =
  registerDefinition<JsonValue>({
    type: "cell-drawer",
    title: "Cell Details",
    icon: "◧",
    defaultSize: { width: 360, height: 480 },
    create(
      host: HTMLElement,
      _state: JsonValue,
      _ctx: ComponentContext,
    ): ComponentHandle<JsonValue> {
      host.innerHTML = createCellDrawerBody();
      const view = new CellDrawerView(host);
      return {
        element: host,
        dispose(): void {
          view.dispose();
          host.remove();
        },
      };
    },
  });
