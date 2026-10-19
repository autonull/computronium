Let’s burn the master plan for a moment. If it feels overwhelming, it’s because I gave you a 15-item roadmap when you really just need a single, compelling visual anchor to make the project feel real. 

You are absolutely right to push back on the "no dashboard" advice. In fact, Section 11 of your own vision document explicitly states: *"Screenshots, demonstrations, and eventually the working interface could make the appeal apparent without awkwardly describing it in promotional language."* 

For a project this conceptually dense, a wall of text (even a brilliantly written README) is a friction point. A beautiful, live dashboard showing a campaign queue, resource utilization, and real-time claims being verified is the exact "visible expression" of the system. It turns a scientific engine into a tangible place. A great screenshot or a 15-second panning video of a live dashboard is often the difference between a stranger scrolling past and a stranger clicking "Star" or opening a discussion.

To kill the overwhelm, let's shrink the horizon from "project transition" to **this week's single visual goal**. 

Here is the antidote to overwhelm: **The Hero Image.**

### 1. Wire the existing dashboard to the CLI
The dashboard code (`computronium/experiment/execution/dashboard/web.py`) is already built, but it's hidden. We just need to expose it.
* Add a single CLI command: `uv run comp dashboard --store demo.duckdb`.
* This command should launch the FastAPI server locally on `localhost:8080` and open it in the browser, pointing it at the local DuckDB store so it renders the 4-arm demo data you already generated.

### 2. Style the "Screenshot" moment
You don't need to build out every interactive edge case yet; you just need one breathtaking "Hero View."
* Make sure the HTMX template (`index.html`) has a striking dark-mode aesthetic (deep blues/blacks, glowing monospace fonts for the metrics, clean cards for the campaign queue and cost tracking). 
* Seed it with the exact data from your `demo` profile: the 4 credit arms, the 31-second runtime, the 0.4389 control accuracy, and the `INSUFFICIENT` power verdict. 
* *Goal:* Make it look like a mission control for algorithmic discovery.

### 3. Put it at the very top of the README
Once it looks right, take a high-resolution screenshot.
* Put that image at the very top of `docs/readme/title.md` (which generates the top of the README). 
* Under the image, put a single sentence: *"Computronium is a composable laboratory for learning mechanisms. Watch algorithms battle it out under a neutral, pre-registered evaluation protocol."*

Ignore PyPI. Ignore the consortium pilot. Ignore the lint pass. Ignore the P2P network. 

**Your only job this week is to make the dashboard look incredible, take a screenshot, and put it on the front page.** 

----

Good instinct — and the mockups already agree on a visual language (near-black, amber, monospace, mission-control). What they *don't* agree on is what the dashboard is **for**. Here's the design that makes it the hook *and* keeps it honest.

## The concept: the game is the science

No points, no badges-for-activity. Every "game" element is an existing scientific artifact with a real cost attached, so casual play and rigorous research are the same loop at different budgets:

| Game feel | Scientific artifact (already in the tree) | v1 |
|---|---|---|
| Fog-of-war map | coverage report + declared, priced space (`--dry-run`) | ✅ |
| "Lighting up" a cell | a record lands in the store, with replay hash | ✅ read / v2 write |
| Wander / exploit / surprise-me buttons | your 8 proposal policies (stratified-random, model-based, contrast design) — the slot machine *is* the sampler | ✅ |
| Price tags, budget burn | `PricePlan`, `Deadline`, per-stage timings | ✅ |
| Quests | coverage gaps + `preregistration_template.md` ("adopt" = fill a registration) | list ✅ / adopt v2 |
| Ranks & trophies | verification levels VL1–VL5, `StabilityCertificate`, `DeterminismSeal` | ✅ |
| Leaderboard | the ablation table — **rules ranked, never people**, control arm mandatory, G13 banner if control is at chance | ✅ |
| Patch-notes lore | `CORRECTIONS.md`, `FINDINGS.md` | ✅ |
| Streaks | **deliberately absent.** Replaced by replication count (independent confirmations), because activity ≠ evidence | v2 |

