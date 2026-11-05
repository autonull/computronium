# Compatibility Plan: NumPy, Pandas, CuPy, and CPU Fallback

**Status:** proposal · **Scope:** install graph, CLI startup, device selection, optional
accelerators · **Non-goal:** removing PyTorch (the one mandatory numerical runtime).

This document answers four questions with measurements from the current tree:

1. Can `pandas` be removed?
2. Can `numpy` be removed?
3. Can `CuPy` be made fully optional?
4. What makes the process exit with no message, and how do we guarantee CPU fallback?

---

## 1. Verdict

| Question | Answer | Cost |
|---|---|---|
| Remove `pandas` from the core install | **Yes, safely.** Three shipped call sites, all function-local. The default `text` report does not touch it. | ~30 min |
| Remove `numpy` from the core install | **No, not as a single change.** 55 shipped modules, 589 `np.*` call sites, and three independent transitive paths (`optuna`, `scikit-learn`, `stability`). Removing it is a staged rewrite, not a dependency edit. | 3 stages, multi-week |
| Make `CuPy` fully optional | **Yes.** It is already optional at runtime in 3 of 4 sites; one module-level import and one duplicate probe need hardening. | ~2 h |
| Guarantee CPU fallback | **Mostly present, not guaranteed.** `CUDA_VISIBLE_DEVICES=""` runs the full seven-beat demo to exit 0 on this tree. Explicit `device="cuda"` paths, eager `torch.compile`, and the demo's import gate still fail ungracefully. | ~1 day |
| Diagnose "exits with no message" | **Add `faulthandler` + subprocess capability probes + `COMP_SAFE_MODE`.** A native crash in NumPy/CuPy/torch currently kills the process before any Python handler runs. | ~1 day |

**Recommendation:** ship Phase 0–3 first. They fix the silent exit and the older-GPU
failure without touching numerical code. Defer Phase 4–5 (actual NumPy removal)
until the startup and install surface is clean, because removing NumPy before then
buys no compatibility and costs a large regression surface.

---

## 2. Measured blast radius

Counts are from the current working tree, excluding `.venv`, `.git`, `docs/archive`,
`scripts/`, and `tests/`.

### 2.1 Direct usage

| Dependency | Declared in | Shipped files importing it | `np.*` / `pd.*` call sites | Notes |
|---|---:|---:|---:|---|
| `numpy` | `pyproject.toml:42` | 55 | 589 | 528 in `computronium/`, 40 in `computronium-lab`, 20 in `stability`, 1 in `ceec` |
| `pandas` | `pyproject.toml:55` | 3 | — | `experiment/reporters/html.py`, `experiment/surface/report.py`, `ceec/builders.py`; all function-local |
| `cupy` | extras only (`pyproject.toml:134`, `:165`) | 4 code + 1 detector | — | `acceleration/backends.py`, `kernels.py`, `triton_kernels.py`, `core/utils/activations.py`, `acceleration/status.py` |
| `scikit-learn` | not declared in core | 8 shipped (2 top-level) | — | `axis_attribution.py` and `energy_landscape.py` import at module level |
| `scipy` | `ml`/`dev` extras | 34 | — | mostly function-local |

### 2.2 Transitive hard requirements

`numpy` cannot be removed by editing `pyproject.toml` alone:

| Path | Why it forces NumPy | Is it on the core path? |
|---|---|---|
| `optuna` | `optuna` declares `numpy` as a hard dependency | **Yes** — `experiment/execution/policy.py:19` imports it at module level |
| `scikit-learn` | requires `numpy` and `joblib`; `joblib` imports `numpy` at import | Indirectly — `computronium-lab` is a core dependency and pulls `scikit-learn` |
| `stability` | `stability/guard.py:15` imports `numpy`; `stability/__init__.py` imports `guard` eagerly | **Yes** — `core/utils/activations.py:19` imports `stability.spectral_norm`, which executes the package `__init__` |
| `pandas` | requires `numpy` | Only if `pandas` is installed |
| `scipy` | requires `numpy` | Only in `ml`/`dev` |

**Conclusion:** a NumPy-free core requires optionalizing `optuna`, removing the
`computronium-lab` core dependency, de-eager-ing `stability`, and rewriting the
statistics modules. That is Phase 5. A `pyproject.toml` edit alone is cosmetic.

### 2.3 Eager import chains on `comp <command>`

