"""The skip scanner reads every reason shape (TODO97 S6d).

A skip whose reason is an f-string or a variable used to evade the gate: the
literal-only scanner saw neither. The audit now reads an f-string's constant
text and reports a reason it cannot read at all. Each case here removes the
mechanism and fails, so the fixture is a lock, not a comment.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.audit import capability_skip

if TYPE_CHECKING:
    from pathlib import Path


def _findings(tmp_path: Path, source: str) -> list[str]:
    (tmp_path / "test_fixture.py").write_text(source, encoding="utf-8")
    return [finding.detail for finding in capability_skip(tmp_path)]


def test_an_fstring_capability_skip_is_a_finding(tmp_path: Path) -> None:
    """A non-literal reason that names no environment is still a skip defect."""
    details = _findings(
        tmp_path,
        "import pytest\n\n"
        "def test_x(name):\n"
        '    pytest.skip(f"{name} has no attachable rung")\n',
    )
    assert len(details) == 1
    assert "has no attachable rung" in details[0]


def test_an_fstring_environment_skip_is_not_a_finding(tmp_path: Path) -> None:
    """An f-string whose constant text names the environment is allowed."""
    details = _findings(
        tmp_path,
        'import pytest\n\ndef test_x(error):\n    pytest.skip(f"no CUDA: {error}")\n',
    )
    assert details == []


def test_a_non_literal_skip_is_a_finding(tmp_path: Path) -> None:
    """A variable reason cannot prove the environment, so it is a finding."""
    details = _findings(
        tmp_path,
        "import pytest\n\n"
        'REASONS = {"x": "not tested"}\n\n'
        "def test_x(name):\n"
        "    pytest.skip(REASONS[name])\n",
    )
    assert len(details) == 1
    assert "non-literal" in details[0]


def test_a_declared_skip_is_not_a_finding(tmp_path: Path) -> None:
    """A row that declares its own state says ``declared:`` literally."""
    details = _findings(
        tmp_path,
        "import pytest\n\n"
        "def test_x(name):\n"
        '    pytest.skip(f"declared: {name} is a no-op contract")\n',
    )
    assert details == []
