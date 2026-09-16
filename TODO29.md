# TODO29 — Continuous Discovery: Budgeted Bursts, Defect Funnel, Live Atlas

> **STATUS: IMPLEMENTED (2026-09-16, Phases 1–5 landed).** The only open
> item from §12 is the §8 shakedown launch of the 500-cell run through
> `comp continuous` (needs GPU wall-time; operational steps unchanged).
> See §13 for the progress log, mid-flight fixes, and new opportunities.
>
> The philosophy stands: shift from one-shot experiment runs to a continuous,
> time-budgeted discovery loop that harvests defects as data. This revision
> turns that philosophy into a build plan wired to what already exists —
> `AutoScientistCampaign`'s resume/branch/ledger machinery, the TODO28
> stratified sweep and atlas, and the CEEC governed-execution link — and
> rejects the parts of the original sketch that would duplicate or
> contradict them.

---

## 0. Alignment Audit — Idea vs. Codebase Reality

Every element of the original TODO29 sketch, dispositioned against what is
already implemented:

| Original idea | Codebase reality | Disposition |
|---|---|---|
| "Stop-and-resume plumbing needed" | **Proven & shipped**: `CampaignDatabase` (SQLite, git-like branches), `CampaignCheckpointer` (YAML), KB coverage seeding in `StratifiedRandomDriver._reload_covered` — the killed pilot resumed seamlessly from KB coverage (TODO28 §pilot) | **Already exists** — build on it, don't rebuild |
| "Stratified sweep over the ontology" | **Shipped** (TODO28): `StratifiedRandomDriver` balances (dynamics, credit, update) triples; `enumerate_constraint_voids` prunes to the 1111 viable cells of 4158 | **Already exists** |
| "Structural voids ledger" | **Shipped**: `structural_voids.jsonl`, append-only, fully categorized (`classify_void`) | **Already exists** |
| "Per-cell instruments" | **Shipped**: `settle_horizon` (`_SettleTelemetry`), σ_max(J) sampled proxy (`probe_spectral_radius`), `credit_alignment` (`--credit-trace`), `lr`, `param_count` — all flow into KB via numeric-key passthrough | **Already exists** |
| "CEEC pre-registration → execute → record" | **Shipped**: `CEECLink` (pre_register / record / record_failure, never-limbo contract) | **Already exists** |
| "Live dashboard polling artifacts" | **Partial**: `demo/campaign_tab.py` polls commissioned campaign artifacts with a 3 s mtime/size signature timer; nothing watches `kb.sqlite` + the JSONL streams | **Adapt** — new `comp dashboard` reusing the polling pattern |
| Time-budgeted `comp continuous` | Missing. The sweep loop (`broad_mapping_sweep.main`) stops on sample-size/max-iterations only | **Build** (Phase 3) |
| `runtime_defects.jsonl` + quarantine | Missing. `run_iteration`'s broad `except` logs and ledger-fails a crashed cell, but there is no defect stream, no defect ID, no re-propose suppression beyond the KB cover-mark | **Build** (Phase 2) |
| Epistemic maturation (Spark → Survivor → Claim) | Missing. All burst cells are 1-epoch/1-seed with no maturity status | **Build** (Phase 4, minimal) |
| "Fog of War" 6-D grid viz, tectonic ρ(J)=1 frontier | The atlas already delivers the islands/voids narrative; a ρ(J)=1 frontier would chart a *sampled ‖Jv‖ proxy*, not a certified radius — the honesty rules forbid presenting it as the stability boundary | **Defer / reject as specified** (§10) |
| Battery-aware degradation, fuzz fraction, adaptive scheduler | Nice-to-haves; the scheduler is blocked on wall-time not being recorded per cell | **Defer** (walltime lands in Phase 1, enabling later work) |

**Consequence:** the plan is four new modules and one CLI surface — not a
rewrite. Everything else is composition of shipped machinery.

---

## 1. Architecture

```
comp continuous --budget 5m            comp dashboard --root <dir>
        │                                      │
        ▼                                      ▼
  run_burst()  ──uses──► BroadMappingCampaign ──► kb.sqlite
  (budget loop)          (dry-run gate, CEEC,        │
        │                 instruments, resume)       │
        ▼                                            ▼
  runtime_defects.jsonl ──► quarantine state ──► live atlas + defect funnel
  structural_voids.jsonl (existing)              + health gauge + ticker
```

New/changed surfaces:

| Artifact | Role |
|---|---|
| `computronium/autoscientist/broad_map.py` | **New (Phase 1).** Library core extracted from `scripts/broad_mapping_sweep.py`: `enumerate_constraint_voids`, `StratifiedRandomDriver`, `BroadMappingCampaign`, `classify_void`, plus the new `run_burst()` and `ContinuousBudget`. |
| `computronium/visualization/atlas.py` | **New (Phase 1).** Library core extracted from `scripts/visualize_atlas.py`: `load_cells`, `load_voids`, `apply_bp_deficit`, `feature_matrix`, `embed`, `pareto_top`, figure builders. |
| `scripts/broad_mapping_sweep.py`, `scripts/visualize_atlas.py` | Become thin argparse wrappers over the library modules (backwards compatibility: none, per AGENTS.md). |
| `computronium/autoscientist/defects.py` | **New (Phase 2).** Defect ledger: `DefectRecord`, `defect_id()`, `read_defects()`, `quarantined_cells()`, `resolve_defect()`. |
| `computronium/cli/continuous.py` | **New (Phase 3/4).** `comp continuous` — burst runner + `unquarantine` + `deep-tier` subcommands. |
| `computronium/cli/dashboard.py` + `computronium/visualization/live_atlas.py` | **New (Phase 5).** `comp dashboard` — live view, no execution. `--log-path` flag for ticker source. |
| `computronium/autoscientist/campaign.py` | **One edit (Phase 1):** `walltime_s` in `_execute_proposal`'s result dict. |
| `computronium/cli/__main__.py` | Two rows in `_SUBCOMMANDS`: `continuous`, `dashboard`. |

Data stores per campaign root (`artifacts/broad_map/` layout, unchanged):
`kb.sqlite` (coverage + measured cells), `ledger.sqlite` (CEEC),
`structural_voids.jsonl` (gate rejections), `runtime_defects.jsonl` (new),
`campaign/campaign.db` (iteration history), `atlas.html` (rendered on demand).

---

## 2. Phase 1 — Library Extraction + the Walltime Instrument

*Purpose: the daemon, the CLI, the script, and the dashboard must share one
implementation of the sweep and the atlas (DRY), and the adaptive/effort
story needs per-cell walltime recorded.*

1. Move, do not copy: `scripts/broad_mapping_sweep.py` →
   `computronium/autoscientist/broad_map.py` (module docstring keeps the
   epistemic rule and the nohup usage line). Script reduces to argparse +
   `broad_map.main(args)`.
2. Move: `scripts/visualize_atlas.py` →
   `computronium/visualization/atlas.py`. Script reduces to argparse wrapper.
   `comp gallery --generate-broad-demo` (`computronium/cli/gallery.py:
   _run_broad_demo`) keeps working unchanged — it shells out to the script.
3. **`walltime_s`**: wrap `trainer.fit()` in
   `AutoScientistCampaign._execute_proposal` with `time.monotonic()`; add
   `round(dt, 3)` to the result dict. The KB's numeric-key passthrough
   (`_update_knowledge_base` lines 1190–1194 in `campaign.py`) picks it up
   automatically — no further wiring. The atlas gains a compute-efficiency
   spoke (`accuracy / walltime_s`), and the burst log reports per-family
   mean walltime.
4. Tests: existing sweep/atlas tests re-pointed at the library imports;
   `test_campaign_fidelity` green (it exercises `_execute_proposal`).

Verification: `uv run python -m pytest tests/ -k "campaign or atlas or broad" -q`
+ dev-env smoke + ruff/pyright on touched files.

---

## 3. Phase 2 — The Defect Funnel (Crashes as Data)

*Current failure path:* `run_iteration` catches `Exception` per proposal,
`_fail_ledger` closes the CEEC trace ("missing" probe output), the failed
cell is *not* KB-cover-marked, so a code bug can burn budget on the same
broken coordinate every burst, forever.

New module `computronium/autoscientist/defects.py` (strict-typed, frozen):

```python
type DefectId = str                      # sha256[:12]

@dataclass(frozen=True, slots=True)
class DefectRecord:
    defect_id: DefectId
    timestamp: float
    task: str
    cell: str                            # cell_key(dynamics, credit, update, topology)
    error_class: str
    message: str
    traceback_tail: str                  # last ~15 lines
    status: Literal["open", "resolved"]  # "resolved" rows appended on fix

def defect_id(error_class: str, message: str) -> DefectId
def read_defects(path: Path) -> list[DefectRecord]        # replay, last-status-wins
def quarantined_cells(records) -> frozenset[str]          # cells with an open defect
def resolve_defect(path: Path, defect_id: DefectId) -> int  # append resolved row
```

Wiring:

1. **Emission.** `BroadMappingCampaign` overrides the failure branch of
   `run_iteration` (or wraps `_execute_proposal`): on exception after the
   dry-run gate passed, append a `DefectRecord` to
   `runtime_defects.jsonl`, *then* proceed with the existing
   `_fail_ledger` + result-row behavior. The CEEC ledger keeps its
   never-limbo guarantee untouched — the defect stream is a side-channel,
   exactly like `structural_voids.jsonl`.
2. **ID stability.** `defect_id` hashes `error_class + message` with
   `0x[0-9a-f]+` addresses and tmp paths normalized away; tensor shapes and
   layer names are preserved (they discriminate shape-mismatch bugs).
   Same bug → same ID across runs and hosts.
