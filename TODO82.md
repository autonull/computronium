# TODO82 — From Laboratory to Evidence to Institution

**Status of `main` at writing:** v1.0.0. The library, the six-axis ontology, the kernel, the demo,
the dashboard, the DuckDB evidence store, the neutrality apparatus (fairness contract, pre-registered
thresholds, identity cards, corrections log), and the CI gates are all real and locked.
**No campaign has been run yet** (README, *Kernel status, stated plainly*). Install is `git clone`;
Computronium is not on PyPI.

> Computronium is a complete instrument that has never measured anything.

## How to read this plan

**Priority order is the document order.** §0 (runnable preliminary system) outranks everything;
Releases 1.1/1.2/2.0 follow. Evidence remains the critical path after §0. Every item cites
provenance: **[T81]** = TODO81 remaining, **[README]** = README, **[T66]** = TODO66 §8, **[T46]** =
TODO46, **[R]** = repo inspection 2026-11-06. The document supersedes TODO81; TODO81 stays as the
record of how the kernel was built.

---

## 0. Phase 0 — Runnable Preliminary System (do first)

**Goal:** a system the owner can launch for 30–60 minute preliminary tests on this machine
(16 cores, RTX 3080 10 GB, 31 GB RAM), with low-effort optimizations applied before handover, and the
faster candidate generation measured rather than assumed.

### 0.1 Low-effort optimizations (in dependency order, each independently verifiable)

| ID | Item | Effort | Verification |
|---|---|---|---|
| P0-1 | **`harvest_schema()` cache** — `@lru_cache(maxsize=1)`; called 68 times per repo, 5+ per run | ≤15 min | `HarvestedSchema` is frozen; `active()`/`by_name()` return fresh objects; unit test or smoke confirms no shared-mutation leak |
| P0-2 | **Compile void constraints in `iter_candidates`** — reuse (or extract) the `_compile_expr` lambda compiler used by `_filter_axes_for_validity`; delete the DSL interpreter loop (`evaluate`) from the scan hot path | ≤1 hr | Parity spot-check: compiled vs interpreter agree on ≥10k random selections; property suite green; dry-run identical cell counts |
| P0-3 | **`_composable` cheap pre-filter** — skip `compose_configs()` when a compiled void predicate already rejects; keep full check for survivors | ≤1 hr | Same cell stream with/without pre-filter is identical; walltime per scan reported |
| P0-4 | **Batch `RecordStore.append`** — buffer 10–50 records per transaction | ≤1 hr | Kill-safe append test (existing kill-proof suite) stays green; row count/order unchanged |
| P0-5 *(judgment call)* | **No larger refactors before handover** — sampler arc, validation codegen, one-runner convergence all wait for Phase 1 | — | — |

**Not done before handover:** B5 gate calibration, B10 codegen, B12 SimpleSurvey convergence (all
Phases 1–2). The preliminary system is the current pipeline, validated and fast — not a rewrite.

### 0.2 End-to-end verification on this machine

1. Dev-env smoke: `uv run python -c "import optuna, scipy, torchvision, pytest"`
2. Short run (~3 min budget): `./experiment_shallow.sh 0.05 --policy random`
3. Measure: walltime per cell, cells/hour, worker saturation, store row count, report renders
4. Longer confirmation (~30 min): `./experiment_shallow.sh 0.5 --policy random`
5. Adaptive spot check: `SKIP_DOCTOR=1 ./experiment_shallow.sh 0.1 --policy tpe --dry-run` (dry-run),
   then a timed 0.5 h TPE run if the smoke run is clean

Record timings in `docs/preliminary_testing.md` (create); every claim in the guide cites a measured
number from this machine, not an estimate.

### 0.3 The exact commands (handover guide)

```bash
uv sync --dev --all-extras
uv run python -c "import optuna, scipy, torchvision, pytest"   # dev-env smoke

# Preliminary tests — both complete unattended:
./experiment_shallow.sh 0.5 --policy random     # 30 min · sampler control (deterministic ordering)
./experiment_shallow.sh 1.0 --policy tpe       # 60 min · adaptive (Optuna TPE)

# Inspect results:
uv run comp status --store experiment.duckdb
uv run comp report --store experiment.duckdb --format text
uv run comp report --store experiment.duckdb --format html
```

(Filenames: `./experiment_shallow.sh` writes `experiments/experiment_<ts>.duckdb`; confirm and
document actual path, it is machine-generated.)

### 0.4 What preliminary runs can and cannot say

