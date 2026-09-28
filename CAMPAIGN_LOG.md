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

