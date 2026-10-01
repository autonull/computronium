# TODO44.md — Clean Codebase, Canonical README, Experiment Readiness

**Follows:** TODO43.plan3.md (kernel WPs complete; legacy delete was claimed but not executed)
**Binding:** `AGENTS.md` in full. Directives inherited from TODO43: no backwards compatibility, delete wholesale, kernel owns semantics.
**Goal:** A completely clean, organized, usable, demonstrable codebase — then a clean, complete, consistent, coherent, readable, referenceable `README.md` introducing the system to users and developers.

---

## 0. End State (Definition of "Done")

```text
computronium/
├── ontology/  core/  algorithms|primitives/  models/  nn/  state/  training/
├── acceleration/  verification.py  visualization/  stability/  domains/
│                      ← the 6-axis ML library (ACTIVE, unchanged scope)
├── experiment/                 ← the unified Experiment Kernel (ACTIVE)
│   ├── schema/                 RunSpec, Coordinate, Schedule, AXES/OBJECTIVES/PRIORS registries
│   ├── legality/               Expr DSL + engine
│   ├── execution/              SearchSpace, policies catalog, PipelineRunner, stages, ContrastDesign
│   ├── evidence/               RecordStore (DuckDB), artifacts, failure linkage
│   ├── learning/               surrogates, priors, ICU, reasoning
│   └── surface/                CLI (run/report/export/conformance/status), profiles, conformance
├── cli/                        ← thin `comp` adapters; every subcommand works or is deleted
└── (nothing else — no autoscientist/, hyperopt/, execution/, core/campaign/, lightning_/, experiments/)

packages/      ceec-core, psi-peft, local-feedback, stability, computronium-lab (kernel-backed only)
scripts/       quickstart.py, generate_identity_cards.py, probes/, demos/   (nothing else)
tests/         property/  acceptance/  integration/  unit/  platform/  ceec/   (zero legacy imports)
docs/          archive/ (historical TODOs, research notes) + curated reference docs + generated/
repo root      README.md, AGENTS.md, TODO43.plan3.md, TODO44.md, pyproject.toml, uv.lock — nothing else loose
```

**Non-negotiables:**
1. Zero imports of deleted pillars anywhere under `computronium/` (full-tree lock proves it).
2. Every `comp` subcommand either works end-to-end or is removed from the dispatcher.
3. Every README code block is runnable and every README claim is true at its stated strength.
4. All current kernel gates stay green: U1–U5 (8), property locks, atomic-append, conformance audit.

---

## Phase A — Inventory & Classification (WP44.0)

Produce the authoritative keep/delete lists **before** deleting anything. Append results as
Appendix tables in this file so execution never re-derives them.

- [ ] **A1.** Classify every `computronium/` top-level module/dir: `Kernel | Library | Legacy | Orphan | Consumer`.
  Known real legacy-import consumers (from grep, 2026-10-01):
  `cli/` (+`cli/commands/`), `analysis/`, `core/profiling.py`, `stability/calibration.py`,
  `validation/core.py`, `validation/power_preregistration.py`, `visualization/atlas.py`,
  `domains/trainer.py`, `p2p/evolution.py`, `experiments/joint/*`.
- [ ] **A2.** CLI decision table — every entry in `cli/__main__.py::_SUBCOMMANDS` (17 commands):
  `Keep (rewire) | Fold into surface CLI | Delete`. Verify each with `comp <cmd> --help` + smoke.
- [ ] **A3.** Tests importing pillars: 45 files found — delete with pillars unless they lock a
  surviving Library capability (then rewire imports only).
- [ ] **A4.** Root docs: 77 `.md` files, ~40 are `TODO*.md` plans → `docs/archive/`. Root keeps only
  `README.md, AGENTS.md, TODO43.plan3.md, TODO44.md`. Assign every other root `.md`
  (`CAMPAIGN_*.md`, `METHODOLOGY*.md`, `RESEARCH3/4.md`, `DECISIONS.md`, `AUTOTILE.md`,
  `COORDINATE_VOIDS.md`, `PROMPT.md`, …) a topical home under `docs/` or archive.
