"""Codegen drift lock (WP13 DoD hardening).

The ten JSON artifacts under docs/generated/ are byte-pinned to their
generator functions: regenerating from the seeded registries must produce
identical bytes. Re-pin by running generate_all("docs/generated") after an
intentional registry change; any other drift fails closed here.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from computronium.experiment.schema.seed_registries import seed_all_registries
from computronium.experiment.surface.codegen import (
    generate_axes_listing,
    generate_capabilities_listing,
    generate_cli_flag_tables,
    generate_compatibility_matrix,
    generate_constraints_listing,
    generate_json_schema_validators,
    generate_objectives_listing,
    generate_policies_listing,
    generate_priors_listing,
    generate_stages_listing,
)

GENERATED_DIR = Path(__file__).resolve().parents[2] / "docs" / "generated"

_GENERATORS: dict[str, Any] = {
    "capabilities.json": generate_capabilities_listing,
    "objectives.json": generate_objectives_listing,
    "axes.json": generate_axes_listing,
    "constraints.json": generate_constraints_listing,
    "priors.json": generate_priors_listing,
    "policies.json": generate_policies_listing,
    "stages.json": generate_stages_listing,
    "compatibility_matrix.json": generate_compatibility_matrix,
    "json_schema_validators.json": generate_json_schema_validators,
    "cli_flag_tables.json": generate_cli_flag_tables,
}


def _seeded() -> None:
    seed_all_registries()


class TestCodegenDriftLock:
    def test_all_expected_files_present(self) -> None:
        _seeded()
        assert set(_GENERATORS) == {
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
        }
        for name in _GENERATORS:
            assert (GENERATED_DIR / name).is_file(), name

    def test_regeneration_is_byte_identical(self) -> None:
        _seeded()
        for name, generate in _GENERATORS.items():
            expected = json.dumps(generate(), indent=2).encode()
            committed = (GENERATED_DIR / name).read_bytes()
            assert (
                hashlib.sha256(expected).hexdigest()
                == hashlib.sha256(committed).hexdigest()
            ), f"drift in docs/generated/{name}: re-pin via generate_all"

    def test_generators_deterministic_in_memory(self) -> None:
        _seeded()
        for name, generate in _GENERATORS.items():
            first = json.dumps(generate(), indent=2)
            second = json.dumps(generate(), indent=2)
            assert first == second, name