- **Can:** uncover crash/freeze/deadlock bugs, measure throughput and per-cell walltime, sanity-check
  that gate verdicts, store writes and reports work, produce *ballpark* rankings for planning
  (exploratory, `n=1` cells).
- **Cannot:** publish or validate any comparison; rank algorithms; support a claim. One cell per
  coordinate, one domain family, small budget = pure exploration. `[at chance]` rows and
  `[unpreregistered_claim]` labels will appear — they mean exactly what they print.
- For anything claim-shaped, wait for Phase 1 (H1–H6 at `n ≥ 3`, pre-registered).

### 0.5 Exit criteria (Phase 0 done ⇒ handover)

- [ ] P0-1…P0-4 committed; property suite green; demo gate green; dry-run cell counts unchanged
- [ ] 0.5 h run completes on this machine; walltime/cell and cells/hour recorded in
      `docs/preliminary_testing.md`; report renders for the produced store
- [ ] Guide covers: install, smoke, the two commands above, how to read the report, the
      "cannot claim" warning box
- [ ] `TODO82` updated: Phase 0 items carry dates + timings; any deviations recorded

**Cost estimate:** ≤ one focused session for P0-1…P0-4 + verification; 30–60 min of compute for
§0.2; guide ≤ 1 hr. Nothing in Phase 0 changes semantics — only speed and certainty.

**In-flight work:** P0-1 (harvest_schema cache) and P0-2 (compiled `iter_candidates` void checks +
`_compiled_void_constraints()` shared with `_filter_axes_for_validity`) are drafted and uncommitted
in `git stash@{0}` ("in-flight low-effort optimizations…"). Apply, verify parity, commit.

---

## 1. Principles that govern this plan

1. **Runnable before ambitious.** A system the owner can execute outranks any refactor; Phase 0
   exists because v1.0.0's claim ("runs unattended") was never executed.
2. **Evidence before features.** No new primitive, panel, or command while zero powered evidence
   exists; the campaign outranks conveniences, after Phase 0.
3. **One evaluation path.** Two front doors (`--mode static` / default LearningSurvey) is a
   temporary fork, not a design. Convergence: Release 1.1 (B12).
4. **Codegen over hand-sync.** Validation generated from the registries; every rule in two places
   is a bug (we fixed one this session — `system.py` vs `seed_registries.py` on nonlayered
   geometries). Release 1.1 (B10).
5. **Fail closed, label loudly.** Unsupported schema → error. Unregistered claim → **refused**, not
   merely labelled (Release 1.2, C1).
6. **Neutrality is the product.** Equal-effort HPO, blinding, pre-registration move from protocol to
   kernel invariant (Release 1.2, C1–C3).
7. **De-scope ruthlessly.** §7 lists what we explicitly will not do.
8. **Hygiene is continuous, not a phase.** Register C → 0, repo-wide pyright, `pip-audit` ride every
   release; never the milestone.

---

## 2. Honest baseline (what exists / what does not)

**Exists and locked:** ontology (57 primitives), kernel (11 stages, 8 policies), 48 objectives
(all but two measured), store (schema v3, fail-closed versioning), claims with verification levels,
ablation tables gated on shared-five-axes, `[at chance]` flags, positive-control requirement,
pre-registration labelling, identity cards (`--strict`), corrections log, demo (7 beats), dashboard,
CI gates (property suite, demo gate, vertical slice, drift locks, version consistency), DuckDB
evidence store, determinism locks.

**Does not exist (the gaps that matter, in order):**

| Gap | Evidence |
|---|---|
| A runnable, timed 0.5–1 h preliminary run on the owner's machine | Never executed — Phase 0 |
| A single measured comparison | README: "No campaign has been run yet." |
| H1–H6 verdicts (the motivating hypotheses) | T81 Step 7 — blocked on full runs; blockers fixed; **never run** |
| PyPI / Docker / versioned releases | `pyproject.toml` is `1.0.0`; git-clone install [R] |
| Pre-registered Class E claim **refused** when unregistered | [README] neutrality gap 4 — labelled, not refused |
| HPO parity enforced by `comp run` | [README] neutrality gap 2 — protocol + `biopl-hpo`, not invariant |
| Blinded arm labels | [README] neutrality gap 3 — unbuilt |
| CEEC in the claim path | `ceec_link` always `None` [R] |
| Cross-domain evidence | [README] neutrality gap 5 — one task family (vision, digits-class) |
| ~650 lint findings (Register C); repo-wide pyright not clean | [T66] §8; `BASELINE = 659` |

