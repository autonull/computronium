This document serves as the master execution plan for the Computronium remediation and development effort. It translates the agreed-upon architectural, mathematical, and documentation corrections into a sequenced, actionable engineering roadmap.

The plan is divided into **Track A (Code & Infrastructure)** and **Track B (Documentation & README)**, followed by **Track C (CI/CD & Enforcement)**. Track A gates Track B: public claims in the README will only be updated once the underlying evidence chain is repaired and verified.

---

# Track A: Code, Infrastructure, and Evidence Chain

## Phase 1: Tooling and Schemas (Week 1)
Before writing tests or rewriting docs, establish the infrastructure for rigorous claim-tracking.

- [x] **1.1. Implement `correction_record.py`**: Create a dataclass/schema for tracking superseded measurements. ✅ `computronium/core/correction_record.py` — frozen `CorrectionRecord` (tuple fields per repo immutability convention), `CorrectionStatus` PEP 695 alias, `to_row()` for table rendering. Exported at root.
- [x] **1.2. Implement `identity_card.py`**: Create a schema for Algorithm Identity Cards. ✅ `computronium/core/identity_card.py` — frozen `AlgorithmIdentityCard`, `render_identity_card_table()` for docs/README tables. Exported at root.
- [x] **1.3. Implement `FrozenThetaAudit` Context Manager**: ✅ `computronium/core/frozen_theta.py`. Class-based `FrozenThetaAudit` + `frozen_theta_audit` contextmanager wrapper. Snapshots clones + `Tensor._version` counters + `data_ptr()` per tensor over geometry params, substrate state tensors, optimizer param groups. Catches in-place mutations, mutate-then-restore (via `_version`), alias mutations, and storage rebinding (re-collects the state at exit so dict rebinding is visible). Raises `FrozenThetaError(AssertionError)`. All exported at root (`_LAZY` + `__all__` + TYPE_CHECKING).

## Phase 2: The Evidence Chain Repair (Weeks 2-3)
Address the mathematical and testing blockers.

- [x] **2.1. Jacobian Estimator Audit & Regression**: ✅
  - [x] Audit: `estimate_spectral_radius` was JVP-only power iteration (finite-difference J·v), labeled ρ(J_F). Measured behavior: on nonnormal J the iteration aligns with the dominant eigenvector, so it converges to ρ-like magnitudes and does NOT certify σ_max(J) transients.
  - [x] Renamed to `estimate_directional_amplification` (module docstring now states exactly what it measures). Exact, separated metrics added: `dominant_singular_value` (σ_max via autograd+SVD) and `spectral_radius_from_jacobian` (ρ via autograd+eigvals). `SpectralRadiusEstimator` → `JacobianAmplificationEstimator`; `SpectralRadiusConfig` → `JacobianAmplificationConfig`. Callers updated: stability/{__init__,guard,config}, core/profiling, core/continual/{metrics,runner,stability}, cli/lab (key `spectral_radius`→`jacobian_amplification`), analysis/training_dynamics (`compute_spectral_radius_proxy`→`compute_jacobian_amplification_proxy`, field `jacobian_amplification`), resources.py (field `jacobian_amplification`). Honesty notes: lab.py's inline proxy labeled "activity-norm proxy, never claim ρ(J)".
  - [x] Regression Test 1 (Normal): `tests/property/test_jacobian_amplification.py` — diagonal J: ρ = σ_max = dominant diagonal, all three estimators agree.
  - [x] Regression Test 2 (Nonnormal): Jordan block [[0.5,10],[0,0.5]]: ρ=0.5, ‖J‖₂≈10.0246, estimator stays on the eigen-direction (~0.5). Seeded (autouse fixture) — 3× repeat stable.
  - [x] CorrectionRecord applied: `docs/CORRECTIONS.md` published (Correction 1: estimator conflation, E1/E3 frontier numbers flagged `requires_rerun` where quoted as ρ; Correction 2: J2 check strength). RESEARCH3.md §stability still references the old estimator name — queued hygiene.
- [x] **2.2. J2 Invariant (Frozen θ) Hardening**: ✅
  - [x] `tests/property/joint/test_lifecycle_locks.py::test_j2_theta_immutable_intra_episode` now wraps the 5 intra-episode steps in `FrozenThetaAudit` (clone/allclose loop removed).
  - [x] Adversarial tests: `tests/property/joint/test_frozen_theta_audit.py` — in-place `add_`, mutate-then-restore (`copy_` rollback caught by `_version`), alias mutation, dict rebinding (`data_ptr`), clean-episode pass. All must fail on violation and do.
  - [x] Frozen scope documented in module docstring: all tensors from `geometry.params`, substrate `state` dict tensors, optimizer `param_groups` params.
- [x] **2.3. Verification Label Audit**: ✅ (enforcement mechanism complete; full taxonomy annotation of legacy tests is incremental)
  - [x] Taxonomy module: `computronium/verification.py` — `VerificationLevel` StrEnum (5 levels), `BANNED_PHRASES` ("formal proof", "formally proven", "machine-checked theorem", "mathematically certified", "no weight transport", "upper bound via power iteration"), `render_taxonomy_markdown()`. Exported at root.
  - [x] Enforcement test: `tests/property/test_verification_labels.py` — scans all test modules under tests/property + tests/integration; fails on banned phrases anywhere in a line, and on "theorem" mentions lacking a `Level N` label. Currently green after fixing flagged files.
  - [x] Fixed flagged claims: `test_zero_extension_theorem_*` renamed + relabeled Level 4 (`test_plasticity_axis_certifications.py`, `test_lifecycle_locks.py`, `test_null_equivalence.py`, `test_plasticity_properties.py`); "no weight transport" reworded to "no transport shortcut" in FA tests + Directed EP docstring (FA legitimately has no transport; EqProp-family claims removed).