`import computronium` is genuinely lazy (no NumPy, torch, duckdb, or optuna).
`comp <command>` is not. Four independent paths import NumPy before the command
handler runs:

| # | Trigger | File | Result |
|---|---|---|---|
| 1 | unconditional `import joblib` | `computronium/cli/__main__.py:184` | joblib's `_memmapping_reducer` imports NumPy. Makes `comp --help` fail in any install without joblib. |
| 2 | `import optuna` at module level | `computronium/experiment/execution/policy.py:19` | pulled by `experiment/surface/cli.py:23` |
| 3 | `import sklearn` at module level | `experiment/analysis/axis_attribution.py:13`; `energy_landscape.py:15` | pulled by `surface/cli.py:28` → `surface/report.py:24` → `analysis/__init__.py` |
| 4 | `import numpy` / `stability` | `core/utils/activations.py:17,19` | activations is imported all over the core; `stability.__init__` imports `guard` → NumPy |

Measured simulations (blocking one module through a `MetaPathFinder`):

```
comp --help                    with joblib blocked  -> exit 1 (ImportError at __main__.py:184)
comp run demo --dry-run        with numpy blocked   -> exit 1 (optuna/study.py imports numpy)
comp run demo --dry-run        with sklearn blocked -> exit 1 (via torch.compile import path)
```

### 2.4 Eager `torch.compile`

Two module-level `torch.compile` calls run at import, not at first use:

- `computronium/ontology/_settle_kernel.py:283`
- `computronium/acceleration/pcalm_kernels.py:102`

Importing `computronium.ontology` therefore imports `torch._dynamo` and the Triton
dispatcher. On an older torch/driver this is both slow and a failure point.

### 2.5 Hardware facts

| Fact | Value | Consequence |
|---|---|---|
| Resolved torch | `2.14.1+cu130` from PyPI | Requires a CUDA 13 driver; CUDA 13 drops older GPU architectures |
| CuPy extra | `cupy-cuda13x>=14.1.1` in `spiking`, and `full` includes `spiking` | `uv sync --dev --all-extras` installs a CUDA-13-only CuPy on every machine |
| NumPy CPU baseline | 2.5.3 = `X86_V2` (`SSE4.2`/`POPCNT`); 2.3.2 and 2.3.5 measured at SSE/SSE2/SSE3; the baseline rose in **2.4.0** | NumPy `SIGILL` on a pre-Nehalem CPU is fixed by pinning to 2.3.5; `AVX2` remains runtime-dispatched, so modern CPUs lose little |
| NumPy cp314 wheel window | Oldest cp314 wheel = `2.3.2`; last pre-v2 release = `2.3.5` | The pin must land in `>=2.3.3,<2.4` (pandas 3.0.6 on py3.14 already requires `>=2.3.3`) |
| CPU-only demo | `CUDA_VISIBLE_DEVICES="" uv run comp demo` → **exit 0** | The training and evidence path already works without a GPU |

The last row is the important one: the CPU fallback is functional. The remaining
work is making the *entry* and *optional-accelerator* paths fail soft.

---

## 3. The silent exit

A Python `except ImportError` cannot catch a `SIGILL`/`SIGSEGV` raised inside a
native extension. The process dies with `$?` 132/139 and no traceback. The same is
true for a driver-level crash in CuPy/torch. Three defenses are needed:

1. **`faulthandler.enable()`** at the top of `comp` so a native crash prints the
   Python stack and signal name.
2. **Subprocess probes** for optional native dependencies: probe in a child
   process, so a crash is data (`returncode != 0`), not a dead parent.
3. **A safe mode** (`COMP_SAFE_MODE=1`) that forces CPU, disables CuPy/Triton/
   `torch.compile`, and reports the reduced capability set.

---

## 4. Plan

### Phase 0 — Make the failure visible (P0, ~2 h)

**Goal:** every failure produces a message and an exit code.

1. `computronium/cli/__main__.py`
   - Add `import faulthandler; faulthandler.enable()` before dispatch.
   - Install a `sys.excepthook` that prints the exception and a one-line hint.
   - Wrap dispatch in a top-level handler that prints `command` and exits non-zero.