---

## 3. The plan after Phase 0 — three releases, dependency-ordered

### Release 1.1 — *The Laboratory Runs* (numbered work, post-handover)

**Goal:** unattended, reproducible, powered runs; first H1–H6 verdicts; the gate is calibrated.
**Theme:** make evidence *affordable and believable*.

#### A. Evidence (the critical path — immediately after Phase 0)

| ID | Item | Source |
|---|---|---|
| A1 | **Full smoke run** — `./experiment_shallow.sh 0.05 --policy random`, then `0.5`; verify walltime, cell counts, gate verdicts, store writes, report output end-to-end | Phase 0 §0.2 (verification *is* A1) |
| A2 | **Sampler control vs adaptive** — static vs learning mode marginal rankings on identical budget; publish both reports verbatim | T81 §11 (step 3) |
| A3 | **H1–H6 triage at n ≥ 3** — six motivating hypotheses, powered; verdicts carry `power_achieved`, seeds, limitations; underpowered cells are `INSUFFICIENT`, never "no effect" | T81 Step 7 |
| A4 | **First pre-registered comparison artifact** — credit × update on digits, OFAT, registered thresholds, positive control passing, report in `docs/experiments/` (or released artifact) | [README] |
| A5 | **Update `docs/FINDINGS.md`** if anything survives audit; otherwise record the null result honestly — both are the brand | docs/FINDINGS.md |

#### B. Instrument correctness & efficiency (locks carried from v1.0.0 review)

| ID | Item | Notes |
|---|---|---|
| B5 | **M1 — gate calibration** — sensitivity/specificity of train/val gate vs held-out cells; publish calibration curve | [T66] (spec first: ≤1 page) |
| B6 | **M2 — drift detection** — alert on NaN rate / walltime collapse / identical val_acc vs same-spec priors | [T66] |
| B7 | **M3 — metric coverage warnings** — refuse silently-empty report sections; print measured vs untouched objectives | [T66] |
| B8 | **`capabilities` command** — machine-readable capability registry dump; lock against it | [T66] |
| B9 | **Finish the sampler arc** — delete candidate-list `propose()` (TODO46 §3.4 remainder); **policy-aware compatibility sampling** | [T46]/[T66] |
| B10 | **`SystemConfig.validate` codegen** — generate validation from registries; delete hand-maintained whitelists; test registry ↔ codegen ↔ validate agree | [T66] |
| B11 | **CEEC in the claim path** — populate `ceec_link`; Class E claim carries ledger hash or `[ceec_absent]` | [T66]/[R] |
| B12 | **One evaluation path** — fold `SimpleSurvey` behind `--deterministic` (or `uniform_random` + fixed seed); delete the execution fork | T79/T81 |

*Phase 0 closed P0-1…P0-4 (former B1–B4); they are not repeated in 1.1.*

**v1.1 acceptance:** A1–A3 done; A4 published; B5 specified; B9 merged; `CONTRIBUTING.md` added
(run gates + the never-`pytest tests/` discipline); release notes; `uv run comp run demo` green on a
clean checkout.

---

### Release 1.2 — *The Evidence Generalizes* (neutrality becomes enforceable)

**Goal:** claims are refused when unregistered; HPO parity is an invariant; evidence beyond digits.

| ID | Item |
|---|---|
| C1 | **Pre-registration enforced** — Class E claims refuse without matching registration; `[unpreregistered_claim]` survives only for Class A–D |
| C2 | **Blinding** — arm labels hashed to A/B/C for analysis; unblinding is a logged, separate step |
| C3 | **HPO parity invariant** — `comp run` verifies equal trials/budget across contrasted arms; violations refuse publication or stamp `[hpo_asymmetry]`; fold `biopl-hpo` into the kernel |
| C4 | **7-domain expansion, incremental** — vision first (`cifar10` done; add `cifar100`, `svhn`), then language (`wikitext2`/`penn_treebank`), RL (`cartpole` done; `mountain_car`/`lunar_lander`), tabular (`diabetes`, `california_housing`), time series (`ett_h1`). **Each task ships its own chance line, positive control, identity-card audit before any contrast is published** |
| C5 | **Cross-domain transfer test** — top credit × update cell on digits, frozen, re-run on `cifar10` + `tiny_shakespeare`; report transfer delta with CIs |
| C6 | **Cross-substrate robustness** — same cell `digital` vs `memristive` (simulated): does ranking hold under noise/IR-drop/bounded precision? |
| C7 | **Default replication** — `n_seeds ≥ 3` floor for claim-bearing fidelity; single-seed runs labelled `[n=1, exploratory]` |
| C8 | **Fair-HPO recovery study** — re-tune each zoo algorithm under equal effort; publish delta vs published numbers; needs C3 + compute; calibrate cost on one algorithm family first |
| C9 | **M2 drift gates in CI canary** — fast nightly seeded canary; failure pages, never merges |
| C10 | **Error-message pass** — every refusal names the rule; catalogue in `docs/errors.md` |

