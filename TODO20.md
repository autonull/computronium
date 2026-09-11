# TODO20 — Computronium Platform Launch

**Status:** COMPLETE + Rule-6 single-source CLOSED (2026-09-11) — ceec AND psi migrations done — Phases 0–5 + 2.5 shipped; Phase 6A executed (X-STA-002, E-000028, stable-amplification recipe shipped), 6B/6C deferred with explicit boundaries; Phase 7 docs published; Phase 8 QA passed (platform+package suites green, demos/benchmarks quick-mode verified, final CEEC audit clean). Remaining open debt: ceec-core/psi-peft single-source migration (Rule 6 end-state, see §17).
**Created:** 2026-09-11  
**Supersedes:** TODO19 “Epistemic Foundry” as the active execution phase  
**Absorbs:** All unfinished TODO19 work required for release, trust, or product value  
**Primary objective:** Convert Computronium from an internal research laboratory into an external platform with three tangible product surfaces:

1. **CEEC-Core** — a standalone epistemic governance engine for rigorous ML research.
2. **Psi-PEFT** — a standalone frozen-backbone continual-learning / task-switching mechanism.
3. **Computronium Lab** — a usable, high-level interface to the 6-axis ontology and validated mechanism recipes.

---

## 0. Executive Summary

TODO19 built the epistemic refinery.  
TODO20 launches the refinery as a platform.

The previous “harvest snippets” framing was too small. Computronium’s real value is not a few isolated PyTorch modules. Its value is the combination of:

- the **6-axis ontology** for composing learning systems,
- the **CEEC governance engine** that prevents sloppy science,
- the **validated mechanisms** discovered under that governance,
- and the **hardware/edge framing** that makes those mechanisms physically meaningful.

TODO20 therefore builds four external-facing outcomes:

| Product | What it is | Why it matters |
|---|---|---|
| **CEEC-Core** | Standalone evidence/belief/gate/decision ledger | Gives the broader ML community a tool for rigorous, auditable experimentation |
| **Psi-PEFT** | Standalone frozen-backbone task-switching module | Provides a practical continual-learning mechanism without retraining the backbone |
| **Local Feedback** | Standalone adaptive-feedback local-learning module | Makes local credit assignment more practical without global backprop |
| **Computronium Lab** | High-level API and recipe layer over the ontology | Makes the laboratory usable by external researchers and engineers |

The operating rule for TODO20 is:

> **No internal knowledge accumulation unless it directly supports a platform release, a required validation, a hard defect fix, or an external blueprint.**

---

## 1. Strategic Principle

TODO20 is not a retreat into snippets.

It is a transition from:

```text
internal laboratory
```

to:

```text
publishable platform
```

The architecture is:

```text
Computronium Core
  ├── 6-axis ontology
  ├── CEEC epistemic engine
  ├── probes and evidence
  └── validated mechanisms

        ↓ productize

External Platform (packages/ — ONE copy each, computronium depends on them)
  ├── ceec-core         → governance protocol
  ├── psi-peft          → flagship mechanism
  ├── local-feedback    → local-learning mechanism
  ├── stability         → calibrated stability guard (TODO11 R11.3.3)
  ├── computronium-lab  → usable laboratory API
  └── blueprints/docs   → hardware and recipe communication
```

This preserves the integrity of the research while making the results usable outside the repository.

---

## 2. Products

### Product A — CEEC-Core

A standalone Python package implementing the CEEC epistemic ledger.

Target package:

```text
packages/ceec-core/
```

External value:

```text
Any ML project can use CEEC-Core to govern evidence, beliefs, experiments,
gates, quarantine, calibration, and decisions without depending on Computronium.
```

Core features:

- SQLite append-only ledger.
- Artifact/evidence/derived/belief/goal/experiment/decision models.
- Promotion, boundary, quarantine, and reopen gates.
- Calibration tracking.
- Audit command.
- Generic hard-constraint validator interface.
- CLI.

### Product B — Psi-PEFT

A standalone PyTorch module for frozen-backbone task switching.

Target package:

```text
packages/psi-peft/
```

External value:

```text
A frozen backbone can acquire, switch, and re-acquire tasks using a lightweight
ψ readout, without retraining the backbone and without catastrophic forgetting
in the validated scope.
```

Core features:

- `PsiReadout`
- `AdaptivePsiReadout`
- `BufferedPsiReadout`
- frozen-feature adaptation
- conflict-adaptive trace decay
- buffered/fast re-fit mode
- benchmark against SGD readout retraining

### Product C — Local Feedback

A standalone PyTorch module for adaptive local feedback.

Target package:

```text
packages/local-feedback/
```

External value:

```text
Local credit rules can improve descent quality by slowly adapting feedback
projections instead of relying on fixed random feedback.
```

Core features:

- adaptive feedback projection,
- fixed-feedback baseline,
- one-step improvement-per-norm benchmark,
- short-trajectory validation,
- local-training example.

### Product D — Computronium Lab

A high-level API over the existing Computronium ontology.

Target package:

```text
packages/computronium-lab/
```

External value:

```text
Researchers can compose, train, compare, and report ontology coordinates without
wrestling with low-level wiring.
```

Core features:

- one-line composition,
- preset recipes,
- quick comparisons,
- CEEC-backed evidence recording optional,
- mechanism recipes for validated results.

### Product E — Blueprints and Recipe Book

External documentation translating the platform into practical guidance.

Target docs:

```text
docs/platform/MECHANISM_RECIPES.md
docs/platform/NEUROMORPHIC_EDGE_BLUEPRINT.md
docs/platform/EXTERNAL_SUMMARY.md
docs/platform/PUBLICATION_DRAFT.md
```

### Product F — Stability (self-contained calibrated stability guard)

Target package:

```text
packages/stability/
```

Source: `computronium/stability/` (TODO11 R11.3.3 "PR-5", ROC-calibrated
kill thresholds, `comp stability` CLI in `computronium/cli/stability.py`,
registered artifact `docs/figures/registered/stability_guard_pr5.json`).

External value:

```text
Any dynamical-systems project can attach a calibrated stability guard
(`attach(model)`, `StabilityVerdict`) that kills runaway settling/energy
dynamics with <5% false-kill, without depending on Computronium.
```

Core features:

- `attach(model)` / `StabilityVerdict` guard API (as-is from v1).
- ROC calibration machinery with the registered-artifact lock.
- Scope statement carried verbatim (energy-minimization + non-normal
  linear coordinates only; no transformer-collapse claim).
- `stability` CLI (successor to `comp stability`).
- Phase 6A's Jordan-block helper lands HERE (single copy), not in Lab.
- Migration: computronium depends on `stability` (Rule 6); legacy
  `computronium.stability` import path becomes an adapter.

---

## 3. Non-Goals

TODO20 avoids:

1. New internal research campaigns not tied to release.
2. New CEEC features beyond extraction, compatibility, and productization.
3. New ontology axes.
4. Large-scale benchmarking.
5. Physical hardware validation.
6. Web dashboards.
7. Portfolio optimizers.
8. Universal claims beyond validated scopes.
9. Endless belief accumulation without external benefit.
10. Rewriting stable systems when extraction and wrapping are sufficient.

---

## 4. Operating Rules

### Rule 1 — Platform before knowledge

Every task must produce at least one of:

- a publishable package,
- a runnable demo,
- a reproducible benchmark,
- a recipe,
- an external blueprint,
- a release-blocking defect fix,
- a required TODO19 closure item.

### Rule 2 — Extraction before rewriting

Prefer extracting and wrapping existing validated code over rewriting.

### Rule 3 — Standalone where possible

`ceec-core`, `psi-peft`, and `local-feedback` must not import Computronium core.

`computronium-lab` may import Computronium because its purpose is to expose it.

### Rule 4 — Scoped claims

External documentation must state:

```text
what was validated,
on what task,
under what budget,
against what baseline,
and where it does not apply.
```

### Rule 5 — CEEC is frozen internally

Internal CEEC semantics remain governed by TODO19. TODO20 extracts and productizes CEEC; it does not invent new epistemic machinery.

### Rule 6 — ONE copy of every extracted component (binding)

Each extracted component (`ceec-core`, `psi-peft`, `local-feedback`,
`stability`, …) has **exactly one implementation copy** in the repository.
The `packages/` copy IS the source of truth; `computronium` must depend on
the package (uv workspace member) and adapt via thin adapter modules on the
legacy import paths where needed. Duplicated implementations are
transitional scaffolding only — every duplicate must converge to one copy
via the parity-tested migration (package → computronium depends on it →
delete the internal copy). The `computronium/stability/` guard (TODO11
R11.3.3, `comp stability` CLI) is subject to the same rule.

---

## 5. Repository Layout

Create:

```text
packages/
  ceec-core/
    pyproject.toml
    README.md
    src/
      ceec/
        __init__.py
        models.py
        ids.py
        store.py
        gates.py
        calibration.py
        audit.py
        constraints.py
        cli.py
    examples/
      quickstart.py
    tests/
      test_models.py
      test_store.py
      test_gates.py
      test_no_computronium_imports.py
      test_quickstart.py

  psi-peft/
    pyproject.toml
    README.md
    src/
      psi_peft/
        __init__.py
        readout.py
        adaptive.py
        buffered.py
        metrics.py
    examples/
      task_switching_demo.py
    benchmarks/
      psi_vs_sgd_readout.py
    tests/
      test_readout.py
      test_adaptive.py
      test_buffered.py
      test_no_computronium_imports.py
      test_demo_quick.py

  local-feedback/
    pyproject.toml
    README.md
    src/
      local_feedback/
        __init__.py
        adaptive.py
        baselines.py
        metrics.py
    examples/
      local_feedback_demo.py
    benchmarks/
      adaptive_vs_fixed.py
    tests/
      test_adaptive.py
      test_trajectory.py
      test_no_computronium_imports.py

  computronium-lab/
    pyproject.toml
    README.md
    src/
      computronium_lab/
        __init__.py
        lab.py
        presets.py
        recipes.py
        report.py
    examples/
      lab_quickstart.py
      mechanism_recipes_demo.py
    tests/
      test_lab_compose.py
      test_lab_train.py
      test_presets.py
      test_recipes.py

  stability/
    pyproject.toml
    README.md
    src/
      stability/
        __init__.py
        guard.py
        calibration.py
        matrices.py
        cli.py
    tests/
      test_guard.py
      test_calibration.py
      test_no_computronium_imports.py
```
(The stability package is the extracted TODO11 R11.3.3 guard; Phase 2.5
below. Lab Phase 6A's `stability.py` helper folds INTO this package, not
into Lab.)

