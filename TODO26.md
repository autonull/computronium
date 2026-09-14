# TODO26 — CEEC Kernel Architecture + ψ Composition

**Status:** PHASES A–H + S LANDED 2026-09-14 (H24.3 carries a certified
round-2 AGAINST verdict; see Progress Log). Open follow-ons are Register
C hygiene items only (see Improvements). Architecture verified against
four live usage patterns (probe closed loop, evolution kernel,
MeasurementRunner, per-epoch training capture); Profile/Session/
store-split/derived-registry all shipped. **Builds on:** TODO25 (all
phases + continuation executed; root `CEEC.md` reference landed;
improvement #6 vacuous-override rule shipped). **Explicit exclusion:**
PyPI publishing remains out of scope.

---

## 0. The Next Synthesis

Two parallel tracks. **Architecture:** CEEC-core is epistemically sound
(four-component confidence, four gate families, calibration beyond spec)
but carries Computronium vocabulary inside the kernel — hardcoded `Scope`
fields, ψ/θ constraint names, budget `Literal`, and quality-flag
spellings duplicated between `gates.py` and `builders.py`. Four call
sites hand-assemble payloads around a 15-positional-arg record API.
TODO26 parameterizes the kernel by a `Profile`, deletes the duplication
at the source, and adds a `Session` façade — enabling entirely different
application domains with ~60 lines each. **Scientific:** TODO25 #7's
composed backbone+ψ system unblocks H24.3 (instrument-blocked), the
first certified measurement the new session API should carry end-to-end.

Core rule unchanged: **evolution/campaigns produce evidence; gates
dispose; claims only at certified tier.**

---

## 1. Measured debts (design inputs)

| Debt | Evidence |
|---|---|
| Domain vocabulary in core | `Scope.substrate/geometry/credit` fields; `frozen_theta_audit_for_psi_only_claims`, `identity_card_for_new_primitive` in `selection.py`; `budget: Literal["quick","standard","nightly"]` in `models.Experiment`; `BUDGET_DEFAULT_COST` |
| Flag spellings duplicated | `gates.py:6-11` flag mapping vs `builders.py:150-165` spelling table — manual lockstep |
| Hand-assembly at 4 sites | `builders.gate_evidence` callers: `ceec.run` (3-call ingest), `corpus.py:_record_ledger`, `evolution.py:_record_candidate`, `training.py:ceec_campaign` |
| Boilerplate record API | `store.record_evidence`/`record_derived` 15+ positional args (ruff ignores) |
| Constraint registry unused | `constraints.py` Protocol exists; real set hardcoded in `check_hard_constraints` |
| Runner triplication | `ceec.run.run_experiment` / lab `MeasurementRunner` / `_scoped_decision` (StoreError-fallback hack) |
| Monolithic store | `store.py` 1393 lines (DDL + records + queries + reports) |
| Unversioned semantics, untyped ledgers | no `policy_version` stamp; no ledger role (TODO25 #10a/b) |

Spec compliance already achieved (no work needed): four-component
confidence (§10.3), artifact-or-justification (§8.2), structured-evidence
enforcement (§8.3), all gate families (§17-21), calibration + drift
cadence (§24), inert/missing labeling. Gaps adopted in Phase F:
derived-operator registry (§9.4), execution provenance defaults (§12.3),
anti-pattern audit extensions (§27). Portfolio budgeting (§22.4) stays
out — greedy is spec-acceptable.

---

## 2. Target architecture

```
┌────────────────────────────────────────────────────────┐
│ Domain adapters: computronium-lab, <new domains>       │
│   Profile + tier maps + probe wiring (~60 lines each)  │
├────────────────────────────────────────────────────────┤
│ ceec-core: epistemic kernel, parameterized by Profile  │
│   models · ledger/ · gates · selection · calibration   │
│   audit · session · report · derived · stats           │
└────────────────────────────────────────────────────────┘
```

### 2.1 `Profile` (`ceec/profile.py`)

```python
@dataclass(frozen=True, slots=True)
class Thresholds:
    promote_low: float = 0.95      # τ_promote
    boundary_high: float = 0.05    # τ_boundary
    reopen_min: float = 0.10       # ε_reopen

@dataclass(frozen=True, slots=True)
class QualitySchema:
    flags: Mapping[str, type]                 # "defect_audit": Literal["pass","fail"], ...
    required: Mapping[str, frozenset[str]]    # gate family -> required flags

@dataclass(frozen=True, slots=True)
class Constraint:
    name: str
    check: Callable[[CEECStore, Experiment], ConstraintResult]

@dataclass(frozen=True, slots=True)
class Profile:
    name: str
    policy_version: str
    scope_dimensions: Mapping[str, type]       # declared dims; unknown dims allowed (spec §6 open map)
    budget_tiers: tuple[str, ...]
    tier_budget: Mapping[str, str] | None      # adapter tier vocab -> budget tier
    default_cost: Mapping[str, float] | None
    constraints: tuple[Constraint, ...]
    quality: QualitySchema
    thresholds: Thresholds
```

- `CORE_CONSTRAINTS` (core): `pre_registration_complete`,
  `no_quarantined_dependencies`, `budget_within_limit`,
  `controls_present_or_justified`, `seed_plan_present`,
  `evaluation_policy_present`, `structured_evidence_plan_present`,
  `instrument_valid_for_claim`, `coordinate_valid` (factory:
  `coordinate_constraint(validator)`).
- Computronium profile adds: `frozen_theta_audit_for_psi_only_claims`,
  `identity_card_for_new_primitive`. Profiles may only *add* constraints
  and declare vocabulary — never weaken gate families (spec §17).
- Gate thresholds read `profile.thresholds` (today hardcoded in `gates.py`).

### 2.2 `Scope` generalization (breaking; AGENTS: no backwards compat)

```python
@dataclass(frozen=True, slots=True)
class Scope:
    dims: Mapping[str, str | tuple[str, ...]]   # frozen; "domain" required

    @classmethod
    def of(cls, **dims) -> Scope: ...
```

`substrate/geometry/credit/budget/extra` become dims declared by the
Computronium profile; store validates known dims against
`profile.scope_dimensions` at record time. `code_commit` moves to
artifact/evidence provenance where it belongs.

### 2.3 `Session` façade (`ceec/session.py`)

```python
def ledger(path, profile, *, role: LedgerRole = LedgerRole.CAMPAIGN) -> Session

class Session:
    profile: Profile
    role: LedgerRole
    def experiment(self, *, question, prediction, rationale, scope,
                   targets=(), design=None, budget=None, tier=None, ...) -> Experiment
    def evidence(self, scope, *, artifact_refs=(), axes=(), values=(),
                 values_ref="", quality=..., notes=None) -> Evidence
    def artifact(self, payload, type_, provenance) -> Artifact
    def decide(self, *, rationale, candidate_ids=None, focus_id=None,
               overrides=(), validator=None) -> Decision
    def run(self, exp, probe, *, evaluate=None) -> ExperimentRun    # closed loop
    def record_result(self, exp, result: ProbeResult) -> ExperimentRun
    def render(self, path=None) -> tuple[str, dict]
    def audit(self) -> list[str]
    def calibration_report(self) -> dict
    def close_round(self, *, fail_on_trigger=False) -> CloseReport
```

- `Session.decide(focus_id=...)` pre-checks the focus candidate's hard
  constraints and passes the selection override only when eligible —
  native fallback, deletes the kernel's `StoreError` try/except hack.
- `tier=` on `experiment()` resolves through `profile.tier_budget`;
  `budget=` takes profile vocabulary directly.
- `record_result` is the one-call ingest: artifact → evidence (quality
  validated against `profile.quality`) → calibration. Replaces
  `run.py`'s hand assembly; probes call it directly.
- `render` = `render_ledger` migrated from `computronium_lab.research.reports`
  (it is domain-agnostic and belongs in core).

### 2.4 Store split (import path stable)

`store.py` → package `ceec/store/`: `schema.py` (DDL, triggers,
migrations, `policy_version` columns, `ledger_meta` role table),
`records.py` (record APIs, keyword-only), `query.py` (getters,
by-status, `state_hash`), `__init__.py` (CEECStore facade composed from
mixins). `ceec.store.CEECStore` import continues to work everywhere.

### 2.5 Derived operators (`ceec/derived.py`, spec §9)

```python
@dataclass(frozen=True, slots=True)
class Operator:
    name: str
    kind: Literal["summary", "relation"]
    fn: Callable[[Mapping[str, list[Any]]], Any]
    assumptions: tuple[str, ...] = ()

OPERATORS: Mapping[str, Operator]   # mean, median, spread, contrast, slope, dominance, replication
def compute_derived(store, operator, inputs, *, scope, parameters=None) -> Derived
```

`chance_verdict`/`chance_band` becomes a registered summary operator;
`ceec.stats.chance_verdict` re-exported for probe compatibility. Ledger
rollups in `render` become recomputable `summary` Derived rows (P7).

### 2.6 Ledger roles + policy version

`LedgerRole` StrEnum: `main | campaign | scratch`. Stamped into
`ledger_meta` at `ceec init --role`; `run_audit` enforces scope (campaign
ledgers cannot gate against main-ledger instruments). `policy_version`
from the profile stamped onto every `Decision` and `CalibrationRecord`
row — semantic changes become readable from data (TODO25 #10b).

### 2.7 Identifier migration map

| Today | TODO26 |
|---|---|
| `ceec.builders.experiment(tier=...)` | `Session.experiment(tier=...)` |
| `ceec.builders.gate_evidence(...)` | `Session.evidence(...)` (profile-validated quality) |
| `ceec.builders.chance_verdict` | `ceec.stats.chance_verdict` (re-export kept one phase) |
| `ceec.run.run_experiment(store, ...)` | `Session.run(exp, probe)` (wrapper kept one phase) |
| `ceec.selection.decide(store, {}, ...)` | `Session.decide(...)` (profile dict arg dies) |
| `lab.research.reports.render_ledger` | `ceec.report.render_ledger` (lab re-export) |
| `evolution._scoped_decision` | `Session.decide(focus_id=...)` |
| `training.ceec_campaign` / `corpus._record_ledger` / `lab._record_exploratory` | `Session.artifact` + `Session.evidence` via `lab.ledger_session()` |
| `CEECStore(db, db.parent / "artifacts")` | `ledger(path, profile, role=...)` |
| `_TIER_BUDGET`, `BUDGET_DEFAULT_COST` | `profile.tier_budget`, `profile.default_cost` |

---

## 3. Usage simulation (verified against live call sites)

**Probe closed loop** (`todo25_recal_record.py` pattern):

```python
with ledger(LEDGER, COMPUTRONIUM, role="campaign") as sess:
    draft = sess.experiment(question=..., prediction=..., tier="certified",
                            scope=Scope.of(domain="research", task="flat_classification_hard"))
    run = sess.run(draft, _campaign_probe, evaluate="boundary")   # or record_result for manual control
    report = sess.close_round()                                   # render + audit + drift flags
```

**Evolution kernel** (replaces `_scoped_decision`):

```python
decision = sess.decide(candidate_ids=gen_ids, focus_id=focus_id,
                       rationale=..., validator=_coordinate_validator)
```

**MeasurementRunner** (replaces `_record_ledger` hand assembly):

```python
sess = lab.ledger_session(role="campaign")          # binds COMPUTRONIUM profile
art = sess.artifact(json_payload, "corpus_run", {"run_id": rid})
ev = sess.evidence(scope, artifact_refs=[art.id], axes=("arm",), values=accs,
                   seeds=3, matched_control=True, evaluation_policy=...)
```

**Per-epoch capture** (replaces `training.ceec_campaign`):

```python
with lab.ledger_session(role="scratch") as sess:
    for row in history:
        sess.evidence(sess.artifact(json.dumps(row).encode(), "lab_training_epoch", ...),
                      ...)
```

**New domain** (Phase H proof — no core changes):

```python
SENTIMENT = Profile(name="sentiment-eval", policy_version="1.0",
    scope_dimensions={"model": str, "benchmark": str, "prompt_version": str},
    budget_tiers=("cheap", "standard", "sweep"),
    constraints=CORE_CONSTRAINTS + (no_train_contamination,),
    quality=QualitySchema(flags={"contamination_check": Literal["pass","fail"]}, ...))
with ledger("ledgers/sentiment.sqlite3", SENTIMENT) as sess: ...
```

---

## Phase A: Kernel parameterization

| Task | Deliverable | Depends On |
|---|---|---|
| **T26.A.1 `Profile` + `Thresholds` + `QualitySchema`** | `ceec/profile.py` with dataclasses above; `CORE_CONSTRAINTS` extracted verbatim from `check_hard_constraints` (behavior-identical); gates read `profile.thresholds` | — |
| **T26.A.2 `LedgerRole` + role stamp** | `ledger_meta` table; `CEECStore(..., role=)`; `ceec init --role`; `run_audit` scope enforcement (campaign ledgers refuse main-ledger instrument gating) | A.1 |
| **T26.A.3 `policy_version` stamp** | `policy_version` columns on `decisions` + `calibration_records`; schema migration; stamped from profile on every write | A.1 |

**Success criterion:** full ceec suite green with the profile threaded
through store/gates/selection; migration handles existing ledgers.

---

## Phase B: Registries (delete the lockstep duplication)

| Task | Deliverable | Depends On |
|---|---|---|
| **T26.B.1 Constraint registry** | `check_hard_constraints` → `for c in profile.constraints`; `coordinate_constraint(validator)` factory; `frozen_theta_audit_for_psi_only_claims` + `identity_card_for_new_primitive` move to the Computronium profile (Phase G wires it) | A.1 |
| **T26.B.2 Quality schema enforcement** | `evidence.quality` validated against `profile.quality` at `record_evidence`; gate readers read flags through the schema; `builders.py` spelling table deleted | A.1 |

**Success criterion:** grep gate zero — `grep -rn "psi\|frozen_theta\|identity_card" packages/ceec-core/src/ceec/ --include="*.py"` returns nothing; flag spelling exists in exactly one place.

---

## Phase C: Store split + record API

| Task | Deliverable | Depends On |
|---|---|---|
| **T26.C.1 Store package split** | `ceec/store/{schema,records,query,__init__}.py` mixins; `ceec.store.CEECStore` facade; no behavior change | A |
| **T26.C.2 Keyword-only record APIs** | `record_evidence`/`record_derived`/`record_decision` keyword-only with validated `*Spec` drafts; ruff positional-arg ignores deleted | C.1 |
| **T26.C.3 `record_result` one-call ingest** | artifact → evidence → calibration in one validated call; `run.py` internals refactored onto it | C.2, B.2 |

**Success criterion:** ceec + lab suites green; no `_conn.commit()` private access outside the store package.

---

## Phase D: Session façade

| Task | Deliverable | Depends On |
|---|---|---|
| **T26.D.1 `ledger()` + `Session`** | `ceec/session.py`: experiment/evidence/artifact/decide/run/record_result/audit/calibration_report; `focus_id` native fallback; `run.py` becomes a thin wrapper | C.3 |
| **T26.D.2 `render_ledger` → core** | `ceec/report.py`; lab module re-exports for compatibility | C.1 |
| **T26.D.3 `close_round`** | render + `run_audit` + `audit_decisions` + `review_flags` in one `CloseReport`; CLI `ceec close-round --fail-on-trigger` (non-zero exit on triggers) — TODO25 #10c | D.1, D.2 |

**Success criterion:** probes (`todo25_recal_record.py` style) rewritten on
`Session` pass the existing closed-loop tests byte-for-byte on verdicts.

---

## Phase E: Scope generalization (breaking)

| Task | Deliverable | Depends On |
|---|---|---|
| **T26.E.1 `Scope.dims` map** | `Scope` → frozen dims map + `Scope.of()`; `substrate/geometry/credit/extra` → dims; `code_commit` → provenance; store validates against `profile.scope_dimensions` | A.1 |
| **T26.E.2 `Experiment.budget` de-Literal** | `budget: str` validated against `profile.budget_tiers` at store boundary; `BUDGET_DEFAULT_COST` → `profile.default_cost` | E.1 |
| **T26.E.3 Adapter sweep** | All `Scope(...)` constructions in lab/probes/tests → `Scope.of(...)` with declared dims (4 sites + tests) | E.1 |

**Success criterion:** repo-wide grep finds no `Scope(domain=` positional-field construction; all suites green.

---

## Phase F: Derived operators + provenance (spec adoption)

| Task | Deliverable | Depends On |
|---|---|---|
| **T26.F.1 Operator registry** | `ceec/derived.py`: `Operator`, `OPERATORS` (mean, median, spread, contrast, slope, dominance, replication, chance_band), `compute_derived` with stored value + provenance (recomputable, §9.4) | C.1 |
| **T26.F.2 Execution provenance defaults** | `Session.run` stamps config hash, code commit, seed policy, deviations into artifact provenance (§12.3) | D.1 |
| **T26.F.3 Anti-pattern audit** | `run_audit` extensions: single-seed promotion attempt, untested-lever boundary declaration, silent-scalarization (structured kinds reduced to scalar primary) (§27) | C.1 |
| **T26.F.4 Rollups as Derived** | `render_ledger` rollup rows recorded as recomputable `summary` Derived (opt-in flag; read-only default preserved) | F.1, D.2 |

**Success criterion:** a Derived row recomputes byte-identically from its
inputs in a property test; provenance present on every closed-loop artifact.

---

## Phase G: Computronium adapter formalization

| Task | Deliverable | Depends On |
|---|---|---|
| **T26.G.1 `COMPUTRONIUM_PROFILE`** | `computronium_lab/ceec_profile.py`: scope dims (substrate/geometry/credit/task/run_id), tier_budget (smoke→quick, quick→standard, certified→nightly), ψ/θ constraints, quality schema | B, E |
| **T26.G.2 `Lab.ledger_session()`** | binds profile + `record_ledger` path + role; `lab.research_report`/`_record_exploratory`/`MeasurementRunner`/`ceec_campaign`/kernel `_scoped_decision` migrate onto Session; per-site dedup | D.1, G.1 |
| **T26.G.3 Shim deprecation** | `computronium/ceec` shim gains DeprecationWarning; 5 legacy probes (`x_ali/x_sta/x_tac/x_tpc/x_rse_001`) migrate to `ceec` imports | G.2 |

**Success criterion:** lab source contains zero direct `CEECStore(...)`/`builders.gate_evidence` calls outside `ceec_profile.py`/`ledger_session`; all research suites + demo gate green.

---

## Phase H: Domain-enablement proof

| Task | Deliverable | Depends On |
|---|---|---|
| **T26.H.1 Fixture-domain test** | `test_domain_profile.py`: sentiment-eval profile (§3 sketch) runs the full loop — experiment → decide → run → boundary → calibration → close_round — with zero core changes; proves the ~60-line onboarding claim | D.1 |
| **T26.H.2 CEEC.md + guide update** | `CEEC.md` architecture section rewritten to Profile/Session reality; `ceec_guide.md` walkthrough rewritten on Session; assessment items #10a/b/c marked landed | H.1 |

**Success criterion:** a newcomer reproduces the fixture-domain loop from
`ceec_guide.md` alone in one session.

---

## Phase S (parallel scientific track — carried from TODO25 #7)

| Task | Deliverable | Depends On |
|---|---|---|
| **T26.S.1 Composed backbone+ψ system** | Trainable feature-extractor θ + ψ ridge readout as a composed mechanism: ψ arm = frozen θ with per-episode ridge re-solve; unblocks the continual corpus path (`AdaptivePsiReadout` bare-readout limitation) | — |
| **T26.S.2 Continual benchmark wiring** | `temporal_psi_task_switcher` runs through the composed system: task-A `lab.train`, θ digest, ridge re-solve per episode | S.1 |
| **T26.S.3 H24.3 round-2 closed-loop run** | Arms: psi / `theta_finetune_matched_compute` (SGD on same backbone, matched compute) / `frozen_no_psi` (frozen θ + linear probe); certified quick-tier continual benchmark; verdict recorded under the round-1 rule | S.2, D.1 (rides Session) |
| **T26.S.4 Round-1 caveat propagation** | ψ-underperformance round-1 result carries the "instrument ≠ registered benchmark" caveat wherever cited (cookbook, CEEC.md worked examples) | S.3 |

**Success criterion:** H24.3 moves from BLOCKED to a certified
FOR/AGAINST verdict through the registered instrument — the first
end-to-end certification on the new Session API.

---

## Gates (whole round)

1. **Kernel purity:** zero domain vocabulary in `packages/ceec-core/src/ceec/` (grep gate, Phase B/E).
2. **Domain proof:** fixture-domain profile test passes without core changes (Phase H).
3. **No duplication:** flag spellings and constraint sets exist in exactly one place.
4. **Suites:** ceec-core + computronium-lab research suites green per phase; demo gate + gallery lock + drift locks at round close; ruff + strict pyright on all touched files.
5. **H24.3 certified verdict** (Phase S).

---

## 17. Progress Log

### Session 2026-09-14 — PLANNED
- [x] Design verified against 4 live call sites; identifiers finalized (this document)

### Session 2026-09-14 — Phases A–H executed (Phases A–G complete; Phase S open)

**Phase A — kernel parameterization (landed)**
- `ceec/profile.py`: `Profile` / `Thresholds` / `QualitySchema` /
  `Constraint` / `LedgerRole`; `CORE_CONSTRAINTS` extracted verbatim;
  `DEFAULT_PROFILE` (core budget tiers + costs + quality schema).
- `ledger_meta` table; `CEECStore(..., role=, profile=)`; `ceec init
  --role`; `run_audit` scope check (`campaign_ledger_instrument_gating`).
- `policy_version` additive migration on `decisions` +
  `calibration_records`; stamped from `store.profile` on every write.
- Gates read `store.profile.thresholds` (module constants deleted;
  decision-time profile overrides per call).

**Phase B — registries (landed)**
- `check_hard_constraints` iterates `profile.constraints`; ψ/θ +
  identity-card constraints moved to the lab profile
  (`computronium_lab/ceec_profile.py::COMPUTRONIUM_PROFILE`). Kernel
  grep gate passes: zero `psi|frozen_theta|identity_card` in ceec-core.
- `QualitySchema.validate` enforced at `record_evidence`; builders'
  spelling table deleted (schema is the single spelling source).
  NOTE: undeclared quality keys are *accepted* (open map, spec §6) —
  live usage records `verification_level`/`predicted_viability`/`tier`;
  `defect_audit`/`integrity_checks` alphabets extended with `not_run`
  (legitimate pre-hunt state used by tests and probes).

**Phase C — store split (landed)**
- `ceec/store/` package: `schema.py` (DDL + `_additive_migrate`),
  `records.py` (`RecordsMixin`), `query.py` (`QueryMixin`),
  `base.py` (`StoreBase` lifecycle/internals), `_store.py` +
  `__init__.py` (composed `CEECStore` facade; import path stable).
- `record_evidence`/`record_derived`/`record_decision` keyword-only
  (kind/scope/type_/operator/inputs stay positional); ruff
  positional-arg ignores deleted; all call sites migrated.
- `ceec.run.record_result(store, experiment, result)` one-call ingest
  (artifact → evidence → calibration); `run_experiment` refactored onto
  it.

**Phase D — Session façade (landed)**
- `ceec/session.py`: `ledger(path, profile, role=)` + `Session` with
  `experiment`/`artifact`/`evidence`/`decide`/`run`/`record_result`/
  `render`/`audit`/`calibration_report`/`close_round`.
- `Session.decide(focus_id=...)` pre-checks focus constraints natively;
  the kernel's `StoreError` fallback hack is deleted from
  `evolution._scoped_decision` (now a thin wrapper). The failed-constraint
  names are appended to the decision rationale (improvement #1 landed).
- `render_ledger` migrated to `ceec.report`; lab module re-exports.
- `close_round` = render + `run_audit` + `audit_decisions` + review
  flags; `fail_on_trigger=True` raises on violations/flags (TODO25
  #10c; CLI parity still open, see improvements).
- Tests: `tests/ceec/test_session.py` (closed-loop promote, manual
  `record_result`, native focus fallback, role stamp, render).

**Phase E — Scope generalization (landed)**
- `Scope` is now an open `dims` map (`Scope.of(**dims)`); legacy
  `domain/substrate/geometry/credit/budget/extra` kwargs are absorbed
  into `dims` at parse time (one-way data migration — old ledger rows
  keep reading). `.substrate/.geometry/.credit` readers updated
  (`_scope_explicit`, `_beliefs_without_scope`).
- `Experiment.budget: str`, validated against `profile.budget_tiers` at
  pre-registration; `BUDGET_DEFAULT_COST` deleted (profile
  `default_cost`); declared scope dims type-checked at record time
  (`_validate_scope`), undeclared dims stay open (§6).
- Construction sweep: all `Scope(domain=...)` → `Scope.of(domain=...)`.

**Phase F — derived operators + provenance (landed)**
- `ceec/derived.py`: `Operator` registry (`mean`, `median`, `spread`,
  `contrast`, `slope`, `dominance`, `replication`, `chance_band`);
  `compute_derived` resolves refs from the ledger and records
  provenance-stamped rows. Recompute byte-identically:
  `tests/ceec/test_derived.py`.
- `ceec/stats.py` is the canonical `chance_verdict` home;
  `builders.chance_verdict` re-exported.
- `Session.run`/`run_experiment` artifacts carry execution provenance:
  code commit (`CEEC_CODE_COMMIT` override, git probe fallback), seed
  policy, evaluation policy, deviations, config hash.
- `run_audit` §27 extensions: `single_seed_promotion_attempt` (violation),
  `untested_lever_boundary_declaration` (warning),
  `silent_scalarization` (warning).
- `render_ledger(store, record_rollups=True)` opt-in records the rollup
  as a recomputable `summary` Derived; read-only default preserved.

**Phase G — Computronium adapter (landed)**
- `computronium_lab/ceec_profile.py::COMPUTRONIUM_PROFILE`: scope dims
  (domain/task/run_id/substrate/geometry/credit/budget), tier ladder,
  ψ/θ + identity-card constraints, core quality schema.
- `Lab.ledger_session(role=...)`; `_record_exploratory`, `_record_ceec`,
  `research_report` ledger block, `training.ceec_campaign` (scratch
  role), and `evolution._scoped_decision` migrated onto Session.
- `computronium/ceec` shim emits DeprecationWarning; legacy probes
  (`x_ali/x_sta/x_tac/x_tpc/x_rse_001`) import `ceec` directly.

**Phase H — domain-enablement proof (landed)**
- `tests/ceec/test_domain_profile.py`: sentiment-eval profile (own scope
  dims, `cheap/standard/sweep` tiers) runs experiment → run → promotion
  → calibration → clean `close_round` with zero core changes.
- `CEEC.md` architecture section + `docs/research/todo24/ceec_guide.md`
  walkthrough rewritten on Profile/Session (legacy store walkthrough
  retained below the fold).

**Verification:** ceec suites 154 passed (tests/ceec +
packages/ceec-core/tests); lab suite 164 passed; platform parity +
boundary tests green; ruff clean on all touched trees; pyright clean on
ceec-core.

**Phase S — composed backbone+ψ + H24.3 round 2 (landed)**

- T26.S.1: `recipes.build_temporal_psi` now returns a **composed
  system** (trainable θ feedforward feature extractor + ψ-owned readout
  role via the P-axis plasticity primitives) instead of the bare
  `AdaptivePsiReadout`. Catalog provenance updated; `trainable_on`
  intentionally stays empty (CampaignFitness is not the mechanism's
  registered surface; task-A `lab.train` feeds the continual path).
- Root-cause fix en route: `adaptation.adapt` discarded ψ statistics
  between calls (fresh `initial_psi` per episode), so the corpus
  per-episode loop re-solved the ridge from one 32-sample batch every
  episode (val 0.19 despite a direct 192-sample ridge hitting 0.95).
  `adapt`/`Lab.adapt` now accept a carried `psi` dict and
  `AdaptationResult.psi` returns the stepped state — the law's
  `G_t = ρG_{t−1} + …` cumulative contract. `corpus._adapt_tracked`
  carries ψ across episodes (and through the zero-episode val probes).
- T26.S.2: `temporal_psi_task_switcher` rides the registered continual
  corpus benchmark end-to-end (`test_benchmark_continual_composed_psi`:
  threshold reached, θ bitwise invariant, beats frozen_no_psi).
- T26.S.3: `scripts/probes/todo26_h243_round2.py` — the first
  end-to-end certification on the Session API (pre-register → §22
  decision → probe → artifact → evidence → calibration). Certified
  round-2 verdict on `two_task_switch`, 3 seeds × 10 episodes, ledger
  `scratch/todo26_h243_round2.sqlite3`: best ψ mode conflict_adaptive
  0.729 (threshold 3/3 seeds, θ invariant) vs frozen_no_psi 0.234 vs
  θ-finetune 0.979 — **AGAINST** under the round-1 rule (ψ beats frozen
  but not the θ-update control at this operating point). H24.3 moves
  from BLOCKED to certified-verdict; hypothesis stays open for other
  curricula and speed-based (episodes-to-threshold) rules.
- T26.S.4: round-1 "instrument ≠ registered benchmark" caveat recorded
  in `docs/research/todo24/hypotheses/H24.3.md` alongside the round-2
  result; round-1's 0.125 is explicitly marked unciteable as a ψ bound.

**Session A follow-ons (improvements #3/#5/#6 landed)**

- CLI `ceec close-round` (`--profile`, `--role`, `--fail-on-trigger`):
  renders + audits + flags; non-zero exit on triggers (T26.D.3 CLI
  slice). Smoke-tested against the round-2 campaign ledger (clean).
- `CEECStore.commit()` public flush; `corpus` drops the last
  `store._conn` private access outside the store package.
- `builders.TIER_BUDGET` deleted: tier is the budget literal; ladders
  live only on `Profile.tier_budget`. `builders.experiment` passes
  domain budget vocabulary through (profile validates at the store
  boundary); `Session.experiment` gained
  `falsification_criterion`/`overturn_criterion`/`hard_gates`.
- `Session.run` gained `decision_rationale` (probe parity with
  `run_experiment`).

**Toolchain repair (env skew, landed this session):** ruff 0.15 rejects
descriptive-name selectors — `pyproject.toml` ignore lists converted to
canonical codes (44 entries) and the `# ruff: ignore[rule-name]`
directives on touched files converted to `# noqa: CODE`. The remaining
~1.5k legacy directives across untouched modules are Register C work
(lint currently only honored on touched trees).

**Verification:** ceec suites 154 passed (tests/ceec +
packages/ceec-core/tests); lab suite 165 passed (incl. the new composed
mechanism + continual benchmark tests); ruff clean on all touched
files. Pyright on ceec/lab trees is blocked by the same env import
resolution skew as the LSP (Register C).

**Phase S — closed.** Remaining round work: Register C hygiene only.

---

### 💡 Improvements discovered this session

1. **Landed:** `Session.decide`'s focus pre-check shares the constraint
   results with the recorded decision — the fallback rationale cites the
   exact failed constraint names (`focus X fell back to default
   selection (failed: seed_plan_present)`).
2. **Landed:** quality-schema enforcement keeps an open map for
   undeclared keys (live ledgers carry `verification_level` etc.);
   `not_run` added to the audit alphabets as a first-class pre-hunt
   state instead of forcing a false "fail".
3. **Landed — CLI `close-round`:** `ceec close-round --profile <yaml>
   --role <role> --fail-on-trigger` renders + audits + flags with
   non-zero exit on triggers.
4. **Landed — psi carry + composed mechanism:** `adapt(psi=…)` seeds a
   carried ψ state; the composed backbone+ψ system replaced the bare
   `AdaptivePsiReadout` (S.1); the legacy probe adapter's
   `record_probe_result` hand-assembly remains the only non-Session
   ingest site (route through `Session.evidence` next hygiene pass).
5. **Landed — builders TIER_BUDGET deleted:** tier is the budget
   literal; ladders live only on `Profile.tier_budget`.
6. **Landed — measurement-block commit:** `CEECStore.commit()` public
   flush; no `_conn` access outside the store package remains.
7. **Open — `Scope.dims` typing:** dims values are `object` (spec §6
   open map) rather than the planned `str | tuple[str, ...]` because
   legacy `extra` dicts must survive the one-way absorption; tighten
   after the legacy-row window closes (Phase H+).
8. **Open — H24.3 round 3 rule refinement:** round 2 scored mean
   post-switch accuracy; the registered hypothesis is about *speed*
   (episodes to threshold under matched compute). A round-3 pre-
   registration with an episodes-to-threshold decision rule (and/or a
   second curriculum) is the natural next scientific step — the ψ arm
   already reaches threshold within the budget, so the speed comparison
   is measurable on the same instrument.
9. **Open — Register C, ruff 0.15 directive migration:** ~1.5k legacy
   `# ruff: ignore[rule-name]` comments and per-file-ignores outside the
   trees touched this session still use descriptive names; ruff 0.15
   only honors canonical codes. Also: `tests/ceec/test_integration_loop.py`
   and `packages/computronium-lab/tests/test_integration_loop.py`
   share a basename and cannot be collected in one pytest invocation
   (rename one).

---

## 18. Implementation notes

- **Migration discipline:** every phase keeps the previous import paths
  working one phase (wrappers/re-exports), then deletes them — per AGENTS
  no-backwards-compat, the deletion is not deferred beyond the next phase.
- **Existing ledgers:** `scratch/todo24_h24.sqlite3` / `todo25_parity.sqlite3`
  predate `policy_version`; their rows read as version `null` = pre-T26
  semantics (vacuous-override caveat already documented in TODO25 #8).
  Schema migration must be additive only (append-only invariant).
- **`chance_verdict`** lands as both `ceec.stats.chance_verdict` (pure
  function, probe-facing) and a registered `chance_band` operator
  (ledger-facing); one implementation, two surfaces.
- **`render_ledger` read-only default preserved**; rollup-as-Derived and
  `audit_decisions(record=True)` remain the only write paths beyond
  experiments.
- **Probe conventions carried:** probes live in `scripts/probes/` with
  measured-regime numbers and citing demos; new probes ride `Session.run`.
- **Out of scope:** PyPI publishing; portfolio budgeting (§22.4 greedy is
  compliant); any real second domain beyond the Phase H fixture.
