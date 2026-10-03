"""TODO48b R8 — a rate is positive, and a group names the cell it is on.

Two claims, both cheap, neither trains a cell (the whole selection is
milliseconds).

**A rate is positive.** ``update_lr=0`` does not train slowly, it does not
train: measured, it returns ``status=evaluated`` with a plausible
``train_acc`` and no defect, so the store cannot tell a dead learning rate from
a measurement. The check is asserted at *both* seams that can produce one — the
declaration (where a user types ``lo: 0``) and the coordinate (which probes and
``cell_record`` construct directly) — because a check on only one of them makes
the two paths disagree, which is the ``RecordSource`` defect class.

Falsifiable: drop ``validate_rate_value`` from ``Coordinate.__post_init__`` and
the coordinate half goes red; drop the declaration check and the other half
does. A param outside the registry is untouched — absence is not validity.

**A group names its cell.** ``matched_group='ofat_update_lr'`` is a claim that
one factor moved and the rest held. The previous construction gave every factor
the levels ``(0.0, 1.0)`` and then stamped whichever group fell on a proposal
by cycling, so the label could name a cell that moved two hyperparameters at
once. Asserted here without a run: every stamped group matches its cell on the
structural axes, and no cell carries a designed origin without a group.
"""

from __future__ import annotations

import pytest

from computronium.experiment.execution.contrast_design import create_ofat_design
from computronium.experiment.execution.evaluate import task_shape
from computronium.experiment.execution.search_space import (
    iter_candidates,
    search_space_from_spec,
)
from computronium.experiment.execution.stage import Proposal
from computronium.experiment.execution.stages_impl import (
    _allocate_origins,
    _design_factors,
    _is_assignment,
    _match_design,
    _origins_for_design,
)
from computronium.experiment.schema.axis import Domain, StructuralAxis
from computronium.experiment.schema.coordinate import (
    Coordinate,
    DataOrigin,
    Schedule,
)
from computronium.experiment.schema.registries import (
    RATE_PARAMETERS,
    validate_rate_value,
)
from computronium.experiment.schema.run_spec import AxisSelection, RunSpec
from computronium.experiment.schema.seed_registries import seed_all_registries

pytestmark = pytest.mark.timeout(120)

_CAMPAIGN = "examples/learning-rules-and-geometry-digits.yaml"
_DESIGNED = frozenset({DataOrigin.CONTROL, DataOrigin.CONTRAST})
_ALLOCATION = {
    "exploration": 0.45,
    "calibration": 0.25,
    "test": 0.20,
    "control": 0.05,
    "contrast": 0.05,
}


@pytest.fixture(autouse=True)
def _seed() -> None:
    seed_all_registries()


def _coordinate(**overrides: object) -> Coordinate:
    fields: dict[str, object] = {
        "substrate": "digital",
        "geometry": "feedforward",
        "dynamics": "energy_minimization",
        "plasticity": "fast_weights",
        "credit": "gradient",
        "update": "euclidean",
        "params": {"hidden_dim": 64},
    }
    fields.update(overrides)
    return Coordinate(**fields)  # type: ignore[arg-type]


def _spec(**overrides: object) -> RunSpec:
    fields: dict[str, object] = {
        "profile": "lock",
        "task": "digits",
        "objectives": ("validation_accuracy",),
        "fidelity": "L0",
        "n_seeds": 1,
        "epochs": 1,
        "param_budget": 10000,
        "batch_limit": 2,
        "axes": (
            AxisSelection(axis=StructuralAxis.SUBSTRATE, primitives=("digital",)),
            AxisSelection(axis=StructuralAxis.GEOMETRY, primitives=("feedforward",)),
            AxisSelection(
                axis=StructuralAxis.DYNAMICS, primitives=("energy_minimization",)
            ),
            AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=("fast_weights",)),
            AxisSelection(axis=StructuralAxis.CREDIT, primitives=("gradient",)),
            AxisSelection(axis=StructuralAxis.UPDATE, primitives=("euclidean",)),
        ),
    }
    fields.update(overrides)
    return RunSpec(**fields)  # type: ignore[arg-type]