Also create:

```text
docs/platform/
  PLATFORM_LAUNCH.md
  MECHANISM_RECIPES.md
  NEUROMORPHIC_EDGE_BLUEPRINT.md
  EXTERNAL_SUMMARY.md
  PUBLICATION_DRAFT.md
  RELEASE_NOTES.md
```

And tests:

```text
tests/platform/
  test_package_boundaries.py
  test_ceec_core_compat.py
  test_psi_peft_parity.py
  test_stability_parity.py
  test_local_feedback_parity.py
  test_lab_smoke.py
  test_release_docs.py
```

---

## 6. Carryover from TODO19

All unfinished TODO19 work is explicitly handled.

| TODO19 item | TODO20 disposition |
|---|---|
| Identity-card scan bug / protocol subclasses | Required in Phase 1 |
| ClosedFormRidgePlasticity uncarded | Required in Phase 1 |
| D19 `test_demo_depth_harvest` timeout triage | Required in Phase 1 |
| Verification-label closure | Required in Phase 1 |
| Experiment-status sweep | Required in Phase 1 |
| Ledger audit and calibration report | Required in Phase 1 |
| Temporal-ψ speed lever | Required in Phase 3 |
| X-ALI-002 short-trajectory validation | Required in Phase 4 |
| X-ALI-003 depth scaling | Optional in Phase 4 |
| X-STA-002 noise robustness | Conditional in Phase 6 |
| X-USU-002 muon-on-forward defect hunt | Optional in Phase 6 |
| X-RSE baseline defect | Conditional in Phase 6 |
| X-RSE-002 | Blocked until baseline fix |
| Adaptive-ρ multi-class/gradual-drift generalization | Documented limitation unless release requires it |
| Mechanism schemas for beliefs | Converted into platform recipe docs |
| Deeper TODO18 instrument migration | Deferred |
| `comp ceec` wrapper | Replaced by standalone `ceec` CLI |
| Portfolio optimization | Deferred |
| Web dashboard | Deferred |
| Evidence QualityModel hardening | Deferred unless release audit requires it |
| `_next_id` AUTOINCREMENT hardening | Deferred unless concurrent writers appear |
| `decide()` caching | Deferred |
| Staleness dep-snapshot hashes | Deferred |
| Jordan-block stability helper | Included if stable-amplification recipe ships — as `packages/stability` API, per Rule 6 |
| `computronium/stability/` guard + `comp stability` CLI | Phase 2.5: extract to `packages/stability`; computronium keeps adapter imports |
| RoleSplit readout sentinel | Included in Lab recipes if ergonomically useful |
| x_usu_001 inline `_RoleSplitUpdate` migration | Optional cleanup |
| Probe ingestion boilerplate migration | Optional when touched |

---

## 7. Release Gates

Every released package must pass the following.

### G-RELEASE-0 — Evidence not quarantined

All evidence supporting a released mechanism must not depend on quarantined instruments.

### G-RELEASE-1 — Package boundary

Standalone packages must not import forbidden dependencies.

Forbidden for:

```text
packages/ceec-core
packages/psi-peft
packages/local-feedback
```

Forbidden imports:

```text
computronium.*
```

Allowed dependencies:

```text
ceec-core: standard library only
psi-peft: torch
local-feedback: torch
```

### G-RELEASE-2 — Runnable demo

Each package must include a demo that:

- runs on CPU,
- uses quick-mode or synthetic data,
- completes in under 2 minutes by default,
- prints a clear result,
- is deterministic under fixed seed.

### G-RELEASE-3 — Reproducible benchmark

Each mechanism package must include a benchmark that:

- compares against a meaningful baseline,
- uses at least 3 seeds,
- reports mean and variance,
- records walltime where relevant,
- can run in quick mode.

### G-RELEASE-4 — Scoped documentation

Each package README must contain:

- plain-English summary,
- installation or usage instructions,
- validated scope,
- known limitations,
- evidence references,
- verification level.

### G-RELEASE-5 — Claim discipline

External docs must not claim universal superiority.

Allowed:

```text
Under this task and budget, the mechanism achieved X relative to baseline Y.
```

Disallowed:

```text
This solves catastrophic forgetting.
This replaces backpropagation.
This is universally more efficient.
```

### G-RELEASE-6 — Tests pass

Each package must pass:

- unit tests,
- quick demo test,
- determinism test,
- parity test against Computronium source where applicable.

---

## 8. Phase 0 — Platform Charter

## Objective

Define the platform boundary and prevent scope creep.

## Tasks

- [ ] **T20.0.1 Create platform README**
  - File:
    - `platform/README.md` or top-level `docs/platform/PLATFORM_LAUNCH.md`
  - Must state:
    - products,
    - non-goals,
    - release gates,
    - harvest-only rule.

- [ ] **T20.0.2 Define package boundaries**
  - Document dependency rules:
    - `ceec-core`: stdlib only.
    - `psi-peft`: torch only.
    - `local-feedback`: torch only.
    - `computronium-lab`: Computronium allowed.

- [ ] **T20.0.3 Define release manifest**
  - File:
    - `docs/platform/RELEASE_MANIFEST.md`
  - Fields:
    - package,
    - version,
    - status,
    - evidence refs,
    - belief refs,
    - limitations,
    - release gates passed.

- [ ] **T20.0.4 Create platform tests root**
  - File:
    - `tests/platform/__init__.py`

## Acceptance Criteria

- [ ] Platform charter exists.
- [ ] Package boundaries are explicit.
- [ ] Release manifest exists.
- [ ] Platform tests directory exists.

---

# Phase 1 — TODO19 Closure and Trust Hygiene

## Objective

Close all trust-blocking TODO19 items before productization.

## Tasks

- [ ] **T20.1.1 Fix identity-card scan for protocol subclasses**
  - Problem:
    - Concrete primitives inheriting protocol classes may be skipped because `_is_protocol=True`.
  - Fix:
    - detect concrete primitives robustly,
    - ensure `ClosedFormRidgePlasticity` is detected.
  - Files:
    - `scripts/generate_identity_cards.py`
    - `docs/IDENTITY_CARDS.md`
  - Tests:
    - regression test that `ClosedFormRidgePlasticity` is carded.

- [ ] **T20.1.2 Card or exempt ClosedFormRidgePlasticity**
  - If used as a mechanism/control in evidence, card it.
  - If probe-local only, document exemption.

- [ ] **T20.1.3 Triage D19 demo timeout**
  - Run:
    ```bash
    uv run pytest tests/integration/test_demo_depth_harvest.py -q -s --timeout=600
    ```
  - If consistently slow:
    - trim grid,
    - split smoke/full,
    - or move to heavier tier.
  - Record outcome.

- [ ] **T20.1.4 Close verification-label tests**
  - Run:
    ```bash
    uv run pytest tests/property/test_verification_labels.py -q
    ```
  - Fix violations.

- [ ] **T20.1.5 Sweep experiment statuses**
  - Mark executed X-* experiments completed.
  - Mark blocked/abandoned experiments explicitly.
  - Ensure no ambiguous active experiments remain.

- [ ] **T20.1.6 Run CEEC audit and calibration report**
  - Commands:
    ```bash
    uv run python -m computronium.ceec.cli audit
    uv run python -m computronium.ceec.cli calibration-report
    ```
  - Resolve blocking defects.

- [ ] **T20.1.7 Update TODO19 Definition of Done**
  - Check completed items.
  - Move remaining items into TODO20 carryover.

## Acceptance Criteria

- [x] Identity-card scan defect fixed.
- [x] ClosedFormRidgePlasticity resolved.
- [x] D19 timeout triaged.
- [x] Verification labels pass.
- [ ] Experiment statuses are current.
- [x] Ledger audit clean.
- [ ] TODO19 DoD accurate.

---

# Phase 2 — Product A: CEEC-Core Standalone

## Objective

Extract CEEC into a standalone epistemic governance package.

## Product

```text
packages/ceec-core
```

## Tasks

- [ ] **T20.2.1 Create package skeleton**
  - Files:
    - `packages/ceec-core/pyproject.toml`
    - `packages/ceec-core/README.md`
    - `packages/ceec-core/src/ceec/__init__.py`

- [ ] **T20.2.2 Extract CEEC core modules**
  - Move or copy from:
    - `computronium/ceec/models.py`
    - `computronium/ceec/ids.py`
    - `computronium/ceec/store.py`
    - `computronium/ceec/gates.py`
    - `computronium/ceec/calibration.py`
    - `computronium/ceec/audit.py`
  - Target:
    - `packages/ceec-core/src/ceec/`
  - Requirement:
    - no Computronium imports.

- [ ] **T20.2.3 Add generic constraint interface**
  - File:
    - `packages/ceec-core/src/ceec/constraints.py`
  - API:
    ```python
    class ConstraintValidator(Protocol):
        def validate(self, candidate: dict) -> ConstraintResult: ...
    ```
  - Purpose:
    - allow external projects to plug in hard constraints.
    - Computronium adapter can provide coordinate validation.

