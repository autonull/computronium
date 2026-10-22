# TODO70: The Dashboard Is the Instrument — Control, Chrome, and Starting From Nothing

**Objective**: Make the dashboard a thing you *drive*, not a thing you watch.
Today it is a picture of a run; it should be the place the run is controlled
from — including the case where there is no run yet.

**Source**: the reader's feedback on the TODO69 dashboard, in four parts:

> - It isn't clear how the experiments can be controlled from the Dashboard.
>   There should be a control area that has a Play/Pause button, a CPU usage
>   slider w/ animated current usage indicator, along with any other controls.
>   A separate popup panel with additional options to control the experiment
>   process.
> - The visualization selector should not be a dropdown but a toolbar of mini
>   icon buttons, with a prev/next pair of buttons to switch in sequence.
> - The pareto popup, and other popups, should be toggleable individually (and
>   closeable).
> - Consider any other functionality that helps a user control the system
>   entirely through the dashboard, starting from no configuration.

**Key Decision**: The controls are real, and they reach a run that lives in
another process. The dashboard's verbs do not act on a picture of a run — they
act on the run itself, through a **control plane** that both processes read and
write: a small document beside the store. Everything else in this plan is the
chrome that makes those verbs findable.

---

## The gap, stated plainly

The TODO69 dashboard is a very good picture and a nearly useless *instrument*.
What it has today:

| What exists | Where | What it does |
|-------------|-------|--------------|
| Three cell verbs | `dashboard/actions.py`, the cell drawer (`src/cell-drawer.ts`) | replicate / preregister / adopt-as-quest, one cell at a time, behind a click on a 3D pillar |
| A campaign queue | `execution/campaign_queue.py` | `enqueue`, `cancel`, `preempt`, `get_resource_usage` |
| Two queue endpoints | `web.py:447`, `web.py:457` | `POST /api/campaigns/{id}/cancel`, `…/preempt` — **the browser never calls them** |
| A run's *declaration* | `RunSpec` | immutable once the run has begun; nothing in the browser edits it |

What it does **not** have:

| Missing | Consequence |
|---------|-------------|
| A run-level control surface | there is no pause, no stop, no "advance one cell"; the only controls are three cell verbs, and they are three clicks deep into a 3D picture |
| A way to set the machine's effort | `_CELL_WORKERS = 4` (`surface/_cli/_execution.py:34`) is a module constant fixed when the backend is built; the reader cannot turn it |
| A live *usage* measure | `cpu_utilization` in the HUD is `used_cpus / max_cpus` (`campaign_queue.py:390`) — the queue's *allocation*, not the machine's use |
| A way to start anything | `comp dashboard` in one terminal, `comp run demo` in another. From no configuration, the dashboard cannot make a run |
| A way to see what is open | the charts are one tabbed container; the legend, the HUD, the rail and the caption each have their own key, and there is no place that shows what is showing |
| A control that reaches another process | the event bus is process-local (`execution/events.py:6`); the dashboard cannot tell a pipeline in another terminal anything |

The last row is the one that shapes the plan. **Everything else is chrome; this
is architecture.**

---

## Current State

| Piece | Path | Status |
|-------|------|--------|
| The live dashboard | `computronium/experiment/execution/dashboard/web.py` (1742 lines) | complete: 3D map, drawer, charts, HUD, live rail, the caption, the three cell verbs |
| The event bus | `computronium/experiment/execution/events.py` | complete — **and process-local**, which is why it cannot carry a control |
| The campaign queue | `computronium/experiment/execution/campaign_queue.py` | complete: priority, quotas, cancel, preempt — `cancel` on a *running* campaign only marks the entry (`campaign_queue.py:322`) |
| The pipeline | `computronium/experiment/execution/pipeline.py` | complete: `_shutdown`, a round loop, a deadline check between batches — **no pause** |
| The backend | `computronium/experiment/execution/backends.py` | `LocalBackend(max_workers=N)` → `asyncio.Semaphore(N)`: the ceiling is fixed at construction |
| The run's declaration | `computronium/experiment/schema/run_spec.py` | complete: a frozen, validated `RunSpec`; `n_seeds`, `epochs`, `budget_seconds`, `device`, `fidelity`, `axes` |
| The profiles | `computronium/experiment/surface/_cli/_profiles.py` | five profiles as data (`quick-verify`, `production-map`, `maturation`, `claim`, `demo`) — **not reachable from the browser** |
| The browser | `dashboard/src/` | `main.ts`, `hud.ts`, `plotter.ts` (3 charts in 1 tabbed panel), `cell-drawer.ts`, `live-rail.ts`, `caption.ts`, `stage/` (24 views + switcher + state) |
| The keys | `dashboard/src/keys.ts` | panels `h r c`, charts `p a s`, cycle `v` — 22 letters taken, **4 free** |
| The tour | `scripts/capture_dashboard_tour.py` | 43 pictures; the browser's acceptance mechanism |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  Pipeline (another process)                                                 │
│    PipelineRunner.run()                                                      │
│      ├─ _await_control()  ← reads the plane at every batch & round boundary │
│      ├─ backend.set_max_workers(n)  ← the ceiling the reader set            │
│      └─ publishes { in_flight, cells_done, stage }                           │
└──────────────────────────────┬───────────────────────────────────────────────┘
                               │  the control plane: one small JSON document
                               │  beside the store, written by whoever holds
                               │  the dashboard, read by the run
                               ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  control.py (TODO70) — the plane                                             │
