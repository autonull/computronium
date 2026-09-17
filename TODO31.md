# TODO31 — Multi-Objective Autonomous Discovery & Operational Hardening

> **STATUS: DRAFT rev 2 (2026-09-17).** Supersedes TODO30 §13 (remaining work) and
> addresses the systemic accuracy-centricity in the AutoScientist loop
> (identified in session review). This revision folds in TODO30's
> improvement opportunities (§13.1) and adds a multi-objective axis to the
> discovery loop, integrating with the full 6-axis ontology, CEEC governance,
> frozen-θ ψ adaptation, and substrate-aware efficiency metrics.

---

## 0. The Core Problem

The continuous discovery loop (`comp daemon` / `comp continuous`) is
**systemically accuracy-centric**:

| Layer | Current Behavior | Why It Matters |
|-------|------------------|----------------|
| **KB schema** (`_CellRow`) | `accuracy`, `walltime`, `param_budget`, `nan_loss` | No `flops`, `memory_mb`, `energy_per_step`, `latency_ms` |
| **Pareto front** | `(accuracy ↑, bp_deficit ↓)` | `bp_deficit` is accuracy-derived; walltime is the only cost |
| **Outcome badges** | Thresholds on `accuracy` only | LEARNED/MARGINAL/CHANCE ignore cost/efficiency |
| **Breakthrough alert** | `≥2% accuracy gain` | Never fires on "same accuracy, 10× cheaper" |
| **Promotion (L1/L2)** | Front membership on accuracy | Claims backed only by accuracy, not efficiency |
| **Driver** | Stratified by `(D,C,U)` only | No objective-aware exploration |

**Result**: The AutoScientist fills a stratified grid; the Pareto front is a
*post-hoc view*, not a driver of proposals. A 40× cost spread (credit-trace
138–540s vs 12s plain) is measured but never optimized.

### 0.1 What "Multi-Objective" Means in Computronium

Computronium's 6-axis ontology (`S × G × D × P × C × U`) naturally induces
**axis-aligned objectives** beyond accuracy:

| Axis | Natural Objectives | Measurement Point |
|------|-------------------|-------------------|
| **Substrate (S)** | Energy per op, spike rate, IR-drop variance, phase noise | Settle telemetry, substrate physics |
| **Geometry (G)** | Param count, depth, fan-in/out, recurrence density | Architecture metadata |
| **StateDynamics (D)** | Settle steps, free energy, Lyapunov exponent, σ_max(J) | Settle trace, stability monitor |
| **Plasticity (P)** | ψ capacity, rewrite rate, consolidation cost | ψ-state metrics, episode boundary |
| **CreditAssignment (C)** | Credit alignment, feedback path length, trace variance | Instruments (credit_alignment, etc.) |
| **ParameterUpdate (U)** | Update norm, Fisher condition, orthogonality | Optimizer state, Riemannian metrics |

**Cross-axis composites** (the real discovery targets):
- **Accuracy / walltime** — adaptation efficiency
- **Accuracy / param_count** — parameter efficiency
- **Accuracy / energy_per_step** — thermodynamic efficiency
- **Stability / plasticity** — ρ(J_F) vs ψ_capacity (the core trade-off)
- **Ruler-relative** — bp_deficit, ruler_walltime_ratio, ruler_energy_ratio

---

## 1. Multi-Objective Architecture

### 1.1 Objective Registry (New)