- [x] **2.4. PEPITA / LEMMA Disambiguation**: ✅
  - [x] Audit confirmed different math: `PepitaCredit` implements published PEPITA (input-modulated second pass, autograd); `create_pepita_mlp` actually composed `LocalGoodnessCredit(local_objective="lemma")` — a Forward-Forward goodness rule, mislabeled since before TODO15.
  - [x] Split: new `LemmaCredit` (`computronium/ontology/credit.py`, LocalGoodnessCredit pinned to lemma); `create_pepita_mlp` now composes `PepitaCredit`; `create_lemma_mlp` composes `LemmaCredit`. Demo registry (`demo/runner.py`) gained `lemma_mlp` and true-PEPITA `pepita_mlp`. Tests updated (`test_params_moved` builds both; `test_ontology_parity` LEMMA parity vs `create_native_pepita_mlp` — both lemma).
  - [x] Identity Cards attached as `IDENTITY_CARD` class attributes on both primitives; exported at root + ontology. NOTE: `computronium/models/native/pepita_native.py` family (create_native_pepita_mlp) is also LEMMA math under a pepita name — still to rename (queued hygiene, touches demo/gallery manifests).

## Phase 3: The Auditable Vertical Slice (Week 4)
Prove the new measurement pipeline works end-to-end on a single, well-understood coordinate.

- [x] **3.1. Define the Slice**: ✅ `computronium/analysis/vertical_slice.py::run_slice` — EqProp (EnergyMinimization) + RecurrentGeometry + DigitalSubstrate + ThermodynamicContrast + EuclideanUpdate via `create_eqprop_system`. Offline synthetic task (seeded) stands in for MNIST so the gate is hermetic; the claim record's config names the task, and an MNIST variant swaps the batch source only.
- [x] **3.2. Implement the Measurement Panel**: ✅
  - [x] Energy trajectory: `measure_energy_trajectory` — initial/final/mean free energy + non-increasing fraction. Labeled: consistent-with-descent (Level 5), never proof.
  - [x] Gradient alignment with **strict sign convention**: `measure_gradient_alignment` — Δθ = θ_after − θ_before, ∇L·Δθ via central finite difference of the coordinate's own free loss along Δθ. Verified: directional_derivative ≈ loss_delta (rel 0.5, abs 1e-3 tolerance holds at slice scale).
  - [x] Resource accounting: `measure_resources` — train-step FLOPs (`estimate_train_step_flops`) + param count.
  - Corrected Jacobian/Spectral tracking: covered by 2.1's separated estimators; not re-run inside the slice (add a σ_max read per N steps when the slice grows a frontier use).
- [x] **3.3. Generate the Claim Record**: ✅ `ClaimRecord` — coordinate, config, seeds, per-metric mean/std/n, verification_level, commit hash, walltime; JSON round-trip; stable `config_digest()` for baseline identity. Baseline pinned at `results/vertical_slice/claim_record.json` (seed 0, 12 steps, digest `5d93dadfa0c3ca5f`).
- [x] CI gate: `tests/integration/test_vertical_slice_gate.py` — regenerates the record and compares means to the pinned baseline (float-tolerance determinism), asserts learning-does-not-regress + schema + digest stability. Complements `tests/property/test_vertical_slice.py` (8 tests: sign convention, determinism, frozen-θ forward audit, resources). This is the C.2 gate body; wiring it into GitHub Actions is the remaining C.2 step (no workflow files exist in-repo yet).

## Phase 4: Structural Refactoring (Weeks 5-6)
Address architectural heterogeneity and API design.

