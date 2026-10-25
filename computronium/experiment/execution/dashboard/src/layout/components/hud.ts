/** HUD definition: every instance owns its nodes and subscriptions. */

import { createHudBody, HudView } from "../../hud.js";
import { registerDefinition } from "../definitions.js";
import type {
  ComponentContext,
  ComponentDefinition,
  ComponentHandle,
  JsonValue,
} from "../types.js";

export const hudDefinition: ComponentDefinition = registerDefinition<JsonValue>({
  type: "hud",
  title: "Mission Control",
  icon: "◱",
  defaultSize: { width: 360, height: 300 },
  create(
    host: HTMLElement,
    state: JsonValue,
    _ctx: ComponentContext,
  ): ComponentHandle<JsonValue> {
    host.innerHTML = createHudBody();
    const view = new HudView(host, state);
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