3. **Quarantine.** `StratifiedRandomDriver` gains
   `quarantined: frozenset[str]`, seeded in `_reload_covered` from
   `read_defects().quarantined_cells()`. `propose_batch` skips quarantined
   keys *in addition to* `seen` — distinct sets, so unquarantining a cell
   re-opens it without re-measuring anything else. Quarantine keys on the
   **cell**, not the defect: 45 cells failing on one `DevicePoisoning`
   bug are 45 quarantined cells sharing one `defect_id` — the bug-bounty
   ranking is a group-by the dashboard gets for free.
4. **Unquarantine.** `comp continuous unquarantine --defect <id> --root <dir>`
   appends a `status: "resolved"` row; next burst re-injects the affected
   cells. Append-only JSONL, replay-derived state — no KB mutation, same
   pattern as the voids ledger.
5. **Taxonomy.** A runtime defect is *not* a structural void: voids are
   ontology boundaries caught by the dry-run gate before any budget is
   spent; defects are implementation failures that passed the gate and
   crashed at runtime (the device-poisoning class is the canonical
   example — TODO28 session 3). The atlas renders them differently.

Tests (`tests/property/test_defect_ledger.py`):
- ID stability under address/path randomization (hypothesis).
- Replay: open → resolved → cell unquarantined; ordering by timestamp.
- Suppression: driver with a quarantined cell never proposes it; after
  `resolve_defect`, it can.
- Integration: one injected-failure burst (monkeypatched proposal) produces
  the JSONL row, the ledger "missing" trace, *and* continued execution of
  the remaining proposals.

---

## 4. Phase 3 — `comp continuous`: The Budgeted Burst Runner

```bash
uv run comp continuous --budget 5m --root artifacts/broad_map --credit-trace
uv run comp continuous --target-cells 100 --loop --sleep 10
uv run comp continuous unquarantine --defect a1b2c3d4e5f6
```

`ContinuousBudget` (frozen, slotted, in `broad_map.py`):

```python
@dataclass(frozen=True, slots=True)
class ContinuousBudget:
    started_at: float  # time.monotonic() anchor
    soft_seconds: float | None = None  # stop *starting* new cells past this
    hard_seconds: float | None = None  # abandon loop between cells past this
    target_cells: int | None = None
    done: int = 0

    @classmethod
    def parse(cls, spec: str) -> ContinuousBudget: ...  # "5m", "90s", "1h"
    def soft_expired(self, now: float) -> bool: ...
    def hard_expired(self, now: float) -> bool: ...
    def advance(self) -> ContinuousBudget: ...  # done += 1 (dataclass replace)
```

`run_burst(campaign, driver, budget, *, max_iterations)` — extracted from
`broad_mapping_sweep.main`'s loop:

- **Budget checks at proposal boundaries only.** Never interrupt a
  `train_step`: each cell is independent and KB-flushed on completion
  (`_update_knowledge_base` runs per cell), so a soft stop loses at most the
  in-flight cell's compute — nothing else. Soft expiry = finish the current
  iteration's remaining proposals, then stop starting work. Hard expiry =
  stop between proposals. This is the "loose time limit" from the design
  conversation, made concrete: the run degrades by *granularity of one
  cell*, never by corruption.
- **Precedence:** `--target-cells` is a hard cap; `--budget` is a soft time
  cap. Both can be set; the first limit reached stops the burst.
- On stop: `campaign.save_checkpoint()`, log cells/voids/defects counts,
  exit 0. Cron or `--loop` just calls it again — the KB coverage seed makes
  every burst resume-safe by construction.
- `--loop --sleep N`: in-process loop instead of a shell loop (still one
  fresh `ContinuousBudget` per iteration; `^C` / `SIGTERM` → same graceful
  flush path, handled via `try/except (KeyboardInterrupt, SystemExit)` around
  the loop, *not* in a `finally` — PEP 765). `signal.signal(SIGTERM, ...)`
  registers the same handler for container stops.
- Flags carried over from the sweep: `--epochs`, `--task`, `--seed`,
  `--cells-per-iter`, `--param-budget`, `--credit-trace` (opt-in: one
  flat batch, settle phases + split-half + BP reference — adds settle
  overhead per cell), `--max-iterations`. New: `--budget`, `--target-cells`,
  `--loop`, `--sleep`, `--root`.

**Budget-aware scheduling note (honest scope):** with `walltime_s` recorded
(Phase 1), the burst log reports per-family mean walltime, and the atlas
gains a compute-efficiency spoke. The *scheduler* that compensates
settling-family cost by mixing cheap `instantaneous` cells into a
settling-dominated queue is **deferred** (§10) — the stratified triple
balancer already prevents starvation, which is the failure mode that
matters at burst scale.

Tests (`tests/property/test_continuous_budget.py`,
`tests/integration/test_continuous_burst.py`):
- Budget semantics with an injected fake clock: soft < hard ordering, parse
  errors, target-cells precedence, `advance` immutability.
