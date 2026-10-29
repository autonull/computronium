"""The version is one fact, stated in three places.

`pyproject.toml` is what an installer reads, `computronium.__version__` is what
a running process reports, and the README's status line is what a reader sees.
A release that updates two of them is a release that lies somewhere.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import computronium

ROOT = Path(__file__).resolve().parents[2]


def _pyproject_version() -> str:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        return tomllib.load(handle)["project"]["version"]


def _readme_version() -> str:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    match = re.search(r"\*\*Status:\*\* `v(\d+\.\d+\.\d+)`", text)
    assert match is not None, "README has no status line carrying a version"
    return match.group(1)


def test_declared_versions_agree() -> None:
    assert _pyproject_version() == computronium.__version__ == _readme_version()


def test_repository_url_is_canonical() -> None:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        urls = tomllib.load(handle)["project"]["urls"]
    assert (
        urls["homepage"]
        == urls["repository"]
        == ("https://github.com/autonull/computronium")
    )