- [ ] **A5.** Scripts: 63 files → keep `quickstart.py`, `generate_identity_cards.py`,
  `scripts/probes/**`, new `scripts/demos/**`; everything else → `scripts/archive/` or delete
  (one-off audit/commission scripts are dead weight).
- [ ] **A6.** Repo strays: `fix_capabilities_v2.py`, scratch `*.json`, stale `*.db`/`*.sqlite`
  (Directive 3: abandon legacy stores — delete files too, not just neglect), `__pycache__` hygiene.
- [ ] **A7.** `computronium-lab`: only `adaptation.py` imports legacy (`hyperopt.experiment`) —
  rewire to kernel `ModelBasedPolicy` or drop the feature. Lab otherwise stays.

**Gate:** tables A1–A7 filled in Appendix §10 before any deletion.

---

## Phase B — Physical Deletion (WP44.1)

- [ ] **B1.** Delete pillar directories (verified present 2026-10-01, NOT deleted by WP21):
  `computronium/autoscientist/`, `computronium/hyperopt/`, `computronium/execution/`,
  `computronium/core/campaign/`, `computronium/lightning_/`, `computronium/experiments/` (plural,
  pre-kernel layer). Also audit for pillared leftovers: `knowledge/` (kb.sqlite era),
  `autopoiesis/`, `leaderboard/` (stubs), `data/`, `mep/`, `graph/` — classify in A1, delete orphans.
- [ ] **B2.** Delete the 45 legacy-importing test files (A3 list) + orphaned fixtures/conftest refs.
- [ ] **B3.** Move root docs per A4 (`git mv` to `docs/archive/…` preserving history); fix any
  inbound links from surviving docs (`docs/CORRECTIONS.md`, `IDENTITY_CARDS.md`, `CEEC.md` homes).
- [ ] **B4.** Prune scripts per A5; delete strays per A6.
- [ ] **B5.** Update `computronium/_surface.py` / `__init__.py` exports: remove any `__all__`/`_LAZY`
  entries pointing at deleted modules (the import-time `assert_public_surface` will flag them).
- [ ] **B6.** Regenerate `docs/generated/capabilities.json` and rerun the codegen drift lock.

**Gate:** `uv run python -c "import computronium"` succeeds; dispatcher survives (C-phase may
temporarily break subcommands — dispatcher table is fixed in C before the lock test lands).

---

## Phase C — Repair Surviving Consumers (WP44.2)

Real imports only (docstring-only references are B7 cleanup):

| File | Legacy import | Action |
|---|---|---|
| `cli/campaign.py`, `cli/stability.py` | `core.campaign.*` | Delete campaign adapter; `stability` → Library-only report (no store) or fold into surface |
| `cli/continuous.py`, `cli/daemon.py`, `cli/scientist.py` | `autoscientist.*` | Replace with kernel equivalents backed by `PipelineRunner` + policy catalog, **or** delete command; pick per A2 table |
| `cli/frontier.py`, `cli/hpo.py`, `cli/rank.py` | `hyperopt.*` | Same: kernel (`ModelBasedPolicy`/evidence store) or delete |
| `cli/shared.py`, `cli/commands/{search,verify,compare,portfolio}.py` | `hyperopt.*` | Delete (pre-dispatcher legacy subcommands) |
| `analysis/{results,dominance,counterfactual,failure_manifesto}.py` | pillars | Delete module set unless a demo/CI consumer exists → then port minimal helpers into kernel `evidence/` |
| `core/profiling.py` | `campaign.evaluation` (lazy) | Inline the needed helper or delete function |
| `stability/calibration.py` | `campaign.evaluation` (lazy) | Inline helper; keep calibration guard functional |
| `validation/core.py` | `execution._state` FailureTracker/FailureRecord | Port to `experiment.evidence.failure` types or drop legacy path |
| `validation/power_preregistration.py` | `FrontierRecord` | Kernel `evidence` equivalent or delete |
| `visualization/atlas.py` | `autoscientist.objectives` | Use `experiment.schema.registries.OBJECTIVES_REGISTRY` or delete atlas |
| `domains/trainer.py` | `execution._guards` SafetyConfig | Move `SafetyConfig/SafetyWrapper` into Library (`core/` or `training/`) |
| `p2p/evolution.py` | `hyperopt.experiment/search_space` | Rewire to kernel SearchSpace+policy or delete evolution worker |
| `experiments/joint/*` | `campaign.evaluation`, `FrontierRecord` | These produced README campaign records; port trial drivers onto kernel store or delete with pillars |
| `packages/computronium-lab/.../adaptation.py` | `hyperopt.experiment` | Rewire to kernel policy; Lab keeps kernel-backed only |

