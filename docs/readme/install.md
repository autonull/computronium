## Install

```bash
git clone https://github.com/autonull/computronium && cd computronium
uv sync --dev --all-extras
```

Requirements: Python **3.14+** (PEP 695 generics, `TypeIs`, free-threaded-CPython
readiness), [uv](https://docs.astral.sh/uv/). The base install (`core`) carries
training and the experiment kernel; every other capability is an extra, so an
install pulls only what it uses.

| Profile | Install | Adds |
|---------|---------|------|
| `core` | `uv sync` | Training, ontology, experiment kernel (torch, duckdb, optuna, pydantic) |
| `search` | `uv sync --extra search` | Campaign search and tabular reporting |
| `vision` | `uv sync --extra vision` | torchvision datasets and transforms |
| `gpu` | `uv sync --extra gpu` | NVIDIA telemetry (`nvidia-ml-py`) |
| `dashboard` | `uv sync --extra dashboard` | FastAPI/uvicorn live dashboard (with `rich`) |

Optional heavy dependencies are imported lazily: `torchvision` is only touched
when a vision dataset or transform is requested, the dashboard stack when the
dashboard is launched. Combining profiles works as expected, e.g.
`uv sync --extra vision --extra dashboard`; `--all-extras` is the development
union.

GPU (CUDA/Triton) is optional — the CPU path is fully functional.

Dev-environment smoke (run this before any gate; a stripped env fails here in seconds):

```bash
uv run python -c "import optuna, scipy, torchvision, pytest"
```