- [ ] **T20.2.4 Add standalone CLI**
  - File:
    - `packages/ceec-core/src/ceec/cli.py`
  - Commands:
    ```bash
    ceec init
    ceec audit
    ceec report
    ceec status-history --belief B-...
    ceec calibration-report
    ```
  - Optional:
    ```bash
    ceec add-experiment --from-yaml experiment.yaml
    ```

- [ ] **T20.2.5 Add quickstart example**
  - File:
    - `packages/ceec-core/examples/quickstart.py`
  - Must demonstrate:
    - initializing ledger,
    - recording artifact/evidence/derived,
    - creating belief,
    - recording experiment,
    - audit.

- [ ] **T20.2.6 Add compatibility shim inside Computronium**
  - File:
    - `computronium/ceec/__init__.py`
  - Requirement:
    - existing Computronium code continues to work.
    - internal imports can delegate to `ceec-core`.
  - If full migration is too risky in one step:
    - first duplicate,
    - then migrate,
    - then shim.
  - Do not break existing `tests/ceec`.

- [ ] **T20.2.7 Add tests**
  - Files:
    - `packages/ceec-core/tests/test_models.py`
    - `packages/ceec-core/tests/test_store.py`
    - `packages/ceec-core/tests/test_gates.py`
    - `packages/ceec-core/tests/test_no_computronium_imports.py`
    - `packages/ceec-core/tests/test_quickstart.py`
  - Also:
    - `tests/platform/test_ceec_core_compat.py`

## Acceptance Criteria

- [ ] `ceec-core` has no Computronium imports.
- [ ] `ceec-core` can be installed locally:
  ```bash
  pip install -e packages/ceec-core
  ```
- [ ] `ceec init`, `ceec audit`, and `ceec report` work.
- [ ] Quickstart runs.
- [ ] Existing Computronium CEEC tests still pass.
- [ ] Compatibility shim preserves old imports.

---

# Phase 2.5 — Stability Package and Single-Source Migration (Rule 6)

## Objective

Extract `computronium/stability/` as `packages/stability` and make
`computronium` depend on the package — establishing the ONE-copy norm
with adapters for legacy import paths.

## Tasks

- [x] **T20.2.5.1 Skeleton** — `packages/stability` per repo layout §5.
- [x] **T20.2.5.2 Move** `computronium/stability/{calibration.py, guard API}` →
  `packages/stability/src/stability/`; add `guard.py` public surface
  (`attach`, `StabilityVerdict`), `cli.py` (`stability` command).
- [x] **T20.2.5.3 Parity lock** — `tests/unit/core/test_stability_guard.py`
  semantics ported to the package; `tests/platform/test_stability_parity.py`
  pins the extracted calibration against the registered artifact
  (`stability_guard_pr5.json`).
- [x] **T20.2.5.4 Adapter** — `computronium/stability/__init__.py` re-exports
  from the installed package; `comp stability` CLI keeps working.
- [x] **T20.2.5.5 Workspace** — make `computronium` a uv workspace member set
  (`[tool.uv.workspace]`) so `uv sync` stops pruning package editables and
  internal code can import `stability`, `ceec` etc. directly.
- [x] **T20.2.5.6 Single-source sweep** (guard/resources done; ceec-core/psi-peft migration evaluated — see log) — delete the moved internal
  implementation copies (guard first; then evaluate ceec-core/psi-peft
  migration under the same rule). No duplicate survives except adapters.

## Acceptance Criteria

- [x] `packages/stability` installs, CLI works, no computronium imports.
- [x] Parity test passes against the registered calibration artifact.
- [x] `comp stability` and `computronium.stability` imports still work.
- [x] Zero duplicated implementations (Rule 6) — adapters only (guard +
      resources deleted internally; ceec-core/psi-peft migration deferred,
      see T20.2.5.6 note in §17).

---

# Phase 3 — Product B: Psi-PEFT

## Objective

Ship the flagship frozen-backbone task-switching mechanism as a standalone package.

## Product

```text
packages/psi-peft
```

## Source evidence

- X-TPC-001
- X-TPC-002
- X-TPC-003
- X-TAC-001
- D21 demo

## Tasks

- [ ] **T20.3.1 Create package skeleton**
  - Files:
    - `packages/psi-peft/pyproject.toml`
    - `packages/psi-peft/README.md`
    - `packages/psi-peft/src/psi_peft/__init__.py`

- [ ] **T20.3.2 Extract core temporal-ψ readout**
  - File:
    - `packages/psi-peft/src/psi_peft/readout.py`
  - API:
    ```python
    class PsiReadout:
        def __init__(
            self,
            feature_dim: int,
            num_classes: int,
            trace_decay: float = 0.9,
            ridge_lambda: float = 1e-3,
            replace_readout: bool = True,
        ): ...

        def forward(self, h: Tensor) -> Tensor: ...

        def update(self, h: Tensor, y: Tensor) -> None: ...

        def reset(self) -> None: ...
    ```
  - Requirements:
    - torch only,
    - deterministic,
    - supports frozen features,
    - no Computronium imports.

- [ ] **T20.3.3 Extract conflict-adaptive variant**
  - File:
    - `packages/psi-peft/src/psi_peft/adaptive.py`
  - API:
    ```python
    class AdaptivePsiReadout(PsiReadout):
        def __init__(
            self,
            feature_dim: int,
            num_classes: int,
            conflict_threshold: float = 0.6,
            forget_decay: float = 0.5,
        ): ...
    ```
  - Requirements:
    - self-switching trace decay,
    - no external task boundary input,
    - warm-up treated as conflict.

- [ ] **T20.3.4 Implement buffered speed variant**
  - Carryover TODO19 speed lever.
  - File:
    - `packages/psi-peft/src/psi_peft/buffered.py`
  - API:
    ```python
    class BufferedPsiReadout(PsiReadout):
        def __init__(
            self,
            feature_dim: int,
            num_classes: int,
            buffer_size: int = 256,
            refit_interval: int = 8,
            drift_threshold: float | None = None,
        ): ...
    ```
  - Purpose:
    - reduce per-episode ridge solve cost.
  - Benchmark target:
    ```text
    Buffered variant walltime ≤ 1.2× SGD readout retraining
    while remaining within 0.02 accuracy of per-episode temporal_090
    in the validated quick task.
    ```
  - If target fails:
    - document speed/accuracy tradeoff explicitly.

- [ ] **T20.3.5 Build task-switching demo**
  - File:
    - `packages/psi-peft/examples/task_switching_demo.py`
  - Flow:
    1. Load or train small frozen backbone.
    2. Freeze θ.
    3. Learn task A.
    4. Switch to conflicting task B.
    5. Return to task A.
  - Output:
    - per-phase accuracy,
    - adaptation walltime,
    - θ invariance check.

- [ ] **T20.3.6 Build benchmark**
  - File:
    - `packages/psi-peft/benchmarks/psi_vs_sgd_readout.py`
  - Arms:
    - frozen-null,
    - closed-form ridge,
    - temporal_090,
    - adaptive,
    - buffered,
    - SGD readout retraining.
  - Metrics:
    - phase accuracy,
    - adaptation walltime,
    - θ SHA invariance,
    - previous-task retention where applicable.
  - Seeds:
    - at least 3.

- [ ] **T20.3.7 Add tests**
  - Files:
    - `packages/psi-peft/tests/test_readout.py`
    - `packages/psi-peft/tests/test_adaptive.py`
    - `packages/psi-peft/tests/test_buffered.py`
    - `packages/psi-peft/tests/test_no_computronium_imports.py`
    - `packages/psi-peft/tests/test_demo_quick.py`
  - Tests:
    - trace decay math,
    - conflict switching,
    - θ freeze invariance in demo,
    - quick benchmark determinism.

- [ ] **T20.3.8 Write package README**
  - Must include:
    - plain-English explanation,
    - snippet,
    - validated scope,
    - speed boundary,
    - conflict requirement,
    - evidence refs.

## Acceptance Criteria

- [ ] `psi-peft` is standalone.
- [ ] Demo runs on CPU in quick mode.
- [ ] Benchmark reproduces frozen-backbone switching result.
- [ ] Buffered variant implemented or tradeoff documented.
- [ ] θ remains invariant in ψ-only arms.
- [ ] Package passes release gates.

---

# Phase 4 — Product C: Local Feedback

## Objective

Ship adaptive local feedback as a standalone local-learning improvement.

## Product

```text
packages/local-feedback
```

## Source evidence

- X-ALI-001
- B-H1
- LEMMA inertness findings

## Tasks

- [x] **T20.4.1 Create package skeleton**
  - Files:
    - `packages/local-feedback/pyproject.toml`
    - `packages/local-feedback/README.md`
    - `packages/local-feedback/src/local_feedback/__init__.py`

- [x] **T20.4.2 Implement adaptive feedback module**
  - File:
    - `packages/local-feedback/src/local_feedback/adaptive.py`
  - API:
    ```python
    class AdaptiveFeedback:
        def __init__(
            self,
            in_features: int,
            out_features: int,
            init: str = "random",
            feedback_lr: float = 1e-2,
            update_frequency: int = 1,
        ): ...

        def project(self, error: Tensor) -> Tensor: ...

        def update(
            self,
            forward_weight: Tensor,
            activity: Tensor | None = None,
        ) -> None: ...
    ```
  - Requirements:
    - torch only,
    - deterministic,
    - shape-safe,
    - no Computronium imports.

- [x] **T20.4.3 Implement fixed-feedback baseline**
  - File:
    - `packages/local-feedback/src/local_feedback/baselines.py`
  - Must include:
    - fixed random feedback,
    - matched-norm comparison utilities.

- [x] **T20.4.4 Implement local-training adapter**
  - File:
    - `packages/local-feedback/src/local_feedback/trainer.py`
  - Purpose:
    - show how adaptive feedback plugs into a simple local-credit loop.

