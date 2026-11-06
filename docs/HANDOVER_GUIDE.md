# Computronium Handover Guide

**Version:** Phase 0 complete (2026-11-06)
**Audience:** New operator taking over the repository
**Prerequisites:** Linux, Python 3.14+, `uv` package manager, 16+ GB RAM, NVIDIA GPU optional

---

## ⚠️  CRITICAL WARNING: What This System CANNOT Do

> **This is a preliminary exploration system. It produces *ballpark rankings* from single-seed (`n=1`) runs on one task family (digits-class vision).**
>
> - **No claim is valid** from these runs. Every report prints `[at chance]` flags and `INSUFFICIENT` power warnings.
> - **Do not publish, cite, or base decisions on** preliminary results. They are crash/smoke tests only.
> - **For claim-grade evidence**: wait for Release 1.1+ (H1–H6 at `n ≥ 3`, pre-registered, calibrated gate, positive control passing).
> - **The "cannot claim" label is not decorative** — it is a technical gate enforced by the report generator.

---

## 1. Installation (Clean Machine)

```bash
# Clone and enter
git clone <repository-url>
cd computronium

# Install dependencies (includes dev extras, CUDA if available)
uv sync --dev --all-extras

# Verify environment
uv run python -c "import optuna, scipy, torchvision, pytest"
# Expected: no errors, prints nothing
```

**Expected walltime:** ~60–120 s (first run downloads wheels)

---

## 2. Smoke Test (3 minutes)

```bash
# Quick verification that the pipeline runs end-to-end
./experiment_shallow.sh 0.05 --policy random
```

**Expected output:**
- Positive control PASS (val_acc ~0.76 on xor)
- 10–11 cells evaluated in ~50 s
- Store created at `experiments/experiment_<timestamp>.duckdb`
- Exit code 0

**If this fails:** Run `./experiment_shallow.sh --doctor` for diagnostics.

---

## 3. Standard Preliminary Runs

### A. Sampler Control (Random Policy) — 30 min budget
```bash
./experiment_shallow.sh 0.5 --policy random
```
- Deterministic cell ordering (seed=42)
- Exhausts L0 search space in ~50 s (11 cells)
- Use for: regression testing, CI, deterministic baselines

### B. Adaptive (TPE Sampler) — 60 min budget
```bash
./experiment_shallow.sh 1.0 --policy tpe
```
- Optuna TPE sampler explores more of the search space
- Will consume full budget (continues proposing new cells)
- Use for: broader exploration, finding promising regions

### C. Fidelity Ladder (L0 → L1 → L2) — single invocation
```bash
./experiment_shallow.sh 1.0 --ladder
```
- Runs L0 (screen), promotes to L1 (confirm), promotes to L2 (publish)
- Only L2 cells are claim-eligible

**All commands write:** `experiments/experiment_<timestamp>.duckdb` (confirm actual path in output)

---

## 4. Inspecting Results

```bash
# Status summary (runs, records, claim-eligible count)
uv run comp status --store experiments/experiment_<timestamp>.duckdb

# Human-readable text report
uv run comp report --store experiments/experiment_<timestamp>.duckdb --format text

# HTML report (open in browser)
uv run comp report --store experiments/experiment_<timestamp>.duckdb --format html --output report.html

# Coverage analysis (which primitives touched)
uv run comp coverage report --store experiments/experiment_<timestamp>.duckdb
```

### Reading the Report

| Section | What It Tells You |
|---|---|
| **Record Statistics** | Total records, claim-eligible (0 in Phase 0), promoted, declared cells |
| **Gate Verdict Distribution** | PASS/FAIL counts; FAIL = runtime error or gate reject |
| **Coordinate Coverage** | Unique cell_keys with seed counts (all `1 seeds` in Phase 0) |
| **Contrast Design** | Data-origin allocation (all `exploration` in Phase 0) |
| **Claims** | **Always empty in Phase 0** — prints "no claim-eligible cells" |
| **Limitations** | Mandatory: `[insufficient_power]`, `[quarantined_cells]`, `[no_eligible_claim]` |
| **Primitive Affinity Heatmaps** | Mean val_acc per primitive pair (n=1, exploratory only) |
| **Top 10 Combinations** | Ranked by mean val_acc (single seed, no statistics) |

