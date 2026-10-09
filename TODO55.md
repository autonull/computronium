# TODO55 — Comprehensive Experiment & Reporting Roadmap

**Goal**: Evolve from "working showcase" to **publication-grade experimental platform** that demonstrates ALL system capabilities through rigorous, diverse, well-communicated experiments.

**Philosophy**: Reports must be self-explanatory, organized, and meaningful — not just data dumps. Every figure/table answers a specific question. Every experiment tests a specific hypothesis.

---

## 🎯 High-Level Objectives

| Objective | Success Metric |
|-----------|----------------|
| **Capability Coverage** | Every ontology axis (substrate, geometry, dynamics, plasticity, credit, update) exercised meaningfully in at least one flagship experiment |
| **Hypothesis-Driven** | Each campaign targets specific scientific questions with pre-registered hypotheses |
| **Statistical Rigor** | Multiple seeds, effect sizes, confidence intervals, power analysis, multiple comparison correction |
| **Reproducibility** | Full export/import/repro round-trip; environment capture; deterministic seeds |
| **Narrative Reports** | HTML/PDF reports tell a coherent story: question → method → result → interpretation |
| **Scalability** | Campaigns from 5-min smoke tests → 24h production runs on multi-GPU |

---

## 📋 Phase Structure

```
Phase A (0.5 days):  Report Architecture & Templates
Phase B (1 day):     Experiment Design Framework
Phase C (2 days):    Capability-Specific Campaigns
Phase D (1 day):     Advanced Analyses & Visualizations
Phase E (1 day):     Scaling & Production Hardening
Phase F (Ongoing):   Continuous Validation & Documentation
```

---

## Phase A: Report Architecture & Templates (0.5 days)

### A1: Report Template System
- **Structured sections**: Abstract, Hypotheses, Methods, Results (per-hypothesis), Discussion, Limitations, Reproducibility
- **Auto-populated metadata**: Campaign config, environment, git commit, hardware, time budget
- **Template inheritance**: Base template + domain-specific overrides (vision, RL, tabular, graph, language)

### A2: Figure/Table Standards
- **Mandatory elements**: Title, axis labels with units, sample sizes, error bars (CI95), statistical annotations
- **Color schemes**: Consistent across reports (credit=hue, dynamics=marker, substrate=facet)
- **Accessibility**: Colorblind-safe palettes, alt-text for screen readers

### A3: Dynamic Report Generation
- **Jinja2 templates** with typed context (Pydantic models for report data)
- **Conditional sections**: Only render stability analysis if data exists
- **Cross-reference system**: Auto-numbered figures/tables with hyperlinks

### A4: Multi-Format Output
- HTML (interactive: hover tooltips, collapsible sections, sortable tables)
- PDF (LaTeX via WeasyPrint/Pandoc for paper submission)
- JSON (machine-readable for downstream analysis)

---

## Phase B: Experiment Design Framework (1 day)

### B1: Hypothesis Registry
```python
# templates/hypotheses.json structure
{
  "hypotheses": [
    {
      "id": "H1_credit_efficiency",
      "question": "Does equilibrium_prop achieve comparable accuracy to gradient with lower energy_per_step?",
      "prediction": "eqprop energy_per_step < gradient energy_per_step at matched val_acc",
      "test": "paired_t_test(val_acc, energy_per_step) grouped by substrate",
      "min_effect_size": 0.5,
      "required_power": 0.8,
      "tags": ["credit", "energy", "efficiency"]
    }
  ]
}
```

### B2: Campaign Builder DSL
```yaml
# campaigns/energy_efficiency.yaml
meta:
  name: "energy_efficiency_comparison"
  hypotheses: ["H1_credit_efficiency", "H2_dynamics_stability"]
  description: "Compare energy efficiency across credit assignments"

design:
  factors:
    credit: [gradient, equilibrium_prop, feedback_alignment, pepita]
    substrate: [digital, analog, memristive]
    dynamics: [energy_minimization, predictive_settling]
  fixed:
    geometry: feedforward
    update: adam
    plasticity: null
  blocks:
    - task: digits
      epochs: 50
      seeds: 10

analysis:
  primary: "val_acc vs energy_per_step Pareto"
  secondary: ["stability_margin", "settle_steps"]
  stats: ["cohens_d", "cliffs_delta", "bayes_factor"]
```

