# TODO82 — From Laboratory to Evidence to Institution

**Status of `main` at writing:** v1.0.0. The library, the six-axis ontology, the kernel, the demo,
the dashboard, the DuckDB evidence store, the neutrality apparatus (fairness contract, pre-registered
thresholds, identity cards, corrections log), and the CI gates are all real and locked.
**No campaign has been run yet** (README, *Kernel status, stated plainly*). Install is `git clone`;
Computronium is not on PyPI. The single fact that matters most is the first:

> Computronium is a complete instrument that has never measured anything.

PURPOSE.md states the destination — *"a continuously improving empirical map of the space of learning
machines."* The value chain is:

```
instrument ──► evidence ──► trust ──► adoption ──► collective infrastructure
```

Everything below is ordered along that chain. Evidence is the critical path; architecture work exists
to make evidence affordable and trustworthy; distribution and the consortium exist to make evidence
matter. Items cite their provenance: **[T81]** = TODO81 remaining, **[README]** = README *Status and
scope* / *Kernel status*, **[T66]** = TODO66 §8, **[T46]** = TODO46, **[R]** = from repo inspection
2026-11-06.

---

## 1. Principles that govern this plan

1. **Evidence before features.** No new primitive, dashboard panel, or command while the instrument
   has produced zero powered evidence. When choosing between the two, always the campaign.
2. **One evaluation path.** Two front doors (`--mode static` / default LearningSurvey) is a
   temporary fork, not a design. Converge them (B12).
3. **Codegen over hand-sync.** Every rule maintained in two places is a bug waiting to happen —
   we fixed one such pair this session (`system.py` `_validate_nonlayered_geometry_dynamics` vs
   the `seed_registries.py` constraint it duplicates). Validation must be generated from one source.
4. **Fail closed, label loudly.** Unsupported schema → error. Unregistered claim → refused, not
   merely labelled ([README] neutrality gap 4). The referee does not estimate for the reader.
5. **Neutrality is the product.** Equal-effort HPO, blinding, pre-registration — these are not
   constraints on the science; they *are* the science's value proposition. They move from protocol
   to kernel invariant.
6. **De-scope ruthlessly.** §7 lists what we explicitly will not do.
7. **Hygiene is continuous, not a phase.** Register C paydown, repo-wide pyright, `pip-audit` ride
   every release; they are never the milestone.

---

## 2. Honest baseline (what exists / what does not)

**Exists and locked:** ontology (57 primitives), kernel (11 stages, 8 policies — the 8-row catalog
in README), 48 objectives (all but two measured), store (schema v3, fail-closed versioning), claims
with verification levels, ablation tables gated on shared-five-axes, `[at chance]` flags, positive
control requirement, pre-registration labelling, identity cards (`--strict`), corrections log, demo
(7 beats), dashboard, CI gates (property suite, demo gate, vertical slice, drift locks, version
consistency), DuckDB evidence store, determinism locks.

**Does not exist:**

| Gap | Evidence |
|---|---|
| A single measured comparison | README: "No campaign has been run yet." |
| H1–H6 verdicts (the motivating hypotheses) | T81 Step 7 — blocked on full runs, blockers fixed, **never run** |
| PyPI / Docker / versioned releases | `pyproject.toml:2` is `1.0.0`; README install is `git clone` [R] |
| Pre-registered Class E claim that is *refused* when unregistered | [README] neutrality gap 4 — labelled, not refused |
| HPO parity enforced by `comp run` | [README] neutrality gap 2 — protocol + `biopl-hpo`, not an invariant |
| Blinded arm labels | [README] neutrality gap 3 — unbuilt |
| CEEC in the claim path | `ceec_link` is always `None` [R]; "full CEEC integration" planned |
| Cross-domain evidence | [README] neutrality gap 5 — one task family (vision, digits-class) |
| ~650 lint findings (Register C), repo-wide pyright not clean | [T66] §8; `BASELINE = 659` |

---

## 3. The plan — three releases, dependency-ordered

