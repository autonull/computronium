# TODO42 — Campaign Issues Collected (2026-09-28)

## Issues Found During Campaign Execution

### 1. Hardcoded Topology Params in `_geometry_for()` (FIXED)
**File**: `computronium/autoscientist/broad_map.py:311-318`
**Problem**: `_geometry_for(topology)` hardcoded `{"topology_type": topology, "depth": 2, "hidden_dim": 64}` instead of letting `build_geometry_config()` auto-size from `param_budget`.
**Fix Applied**: Modified `_geometry_for(topology, param_budget=25000)` to pass only topology; `build_geometry_config()` now auto-sizes `hidden_dims` and `depth` from budget when not explicitly provided.

### 2. Auto-Sizing Logic in `build_geometry_config()` (COMPLETED)
**File**: `computronium/autoscientist/compose.py:198-385`
**Problem**: Auto-sizing `_auto_size_geometry()` only handles `feedforward`, `recurrent`, `attention`, `ntm`, `causal_transformer`. Other topologies (`tile_mesh`, `spatial_lattice`, `nca`, `conv`, `graph`) still use hardcoded defaults.
**Fix Applied**: Extended `_auto_size_geometry()` with param estimation formulas for all topologies. Updated `build_geometry_config()` to use auto-sized values for tile_mesh, spatial_lattice, nca, conv, graph.
**Verified**: Dry-run shows topology diversity (recurrent, feedforward, ntm, tile_mesh, spatial_lattice) with auto-sized params ~25K budget. Production burst: 9 cells completed, params 22K-32K, spectral <1.0, clamp rates <20%, Pareto spread 63.7pp.

### 3. Dry-Run Output Shows `depth=? hidden=?` (FIXED)
**File**: `computronium/cli/continuous.py:371-381`
**Problem**: Dry-run prints `geo.get("depth", "?")` and `geo.get("hidden_dim", "?")` but proposals no longer include these keys (auto-sized at execution time).
**Fix Applied**: Modified `propose_batch()` in `broad_map.py` to compute auto-sized `depth` and `hidden_dim` using `_auto_size_geometry()` and include them in proposal geometry dict.
**Verified**: Dry-run now shows `depth=6 hidden=48` etc. for all proposals.

### 4. Historical 574s Walltime Outlier Pollutes Analysis
**File**: `scripts/campaign_analyze.py` scans full KB history
**Problem**: Old `lazy × gradient × ortho_adam × feedforward` cell (574s, acc=0.0000) persists in KB, skewing Pareto walltime range. Fixed via step_size override `("lazy", "gradient"): 0.01` but analysis still shows historical data.
**Mitigation**: Per CAMPAIGN_PLAN.md §4, run fresh verification burst (new root) for ground truth.
**Status**: Fresh burst completed on `artifacts/broad_map_v2` with clean KB - no historical baggage.

### 5. Energy Clamp Fixes Applied
**File**: `computronium/ontology/update.py:53-76` (`_STEP_SIZE_OVERRIDES`)
**Fixed Combos**:
- `("energy_minimization", "thermodynamic_contrast"): 0.00005` (was 0.0001)
- `("energy_minimization", "pepita"): 0.0001` (was 0.001)
- `("energy_minimization", "local_goodness"): 0.0005`
- `("energy_minimization", "temporal_trace"): 0.0001`
- `("diffusion", "temporal_trace"): 0.0001` (was 0.0005)
- `("lazy", "temporal_trace"): 0.0001` (was 0.001)
- `("lazy", "thermodynamic_contrast"): 0.001` (was 0.005)
- `("lazy", "local_contrastive"): 0.0005` (was 0.005)
- `("lazy", "pepita"): 0.001`
- `("lazy", "gradient"): 0.01` (ortho_adam SVD too slow)
- `("instantaneous", "temporal_trace"): 0.0001` (was 0.001)
- `("spike_integration", "temporal_trace"): 0.0001` (was 0.001)
- Added `("error_predictive_coding", "thermodynamic_contrast"): 0.1`
- Added `("error_predictive_coding", "local_goodness"): 0.1`

