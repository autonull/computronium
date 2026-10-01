# Campaign Log — Iteration History

**Format**: Append-only. One entry per iteration. Never edit past entries.

---

## 2026-09-28 — Iteration 1 (TODO41 initialization)

**Command**:
```bash
uv run comp continuous --budget 120s --target-cells 10 \
  --limit-batches 10 --epochs 1 --task mnist --seed 42 \
  --objectives accuracy,walltime_s,param_count \
  --root artifacts/verify_todo41
```

**Results**: 8 completed, 0 failed, 3940 structural voids, 0 defects
- No energy clamp warnings
- No spectral radius explosions (max 0.34)
- No param blowups (tile_mesh 27K, spatial_lattice ~29K)
- Diffusion voided for non-recurrent geometries

**Fixes Applied** (from TODO40):
1. Single shared KnowledgeBase instance
2. Driver stratification with pre-computed viable topologies
3. KB path storage in driver
4. Diffusion restricted to recurrent geometries
5. spatial_lattice param budget constraint
6. tile_mesh fixed tiles_per_layer + separate backend
7. Diffusion step_size overrides
8. Structural voids documented

---

## 2026-09-28 — Iteration 2 (Post-TODO41 fixes)

**Command**:
```bash
uv run comp continuous --budget 60s --target-cells 3 \
  --limit-batches 5 --epochs 1 --task mnist --seed 42 \
  --objectives accuracy,walltime_s,param_count \
  --root artifacts/test_final
```

**Results**: 3 completed, 0 failed, 3938 structural voids, 0 defects
- Energy clamp tracking verified: `energy_clamp_count` persisted to KB (0.0)
- Tile mesh spectral radius: ~0.05 (vs ~1.87 before fix), comparable to feedforward (~0.018)
- All spectral radii < 1.0 (stable)

**Fixes Applied**:
1. **Driver RNG tiebreaker bias** (CAMPAIGN_REFERENCE.md item 7): Changed `min(..., key=lambda k: (balance, rng.random()))` to uniform sampling from minimum-balance triples via `rng.choice(min_triples)`
2. **Pre-computed viable topologies fallback** (item 8): When `viable=None`, driver now falls back to all `GRID_TOPOLOGIES` per triple
3. **Tile mesh spectral radius** (item 11): Weight initialization now scales by `1/sqrt(tiles_per_layer)` for dense fan-in

**Investigated**:
- **Spatial lattice accuracy** (item 12): With `gradient` credit (backprop), achieves ~35% val accuracy at 200K params. Limited to `instantaneous` dynamics. Low accuracy with `random_projections` is due to non-layered geometry incompatibility.

**Files Changed**:
- `computronium/autoscientist/broad_map.py` (lines 378-382, 531-536)
- `computronium/ontology/geometry.py` (lines 1321-1331)
- `tests/integration/test_continuous_burst.py` (promote_candidates call fix)

**Verification**: All integration tests pass (8/8), campaign readers pass (7/7)

---

## Template for Future Entries

```
## YYYY-MM-DD — Iteration N (tag)

**Command**:
```bash
<full command used>
```

**Results**: <N completed, M failed, V voids, D defects>
- <key metric 1>
- <key metric 2>

**Fixes Applied**:
1. <description> (CAMPAIGN_REFERENCE.md item X)
2. ...

**Investigated**:
- <description>

**Files Changed**:
- <file>: <lines/function>

**Verification**: <test results>
```
## 2026-09-28 — Iteration (auto)

**Command**:
```bash
uv run comp continuous --budget 60s --target-cells 3 --limit-batches 5 --epochs 1 --task mnist --seed 42 --objectives accuracy,walltime_s,param_count --root artifacts/test_final
```

**Results**: 3 completed, 0 failed, 3938 structural voids, 0 defects
- No energy clamp warnings
- No spectral radius explosions
- No param blowups
- Pareto spread: 3.5 pp

**Fixes Applied**:
1. Fixed driver RNG tiebreaker bias
2. Fixed tile_mesh spectral radius

**Investigated**:
- Spatial lattice accuracy with gradient credit

---

## 2026-09-28 — Iteration 3 (Diffusion + Spectral Probe Fixes)

**Command**:
```bash
uv run comp continuous --budget 60s --target-cells 10 --limit-batches 5 --epochs 1 --task mnist --seed 42 --objectives accuracy,walltime_s,param_count --root artifacts/test_fixed_probe
```

**Results**: 10 completed, 0 failed, 3894 structural voids, 0 defects
- All spectral radii < 1.0 (diffusion: 0.014, was 30K)
- All param counts within 1.5x budget (spatial_lattice 27K, tile_mesh 27K)
- Energy clamp rates: 0% (no clamps detected)
- Pareto spread: 20.0 pp (accuracy range 8.5%–28.4%)
- Median L0 accuracy: ~14% (target >25% via maturation)