### Release 1.1 — *The Laboratory Runs* (evidence unblocked, instrument calibrated)

**Goal:** unattended, reproducible, powered runs; the first H1–H6 verdicts; the gate is calibrated.
**Theme:** make evidence *affordable and believable*.

#### A. Evidence (the critical path — do first)

| ID | Item | Source |
|---|---|---|
| A1 | **Full smoke run** — `./experiment_shallow.sh 0.05 --policy random`, then `0.5`; verify walltime, cell counts, gate verdicts, store writes, report output end-to-end | T81 §11 |
| A2 | **Sampler control vs adaptive** — static vs learning mode marginal rankings on identical budget; publish both reports verbatim (they *will* differ on any non-reproducible axis — document) | T81 §11 (step 3) |
| A3 | **H1–H6 triage at n ≥ 3** — the six motivating hypotheses, powered; each verdict carries `power_achieved`, seeds, limitations; underpowered cells are `INSUFFICIENT`, never "no effect" | T81 Step 7 |
| A4 | **First pre-registered comparison artifact** — credit × update on digits, OFAT, registered thresholds, positive control passing, report checked into `docs/experiments/` (or a released artifact) | [README] |
| A5 | **Update `docs/FINDINGS.md`** if anything survives audit; otherwise record the null result honestly — both are the brand | docs/FINDINGS.md |

#### B. Instrument correctness & efficiency (unlocks A; mostly small)

| ID | Item | Notes |
|---|---|---|
| B1 | **`harvest_schema()` cache** — `@lru_cache` (called 5+ times per run) | T81 §12.2 — 1-line |
| B2 | **Compile `iter_candidates` void checks** with the same lambda compiler used in `_filter_axes_for_validity` | T81 §12.1 |
| B3 | **`_composable` cache split** — structural validity (shared) vs param-budget validity (specific); add cheap pre-filter before `compose_configs()` | T81 §12.3 |
| B4 | **Batch `RecordStore.append`** (10–50 per transaction) | T81 §12.4 |
| B5 | **M1 — gate calibration** — measure sensitivity/specificity of the train/val gate against held-out cells; publish calibration curve; the verdict is the product's core claim | [README]/[T66] (unspecified — spec first: ≤1 page, then implement) |
| B6 | **M2 — drift detection** — alert when a run's measured distribution departs from the same spec's prior runs (early corruption canary: NaN rate, walltime collapse, identical val_acc runs) | [T66] |
| B7 | **M3 — metric coverage warnings** — report which named objectives were measured vs untouched; refuse silently-empty sections | [T66] |
| B8 | **`capabilities` command** — machine-readable capability registry dump (a named ledger row; lock against it) | [T66] |
| B9 | **Finish the sampler arc** — delete the candidate-list `propose()` signature (TODO46 §3.4 remainder); **policy-aware compatibility sampling** (propose only cells with ≥1 legal completion) | [T46]/[README]/[T66] |
| B10 | **`SystemConfig.validate` codegen** — generate the validation matrix from the registries; delete hand-maintained whitelists | [T66] |
| B11 | **CEEC in the claim path** — populate `ceec_link`; a Class E claim carries its ledger hash or `[ceec_absent]` | [README]/[T66] |
| B12 | **One evaluation path** — fold `SimpleSurvey` into the kernel behind a `--deterministic` flag (or LearningSurvey `--policy uniform_random` with fixed seed + zero adaptivity); remove `simple_survey.py` execution fork, keep the file as historical reference only if it costs nothing to delete | T79/T81 split |

**v1.1 acceptance:** A1–A3 done; A4 published; B1–B4 landed; B5 specified and drafted; B9 merged;
`CONTRIBUTING.md` added (commit checklist + the never-`pytest tests/` discipline); release notes
cut; `uv run comp run demo` passes on a clean checkout.

---

### Release 1.2 — *The Evidence Generalizes* (neutrality becomes enforceable)

