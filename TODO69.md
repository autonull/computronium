# TODO69: The Dashboard Tells Its Own Story — Narration, Screenshots, Video

**Objective**: Make the dashboard legible to a reader who sees only the screen,
so a person — or a model reading the screen — can say what is happening, in
words, without knowing the interface. And give the system more than one
screenshot: a tour of its views, and a short recording of a live session.

**Source**: the request after the hero screenshot landed — *"it would be great
to see more screenshots showing other parts of the system… the dashboard
[should be] self-explanatory as to everything occurring, so that if an AI were
to narrate it based on screen content, it could produce a coherent voice-over
narrative and/or closed-caption overlay. This would effectively 'close the
loop'."*

**Key Decision**: The narration is written **once, on the server, in Python**.
The browser renders it; an agent reads it over HTTP. Two readers, one
vocabulary — the same rule that keeps the palette, the axis metadata and the
report's claims in step.

---

## The main view area shows more than one picture ✅ done

**This was the thing the next session had to do, and it is done.** The
narration, the caption, the tour and the recording were done before it. What
was left was the picture in the middle of the screen: the content area was one
picture in every shot — a grid of coloured cubes — and every picture the tour
took of it looked the same.

The canvas is now a **stage**, and a view is what stands on it. There are
nineteen, and the tour has a shot of each:

| # | View | The picture | The shot |
|---|------|-------------|----------|
| 1 | **The space** | the declared space as a field of cells: the gaps as cages, the measured cells as pillars, the refusals as crosses | `dashboard-map.png` |
| 2 | **The terrain** | the same space as a *heightfield*: accuracy as height over the two free axes, the gaps flat ground, the refusals craters | `dashboard-terrain.png` |
| 3 | **The frontier** | every measured record as a point in (accuracy, speed, parameters), the Pareto front drawn through them, the chance plane as a floor | `dashboard-frontier.png` |
| 4 | **The evidence matrix** | the space *flat*: one axis against another, each cell a number, the refusals in the void colour | `dashboard-matrix.png` |
| 5 | **The convergence** | accuracy against epoch, one curve per arm, the chance line under them | `dashboard-convergence.png` |
| 6 | **The small multiples** | one panel per cell: every seed's own curve, on one accuracy scale | `dashboard-multiples.png` |
| 7 | **The spread** | one violin per arm, across its seeds; the seeds a claim still needs under it | `dashboard-spread.png` |
| 8 | **The claim's cost** | the seeds each cell measured against the seeds a claim needs, with the gap | `dashboard-claim-cost.png` |
| 9 | **The uncertainty** | each cell's mean and the margin the gate asks for, against the chance level | `dashboard-uncertainty.png` |
| 10 | **The timeline** | the run's stages, one lane each, and the time each held it; the longest silence named | `dashboard-timeline.png` |
| 11 | **The ledger** | every arm the run measured, its evidence, and the gate's standing on it; the report's limitations beneath | `dashboard-ledger.png` |
| 12 | **The contrast** | the arms against one another, over the cells they share, with the test's verdict | `dashboard-contrast.png` |
| 13 | **The flow** | the run's cells stage by stage: one column per stage, what it carried and what it wrote, and what the gate refused | `dashboard-flow.png` |
| 14 | **The effect** | one column per axis: a band for an axis whose arms differ, a mark for an axis that was held fixed | `dashboard-effect.png` |
| 15 | **The layers** | the space cut into sheets: one sheet per value of the third axis, the cells the run measured standing up off their own | `dashboard-layers.png` |
| 16 | **The trajectory** | a cell's own state, drawn through the space it moves in, coloured by time, with the error its relaxation was driving down | `dashboard-trajectory.png` |
| 17 | **The spectrum** | the Lyapunov exponents of the cell's own map, one bar per direction, against the zero line | `dashboard-spectrum.png` |
| 18 | **The basin** | the states near the cell's own: how far each stray went, and how many came back | `dashboard-basin.png` |
| 19 | **The landscape** | the cell's own energy over the ground its trajectory crossed, with the path drawn over it | `dashboard-landscape.png` |

**The switcher that makes them a choice**: `V` cycles the views, the number
keys pick the first nine (like the plotter's tabs — which moved to `P`, `A`
and `S` so the numbers could belong to the stage), and the ten that do not
fit in the numbers have a **letter** of their own — `T` the timeline, `L` the
ledger, `D` the contrast, `F` the flow, `E` the effect, `Y` the layers, `J`
the trajectory, `M` the spectrum, `B` the basin, `N` the landscape. A
**View** selector in the legend names the view where it is chosen. The
legend's title is the view's name, and the caption under the selector says
what a reader would say after looking at it.

**The acceptance, in pictures, is now mechanical**: the tour photographs the
fifteen views and then measures them — the browser decodes each pair of
shots and reports the share of the pixels that differ. A pair that is too
alike fails the tour. The measured differences run from 2.4 % to 30.5 %; the
floor is 2 %.

The full catalogue — twenty-odd views, 3D and 2D, from the evidence to the
dynamics of a cell — is in **Phase 5** below, and the surfaces *outside* the
canvas (the gallery, the report's eleven figures, the energy landscape, the
seed violins, the `comp` reports) are in the table after it.

---

## Current State

| Piece | Path | Status |
|-------|------|--------|
| The live dashboard | `computronium/experiment/execution/dashboard/web.py` | complete: 3D map, drawer, charts, HUD, live rail, the three verbs |
| The event bus | `computronium/experiment/execution/events.py` | complete: stage and measurement events, process-wide |
| The narration | `computronium/experiment/execution/dashboard/narration.py` | complete: the sentences, the account, the state |
| The caption | `dashboard/src/caption.ts` | complete: the sentences, rendered |
| **The stage** | `dashboard/src/stage/` | complete: the shared state, fifteen views, the switcher |
| **The run's account** | `computronium/experiment/execution/dashboard/ledger.py` | complete: the ledger, the contrast, the rules they are measured by |
| **The run's arms** | `computronium/experiment/execution/dashboard/arms.py` | complete: the statistics of an arm, read once for the ledger and the effect |
| **The run's flow** | `computronium/experiment/execution/dashboard/flow.py` | complete: the stages, the counts, the refusals, the shape in a sentence |
| **The run's effect** | `computronium/experiment/execution/dashboard/attribution.py` | complete: the axes, the spread, and what the design cannot say |
| **The cell's own dynamics** | `computronium/experiment/execution/dashboard/dynamics.py` | complete: the trajectory, the spectrum, the basin, the landscape |
| **The system's own transition** | `computronium/experiment/analysis/transition.py` | complete: the relaxation the cell's own settle performs, one step at a time |
| The keys | `dashboard/src/keys.ts` | complete: the panels, the charts and the stage's views, in one list |
| The hero capture | `scripts/capture_dashboard_screenshot.py` | one image, one view |
| The tour | `scripts/capture_dashboard_tour.py` | forty-two pictures: nineteen views on the stage, the gallery, the report's own plots, and the `comp` reports |
| The recording | `scripts/capture_dashboard_video.py` | a `.webm` of a live session, uncommitted |
| The live rail | `dashboard/src/live-rail.ts` | terse pills: `[s6_train] train cells` — a log, not a story |
| The console dashboard | `computronium/experiment/execution/dashboard/console.py` | the same picture in a terminal, and a frame of it as text |
| The report | `comp report` | the numbers, as prose and tables |

### What was missing, and what closed it

| Gap | Impact | Closed by |
|-----|--------|-----------|
| No narration | the screen shows numbers and a log; it does not *say* what is happening, so a narrator reading the screen has to reconstruct the story from the panels | `narration.py`: the sentences, written once |
| No closed captions | a recording of the dashboard has no subtitles; the viewer reads a 3D scene in silence | `caption.ts`: the server's sentences, rendered |
| One screenshot | the hero is the dashboard's overview; nothing shows the drawer, the charts, the void cells, the space, the report | the tour: twenty-six views |
| No recording | "show me it working" needs a terminal in front of the reader | the recording: a live session, with captions |
| One picture in the content area | every shot of the canvas was the same field of cubes, so the tour's variety was the furniture in front of the scene | the stage: fourteen views, a switcher, and a shot of each |
| The run was only its evidence | a reader saw what the run measured and nothing of what it *decided*, what it *cannot say*, or how long it took | the ledger, the contrast and the timeline |
| The run was only its records | a reader saw what the run measured and nothing of how the cells got there, or of what the run's design can and cannot be credited for | the flow and the effect |
| The run was only its evidence | a reader saw what the run measured and nothing of the *system* it measured: where its state goes, whether it settles, how wide the set of states that come back to it is | the trajectory, the spectrum, the basin and the landscape |
| The transition the stability analysis measured was the identity | the forward pass was computed and thrown away, and the settle was handed the state it already had, so the map was the identity and the spectrum was a row of zeros | the system's own relaxation, in one place, read by the command and the dashboard |

