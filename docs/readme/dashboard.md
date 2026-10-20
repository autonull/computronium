## The dashboard, in pictures

The live dashboard is a three.js application that watches a campaign and shows
what it is doing: the space it is searching, the cells it has measured, the
cells the system refuses, and the charts the evidence draws. Its canvas is a
stage: the same run can be seen as a space, a terrain, a frontier, a matrix, a
family of curves, or as the spread and the cost of its own evidence. It says
what it is doing in words, at the bottom of the screen, so a reader who sees
only the picture can follow it.

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

The canvas is a stage, and the view is a choice: `V` cycles the views, the
number keys pick one — and a view that does not fit in the numbers has a
letter of its own — and the legend names the view that is on. The same run,
drawn four ways — a heightfield, a frontier, a table and a family of curves:

| The terrain | The frontier | The evidence matrix | The convergence |
|---|---|---|---|
| ![The terrain](docs/readme/assets/dashboard-terrain.png) | ![The frontier](docs/readme/assets/dashboard-frontier.png) | ![The evidence matrix](docs/readme/assets/dashboard-matrix.png) | ![The convergence](docs/readme/assets/dashboard-convergence.png) |

And the run's evidence, four ways again — every seed of every cell, the
spread of the arms, what the claim still costs in seeds, and the margin
around each mean:

| The small multiples | The spread | The claim's cost | The uncertainty |
|---|---|---|---|
| ![The small multiples](docs/readme/assets/dashboard-multiples.png) | ![The spread](docs/readme/assets/dashboard-spread.png) | ![The claim's cost](docs/readme/assets/dashboard-claim-cost.png) | ![The uncertainty](docs/readme/assets/dashboard-uncertainty.png) |

And the run as a process, and as a judgement — the time it took, what it can
say, and how its arms compare:

| The timeline | The ledger | The contrast |
|---|---|---|
| ![The timeline](docs/readme/assets/dashboard-timeline.png) | ![The ledger](docs/readme/assets/dashboard-ledger.png) | ![The contrast](docs/readme/assets/dashboard-contrast.png) |

The same run, told three other ways — as a report in the browser, as the
console dashboard in a terminal, and as the dashboard's own account of itself:

| The report | The console dashboard | The narration |
|---|---|---|
| ![The report](docs/readme/assets/report-run.png) | ![The console dashboard](docs/readme/assets/console-dashboard.png) | ![The narration](docs/readme/assets/narration-script.png) |

And the same evidence, drawn by the analysis that measures it rather than by
the canvas:

| The seed violins |
|---|
| ![The seed violins](docs/readme/assets/figure-seed-violins.png) |

The narration is written once, on the server, and read by two: the browser
renders it as captions, and `GET /api/narration` hands the same sentences to
anything that wants to read the screen without a browser. It speaks in words
rather than figures — the panels carry the numbers, the narration carries the
meaning — and every claim it makes can be checked against the picture.

See [the dashboard guide](docs/DASHBOARD.md) for the endpoints, the keyboard
shortcuts, and how the pictures are made.
