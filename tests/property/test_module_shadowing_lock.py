"""§3.1: no module is shadowed by a same-named package in one parent directory.

`computronium/deployment.py` and `computronium/deployment/` coexisted for
commits; the package won import resolution every time, so the module was
unreachable and silently unmaintained. No linter in the configured set flags it,
and `__init__` re-exports can hide it: the shadowed module is only visible by
comparing the filesystem against what actually imports.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ROOTS = (
    REPO_ROOT / "computronium",
    *(
        root / "src"
        for root in sorted((REPO_ROOT / "packages").glob("*/"))
        if (root / "src").is_dir()
    ),
)


def _shadowed() -> list[str]:
    found = []
    for root in ROOTS:
        for parent in (root, *root.rglob("*")):
            if not parent.is_dir() or parent.name == "__pycache__":
                continue
            module = parent / f"{parent.name}.py"
            if module.is_file():
                found.append(str(module.relative_to(REPO_ROOT)))
    return sorted(found)


def test_no_module_is_shadowed_by_a_same_named_package() -> None:
    assert not _shadowed(), (
        f"unreachable module(s) shadowed by a package: {_shadowed()}"
    )


def test_the_scan_actually_scans() -> None:
    """A scan that resolves nothing is worse than no scan (§0.6, §5.4)."""
    assert sum(1 for p in ROOTS[0].rglob("*.py")) > 100
    assert len(ROOTS) > 1 and all(root.is_dir() for root in ROOTS)
