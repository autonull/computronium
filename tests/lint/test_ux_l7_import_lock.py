"""UX-L7: Integrity lock — projector has zero imports from campaign/gate mutation paths.

This test ensures the recognition projector (and recognition package) does not
import from campaign execution, gate mutation, or other write-path modules.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

# Forbidden import patterns — these are campaign/gate mutation paths
FORBIDDEN_IMPORTS = {
    # Campaign execution
    "computronium.autoscientist.campaign",
    "computronium.autoscientist.driver",
    "computronium.autoscientist.proposer",
    "computronium.autoscientist.budget",
    "computronium.autoscientist.scheduler",
    # Gate mutation / promotion
    "computronium.autoscientist.gates",
    "computronium.autoscientist.promotion",
    "computronium.autoscientist.mutation",
    "computronium.autoscientist.crossover",
    # Cell execution / training
    "computronium.core.trainer",
    "computronium.core.system_trainer",
    "computronium.training",
    # CEEC write paths (only read is allowed)
    "computronium.ceec.builders",
    "computronium.ceec.run",
    # KB write paths
    "computronium.autoscientist.broad_map",
    # Daemon/continuous (execution control)
    "computronium.daemon",
    "computronium.continuous",
    # Stability guard (mutation path)
    "computronium.stability",
    "stability",
}


# Allowed imports from autoscientist (read-only)
ALLOWED_AUTOSCIENTIST = {
    "computronium.autoscientist.objectives",
    "computronium.autoscientist.defects",
    "computronium.autoscientist.broad_map",  # for reading KB only
}


def _collect_imports(file_path: Path) -> set[str]:
    """Collect all imported module names from a Python file."""
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
            imports.add(node.module)

    return imports


def _check_file_imports(file_path: Path) -> list[str]:
    """Check a file for forbidden imports. Returns list of violations."""
    imports = _collect_imports(file_path)
    violations = []

    for imp in imports:
        # Check if import starts with any forbidden pattern
        for forbidden in FORBIDDEN_IMPORTS:
            if imp == forbidden or imp.startswith(forbidden + "."):
                # Check if it's in allowed list
                allowed = False
                for allowed_pattern in ALLOWED_AUTOSCIENTIST:
                    if imp == allowed_pattern or imp.startswith(allowed_pattern + "."):
                        allowed = True
                        break
                if not allowed:
                    violations.append(
                        f"{file_path}: imports '{imp}' (forbidden: '{forbidden}')"
                    )

    return violations


class TestUXL7ImportLock:
    """UX-L7: Recognition projector must not import from campaign/gate mutation paths."""

    def test_recognition_package_imports(self) -> None:
        """Check all files in recognition package for forbidden imports."""
        recognition_root = Path("computronium/ui/recognition")
        all_violations = []

        for py_file in recognition_root.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue
            violations = _check_file_imports(py_file)
            all_violations.extend(violations)

        assert not all_violations, (
            "UX-L7 violations in recognition package:\n" + "\n".join(all_violations)
        )

    def test_recognition_projector_no_campaign_imports(self) -> None:
        """Specifically check the projector module."""
        projector_path = Path("computronium/ui/recognition/projector.py")
        violations = _check_file_imports(projector_path)
        assert not violations, "UX-L7 violations in projector:\n" + "\n".join(
            violations
        )

    def test_recognition_no_stability_imports(self) -> None:
        """Recognition must not import stability (which is a guard/mutation path)."""
        recognition_root = Path("computronium/ui/recognition")

        for py_file in recognition_root.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == "stability" or alias.name.startswith(
                            "stability."
                        ):
                            pytest.fail(f"{py_file}: imports 'stability' (forbidden)")
                elif isinstance(node, ast.ImportFrom) and node.module and (
                    node.module == "stability" or node.module.startswith("stability.")
                ):
                    pytest.fail(f"{py_file}: imports from 'stability' (forbidden)")

    def test_components_progress_panel_imports(self) -> None:
        """Check progress panel doesn't import forbidden modules."""
        panel_path = Path("computronium/ui/components/progress_panel.py")
        if panel_path.exists():
            violations = _check_file_imports(panel_path)
            # Progress panel may import recognition, which is allowed
            # Filter out recognition imports
            filtered = [v for v in violations if "recognition" not in v]
            assert not filtered, "UX-L7 violations in progress_panel:\n" + "\n".join(
                filtered
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
