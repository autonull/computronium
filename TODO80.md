# TODO80 — Compatibility & UX Hardening for CPU-first Runs

**Motivation:** A user on older hardware (driver version 9010 → CUDA 9.x) sees:
1. CUDA warning spam during self-test even with `--device cpu`
2. `budget=3s` log from self-test dry-run, then nothing appears to happen
3. Self-test runs by default adding ~35s overhead per invocation
4. General opacity about what's running and why

This document consolidates the fixes.

---

## 1. Make CUDA loading fully on-demand (no implicit `torch.cuda.is_available()` in CPU mode)

### Problem
`_check_torch()` in `simple_survey.py:699` unconditionally calls `torch.cuda.is_available()`.
This initializes the CUDA driver, which:
- Prints a scary `UserWarning` about old drivers
- Takes 1–3s on cold start
- May crash on mismatched driver/toolkit (segfault in `CUDAFunctions.cpp`)

Same issue in `diagnostics.py:121`, `_trainer_utils.py:21`.

### Fix
- **Self-test / diagnostics**: skip CUDA probe entirely when `device="cpu"` is explicit.
- **Device resolution**: `_resolve_device()` already does the right thing for `"auto"`. Just don't call `torch.cuda.is_available()` when the caller already said `"cpu"`.
- **Trainer**: `SystemTrainer._setup_device()` already checks `config.device == "auto"` before probing. Good.

### Files
| File | Change |
|---|---|
| `simple_survey.py:_check_torch()` | Accept `device: str` param; if `device == "cpu"`, skip CUDA check and log `"CUDA: skipped (cpu mode)"`. |
| `diagnostics.py:check_torch()` | Same — add `device` param. |
| `simple_survey.py:_run_self_test()` | Pass `device="cpu"` when CLI `--device cpu`. |
| `_trainer_utils.py:_resolve_device()` | Already correct — only probes on `"auto"`. No change. |

### Acceptance
```
CUDA_VISIBLE_DEVICES="" uv run comp run 0.5 --device cpu --no-self-test
# No CUDA warning, no driver init, instant start
```

---

## 2. Fix "budget=3s" confusion — self-test log leaks into user output

### Problem
The log line `"SimpleSurvey: budget=3s, fidelity=L0, cost_per_cell=5s, estimated_cells=1"`
comes from `_generate_cells()` called *inside* the self-test dry-run
(`_SelfTestConfig.dry_run_hours = 0.001` → 3.6s budget).

User sees this, thinks it's their actual run, then the real run either:
- Doesn't start (crash in self-test)
- Runs silently (no verbose output)
- Runs but output is truncated in their terminal

### Fix
- **Prefix self-test logs**: `_check_dry_run()` should use a distinct logger prefix
  (`"SelfTest:"`) or run at `DEBUG` level.
- **Actual run log**: Ensure the real `run_simple_survey()` call logs with the real
  budget (e.g. `budget=1800s`) at `INFO` level.

### Files
| File | Change |
|---|---|
| `simple_survey.py:_check_dry_run()` | Use `logger.debug()` for the budget line, or wrap in a context that suppresses `INFO` during self-test. |
| `simple_survey.py:_generate_cells()` | No change — the log is correct; just don't show it during self-test. |

---

## 3. Self-test disabled by default; opt-in with `--self-test`

### Problem
Current: `--no-self-test` to skip. Default runs 6 checks + dry-run (~35s).
User expectation: `comp run 0.5` should start evaluating immediately.

### Fix
- Flip the flag: add `--self-test` / `--doctor` to *enable* it.
- Keep `--no-self-test` as deprecated alias for compatibility.
- Self-test becomes a developer/CI tool, not a user prerequisite.

### Files
| File | Change |
|---|---|
| `simple_survey.py:main()` | Change `if not args.no_self_test:` → `if args.self_test:`; add `--self-test` flag. |
| `simple_survey.py:parser` | Add `--self-test` action; deprecate `--no-self-test`. |
| `pyproject.toml` | Update CLI help text if referenced. |