- [ ] **B7.** Purge docstring-only legacy mentions: `experiment/learning/prior.py:7-9`,
  `core/metrics.py`, `core/training_state.py`, any `computronium/cli/__init__.py` notes.
- [ ] **C-final.** Rationalized `comp` dispatcher: rebuild `_SUBCOMMANDS` from the A2 decision
  table; every retained subcommand gets `--help` + smoke verification recorded in the table.

---

## Phase D — Full-Tree Locks (WP44.3)

- [ ] **D1.** New `tests/property/test_full_import_isolation_lock.py`: AST-scan **all** of
  `computronium/` + `packages/` (not just `experiment/`) for the forbidden pillar prefixes;
  forbid `computronium.experiments` too. Extends, never weakens, `test_kernel_isolation_lock.py`.
- [ ] **D2.** New CLI↔README lock: parse the README CLI table and assert it equals the dispatcher
  `_SUBCOMMANDS` (command set + one-line purpose). Drift fails CI — README stays referenceable.
- [ ] **D3.** Keep `assert_public_surface` green (already validates `__all__`/`_LAZY` and
  README-documented modules resolve).

---

## Phase E — README.md Rewrite (WP44.4)

**Style rules (binding):** accurate at stated claim strength (reuse the 5-level verification
taxonomy; never upgrade Level 4/5 evidence to fact); every code block runnable and locked
verbatim against a test where one exists (existing `<!-- lock: … -->` mechanism); stable
anchors + TOC at top; no dangling links (link-check in D2 or a doc-link lock); consistent
terminology (Coordinate, RunSpec, SearchSpace, Policy, Stage, Record, Claim); developers get
exact commands (`uv run …`), users get copy-paste quickstarts.

**Required outline (section → content):**
1. **What is Computronium** — 2 paragraphs + the three-layer table (ML Library / Experiment Kernel / Scientific Program). Status line: kernel complete, evidence classes recorded.
2. **Install** — `uv sync --dev --all-extras`, Python 3.14, GPU optional; dev-env smoke command.
3. **60-second quickstart** — compose a 6-axis system + train (existing locked block).
4. **The 6-axis ontology** — axis table (S/G/D/P/C/U), composition rules, identity cards link, substrate specs.
5. **The Experiment Kernel** — the new centerpiece:
   - Architecture flow: `Question → RunSpec → SearchSpace → ProposalPolicy → Stages S1–S11 → RecordStore → Claims`
   - Policy catalog table (Synthesis / StratifiedRandom / TPE / NSGA-II / GP / Evolution / TrainerDriven) — differ only in proposal policy
   - Measurement identity, legality, provenance, three-tier status, schema versioning (fail-closed)
   - ContrastDesign + DataOrigin (WP18) in one paragraph
   - U1–U5 guarantees as a table with test pointers (`tests/acceptance/unified_kernel.py`)
6. **CLI reference** — generated-consistent table (D2 lock); kernel ops via surface CLI, library ops via retained adapters.
7. **Demonstrations** — table of `scripts/demos/*` with one-line purpose + expected output (Phase F).
8. **Evidence & claims** — Class E benchmarks table with measured numbers (E2 d=-1.52, E3 d=-1.499, E4 d=-1.519, C1–C88 audit counts), effect-size protocol summary, CEEC governance link.
9. **For developers** — layout map (§0 tree), toolchain (uv/ruff/pyright/pre-commit), testing tiers, commit checklist, how to add an ontology primitive (pointer to AGENTS.md), how to add a kernel policy.
10. **Research program** — motivating hypothesis, open questions, where historical campaign records live (`docs/archive/`).
11. **FAQ/Troubleshooting + Glossary** — include the DuckDB single-writer / cross-process caveat.