2. Add `computronium/core/compat.py` with:
   - `probe_module(name) -> ProbeResult` — runs `python -c "import <name>"` in a
     subprocess with a timeout, captures `returncode`/`stderr`, maps known signals
     to plain English (`-4` → `SIGILL`, `-11` → `SIGSEGV`, `-9` → `SIGKILL/OOM`).
   - `probe_cuda() -> ProbeResult` — subprocess that imports torch, checks
     `torch.cuda.is_available()`, allocates a tensor, runs one matmul, synchronizes.
   - `probe_cupy() -> ProbeResult` — same, with a real allocation.
   - Results are cached per process in a frozen dataclass.
3. Expose `comp doctor`:
   - Reuse `experiment/environment/diagnostics.py` but run each check through
     `probe_module`/`probe_cuda` so a native crash is reported, not fatal.
   - Print Python, platform, CPU feature flags (`numpy._core._multiarray_umath.__cpu_features__`),
     torch version + CUDA version + driver, CuPy status, NumPy status, and the
     selected device.
   - Exit non-zero only when a *required* capability is missing.

**Acceptance:** `comp doctor` on a machine where `import numpy` dies returns 0
with a `SIGILL` row and a remediation line, not a dead process.

### Phase 1 — De-eager the startup path (P0, ~4 h)

**Goal:** `comp --help` and `comp <command> --help` never import NumPy, sklearn,
optuna, joblib, CuPy, or torch.

1. `computronium/cli/__main__.py:184`
   - Remove the unconditional `import joblib`.
   - Set the backend only when joblib is importable:
     ```python
     try:
         import joblib
         joblib.parallel.DEFAULT_BACKEND = "threading"
     except Exception:
         pass
     ```
     Do this once, in a helper, and do not import sklearn.
2. `computronium/experiment/surface/cli.py`
   - Replace the top-level `from ._cli._analysis import ...`, `._campaign`,
     `._commands`, `._execution`, `._registry`, and `execution.policy` imports
     with a command → loader table. Import only the module that serves the
     selected command.
   - Each `_cmd_*` handler already does lazy imports internally; keep that.
3. `computronium/experiment/analysis/__init__.py`
   - Convert the eager re-export block to PEP 562 `__getattr__` over a name →
     module map. This alone stops `surface/report.py` from importing sklearn.
4. `computronium/experiment/analysis/axis_attribution.py:13` and
   `energy_landscape.py:15`
   - Move `sklearn` imports inside the functions that use them. Raise a clear
     `ImportError` naming the `ml` extra when selected.
5. `computronium/experiment/execution/policy.py:19-25`
   - Move `optuna` imports into `ModelBasedPolicy` methods (or a small
     `_optuna()` accessor) and keep the types under `TYPE_CHECKING`.
   - Keep `POLICY_CATALOG` importable without optuna; only *constructing*
     `ModelBasedPolicy` should require it.
6. `computronium/core/utils/activations.py:17,19`
   - Move `import numpy` into the four functions that need it.
   - Import `stability.spectral_norm` lazily, or change
     `stability/__init__.py` to PEP 562 lazy exports so `import
     stability.spectral_norm` does not execute `guard`.
7. `computronium/ontology/_settle_kernel.py:283` and
   `computronium/acceleration/pcalm_kernels.py:102`
   - Replace module-level `torch.compile(...)` with a guarded lazy wrapper:
     compile on first call; return the eager function when
     `COMP_SAFE_MODE=1`, `TORCHDYNAMO_DISABLE=1`, or compilation fails.
8. `computronium/experiment/surface/_cli/_demo.py:85-92`
   - Beat 0 must probe `optuna`, `scipy`, `torchvision`, `duckdb`, not import them
     as a hard gate. Missing optional packages become warnings; only torch/duckdb
     are required.

**Acceptance:**

```bash
# All of these must exit 0 without loading numpy/sklearn/optuna/cupy:
uv run comp --help
uv run comp run --help
uv run comp status --help
# And the full CPU demo still runs:
CUDA_VISIBLE_DEVICES="" uv run comp demo --store /tmp/demo.duckdb
```

Add a property test that imports `computronium.cli.__main__` and asserts
`{"numpy","pandas","cupy","sklearn","optuna","joblib"} & sys.modules == set()`.

### Phase 2 — Remove pandas from core (P1, ~30 min)

1. Delete `pandas>=3.0.5` from `[project.dependencies]` (`pyproject.toml:55`).
2. Add `pandas` to the `ml` extra (already there) and to a new `report` extra if
   Parquet/HTML export should be installable alone.
3. Keep the three function-local imports; improve the error text in
   `experiment/surface/report.py:1598` and `experiment/reporters/html.py` to name
   the extra: `uv sync --extra ml`.