│    ControlState: paused · step_budget · max_workers · cancel · revision      │
│    control_plane_path(store)  ← both sides derive the same path             │
│    ControlPlane.read() / .write(**changes) / .wait_for_release()            │
└──────────────────────────────┬───────────────────────────────────────────────┘
                               │  GET  /api/control     POST /api/control
                               │  POST /api/runs       GET /api/profiles
                               │  GET  /api/axes
                               ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  Browser                                                                      │
│    control-bar.ts     the verbs, always visible: ⏵ ⏹ ⏭ · ceiling · meter   │
│    control-panel.ts   the popup: the new-run form, the queue, the exports    │
│    panels.ts          the panel registry: one toggle per popup, one rail     │
│    stage/switcher.ts  the view toolbar: mini icon buttons, ‹ ›              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### The control plane — the one new idea

`computronium/experiment/execution/control.py`:

| Piece | What it is |
|-------|------------|
| `ControlState` | a frozen dataclass: `paused: bool`, `step_budget: int`, `max_workers: int | None`, `cancel: bool`, `revision: int`, `updated_at: float` |
| `control_plane_path(store_path)` | the plane's path, derived from the store's — the **only** place that knows where it lives |
| `ControlPlane` | reads the document, merges a write into it (revision-stamped), and waits for a release |

The dashboard **writes** the plane; the pipeline **reads** it. Both sides call
`control_plane_path`, so they cannot disagree about where it is.

**Why a file and not something cleverer.** Four alternatives were considered
and rejected:

| Alternative | Why not |
|-------------|---------|
| The store (DuckDB) | the dashboard *refuses* to write the store (`DashboardConfig`'s docstring, `web.py:204`); DuckDB is single-writer, and the writer is the run |
| The mirror | the mirror lags by a publish — a control that arrives one publish late is a control that arrives late |
| The event bus | process-local by construction (`events.py:6`); the dashboard and the run are usually two processes |
| A socket / HTTP callback from the pipeline to the dashboard | the run would have to know the dashboard's address, and the dashboard would have to be up before the run — the wrong dependency direction for "start from nothing" |

A small JSON document beside the store crosses the process boundary with no
lock, no port, and no new dependency. It is also *inspectable*: a reader can
`cat` it and see exactly what the dashboard asked the run to do.

### The verbs, and what each one means

| Verb | The plane says | The run does | Why it is not something else |
|------|----------------|--------------|------------------------------|
| **Play** | `paused = false` | releases at the next boundary | — |
| **Pause** | `paused = true` | finishes the cell in flight, records it, and holds | **A pause is not a kill.** The cell in flight is completed and stored; a pause that killed the process would lose the cell *and* the run's place in the space |
| **Step** | `step_budget += 1` | releases exactly one more batch, then holds again | stepping a *batch* and stepping a *cell* are different things; the plan says **batch**, and the payload says which |
| **Stop** | `cancel = true` | the pipeline's own `_shutdown`, at the next boundary | a stop is not a pause: it ends the run and the run's report says it was stopped |
| **Ceiling** | `max_workers = n` | `backend.set_max_workers(n)`, live | the ceiling is the number of cells *in flight at once*, not a percentage of the machine |
| **Budget** | — | immutable | a run's declaration is frozen once it has begun; the panel shows it and says so rather than offering an editor that would lie |

**The ceiling and the use are two different numbers, and the picture must show
both.** The slider sets the ceiling; the meter shows the cells in flight *now*;
a third mark shows the machine's own CPU. Collapsing them into one number would
be a lie about which is which, and the reader would have no way to tell a
saturated run from a starved one.

### The animated current usage

- The control bar polls `GET /api/control` at **2 Hz**. The dashboard's own
  update loop is `update_interval = 2.0` seconds (`DashboardConfig`) — far too
  slow for an indicator that is meant to move.
- The meter has three parts: the **target** (the slider's thumb), the **level**
  (cells in flight, over the ceiling) and the **trace** (a sparkline of the last
  sixty samples).
- The *trace* is what says "saturating" or "starved". A level alone cannot: a
  run at four of four cells and a run at four of four cells on a machine with
  four free cores look identical.
- The measurement is the server's, never the browser's: `psutil` is already a
  dependency (`pyproject.toml:108`), and the pipeline publishes its own
  in-flight count.

### From no configuration

| Endpoint | What it answers |
|----------|-----------------|
| `GET /api/profiles` | the five run profiles as data (`_profiles.py:64`): name, description, stages, fidelity, task, seeds, epochs, budget, the axes it varies |
| `GET /api/axes` | the six structural axes and the primitives available on each (`AXES_REGISTRIES`) |
| `POST /api/runs` | build a `RunSpec` from a profile plus the reader's edits, write it, and enqueue a `CampaignSpec` |

**Without a campaign queue the button refuses, and says the command to run
instead.** The dashboard must never appear to have a control it does not have;
the honest answer is the exact `uv run comp run demo --store …` the reader
could type. (The existing cell verbs already take this stance — see
`_schedule_quest`, `web.py:1136`.)

### What else the reader can do from the dashboard

The fourth piece of the feedback asks for *any* functionality that lets the
system be controlled from the dashboard. These are the affordances that fall
out of the same machinery, and each one is a thing that today needs a terminal:

| Affordance | What it replaces | Where it lives |
|------------|------------------|----------------|
| **Start a run** | `uv run comp run demo --store …` | the control panel's *New run* section |
| **Measure more seeds of a cell** | `comp …` by hand | the *replicate* verb, hoisted out of the cell drawer so it needs no 3D click |
| **Preregister a claim** | writing a registration file | the *preregister* verb, hoisted the same way |
| **Adopt an unmeasured cell as a question** | — | the *quest* verb, hoisted the same way |
| **Cancel or preempt a queued campaign** | `kill` | the control panel's *Queue* section |
| **Set the queue's ceilings** | editing the queue's construction | the control panel's *Queue* section |
| **Choose which run the dashboard shows** | — | the legend's run picker (already there) |
| **Read the run's own account of itself** | `comp report` | the control panel's *exports*: the narration script, the report, the records as JSON |
| **Take the current picture away** | a screenshot | an export of the stage's current view as a PNG (the Pareto chart already has its own) |
| **Watch a session as a film** | the tour's recorder | a *record this session* button in the control panel — the recorder the tour uses, driven from the browser |

The last one is the most speculative and the most worth having: the tour
already photographs a live session with the captions on screen
(`scripts/capture_dashboard_video.py`), and the machinery exists. It is listed
here so the decision is made deliberately rather than rediscovered.

### The view toolbar

The `<select>` in the legend (`src/stage/switcher.ts:234`) becomes a strip of
**mini icon buttons**, one per view, with a **‹ / ›** pair at the ends.

| Rule | Why |
|------|-----|
| A dropdown hides twenty-four views behind one line of text | a reader who wants the terrain should not have to open a menu to find it |
| The strip scrolls horizontally; it never wraps | a wrapped strip would grow the legend until it pushed the map off the screen |
| `‹` / `›` step the sequence *and* scroll the strip | the strip is longer than the screen, so stepping must bring the button into view |
| Each view gets a glyph, grouped by kind | solids for the 3D views, marks for the flat ones, bars for the process, curves for the dynamics — a reader learns the grammar once |
| The active button is lit; the hovered one names the view and its key | the choice stays visible *where it is made* — the legend's title still says the view's name |
| The dropdown is not replaced by a worse menu | the view's name still appears in the legend's title, so a reader who cannot use the toolbar still reads the view's name |

### The popups, one at a time

A **panel registry** (`src/panels.ts`) owns every floating panel:

| Panel | Dom id | Toggle | Key |
|-------|--------|--------|-----|
| The HUD | `hud` | ✓ | `h` |
| The live rail | `live-rail` | ✓ | `r` |
| The caption | `caption` | ✓ | `c` |
| The Pareto chart | `plotter-pareto` | ✓ | `p` |
| The ablation chart | `plotter-ablation` | ✓ | `a` |
| The variability chart | `plotter-variability` | ✓ | `s` |
| The legend | `discovery-legend` | ✓ | `q` |
| The cell drawer | `cell-drawer` | ✓ (click a cell) | — |
| The control panel | `control-panel` | ✓ | `z` |

Three changes fall out of the registry:

1. **The charts become three panels, not one tabbed container.** Closing the
   Pareto chart must leave the ablation chart alone; today they share a
   container, so closing one closes all three. The tour's `show_tab` and
   `enlarge_plotter` helpers (`scripts/capture_dashboard_tour.py:378`, `:383`)
   are updated with it.
2. **Every panel gets a `×` and a toggle**, and the **rail** — a column of
   mini buttons down one edge — shows at a glance which panels are open. The
   rail is the honest home for "toggleable individually": a reader sees the
   set, not a list of keys.
3. **The dom ids the tour toggles keep working** (`hud`, `plotter`,
   `live-rail`, `caption`), or the tour is updated in the same commit. A
   rename that silently breaks the tour is a rename nobody notices until the
   pictures stop being taken.

### The keys

TODO69 left four letters free. TODO70 claims all four:

| Key | Verb |
|-----|------|
| `space` | play / pause |
| `x` | stop |
| `w` | step once |
| `z` | the control panel |
| `q` | the legend |

**After TODO70 no letter is free.** Twenty-six letters: fifteen belong to
views (`T L D F E Y J M B N U G I K O`), three to charts (`P A S`), three to
panels (`H R C`), one to the cycle (`V`), four to the control bar (`Q W X Z`).
The next view takes a **punctuation key** from a stated list (`,` `.` `/` `;`
`'`) or a chord — and `src/keys.ts` grows the list that says which. This is
recorded here because it is a decision, not an accident.

---

## Phases

### Phase 0: The control plane (server) ✅

**Goal**: one document both processes agree on, and a run that reads it.

1. `computronium/experiment/execution/control.py` — new:
   - `ControlState` (frozen dataclass) — `paused`, `step_budget`, `max_workers`,
     `cancel`, `revision`, `updated_at`.
   - `control_plane_path(store_path)` — the path both sides derive; `:memory:`
     and a pathless store get a path beside the working directory.
   - `ControlPlane` — `read()`, `write(**changes)` (revision-stamped, atomic
     replace), `wait_for_release()` (an async poll that returns when the plane
     is not paused, or when a step is owed).
   - A corrupt or half-written document is **not** an error: the plane reads as
     "not paused" and the dashboard says the plane could not be read. A
     truncated file must not stop a run.
2. `execution/backends.py` — the admission becomes adjustable:
   - the fixed `asyncio.Semaphore` is replaced by a gate whose limit can be
     lowered *and* raised without releasing permits the workers hold;
   - `set_max_workers(n)` on the backend.
3. `execution/pipeline.py` — the run reads the plane:
   - `_await_control()` at the start of `run()`, at every round boundary
     (`_run_round_loop`) and before every batch
     (`_execute_batch_with_isolation`);
   - a pause holds at the boundary; a step releases exactly one batch;
   - `cancel` sets the pipeline's own `_shutdown`;
   - the ceiling is pushed into the backend when it changes;
   - the run publishes its in-flight count and its stage.

**Acceptance**: a plane written by one process is read by another; a pause
takes effect at a boundary and not before; a step releases exactly one batch;
`set_max_workers` lowers the ceiling without disturbing the cells in flight;
a corrupt plane does not stop a run.

### Phase 1: The verbs (server) ✅

**Goal**: the browser can ask for what Phase 0 made possible.

1. `web.py`:
   - `GET /api/control` — the plane's state, the run's live counters, and the
     machine's CPU (psutil). The endpoint is *cheap*: it is polled at 2 Hz.
   - `POST /api/control` — `{paused?, step?, max_workers?, cancel?}`; merges
     into the plane; returns the new state.
   - `POST /api/runs` — a new run: `{profile, overrides}` → a `RunSpec` →
     a `CampaignSpec` → `queue.enqueue`. **Without a queue: a refusal that
     names the command to run.**
   - `GET /api/profiles`, `GET /api/axes` — what the form offers.
2. `dashboard/runs.py` — new, and it keeps `web.py` from growing: the
   profiles, the axes, the build-a-spec, the enqueue.
3. The **narration** says the verbs: *"The run is paused."*, *"The run is
   holding at four cells."* — the same rule as every other sentence: the
   *shape*, never a figure. The numbers are on the panels.

**Acceptance**: every verb the control bar shows has an endpoint that a
reader (or an agent) can call without a browser; a request for a run without a
queue is refused in words that name the alternative.

### Phase 2: The control bar (browser) ✅

**Goal**: the verbs are findable in one glance.

`src/control-bar.ts` — new, docked at the bottom-centre, always visible:

| Piece | What it is |
|-------|------------|
| **Play / Pause** | one button, two states; the state is the *server's* — the button shows what the server says, and the browser never decides |
| **Stop** | confirms before it stops a run |
| **Step** | enabled only while paused |
| **The ceiling** | a slider, `1 … max_workers`, with the current value named |
| **The meter** | the level (cells in flight / the ceiling), the machine's CPU, and the trace of the last sixty samples |
| **The door** | `⚙` opens the control panel |

**Rules**: the bar is a *panel* in the registry, so `h`-style hiding still
works; a verb that cannot be honoured is **disabled with the reason in its
tooltip** ("no campaign queue is attached"); nothing in the bar is a control
the server does not offer.

### Phase 3: The control panel (browser) ✅

**Goal**: the options that do not belong on a bar.

`src/control-panel.ts` — new, a popup with three sections:

| Section | What it holds |
|---------|---------------|
| **New run** | the profile picker → what the profile declares → the reader's edits (seeds, epochs, budget, device, fidelity, the axes to vary) → **Start**; without a queue, the refusal and the command |
| **This run** | the run's declaration as it stands — immutable, and the panel says so; its stage, its walltime, its records, the seeds it still owes |
| **The queue** | the queue's campaigns with their status; cancel / preempt each; the queue's own ceilings (`max_concurrent`, `max_cpus`, `max_gpus`) |

And the exports that make the dashboard the whole instrument: the narration
script, the run's report, the records as JSON.

### Phase 4: The view toolbar (browser) ✅

**Goal**: twenty-four views, visible at once.

`src/stage/switcher.ts` — the `<select>` becomes a strip; `src/icons.ts` — new,
the glyph set, one per view, grouped by kind; the ‹ / › pair steps and scrolls.

### Phase 5: The panels (browser) ✅

**Goal**: every popup is individually toggleable and closeable.

`src/panels.ts` — the registry, the rail, the close buttons; `src/plotter.ts` —
the one tabbed container becomes three panels.

### Phase 6: The tour, the narration, the docs ✅

- `scripts/capture_dashboard_tour.py` — shots of the control bar, the control
  panel, the view toolbar, the panel rail, the charts closed and open; and a
  **control round-trip**: the tour presses Play, reads `GET /api/control`, and
  *fails* if the server does not agree. A tour that photographs a control and
  never exercises it is a picture of a button.
- `docs/DASHBOARD.md` — the control plane, the verbs, the new endpoints, the
  panel registry.
- `docs/readme/dashboard.md` — the control bar, in pictures. **The README is
  rebuilt in the same commit** (`tests/property/test_readme_build_lock.py`
  failed at the commit before TODO69 for exactly this).
- `tests/unit/experiment/test_dashboard_control.py` — the endpoints.
- `tests/unit/experiment/test_control_plane.py` — the plane.
- `tests/property/test_dashboard_keys_lock.py` — no key is claimed twice, and
  the free-key list is the one the plan says.

### Phase 7: Carried from TODO69 — the map in more slices ✅

The one surface TODO69 left open (its "surfaces outside the canvas" table,
last row): *"the same run's space, cut three ways, side by side"*, from the
legend's axis picker. TODO69 cut it one way (the void view).

The toolbar of Phase 4 makes this cheap: the axis picker's three selects
(`#legend-axis-picker`) become three small rows of buttons, and a **slices**
view puts the three cuts side by side, so a reader sees that the space is not
one picture but six axes' worth of pictures.

---

## Risks

| Risk | Mitigation |
|------|------------|
| The controls are decorative | the tour presses Play and *fails* if the server does not agree; a verb that does not reach the server is a bug the tour finds |
| The plane and the run disagree | one path, derived by one function (`control_plane_path`); both sides call it, and the payload names the revision the browser last saw |
| A pause loses a cell | the pause takes effect at a *boundary*; the cell in flight finishes and is recorded. The plan says where the boundary is, and the test asserts the cell is stored |
| The plane is stale | every write is revision-stamped and the payload carries the revision; a stale browser's write is refused rather than applied |
| The ceiling fights the machine | the ceiling is a *cap*, not a target; the meter shows the use, and the trace shows whether the cap is binding |
| The letters run out | they have: the plan assigns the last four and names the punctuation list for the view after next |
| The dashboard appears to control a run it cannot | without a queue, `POST /api/runs` refuses in words that name the command to run. The panel is honest about what it can reach |
| The rail crowds the screen | the rail is one column of 20-pixel buttons on the right edge, and the panels it opens are the same panels as before |
| The panel registry duplicates the existing toggles | one registry: `hud.ts`, `plotter.ts`, `live-rail.ts` and `caption.ts` register with it, and the keys keep working |
| The tour breaks on a renamed dom id | the tour's panel ids are listed in the plan; a rename updates the tour in the same commit |

---

## Definition of Done

- [ ] `control.py` exists, both sides derive its path by one function, and a
      plane written by one process is read by another
- [ ] A pause takes effect at a boundary; the cell in flight is recorded
- [ ] A step releases exactly one batch and then holds again
- [ ] The ceiling is adjustable at runtime, and lowering it does not disturb
      the cells in flight
- [ ] `GET /api/control` is cheap enough to poll at 2 Hz, and carries the
      plane, the run's counters and the machine's CPU
- [ ] `POST /api/control` merges into the plane and refuses a stale revision
- [ ] `POST /api/runs` starts a run from the dashboard; without a queue it
      refuses in words that name the command to run
- [ ] `GET /api/profiles` and `GET /api/axes` answer what the form offers
- [ ] The control bar shows play/pause, stop, step, the ceiling slider and the
      animated meter; every verb it shows the server offers
- [ ] A verb the server cannot honour is disabled, with the reason
- [ ] The control panel holds the new-run form, the run's declaration, the
      queue, and the exports
- [ ] The cell verbs (replicate, preregister, quest) are reachable without
      clicking a cell in the 3D scene
- [ ] The view selector is a toolbar of mini icon buttons with a ‹ / › pair,
      and the view's name is still in the legend's title
- [ ] Every panel is individually toggleable and closeable; the charts are
      three panels, not one tabbed container
- [ ] The panel rail shows which panels are open
- [ ] The keys are in one list, no key is claimed twice, and the free-key list
      is the one the plan says
- [ ] The narration says the verbs in shape, not in figures
- [ ] The tour exercises the controls and fails when the server disagrees
- [ ] `docs/DASHBOARD.md` and the README show the control bar, and the README
      is rebuilt in the same commit
- [ ] The map can be cut three ways, side by side (carried from TODO69)

---

## Where the work stands

| Piece | State |
|-------|-------|
| The control plane (`control.py`) | ✅ done — Phase 0 |
| The dynamic admission (`backends.py`) | ✅ done — Phase 0 |
| The run reads the plane (`pipeline.py`) | ✅ done — Phase 0 |
| The endpoints (`web.py`, `runs.py`) | ✅ done — Phase 1 |
| The control bar | ✅ done — Phase 2 |
| The control panel | ✅ done — Phase 3 |
| The view toolbar | ✅ done — Phase 4 |
| The panel registry and the rail | ✅ done — Phase 5 |
| The tour, the narration, the docs | ✅ done — Phase 6 |
| The map in more slices (carried from TODO69) | ✅ done — Phase 7 |
| The property suite's 23 pre-existing failures (the gallery's `env_sha256`, `PROOF.md`'s banned phrases, the priors registry) | ⬜ carried — pre-existing and unrelated to this work; Register C hygiene |

TODO69 is done: the server speaks, the browser shows it, the tour and the
recording photograph both, and the stage shows twenty-four views of one run.
**What is missing is not a picture. It is a hand on the throttle.**

---

## Notes on the work done so far

### Phase 0 — the control plane

**What was built.**

- `computronium/experiment/execution/control.py` — the plane.
  `ControlState` (paused · step_budget · max_workers · cancel · revision ·
  updated_at), `RunStatus` (run_id · stage · in_flight · cells_done · at),
  `control_plane_path(store_path)`, and `ControlPlane` with `read()`,
  `read_all()`, `write(**changes)`, `write_status(status)` and
  `wait_for_release()`.
- `execution/backends.py` — `asyncio.Semaphore` is gone. `_AdmissionGate`
  counts what is in flight and compares it to a limit that may move in either
  direction; `set_max_workers(n)` raises it (waking the waiters) or lowers it
  (leaving the cells in flight alone). `ExecutionBackend` grew
  `set_max_workers`, `max_workers` and `in_flight`.
- `execution/pipeline.py` — `_await_control(consumes_step=…)` at three
  boundaries: the start of `run()`, every round boundary, and every batch
  boundary. `_apply_ceiling` pushes the plane's ceiling into the backend;
  `_publish_status` writes the run's own counters back onto the plane.
- `PipelineConfig.control_plane` carries the path. The CLI (`_execution.py`)
  and the campaign runner (`campaign.py`) both set it from
  `control_plane_path(store_path)`, so the run and the dashboard derive the
  same document from the same store.

**Decisions taken here, and why.**

- **The document holds two sections, not one.** `control` is the dashboard's
  half (what the run has been asked to do); `status` is the run's half (what
  it is doing now). The plan's architecture diagram has the pipeline writing
  `{ in_flight, cells_done, stage }`, and the run is in another process: a
  counter that only travelled on the process-local event bus would never
  reach the dashboard that needs it. Both sections are written whole, each
  preserving the other, so a pause never drops the run's status.
- **An advisory lock (`fcntl.flock`) guards the rewrite.** The plan wanted a
  channel with "no lock", and meant no lock *protocol* between the processes.
  A read-modify-write without one loses a pause when the run publishes its
  status at the same moment — and a lost pause is a control that does not
  work. The lock is a file beside the document; it needs no coordination and
  no port.
- **The ceiling is not a percentage.** `max_workers` is the number of cells
  in flight at once. The machine's own CPU is measured separately
  (`psutil`, non-blocking) and is a *different number*; the control bar shows
  both, because collapsing them would be a lie about which is which.
- **A step is spent at a batch boundary.** `step_budget` counts batches
  released. A round boundary lets a run *proceed* to the batch that will
  spend the step; the batch boundary spends it and then holds again. A
  round that produces no batch carries the step to the next one.
- **A pause holds; it never kills.** The cell in flight finishes and is
  recorded. The cell's absence would read as "the system refuses this cell"
  to every reader who looks at the map afterwards.
- **A corrupt document is not an error.** The plane reads as "not paused" and
  records why in `last_error`; the dashboard reports `readable: false` rather
  than showing a control it cannot honour.

**Evidence.** `tests/unit/experiment/test_control_plane.py` — 16 tests. A
plane written by a *separate interpreter* is read here; a pause holds a run
at a boundary and releases it; a step releases one batch; a corrupt plane
does not stop a run; the run publishes its counters; the ceiling moves in
both directions without disturbing the cells in flight.

### Phase 1 — the verbs

**What was built.**

- `GET /api/control` — the plane, the run's counters, the machine's CPU, and
  the queue's usage. Polled at 2 Hz, so every part is cheap: one small file
  read and one non-blocking sample.
- `POST /api/control` — `{paused?, step?, max_workers?, cancel?, revision?}`.
  The command merges into the plane; a browser that offers a stale revision
  is **refused** (409) rather than applied.
- `GET /api/profiles`, `GET /api/axes` — the five profiles and the six
  structural axes, as data, read from the same places the CLI reads them.
- `POST /api/runs` — `{profile, overrides, device?}` → a `RunSpec` → a
  `CampaignSpec` → `queue.enqueue`. **Without a queue the answer is 409 with
  the exact command to type** (`uv run comp run demo --store …`).
- `dashboard/runs.py` — the profiles, the axes, the build-a-spec, the
  campaign, the enqueue. `web.py` does not grow.
- `narration.py` — `control_sentence(control)`: *"The run is paused."*,
  *"The run has been stopped."* Shape, not figures: the ceiling and the
  counts are on the panels.

**Decisions taken here, and why.**

- **The edits travel as overrides, not as a spec file.** The campaign runner
  derives the declaration from the profile and the overrides; a declaration
  it derived differently from the one on screen would be a second truth.
- **`spec_from_profile` is the CLI's own mapping**, so a run started from
  the browser declares the run the command line would have declared.
- **`max_workers: null` clears the ceiling**; the endpoint reads
  `model_fields_set` so "not given" and "given as null" are different
  requests.
- **The CPU sample is primed.** `psutil`'s non-blocking percentage compares
  this call with the last one, so the first sample reads zero; the sampler
  keeps the last reading until a second exists, so a page that has just
  opened does not show a machine that looks idle.

**Evidence.** `tests/unit/experiment/test_dashboard_control.py` — 14 tests,
all over HTTP with no browser: the verbs land on the document the run reads,
a stale revision is refused, a run without a queue is refused in words that
name the command, the profiles and the axes answer what the form offers.

**Known pre-existing failure, unrelated.** `tests/unit/experiment/
test_dashboard_capture.py::test_surface_frames_name_their_command` fails on
`method_cards.py`'s import of `_GEOMETRY_BACKENDS`. It fails the same way on
the commit before this work.

### Phases 2–5 — the browser

**What was built.**

- `src/panels.ts` — the **panel registry** and the **panel rail**. Every
  floating panel registers: the HUD, the live rail, the caption, the three
  charts, the legend, the cell drawer, the control bar and the control panel.
  The registry is the one place that answers "what is open"; the rail is that
  answer drawn as a column of mini buttons down the right edge. Every panel
  also carries its own `×`.
- `src/control-bar.ts` — the **control bar**, docked at the bottom centre:
  play/pause, step, stop, the ceiling slider, the meter (the level, the
  machine's CPU, and the trace of the last sixty samples) and the door to the
  control panel. It polls `GET /api/control` at **2 Hz**.
- `src/control-panel.ts` — the **control panel**: *New run* (the profile
  picker, what the profile declares, the reader's edits, Start), *This run*
  (the declaration, immutable, and the panel says so), *The queue* (the
  campaigns, cancel and preempt, the queue's ceilings), *Cells* (the three
  cell verbs, reachable without a click in the 3D scene) and *Exports* (the
  narration script, the report, the records as JSON).
- `src/icons.ts` — the **glyph set**, one per view, grouped by kind: solids
  for the 3D views, marks for the flat ones, bars for the process, curves for
  the dynamics.
- `src/stage/switcher.ts` — the `<select>` is gone. The strip is a row of
  mini buttons that scrolls sideways and never wraps, with a `‹` / `›` pair
  that steps the sequence and scrolls the strip. The view's name is still in
  the legend's title.
- `src/plotter.ts` — the one tabbed container became **three panels**. Closing
  the Pareto chart leaves the ablation chart alone.

**Decisions taken here, and why.**

- **A panel is hidden by a class, not by clearing its `display`.** Clearing
  the inline `display` flattens a flex panel into a stack: the control bar is
  a row of verbs, and a row of verbs that has become a column is a different
  control. `.panel-hidden { display: none !important; }` hides a panel and
  leaves the display it was built with alone.
- **The charts sit in a column under the HUD** (`#chart-column`), not in
  three fixed slots: three 300-pixel panels do not fit beside the HUD on a
  1080-line screen, and a column that scrolls does.
- **The ceiling slider's maximum is the machine's cores**, and the value it
  shows is the ceiling *the run is holding to* — the plane's, or the run's own
  when the plane does not set one. The run publishes its ceiling on the plane
  so the bar never has to guess.
- **The trace carries two lines**: the cells in flight and the machine's own
  CPU. That is what says "saturating" against "starved" — a level alone
  cannot, because a run at four of four cells and a run at four of four cells
  on a machine with four free cores look identical.
- **The step button is enabled only while paused**, and the play/pause button
  shows what the *server* says. The browser never decides.
- **The verb keys are read through the registry**, not through a second list:
  `panels.byKey(key)` is the only place that knows which panel a key owns.

### Phase 6 — the tour, the narration, the docs

- The tour presses **Play** on the control bar, reads `GET /api/control`, and
  **fails** if the server does not agree; then it presses it again, so the run
  is not left paused by a photograph.
- New shots: the control bar, the control panel, the panel rail, the view
  toolbar, and the slices.
- `docs/DASHBOARD.md` gained the control plane, the verbs, the endpoints, the
  panel registry and the new keys. `docs/readme/dashboard.md` shows the
  control bar in pictures, and **the README was rebuilt in the same commit**.

### Phase 7 — the map in more slices

- The axis picker's three `<select>`s became three small rows of **buttons**,
  one per axis, with the ones another cut already holds dimmed.
- `src/stage/slices.ts` — the **slices** view: the same space cut three ways
  (x×y, x×z, y×z), side by side, so a reader sees that the space is not one
  picture. It needs no new data: the space and the records are already on the
  stage.
- The slices view is the **first view to take a punctuation key** (`,`), which
  is what the plan said would happen when the letters ran out.

**Two defects found and fixed on the way (both pre-existing).**

- `scripts/capture_dashboard_tour.py` started its capture thread **twice**,
  which raised `RuntimeError: threads can only be started once` — the tour had
  been dying before it took a picture.
- `computronium/experiment/documentation/method_cards.py` imported
  `_GEOMETRY_BACKENDS` and `_UPDATE_BACKENDS`, which the registry refactor
  replaced with `_GEOMETRY_REGISTRY` and `_UPDATE_REGISTRY`. The method-card
  command raised `ImportError`, and with it the tour's last frames — and
  `tests/unit/experiment/test_dashboard_capture.py` had been failing on it.
- Uvicorn's default logging config **disables every logger it does not
  name**, and the tour's logger was one of them: the tour could fail
  silently. The dashboard now starts uvicorn with `log_config=None`.

---

## What the work taught (for whoever comes next)

*Carried forward from TODO69, and true again here.*

**The dashboard had verbs, and none of them were run-level.** Three cell verbs
— replicate, preregister, quest — lived behind a click on a 3D pillar, and the
two endpoints that *could* stop a campaign were never called by the browser.
The instrument had a shutter release and no throttle.

**The event bus could not carry a control, and that was never its job.**
`events.py` says so in its own docstring: process-local, best-effort, and the
run that produced the event must never fail because a subscriber raised. A
control channel wants the opposite properties — durable, cross-process, and
silent when it is not read. Two different jobs, two different mechanisms.

**The store was the wrong place for the control, and the mirror was worse.**
The dashboard's own contract says it never writes the store; the writer is the
run. The mirror lags by a publish, and a control that arrives a publish late
is a control that arrives late.

**A pause is a boundary, not a kill.** The pipeline already had the right
shape for it: batches, rounds, and a deadline check between them. A pause
that raised a signal mid-cell would have thrown away a measurement the run
had already paid for — and the cell's absence would have been a *gap* in the
space, which reads as "the system refuses this cell" to every reader who
looks at the map afterwards.

**The ceiling was a constant pretending to be a setting.** `_CELL_WORKERS = 4`
is read when the backend is built, and `asyncio.Semaphore` cannot be
loosened without releasing permits the workers hold. Making the ceiling
movable is therefore not a slider in the browser; it is a different admission
gate in the backend.

**`cpu_utilization` was an allocation, not a use.** The HUD's CPU meter showed
`used_cpus / max_cpus` — the queue's bookkeeping — and the reader would have
taken it for the machine's load. The control bar has to show the *measured*
thing (psutil, the cells actually in flight) and label it as such.

**A dropdown is a menu for a choice nobody should have to hunt for.** Twenty-
four views behind one `<select>` is twenty-four views hidden. The toolbar makes
them a row of buttons; the ‹ / › pair is what makes a row longer than the
screen usable.

**The letters ran out at exactly the moment a new surface wanted one.** TODO69
left four free; TODO70's controls took all four of them, and took the spacebar
for play/pause besides. The next view needs a punctuation key, and the list
that says which belongs in `keys.ts` beside the others — not in a plan that
will be forgotten.

---

## The merged TODO69 remainder

TODO69 closed every item it listed. One was left open, and it is carried here
as Phase 7:

| TODO69 item | State |
|-------------|-------|
| The trained cell (server + views + tour) | ✅ done in TODO69 |
| The comparison between two runs (`comp diff`) | ✅ done in TODO69 |
| The remaining surfaces (the defect registry, the panels on their own) | ✅ done in TODO69 |
| **The map in more slices — the space cut three ways, side by side** | ⬜ **carried into Phase 7** |
| The property suite's 23 pre-existing failures | ⬜ carried as a note — Register C hygiene, unrelated to this work |
