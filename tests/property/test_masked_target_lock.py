"""Lock: the cross-entropy ignore sentinel is free, never an index (TODO94 R4).

The graph trainer masks its training nodes with ``IGNORE_INDEX`` (-100). The
settle nudge and the credit laws read that target, and one scatter without the
guard crashed the measured cell
``ternary/graph/spike_integration/fast_weights/target_inversion/lion``:
``index -100 is out of bounds for dimension 1 with size 7``.

One class-index form (`core.losses.class_one_hot`) now carries the rule: a
target entry below zero names no class, so its row stays free. This lock
fails if a second scatter returns, or if a masked graph cell crashes again.
"""

from __future__ import annotations

import torch

from computronium.core.losses import class_one_hot, one_hot_like
from computronium.experiment.kernel.evaluate import cell_record
from computronium.experiment.schema.coordinate import Coordinate, Provenance, Schedule
from computronium.ontology._settle_kernel import nudged_output
from computronium.ontology._utils import output_target

V = 7


class TestTheIgnoreRowStaysFree:
    def test_class_one_hot_leaves_the_sentinel_row_free(self) -> None:
        like = torch.zeros(3, V)
        hot = class_one_hot(torch.tensor([1, -100, 4]), like)
        assert torch.equal(hot[0], torch.nn.functional.one_hot(torch.tensor(1), V))
        assert torch.equal(hot[1], torch.zeros(V))
        assert hot[2, 4] == 1.0

    def test_output_target_ignores_the_sentinel(self) -> None:
        target = output_target(torch.tensor([2, -100, 0]), torch.zeros(3, V))
        assert torch.equal(target[1], torch.zeros(V))
        assert target[0, 2] == 1.0

    def test_one_hot_like_keeps_a_dense_target(self) -> None:
        dense = torch.rand(2, V)
        assert torch.equal(one_hot_like(dense, torch.zeros(2, V)), dense)

    def test_the_settle_nudge_leaves_the_sentinel_row_free(self) -> None:
        out = torch.randn(3, V)
        y = torch.tensor([1, -100, 4])
        nudged = nudged_output(out, y, 0.5)
        assert torch.equal(nudged[1], out[1])
        assert not torch.equal(nudged[0], out[0])


class TestTheMeasuredGraphCellTrains:
    def test_a_masked_graph_target_does_not_crash_the_cell(self) -> None:
        coordinate = Coordinate(
            substrate="ternary",
            geometry="graph",
            dynamics="spike_integration",
            plasticity="fast_weights",
            credit="target_inversion",
            update="lion",
            params={},
        )
        schedule = Schedule(
            fidelity="L0",
            seed=0,
            n_seeds=1,
            epochs=1,
            batch_limit=1,
            budget_id="todo94-r4",
            task_id="cora",
            param_budget=50_000,
            device="cpu",
            num_workers=0,
        )
        provenance = Provenance(
            env={},
            dataset="cora",
            dataset_version="masked-target",
            code_sha="",
            policy="masked-target lock",
            links={},
        )
        record = cell_record(coordinate, schedule, provenance)
        assert str(record.status.cause) != "runtime_error", record.status.defect
