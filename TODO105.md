# TODO105 — Close the Remaining Gaps

## Scope
The capability map is evidence-based (52/75 viable+blind, breadth PASS, box-keyed cost model). Three items remain, each with a trigger and a measured box.

---

## 1. Geometry re-run — record the two carriers
**What:** run the geometry axis at `SEC_RUNG2=none` so `geometry/graph@cora` (0.114 @ 1.0 s) and `geometry/spatial_lattice@mnist` (0.917 @ 52.5 s) appear in the serial map, closing A30's "unsupplied" gap on data.
**Command:**
```bash
SEC_AXES=geometry SEC_RUNG2=none SEC_RESULTS_DIR=results/sec/serial4 \
uv run python scripts/run_full_sec_competitive.py
```
**Lock:** both rows measure and are viable in `results/sec/serial4/geometry/geometry_results.json`.

---

## 2. 5.3 Claim — pre-register a certifiable minimum
**What:** the n=64 run missed 0.8 by 0.017; seed-block d varies 0.83–1.07 (>within-block CI). A claim needs a pre-registered family minimum **every seed block clears** plus a block-variance estimate.
**Design:**
- Pilot: three seed blocks (0..63, 64..127, 128..191), each n=64, measure d and its block variance
- Pre-register: `min_d = min(block_lower_bounds) - 1.96 * block_sd` (so every block's 95% CI lower bound exceeds it)
- Fresh seeds for the confirmatory run at that `min_d`
**Target:** `credit/random_projections` at the mnist base box (measured 6 s/cell). 128 cells ≈ 15 min.

---

## 3. Hygiene queue — fix 6 stale fixtures
**What:** API drift only (no new mechanisms):
- `test_paired_ci.py` ×2: registration carries `min_d`, not `threshold`; `claim_schedule` normalises to the registered box
- `test_ladder_record_lock.py` ×2: `_train_nearest` gained `budget_s`; box-builder moved
- `test_screen_has_no_verdict.py` ×2: same `_train_nearest` signature change
**Cost:** <1 hour, parallelisable. Not a blocker for the map/claim.

---

## Success Metrics (TODO105)
| Metric | Target |
|--------|--------|
| Serial map | graph/cora and spatial_lattice/mnist viable in `serial4` |
| Claim | one pre-registered comparison at the family minimum every block clears |
| Fixtures | 127/127 property locks pass |

---

## Process Note
The SEC methodology is stable. No changes needed — each rung's stop rule is "evidence, not wall-clock". The next session closes these three items and the system is production-ready.