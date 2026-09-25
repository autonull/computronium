"""Layering lock: domain code may not import a renderer (TODO34 §4.1).

    domain core (no I/O, no network, no render imports)
       └── presenters (pure: state -> view-model)
               └── renderers (text/rich, static image, notebook, future UI)

The rule this enforces is "no core module may import a renderer". It is the
half that is mechanically checkable, and it is the half that rots: a
correctness invariant that lives in a view module is an invariant nobody looks
for when the invariant breaks.

This lock exists because `broad_map.py` and `campaign_readers.py` both reached
into `visualization/atlas.py` for two things that are not visualization at
all — Pareto front selection, and a cache key whose correctness depends on
SQLite running in WAL mode. Both have since moved to
`computronium/analysis/dominance.py` and `computronium/knowledge/kb_cache.py`.

The other half of §4.1 — "no renderer may contain science" — is not
mechanically checkable and is not attempted here. `analysis/pareto.py` still
imports plotly for its own plotting helpers; that is a known violation of the
spirit of the rule and is tracked in TODO34 §5.2, not fixed by pretending a
regex covers it.

Exemptions are explicit and each carries a reason. Adding to this list is a
design decision, not a lint suppression.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = REPO_ROOT / "computronium"

# Top-level subpackages that *are* the presentation layer. They may import
# each other freely.
PRESENTATION_LAYERS = frozenset({
    "visualization",
    "plotting",
    "rendering",
    "widgets",
    "dashboard",
})
LAYER_DIRS = frozenset(PRESENTATION_LAYERS | {"cli"})

# Import names of rendering libraries that must not be pulled in by
# `import computronium`.
RENDER_MODULES = ("rich", "plotly", "matplotlib", "altair", "bokeh", "dash")

# Distributions §4.1 requires to be managed as optional extras. `rich` is
# deliberately absent: it is currently a *hard* dependency in pyproject.toml,
# but nothing on the import path of `computronium` reaches it (see
# `test_import_computronium_pulls_no_renderer`), so the requirement §4.1
# actually states -- "must not be import-time requirements of
# `import computronium`" -- holds. Moving the declaration to an extra is
# recorded in TODO34 §2.9, not smuggled in here.
EXTRA_MANAGED = ("plotly", "matplotlib")

EXEMPT: dict[str, str] = {
    # The CLI is a consumer, not core: it selects a renderer by name at
    # dispatch time, which is the correct direction of dependency.
    "cli": "entry point; dispatches to renderers, never the reverse",
}


def _module_imports(path: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [(node.lineno, a.name) for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.append((node.lineno, node.module))
    return found


def _relative_to_package(module: str) -> str | None:
    parts = module.split(".")
    if "computronium" not in parts:
        return None
    return ".".join(parts[parts.index("computronium") + 1 :])


def _scan(rel: Path, source: str) -> list[tuple[int, str]]:
    """Renderer imports in one module, or [] if it is itself a layer."""
    if rel.parts and rel.parts[0] in LAYER_DIRS:
        return []
    hits: list[tuple[int, str]] = []
    for lineno, module in _module_imports_from_source(source):
        target = _relative_to_package(module)
        if target and target.split(".")[0] in PRESENTATION_LAYERS:
            hits.append((lineno, module))
    return hits


def _violations() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for path in sorted(PACKAGE_ROOT.rglob("*.py")):
        rel = path.relative_to(PACKAGE_ROOT)
        hits = _scan(rel, path.read_text(encoding="utf-8"))
        if hits:
            out[str(rel)] = [f"{lineno}: {module}" for lineno, module in hits]
    return out


def test_no_core_module_imports_a_renderer() -> None:
    violations = _violations()
    assert violations == {}, (
        "domain code must not import the presentation layer; move the logic to "
        f"analysis/ or knowledge/ and re-point the import: {violations}"
    )


def test_exemptions_still_point_at_real_directories() -> None:
    """An exemption for a path that no longer exists is a stale escape hatch."""
    for name in EXEMPT:
        assert (PACKAGE_ROOT / name).is_dir(), f"exemption {name!r} has no directory"
    assert EXEMPT.keys() <= LAYER_DIRS, "exemption names a non-layer directory"


def test_the_scanner_actually_scans() -> None:
    """Guard the guard: the violation finder must see imports it should catch.

    Without this, a refactor that breaks ``_module_imports`` would leave the
    lock permanently green and nobody would notice.
    """
    fixtures = {
        "domain/uses_renderer.py": "from computronium.visualization.atlas import f\n",
        "domain/uses_renderer_deep.py": "import computronium.visualization.atlas\n",
        "domain/uses_relative.py": "from . import sibling\n",
        "domain/uses_render_dep.py": "import plotly.graph_objects as go\n",
        "visualization/uses_renderer.py": "from computronium.visualization import atlas\n",
        "cli/uses_renderer.py": "from computronium.visualization.gallery import main\n",
    }

    flagged = {name for name, source in fixtures.items() if _scan(Path(name), source)}
    assert flagged == {
        "domain/uses_renderer.py",
        "domain/uses_renderer_deep.py",
    }, f"scanner mis-flagged: {sorted(flagged)}"


def _module_imports_from_source(source: str) -> list[tuple[int, str]]:
    tree = ast.parse(source)
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [(node.lineno, a.name) for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.append((node.lineno, node.module))
    return found


@pytest.mark.parametrize("dep", EXTRA_MANAGED)
def test_render_deps_are_optional_extras(dep: str) -> None:
    """§4.1: plotly and matplotlib are managed as optional extras, not as
    import-time requirements."""
    import tomllib

    project = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]
    assert dep not in project.get("dependencies", []), (
        f"{dep} is a hard dependency of computronium; §4.1 requires an extra"
    )
    extras = project.get("optional-dependencies", {})
    declared = {
        spec.partition(">=")[0].partition("==")[0].strip()
        for name, specs in extras.items()
        if name != "dev"
        for spec in specs
    }
    assert dep in declared, f"{dep} is not declared under any non-dev extra"


def test_import_computronium_pulls_no_renderer() -> None:
    """§4.1's operative claim: importing the package loads no renderer.

    Checked in a subprocess so this module's own imports (and pytest's) cannot
    mask the answer. This is the requirement that actually binds; the
    pyproject test above only covers the two distributions that happen to be
    declared as extras today.
    """
    import subprocess
    import sys

    probe = (
        "import sys, computronium;"
        f"loaded=[m for m in {RENDER_MODULES!r} if m in sys.modules];"
        "print(','.join(loaded))"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "", (
        f"import computronium loaded renderer(s): {result.stdout.strip().split(',')}"
    )
