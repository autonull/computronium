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

## 🎪 Phase 0: Enhanced Generic Showcase Experiment (0.5 days)

**Goal**: Make `scripts/showcase.py` a **zero-config, bias-free, maximally informative** demonstration of full system versatility.

### 0.1: Intelligent Component Selection
- **Validity-aware sampling**: Only propose combinations that pass `SystemConfig.validate()` (use `_is_valid_combination()`)
- **Diversity maximization**: Latin hypercube / Sobol sequence over valid component space, not random
- **Coverage tracking**: Report which axes/primitives were exercised, which were skipped (and why)
- **Adaptive strategy**: Start with `round_robin_grid` for broad coverage; switch to `model_based` only after sufficient exploration

### 0.2: Progressive Disclosure & Budget Pacing
- **Tiered execution**:
  - Tier 1 (0-20% budget): All axes, minimal depth (1 epoch, 1 seed) — max diversity
  - Tier 2 (20-60% budget): Promising regions, moderate depth (5 epochs, 3 seeds)
  - Tier 3 (60-100% budget): Deep dive on Pareto front (20 epochs, 5 seeds)
- **Automatic pacing**: Real-time budget tracking with early-stop if Tier 1 exceeds 25% budget
- **Graceful degradation**: If time runs out, complete current tier; report partial results honestly

### 0.3: Bias Detection & Mitigation
- **Implicit bias audit**: Log marginal distributions of each axis; flag over/under-representation
- **Policy comparison**: Run same budget with `round_robin_grid` vs `model_based` vs `stratified_random`; report divergence
- **Subspace coverage**: Compute hypervolume of explored vs total valid space
- **Failure analysis**: Categorize failures (validation, runtime, numerical) per axis combination

### 0.4: Self-Explanatory Showcase Report
- **Executive summary**: "In X hours, we explored Y valid combinations across Z axes. Key findings: ..."
- **Coverage matrix**: Heatmap of (axis × primitive) with cell count, success rate, mean val_acc
- **Pareto gallery**: One figure per objective pair with all evaluated points
- **Stability atlas**: Lyapunov/basin/settling summary per dynamics family
- **Failure taxonomy**: Table of failure modes × axis combinations with counts
- **Reproducibility block**: Exact commands, environment hash, export JSON link

### 0.5: Zero-Config UX Enhancements
```bash
# Current (works but rigid)
uv run scripts/showcase.py --hours 1 --strategy balanced --device auto

# Enhanced (smart defaults, progressive output)
uv run scripts/showcase.py --hours 1                    # auto-detects device, picks balanced
uv run scripts/showcase.py --hours 1 --interactive      # TUI: live metrics, early stop, drill-down
uv run scripts/showcase.py --hours 1 --profile thorough # alias for balanced + more seeds/epochs
uv run scripts/showcase.py --hours 1 --profile quick    # alias for broad_shallow
uv run scripts/showcase.py --hours 1 --profile deep     # alias for narrow_deep
uv run scripts/showcase.py --hours 1 --bias-check       # runs policy comparison, outputs bias report
```

### 0.6: Built-in Hypothesis Generation
- **Auto-hypotheses**: From showcase data, generate testable hypotheses:
  - "Substrate X outperforms digital on task Y by Z%"
  - "Dynamics A has larger basins than B on recurrent geometry"
  - "Credit C achieves Pareto-optimal energy/accuracy on substrate D"
- **Export to campaign DSL**: One-click conversion to Phase B2 YAML for focused follow-up

### 0.7: Resource-Aware Defaults
- **Hardware profiling**: On first run, benchmark 1 cell per dynamics; cache for future time estimates
- **Memory-aware batching**: Auto-reduce batch size / gradient accumulation if OOM detected
- **Energy budgeting**: If NVML available, track Joules; report energy-per-experiment

### 0.8: Interactive Exploration (Optional)
- **TUI mode** (`--interactive`): Textual dashboard with live metrics, cell drill-down, early termination
- **Web mode** (`--serve`): FastAPI + HTMX server for browser-based live monitoring
- **Notebook export**: `--export-notebook` generates Jupyter notebook with all results + analysis cells

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

- [ ] **Phase 0: Enhanced showcase** runs zero-config, produces bias-audited coverage report with executive summary
- [ ] **Report templates** render publication-ready HTML/PDF for any campaign
- [ ] **Hypothesis registry** drives experiment design and report structure
- [ ] **6 capability campaigns** executed with statistical rigor (10+ seeds each)
- [ ] **Advanced analyses** (stability, attribution, Pareto) integrated in reports
- [ ] **Multi-GPU campaigns** run successfully on 2+ GPUs
- [ ] **CI/CD gates** prevent regression of report quality and metrics
- [ ] **Documentation** complete: method cards, tutorial notebooks, FAQ
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
# 1. Validate enhanced showcase works (zero-config)
uv run scripts/showcase.py --hours 0.05

# 2. Run with bias check (policy comparison)
uv run scripts/showcase.py --hours 0.1 --bias-check

# 3. Generate report template skeleton
uv run comp report --template base --output templates/report_base.html

# 4. Create first hypothesis-driven campaign
cat > campaigns/credit_efficiency.yaml << 'EOF'
# (use Phase B2 DSL)
EOF

# 5. Run with hypothesis testing
uv run comp hypothesis-campaign --campaign campaigns/credit_efficiency.yaml --store exp.db

# 6. Generate narrative report
uv run comp report --store exp.db --template credit_efficiency --output report.html

# 7. Export showcase results to notebook for exploration
uv run scripts/showcase.py --hours 0.1 --export-notebook showcase_exploration.ipynb
```

---

*This roadmap evolves. Update after each phase based on learnings.*