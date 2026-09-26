"""One `device` fixture, and it is the one that reads `cpu_only`.

TODO35 §10.4: 37 slow-tier tests failed because of one sticky
`cudaErrorAssert`, and the file that reported it could not be trusted to
report its own failures. Bisected to a single test
(`test_grpc_seam_subprocess.py::TestGRPCSeamSubprocess::test_distributed_train_step_parity`),
which is marked `cpu_only` and `xfail` and was running on CUDA anyway: the
class defined its own `device` fixture that shadowed the shared one and
never looked at the marker. Deleting the shadow copy is the fix; this is
what stops it coming back.

Scope is `tests/integration/**` on purpose. A unit test that defines its own
device fixture owns a process it shares with nobody that matters — a poisoned
context there fails its own test, which is visible. The integration tier is
where the demos, the gRPC workers and the geometry tests share one CUDA
context, which is where a hidden shadow fixture costs 37 tests six files away.

The population is the scan itself: a lock that finds no local `device`
fixture has nothing to be right about, and the shared fixture's presence in
`tests/conftest.py` is what the second assertion pins.
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INTEGRATION = REPO_ROOT / "tests" / "integration"
SHARED = REPO_ROOT / "tests" / "conftest.py"


def _fixture_names(path: Path) -> set[str]:
    return {
        node.name
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
        if isinstance(node, ast.FunctionDef)
        and any(
            (isinstance(dec, ast.Attribute) and dec.attr == "fixture")
            or (isinstance(dec, ast.Call) and getattr(dec.func, "id", "") == "fixture")
            for dec in node.decorator_list
        )
    }


def test_the_shared_fixture_is_the_one_that_exists() -> None:
    assert "device" in _fixture_names(SHARED), (
        "tests/conftest.py no longer defines the shared `device` fixture; every "
        "test that relies on the cpu_only rule is now on its own"
    )


def test_no_integration_module_shadows_the_device_fixture() -> None:
    shadows = {
        path.relative_to(REPO_ROOT).as_posix(): _fixture_names(path)
        for path in sorted(INTEGRATION.rglob("test_*.py"))
        if "device" in _fixture_names(path)
    }
    assert not shadows, (
        f"{shadows} define their own `device` fixture. A local copy shadows "
        "the shared one and cannot see the `cpu_only` marker, so the test runs "
        "on the device its marker forbids — which is how "
        "test_grpc_seam_subprocess poisoned the CUDA context and took 37 "
        "slow-tier failures with it (TODO35 §10.4). Delete the shadow; the "
        "shared fixture is function-scoped, so drop any class-scoped fixture "
        "that depends on it too."
    )
