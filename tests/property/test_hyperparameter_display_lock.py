"""Lock: hyperparameter display in cell output.

The runner prints ALL resolved hyperparameters for each cell (swept values win
over defaults), excluding structural knobs (input_dim/output_dim) which are
task-derived. This lock drives the real search space — no injected params.
"""

import sys

import pytest

sys.path.insert(0, "/home/me/computronium/scripts")
import asyncio
import tempfile

from run_experiment import _run_loop

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.backends import LocalBackend
from computronium.experiment.execution.deadline import Deadline
from computronium.experiment.kernel.search_space import search_space_from_spec
from computronium.experiment.schema import RunSpec
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.run_spec import AxisSelection
from computronium.experiment.surface.cli import RUN_PROFILES


class TestHyperparameterDisplayLock:
    """Runner must print resolved hyperparameters in cell output."""

    @pytest.mark.timeout(300)
    def test_run_loop_prints_all_resolved_hyperparameters(self, capsys):
        """_run_loop prints all resolved hyperparameters (swept + defaults)."""
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
                    axis=StructuralAxis.SUBSTRATE,
                    primitives=("digital",),
                ),
                AxisSelection(
                    axis=StructuralAxis.GEOMETRY,
                    primitives=("feedforward",),
                ),
                AxisSelection(
                    axis=StructuralAxis.DYNAMICS,
                    primitives=("energy_minimization",),
                ),
                AxisSelection(
                    axis=StructuralAxis.CREDIT,
                    primitives=("thermodynamic_contrast",),
                ),
                AxisSelection(
                    axis=StructuralAxis.UPDATE,
                    primitives=("euclidean",),
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

                deadline = Deadline.from_hours(0.001)
                backend = LocalBackend(max_workers=1)

                captured_coords = []

                async def mock_submit(coord, sched, prov, params, store):
                    # No injection: the real search space must populate the
                    # coordinate's swept hyperparameters (TODO61 §11.1).
                    captured_coords.append(coord)

                    from computronium.experiment.schema.record import (
                        FailureCause,
                        GateVerdict,
                        Maturity,
                        Record,
                        ReproducibilityClass,
                        Severity,
                        Status,
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
                            params=dict(coord.params),
                            schedule=sched,
                            provenance=prov,
                            status=Status(
                                gate_verdict=GateVerdict.PASS_,
                                defect="",
                                cause=FailureCause.UNKNOWN,
                                severity=Severity.LOW,
                                quarantine=False,
                                maturity=Maturity.L0,
                                uncertainty={},
                                reproducibility=ReproducibilityClass.REPLAYABLE,
                                assessment_procedure_version="1.0",
                                ceec_link=None,
                            ),
                            payload={
                                "status": "evaluated",
                                "val_acc": 0.5,
                                "val_loss": 1.0,
                                "walltime_s": 1.0,
                                "epochs_completed": 1,
                                "epochs_requested": 1,
                                "seed": 42,
                                "fidelity": "L0",
                                "task_id": "digits",
                                "params": {},
                                "param_count": 1000,
                                "param_budget": 50000,
                            },
                            effective_params=dict(coord.params),
                            unknown={},
                        )
                    ]

                backend.submit = mock_submit

                asyncio.run(
                    _run_loop(
                        spec=spec,
                        store=store,
                        run_id=run_id,
                        deadline=deadline,
                        backend=backend,
                        device="cpu",
                        verbose=True,
                    )
                )

                # Verify hyperparameters were injected by the real search space
                assert len(captured_coords) > 0, "No cells processed"
                coord = captured_coords[0]
                assert coord.params, "Expected hyperparameters, got empty params"
                assert any(k.startswith("geometry.") for k in coord.params), (
                    f"Expected a swept geometry width, got: {coord.params}"
                )

                # Capture output
                captured = capsys.readouterr()
                output = captured.out

                # Verify ALL resolved hyperparameters are printed (not just swept)
                # Swept geometry width
                assert "geometry.hidden_dim=" in output, (
                    f"Swept geometry.hidden_dim not printed in output: {output}"
                )
                # Resolved update step_size (from _SEARCH_SWEEP)
                assert "update.step_size=" in output, (
                    f"Resolved update.step_size not printed in output: {output}"
                )
                # Resolved dynamics step_size (from _SEARCH_SWEEP)
                assert "dynamics.step_size=" in output, (
                    f"Resolved dynamics.step_size not printed in output: {output}"
                )
                # Structural knobs (input_dim/output_dim) must NOT appear
                assert "geometry.input_dim=" not in output, (
                    f"Structural geometry.input_dim should be excluded: {output}"
                )
                assert "geometry.output_dim=" not in output, (
                    f"Structural geometry.output_dim should be excluded: {output}"
                )

    @pytest.mark.timeout(300)
    def test_run_loop_prints_hyperparams_even_with_no_swept(self, capsys):
        """_run_loop prints resolved defaults even when no params are swept."""
        profile = RUN_PROFILES["quick-verify"]
        spec = RunSpec(
            profile=profile.name,
            task=profile.task,
            objectives=profile.objectives,
            stages=tuple(profile.stages),
            fidelity=profile.fidelity,
            n_seeds=profile.n_seeds,
            epochs=profile.epochs,
            batch_limit=profile.batch_limit,
            budget_seconds=300.0,
            param_budget=0,  # no ceiling: nothing is auto-swept
            policy=profile.policy,
            axes=(
                AxisSelection(axis=StructuralAxis.SUBSTRATE, primitives=("digital",)),
                AxisSelection(
                    axis=StructuralAxis.GEOMETRY, primitives=("feedforward",)
                ),
                AxisSelection(
                    axis=StructuralAxis.DYNAMICS, primitives=("instantaneous",)
                ),
                AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=("null",)),
                AxisSelection(axis=StructuralAxis.CREDIT, primitives=("gradient",)),
                AxisSelection(axis=StructuralAxis.UPDATE, primitives=("euclidean",)),
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
                        FailureCause,
                        GateVerdict,
                        Maturity,
                        Record,
                        ReproducibilityClass,
                        Severity,
                        Status,
                    )

                    # Even with param_budget=0, coord.params may have defaults
                    # from the harvest; the display shows resolved values
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
                            params=dict(coord.params),
                            schedule=sched,
                            provenance=prov,
                            status=Status(
                                gate_verdict=GateVerdict.PASS_,
                                defect="",
                                cause=FailureCause.UNKNOWN,
                                severity=Severity.LOW,
                                quarantine=False,
                                maturity=Maturity.L0,
                                uncertainty={},
                                reproducibility=ReproducibilityClass.REPLAYABLE,
                                assessment_procedure_version="1.0",
                                ceec_link=None,
                            ),
                            payload={
                                "status": "evaluated",
                                "val_acc": 0.5,
                                "val_loss": 1.0,
                                "walltime_s": 1.0,
                                "epochs_completed": 1,
                                "epochs_requested": 1,
                                "seed": 42,
                                "fidelity": "L0",
                                "task_id": "digits",
                                "params": {},
                                "param_count": 1000,
                                "param_budget": 50000,
                            },
                            effective_params=dict(coord.params),
                            unknown={},
                        )
                    ]

                backend.submit = mock_submit

                asyncio.run(
                    _run_loop(
                        spec=spec,
                        store=store,
                        run_id=run_id,
                        deadline=deadline,
                        backend=backend,
                        device="cpu",
                        verbose=True,
                    )
                )

                captured = capsys.readouterr()
                output = captured.out

                # Even with no swept params, resolved defaults are printed
                assert "dynamics.step_size=" in output, (
                    f"Resolved dynamics.step_size not printed: {output}"
                )
                assert "update.step_size=" in output, (
                    f"Resolved update.step_size not printed: {output}"
                )
                assert "geometry.hidden_dim=" in output, (
                    f"Resolved geometry.hidden_dim not printed: {output}"
                )
                # Structural knobs still excluded
                assert "geometry.input_dim=" not in output
                assert "geometry.output_dim=" not in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
