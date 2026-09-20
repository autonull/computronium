"""Import-time performance lock.

Ensures that lazy loading doesn't regress and cold imports stay fast.
"""

import importlib.util
import time


def test_import_primitives_under_10ms():
    """Cold import of computronium.primitives must complete in < 10ms."""
    start = time.perf_counter()
    _ = __import__("computronium.primitives")
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 10, (
        f"primitives import took {elapsed_ms:.2f}ms, expected < 10ms"
    )


def test_import_algorithms_under_10ms():
    """Cold import of computronium.algorithms must complete in < 10ms."""
    start = time.perf_counter()
    _ = __import__("computronium.algorithms")
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 10, (
        f"algorithms import took {elapsed_ms:.2f}ms, expected < 10ms"
    )


def test_import_primitives_core_under_10ms():
    """Cold import of computronium.acceleration.registry must complete in < 10ms.

    Tests the lightweight registry module loaded directly (bypassing the
    heavy acceleration package __init__).
    """
    start = time.perf_counter()
    spec = importlib.util.spec_from_file_location(
        "registry", "computronium/acceleration/registry.py"
    )
    assert spec is not None
    registry = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(registry)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 10, (
        f"acceleration.registry direct load took {elapsed_ms:.2f}ms, expected < 10ms"
    )
