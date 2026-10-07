# TODO53 — Development Plan: Academic/Industrial Quality Experiment Infrastructure

**Goal**: Enable running experiments with compelling, shareable preliminary results that conclusively demonstrate Computronium's capabilities and potential. Default to GPU; ensure reproducibility, rigorous analysis, and publication-ready outputs.

---

## 1. GPU-First Execution Infrastructure

### 1.1 Default GPU for All Experiment Commands
- [ ] **CLI**: Add `--device auto` (default) → CUDA if available, else CPU to all `comp` subcommands (`run`, `benchmark`, `stability-plasticity`, `frozen-theta-psi`, `parity`)
- [ ] **RunSpec**: Add `device: "auto" | "cuda" | "cpu"` field with auto-detection logic in `RunSpec.model_validator`
- [ ] **Trainer**: Ensure `SystemTrainerConfig.device="auto"` resolves to CUDA; propagate to all sub-components (geometry, substrate, kernels)
- [ ] **Kernels**: Verify Triton kernels auto-dispatch on CUDA (status: `kernel_verified` → `select_backend(spec, "auto")` returns `"kernel"`)
- [ ] **Tests**: Add `@pytest.mark.gpu` marker to GPU-required tests; ensure CI can run on GPU runners

### 1.2 GPU Memory Management
- [ ] **Batch sizing**: Auto-scale batch size based on `torch.cuda.get_device_properties(0).total_memory` (target 80% utilization)
- [ ] **Gradient accumulation**: Implement for large models that exceed memory at desired batch size
- [ ] **Mixed precision**: Enable `torch.autocast("cuda")` by default for FP16/BF16 training; add `precision` field to RunSpec (`fp32`, `fp16`, `bf16`)
- [ ] **Memory profiling**: Integrate `torch.cuda.max_memory_allocated()` into metrics payload for `memory_usage` objective

### 1.3 Multi-GPU Support (DDP/FSDP)
- [ ] **DistributedSystemTrainer**: Wire `DistributedSystemTrainer` into experiment kernel evaluator for `s6_train` stage
- [ ] **TileNet sharding**: Activate `TileShardedBackend` with NCCL `all_reduce_gradients`/`broadcast_params` for large TileMesh geometries
- [ ] **RunSpec**: Add `num_gpus: int = 1`, `distributed_backend: "ddp" | "fsdp" | "deepspeed"` fields

---

## 2. Measured Objectives — Close the Measurement Gap

**Problem**: 4 of 36 registered objectives are measured; rest refused at RunSpec validation.

### 2.1 Cost Objectives (High Priority)
| Objective | Implementation | Effort |
|-----------|----------------|--------|
| `flops` | `fvcore.nn.FlopCountAnalysis` or custom counter in `SystemTrainer.train_step` | Medium |
| `macs_per_step` | Same as FLOPs; 1 MAC = 2 FLOPs | Low (derivative) |
| `memory_usage` | `torch.cuda.max_memory_allocated()` / CPU RSS delta in trainer | Low |
| `energy_per_step` | NVML `nvidia-smi` power draw × step time; fallback: `macs_per_step × substrate.energy_per_mac` | Medium |
| `energy_per_mac` | SubstrateSpec field: `Digital=0.1pJ`, `Memristive=0.01pJ`, `Neuromorphic=0.001pJ` (literature) | Low |
| `latency_ms` | `torch.cuda.Event` timing around forward+backward; avg over 100 steps | Low |

### 2.2 Substrate Objectives
- [ ] Implement `spike_rate` for NeuromorphicSubstrate (count spikes / neuron / step)
- [ ] Implement `ir_drop_variance` for MemristiveSubstrate (measured in forward_operator)
- [ ] Implement `phase_noise` for OpticalSubstrate
- [ ] Implement `gate_fidelity`, `coherence_time` for QuantumSubstrate

### 2.3 Plasticity Objectives
- [ ] `psi_capacity`: `psi.numel()` for routing/fast_weights/rule_state
- [ ] `consolidation_cost`: FLOPs of ψ→θ consolidation step
- [ ] `rewrite_rate`: `‖ψ_t - ψ_{t-1}‖ / ‖ψ_{t-1}‖` per episode

### 2.4 Stability Objectives (Partial)
- [ ] `spectral_radius`: Already implemented via `spectral_radius_from_jacobian` — wire to evaluator
- [ ] `max_singular_value`: Already implemented via `dominant_singular_value` — wire to evaluator
- [ ] `lyapunov_exponent`: QR method over trajectory (exists in `StabilityMonitor`)

---

## 3. Experiment Kernel — Evaluator Hardening