### 6. Substrate Noise for PC-ALM (FIXED)
**File**: `computronium/autoscientist/compose.py:565-566`
**Fix**: Added `"pc_alm"` to dynamics requiring `noise_level=0.05` substrate config. Fixed spectral radius 199 → <1.0.

### 7. Void Classification Patterns Extended (FIXED)
**File**: `computronium/autoscientist/broad_map.py:634-670` (`_VOID_CATEGORIES`)
**Added Patterns**:
- `("Recurrent geometry", "geometry_constraint")`
- `("recurrent geometry requires", "geometry_constraint")`
- `("must be divisible by num_heads", "geometry_constraint")`
- `("PCALM dynamics requires", "dynamics_credit")` (already existed)

### 8. Test Budget Issue (FIXED)
**File**: `tests/integration/test_continuous_burst.py:38`
**Problem**: Test uses `param_budget=0` which bypasses auto-sizing (falls back to defaults). Test should use realistic budget to exercise auto-sizing path.
**Fix Applied**: Changed `param_budget=0` to `param_budget=25000` in `_args()` fixture.
**Verified**: Tests pass with auto-sizing exercised.

### 9. Param Count Verification (VERIFIED)
**Observation**: Fresh burst with `param_budget=25000` shows all cells at params 22K-32K (within 1.5x budget). Auto-sizing working for all topologies.

### 10. LSP Type Errors (Pre-existing, Not Blocking)
**Files**: `broad_map.py`, `credit.py`, `test_dynamics.py`
**Note**: These are pre-existing type annotation issues unrelated to campaign fixes. Address in separate hygiene pass.

## Verification Checklist for Next Session
- [x] Fix dry-run display (Option A: add computed depth/hidden to proposal geometry)
- [x] Complete auto-sizing for all topologies in `_auto_size_geometry()`
- [x] Update test `test_continuous_burst.py` to use `param_budget=25000`
- [x] Run dry-run with param budget to verify topology diversity and auto-sized params
- [x] Run fresh production burst (new root, no historical baggage)
- [x] Verify: clamp rates <20%, spectral <1.0, param counts ~budget, Pareto spread >15pp
- [ ] Run maturation pipeline on clean KB (should produce L1 candidates)
- [ ] Run deep-tier promotion to L2

## New Improvement Opportunities (Discovered During This Session)

### 11. Conv Topology Param Estimation Refinement
**Observation**: Conv auto-sizing produces large channel counts (531, 265, 177, 132) because the estimation formula `in_channels * h * kernel^2 + h * output_dim` with `in_channels=3, kernel=3, output_dim=10` gives ~37h params. With 25K budget, h≈675 hits the 512 cap.
**Improvement**: Use more accurate CNN param estimation accounting for spatial dimensions and pooling. Current formula treats conv as fully-connected.

### 12. Tile_Mesh NPT/TPL Estimation
**Observation**: Tile_mesh auto-sizing uses simplified npt/tpl derivation from hidden/depth. Could be more precise.
**Improvement**: Derive npt, tpl directly from param budget equation: `params ≈ input_dim * npt + (depth-1) * npt * tpl * npt + npt * tpl * output_dim`.

### 13. NCA Grid Sizing
**Observation**: NCA grid_hw auto-sizing uses fixed 256 area (16x16). With hidden=9, params=9*9*256=20736, well under budget.
**Improvement**: Could increase grid size for more expressive NCA within budget.

### 14. Run Full 50-Cell Burst with Maturation
**Next Step**: Run the full 5-minute burst with 50 target cells and 10 maturation cells to produce L1 candidates, then deep-tier for L2.

## Commands for Next Session
```bash
# 1. Full production burst with maturation
uv run comp continuous --budget 5m --target-cells 50 --limit-batches 30 --epochs 1 --task mnist --seed 42 --objectives accuracy,walltime_s,param_count --root artifacts/broad_map_v2 --maturation 10 --param-budget 25000

# 2. Analyze fresh run
uv run python scripts/campaign_analyze.py --root artifacts/broad_map_v2/mnist

# 3. If maturation produced candidates, run deep-tier
uv run comp continuous deep-tier --root artifacts/broad_map_v2 --task mnist
```