**Fixes Applied**:
1. **Diffusion geometry validation contradiction** (CAMPAIGN_REFERENCE.md void category: geometry_constraint): Fixed mutually exclusive validations — recurrent geometry now allows diffusion dynamics; diffusion dynamics requires recurrent geometry. Both validations now consistent.
2. **Spectral radius probe for stochastic dynamics** (CAMPAIGN_REFERENCE.md: spectral radius explosions): Added `torch.manual_seed(0)` before each settle call in `probe_spectral_radius` to isolate deterministic Jacobian from sampling noise. Diffusion spectral radius now reports ~0.01 instead of ~30K artifact.
3. **Verified budget rematching** (CAMPAIGN_REFERENCE.md: param blowups): Spatial lattice and tile_mesh correctly constrain params to ~25K budget via existing logic.
4. **Diffusion substrate noise** (CAMPAIGN_REFERENCE.md: diffusion_noise): Confirmed `_build_substrate_config` sets `noise_level=0.05` for diffusion dynamics.

**Files Changed**:
- `computronium/ontology/system.py` (line 411): Added "diffusion" to allowed dynamics in `_validate_recurrent_geometry_dynamics`
- `computronium/autoscientist/campaign.py` (line 137): Added `torch.manual_seed(0)` in `probe_spectral_radius` activity function

**Verification**: 
- Campaign analysis: All spectral radii < 1.0, all params within budget
- Integration tests: 8/8 pass
- Campaign readers: 7/7 pass

---

## 2026-09-28 — Iteration 4 (Step Size Override Tuning — Production Broad Map)

**Command**:
```bash
uv run comp continuous --budget 5m --target-cells 50 \
  --limit-batches 30 --epochs 1 --task mnist --seed 42 \
  --objectives accuracy,walltime_s,param_count \
  --root artifacts/broad_map
```

**Results**: 65 completed (37 + 28), 0 failed, 3913 structural voids, 0 defects (new runs clean)
- Energy clamp rate on `energy_minimization × pepita × mean_norm`: 33% → 25% (1/4) after override
- All spectral radii < 1.0 ✅
- All param counts within 1.5× budget ✅
- Pareto front: 7 points, accuracy 46%–96%, spread 49.9pp
- Zero numerical defects in new verification + production runs

**Fixes Applied**:
1. **Step size overrides** (`ontology/update.py:53-76`): Aggressive multipliers for clamp/explosion-prone combos:
   - `energy_minimization × pepita`: 0.01 → **0.001**
   - `lazy × thermodynamic_contrast`: 0.05 → **0.005**
   - `lazy × local_contrastive`: 0.05 → **0.005**
   - `instantaneous × temporal_trace`: 0.01 → **0.001**
   - `spike_integration × temporal_trace`: 0.01 → **0.001**
   - `diffusion × temporal_trace`: 0.001 → **0.0005**
   - `energy_minimization × temporal_trace`: 0.005 → **0.001**
   - `lazy × temporal_trace`: 0.005 → **0.001**

**Verification Burst** (2-min, new root):
```bash
uv run comp continuous --budget 120s --target-cells 20 \
  --limit-batches 10 --epochs 1 --task mnist --seed 42 \
  --objectives accuracy,walltime_s,param_count \
  --root artifacts/verify_fix
```
- 10 cells, 0 energy clamps, 0 numerical defects, Pareto spread 43.1pp

**Files Changed**:
- `computronium/ontology/update.py` (lines 53-76): `_STEP_SIZE_OVERRIDES` entries

**CAMPAIGN_PLAN.md Improvements**:
- Added Step Size Override Tuning pattern section
- Clarified maturation pipeline (L0→L1→L2 via `--maturation` then `deep-tier`)
- Added "Interpreting Analysis Output" (historical vs new defects)
- Added Common Fix Patterns quick-reference table
- Added Iteration Log Pattern template
- Noted multi-task budget scaling (3× walltime)

**Verification**:
- Fresh verification burst: clean (0 clamps, 0 defects)
- Resumed production burst: 28 more cells, clean logs
- KB report generated: 12 Pareto points, 254 experiments
- Deep-tier: no candidates yet (L1 maturation needed first)

---

## 2026-09-28 — Iteration 5 (Multi-Task Broad Map — Started)


