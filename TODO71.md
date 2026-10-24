# TODO71: The Dashboard, Arranged — Bindings as Data, Docks, Workspaces, and a Door for Every Verb

**Objective**: Make the dashboard's chrome easy to use, modular, flexible,
organized — in the service of the purpose the README states for it. The
dashboard exists to *watch algorithms battle it out under a neutral,
pre-registered evaluation protocol*, and the kernel's outer flow closes
with *evidence → next question*. TODO70 made the dashboard an instrument;
this TODO arranges the instrument so that both halves of its purpose —
the watching and the loop — are one switch and one palette away.

**Source**: the reader's request, in four words:

> Consider if the Dashboard's UI can be redesigned, more: easy to use,
> modular, flexible, organized

verified against `README.md` (the system's statement of purpose), and
sharpened by four defects found on inspection:

- `main.ts:157-168` dispatches cell verbs on `r`, `p`, `q` — but the key
  chain claims all three first (`rail = r`, `pareto = p`, `legend = q`), so
  **the branches are unreachable**. The keys have never worked.
- `help-overlay.ts:53-59` advertises them anyway. The help lies.
- `test_dashboard_keys_lock.py` reads `keys.ts`'s own lists only, so the
  lock cannot see a collision with a dispatcher branch or a view key.
- `main.ts:98-105` builds `TAB_BY_KEY` and `PANEL_BY_KEY` beside a registry
  that already answers `byKey` — two lists for one question, and they have
  already disagreed.

**Key Decision**: The chrome becomes **data**, and the loop becomes the
**organizing principle**. Every binding, panel, view, workspace and dock
placement is declared once, and every consumer — the dispatcher, the rail,
the toolbar, the help, the palette, the lock test, the tour — reads that
declaration. Around that data, the screen is organized by what the reader
is *doing* — watching a campaign, auditing its evidence, driving the run —
because that is how the README already describes the dashboard, and the
chrome should speak the README's language.

---

## System purpose, verified

The README is the statement of purpose; this table verifies that the
redesign serves it, line by line, and names the phase that secures each.

| The README says | The dashboard's answer | Secured by |
|-----------------|------------------------|------------|
| "Watch algorithms battle it out under a neutral, pre-registered evaluation protocol" | the stage and the caption; the neutrality instruments — the ledger's verdicts, the arms' evidence, the claim's cost in seeds, the margin on every mean | the views exist and are untouched; Phase 4 gathers them under *the evidence* and *the judgement*, so the protocol's picture is one section of the toolbar |
| The outer flow: "🔁 evidence → next question" | the loop's verbs: start a run, replicate a cell, preregister a claim, adopt a cell as a quest, the queue | built in TODO70; Phase 3 makes them one palette group — *the next question* — so the loop is visible as a loop and drivable with no letter |
| "start a run from nothing" | the control panel's New run section | Phase 3's first-run door: an empty store names the door in the caption, and the palette's top entry is *start a run* |
| "It says what it is doing in words … so a reader who sees only the picture can follow it" | the caption and the narration API — shape, not figures | untouched; the help and the palette render from the binding layer, so the words cannot lie (Phase 0 fixes the lying help) |
| "an instrument, not a picture … reaching the run rather than a picture of it" | the control bar, the control panel, the control plane | TODO70's work, untouched below the chrome; Phase 2 docks the bar, Phase 3 exposes its verbs in the palette |
| "the panel rail says which panels are open" · "the legend's toolbar holds every view at once" | the rail and the view toolbar | kept; Phase 4 renames the toolbar's groups to the README's own section names, so toolbar, tour and README describe the same stage in the same words |
| "See the dashboard guide … for the endpoints, the keyboard shortcuts, and how the pictures are made" | `docs/DASHBOARD.md`, the tour, the README pictures | Phase 6 re-takes the pictures, rebuilds the README in the same commit |
| "Six commands, no second document" — the start-here philosophy | the dashboard must explain itself the same way | the palette is the dashboard's `--help`, and the help renders from the binding layer — one source, nothing to drift (Phases 0 and 3) |
| The four audiences: scientists, ML researchers, hardware researchers, systems engineers | three ways of using one screen | the **workspaces** (Phase 2): *watch* — the campaign as it happens; *audit* — the evidence and the judgement; *drive* — the instrument. Each is one arrangement, remembered |
| "The system has more pictures than the dashboard shows" | out of scope — adding views is gallery work | what this TODO owes is **cheap arrival**: Phase 4 makes the next view one file plus one registry row |

**What the verification found missing.** Two gaps, and the plan is
architected around both:

1. **The chrome was organized by kinds; the purpose is organized by
   tasks.** Docks and registries make the parts modular, but a reader
   arrives with a *task* — watch this run, judge this evidence, drive
   this machine — and today must arrange a dozen panels by hand for
   each, every session. The workspaces close this: three named
   arrangements, one switch.
2. **The loop was reachable but not visible.** The verbs of
   *evidence → next question* exist (TODO70), but nothing on the screen
   says they are one loop. The palette's *next question* group and the
   first-run door close this: the loop becomes a list, and the empty
   store points at its first step.

**What is deliberately untouched.** The control plane, the endpoints, the
narration sentences, the views' drawings, the store. TODO70's instrument
works; this TODO arranges its chrome. No new endpoints — the server's
verbs are already complete.

---

## The gap, stated plainly

The TODO70 dashboard is a working instrument with a handmade chassis. The
registries are right; everything that hand-wires around them is not.

| What exists | Where | What it is |
|-------------|-------|------------|
| A component lifecycle | `src/components/registry.ts` | init/destroy in dependency order, health checks |
| A panel registry + the rail | `src/panels.ts` | every popup individually toggleable; one place answers "what is open" |
| A view protocol | `src/stage/views.ts` | `enter/exit/refresh/ready`; six groups; glyph toolbar |
| One keys list | `src/keys.ts` | the budget, the punctuation reserve, the property lock |
| A chart pattern | `plotter.ts:195` | `createChartPanel(chart: ChartSpec)` — already spec-driven |
| The control bar + panel | TODO70 | play/pause/step/stop, the ceiling, the meter; new-run, this-run, queue, cells, exports |

What the four words ask for, and what is missing:

| The word | What is missing | Evidence |
|----------|-----------------|----------|
| **Easy to use** | A way to find a verb without memorizing its letter. Twenty-six letters spent, punctuation begun (`,` = slices); twenty-five views, eleven panels, five sections — and no discovery surface beyond the help overlay, which lies (above) | `keys.ts:39-46` |
| **Easy to use** | A screen that matches the task. Watching, auditing and driving are three arrangements of the same dozen panels; today each is arranged by hand, every session | no workspace concept; `localStorage` is used nowhere |
| **Modular** | A declarative layer. `index.html` is 16 lines (a canvas and an empty div); every panel builds its DOM by `createElement` + `innerHTML` strings, with 43 inline `cssText` blocks across 13 files; styling lives in three places | `templates/index.html`; `grep cssText src/` |
| **Modular** | One file, one thing. `stage/dynamics.ts` holds 8 views in 836 lines (elsewhere: one view per file); `stage/state.ts` mixes ~20 payload types, 8 fetchers, and notification in 840 lines; `control-panel.ts` builds 5 sections in one class; `switcher.ts:84-110` hardcodes 25 constructors | file sizes |
| **Flexible** | A layout grammar. Twelve panels each fix their own `position: fixed` coordinates; the `#chart-column` exists because three 300-px panels don't fit beside the HUD; no docking, no persistence | `grep "position: fixed" src/` — 12 sites |
| **Organized** | A taxonomy the README agrees with. The toolbar groups views by kind (`space/analysis/process/dynamics/trained/multi`, `views.ts:12`); the README describes them by purpose — the run, the evidence, the judgement — so the toolbar and the README disagree about what the views are for | `views.ts:12` vs `docs/readme/dashboard.md` |
| **Organized** | Registries that hold what arrives. Views cannot self-register the way panels do; cell verbs travel as stringly `window.dispatchEvent` events (`main.ts:158-166`); the help re-lists keys by hand | `switcher.ts` constructor list |
| **Honest** | Keys that do what they say. The `r/p/q` branches are dead and the help names them | the four defects above |

---

## Current State

| Piece | Path | Lines | Note |
|-------|------|-------|------|
| The 3D map | `src/discovery-map.ts` | 1262 | the stage's first view; owns the legend |
| The charts | `src/plotter.ts` | 1065 | three panels from one `ChartSpec`; ids `plotter-{tab}` |
| The stage state | `src/stage/state.ts` | 840 | types + fetchers + notification, in one |
| Eight views | `src/stage/dynamics.ts` | 836 | the one-file-many-views outlier |
| The control panel | `src/control-panel.ts` | 681 | five sections, one class |
| The cell drawer | `src/cell-drawer.ts` | 643 | the three cell verbs live here |
| The control bar | `src/control-bar.ts` | 553 | polls `/api/control` at 2 Hz |
| The switcher | `src/stage/switcher.ts` | 479 | toolbar, keys, and a 25-view constructor list |
| The HUD | `src/hud.ts` | 376 | meters in the 3D scene |
| Everything else | `src/` + `src/stage/` | ~5,600 | panels, views, helpers |
| The styles | `templates/static/css/dashboard.css` | 934 | organized; the inline `cssText` beside it is not |
| The tour | `scripts/capture_dashboard_tour.py` | — | 43 pictures; the browser's acceptance mechanism |

The tour couples to: DOM ids `dashboard-canvas`, `caption-headline`,
`discovery-legend`, `legend-axis-picker`, `panel-rail`, `view-strip`,
`plotter-{tab}`, `plotter-{tab}-chart`, `[data-_tour-wrapper]`; and the
debug handle `__DASHBOARD__` (`plotter.showTab`, `controlBar.togglePlay`).
**This list is the compatibility contract**; a rename updates the tour in
the same commit or it is not a rename.

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│  src/bindings.ts — the one list of what the reader can do            │
│    Binding: id · label · group · key? · chord? · when? · run()      │
└──────┬──────────────┬───────────────┬──────────────┬───────────────┘
       │ read by, and only by:
       ▼              ▼               ▼              ▼
  the dispatcher  the panel rail  the help       the command palette
  (one, in main)  (panels.ts)     (rendered)    (src/palette.ts)
       ▲
       └── and by the tour: __DASHBOARD__.bindings.list() hands the
           same table to any agent, so a verb is never scraped from help
┌────────────────────────────────────────────────────────────────────┐
│  src/shell.ts — the panel shell                                      │
│    panel({ id, title, dock, glyph, key?, body }): header · × · body  │
│    markup declared in each panel's module; static style in css       │
└──────────────────────────────┬─────────────────────────────────────┘
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│  src/layout.ts — the docks and the workspaces                        │
│    docks: top strip · bottom strip · left column · right column     │
│           · floating                                                │
│    workspaces: watch · audit · drive · free — each one data row     │
│    { view, open panels, dock order }; a manual change makes it free  │
└────────────────────────────────────────────────────────────────────┘
```

### What this is not

| Not this | Why not |
|----------|---------|
| A framework (React, Vue, lit) | a render layer buys re-render the dashboard does not need; the DOM is small and mostly static, and the tour photographs real ids |
| Freeform drag-and-drop | a desktop metaphor over a full-screen 3D canvas; the reader wants the map big, not the panels arranged |
| A reskin | `palette.css` is generated and untouched; this TODO moves chrome, not colour |
| New server endpoints | the server's verbs are already complete (TODO70); this TODO makes them findable |
| A behaviour change | the default screen and every verb's effect are pinned by the tour, which runs after every phase |

### The binding layer — the one new idea

`src/bindings.ts` holds every key the reader can press, as data, in one
table with a stated order. The dispatcher in `main.ts` walks that table;
the rail's tooltips, the help overlay, and the palette render it; the
property lock parses it. `keys.ts` stays as the budget's ledger —
`PUNCTUATION_KEYS`, `FREE_KEYS` — but `PANEL_KEYS`, `TAB_KEYS` and
`CONTROL_KEYS` become derived from the table rather than maintained
beside it.

| Alternative | Why not |
|-------------|---------|
| Keep three lists in `keys.ts` and maps in `main.ts` | that is the design that produced the dead `r/p/q` branches and the lying help |
| Generate the help by hand, forever | it has already drifted from the dispatcher once |
| A hotkey library | the table is ~40 rows and a dispatcher is 20 lines; a dependency buys a config format, not correctness |

**The cell verbs lose their keys.** `r`, `p`, `q` stay with the rail, the
Pareto chart and the legend — they were there first, and the cell verbs'
branches never fired. The verbs become palette entries that act on the
selected cell (disabled, with the reason, when none is), beside the drawer
buttons and the Cells section that already work. **No verb loses its
reach; three dead letters gain their honesty.**

**The table is also the agent's.** `__DASHBOARD__.bindings.list()` returns
`{id, label, group, key}` for every binding, so the tour generates its
key-press shots from the table and any agent can enumerate the dashboard's
verbs without scraping prose. TODO70 made every verb callable without a
browser; this makes them enumerable without one.

### The panel shell

`src/shell.ts` builds every panel the same way: a header with a title and
a `×`, a body the panel's own module declares (template literals — the
DOM is small and mostly static; the tour reads real ids). Static styling
moves into `dashboard.css` as one class taxonomy; the 43 inline `cssText`
blocks go; only genuinely dynamic values — meter levels, trace points —
set `element.style`.

The shell also sets the chrome's accessibility once: a panel's title is
its `aria-label`, its close button carries its own (it already does), and
focus moves to the panel's header when it opens. The narration already
speaks in sentences; the chrome it labels should be no less legible to a
reader who cannot see the picture.

| Alternative | Why not |
|-------------|---------|
| A framework (React, Vue, lit) | a render layer buys re-render the dashboard does not need; the tour photographs real DOM ids |
| Keep `createElement` + `cssText` | restyling means editing TypeScript; a panel's look is scattered across three languages |

### The layout grammar — and the workspaces

Five docks — a top strip, a bottom strip, a left column, a right column,
and floating — and one `LayoutManager` in `src/layout.ts` that owns
coordinates, z-order, and membership. A panel declares its preferred dock
and its default openness; **the default placement table reproduces
today's screen exactly** (the tour photographs before and after in the
same commit to prove it). The `#chart-column` becomes the right dock — a
region that holds any panel, not a special case for charts.

**A workspace is one row of layout data** — `{the view on the stage, the
panels that are open, their dock order}` — read by the same manager, not a
second layout system. Three ship, plus the reader's own:

| Workspace | For | Arrangement |
|-----------|-----|-------------|
| **watch** | "watch campaigns in real time" — the headline use | today's default screen, exactly as a fresh page shows it |
| **audit** | the evidence and the judgement — what the run can say | watch, with the ledger view on the stage and the three charts open |
| **drive** | the instrument — the verbs, the queue, the flow | watch, with the flow view on the stage and the control panel open |
| **free** | whatever the reader arranged | remembered; any manual change after a preset moves to *free* |

Switching is one action: a `watch · audit · drive` segmented control on
the control bar, and entries in the palette. **No letter keys** — the
alphabet is spent, and a workspace is not a letter's worth of meaning.
`layout.reset()` restores *watch* and the default docks. Persistence is
`localStorage`, versioned (`computronium.layout.v1`: workspace, view,
open panels, dock order); a version bump clears it; the tour calls
`layout.reset()` before every shot set.

| Alternative | Why not |
|-------------|---------|
| No workspaces (today) | three audiences, three tasks, one hand-arranged pile — the reader pays the arrangement cost every session |
| Workspaces as a second manager | a workspace is a row the existing manager reads; there is nothing to drift |
| CSS grid areas in the stylesheet | docks are runtime membership, not stylesheet layout |

### The command palette and the first-run door

The palette opens on **`:`** (shift-`;` — the punctuation reserve loses
`;`; `keys.ts` says so). It fuzzy-matches the binding table, the views,
the panels, and the cell verbs; Enter runs; Esc closes. It is the honest
answer to the exhausted alphabet: **a new surface gets a palette entry,
not a letter.**

The palette's groups put the loop first:

| Group | Holds |
|-------|-------|
| **the next question** | start a run · replicate the selected cell · preregister a claim · adopt a cell as a quest · the queue |
| **workspaces** | watch · audit · drive · free · reset |
| **views** | all twenty-five, in the six sections |
| **panels** | all eleven |
| **verbs** | play/pause · step · stop · help |

The palette is a focus-trapped dialog: arrows navigate, Enter runs, Esc
closes, and every entry's label doubles as its accessible name. A cell
verb without a selected cell is disabled with the reason — the honesty
rule TODO70 set for controls, applied to the palette.

**The first-run door.** When the store holds no run, the void view and
the caption name the door: the control panel's New run section, one `z`
or one palette entry away — and the palette's top entry on an empty store
is *start a run*. Shape, not figures; the narration rule holds.

### The view taxonomy — the README's sections

The toolbar's groups become the README's own section names, so the
toolbar, the tour and the README describe the same stage in the same
words — and a section of the README is a run of the toolbar:

| Group | Views | The README's words |
|-------|-------|--------------------|
| **the space** | space, layers, slices, multi-run | "the space it is searching" · "the space cut into sheets" · "two runs in one space" |
| **the run** | terrain, frontier, matrix, convergence | "the same run, drawn four ways" |
| **the evidence** | small multiples, spread, claim-cost, uncertainty | "the run's evidence, four ways again" |
| **the process** | timeline, flow, effect | "the run's cells as they went through the pipeline" |
| **the judgement** | ledger, contrast | "the run as a process, and as a judgement" |
| **the system** | trajectory, spectrum, basin, landscape, the four trained views | "the system itself, rather than its bookkeeping" |

The glyph grammar stays by *kind* (solids for the 3D views, marks for the
flat ones) — a glyph says what a view is drawn with; a group says what it
is for. `ViewGroup` (`views.ts:12`) becomes these six; the tour's shot
list and the README's picture tables adopt the same order in Phase 6.

### The registries for what arrives

- `stage/registry.ts` — views self-register, the way panels already do;
  the switcher's 25-constructor list dies; `dynamics.ts` splits into
  eight files, one view each, matching the convention everywhere else.
  **Cheap arrival is the point**: the next view is one file plus one
  registry row, and nothing else moves.
- The charts — `plotter.ts:195` already builds panels from a `ChartSpec`;
  the spec becomes a registry row. A chart is its file plus its row.
- `control-panel.ts` becomes a shell hosting five section modules —
  new-run, this-run, queue, cells, exports — each registered.
- `src/verbs.ts` — the cell verbs become typed calls one function owns;
  the drawer, the Cells section, and the palette all call it;
  `window.dispatchEvent(new CustomEvent(...))` is gone.

### The store, split

`stage/state.ts` becomes three modules: `payloads.ts` (the interfaces),
`store.ts` (`StageState`: absorb, setAxes, onChange, recomputeEvidence),
`sources.ts` (the eight `sync*` fetchers). Views subscribe to the store;
no view imports a fetcher.

---

## Phases

### Phase 0: The binding layer

**Goal**: one list of what the reader can do, and one place that hands out
its keys.

1. `src/bindings.ts` — the `Binding` record and the table, in a stated
   precedence order.
2. `main.ts` — delete `TAB_BY_KEY`, `PANEL_BY_KEY`, the inline chain, and
   the dead `r/p/q` branches; one dispatcher walks the table.
3. `keys.ts` — `PANEL_KEYS`/`TAB_KEYS`/`CONTROL_KEYS` derived from the
   table; the budget bookkeeping stays.
4. `help-overlay.ts` — the shortcut groups render from the table; the
   hand-written list is deleted.
5. `tests/property/test_dashboard_keys_lock.py` — parses the table **and**
   every view's `key` field; a key claimed twice anywhere fails; the
   free-key list is what `keys.ts` says.
6. `__DASHBOARD__.bindings.list()` — the table, readable by the tour and
   any agent.

**Acceptance**: every key in the repo does exactly one thing; the help
names exactly the bindings that exist; the lock test fails on a
deliberately duplicated key; the tour can enumerate every verb from the
handle.

### Phase 1: The panel shell

**Goal**: panels declare what they are; the shell says how they look.

1. `src/shell.ts` — `panel({ id, title, dock, glyph, key?, body })`,
   registering with the panel registry so the rail works unchanged.
2. Each panel's markup moves to its own module as template literals;
   static style moves to `dashboard.css`; the `cssText` blocks go.
3. The DOM ids do not change (the compatibility contract, above).
4. The shell sets the chrome's accessibility once: titles as
   `aria-label`s, focus to the header on open.

**Acceptance**: `grep cssText src/` finds only dynamic-value sites; the
tour's existing pictures still pass.

### Phase 2: The layout grammar and the workspaces

**Goal**: the screen has regions; panels live in them; a task is one
switch.

1. `src/layout.ts` — the five docks and the `LayoutManager`.
2. Panels declare preferred dock + default openness; the default placement
   table reproduces today's screen; the tour photographs before/after.
3. The `#chart-column` becomes the right dock.
4. `localStorage` persistence, versioned; `layout.reset()`, called by the
   tour before every shot set.
5. The three workspaces as data rows in `layout.ts`; the segmented
   control on the control bar; palette entries (Phase 3 wires them).

**Acceptance**: no panel positions itself; a fresh page equals today's
default; a reload restores the workspace; switching is one action and
restores the named arrangement; a manual change makes the state *free*
and persists; `reset()` restores *watch*; docks never push the map —
they overlay or hold.

### Phase 3: The palette and the first-run door

**Goal**: every verb reachable without a memorized letter, and the loop
visible as a loop.

1. `src/palette.ts` — `:` opens; fuzzy over the binding table, views,
   panels, cell verbs; the groups as specified, *the next question*
   first; Enter runs; a cell verb without a selected cell is disabled
   with the reason; focus-trapped, arrow-navigable, Esc-closable.
2. `keys.ts` — `;` leaves the punctuation reserve; the list says so.
3. The empty dashboard names the door to a first run — the void view and
   the caption, in shape, not figures; the palette's top entry on an
   empty store is *start a run*.

**Acceptance**: every verb is ≤2 actions from anywhere with no letter;
the loop's five verbs sit in one group; the palette works from an empty
store; the tour gains palette and empty-store shots.

### Phase 4: The registries and the taxonomy

**Goal**: what arrives registers itself; consumers keep no lists; the
toolbar speaks the README's language.

1. `stage/registry.ts` — views self-register; the switcher consumes;
   `dynamics.ts` becomes eight files.
2. The `ChartSpec` registry — a chart is its file plus its row.
3. `control-panel.ts` → a shell + five section modules.
4. `src/verbs.ts` — typed cell verbs; the stringly events are gone.
5. `ViewGroup` becomes the six README sections (the table above); the
   tour's shot list and `docs/readme/dashboard.md`'s tables adopt the
   group order in Phase 6.

**Acceptance**: adding a view, chart, or section touches its own file and
one registry row; `grep "new CustomEvent" src/` is empty; the toolbar's
six sections carry the README's names; the tour passes.

### Phase 5: The store, split

**Goal**: views read state, not transport.

1. `stage/payloads.ts` — the interfaces.
2. `stage/store.ts` — `StageState` and its change notification.
3. `stage/sources.ts` — the eight `sync*` fetchers.
4. `state.ts` is deleted; one commit per file; the tour runs after each.

**Acceptance**: no view imports a fetcher; behavior unchanged.

### Phase 6: The tour, the help, the docs

1. The tour calls `layout.reset()` before shot sets; gains palette,
   empty-store, workspace, and dock shots; its shot list is ordered by
   the six sections; every id and `__DASHBOARD__` method in the
   compatibility contract keeps working.
2. `docs/DASHBOARD.md` — the binding layer, the docks, the workspaces,
   the palette, the registries, the new taxonomy.
3. `docs/readme/dashboard.md` — the palette, the workspaces and the
   docked screen, in pictures; the picture tables re-ordered by the
   group names, so every README section names its group; **the README is
   rebuilt in the same commit** (`test_readme_build_lock.py`).

**Acceptance**: the tour is green end to end; the README lock is green;
the README's dashboard section and the toolbar agree, word for word.

---

## Risks

| Risk | Mitigation |
|------|------------|
| A rename silently breaks the tour | the compatibility contract is listed in Current State; a rename updates the tour in the same commit |
| The palette becomes a second help that drifts | both render the one binding table; there is nothing to drift |
| Docks change the default screen | the default placement table reproduces today's screen; the tour photographs before and after in the same commit |
| Persistence makes the tour nondeterministic | the tour calls `layout.reset()`; storage is versioned and cleared on bump |
| The binding table grows a duplicate again | the lock test parses the table and every view key; a duplicate anywhere fails CI |
| The workspaces become a second layout system | a workspace is one row the same manager reads; there is no second system to drift |
| The group renames churn the README | the new names *are* the README's own section titles; the pictures are re-taken and the tables re-ordered in the same commit, and the README lock runs |
| The store split breaks a view mid-move | one commit per file; the tour runs after each |
| The chart registry over-builds | three charts ship through it, and the lock's fixture contains the case the registry exists for (a fourth chart arrives as data or the registry is a comment) |
| The letters run out again | they already have; the palette is the answer, and the remaining reserve (`, . / '`) is stated in `keys.ts` |
| The redesign changes behavior by accident | the default screen and every verb's effect are pinned by the tour, which runs after every phase |

---

## Definition of Done

- [ ] One binding layer; every key claimed exactly once; the lock test
      parses it and every view's key, and fails on any duplicate
- [ ] The dead `r/p/q` branches are gone; the cell verbs are reachable
      from the drawer, the Cells section, and the palette
- [ ] The help renders from the binding table; no hand-written key list
      remains anywhere
- [ ] The binding table is readable by the tour
      (`__DASHBOARD__.bindings.list()`), and the tour's key shots are
      generated from it
- [ ] No static inline `cssText`; the shell supplies the panel chrome, and
      the chrome's accessibility is set once
- [ ] Every panel is placed by the layout manager into a dock; no panel
      fixes its own position
- [ ] The default layout reproduces today's screen; a reload restores the
      workspace; `layout.reset()` restores *watch*
- [ ] The three workspaces ship; switching is one action from the control
      bar or the palette; a manual change makes the arrangement *free*
- [ ] The palette opens on `:`, is a focus-trapped dialog, and reaches
      every verb — the research loop's five verbs in one group — without
      a memorized letter
- [ ] An empty dashboard names the door to a first run
- [ ] Views self-register; `dynamics.ts` is eight files; the switcher
      holds no constructor list
- [ ] The control panel is five section modules
- [ ] The cell verbs are typed calls; no stringly `CustomEvent` remains
- [ ] `state.ts` is payloads/store/sources; no view imports a fetcher
- [ ] The toolbar's groups are the README's sections; the tour's shot list
      and the README's tables share the order
- [ ] The tour is green with the new shots; the README is rebuilt in the
      same commit

---

## Where the work stands

| Piece | State |
|-------|-------|
| Phase 0 — the binding layer | ✅ |
| Phase 1 — the panel shell | ⬜ |
| Phase 2 — the layout grammar and the workspaces | ⬜ |
| Phase 3 — the palette and the first-run door | ⬜ |
| Phase 4 — the registries and the taxonomy | ⬜ |
| Phase 5 — the store, split | ⬜ |
| Phase 6 — the tour, the help, the docs | ⬜ |
| The property suite's pre-existing failures (carried from TODO70) | ⬜ carried — Register C hygiene, unrelated to this work |
