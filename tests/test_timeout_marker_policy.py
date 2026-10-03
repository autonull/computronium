"""A test that can outrun the global timeout must say how long it may take.

TODO36 §4.12, and the defect it describes: ``pytest-timeout`` kills a test at
120 s and reports ``Failed: Timeout (>120.0s)``, which reads exactly like a flake
— the failure mode the plan was written about. The first version of this policy
was five hand-marked tests from one ``--durations`` run, with nothing stopping
the next 100-second test from appearing unmarked.

The declaration is a marker next to the test, so the budget is a decision on the
test rather than a surprise in a log: ``@pytest.mark.timeout(N)`` on a test, on
a class, or in a module-level ``pytestmark``. :data:`KNOWN_LONG` is the census
of those declarations, and the two locks make the census and the tree agree in
both directions — a marker nobody recorded and a row nothing declares are the
same drift, seen from opposite sides.

The third half cannot be static: a test that *became* slow has no marker to
census. ``tests/conftest.py`` times every undeclared test and reports the ones
over ``WALLTIME_DISCOVERY_S`` at the end of the run, so the notice arrives with
the run rather than a season later.

The remedy for a row here is always a marker. Never a deletion, and never a
``skip`` to make the number go away.
"""

import ast
import pathlib
import re

import pytest

TESTS = pathlib.Path("tests")

#: ``(path::name, seconds)`` for every walltime budget declared in the tree.
#: ``name`` is the test function or class carrying the marker; a bare ``path``
#: is a module-level ``pytestmark``. Derived 2026-09-27 by ``_declarations``
#: below, from the 46 markers in the tree — of which this table previously
#: recorded one, which is how 45 unmarked-budget tests went unremarked. The 24
#: rows at 300s came from the end-of-run report in ``tests/conftest.py``, the
#: mechanism that found them; the rest were already declared and simply never
#: recorded here.
KNOWN_LONG: tuple[tuple[str, int], ...] = (
    (
        "tests/acceptance/test_unified_kernel.py::test_legality_same_for_all_policies",
        120,
    ),
    (
        "tests/acceptance/test_unified_kernel.py::test_u1_synthesis_policy_end_to_end",
        120,
    ),
    (
        "tests/acceptance/test_unified_kernel.py::test_u2_model_based_policy_end_to_end",
        120,
    ),
    (
        "tests/acceptance/test_unified_kernel.py::test_u3_multi_round_with_allocator",
        180,
    ),
    ("tests/acceptance/test_unified_kernel.py::test_u3_pause_resume_via_run_id", 180),
    ("tests/acceptance/test_unified_kernel.py::test_u4_policy_interchangeability", 300),
    (
        "tests/acceptance/test_unified_kernel.py::test_u5_cross_policy_evidence_reuse",
        300,
    ),
    ("tests/acceptance/test_unified_kernel.py::test_u5_same_measurement_identity", 120),
    ("tests/integration/test_demo_compose_6axis.py::test_demo_compose_6axis", 300),
    (
        "tests/integration/test_demo_credit_channel_map.py::test_demo_credit_channel_map",
        600,
    ),
    ("tests/integration/test_demo_depth_harvest.py::test_demo_depth_harvest", 900),
    ("tests/integration/test_demo_epc_fast_settle.py::test_demo_epc_fast_settle", 300),
    (
        "tests/integration/test_demo_failure_manifesto.py::test_demo_failure_manifesto",
        300,
    ),
    ("tests/integration/test_demo_geometry_swap.py::test_demo_geometry_swap", 300),
    (
        "tests/integration/test_demo_jpc_faithful_depth.py::test_demo_jpc_faithful_depth",
        600,
    ),
    ("tests/integration/test_demo_ntm_local.py::test_demo_ntm_local", 900),
    ("tests/integration/test_demo_pc_alm.py::test_demo_pc_alm", 600),
    (
        "tests/integration/test_demo_spatial_lattice_geometry_swap.py::test_demo_spatial_lattice_geometry_swap",
        300,
    ),
    ("tests/integration/test_demo_spike_settle.py::test_demo_spike_settle", 300),
    ("tests/integration/test_demo_substrate_swap.py::test_demo_substrate_swap", 300),
    ("tests/integration/test_demo_swap_credit.py::test_demo_swap_credit", 300),
    ("tests/integration/test_demo_uaxis_coverage.py::test_demo_uaxis_coverage", 600),
    (
        "tests/integration/test_demo_uaxis_depth_frontier.py::test_demo_uaxis_depth_frontier",
        900,
    ),
    ("tests/integration/test_demo_uaxis_muon_swap.py::test_demo_uaxis_muon_swap", 300),
    ("tests/integration/test_demo_update_ladder.py::test_demo_update_ladder", 1200),
    ("tests/integration/test_gallery_lock.py::test_figure_lock", 300),
    (
        "tests/integration/test_pc_alm_validation.py::test_pcalm_depth_100_no_explosion",
        300,
    ),
    ("tests/integration/test_pc_alm_validation.py::test_pcalm_depth_scaling", 300),
    ("tests/integration/test_quickstart.py::test_backprop_vs_eqprop_mnist", 600),
    ("tests/integration/test_smoke_all_tasks.py::test_vision_kmnist", 300),
    ("tests/integration/test_wheel_acceptance.py::test_wheel_installs_and_runs", 300),
    ("tests/property/test_axis_certifications.py::TestCAxisLocalGoodnessCredit", 600),
    ("tests/property/test_axis_certifications.py::TestCAxisTargetInversionCredit", 600),
    ("tests/property/test_ontology_parity.py", 300),
    (
        "tests/property/test_state_algebra_lock.py::test_type_checking_imports_are_not_called_at_runtime",
        300,
    ),
    (
        "tests/property/test_undefined_name_lock.py::test_every_cross_module_import_names_a_defined_symbol",
        300,
    ),
    ("tests/unit/core/test_credit.py::test_cosine_similarity_reasonable", 600),
    ("tests/unit/core/test_nca_geometry.py::test_distill_then_grow", 300),
    ("tests/unit/core/test_ntm_geometry.py::test_bptt_learns_copy_mechanics", 900),
    (
        "tests/unit/core/test_transformer_geometry.py::test_bp_learns_structured_tokens",
        300,
    ),
)