**Goal:** claims are refused when unregistered; HPO parity is an invariant; evidence exists on
more than one task family; transfer is measured.
**Theme:** trust through enforcement, not through vigilance.

| ID | Item |
|---|---|
| C1 | **Pre-registration enforced** — Class E claims refuse without a matching registration (label becomes error); `[unpreregistered_claim]` survives only for exploratory (Class A–D) claims |
| C2 | **Blinding** — arm labels hashed to A/B/C for analysis; unblinding is a logged, separate step |
| C3 | **HPO parity invariant** — `comp run` (and `campaign`) verify every contrasted arm got the same trials/budget; violations refuse publication or stamp `[hpo_asymmetry]`; extend `biopl-hpo` into the kernel |
| C4 | **7-domain expansion, incremental** — vision first (`cifar10` is implemented; add `cifar100`, `svhn`), then language (`wikitext2`/`penn_treebank` per ledger), RL (`cartpole` done; `mountain_car`/`lunar_lander`), tabular (`diabetes`, `california_housing`), time series (`ett_h1`). **Each new task must ship with its own chance line, positive control, and identity-card audit before any contrast is published on it** |
| C5 | **Cross-domain transfer test** — pick the top credit × update cell on `digits`; re-run frozen on `cifar10` and `tiny_shakespeare`; report transfer delta with CIs. This is the claim no benchmark table makes |
| C6 | **Cross-substrate robustness** — the same cell on `digital` vs `memristive` (simulated): does ranking hold under noise/IR-drop/bounded precision? Substrate value proposition, measured |
| C7 | **Default replication** — `n_seeds ≥ 3` floor for any claim-bearing fidelity (L1+); single-seed runs labelled `[n=1, exploratory]` |
| C8 | **Fair-HPO recovery study** — the flagship: re-tune each zoo algorithm under equal effort; publish delta vs published numbers (the "better than commonly believed?" programme). Needs C3 + real compute; run one algorithm family first to calibrate cost |
| C9 | **M2 drift gates wired into CI for canaries** — a fast nightly seeded canary run asserts metric distributions within tolerance; failure pages, does not merge |
| C10 | **Error-message pass** — every refusal names the rule that refused it (dashboard already does this; extend to CLI/report); catalogue them in `docs/errors.md` |

**v1.2 acceptance:** C1–C3 enforced and tested (a deliberately unregistered claim is refused in a
test); C4 delivers ≥2 new tasks with full control protocol; C5 published; C8 protocol + first
family drafted; release notes; PyPI `computronium==1.2.0` (see D1).

---

### Release 2.0 — *The Consortium* (evidence becomes infrastructure)

**Goal:** someone who is not us can use this to produce a claim we will print.
**Theme:** the referee becomes a referee.

| ID | Item |
|---|---|
| D1 | **Distribution** — PyPI (`pip install computronium`), Docker image (CUDA + CPU), `CHANGELOG.md`, semver discipline, version-consistency lock extended to 2.0 |
| D2 | **Ten-minute path** — rewrite the onboarding around **RunSpec YAML + `question_first()`**: install → ask → run → report, one command per step; the existing `docs/experiments/*.md` are CLI-flag archaeology — replace with a spec-first tutorial and 5 worked YAML examples (`examples/`) |
| D3 | **API reference** — `docs/generated/` completed for public API; every public symbol has a one-line contract + example; lock README blocks against tests (existing lock pattern) |
| D4 | **Consortium pilot** — one bounded question (credit × update on vision, three independent labs), pre-registered, replicated, published with corrections log; the pilot *is* the constitution's first test |
| D5 | **Public record** — run registry (provenance-hashed), corrections log rendered as a public page; `comp benchmark-contrib` seeded with the pilot; admission = identity cards pass `--strict` on the contributor's implementation |
| D6 | **Adoption kit** — FAIRNESS_CONTRACT as standalone spec; pre-registration templates; fork-and-run instructions for labs without our stack (protocol is the contribution, not the code) |
| D7 | **Docs information architecture** — README stays the map (≤600 lines); depth moves to `docs/`; per-audience landing pages exist — audit them |
| D8 | **Release signing & provenance** — artifacts signed; `comp export --docker` + `comp repro --docker` reproduces a published record; **fix `docs/experiments/reproducibility.md`** — it documents `comp export --format docker`, which does not exist (`--format` is json/parquet; `--docker` is the flag) |