```python
# computronium/autoscientist/objectives.py
from enum import StrEnum
from dataclasses import dataclass
from typing import Callable, Literal

class Objective(StrEnum):
    # Primary task objectives
    ACCURACY = "accuracy"           # maximize
    # Resource objectives
    WALLTIME_S = "walltime_s"       # minimize
    PARAM_COUNT = "param_count"     # minimize
    FLOPS = "flops"                 # minimize
    MEMORY_MB = "memory_mb"         # minimize
    ENERGY_PER_STEP = "energy_per_step"  # minimize (from settle telemetry)
    LATENCY_MS = "latency_ms"       # minimize (inference)
    # Ruler-relative objectives
    BP_DEFICIT = "bp_deficit"       # minimize (ruler-relative accuracy)
    RULER_WALLTIME_RATIO = "ruler_walltime_ratio"  # minimize
    RULER_ENERGY_RATIO = "ruler_energy_ratio"      # minimize
    # Stability objectives
    SPECTRAL_RADIUS = "spectral_radius"  # minimize (ρ(J_F))
    LYAPUNOV_EXPONENT = "lyapunov_exponent"  # minimize (max λ)
    MAX_SINGULAR_VALUE = "max_singular_value"  # minimize (σ_max(J))
    # Plasticity objectives
    PSI_CAPACITY = "psi_capacity"   # maximize (bits storable in ψ)
    CONSOLIDATION_COST = "consolidation_cost"  # minimize (θ update energy)
    REWRITE_RATE = "rewrite_rate"   # maximize (ψ updates/episode)
    # Credit objectives
    CREDIT_ALIGNMENT = "credit_alignment"  # maximize (cosine with true grad)
    FEEDBACK_PATH_LENGTH = "feedback_path_length"  # minimize
    TRACE_VARIANCE = "trace_variance"  # minimize

@dataclass(frozen=True, slots=True)
class ObjectiveSpec:
    """One objective in a multi-objective optimization."""
    name: Objective
    direction: Literal["maximize", "minimize"]
    weight: float = 1.0             # for scalarization
    normalizer: Callable[[float], float] | None = None  # min-max, log, etc.
    axis: str | None = None         # ontology axis: S|G|D|P|C|U (for grouping)

DEFAULT_OBJECTIVES: tuple[ObjectiveSpec, ...] = (
    ObjectiveSpec(Objective.ACCURACY, "maximize", axis="task"),
    ObjectiveSpec(Objective.WALLTIME_S, "minimize", axis="cost"),
)
```

### 1.2 Extended KB Row

```python
# In broad_map.py — extend _CellRow
@dataclass(frozen=True, slots=True)
class _CellRow:
    key: str
    task: str
    dynamics: str
    credit: str
    update: str
    topology: str
    geometry: dict[str, object]
    accuracy: float
    walltime: float
    param_budget: int
    nan_loss: bool
    bursts: tuple[str, ...]
    levels: tuple[str, ...]
    # NEW — multi-objective fields
    flops: float = 0.0
    memory_mb: float = 0.0
    energy_per_step: float = 0.0
    latency_ms: float = 0.0
    # Ruler-relative
    bp_deficit: float = 0.0
    ruler_walltime_ratio: float = 0.0
    ruler_energy_ratio: float = 0.0
    # Stability instruments
    spectral_radius: float = 0.0
    lyapunov_exponent: float = 0.0
    max_singular_value: float = 0.0
    # Credit instruments
    credit_alignment: float = 0.0
    feedback_path_length: float = 0.0
    trace_variance: float = 0.0
    # Plasticity
    psi_capacity: float = 0.0
    consolidation_cost: float = 0.0
    rewrite_rate: float = 0.0
    # Settle
    settle_steps_used: int = 0
    free_energy_final: float = 0.0
```

### 1.3 Configurable Pareto Front

```python
# In atlas.py — generalize pareto_top
def pareto_top(
    df: pd.DataFrame,
    k: int = 3,
    objectives: tuple[ObjectiveSpec, ...] = DEFAULT_OBJECTIVES,
) -> pd.DataFrame:
    """Non-dominated cells on configurable objectives."""
    # Build objective vectors, apply normalizers, compute dominance
    # Returns DataFrame with Pareto-front cells + objective values
```

### 1.4 Objective-Aware Driver (Phase 2)

```python
# In broad_map.py — StratifiedRandomDriver gains objective awareness
class StratifiedRandomDriver(BurstDriver):
    def __init__(
        self,
        ...,
        objectives: tuple[ObjectiveSpec, ...] = DEFAULT_OBJECTIVES,
    ):
        self.objectives = objectives

    def propose_batch(self, n: int, recent_results: list[dict] | None = None):
        # Bias toward under-explored regions of OBJECTIVE space
        # Not just (D,C,U) strata — use KB coverage in objective space
```

### 1.5 Ontology-Axis Objective Groups (Dashboard)

The dashboard presents objectives grouped by ontology axis:

| Axis | Objectives (auto-populated) |
|------|----------------------------|
| **S** (Substrate) | energy_per_step, spike_rate, ir_drop_variance, phase_noise |
| **G** (Geometry) | param_count, flops, depth, fan_in_out, recurrence_density |
| **D** (Dynamics) | settle_steps, free_energy, spectral_radius, lyapunov_exponent, max_singular_value |
| **P** (Plasticity) | psi_capacity, consolidation_cost, rewrite_rate |
| **C** (Credit) | credit_alignment, feedback_path_length, trace_variance |
| **U** (Update) | update_norm, fisher_condition, orthogonality |
| **Task** | accuracy, bp_deficit, ruler_walltime_ratio, ruler_energy_ratio |

