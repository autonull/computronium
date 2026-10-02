## Install

```bash
git clone <repository-url> && cd computronium
uv sync --dev --all-extras
```

Requirements: Python 3.14+, [uv](https://docs.astral.sh/uv/). GPU (CUDA/Triton) is optional — the CPU path is fully functional.

Dev-environment smoke (run this before any gate; a stripped env fails here in seconds):

```bash
uv run python -c "import optuna, scipy, torchvision, pytest"
```

---