**v2.0 acceptance:** D1 published; D2 replaces the quickstart and passes on a clean VM; D4 pilot
signed off (or honestly reported as failed); D5 public; ≥1 external contributor record in the store.

---

## 4. Continuous engineering (rides along; never the milestone)

| ID | Item |
|---|---|
| E1 | **Register C paydown** — 650 findings → 0; ratchet only downward; per-rule census updated in this file's logs |
| E2 | **Repo-wide pyright** — finish Register C type work; strict on new modules from now on, no exceptions |
| E3 | **`pip-audit` clean** — currently green? verify and keep; add to CI as advisory then gate |
| E4 | **CI stays** — property suite + demo gate + vertical slice + drift locks + version consistency; never `pytest tests/`; directory shards are round-close artifacts only |
| E5 | **Determinism across platforms** — document CPU/GPU/BLAS variance; golden digests for the demo store |
| E6 | **Dependency diet** — audit `uv.lock`; anything unimportable after 12 months gets a removal ticket |

---

## 5. Architecture decisions embedded in this plan (do not re-litigate)

1. **LearningSurvey is the runner**; `--mode static` survives as a thin flag until B12 removes it.
2. **Validation is generated, not hand-maintained** (B10); the audit residue is a test that proves
   registry ↔ codegen ↔ `SystemConfig.validate` agree.
3. **The store is the source of truth**; reports are re-derived views; never patch a store.
4. **CEEC is mandatory for claims, optional for exploration** (B11).
5. **FIDELITY ladder earns its keep by doing work**: L0 screens, L1 confirms, L2 publishes; a claim
   never cites L0.
6. **SimpleSurvey dies** (B12). No third runner.
7. **Docs move out of README** as they stabilize; README links, doesn't contain.

---

## 6. Success metrics (falsifiable; checked per release)

| Release | Metric | Target |
|---|---|---|
| 1.1 | Walltime to first report on clean machine | ≤ 15 min |
| 1.1 | H1–H6 verdicts with `power_achieved` and seeds | 6/6 issued, zero "no effect" language |
| 1.1 | Published A4 artifact | exists, reproducible from store hash |
| 1.2 | Unregistered Class E claim in CI | refused, test proves it |
| 1.2 | New tasks passing full control protocol | ≥ 2 |
| 1.2 | `pip install computronium` | works |
| 2.0 | External reproduction of a Computronium record | ≥ 1, acknowledged in corrections log |
| 2.0 | Contract adoption by an outside lab | ≥ 1 (signed or publicly stated) |
| any | Register C findings | strictly decreases per release |

---

## 7. Explicitly de-scoped (binding unless a partner appears)

- **A real TUI** — web dashboard already covers the interaction surface; a TUI splits maintenance.
  Cut unless dashboard adoption fails *because of* terminal-only users.
- **Ray / SLURM / DDP at scale** — single-node must be routine first; revisit when a campaign
  demonstrably needs >8 GPUs or >24h walltime.
- **PDE scientific suite** — after the seven domains are characterized; numerical PDEs are a second
  project (meshing, boundary conditions, verification).
- **Physical-hardware validation** — memristive/neuromorphic/optical/quantum require a lab partner;
  until then, simulation honesty stays in the README (it is a feature, not an apology).
- **"Computronium found a better algorithm"** — not a milestone. A powered, pre-registered
  comparison is; "better" is the reader's word.
- **New axes / new primitive families** — ontology grows only through the checklist; no additions
  during 1.1/1.2.