**v1.2 acceptance:** C1–C3 enforced and tested (a deliberately unregistered claim is refused in a
test); C4 delivers ≥2 new tasks with full control protocol; C5 published; C8 protocol drafted;
release notes; PyPI `computronium==1.2.0`.

---

### Release 2.0 — *The Consortium* (evidence becomes infrastructure)

**Goal:** someone who is not us can use this to produce a claim we will print.

| ID | Item |
|---|---|
| D1 | **Distribution** — PyPI, Docker image (CUDA + CPU), `CHANGELOG.md`, semver discipline, version lock extended |
| D2 | **Ten-minute path** — onboarding rewritten around **RunSpec YAML + `question_first()`**; spec-first tutorial; 5 worked YAML examples in `examples/`; retire CLI-flag archaeology in `docs/experiments/` |
| D3 | **API reference** — generated API docs complete; one-line contract + example per public symbol; README blocks locked to tests |
| D4 | **Consortium pilot** — one bounded question (credit × update on vision), three independent labs, pre-registered, published with corrections log |
| D5 | **Public record** — provenance-hashed run registry; public corrections log; `comp benchmark-contrib` seeded with the pilot; admission = identity cards `--strict` on the contributor's implementation |
| D6 | **Adoption kit** — FAIRNESS_CONTRACT as standalone spec; pre-registration templates; fork-and-run guide (protocol is the contribution, not the code) |
| D7 | **Docs IA** — README stays a map (≤600 lines); depth moves to `docs/`; per-audience landing pages audited |
| D8 | **Release signing & provenance** — signed artifacts; `comp export --docker` + `comp repro --docker` reproduction; **fix `docs/experiments/reproducibility.md`** (it cites non-existent `export --format docker`; `--format` is json/parquet, `--docker` is the flag) |

**v2.0 acceptance:** D1 published; D2 passes on a clean VM; D4 signed off (or honestly reported
failed); D5 public; ≥1 external contributor record in the store.

---

## 4. Continuous engineering (rides along; never the milestone)

| ID | Item |
|---|---|
| E1 | **Register C paydown** — 650 findings → 0; ratchet only downward |
| E2 | **Repo-wide pyright** — finish Register C type work; strict on new modules |
| E3 | **`pip-audit` clean** — verify; add to CI as advisory then gate |
| E4 | **CI stays** — property suite + demo gate + vertical slice + drift locks; never `pytest tests/`; shards are round-close only |
| E5 | **Determinism across platforms** — document CPU/GPU/BLAS variance; golden digests for the demo store |
| E6 | **Dependency diet** — audit `uv.lock` annually |

---

## 5. Architecture decisions embedded in this plan (do not re-litigate)

1. **LearningSurvey is the runner**; `--mode static` survives only as the Phase 1 B12 shim.
2. **Validation is generated, not hand-maintained** (B10); audit residue = a test proving registry ↔
   codegen ↔ `SystemConfig.validate` agree.
3. **The store is the source of truth**; reports are re-derived views.
4. **CEEC is mandatory for claims, optional for exploration** (B11).
5. **Fidelity ladder does work**: L0 screens, L1 confirms, L2 publishes; a claim never cites L0.
6. **SimpleSurvey dies** (B12). No third runner.
7. **Docs move out of README** as they stabilize; README links, doesn't contain.
8. **Phase 0 changes speed only** — no semantic changes before handover; semantics land in Phases
   1–3 under their acceptance criteria.

---

## 6. Success metrics (falsifiable; checked per release)

