"""A test that can outrun the global timeout must say how long it may take.

TODO36 §4.12, and the defect it describes: ``pytest-timeout`` kills a test at
120 s and reports ``Failed: Timeout (>120.0s)``, which reads exactly like a flake
— the failure mode the plan was written about. The first version of this policy
was five hand-marked tests from one ``--durations`` run, with nothing stopping
the next 100-second test from appearing unmarked.

This is that something, on the half that can be checked statically:

* :data:`KNOWN_LONG` is the list of tests *observed* to exceed the default
  timeout. Each must carry an explicit ``@pytest.mark.timeout``, so its budget is
  a decision on the test rather than a surprise in a log.
* A new slow test is found the only way it can be — a full run's
  ``--durations=25`` — and added here. That half cannot be a static check; this
  file's docstring is the honest statement of that limit.

The remedy for a row here is always a marker. Never a deletion, and never a
``skip`` to make the number go away.
"""

import ast
import pathlib

import pytest

TESTS = pathlib.Path("tests")

#: ``path::test`` for tests measured over the 120 s default timeout.
#: 2026-09-26, from ``pytest tests/ --durations=25`` on the full suite:
#: ``test_demo_pc_alm`` took 36 s alone and over 120 s under full-suite load.
KNOWN_LONG: tuple[str, ...] = (
    "tests/integration/test_demo_pc_alm.py::test_demo_pc_alm",
)


def _marked(path: pathlib.Path, name: str) -> bool:
    """Whether the test function ``name`` in ``path`` carries a timeout marker."""
    source = path.read_text(encoding="utf-8")
    for node in ast.walk(ast.parse(source)):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == name
        ):
            segment = ast.get_source_segment(source, node) or ""
            decorators = "\n".join(
                ast.get_source_segment(source, d) or "" for d in node.decorator_list
            )
            return (
                "mark.timeout" in decorators or "mark.timeout" in segment.split("\n")[0]
            )
    pytest.fail(f"{path}::{name} is in KNOWN_LONG but no such test exists")


@pytest.mark.parametrize("node_id", KNOWN_LONG)
def test_known_long_test_declares_its_budget(node_id: str) -> None:
    path_text, _, name = node_id.partition("::")
    assert _marked(TESTS / path_text.removeprefix("tests/"), name), (
        f"{node_id} is known to exceed the 120s default and must carry "
        f"@pytest.mark.timeout"
    )


def test_known_long_is_not_stale() -> None:
    """Every row must point at a file that exists."""
    for node_id in KNOWN_LONG:
        path_text, _, name = node_id.partition("::")
        assert (TESTS / path_text.removeprefix("tests/")).exists(), node_id
        assert name.startswith("test_"), node_id


def test_the_default_timeout_is_still_the_policy() -> None:
    """The marker is an exception to a stated budget, so the budget must exist."""
    pyproject = (TESTS.parent / "pyproject.toml").read_text(encoding="utf-8")
    assert "timeout = 120" in pyproject, (
        "the global timeout moved; re-derive KNOWN_LONG"
    )