Casual loop (30 s): open the Atlas → see fog → press *wander* → a legal unmeasured cell gets priced → (v2) launch it for ~30 s → it lights up with `n=5`, a chance line, and an honest `INSUFFICIENT — 58 seeds to a claim` → one button: *queue the rest* or *adopt as quest*. That last click is the exact moment a curious newcomer becomes a preregistering researcher. Same artifacts, deeper budget.

## v1 scope: a read-only Atlas (days, not weeks)

One page, four panels, **zero new engine code and zero writes**:

```
┌────────────────────────────────────────────────────────────────────────┐
│ COMPUTRONIUM // ATLAS   STORE: demo.duckdb   MODE: [EXPLORATORY ▾]     │
│ S1→S2→…→[S7 EVALUATING]→…→S11    burn 31s/120s    claim price: 63 seeds/arm │
├─────────────────────────────────────────────┬─────────────────────────┤
│ ATLAS    │ DISCOVERY MAP (fog of war)        │ CELL DRAWER             │
│ EXPED.   │ ● lit = measured (size=n, ring=VL)│ credit=pepita           │
│ RESULTS  │ ○ fog = legal, unmeasured (price) │ 0.542 ±0.072 (n=5)      │
│ CLAIMS   │ ▨ void = illegal combination      │ chance 0.10 · clears    │
│ BESTIARY │ [wander][exploit][contrast][?]    │ INSUFFICIENT → 58 seeds │
│ QUESTS   │                                   │ [queue] [preregister]   │
├──────────────────────────────────────────────────────────────────────┤
│ PLOTTER — figure-spec panels (bars/lines/    │ CLAIMS & CORRECTIONS    │
│ scatter/heatmap), chance line + n/std always │ [L1] pepita … n=5       │
│ LIVE LOG [OK] compose joint system…          │ [—] 4× INSUFFICIENT     │
└──────────────────────────────────────────────┴─────────────────────────┘
```

Why this is fast: the FastAPI+HTMX shell, the Jinja template, the figure-spec renderer (`figure_from_spec`), `RecordStore` queries, coverage and pricing all exist. v1 adds only `dashboard/views.py` — pure functions `store → JSON` (`space_view`, `claims_view`, `run_view`, `figures_view`) — plus four GET endpoints, and renders charts **server-side as SVG/PNG from the existing spec** (no JS chart library). HTMX polls `/api/runs` and `/ws` for the live rail. One acceptance lock: the Atlas's measured set must equal the store's records, so the map can never drift from the evidence — same idiom as `test_demo_script.py`.

## Guardrails (the "still entirely scientific" contract)

1. Every number on screen carries a hover to its record id / replay hash.
2. Chance line on every accuracy plot; rows at chance flagged `[at chance]`.
3. Ablation tables render only for valid contrast groups (your existing lock); otherwise raw cells + a confound banner.
4. Verdicts always show `power_achieved`; `INSUFFICIENT` is never styled as `REJECTED`.
5. A global `EXPLORATORY / PREREGISTERED` mode chip; exploratory claims carry the tag, visibly.
6. The "price of a real answer" line sits in the footer of every comparison view.
7. Knobs are the real priors/search-space declarations — and turning a knob that reaches no cell triggers the **phantom-knob warning in the UI**. The detector becomes a guardrail you can see.
8. Light/dark parity (consortium-mark precedent), colorblind-safe arm palette added to the central `_style.py`.

## Expansion path

- **v2 — Launch & adopt:** knob panel → `RunSpec` preview → dry-run price → queue (same kernel path as `comp run`); quest adoption writes a preregistration JSON; publish toggle = CEEC export.
- **v3 — Federation:** the frozen export schema carries results between nodes; community quest board; replication bounties. Transport decided last, contract first.

And the hero screenshot for the README should show the dashboard mid-campaign with an `INSUFFICIENT` line plainly visible — the image itself demonstrates the honesty claim.


