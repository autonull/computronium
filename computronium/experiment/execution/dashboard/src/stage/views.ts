/** What stands on the stage (TODO69 Phase 5).

    A view is a component with four parts: it puts its objects on the shared
    scene, it takes them off again, it re-reads the run's records, and it
    frames the camera. The discovery map already had all four, so the shape
    was copied rather than invented.
*/

import type { StageChange } from "./state.js";

export interface StageView {
  /** The view's name, as the reader sees it. */
  id: string;
  name: string;
  /** What a reader would say after looking at it. */
  caption: string;
  /** Put the view on the stage. */
  enter(): void;
  /** Take the view off the stage: nothing of it may remain. */
  exit(): void;
  /** Re-read the run's records and redraw. */
  refresh(change: StageChange): void;
  /** Whether the view has something to show. */
  ready(): boolean;
}
