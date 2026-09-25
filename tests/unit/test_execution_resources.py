"""ResourceMonitor behavior (execution guard)."""

from computronium.execution.resources import ResourceMonitor


def test_should_pause_when_cpu_exceeds_limit() -> None:
    """A limit below any measurable CPU reading must trip the guard.

    ``cpu_percent(interval=1)`` samples the live machine, so asserting on the
    default 98% limit is environment-dependent -- the previous version of
    this test asserted only that the call returned a bool, which the return
    annotation already guarantees.
    """
    assert ResourceMonitor(cpu_limit=-1.0).should_pause() is True


def test_gpu_probe_tolerates_missing_gpu() -> None:
    """``gpu_limit=0.0`` must not raise on a CPU-only box, and must not
    become the reason for the verdict -- the CPU guard is checked first."""
    monitor = ResourceMonitor(cpu_limit=-1.0, gpu_limit=0.0)
    assert monitor.should_pause() is True
