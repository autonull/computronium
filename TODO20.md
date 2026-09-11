# TODO20 — Computronium Platform Launch

**Status:** Final actionable plan  
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

External Platform
  ├── ceec-core         → governance protocol
  ├── psi-peft          → flagship mechanism
  ├── local-feedback    → local-learning mechanism
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
```

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
| Jordan-block stability helper | Included if stable-amplification recipe ships |
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

- [ ] Identity-card scan defect fixed.
- [ ] ClosedFormRidgePlasticity resolved.
- [ ] D19 timeout triaged.
- [ ] Verification labels pass.
- [ ] Experiment statuses are current.
- [ ] Ledger audit clean.
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

- [ ] **T20.4.1 Create package skeleton**
  - Files:
    - `packages/local-feedback/pyproject.toml`
    - `packages/local-feedback/README.md`
    - `packages/local-feedback/src/local_feedback/__init__.py`

- [ ] **T20.4.2 Implement adaptive feedback module**
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

- [ ] **T20.4.3 Implement fixed-feedback baseline**
  - File:
    - `packages/local-feedback/src/local_feedback/baselines.py`
  - Must include:
    - fixed random feedback,
    - matched-norm comparison utilities.

- [ ] **T20.4.4 Implement local-training adapter**
  - File:
    - `packages/local-feedback/src/local_feedback/trainer.py`
  - Purpose:
    - show how adaptive feedback plugs into a simple local-credit loop.

- [ ] **T20.4.5 Run X-ALI-002 short-trajectory validation**
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

- [ ] **T20.4.7 Build demo**
  - File:
    - `packages/local-feedback/examples/local_feedback_demo.py`
  - Must show:
    - fixed feedback baseline,
    - adaptive feedback improvement,
    - matched norm.

- [ ] **T20.4.8 Build benchmark**
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

- [ ] **T20.4.9 Add tests**
  - Files:
    - `packages/local-feedback/tests/test_adaptive.py`
    - `packages/local-feedback/tests/test_trajectory.py`
    - `packages/local-feedback/tests/test_no_computronium_imports.py`

- [ ] **T20.4.10 Write package README**
  - Must include:
    - when adaptive feedback helps,
    - when it does not,
    - validated scope,
    - evidence refs.

## Acceptance Criteria

- [ ] Package is standalone.
- [ ] Demo runs on CPU.
- [ ] One-step and short-trajectory validations exist.
- [ ] Benchmark shows adaptive feedback beating fixed feedback under matched norm in validated scope.
- [ ] Documentation includes limits.

---

# Phase 5 — Product D: Computronium Lab

## Objective

Make the ontology usable.

## Product

```text
packages/computronium-lab
```

## Tasks

- [ ] **T20.5.1 Create package skeleton**
  - Files:
    - `packages/computronium-lab/pyproject.toml`
    - `packages/computronium-lab/README.md`
    - `packages/computronium-lab/src/computronium_lab/__init__.py`

- [ ] **T20.5.2 Implement Lab API**
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

- [ ] **T20.5.3 Implement presets**
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

- [ ] **T20.5.4 Implement recipe layer**
  - File:
    - `packages/computronium-lab/src/computronium_lab/recipes.py`
  - Recipes should wrap validated mechanisms:
    - temporal ψ,
    - adaptive feedback,
    - role split,
    - stable amplification helper if released,
    - routing recipe only if unblocked.

- [ ] **T20.5.5 Optional CEEC recording**
  - Lab may optionally record evidence using CEEC-Core.
  - Must be off by default for external simplicity.

- [ ] **T20.5.6 Build quickstart example**
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

- [ ] **T20.5.7 Build mechanism recipes demo**
  - File:
    - `packages/computronium-lab/examples/mechanism_recipes_demo.py`
  - Must show:
    - temporal ψ recipe,
    - adaptive feedback recipe,
    - role-split recipe.

- [ ] **T20.5.8 Add tests**
  - Files:
    - `packages/computronium-lab/tests/test_lab_compose.py`
    - `packages/computronium-lab/tests/test_lab_train.py`
    - `packages/computronium-lab/tests/test_presets.py`
    - `packages/computronium-lab/tests/test_recipes.py`
    - `tests/platform/test_lab_smoke.py`

## Acceptance Criteria

- [ ] `Lab.compose` works for minimum presets.
- [ ] `Lab.train` works on quick tasks.
- [ ] `Lab.compare` produces a readable table.
- [ ] `Lab.recipe` exposes validated mechanisms.
- [ ] Quickstart runs on CPU.
- [ ] Lab does not require users to understand CEEC internals.

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

- [ ] **T20.6A.1 Pre-register X-STA-002**
  - Question:
    ```text
    Do coordinates with ρ ≤ ρ_limit and σ_max > 1 improve noise robustness
    relative to matched contractive coordinates?
    ```
  - Evidence kind:
    - tensor.
  - Axes:
    - c × noise_level × seed.

- [ ] **T20.6A.2 Build stable-matrix helper**
  - File:
    - `packages/computronium-lab/src/computronium_lab/stability.py`
  - Must include:
    - size-4 Jordan-block construction,
    - rotation,
    - realized ρ check,
    - realized σ_max check.

- [ ] **T20.6A.3 Run X-STA-002**
  - Metrics:
    - signal retention,
    - settling success,
    - settling time,
    - noise divergence if paired replay used.

- [ ] **T20.6A.4 Ship or boundary**
  - If supported:
    - add stable-amplification recipe to Lab and recipe book.
  - If falsified:
    - publish boundary and provide helper with limits.

## Acceptance Criteria

- [ ] X-STA-002 evidence recorded.
- [ ] Stability helper verifies constructed spectra.
- [ ] Documentation matches outcome.

---

## 6B — Role-Split Defect Hunt

## Condition

Include if it improves the RoleSplit recipe or prevents misuse.

## Carryover

```text
X-USU-002
```

## Tasks

- [ ] **T20.6B.1 Pre-register X-USU-002**
  - Question:
    ```text
    Does muon-on-forward degrade one-step descent because orthogonalization
    amplifies pseudo-gradient noise?
    ```
  - Axes:
    - update_arm × batch_size × smoothing × seed.

- [ ] **T20.6B.2 Run defect hunt**
  - Check:
    - batch size,
    - smoothing,
    - momentum,
    - norm clipping,
    - role partitioning.

- [ ] **T20.6B.3 Update RoleSplit recipe**
  - Add explanation if found.
  - Add boundary if not found.

## Acceptance Criteria

- [ ] Evidence recorded.
- [ ] RoleSplit documentation updated.
- [ ] No boundary declared without defect hunt.

---

## 6C — Routing Baseline Fix

## Condition

Include only if routing efficiency is desired as a Lab recipe.

## Carryover

```text
X-RSE baseline defect
```

## Tasks

- [ ] **T20.6C.1 Fix dense baseline learnability**
  - Options:
    - lengthen budget,
    - simplify task,
    - replace sparse task.
  - Requirement:
    - dense baseline reliably above chance.

- [ ] **T20.6C.2 Re-run X-RSE baseline**
  - Metrics:
    - dense accuracy,
    - effective ops,
    - walltime.

- [ ] **T20.6C.3 Run X-RSE-002 only if baseline passes**
  - Question:
    ```text
    At matched effective ops, does routed system maintain or improve task performance?
    ```

- [ ] **T20.6C.4 Ship or boundary**
  - If benefit is real:
    - add routing recipe.
  - If not:
    - publish boundary.

## Acceptance Criteria

- [ ] Routing recipe ships only with valid baseline.
- [ ] Otherwise boundary is recorded.

---

# Phase 7 — Blueprints, Recipes, and External Communication

## Objective

Make the platform understandable and useful to external audiences.

## Tasks

- [ ] **T20.7.1 Write mechanism recipe book**
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

- [ ] **T20.7.2 Write hardware/edge blueprint**
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

- [ ] **T20.7.3 Write external summary**
  - File:
    - `docs/platform/EXTERNAL_SUMMARY.md`
  - Audience:
    - ML engineers,
    - researchers,
    - hardware-oriented readers.

- [ ] **T20.7.4 Write publication draft**
  - File:
    - `docs/platform/PUBLICATION_DRAFT.md`
  - Based only on released mechanisms.
  - No overclaims.

- [ ] **T20.7.5 Write release notes**
  - File:
    - `docs/platform/RELEASE_NOTES.md`
  - Include:
    - packages,
    - versions,
    - evidence status,
    - known limitations.

## Acceptance Criteria

- [ ] Recipe book exists.
- [ ] Hardware blueprint exists.
- [ ] External summary exists.
- [ ] Publication draft exists.
- [ ] Release notes exist.
- [ ] All external claims are scoped.

---

# Phase 8 — Release QA and Final Audit

## Objective

Ensure the platform is trustworthy and reproducible.

## Tasks

- [ ] **T20.8.1 Run package boundary tests**
  - File:
    - `tests/platform/test_package_boundaries.py`
  - Checks:
    - `ceec-core`, `psi-peft`, `local-feedback` do not import Computronium.

- [ ] **T20.8.2 Run parity tests**
  - Files:
    - `tests/platform/test_psi_peft_parity.py`
    - `tests/platform/test_local_feedback_parity.py`
  - Purpose:
    - ensure extracted modules match validated core/probe behavior within tolerance.

- [ ] **T20.8.3 Run all platform demos in quick mode**
  - Commands:
    ```bash
    uv run python packages/ceec-core/examples/quickstart.py
    uv run python packages/psi-peft/examples/task_switching_demo.py
    uv run python packages/local-feedback/examples/local_feedback_demo.py
    uv run python packages/computronium-lab/examples/lab_quickstart.py
    ```

- [ ] **T20.8.4 Run all platform benchmarks in quick mode**
  - Commands:
    ```bash
    uv run python packages/psi-peft/benchmarks/psi_vs_sgd_readout.py --quick
    uv run python packages/local-feedback/benchmarks/adaptive_vs_fixed.py --quick
    ```

- [ ] **T20.8.5 Run documentation claim checks**
  - File:
    - `tests/platform/test_release_docs.py`
  - Checks:
    - each package README has scope,
    - each package README has limitations,
    - banned overclaim phrases are absent.

- [ ] **T20.8.6 Final CEEC audit**
  - Command:
    ```bash
    uv run python -m computronium.ceec.cli audit
    ```

- [ ] **T20.8.7 Update release manifest**
  - File:
    - `docs/platform/RELEASE_MANIFEST.md`
  - Mark packages:
    - `draft`,
    - `validated`,
    - or `released`.

## Acceptance Criteria

- [ ] All package boundary tests pass.
- [ ] All parity tests pass.
- [ ] All demos run in quick mode.
- [ ] All benchmarks run in quick mode.
- [ ] Documentation passes claim checks.
- [ ] Final audit clean.
- [ ] Release manifest updated.

---

## 9. Tests and CI

Required test roots:

```text
tests/platform/
packages/ceec-core/tests/
packages/psi-peft/tests/
packages/local-feedback/tests/
packages/computronium-lab/tests/
```

Suggested CI gate:

```bash
uv run pytest tests/platform -q
uv run pytest packages/ceec-core/tests -q
uv run pytest packages/psi-peft/tests -q
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

