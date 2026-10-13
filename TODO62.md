# TODO62: Continuous Experiment Loop & System Self-Improvement

**Goal:** A continuous, self-driving experiment process: **propose → run → analyze → fix → repeat**.
Each iteration either finds a better configuration or exposes a defect; both feed back
into the system so the next iteration is stronger. No human in the loop to start a run.

**Seed finding (TODO61):** full 2h maturation reached **95.8%** on digits with
`memristive/tile_mesh/instantaneous/target_inversion/ortho_adam/conflict_adaptive`.

---

## 0. The Loop (what "continuous" means here)

```
        ┌──────────────────────────────────────────────┐
        │  propose(spec)  ← prior knowledge + last top │
        │      ↓                                        │
        │  run(bounded)   ← resumable, watchdog-safe    │
        │      ↓                                        │
        │  analyze(store) ← diff vs best, classify      │
        │      ↓                                        │
        │  update(priors, ledger)                       │
        │      ↓                                        │
        │  defect? ──yes──> fix → verify → resume       │
        └──────────────┬───────────────────────────────┘
                       │ no
                       └──────────────> next cycle
```

Two outputs per cycle, both durable:
1. **Evidence** — cells measured, Pareto front updated (`store` + `ledger.jsonl`).
2. **System delta** — a bug fixed, a capability added, a prior sharpened.

The controller (`scripts/continuous_experiment.py`) already implements the outer
shell (propose → run → analyze → state/ledger, resumable). This plan is about
**making it trustworthy and self-improving**, then running it unattended.

---

## 1. Current State

### 1.1 Confirmed results (TODO61)

| Config | L0 | L1 (3 ep) | L1 (10 ep, 5 seeds) |
|--------|-----|-----------|---------------------|
| memristive/tile_mesh/instantaneous/target_inversion/ortho_adam/conflict_adaptive | 30% | 89% | **95.8%** |
| optical/tile_mesh/instantaneous/target_inversion/ortho_adam/conflict_adaptive | — | — | **95.3%** |
| memristive/tile_mesh/energy_minimization/target_inversion/ortho_adam/routing | 64% | 89% | **95.3%** |
| digital/tile/energy_minimization/temporal_trace/lion/rule_state | 23% | 15% | false positive |
| sparse/tile/energy_minimization/pc_alm/local_adam/null | 23% | 15% | false positive |
| complex/tile/energy_minimization/target_inversion/muon/rule_state | 23% | 13% | false positive |

**Signal:** `tile_mesh` geometry + `target_inversion` (local credit) + `ortho_adam`
+ `conflict_adaptive`/`routing` plasticity. Learning converges by epoch 3–4.
`ρ ≈ 1.0–1.1` throughout.

### 1.2 The controller (built, smoke-tested)

`scripts/continuous_experiment.py` — outer loop over `run_experiment.py`.
- **Ladder:** `explore` (L0, broad, cheap) ↔ `exploit` (L1, axes restricted to
  cumulative top-K primitives).
- **Durable state:** `experiments/continuous/{state.json, ledger.jsonl, continuous.duckdb}`.
- **Resumable:** re-running continues from `state["cycle"]`.
- **Seeded** with `KNOWN_GOOD` (the 3 confirmed configs above) so exploit starts
  in a productive region instead of narrowing onto L0 noise.

### 1.3 Known defects (found while building the loop)

| # | Defect | Evidence | Impact |
|---|--------|----------|--------|
| **D1** | `gradient` (backprop) credit × `tile_mesh` geometry fails the forward pass | `RuntimeError: mat1 and mat2 shapes cannot be multiplied (16x8 and 64x108)`, independent of dynamics | **Blocks every backprop baseline** — cannot compare local credit vs global on the winning architecture |
| **D2** | L0 explore signal is near-chance (12.8%) | 1 epoch × batch_limit=2000 on random configs = noise | Explore cannot discriminate; exploit only works because it is *seeded* |
| **D3** | `_composable` uses `except ValueError, TypeError, KeyError:` | `search_space.py:781` (Python-2 syntax; parses under 3.14 but is a latent trap) | Fragile; must be `except (ValueError, TypeError, KeyError):` |
| **D4** | `gradient` × `tile_mesh` passes `SystemConfig.validate()` but fails at train | `_validate_gradient_credit_instantaneous_output_proj` only rejects `instantaneous` | Validation gap: energy_minimization + gradient + tile_mesh also broken, not rejected |