### B3: Power Analysis Integration
- **Pre-campaign**: Compute required `n_seeds` per cell for target power
- **Adaptive**: Stop early if effect detected; continue if underpowered
- **Post-hoc**: Report achieved power, confidence intervals

### B4: Factorial Design Support
- Full factorial, fractional factorial, response surface
- Automatic aliasing detection for fractional designs
- Blocking by task/hardware for nuisance factor control

---

## Phase C: Capability-Specific Campaigns (2 days)

### C1: Credit Assignment Deep Dive
| Campaign | Question | Key Comparisons |
|----------|----------|-----------------|
| `credit_local_vs_global` | Can local credits (FA, Hebbian, PEPITA) match backprop? | val_acc, energy, walltime, stability |
| `credit_beta_sweep` | How does β affect EQProp/PC convergence? | β ∈ [0.1, 0.3, 0.5, 0.7, 0.9] |
| `credit_noise_robustness` | Which credits degrade gracefully with substrate noise? | Add noise_level ∈ [0, 0.01, 0.05, 0.1] |

### C2: Dynamics Family Characterization
| Campaign | Question | Key Comparisons |
|----------|----------|-----------------|
| `dynamics_settling_speed` | Iterations to converge vs accuracy? | Settling steps, spectral radius, Lyapunov |
| `dynamics_stability_landscape` | Basin stability across dynamics families? | Basin radius profiles, nonnormality |
| `dynamics_energy_trajectories` | Free energy evolution per dynamics? | Per-iteration energy, drift metrics |

### C3: Substrate Physics Ablation
| Campaign | Question | Key Comparisons |
|----------|----------|-----------------|
| `substrate_noise_sensitivity` | Accuracy vs noise for analog/memristive/optical? | Noise sweep, error bars |
| `substrate_quantization` | Bit-width vs accuracy/energy? | 4/8/16/32-bit, STE vs quantization-aware |
| `substrate_nonlinearity` | Activation function impact per substrate? | ReLU, tanh, sigmoid, custom |

### C4: Plasticity & Continual Learning
| Campaign | Question | Key Comparisons |
|----------|----------|-----------------|
| `plasticity_catastrophic_forgetting` | Which plasticities mitigate forgetting? | Split MNIST, Permuted MNIST |
| `plasticity_forward_transfer` | Does fast_weights/routing improve new task learning? | Few-shot accuracy |
| `plasticity_stability_plasticity_dilemma` | EWC vs synaptic intelligence vs null? | Stability-plasticity tradeoff curves |

### C5: Geometry Topology Effects
| Campaign | Question | Key Comparisons |
|----------|----------|-----------------|
| `geometry_recurrent_vs_feedforward` | When does recurrence help? | Sequence tasks, memory capacity |
| `geometry_depth_width` | Depth vs width tradeoff per dynamics? | Param-matched comparisons |
| `geometry_attention` | Causal transformer vs recurrent for sequences? | Long-range dependency tasks |

### C6: Update Rule & Optimization
| Campaign | Question | Key Comparisons |
|----------|----------|-----------------|
| `update_adaptive_vs_fixed` | Adam/Lion/Muon vs Euclidean/SGD? | Convergence speed, final accuracy |
| `update_orthogonal_constraints` | Riemannian/Spectral vs unconstrained? | Gradient norm, stability |
| `update_credit_interaction` | Which update × credit pairs work best? | Heatmap of val_acc |

---

## Phase D: Advanced Analyses & Visualizations (1 day)

### D1: Stability Analysis Suite
- **Lyapunov spectra**: Full spectrum + max exponent distributions per dynamics
- **Basin stability**: Radius profiles with confidence bands (bootstrap)
- **Settling trajectories**: Norm evolution, convergence diagnostics
- **Energy landscapes**: 2D slices (PCA of activation space) for small models
- **Nonnormality analysis**: Pseudospectra, transient amplification bounds

### D2: Attribution & Counterfactuals
- **Axis attribution**: SHAP/ICE for each ontology axis on objectives
- **Counterfactual trajectories**: "What if this cell used energy_minimization instead of instantaneous?"
- **Mediation analysis**: Does stability mediate credit→accuracy?

### D3: Convergence Diagnostics
- **Learning curves**: Train/val loss/acc with confidence bands
- **Gradient statistics**: Norm, cosine similarity, alignment per layer
- **Weight evolution**: Spectral norm, effective rank, plasticity metrics