---

## Architecture

```
┌───────────────────────────────────────────────────────────────────────────┐
│  Pipeline / CampaignQueue                                                 │
│    └─ publish_event(stage, message, detail)  ──►  event bus               │
└──────────────────────────────┬────────────────────────────────────────────┘
                               │  (process-local, replayed to late clients)
                               ▼
┌───────────────────────────────────────────────────────────────────────────┐
│  narration.py  (TODO69) — the sentences, written once                      │
│    ├─ event → sentence      "Measured gradient/feedforward, seed 3: 0.412" │
│    ├─ state  → the "now"    "Run demo is EXPLORATORY: 4 cells measured…"  │
│    └─ script → the whole story as text                                    │
└──────────────┬────────────────────────────────────┬───────────────────────┘
               │ WebSocket frame "narration"        │ GET /api/narration
               ▼                                    ▼
┌───────────────────────────────────────────────────────────────────────────┐
│  Browser: caption.ts — the closed-caption overlay                          │
│    two lines, large, high contrast, bottom centre; the latest sentence,   │
│    then the state summary when nothing is happening                        │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│  Browser: stage/state.ts — the run's evidence, once                        │
│    the run · the axes · the declared space · the records per cell          │
│    the gate's rules · the chance level · the run's account · its stages    │
│    its flow · its attribution                                               │
│         │                                                                 │
│         ├──► the space (the discovery map)   ──► the 3D scene              │
│         ├──► the terrain                      ──► the 3D scene              │
│         ├──► the frontier                     ──► the 3D scene              │
│         ├──► the evidence matrix              ──► the 2D canvas            │
│         ├──► the convergence                  ──► the 2D canvas            │
│         ├──► the small multiples              ──► the 2D canvas            │
│         ├──► the spread                       ──► the 2D canvas            │
│         ├──► the claim's cost                 ──► the 2D canvas            │
│         ├──► the uncertainty                  ──► the 2D canvas            │
│         ├──► the timeline                     ──► the 2D canvas            │
│         ├──► the ledger                       ──► the 2D canvas            │
│         ├──► the contrast                     ──► the 2D canvas            │
│         ├──► the flow                         ──► the 2D canvas            │
│         ├──► the effect                       ──► the 2D canvas            │
│         ├──► the trajectory                   ──► the 2D canvas            │
│         ├──► the spectrum                     ──► the 2D canvas            │
│         ├──► the basin                        ──► the 2D canvas            │
│         └──► the landscape                    ──► the 2D canvas            │
│    stage/switcher.ts — V cycles · 1–9 and T L D F E pick · the selector     │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│  ledger.py  (TODO69) — the run's account of itself, on the server          │
│    the ledger  — every arm, its evidence, the gate's standing on it        │
│    the contrast — the arms against one another, and the test               │
│    GET /api/runs/{id}/account     GET /api/events?run_id=                  │
├───────────────────────────────────────────────────────────────────────────┤
│  arms.py  (TODO69) — what an arm measured, read once for both              │
│    the arms of every axis · their means, their spread, their standing      │
├───────────────────────────────────────────────────────────────────────────┤
│  flow.py  (TODO69) — the run as a process                                  │
│    the stages · the count each one handled · what the gate refused         │
│    GET /api/runs/{id}/flow                                                 │
├───────────────────────────────────────────────────────────────────────────┤
│  attribution.py  (TODO69) — what the run can attribute                     │
│    the axes · the spread of their arms · what the design cannot say       │
│    GET /api/runs/{id}/attribution                                          │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## Phases

Phases 0–5 are done: the server speaks, the browser shows it, the tour and
the recording show both, and the canvas can show more than one thing. The
surfaces outside the canvas are in the tour too. What is left of the stage is
the catalogue in Phase 5 — the multi-run space, and the family that needs a
cell with a state.

### Phase 0: The narration (server) — the server half is done

**Goal**: one place that says what the system is doing, in sentences.

1. `computronium/experiment/execution/dashboard/narration.py`: ✅
   - `Line` — one narrated moment: when, what, how loud.
   - `Narration` — the account: `event(event)` for a sentence, `state(...)`
     for the summary, `lines()`, `current()`, `script()`.
   - `event_sentence(event)` — a stage event becomes a sentence about a stage;
     a measurement event becomes a sentence about a cell and its number.
   - `state_sentences(...)` — the summary: the run, its mode, the cells
     measured, the best cell, the seeds a claim still needs, the queue, and
     where the picture came from.
2. `web.py`: ✅
   - the dashboard narrates every event it forwards, and refreshes the state
     sentence on its poll;
   - `GET /api/narration` — the current sentence, the recent lines, and the
     whole story as one text block (`?run_id=` for a specific run);
   - a `narration` WebSocket frame, so the caption updates as things happen.
   - every `pipeline_event` frame now carries its `sentence`, so the browser
     never writes one.
3. The producer names the cell and the seed it measured (`pipeline.py` → the
   event's `detail`), so the sentence needs no parsing of the message. ✅

**What the sentences say** (measured, against the probe's store):

```
The demo run on digits is exploratory and has measured every cell it declared.
The gradient arm is ahead of the others and beats chance. The claim cannot be
made yet: too few seeds. The queue is idle.

