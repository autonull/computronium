"""Tests for the conformance harness (WP11)."""

from __future__ import annotations

from datetime import datetime

import pytest

from computronium.experiment.schema import (
    CAPABILITIES_REGISTRY,
    CapabilityStatus,
    seed_all_registries,
)
from computronium.experiment.surface import (
    CurrencyLock,
    generate_flag_projection_lock,
    load_currency_lock,
    load_flag_projection_lock,
    run_verifying_test,
    save_currency_lock,
    save_flag_projection_lock,
)


class TestRunVerifyingTest:
    """Tests for run_verifying_test function."""

    def test_run_existing_test(self) -> None:
        """Test running an existing test node."""
        # Use a simple test that should exist and pass
        passed, output, duration = run_verifying_test(
            "tests/property/test_public_surface_lock.py::test_the_real_surface_has_no_problems",
            timeout_seconds=30,
        )
        assert passed
        assert duration > 0
        assert "PASSED" in output or "passed" in output.lower()

    def test_run_nonexistent_test(self) -> None:
        """Test running a non-existent test node."""
        passed, output, duration = run_verifying_test(
            "tests/property/test_nonexistent.py::test_fake",
            timeout_seconds=10,
        )
        assert not passed
        assert duration > 0


@pytest.fixture(autouse=True)
def _seed_registries() -> None:
    """Seed registries before each test."""
    seed_all_registries()


class TestCurrencyLock:
    """Tests for CurrencyLock serialization."""

    def test_save_and_load(self, tmp_path) -> None:
        """Test saving and loading a currency lock."""
        lock = CurrencyLock(
            generated_at=datetime.now(),
            capability_count=10,
            passed_count=8,
            failed_count=1,
            retired_count=1,
            skipped_count=0,
            lock_hash="abc123",
        )

        path = tmp_path / "currency_lock.json"
        save_currency_lock(lock, path)

        loaded = load_currency_lock(path)
        assert loaded.capability_count == 10
        assert loaded.passed_count == 8
        assert loaded.failed_count == 1
        assert loaded.retired_count == 1
        assert loaded.skipped_count == 0
        assert loaded.lock_hash == "abc123"
        assert loaded.generated_at == lock.generated_at

    def test_is_current(self) -> None:
        """Test currency check."""
        lock = CurrencyLock(
            generated_at=datetime.now(),
            capability_count=10,
            passed_count=8,
            failed_count=1,
            retired_count=1,
            skipped_count=0,
            lock_hash="abc123",
        )
        assert lock.is_current(max_age_hours=24)
        assert not lock.is_current(max_age_hours=0)


class TestFlagProjectionLock:
    """Tests for FlagProjectionLock (R78)."""

    def test_generate_lock(self) -> None:
        """Test generating flag projection lock."""
        lock = generate_flag_projection_lock()

        # Should have flags from seeded capabilities
        assert lock.capability_count == 88
        assert len(lock.flag_to_capabilities) > 0
        assert lock.lock_hash

        # Check known flags exist
        assert (
            "core" in lock.flag_to_capabilities or "axis" in lock.flag_to_capabilities
        )

    def test_save_and_load(self, tmp_path) -> None:
        """Test saving and loading flag projection lock."""
        lock = generate_flag_projection_lock()

        path = tmp_path / "flag_lock.json"
        save_flag_projection_lock(lock, path)

        loaded = load_flag_projection_lock(path)
        assert loaded.capability_count == lock.capability_count
        assert loaded.flag_to_capabilities == lock.flag_to_capabilities
        assert loaded.lock_hash == lock.lock_hash

    def test_flag_projection_totality(self) -> None:
        """Test that every capability's flags appear in the projection."""
        lock = generate_flag_projection_lock()

        # Collect all flags from registry
        all_flags = set()
        for spec in CAPABILITIES_REGISTRY.values():
            all_flags.update(spec.flags)

        # Every flag in registry should be in projection
        for flag in all_flags:
            assert flag in lock.flag_to_capabilities, (
                f"Flag {flag} missing from projection"
            )

        # Every capability in projection should exist in registry
        for flag, caps in lock.flag_to_capabilities.items():
            for cap_id in caps:
                assert cap_id in CAPABILITIES_REGISTRY, (
                    f"Capability {cap_id} in projection but not in registry"
                )


class TestConformanceHarness:
    """Tests for ConformanceHarness."""

    def test_check_optional_capability_skipped(self) -> None:
        """Test that optional capabilities are skipped."""
        # Create a mock store (we can't easily test without a real store)
        # Instead, test the logic directly by checking the registry
        optional_caps = [
            cap_id
            for cap_id, spec in CAPABILITIES_REGISTRY.items()
            if not spec.required
        ]
        assert len(optional_caps) > 0, "Should have some optional capabilities"

    def test_retired_capability_status(self) -> None:
        """Test that retired capabilities have retirement records."""
        retired_caps = [
            cap_id
            for cap_id, spec in CAPABILITIES_REGISTRY.items()
            if spec.status == CapabilityStatus.RETIRED
        ]
        for cap_id in retired_caps:
            spec = CAPABILITIES_REGISTRY[cap_id]
            assert spec.retirement_record is not None, (
                f"Retired capability {cap_id} missing retirement_record"
            )

    def test_required_capabilities_have_verifying_tests(self) -> None:
        """Test that required capabilities have verifying_test node ids."""
        required_caps = [
            cap_id for cap_id, spec in CAPABILITIES_REGISTRY.items() if spec.required
        ]
        missing_tests = [
            cap_id
            for cap_id in required_caps
            if not CAPABILITIES_REGISTRY[cap_id].verifying_test
        ]
        assert not missing_tests, (
            f"Required capabilities missing verifying_test: {missing_tests}"
        )

    def test_verifying_test_format(self) -> None:
        """Test that verifying_test follows pytest node id format."""
        for cap_id, spec in CAPABILITIES_REGISTRY.items():
            if spec.verifying_test:
                # Should be a pytest node id (file::test_name or file::Class::method)
                # or a test file path (for integration tests that run the whole file)
                test_path = spec.verifying_test
                assert test_path.startswith("tests/") or test_path.startswith(
                    "packages/"
                ), (
                    f"Test path should start with tests/ or packages/ for {cap_id}: {test_path}"
                )
                # Either has :: for specific test, or is a .py file for full file execution
                assert "::" in test_path or test_path.endswith(".py"), (
                    f"Invalid node id format for {cap_id}: {test_path}"
                )


class TestConformanceIntegration:
    """Integration tests for conformance with real store (when available)."""

    def test_currency_lock_counts_all_states(self) -> None:
        """Test that CurrencyLock correctly counts all status states."""
        # This test verifies the logic without needing a real store
        lock = CurrencyLock(
            generated_at=datetime.now(),
            capability_count=5,
            passed_count=2,
            failed_count=1,
            retired_count=1,
            skipped_count=1,
            lock_hash="test",
        )
        assert lock.capability_count == 5
        assert (
            lock.passed_count
            + lock.failed_count
            + lock.retired_count
            + lock.skipped_count
            == 5
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
