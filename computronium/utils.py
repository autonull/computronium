"""
Computronium Utilities

Helper functions for reproducibility and training utilities.
"""

import os
import random
import subprocess
import sys

import numpy as np
import torch
from torch import nn

from computronium.core.logging import get_logger

logger = get_logger()


def seed_everything(
    seed: int = 42, device: str = "cpu", deterministic: bool = False
) -> dict[str, str]:
    """
    Seed all random number generators for reproducibility.

    Single consolidated seeding API: seeds Python's ``random``, NumPy,
    PyTorch (CPU), and — when ``device`` is ``cuda``/``gpu`` and CUDA is
    present — the CUDA generator(s) plus cuDNN deterministic/benchmark flags.
    Also captures the environment fingerprint so a ``biopl-repro-check`` run can
    prove two runs are bitwise identical.

    Args:
        seed: Random seed (default: 42).
        device: ``"cpu"`` (default), ``"cuda"``/``"gpu"`` (also seeds CUDA +
            cuDNN, and refuses to pretend determinism without CUDA).
        deterministic: When ``True``, also enables
            ``torch.use_deterministic_algorithms`` (CPU) and the cuDNN
            deterministic mode (CUDA). Use only when bit-exact reproducibility
            is required — it can slow or fail some non-deterministic ops.

    Returns:
        Environment fingerprint dict (see :func:`capture_environment`).

    Raises:
        RuntimeError: If ``device`` asks for CUDA seeding but CUDA is
            unavailable — a silent CPU fallback would silently defeat the
            bitwise-identical guarantee the caller is relying on.
    """
    want_cuda = device in ("cuda", "gpu") or device.startswith("cuda:")  # ruff: ignore[literal-membership]
    if want_cuda and not torch.cuda.is_available():
        raise RuntimeError(f"seed_everything device={device!r} but CUDA is unavailable")

    if deterministic:
        torch.use_deterministic_algorithms(True)

    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if want_cuda:
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    return capture_environment()


def capture_environment() -> dict[str, str]:
    """Capture a compact, hashable fingerprint of the execution environment.

    Returns a dict that stays stable within a machine/commit so the same-input
    guarantee can be asserted across two identical runs. Keys: ``git_commit``,
    ``torch_version``, ``cuda_version`` (or ``"n/a"``), ``python_version``.
    """
    git_commit = "unknown"
    try:
        git_commit = (
            subprocess
            .check_output(["git", "rev-parse", "HEAD"])  # ruff: ignore[start-process-with-partial-path]
            .decode("ascii")
            .strip()
        )
    except OSError, subprocess.CalledProcessError:
        pass

    return {
        "git_commit": git_commit,
        "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda if torch.version.cuda else "n/a",
        "python_version": (
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        ),
    }


def count_parameters(model: nn.Module, trainable_only: bool = True) -> int:
    """
    Count the number of parameters in a model.

    Args:
        model: PyTorch model
        trainable_only: If True, only count trainable parameters

    Returns:
        Number of parameters
    """
    if trainable_only:
        return sum(p.numel() for p in model.parameters() if p.requires_grad)
    return sum(p.numel() for p in model.parameters())


def deps_hash(environment: dict[str, str] | None = None) -> str:
    """Return a short digest of :func:`capture_environment` for rollup reporting."""
    import hashlib

    env = environment if environment is not None else capture_environment()
    canonical = "|".join(f"{k}={env[k]}" for k in sorted(env))
    return hashlib.sha256(canonical.encode()).hexdigest()[:12]