---

## 2. Phased Implementation Plan

### Phase 1 — KB & Dashboard Multi-Objectives (Week 1–2)

| Item | Description | Files |
|------|-------------|-------|
| **1.1** | Add `Objective`, `ObjectiveSpec` registry | `autoscientist/objectives.py` (new) |
| **1.2** | Extend `_CellRow` with `flops`, `memory_mb`, `energy_per_step`, `latency_ms` | `broad_map.py` |
| **1.3** | Persist new fields from trainer metrics (`estimate_memory_usage`, `profile_flops`) | `trainer.py`, `broad_map.py:_absorb_results` |
| **1.4** | Generalize `pareto_top` to accept `objectives` spec | `visualization/atlas.py` |
| **1.5** | Dashboard: Pareto panel shows objective pair selector (dropdown) | `live_atlas.py` |
| **1.6** | Dashboard: Outcome badges become multi-objective (configurable threshold sets) | `live_atlas.py` |

**Acceptance**: Dashboard shows Pareto front on `(accuracy, walltime)` AND `(accuracy, param_count)` with selector; KB rows carry all fields.

### Phase 2 — Objective-Aware Discovery Loop (Week 3–4)

| Item | Description | Files |
|------|-------------|-------|
| **2.1** | CLI: `--objectives accuracy,walltime,param_count` → `comp daemon` | `cli/daemon.py`, `broad_map.py:budget_from_args` |
| **2.2** | Driver: `StratifiedRandomDriver` accepts `objectives`; biases proposals toward unexplored objective-space regions | `broad_map.py` |
| **2.3** | Alerts: `breakthrough_alert` fires on *any* objective improvement (configurable margin per objective) | `alerts.py` |
| **2.4** | Promotion: L1/L2 gates use configured Pareto front, not accuracy-only | `broad_map.py:run_l1_maturation`, `deep_tier` |
| **2.5** | **CEEC integration**: Multi-objective Experiment registration; beliefs track Pareto dominance across objectives | `ceec/builders.py`, `autoscientist/report.py` |
| **2.6** | **Ruler-relative objectives**: Compute `ruler_walltime_ratio`, `ruler_energy_ratio` from ruler table | `atlas.py:apply_bp_deficit`, `broad_map.py` |

**Acceptance**: Launch `comp daemon --objectives accuracy,walltime,param_count --target-cells 200`; driver biases toward efficient cells; alerts fire on walltime breakthroughs; CEEC ledger records multi-objective beliefs.

### Phase 3 — Scalarization, Frozen-θ ψ & Advanced Objectives (Week 5–6)

| Item | Description | Files |
|------|-------------|-------|
| **3.1** | Scalarized score: `Σ weight_i × normalized(obj_i)` for ranking when single-number needed | `hyperopt/metrics.py` |
| **3.2** | Energy objective: integrate settle-phase `energy_per_step` from telemetry into KB | `daemon.py` (telemetry bridge), `broad_map.py` |
| **3.3** | Latency/throughput: add inference benchmark to KB on promotion (L1+) | `autoscientist/benchmark.py` (new) |
| **3.4** | Ruler-relative objectives: `bp_deficit`, `ruler_walltime_ratio` | `atlas.py:apply_bp_deficit` |
| **3.5** | **Frozen-θ ψ adaptation with multi-objective criteria**: `Lab.adapt` uses Pareto front over (accuracy, stability, cost) for ψ-only optimization | `packages/computronium-lab`, `psi_peft` |
| **3.6** | **Substrate-aware objectives**: Memristive → energy_per_op, IR_drop; Neuromorphic → spike_rate, event_density; Photonic → phase_noise, power | `ontology/substrate/spec.py`, `broad_map.py` |
| **3.7** | **Stability/Plasticity trade-off objective**: `stability_plasticity_ratio = spectral_radius / psi_capacity` — the core trade-off | `stability/`, `broad_map.py` |
| **3.7** | **NTM/NCA specific objectives**: NTM → tape_utilization, head_entropy; NCA → pattern_diversity, fabric_stability | `ontology/geometry/ntm.py`, `nca.py` |
| **3.8** | **Credit efficiency objectives**: alignment_per_flop, feedback_path_length, trace_variance_per_param | `ontology/credit.py`, `broad_map.py` |

