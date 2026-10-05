"""Codegen drift locks (split from test_wp11_surface_lock.py for walltime).

These tests exercise the codegen surface and are slow (~100s each).
"""

from pathlib import Path

import pytest

from computronium.experiment.surface.codegen import (
    generate_all,
    generate_capabilities_listing,
)


class TestCodegenDrift:
    @pytest.mark.timeout(600)
    def test_listings_deterministic(self) -> None:
        assert generate_capabilities_listing() == generate_capabilities_listing()

    @pytest.mark.timeout(600)
    def test_generate_all_writes_expected_files(self, tmp_path: Path) -> None:
        summary = generate_all(tmp_path)
        assert summary["capabilities"] == 88
        for name in (
            "capabilities.json",
            "objectives.json",
            "axes.json",
            "constraints.json",
            "priors.json",
            "policies.json",
            "stages.json",
            "compatibility_matrix.json",
            "json_schema_validators.json",
            "cli_flag_tables.json",
        ):
            assert (tmp_path / name).exists(), name
