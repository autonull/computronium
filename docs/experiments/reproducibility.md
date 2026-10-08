# Reproducibility

Ensure bitwise-identical results across runs, machines, and time.

## Overview

Computronium provides multiple layers of reproducibility:

1. **Deterministic execution** - Fixed seeds, cuDNN deterministic, CUBLAS config
2. **Environment capture** - Git commit, dependencies, hardware fingerprint
3. **Docker export** - Complete container with pinned versions
4. **Bitwise verification** - Re-run inside container, compare outputs

## Deterministic Execution

All runs are deterministic by default:

```bash
# Automatic deterministic settings
uv run comp run backprop --task digits --seed 42 --device cuda
```

Internally sets:
- `torch.manual_seed(seed)`
- `torch.cuda.manual_seed_all(seed)`
- `torch.backends.cudnn.deterministic = True`
- `torch.backends.cudnn.benchmark = False`
- `CUBLAS_WORKSPACE_CONFIG=:4096:8`
- `PYTHONHASHSEED=seed`

## Environment Capture

Every run captures:

```json
{
  "git_commit": "abc123def...",
  "git_dirty": false,
  "python_version": "3.14.0",
  "torch_version": "2.6.0",
  "cuda_version": "12.6",
  "cudnn_version": "9.4.0",
  "gpu_name": "NVIDIA A100",
  "gpu_driver": "560.35.03",
  "cpu_model": "AMD EPYC 7742",
  "memory_gb": 256,
  "env_fingerprint": "sha256:..."
}
```

## Export for Reproducibility

### JSON Export (Lightweight)

```bash
# Export run configuration and metadata
uv run comp export --store results.db --run-id RUN_ID --format json --output ./repro
```

Output:
```
repro/
├── manifest.json       # Full run specification
├── config.json         # Model/task configuration
├── payload.json        # Measured metrics
├── environment.json    # Environment capture
└── README.md           # Reproduction instructions
```

### Docker Export (Complete)

```bash
# Export complete Docker environment
uv run comp export --store results.db --run-id RUN_ID --format docker --output ./docker_repro
```

Output:
```
docker_repro/
├── Dockerfile          # Pinned base image, dependencies
├── run_repro.sh        # Reproduction script
├── manifest.json       # Run specification
├── environment.json    # Environment capture
└── requirements.txt    # Pinned Python dependencies
```

Dockerfile includes:
- Pinned CUDA/PyTorch base image
- Exact git commit checkout
- `CUBLAS_WORKSPACE_CONFIG=:4096:8`
- `TORCH_DETERMINISTIC=1`
- All dependencies from `uv.lock`

## Reproduce a Run

### Local Reproduction

```bash
# Re-run with same seed (should match bitwise)
uv run comp repro --store results.db --run-id RUN_ID --device cuda
```

### Docker Reproduction

```bash
# Build and run in container
cd docker_repro
docker build -t comp-repro .
docker run --rm --gpus all comp-repro
```

### Verification

```bash
# Verify bitwise match
uv run comp repro --store results.db --run-id RUN_ID --verify

# Compare payloads
uv run comp diff --store results.db --run-id ORIGINAL --run-id REPRODUCED
```

Expected: All metrics match within numerical precision (typically exact match for FP32, <1e-6 for FP16).

## Nightly Regression Testing

CI runs nightly regression tests:

```yaml
# .github/workflows/nightly-benchmarks.yml
# Runs on schedule, compares against baselines
```

- Runs benchmark suites on reference hardware
- Compares against stored baselines
- Fails if metrics drift beyond tolerance
- Generates regression report

## Best Practices

1. **Always use `--store`** - Captures everything in SQLite database
2. **Record seeds** - `--seed 42` ensures reproducibility
3. **Export after important runs** - `comp export --format docker`
4. **Test in CI** - Add reproduction test to your pipeline
5. **Archive Docker images** - `docker save comp-repro > repro.tar`

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Results differ slightly | FP non-associativity | Use FP32, same GPU architecture |
| Results differ significantly | Non-deterministic op | Check for `cudnn.benchmark=True` |
| Docker build fails | Base image unavailable | Pin exact CUDA/PyTorch version |
| GPU not found in container | No `--gpus all` | Run with `docker run --gpus all` |

## Verification Checklist

- [ ] Same seed produces identical results
- [ ] Docker export builds successfully
- [ ] Docker run produces matching metrics
- [ ] Environment capture includes all dependencies
- [ ] Git commit matches source code
- [ ] Nightly CI passes regression tests

## Next Steps

- [Quickstart](../experiments/quickstart.md) - Run your first reproducible experiment
- [GPU Optimization](../gpu_guide/index.md) - Deterministic GPU settings
- [Benchmark Suites](../benchmarks/index.md) - Standardized benchmarks