class TestRateParameters:
    """A rate is positive, at both seams that can produce one."""

    def test_a_coordinate_refuses_a_non_positive_rate(self) -> None:
        """The coordinate seam: an invalid cell cannot be constructed."""
        for name in sorted(RATE_PARAMETERS):
            for bad in (0.0, -0.1):
                with pytest.raises(ValueError, match="is not a rate"):
                    _coordinate(params={"hidden_dim": 64, name: bad})

    def test_a_declaration_refuses_a_non_positive_rate(self) -> None:
        """The declaration seam: `update_lr: {lo: 0}` is refused at the spec."""
        with pytest.raises(ValueError, match="is not a rate"):
            _spec(hyperparameters={"update_lr": Domain(lo=0.0, hi=0.1)})
        _spec(hyperparameters={"update_lr": Domain(lo=1e-3, hi=0.1)})

    def test_the_registry_is_about_rates_not_about_names(self) -> None:
        """Membership is a claim per parameter, and absence is not validity.

        ``momentum`` is a multiplier where 0 is legitimate (no smoothing), so it
        is deliberately absent; asserting the set's membership directly stops a
        later session from widening it to "everything numeric".
        """
        assert "momentum" not in RATE_PARAMETERS
        validate_rate_value("momentum", 0.0)  # no raise
        validate_rate_value("hidden_dim", 0)  # not a rate this registry claims
        with pytest.raises(ValueError, match="is not a rate"):
            validate_rate_value("update_lr", 0)

    def test_a_zero_learning_rate_is_rejected_not_trained(self) -> None:
        """The claim this exists for, stated as the value that motivated it.

        Falsifiable in one line: remove ``RATE_PARAMETERS.update_lr`` and this
        still passes, which is the point — it documents the *case*, while the
        tests above hold the *mechanism*.
        """
        assert "update_lr" in RATE_PARAMETERS
        with pytest.raises(ValueError, match="update_lr"):
            _coordinate(params={"update_lr": 0.0})


