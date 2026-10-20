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

## Current State

| Piece | Path | Status |
|-------|------|--------|
| The live dashboard | `computronium/experiment/execution/dashboard/web.py` | complete: 3D map, drawer, charts, HUD, live rail, the three verbs |
| The event bus | `computronium/experiment/execution/events.py` | complete: stage and measurement events, process-wide |
| The narration | `computronium/experiment/execution/dashboard/narration.py` | complete: the sentences, the account, the state |
| The caption | `dashboard/src/caption.ts` | complete: the sentences, rendered |
| The hero capture | `scripts/capture_dashboard_screenshot.py` | one image, one view |
| The tour | `scripts/capture_dashboard_tour.py` | twelve views, four kinds of picture |
| The recording | `scripts/capture_dashboard_video.py` | a `.webm` of a live session, uncommitted |
| The live rail | `dashboard/src/live-rail.ts` | terse pills: `[s6_train] train cells` — a log, not a story |
| The console dashboard | `computronium/experiment/execution/dashboard/console.py` | the same picture in a terminal, and a frame of it as text |
| The report | `comp report` | the numbers, as prose and tables |

### What was missing, and what closed it

| Gap | Impact | Closed by |
|-----|--------|-----------|
| No narration | the screen shows numbers and a log; it does not *say* what is happening, so a narrator reading the screen has to reconstruct the story from the panels | `narration.py`: the sentences, written once |
| No closed captions | a recording of the dashboard has no subtitles; the viewer reads a 3D scene in silence | `caption.ts`: the server's sentences, rendered |
| One screenshot | the hero is the dashboard's overview; nothing shows the drawer, the charts, the void cells, the space, the report | the tour: twelve views |
| No recording | "show me it working" needs a terminal in front of the reader | the recording: a live session, with captions |

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
```

---

## Phases

Phases 0–4 are done: the server speaks, the browser shows it, and the tour
and the recording show both. **Phase 5** — the main view area — is the
remaining work, and it is the one that changes what the dashboard *is*.

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
twelve views:

| Shot | What it shows |
|------|---------------|
| `dashboard-hero.png` | the overview (the existing shot, regenerated) |
| `dashboard-map.png` | the discovery map alone: the fog of war, panels hidden |
| `dashboard-cell.png` | the leading cell's drawer: metrics, curve, verdict, seeds to claim |
| `dashboard-void.png` | a void cell, in a slice of the space cut a different way, and the rule that refuses it |
| `dashboard-pareto.png`, `-ablation.png`, `-variability.png` | the three charts, each on its own, over the map |
| `dashboard-caption.png` | the caption over the map — the narrated picture |
| `narration-script.png` | the dashboard's account of itself, as text |
| `report-run.png` | the run's report, in the browser |
| `console-dashboard.png` | the console dashboard: the same picture, in a terminal |
| `report-text.png` | the run's report, in a terminal |

**Acceptance**: ✅ every shot is 1920×1080, has real data in it, and lands in
`docs/readme/assets/` (committed) and `docs/screenshots/` (mirrored). ✅ the
shots are of *different things*: the 3D map, the panels, the charts, a
browser report, and two terminal views. ✅ a shot that cannot be taken is
reported, not silently skipped.

**The tour's rule**: it waits for the dashboard's *state* — a measured cell,
a drawn chart, a caption with words in it — and never for a fixed pause.

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
- `docs/DASHBOARD.md` — the caption, the narration endpoint, the tour.
- `docs/readme/dashboard.md` — a "the dashboard, in pictures" section, in
  the README.

---

## Phase 5: The main view area — one canvas, many views ⬜ next session

**The problem**: the main view area — the canvas, the big picture — shows
*one* picture. The space, as a field of cubes: gaps as wireframe boxes,
measured cells as glowing pillars, refusals as red crosses. Everything else
the system knows — the frontier, the curves, the spread, the attribution,
the rules that refuse — is either a small panel over the scene or nothing at
all. A reader who wants to *see* the evidence has to read a table.

**The shape of the change**: the canvas is a *stage*, and a view is what
stands on it. The discovery map is one view; it should be one of several.
The scene is already shared (`components/context.ts` gives every component
the same scene, camera and renderer), and the map already knows how to clear
what it built (`clearGrid`) — so a view is a component with the same shape
as the map, and a switcher that stands where the plotter's tabs stand.

A view needs four things, and the map has all four:

| Part | What it does | Where it lives today |
|------|--------------|----------------------|
| `build` | put its objects in the shared scene | `createCell`, `createVoidMarkers` |
| `clear` | take them away again | `clearGrid` |
| `update` | re-read the run's records | `applyAggregates` |
| `frame` | put the camera where this picture wants to be seen | `frameGrid` |

**The views, in the order they should be built.** Each is a *different kind
of picture* of the same run; each is drawn from data the dashboard already
has, or can already ask for. The right-hand column is the test a view has
to pass: **what can a reader say after looking at it?**

#### The space, seen other ways (3D)

| View | What the main area would show | The data it needs | A reader would say |
|------|-------------------------------|-------------------|--------------------|
| **The space** (today) | the declared space: gaps as wireframe cubes, measured cells as glowing pillars, refusals as red crosses; the pillar's height carries the value | the space payload, the records | "the run measured four of the cells it declared, and here they are" |
| **The terrain** | the same space as a *heightfield* instead of cubes: accuracy as height over the two free axes, the gaps flat, the refusals holes in the ground | the space payload, the records | "this arm's accuracy is a ridge, and the ridge stops where the run stopped" |
| **The frontier** | every measured cell as a point in (accuracy, speed, parameters); the Pareto front drawn through them; the chance plane as a floor | the records, the `pareto` flags, `chance` | "nothing beat this cell on all three counts at once" |
| **The layers** | the three axes as a stack of 2D slices — the space cut into planes, so a reader can see the space from the side | the space payload | "the run filled a slab, and the slab is thin" |
| **The multi-run space** | several runs' evidence in one space, coloured by run | the store's runs, the space per run | "the second run went where the first one did not" |

#### The evidence, seen other ways (2D)

| View | What the main area would show | The data it needs | A reader would say |
|------|-------------------------------|-------------------|--------------------|
| **The evidence matrix** | one axis against another, each cell a number, the refusals in the void colour | the space payload, the records | "the credit arm mattered, and here is where" |
| **The convergence** | accuracy against epoch, one curve per arm, the chance line under them | the per-cell curves (the map's aggregates already carry them) | "the arms separate in the second epoch, not the first" |
| **The small multiples** | one panel per cell — every seed's curve, side by side | the per-cell curves | "this cell is steady and that one is not" |
| **The spread** | one violin per arm across the seeds, and the seeds a claim still needs as a mark | the records' seeds | "this arm is wide, and that is why the claim is not made" |
| **The claim's cost** | seeds measured against seeds needed, per cell, with the gap | the records' seeds, `required_seeds` | "the claim is 58 seeds short on four cells" |
| **The pairwise contrast** | arm against arm: which beat which, by how much, and whether the test was even run | the records, the report's contrast design | "pepita beat random_projections, and here is the margin" |
| **The attribution** | the objective attributed to the axis values — which axis moved it, and by how much | the attribution analysis over the records (`computronium/experiment/analysis/axis_attribution.py`: `analyze_axis_importance`, `compute_shap_attribution`, `compute_ice_curves`) | "the credit rule mattered most, and here is how much" |
| **The uncertainty** | each cell's interval against the threshold a claim would need | the records' spread, `required_seeds`, `alpha` | "even the best cell is not separable yet" |

#### The run, as a process (not as evidence)

| View | What the main area would show | The data it needs | A reader would say |
|------|-------------------------------|-------------------|-------------------| 
| **The timeline** | the run's stages as a waterfall, with their durations and their rounds | the pipeline's events (the live rail already has them, with timestamps) | "the run spent two thirds of its time training, and it measured nothing until the end" |
| **The pipeline flow** | the cells flowing through the stages, with the gate's refusals at the gate | the events, the space's refusals | "four proposals went in and one cell came out" |
| **The ledger** | every claim, its evidence and its verdict — PASS, INSUFFICIENT, REJECTED | the report's claims and limitations | "nothing here is a claim yet, and the report says why" |

#### The system, not the bookkeeping

These need the *trained system*, not just the records, so they are the most
work and the most worth having.

| View | What the main area would show | The data it needs | A reader would say |
|------|-------------------------------|-------------------|-------------------|
| **The settling trajectory** | a cell's state, drawn through the state space from where it started to where it stopped, coloured by time | the trained system (`comp stability-analysis`: settling trajectories) | "this cell does not settle where you think it does" |
| **The basin** | every initial state that settles to the same fixed point — the set of states the system is really in | the trained system (basin stability) | "the basin is a sliver, and the run is inside it" |
| **The energy landscape** | the system's energy as a surface, with the trajectory over it | the trained system (`computronium/experiment/analysis/energy_landscape.py`: `plot_energy_landscape`) | "the state it settled into is a local minimum, and this one is not" |
| **The spectrum** | the Lyapunov exponents — is the system stable, and in which directions | the trained system (Lyapunov spectra) | "this dynamics is stable, that one is not" |

**The last family is the one that changes what the dashboard is.** Every
view above is about the *bookkeeping* of a run — what was measured, what was
refused, what it cost, how long it took. The last family is about the
*system* being measured: where its states go, whether they settle, how much
energy they carry. A dashboard that can show that is a different instrument,
and it is the one the 3D canvas was built for in the first place.

**The switcher**: the view is a choice a person makes, so it is a key
(`V` cycles; the number keys, like the plotter's tabs, pick one) *and* a
selector in the legend, so the choice is visible rather than remembered. The
tour then captures one shot per view, and the tour's variety stops being a
matter of which panel is in front of the map.

### Where to start

1. **The terrain** — the first new view, because it is the *same* picture
   with a different geometry: the space the map already builds becomes a
   surface instead of a field of boxes. The map already knows each cell's
   position and its value; a heightfield is the same arithmetic with a mesh
   instead of a cube.
2. **The frontier** — the second, because it needs only the records, and it
   is the one picture every reader of a run actually wants: the accuracy,
   the speed and the parameters of every cell, and the line through the ones
   nothing beat.
3. **The switcher** — with two views on the stage, the switcher is what
   turns "two pictures" into "a canvas that can show more than one thing":
   a key that cycles and a selector that names the view where it is chosen.
4. **Then the 2D views** — the matrix, the convergence, the spread. A 2D
   view does not have to be three.js: `uplot` is already a dependency, and
   a 2D canvas can fill the content area just as well. What they share with
   the 3D views is the *switcher*, the *data* and the *tour shot*.
5. **Then the dynamics views** — the ones that need a cell re-instantiated,
   and the ones worth the most.

**Acceptance**: ✅ the canvas can show the space, the frontier, the matrix
and the spread, and the tour has a shot of each. ✅ a reader can answer
"what did the run find?" from any one of them. ✅ a view that is not active
leaves nothing of itself on the stage.

---

## The surfaces outside the canvas — the same argument, applied

The main view area is the biggest miss, but the system has more pictures
than the dashboard shows, and each is a *different kind* of picture of the
same evidence. Every row is a real surface in this repository, with the
command or the module that produces it; none of it is speculative.

| Surface | What it would show | Where it comes from | What it would add |
|---------|-------------------|--------------------|-------------------|
| **The gallery** | 21 figures — one per demonstrated capability: swaps, frontiers, coverage, ladders, failure manifestos | `comp gallery` (records in `docs/figures/run_records`, PNGs in `docs/figures/gallery`); the panel vocabulary is bars / graph / heatmap / lines / scatter / tree (`computronium/visualization/_demo_api.py`) | the *scientific* family: static figures with a palette, chance lines and value labels by construction |
| **The report's own figures** | 3 Pareto fronts (acc×walltime, acc×params, acc×flops), 4 coverage heatmaps (geometry×dynamics, geometry×credit, dynamics×credit, credit×update), failure clustering, convergence, scaling laws, seed stability | `computronium/experiment/reporters/html.py` — they are in the HTML report already, but only as one page | the report's plots, one at a time and at full size |
| **The energy landscape** | the system's energy as a surface, and where the states sit in it | `computronium/experiment/analysis/energy_landscape.py` (`plot_energy_landscape`) | a picture of *why* a cell settles where it does |
| **The seed violins** | per-arm distribution across seeds, not a mean | `computronium/experiment/analysis/seed_variability.py` (`plot_violin_plots`) | the spread the narration calls "the claim cannot be made yet" |
| **The coverage report** | which primitives of each axis the run touched, and which it did not | `comp coverage report` | the run's reach, as a table |
| **The catalogue** | the store queried by axis — every run and record, filtered | `comp catalog` | the evidence, browsable |
| **The defect registry** | the constraints, clustered, and which are revoked | `comp defect` | the rules that refuse cells, in the system's own ledger |
| **The method cards** | a card per primitive: what it is, what it costs, what it was measured at | `comp method-card` | the ontology, pictured |
| **The comparison** | two runs, differenced, with effect sizes | `comp diff` | what changed between two claims |
| **The power analysis** | the seeds a design needs, before it runs | `comp power-analysis` | the design, not the result |
| **The panels alone** | the live rail by itself, the HUD by itself, the legend and the axis picker by themselves | the dashboard's own DOM | each panel, as its own picture |
| **The map in more slices** | the same run's space, cut three ways, side by side | the legend's axis picker (`#legend-axis-picker`) | the space is not one picture: it is six axes |