**Acceptance**: Full multi-objective campaign runs; energy/latency objectives populated; frozen-θ ψ adaptation uses Pareto criteria; substrate-specific objectives auto-populated; stability/plasticity trade-off visible in dashboard.

---

## 3. Folded-In TODO30 Remaining Work

### 3.1 Shakedown & Hardening (Week 1, parallel with Phase 1)

| # | Item | Status | Notes |
|---|------|--------|-------|
| 30.4 | **500-cell shakedown** | **DO** | Now with `--objectives accuracy,walltime`; validates Phase 1 |
| 30.8 | **Adaptive scheduler** | **DEFER** | Becomes Phase 2.5 — uses multi-objective data |
| 13.1.1 | Per-iteration cell progress | **DONE** | `_on_cell_complete` callback added |
| 13.1.2 | Event payload enrichment (`burst_finished` carries summary) | **DO** | `events.publish({"kind": "burst_finished", **summary})` |
| 13.1.3 | Settle-phase energy traces to telemetry | **DONE** | `on_step` callback in `StateDynamics.settle` |
| 13.1.4 | Resource gauges in heartbeat | **DONE** | `psutil` CPU/RAM/VRAM in heartbeat |
| 13.1.5 | §3.2 event-stream UI (toast panel) | **DONE** | `_event_panel` + `_make_events_consumer` |
| 13.1.6 | Outcome badges (LEARNED/MARGINAL/DIVERGED/DEFECT/VOID) | **DONE** | `OutcomeBadge` enum + `_classify_event` |
| 13.1.7 | Alert hardening from shakedown data | **DO** | After 500-cell run; fold NaN into cascade |
| 13.1.8 | Front-history honesty (label objective pair) | **DO** | Dashboard shows "(accuracy ↑, walltime ↓)" |
| 13.1.9 | Graceful-stop watchdog (stale lockfile) | **DO** | PID liveness check before refusing start |
| 13.1.10 | Campaign-config provenance in report | **DO** | Heartbeat carries task, epochs, limit-batches, seed |
| 13.1.11 | Dashboard readiness (stale heartbeat = CONNECTION LOST) | **DONE** | `liveness()` already implements |

### 3.2 Defect ID Hardening (TODO29 §12.3, ride-along)

```python
# In defects.py — if collision rate > 1% in shakedown:
def defect_id(record) -> str:
    base = hash(record.error_class + record.message[:200])
    frame = traceback.extract_tb(record.exc_info)[-1] if record.exc_info else None
    return f"{base:08x}{frame.filename[:2]}{frame.lineno:04x}" if frame else f"{base:08x}"
```

---

## 4. CEEC Governance for Multi-Objective Claims

**New Requirement**: Every comparative claim must be backed by CEEC-governed
evidence across the *declared objectives*, not just accuracy.

| Maturity | CEEC Requirements |
|----------|-------------------|
| **L0 (Mapping)** | Single-burst, 1 seed. Experiment registered with objective spec. |
| **L1 (Promoted)** | 3 bursts, 1 seed. Belief: "Pareto-optimal on objectives O at maturity L1". |
| **L2 (Claim-grade)** | 10 bursts, 3 seeds. Belief: "Pareto-optimal on O across seeds/bursts". Gate: `belief.confidence ≥ 0.95`. |

### 4.1 Multi-Objective CEEC Builders

```python
# ceec/builders.py additions
def build_multi_objective_experiment(
    coordinate: str,
    objectives: tuple[ObjectiveSpec, ...],
    pareto_front: pd.DataFrame,
    seeds: int,
) -> Experiment:
    """Register experiment with Pareto-front evidence across objectives."""
    payload = {
        "objectives": [o.name for o in objectives],
        "pareto_cells": pareto_front["key"].tolist(),
        "seed_count": seeds,
        "dominance_matrix": compute_dominance(pareto_front, objectives),
    }
    return Experiment(...)

def build_pareto_belief(
    experiment: Experiment,
    objective: Objective,
    confidence: float,
) -> Belief:
    """Belief that a cell is Pareto-optimal on a specific objective."""
    ...
```