**Key markers to recognize:**
- `[at chance]` — val_acc within binomial noise of random guessing
- `[n=1, exploratory]` — single seed, no replication
- `INSUFFICIENT` — statistical power < target (63 seeds needed for d=0.5)
- `UNVERIFIED` — reproducibility not confirmed (should not appear after P0 fix)

---

## 5. Common Operations

### Resume a stopped run (static mode only)
```bash
./experiment_shallow.sh 0.5 --mode static --resume --store experiments/experiment_<ts>.duckdb
```

### Warm start from prior run (learning mode)
```bash
./experiment_shallow.sh 0.5 --policy tpe --promote-from experiments/experiment_<ts>.duckdb --promote-top 20
```

### Dry-run (preview cells without training)
```bash
./experiment_shallow.sh 0.1 --policy tpe --dry-run
```

### Skip diagnostics (faster startup)
```bash
SKIP_DOCTOR=1 ./experiment_shallow.sh 0.5 --policy random
```

---

## 6. Known Issues (Phase 0)

| Issue | Status | Workaround |
|---|---|---|
| `temporal_psi` shape mismatch on some analog/conv cells | Pre-existing, handled gracefully | Cell marked FAIL, experiment continues |
| Search space exhausted at L0 with random sampler (~11 cells) | Expected at L0 | Use `--policy tpe` or `--ladder` for longer runs |
| CUDA not used even with GPU | Torch CUDA unavailable in venv | `uv add torch --index-url https://download.pytorch.org/whl/cu124` if needed |
| 650 lint findings (Register C) | Deferred to hygiene pass | `ruff check` on changed files only per commit |

---

## 7. Troubleshooting

### `uv run` fails / ModuleNotFoundError
```bash
uv sync --dev --all-extras  # restores dev extras
```

### Experiment hangs / deadlock
- Check `htop` for worker processes
- Kill with `pkill -f learning_survey`
- Run with `--verbose` to see progress

### Store locked / "database is locked"
- Only one process can write to a DuckDB file
- Ensure no other `experiment_shallow.sh` or `comp` command is running on same store

### "Positive control failed"
- Run `./experiment_shallow.sh --doctor`
- Check GPU memory / CUDA version if using GPU

---

## 8. Next Steps for Operator

1. **Run both standard commands** (Section 3A and 3B) and verify output matches this guide
2. **Read the full TODO82.md** — it is the authoritative plan
3. **Phase 1 starts with A1–A3** (powered H1–H6 at `n ≥ 3`) and **B9/B10** (sampler arc + validation codegen)
4. **Do not add features** — evidence is the critical path (Principle 2)
5. **Keep AGENTS.md current** — it is the onboarding contract

---

## 9. Key Files Reference

| File | Purpose |
|---|---|
| `TODO82.md` | Master plan (this supersedes TODO81, README status) |
| `docs/preliminary_testing.md` | Measured timings from this machine |
| `experiment_shallow.sh` | Main entry point (time-budgeted runs) |
| `AGENTS.md` | Coding standards, toolchain, commit checklist |
| `computronium/experiment/learning_survey.py` | LearningSurvey implementation |
| `computronium/experiment/simple_survey.py` | SimpleSurvey (static mode, deprecated post-B12) |

---

## 10. Contact / Escalation

- **Code questions:** Read `AGENTS.md` first, then search codebase (`grep -rn`)
- **Architecture questions:** Check `TODO82.md` §5 (Architecture decisions)
- **Failed run:** Run `--doctor`, check logs in `logs/`, then file issue with store + command
- **Claim/evidence questions:** Read `docs/FINDINGS.md` (may be empty) and `README` neutrality section

---

*Generated 2026-11-06 as part of Phase 0 handover. Update this guide when Phase 1 changes the interface.*