### 3.1 Replace Placeholder Evaluator
- **Current**: Acceptance tests (U1-U5) use placeholder returning walltime only
- **Fix**: Wire `execution/evaluate.py` → `SystemTrainer` → real metrics (`train_acc`, `val_acc`, `val_loss`, all measured objectives)
- [ ] Verify `evaluate_cell` composes coordinate → System → trains → measures → returns payload
- [ ] Ensure all measured objectives populate `Record.payload`
- [ ] Add `metric_key` mapping in `MEASURED_OBJECTIVES` for newly implemented objectives (§2)

### 3.2 RunSpec → Evaluator Integration
- [ ] `batch_limit` respected (currently `MEASURED_BATCH_LIMIT=2` for quick gate)
- [ ] `param_budget` enforced in geometry sizing (auto-narrow `hidden_dim`)
- [ ] `fidelity` → `n_seeds`, `epochs`, `batch_limit` mapping (L0=1/1/2, L1=3/3/0, L2=5/10/0)
- [ ] `deterministic=True` → `torch.use_deterministic_algorithms(True)`, `CUBLAS_WORKSPACE_CONFIG=:4096:8`

### 3.3 Long-Run Resilience
- [ ] **Checkpointing**: Save `SystemTrainer` state (model, optimizer, epoch, RNG) every N epochs to store
- [ ] **Resume**: `comp run --run-id <id>` loads checkpoint, continues from last epoch
- [ ] **Heartbeat**: Write `run.heartbeat` timestamp every 30s; detect stalls
- [ ] **Timeout handling**: Graceful shutdown on SIGTERM → save checkpoint → exit(0)

---

## 4. Reporting & Visualization — Publication Ready

### 4.1 Automated Report Generation
- [ ] **`comp report`**: Enhance to produce:
  - Markdown summary with tables (accuracy, walltime, params, stability metrics)
  - Pareto frontier plots (accuracy vs walltime, accuracy vs params, stability vs plasticity)
  - Per-axis ablation tables (credit swap, substrate swap, plasticity swap)
  - Convergence curves (loss/accuracy per epoch, per seed)
  - Stability proxies (ρ(J), σ_max, Lyapunov) over training
- [ ] **HTML dashboard**: Interactive Plotly charts (filter by axis, seed, epoch)
- [ ] **LaTeX/PDF**: `pandoc` export for paper insertion

### 4.2 Gallery Figures (Re-pin Infrastructure)
- [ ] **`comp gallery`**: Render all demo figures from store records (locked in `test_gallery_lock.py`)
- [ ] **Manifest**: `docs/figures/manifest.json` with SHA, params, metrics for reproducibility
- [ ] **CI integration**: Gallery lock fails if figures drift from committed manifest

### 4.3 Comparative Analysis Tools
- [ ] **Ablation reporter**: `analysis/ablation.py` → leave-one-out, Sobol indices → HTML/Markdown
- [ ] **Genealogy**: `analysis/genealogy.py` → hyperparameter fingerprinting, PCA/t-SNE/UMAP of coordinates
- [ ] **Energy landscapes**: `analysis/energy_landscape.py` → 2D slices, Hessian spectrum, minima detection
- [ ] **Tile dynamics**: `analysis/tile_dynamics.py` → settling trajectories, routing patterns, utilization

### 4.4 Experiment Metadata & Provenance
- [ ] **Code SHA**: Embed `git rev-parse HEAD` in every record (already in `Record.code_sha`)
- [ ] **Environment**: Capture `pip freeze`, `nvidia-smi`, `torch.__version__`, CUDA version
- [ ] **Data version**: Hash of dataset files (MNIST/CIFAR/etc.)
- [ ] **Config snapshot**: Full RunSpec + resolved hyperparameters in every record

---

## 5. Benchmark Suites — Expand & Harden

### 5.1 Existing Suites (Verify GPU, Add Metrics)
| Suite | Status | GPU Test | Add Objectives |
|-------|--------|----------|----------------|
| `adaptation_efficiency` | Implemented | [ ] | `memory_usage`, `flops`, `psi_capacity` |
| `compute_efficiency` | Implemented | [ ] | `macs_per_step`, `latency_ms`, `energy_per_step` |
| `structural_robustness` | Implemented | [ ] | `basin_stability`, `recovery_time` |
| `algorithm_migration` | Implemented | [ ] | `migration_accuracy`, `θ_bitwise_invariance` |
| `z3_fixed_weights` | Implemented | [ ] | `task_diversity`, `ψ_orthogonality` |

