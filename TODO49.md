# TODO49: From Validation to Usable System

> **This plan produces a system you can use for real problems.** Iterations 0–4
> are the validation gate (compressed from the old plan). Iterations 5–11 build
> the capabilities that make the system usable for real problems. The headline is
> the **first iteration that ships a real capability**, not the last one that
> passes a validation gate.

---

## Phase 1: Validation Gate (Iterations 0–4, ~20 min)

*The old Iterations 0–8, compressed to what's necessary and run on GPU by
default.*

| Iteration | Scope | Time | Success Signal |
|---|---|---|---|
| 0 | Env + fixtures + device | 30s | GPU present; fixtures built |
| 1 | Config validation + round-trip | 10s | Valid combos pass; invalid rejected; round-trip bitwise |
| 2 | Config→system→train_step on synthetic | 15s | Metrics on right device; data actually on GPU |
| 3 | ExperimentConfig presets → trainer on digits | 45s | **10 epochs, 3 seeds, clears 1.5× chance** |
| 4 | Spec round-trip + determinism + CPU↔GPU agreement | 20s | Bitwise on CPU; tolerance on GPU; cross-device within registered tolerance |

**Device policy:** GPU is default (`device="cuda"`). `device="cpu"` is a weaker,
separately reported pass. No slice silently falls back to CPU — `gpu_required`
skips loudly.

**Fixtures** (built in Iteration 0, not assumed):
```python
@pytest.fixture(scope="session")
def device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"

@pytest.fixture(scope="session")
def gpu_required() -> None:
    if not torch.cuda.is_available():
        pytest.skip("CUDA unavailable: this slice is a GPU claim")

@pytest.fixture(scope="session")
def seed() -> int: return 42

@pytest.fixture(scope="session")
def sample_data(device: str, seed: int):
    """4-sample 2D linearly separable, resident on `device`."""
    generator = torch.Generator().manual_seed(seed)
    x = torch.randn(4, 2, generator=generator).to(device)
    y = (x.sum(dim=1) >= 0).long()
    return DataLoader(TensorDataset(x, y), batch_size=4, shuffle=False, generator=generator)
```

**Fail fast:** Run iterations by file with `-p no:xdist`. Stop on first failure,
fix, re-run only that iteration.

---

## Phase 2: Real Capabilities (Iterations 5–11, the actual work)

*Each iteration adds a capability that makes the system usable for real problems.
They are sequenced so each enables the next. Success = the capability works at a
real regime, not a smoke test.*

### Iteration 5: Convergence Training on Real Data (~30 min)

**Goal:** Train to convergence on MNIST and CIFAR-10 with learning curves,
early stopping, and checkpoint resume.

| Slice | Test | Success Signal |
|---|---|---|
| 5.1 MNIST convergence | 4 rules × MNIST × 100 epochs, full batches, early stopping (patience=5) | Each rule reaches ≥95% train_acc; learning curve plotted; best checkpoint saved |
| 5.2 CIFAR-10 convergence | 4 rules × CIFAR-10 × 100 epochs, full batches, early stopping | Each rule reaches ≥70% train_acc; learning curve plotted |
| 5.3 Checkpoint resume | Interrupt at epoch 50 → resume → complete | Identical final metrics; bitwise-identical weights at resume point |
| 5.4 Learning curve artifacts | Save loss/acc per epoch as JSON | File written; loadable; monotonic decrease after epoch 10 |

**Deliverable:** A trained model checkpoint you can load and use.

### Iteration 6: Model Export for Serving (~20 min)

**Goal:** Export a trained model to a portable format that runs without this repo.

| Slice | Test | Success Signal |
|---|---|---|
| 6.1 ONNX export | `model.export_onnx("model.onnx")` | File loads in ONNX Runtime; inference matches PyTorch within 1e-4 |
| 6.2 TorchScript export | `model.export_torchscript("model.pt")` | Loads in libtorch C++ API; inference matches |
| 6.3 Export includes preprocessing | Export includes input normalization | Exported model accepts raw pixels; applies normalization internally |
| 6.4 Batch inference | Export accepts batch dimension | Runs 32-sample batch without code changes |

**Deliverable:** An `.onnx` file you can deploy.

### Iteration 7: Data Pipelines for Real Datasets (~30 min)

**Goal:** Load real datasets (MNIST, CIFAR, ImageNet subset, custom CSV) with
standard preprocessing, batching, shuffling, and augmentation — no manual
tensor manipulation.

| Slice | Test | Success Signal |
|---|---|---|
| 7.1 MNIST/CIFAR loaders | `DataLoader.from_torchvision("MNIST", batch_size=128)` | Returns batched, normalized tensors on device |
| 7.2 ImageFolder loader | `DataLoader.from_imagefolder("path/", batch_size=64)` | Loads directory structure; applies resize/normalize/augment |
| 7.3 CSV/Parquet loader | `DataLoader.from_csv("data.csv", target="label", batch_size=256)` | Handles missing values, categorical encoding, normalization |
| 7.4 Streaming loader | `DataLoader.from_webdataset("s3://bucket/")` | Streams without loading full dataset into memory |