_MARKER = re.compile(r"^pytest\.mark\.timeout$")


def _seconds(expr: ast.AST) -> list[int]:
    """Every ``pytest.mark.timeout(N)`` in ``expr``, as its declared seconds.

    Searched rather than pattern-matched on the source, so a marker inside a
    list — the ``pytestmark = [pytest.mark.slow, pytest.mark.timeout(300)]``
    shape — is found by the same walk as a bare decorator.
    """
    return [
        int(ast.literal_eval(node.args[0]))
        for node in ast.walk(expr)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and _MARKER.match(ast.unparse(node.func))
    ]


def _declarations(path: pathlib.Path) -> list[tuple[str, int]]:
    """Every budget declared in ``path``, as ``(scope, seconds)``.

    ``scope`` is the function or class carrying the marker, or ``""`` for a
    module-level ``pytestmark`` — the three places a budget can be declared
    next to a test, and the three the census has to read.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: list[tuple[str, int]] = []
    for node in tree.body:
        if isinstance(node, ast.Assign | ast.AnnAssign) and node.value is not None:
            found += [("", seconds) for seconds in _seconds(node.value)]
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            for decorator in node.decorator_list:
                found += [(node.name, seconds) for seconds in _seconds(decorator)]
    return found


def _census() -> dict[str, int]:
    """The whole tree's declarations, keyed the way :data:`KNOWN_LONG` keys them."""
    declared: dict[str, int] = {}
    for path in sorted(TESTS.rglob("*.py")):
        if path.name == pathlib.Path(__file__).name and path.parent == TESTS:
            continue
        for scope, seconds in _declarations(path):
            key = f"{path.as_posix()}::{scope}" if scope else path.as_posix()
            declared[key] = seconds
    return declared


@pytest.fixture(scope="session")
def census() -> dict[str, int]:
    """The tree's declarations, parsed once.

    Session-scoped for the reason TODO37 §4.5 gave for the twin census: 25
    parametrized rows re-walking every test file is a minute of parse to answer
    a question about a file tree that cannot change mid-run.
    """
    return _census()


@pytest.mark.parametrize(("node_id", "seconds"), KNOWN_LONG)
def test_known_long_test_declares_its_budget(
    node_id: str, seconds: int, census: dict[str, int]
) -> None:
    """A recorded row is a real declaration, with the seconds it claims."""
    assert census.get(node_id) == seconds, (
        f"{node_id} is in KNOWN_LONG at {seconds}s but the tree declares "
        f"{census.get(node_id)}; a budget nobody declares is not a budget"
    )


def test_every_declared_budget_is_recorded(census: dict[str, int]) -> None:
    """The other direction: a marker in the tree that :data:`KNOWN_LONG` omits.

    This is the half the first version of this policy lacked. It recorded five
    markers by hand and nothing stopped the next twenty from appearing, so the
    table drifted to one row against twenty-two declarations while reading, in
    the diff, like a policy that was working.
    """
    unrecorded = {
        node_id: seconds
        for node_id, seconds in census.items()
        if (node_id, seconds) not in KNOWN_LONG
    }
    assert not unrecorded, (
        "a declared walltime budget missing from KNOWN_LONG: add the row "
        f"(declared seconds come from the marker) — {unrecorded}"
    )


def test_the_census_is_not_empty(census: dict[str, int]) -> None:
    """A census that resolved no file would pass both locks for the wrong reason."""
    assert len(census) >= 20, sorted(census)


def test_the_default_timeout_is_still_the_policy() -> None:
    """The marker is an exception to a stated budget, so the budget must exist."""
    pyproject = (TESTS.parent / "pyproject.toml").read_text(encoding="utf-8")
    assert "timeout = 120" in pyproject, (
        "the global timeout moved; re-derive KNOWN_LONG"
    )