- One tiny CPU burst on `digits` (2 cells, `--budget 60s`): exit 0, KB rows
  present, second call proposes no already-measured cells, checkpoint
  written. Walltime under the 5-minute foreground cell rule.

---

## 5. Phase 4 — Epistemic Maturation (Minimal Claimable Version)

Burst cells are 1-epoch/1-seed: valid for *mapping topology*, not for
*claims*. Encode that status rather than hoping readers remember it.

- **Tags.** Every burst result enters the KB tagged `maturity:l0` +
  `burst:<utc-date>-<seq>`. (KB entry tags are the natural home; CEEC
  `design` dict additionally records `"maturity": "l0"` at pre-registration
  via `CEECLink.pre_register` — one extra dict key, no schema change.)
- **Promotion query** (`broad_map.promote_candidates(kb, voids, k)`):
  cells on the burst Pareto front (`pareto_top`, reused from the atlas
  module) that have no `maturity:l1` row yet.
- **L1 re-runs.** `--maturation N` reserves up to N cells of each burst for
  promotion re-runs at `epochs=3` (tagged `maturity:l1`). Same cell key,
  fresh execution — the KB already stores per-run rows keyed by
  campaign/iter/cell, so evidence accumulates across levels.
- **L2 deep tier.** `comp continuous deep-tier --top 5 --epochs 10 --seeds 3`
  promotes cells that appeared on a Pareto front in ≥ 2 distinct bursts;
  each seed is a separate pre-registered CEEC experiment (3-seed replication
  is what buys claim status, matching the repo's `quality={"seeds": n}`
  convention). Output: one claim-grade row per cell + `maturation.jsonl`
  summary under the campaign root.
  - `deep-tier` flags: `--top K`, `--epochs E` (default 10), `--seeds S`
    (default 3), `--root`, `--task` (filter), `--dry-run` (show plan only).
- **Variance audit.** The promotion query also flags cells measured in ≥ 2
  bursts whose accuracy spread exceeds 0.2 → `seed_sensitivity` note in
  `maturation.jsonl` (contradictions become findings, not discarded data —
  for a dynamical systems framework, high initialization sensitivity is a
  measurement).

Deliberately *not* built: an automatic pipeline. Promotion is a query run
per burst + one explicit deep-tier command — the human stays in the loop
for claims, which is the CEEC governance model anyway.

---

## 6. Phase 5 — `comp dashboard`: The Live Window

`computronium/visualization/live_atlas.py` + `computronium/cli/dashboard.py`.
Read-only. Runs `uv run comp dashboard --root artifacts/broad_map --port 8088`.

- **Polling pattern stolen from `demo/campaign_tab.py`:** `ui.timer(2.0, poll)`
  with a `(mtime_ns, st_size)` signature over
  `{kb.sqlite, structural_voids.jsonl, runtime_defects.jsonl}`; re-render on
  change only. NiceGUI is already a project dependency (demo), no new dep.
- **Panels:**
  1. *Living atlas* — the islands-and-voids scatter from
     `atlas.embed`/`_islands_figure`. Embedding recomputed only when the
     measured-cell count changes (UMAP re-fit on every 2 s poll is
     wasteful; cache coordinates, debounce).
  2. *Defect funnel* — table grouped by `defect_id`: count, open/resolved,
     last-seen, message head. This *is* the bug-bounty board.
  3. *Health gauge* — open defects, resolved defects, cells/burst rate,
     last-burst walltime. Falls when the daemon hammers a recurring bug;
     recovers as `unquarantine` lands fixes.
  4. *Pareto strip* — current top-3 cells with instrument spokes
     (accuracy, 1−deficit, credit_alignment, settle_horizon).
  5. *Ticker* — tail of the burst log (`logs/continuous-*.log`), last 30
     lines, monospace. The CLI `--log-path` flag (default derived from
     `--root`) points the dashboard at the right file.
- **Gallery note:** HTML/live artifact, not a PNG demo — per TODO28 §
  improvement 3 precedent, no `DEMOS` registry row or manifest re-pin.

Tests: `tests/integration/test_dashboard_smoke.py` — build the app against a
fixture campaign root (tiny KB + JSONLs), assert one render pass produces
the panels without a live loop; change a JSONL, assert the signature
triggers.

---

## 7. Epistemic Rules (carried into the modules' docstrings)

1. **Voids ≠ defects.** Gate-rejected coordinates are ontology boundaries
   (`structural_voids.jsonl`, never ledgered). Gate-passing runtime crashes
   are implementation defects (`runtime_defects.jsonl`, CEEC-failed, cell
   quarantined until the code changes). Neither is a scientific measurement.
2. **Maturity gates claims.** `maturity:l0` rows map the space; only
   `maturity:l2` (10 epochs, 3 seeds, cross-burst stable) rows may back a
   comparative claim. Verification-level framing: burst cells are Level 5
   (empirical, n=1); the deep tier aspires to Level 4 quality (seeds,
   matched controls) — say so in the ledger `quality` fields, per CEEC.
