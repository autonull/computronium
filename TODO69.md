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
`.webm`, it is **not committed** (it is large), and it is written outside
the repository's tracked paths.

**Acceptance**: ✅ a `.webm` exists after a run, the captions are legible in
it, and `git status` stays clean.

**The recorder is not Playwright's own**: it needs a particular `ffmpeg`
build, and a machine without that build records *nothing* without saying so.
The script photographs the page and encodes the frames with the system
`ffmpeg`, at the rate the session actually happened.

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

## Risks

| Risk | Mitigation |
|------|------------|
| The narration becomes a second source of truth | it is composed on the server from the same payloads the panels render; the browser never writes a sentence |
| The caption covers the scene | it is two lines at the bottom, and the camera framing already leaves the panels' space free |
| The tour is flaky (software rasterizer, slow page) | the capture waits for the page's *state*, never for a fixed pause; a failed view is reported, not silently skipped |
| The video is large | it is written outside the repository's tracked paths and ignored |
| The narration is prose nobody reads | the same text is available over HTTP, so an agent can read it without a browser |

---

## Definition of Done

- [x] Every event the dashboard forwards becomes a sentence that names a run, a cell, a number or a rule
- [x] `GET /api/narration` returns the current sentence, the recent lines and the whole story
- [x] The dashboard shows the narration as a closed-caption overlay
- [x] The tour captures the overview, the map, a measured cell, a void cell, the three charts, the caption, the narration, the report and the terminal views
- [x] A short recording of a live session exists, with the captions on screen, and is not committed
- [x] `docs/DASHBOARD.md` and the README show the tour

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

The server speaks, the browser shows it, and the pictures show both.

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

**The map needs the run's records before it draws anything.** The declared
space could be drawn from the run's declaration alone, but the dashboard
only learns of a run through its metrics, and the metrics need records. So
the first half of a filmed session is an empty stage with the events
streaming in the rail. The caption carries that half: it keeps the last
event's sentence when there is no state to fall back to.

**The store's mirror outlives the store.** A capture that deletes the store
but not its mirror reads the *last* run's records as if they were this run's
— and the tour then asks the server about a run that is not in the store.
`dashboard_capture.clear_store` removes both.

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
