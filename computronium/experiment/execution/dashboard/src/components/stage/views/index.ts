/** Stage view definitions — register all views here (TODO72 P5/P6). */

import { registerStageView } from "../registry.js";
import { spaceViewDefinition } from "./space.js";

// Register the space view
registerStageView(spaceViewDefinition);

// Re-export for external access
export { spaceViewDefinition };