### D4: Pareto & Multi-Objective
- **Interactive Pareto fronts**: Hover for cell config, click for details
- **Scalarization sweeps**: Weight sensitivity analysis
- **Hypervolume tracking**: Across rounds/seeds

### D5: Reproducibility & Uncertainty
- **Seed variability**: Violin plots of metrics across seeds
- **Hardware variance**: CPU vs GPU, different GPU architectures
- **Checkpoint replay**: Bitwise match verification

---

## Phase E: Scaling & Production Hardening (1 day)

### E1: Multi-GPU / Distributed
- **DDP/FSDP support**: Transparent scaling for large models
- **Campaign sharding**: Split runs across nodes with shared store
- **Fault tolerance**: Automatic retry, checkpoint resume, straggler mitigation

### E2: Large-Scale Campaign Management
- **Campaign queue**: Priority, dependencies, resource quotas
- **Live monitoring**: Dashboard with run status, metrics streaming
- **Cost tracking**: GPU-hours, energy (J), carbon estimates

### E3: Artifact Management
- **Model registry**: Versioned checkpoints with metadata
- **Dataset versioning**: Hash-verified data splits
- **Environment snapshots**: Conda/uv lockfiles, container images

### E4: CI/CD Integration
- **Nightly regression**: Smoke tests + key metric thresholds
- **PR validation**: Affected component tests + quick campaign
- **Release gates**: Full property locks + acceptance suite

---

## Phase F: Continuous Validation & Documentation

### F1: Automated Quality Gates
- **Report linting**: Missing labels, empty tables, statistical errors
- **Data integrity**: Schema validation, monotonicity checks, outlier detection
- **Narrative coherence**: Hypothesis→result traceability

### F2: Living Documentation
- **Experiment catalog**: Searchable index of all campaigns with results
- **Method cards**: Standardized descriptions of each primitive
- **FAQ/Troubleshooting**: Common failure modes and fixes

### F3: Community & Extensibility
- **Plugin API**: Custom objectives, substrates, dynamics
- **Benchmark contributions**: Standard tasks with reference results
- **Tutorial notebooks**: From quick-start to advanced analyses

---

## 🎪 Phase 0: Enhanced Generic Showcase Experiment (0.5 days) — **✅ COMPLETED**

**Goal**: Make `scripts/showcase.py` a **zero-config, bias-free, maximally informative** demonstration of full system versatility.

### 0.1: Intelligent Component Selection — **✅ IMPLEMENTED**
- **Validity-aware sampling**: Uses `_is_valid_combination()` to filter known-invalid combinations (e.g., instantaneous dynamics + recurrent geometry + gradient credit)
- **Diversity maximization**: Round-robin grid interleaving across substrates ensures broad coverage
- **Coverage tracking**: `axis_coverage()` in report generator tracks which axes/primitives exercised
- **Adaptive strategy**: Starts with `round_robin_grid` for broad exploration; `model_based` available for focused follow-up

### 0.2: Progressive Disclosure & Budget Pacing — **✅ IMPLEMENTED**
- **Tiered execution** (3 tiers):
  - Tier 1 (0-20% budget): All axes, minimal depth (1 epoch, 1 seed) — max diversity
  - Tier 2 (20-60% budget): Promising regions, moderate depth (5 epochs, 3 seeds)
  - Tier 3 (60-100% budget): Deep dive on Pareto front (20 epochs, 5 seeds)
- **Automatic pacing**: Budget fractions enforced per tier; early-stop if budget exceeded
- **Graceful degradation**: Completes current tier if time runs out; reports partial results

### 0.3: Bias Detection & Mitigation — **✅ IMPLEMENTED**
- **Implicit bias audit**: `axis_coverage()` logs marginal distributions per axis
- **Policy comparison**: `--bias-check` runs `round_robin_grid` vs `model_based` vs `stratified_random` and compares results
- **Subspace coverage**: Framework for hypervolume computation (placeholder for future)
- **Failure analysis**: `failures_by_cause()` categorizes failures by axis combination

### 0.4: Self-Explanatory Showcase Report — **✅ IMPLEMENTED**
- **Executive summary**: Auto-generated with duration, cells evaluated, key findings
- **Coverage matrix**: Heatmap of (axis × primitive) with cell counts
- **Pareto gallery**: Top Pareto-optimal configurations across objective pairs
- **Stability atlas**: Lyapunov/basin/settling summary per dynamics family (when data available)
- **Failure taxonomy**: Table of failure modes with counts
- **Reproducibility block**: Exact commands, environment hash, export JSON link

