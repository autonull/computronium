## The dashboard, in pictures

The live dashboard is a three.js application that watches a campaign and shows
what it is doing: the space it is searching, the cells it has measured, the
cells the system refuses, and the charts the evidence draws. Its canvas is a
stage: the same run can be seen as a space, a terrain, a frontier, a matrix, a
family of curves, a stack of sheets, or as the spread and the cost of its own
evidence. It says what it is doing in words, at the bottom of the screen, so a
reader who sees only the picture can follow it.

```bash
uv run comp dashboard --store experiment.duckdb   # the dashboard
uv run comp run demo --store experiment.duckdb     # a campaign to watch
```

| The whole system | The space, alone | One cell's evidence |
|---|---|---|
| ![The dashboard](docs/readme/assets/dashboard-hero.png) | ![The discovery map](docs/readme/assets/dashboard-map.png) | ![A measured cell](docs/readme/assets/dashboard-cell.png) |

| What the system refuses | The charts | The caption |
|---|---|---|
| ![A void cell](docs/readme/assets/dashboard-void.png) | ![The Pareto chart](docs/readme/assets/dashboard-pareto.png) | ![The caption](docs/readme/assets/dashboard-caption.png) |

And the dashboard is an instrument, not a picture: the verbs at the bottom of
the screen reach the run itself, through a control plane the run in another
process reads. The rail down the right edge says which panels are open, and
the legend's toolbar holds every view of the stage at once:

| The control bar | The control panel | Mission Control | Discovery Legend |
|---|---|---|---|
| ![The control bar](docs/readme/assets/panel-control-bar.png) | ![The control panel](docs/readme/assets/panel-control-panel.png) | ![Mission Control](docs/readme/assets/panel-hud.png) | ![Discovery Legend](docs/readme/assets/panel-legend.png) |

| Pareto | Ablation | Variability | Live Rail | Caption |
|---|---|---|---|---|
| ![Pareto](docs/readme/assets/panel-pareto.png) | ![Ablation](docs/readme/assets/panel-ablation.png) | ![Variability](docs/readme/assets/panel-variability.png) | ![Live Rail](docs/readme/assets/panel-live-rail.png) | ![Caption](docs/readme/assets/panel-caption.png) |

Play and pause the run, step it one batch at a time, move the ceiling on the
cells in flight at once, and start a run from nothing — all of it from the
browser, and all of it reaching the run rather than a picture of it.

**Workspaces** — four named arrangements, one switch:
| Watch | Audit | Drive | Free |
|---|---|---|---|
| ![Watch](docs/readme/assets/dashboard-watch.png) | ![Audit](docs/readme/assets/dashboard-audit.png) | ![Drive](docs/readme/assets/dashboard-drive.png) | ![Free](docs/readme/assets/dashboard-free.png) |

The canvas is a stage, and the view is a choice: `V` cycles the views, the
number keys pick one — and a view that does not fit in the numbers has a
letter of its own — and the legend names the view that is on.

---

### Stage Views (captured from live dashboard)

| Space (Discovery Map) | Terrain | Frontier | Matrix | Convergence |
|---|---|---|---|---|
| ![Space](docs/screenshots/tour/stage-space.png) | ![Terrain](docs/screenshots/tour/stage-terrain.png) | ![Frontier](docs/screenshots/tour/stage-frontier.png) | ![Matrix](docs/screenshots/tour/stage-matrix.png) | ![Convergence](docs/screenshots/tour/stage-convergence.png) |

| Layers | Slices | Multi-run | Ledger | Timeline |
|---|---|---|---|---|
| ![Layers](docs/screenshots/tour/stage-layers.png) | ![Slices](docs/screenshots/tour/stage-slices.png) | ![Multi-run](docs/screenshots/tour/stage-multirun.png) | ![Ledger](docs/screenshots/tour/stage-ledger.png) | ![Timeline](docs/screenshots/tour/stage-timeline.png) |

| Small Multiples | Spread | Claim Cost | Uncertainty | Contrast |
|---|---|---|---|---|
| ![Small Multiples](docs/screenshots/tour/stage-small-multiples.png) | ![Spread](docs/screenshots/tour/stage-spread.png) | ![Claim Cost](docs/screenshots/tour/stage-claim-cost.png) | ![Uncertainty](docs/screenshots/tour/stage-uncertainty.png) | ![Contrast](docs/screenshots/tour/stage-contrast.png) |

| Flow | Effect | Trajectory | Spectrum | Basin |
|---|---|---|---|---|
| ![Flow](docs/screenshots/tour/stage-flow.png) | ![Effect](docs/screenshots/tour/stage-effect.png) | ![Trajectory](docs/screenshots/tour/stage-trajectory.png) | ![Spectrum](docs/screenshots/tour/stage-spectrum.png) | ![Basin](docs/screenshots/tour/stage-basin.png) |

| Landscape | Trained Trajectory | Trained Spectrum | Trained Basin | Trained Landscape |
|---|---|---|---|---|
| ![Landscape](docs/screenshots/tour/stage-landscape.png) | ![Trained Trajectory](docs/screenshots/tour/stage-trained-trajectory.png) | ![Trained Spectrum](docs/screenshots/tour/stage-trained-spectrum.png) | ![Trained Basin](docs/screenshots/tour/stage-trained-basin.png) | ![Trained Landscape](docs/screenshots/tour/stage-trained-landscape.png) |

| Plot2D | Ramp |
|---|---|
| ![Plot2D](docs/screenshots/tour/stage-plot2d.png) | ![Ramp](docs/screenshots/tour/stage-ramp.png) |

---

*All stage view images above are live captures from the Dockview-migrated dashboard (TODO73), cropped to the stage panel. Full dashboard workspace shots are the four presets above (Watch, Audit, Drive, Free).*

---

**Legacy system captures** (not yet re-captured after Dockview migration):

- Report views: `report-run.png`, `console-dashboard.png`, `narration-script.png`
- Figure gallery: `figure-seed-violins.png`, `figure-gallery-swap-credit.png`, `figure-gallery-epc-settle.png`, `figure-gallery-coverage.png`, `figure-gallery-failures.png`
- Report plots: `report-pareto.png`, `report-seed-stability.png`
- Coverage/catalogue: `coverage-report.png`, `catalog.png`, `method-cards.png`, `power-analysis.png`
- Cell/void evidence: `dashboard-cell.png`, `dashboard-void.png`, `dashboard-caption.png`, `dashboard-pareto.png`

These will be regenerated in a follow-up capture pass.

See [the dashboard guide](docs/DASHBOARD.md) for the endpoints, the keyboard
shortcuts, and how the pictures are made.