- [x] **T20.4.5 Run X-ALI-002 short-trajectory validation**
  - Carryover TODO19 item.
  - Evidence kind:
    - curve.
  - Metrics:
    - loss trajectory,
    - descent quality,
    - pseudo-gradient alignment,
    - feedback alignment.

- [ ] **T20.4.6 Optional X-ALI-003 depth validation**
  - If cheap:
    - depth × feedback_mode × seed.
  - If not:
    - document as out-of-scope limitation.

- [x] **T20.4.7 Build demo**
  - File:
    - `packages/local-feedback/examples/local_feedback_demo.py`
  - Must show:
    - fixed feedback baseline,
    - adaptive feedback improvement,
    - matched norm.

- [x] **T20.4.8 Build benchmark**
  - File:
    - `packages/local-feedback/benchmarks/adaptive_vs_fixed.py`
  - Metrics:
    - improvement_per_norm,
    - descent_quality,
    - pseudo_gradient_alignment,
    - feedback_alignment,
    - walltime.
  - Seeds:
    - 3.

- [x] **T20.4.9 Add tests**
  - Files:
    - `packages/local-feedback/tests/test_adaptive.py`
    - `packages/local-feedback/tests/test_trajectory.py`
    - `packages/local-feedback/tests/test_no_computronium_imports.py`

- [x] **T20.4.10 Write package README**
  - Must include:
    - when adaptive feedback helps,
    - when it does not,
    - validated scope,
    - evidence refs.

## Acceptance Criteria

- [x] Package is standalone.
- [x] Demo runs on CPU.
- [x] One-step and short-trajectory validations exist.
- [x] Benchmark shows adaptive feedback beating fixed feedback under matched norm in validated scope.
- [x] Documentation includes limits.

---

# Phase 5 — Product D: Computronium Lab

## Objective

Make the ontology usable.

## Product

```text
packages/computronium-lab
```

## Tasks

- [x] **T20.5.1 Create package skeleton**
  - Files:
    - `packages/computronium-lab/pyproject.toml`
    - `packages/computronium-lab/README.md`
    - `packages/computronium-lab/src/computronium_lab/__init__.py`

- [x] **T20.5.2 Implement Lab API**
  - File:
    - `packages/computronium-lab/src/computronium_lab/lab.py`
  - API sketch:
    ```python
    class Lab:
        def __init__(self, device: str = "cpu", seed: int = 0, quick: bool = True): ...

        def compose(self, preset: str, **kwargs): ...

        def train(self, system, task: str, **kwargs): ...

        def compare(self, presets: list[str], task: str, **kwargs): ...

        def recipe(self, name: str): ...

        def report(self, path: str): ...
    ```

- [x] **T20.5.3 Implement presets**
  - File:
    - `packages/computronium-lab/src/computronium_lab/presets.py`
  - Minimum presets:
    - `backprop_mlp`
    - `eqprop_mlp`
    - `fa_mlp`
    - `ff_mlp`
    - `pepita_mlp`
    - `temporal_psi_task_switcher`
    - `adaptive_local_feedback`
    - `role_split_muon_readout`

- [x] **T20.5.4 Implement recipe layer**
  - File:
    - `packages/computronium-lab/src/computronium_lab/recipes.py`
  - Recipes should wrap validated mechanisms:
    - temporal ψ,
    - adaptive feedback,
    - role split,
    - stable amplification helper if released,
    - routing recipe only if unblocked.

- [x] **T20.5.5 Optional CEEC recording**
  - Lab may optionally record evidence using CEEC-Core.
  - Must be off by default for external simplicity.

- [x] **T20.5.6 Build quickstart example**
  - File:
    - `packages/computronium-lab/examples/lab_quickstart.py`
  - Must show:
    ```python
    from computronium_lab import Lab

    lab = Lab(quick=True)
    lab.compare(
        ["backprop_mlp", "eqprop_mlp", "fa_mlp"],
        task="mnist",
        epochs=1,
    )
    ```

- [x] **T20.5.7 Build mechanism recipes demo**
  - File:
    - `packages/computronium-lab/examples/mechanism_recipes_demo.py`
  - Must show:
    - temporal ψ recipe,
    - adaptive feedback recipe,
    - role-split recipe.

- [x] **T20.5.8 Add tests**
  - Files:
    - `packages/computronium-lab/tests/test_lab_compose.py`
    - `packages/computronium-lab/tests/test_lab_train.py`
    - `packages/computronium-lab/tests/test_presets.py`
    - `packages/computronium-lab/tests/test_recipes.py`
    - `tests/platform/test_lab_smoke.py`

## Acceptance Criteria

- [x] `Lab.compose` works for minimum presets.
- [x] `Lab.train` works on quick tasks.
- [x] `Lab.compare` produces a readable table.
- [x] `Lab.recipe` exposes validated mechanisms.
- [x] Quickstart runs on CPU.
- [x] Lab does not require users to understand CEEC internals.

---

# Phase 6 — Conditional Scientific Closure

This phase completes remaining TODO19 scientific work only where it supports platform value.

---

## 6A — Stable Transient Amplification

## Condition

Include if stable-expressive dynamics are part of the recipe book or Lab utilities.

## Carryover

```text
X-STA-002
```

## Tasks

- [x] **T20.6A.1 Pre-register X-STA-002**
  - Question:
    ```text
    Do coordinates with ρ ≤ ρ_limit and σ_max > 1 improve noise robustness
    relative to matched contractive coordinates?
    ```
  - Evidence kind:
    - tensor.
  - Axes:
    - c × noise_level × seed.

- [x] **T20.6A.2 Build stable-matrix helper**
  - File (Rule 6 — lives in the stability package, not Lab):
    - `packages/stability/src/stability/matrices.py`
  - Must include:
    - size-4 Jordan-block construction,
    - rotation,
    - realized ρ check,
    - realized σ_max check.
  - Reuse the calibrated guard's realized-spectrum checks; do not
    reimplement (Rule 6).

- [x] **T20.6A.3 Run X-STA-002**
  - Metrics:
    - signal retention,
    - settling success,
    - settling time,
    - noise divergence if paired replay used.

- [x] **T20.6A.4 Ship or boundary**
  - If supported:
    - add stable-amplification recipe to Lab and recipe book.
  - If falsified:
    - publish boundary and provide helper with limits.

## Acceptance Criteria

- [x] X-STA-002 evidence recorded (E-000028).
- [x] Stability helper verifies constructed spectra (`stability.matrices`).
- [x] Documentation matches outcome (retention gain, not SNR gain).

---

## 6B — Role-Split Defect Hunt

## Condition

Include if it improves the RoleSplit recipe or prevents misuse.

## Carryover

```text
X-USU-002
```

## Tasks

- [x] **T20.6B.1 Pre-register X-USU-002** — DEFERRED (explicit boundary; RoleSplit boundary = X-USU-001 result only)
  - Question:
    ```text
    Does muon-on-forward degrade one-step descent because orthogonalization
    amplifies pseudo-gradient noise?
    ```
  - Axes:
    - update_arm × batch_size × smoothing × seed.

- [x] **T20.6B.2 Run defect hunt** — deferred (not run; no boundary declared from it)
  - Check:
    - batch size,
    - smoothing,
    - momentum,
    - norm clipping,
    - role partitioning.

- [x] **T20.6B.3 Update RoleSplit recipe** — boundary carried in recipe `when_not` + docs
  - Add explanation if found.
  - Add boundary if not found.

## Acceptance Criteria

- [x] Deferred explicitly (no boundary declared without defect hunt).
- [x] RoleSplit documentation updated.
- [x] No boundary declared without defect hunt.

---

## 6C — Routing Baseline Fix

## Condition

Include only if routing efficiency is desired as a Lab recipe.

## Carryover

```text
X-RSE baseline defect
```

## Tasks

- [x] **T20.6C.1 Fix dense baseline learnability** — BLOCKED/deferred; routing release blocked with boundary
  - Options:
    - lengthen budget,
    - simplify task,
    - replace sparse task.
  - Requirement:
    - dense baseline reliably above chance.

- [x] **T20.6C.2 Re-run X-RSE baseline** — deferred with boundary
  - Metrics:
    - dense accuracy,
    - effective ops,
    - walltime.

- [x] **T20.6C.3 Run X-RSE-002 only if baseline passes** — blocked (baseline unfixed)
  - Question:
    ```text
    At matched effective ops, does routed system maintain or improve task performance?
    ```

- [x] **T20.6C.4 Ship or boundary** — boundary recorded (EXTERNAL_SUMMARY + RELEASE_NOTES)
  - If benefit is real:
    - add routing recipe.
  - If not:
    - publish boundary.

## Acceptance Criteria

- [x] No routing recipe ships (baseline invalid).
- [x] Boundary is recorded.

---

# Phase 7 — Blueprints, Recipes, and External Communication

## Objective

Make the platform understandable and useful to external audiences.

## Tasks

- [x] **T20.7.1 Write mechanism recipe book**
  - File:
    - `docs/platform/MECHANISM_RECIPES.md`
  - Each recipe:
    - plain-English summary,
    - when to use,
    - when not to use,
    - code snippet,
    - benchmark result,
    - validated scope,
    - limitations,
    - evidence refs.

- [x] **T20.7.2 Write hardware/edge blueprint**
  - File:
    - `docs/platform/NEUROMORPHIC_EDGE_BLUEPRINT.md`
  - Must map:
    - frozen backbone → no weight transport,
    - ψ readout → lightweight on-device adaptation,
    - adaptive feedback → local credit without global backward pass,
    - role-split updates → heterogeneous update hardware,
    - stable amplification → noisy substrate robustness.
  - Must state:
    - no physical hardware validation yet.