| Release | Metric | Target |
|---|---|---|
| Phase 0 | `./experiment_shallow.sh 0.5 --policy random` completes on this machine | unattended, report renders |
| Phase 0 | Guide accuracy | every command executed verbatim, output matches doc |
| 1.1 | Walltime to first report on clean machine | ≤ 15 min |
| 1.1 | H1–H6 verdicts with `power_achieved` and seeds | 6/6 issued, zero "no effect" language |
| 1.1 | Published A4 artifact | exists, reproducible from store hash |
| 1.2 | Unregistered Class E claim in CI | refused, test proves it |
| 1.2 | New tasks passing full control protocol | ≥ 2 |
| 1.2 | `pip install computronium` | works |
| 2.0 | External reproduction of a record | ≥ 1, acknowledged in corrections log |
| any | Register C findings | strictly decreases per release |

---

## 7. Explicitly de-scoped (binding unless a partner appears)

- **A real TUI** — web dashboard covers the interaction surface; a TUI splits maintenance.
- **Ray / SLURM / DDP at scale** — single-node must be routine first.
- **PDE scientific suite** — after the seven domains are characterized.
- **Physical-hardware validation** — requires a lab partner; simulation honesty stays in the README.
- **"Computronium found a better algorithm"** — not a milestone; a powered, pre-registered
  comparison is.
- **New axes / new primitive families** — ontology grows only through the checklist.
- **Multi-tenant SaaS / hosted campaigns** — pip/Docker distribution only.
- **`vmap` full multi-seed** — orthogonal; file as issue, not plan.

---

## 8. Risks and open questions

1. **Powered comparisons are expensive** — 63 seeds/group for d=0.5; `comp power-analysis` prices
   every claim before launch. Mitigation: one hypothesis per week, report each, never batch.
2. **Rankings may not replicate hardware** — that is *why* C6 exists; publish with the caveat.
3. **The reference implementations are ours** — consortium replication (D4) outranks adding benchmarks.
4. **Ontology drift vs simplicity** — B10 codegen keeps legality honest; the editorial burden is
   real; budget it.
5. **Preliminary-run misread risk** — an owner may mistake Phase 0 timings for “it’s fast enough
   to publish”; the guide’s warning box (§0.4) exists for this.
6. **Single-maintainer bus factor** — D2/D7 reduce onboarding; keep AGENTS.md current.
7. **Open questions for the owner:**
   - Is a v1.1 tag acceptable before A4 is published, or A4-gated?
   - Consortium pilot: which question, and is a university lab partner identified?
   - Claim the `computronium` PyPI name now, before 2.0?

---

## 9. Execution order (dependency-ordered; Phase 0 first)

```
Phase 0 (today, ≤1 session)
        P0-1 → P0-2 → P0-3 → P0-4  (verify each; suite green)
        §0.2 smoke (0.05 h) → 0.5 h run  → docs/preliminary_testing.md
        §0.5 exit checklist
Week 1       A1 confirmation ∥ A2 (static vs LearningSurvey identical-budget reports)
Weeks 2–4    A3 one hypothesis at a time   ∥ B9, B10
Week 5       A4 → FINDINGS.md → v1.1 tag
Weeks 6–8    B5 (spec+impl), B6, B7, B8, B11   ∥ C1–C3
Weeks 9–13   C4 (cifar100, svhn) → C5, C6      ∥ C7, C9, D1
Weeks 14–19  C8 (one algorithm family)  → v1.2 tag
Months 6–9   D2–D4 (pilot)    → v2.0 tag
Continuous   E1–E6
```

---

## 10. Provenance of every line item

- **P0-1…P0-4** ← TODO81 §12 low-effort tier (12.1–12.4); verified beneficial on 2026-11-06
  (search-space scan hot path is interpreter-bound at ~1 ms/candidate).
- **A1–A5** ← TODO81 §11 (full-run enablement) + README *Kernel status* + TODO66 §8.
- **B5–B12** ← [T66] §8 *Designed, not built* (M1/M2/M3/`capabilities`/codegen/compatibility
  sampling), [T46] §3.4, T79/T81 runner split.
- **C1–C3** ← [README] *Neutral evaluation* gaps 2/3/4.
- **C4–C8** ← [T66] §8 *Planned* + [README] *Status and scope*.
- **C8** ← [T66] §8 flagship (fair-HPO recovery study).
- **D1–D8** ← [R] + [T66] §8 + correction found 2026-11-06 (reproducibility doc).
- **E1–E6** ← [T66] §8 Register C + AGENTS.md checklist + `.github/workflows/ci.yml`.

---

*Supersedes TODO81 §11/§12 and README *Status and scope*. TODO81 remains the record of how the
kernel was built; TODO82 is the plan of what it is for — starting with giving the owner a run they
can press.*