**Deliverable:** A `DataLoader` API you point at data and get batches.

### Iteration 8: Distributed Training (~45 min)

**Goal:** Train the same model on 2+ GPUs with data parallelism, same convergence
as single-GPU.

| Slice | Test | Success Signal |
|---|---|---|
| 8.1 DDP launch | `torchrun --nproc_per_node=2 train.py` | Launches 2 processes; same epochs-to-convergence as single GPU (±10%) |
| 8.2 Gradient sync | Verify gradients averaged across ranks | `all_reduce` on gradients; identical updates to single-GPU |
| 8.3 Checkpoint sharding | Save/load sharded checkpoint | Resumes on different world size; identical metrics |
| 8.4 Gradient accumulation | `accumulation_steps=4` matches batch×4 | Same convergence as full batch |

**Deliverable:** A `DistributedTrainer` that scales to N GPUs.

### Iteration 9: Performance Benchmarks (~20 min)

**Goal:** Measured throughput, memory, latency at scale — numbers you can
capacity-plan with.

| Slice | Test | Success Signal |
|---|---|---|
| 9.1 Throughput | `benchmark_throughput(model, batch_sizes=[32,64,128,256])` | Samples/sec per GPU; linear scaling up to memory limit |
| 9.2 Memory profile | `benchmark_memory(model, batch_sizes=[32..512])` | Peak GPU memory; OOM batch size identified |
| 9.3 Latency | `benchmark_latency(model, batch_sizes=[1,4,16,64])` | p50/p99 latency per batch; GPU utilization >80% |
| 9.4 Mixed precision | Compare fp32 vs fp16/bf16 | ≥1.5× throughput; <1% accuracy drop |

**Deliverable:** A benchmark JSON you can capacity-plan with.

### Iteration 10: Monitoring & Production Hardening (~30 min)

**Goal:** The system survives production: logging, metrics, graceful degradation,
recovery.

| Slice | Test | Success Signal |
|---|---|---|
| 10.1 Structured logging | `trainer.fit(log_interval=10)` | JSON logs with epoch, loss, acc, lr, GPU mem, throughput |
| 10.2 Metrics export | Prometheus `/metrics` endpoint | Exposes loss, acc, throughput, GPU util, memory |
| 10.3 Graceful shutdown | SIGTERM at epoch 50 → saves checkpoint | Resumes from exact epoch; no data loss |
| 10.4 OOM recovery | OOM at batch 100 → skips batch → continues | Training continues; skipped batch logged; no crash |
| 10.5 Health checks | `/health` endpoint | Returns model status, GPU status, queue depth |

**Deliverable:** A trainer you can run unattended.

### Iteration 11: API Stability & Versioning (~15 min)

**Goal:** The Python API has a version contract; breaking changes require a major
bump.

| Slice | Test | Success Signal |
|---|---|---|
| 11.1 Versioned API | `computronium.__version__` follows semver | Major bump = breaking change; minor = feature; patch = fix |
| 11.2 Deprecation policy | `@deprecated` on old API | Warning at runtime; 2 minor versions before removal |
| 11.3 Changelog | `CHANGELOG.md` auto-generated from commits | Every PR updates changelog; release notes generated |
| 11.4 Compatibility test | `pip install computronium==X.Y` → run smoke test | Previous minor version's smoke test passes |

**Deliverable:** A library you can depend on.

---

## Success Criteria: The System Is Usable

**You can say the system is usable when ALL of these are true:**

1. **Phase 1 passes** — wiring is correct (Iterations 0–4)
2. **Phase 2 passes** — real capabilities work (Iterations 5–11)
3. **You can load a real dataset, train to convergence, export the model, and
   run inference on it without touching this repo's code.**
4. **The exported model runs in ONNX Runtime / libtorch with matching accuracy.**
5. **Training scales to 2+ GPUs with identical convergence.**
6. **You have throughput/memory numbers to capacity-plan.**
7. **Training survives SIGTERM, OOM, and node failure.**
8. **The Python API has a version contract you can depend on.**

**That's it. No "9/9 green." The green iterations are the means; the eight
bullets above are the end.**

---

## Execution Protocol

```bash
# Phase 1: Validation (GPU required; CPU is a weaker, separately reported pass)
for i in 0 1 2 3 4; do
  echo "=== PHASE 1 ITERATION $i ==="
  uv run python -m pytest "tests/integration/phase1_iter${i}.py" -q --tb=line -p no:xdist || exit 1
done

# Phase 2: Real capabilities (run sequentially; each is independently valuable)
for i in 5 6 7 8 9 10 11; do
  echo "=== PHASE 2 ITERATION $i ==="
  uv run python -m pytest "tests/integration/phase2_iter${i}.py" -q --tb=line -p no:xdist || exit 1
done

echo "SYSTEM USABLE"
```