---

## 2. Make the Loop Trustworthy (P0 — before unattended runs)

### 2.1 Fix D1/D4 — the `gradient × tile_mesh` forward break
- **Root:** tile_mesh's forward/settle path mis-shapes the input projection when
  composed with backprop credit (`mat1 (16x8) @ mat2 (64x108)`).
- **Fix path:** trace the tile_mesh forward in `compose.py` / `geometry/tile_mesh`;
  the first-layer projection expects `input_dim` (64) but receives a tile-width (8).
- **Validation:** extend `_validate_gradient_credit_instantaneous_output_proj` to
  reject `gradient × tile_mesh` under **all** dynamics until the path is fixed,
  so the search space never proposes an untrainable cell (D4).
- **Lock:** a property test that `gradient × tile_mesh` either composes **and**
  dry-run-trains, or is rejected by validation — never passes one and fails the other.

### 2.2 Fix D3 — the exception clause
- One-line: `except (ValueError, TypeError, KeyError):`.
- Lock: the dry-run gate's exception handling is exercised by a case that raises.

### 2.3 Fix D2 — make explore discriminate
- Explore currently uses `batch_limit=2000`, 1 epoch → chance. Options:
  - **a.** Explore at L1 (3 epochs, full batch) on a *small* cell budget — more
    signal per cell, fewer cells.
  - **b.** Rank explore cells by a *stability-aware* score (ρ near 1, finite
    metrics) rather than raw accuracy, so noise doesn't dominate.
  - **c.** Keep L0 for breadth but require **multi-seed** agreement before a cell
    is promoted to the exploit set.
- **Recommendation:** (b) + (c): cheap L0 scan, promote only cells whose ρ is in
  band and whose score is stable across the sweep steps.

### 2.4 Resume hardening
- `CellStreamState` already supports checkpoint/resume; wire it into the
  controller so a killed cycle resumes mid-page rather than restarting the run.
- Verify: kill mid-cycle, re-run, assert no cell is measured twice.

---

## 3. Make the Loop Self-Improving (P1)