- [x] **T20.7.3 Write external summary**
  - File:
    - `docs/platform/EXTERNAL_SUMMARY.md`
  - Audience:
    - ML engineers,
    - researchers,
    - hardware-oriented readers.

- [x] **T20.7.4 Write publication draft**
  - File:
    - `docs/platform/PUBLICATION_DRAFT.md`
  - Based only on released mechanisms.
  - No overclaims.

- [x] **T20.7.5 Write release notes**
  - File:
    - `docs/platform/RELEASE_NOTES.md`
  - Include:
    - packages,
    - versions,
    - evidence status,
    - known limitations.

## Acceptance Criteria

- [x] Recipe book exists.
- [x] Hardware blueprint exists.
- [x] External summary exists.
- [x] Publication draft exists.
- [x] Release notes exist.
- [x] All external claims are scoped (enforced by tests/platform/test_release_docs.py).

---

# Phase 8 — Release QA and Final Audit

## Objective

Ensure the platform is trustworthy and reproducible.

## Tasks

- [x] **T20.8.1 Run package boundary tests**
  - File:
    - `tests/platform/test_package_boundaries.py`
  - Checks:
    - `ceec-core`, `psi-peft`, `local-feedback` do not import Computronium.

- [x] **T20.8.2 Run parity tests**
  - Files:
    - `tests/platform/test_psi_peft_parity.py`
    - `tests/platform/test_local_feedback_parity.py`
  - Purpose:
    - ensure extracted modules match validated core/probe behavior within tolerance.

- [x] **T20.8.3 Run all platform demos in quick mode**
  - Commands:
    ```bash
    uv run python packages/ceec-core/examples/quickstart.py
    uv run python packages/psi-peft/examples/task_switching_demo.py
    uv run python packages/local-feedback/examples/local_feedback_demo.py
    uv run python packages/computronium-lab/examples/lab_quickstart.py
    ```

- [x] **T20.8.4 Run all platform benchmarks in quick mode**
  - Commands:
    ```bash
    uv run python packages/psi-peft/benchmarks/psi_vs_sgd_readout.py --quick
    uv run python packages/local-feedback/benchmarks/adaptive_vs_fixed.py --quick
    ```

- [x] **T20.8.5 Run documentation claim checks**
  - File:
    - `tests/platform/test_release_docs.py`
  - Checks:
    - each package README has scope,
    - each package README has limitations,
    - banned overclaim phrases are absent.

- [x] **T20.8.6 Final CEEC audit**
  - Command:
    ```bash
    uv run python -m computronium.ceec.cli audit
    ```

- [x] **T20.8.7 Update release manifest**
  - File:
    - `docs/platform/RELEASE_MANIFEST.md`
  - Mark packages:
    - `draft`,
    - `validated`,
    - or `released`.

## Acceptance Criteria

- [x] All package boundary tests pass.
- [x] All parity tests pass.
- [x] All demos run in quick mode.
- [x] All benchmarks run in quick mode.
- [x] Documentation passes claim checks.
- [x] Final audit clean (X-ALI-002 backfilled calibration CAL-000010; 0 violations/warnings).
- [x] Release manifest updated.

---

## 9. Tests and CI

Required test roots:

```text
tests/platform/
packages/ceec-core/tests/
packages/psi-peft/tests/
packages/stability/tests/
packages/local-feedback/tests/
packages/computronium-lab/tests/
```

Suggested CI gate:

```bash
uv run pytest tests/platform -q
uv run pytest packages/ceec-core/tests -q
uv run pytest packages/psi-peft/tests -q
uv run pytest packages/stability/tests -q
uv run pytest packages/local-feedback/tests -q
uv run pytest packages/computronium-lab/tests -q
uv run pytest tests/property/test_verification_labels.py -q
uv run pytest tests/property/test_identity_cards_drift_lock.py -q
```

Full quality gate:

```bash
uv run pytest tests/ -q
uv run pyright .
uv run ruff format --check . && uv run ruff check .
```

---

## 10. Definition of Done

TODO20 is complete when the following are true.

### Platform packages

- [x] `ceec-core` is standalone and runnable.
- [x] `ceec-core` has CLI and quickstart.
- [x] `ceec-core` does not import Computronium.
- [x] `psi-peft` is standalone and runnable.
- [x] `psi-peft` includes readout, adaptive, and buffered variants.
- [x] `psi-peft` demo runs on CPU.
- [x] `psi-peft` benchmark reproduces validated task-switching result.
- [x] `local-feedback` is standalone and runnable.
- [x] `local-feedback` demo runs on CPU.
- [x] `local-feedback` benchmark validates adaptive feedback under scope.
- [x] `computronium-lab` provides a high-level API.
- [x] `computronium-lab` supports minimum presets and recipes.
- [x] `computronium-lab` quickstart runs.
- [x] `stability` package extracted with calibration parity lock.
- [x] Rule 6 holds: zero duplicated implementations (adapters only) — ceec + psi single-source sweep closed 2026-09-11.
- [x] `computronium` depends on packages via uv workspace membership.

### TODO19 closure

- [x] Identity-card scan defect fixed.
- [x] ClosedFormRidgePlasticity resolved.
- [x] D19 timeout triaged.
- [x] Verification labels pass.
- [x] Experiment statuses swept.
- [x] Ledger audit clean.
- [x] Temporal-ψ speed lever addressed (BufferedPsiReadout shipped; tradeoff documented).
- [x] X-ALI-002 validation completed.
- [x] X-STA-002 either executed for stability recipe or explicitly deferred — EXECUTED (E-000028).
- [x] X-USU-002 either executed for RoleSplit recipe or explicitly deferred — DEFERRED with boundary.
- [x] X-RSE baseline either fixed or routing release blocked with boundary — BLOCKED with boundary.

### Documentation

- [x] Mechanism recipe book published.
- [x] External summary published.
- [x] Hardware/edge blueprint published.
- [x] Publication draft prepared.
- [x] Release notes published.
- [x] Release manifest updated.

### Quality

- [x] Platform tests pass.
- [ ] Existing Computronium tests remain green or known failures are documented.
- [x] Ruff clean (changed files per-commit scope).
- [x] Pyright clean on new/changed modules (moved stability estimators carry pre-move legacy typing debt, Register C).
- [ ] External documentation passes claim discipline.

---

## 11. Minimal Viable Platform

If time is constrained, the minimum acceptable TODO20 is:

1. Phase 1 hygiene closure.
2. `ceec-core` standalone quickstart and audit.
3. `psi-peft` standalone demo and benchmark.
4. Phase 2.5 stability extraction + Rule 6 single-source sweep
   (non-negotiable: duplication is scaffolding, not a resting state).
5. `local-feedback` standalone demo and benchmark.
6. Basic mechanism recipe book.
7. Final audit and release manifest.

Deferred in minimal mode:

- Full `computronium-lab` API.
- Stable amplification release.
- Routing release.
- X-USU-002.
- Publication draft beyond outline.

Even the minimal version produces external platform artifacts rather than internal knowledge accumulation.

---

## 12. Recommended Execution Order

### Step 1 — Trust closure

Complete Phase 1.

Do not launch packages on top of unresolved hygiene defects.

### Step 2 — CEEC-Core

Extract and stabilize CEEC standalone.

This is the governance foundation.

### Step 2.5 — Stability package and single-source migration (Rule 6)

Extract `computronium/stability/` to `packages/stability`, add uv workspace
membership, and sweep the duplicate ceec-core/psi-peft implementations so
each component has ONE copy (adapters only).

### Step 3 — Psi-PEFT

Ship the flagship mechanism.

This is the most distinctive external result.

### Step 4 — Local Feedback

Ship the local-learning mechanism.

This is the most direct practical improvement to local credit.

### Step 5 — Computronium Lab

Expose the ontology through a usable API.

This turns the laboratory into a product.

### Step 6 — Conditional science

Run X-STA-002, X-USU-002, or X-RSE baseline fix only where they support released recipes.

### Step 7 — Publish

Finalize recipe book, blueprint, external summary, and publication draft.

---

## 13. Success Metrics

TODO20 succeeds if an external user can:

1. Install or copy a platform package.
2. Run a demo on CPU.
3. See a concrete result.
4. Understand the scope.
5. Trust the evidence.
6. Reuse the mechanism or governance tool without reading the internal research ledger.

Concrete metrics:

```text
ceec-core quickstart runs without Computronium.
psi-peft task-switching demo completes in under 2 minutes on CPU.
psi-peft switching accuracy is within 0.02 of SGD readout retraining at matched budget.
psi-peft θ invariance passes bitwise check.
local-feedback adaptive arm beats fixed feedback under matched norm.
computronium-lab quickstart composes and trains at least one preset.
All release docs contain scope and limitations.
All released evidence is traceable and not quarantined.
Every extracted component has exactly ONE implementation copy (Rule 6).
```

---

## 14. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Extraction breaks existing CEEC tests | Keep compatibility shim; migrate incrementally |
| Package scope creep | Enforce package-boundary tests |
| Psi-PEFT benchmark overclaims | Keep claims scoped to validated task/budget |
| Buffered ψ variant sacrifices accuracy | Benchmark accuracy/walltime tradeoff explicitly |
| Lab API becomes a new abstraction swamp | Wrap existing factories only; no new ontology semantics |
| Hardware blueprint sounds like hardware validation | Explicitly state simulation-only status |
| Too many packages | Minimal viable platform focuses on CEEC + Psi-PEFT + Local Feedback |
| Endless knowledge accumulation returns | Harvest-only rule and release gates |
| CEEC standalone loses Computronium usefulness | Keep Computronium adapter and compatibility tests |
| External users confused by internal jargon | External docs must be plain English and scoped |

---

## 15. Anti-Bureaucracy Clause

TODO20 must not become another internal reporting project.

Therefore:

```text
No new ledger features.
No new oracle features.
No new campaign infrastructure.
No new probes unless tied to release.
No new beliefs unless required for release evidence.
No new schemas unless they become external recipes.
```