### 4.2 Dashboard: CEEC Ledger Panel

- Shows registered experiments, beliefs, gates for current campaign
- Filters by objective: "Show only L2 beliefs on walltime"
- Alert when belief confidence crosses threshold (integrated with toast system)

---

## 5. Dashboard Enhancements (Engagement & Assurance)

| Item | Description | Priority |
|------|-------------|----------|
| **5.1** | **Objective pair selector** — dropdown in Pareto panel: `(acc, walltime)`, `(acc, params)`, `(acc, flops)`, `(walltime, params)`, custom | P1 |
| **5.2** | **Cost breakdown per objective** — bar charts for each objective (not just walltime) | P1 |
| **5.3** | **Efficiency badges** — "PARETO OPTIMAL", "PARETO NEAR", "DOMINATED" on cells | P1 |
| **5.4** | **Axis-grouped objective panel** — tabs for S/G/D/P/C/U/Task objectives with per-axis Pareto | P1 |
| **5.5** | **Trend sparklines** — per-objective trend over last N bursts (mini charts in event stream) | P2 |
| **5.6** | **Campaign config panel** — shows full CLI config from heartbeat (no CLI needed) | P2 |
| **5.7** | **Stale-lock recovery button** — "Force unlock" in lifecycle bar when PID dead | P2 |
| **5.8** | **Settle trace panel** — energy descent curve from `on_step` telemetry (EnergyMinimization, PredictiveSettling) | P2 |
| **5.9** | **CEEC Ledger panel** — experiments, beliefs, gates filtered by objective | P2 |
| **5.10** | **Stability/Plasticity trade-off panel** — ρ(J_F) vs ψ_capacity scatter with Pareto front | P3 |
| **5.11** | **Substrate-specific panel** — Memristive: energy/IR-drop; Neuromorphic: spikes/event density; Photonic: phase/power | P3 |
| **5.12** | **Ruler-relative front** — toggle between absolute and ruler-relative objectives | P3 |

---

## 6. Testing Strategy

### 6.1 Unit Tests (New)

| Test | Purpose |
|------|---------|
| `test_objectives_registry.py` | `ObjectiveSpec` round-trip, normalizers, scalarization |
| `test_pareto_multi_obj.py` | `pareto_top` with 2, 3, 4 objectives; dominance correctness |
| `test_cell_row_extended.py` | KB write/read with new fields; backward compat (missing=0) |
| `test_driver_objective_bias.py` | Driver proposes more efficient cells when `objectives` includes cost |
| `test_ceec_multi_objective.py` | Experiment/belief builders with multi-objective payloads |
| `test_substrate_objectives.py` | Substrate-specific objective auto-population |
| `test_stability_plasticity.py` | ρ(J_F) vs ψ_capacity trade-off computation |

### 6.2 Integration Tests (Extended)

| Test | Extension |
|------|-----------|
| `test_dashboard_smoke.py::test_landscape_panels_headless` | Assert Pareto panel renders with selector; outcome badges present |
| `test_daemon_state.py::test_full_lifecycle` | Add `--objectives` flag; verify heartbeat carries config |
| `test_ceec_integration.py` | Multi-objective experiment registration → belief → gate |

### 6.3 Property Tests

| Test | Purpose |
|------|---------|
| `test_objective_dominance.py` | Hypothesis: random points → Pareto front size ≤ N; transitivity |
| `test_scalarization_monotonic.py` | Scalarized score respects Pareto dominance |
| `test_driver_coverage_objective_space.py` | Driver covers objective space, not just (D,C,U) strata |

### 6.4 Shakedown Acceptance (500-cell run)

```bash
uv run comp daemon \
  --target-cells 500 \
  --limit-batches 30 \
  --loop --sleep 15 \
  --objectives accuracy,walltime,param_count \
  --root artifacts/todo31_shakedown
```

**Success criteria**:
- [ ] Dashboard shows live Pareto on `(accuracy, walltime)` with selector
- [ ] Event stream shows breakthrough toasts on walltime improvement
- [ ] KB rows have `flops`, `memory_mb`, `energy_per_step` populated
- [ ] No terminal needed for full run
- [ ] Defect ID collision rate < 1%
- [ ] Report generated on completion with multi-objective front
- [ ] CEEC ledger shows multi-objective experiments/beliefs
- [ ] Axis-grouped objective panel renders S/G/D/P/C/U tabs

