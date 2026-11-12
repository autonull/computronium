# TODO89 — Claims, not defect counts (Successor to TODO88)

**Status:** 2026-11-12 · base `7110e5f4` · T1–T10 closed with measured numbers
in this session · T6 not triggered · no open ticket. T10 (this session) turns
T9's cell fold into a target, giving nca its third error-aware credit at 0.9389
(above the 0.9231 gradient control).

**Mission:** the instrument is now trustworthy enough that a low number means
something. TODO88 proved that 20 times over: six "algorithm failures" were
harness defects (wine 0.00 → 0.94, `local_contrastive` 0.11 → 0.7043, MUTAG
0.63 → 0.693, Cora 0.618 → 0.766, `sparse` ≡ digital, CUDA graph dead → parity).
TODO89 spends that instrument on the **three domains with no claim**: RL, Iris,
and credit breadth.

---

## 0. Rules — carried by AGENTS.md

TODO88's stopping rule was "every anomaly is a signal": unfalsifiable, so the
defect count substituted for the claim. Those corrections are permanent process
rules and now live in `AGENTS.md` — §Architecture *One Source of Truth per
Rule*, §SEC step 5 and *Never*, §Success Criteria (*every number carries its
ruler*, *marginal is not met*, *a ticket closes on a claim*). Read them there; a
rule in a closing TODO is prose that expires with the file.

---

## 1. Session ledger — every ticket with its measured number

