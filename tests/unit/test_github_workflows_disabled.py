"""Lock: GitHub Actions is disabled (TODO107).

GitHub runs only YAML files in ``.github/workflows``. An accidental file
there is a CI job the local release does not gate. The disabled directory
keeps the history; re-enabling is a deliberate move, not a stray save.
"""

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_WORKFLOWS = _ROOT / ".github" / "workflows"


def test_no_github_workflow_is_active() -> None:
    """The active workflow path holds no YAML file."""
    active = sorted(_WORKFLOWS.glob("*.y*ml")) if _WORKFLOWS.exists() else []
    assert not active, f"GitHub Actions is disabled; move these out first: {active}"