---

## 7. Migration & Backwards Compatibility

| Existing | Becomes |
|----------|---------|
| `comp continuous` | `comp daemon` (unchanged; default `--objectives accuracy,walltime`) |
| `comp dashboard` | Reads `objectives` from heartbeat; defaults to accuracy+walltime |
| `_CellRow` without new fields | `flops=0, memory_mb=0, ...` — backward compatible |
| `pareto_top(df, k)` | `pareto_top(df, k, DEFAULT_OBJECTIVES)` — same behavior |
| Breakthrough alert on accuracy | Configurable per-objective margins |

**No breaking changes** — all additions are additive with sensible defaults.

---

## 8. Success Criteria (Extended from TODO30 §10)

The system is complete when a scientist can:

1. **Launch** a campaign with `--objectives accuracy,walltime,param_count` and walk away.
2. **Glance** at the dashboard and see: is it alive, what is it doing, how far along, **at what cost on each objective**.
3. **Sit down** and understand: what has been discovered **on each objective**, what has failed, what remains unexplored, whether the search is healthy.
4. **Receive an alert** on their phone when **any objective** improves significantly.
5. **Generate a report** with **multi-objective Pareto frontiers**, ready for review.
6. **Never need to open a terminal** during the campaign's lifetime.
7. **Switch objective pairs** in the dashboard and see the front recompute instantly.

---

## 9. Immediate Next Actions (in order)

1. **Create `autoscientist/objectives.py`** — `Objective`, `ObjectiveSpec`, `DEFAULT_OBJECTIVES`
2. **Extend `_CellRow`** — add `flops`, `memory_mb`, `energy_per_step`, `latency_ms`
3. **Generalize `pareto_top`** — accept `objectives` tuple; update `pareto_strip_rows`, `front_history_rows`
4. **Wire CLI** — `--objectives` flag in `comp daemon`; pass through to driver + dashboard
5. **Dashboard Pareto selector** — dropdown in Pareto panel; recompute on change
6. **Run 500-cell shakedown** with `--objectives accuracy,walltime,param_count`
7. **Alert generalization** — `breakthrough_alert` uses `objectives` config
8. **Driver objective bias** — `StratifiedRandomDriver` explores objective space
9. **Promotion on configured front** — L1/L2 use multi-objective Pareto
10. **Energy/latency objectives** — populate from telemetry + inference benchmark

---

## 10. Out of Scope (Explicit)

| Item | Reason |
|------|--------|
| Human-in-the-loop steering | Violates autonomous philosophy (TODO30 §0) |
| Interactive lasso/fork on dashboard | Same |
| Multi-user collaboration | Single-operator telemetry only |
| Campaign config editing in dashboard | CLI-immutable by design |
| HPO integration | Separate `comp hpo` surface; Pareto frontier shared but distinct |

---

## 11. Dependencies & Risks

| Risk | Mitigation |
|------|------------|
| KB schema migration | Add fields with defaults; `_load_measured_cells` handles missing keys |
| Pareto computation cost | `pareto_top` is O(N²) but N ≤ 5000; cache per burst |
| Driver bias complexity | Start simple: reject proposals in dominated objective regions |
| Energy telemetry noise | Average over settle steps; only populate if `track_free_energy_per_iter` |
| GPU VRAM via pynvml | Optional; gracefully return `None` if unavailable |
| CEEC ledger growth | Prune L0 experiments after L1 promotion; archive old campaigns |
| Ruler table staleness | Recompute ruler on promotion; version ruler_table.json |
| Substrate physics calibration | Per-substrate normalizers from characterization runs |
| Frozen-θ ψ multi-objective | Start with accuracy+stability; add cost objectives incrementally |

---

## 12. Hyperopt Integration (Existing Infrastructure)

The multi-objective AutoScientist **shares** Pareto infrastructure with `comp hpo`:

| Layer | AutoScientist | HPO (`optuna_bridge.py`) |
|-------|---------------|--------------------------|
| **Objectives** | Campaign-level (configured at launch) | Study-level (configured per study) |
| **Pareto** | `atlas.pareto_top` on KB rows | `optuna.get_pareto_trials` |
| **Scalarization** | Weights from `ObjectiveSpec.weight` | `optuna.samplers.TPESampler` scalarization |
| **Frontier persistence** | KB + CEEC ledger | Optuna study + `hyperopt/frontier.py` |
| **Comparison** | `hyperopt/comparator.py` (bio vs backprop) | Same — bio rules compared on their frontiers |

