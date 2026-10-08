"""Test wrappers for t51 probe scripts.

These tests run the probe scripts as smoke tests to ensure they execute
without error. They are marked as slow/probe tests and excluded from the
default test gate.
"""

import pytest


@pytest.mark.slow
@pytest.mark.probe
@pytest.mark.timeout(120)
def test_t51_stability_operator_probe():
    """Smoke test: t51_stability_operator_probe runs without error."""
    from scripts.probes.t51_stability_operator_probe import main

    main()


@pytest.mark.slow
@pytest.mark.probe
@pytest.mark.timeout(120)
def test_t51_energy_model_probe():
    """Smoke test: t51_energy_model_probe runs without error."""
    from scripts.probes.t51_energy_model_probe import main

    main()


@pytest.mark.slow
@pytest.mark.probe
@pytest.mark.timeout(300)
def test_t51_learning_signal_probe():
    """Smoke test: t51_learning_signal_probe runs without error."""
    from scripts.probes.t51_learning_signal_probe import main

    main()


@pytest.mark.slow
@pytest.mark.probe
@pytest.mark.timeout(120)
def test_t51_metric_coverage_probe():
    """Smoke test: t51_metric_coverage_probe runs without error."""
    from scripts.probes.t51_metric_coverage_probe import main

    main()


@pytest.mark.slow
@pytest.mark.probe
@pytest.mark.timeout(120)
def test_t51_nonnormality_verification_probe():
    """Smoke test: t51_nonnormality_verification_probe runs without error."""
    from scripts.probes.t51_nonnormality_verification_probe import main

    main()