**On any failure:** Fix the smallest broken layer. Re-run ONLY that iteration's
test file. Do not re-run green iterations.

---

## Test Files Needed (One per Iteration)

| Iteration | Test File | Purpose |
|---|---|---|
| 0 | `tests/integration/phase1_iter0.py` | Env + fixtures + device |
| 1 | `tests/integration/phase1_iter1.py` | Config validation + round-trip |
| 2 | `tests/integration/phase1_iter2.py` | Config→system→train_step on synthetic |
| 3 | `tests/integration/phase1_iter3.py` | ExperimentConfig presets → trainer (10 epochs) |
| 4 | `tests/integration/phase1_iter4.py` | Spec round-trip + determinism + CPU↔GPU |
| 5 | `tests/integration/phase2_iter5.py` | Convergence on MNIST/CIFAR + checkpoint resume |
| 6 | `tests/integration/phase2_iter6.py` | ONNX + TorchScript export |
| 7 | `tests/integration/phase2_iter7.py` | DataLoader for MNIST/CIFAR/ImageFolder/CSV |
| 8 | `tests/integration/phase2_iter8.py` | DDP distributed training |
| 9 | `tests/integration/phase2_iter9.py` | Throughput/memory/latency benchmarks |
| 10 | `tests/integration/phase2_iter10.py` | Logging, metrics, graceful shutdown, OOM recovery |
| 11 | `tests/integration/phase2_iter11.py` | Semver API, deprecation, changelog |

**Create the file before writing the test.** A missing file fails on collection,
not hypothesis — a confusing signal.

---

## What This Plan Does NOT Do

| Not Done | Why |
|---|---|
| LLM / vision / RL full tasks | Separate domain-specific validation |
| Formal verification | Separate Rocq/Coq effort |
| Hardware-specific kernels (Triton/CUDA) | Separate acceleration effort |
| Hyperparameter optimization at scale | Separate Optuna integration |
| AutoML / NAS | Separate product |

---

## Cost Estimate (Measured Where Possible)

| Phase | Estimated Time | Basis |
|---|---|---|
| Phase 1 (0–4) | ~20 min | Measured: old plan's Iteration 1–4 were ~4 min each |
| Iteration 5 | ~30 min | MNIST 100 epochs × 4 rules × 3 seeds ≈ 12 × 90s (R4 ladder) |
| Iteration 6 | ~20 min | Export is fast; validation is the cost |
| Iteration 7 | ~30 min | Loader implementation + 3 dataset tests |
| Iteration 8 | ~45 min | DDP launch + 4 validation slices |
| Iteration 9 | ~20 min | Benchmark runs are fast |
| Iteration 10 | ~30 min | Logging + 4 resilience tests |
| Iteration 11 | ~15 min | Semver + deprecation checks are fast |
| **Total** | **~3 hours** | Can run overnight; each iteration independently valuable |

---

## The Difference From The Old Plan

| Old Plan | This Plan |
|---|---|
| Validation gate | Validation gate (Phase 1) → Capability building (Phase 2) |
| "9/9 iterations green" | "System usable for real problems" (8 concrete bullets) |
| Stops at synthetic smoke | Ships exported model + convergence + export + distributed + benchmarks |
| Excludes convergence | Iteration 5 = convergence with learning curves |
| Excludes export | Iteration 6 = ONNX + TorchScript |
| Excludes data pipelines | Iteration 7 = real data loaders |
| Excludes distributed | Iteration 8 = DDP |
| Excludes benchmarks | Iteration 9 = throughput/memory/latency |
| Excludes monitoring | Iteration 10 = logging, metrics, graceful shutdown |
| Excludes API stability | Iteration 11 = semver, deprecation, changelog |
| Success = "all green" | Success = "you can use it for a real problem" |

---

## Start Here (Fresh Session)

```bash
# 1. Read this file
# 2. Run Iteration 0 (builds fixtures, confirms GPU)
uv run python -m pytest tests/integration/phase1_iter0.py -q --tb=line -p no:xdist

# 2. Run Phase 1 (validation gate)
for i in 1 2 3 4; do
  uv run python -m pytest "tests/integration/phase1_iter${i}.py" -q --tb=line -p no:xdist
done

# 3. Run Phase 2 (real capabilities) — each iteration independently valuable
for i in 5 6 7 8 9 10 11; do
  uv run python -m pytest "tests/integration/phase2_iter${i}.py" -q --tb=line -p no:xdist
done

# When all pass, the system is usable for real problems.
```

---

**No more validation gates. No more "does the wire connect." This plan builds the
thing you can use.**