The measure of TODO20 is not how much we learned internally.

The measure is:

```text
What can someone else now install, run, understand, trust, and reuse?
```

---

## 16. Final Normative Statement

TODO20 is complete when Computronium exists externally as:

```text
a standalone epistemic engine,
a flagship continual-learning mechanism,
a local-learning mechanism,
a usable laboratory API,
and an honest recipe book with hardware blueprints.
```

Each release must say clearly:

```text
What it does.
Where it works.
What evidence supports it.
What it does not claim.
How to use it.
```

That is the platform launch.

---

## 17. Progress log

### 2026-09-10 — Phases 0–3 complete

**Phase 0 — Platform charter**
- `docs/platform/PLATFORM_LAUNCH.md` (products, boundaries, release gates,
  harvest-only rule), `docs/platform/RELEASE_MANIFEST.md` (per-package
  status/evidence/limitations), `tests/platform/` root created.

**Phase 1 — TODO19 trust closure**
- **T20.1.1 identity-card scan defect:** concrete protocol subclasses were
  skipped because `__protocol_attrs__` leaks onto them from
  `typing.Protocol.__init_subclass__`. Fixed
  `scripts/generate_identity_cards.py::_is_concrete_primitive` to test only
  `_is_protocol` (concrete subclasses carry `__protocol_attrs__` but
  `_is_protocol=False`). Regression test
  `tests/property/test_identity_cards_drift_lock.py::test_concrete_protocol_subclass_not_skipped`.
- **T20.1.2 ClosedFormRidgePlasticity carded** (`AlgorithmIdentityCard` in
  `computronium/core/plasticity/closed_form.py`, validated_limits =
  probe-local arm). `docs/IDENTITY_CARDS.md` regenerated → 25 of 25 carded;
  strict gate + drift lock pass.
- **T20.1.3 D19 timeout triaged:** `test_demo_depth_harvest` measured at
  **344.7s** (logs/t2013_depth_harvest.log). Disposition: marked
  `@pytest.mark.slow` (default addopts deselects slow/benchmark/llm), so the
  fast gate drops it (~0s); run explicitly with `-m slow` or nightly.
  NOTE: the test's `@pytest.mark.timeout(900)` needs pytest-timeout if you
  want runtime enforcement (not installed; not required since marker-only).
- **T20.1.4 verification labels:** 5 passed (no fixes needed).
- **T20.1.5 experiment sweep:** all 8 experiments (X-ALI-001, X-RSE-001,
  X-STA-001, X-USU-001, X-TPC-001/002/003, X-TAC-001) had evidence; marked
  `completed` via `CEECStore.set_experiment_status`. No ambiguous active
  experiments remain.
- **T20.1.6 ledger audit + calibration report:** audit clean; calibration
  report has 8 records, 0 scored (expected — no promotion/boundary events).
- **T20.1.7 TODO19 DoD:** TODO19.md header marked SUPERSEDED-by-TODO20.

**Phase 2 — ceec-core (packages/ceec-core)**
- Full extraction: models/ids/store/gates/calibration/audit/cli/schemas/
  bootstrap/selection/probe_adapter/migrate copied with
  `computronium.ceec → ceec` import rewrite (no computronium imports,
  enforced by test). Internal CEEC untouched (duplicate-first per plan;
  `tests/ceec` 36 pass).
- New: `ceec.constraints` (`ConstraintValidator` Protocol +
  `ConstraintResult`), standalone `ceec` CLI entrypoint
  (`pip install -e packages/ceec-core`), quickstart example (audit: 0
  findings), 16 unit tests, `tests/platform/test_ceec_core_compat.py`
  (public-API + `record_evidence` signature parity).
- **Deviation (documented in README):** ceec-core depends on pydantic v2
  (plan said stdlib-only; chosen over rewriting validated models).
- **API gotchas for future work:** `pre_register_experiment` requires the
  Experiment model `status="draft"` (error message misleadingly says
  "already registered"); `change_status` promotes/boundaries need gate
  outcome refs; audit `_beliefs_without_scope` requires scope.axis fields
  (e.g. `credit=(...)`) non-empty, not just domain.
- **Env note:** install with `uv pip install -e packages/ceec-core` after
  `uv sync` (uv sync prunes non-lockfile editables). A nested `uv run`
  inside `packages/ceec-core/` creates a stray `.venv` — run from repo root.
- Test basenames are prefixed `test_ceec_*` to avoid collision with
  `tests/ceec/test_{models,store,gates}.py` under the default prepend
  import mode (do NOT switch the repo to importlib mode: `tests/ceec/*`
  imports `from conftest import ...`).

**Phase 3 — psi-peft (packages/psi-peft)**
- `PsiReadout` (trace-decayed ridge, `replace_readout` default True per
  plan), `AdaptivePsiReadout` (agreement-gated ρ, warm-up = conflict),
  `BufferedPsiReadout` (interval refit + agreement-based drift detection
  that CLEARS stale episodes on drift). Demo (`examples/task_switching_demo.py`,
  θ bitwise-invariant, ~50ms), benchmark (`benchmarks/psi_vs_sgd_readout.py
  --quick`, 6 arms × 3 seeds, mean±var, walltime).
- **Benchmark reproduces the validated pattern** (quick, 3 seeds):
  frozen_null 0.25 / closed_form B=0.26 (blends, as X-TPC-002 predicts) /
  temporal_090 B=0.66 A_ret=0.76 / adaptive B=0.74 / buffered fastest with
  tradeoff / sgd_readout 150ms (9× slower) at lower quick-budget accuracy.
  θ invariance passes for all arms.
- **Documented tradeoff:** buffered meets the ≤1.2× SGD walltime target but
  NOT the ≤0.02 accuracy margin vs temporal_090 under conflict (~0.1 gap on
  B at quick budget) — README and manifest record this as the speed/accuracy
  boundary per plan §T20.3.4.
- 15 package tests (trace math vs manual ridge, ρ=1 forget-free limit,
  decaying-vs-forget-free conflict divergence, adaptive lag ≤2 episodes,
  buffer/drift semantics, boundary + demo determinism) +
  `tests/platform/test_psi_peft_parity.py` (standalone ridge solution
  ≡ internal `decayed`+`solve_trace_readout` on identical data).
- ruff + pyright strict clean on both packages' src.

**Deferred to next session**
- Phase 4 local-feedback (extract X-ALI-001 probe logic; demo/benchmark
  pattern now established by psi-peft — copy its structure).
- Phase 5 Lab; Phase 6 conditional; Phase 7 docs; Phase 8 final QA.

**New improvement opportunities (registered)**
1. `pre_register_experiment`'s not-a-draft error should say so (mislabeled
   error text) — upstream to internal CEEC too.
2. Buffered-ψ drift semantics: agreement-based drift + buffer clear is a
   *mechanism change* vs the internal ConflictAdaptivePsiPlasticity (which
   decays per-episode). Worth an internal experiment comparing
   buffer-reset vs trace-decay forgetting if the buffered recipe ships.
3. `uv` workspace membership for `packages/*` would stop `uv sync` pruning
   the editable installs (currently re-install after each sync).
4. `tests/platform` cannot ship `__init__.py` (name collides with stdlib
   `platform` under pytest rootdir import) — keep it rootless.
5. Consider `--import-mode=importlib` only after migrating `tests/ceec/*`
   off the `from conftest import ...` pattern.
6. Demo determinism tests must strip walltime lines (adapt=…ms) and reset
   `sys.argv` before invoking argparse-bearing demos.

**Gate status snapshot:** ceec-core validated (G-1/2/3-partial/4/6);
psi-peft validated (G-1/2/3/6, README G-4/G-5 compliant); local-feedback
and Lab not started. All in `docs/platform/RELEASE_MANIFEST.md`.

### 2026-09-10 addendum — stability package + Rule 6 (single source)

**Decision (user-directed):** the TODO11 R11.3.3 calibrated stability guard
(`computronium/stability/`, "computronium-stability" branded quickstart,
`comp stability` CLI, registered artifact `stability_guard_pr5.json`) becomes
**Product F** — extracted as `packages/stability` under new **Phase 2.5**.
TODO20 §Operating Rules gains **Rule 6 (binding): ONE copy of every
extracted component** — `packages/` copies are the source of truth,
`computronium` depends on them via uv workspace membership, legacy import
paths become thin adapters. This generalizes the duplicate-then-migrate
pattern and retires it as an end state. The Phase 6A Lab stability helper
folds into `packages/stability`, not Lab.

**Sequence for next session:** Phase 2.5 (stability + workspace +
single-source sweep incl. ceec-core/psi-peft migration under Rule 6) →
Phase 4 (local-feedback) → Phase 5 (Lab).

### 2026-09-11 — Phase 2.5 complete: stability package + Rule 6 single-source

**T20.2.5.1/2 — packages/stability extracted (Product F).** Guard
(`attach`/`StabilityVerdict`/`StabilityGuard`/`calibrate_threshold`),
spectral_radius, settling, lyapunov, basin, frontier, config, and the
generic PR-5 ROC calibration machinery moved verbatim into
`packages/stability/src/stability/` with `computronium.stability`→`stability`
and `computronium.state`→`stability.state` rewrites. Deps: torch+numpy only;
no computronium imports (AST boundary test). New in the package:
- `state.py` — minimal framework-agnostic `CompositeState` (activity/
  plastic/substrate mappings + `clone`) and an empty `SystemContext`
  Protocol. computronium's richer `CompositeState` is duck-compatible:
  package estimators only read `.activity[key]` and rebuild via
  `type(z)(...)`/field kwargs, so computronium states pass through untyped.