| # | Ticket | Result | Evidence |
|---|---|---|---|
| T1 | **Pendulum claim.** Reference probe decides budget vs defect. | **Budget is not the limit; the claim is met.** Plain DDPG reference reaches **−123.6** at 400 episodes (untrained −1312.5). The harness reached **−6604** on its one-update-per-episode lane and **−161.2 ± 25.3** after the per-step continuous lane (n=3 training seeds; 20 deterministic eval episodes each; seeds −133.9 / −165.9 / −183.8; SE 14.6, margin over −200 = 38.8). | `scripts/probes/t1_pendulum_reference.py`, `scripts/probes/t1_pendulum_harness.py`; fix in `core/system_trainer/rl_trainer.py`; lock `tests/property/test_rl_training_lane_lock.py` |
| T2 | **Iris resolution.** Fold-mean instead of a 30-row holdout. | **Met.** Pipeline fold-mean **0.9533 ± 0.0163** (n=5 stratified folds, 100 epochs) vs target 0.90; sklearn LogisticRegression 0.9600, sklearn MLP 0.9533 on identical folds. Resolution 1/150 = 0.0067; margin 0.053 ≈ 3.2σ. The 0.867 holdout was one row. | `domains/tabular.py::fold_indices/set_fold`, `evaluation/base.py::cross_validate`; probe `scripts/probes/t2_iris_folds.py`; lock `test_tabular_split_lock.py::test_folds_partition_every_row_and_select_one` |
| T3 | **Credit-breadth table.** Read stores first, sweep only gaps. | **Table landed; four gaps named, two closed, two verdicted.** Store scan: feedforward 8, recurrent 5, tile_mesh 5, tile 4, conv 3, causal_transformer 3, ntm 3; attention 2 and spatial_lattice 2 then closed by sweep (gradient 0.9472 / 0.9361 on digits); nca 1 and graph 2 remained → verdicts in T7/T8, and nca's turned out to be dispatch (T9). Details in §2. | probes `scripts/probes/t3_credit_breadth.py`, `t3_credit_gap_sweep.py` |
| T4 | **N8 planner drift.** Delete the flat matrix; `iter_candidates` only. | **Landed by deletion.** Re-walked this session: 46,800 walked → 9,516 yielded + 37,284 counted rejections + **0 silent** (390 of the drops are T7's new declaration). The earlier 58,500 → 10,296 → 48,204 walk counted `attention`, whose only legal cell in that curated 5-geometry grid was the all-zero FA coordinate T7 now voids; `_filter_axes_for_validity` correctly drops it. Every drop still names a declared constraint. | deleted `_INCOMPATIBILITY_RULES`/`check_compatibility_matrix`/matrix from `ontology/system.py`, call sites in `wave.py`, `_admission_gate.py`; probe `scripts/probes/t4_planner_legality.py`; locks `test_prune_diagnostics_lock.py`, `test_system_config_validate_lock.py` |
| T5 | **R6 Register C hygiene.** | **Changed files clean.** `ruff check` passes on every changed file except pre-existing Register C findings in the two legacy modules we touched (`wave.py` 25, `rl_trainer.py` 5). Package-wide 316 (HEAD 315); changed files introduce **no new** finding and reduce the touched legacy modules (rl_trainer 6→5, wave 30→25). `unreachable_spec` renamed `filtered_spec` and its lock states the filtering contract instead of a stale void claim. | `tests/property/_specs.py`, `test_price_oracle_lock.py` |
| T6 | **PROTEINS marginal re-measure.** Only if cited. | **Not triggered.** T3 cites the store's gradient/random_projections cells, not the 0.7040 arm. The status table keeps `marginal` unchanged. | — |
| T7 | **FA geometry declaration.** `random_projections` returned all-zero pseudo-gradients on five geometries; declare the rule instead of inferring it at dry-run. | **Declared.** Digits 8×8 dry runs report all-zero layered-FA pseudo-gradients for every weight on attention (38), spatial_lattice (98), conv (5), nca (3) and ntm (7); tile, tile_mesh and causal_transformer train (dedicated paths). One VOID row, `random_projections_layered_geometry`, now owns the rule; the dry-run probe stays as the runtime backstop for any geometry the row does not name. **nca removed from the row by T9** (the void was dispatch). | `experiment/schema/seed_registries.py`; lock `test_dry_run_gate_lock.py` (parameterised over the four remaining, plus a removal test that bypasses dry-run and proves the row is the mechanism) |
| T8 | **Graph third credit.** Re-measure `target_inversion` at n≥3; name the `thermodynamic_contrast` verdict. | **Marginal, not met.** 200 epochs × 5 seeds on MUTAG (38 held-out graphs, resolution 0.0263, majority 0.6579): `target_inversion` **0.6842 ± 0.0204**, margin +0.0263 = **+1.29 SE**; seeds 0.684 / 0.763 / 0.658 / 0.658 / 0.658. Positive control `gradient` **0.7105 ± 0.0000**, +0.0526 = 2 graphs, all five seeds clear. The one-seed 0.6842 was one extra graph. `thermodynamic_contrast` is unreachable by declaration: `nonlayered_geometry_dynamics` admits only instantaneous dynamics on graph, and composing it anyway breaks the settle shape (`560×64 + 32×64`: pooled head block against node-mode hidden acts) — a contract break, not a Dynamo bug. | probe `scripts/probes/t8_graph_third_credit.py` |
| T9 | **NCA cell-mode FA.** T7's nca void was dispatch, not accuracy: give `random_projections` a declared cell fold. | **Met.** `NcaGeometry.cell_readout_shape()` declares `(channels, cells)`; the credit folds the sample-mode readout error back to `B*H*W` rows and the act chain now carries the post-step state act the readout consumes. Digits 8×8, 20 epochs, 3 seeds, 360 held-out rows (resolution 0.0028, majority 0.1306, chance 0.10): `random_projections` **0.8907 ± 0.0009** (SE; seeds 0.8889 / 0.8917 / 0.8917) vs `gradient` control **0.9231 ± 0.0009**. nca now has **2** error-aware credits; removing the fold raises the layered-FA contract. | probe `scripts/probes/t9_nca_cell_fa.py`; locks `test_credit.py::TestCellModeFA`, `test_dry_run_gate_lock.py`; row edited in `seed_registries.py` |
| T10 | **NCA third credit.** T9's fold carries an error; the target needs the same fold. | **Met, and above the control.** `_fold_cell_targets` folds the sample-mode one-hot output target back to `B*H*W` rows and passes it through the delta weight's transpose to the hidden act; `TargetInversionCredit` dispatches on `cell_readout_shape`. Same protocol as T9 (digits 8×8, 20 epochs, 3 seeds, 360 held-out rows; resolution 0.0028, majority 0.1306, chance 0.10): `target_inversion` **0.9389 ± 0.0056** (seeds 0.9333 / 0.9500 / 0.9333) vs `gradient` control **0.9231 ± 0.0009** — +0.0158 ≈ +2.8 pooled SE, ≈6 held-out rows. **nca now has 3** error-aware credits. The declaration that voided the coordinate (`nca_instantaneous_target_inversion`, in both the registry and `SystemConfig.validate`) is deleted; removing the fold leaves every target None (all-zero pseudo-gradients), which is the lock. | probe `scripts/probes/t10_nca_cell_target.py` (24.8 s); locks `test_credit.py::TestCellModeTargetInversion`, `test_dry_run_gate_lock.py::test_target_inversion_accepts_nca_digits` |

**Do not reopen (TODO88 §Closed):** G1–G20, R1–R5, R7–R9, N1–N7, N9, N10.
Each has a measured number and a lock; the numbers are at the mechanism and in
the commit.

---

## 2. Credit-breadth table (T3) — the criterion behind the words

Counted from PASS records with `error_blind == False`; `homeostatic` and
`temporal_trace` never count.

| Geometry | Error-aware credits | Count | Status |
|---|---|---|---|
| feedforward | gradient, local_contrastive, local_goodness, pc_alm, pepita, random_projections, target_inversion, thermodynamic_contrast | 8 | met |
| recurrent | gradient, pc_alm, random_projections, target_inversion, thermodynamic_contrast | 5 | met |
| tile_mesh | gradient, pc_alm, random_projections, target_inversion, thermodynamic_contrast | 5 | met |
| tile | pc_alm, random_projections, target_inversion, thermodynamic_contrast | 4 | met |
| conv | gradient, pc_alm, target_inversion | 3 | met |
| causal_transformer | gradient, pc_alm, random_projections | 3 | met |
| ntm | gradient, pc_alm, target_inversion | 3 | met |
| attention | pc_alm, target_inversion + **gradient 0.9472** (sweep) | 3 | met |
| spatial_lattice | pc_alm, target_inversion + **gradient 0.9361** (sweep) | 3 | met |
| nca | gradient, random_projections, **target_inversion 0.9389** (T10) | 3 | met (T10): the target folds like the T9 error, clearing the 0.9231 gradient control by +0.0158 (≈+2.8 SE, 360 held-out rows). `pc_alm` and `homeostatic` remain void on nca × instantaneous by declaration. |
| graph | gradient, random_projections | 2 (+1 verdict) | **gap with verdict (T8):** `target_inversion` 0.6842 ± 0.0204 at n=5 × 200 epochs vs 0.6579 majority — +1.29 SE, marginal, not met (gradient control 0.7105, all seeds clear). `pc_alm` 0.3421 (below majority); `thermodynamic_contrast` is unreachable by `nonlayered_geometry_dynamics` and the energy settle cannot represent a pooled readout. |

**Every gap carries a verdict** (graph measured, T8). No ticket is open here:
the remaining third credit on graph is new algorithm work, not a defect in
TODO89's scope.

**Known duplicate (blocks the next nca credit):** the nca × instantaneous
`homeostatic` and `pc_alm` voids exist twice — as registry rows and as
`SystemConfig.validate` methods. This session had to delete both for
`target_inversion`'s rule. Consolidate onto the registry row (or make
`validate` consult it) before adding the next cell-mode credit; the duplicate
is a one-source-of-truth defect and can drift silently.