3. **Instruments stay honest.** σ_max(J) remains the sampled ‖Jv‖ proxy it
   is today (`probe_spectral_radius` docstring); the dashboard must not
   market it as ρ(J_F) or a stability frontier.
4. **The ledger only sees gate-passing cells.** Pre-register → execute →
   record/fail, exactly as TODO28 set it. The daemon adds no new ledger
   pathways.

---

## 8. First Campaign — the 500-Cell Run as Shakedown Cruise

TODO28 left the 500-cell production run "execution ready". It becomes
TODO29's shakedown: launch it *through* the new loop once Phases 1–3 land,
instead of a monolithic 2–4 h run:

```bash
# AGENTS environment rules: background, streaming log, ≤2-min polls
nohup uv run comp continuous --target-cells 500 --credit-trace \
    --root artifacts/broad_map --loop --sleep 15 \
    --log-path logs/continuous_500.log \
    > logs/continuous_500.log 2>&1 &
```

Expected outcome per the TODO29 thesis: every crash the 500-cell run would
have hit is now a quarantined defect row + a continuing run; the walltime
instrument measures the real per-family cost profile; and the first
`unquarantine` cycles are the defect funnel's acceptance test.

---

## 9. Verification Gates

Per-commit (AGENTS checklist): dev-env smoke → `ruff format` + `ruff check
--fix` on changed files → `pyright` (strict: `broad_map.py`, `defects.py`,
`continuous.py`, `atlas.py`, `live_atlas.py` are new modules) → targeted
tests shown above.

**Targeted test commands per phase:**
```bash
# Phase 1: library extraction + walltime
uv run python -m pytest tests/ -k "campaign or atlas or broad" -q

# Phase 2: defect funnel
uv run python -m pytest tests/property/test_defect_ledger.py -q
uv run python -m pytest tests/integration/test_continuous_burst.py -q

# Phase 3: continuous budget + CLI
uv run python -m pytest tests/property/test_continuous_budget.py -q
uv run python -m pytest tests/integration/test_continuous_burst.py -q

# Phase 4: maturation
uv run python -m pytest tests/integration/test_continuous_burst.py -k "maturation" -q

# Phase 5: dashboard
uv run python -m pytest tests/integration/test_dashboard_smoke.py -q
```

Fast gate at round close: demo/gallery-adjacent (`gallery.py` now imports
the moved atlas path indirectly via the script) — run
`uv run python -m pytest tests/integration/ -k "demo or gallery_lock" -q`
+ the property suite. Full suite only at round close, per AGENTS.

Wiring locks: no ontology primitives are added, so the dynamics wiring
lockstep lock is untouched — assert it stays green in the round-close run.

---

## 10. Explicitly Deferred (with reasons)

| Item | Reason |
|---|---|
| "Fog of War" 6-D grid visualization | The UMAP atlas already carries the islands/voids narrative; a bespoke 6-D grid is a second frontend for the same KB. Revisit only if the atlas demonstrably fails to answer a question. |
| Tectonic ρ(J)=1 frontier plot | Only a sampled ‖Jv‖ proxy exists; charting it *as* the stability boundary violates the instrument-honesty rules. Waits on σ_max certification (TODO28 §improvement 5). |
| Adaptive scheduler (cost-compensated mixing) | Needs accumulated `walltime_s` data first; the stratified balancer prevents starvation meanwhile. Revisit after the 500-cell campaign. |
| Adversarial fuzz fraction (`--fuzz-fraction`) | Contradicts the constraint-map budget discipline unless fuzz cells are quarantined from the viability enumeration; design it *on top of* the defect funnel once defect taxonomy stabilizes. |
| Battery/graceful-degradation OS hooks | Cute, no evidence of need; `--loop` + cron covers the operational story. |
| Surrogate-guided proposals | Bypassed by design since TODO28 (stratified mapping); reintroducing the surrogate is a separate research question, not a continuous-mode prerequisite. |
| P-axis 6-D grid expansion, ntm device defect, diffusion at more epochs | Unchanged TODO28 deferrals — bigger coverage/robustness work items, not continuous-mode blockers. |

---

## 11. Risks & Open Questions

- **Concurrent bursts on one KB.** SQLite write contention if two daemons
  share `--root`. Mitigation: single-daemon assumption documented in
  `continuous.py`; optional lockfile (`<root>/continuous.lock`, `O_EXCL`)
  if it ever bites in practice.
- **UMAP re-fit drift.** `random_state=0` is pinned, but re-fitting on a
  growing set moves *all* points; the dashboard should label the map
  "layout recomputed at n=…" to avoid implying trajectories. (The static
  atlas PNG has the same property today — pre-existing, noted.)
- **Defect ID collisions on generic messages.** `ValueError: expected 2D`
  from two unrelated bugs could hash equal. Acceptable: quarantine is
  conservative (over-blocking), and `unquarantine` is one command. If
  collisions annoy, add the first traceback frame to the hash.