Measured the gradient arm.
Training cells.
Recording evidence.
A campaign was queued.
The pipeline could not compose systems.
```

**The rule the wording obeys**: the narration speaks in words, not in
figures. It does not read out an accuracy, a seed count or a threshold —
those are on the panels, and a voice-over that recites them is worse than
useless. What it says is the *shape* of what is happening: the run is
exploratory, one arm is ahead of the others, the claim cannot be made yet,
the queue is idle. Every claim it makes can be checked against the picture.

**Acceptance**: ✅ every sentence names a run, a cell, a number or a rule — no
sentence a reader cannot check against the panels. ✅ `GET /api/narration`
returns text an agent can read aloud without the browser. ✅ the sentences
read no figures — the panels carry the numbers, the narration carries the
meaning.
**Still to do here**: the browser half — the caption overlay that renders
these sentences (Phase 1). The server speaks; nothing draws it yet.

### Phase 1: The caption (browser) ✅

**Goal**: the screen says what it is doing, without being asked.

1. `dashboard/src/caption.ts` — a closed-caption overlay:
   - the latest sentence, in two lines, 22px, high contrast, bottom centre;
   - the state summary when nothing is happening;
   - a sentence stays up for a few seconds, then the summary returns;
   - `C` toggles it, like the other panels.
2. The caption is *rendered*, not composed: the words come from the server.

**Acceptance**: with the browser showing only the dashboard, a reader can say
what is running, what was measured, and what the number means.

**What the caption does when there is no run yet**: the state has nothing to
say, so the caption keeps the *last event's* sentence ("Training cells.")
rather than falling back to a placeholder. The events are the story while
the run is still running; the state is the story once it has finished.

### Phase 2: The tour (screenshots) ✅

**Goal**: more than one picture of the system.

`scripts/capture_dashboard_tour.py` — one store, one dashboard, one browser,
twenty-one views:

| Shot | What it shows |
|------|---------------|
| `dashboard-hero.png` | the overview (the existing shot, regenerated) |
| `dashboard-map.png` | the discovery map alone: the fog of war, panels hidden — the **space** view |
| `dashboard-terrain.png`, `-frontier.png`, `-matrix.png`, `-convergence.png` | the stage's other views, one shot each |
| `dashboard-multiples.png`, `-spread.png`, `-claim-cost.png`, `-uncertainty.png` | the stage's flat views of the evidence, one shot each |
| `dashboard-cell.png` | the leading cell's drawer: metrics, curve, verdict, seeds to claim |
| `dashboard-void.png` | a void cell, in a slice of the space cut a different way, and the rule that refuses it |
| `dashboard-pareto.png`, `-ablation.png`, `-variability.png` | the three charts, each on its own, over the map |
| `dashboard-caption.png` | the caption over the map — the narrated picture |
| `narration-script.png` | the dashboard's account of itself, as text |
| `report-run.png` | the run's report, in the browser |
| `console-dashboard.png` | the console dashboard: the same picture, in a terminal |
| `report-text.png` | the run's report, in a terminal |
| `figure-seed-violins.png` | the seed violins: a figure, with its caption and its provenance |

**Acceptance**: ✅ every shot is 1920×1080, has real data in it, and lands in
`docs/readme/assets/` (committed) and `docs/screenshots/` (mirrored). ✅ the
shots are of *different things*: the 3D map, the panels, the charts, a
browser report, two terminal views and a figure. ✅ a shot that cannot be
taken is reported, not silently skipped. ✅ **the stage's nine views are
measured against one another**: the browser decodes each pair and reports the
share of the pixels that differ, and a pair below 2 % fails the tour.

**The tour's rule**: it waits for the dashboard's *state* — a measured cell,
a drawn chart, a caption with words in it, a view that has drawn — and never
for a fixed pause.

### Phase 3: The recording ✅

**Goal**: a short video of a live session, with the captions on screen.

`scripts/capture_dashboard_video.py` — the camera photographs the dashboard
while the demo campaign runs; the caption narrates it. The file is a
`.webm`, it is **not committed** (it is large), and it is written to
`docs/recordings/`, which `*.webm` ignores.

**Acceptance**: ✅ a `.webm` exists after a run, the captions are legible in
it, and `git status` stays clean.

**The recorder is not Playwright's own**: it needs a particular `ffmpeg`
build, and a machine without that build records *nothing* without saying so.
The script photographs the page and encodes the frames with the system
`ffmpeg`, at the rate the session actually happened.

**The film ends when the run's evidence lands, not when a timer says so.**
A fixed length is a guess about the machine's speed: on a slow one the film
stops before the run does, and the last thing the reader sees is an empty
space. The camera watches the dashboard instead, and holds on the finished
run for a few seconds before it stops.

### Phase 4: Polish, test, document ✅

- `tests/unit/experiment/test_dashboard_narration.py` — the sentences, the
  summary, the endpoint.
- `tests/unit/experiment/test_dashboard_events.py` — every event frame
  carries its sentence, and the frame and the account say the same thing.
- `tests/unit/experiment/test_console_dashboard.py` — the console
  dashboard's frame as text.
- `tests/unit/experiment/test_dashboard_gate.py` — the run carries the
  gate's own thresholds, and the payload carries none of its own.
- `docs/DASHBOARD.md` — the caption, the narration endpoint, the tour.
- `docs/readme/dashboard.md` — a "the dashboard, in pictures" section, in
  the README.

---

## Phase 5: The main view area — one canvas, many views ✅ done

**The problem** (now solved): the main view area — the canvas, the big
picture — showed *one* picture. The space, as a field of cubes: gaps as
wireframe boxes, measured cells as glowing pillars, refusals as red crosses.
Everything else the system knows — the frontier, the curves, the spread, the
attribution, the rules that refuse — was either a small panel over the scene
or nothing at all. A reader who wanted to *see* the evidence had to read a
table.

**The shape of the change**: the canvas is a *stage*, and a view is what
stands on it. The discovery map is one view; it is now one of nine. The
scene is shared (`components/context.ts` gives every component the same
scene, camera and renderer), and the map already knew how to clear what it
built (`clearGrid`) — so a view is a component with the same shape as the
map, and a switcher that stands where the plotter's tabs stand.

A view needs four things, and the map has all four:

| Part | What it does | Where it lives today |
|------|--------------|----------------------|
| `build` | put its objects in the shared scene | `createCell`, `createVoidMarkers` |
| `clear` | take them away again | `clearGrid` |
| `update` | re-read the run's records | `applyAggregates` |
| `frame` | put the camera where this picture wants to be seen | `frameGrid` |

**What was built** (`computronium/experiment/execution/dashboard/src/stage/`):

| Module | What it holds |
|--------|---------------|
| `state.ts` | the state every view shares: the run, the axes, the declared space, the records folded per cell, the chance level, the gate's rules — and the space fetch, so it is asked for once |
| `views.ts` | the `StageView` shape: `enter`, `exit`, `refresh`, `ready` |
| `switcher.ts` | the choice: `V` cycles, the number keys pick, the **View** selector in the legend, and the legend's title and marks follow the view |
| `terrain.ts` | the space as a heightfield |
| `frontier.ts` | the records as points in accuracy, speed and parameters, with the front and the chance floor |
| `matrix.ts` | the space flat, every column a number |
| `convergence.ts` | accuracy against epoch, one curve per arm |
| `small-multiples.ts` | one panel per cell, every seed's own curve |
| `spread.ts` | one violin per arm, across its seeds |
| `claim-cost.ts` | the seeds each cell measured against the seeds a claim needs |
| `uncertainty.ts` | each cell's mean and the gate's margin, against the chance level |
| `canvas2d.ts`, `plot2d.ts` | the flat stage: one canvas over the 3D scene, and the frame, ticks and labels the flat views share (a numeric frame, a frame of categories, a frame of rows) |
| `framing.ts`, `sprites.ts`, `scene.ts`, `ramp.ts` | the camera, the labels, the disposal, and the colour ramp — shared by the stage's views |

**The views, in the order they were built.** Each is a *different kind
of picture* of the same run; each is drawn from data the dashboard already
has, or can already ask for. The right-hand column is the test a view has
to pass: **what can a reader say after looking at it?**

#### The space, seen other ways (3D)

| View | What the main area shows | The data it needs | A reader would say |
|------|---------------------------|-------------------|--------------------|
| **The space** (the map) ✅ | the declared space: gaps as wireframe cubes, measured cells as glowing pillars, refusals as red crosses; the pillar's height carries the value | the space payload, the records | "the run measured four of the cells it declared, and here they are" |
| **The terrain** ✅ | the same space as a *heightfield*: accuracy as height over the two free axes, the gaps flat ground, the refusals craters in it | the space payload, the records | "the arms that were measured stand up, and the region the system refuses is a hole in the ground" |
| **The frontier** ✅ | every measured record as a point in (accuracy, speed, parameters); the front the run computed drawn through them; the chance plane as a floor | the records, the `pareto` flags, `chance` | "nothing beat these cells on all three counts at once" |
| **The layers** ✅ | the space cut into sheets: one sheet per value of the third axis, the cells the run measured standing up off their own sheet, the rest of the space the ground they were not in | the space payload, the records | "the run filled one sheet of eight, and four cells of it" |
| **The multi-run space** ⬜ | several runs' evidence in one space, coloured by run | the store's runs, the space per run | "the second run went where the first one did not" |
| **The trained cell** ⬜ | the same four pictures, of a cell whose weights were trained first | the trainer, on the server | "a trained cell settles where an untrained one does not" |

#### The evidence, seen other ways (2D)

| View | What the main area shows | The data it needs | A reader would say |
|------|---------------------------|-------------------|--------------------|
| **The evidence matrix** ✅ | one axis against another, each cell a number, the refusals in the void colour | the space payload, the records | "the credit arm mattered, and here is where" |
| **The convergence** ✅ | accuracy against epoch, one curve per arm, the chance line under them | the per-cell curves (the map's aggregates already carry them) | "the arms separate in the second epoch, not the first" |
| **The small multiples** ✅ | one panel per cell — every seed's curve, side by side | the per-cell curves | "this cell is steady and that one is a toss of the coin" |
| **The spread** ✅ | one violin per arm across the seeds, and the seeds a claim still needs under it | the records' seeds | "this arm is wide, and that is why the claim is not made" |
| **The claim's cost** ✅ | seeds measured against seeds needed, per cell, with the gap | the records' seeds, `required_seeds` | "the claim is 232 seeds short over four cells" |
| **The pairwise contrast** ✅ | arm against arm: which beat which, by how much, and whether the test was even run | the records, the report's contrast design | "pepita beat random_projections, and here is the margin" |
| **The attribution** ✅ | the objective attributed to the axis values — which axis moved it, and by how much — and the axes the run held fixed | the arms of every axis, read from the records (`arms.py`), and the report's own claim machinery | "one axis varied and five were held fixed, so this run can speak about credit alone" |
| **The uncertainty** ✅ | each cell's interval against the threshold a claim would need — the gate's own margin, against the chance level | the records' spread, the gate's thresholds (`gate`) | "which cells are separable from chance, and which are not yet" |

#### The run, as a process (not as evidence)

| View | What the main area shows | The data it needs | A reader would say |
|------|---------------------------|-------------------|-------------------|
| **The timeline** ✅ | the run's stages, one lane each, and the time each held it; the longest silence named | the pipeline's events (`GET /api/events`), with their timestamps | "the run trained for 34 seconds and measured nothing until the end" |
| **The pipeline flow** ✅ | the cells flowing through the stages, with the gate's refusals at the gate | the events' own counts, and the space's rules (`GET /api/runs/{id}/flow`) | "four cells went through the pipeline, the gate refused none, and twenty records were written" |
| **The ledger** ✅ | every arm the run measured, its evidence, and the gate's standing on it — PASSED, INSUFFICIENT, REJECTED; the report's limitations and its test beneath | the report's claims and limitations, the records' gate verdicts (`GET /api/runs/{id}/account`) | "nothing here is a claim yet, and the report says why" |
| **The contrast** ✅ | the arms of the axis that spread widest on the run's objective, against one another, over the cells they share, with the paired test's verdict | the records, the paired test (`GET /api/runs/{id}/account`) | "pepita beat random_projections by 0.44, on one shared cell" |

#### The system, not the bookkeeping

These need the *trained system*, not just the records, so they are the most
work and the most worth having.

| View | What the main area shows | The data it needs | A reader would say |
|------|---------------------------|-------------------|-------------------|
| **The settling trajectory** ✅ | a cell's state, drawn through the state space from where it started to where it stopped, coloured by time | the cell's own relaxation, stepped on the server (`GET /api/runs/{id}/dynamics`) | "this cell does not settle where you think it does" |
| **The basin** ✅ | every initial state that settles to the same fixed point — the set of states the system is really in | the same measurement: the share that comes back at each radius, and the strays' paths | "the basin is a sliver, and the run is inside it" |
| **The energy landscape** ✅ | the cell's own energy over the ground its trajectory crossed, with the trajectory over it | the same measurement: the cell's own `compute_energy` over a slice of its own state space | "the state it settled into is a local minimum, and this one is not" |
| **The spectrum** ✅ | the Lyapunov exponents — is the system stable, and in which directions | the same measurement: the stability package's spectrum of the cell's own map | "this dynamics is stable, that one is not" |

**The last family is the one that changes what the dashboard is.** Every
view above is about the *bookkeeping* of a run — what was measured, what was
refused, what it cost, how long it took. The last family is about the
*system* being measured: where its states go, whether they settle, how much
energy they carry. A dashboard that can show that is a different instrument,
and it is the one the 3D canvas was built for in the first place.

**The switcher** ✅: the view is a choice a person makes, so it is a key
(`V` cycles; the number keys, like the plotter's tabs, pick one; a view that
does not fit in the numbers has a letter of its own) *and* a selector in the
legend, so the choice is visible rather than remembered. The plotter's own
tabs moved to `P`, `A` and `S` — the letters that name them — so the numbers
could belong to the stage. The tour then captures one shot per view, and the
tour's variety stops being a matter of which panel is in front of the map.

### What the batch changed in the dashboard itself

The map no longer owns the run's evidence. `stage/state.ts` holds it — the
run the dashboard shows, the axes the reader picked, the space the backend
declares, the records folded per cell — and the map reads it like every other
view. That is what makes the views *one* picture of the run rather than five
pictures that may disagree. The map's own logic (the grid, the hover, the
drawer, the framing) is unchanged; what changed is where the numbers come
from.

### Where to start next

The four flat views of the evidence are built, and the run now has a timeline,
a ledger, a contrast, a flow and an effect. The layers are built too, and so
are the surfaces outside the canvas. What is left of the catalogue:

1. **The dynamics views** — the ones that need a cell re-instantiated, and
   the ones worth the most: the settling trajectory, the basin, the energy
   landscape, the spectrum. The machinery is in `computronium.stability` and
   in `computronium/experiment/analysis/energy_landscape.py`; what is
   missing is a server that re-composes a cell from a record and a view
   that draws the answer. **The probe says what has to be true first** — the
   demo's cells have no state to settle, and the transition the stability
   analysis builds is the identity for them: see the batch at the end of
   this plan.
2. **The multi-run space** — several runs' evidence in one space, coloured
   by run. It needs two runs in one store.
3. **The remaining surfaces** — the defect registry, the comparison between
   two runs, and the panels on their own.

**Acceptance**: ✅ the canvas can show the space, the terrain, the frontier,
the matrix, the convergence, the small multiples, the spread, the claim's
cost, the uncertainty, the timeline, the ledger, the contrast, the flow, the
effect and the layers, and the tour has a shot of each. ✅ the shots are
*visibly different pictures* — measured, not asserted, and the tour fails
below 2 %. ✅ a reader can answer "what did the run find?" from any one of
them. ✅ a view that is not active leaves nothing of itself on the stage. ✅
the view is a choice — a key, a number or a letter, and a selector that names
it where it is chosen. ✅ the tour can photograph a *figure* — a PNG with its
caption and its provenance under it — and a *plot* the report drew. ✅ the
tour photographs the surfaces outside the canvas: the gallery, the report's
charts, and the `comp` reports.


---

## The surfaces outside the canvas — the same argument, applied

The main view area is the biggest miss, but the system has more pictures
than the dashboard shows, and each is a *different kind* of picture of the
same evidence. Every row is a real surface in this repository, with the
command or the module that produces it; none of it is speculative. **Seven of
the twelve are now in the tour** — the ones marked ✅ were photographed by
`scripts/capture_dashboard_tour.py` and are in the README.

| Surface | What it would show | Where it comes from | What it would add | In the tour |
|---------|-------------------|--------------------|-------------------|-------------|
| **The gallery** ✅ | 21 figures — one per demonstrated capability: swaps, frontiers, coverage, ladders, failure manifestos | `comp gallery` (records in `docs/figures/run_records`, the PNGs and the manifest in `docs/figures`); the panel vocabulary is bars / graph / heatmap / lines / scatter / tree (`computronium/visualization/_demo_api.py`) | the *scientific* family: static figures with a palette, chance lines and value labels by construction | four of them: the credit swap, the fast settle, the coverage, the failure manifesto |
| **The report's own figures** ✅ | 3 Pareto fronts (acc×walltime, acc×params, acc×flops), 4 coverage heatmaps (geometry×dynamics, geometry×credit, dynamics×credit, credit×update), failure clustering, convergence, scaling laws, seed stability | `computronium/experiment/reporters/html.py` — they are in the HTML report already, but only as one page | the report's plots, one at a time and at full size | the Pareto front and the seed stability, each on a page of its own |
| **The energy landscape** | the system's energy as a surface, and where the states sit in it | `computronium/experiment/analysis/energy_landscape.py` (`plot_energy_landscape`) | a picture of *why* a cell settles where it does | ⬜ with the dynamics family |
| **The seed violins** ✅ | per-arm distribution across seeds, not a mean | `computronium/experiment/analysis/seed_variability.py` (`plot_violin_plots`) | the spread the narration calls "the claim cannot be made yet" | ✅ |
| **The coverage report** ✅ | which primitives of each axis the run touched, and which it did not | `comp coverage report` | the run's reach, as a table | ✅ with the objectives the system has *not* measured |
| **The catalogue** ✅ | the store queried by axis — every run and record, filtered | `comp catalog` | the evidence, browsable | ✅ |
| **The defect registry** | the constraints, clustered, and which are revoked | `comp defect` | the rules that refuse cells, in the system's own ledger | ⬜ the registry is empty for a run with no defects: a picture of nothing |
| **The method cards** ✅ | a card per primitive: what it is, what it costs, what it was measured at | `comp method-card` | the ontology, pictured | ✅ |
| **The comparison** | two runs, differenced, with effect sizes | `comp diff` | what changed between two claims | ⬜ needs two runs in the store |
| **The power analysis** ✅ | the seeds a design needs, before it runs | `comp power-analysis` | the design, not the result | ✅ |
| **The panels alone** | the live rail by itself, the HUD by itself, the legend and the axis picker by themselves | the dashboard's own DOM | each panel, as its own picture | ⬜ |
| **The map in more slices** | the same run's space, cut three ways, side by side | the legend's axis picker (`#legend-axis-picker`) | the space is not one picture: it is six axes | ⬜ one slice is cut today (the void view) |