**Burst** (15m/task, sequential mnist -> cifar10 -> spiral, L0, `--maturation 10`):
```bash
uv run comp continuous --tasks mnist,cifar10,spiral --budget 15m \
  --target-cells 50 --limit-batches 30 --epochs 1 --seed 42 \
  --objectives accuracy,walltime_s,param_count --maturation 10 \
  --root artifacts/broad_map_mt --log-path logs/iter5_mt.log
```

**Cells**: 158 measured (mnist 59, cifar10 48, spiral 51), 0 failed, 0 runtime
defects, 57 energy-clamp events total, ~3.9k structural voids per task.
Voids: geometry_constraint 3346 / credit_geometry 288 / dynamics_credit 264 /
unclassified 1 per task (858 viable cells enumerated).

**Maturation (L1, epochs=3, full batches, 1 seed)**: 1 candidate promoted per task
— mnist `lazy|gradient|ortho_adam|feedforward` acc 0.9368 (490 s), spiral
`lazy|gradient|ortho_adam|feedforward` acc 0.9875 (9.7 s), cifar10
`energy_minimization|gradient|adam|tile_mesh` acc 0.1002 (930 s, no gain over L0).
Only 1 of 10 reserved slots was used on every task.

**Defects found and fixed**

1. `pc_alm × tile_mesh` — gate-passing crash quarantined as
   `runtime_defect: PC-ALM requires valid feedforward intermediates`
   (`pc_alm|thermodynamic_contrast|*|tile_mesh`, 1 void coordinate/task).
   Diagnosis: `validate()` whitelists `tile_mesh` for PC-ALM, but
   `PCALMDynamics._pcalm_setup` read `forward_with_intermediates` (2 acts)
   while the mesh's transitions are per-edge block matrices needing the
   5-act `settle_blocks` layout. Fix: new `_init_settle_acts` helper
   (`ontology/dynamics/_dynamics.py:833`) routes block-view geometries through
   `settle_blocks`; PC-ALM now settles and reaches all 16 edge weights.
   Regression test: `TestPCALMDynamics::test_tile_mesh_settles_with_gradients`
   (fails without the helper).
2. Spiral NaN losses (2 cells) — root-caused with
   `scripts/probes/iter5_nan_local_goodness.py`:
   - `predictive_settling × local_goodness`, hidden=512: loss 1.8e22 at batch 0
     at the default step 0.1, update-rule independent; stable for hidden=64.
     Fix: `_DYNAMICS_STEP_SIZE_OVERRIDES["predictive_settling"] = 0.01`
     (`autoscientist/compose.py:44`).
   - `lazy × local_goodness × mean_norm`, hidden=512: loss spikes to 2.9e8
     (euclidean clean). Fix: `_STEP_SIZE_OVERRIDES[("lazy","local_goodness")] = 0.1`
     (`ontology/update.py`) — max loss 0.46, still learning.
   Both cells now train a full epoch clean (0.48 / 0.45).
3. `kb_report` headline experiment count ignored `--task`, so a task-scoped
   report advertised the unfiltered table count next to its own (possibly empty)
   Pareto front. Fix: `_get_kb_stats` now takes the already-filtered experiments
   (`core/campaign/kb_report.py:526`) + regression test in
   `tests/unit/test_campaign_readers.py`.

**Verification** (2-min burst, fresh root `artifacts/verify_iter5`):
- 39 cells (mnist 19, spiral 20), 0 failed, 0 defects, 0 clamps, 0 non-finite losses
- mnist accuracy 4.8–64.0%, spiral 39.8–88.8%
- Gate: `tests/unit/core/test_dynamics.py` + `tests/integration/test_continuous_burst.py`
  → 16 passed, 1 xfailed (4m42s); `tests/unit/test_campaign_readers.py -k "not daemon"`
  → 8 passed; pyright clean on all touched modules; ruff clean (14 remaining
  findings are pre-existing complexity in untouched functions).

**KB reports** (`--task` is required; the default is mnist):
mnist 9 Pareto points / 59 experiments, cifar10 2 / 48, spiral 10 / 51.

**Open items queued for the next iteration**
- `energy_minimization × local_contrastive × mean_norm` (spiral, depth=6,
  hidden=24) recorded 57 clamp events and final_loss 190.5; the clamp did not
  reproduce on the quick-mode prefix (0 clamps at multipliers 1 / 0.1 / 0.01 /
  0.001), so no override was added without evidence. Needs a full-epoch repro.
- Only 1 of 10 L1 maturation slots filled per task, and L1 is 1 seed (the plan
  says 3 seeds) with no `--limit-batches` — a single cifar10 L1 re-run took
  930 s. Future Work #4 (maturation `--limit-batches`) plus a seed-count fix.
- Plan drift in the documented commands: `scripts/campaign_analyze.py` and
  `comp campaign kb-report` both default `--task mnist`, so the §3 commands
  report "No experiments found" on a cifar10/spiral root; `comp frontier` takes
  `--report/--backprop`, not `--study/--db`.

