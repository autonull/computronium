/** Caption definition: every instance owns its nodes and subscriptions. */

import { CaptionView, createCaptionBody } from "../../caption.js";
import { registerDefinition } from "../definitions.js";
import type {
  ComponentContext,
  ComponentDefinition,
  ComponentHandle,
  JsonValue,
} from "../types.js";

export const captionDefinition: ComponentDefinition =
  registerDefinition<JsonValue>({
    type: "caption",
    title: "Caption",
    icon: "◈",
    defaultSize: { width: 360, height: 80 },
    create(
      host: HTMLElement,
      _state: JsonValue,
      _ctx: ComponentContext,
    ): ComponentHandle<JsonValue> {
      host.innerHTML = createCaptionBody();
      const view = new CaptionView(host);
      return {
        element: host,
        dispose(): void {
          view.dispose();
          host.remove();
        },
      };
    },
  });