**How to add them**: the tour has a `Frame` with four kinds — `browser` (a
URL), `terminal` (text in a window), `figure` (a PNG rendered in a page, with
its caption and its provenance under it) and **`plot`** (a chart the report
drew, taken out of the report and given a window of its own). The terminal
kind covers every `comp …` command that prints a report, so the coverage
report, the catalogue, the method cards and the power analysis are one
`Frame` each; the figure kind photographs the gallery's own PNGs; the plot
kind photographs the report's charts.

---

## Risks

| Risk | Mitigation |
|------|------------|
| The narration becomes a second source of truth | it is composed on the server from the same payloads the panels render; the browser never writes a sentence |
| The caption covers the scene | it is two lines at the bottom, and the camera framing already leaves the panels' space free |
| The tour is flaky (software rasterizer, slow page) | the capture waits for the page's *state*, never for a fixed pause; a failed view is reported, not silently skipped |
| The video is large | it is written to `docs/recordings/`, which `*.webm` ignores, so it is findable and uncommitted |
| The film ends before the run does | the camera watches the dashboard and holds on the finished run, instead of trusting a timer |
| The narration is prose nobody reads | the same text is available over HTTP, so an agent can read it without a browser |
| A view leaves its objects on the stage | the scene is shared, so a view must clear what it built — the map already knows how (`clearGrid`), and a view that does not clear is a bug the next view shows |
| The canvas becomes a gallery of pictures | a view is a *choice* with a switcher, not a slideshow: the view is named where it is chosen, and the tour's shots are of views a reader would choose |
| A view needs the trained system, so it cannot be built from the store | the dynamics views are last, and they are the ones that need a cell to be re-instantiated; the evidence views need nothing the dashboard does not already have |
| A surface with nothing to say is a picture of nothing | the defect registry holds no constraints for a run with no defects, and the report's coverage heatmaps are one cell wide for a run that varied one axis; neither is in the tour, and a surface is photographed only when it says something |
| The next session builds one view and stops | the batch is four views *and* a tour shot of each: a switcher with one view on it is a demo, not a dashboard |
| A cell with no state has no dynamics to show | the transition says so, and the server looks for the nearest cell of the space that has one — and the payload names every axis it swapped |
| A cached measurement is an answer to yesterday's question | the cache holds a measurement of a *cell*; a run that has measured nothing yet is asked again |
| A spectrum that samples eight directions out of hundreds says less than it seems | the verdict needs the basin as well: a state whose neighbourhood never comes back has not settled, whatever the sampled directions do |

