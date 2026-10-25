/** Stage view definitions — register all views here (TODO72 P5/P6). */

import { registerStageView } from "../registry.js";
import { spaceViewDefinition } from "./space.js";
import { ledgerViewDefinition } from "./ledger.js";
import { timelineViewDefinition } from "./timeline.js";
import { landscapeViewDefinition } from "./landscape.js";
import { basinViewDefinition } from "./basin.js";
import { spectrumViewDefinition } from "./spectrum.js";
import { trajectoryViewDefinition } from "./trajectory.js";
import { flowViewDefinition } from "./flow.js";
import { frontierViewDefinition } from "./frontier.js";
import { contrastViewDefinition } from "./contrast.js";
import { convergenceViewDefinition } from "./convergence.js";
import { uncertaintyViewDefinition } from "./uncertainty.js";
import { effectViewDefinition } from "./effect.js";
import { spreadViewDefinition } from "./spread.js";
import { matrixViewDefinition } from "./matrix.js";
import { layersViewDefinition } from "./layers.js";
import { slicesViewDefinition } from "./slices.js";
import { smallMultiplesViewDefinition } from "./small-multiples.js";
import { terrainViewDefinition } from "./terrain.js";
import { claimCostViewDefinition } from "./claim-cost.js";
import { multirunViewDefinition } from "./multirun.js";
import { trainedTrajectoryViewDefinition } from "./trained-trajectory.js";
import { trainedBasinViewDefinition } from "./trained-basin.js";
import { trainedLandscapeViewDefinition } from "./trained-landscape.js";
import { trainedSpectrumViewDefinition } from "./trained-spectrum.js";

// Register all stage views
registerStageView(spaceViewDefinition);
registerStageView(ledgerViewDefinition);
registerStageView(timelineViewDefinition);
registerStageView(landscapeViewDefinition);
registerStageView(basinViewDefinition);
registerStageView(spectrumViewDefinition);
registerStageView(trajectoryViewDefinition);
registerStageView(flowViewDefinition);
registerStageView(frontierViewDefinition);
registerStageView(contrastViewDefinition);
registerStageView(convergenceViewDefinition);
registerStageView(uncertaintyViewDefinition);
registerStageView(effectViewDefinition);
registerStageView(spreadViewDefinition);
registerStageView(matrixViewDefinition);
registerStageView(layersViewDefinition);
registerStageView(slicesViewDefinition);
registerStageView(smallMultiplesViewDefinition);
registerStageView(terrainViewDefinition);
registerStageView(claimCostViewDefinition);
registerStageView(multirunViewDefinition);
registerStageView(trainedTrajectoryViewDefinition);
registerStageView(trainedBasinViewDefinition);
registerStageView(trainedLandscapeViewDefinition);
registerStageView(trainedSpectrumViewDefinition);

// Re-export for external access
export {
  spaceViewDefinition,
  ledgerViewDefinition,
  timelineViewDefinition,
  landscapeViewDefinition,
  basinViewDefinition,
  spectrumViewDefinition,
  trajectoryViewDefinition,
  flowViewDefinition,
  frontierViewDefinition,
  contrastViewDefinition,
  convergenceViewDefinition,
  uncertaintyViewDefinition,
  effectViewDefinition,
  spreadViewDefinition,
  matrixViewDefinition,
  layersViewDefinition,
  slicesViewDefinition,
  smallMultiplesViewDefinition,
  terrainViewDefinition,
  claimCostViewDefinition,
  multirunViewDefinition,
  trainedTrajectoryViewDefinition,
  trainedBasinViewDefinition,
  trainedLandscapeViewDefinition,
  trainedSpectrumViewDefinition,
};