- **CEEC ledger growth.** One pre-registration per cell, forever appending.
  Fine for the ledger's purpose; `ceec` tooling already reports rollups.

---

## 12. Immediate Next Actions (in order)

1. **§8 production run — READY** — launch the endless 500-cell run (§13
   session 4 "Ready-state" command: `--target-cells 500 --limit-batches 30
   --loop --sleep 15`), watch it on `comp dashboard`, fix-and-`unquarantine`
   as defects surface.
2. **Adaptive scheduler revisit (§10)** — per-family mean `walltime_s`
   (already logged per burst, and now cheap to accumulate at
   `--limit-batches` scale) is the cost-compensated scheduler's input;
   design on top of `run_burst`'s summary dict.
3. **Defect ID hardening (§11)** — if the funnel shows collisions on
   generic messages, add the first traceback frame to `defect_id`.
4. **Faulthandler noise (§13 session 2b)** — `test_demo_ntm_local` (~3 min)
   trips the 2-min `faulthandler_timeout` on every demo-gate run; silence
   it per-test before it trains operators to ignore real crash dumps.
5. **Optional lockfile (§11)** — only if concurrent bursts on one root
   ever bite (`<root>/continuous.lock`, `O_EXCL`).
6. **Multi-task maturation** — `promote_candidates`/`deep-tier` accept a
   `--task` filter; per-task Pareto fronts within one KB are the natural
   next step if multi-task sweeps resume.

---

## 13. Progress Log (2026-09-16)

### Landed (Phases 1–5)

| Phase | Delivered |
|---|---|
| **1 — Library extraction** | `computronium/autoscientist/broad_map.py` + `computronium/visualization/atlas.py` are the single implementations; `scripts/broad_mapping_sweep.py` / `scripts/visualize_atlas.py` are thin argparse wrappers (gallery shell-out unchanged). `walltime_s` (monotonic around `trainer.fit()`) rides the KB numeric-key passthrough; the radar gains an `acc/walltime` spoke. |
| **2 — Defect funnel** | `computronium/autoscientist/defects.py` (`DefectRecord`, `defect_id` sha256[:12] with address/tmp-path normalization, `read_defects`, `quarantined_cells` replay, `resolve_defect`, `append_defect`). `BroadMappingCampaign._execute_proposal` wraps the base executor dry-run-aware — gate rejections stay voids, gate-passing crashes become defects *then* the CEEC trace closes (never-limbo untouched). Driver gains `quarantined` seeded from the JSONL; `comp continuous unquarantine` re-opens cells. |
| **3 — Budgeted bursts** | `ContinuousBudget` (frozen/slotted, `parse("5m")`, soft/hard/target, immutable `advance`) + `run_burst` in `broad_map.py`: budget checks at proposal-batch boundaries only, the final batch is *trimmed* to the target cap (no overshoot), a 3-empty-iteration streak distinguishes gate-rejected batches from true exhaustion, checkpoint on stop, per-family mean walltime in the log. `computronium/cli/continuous.py` wires `--budget/--target-cells/--loop/--sleep/--log-path` + `_SUBCOMMANDS` row; SIGTERM/^C share one graceful flush path (no `finally` returns, PEP 765). |
| **4 — Maturation** | Burst proposals tagged `maturity:l0` + `burst:<utc-date>-<seq>` (`next_burst_tag`); proposal tags now propagate into KB entries; CEEC `design` records `maturity`. `promote_candidates` (front via `atlas.pareto_top`, void-excluded, l1/l2-suppressed) + `--maturation N` L1 re-runs at epochs=3. `comp continuous deep-tier --top --epochs --seeds --dry-run`: front-stable-across-≥2-bursts cells re-executed per seed as separate CEEC experiments; claim-grade rows + `seed_sensitivity` variance audit land in `maturation.jsonl`. |
| **5 — Live window** | `computronium/visualization/live_atlas.py`: headless `DashboardSnapshot` render (funnel, health, Pareto strip, ticker, islands figure via `EmbedCache` — UMAP re-fit only when the cell count changes, honesty caption on the layout) + `build_dashboard` (NiceGUI, `ui.timer` poll on the (mtime,size) signature of kb/voids/defects). `computronium/cli/dashboard.py` = `comp dashboard --root --port --log-path --poll`, read-only. |

Tests: `tests/property/test_defect_ledger.py` (7), `tests/property/test_continuous_budget.py` (17),
`tests/integration/test_continuous_burst.py` (5, includes L1 promotion + deep-tier scan/dry-run),
`tests/integration/test_dashboard_smoke.py` (5). All green; ruff + pyright clean on every touched file.

### Mid-flight fixes (each exposed by the new machinery)

- **pyproject/ruff skew (blocked every gate):** ruff 0.16.6 rejects bare
  pylint-style rule names (`line-too-long`, …) in `ignore` lists and no
  longer honors the legacy `# ruff: ignore[...]` directives. Selectors
  rewritten to codes; dead directives converted to working `# noqa:`
  on touched lines only (canonical migration stays Register C).