### 5.2 New Benchmark Suites (High Impact)
- [ ] **`credit_assignment_scaling`**: Depth scaling (2→50 layers) for Backprop/FA/EqProp/PEPITA/TargetProp
- [ ] **`substrate_precision_scaling`**: Digital FP32/FP16/BF16/INT8/Ternary vs Memristive/Neuromorphic
- [ ] **`stability_plasticity_frontier`**: Systematic ρ(J) sweep (0.5→1.2) × plasticity types × tasks
- [ ] **`local_credit_scaling`**: FA/DFA/PEPITA/TargetProp on ImageNet-scale (resnet50, vit-small)
- [ ] **`energy_accuracy_pareto`**: Multi-objective: accuracy vs energy_per_step across all axes

### 5.3 Benchmark Runner Improvements
- [ ] **Parallel execution**: Run coordinates in parallel across GPUs (Ray/Joblib)
- [ ] **Progress tracking**: Rich progress bars with ETA, per-coordinate status
- [ ] **Partial results**: Save intermediate results; resume on interruption
- [ ] **Statistical rigor**: Bootstrap CIs (1000 resamples) for all metrics; report median + 95% CI

---

## 6. Fixes & Correctness

### 6.1 Known Issues
- [ ] **NCA Geometry**: Fix `NcaGeometry.step` to accept flattened batch `(B, F)` → reshape to `(B, C, H, W)` in `route`; remove from `_UNAVAILABLE`
- [ ] **EnergyMinimization β≥1**: Gradient credit with β≥1 has zero pseudo-gradient (constraint exists); verify EqProp works at β=1.0
- [ ] **Determinism**: Ensure bitwise reproducibility on GPU (CUDA determinism + fixed conv algorithms)
- [ ] **Memory leaks**: Profile long runs; fix any tensor accumulation in trajectory recording

### 6.2 Property Locks (Must Stay Green)
- [ ] **L1-L7**: `tests/property/test_ontology_locks.py`
- [ ] **J1-J7**: `tests/property/joint/`
- [ ] **S/D/C/U/P-axis**: `tests/property/test_*_axis.py`
- [ ] **Registry locks**: `test_registry_completeness_lock.py`, `test_kernel_verified_promotion_rule.py`
- [ ] **CLI lock**: `test_cli_readme_lock.py` (every fenced bash block in README executes)

### 6.3 Type Safety
- [ ] **Pyright strict**: Enable on `computronium/experiment/`, `computronium/core/`, `computronium/ontology/`
- [ ] **No `Any`**: Replace with generics/Protocol in experiment kernel
- [ ] **Config round-trip**: `extract_config` ↔ `compose_system_from_configs` identity for all primitives

---

## 7. Analysis Infrastructure

### 7.1 Statistical Analysis
- [ ] **Bootstrap CIs**: `analysis/bootstrap.py` — percentile BCa for all metrics
- [ ] **Significance testing**: Paired t-test / Wilcoxon for credit/plasticity comparisons
- [ ] **Effect sizes**: Cohen's d, Cliff's delta for practical significance
- [ ] **Power analysis**: Minimum seeds for 80% power at α=0.05

### 7.2 Multi-Objective Analysis
- [ ] **Pareto front**: `analysis/pareto.py` — knee detection, hypervolume indicator
- [ ] **Axis-aligned objectives**: Per-axis Pareto fronts (substrate: energy vs accuracy; plasticity: ψ_capacity vs stability)
- [ ] **Ruler-relative**: Normalize all metrics to Backprop baseline per task

### 7.3 Dynamical Analysis
- [ ] **Lyapunov spectra**: QR decomposition over full trajectory
- [ ] **Basin stability**: Monte Carlo perturbation → measure return probability
- [ ] **Transient amplification**: `estimate_directional_amplification` on probed directions
- [ ] **Energy tracking**: Per-iteration free energy for PC/EqProp; Hopfield energy for EM

---

## 8. Reproducibility & Packaging

### 8.1 Experiment Packaging
- [ ] **`comp export`**: Export run → self-contained directory (spec, records, code SHA, env, figures)
- [ ] **`comp repro`**: Replay exported run → bitwise diff metrics (within tolerance)
- [ ] **Docker/Apptainer**: `Dockerfile.experiment` with pinned CUDA, PyTorch, dependencies

### 8.2 Continuous Benchmarking
- [ ] **Nightly**: `comp benchmark run --suite all --device cuda` → upload results to S3/GCS
- [ ] **Regression detection**: Compare `validation_accuracy`, `walltime_total` vs baseline (alert on >5% regression)
- [ ] **Benchmark dashboard**: `scripts/bench_dashboard.py` → latency/memory vs commit (already exists)

---

## 9. Documentation & Examples

