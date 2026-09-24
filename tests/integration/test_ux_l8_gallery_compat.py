"""UX-L8 Gallery Compatibility Test — `comp gallery` artifacts remain renderable.

Regression test ensuring the gallery demo suite continues to work with
the new dashboard components.
"""

from __future__ import annotations

import json
import subprocess  # ruff: ignore[suspicious-subprocess-import] (fixed arg list, no shell)
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FIGURES_DIR = REPO_ROOT / "docs" / "figures"
MANIFEST = FIGURES_DIR / "manifest.json"


def test_manifest_exists() -> None:
    """Manifest file must exist."""
    assert MANIFEST.exists(), f"Gallery manifest not found: {MANIFEST}"


def test_manifest_valid_json() -> None:
    """Manifest must be valid JSON with expected structure."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert "figures" in manifest, "Manifest missing 'figures' key"
    assert isinstance(manifest["figures"], list), "Figures must be a list"
    assert len(manifest["figures"]) > 0, "Manifest has no figures"


def test_manifest_figures_have_required_fields() -> None:
    """Each figure entry must have required fields."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for fig in manifest["figures"]:
        assert "capability_name" in fig, f"Missing capability_name in {fig}"
        assert "data_sha256" in fig, f"Missing data_sha256 in {fig}"
        assert "demo_test" in fig, f"Missing demo_test in {fig}"
        assert "figure_png" in fig, f"Missing figure_png in {fig}"


def test_figure_files_exist() -> None:
    """All figure files referenced in manifest must exist."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for fig in manifest["figures"]:
        fig_path = FIGURES_DIR / fig["figure_png"]
        assert fig_path.exists(), f"Figure file not found: {fig_path}"


def test_gallery_cli_runs() -> None:
    """`comp gallery --run` should execute without error (smoke test).

    This is a quick smoke test - full gallery run is in test_gallery_lock.py
    """
    # Run with --help first to verify CLI loads
    result = subprocess.run(  # noqa: S603 (fixed arg list, no shell)
        ["uv", "run", "comp", "gallery", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO_ROOT,
        check=False,
    )
    assert result.returncode == 0, f"gallery --help failed: {result.stderr}"
    assert "usage" in result.stdout.lower() or "gallery" in result.stdout.lower()


def test_gallery_render_smoke(tmp_path: Path) -> None:
    """Gallery render should produce output without crashing.

    Uses the existing run records to regenerate gallery in a temp dir.
    """
    from computronium.visualization.gallery import render_gallery

    records_dir = FIGURES_DIR / "run_records"
    if not records_dir.exists():
        pytest.skip("No run records directory found")

    metas = render_gallery(records_dir, tmp_path)
    assert len(metas) > 0, "No gallery metadata produced"

    for meta in metas:
        assert meta.capability_name, "Missing capability_name"
        # FigureMeta uses figure_png, not figure_path
        fig_path = tmp_path / meta.figure_png
        assert fig_path.exists(), f"Figure not generated: {fig_path}"
        assert meta.data_sha256, "Missing data_sha256"


def test_dashboard_imports_with_gallery() -> None:
    """Dashboard components should import alongside gallery without conflict."""
    # This tests that the new M3 components don't break gallery imports
    from computronium.ui.components import (
        GenomeHealthTracker,
        MutationExplorer,
        PreviewShelf,
        ProbeAnalytics,
        RegionNaming,
        StagnationDashboard,
        TeamWall,
        VetoLog,
    )
    from computronium.ui.onboarding import ComfortQuiz, GuidedTour
    from computronium.visualization.gallery import DEMOS

    # All imports successful
    assert DEMOS
    assert PreviewShelf
    assert ProbeAnalytics
    assert StagnationDashboard
    assert GenomeHealthTracker
    assert MutationExplorer
    assert VetoLog
    assert RegionNaming
    assert TeamWall
    assert GuidedTour
    assert ComfortQuiz


def test_dashboard_cli_help() -> None:
    """`comp dashboard --help` should work with new flags."""
    result = subprocess.run(  # noqa: S603 (fixed arg list, no shell)
        ["uv", "run", "comp", "dashboard", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO_ROOT,
        check=False,
    )
    assert result.returncode == 0, f"dashboard --help failed: {result.stderr}"
    # Check for new M3 flags
    assert "--ui-mode" in result.stdout
    assert "--ui-actions" in result.stdout
    assert "--quiet" in result.stdout
    # Old flags removed
    assert "--gamify" not in result.stdout
    assert "--rebuild-ui-state" not in result.stdout