**How to add them**: the tour already has a `Frame` with two kinds —
`browser` (a URL) and `terminal` (text in a window). A third kind,
**`figure`** (a PNG rendered in a page, with its caption and its provenance
under it), is all the gallery, the report's plots and the analysis figures
need. The terminal kind already covers every `comp …` command that prints a
report, so the coverage report, the catalogue, the defect registry and the
method cards are one `Frame` each.

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

---

## Definition of Done

- [x] Every event the dashboard forwards becomes a sentence that names a run, a cell, a number or a rule
- [x] `GET /api/narration` returns the current sentence, the recent lines and the whole story
- [x] The dashboard shows the narration as a closed-caption overlay
- [x] The tour captures the overview, the map, a measured cell, a void cell, the three charts, the caption, the narration, the report and the terminal views
- [x] A short recording of a live session exists, with the captions on screen, and is not committed
- [x] `docs/DASHBOARD.md` and the README show the tour
- [ ] The main view area can show more than one picture of the run: the space, the terrain, the frontier and the evidence matrix at least
- [ ] The view is a choice — a key and a selector — and the inactive view leaves nothing of itself on the stage
- [ ] The tour has a shot of every main view
- [ ] The tour can photograph a *figure* (a PNG with its caption and provenance), not only a page and a terminal

---

## Where the work stands

| Piece | State |
|-------|-------|
| `narration.py` — the sentences, the account | ✅ done |
| `web.py` — the frames, the endpoint, the state refresh | ✅ done |
| `pipeline.py` — the producer names the cell and the seed | ✅ done |
| `caption.ts` — the browser renders the sentences | ✅ done |
| the tour — twelve views in one browser session | ✅ done |
| the recording — a `.webm` of a live session, uncommitted | ✅ done |
| the docs — the caption, the endpoint, the tour | ✅ done |
| the dashboard shows a run before it has measured | ✅ done (the space is on screen from the first second) |
| the main view area — the stage, the views, the switcher | ⬜ Phase 5, next session |
| the figures — the gallery, the report's plots, the analyses | ⬜ the "surfaces outside the canvas" table |
| the mirror's publish can fail and lag | ⬜ a known flake, diagnosed above |

The server speaks, the browser shows it, and the pictures show both. The
canvas is still showing one picture, and that is the next thing to change.

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
