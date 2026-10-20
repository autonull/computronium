## The dashboard, in pictures

The live dashboard is a three.js application that watches a campaign and shows
what it is doing: the space it is searching, the cells it has measured, the
cells the system refuses, and the charts the evidence draws. It says what it
is doing in words, at the bottom of the screen, so a reader who sees only the
picture can follow it.

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

The same run, told three other ways — as a report in the browser, as the
console dashboard in a terminal, and as the dashboard's own account of itself:

| The report | The console dashboard | The narration |
|---|---|---|
| ![The report](docs/readme/assets/report-run.png) | ![The console dashboard](docs/readme/assets/console-dashboard.png) | ![The narration](docs/readme/assets/narration-script.png) |

The narration is written once, on the server, and read by two: the browser
renders it as captions, and `GET /api/narration` hands the same sentences to
anything that wants to read the screen without a browser. It speaks in words
rather than figures — the panels carry the numbers, the narration carries the
meaning — and every claim it makes can be checked against the picture.

See [the dashboard guide](docs/DASHBOARD.md) for the endpoints, the keyboard
shortcuts, and how the pictures are made.