### 0.5: Zero-Config UX Enhancements — **✅ IMPLEMENTED**
```bash
# Enhanced (smart defaults, progressive output)
uv run scripts/showcase.py --hours 1                    # auto-detects device, picks balanced
uv run scripts/showcase.py --hours 1 --profile quick    # 5-min smoke test (broad_shallow, 1 epoch, 1 seed)
uv run scripts/showcase.py --hours 1 --profile balanced # 30-min default (balanced, 5 epochs, 3 seeds)
uv run scripts/showcase.py --hours 1 --profile thorough # 1-2h thorough (balanced, 10 epochs, 5 seeds)
uv run scripts/showcase.py --hours 1 --profile deep     # max depth (narrow_deep, 20 epochs, 5 seeds)
uv run scripts/showcase.py --hours 1 --bias-check       # runs policy comparison, outputs bias report
uv run scripts/showcase.py --hours 1 --export-notebook showcase.ipynb  # exports Jupyter notebook
uv run scripts/showcase.py --dry-run                    # preview plan without execution
```

### 0.6: Built-in Hypothesis Generation — **✅ IMPLEMENTED**
- **Auto-hypotheses**: From showcase data, generates testable hypotheses:
  - Credit assignment effects on validation accuracy
  - Dynamics family effects on stability metrics
  - Substrate effects on energy efficiency
  - Cross-axis interactions (credit × dynamics)
- **Export to campaign DSL**: Hypotheses include test specification, effect size, power requirements

### 0.7: Resource-Aware Defaults — **🔄 PARTIALLY IMPLEMENTED**
- ✅ Hardware detection (auto CPU/GPU)
- ✅ Time budget estimation via `BudgetPlanner`
- ⏳ Hardware profiling: On first run, benchmark 1 cell per dynamics; cache for future time estimates
- ⏳ Memory-aware batching: Auto-reduce batch size / gradient accumulation if OOM detected
- ⏳ Energy budgeting: If NVML available, track Joules; report energy-per-experiment

### 0.8: Interactive Exploration — **🔄 PARTIALLY IMPLEMENTED**
- ✅ Notebook export: `--export-notebook` generates Jupyter notebook with all results + analysis cells
- ⏳ TUI mode (`--interactive`): Textual dashboard with live metrics, cell drill-down, early termination (stubbed)
- ⏳ Web mode (`--serve`): FastAPI + HTMX server for browser-based live monitoring (not started)

---

## 📦 Carried Forward from TODO54.md

### Non-Blocking Items (Deferred)

| Item | Status | Resolution |
|------|--------|------------|
| Basin stability Monte Carlo timeout (2+ min) | Known | `--basin-samples`/`--basin-steps` CLI options; `fast_mode` proxy |
| Lint findings in acceleration kernels | Pre-existing | Ratchet holds at 418; hygiene pass scheduled |
| `production-map` policy convergence | Expected NSGA-II | Use `round_robin_grid` for broad exploration |
| `energy_per_step` = 0.0 in quick-verify | CPU limitation | GPU runs measure NVML energy |
| `test_promotion_lock.py` expectation | Expected behavior | Correct NSGA-II selection behavior |

### Deferred / Nice-to-Have

| Item | Reason | TODO55 Integration |
|------|--------|---------------------|
| Multi-GPU DDP/FSDP support | Requires hardware | **Phase E1** |
| TileNet sharding | Niche | **Phase C5** (if needed) |
| Genealogy/t-SNE analysis | Advanced | **Phase D2** |
| Energy landscape 2D slices | Research | **Phase D1** |
| Tile dynamics analysis | Research | **Phase C5** |
| Z3 verification integration | Benchmark-only | **Phase B4** (formal methods) |
| Docker round-trip testing | Env constraints | **Phase E3** (containers) |

---

## 🔬 Specific Investigation Priorities

### Priority 1: Credit Assignment Physics (Week 1)
- **Hypothesis**: Local credits (FA, Hebbian, PEPITA) achieve >90% backprop accuracy on feedforward nets with <50% energy
- **Experiment**: `credit_local_vs_global` campaign (C1)
- **Report**: Energy-accuracy Pareto per substrate; stability comparison