**Integration point**: `comp daemon` campaign results can seed HPO studies:
```python
# Export campaign Pareto frontier as HPO study seeds
def campaign_to_hpo_seeds(campaign_root: Path, objectives: tuple[ObjectiveSpec, ...]) -> list[FrozenTrial]:
    front = pareto_top(load_kb(campaign_root), objectives=objectives)
    return [trial_from_cell_row(row) for _, row in front.iterrows()]
```

---

## 13. Appendix: Objective Normalizers (Reference)

```python
# Default normalizers for common objectives
def normalize_accuracy(x: float) -> float:
    return x  # already [0, 1]

def normalize_walltime(x: float) -> float:
    return 1.0 / (1.0 + x)  # minimize → maximize reciprocal

def normalize_param_count(x: float) -> float:
    return 1.0 / (1.0 + x / 1e6)  # minimize; scale to millions

def normalize_flops(x: float) -> float:
    return 1.0 / (1.0 + x / 1e9)  # minimize; scale to GFLOPs

def normalize_memory_mb(x: float) -> float:
    return 1.0 / (1.0 + x / 1024)  # minimize; scale to GB

def normalize_energy_per_step(x: float) -> float:
    return 1.0 / (1.0 + x / 1e-3)  # minimize; scale to mJ

def normalize_latency_ms(x: float) -> float:
    return 1.0 / (1.0 + x)  # minimize; scale to ms

def normalize_spectral_radius(x: float) -> float:
    return 1.0 / (1.0 + max(0.0, x - 1.0))  # penalize >1; maximize contraction

def normalize_lyapunov_exponent(x: float) -> float:
    return 1.0 / (1.0 + max(0.0, x))  # minimize; negative is stable

def normalize_max_singular_value(x: float) -> float:
    return 1.0 / (1.0 + max(0.0, x - 1.0))  # penalize transient amplification

def normalize_psi_capacity(x: float) -> float:
    return x / (1.0 + x)  # maximize; saturating

def normalize_consolidation_cost(x: float) -> float:
    return 1.0 / (1.0 + x / 1e3)  # minimize; scale to kJ

def normalize_credit_alignment(x: float) -> float:
    return (x + 1.0) / 2.0  # cosine [-1,1] → [0,1]

def normalize_feedback_path_length(x: float) -> float:
    return 1.0 / (1.0 + x)  # minimize; layers

def normalize_trace_variance(x: float) -> float:
    return 1.0 / (1.0 + x)  # minimize

def normalize_bp_deficit(x: float) -> float:
    return 1.0 - x  # already [0,1]; minimize deficit

def normalize_ruler_ratio(x: float) -> float:
    return 1.0 / (1.0 + max(0.0, x - 1.0))  # penalize >1x ruler

DEFAULT_NORMALIZERS: dict[Objective, Callable[[float], float]] = {
    Objective.ACCURACY: normalize_accuracy,
    Objective.WALLTIME_S: normalize_walltime,
    Objective.PARAM_COUNT: normalize_param_count,
    Objective.FLOPS: normalize_flops,
    Objective.MEMORY_MB: normalize_memory_mb,
    Objective.ENERGY_PER_STEP: normalize_energy_per_step,
    Objective.LATENCY_MS: normalize_latency_ms,
    Objective.SPECTRAL_RADIUS: normalize_spectral_radius,
    Objective.LYAPUNOV_EXPONENT: normalize_lyapunov_exponent,
    Objective.MAX_SINGULAR_VALUE: normalize_max_singular_value,
    Objective.PSI_CAPACITY: normalize_psi_capacity,
    Objective.CONSOLIDATION_COST: normalize_consolidation_cost,
    Objective.CREDIT_ALIGNMENT: normalize_credit_alignment,
    Objective.FEEDBACK_PATH_LENGTH: normalize_feedback_path_length,
    Objective.TRACE_VARIANCE: normalize_trace_variance,
    Objective.BP_DEFICIT: normalize_bp_deficit,
    Objective.RULER_WALLTIME_RATIO: normalize_ruler_ratio,
    Objective.RULER_ENERGY_RATIO: normalize_ruler_ratio,
}
```

---

*End of TODO31.md*