- [ ] **E-final.** Reconcile `computronium._surface` README-module validation and `docs/` links;
  delete README claims about deleted features (broad_map dashboard, kb.sqlite, comp scientist legacy flags, etc.).

---

## Phase F — Demonstrable Experiments (WP44.5)

New `scripts/demos/` — each: docstring (what it shows, expected numbers), prints results, exit 0.
Built **programmatically on the kernel** (same APIs as `tests/acceptance/unified_kernel.py`), not via deleted CLIs.

| Demo | Shows | Expected |
|---|---|---|
| `demo_unified_pipeline.py` | U1 end-to-end: question → RunSpec → Synthesis → pipeline → store → report | records persisted, report renders |
| `demo_policy_swap.py` | U4: 4 policies, same RunSpec/Space/Store | identical schema, different search behavior |
| `demo_pause_resume.py` | U3: multi-round, pause, resume by `run_id` | no re-measurement, monotonic seq |
| `demo_multi_objective.py` | Pareto over accuracy/walltime/params via OBJECTIVES registry | non-dominated set printed |
| `demo_cross_policy_reuse.py` | U5: evidence reuse across policies, one store | no migration, same legality/claims |
| `demo_contrast_design.py` | WP18: OFAT/factorial DOE + DataOrigin | known effect recovered |

- [ ] **F2.** Re-run evidence probes post-cleanup: `e3_seeded_axis_effect.py`, `e4_transfer_provenance.py`,
  `conformance_evidence_audit.py` (targets: 46 pass / 42 skip / 0 fail; E3/E4 d≈-1.5, p<0.01).
- [ ] **F3.** `comp gallery --run` re-pin `docs/figures/manifest.json` (accept changed figures; archive stale ones).
- [ ] **F4.** `docs/generated/capabilities.json` regeneration + drift lock green.

---

## Phase G — Environment, Gates & Commit (WP44.6)

- [ ] **G1.** Fix `pyrightconfig.json`: add `"venvPath": ".", "venv": ".venv"` so `duckdb` resolves
  (kills the recurring artifacts/store import errors in IDE + CI).
- [ ] **G2.** `uv sync --dev --all-extras`; dev-env smoke; prune any dependency only legacy used.
- [ ] **G3.** Per-commit checklist (AGENTS.md): ruff format+check changed files, pyright changed
  files, targeted tests — output + walltime shown.
- [ ] **G4.** Round-close gates: full `uv run python -m pytest` (record counts), repo-wide ruff/pyright
  now **in scope** (this IS the hygiene pass), `pip-audit`.

---

## Execution Order

```text
A Inventory ──► B Delete ──► C Repair consumers ──► D Full-tree locks ──► E README ──► F Demos ──► G Gates
                      │                                   │
                      └── B6 regen docs ──────────────────┴── D2 CLI↔README lock feeds E §6
```
Commit per phase (B, C, D, E, F) so any regression bisects cleanly.

---

## 9. Risks

| Risk | Mitigation |
|---|---|
| Hidden importer of a deleted pillar surfaces at runtime (lazy imports) | D1 full-tree AST lock + `grep` gate + import smoke `python -c "import computronium, computronium.cli.__main__"` |
| Gallery/demo code depends on deleted visualization paths | F3 runs gallery before final commit; atlas decision in C is explicit |
| README overclaims | E style rules + existing 5-level taxonomy + `_surface` module check |
| Lost historical context from root-doc moves | `git mv` only; `docs/archive/README.md` index; links updated in B3 |
| computronium-lab breaks | A7 single-file rewire; Lab integration tests in `tests/platform/` gate it |

---

## 10. Appendix — Inventory (filled by Phase A)

<!-- Execution appends: A1 classification table, A2 CLI decision table,
     A3 deleted-test list, A4 root-doc destinations, A5 script dispositions.
     These tables are the authoritative record for Phases B–C. -->

---

## 11. Status

- [ ] Phase A inventory complete
- [ ] Phase B pillars deleted (for real this time)
- [ ] Phase C consumers repaired, dispatcher rationalized
- [ ] Phase D full-tree lock + CLI↔README lock green
- [ ] Phase E README rewritten and locked
- [ ] Phase F demos + probes + gallery green
- [ ] Phase G gates pass, committed