### Priority 2: Dynamics Stability Landscape (Week 1)
- **Hypothesis**: Energy-minimization dynamics have larger basins but slower settling than predictive coding
- **Experiment**: `dynamics_stability_landscape` (C2) + `dynamics_settling_speed`
- **Report**: Basin radius profiles, Lyapunov spectra, settling time distributions

### Priority 3: Substrate Noise Robustness (Week 2)
- **Hypothesis**: Analog/memristive substrates degrade gracefully; digital is brittle to quantization
- **Experiment**: `substrate_noise_sensitivity` (C3) + `substrate_quantization`
- **Report**: Accuracy vs noise/bit-width curves; error bar overlap analysis

### Priority 4: Plasticity for Continual Learning (Week 2)
- **Hypothesis**: `conflict_adaptive` plasticity reduces catastrophic forgetting vs `null`/`ewc`
- **Experiment**: `plasticity_catastrophic_forgetting` (C4) on Split MNIST
- **Report**: Forgetting curves, forward/backward transfer metrics

---

## 📊 Report Quality Checklist (Every Campaign)

- [ ] **Abstract**: 150 words, states question, method, key finding
- [ ] **Hypotheses**: Pre-registered, numbered, with predictions
- [ ] **Methods**: Complete config (all 6 axes), seeds, hardware, time budget
- [ ] **Results**: Per-hypothesis subsection with stats + figures
- [ ] **Figures**: Titles, labels, units, error bars, n, statistical annotations
- [ ] **Tables**: Sortable, searchable, downloadable (CSV)
- [ ] **Statistics**: Effect sizes, CIs, p-values (corrected), power
- [ ] **Discussion**: Interpretation, limitations, alternative explanations
- [ ] **Reproducibility**: Export JSON, repro commands, environment hash
- [ ] **Accessibility**: Alt-text, colorblind-safe, semantic HTML

---

## 🛠 Technical Debt & Infrastructure

| Area | Issue | Fix |
|------|-------|-----|
| **Report generation** | Fragile string concatenation | Jinja2 + Pydantic context |
| **Campaign YAML** | No schema validation | Pydantic `CampaignSpec` with validation |
| **Hypothesis testing** | Manual JSON templates | Type-safe `Hypothesis` class + registry |
| **Visualization** | Matplotlib-only, static | Plotly for interactive HTML; Matplotlib for PDF |
| **Store schema** | Ad-hoc payload keys | Typed `Payload` models per analysis type |
| **Error handling** | Silent failures in stages | Structured `EvaluationResult` with error taxonomy |

---

## 📅 Suggested Timeline

```
Week 1 (Days 1-3):  Phase 0 + Phase A + Phase B (Enhanced showcase + Report templates + Hypothesis framework)
Week 2 (Days 4-6):  Phase C Priority 1-2 (Credit + Dynamics campaigns)
Week 3 (Days 7-9):  Phase C Priority 3-4 (Substrate + Plasticity campaigns)
Week 4 (Days 10-12): Phase D (Advanced analyses + visualizations)
Week 5 (Days 13-15): Phase E (Scaling + hardening)
Ongoing:             Phase F (Validation + documentation)
```

---

## 🎯 Definition of Done for TODO55

- [x] **Phase 0: Enhanced showcase** runs zero-config, produces bias-audited coverage report with executive summary
- [ ] **Report templates** render publication-ready HTML/PDF for any campaign (Phase A)
- [ ] **Hypothesis registry** drives experiment design and report structure (Phase B)
- [ ] **6 capability campaigns** executed with statistical rigor (10+ seeds each) (Phase C)
- [ ] **Advanced analyses** (stability, attribution, Pareto) integrated in reports (Phase D)
- [ ] **Multi-GPU campaigns** run successfully on 2+ GPUs (Phase E)
- [ ] **CI/CD gates** prevent regression of report quality and metrics (Phase E/F)
- [ ] **Documentation** complete: method cards, tutorial notebooks, FAQ (Phase F)
- [ ] **All TODO54 deferred items** either resolved or explicitly scheduled

---

## 💡 High-Level Considerations

### Scientific Validity
- **Pre-registration**: Hypotheses locked before campaign launch
- **Multiple comparison correction**: Benjamini-Hochberg FDR for exploratory analyses
- **Effect sizes over p-values**: Report Cohen's d, Cliff's Δ, Bayes factors
- **Confidence intervals**: Always prefer CIs over point estimates