### 9.1 User-Facing Docs
- [ ] **Experiment Guide**: `docs/experiments/` — end-to-end tutorials (quick-verify → production-map → claim)
- [ ] **Benchmark Cookbook**: `docs/benchmarks/` — each suite with expected results, interpretation
- [ ] **Analysis Recipes**: `docs/analysis/` — Pareto, ablation, stability-plasticity, energy landscapes
- [ ] **GPU Guide**: Mixed precision, multi-GPU, memory optimization

### 9.2 API Reference
- [ ] **RunSpec schema**: Auto-generate from Pydantic model (field descriptions, examples)
- [ ] **Objectives registry**: `docs/generated/objectives.md` (already generated) — add measurement status
- [ ] **CLI reference**: `comp --help` output → markdown (locked by `test_cli_readme_lock.py`)

---

## 10. Prioritized Execution Order

| Phase | Focus | Deliverable | Est. Effort |
|-------|-------|-------------|-------------|
| **P0** | GPU default + measured objectives | `quick-verify` on GPU with flops/memory/energy | 2-3 days |
| **P1** | Evaluator hardening + checkpointing | Full `production-map` run on GPU, resumable | 3-4 days |
| **P2** | Reporting + gallery | Publication-ready HTML/PDF from `comp report` | 2-3 days |
| **P3** | Benchmark suites + analysis | All 5 suites + 3 new suites with statistical rigor | 4-5 days |
| **P4** | Reproducibility + packaging | Docker export, nightly benchmark CI | 2-3 days |

**Total**: ~13-18 days for production-ready experiment infrastructure.

---

## 11. Success Criteria (Definition of Done)

- [ ] `comp run quick-verify --store exp.db --device auto` completes in <2 min on RTX 3080 with all 6 measured objectives populated
- [ ] `comp benchmark run --suite adaptation_efficiency --device cuda` produces HTML report with Pareto frontiers, bootstrap CIs
- [ ] `comp stability-plasticity --run --device cuda` maps ρ(J) 0.5→1.2 across 3 plasticity types, 3 seeds, produces stability-plasticity trade-off figure
- [ ] `comp frozen-theta-psi --run --device cuda --substrates digital,memristive,ternary` demonstrates task migration on frozen θ with bitwise θ audit
- [ ] All property locks (L1-J7, axis locks, registry locks) pass on GPU
- [ ] Gallery figures re-pinned and committed (`docs/figures/manifest.json` updated)
- [ ] Experiment export → repro yields bitwise-identical metrics (within 1e-7)
- [ ] Documentation renders without errors; all code blocks execute

---

## 12. Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GPU OOM on large geometries | High | Blocks runs | Auto batch scaling + gradient accumulation |
| Triton kernel parity failures | Medium | Slow fallback | Keep reference kernels; parity gate in CI |
| Non-determinism on GPU | Medium | Repro failures | `torch.use_deterministic_algorithms`, fixed conv algos |
| Long run interruption | High | Lost compute | Checkpointing every epoch + resume |
| Objective measurement gaps | Medium | Incomplete Pareto | Prioritize §2 objectives; stub unmeasured with `None` |
| NCA geometry blocking geometry sweep | Low | Reduced coverage | Fix or document as known limitation |

---

## 13. Quick Wins (Do First, <1 Day Each)

1. **GPU default**: Add `device="auto"` → CUDA detection to `RunSpec` and all CLI commands
2. **Memory metric**: Add `torch.cuda.max_memory_allocated()` to trainer → `memory_usage` objective
3. **FLOPs metric**: Add `fvcore.nn.FlopCountAnalysis` wrapper → `flops` objective
4. **Checkpointing**: Save trainer state dict to DuckDB every epoch
5. **Mixed precision**: `torch.autocast("cuda")` in `SystemTrainer.train_step`
6. **NCA fix**: Reshape in `NcaGeometry.route` → remove from `_UNAVAILABLE`
7. **Report enhancement**: Add Pareto plots to `comp report --format html`

---

## 14. References

- `AGENTS.md` — Code guidelines, commit checklist, testing tiers
- `README.md` — System overview, 6-axis ontology, CLI reference
- `computronium/experiment/schema/` — RunSpec, objectives, registries, constraints
- `computronium/experiment/surface/profiles.py` — Run profiles (quick-verify, production-map, etc.)
- `computronium/benchmarks/joint/` — 5 benchmark suites
- `computronium/analysis/` — Pareto, ablation, energy landscape, genealogy
- `tests/property/` — Property locks (L1-J7, axis locks, registry locks)
- `tests/acceptance/test_unified_kernel.py` — U1-U5 kernel guarantees
- `scripts/probes/` — Probe scripts with measured-regime numbers