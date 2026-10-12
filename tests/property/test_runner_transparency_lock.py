"""Lock: experiment runner outputs real-time cell progress with full axis values."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import sys

sys.path.insert(0, "/home/me/computronium/scripts")
from run_experiment import _run_loop
from computronium.experiment.schema import RunSpec
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.run_spec import AxisSelection
from computronium.experiment.surface.cli import RUN_PROFILES
from computronium.experiment.kernel.search_space import search_space_from_spec
from computronium.experiment.execution.deadline import Deadline
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.backends import LocalBackend
from computronium.experiment.schema.coordinate import Coordinate, Schedule, Provenance
import tempfile
import asyncio


class TestRunnerTransparencyLock:
    """Runner must print every cell with full axis values in real-time."""

    @pytest.mark.timeout(300)
    def test_run_loop_prints_cell_details(self, capsys):
        """_run_loop prints substrate, geometry, dynamics, credit, update, plasticity for each cell."""
        profile = RUN_PROFILES["production-map"]
        spec = RunSpec(
            profile=profile.name,
            task=profile.task,
            objectives=profile.objectives,
            stages=tuple(profile.stages),
            fidelity=profile.fidelity,
            n_seeds=profile.n_seeds,
            epochs=profile.epochs,
            batch_limit=profile.batch_limit,
            budget_seconds=3600.0,
            param_budget=profile.param_budget,
            policy=profile.policy,
            axes=(
                AxisSelection(
                    axis=StructuralAxis.CREDIT,
                    primitives=("gradient", "random_projections"),
                ),
                AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=("null",)),
            ),
            checkpoint_every_n=profile.checkpoint_every_n,
            seed=42,
            device="cpu",
        )

        space = search_space_from_spec(spec, tasks=spec.task_names)

        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = f"{tmpdir}/test.db"
            with RecordStore(StoreConfig(path=store_path)) as store:
                run_id = store.create_run(spec=spec)

                deadline = Deadline.from_hours(0.001)  # Very short
                backend = LocalBackend(max_workers=1)

                # Mock backend.submit to return quickly
                async def mock_submit(coord, sched, prov, params, store):
                    from computronium.experiment.schema.record import (
                        Record,
                        Status,
                        GateVerdict,
                    )

                    return [
                        Record(
                            record_id="test",
                            seq=1,
                            run_id=run_id,
                            schema_version=3,
                            cell_key=coord.cell_key(),
                            measurement_key=coord.measurement_key(sched),
                            substrate=coord.substrate,
                            geometry=coord.geometry,
                            dynamics=coord.dynamics,
                            plasticity=coord.plasticity,
                            credit=coord.credit,
                            update=coord.update,
                            params={},
                            schedule=sched,
                            provenance=prov,
                            status=Status(
                                gate_verdict=GateVerdict.PASS,
                                defect="",
                                cause="unknown",
                                severity="low",
                                quarantine=False,
                                maturity="l0",
                                uncertainty={},
                                reproducibility="replayable",
                                assessment_procedure_version="1.0",
                                ceec_link=None,
                            ),
                            payload={
                                "status": "evaluated",
                                "val_acc": 0.5,
                                "walltime_s": 0.1,
                                "epochs_completed": 1,
                                "epochs_requested": 1,
                                "seed": sched.seed,
                                "fidelity": sched.fidelity,
                                "task_id": sched.task_id,
                                "params": {},
                                "param_count": 1000,
                                "param_budget": 50000,
                            },
                            unknown=None,
                            effective_params={},
                        )
                    ]

                backend.submit = mock_submit

                asyncio.run(_run_loop(spec, store, run_id, deadline, backend, "cpu"))

        captured = capsys.readouterr()
        output = captured.out

        # Check that cell output contains all axis values
        assert "substrate=" in output
        assert "geometry=" in output
        assert "dynamics=" in output
        assert "credit=" in output
        assert "update=" in output
        assert "plasticity=" in output
        assert "seed=" in output

    @pytest.mark.timeout(300)
    def test_run_loop_prints_cell_count(self, capsys):
        """Runner prints cell number for each cell."""
        profile = RUN_PROFILES["production-map"]
        spec = RunSpec(
            profile=profile.name,
            task=profile.task,
            objectives=profile.objectives,
            stages=tuple(profile.stages),
            fidelity=profile.fidelity,
            n_seeds=profile.n_seeds,
            epochs=profile.epochs,
            batch_limit=profile.batch_limit,
            budget_seconds=3600.0,
            param_budget=profile.param_budget,
            policy=profile.policy,
            axes=(
                AxisSelection(axis=StructuralAxis.CREDIT, primitives=("gradient",)),
                AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=("null",)),
            ),
            checkpoint_every_n=profile.checkpoint_every_n,
            seed=42,
            device="cpu",
        )

        space = search_space_from_spec(spec, tasks=spec.task_names)

        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = f"{tmpdir}/test.db"
            with RecordStore(StoreConfig(path=store_path)) as store:
                run_id = store.create_run(spec=spec)

                deadline = Deadline.from_hours(0.001)
                backend = LocalBackend(max_workers=1)

                async def mock_submit(coord, sched, prov, params, store):
                    from computronium.experiment.schema.record import (
                        Record,
                        Status,
                        GateVerdict,
                    )

                    return [
                        Record(
                            record_id="test",
                            seq=1,
                            run_id=run_id,
                            schema_version=3,
                            cell_key=coord.cell_key(),
                            measurement_key=coord.measurement_key(sched),
                            substrate=coord.substrate,
                            geometry=coord.geometry,
                            dynamics=coord.dynamics,
                            plasticity=coord.plasticity,
                            credit=coord.credit,
                            update=coord.update,
                            params={},
                            schedule=sched,
                            provenance=prov,
                            status=Status(
                                gate_verdict=GateVerdict.PASS,
                                defect="",
                                cause="unknown",
                                severity="low",
                                quarantine=False,
                                maturity="l0",
                                uncertainty={},
                                reproducibility="replayable",
                                assessment_procedure_version="1.0",
                                ceec_link=None,
                            ),
                            payload={
                                "status": "evaluated",
                                "val_acc": 0.5,
                                "walltime_s": 0.1,
                                "epochs_completed": 1,
                                "epochs_requested": 1,
                                "seed": sched.seed,
                                "fidelity": sched.fidelity,
                                "task_id": sched.task_id,
                                "params": {},
                                "param_count": 1000,
                                "param_budget": 50000,
                            },
                            unknown=None,
                            effective_params={},
                        )
                    ]

                backend.submit = mock_submit

                asyncio.run(_run_loop(spec, store, run_id, deadline, backend, "cpu"))

        captured = capsys.readouterr()
        output = captured.out

        # Check that cell numbers are printed
        assert "Cell 1:" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
