"""Lock: rows are comparable only when the varied axis is the only difference.

TODO95 D3. The screen tries compose-legal swap boxes when a primitive is
illegal at the base. A swapped row is a measurement, never a comparison: the
map prints that label instead of hiding it. An inert row keeps its number but
is not a result about its axis.
"""

from __future__ import annotations

from computronium.experiment.schema.coordinate import Coordinate
from computronium.experiment.sec_census import PrimitiveCensusEntry
from computronium.experiment.sec_loop import _map_row


def _entry(
    axis: str = "credit_assignment", name: str = "homeostatic"
) -> PrimitiveCensusEntry:
    return PrimitiveCensusEntry(
        id=f"primitive.{axis}.{name}",
        axis=axis,
        name=name,
        task_families=("vision",),
        available=True,
        capability_card="test",
        status="reference_only",
        reference_entrypoint="",
        kernel_entrypoint=None,
        supported_backends=(),
    )


def _cell(**overrides: object) -> dict:
    cell: dict = {
        "primitive": "primitive.credit_assignment.homeostatic",
        "status": "MEASURED",
        "val_acc": 0.12,
        "loss": 2.3,
        "param_count": 1000,
        "within_ceiling": True,
        "walltime_s": 1.0,
        "box": {"task": "mnist", "seed": 0, "batch_limit": 375},
        "ruler": "val_acc on mnist",
        "control_val_acc": 0.89,
        "binding": "inert",
        "binding_reason": "reads no label",
        "swapped": False,
    }
    cell.update(overrides)
    return cell


def test_a_swapped_row_is_labelled_not_compared() -> None:
    row = _map_row(_entry(), _cell(swapped=True))
    assert row["status"] == "measured"
    assert row["swapped"] is True
    assert row["rule"] == "nearest-legal swap"


def test_a_base_row_names_its_rule() -> None:
    row = _map_row(_entry(), _cell())
    assert row["swapped"] is False
    assert row["rule"] == "base box, one axis varied"


def test_an_inert_row_is_not_a_result_about_its_axis() -> None:
    row = _map_row(_entry(), _cell())
    assert row["status"] == "measured"
    assert row["binding"] == "inert"
    assert row["binding_reason"]
    assert row["measurement"]["val_acc"] == 0.12


def test_a_cached_coordinate_keeps_its_structural_values() -> None:
    """The compose cache is a serialization, not an identity: a graph edge
    index must come back as a list, or the graph topology is refused."""
    from computronium.experiment.kernel.compose import compose_configs

    coordinate = Coordinate(
        substrate="digital",
        geometry="graph",
        dynamics="instantaneous",
        plasticity="null",
        credit="gradient",
        update="euclidean",
        params={
            "credit.lr": 0.01,
            "update.lr": 0.01,
            "geometry.hidden_dim": 128,
            "geometry.depth": 2,
            "geometry.edge_index": [[0, 1], [1, 0]],
        },
    )
    config = compose_configs(
        coordinate=coordinate,
        geometry={},
        input_shape=(1, 28, 28),
        output_dim=10,
    )
    assert config.geometry.connectivity["edge_index"] == [[0, 1], [1, 0]]