**Known limit:** continuous RL checkpoint resume restores the system and
optimiser but not the replay buffer or target networks, so a resumed
continuous run cold-starts its critic. Open only if resumable RL runs matter.

---

## 3. Success criteria — current truth

| Domain | Target | Measured | Status |
|---|---|---|---|
| Vision (MNIST) | > 0.95 | 0.972 | met |
| Node classification (Cora) | > 0.75 | 0.766 (n=3) | met |
| Graph classification (PROTEINS) | > 0.70 | 0.7040 ± 0.0071 (n=5, non-default arm) | **marginal** (§0, T6 not triggered) |
| Tabular wine | > 0.90 | 0.94–0.97 | met |
| Tabular Iris | > 0.90 | **0.9533 ± 0.0163** (n=5 folds) | met |
| RL (Pendulum) | mean_reward > −200 | **−161.2 ± 25.3** (n=3 seeds, 20 eval episodes each; SE 14.6) | met (margin 1.5 seed-σ) |
| ≥3 error-aware credits per geometry | per geometry | 10 of 11 geometries | graph (2) carries a verdict (§2) |
| Telemetry warnings | 0 | 0 after G9 | met |
| Positive control PASS | 100 % | pass on every claimed run | met |

---

## 4. Per-ticket protocol (SEC, tightened)

```
RUN      ≤15 min, one hypothesis, kill time pre-registered
ANALYZE  30 s: chance-level? loss growing? pruned? telemetry? majority baseline?
FIX      ≤15 min, infrastructure only, one defect class (§0.2)
VERIFY   same command, one re-run
CLAIM    a number, or the word exploratory — nothing else closes a ticket
```

A domain claim additionally writes `configs/preregistrations/<slug>.json`
**before** the confirming run when it gates a decision (§0.3).

---

## 4b. Remaining work — feature, not tickets

No TODO89 ticket is open. One breadth gap is left, so the plan keeps the
trigger explicit instead of re-deriving it:

1. **graph third credit** (currently 2: `gradient`, `random_projections`).
   `target_inversion` is marginal (+1.29 SE, n=5); closing it needs either a
   credit that clears the 200-epoch protocol on every seed, or a graph-aware
   energy settle (pooling before the head, neighbor aggregation inside the
   settle chain) to unlock `thermodynamic_contrast`. The settle contract's
   single row space is the blocker, not Dynamo. `pc_alm` is 0.3421 (below the
   0.6579 majority).
   - **Acceptance:** n=5 seeds × 200 epochs on MUTAG, every seed above the
     0.6579 majority by more than 1 σ (38 held-out graphs, resolution 0.0263);
     otherwise the verdict stays `marginal`.
2. **PROTEINS 0.7040** stays `marginal` until a claim cites that arm; then T6's
   paired re-measure (pre-registered if it gates a decision) is the trigger.

**Closed by T10:** the nca third credit (`target_inversion` 0.9389, §1). Do not
re-derive it; the fold lives in `_fold_cell_targets` and the locks hide it.

---

## 5. NO (unchanged from TODO86–88)

Paper figures · publishing artifacts · hypothesis backlogs · preventive fixes ·
retrospectives · cycles > 30 min · repo-wide gates outside round close.
