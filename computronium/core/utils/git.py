"""The current commit SHA — single source of truth for git provenance.

Six copies of ``git rev-parse HEAD`` had accumulated across the model and
dataset registries, the run provenance builders, the microbenchmark, and the
docs generator. They disagreed on the fallback (None against "unknown") and
on the timeout, so a run could report its provenance differently depending on
which registry wrote the record. The one implementation lives here; the
callers choose only the fallback they want.
"""

from __future__ import annotations

import shutil
import subprocess  # ruff: ignore[suspicious-subprocess-import] -- one fixed git call

from computronium.core.logging import get_logger

logger = get_logger()

__all__ = ["git_sha"]


def git_sha(*, timeout: float = 10.0) -> str | None:
    """The current commit SHA, or None when git cannot answer.

    Args:
        timeout: Seconds to wait for git before giving up.

    Returns:
        The commit SHA, or None when git is absent, the working directory is
        not a repository, or git did not answer within ``timeout``.
    """
    try:
        git_path = shutil.which("git")
        if git_path is None:
            return None
        result = subprocess.run(  # ruff: ignore[start-process-with-partial-path, subprocess-without-shell-equals-true]
            [git_path, "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except Exception as exc:
        logger.debug("git SHA unavailable: %s", exc)
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()