---

*Next: re-run the multi-task burst on `artifacts/broad_map_mt` to re-measure the
fixed coordinates, then promote the L1 front through `deep-tier`.*

---

## 2026-09-28 — Iteration 5b (Re-run + L2 promotion)

**Re-run** (same root, seed 43, 5m/task, mnist + spiral — coverage seed honoured
52/51 known cells and skipped them):
```bash
uv run comp continuous --tasks mnist,spiral --budget 5m --target-cells 30 \
  --limit-batches 30 --epochs 1 --seed 43 \
  --objectives accuracy,walltime_s,param_count --root artifacts/broad_map_mt
```
- 49 new cells, 0 failed, 0 defects, 0 clamps, 0 non-finite losses
- KB totals now: mnist 78 measured rows / 77 coordinates, spiral 81 / 80

**Defects found and fixed (deep-tier pipeline)**

1. **L2 was unreachable** — `_deep_tier_candidates` gated on front membership in
   ≥2 *distinct bursts*, but an L1 re-run inherits its burst's tag and the
   driver rarely re-samples a coordinate across bursts (1 multi-burst key in
   858 viable cells). Every task reported "0 candidate(s)" despite having an L1
   cell. Fix: `broad_map.py:1641` — stability evidence is the union of front
   memberships *and* maturity levels, so an L1 cell (a second, independent
   measurement) reaches L2. `_Candidate.stability_evidence` is reported next to
   `front_bursts`; regression test
   `test_deep_tier_promotes_an_l1_cell_in_a_single_burst`.
2. **`deep-tier --root <task dir>` reported an empty plan instead of failing** —
   the command appends the task to `--root`, so passing a task dir resolved a
   nonexistent KB and printed "0 candidate(s); 0 CEEC experiments".
   Fix: `cli/continuous.py:423` raises `FileNotFoundError` naming the campaign
   root; regression test `test_deep_tier_rejects_a_task_directory_as_root`.

**L2 promotion (3 seeds × 3 epochs, full batches)**

| Task | Cell | Accuracies | Mean | Spread |
|------|------|-----------|------|--------|
| spiral | `lazy\|local_goodness\|ortho_adam\|feedforward` | 0.9825 / 0.9875 / 0.9900 | 0.9867 | 0.0075 |
| spiral | `lazy\|gradient\|ortho_adam\|feedforward` | 0.9350 / 0.9350 / 0.9825 | 0.9508 | 0.0475 |

Both are the first claim-grade (L2) cells of the campaign: 3 fresh seeds, full
epochs, no `--limit-batches`, no clamps, no defects. `matched_control` is still
false, so these are measurement-grade, not claim-grade per §7.

**Verification**: `tests/integration/test_continuous_burst.py` 10 passed
(5m51s), including the two new regression tests; pyright clean on
`broad_map.py` and `cli/continuous.py`.

3. **L1/L2 latency was always 0.0** — `benchmark_inference` passed the task's
   raw `input_dim` to `compose_proposal_system`; vision-shaped tasks report
   `(C, H, W)`, geometry construction raised `TypeError`, and the caller's
   blanket `except Exception: return None` swallowed it into a missing metric.
   Fix: `autoscientist/benchmark.py:73` flattens through `flat_input_dim`, the
   same reduction `train_task` uses. Spiral `diffusion|target_integration|
   riemannian_orthogonal` now reports 107.2 ms / 298 samples/s. Regression test
   `tests/unit/test_inference_benchmark.py` (spiral + mnist).

**mnist L2 promotion** (3 seeds × 3 epochs, full batches) — still running at log
time, 4/6 runs done:
- `lazy|gradient|ortho_adam|feedforward`: 0.9171 / 0.9535 / 0.9552 (mean 0.9420,
  spread 0.0381)
- `energy_minimization|gradient|riemannian_orthogonal|feedforward`: 0.0973 with
  **1457 energy-clamp events** in one run and 1357 s walltime. The L0 cell sat at
  0.211 on the front, so full epochs make it worse, not better.

**Open items**
- `energy_minimization × gradient` is at override 0.5 and still clamps hard over
  full epochs with `riemannian_orthogonal`; needs a stronger override, measured
  on a short-prefix sweep (a single full run costs 1357 s).
- cifar10's only L1 cell (`energy_minimization|gradient|adam|tile_mesh`, 0.239)
  is unpromoted; its L1 re-run showed no gain over L0.
- L1/L2 rows written *before* the benchmark fix carry `latency_ms=0.0`; re-run
  the promotion for corrected latency numbers.