class TestContrastGroupsAreHonest:
    """A group names the cell it is stamped on."""

    @pytest.fixture(scope="class")
    def campaign_design(self) -> tuple[list[Proposal], list]:
        spec = RunSpec.load(_CAMPAIGN)
        space = search_space_from_spec(spec, tasks=spec.task_names)
        proposals = []
        for coordinate, task in iter_candidates(spec, space, shape=task_shape):
            if len(proposals) >= 12:
                break
            proposals.append(
                Proposal(
                    coordinate=coordinate,
                    schedule=Schedule(
                        fidelity="L0",
                        seed=0,
                        n_seeds=1,
                        epochs=1,
                        batch_limit=2,
                        budget_id="lock",
                        task_id=task.task_id,
                        param_budget=10000,
                    ),
                    rationale="lock",
                )
            )
        return proposals, list(
            create_ofat_design(_design_factors(space), seed=1).assignments
        )

    def test_factors_carry_the_primitives_the_run_actually_sweeps(
        self, campaign_design: tuple[list[Proposal], list]
    ) -> None:
        """A design factor's levels are real cells, not normalized labels.

        Falsifiable: revert to ``levels=(0.0, 1.0)`` and this reads
        ``('credit', (0.0, 1.0))`` — the shape that produced
        ``update_lr=0.0`` and a group that named a two-factor change.
        """
        _, assignments = campaign_design
        spec = RunSpec.load(_CAMPAIGN)
        space = search_space_from_spec(spec, tasks=spec.task_names)
        factors = {f.name: f.levels for f in _design_factors(space)}
        assert factors, "the campaign varies axes but the design found no factor"
        for name, levels in factors.items():
            axis = StructuralAxis(name)
            assert tuple(levels) == space.primitives(axis), (
                f"factor {name} carries {levels}, not the axis's {space.primitives(axis)}"
            )
            assert all(isinstance(level, str) for level in levels), (
                f"factor {name} has non-primitive levels {levels}"
            )
        # Every assignment names at least one factor the run varies.
        assert any(set(a.factor_assignments) <= set(factors) for a in assignments)

    def test_every_stamped_group_matches_the_cell_it_is_on(
        self, campaign_design: tuple[list[Proposal], list]
    ) -> None:
        """The invariant the previous implementation violated."""
        proposals, assignments = campaign_design
        matched = _match_design(proposals, assignments)
        assert matched, "the design matched nothing: it would stamp nothing"
        for index, assignment in matched.items():
            assert _is_assignment(proposals[index].coordinate, assignment), (
                f"proposal {index} carries group {assignment.matched_group!r} but is "
                f"{proposals[index].coordinate.cell_key()[:12]}"
            )

    def test_one_factor_moves_and_the_rest_hold(
        self, campaign_design: tuple[list[Proposal], list]
    ) -> None:
        """The contrast claim itself: a group differs from the control in one axis.

        Falsifiable: cycle groups onto proposals regardless of the cell and this
        is the assertion that catches it.
        """
        _, assignments = campaign_design
        control = next(a for a in assignments if a.data_origin == DataOrigin.CONTROL)
        contrasts = [a for a in assignments if a.data_origin == DataOrigin.CONTRAST]
        assert contrasts, "an OFAT design with no contrasts is a control"
        for contrast in contrasts:
            differing = [
                name
                for name, level in contrast.factor_assignments.items()
                if control.factor_assignments.get(name) != level
            ]
            assert len(differing) == 1, (
                f"group {contrast.matched_group!r} differs from the control in "
                f"{differing}: OFAT varies exactly one factor"
            )
            assert differing[0] in contrast.matched_group, (
                f"group {contrast.matched_group!r} names a factor it does not vary"
            )

    def test_no_cell_claims_a_designed_origin_without_a_group(
        self, campaign_design: tuple[list[Proposal], list]
    ) -> None:
        """An origin the design did not place is not a design origin."""
        proposals, assignments = campaign_design
        allocated = _allocate_origins(len(proposals), _ALLOCATION)
        origins = _origins_for_design(proposals, assignments, allocated)
        matched = _match_design(proposals, assignments)
        assert len(origins) == len(proposals)
        for index, origin in enumerate(origins):
            if origin in _DESIGNED:
                assert index in matched, (
                    f"proposal {index} is {origin.value} with no design group"
                )

    def test_the_allocation_is_exact_and_keeps_the_design_from_losing(
        self, campaign_design: tuple[list[Proposal], list]
    ) -> None:
        """The defect that made the design inert in the first place.

        Measured: a 450-record campaign carried 250 exploration / 120
        calibration / 80 test and **zero** control or contrast, because five
        ``max(1, ...)`` counts summed past the round size and
        ``data_origins[:total]`` truncated the two 5%-quota origins away.

        Two properties, because the second is not the first: the allocation is
        exactly the round size at every size, and a round long enough for a 5%
        share keeps its designed origins. A two-proposal round *cannot* hold a
        5% group, and the honest behaviour there is to run the round without
        one rather than to over-allocate.
        """
        for total in (1, 2, 3, 5, 8, 10, 18, 45, 90):
            origins = _allocate_origins(total, _ALLOCATION)
            assert len(origins) == total, (
                f"{len(origins)} origins for {total} slots: the allocation is "
                "truncating, which is what ate the design"
            )
            if total < 20:
                continue
            for required in _DESIGNED:
                assert required in origins, (
                    f"a round of {total} has no {required.value}: a 5% share fits "
                    f"in {total} proposals and was truncated away"
                )