### Acceptance
```
uv run comp run 0.5 --device cpu
# Starts evaluating cells immediately, no self-test delay

uv run comp run 0.5 --self-test --device cpu
# Runs self-test first
```

---

## 4. Verbose progress by default for interactive runs

### Problem
Default output is near-silent. User runs `comp run 0.5`, waits 30s, sees nothing,
assumes it's stuck. The evaluation happens in `ProcessPoolExecutor` workers whose
logs don't propagate to the parent by default.

### Fix
- **Default to verbose for TTY**: if `sys.stdout.isatty()`, set `verbose=True`
  unless `--quiet` given.
- **Progress bar**: Use `tqdm` (already a dep) to show cells completed / ETA.
- **Worker logs**: Configure `logging` in `_evaluate_one()` to emit to a queue
  that the parent drains and prints with `[worker N]` prefix.

### Files
| File | Change |
|---|---|
| `simple_survey.py:main()` | `verbose = args.verbose or (not args.quiet and sys.stdout.isatty())` |
| `simple_survey.py:_evaluate_cells_parallel()` | Add `tqdm` progress bar over `as_completed`. |
| `simple_survey.py:_evaluate_one()` | Use `logger = get_logger(__name__)`; ensure logs reach parent. |

---

## 5. Dry-run should show the *actual* cells that will run

### Problem
`--dry-run` currently returns `{"cells": [...], "n": N}` but the CLI prints
this as raw JSON. User can't tell if the search space is reasonable.

### Fix
- Pretty-print dry-run: show task, fidelity, each cell's coordinate summary,
  estimated time per cell, total estimated time.
- Add `--dry-run-format {json,table,summary}`.

### Files
| File | Change |
|---|---|
| `simple_survey.py:main()` | Handle `dry_run` result with pretty formatting. |

---

## 6. Budget estimation should be honest and configurable

### Problem
`FIDELITY_COSTS = {"L0": 5, "L1": 30, "L2": 300}` are hardcoded guesses.
On CPU, L0 is ~10–15s; on GPU, ~3–5s. The budget math is wrong for CPU.

### Fix
- **Calibrate on first run**: Run 1 dummy cell at startup, measure actual time,
  use that for `cost_per_cell` estimation.
- **Or**: Accept `--cost-per-cell` override.
- **Persist**: Store measured cost in the DuckDB store for reuse.

### Files
| File | Change |
|---|---|
| `simple_survey.py:_estimate_cell_count()` | Read calibrated cost from store if available; else use default. |
| `simple_survey.py:_evaluate_cells_parallel()` | After first cell completes, update estimate and log revised ETA. |

---

## 7. Device string consistency — `"auto"` vs `"cuda"` vs `"cpu"`

### Problem
- CLI accepts `--device auto|cpu|cuda`
- `RunSpec.device` stores the raw string
- `_resolve_device()` converts `"auto"` → `"cuda"` or `"cpu"`
- But `_check_torch()` doesn't know the resolved device

### Fix
- Centralize device resolution in one place: `core.utils.device.get_device()`.
- Pass resolved `torch.device` object through the call chain, not strings.
- Remove all inline `"cuda" if torch.cuda.is_available() else "cpu"`.

### Files
| File | Change |
|---|---|
| `simple_survey.py:main()` | Resolve device once: `device = get_device(args.device)` before self-test. |
| `simple_survey.py:_run_self_test()` | Pass resolved device string. |
| `diagnostics.py:run_diagnostics()` | Same. |

---

## 8. Error messages should be actionable, not stack traces