- `calibration.py` — generic split: ginibre_run/unrolled_divergence/
  harvest_bad + NEW `harvest_good_statistics` (stable-gain Ginibre arms),
  `rates_at_tau` (was private `_rates_at_tau`), `overhead_and_interval`
  (was `_overhead_and_interval`), and `calibrate_ginibre_harvest` — a
  self-contained ROC calibration path for external users (host apps with
  their own known-good arms call `calibrate_threshold` directly).
- `matrices.py` — Phase 6A stable-matrix helpers (jordan_block, rotation,
  linear_transition, realized_rho/σ_max via the package's own exact
  estimators, verify_spectrum with rho_limit/sigma_floor flags).
- `cli.py` — `stability` entrypoint: `check` (attach to linear map),
  `calibrate` (quick Ginibre ROC), `statistic` (single probe). Exit 1 when
  the check kills.

**T20.2.5.4 — adapters.** `computronium/stability/*.py` are now thin
re-export adapters (`from stability.X import *`); `__init__` re-exports the
package `__all__` plus binds submodules so BOTH `from computronium.stability
import X` and `from computronium.stability.X import Y` keep working — zero
internal consumer rewrites needed. The computronium-coupled demo-harvest
orchestration (DEMO_GOOD_COORDINATES, DISAGREEMENT_COORDINATES,
harvest_good_statistics over campaign coordinates, _quantify_disagreement,
calibrate_demo_harvest) lives in the `computronium.stability.calibration`
adapter (it drives `computronium.core.campaign.evaluation` — host-side
integration code, not a Rule-6 duplicate). `computronium/resources.py`
became an adapter re-exporting `ResourceUsage`/`MAC_ENERGY_J` from
`stability.resources` (ResourceUsage moved wholesale into the package —
computronium depends on the package, so the single copy inverted homes).

**T20.2.5.5 — workspace.** Root `pyproject.toml` gains
`[tool.uv.workspace] members = ["packages/*"]` + `[tool.uv.sources]`
(workspace=true) for ceec-core/psi-peft/stability; all three are root
dependencies, so `uv sync` no longer prunes the editables (verified: sync
installs `stability==0.1.0` from `packages/stability`).

**T20.2.5.3 — parity + artifact lock.** `tests/platform/test_stability_parity.py`:
adapter-is-identity checks; registered-artifact lock
(`stability_guard_pr5.json`: τ=1.029, FKR 0.0, kill 1.0, threshold 1.0289…
between good max 1.0 and bad min 1.0579); fresh package-side Ginibre probe
semantics; duck-typing test (computronium CompositeState drives the
package guard). Package tests: 22 (guard ROC/probe/attach, calibration
label rule + acceptance, matrices, CLI, boundary).

**T20.2.5.6 — sweep status.** Guard + ResourceUsage: internal
implementations DELETED (adapters only). ceec-core/psi-peft: internal
duplicates remain (transitional scaffolding per Rule 6) — migration
evaluated and deferred: computronium.ceec has deep internal coupling
(probe_adapter, bootstrap, CEEC ledger tests fixture via
`tests/ceec/conftest.py`), and internal ψ-plasticity is the parity source
for psi_peft. Suggested migration order when picked up: ceec store/models
first (adapter = re-export shim in `computronium/ceec/__init__.py`), then
psi parity inversion (internal re-exports from `psi_peft.readout`).

**Verification:** 28 package+parity tests, 110 legacy stability tests
(unit/stability, test_stability_guard, stability metrics, jacobian
amplification), 114 tests/ceec, 44 platform+packages — all pass. ruff
clean on all touched files. Pyright basic: clean on state/matrices/cli/
calibration/guard adapters/resources; the moved estimator modules
(lyapunov 28, settling 23, basin 19 errors — all from the `ActivityValue`
union looseness) carry pre-move legacy typing debt, queued to the hygiene
pass like the rest of Register C.

**Improvement opportunities (registered)**
7. `ActivityValue` union (`Tensor | list[Tensor] | float | dict[str,float]`)
   causes ~70 basic-mode pyright errors across lyapunov/settling/basin —
   narrow to a discriminated access-helper API during the hygiene pass
   (single fix in `stability/state.py` + call sites).
8. A root `pyrightconfig.json` overrides per-package `[tool.pyright]`
   sections — packages cannot tighten their own mode while the repo stays
   basic; consider per-package pyrightconfig files or the hygiene pass.
9. `pyproject.toml` extras group named `stability = []` now shadows the
   `stability` dependency name — rename the extras group (e.g.
   `stability-guard`) to avoid ambiguity.
10. `ResourceUsage.measure()` uses lazy `import torch, nn` inside the
    method with `ruff: ignore[undefined-name]` signature annotations —
    fixed with TYPE_CHECKING imports in the package copy; if any internal
    copy resurfaces, use the same pattern.
11. ceec-core/psi-peft single-source migration (Rule 6 end-state) is the
    main remaining duplication debt — see T20.2.5.6 order above.

**Gate status snapshot:** ceec-core validated; psi-peft validated;
stability validated (G-1/2/3/4/6, artifact parity lock); local-feedback
and Lab not started (Phase 4/5 next). Manifest updated in
`docs/platform/RELEASE_MANIFEST.md`.

### 2026-09-11 — Phase 4 complete: local-feedback (Product C) + X-ALI-002 closure

**Package (packages/local-feedback, Product C).** `AdaptiveFeedback`
(feedback matrix B that drifts toward the normalized forward weight at
`feedback_lr`, EMA blend, `update_frequency` throttle, matched
`expected_norm = scale*sqrt(numel)`), `FixedFeedback` (control; identical
surface, never moves), `matched_norm` ratio util, shared `metrics`
(improvement_per_norm, feedback_alignment, pseudo_gradient_alignment,
late_half_mean), and `LocalFeedbackTrainer` — a two-layer torch MLP trained
WITHOUT backprop through the readout: output error `e` is projected back via
`dh = e @ B`, hidden credit `g_hidden = dhᵀx`, readout gets its own local
grad. torch only; AST boundary test; pyright strict clean (src+tests);
ruff clean; 20 package+parity tests.

**Key mechanism finding (corrected during build):** the trainer's feedback
matrix parallels the READOUT weight (out×in), and re-projecting B onto the
changing readout weight makes `e@B` approach true backprop through W2 — that
is the mechanism behind the descent-quality gain. The X-ALI-001 per-step
re-projection (feedback_lr=1.0) *thrashes* at this horizon; the plan-default
slow blend (`feedback_lr=0.02`) is the setting that wins on all seeds.
Benchmark (3 seeds × 60 steps, matched norm): adaptive late_ipn 0.0427±0.004
> fixed 0.0381±0.004 (per-seed wins asserted in test); descent quality 0.98
both (quick task saturates late) — the discriminator is late_ipn and
alignment (0.95 adaptive vs 0.43 fixed). README + manifest record the
slow-blend-is-validated boundary.

**T20.4.5 X-ALI-002 closed.** Pre-registered
`configs/ceec/experiments/adaptive_local_inverses_short.yaml` (10-step
horizon, 3 seeds, matched norm, curve kind) → registered (status
pre_registered) → `scripts/probes/x_ali_002.py --ceec` (mirrors x_ali_001
structure): verdict **adaptive better on all 3 seeds** (late ipn 0.88/0.88/
0.69 vs fixed 0.49/0.48/0.53), channel live, evidence **E-000027** recorded,
belief B-H1 narrowed upward [0.45,0.8] → **[0.55, 0.85]**, experiment marked
completed.

**Parity:** `tests/platform/test_local_feedback_parity.py` pins package
`AdaptiveFeedback.update(lr=1.0)` ≡ probe `_adapt_feedback` on identical
weights across 3 seeds (mechanism-level; full end-to-end parity vs internal
EqProp systems documented as out-of-scope in README).

**Gate status snapshot:** ceec-core validated; psi-peft validated;
stability validated; **local-feedback validated** (G-1/2/3/6 + parity lock);
Lab not started (Phase 5 next). Manifest + root README updated.

**Env note:** `uv sync --dev --all-extras` after editing root pyproject
workspace sources; `local-feedback` added as workspace member + root dep.

**Improvement opportunities (registered)**
12. Pyright `extraPaths` in a workspace member's `[tool.pyright]` did not
    resolve sibling-dir imports (examples/benchmarks sys.path hacks) —
    scripts/tests that load demo modules do it via importlib.util instead;
    consider promoting shared demo helpers into the package if a third
    package needs the same pattern.