---

## Definition of Done

- [x] Every event the dashboard forwards becomes a sentence that names a run, a cell, a number or a rule
- [x] `GET /api/narration` returns the current sentence, the recent lines and the whole story
- [x] The dashboard shows the narration as a closed-caption overlay
- [x] The tour captures the overview, the map, a measured cell, a void cell, the three charts, the caption, the narration, the report and the terminal views
- [x] A short recording of a live session exists, with the captions on screen, and is not committed
- [x] `docs/DASHBOARD.md` and the README show the tour
- [x] The main view area can show more than one picture of the run: the space, the terrain, the frontier, the matrix, the convergence, the small multiples, the spread, the claim's cost, the uncertainty, the timeline, the ledger, the contrast, the flow, the effect and the layers
- [x] The view is a choice — a key and a selector — and the inactive view leaves nothing of itself on the stage
- [x] The tour has a shot of every main view, and the shots are visibly different pictures of one another — *measured*, not asserted
- [x] The tour can photograph a *figure* (a PNG with its caption and provenance), not only a page and a terminal
- [x] The tour can photograph a *plot* the report drew, on a page of its own
- [x] The tour photographs the surfaces outside the canvas: the gallery's figures, the report's plots, the coverage report, the objectives the system has not measured, the catalogue, the method cards and the power analysis
- [x] The run's account of itself is on the server: `GET /api/runs/{id}/account` and `GET /api/events`
- [x] The run's process is on the server: `GET /api/runs/{id}/flow`
- [x] The run's attribution is on the server: `GET /api/runs/{id}/attribution`
- [x] The transition the stability analysis measures is the system's own relaxation, and not the identity
- [x] The cell's own dynamics are on the server: `GET /api/runs/{id}/dynamics` and `GET /api/cells/dynamics`
- [x] The main view area can show the cell's own dynamics: the trajectory, the spectrum, the basin and the landscape

---

## Where the work stands

