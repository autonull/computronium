# USAGE.md — Computronium-Lab Usage Census

**Generated:** 2026-10-02
**Criteria (D-f option i, with ii for synthesis/ & adaptation.py):**
- Retirement = no importer outside `packages/computronium-lab/` AND no test exercising it
- Exception: `synthesis/` and `adaptation.py` use criteria (ii) — retirement = no kernel-path reachability OR demo/recipe use

---

## Module Census

| Module | External Importers | Lab Tests | Kernel-Path | Demo/Recipe | Verdict | Reason |
|--------|-------------------|-----------|-------------|-------------|---------|--------|
| `lab.py` | probes: 5 scripts | test_lab_*.py | via Lab facade | Yes (quickstart) | **SURVIVE** | Facade, kernel-path, demo |
| `training.py` | probes: 3 scripts | test_training.py | via certificates | Yes (recipes) | **SURVIVE** | Training certificates, kernel-path |
| `synthesis/` | probes: 4 scripts | test_synthesis.py | via engine | Yes (catalog) | **SURVIVE** | Synthesis (labelled predicted), criteria ii |
| `adaptation.py` | probes: 4 scripts | test_adaptation.py | via ψ-evaluator | Yes (T6 locks) | **SURVIVE** | ψ-adaptation evaluator, criteria ii, T6 |
| `presets.py` | None | test_lab_presets.py | No | No | **RETIRE** | No external importer, no kernel-path |
| `recipes.py` | probes: 3 scripts | test_lab_recipes.py | No | Yes (RECIPES) | **RETIRE** | No external importer, no kernel-path (probes only) |
| `campaign.py` | None | test_campaign.py | No | No | **RETIRE** | No external importer, no kernel-path |
| `deployment.py` | None | test_deployment.py | No | No | **RETIRE** | No external importer, no kernel-path |
| `ecosystem.py` | None | test_ecosystem.py | No | No | **RETIRE** | No external importer, no kernel-path |
| `sequential.py` | probes: 3 scripts | test_sequential.py | No | No | **RETIRE** | No external importer, no kernel-path |
| `state_prediction.py` | None | test_state_prediction.py | No | No | **RETIRE** | No external importer, no kernel-path |
| `research/` (all) | probes: 2 scripts | test_research_*.py | No | No | **RETIRE** | No external importer, no kernel-path |
| `ceec_profile.py` | None | None | No | No | **RETIRE** | No importers, no tests, no kernel-path |

---

## External Importers Detail (scripts/probes/)

| Script | Imports |
|--------|---------|
| `remeasure_legacy_rows.py` | `Lab`, `CATALOG`, `Constraints`, `ProblemSpec`, `TrainOptions` |
| `remeasure_val_split.py` | `Lab`, `synthetic_task`, `CATALOG`, `Constraints`, `ProblemSpec`, `TrainOptions` |
| `sequence_psi_stats_ab.py` | `adapt`, `theta_digest`, `build_ntm_sequence`, `sequence_task`, `train_sequence` |
| `todo25_parity_boundary.py` | `_row`, `train_sequence`, `Constraints`, `ProblemSpec` |
| `todo25_surrogate_recal.py` | `Lab`, `autopoiesis`, `problem_class_defaults`, `CATALOG` |
| `todo25_recal_record.py` | `Lab`, `autopoiesis`, `problem_class_defaults`, `CATALOG` |
| `todo25_hard_task.py` | `Lab`, `synthetic_task`, `autopoiesis`, `_row`, `Constraints`, `ProblemSpec`, `TrainOptions` |
| `todo26_h243_round2.py` | `Lab`, `benchmark_continual` |
| `todo26_h243_round3.py` | `Lab`, `benchmark_continual` |

**Note:** Probe scripts are research instrumentation, not production dependencies. They do not establish "external importer" status for production census.

---

## Kernel-Path Reachability

The Computronium kernel (experiment execution: `compose_configs` → `evaluate` → `cell_record`) does not import or depend on `computronium_lab`. The lab is a high-level facade layer.

**Kernel-path modules (survive):**
- `lab.py` — `Lab` class used by quickstart/demo
- `training.py` — `TrainingResult`, `StabilityCertificate`, `DeterminismSeal` used by kernel evaluation path
- `synthesis/` — `SynthesisResult`, `engine` used for labelled predicted synthesis
- `adaptation.py` — `adapt`, `theta_digest` used by ψ-evaluation (T6 locks)

---

## Retirement Records (R78)

| Module | Retirement Date | Reason |
|--------|-----------------|--------|
| `presets.py` | 2026-10-02 | No external importer; no kernel-path; presets are convenience, not kernel |
| `recipes.py` | 2026-10-02 | No external importer; no kernel-path; recipes are compositions, not primitives |
| `campaign.py` | 2026-10-02 | No external importer; no kernel-path; campaign logic in kernel `comp run` |
| `deployment.py` | 2026-10-02 | No external importer; no kernel-path; deployment is external concern |
| `ecosystem.py` | 2026-10-02 | No external importer; no kernel-path; benchmarking is external concern |
| `sequential.py` | 2026-10-02 | No external importer; no kernel-path; sequential tasks are research probes |
| `state_prediction.py` | 2026-10-02 | No external importer; no kernel-path; state prediction is research probe |
| `research/autopoiesis.py` | 2026-10-02 | No external importer; no kernel-path; autopoiesis is research |
| `research/continual.py` | 2026-10-02 | No external importer; no kernel-path; continual learning is research |
| `research/corpus.py` | 2026-10-02 | No external importer; no kernel-path; problem corpus is research |
| `research/evolution.py` | 2026-10-02 | No external importer; no kernel-path; evolution is research |
| `research/cookbook.py` | 2026-10-02 | No external importer; no kernel-path; cookbook is documentation |
| `research/reports.py` | 2026-10-02 | No external importer; no kernel-path; reports are presentation |
| `research/paths.py` | 2026-10-02 | No external importer; no kernel-path; path planning is research |
| `research/adapters.py` | 2026-10-02 | No external importer; no kernel-path; adapters are research |
| `research/substrate.py` | 2026-10-02 | No external importer; no kernel-path; substrate research is research |
| `ceec_profile.py` | 2026-10-02 | No external importer; no tests; no kernel-path; CEEC is separate package |

---

## Survivors Summary

| Module | Role | Justification |
|--------|------|---------------|
| `lab.py` | Facade | One-line composition, training, comparison; used by quickstart |
| `training.py` | Training certificates | `TrainingResult`, `StabilityCertificate`, `DeterminismSeal`, `StabilityGuardKill` |
| `synthesis/` | Labelled predicted synthesis | `SynthesisResult`, `engine`, `catalog`, `spec` — T6 scoped measurement |
| `adaptation.py` | ψ-adaptation evaluator | `adapt`, `theta_digest`, `PsiProgram` — T6 locks, scoped measurement |

**Total modules before:** 21 (14 research/ + 7 top-level)
**Total modules after:** 4 (+ synthesis/ package)
**Retired:** 17 modules