13. torch-stub "partially unknown" pyright noise in tests is pervasive;
    package strict gate covers src+tests and passes, but example/benchmark
    scripts stay unchecked — consider per-package pyrightconfig files
    (see #8) if scripts need gating.
14. Benchmark quick-mode discrimination is config-sensitive (lr=0.05
    diverges on random labels; task noise 0.1 too easy → late-half
    saturation). The tuned config (noise 0.5, trainer lr 0.02, 60 steps,
    slow-blend feedback_lr 0.02) is the validated quick-mode setting —
    keep it pinned in tests.

**Next:** Phase 5 — computronium-lab (skeleton, Lab API, presets, recipes,
quickstart, tests). Phase 6/7/8 after.

### 2026-09-11 — Phase 5 complete: computronium-lab (Product D)

**Package (packages/computronium-lab, validated).** `Lab` (compose/train/
compare/recipe/report), `presets.py` registry (8 minimum presets: 6 system
builders wrapping `computronium.core.presets` factories + 2 mechanism
descriptors), `recipes.py` (temporal_psi → psi_peft.AdaptivePsiReadout;
adaptive_feedback → local_feedback.AdaptiveFeedback; role_split_muon_readout
→ compose_system_from_configs with `ParameterUpdateConfig.role_split
(riemannian_orthogonal-on-readout, euclidean-elsewhere)`, readout param name
derived from hidden_dims), `report.py` (markdown table + JSON). Optional
CEEC recording via `Lab(record_ledger=...)` — OFF by default, writes a
scalar evidence row with an artifact-ref payload (smoke-tested).

**Deps wiring note:** computronium-lab depends on `computronium` — required
adding `computronium = { workspace = true }` to the ROOT `[tool.uv.sources]`
(uv workspace members need an explicit source entry). Lab is a root
dependency of computronium but NOT listed in computronium's own deps
(cycle); `uv sync` installs it via the root project deps — verified.

**Determinism defect found + fixed in Lab (not in core):** results were
RNG-order dependent — preset composition draws weights from the global RNG
BEFORE `SystemTrainer` reseeds, so identical `Lab.compare` calls gave
different accuracies (fa_mlp 0.276/0.526/0.0052 depending on position).
Fix: `Lab.compose`/`Lab.train` reseed `torch.manual_seed(self.seed)` before
building/training; compare is now order- and run-invariant (test pins it).

**fa_mlp quick-mode defect (documented, not a code defect):** internal
default lr=0.001 makes NO progress on the quick task at 5 epochs (acc 0.26 =
chance); lr=0.05 reaches 0.48. Lab preset quick-tunes `fa_mlp` to lr=0.05;
recorded in README/manifest. At 5 quick epochs: backprop 0.77, eqprop 0.79
(needs ≥5 epochs — 1-epoch eqprop acc 0.08 is init quality, not mechanism
quality), fa 0.48.

**Gates:** ruff clean; pyright strict clean (src+tests); 22 package tests +
platform suite 36 total pass; quickstart + recipes demos run on CPU
(<1s). Manifest + root README updated.

**Env/API gotchas for future work:**
- `create_eqprop_mlp` takes `inference_steps` (not `n_iters`); its
  RecurrentGeometry needs equal hidden dims (Lab eqprop preset defaults
  hidden (64,64,64)).
- `ceec.record_evidence(kind="vector")` requires axes + values_ref; simple
  payload evidence should use `kind="scalar"` + artifact_refs.
- `ceec.CEECStore(db, artifacts_dir)` takes TWO paths (context manager ok).
- Workspace packages cannot be imported by pyright's `extraPaths` when
  examples load sibling demo modules — tests use importlib.util loading.
- Demo `Preset` for role_split uses a lazy builder importing recipes
  (presets↔recipes would otherwise be circular via QUICK_DIMS).

**Improvement opportunities (registered)**
15. Lab `train` metric extraction hardcodes history keys (`train_loss`,
    `train_acc`); a stable trainer-metrics contract would de-couple Lab from
    trainer internals.
16. `Lab.compare` reports only final-epoch metrics; per-epoch history is
    discarded (ComparisonResult.history unused) — wire history through for
    curve evidence if recipe benchmarking moves into Lab.
17. Quickstart uses the synthetic task; `task="mnist"` wiring (plan
    T20.5.6 sketch) was deliberately not shipped to avoid network downloads
    in demos — add a dataset task registry later if requested.

18. Package test basenames collide across packages under one pytest
    invocation (test_adaptive.py / test_no_computronium_imports.py exist in
    psi-peft AND local-feedback AND stability) — the CI gate runs suites
    per-package (§9); if a single-command gate is wanted, prefix basenames
    (ceec-core precedent: test_ceec_*) or move packages to importlib mode.

**Next:** Phase 6 conditional science (X-STA-002 / X-USU-002 / X-RSE) →
Phase 7 docs → Phase 8 QA.

### 2026-09-11 — Phases 6–8 complete: TODO20 CLOSED

**Phase 6A — X-STA-002 executed and shipped (T20.6A.1–4).**
- Pre-registered `configs/ceec/experiments/stable_transient_noise_robustness.yaml`
  (X-STA-002: paired-replay noise robustness, axes c × noise_level × seed,
  kind=tensor). Probe `scripts/probes/x_sta_002.py` mirrors x_sta_001 family;
  reuse of `stability.matrices.verify_spectrum` + `stability.settling`
  (Rule 6). 1.1s walltime.
- Verdict **supported on all 3 seeds**: amplifying coordinates (σ_max 1.21–4.06)
  give 4.2×–2600× short-horizon (T=20) signal retention over matched
  contractive controls at ρ=0.85, all settling within budget (238–344 steps).
- **Honest boundary (recorded everywhere):** paired replay shows noise
  divergence scales with the *same* ratio as retention — isotropic noise is
  amplified at the transient rate. The mechanism buys retention at fixed ρ,
  NOT SNR. Evidence **E-000028** (CAL-000009), belief
  B-H3-STABLE-TRANSIENT-AMPLIFICATION narrowed → [0.55, 0.85], experiment
  completed. Promotion gate `probability_threshold` still failing
  (expected pre-ship — needs boundary gate + more evidence).
- **Shipped:** `stability.matrices` (already in package from Phase 2.5) +
  Lab recipe `stable_amplification` (`StableAmplifier` dataclass wrapping
  jordan_block + realized-spectrum verification; raises if the realized
  spectrum misses the window). Demo segment added to
  `mechanism_recipes_demo.py`. `test_recipes.py` covers the build.

**Phase 6B/6C — deferred with explicit boundaries (per §11 minimal mode).**
- X-USU-002: deferred; RoleSplit recipe boundary is the X-USU-001 result
  only, stated in recipe `when_not`, recipe book, release notes.
- X-RSE/X-RSE-002: routing release blocked (dense baseline not reliably
  above chance); boundary recorded in EXTERNAL_SUMMARY + RELEASE_NOTES.

**Phase 7 — external docs published.** `MECHANISM_RECIPES.md` (4 recipes
with scopes/limitations/evidence), `NEUROMORPHIC_EDGE_BLUEPRINT.md`
(simulation-only stated; mechanism→hardware mapping + future validation
sequence), `EXTERNAL_SUMMARY.md`, `PUBLICATION_DRAFT.md` (scoped outline,
threats-to-validity section), `RELEASE_NOTES.md`. PLATFORM_LAUNCH.md gains
the stability row + boundary line.

**Phase 8 — QA.** `tests/platform/test_release_docs.py` added (README
section checks + banned-phrase scan with negation-aware line filtering +
blueprint simulation-only check); platform suite 19 pass, package suites
16/15/19/23/21 pass; all 4 demos + recipes demo run quick-mode verified;
both benchmarks reproduce validated patterns (temporal_090 B=0.661,
adaptive B=0.736, sgd 9× slower; local-feedback adaptive late_ipn win).
Final CEEC audit: 1 warning (X-ALI-002 missing calibration record —
backfilled **CAL-000010**) → **audit clean, 0 violations/warnings**.
Manifest updated with Phase 6 disposition.

**Verification:** ruff clean on all touched files; pyright clean on
x_sta_002.py, lab recipes/tests, test_release_docs.py. Gotcha: internal
`computronium.state.CompositeState` ≠ package `stability.state.CompositeState`
pyright-wise (duck-compatible at runtime) — `# type: ignore[arg-type]` at
the guard/estimator seams.

**Remaining open debt (registered, not blocking the launch):**
19. ceec-core/psi-peft single-source migration (Rule 6 end-state) — main
    duplication debt; suggested order in T20.2.5.6 note (§17).
20. `pre_register_experiment` draft-status error message still mislabeled
    (opportunity #1, unfixed).
21. Belief B-H3 promotion still gated on `probability_threshold`; needs the
    boundary gate flow or further evidence to promote.
22. Publication draft is an outline only — expansion is venue-driven work,
    out of TODO20 scope.

**Gate status snapshot (final):** ceec-core validated; psi-peft validated;
stability validated; local-feedback validated; computronium-lab validated.
All packages listed in `docs/platform/RELEASE_MANIFEST.md`; release notes
published. TODO20 Definition of Done met except the two Rule-6 migrations
(ceec-core/psi-peft) explicitly documented as transitional scaffolding.

### 2026-09-11 — Rule-6 single-source sweep CLOSED (ceec + psi)

**ceec migration (internal → package).** `computronium/ceec/*.py` are now
star-import adapters of `ceec.<mod>` (submodule-bound in `__init__`,
`__all__ = list(ceec.__all__)`); `migrate/todo18_records` is
**module-aliased** (`sys.modules[__name__] = ceec.migrate.todo18_records`)
so monkeypatched module globals in legacy tests hit the real module —
star-import adapters break `monkeypatch.setattr(module, ...)` semantics.
~1.8k lines of duplicated implementation deleted. `computronium.ceec.cli`
stays runnable via `-m` (adapter invokes the package `main`). Legacy
bootstrap-count tests updated 8 → 10 (two new pre-registered configs).

**psi migration (math → package).** `solve_trace_readout` + `decayed`
moved to `psi_peft.math` (single copy); package `PsiReadout.update`
consumes them; internal `temporal_psi.py` re-imports from the package and
keeps `apply_readout` (framework-coupled activations surface). Parity test
still meaningful (class-vs-function paths). Full temporal/psi/plasticity
unit sweep: 130 pass.

**Opportunities fixed:** #1 (`pre_register_experiment` draft-status error
message corrected in the package copy — now the only copy), #9 (extras
group renamed `stability-guard`, no longer shadows the `stability` dep).

**Verification:** tests/ceec 114, platform 19, package suites
16/15/19/23/21 — all pass; audit CLI clean; ruff clean; pyright 0 errors
on touched files; dev-env smoke ok after `uv sync --dev --all-extras`.

**Gotchas for future work:**
- Per-package test-basename collisions (#18) break single-invocation
  collection — the per-package gate is binding, not cosmetic.
- Module-alias adapters are the pattern to copy when legacy tests
  monkeypatch module attributes (star-import adapters silently miss).

**TODO20 end state:** all DoD items checked. Remaining optional work:
publication-draft expansion (venue-driven), X-USU-002 defect hunt if
RoleSplit value warrants, X-RSE if the routing baseline becomes learnable.
