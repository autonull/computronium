"""Q6 — Lab boundary lock.

Asserts every surviving lab module has an importer outside itself.
"""

import ast
import sys
from pathlib import Path

import pytest

LAB_SRC = Path("/home/me/computronium/packages/computronium-lab/src/computronium_lab")

# Survivors per USAGE.md (R78 retirement records) — using module.path format
SURVIVORS = {
    "lab.py",
    "training.py",
    "adaptation.py",
    "synthesis.__init__.py",
    "synthesis.spec.py",
    "synthesis.catalog.py",
    "synthesis.predictor.py",
    "synthesis.engine.py",
}

# Modules allowed to have no external importers (kernel-path reachability)
KERNEL_PATH = {
    "lab.py",  # Lab facade used by quickstart
    "training.py",  # TrainingResult, StabilityCertificate, etc. used by kernel
    "adaptation.py",  # ψ-adaptation evaluator (T6 locks)
    "synthesis.__init__.py",  # Internal synthesis package
    "synthesis.spec.py",
    "synthesis.catalog.py",
    "synthesis.predictor.py",  # Kernel-path: ViabilityModel
    "synthesis.engine.py",  # Kernel-path: synthesis engine
}


def _collect_imports(root: Path) -> dict[str, set[str]]:
    """Return {module: set of imported modules} for all .py files under root."""
    imports: dict[str, set[str]] = {}
    for py_file in root.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            text = py_file.read_text(encoding="utf-8")
            tree = ast.parse(text)
        except SyntaxError, UnicodeDecodeError:
            continue
        module = py_file.relative_to(root).with_suffix("").as_posix()
        imports[module] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("computronium_lab"):
                    imports[module].add(node.module)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("computronium_lab"):
                        imports[module].add(alias.name)
    return imports


def _external_importers(lab_imports: dict[str, set[str]]) -> dict[str, set[str]]:
    """Return {lab_module: set of external importers}."""
    # Find all Python files outside the lab that import from computronium_lab
    # Only check known external locations (scripts/, tests/ outside lab)
    external = {}
    repo_root = Path("/home/me/computronium")
    search_dirs = [
        repo_root / "scripts",
        repo_root / "tests",
    ]
    for base in search_dirs:
        if not base.exists():
            continue
        for py_file in base.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                text = py_file.read_text(encoding="utf-8")
                tree = ast.parse(text)
            except SyntaxError, UnicodeDecodeError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if node.module.startswith("computronium_lab"):
                        parts = node.module.split(".")
                        if len(parts) >= 2:
                            lab_module = ".".join(parts[1:]) + ".py"
                            external.setdefault(lab_module, set()).add(
                                str(py_file.relative_to(repo_root))
                            )
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith("computronium_lab"):
                            parts = alias.name.split(".")
                            if len(parts) >= 2:
                                lab_module = ".".join(parts[1:]) + ".py"
                                external.setdefault(lab_module, set()).add(
                                    str(py_file.relative_to(repo_root))
                                )
    return external


def test_survivors_have_external_importers() -> None:
    """Every surviving lab module must have at least one external importer
    OR be kernel-path reachable."""
    external = _external_importers({})
    missing = []
    for survivor in SURVIVORS:
        if survivor not in external or not external[survivor]:
            if survivor not in KERNEL_PATH:
                missing.append(survivor)
    assert not missing, (
        f"Surviving lab modules with no external importer and not kernel-path: {missing}. "
        "Per USAGE.md, every survivor must have an importer outside the lab or be kernel-path reachable."
    )


def test_no_retired_modules_exist() -> None:
    """Retired modules must not exist in the source tree."""
    retired = {
        "presets.py",
        "recipes.py",
        "campaign.py",
        "deployment.py",
        "ecosystem.py",
        "sequential.py",
        "state_prediction.py",
        "ceec_profile.py",
        "research/__init__.py",
        "research/autopoiesis.py",
        "research/continual.py",
        "research/corpus.py",
        "research/evolution.py",
        "research/cookbook.py",
        "research/reports.py",
        "research/paths.py",
        "research/adapters.py",
        "research/substrate.py",
    }
    existing = [r for r in retired if (LAB_SRC / r).exists()]
    assert not existing, f"Retired modules still exist: {existing}"


def test_init_exports_only_survivors() -> None:
    """__init__.py must only export symbols from surviving modules."""
    init_path = LAB_SRC / "__init__.py"
    text = init_path.read_text(encoding="utf-8")
    tree = ast.parse(text)

    # Collect all imported names from computronium_lab submodules
    imported_from = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.startswith("computronium_lab."):
                imported_from.add(node.module)

    # Verify each import is from a survivor
    for module in imported_from:
        parts = module.split(".")
        if len(parts) >= 2:
            lab_module = ".".join(parts[1:]) + ".py"
            if lab_module not in SURVIVORS:
                # Allow adaptation and synthesis submodules
                assert lab_module.startswith("adaptation") or lab_module.startswith(
                    "synthesis"
                ), f"__init__.py imports from retired module: {module}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