### Communication Strategy
- **Layered reports**: Executive summary → technical details → raw data
- **Audience awareness**: ML researchers (methods), neuroscientists (dynamics), hardware engineers (substrates)
- **Visual hierarchy**: Key findings prominent; supplementary in appendices
- **Reproducibility first**: Every claim traceable to record + command

### Resource Optimization
- **Adaptive allocation**: Evidence-driven allocator shifts budget to promising regions
- **Early stopping**: Futility bounds + efficacy bounds per cell
- **Caching**: Reuse settled states, Jacobians, embeddings across analyses
- **Profiling**: Per-cell walltime/energy breakdown for cost modeling

### Extensibility
- **Primitive registration**: New substrate/geometry/dynamics auto-appear in campaigns
- **Objective plugins**: Custom metrics without core changes
- **Analysis pipelines**: Composable, reusable, testable
- **Export standards**: JSON-LD for semantic interoperability

---

## 🚀 Quick Start for Next Session

```bash
# 1. Validate enhanced showcase works (zero-config) — ✅ WORKING
uv run scripts/showcase.py --hours 0.05 --profile quick

# 2. Run with bias check (policy comparison) — ✅ WORKING
uv run scripts/showcase.py --hours 0.1 --profile balanced --bias-check

# 3. Export showcase results to notebook for exploration — ✅ WORKING
uv run scripts/showcase.py --hours 0.1 --profile balanced --export-notebook showcase_exploration.ipynb

# 4. Generate report template skeleton (Phase A) — ⏳ TODO
uv run comp report --template base --output templates/report_base.html

# 5. Create first hypothesis-driven campaign (Phase B) — ⏳ TODO
cat > campaigns/credit_efficiency.yaml << 'EOF'
# (use Phase B2 DSL)
EOF

# 6. Run with hypothesis testing — ⏳ TODO
uv run comp hypothesis-campaign --campaign campaigns/credit_efficiency.yaml --store exp.db

# 7. Generate narrative report — ⏳ TODO
uv run comp report --store exp.db --template credit_efficiency --output report.html
```

---

## 📈 Progress Summary (Updated 2026-10-09)

### ✅ Phase 0 Complete: Enhanced Showcase Campaign

**Implemented Features:**
1. **Zero-config UX**: `--profile quick|balanced|thorough|deep` presets with smart defaults
2. **Tiered execution**: 3-tier progressive disclosure (exploration → refinement → deep dive)
3. **Bias detection**: `--bias-check` compares 3 sampling policies, outputs JSON audit
4. **Self-explanatory HTML report**: Executive summary, coverage matrix, Pareto gallery, stability atlas, failure taxonomy, reproducibility block
5. **Auto-hypothesis generation**: From showcase data → testable hypotheses with statistical test specs
6. **Notebook export**: `--export-notebook` generates Jupyter notebook with analysis cells
7. **Dry-run mode**: Preview campaign plan without execution
8. **Resource-aware**: Auto CPU/GPU detection, time budget estimation

**Remaining in Phase 0 (deferred to later):**
- Hardware profiling cache for time estimates
- OOM recovery with gradient accumulation
- NVML energy tracking
- Full TUI interactive mode (`--interactive`)
- Web dashboard mode (`--serve`)

### 🔄 Next Phases (Not Started)

| Phase | Status | Key Deliverables |
|-------|--------|------------------|
| A: Report Architecture | Not started | Jinja2 templates, Pydantic context, multi-format output |
| B: Experiment Design | Not started | Hypothesis registry, Campaign DSL, Power analysis |
| C: Capability Campaigns | Not started | 6 campaign families (credit, dynamics, substrate, plasticity, geometry, update) |
| D: Advanced Analyses | Not started | Stability suite, Attribution, Pareto, Reproducibility |
| E: Scaling | Not started | Multi-GPU, Campaign queue, Artifact mgmt, CI/CD |
| F: Validation | Not started | Quality gates, Living docs, Plugin API |

### 🎯 Immediate Next Steps

1. **Phase A**: Implement Jinja2-based report templates with Pydantic context models
2. **Phase B**: Create `Hypothesis` class + registry, Campaign DSL with Pydantic validation
3. **Phase C**: Run first flagship campaign (`credit_local_vs_global`) with 10+ seeds
4. **Integration**: Wire showcase hypotheses → campaign DSL → focused follow-up campaigns