4. `experiment/reporters/html.py:578` already requires pandas for every HTML
   report; document that `--format html` needs the extra.

**Blast radius:** 3 files, no numerical code. Default `text`/`json` reports and
the evidence store are unaffected.

### Phase 3 — Make CuPy and GPU fully optional (P1, ~2 h)

1. `computronium/acceleration/backends.py`
   - Delete the duplicate module-level `import cupy` at line 18; keep one guarded
     probe at line ~388.
   - Catch `Exception` (not just `ImportError`) around the probe, because a
     driver/library mismatch can raise `OSError`, `RuntimeError`, `CUDARuntimeError`,
     or `SystemError`.
   - Never call `cp.cuda.is_available()` unless the import succeeded.
   - Export a single `get_cupy() -> tuple[object | None, bool]` used by every
     CuPy consumer.
2. `computronium/acceleration/kernels.py:170`
   - Reuse `get_cupy()`; keep the real allocation check.
3. `computronium/acceleration/triton_kernels.py:137,297`
   - Replace the inline `import cupy` with `get_cupy()` so the fallback is
     identical everywhere.
4. `computronium/core/utils/activations.py:152-162`
   - Reuse `get_cupy()`; remove the duplicated try/except.
5. Device resolution — one helper:
   - `core/utils/device.py:get_device` already falls back for explicit `cuda`.
   - Make `SystemTrainer._setup_device` (`core/system_trainer/trainer.py:200`),
     `experiment/kernel/_trainer_utils.py:18`, and
     `experiment/surface/_cli/_analysis.py:24` call `get_device` instead of their
     own `"cuda" if is_available() else "cpu"`.
   - Honor `COMP_DEVICE=cpu|cuda|auto` before the hint.
   - Emit one `logger.warning` when an explicit CUDA request degrades to CPU.
6. `computronium/utils.py:52`
   - Keep the hard error in `seed_everything(device="cuda")` (silent fallback
     would break the bitwise guarantee), but catch it at the CLI boundary and
     retry on CPU when `--device auto`.
7. `computronium/nn/module.py:301`
   - Replace `self.to(device or torch.device("cuda"))` with `get_device(device)`.
8. `computronium/config/experiment.py:404`
   - Change the `_base_hardware()` preset default from `"cuda"` to `"auto"`.
9. Install profiles:
   - Move `cupy-cuda13x` out of `spiking` (or rename the extra) and out of `full`.
     Add:
     - `gpu-cu13 = ["cupy-cuda13x>=14.1.1"]`
     - `gpu-cu12 = ["cupy-cuda12x>=13"]`
   - `full` should not silently install a driver-specific wheel.

**Acceptance:**

```bash
CUDA_VISIBLE_DEVICES="" uv run python -c "from computronium.acceleration.backends import HAS_CUPY; print(HAS_CUPY)"  # False, exit 0
uv run python -c "import computronium.acceleration.backends"  # no crash with a broken CuPy
uv run python -m pytest tests/property -k "device or backend" -q
```

### Phase 3a — Pin NumPy to the last pre-X86_V2 release (P0 for pre-Nehalem CPUs, ~10 min)

**Goal:** remove NumPy's `X86_V2` baseline from the install without changing the
`comp` path. This is the smallest change that lets a pre-Nehalem CPU run the stack.

**Evidence:** NumPy's own build config reports `baseline: X86_V2` for 2.5.3 and
`baseline: SSE/SSE2/SSE3` for 2.3.2 and 2.3.5; 2.4.0 is the first release with the
`X86_V2` baseline. The oldest cp314 wheel is 2.3.2, so the safe window is
2.3.2–2.3.5.

**Change:**
- `pyproject.toml`: `"numpy"` → `"numpy>=2.3.3,<2.4"` (pandas 3.0.6 on Python
  3.14 already requires `numpy>=2.3.3`; the upper bound excludes 2.4.0).
- Re-lock: `uv lock`.
- Verify on the target: `grep -o 'sse4_2\|popcnt' /proc/cpuinfo | sort -u`.
  If both flags are present, NumPy 2.5 was not the crash; do not pin.

**Why the pin resolves:** every transitive NumPy constraint in the current lock
accepts 2.3.5 — `numba<2.6`, `cupy-cuda13x<2.6`, `scipy<2.8`, `pandas>=2.3.3`
(py3.14), `ml_dtypes>=2.3.0` (py3.14), `torchmetrics[dev]<2.4.0`.