### Problem
- `torch` import crash → full stack trace + "Try: export CUDA_VISIBLE_DEVICES=''"
- Self-test failure → "Self-test failed. Use --no-self-test to skip." (doesn't say *what* failed)
- Zero cells generated → "search space may be empty or over-constrained" (no hint which constraint)

### Fix
- Catch exceptions at top level, print one-line summary + remediation.
- For self-test: print which check failed (`Test 4/6: torch... FAILED: <reason>`).
- For zero cells: print the active constraints and which axis has no primitives.

### Files
| File | Change |
|---|---|
| `simple_survey.py:main()` | Wrap `run_simple_survey` in try/except with friendly error. |
| `simple_survey.py:_run_self_test()` | Track and print which check failed. |
| `simple_survey.py:_generate_valid_cells()` | On zero cells, log the constraint matrix. |

---

## 9. Parallel worker count should respect CPU cores

### Problem
Default `--max-workers 4` may oversubscribe on small machines or undersubscribe
on large ones. No awareness of `--device cpu` vs `cuda`.

### Fix
- Default: `min(4, os.cpu_count() or 4)` for CPU; `torch.cuda.device_count()` for CUDA.
- Add `--max-workers auto` to use this logic explicitly.

### Files
| File | Change |
|---|---|
| `simple_survey.py:parser` | Change default to `"auto"`, resolve in `main()`. |

---

## 10. Store path should be auto-generated with timestamp

### Problem
Default `--store experiment.duckdb` overwrites previous run. User loses history.

### Fix
- Default: `experiment_YYYYMMDD_HHMMSS.duckdb` in `experiments/` dir.
- Keep `--store` to override.

### Files
| File | Change |
|---|---|
| `simple_survey.py:parser` | Generate default path with timestamp. |

---

## Implementation Order (suggested)

| Phase | Changes | Time |
|---|---|---|
| **P0** | #1 (on-demand CUDA), #3 (self-test opt-in), #8 (error messages) | 2h |
| **P1** | #2 (budget log leak), #4 (verbose default), #7 (device consistency) | 2h |
| **P2** | #5 (dry-run pretty), #6 (honest budget), #9 (worker auto), #10 (store timestamp) | 2h |

---

## Acceptance Criteria (all must pass)

```bash
# 1. CPU run starts instantly, no CUDA noise
CUDA_VISIBLE_DEVICES="" uv run comp run 0.1 --device cpu
# → "Evaluating N cells..." within 2s, no "CUDA initialization" warning

# 2. Self-test opt-in
uv run comp run 0.1 --device cpu --self-test
# → Runs self-test first, prints which checks pass/fail

# 3. Verbose by default on TTY
uv run comp run 0.1 --device cpu 2>&1 | head -5
# → Shows "Evaluating N cells with M workers..." + progress bar

# 4. Dry-run is readable
uv run comp run 0.1 --device cpu --dry-run
# → Table of cells with coordinate summary, not raw JSON

# 5. Budget math is honest
uv run comp run 0.5 --device cpu --dry-run
# → "budget=1800s, cost_per_cell=~12s (measured), estimated_cells=150"

# 6. Store doesn't overwrite
uv run comp run 0.1 --device cpu
uv run comp run 0.1 --device cpu
ls experiments/
# → Two timestamped .duckdb files

# 7. Old driver doesn't crash
# (Simulated by forcing torch.cuda.is_available() to raise)
# → Graceful "CUDA unavailable, using CPU" message
```

---

## Related Files (for quick navigation)

| Area | Files |
|---|---|
| Self-test & entry | `computronium/experiment/simple_survey.py` |
| Device resolution | `computronium/core/utils/device.py`, `computronium/experiment/kernel/_trainer_utils.py` |
| Diagnostics | `computronium/experiment/environment/diagnostics.py` |
| Kernel evaluation | `computronium/experiment/kernel/evaluate.py` |
| Store | `computronium/experiment/evidence/store/` |

---

## Notes

- The `simple_survey.py` script is the *primary user entry point* for experiments.
  Fixing it fixes the "nothing happens" perception.
- The CUDA warning in the user's log comes from `torch.cuda.is_available()` in
  `_check_torch()`. This is called during self-test *before* the device is known.
  Moving device resolution earlier fixes this.
- The "budget=3s" is a red herring — it's the self-test dry-run. Suppressing
  self-test logs at INFO level fixes the confusion.