### 3.1 Analysis that classifies, not just ranks
Each cycle should emit, per promoted cell, one of:
- **win** — improved on the prior best at the same fidelity
- **validated** — L0 winner held at L1
- **false-positive** — L0 winner collapsed at L1
- **regressed** — previously good cell got worse (shouldn't happen; flag it)

The ledger already records `best_acc` + `improvement`; add the classification so
the prior update is mechanical.

### 3.2 Prior update rule
- Boost axes/primitives that appear in wins.
- Prune primitives that only ever produce false-positives.
- Widen an axis when a cycle's best is flat (no improvement for K cycles).

### 3.3 Fix-feed loop
- When `analyze` detects a **defect signature** (exception in the cycle log,
  e.g. the D1 shape error), the controller:
  1. records it in the ledger as a defect, not a cell failure;
  2. narrows the space away from it (compatibility matrix, §4);
  3. surfaces it for a code fix.
- This is the "can be fixed" half of the loop: defects become first-class outputs.

### 3.4 Compatibility matrix in `RunSpec`
- Encode known-broken combinations (D1/D4) so `ModelBasedPolicy` never samples them.
- Single source of truth; the search space and the validator read the same table.

---

## 4. Capability Improvements (P2 — as cycles reveal need)

| Item | Trigger | Fix |
|------|---------|-----|
| Early stopping from convergence curve | Optical converges by epoch 2–3 | Stop when `val_acc` plateau < 0.1% for 3 epochs; add `early_stopped_at_epoch` |
| Basin stability | ρ near 1 but generalization varies | Multi-start perturbation; add `basin_stability` |
| Adaptive step_size (predictive settling) | Fixed 0.5 clamp is heuristic | `step_size = min(0.5, 1/L_local)` |
| Pareto CSV/JSON export | Reports exist but no downstream feed | Export top-N with coordinate + mean/std + curve summary |
| Claim-grade automation | After a config survives N cycles | `--claim`: 10 seeds × 20 epochs + CEEC governance |

---

## 5. Execution Plan

### Phase 0 — Trust (P0)
1. Fix D3 (exception clause). 2. Fix D1/D4 (gradient × tile_mesh + validation gap).
3. Fix D2 (explore discrimination). 4. Resume hardening.
5. Property locks for each (D1/D4 lock is the key one).

### Phase 1 — Run unattended (P1)
```bash
# On bare metal (no 6-min watchdog):
nohup uv run python scripts/continuous_experiment.py --hours 8 --device cuda \
  > logs/continuous_main.log 2>&1 &
# Poll every ≤2 min; ledger is the live artifact:
tail -f experiments/continuous/ledger.jsonl
```
- 8h budget → ~80 cycles at ~5 min each (explore+exploit pairs).
- Controller resumes if killed; state is durable.

### Phase 2 — Analyze & fix (P1)
- After each poll: read `ledger.jsonl`; classify wins/false-positives; if a defect
  signature appears, fix it and resume.
- Expected defects: D1 shape errors (now caught by §3.4), memory blowups on large
  geometries, slow cells.

### Phase 3 — Promote & claim (P2)
- Any config surviving 3+ cycles at ≥95% → claim-grade run (10 seeds × 20 epochs).

---

## 6. Success Metrics

| Metric | Target |
|--------|--------|
| Controller runs unattended | ≥ 8h, ≥ 50 cycles, survives kill/resume |
| Best accuracy found | ≥ 96% (beat 95.8%) |
| Backprop baseline available | D1 fixed; local vs global compared on tile_mesh |
| False-positive rate | < 20% of L0-promoted cells collapse at L1 |
| Defect capture | Every cycle exception recorded + classified, not silently dropped |
| Reproducibility | Same seed + device → bitwise-equal best (L5 lock) |

---

## 7. Open Questions

- **Is 95.8% the ceiling for digits?** The task is small; saturation may be near.
  Scale to a harder task (CIFAR-10 subset, or a longer-sequence task) once the
  loop is trusted.
- **Does the win transfer across substrates?** optical and memristive both hit
  ~95%; is the mechanism substrate-independent (tile_mesh + local credit) or does
  the substrate matter?
- **What does `target_inversion` do that `thermodynamic_contrast` doesn't?** Both
  are local credits; the winner uses target_inversion. Ablate the credit on the
  winning cell at high fidelity.
- **Can the loop find the win from scratch?** Currently seeded. Test whether
  explore + stability-ranking (§2.3) rediscovers the tile_mesh region without the
  `KNOWN_GOOD` seed.

---

## 8. Files

| File | Role |
|------|------|
| `scripts/continuous_experiment.py` | Outer controller (propose/run/analyze/state) |
| `experiments/continuous/state.json` | Resumable state (cycle, best, top-K) |
| `experiments/continuous/ledger.jsonl` | Durable per-cycle record |
| `experiments/continuous/continuous.duckdb` | Cumulative evidence store |
| `logs/continuous_cycle_NNN.log` | Per-cycle raw output |
| `computronium/experiment/kernel/search_space.py` | D3 fix; `_composable` |
| `computronium/ontology/system.py` | D4 fix; `_validate_gradient_credit_*` |
| `computronium/experiment/kernel/compose.py` | D1 fix; tile_mesh forward |

---

**Status:** Controller built + smoke-tested (2 cycles: explore→exploit, state +
ledger + resume). Seeded with TODO61 priors. **Next: Phase 0 (fix D1–D4), then
launch unattended on bare metal.**