**Measured consequences** (this machine, 2.5.3 vs 2.3.5):
- matmul 1200²: 0.0214 s → 0.0222 s; sort 3M: 0.0498 s → 0.0501 s; sum/std/
  randn/fft within noise; `np.unique` 2M measured *faster* on 2.3.5.
- Import check: numpy/scipy/pandas/torch/sklearn all import and run basic ops
  against 2.3.5.

**Risks:**
- Wheels built against 2.4/2.5 headers run on 2.3.5 only by ABI tolerance; the
  import test passed, but run the targeted test tier before trusting it.
- No 2.4/2.5 bug or security fixes while the pin stands.
- Future `pandas`/`scipy` releases may raise the floor above 2.3.5; the pin is a
  shim, not a permanent state.
- The pin fixes NumPy's baseline only. If `torch`'s wheel has its own AVX/AVX2
  baseline, or the crash is the CUDA-13 driver, NumPy 2.3.5 will not help.

### Phase 4 — NumPy de-eager and optionality (P2, ~2 days)

**Goal:** NumPy is imported only by the modules that compute with it. This is the
prerequisite for Phase 5 and already delivers most of the compatibility win.

1. Move every top-level `import numpy` in the 55 files behind a function or a
   module-level `TYPE_CHECKING` import. Prioritize the modules reachable from
   `comp`:
   - `experiment/evidence/statistics.py`, `experiment/evidence/significance.py`
   - `experiment/execution/statistical_promotion.py`
   - `experiment/learning/{benchmark,icu,surrogate}.py`
   - `experiment/registry/{loop,seed}.py`
   - `validation/{analysis,notebook,preregistration,statistics,tracks/core_tracks,utils,verifier}.py`
   - `core/statistics.py`, `core/_caching.py`, `core/utils/{seeds,activations}.py`
   - `benchmarks/rigorous.py`
2. Convert the data-synthesis modules to torch tensors so the `torch.from_numpy`
   round-trips disappear:
   - `domains/{scientific,tabular,timeseries}.py`
   - `domains/{vision,rl,lm}.py` (metrics only)
3. `packages/stability/src/stability/guard.py`
   - Convert the 15 `np.*` calls to `torch` (calibration arrays can be Python
     lists or float64 tensors).
4. `packages/computronium-lab/.../synthesis/predictor.py`
   - Either convert to torch or make sklearn an extra. Do not keep sklearn in the
     base graph.
5. `packages/ceec-core/.../builders.py`
   - The single NumPy use is already local; keep it optional.
6. `computronium/acceleration/kernels.py`
   - Keep the standalone NumPy/CuPy EqProp kernel as an optional backend
     (`COMP_KERNEL_BACKEND=python`), or convert it to torch. It is not on the
     default training path.
7. `pyproject.toml`
   - Move `optuna` from core to `search` (already listed there) and make
     `ModelBasedPolicy` raise a clear "install the search extra" error.
   - Remove `computronium-lab` from core; add a `lab` extra. It is not imported by
     the core library.
   - Then NumPy becomes a dependency of `search`/`ml`/`lab`/`stability`, not core.

**Acceptance:** `uv sync --no-extra search --no-extra ml --no-extra lab` installs
without NumPy, and `comp run demo` (non-`model_based`) still runs.

### Phase 5 — Actual NumPy removal (P3, optional, ~1–2 weeks)

Only if a NumPy-free install is a hard requirement. Requires preserving statistical
results, so it is a numerical change, not a dependency change.

1. Rewrite `core/statistics.py`, `validation/statistics.py`,
   `experiment/evidence/statistics.py`, `experiment/evidence/significance.py` on
   torch or the standard library.
   - Bootstrap/permutation RNG must be re-pinned and the existing golden tests
     re-baselined; the current NumPy `default_rng` stream will not match.
2. Rewrite `experiment/analysis/*` on torch (most already use torch for tensors;
   only the small-array statistics use NumPy).
3. Remove the `numpy` import from `computronium/core/utils/activations.py` by
   splitting `to_numpy`/`softmax`/`cross_entropy` into a NumPy-compatible module
   that is imported only by the acceleration backends.
4. Delete the `numpy` declaration only after `pip install --no-deps` +
   `comp demo` passes in CI.