| Piece | State |
|-------|-------|
| `narration.py` — the sentences, the account | ✅ done |
| `web.py` — the frames, the endpoint, the state refresh | ✅ done |
| `pipeline.py` — the producer names the cell and the seed | ✅ done |
| `caption.ts` — the browser renders the sentences | ✅ done |
| the tour — forty-two pictures in one browser session | ✅ done (nineteen views on the stage, the gallery, the report's plots, the `comp` reports) |
| the recording — a `.webm` of a live session, uncommitted | ✅ done |
| the docs — the caption, the endpoint, the tour, the stage | ✅ done |
| the dashboard shows a run before it has measured | ✅ done (the space is on screen from the first second) |
| the main view area — the stage, the views, the switcher | ✅ done: nineteen views, a key, a selector, a shot of each |
| the flat views — the matrix, the convergence, the small multiples, the spread, the claim's cost, the uncertainty | ✅ done (the canvas, the frame and the ticks are shared) |
| the dynamics views — the trajectory, the spectrum, the basin, the landscape | ✅ done (one payload, four readings of one measurement) |
| the gate's rules travel with the run | ✅ done (`gate` in the metrics payload; the browser invents no margin) |
| the figures — the seed violins | ✅ done (the tour's third frame kind: a PNG, its caption, its provenance) |
| the surfaces outside the canvas — the gallery, the report's plots, the `comp` reports | ✅ done (eleven more frames: four gallery figures, two report plots, five commands) |
| `ledger.py` — the run's account of itself | ✅ done (the ledger, the contrast, the rules they are measured by) |
| the timeline — the run as a process | ✅ done (the events, one lane per stage, the silence named) |
| `arms.py` — the statistics of an arm | ✅ done (read once for the ledger and the effect) |
| `flow.py` — the run's cells through the stages | ✅ done (the events' counts, the gate's refusals, the shape in a sentence) |
| `attribution.py` — what the run can attribute | ✅ done (the axes, the spread, and the design's limits in words) |
| the other views — the dynamics | ✅ done (the trajectory, the spectrum, the basin, the landscape: the cell's own relaxation, measured on the server) |
| the trained cell | ⬜ the dynamics views measure an untrained cell, and say so; a trained one is the next thing to try |
| the multi-run space | ⬜ needs two runs in one store |
| the mirror's publish can fail and lag | ⬜ a known flake, diagnosed above |
| the property suite fails 23 tests at HEAD | ⬜ pre-existing and unrelated: the gallery's `env_sha256` (19), `PROOF.md`'s banned phrases, the priors registry — verified by stashing this batch and re-running |
| the README was stale against `docs/readme/` | ✅ fixed here (the build lock was failing at the commit before) |

The server speaks, the browser shows it, the pictures show both, and the
canvas can show more than one thing. What is left of the stage is the
dynamics family, and the probe below says what has to be true before it can
be drawn: the demo's own cells have no state to settle.

---

## What the work taught (for whoever comes next)

**The pictures had to be of *different things*, not of the same scene.** The
first tour changed the panels in front of the map and the map stayed the
same picture in every frame. A tour of one scene is one picture repeated.
The tour now spans the 3D map, the panels, the charts, a browser report and
two terminal views — and the void view cuts the space a *different* way, so
even the 3D pictures differ from one another.

**A "live" shot of the map is not available, and pretending otherwise would
be a lie.** The pipeline measures in `s7` and records in `s8`, so the records
land in a burst at the end: there is no moment when the map is half-lit. The
tour dropped the live shot rather than re-shoot the finished map under
another name. The *recording* is where the live session is: the caption
narrates the events while the run happens.

**The map needed the run's records before it drew anything — and that was
the wrong rule.** The dashboard only learned of a run through its metrics,
and the metrics need records, so the first half of every filmed session was
an empty stage. But a run's *declaration* is in the store from the moment it
starts: the declared space, the held axes, the refusals. The dashboard now
sends the metrics of a run that has started but not yet measured — with its
numbers at zero, because zero is the honest answer — and the map draws the
fog of war from the first second. The evidence then lights it up. A
dashboard that shows nothing until the work is done is a dashboard that has
forgotten the run it is watching.

**The store's mirror outlives the store.** A capture that deletes the store
but not its mirror reads the *last* run's records as if they were this run's
— and the tour then asks the server about a run that is not in the store.
`dashboard_capture.clear_store` removes both.

**The mirror's publish can fail, and it fails silently** (found while
running the unit shard, and it is *not* new — it reproduces at the commit
before this work). DuckDB's `COPY FROM DATABASE` copies the tables in an
order that can violate the foreign key from `records` to `runs`:

```
Mirror … could not be published: Constraint Error: Violates foreign key
constraint because key "run_id: …" does not exist in the referenced table
```

The mirror then holds one append fewer than the store, and the reader sees a
picture that is a moment behind — which is exactly what the mirror is for.
`tests/unit/experiment/test_dashboard_mirror.py` fails about one run in
three. The fix belongs in `publish_mirror` (an `EXPORT`/`IMPORT` pair
imports in dependency order; a `CHECKPOINT` before the copy is worth
trying), and it matters more now: the live dashboard reads the mirror
whenever the writer holds the store, so a lagging mirror is a lagging
picture.

**Playwright's own video recorder needs a particular `ffmpeg`.** The
environment's bundled build is older than the one the Playwright version
expects: it refuses an option, records nothing, and says nothing. The
recorder now photographs the page and encodes the frames with the system
`ffmpeg`, at the rate the session actually happened.

**The console dashboard can hand out a frame of itself.** `ConsoleDashboard`
read the store inside its update loop, so a reader without a terminal could
not have the picture. `refresh()`, `read_store()` and `snapshot()` make one
frame available as text — the same words, in the same order, for a document
or an agent.

**The main view area was the biggest miss, and it was hiding in plain sight.**
The tour was asked for "more pictures of the system", and the answer given
was pictures of the *panels over* the scene. The scene itself — the thing
that fills the content area, the reason there is a canvas at all — was one
picture in every frame: a field of coloured cubes. The panels were never
the point; they are the furniture. What the canvas could show — the terrain,
the frontier, the convergence, the settling trajectory — is the potential,
and it was all sitting one design decision away.

**The scene is already a stage, so the change is smaller than it looks.**
`components/context.ts` hands every component the same scene, camera and
renderer, and the discovery map already does the four things a view must do:
build its objects, clear them, re-read the records, and frame the camera.
A view is a component with that shape; a switcher is what the plotter's
tabs already are. The canvas was never a picture — it was a stage waiting
for a second act.

**The stage needed one owner for the run's evidence, or the views would
have become five pictures that may disagree.** The map used to hold the
space, the axes and the records itself; the new views need the same three
things, and the cheapest honest answer was to lift them into one place
(`src/stage/state.ts`) and let the map read them like everyone else. The
map's own logic did not change — where the numbers *come from* did.

**A heightfield over a mostly-refused space is a picture of nothing, unless
the refusals are drawn rather than removed.** The first terrain skipped the
faces the refusals touched, and in this run's slice 25 of the 64 columns are
refused — the ground was a strip and a scrap, because the holes ate it.
The terrain now digs the refusals as *craters*: the ground is continuous,
the refused columns sink, and the picture reads as "the system refuses this
whole region, and the arms that were measured stand up beside it".

**A surface can be drawn and still be invisible.** The terrain's first
version was wound the wrong way round, so its normals pointed into the
ground and the light never reached it: the picture was a dark quad that
looked like the floor grid. The winding of a heightfield is not a detail.

**The number keys had to be taken from the plotter.** The plan wanted the
number keys for the views, "like the plotter's tabs" — and the plotter had
them. The charts moved to the letters that name them (`P`, `A`, `S` — the
variability chart is the *spread*), and the numbers now belong to the stage,
which is where the reader's attention is.

**"Visibly different" is a measurement, not a promise.** The tour now
decodes each pair of the stage's shots in the browser and reports the share
of the pixels that differ; below 2 % the tour fails. The measured spread is
2.5 % to 28.1 % — the smallest pair is the frontier and the uncertainty,
which are both dark pictures with few marks, and they are still above the
floor.

**A flat view does not need three.js, and it does not need uplot either.**
The matrix and the convergence are drawn on one 2D canvas over the stage,
with the frame, the ticks and the labels shared. What they share with the
3D views — the switcher, the data, the tour shot — is what makes them part
of the same instrument rather than three more panels.

---

## This batch (the second flat views, and the figure)

**What was built.** Four more views of the evidence, all flat, all on the
shared 2D canvas, and a tour shot of each:

| View | The file | The picture |
|------|----------|-------------|
| The small multiples | `src/stage/small-multiples.ts` | one panel per cell, every seed's own curve, one accuracy scale for all of them |
| The spread | `src/stage/spread.ts` | one violin per arm (a Gaussian kernel, Silverman's bandwidth), the seeds as the points it is made of, the mean as a line, and the seeds a claim still needs written under it |
| The claim's cost | `src/stage/claim-cost.ts` | per cell, the seeds measured against the seeds a claim needs, with the gap between them |
| The uncertainty | `src/stage/uncertainty.ts` | per cell, the mean and the margin the gate asks for, against the chance level, and the threshold each cell has to clear |

And the tour's third frame kind: **`figure`** — a PNG rendered in a page
with its caption and its provenance under it (`dashboard_capture.shoot_figure`).
The seed violins of the run are the first figure photographed
(`figure-seed-violins.png`): the same spread, drawn by the analysis that
measures it.

**The rules came from the server, not from the browser.** The uncertainty view
needs a margin, and the claim's cost needs a seed count; both belong to the
statistical gate. The metrics payload now carries them — `gate` is
`GateThresholds().to_dict()` — and the browser draws what it is given. A
view that measured the run against a margin of its own would be measuring a
different run from the one the report describes.

**What the work taught.**

**A violin's shape reaches past its data, and the frame has to hold it.** The
first spread drew the kernel's tails above the plot's top edge, so the widest
arm poked out of its own frame. The frame is now sized by what the violin
draws — the extent of the kernel, not the extent of the values — and the
drawing is clipped to the frame as well.

**A row label is as long as it is, and the space beside the plot is not.**
`random_projections` did not fit in the frame's fixed left margin, and the
legend cut off what was left of it. The row frame now measures its labels
and gives them the room they need.

**The tour's picture check caught what the eye did not.** The spread and the
claim's cost were drawn to look alike from the outside, and the measurement
of the pairs (2.5 % to 28.1 %) is what says which pictures are too close. It
is a check on the *view*, not only on the tour.

**The README was stale, and the lock said so.** `docs/readme/dashboard.md`
had been edited without rebuilding `README.md`, and
`tests/property/test_readme_build_lock.py` had been failing at the commit
before this one. A doc lock that nobody runs is a lock that does not exist;
the fix is in this commit, and the lesson is in the plan: **rebuild the
README in the same commit that edits the snippet.**

---

## This batch (the run as a process, and the run's account)

**What was built.** Three more views of the stage, all flat, all drawn from
the run's own account, and a tour shot of each:

| View | The file | The picture |
|------|----------|-------------|
| The timeline | `src/stage/timeline.ts` | one lane per stage, in the order the run reached it, with the events it left on the clock; the longest silence is named |
| The ledger | `src/stage/ledger.ts` | every arm the run measured, its evidence, and the gate's standing on it; what was held fixed; the report's limitations; the report's own test |
| The contrast | `src/stage/contrast.ts` | the arms of the axis that spread widest on the run's objective, against one another, over the cells they share, with the paired test's verdict |

And the server half, in `computronium/experiment/execution/dashboard/ledger.py`
and two endpoints: `GET /api/runs/{id}/account` (the ledger and the contrast)
and `GET /api/events?run_id=` (the run's stages, as they happened).

**The rules came from the server again.** The ledger's standing is the
statistical gate's verdict (PASSED, INSUFFICIENT, REJECTED) read over the
records; the contrast's test is the report's own paired test, with the
report's own floors; the timeline's stage names are the pipeline's own verbs.
The browser draws what it is given.

**What the work taught.**

**The number keys ran out, and the answer was a letter each — not a
sacrifice.** The plan said the tenth view would have to come in another way.
The live rail's toggle moved from `L` to `R` (the *rail*), and `L` went to the
ledger; the keys everything else owns now live in one list (`src/keys.ts`), so
a view that claims a key another panel holds is refused rather than stealing
it. The stage is the main view area: it holds the first claim on a key.

**A stage that spoke twice has two times, and a bar between them lies.** The
first timeline drew each stage as a bar from its first word to its last, and
the stages that ran in two rounds drew a bar across the whole run — as if the
training had taken the entire forty seconds. The picture now draws the
*events* as marks and joins the stages by the gap between them: the run's
shape is the silence between the lanes, and the silence is named.

**A ledger that lists only the claims hides the hole they leave.** The arms
that fell short of the seed floor are on the ledger too, with their standing
(`INSUFFICIENT`), because a reader who sees only the claims cannot see what
the run is missing. The report's own limitations sit underneath, and they
say it in words: "4 of 4 cells have fewer than the 63 seeds needed".

**The report's test and the dashboard's test are not the same test, and the
plan should say so.** The report picks the pair with the widest spread
*across metrics* — for the demo run that is `walltime_s`, not `val_acc`,
because 3.6 seconds is a wider number than 0.37. The contrast is measured on
the run's *own objective* (its first claim metric) and on the axis that
spread widest on it. Both are the system's own machinery; they are measured
on different metrics, and the ledger quotes the report's verdict verbatim so
the reader can see which is which.

**A picture of a run is not a picture of its evidence.** The nine evidence
views all answer "what did the run measure?". The three new ones answer
"how did it get there", "what can it say", and "which arm won" — and the
tour's own check agrees: the closest pair that involves a new view is the
uncertainty and the contrast (3.4 %), and the timeline is 20 % away from
the closest picture it shares a frame with.

**The silence had to be *shaded*, not merely drawn.** The timeline's first
version marked the run's long pause with a line and a label, and it measured
2.4 % different from the uncertainty view — below the floor, and a warning:
two pictures of the same run, both mostly empty, are the same picture to a
reader. Shading the pause across the frame turned the same view into 27 %
different, because the pause is the *biggest thing in the picture* and it had
not been drawn as one. A picture's weight is its ink, and the check measures
ink. The closest pair in the whole set is still the convergence and the
uncertainty (2.7 %) — both are dark pictures with few marks, and they were
that close before this batch.

**The number keys are not the only way in, and the selector is the honest
one.** The tour drives the views by their keys, so the keys are exercised
end to end; but the legend's selector names every view, and the plan's
"twelfth view needs a different way in" is now a letter rather than a
sacrifice.

---

## This batch (the flow, and the effect)

**What was built.** Two more views of the stage — one of the run as a
*process*, one of what the run can *attribute* — and the server half that
both of them draw:

| Piece | The file | What it is |
|-------|----------|------------|
| The flow | `src/stage/flow.ts` | one column per stage, in the order the run reached it: the cells it carried, the records it wrote, and what the gate refused drawn on top of the stage that refused it |
| The effect | `src/stage/effect.ts` | one column per axis: a band spanning the arms of an axis that varied, a mark for an axis that was held fixed |
| The run's arms | `dashboard/arms.py` | the statistics of an arm — its mean, its spread, its seed count, the gate's standing — read once for the ledger and the effect |
| The run's flow | `dashboard/flow.py` | the stages, the count each handled, the refusals, and the run's shape in a sentence |
| The run's effect | `dashboard/attribution.py` | every axis, whether it varied, the spread of its arms, and the reason the run can or cannot attribute |
| The endpoints | `web.py` | `GET /api/runs/{id}/flow` and `GET /api/runs/{id}/attribution` |

And one small change to the producer: `_announce_stage` now publishes the
gate's refusals with the stage's counts (`rejected_count` off the stage's
fragment), so the flow can say what the gate threw away.

**The rules came from the server, as always.** The flow's counts are the
events' own — the stage announcement carries them, and the measurements carry
the cell they measured. The effect's arms are the records' own, read through
the same `arms.py` the ledger reads, so the two pictures cannot disagree
about what an arm measured. The effect's *judgement* — whether the run is
big enough to attribute anything — is the server's sentence, not the
browser's: *"one axis varied (credit) and five were held fixed: this run can
speak about credit alone."*

**The forest was not run, on purpose.** The plan's caution was right, and it
is worth keeping in the code rather than only in the plan: over twenty
records and one varied axis, a random forest over one-hot features has
nothing to fit, and what it returns is a worse attribution than the spread
the ledger already draws. The view says plainly that the design is too small
to attribute, which is both the honest answer and the more useful one — a
reader who knows which axes were held fixed cannot be misled by a number.

**What the work taught.**

**A stage that shares a canvas with the view before it must clear it.**
Every flat view draws on one 2D canvas, and a view with nothing to draw
returned *before* it cleared anything: the picture of the view it replaced
stayed on the stage while the legend named the new one. The canvas now
clears itself when it is shown, so a view that has nothing to say leaves an
empty stage instead of a stale one.

**Two arms that stand at the same level write their names on top of one
another.** The demo's `gradient` and `local_goodness` arms are 0.0008 apart
on `val_acc` — one pixel on the picture — and the first version of the
effect drew their names over each other. A name that would collide is now
stepped aside, and the arms' names sit *beside* their dots rather than
above them, so a name is never mistaken for a neighbour's.

**The run's stages say three different things, and the picture has to know
which is which.** The stage announcement says how many *cells* the stage
handled; the records arrive one *batch* at a time; and the measurements
arrive one *cell* at a time, each naming the cell it measured. Adding them
up gives a number that is none of them. The flow reads them apart: the
count of a stage is the cells it carried, else the records it wrote, else
the measurements it made.

**The picture's own furniture is worth looking at.** The flow's first
version put the rules that refuse a cell in the top right, and the gold
record columns ran straight through the text. The rules were also a copy of
what the map's legend already says, in a panel that is on screen in every
view. The rules moved to the empty top left, and the picture got a column
of its own for the run's own refusals — the gate's, which is the part the
plan asked for and the part that is about the *run*.

**A summary is a sentence, not a list of facts.** The flow's first summary
read "four cells went through · 5 stages · the gate refused none · four
cells measured · twenty records written" — five facts, none of them
attached to a verb. It reads better as "four cells went through the
pipeline; the gate refused none; four cells measured; twenty records
written", and the numbers are said in words, as the narration says them.

---

## This batch (the surfaces outside the canvas, and the layers)

**What was built.** Two things: the stage's fifteenth view, and the pictures
of the system that live *outside* the canvas.

| Piece | The file | What it is |
|-------|----------|------------|
| The layers | `dashboard/src/stage/layers.ts` | the space cut into sheets: one sheet per value of the third axis, the cells the run measured standing up off their own sheet, the rest of the space the ground they were not in |
| The gallery's figures | `scripts/capture_dashboard_tour.py` | four of the gallery's own PNGs, each with its caption and the demo that produced it under it |
| The report's plots | `scripts/dashboard_capture.py` | a fourth frame kind, `plot`: a chart the report drew, taken out of the report and given a window of its own |
| The `comp` reports | `scripts/capture_dashboard_tour.py` | five commands, run in the tour's own process, their own words photographed: the coverage report, the objectives the system has *not* measured, the catalogue, the method cards, the power analysis |

The tour is now thirty-eight pictures: the fifteen views of the stage, the
run's own report and text, the gallery, the report's charts, and the
commands. The measured spread over the stage's views is 2.4 % to 30.5 % (the
tightest pair is the uncertainty and the layers, both dark pictures with few
marks); the floor is 2 %.

**What the work taught.**

**The demo's own cells have no state to settle, and the stability analysis
does not notice.** The probe (`scripts/probes/todo69_dynamics_probe.py`)
composes the demo's leading cell — digital / feedforward / instantaneous /
null / gradient / adam, `geometry.hidden_dim=32`, untrained — and measures
what the dashboard would draw. The settling norm is `0.0` at every step, and
the Lyapunov spectrum is `[0.0046, 0.0016, -0.0002]`: the transition being
measured is the identity. The reason is in `computronium/experiment/surface/
cli.py`'s `_build_transition_fn`: it calls `forward_pass` and *discards the
result*, then settles the activity it already had — so for an instantaneous
dynamics the map is the identity, and for a feedforward geometry the state's
activity is the *input*, which the output cannot be fed back into. The
dynamics family cannot be drawn from the demo's measured cells; it has to
measure a cell of the *declared space* that has a state (the space holds
`recurrent` geometry and `error_predictive_coding` dynamics), and it has to
say which cell it measured and whether the weights were trained.

**A basin needs an iterative dynamics and a recurrent geometry, and the
command already knows it.** `_run_basin_analysis` refuses to run the basin
for anything else, and the refusal is in the code rather than in a note.
The dashboard's basin view should read the same rule from the server rather
than deciding for itself.

**A terminal frame that cuts its text off is a picture of half an answer.**
The terminal's font was fixed at 14 px, and the method cards' list — sixty-
eight lines — ran off the bottom of the picture. The font is now sized to
the text (`dashboard_capture.terminal_font_size`): a short answer is drawn
large, a long one small, and the whole of it is in the frame.

**A chart that is still drawing moves the thing it is drawn in.** The first
attempt at the report's plots scrolled the page to the chart and took the
picture; the chart was still rendering, the page grew under the scroll, and
the picture held the *bottom* of the plot. The chart is now taken out of the
report altogether and given a page of its own — a picture of one thing
deserves the whole frame, and the report's plot is a picture of one thing.

**The report's heatmaps are empty for a run that varied one axis.** The
demo run measured one geometry and one dynamics, so the coverage heatmap
over its own records is a single cell and the chart draws nothing but its
axes. The tour photographs the Pareto front and the seed stability instead,
and the heatmaps are left for a run that has a grid to draw.

**A letter of its own is not always a free initial.** The layers view would
have been `L`, and `L` is the ledger's; `A` is the ablation chart's and `S`
the variability chart's. The view took `Y` — the first free letter in its own
name — and the rule is now written down: a view takes a letter of its own
that no panel, chart or view already holds.

**A sheet of eight with four pins on one of them says what a run filled.**
The layers view is the only picture of the *shape* of the run's reach: the
demo measured one value of the dynamics axis out of the eight the space
declares, and four cells of it. The terrain says the same thing as a surface
and the map says it as a field of cubes; the sheets say it as a stack.

---

## This batch (the cell's own dynamics)

**What was built.** The last family of the stage: four views of the *system*
being measured rather than the bookkeeping around it, and the server half
that measures them.

| Piece | The file | What it is |
|-------|----------|------------|
| The system's own transition | `computronium/experiment/analysis/transition.py` | the map: one step of the relaxation the cell's own settle performs, over the cell's own activity |
| The shared relaxation | `computronium/ontology/dynamics/_relaxation.py` | the prediction relaxation, in one place: the settle loops over it and the stability analysis measures it |
| The cell's own dynamics | `computronium/experiment/execution/dashboard/dynamics.py` | the trajectory, the spectrum, the basin and the landscape, and the sentence that says what they mean together |
| The endpoints | `web.py` | `GET /api/runs/{id}/dynamics` and `GET /api/cells/dynamics` |
| The views | `src/stage/dynamics.ts` | the trajectory (`J`), the spectrum (`M`), the basin (`B`), the landscape (`N`) |

**The transition was the identity, and the plan had already said so.** The
probe found it: `_build_transition_fn` computed the forward pass and threw it
away, then handed the settle the activity the state already had, so the map
was the identity and the spectrum was a row of zeros. The transition is now
the relaxation the cell's own settle performs, one step at a time, over the
cell's own activity — the hidden layers and the readout, with the input
clamped as the settle clamps it. The same function is read by
`comp stability-analysis`, so the picture and the command cannot disagree.

**A cell has to have a state, and the run's cells do not.** The demo's cells
are feedforward with an instantaneous pass: a cell like that has nothing to
settle, and the transition says so rather than measuring the identity. The
server therefore looks for the *nearest* cell of the space that does have a
state — the dynamics swapped for one that relaxes, the geometry for a
recurrent one, the credit for one that dynamics accepts — and the payload
names every axis it swapped, so a picture of a cell the run never measured
is never mistaken for one it did.

**What the work taught.**

**The relaxation is the system's own, and it is not the same relaxation for
every dynamics.** An energy-based cell relaxes toward its Hopfield energy
and a predictive one toward its prediction error; the transition has to be
*that* cell's, or it measures a system that does not exist. The prediction
relaxation was pulled out of the settle that looped over it
(`ontology/dynamics/_relaxation.py`) so that the settle and the analysis
step the same function.

**A cached answer is only an answer if the question had something to
answer.** The dashboard cached the first measurement of a run — taken before
the run had measured anything — and served "this run measured nothing" for
the rest of the run's life. The cache now holds a measurement of a *cell*,
and a run without a cell is asked again.

**The browser asks again, and only once at a time.** The dynamics are
measured on the server and are expensive to measure, so the browser asked on
every poll and piled up six requests before the first had answered. It asks
again only when the run has a cell to show, and it holds one request at a
time.

**What the work did not settle.** The pictures are of an *untrained* cell,
and the payload says so: the store does not carry the trained cell, so the
server would have to train one before it measures. An untrained recurrent
cell's relaxation drifts rather than settling, and the pictures say that —
the state does not settle, one direction grows, and nothing comes back —
which is a true answer about an untrained architecture, and not yet an answer
about a trained one. The next thing to try is the trained cell.

---

## Where the next session starts

1. **The dynamics views** — the ones worth the most, and the ones the probe
   says are not ready yet. Two things have to be true first:
   - **the transition must be the system's own.** The transition that
     `comp stability-analysis` builds is the identity for the demo's cells
     (the forward pass is computed and discarded), so the picture it would
     draw is of nothing. A dashboard-side transition has to feed the
     forward pass into the settle, and it has to be the *same* transition
     the command uses — one function, in one place, read by both. Whether
     that changes the command's own numbers is a question for whoever
     changes it: the numbers are currently the exponents of an identity.
   - **the cell must have a state.** The demo's measured cells are
     feedforward with instantaneous dynamics, so they have nothing to settle.
     The declared space holds cells that do (`recurrent` geometry with
     `error_predictive_coding` or `predictive_settling`), and the view can
     measure one of those — but then the picture is of a *cell of the space*,
     not of a cell the run measured, and the payload must say so.
   - The machinery is in `computronium.stability`
     (`measure_settling_time`, `estimate_basin_stability_multistart`,
     `estimate_lyapunov_spectrum`) and in
     `computronium/experiment/analysis/energy_landscape.py`; what is missing
     is the server that composes the cell and the view that draws the
     answer. The endpoint has to be asked for a *cell*, not a run.
2. **The multi-run space** — several runs' evidence in one space, coloured
   by run. It needs two runs in one store, and the tour's campaign writes
   one: a second campaign (or a second profile) in the same store is the
   smallest change that makes the view show anything.
3. **The remaining surfaces** — the defect registry (empty for a run with no
   defects: a picture of nothing, so it wants a run that has some), the
   comparison between two runs, and the panels on their own.

**The number keys are full** (fifteen views, the keys `1`–`9` and `T`, `L`,
`D`, `F`, `E`, `Y`). The next view needs a letter of its own, and the letter
has to be one the panels and the charts do not hold — `src/keys.ts` is the
list that says which, and `buildKeys` refuses a view that claims one. The
free letters are `B`, `G`, `I`, `J`, `K`, `M`, `N`, `O`, `Q`, `U`, `W`, `X`
and `Z`.