- **KB entry-id collision (silent data loss):** `_update_knowledge_base`
  built entry ids from a second-resolution timestamp; two cells completing
  in the same wall-clock second hit `INSERT OR REPLACE` and one result
  vanished. Ids are now cell-key-unique (the rev-7 fix's knowledge-entry
  half — the experiments-table half existed already).
- **`enumerate_constraint_voids`** now creates the voids file's parent
  dirs (library callers don't pre-mkdir).
- **`atlas.embed`** falls back to t-SNE on UMAP crashes from broken
  optional GPU stacks (test conftest stubs `cupy` as a `MagicMock`), and
  scales t-SNE perplexity below the sample count for small maps.
- **`docs/IDENTITY_CARDS.md`** regenerated (PCALMCredit card drifted since
  the pre-TODO29 PC-ALM commits); drift lock green again.

### Changes that facilitate the remaining work

- `build_sweep(args)` is the one construction path shared by the sweep
  script and the CLI — new instruments only wire once.
- `run_burst`'s summary dict (completed/failed/stop_reason/walltime means)
  is the adaptive scheduler's ready-made input.
- `_load_measured_cells`/`_Candidate` (typed frozen dataclasses with burst
  and maturity provenance) are the shared read path for maturation and the
  dashboard; walltime now rides along.
- `DashboardSnapshot` decouples panel data from NiceGUI — the whole
  dashboard is testable headless.

### Session 2 hardening (2026-09-16, post-landing verification)

Re-ran the per-phase gates after landing; they exposed four items, all fixed:

- **`--loop` branch had zero test coverage:** the interrupt clause used
  PEP 758 tuple syntax (`except KeyboardInterrupt, SystemExit:` — legal on
  Python 3.14, the toolchain target, but not on 3.13-), so a regression
  there could never be caught. Fixed as an explicit tuple and locked in by
  `test_loop_smoke_exhaustion_and_sigterm` (exercises exhaustion-stop, the
  SIGTERM handler, and the graceful-flush path) +
  `test_budget_parse_and_target_precedence`.
- **Ruff 0.16 preview-rule inversion:** the preview rules `RUF105`
  (`noqa-comments`) and `RUF201` (`rule-codes-in-selectors`) now fire on
  exactly the forms the mid-flight fix migrated *to*. Both added to the
  `pyproject` ignore list alongside RUF100/RUF103 — the canonical
  directive/selector migration remains Register C work; pick one canonical
  form then and delete both ignore rows.
- **PLW0717 (`too-many-statements-in-try-clause`)** on `continuous` and
  `live_atlas`: extracted `_loop_bursts`/`_burst_once` (SIGTERM/^C path now
  guards a single call) and `_atlas_data`/`_load_atlas` in
  `live_atlas.py` — which also resolved a latent name collision with the
  NiceGUI container renderer of the same name (pyright
  `reportRedeclaration`).
- Verified: the 34 targeted tests (defect ledger, budget, burst, dashboard)
  green; ruff + pyright clean on all six new/changed modules.

### Session 2b — pre-experiment follow-ups (2026-09-16)

- **`--loop` smoke tests added** (`tests/integration/test_continuous_burst.py`):
  `test_loop_smoke_exhaustion_and_sigterm` (fake-clock bursts: exhaustion
  ends the loop; SIGTERM mid-loop takes the graceful-flush path, exit 0) +
  `test_budget_parse_and_target_precedence`. Targeted suite now 36 green.
- **CLI surface audit before the shakedown:** `_deep_tier`'s non-dry-run
  construction path validated against `AutoScientistCampaign`/`CEECLink`
  contracts (kwargs correct; `output_dir`/`CampaignDatabase`/ledger all
  self-create parents, so the campaign-before-`mkdir` ordering is safe).
  `_unquarantine` returns 1 on unknown/already-resolved ids — intended.
- **Round-close fast gate green:** demo/gallery 29 passed (11:25) +
  property suite 1214 passed / 12 skipped / 25 xfailed.
- **Cosmetic (opportunity):** `test_demo_ntm_local` runs ~3 min and
  trips the suite's 2-min `faulthandler_timeout` — every demo-gate run
  prints a scary native traceback that is *not* a failure. Raise
  `faulthandler_timeout` for that test (pytest.ini marker/`timeout`-style
  opt-out) or trim the probe; otherwise operators will chase ghosts.

### Session 3 — shakedown (2026-09-16, 12-min budget cap)

Launched `comp continuous --budget 12m --credit-trace` against the existing
TODO28 root; stopped early via SIGTERM. Results and fixes:

- **Working:** resume seeding (36 known cells reloaded, 34→37 measured),
  voids gate (561 new void rows, 3611 total), CEEC traces, `walltime_s`
  instrument flowing into the KB (540 s / 324 s / 138 s on the three
  completed cells), checkpoint files, `unquarantine` CLI (exit 1 on unknown
  id). Defect funnel stayed empty — zero gate-passing crashes.
- **Fixed: SIGTERM was loop-only.** Without `--loop` no handler existed —
  SIGTERM killed the process instantly, skipping the "Interrupted" log and
  any flush. `_install_sigterm()` now runs in `_burst` for all modes, and
  the interrupt `except` wraps the whole burst (extracted `_run_burst`).
  Resume-safety was unaffected (KB coverage seed), but the graceful path is
  now uniform.
- **Fixed: file logger was deaf.** Handlers attached to loggers named
  `"broad_map"`/`"continuous"` while the modules log under
  `computronium.*` — the `--log-path` file only ever got content via the
  shell's stderr redirect. Handler now attaches to the root logger.
- **Cost finding (major):** credit-trace cell walltimes are 138–540 s →
  a 500-cell `--credit-trace` run is ~19–75 h, not the 2–4 h estimate.
  The §8 production run should either drop `--credit-trace` (instruments
  except credit_alignment/settle_horizon still ride the numeric
  passthrough) or accept a multi-day run. Per-family cost data now
  accumulates in the KB for the adaptive scheduler.
- **Budget granularity (spec consequence):** soft expiry finishes the whole
  current iteration — at `--cells-per-iter 10` × minutes/cell a 12-min
  budget overshoots by ~40 min. Acceptable for daemon use; if it bites,
  trim the batch per proposal (cells are independent and KB-flushed).
- **Data-quality gap:** 2 of 3 cells recorded `final_loss: NaN` at
  chance-level accuracy (NaN losses already visible mid-training in the
  trainer log). A NaN-loss policy (defect tag? instrument? rejection?) is
  un-designed — the funnel only catches crashes, not silent NaN runs.
  Candidate follow-up: tag `maturity:l0` entries with `nan_loss` in
  the KB and let the atlas/dashboard surface them.

### Session 4 — NaN policy, shorter cells, dashboard live (2026-09-16)

- **NaN policy implemented.** `_execute_proposal` emits a numeric
  `nan_loss` flag (non-finite val_loss or val_acc) that rides the KB
  passthrough into entry metrics + the experiments table, plus a
  `nan_loss` entry tag. `_CellRow.nan_loss` carries it to every consumer:
  `promote_candidates` and `_deep_tier_candidates` per-burst fronts exclude
  diverged cells, the dashboard Pareto strip filters them, and the health
  gauge gained a "diverged (NaN)" card. Bonus fix the test exposed:
  `promote_candidates` crashed on an all-diverged KB (empty frame into
  `pareto_top`) — guarded.
- **Shorter cells: `--limit-batches N`.** New
  `SystemTrainerConfig.limit_train_batches` (epoch stops after N batches),
  wired CLI → driver hyperparams → trainer config; 0 = full epoch.
  Verified live: **25 cells in 4 min** (`--limit-batches 30`, no
  credit-trace; ~12 s/cell, per-family mean 3.9–32.7 s) vs 3 cells in
  19 min with the old settings — ~40× throughput for L0 mapping.
- **Shakedown 2 (4-min budget):** burst stopped cleanly on hard budget
  ("25 measured cells, 0 failed runs, 3616 voids, 0 defects"), per-family
  walltime logged, KB + checkpoint flushed. Dashboard rendered headless
  against the real root: health (46 rows, 3 diverged), funnel, Pareto
  strip (NaN-free), islands figure, ticker — no errors.
- **Ready-state:** the pipeline is production-ready for an endless run.
  Recommended launch (L0 mapping; add `--credit-trace` only if the
  alignment spokes are needed and multi-day walltime is acceptable):
  `nohup uv run comp continuous --target-cells 500 --limit-batches 30
  --loop --sleep 15 --root artifacts/broad_map
  --log-path logs/continuous_500.log > logs/continuous_500.log 2>&1 &`
  Then `uv run comp dashboard --root artifacts/broad_map --port 8088`.
- **Dashboard made actually usable (session 4 fixes, each found by real
  HTTP smoke):**
  - `resolve_log_path` crashed at runtime (`Path` was TYPE_CHECKING-only)
    and only searched `<root>/logs/` while the daemon writes repo-level
    `logs/` — now checks both homes, newest wins, so the default ticker
    is deaf no more.
  - NiceGUI's auto-index page needs script-mode re-execution, which fails
    under a console-script entry point (HTTP 500 on every request) — the
    dashboard now registers an explicit `@ui.page("/")`.
  - First paint blocked ~40 s on the UMAP fit — the page now paints the
    cheap panels immediately, computes the atlas off-thread
    (`run.io_bound`), and swaps it in with a "pending" placeholder.
    Verified: `GET /` returns 200 in ~4 s with the full chrome.
  - `--no-open` flag added (browser auto-open by default for desktop use).

  The one-liner anyone can run from the repo root:
  `uv run comp dashboard` (defaults: `--root artifacts/broad_map
  --port 8088`, opens a browser).
