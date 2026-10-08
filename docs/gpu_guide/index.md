# GPU Optimization Guide

Mixed precision, multi-GPU, and memory optimization for computronium.

## Overview

Computronium supports multiple GPU optimization strategies:

- **Mixed Precision**: FP16/BF16 training with loss scaling
- **Multi-GPU**: Data parallelism (DDP) and model parallelism
- **Memory Optimization**: Gradient checkpointing, activation offloading
- **Kernel Fusion**: Custom Triton kernels for bio-plausible algorithms

## Mixed Precision Training

### Quick Start

```bash
# Enable FP16 (automatic loss scaling)
uv run comp run backprop --task digits --precision fp16 --device cuda

# Enable BF16 (Ampere+ GPUs)
uv run comp run backprop --task digits --precision bf16 --device cuda

# Verify precision
uv run comp stats --store results.db --metrics precision_mode
```

### How It Works

```python
# Internal implementation
with torch.autocast(device_type='cuda', dtype=torch.float16):
    output = model(input)
    loss = criterion(output, target)

scaler = torch.amp.GradScaler()
scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```

### Precision Comparison

| Precision | Speedup | Memory | Accuracy Drop | Best For |
|-----------|---------|--------|---------------|----------|
| FP32 | 1.0x | 1.0x | 0% | Reference, sensitive models |
| FP16 | 1.5-2.0x | 0.5-0.6x | <0.5% | Most models, older GPUs |
| BF16 | 1.3-1.8x | 0.5-0.6x | <0.3% | Ampere+, large models |

### Troubleshooting Mixed Precision

| Issue | Solution |
|-------|----------|
| NaN loss | Reduce learning rate, check gradient clipping |
| Overflow | Increase loss scale, check for inf gradients |
| Accuracy drop | Use BF16, increase batch size, gradient accumulation |
| Slow convergence | Disable for first N epochs, then enable |

## Multi-GPU Training

### Data Parallelism (DDP)

```bash
# Single node, multi-GPU
uv run comp run backprop --task digits --device cuda --gpus 4

# Multi-node (requires torchrun)
torchrun --nproc_per_node=4 --nnodes=2 \
  -m computronium.experiment.surface.cli run backprop --task digits
```

### Model Parallelism

```bash
# Pipeline parallelism (for large models)
uv run comp run backprop --task imagenet \
  --device cuda --gpus 8 \
  --pipeline-parallel 4
```

### Multi-GPU Configuration

```python
# In RunSpec
spec = RunSpecBuilder() \
  .model("backprop") \
  .task("imagenet") \
  .device("cuda") \
  .gpus(4) \
  .ddp(True) \
  .build()
```

### Scaling Efficiency

| GPUs | Speedup (Ideal) | Speedup (Typical) | Efficiency |
|------|-----------------|-------------------|------------|
| 2 | 2.0x | 1.8-1.9x | 90-95% |
| 4 | 4.0x | 3.4-3.7x | 85-92% |
| 8 | 8.0x | 6.0-7.0x | 75-88% |

## Memory Optimization

### Gradient Checkpointing

```bash
# Enable gradient checkpointing (trades compute for memory)
uv run comp run backprop --task imagenet \
  --device cuda --checkpoint-activations
```

Memory savings: ~40-60% for transformer-like architectures

### Activation Offloading

```bash
# Offload activations to CPU
uv run comp run backprop --task imagenet \
  --device cuda --offload-activations
```

Memory savings: ~70-80%, ~20% slowdown

### Gradient Accumulation

```bash
# Simulate larger batch size
uv run comp run backprop --task imagenet \
  --device cuda --batch-size 32 --grad-accum 4
```

Effective batch size: 128 with memory of 32

### Memory Profiling

```bash
# Profile memory usage
uv run comp run backprop --task digits \
  --device cuda --profile-memory \
  --store mem_profile.db

# View results
uv run comp stats --store mem_profile.db \
  --metrics peak_memory_mb,memory_usage
```

## Kernel Fusion (Triton)

### Custom Kernels

Computronium includes optimized Triton kernels for bio-plausible algorithms:

| Algorithm | Kernel | Speedup vs PyTorch |
|-----------|--------|-------------------|
| FA | `fa_forward`, `fa_backward` | 2-3x |
| Hebbian | `hebbian_update` | 3-5x |
| FF | `ff_goodness` | 2-4x |
| TP | `tp_forward`, `tp_inverse` | 2-3x |
| PC | `pc_inference_step` | 1.5-2x |
| EqProp | `eqprop_settle` | 2-3x |

### Enabling Triton Kernels

```bash
# Auto-enabled for CUDA devices
uv run comp run fa --task digits --device cuda --kernel triton

# Force Triton (default for compatible algorithms)
uv run comp run hebbian --task digits --device cuda --kernel triton

# Disable Triton (use PyTorch fallback)
uv run comp run fa --task digits --device cuda --kernel pytorch
```

### Writing Custom Kernels

```python
# computronium/acceleration/kernels/my_kernel.py
import triton
import triton.language as tl

@triton.jit
def my_kernel(
    input_ptr, output_ptr, weight_ptr,
    M, N, K,
    stride_im, stride_in, stride_wm, stride_wn,
    BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr
):
    # Kernel implementation
    ...
```

## GPU Selection

### Device Selection

```bash
# Specific GPU
uv run comp run backprop --task digits --device cuda:0

# All GPUs
uv run comp run backprop --task digits --device cuda --gpus all

# Exclude GPU
uv run comp run backprop --task digits --device cuda --exclude-gpu 1
```

### GPU Requirements

| Algorithm | Min VRAM | Recommended VRAM | Compute Capability |
|-----------|----------|------------------|-------------------|
| backprop | 4GB | 8GB+ | 7.0+ (Volta) |
| eqprop | 6GB | 12GB+ | 7.0+ |
| fa/hebbian | 4GB | 8GB+ | 7.0+ |
| tp/pc | 8GB | 16GB+ | 8.0+ (Ampere) |

## Benchmarking GPU Performance

```bash
# Run GPU benchmarks
uv run comp benchmark --suite gpu --store gpu_bench.db

# Compare kernels
uv run comp benchmark --suite kernels --store kernel_bench.db

# Profile specific operation
uv run comp run backprop --task digits \
  --device cuda --profile-kernels \
  --store kernel_profile.db
```

### Expected Performance (A100 40GB)

| Model | Batch | FP32 (s/epoch) | FP16 (s/epoch) | BF16 (s/epoch) | Speedup |
|-------|-------|----------------|----------------|----------------|---------|
| backprop (ResNet-50) | 256 | 45 | 28 | 30 | 1.5-1.6x |
| eqprop (MLP-784-512-10) | 128 | 120 | 75 | 80 | 1.5-1.6x |
| fa (MLP-784-512-10) | 128 | 90 | 55 | 60 | 1.5-1.6x |

## Best Practices

1. **Start with FP16** - Best balance of speed/memory/accuracy
2. **Use BF16 on Ampere+** - Better numerical stability
3. **Enable DDP for multi-GPU** - Near-linear scaling
4. **Gradient checkpointing for large models** - Trade compute for memory
5. **Profile before optimizing** - `comp run --profile-memory --profile-kernels`
6. **Pin CUDA version** - Reproducibility requires exact versions

## Troubleshooting

| Problem | Diagnosis | Solution |
|---------|-----------|----------|
| OOM | `torch.cuda.outofmemoryerror` | Reduce batch, enable checkpointing, offload |
| Slow | Low GPU utilization | Increase batch, check DDP, kernel fusion |
| NaN | Mixed precision overflow | Gradient clipping, loss scaling, BF16 |
| Hang | DDP deadlock | Check `find_unused_parameters`, timeout |
| Mismatch | Non-deterministic | `CUBLAS_WORKSPACE_CONFIG=:4096:8`, seed |

## Configuration Reference

```yaml
# GPU config in RunSpec
gpu_config:
  device: "cuda"
  gpus: 4
  precision: "fp16"  # fp32, fp16, bf16
  ddp: true
  checkpoint_activations: false
  offload_activations: false
  grad_accum: 1
  kernel: "triton"  # triton, pytorch
  profile_memory: false
  profile_kernels: false
```

## Next Steps

- [Benchmark Suites](../benchmarks/index.md) - GPU benchmarks
- [Reproducibility](../experiments/reproducibility.md) - Deterministic GPU execution
- [Analysis](../analysis/index.md) - GPU performance analysis