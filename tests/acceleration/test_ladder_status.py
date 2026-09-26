"""The dispatch names a technology, and the status table says one thing per rung.

TODO36 §4.3 and §6.2. Two claims are locked here:

* ``select_backend(spec, "triton")`` is expressible, and asking for a technology a
  spec does not use raises an error that names what it does have;
* ``computronium.acceleration.status`` prints one line per rung, and
  ``--family <name>`` prints the rungs of that family and nothing else — §4.3's
  "one unambiguous answer per family".
"""

import json
from dataclasses import asdict

import pytest

from computronium.acceleration import status
from computronium.acceleration.dispatch import resolve_rung, select_backend
from computronium.acceleration.registry import all_specs, get

SPECS = all_specs()
TRITON_SPECS = [s for s in SPECS if s.kernel_technology == "triton"]


def _cli(capsys: pytest.CaptureFixture[str], *args: str) -> str:
    assert status.main(list(args)) == 0
    return capsys.readouterr().out


def test_a_technology_is_a_selectable_request() -> None:
    spec = get("primitive.credit_assignment.local_goodness")
    assert select_backend(spec, "triton") == "kernel"
    assert resolve_rung(spec, "triton").technology == "triton"
    assert resolve_rung(spec, "triton").entrypoint == spec.kernel_entrypoint


def test_selecting_an_unused_technology_names_what_exists() -> None:
    spec = get("primitive.state_dynamics.energy_minimization")
    with pytest.raises(ValueError) as excinfo:
        select_backend(spec, "triton")
    message = str(excinfo.value)
    assert spec.id in message
    assert "torch_compile" in message, "the error must name the technology in use"


def test_unknown_request_is_rejected() -> None:
    spec = SPECS[0]
    with pytest.raises(ValueError, match="unknown backend request"):
        select_backend(spec, "quantum")


def test_auto_never_selects_an_unpromoted_kernel_rung() -> None:
    for spec in SPECS:
        promoted = spec.status in {"kernel_verified", "microbenched", "campaign_ready"}
        assert (select_backend(spec, "auto") == "kernel") is (
            promoted and "kernel" in spec.supported_backends
        )


@pytest.mark.parametrize("family", ["fa", "pcalm", "tile"])
def test_status_family_filter_names_one_family(family: str) -> None:
    """§4.3's done-when: one unambiguous answer per family."""
    table = status.rows()
    selected = [row for row in table if row.family == family]
    assert selected, f"no rungs for family {family}"
    assert {row.family for row in selected} == {family}


def test_every_spec_has_a_reference_row_and_a_kernel_row_when_declared() -> None:
    rows = status.rows()
    by_spec: dict[str, set[str]] = {}
    for row in rows:
        by_spec.setdefault(row.spec, set()).add(row.rung)
    for spec in SPECS:
        rungs = by_spec[spec.id]
        assert "reference" in rungs
        assert ("kernel" in rungs) is ("kernel" in spec.supported_backends)


def test_status_json_round_trips() -> None:
    table = status.rows()
    assert json.loads(json.dumps([asdict(row) for row in table])) == [
        asdict(r) for r in table
    ]


def test_cli_table_has_a_line_per_rung(capsys: pytest.CaptureFixture[str]) -> None:
    out = _cli(capsys, "--json")
    assert len(json.loads(out)) == len(status.rows())


def test_cli_family_filter_is_a_report_not_a_substring_search(
    capsys: pytest.CaptureFixture[str],
) -> None:
    out = _cli(capsys, "--family", "fa", "--json")
    families = {row["family"] for row in json.loads(out)}
    assert families == {"fa"}
    assert not any("fabric" in row["spec"] for row in json.loads(out))
    by_spec = json.loads(_cli(capsys, "--spec", "algorithm.fa", "--json"))
    assert {row["spec"] for row in by_spec} == {"algorithm.fa"}


def test_gpu_column_reflects_recorded_rows_only() -> None:
    """`none` in the gpu column means unmeasured, never absent."""
    gpu = status.gpu_rungs()
    for row in status.rows():
        assert (row.gpu == "yes") is ((row.spec, row.rung) in gpu)
