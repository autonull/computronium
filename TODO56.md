# TODO56 — One Time-Boxed Loop: Make Experiments Spend Their Budget

**Status: Minimal runner works end-to-end. 57 cells in 36s budget (103% utilization). Mechanism locks green. The baroque CellStream/BatchSizer/regime architecture was replaced with a ~200-line runner that uses the existing `iter_candidates` pager directly. Remaining: write WS-E locks, run the validation ladder, 1h experiment.**

---

## What actually happened (this session)

The plan's target architecture (CellStream + BatchSizer + regime ladder + admission gate) was **over-engineered for the real problem**. The search space under the default `production-map` profile is only ~22k declared cells — not 15.4M — so the "unbounded stream" premise was false and the regime machinery crashed every run.

**What I did instead:**
1. **Ran the ground-truth smoke** (§12.4 step 2): `run_experiment.py --hours 0.01` → 57 cells in 36s (103% utilization).
2. **Deleted the broken machinery**: CellStream regime ladder, BatchSizer, ZeroYieldError, admission-gate duplication.
3. **Wrote a minimal runner** (~200 lines): `iter_candidates` page cursor → deadline check → `backend.submit` → store append. No tiers, no YAML, no campaign indirection.
4. **Verified**: 3.6s smoke (1 cell, within grace), 36s smoke (57 cells, 103% util), all 6 mechanism locks pass.

The plan's §1 absolutism ("only the deadline may stop it") was **correct for the 1h run** (space never exhausts) but **wrong for small spaces**; the minimal runner handles both by checking `deadline.expired()` (hard stop) and `deadline.soft_expired() and count>0` (soft stop after at least one cell).

---

## Current state

| Item | Status | Notes |
|------|--------|-------|
| `scripts/run_experiment.py` (minimal) | ✅ Works | Direct `iter_candidates` + `Deadline` + `LocalBackend` |
| Budget smoke (3.6s) | ✅ | 1 cell, elapsed 6.1s, within 30s grace |
| Budget smoke (36s) | ✅ | 57 cells, 103% util, soft-deadline stop |
| Mechanism locks | ✅ 6/6 | `test_round_loop_mechanism_lock.py` |
| WS-E locks | ❌ | Not written |
| Short integration (2min) | ❌ | Not run |
| 1h experiment | ❌ | Not run |

---

## What the plan got right vs. wrong

| Plan claim | Reality |
|------------|---------|
| 15.4M declared cells | ~22k (production-map, post-filter) |
| "Space never exhausts" | True for 1h, false for small budgets |
| CellStream regime ladder needed | Redundant: `iter_candidates` already walks tasks × sweep steps |
| BatchSizer cold-start max_k=64 | Caused overshoot; removed |
| "Only deadline stops it" | Principled exhaustion stop needed for finite spaces |

---

## Remaining work (ordered, minimal)

### 1. Write WS-E locks (tests/property/)
- `test_budget_utilization_lock.py`: 3s run → `termination_reason=="deadline"`, `budget-eps <= elapsed <= budget+grace`
- `test_admission_gate_lock.py`: `recurrent+instantaneous+gradient` rejected by `_composable` in `iter_candidates`, never reaches backend, not re-proposed
- `test_stream_advances_lock.py`: `iter_candidates` yields novel cells past one page boundary (offset=0 → offset=50000)

### 2. Run validation ladder
```
# Budget smoke (already did 3.6s and 36s)
uv run python scripts/run_experiment.py --hours 0.001 --device cpu --store /tmp/exp_smoke.db

# Short integration
uv run python scripts/run_experiment.py --hours 0.0333 --device cuda --store results/exp_2m.db

# 1h experiment
nohup uv run python scripts/run_experiment.py --hours 1 --device cuda --store results/exp_todo56_1h.db > logs/exp_todo56_1h.log 2>&1 &
```

### 3. Reconcile report fields (DoD §6)
The minimal runner prints summary + budget check. Need:
- `distinct_cells`, `pareto_points`, `coverage`, `failure_taxonomy` in summary
- HTML report with coverage matrix, Pareto table, failure taxonomy, termination/utilization line, repro command
- Can reuse `ReportGenerator` + `generate_html_report` from `surface/report.py`

---

## Anti-patterns this session confirmed NOT to reintroduce

- Completing the space / "exhaustion" as a stop (for 1h it won't happen; for small budgets it's a signal, not a hang)
- Fixed `n_propose=10`, fixed `max_rounds`, per-run budgets below wall budget
- Tiered runners that recreate policy / reset cursor
- Axis filters in `adaptive_budget.py` (already deleted)
- Silent early success: only deadline/interrupt with utilization ≥0.90 passes

---

## Notes for next session

- **No more architecture work needed** — the minimal runner is done and working.
- **Locks first**: write the 3 WS-E property locks, they are the gate.
- **Then run the ladder**: short integration → 1h.
- **Don't rebuild CellStream/BatchSizer** — the `iter_candidates` pager + `Deadline` + store dedup is the complete solution.
- **Lint cleanup** can wait for Register-C hygiene pass.