"""Script-default lock: no `scripts/` default may point into a gitignored path.

The third instance of one class, which is why the class is what is locked.
`scripts/visualize_atlas.py` and `scripts/g1_core_sweep.py` both defaulted to
`Path("artifacts/ruler_table.json")`; `artifacts/` is gitignored, so those
defaults resolved only because of a stale local copy left from before the
table moved into the package. A fresh clone has no `artifacts/` at all and both
scripts break there — a failure that cannot be seen in CI, because CI is a
fresh clone.

The rule: a *default* in `scripts/` that names a repository file must name one
git tracks. Output directories are exempt — a script that writes to
`results/<name>` is supposed to create it.

Population assertion, per TODO35 §0: the scan must actually find defaults to
scan, or it is a lock that cannot fail.
"""

from __future__ import annotations

import ast
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ROOT = REPO_ROOT / "scripts"

_MIN_DEFAULTS = 20


def _script_files() -> list[Path]:
    return sorted(p for p in SCRIPTS_ROOT.rglob("*.py") if "__pycache__" not in p.parts)


def _git(*args: str, stdin: str | None = None) -> str:
    return subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
        ["git", *args],
        cwd=REPO_ROOT,
        input=stdin,
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def _tracked_basenames() -> set[str]:
    """Basenames git tracks. `git ls-files`, not rglob: the working tree holds
    ~15M of gitignored output, and a filesystem walk made this lock slower
    than the tests it guards."""
    return {Path(line).name for line in _git("ls-files").splitlines() if line}


def _ignored(literals: set[str]) -> set[str]:
    if not literals:
        return set()
    out = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
        ["git", "check-ignore", "--stdin", "-z"],
        cwd=REPO_ROOT,
        input="\0".join(literals),  # -z on stdin means NUL-separated, not newline
        capture_output=True,
        text=True,
        check=False,
    )
    return {p for p in out.stdout.split("\0") if p}


def _is_path_literal(value: ast.expr) -> bool:
    """`Path("a/b")` with a constant first argument, or anything else."""
    if not isinstance(value, ast.Call) or not isinstance(value.func, ast.Name):
        return False
    if value.func.id != "Path" or not value.args:
        return False
    return isinstance(value.args[0], ast.Constant) and isinstance(
        value.args[0].value, str
    )


def _literal_path_defaults(path: Path) -> list[tuple[int, str]]:
    """Every `Path("a/b")` literal that sits in a default position.

    Both spellings count: a module-level constant (`RULER_TABLE = Path(...)`)
    is read as a default exactly as much as an `add_argument(default=...)` is.
    """
    found: list[tuple[int, str]] = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return found
    for node in ast.walk(tree):
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, (ast.AnnAssign, ast.keyword)):
            targets = [node.target if isinstance(node, ast.AnnAssign) else node.value]
        else:
            continue
        for target in targets:
            value = node.value
            if not _is_path_literal(value):
                continue
            found.append((node.lineno, value.args[0].value))
    return found


def test_population_of_scanned_defaults_is_not_empty() -> None:
    total = sum(len(_literal_path_defaults(p)) for p in _script_files())
    assert total >= _MIN_DEFAULTS, (
        f'only {total} `Path("...")` defaults found under scripts/; the scan '
        "population changed shape and the lock below is now near-vacuous"
    )


def test_no_script_default_shadows_a_tracked_data_file() -> None:
    """A gitignored default whose basename the repo also tracks is a stale copy.

    Scoped to the shadowing class rather than to "any gitignored path" on
    purpose: a script defaulting to `results/foo` or
    `scripts/probes/data/x.json` names a directory the script is meant to
    create, and a lock that flagged those would be a lock that gets switched
    off. Shadowing a file the package ships is the defect — it works on this
    machine and nowhere else, and only the machine's leftover makes it work.
    """
    tracked = _tracked_basenames()
    literals = {
        literal
        for script in _script_files()
        for _, literal in _literal_path_defaults(script)
    }
    ignored = _ignored({lit for lit in literals if Path(lit).name in tracked})
    offenders = [
        f"{script.relative_to(REPO_ROOT)}:{lineno} -> {literal}"
        for script in _script_files()
        for lineno, literal in _literal_path_defaults(script)
        if literal in ignored
    ]
    assert not offenders, f"scripts/ defaults that shadow a tracked file: {offenders}"


def test_the_two_named_sites_use_the_packaged_table() -> None:
    """The specific regression TODO35 §1.7 names, kept by name."""
    for name in ("visualize_atlas.py", "g1_core_sweep.py"):
        text = (SCRIPTS_ROOT / name).read_text(encoding="utf-8")
        assert "artifacts/ruler_table.json" not in text, (
            f"{name} still defaults to the stale copy"
        )
        assert "_ruler_table_path()" in text