- [ ] `ceec-core` is standalone and runnable.
- [ ] `ceec-core` has CLI and quickstart.
- [ ] `ceec-core` does not import Computronium.
- [ ] `psi-peft` is standalone and runnable.
- [ ] `psi-peft` includes readout, adaptive, and buffered variants.
- [ ] `psi-peft` demo runs on CPU.
- [ ] `psi-peft` benchmark reproduces validated task-switching result.
- [ ] `local-feedback` is standalone and runnable.
- [ ] `local-feedback` demo runs on CPU.
- [ ] `local-feedback` benchmark validates adaptive feedback under scope.
- [ ] `computronium-lab` provides a high-level API.
- [ ] `computronium-lab` supports minimum presets and recipes.
- [ ] `computronium-lab` quickstart runs.

### TODO19 closure

- [ ] Identity-card scan defect fixed.
- [ ] ClosedFormRidgePlasticity resolved.
- [ ] D19 timeout triaged.
- [ ] Verification labels pass.
- [ ] Experiment statuses swept.
- [ ] Ledger audit clean.
- [ ] Temporal-ψ speed lever addressed.
- [ ] X-ALI-002 validation completed.
- [ ] X-STA-002 either executed for stability recipe or explicitly deferred.
- [ ] X-USU-002 either executed for RoleSplit recipe or explicitly deferred.
- [ ] X-RSE baseline either fixed or routing release blocked with boundary.

### Documentation

- [ ] Mechanism recipe book published.
- [ ] External summary published.
- [ ] Hardware/edge blueprint published.
- [ ] Publication draft prepared.
- [ ] Release notes published.
- [ ] Release manifest updated.

### Quality

- [ ] Platform tests pass.
- [ ] Existing Computronium tests remain green or known failures are documented.
- [ ] Ruff clean.
- [ ] Pyright clean under repository standard.
- [ ] External documentation passes claim discipline.

---

## 11. Minimal Viable Platform

If time is constrained, the minimum acceptable TODO20 is:

1. Phase 1 hygiene closure.
2. `ceec-core` standalone quickstart and audit.
3. `psi-peft` standalone demo and benchmark.
4. `local-feedback` standalone demo and benchmark.
5. Basic mechanism recipe book.
6. Final audit and release manifest.

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