- **Multi-tenant SaaS / hosted campaigns** — not now; distribution via pip/Docker only.
- **`vmap` full multi-seed** — correct but orthogonal; file as issue, not plan.

---

## 8. Risks and open questions

1. **Powered comparisons are expensive** — 63 seeds/group for d=0.5; the allocator + fidelity ladder
   must price every claim before launch (`comp power-analysis` exists). Risk: ambitious A3 becomes
   A3-abandoned. Mitigation: one hypothesis per week, report each, never batch.
2. **Rankings may not replicate hardware** — digits-winner ≠ deployed-winner; that is *why* B7/C6
   exist; publish with the caveat, don't soften it.
3. **The reference implementations are ours** — consortium replication (D4) is the only cure;
   accelerating it outranks adding benchmarks.
4. **Ontology drift vs simplicity** — every axis addition multiplies the space; B10 codegen keeps
   legality honest, but the *editorial* burden (identity cards, deviations, docs) is real. Budget it.
5. **Single-maintainer bus factor** — D2/D7 reduce onboarding cost for successors; keep the
   commit checklist in AGENTS.md current.
6. **Open questions for the owner:**
   - Is a v1.1 release (tag + notes) acceptable before A4 is published, or is the tag A4-gated?
   - Consortium pilot: which question, and is a university lab partner identified?
   - Do we want `comp` on PyPI with the `computronium` name claimed now, before 2.0?

---

## 9. Execution order (≈ effort, dependency-ordered)

```
Weeks 1–2   B1–B4 (half day) → A1 → A2 → B12(design) → B5 spec
Weeks 3–5   A3 (one hypothesis at a time)  ∥ B9, B10
Weeks 6     A4 → FINDINGS.md → v1.1 tag → release notes
Weeks 7–9   B5 impl, B6, B7, B8, B11      ∥ C1–C3
Weeks 10–14 C4 (cifar100+svhn) → C5, C6    ∥ C7, C9, D1
Weeks 15–20 C8 (one family)  → v1.2 tag
Months 6–9  D2–D4 (pilot)    → v2.0 tag
Continuous  E1–E6; every PR runs property + demo gate; Register C only falls
```

---

## 10. Provenance of every line item

- **A1–A5** ← TODO81 §11 (Step 7, full-run enablement) + README *Kernel status* ("No campaign has
  been run yet") + TODO66 §8 *Results we actually own*.
- **B1–B4, B9** ← TODO81 §12 (this session's optimization pass; P0/P1 tier).
- **B5–B8, B10** ← [T66] §8 *Designed, not built* (M1 gate calibration · M2 drift detection · M3
  metric coverage warnings · `capabilities` · `SystemConfig.validate` codegen · policy-aware
  compatibility sampling · repo-wide effect lock folded into B9).
- **B11** ← [README] *Evidence & claims* (`ceec_link` always `None`) + [T66] *full CEEC
  integration*.
- **C1–C3** ← [README] *Neutral evaluation* gaps 2/3/4 (HPO protocol, blinding, unregistered
  claims labelled not refused) + [T66] §8 C11/C12 family.
- **C4–C8** ← [README] *Status and scope → Planned* (7-domain expansion; fair-HPO recovery study) +
  [T66] §8 *Planned*.
- **C8** ← [T66] §8 flagship: *"fair-HPO recovery study — for each zoo algorithm, re-tune under
  equal effort and publish the delta from its published number."*
- **D1–D8** ← [R] (git-clone install, v1.0.0, no CHANGELOG) + [README] *Planned* (consortium,
  literature store — literature store folded into D2) + [T66] §8 (TUI → §7 de-scoped; Ray/SLURM → §7).
- **E1–E6** ← [T66] §8 Register C + AGENTS.md commit checklist + `.github/workflows/ci.yml` [R].
- **Everything deliberately omitted** ← §7.

---

*This document supersedes the remaining-work sections of TODO81 (§11, §12) and the README *Status
and scope* lists. TODO81 remains the record of how the kernel was built; TODO82 is the plan of what
it is for.*