**Risk:** statistical reproducibility and the property locks that compare exact
values. Do not start Phase 5 before Phase 4 is green.

---

## 5. Install matrix after the plan

| Profile | Adds | NumPy? | CUDA? | Use |
|---|---|---:|---:|---|
| `core` | torch, duckdb, pydantic, omegaconf, pyyaml, tqdm | yes (until Phase 5) | no (CPU wheel) | CPU-only lab |
| `search` | optuna, tabulate | yes | no | model-based policy |
| `ml` | scikit-learn, pandas, scipy | yes | no | analysis/reporting |
| `lab` | computronium-lab | yes | no | high-level Lab API |
| `vision` | torchvision | yes | no | vision datasets |
| `gpu-cu12` | `cupy-cuda12x`, `nvidia-ml-py` | yes | CUDA 12 driver | older NVIDIA GPUs |
| `gpu-cu13` | `cupy-cuda13x`, `nvidia-ml-py` | yes | CUDA 13 driver | current NVIDIA GPUs |
| `full` | union **without** a CUDA-specific CuPy | yes | no | development |

### CPU-only torch install

The lock resolves torch from PyPI as `2.14.1+cu130`. On a machine whose driver is
older than CUDA 13, install the CPU wheel explicitly:

```bash
# Preferred: a uv release that supports the torch backend selector
UV_TORCH_BACKEND=cpu uv sync --dev --all-extras

# Current uv 0.5.13 fallback (no --torch-backend flag)
uv sync --dev --no-install-package torch
uv pip install torch --index-url https://download.pytorch.org/whl/cpu
```

Verify:

```bash
uv run python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
# expected: 2.x.x+cpu False
```

---

## 6. Acceptance gates

Run these on the target older machine, in order. Each must exit 0.

```bash
# 1. Environment truth, crash-safe
uv run comp doctor

# 2. CPU-only, no GPU visible
CUDA_VISIBLE_DEVICES="" uv run comp --help
CUDA_VISIBLE_DEVICES="" uv run comp run demo --dry-run
CUDA_VISIBLE_DEVICES="" uv run comp demo --store /tmp/demo.duckdb

# 3. No eager optional imports
uv run python -c "import sys, computronium.cli.__main__ as m; bad={'numpy','pandas','cupy','sklearn','optuna','joblib'} & set(sys.modules); assert not bad, bad"

# 4. Broken CuPy is non-fatal
uv run python -c "import computronium.acceleration.backends as b; print('HAS_CUPY', b.HAS_CUPY)"

# 5. Targeted tests
uv run python -m pytest tests/property/test_kernel_isolation_lock.py \
    tests/property/test_full_import_isolation_lock.py \
    tests/property/test_cli_readme_lock.py -q
```

---

## 7. Risk register

| Risk | Mitigation |
|---|---|
| Removing NumPy changes bootstrap/permutation results | Defer Phase 5; re-baseline only the affected locks with a recorded correction |
| Lazy imports change public API timing | Keep names importable; add an import-surface test |
| `comp --help` loses subcommands after de-eager | The dispatcher table is data; add a lock comparing `--help` output to `_SUBCOMMANDS` |
| CPU fallback hides a real GPU bug | Log a single warning with the probe failure; never fall back silently in `seed_everything` |
| Driver-specific CuPy in `full` breaks installs | Remove it from `full`; require an explicit `gpu-cu12`/`gpu-cu13` extra |
| `torch.compile` at import still crashes old torch | Guard with `COMP_SAFE_MODE` and `TORCHDYNAMO_DISABLE`; compile lazily |

---

## 8. Decision summary

- **Do now:** Phase 0–3. They are surgical, testable, and solve the reported
  "older GPU / silent exit" problem.
- **Do first on the legacy machine:** Phase 3a — pin `numpy>=2.3.3,<2.4`. It is a
  one-line change, resolves cleanly against the current lock, and costs no
  measurable throughput on this machine. Confirm the CPU lacks `sse4_2`/`popcnt`
  first; if it has them, NumPy 2.5 was not the culprit and the pin is unnecessary.
- **Do next:** Phase 4. It removes NumPy from the startup path and makes the
  dependency graph honest, without changing numerical results.
- **Do only on demand:** Phase 5. A NumPy-free install is a numerical migration,
  not a packaging change.
- **Do not:** delete `numpy` from `pyproject.toml` while `optuna`, `scikit-learn`,
  and `stability` still require it. That hides the dependency without removing it.