- [x] **4.1. `SubstrateSpec` Implementation**: ✅
  - [x] `computronium/ontology/substrate/spec.py` — frozen `SubstrateSpec` with `ExecutionModel`/`DeviceModel`/`NumericRepresentation` StrEnums, `NoiseConfig`, `ConstraintConfig`, `CostConfig`, plus a `substrate_type` hint field because legacy `SubstrateConfig` is lossy for the ternary/complex/sparse digital-family trio (their configs don't record the family in any field). `from_config`/`to_config` round-trip substrate_type faithfully for all 9 presets.
  - [x] `make_substrate(spec)` delegates to the existing `substrate_from_config` dispatch (single class table, no duplication). Exported: ontology/substrate → root (`_LAZY` + `__all__` + TYPE_CHECKING; wiring lock green).
  - [x] Tests: `tests/property/test_substrate_spec.py` — 9-preset round-trip + factory parity, native-vs-simulated execution split, numeric mapping, compound noisy+sparse construction, fully-stated defaults.
  - Substrate classes NOT refactored to wrap SubstrateSpec internally — the spec is a projection layer over SubstrateConfig; wrapping would touch every substrate subclass + compose path for no behavioral gain this round (queued as optional consolidation).
- [x] **4.2. Algorithm Identity Cards Integration**: ✅ COMPLETE (round 5)
  - [x] `IDENTITY_CARD` class attributes on all 22 cardless primitives (8 credit incl. `GradientCredit`; 10 update; 5 plasticity incl. `NullPlasticity` in `state/transitions.py`). Aliases (`BackpropCredit`=`GradientCredit`, `ThermodynamicContrastCredit`=`ThermodynamicContrast`) dedupe to their target class in the generator (same class object renders once).
  - [x] Generator: `scripts/generate_identity_cards.py` — scans credit/update/plasticity ontology modules (protocols/abstracts excluded), renders Markdown to stdout; `--strict` exits 1 when any concrete primitive lacks a card. **Now 22/22 — strict passes.**
  - [x] **C.1 wired**: `identity-cards` hook added to `.pre-commit-config.yaml`. Adding a Credit/Update/Plasticity primitive without a card now blocks the commit.
  - [x] `docs/IDENTITY_CARDS.md` regenerated with all cards + status header; README §5 link updated.
- [x] **4.3. Axis Boundary Review**: ✅ `HomeostaticCredit` documented, not moved — its pseudo-gradient is loss-blind norm regulation (constraint controller) but the pipeline contract routes per-weight directional signals through `compute_pseudo_gradient`, so relocating it would break the C-axis contract. Dual role documented in its `IDENTITY_CARD` + class docstring; explicitly excluded from being read as a learning signal in the Credit × Update mechanistic study (5.1).

## Phase 5: New Experimental Campaigns (Weeks 7-8)
Execute the mechanistic and stability studies proposed in the review.

- [x] **5.1. Credit $\times$ Update Mechanistic Study**: ✅ `computronium/analysis/mechanistic_study.py` (+ `MechanisticStudyRecord`, root-exported)
  - [x] **One-Step Reset-State**: fresh θ + fresh optimizer per run, one C×U step, `‖Δθ‖` and ΔL via the panel's `free_loss` (now public in `vertical_slice.py`); `improvement_per_norm` = −ΔL/‖Δθ‖.
  - [x] **Trajectory-Trained**: 30-step runs, loss trajectory + per-step `‖Δθ‖` + tuning budget (steps×params).
  - [x] **Norm matching**: each non-euclidean cell's step size calibrated (single proportional rescale — first-step disp ∝ step_size at momentum 0 for both step semantics) so first-step `‖Δθ‖` matches its credit's euclidean reference; LR-categorization respected.
  - [x] Grid: 4 credits (eqprop/fa/lemma/bp) × 3 updates (euclidean/adam/muon) = 12 cells × 3 seeds on the vertical-slice coordinate (digital/recurrent/energy_min). PEPITA excluded (memory-backprop-class, needs Instantaneous+Feedforward — documented).
  - [x] **First record** pinned at `results/mechanistic_study/claim_record.json` (10 s walltime). Headline: muon gives the best immediate transformation quality (eqprop×muon qual +0.324 vs euclidean +0.221); BP reference has the highest descent quality (+0.589) but smallest displacement; lemma cells near-inert at matched norms (quality ≈ 0, lemma×muon ΔL positive) — a real finding to investigate before any lemma-on-settle claim.
- [x] **5.2. Stability $\times$ Memory Campaign**: ✅ `computronium/analysis/memory_stability.py` (+ campaign runner, parameterized grid)
  - [x] **Block-structured dynamics**: `x_{t+1} = tanh(W_x x_t + W_in u_t [+ W_fb m_t] + ξ_t)`, `m_{t+1} = (1−g·w_t)m_t + g·w_t·u_t` with write signal on cue only (selective) or every step (ungated). Round 6: `W_fb` feedback coupling axis (`open`/`coupled`), delay 32, `state_noise_divergence` paired-replay metric, `retention_contraction_scatter`.
  - [x] Swept axes: contraction {0.5, 0.9, 1.05} × gate {selective, ungated} × coupling {open, coupled} × precision {f32, f16, bf16} × noise {0, 0.1} × readout {full, low-rank-4, 4-bit-quantized} × delay {1, 8, 32 distractor steps}; 648 cells, 3 seeds × 8 trials.
  - [x] **Hypothesis test**: "Useful adaptation needs selective preservation of state, not global instability." **Direction confirmed in the first record** (`results/memory_stability/claim_record.json`, 5 s): selective retention ≈ 0.998 at *every* measured contraction rate including unstable (measured ≈ 1.0), while ungated collapses with distractor count (0.41 → 0.06 over 8 steps). Instrument notes below.
  - [x] `measured_contraction` = linearized perturbation decay (tanh-Jacobian), tracks nominal monotonically but sits below it — recorded as such, never conflated with ρ.

---

# Track B: README.md Revision Plan

The README must be rewritten to reflect the "Composable Laboratory" framing. The "Search for Computronium" narrative is moved to a clearly labeled Motivation section.

## Section-by-Section Rewrite Guide

### 1. Header and Framing
*   **Old:** "Computronium: Composable ML Library + Research Framework... The search for computronium investigates..."
*   **New:**
    *   **Title:** Computronium: A Composable Laboratory for Learning Mechanisms
    *   **Lead Paragraph:** "Computronium is a composable ML library and experimental laboratory for studying how learning mechanisms interact with dynamics, writable state, communication, precision, and resource constraints. Its six-axis interface supports controlled comparisons; its research program investigates when particular combinations offer measurable benefits."
    *   **Motivation (Collapsible/Secondary):** Move the "search for computronium" and physical substrate vision here, clearly labeled as the *motivating hypothesis*, not an established result.

### 2. The Six-Axis Decomposition
*   **Correction:** Clarify that the space is a *compatibility-constrained subset*, not a free Cartesian product.
*   **Addition:** Introduce the `SubstrateSpec` structure. Explain that substrates are defined by execution model, device model, numeric representation, noise, and cost, allowing compound configurations (e.g., "noisy, sparse, complex-valued").
*   **Diagram Fix:** Relabel the Mermaid architecture diagram from "Execution Order" to **"Schematic Coupling Diagram"**. Add a note that the cyclic $U \to S$ dependency represents physical state updates, not a strict sequential pipeline.

### 3. Joint Dynamics & Frozen-$\theta$
*   **Correction:** Rewrite the joint transition operator to explicitly include inputs, stochasticity, and time: $z_{t+1} = F_{\theta_e}(z_t, u_t, \xi_t, \Delta t_t; G, S, D, P)$.
*   **Correction (J2):** Define the "Frozen $\theta$" contract explicitly. State that the framework enforces **Boundary Invariance** and **Stage-Boundary Invariance** via the `FrozenThetaAudit` context manager, detecting in-place and alias mutations.
*   **Correction (P-axis):** Remove claims that P-axis "unfolds arbitrarily deep computation" as a validated capability. Reframe P-axis as providing *architectural* benefits (lifecycle control, intervention, explicit routing) independent of whether it outperforms standard recurrent memory on benchmarks.

### 4. Stability, Energy, and Verification
*   **Correction (LaSalle/Lyapunov):** Replace "Symmetric topology + EnergyMinimization → fixed-point convergence" with: "Under documented regularity and discretization assumptions, the specified dynamics admit a Lyapunov argument. Convergence to an equilibrium depends on additional conditions stated per implementation."
*   **Correction (Jacobian):** Remove conflation of spectral radius ($\rho$) and singular values ($\sigma_{\max}$). Define the "Stability-Expressiveness Frontier" using explicitly named metrics (e.g., "Asymptotic Stability Margin ($\rho$)" vs "Transient Amplification Bound ($\|J\|_2$)").
*   **New Section: Verification Taxonomy:** Explicitly list the 5 levels of verification (Analytical, Machine-checked, Certified Numerical, Sampled Numerical, Empirical). State that the CI gate relies primarily on Level 4 (Sampled Numerical) and Level 5 (Empirical).

### 5. Algorithm Primitives & Identity Cards
*   **Correction:** Remove the phrase "no weight transport" from EqProp; clarify it requires reciprocal/symmetric interactions.
*   **Correction:** Fix PEPITA description to match the actual error-driven input modulation math, distinct from Forward-Forward goodness.
*   **Correction:** Clarify Holomorphic EP is *complex-valued*, not necessarily *quantum* (unless running on the specific simulated unitary gate substrate).
*   **Addition:** Add a link to the **Algorithm Identity Cards** (hosted in docs or an appendix), which detail reference equations, deviations from literature, and pseudo-gradient definitions for every primitive.

### 6. Expressiveness and Negative Results
*   **Correction (Kolmogorov):** Remove the $O(K/D)$ runtime claim. Replace with: "A fixed recurrent controller with writable memory can execute computations whose temporal depth exceeds its architectural depth, bounded by precision and program semantics."
*   **Correction (Composition Error):** Remove the universal "law" formula. Reframe the E1 result as: "Under this architecture and precision, short-horizon local learning failed to achieve the one-step accuracy needed for reliable long-horizon rollout due to composition-error compounding."
*   **Correction ($\psi$ Modulation):** Replace "passenger" or "small relative to" with exact descriptive statistics: "Across tested configurations, observed $\psi$ modulation averaged 2.0 percentage points (max 9.1 points). These measurements do not establish equivalence or negligibility."

### 7. Installation, CLI, and Quickstarts
*   **Fix:** Add explicit installation prerequisites (Python version, PyTorch version, optional GPU/CUDA requirements).
*   **Fix:** In all Python quickstart snippets, define `device = torch.device("cuda" if torch.cuda.is_available() else "cpu")` or explicitly set it to `"cpu"` so the code is copy-paste runnable.
*   **Fix:** Clarify that `comp scientist` and `comp frontier` are *automation tools* for exploring the space, not guarantees of finding superior algorithms.

---

# Track C: CI/CD and Enforcement

To ensure the project does not regress into overclaiming or mathematical sloppiness, the CI pipeline must be updated.

- [ ] **C.1. Identity Card Pre-Commit Hook**: Write a pre-commit script that parses `computronium/core/ontology.py` and fails if any new Credit, Update, or Plasticity primitive is added without an attached `AlgorithmIdentityCard`.
- [x] **C.2. Vertical Slice CI Gate**: ✅ `.github/workflows/ci.yml` already existed (plan was stale); added the vertical-slice gate step (`test_vertical_slice_gate.py` + `test_vertical_slice.py`) to the `ci` job.
- [ ] **C.3. Mutation Testing for J2**: Not wired — the adversarial suite (`tests/property/joint/test_frozen_theta_audit.py`: in-place, mutate-then-restore via `_version`, alias, rebinding) already asserts the audit catches each mutation class by construction; mutmut would add independence but is expensive. Optional follow-up if the audit logic changes.
- [x] **C.4. Claim Record Linting**: ✅ `tests/property/test_verification_labels.py` now scans (1) all tests/ modules (existing), (2) **every docstring under `computronium/`** (AST-based), and (3) **README.md + docs/*.md excluding `docs/archive/`** against `BANNED_PHRASES`. Currently zero violations.

---

# Definition of Done

This remediation plan is considered complete when:
1.  **Track A (Phases 1-5)** is merged into `main`, with all Tier 1 blockers resolved and the new campaigns (Credit $\times$ Update, Stability $\times$ Memory) yielding their first structured claim records.
2.  **Track B** is published: The `README.md` strictly adheres to the "Composable Laboratory" framing, all mathematical claims are narrowed to their proven bounds, and the 5-level verification taxonomy is visible.
3.  **Track C** is active: The CI pipeline automatically rejects PRs that introduce unverified mathematical claims or primitives lacking identity cards.
4.  **The Correction Log** is published in the repository (e.g., `docs/CORRECTIONS.md`), transparently listing the Jacobian, J2, and PEPITA fixes using the `CorrectionRecord` schema, demonstrating the project's commitment to rigorous negative-result and measurement-error culture.

---

# Execution Status (TODO18 rounds 1-14 — Phases 1-5, Track B, Track C, Tier-3 clusters, round close, improvement opportunities: COMPLETE)

## Progress (round 14 — improvement opportunities closed)
- **Card-drift lock**: `tests/property/test_identity_cards_drift_lock.py` — regenerates the card body from `collect_cards()` and asserts it is an ordered, stripped subsequence of `docs/IDENTITY_CARDS.md` (mirrors the readme-snippet-lock pattern; doc header/status prose is the unlocked hand-maintained index). Editing a card in code without regenerating the doc (or vice versa) now fails. Runtime-sys.path import matches the existing lock-test convention.
- **Vertical-slice baseline multi-seed**: re-pinned `results/vertical_slice/claim_record.json` over seeds (0,1,2) — `ClaimRecord.from_runs` aggregates to n=36 per metric; `config_digest` unchanged (`5d93dadfa0c3ca5f`, config-identity is seed-independent). Gate fixture `fresh_record` now regenerates all 3 seeds; 16/16 slice tests green. Closes the "multi-seed pinning" opportunity.
- **Lemma inertness probe**: `scripts/probes/lemma_settle_inertness.py` (verdict in docstring). Cos(pseudo-grad, ∇ free loss), 3 seeds, per layer: lemma ≈ 0 on BOTH coordinates (settle +0.003/+0.086/+0.000; feedforward/instant −0.010/+0.107); ff healthy on both (+0.43..0.53); bp +1.000 anchor; eqprop healthy on its own coordinate (+0.70/+0.55) and ≈0 on the instantaneous control's first layer (FREE==NUDGED collapse — expected). **Coordinate-mismatch hypothesis falsified: the 5.1 lemma-cell inertness is the LEMMA closed form's own directional quality (fixed random inverse projections), consistent with TODO15 §12. Lemma-on-settle stays closed until the projection structure changes (learned-B already measured worse).** No record re-pin needed (5.1 numbers already reflect this).
- Battery: slice 16, card lock 1, fidelity 45, verification labels 5 — all green; ruff format+check clean on changed files.

## Round close (round 13 — Tier-3 verification run)
- **Full suite green**: `1513 passed, 48 skipped, 34 deselected, 27 xfailed, 0 failed` in 3m04s (`logs/tier3_round_close.log`). All 15 pre-existing failure clusters from round 11 confirmed fixed; no regressions from the round-12 one-line fixes. Skips/xfails are deliberate (walltime-tiered demos, platform-conditional, expected-fail contracts).
- **TODO18 is complete**: all Tracks (A phases 1-5, B §1-7, C.1/C.2/C.4), Definition of Done items 1-4 satisfied. Only C.3 (optional mutmut) remains deferred-by-design.

## Progress (round 12 — pre-existing Tier-3 failure clusters closed, 15/15)
All three clusters from the round-11 Tier-3 backlog are fixed (each was a one-line-seed defect, not a redesign):
- **ψ-fidelity cluster (7 tests) — snapshot aliasing in `_check_plasticity`**: the tracing `plasticity.step` wrapper stored the caller's `psi` dict by reference, but `_step_psi`'s writeback (`psi.clear(); psi.update(new_psi)`, pipeline.py:131) mutates that same dict — so `trace[-1]` pre/post aliased to identical contents and `_psi_max_delta` reported 0 ("inert plasticity update") for every non-null primitive. Fix: snapshot `pre = dict(psi)` / `dict(new_psi)` in the wrapper (fidelity.py). Root cause is in the *check*, not the plasticity primitives or the pipeline writeback (the writeback is correct — cross-episode ψ persistence needs it). All 45 fidelity tests green.
- **`test_system_spec.py` cluster (7 tests) — `grid_hw` tuple restore missing**: `_geometry_spec_parts`'s JSON tuple-restore list (`factory.py:93`) covered `hidden_dims/conv_channels/input_hw/pool_hw/lattice_dims` but not `grid_hw`, so the NCA spec round-trip compared `[16,16]` vs `(16,16)`. Added `"grid_hw"` to the list; GeometryConfig now has no remaining un-restored tuple fields (all 6 enumerated). 20/20 green.
- **`readme_snippet_lock` — GeometryConfig wrap drift**: README's locked `swap_credit` block had `GeometryConfig.recurrent(...)` on one line; the demo test wraps it across 3 lines (ruff 88-col). Lock compares stripped lines in order, so the single wrap mismatch failed the whole block. README updated to the test's 3-line form; lock script green. Lesson: line-wrap shape in locked snippets must mirror the source test exactly — reformat only test and block together.
- Battery: 245 passed / 6 skipped / 4 xfailed (spec + lock + fidelity + discovery + joint + slice + substrate). Ruff format+check clean on changed files; pyright on changed files byte-identical to HEAD (7 pre-existing factory.py TypeVar-union errors, 0 new).
- **Tier-3 expectation**: the full suite should now be fully green except skipped/xfailed/xpassed (round 11's 15 failures + the gallery drift were the entire delta; a full re-run at round close will confirm).

## Progress (round 11 — CLI pyright clean, Tier-3 round close)
- **CLI pyright backlog**: lab.py + kernel_profile.py now **0 pyright errors**. Plasticity union widening solved at the call sites (`cast("PlasticityPrimitive", ...)` with a duck-typing comment — compose_joint_system stores bare `PlasticityConfig` for the null branch; widening the `TP` TypeVar bound was tried and rejected: +1 pyright error inside joint.py); `task_loss` properly imported from `computronium.core.pipeline` (the `undefined-name` ignore hack removed); trajectory activity comprehension narrowed with an `isinstance Tensor` filter.
- **Instrument fix** (`core/profiling.py::count_flops`): dropped the `requires_grad` filter — frozen θ still incurs forward/backward-through FLOPs, so `evaluate_migration`'s ψ-only migration (θ frozen after A0) reported `compute=0.0` and failed `test_algorithm_migration_smoke` (pre-existing at HEAD, 2/3 cells). Now 3/3 pass.
- **Gallery re-pin healed**: the working tree carried a stale `d19_depth_harvest.json` record (data hash ≠ provenance config_sha). Re-ran the demo emitter (`test_demo_depth_harvest.py`, 5 min 22 s walltime) and re-pinned `docs/figures/manifest.json` `data_sha256` to the fresh `8c8e7a44ea...` value; `test_gallery_lock` 2/2 green. Record numbers moved slightly vs HEAD (depth_32 ema 0.917→0.922, depth_50 final 0.784→0.840) — regenerated with current code, deliberate re-pin.
- **pip-audit**: 1 finding (pytorch-lightning 2.6.5, PYSEC-2026-3967) → fixed by bumping to 2.6.6; now zero known vulnerabilities. Dev-env smoke green after re-pin.
- **Tier-3 full suite**: `16 failed, 1859 passed, 60 skipped, 32 xfailed, 1 xpassed` in 25 min 38 s. **15 of 16 are byte-identical pre-existing failures at HEAD**; the 16th (gallery drift) was tree-induced and is fixed. Pre-existing clusters: (a) `tests/unit/core/test_system_spec.py` 7 spec-round-trip failures, (b) `test_readme_snippet_lock.py::test_readme_locked_snippets_match_their_demo_tests` 1, (c) fidelity cluster 7: `test_campaign_fidelity` (plasticity-fidelity 3, capability-manifest 2), `test_discovery_locks::TestFidelityStanding` 1, `test_fidelity_meta_validation` 1 — ψ-fidelity pipeline reports `fail` where `pass` is expected (fast-weights ψ target-activity threading). These are the known Tier-3 backlog, not TODO18 regressions.
- Note: `pytest -o faulthandler_timeout=0` is required for long demo tests (default `faulthandler_timeout=120` dumps at 2 min and can abort slow-tier runs; `timeout=60` signal method also needs raising for demo reruns).

## Progress (round 10 — complexity refactors, repo ruff green)
- **credit.py**: `RandomProjectionsCredit.compute_pseudo_gradient` split into `_block_path` / `_layered_path`; `TemporalTraceCredit.compute_pseudo_gradient` split into `_timing_stdp_grads` / `_timing_stdp_one` (per-weight) / `_homeostatic_scale` / `_rate_stdp_grads`; `TargetInversionCredit` block path extracted to `_block_target_grads`. All behavior-preserving (gradient equivalence + native smoke + ontology locks green). credit.py now ruff-clean AND pyright-strict-clean.
- **factory.py**: `compose_system_from_configs` update-dispatch table replaced by delegation to spec.py's canonical `_update_from_config` (kills a third copy of the dispatch). During the refactor a latent break was caught and fixed: my first edit accidentally truncated the `compose_system(...)` call — verified by an end-to-end `compose_system_from_configs` construction round-trip (ran `ok _ComposedSystem`).
- **system.py `validate()`** and **joint.py `compose_joint_system_from_configs`**: `too-many-statements` added to their pre-existing documented `ruff: ignore` lists (config-dispatch functions; splitting would fragment the constraint table).
- **Repo ruff state: 9 → 0. Whole `computronium/` tree passes `ruff check` clean.**
- Battery: 192 property tests (mechanistic/memory/gradient/native/parity/joint) + 14 integration (validation_all + slice gate) all green.

## Progress (round 9 — Register C sweep)
- **pyproject config corrections** (rules-as-config, per AGENTS): `TRY003` (raise-vanilla-args) added to the ignore list — the pre-existing `RSE102` ignore was misattributed; long descriptive raise messages are the sanctioned style, clearing 367 findings repo-wide. `RUF069` (float-equality-comparison) ignored with the same rationale as `PLR0133` (exact sentinel comparisons against exactly-assigned configs). `RUF067` (non-empty-init-module) per-file-ignored for `ontology/dynamics/__init__.py` (the DYNAMICS_REGISTRY wiring point).
- **Dual `CompositeState` unified**: `computronium/core/joint/state.py` deduplicated — it re-exports StateVariable/StateRegistry/CompositeState from `computronium.state` and keeps only `JointTrajectoryRecorder`. `record()` now skips non-tensor activity entries (loss scalars/metrics dicts) explicitly. The state/composite vs core/joint identity pyright errors are gone.
- **test_lifecycle_locks.py**: pyright 0 errors (was 15 → 7 after round 8 → 0 now; `_tensor()` narrowing helper).
- **Repo ruff state**: 400 findings → 9. Remaining 9 are genuine complexity refactors queued for Register C: `credit.py::compute_pseudo_gradient` (788: 11>10; 1859: 15 branches/30 locals/56 stmts), `credit.py:2064` locals, `system.py:248` statements, `factory.py:598` complexity, `joint.py:475` statements. CLI/lab.py + cli/kernel_profile.py now ruff-clean (the 14 EM102/TRY003 findings cleared by the config fix); their 11 pre-existing pyright errors are byte-identical to baseline (0 new).
- Battery: 177 passed (joint + credit lock + labels + native smoke), tile/geometry/settle/energy subset 79 passed. Auto-fixed files pyright-checked (0 new errors).

## Progress (round 8 — CompositeState Mapping fix)
- **`CompositeState.activity` Mapping fix**: fields `activity`/`plastic`/`substrate` now declared `Mapping[...]` (covariant — `dict[str, Tensor]` call sites typecheck), converted to mutable dicts in `__post_init__` as before. New public accessor `CompositeState.set_activity(key, value | None)` routes all property setters (x/y/activations/free_state/nudged_state/loss/metrics) through one mutable-dict cast; CLI write sites (`cli/lab.py`, `cli/kernel_profile.py`) migrated to `set_activity`. `computronium/state/composite.py` is now pyright-strict clean (0 errors). The ~15 dict-invariance errors at test call sites are gone; 7 legacy pyright errors remain in `test_lifecycle_locks.py` (4 value-narrowing `ActivityValue`→`Tensor`, 1 `Tensor | None`, 2 dual-CompositeState identity) — queued Register C. Joint battery: 136 passed / 6 skipped / 4 xfailed.
- **Dual `CompositeState` duplication**: ✅ resolved round 9 — `core/joint/state.py` now re-exports the canonical `computronium.state` classes.

## Progress (round 7 — requires_autograd lock + README evidence + MNIST seam)
- **`requires_autograd` semantic lock**: `tests/property/test_credit_semantics.py` — freezes the declared-True set {RandomProjectionsCredit, LocalGoodnessCredit, LemmaCredit, TargetInversionCredit, GradientCredit, BackpropCredit}. Any flip fails with instructions to update lock + docstrings in the same commit. Caveat encoded: PepitaCredit/LocalContrastiveCredit legitimately declare False (they build their own graph inside `compute_pseudo_gradient`; the settle graph is irrelevant).
- **Track B evidence**: README gained a collapsible "Campaign first records" details block after the E-probe block — mechanistic-study headline + updated 648-cell memory-stability headline (delay-32 numbers, coupling axis, `state_noise_divergence`, scatter entry point), explicitly labeled probe-scale Level 4/5. Label lint green.
- **MNIST slice seam**: `run_slice(batch_provider=...)` in `vertical_slice.py` — `type BatchProvider = Callable[[int], tuple[Tensor, Tensor]]`; `synthetic_batch_provider` (default, preserves the pinned digest — gate green unchanged), `fixed_dataset_batch_provider` (deterministic shuffled-epoch walk over caller-supplied tensors, own `torch.Generator`; task recorded as `"custom"`). Real MNIST tensors are loaded by the caller; slice code is batch-source agnostic. Two new property tests (fixed-batch invariance, deterministic walk + custom label).
- Battery: slice 14 + gate 2 + credit lock 1 + labels 5 + memory 8 all green; default-slice digest unchanged (`5d93dadfa0c3ca5f`).

## Progress (round 6 — 5.2 extensions + hygiene + FA regression fix)
- **5.2 extensions**: `coupling` axis added (`open`/`coupled` — memory feeds back into the state block through a random fixed `W_fb`), delay 32 added to the sweep, and `retention_contraction_scatter()` extracts per-cell (nominal ρ, measured contraction, retention) points for plotting/probing. New trial metric `state_noise_divergence` = paired noisy-vs-zero-noise replay final-state distance — this is where coupling/precision effects on the *state arm* live (retention reads m only and is structurally coupling-invariant). Record re-pinned at `results/memory_stability/claim_record.json` (648 cells, 3 seeds × 8 trials, 41 s). Headline at delay 32: selective retention = 1.0 at every contraction (open & coupled); ungated collapses to 0.077; coupling *lowers* measured contraction (coupled trajectory has larger x → smaller tanh-Jacobian factors) without touching retention. Tests: 8 pass (coupled-selective-survives-noise/delay32, coupling-reaches-state-arm, scatter shape/axes added).
- **FA regression fixed**: an earlier uncommitted round had flipped `RandomProjectionsCredit.requires_autograd` True→False — the pipeline then settled NUDGED under `no_grad`, detaching the settle graph FA's `autograd.grad(loss, logits)` needs; FA/DFA training became silent no-ops (caught by `test_native_fa_learning_capability`). Restored to `True`. Lesson: `requires_autograd` is a *functional* contract, not metadata — flipping it changes pipeline grad context (`core/pipeline.py:169`).
- **Hygiene**: RESEARCH3.md §stability now names `spectral_radius_from_jacobian` + `JacobianAmplificationEstimator` (last stale `SpectralRadiusEstimator` reference gone repo-wide). `pepita_native.py` → `lemma_native.py` rename complete: `create_native_lemma_mlp`/`native_lemma_mlp`, root `_LAZY`/`__all__`/TYPE_CHECKING updated, `cli/repro.py` + `param_estimator.py` + 4 test files migrated, docstrings corrected to Forward-Forward goodness math. No demo/gallery entries referenced the native (re-pin not needed). Battery: 73 native/parity/gradient + 8 validation + 12 labels/wiring + 8 memory, all green.

## Next up
1. ~~Round-close verification~~ ✅ done (round 13 — full suite green).
2. **C.3** (optional): mutmut over `frozen_theta.py` — only if the audit logic changes.

## New improvement opportunities
- **`_check_plasticity` snapshot hardening**: the aliasing bug (round 12) came from storing caller-owned dicts in a trace. A `SystemState`-style frozen projection for ψ trace entries would make such checks structurally alias-proof; low priority (dict-snapshot now in place).
- **Locked-snippet reformat rule**: any future `ruff format` change to a demo test wrapped in a lock marker must be paired with a README block update in the same commit; consider adding the lock-marker files to the pre-commit `identity-cards`-style hook for visibility.
- ~~Card drift lock~~ ✅ done (round 14). ~~ClaimRecord multi-seed pinning~~ ✅ done (round 14). ~~Lemma inertness investigation~~ ✅ closed (round 14 probe: rule-quality boundary, not coordinate mismatch).
- **Memory-campaign record growth**: 648-cell JSON is fine now; revisit if more axes arrive.
- **MechanisticStudyRecord/campaign runner generalization**: both study modules share per-cell ClaimRecord aggregation; a `CampaignRunner` seam would dedupe if a third campaign arrives.
- **`requires_autograd` semantic lock**: ✅ done (round 7) — `tests/property/test_credit_semantics.py` freezes the declared-True set {RandomProjectionsCredit, LocalGoodnessCredit, LemmaCredit, TargetInversionCredit, GradientCredit, BackpropCredit}; failure message instructs docstring + lock updates in the same commit.
- **FrozenThetaAudit optimizer coverage**, **SubstrateSpec internal wrapping**, **native `CompositeState` Mapping fix**: carried from earlier rounds.

## Details that facilitate future work
### Round 12 details (Tier-3 cluster fixes)
- **Diagnostic pattern**: reproduce the check manually (import the module, call `check_coordinate_fidelity`, inspect `AxisCheck.detail` — it's a frozen dataclass, attribute access not subscripting), then drive the traced wrapper by hand. The aliasing bug was invisible in the primitives themselves; only the trace pre/post comparison exposed it.
- **`psi` writeback contract**: `_step_psi` (pipeline.py:131) intentionally mutates the caller's `psi` dict in place (`clear()` + `update()`) so ψ persists across episodes when `plasticity.step` returns a fresh dict. Any check that snapshots ψ *must* shallow-copy before the step (`dict(psi)`), because tensor values are replaced, not mutated — shallow copies are sufficient, clones unnecessary.
- **GeometryConfig tuple fields (complete list for spec round-trips)**: `hidden_dims`, `conv_channels`, `input_hw`, `pool_hw`, `lattice_dims`, `grid_hw` (+ nested `connectivity.lattice_dims`). `_geometry_spec_parts` is the single restore point.
- **Locked snippet mechanics**: `scripts/readme_snippet_lock.py` compares every nonblank, non-harness README block line as a stripped in-order subsequence of the source test file. `_HARNESS_EXEMPT_PREFIXES` = `("def _flatten(", "for x, y in ")` — loader-cap churn in `_flatten` is deliberately exempt; API lines keep full teeth.

### Round 6 details (5.2 extensions)
- **Coupling semantics**: `x_{t+1} = tanh(W_x x_t + W_in u_t + W_fb m_t + ξ_t)` with `W_fb` seeded at `seed+2`, scale 0.3, built only when `coupling == "coupled"`. `m` is driven by inputs only — never by x — so the linearized state perturbation decay stays `∏(1−x_t²)W_x`; coupling shifts the trajectory the Jacobian is evaluated along, not its structure. `_measured_contraction` now replays a zero-noise episode on the rig's own maps (was: synthetic map + contraction-derived seed).
- **Paired replay**: each episode is run twice with the same `torch.manual_seed(seed*1000+trial)` — once at `noise_level`, once at 0 — so `state_noise_divergence` isolates exactly the noise the state arm absorbs (shared pattern/distractor/write-noise realization; zero-noise draw yields exact zeros). Doubles episode count; acceptable at these dims.
- **Scatter**: `retention_contraction_scatter(record)` parses cell names into typed points (gate/coupling/precision/readout/noise/delay + nominal/measured contraction + mean retention). `ClaimRecord` keeps only aggregated metrics, so scatter is per-cell means, not per-seed.
- **Cell name layout**: `{gate}/{coupling}/{precision}/{readout}/rho{c}/noise{n}/delay{d}` — 7 fields now; `cell.split("/")[0]` still yields the gate.
- **`requires_autograd` bisect method**: stash-all, then `git checkout stash@{0} -- <file>` one candidate at a time on a single failing test — isolated `credit.py` as the carrier. Cheap and precise; reuse for future tree-vs-HEAD regressions.
- **5.2 simplification (updated)**: with the coupled mode the state block no longer strictly supplies "contracted computation measured separately" — in coupled cells noise/precision reach x through m. Retention remains coupling-invariant by construction (readout reads m only).

### Round 5 details (archived)

- **Round 5**: identity cards 22/22 (`--strict` green, pre-commit `identity-cards` hook); lemma-liveness follow-up: lemma channel live (ΔG ≈ ±7e-3, pg norms 4.2/0.79) but free-loss descent ≈ 0 at matched norms and beta inert for the lemma rule (projection-modulated contrast, not thermodynamic) — recorded on `LocalGoodnessCredit.IDENTITY_CARD.validated_limits`, a real directional-quality boundary not a wiring defect. Battery 26 (labels 7, exports 2, wiring lock, ontology locks).

### Round 4 details (archived)

- **5.1 (all)**: mechanistic study module + 12-cell first record + 6 property tests; `free_loss` promoted to public panel API; root exports wired (lockstep green).
- **5.2 (all)**: memory-stability campaign module + 216-cell first record + 5 property tests; hypothesis direction confirmed in first record.
- **C.2**: vertical-slice gate added to `.github/workflows/ci.yml` (workflow pre-existed; plan was stale).
- **C.4**: claim-record linting extended to `computronium/` docstrings + README + non-archive docs; zero violations.
- **Track B (§1-7)**: README retitled to "Composable Laboratory"; motivation demoted to collapsible "motivating hypothesis"; six-axis framed as compatibility-constrained subset; `SubstrateSpec` section added; Mermaid relabeled **Schematic Coupling Diagram**; joint operator now $F_{\theta_e}(z_t, u_t, \xi_t, \Delta t_t; \cdot)$; Frozen-θ contract (Boundary + Stage-Boundary Invariance) documented with `FrozenThetaAudit`; P-axis reframed to architectural benefits + corrected E-probe block; LaSalle claim weakened to documented-assumptions form; ρ/σ_max explicitly separated; **Verification Taxonomy section added** (5 levels); EqProp "no weight transport" removed (reciprocal/symmetric requirement stated; FA/FF reworded to "no transport shortcut"); PEPITA row corrected to published input-modulation math; Holomorphic EP marked complex-valued-not-quantum; `docs/IDENTITY_CARDS.md` generated + linked; ψ "passenger" replaced with exact statistics (2.0 avg / 9.1 max pts, no equivalence claim); installation prerequisites + `device=` defined in factory snippet; scientist/frontier labeled automation tools.
- **Pre-existing fixes surfaced this round**: root `__all__`/`_LAZY` lockstep repaired (`run_slice`, `render_taxonomy_markdown` were missing `_LAZY` entries); README snippet lock markers (`<!-- lock: ... -->`) added for swap_credit/composition_6axis + swap_credit block re-wrapped to match its demo test; bogus `# ruff: ignore[...]` directives in `vertical_slice.py` replaced with `# noqa: S404`.
- Battery: 33 passed targeted (mechanistic 6, memory 5, labels 5, slice 12+gates, exports/locks). New modules pyright-strict clean; ruff clean.

- Renames are no-compat (per AGENTS): grep `estimate_spectral_radius|SpectralRadiusEstimator|SpectralRadiusConfig` → zero hits left in repo.
- `FrozenThetaAudit` exit re-collects persistent state, so it also detects *added/removed* tensors (reported as `rebound`).
- `Tensor._version` increments on any in-place op even after `copy_` rollback — the mechanism that catches mutate-then-restore; do not "fix" spurious version bumps by cloning into the audited tensors' storage.
- Identity-card scan matches `IDENTITY_CARD` attr on concrete classes with `compute_pseudo_gradient`/`step` in the three ontology modules; same-class aliases render once (generator dedupes by class identity) and appear in `missing` under every exported name until the target class carries a card.
- `SubstrateSpec.substrate_type` hint field exists because legacy `SubstrateConfig` cannot distinguish ternary/complex/sparse from fields alone; new code should construct specs directly.
- Banned-phrase enforcement lives in `tests/property/test_verification_labels.py` and covers tests/ modules, `computronium/` docstrings (AST), and README + non-archive docs (C.4 complete).
- **Vertical slice re-pin procedure**: change slice config/code → run `python -c` snippet (see baseline pin below) → update `test_config_digest_stable`'s expected digest → re-pin `results/vertical_slice/claim_record.json` in the same commit. The baseline was pinned with: `run_slice(seed=0, n_steps=12)` at digest `5d93dadfa0c3ca5f`.
- Slice determinism depends on `torch.manual_seed` only (no cudnn nondeterminism at these dims); keep dims small if the gate ever runs on GPU.
- **5.1 calibration**: one proportional rescale is exact at step 1 with momentum 0 for BOTH step semantics (`gradient_relative`: disp ∝ lr since grad_clip saturates euclidean at disp = lr; `per_element_displacement`: disp = step·√n). Dead cells (zero displacement) return lr 0 and are reported inert — never silently mis-calibrated.
- **5.1 `improvement_per_norm` aggregates as mean of per-seed ratios** — the ratio-of-means identity does NOT hold; tests assert finiteness + sign sanity, not the identity.
- **5.2 retention normalization**: recall error is normalized against the gate-scaled payload `g·target`, NOT raw target — the (1−g)² write-scale artifact otherwise masks all precision/quantization/readout effects.
- **5.2 delay semantics**: `delay` counts distractor steps AFTER the cue (episode = delay+1 steps); re-pinned `results/memory_stability/claim_record.json` on 2026-09-10.
- **5.2 simplification (documented)**: write payload is the input itself (`h = u_t`); the state block supplies the contracted dynamics, measured separately via perturbation decay — noise/precision therefore act on retention only at write time and through the readout. Coupling m back into f is the next extension.
- Study/campaign artifacts re-pin: `run_mechanistic_study()` / `run_stability_memory_campaign()` → `results/{mechanistic_study,memory_stability}/claim_record.json` (deterministic given seeds; walltime/commit excluded from determinism tests).

