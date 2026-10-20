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
| The hero capture | `scripts/capture_dashboard_screenshot.py` | one image, one view |
| The live rail | `dashboard/src/live-rail.ts` | terse pills: `[s6_train] train cells` — a log, not a story |
| The console dashboard | `computronium/experiment/execution/dashboard/console.py` | the same picture in a terminal |
| The report | `comp report` | the numbers, as prose and tables |

### What is missing

| Gap | Impact |
|-----|--------|
| No narration | the screen shows numbers and a log; it does not *say* what is happening, so a narrator reading the screen has to reconstruct the story from the panels |
| No closed captions | a recording of the dashboard has no subtitles; the viewer reads a 3D scene in silence |
| One screenshot | the hero is the dashboard's overview; nothing shows the drawer, the charts, the void cells, the space, the report |
| No recording | "show me it working" needs a terminal in front of the reader |

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
Run demo · digits · L1 — EXPLORATORY. 1 cell measured, 5 records.
Best cell: gradient at 0.440 ± 0.032 (n=5). Chance 0.10. 58 more seeds
needed for a claim. Queue: 1 running, 0 queued. Picture: live.

Measured pepita/feedforward/instantaneous, seed 2: val_acc 0.512 (chance 0.10).
Stage 6 — train cells: 4 proposals.
Campaign queued quest-abc (normal priority).
```

**Acceptance**: ✅ every sentence names a run, a cell, a number or a rule — no
sentence a reader cannot check against the panels. ✅ `GET /api/narration`
returns text an agent can read aloud without the browser.

**Still to do here**: the browser half — the caption overlay that renders
these sentences (Phase 1). The server speaks; nothing draws it yet.

### Phase 1: The caption (browser) ✅

**Goal**: the screen says what it is doing, without being asked.

1. `dashboard/src/caption.ts` — a closed-caption overlay:
   - the latest sentence, in two lines, 22px, high contrast, bottom centre;
   - the state summary when nothing is happening;
   - a sentence stays up for a few seconds, then the summary returns;
   - `H`/`C` toggles it, like the other panels.
2. The caption is *rendered*, not composed: the words come from the server.

**Acceptance**: with the browser showing only the dashboard, a reader can say
what is running, what was measured, and what the number means.

### Phase 2: The tour (screenshots) ✅

**Goal**: more than one picture of the system.

`scripts/capture_dashboard_tour.py` — one store, one dashboard, one browser,
several views:

| Shot | What it shows |
|------|---------------|
| `dashboard-hero.png` | the overview (the existing shot, regenerated) |
| `dashboard-map.png` | the discovery map alone: the fog of war, panels hidden |
| `dashboard-cell.png` | a measured cell's drawer: metrics, curve, verdict, seeds to claim |
| `dashboard-void.png` | a void cell: the rule that refuses it |
| `dashboard-pareto.png`, `-ablation.png`, `-variability.png` | the three charts |
| `dashboard-caption.png` | the caption over the map — the narrated picture |
| `report-run.png` | the run's report, as a reader sees it |

**Acceptance**: every shot is 1920×1080, has real data in it, and lands in
`docs/readme/assets/` (committed) and `docs/screenshots/` (mirrored).

### Phase 3: The recording ✅

**Goal**: a short video of a live session, with the captions on screen.

`scripts/capture_dashboard_video.py` — Playwright records the browser while
the demo campaign runs; the caption narrates it. The file is a `.webm`, it is
**not committed** (it is large), and the path is ignored.

**Acceptance**: a `.webm` exists after a run, the captions are legible in it,
and `git status` stays clean.

### Phase 4: Polish, test, document ✅

- `tests/unit/experiment/test_dashboard_narration.py` — the sentences, the
  summary, the endpoint.
- `docs/DASHBOARD.md` — the caption, the narration endpoint, the tour.
- `docs/readme/` — a "the dashboard, in pictures" section.

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
- [ ] The dashboard shows the narration as a closed-caption overlay
- [ ] The tour captures the overview, the map, a measured cell, a void cell, the three charts, the caption and the report
- [ ] A short recording of a live session exists, with the captions on screen, and is not committed
- [ ] `docs/DASHBOARD.md` and the README show the tour

---

## Where the work stands

| Piece | State |
|-------|-------|
| `narration.py` — the sentences, the account | ✅ done, 14 tests |
| `web.py` — the frames, the endpoint, the state refresh | ✅ done |
| `pipeline.py` — the producer names the cell and the seed | ✅ done |
| `caption.ts` — the browser renders the sentences | ⬜ next session |
| the tour — seven views in one browser session | ⬜ next session |
| the recording — a `.webm` of a live session, uncommitted | ⬜ next session |
| the docs — the caption, the endpoint, the tour | ⬜ next session |

The server already speaks: every event it forwards now carries its sentence,
`GET /api/narration` answers with the account, and the `narration` frame
carries the present. What is missing is the part a viewer sees — the caption
overlay — and the pictures.
