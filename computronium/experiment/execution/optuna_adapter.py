"""Optuna distribution adapter for AXES-driven suggestion (WP17).

Maps AxisSpec → Optuna distribution using availability predicates.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from optuna.distributions import (
    BaseDistribution,
    CategoricalDistribution,
    FloatDistribution,
    IntDistribution,
)

if TYPE_CHECKING:
    from computronium.experiment.execution.search_space import SearchSpace
    from computronium.experiment.legality.dsl import EvaluationContext
    from computronium.experiment.schema.axis import AxisSpec, HyperparameterSpec
    from computronium.experiment.schema.coordinate import Coordinate


class OptunaDistributionAdapter:
    """Maps AxisSpec → Optuna distribution using availability predicates."""

    @staticmethod
    def adapt(spec: AxisSpec, coord: Coordinate) -> BaseDistribution | None:
        """Convert an AxisSpec to an Optuna distribution.

        Args:
            spec: AxisSpec with domain, kind, and availability
            coord: Current coordinate for availability evaluation

        Returns:
            Optuna distribution or None if unavailable/structural.
        """

        # Check availability
        if spec.availability_predicate and not spec.availability_predicate.evaluate(
            coord
        ):
            return None

        # Structural axes are not sampled
        if spec.axis_kind.value == "structural":
            return None

        # Get the hyperparameters for this primitive
        # We need to extract from topology_params or the primitive's config
        # For now, return None for structural - will be handled by SearchSpace
        return None

    @staticmethod
    def adapt_hyperparameter(
        hp_spec: HyperparameterSpec, coord: Coordinate
    ) -> BaseDistribution | None:
        """Convert a HyperparameterSpec to an Optuna distribution.

        Args:
            hp_spec: HyperparameterSpec with domain, axis_kind, availability
            coord: Current coordinate for availability evaluation

        Returns:
            Optuna distribution or None if unavailable.
        """
        from computronium.experiment.legality.dsl import evaluate
        from computronium.experiment.schema.axis import AxisKind, Scale
        from computronium.experiment.schema.record import Record

        # Check availability using the legality DSL evaluate function
        if hp_spec.availability:
            # Create a minimal record for evaluation context
            ctx = EvaluationContext(
                Record.create(
                    run_id="",
                    coordinate=coord,
                    schedule=None,  # type: ignore
                    provenance=None,  # type: ignore
                    status=None,  # type: ignore
                    payload={},
                )
            )
            if not evaluate(hp_spec.availability, ctx):
                return None

        domain = hp_spec.domain
        kind = hp_spec.axis_kind

        if kind == AxisKind.CONTINUOUS:
            if domain.lo is None or domain.hi is None:
                return None
            return FloatDistribution(
                domain.lo,
                domain.hi,
                log=(domain.scale == Scale.LOG),
            )
        elif kind == AxisKind.INTEGER:
            if domain.lo is None or domain.hi is None:
                return None
            return IntDistribution(
                int(domain.lo),
                int(domain.hi),
                log=(domain.scale == Scale.LOG),
            )
        elif kind == AxisKind.CATEGORICAL:
            if not domain.members:
                return None
            return CategoricalDistribution(domain.members)
        elif kind == AxisKind.STRUCTURAL:
            return None

        return None

    @staticmethod
    def build_distributions(
        search_space: SearchSpace, coord: Coordinate
    ) -> dict[str, BaseDistribution]:
        """Build all distributions for a search space at a given coordinate.

        Args:
            search_space: The canonical search space
            coord: Current coordinate for availability evaluation

        Returns:
            Dict mapping parameter name to Optuna distribution.
        """
        from computronium.experiment.legality.dsl import evaluate
        from computronium.experiment.schema.record import Record

        distributions = {}

        for axis in search_space.axes_snapshot:
            # Skip structural axes
            if axis.axis_kind.value == "structural":
                continue

            # Check primitive availability
            if axis.availability_predicate:
                ctx = EvaluationContext(
                    Record.create(
                        run_id="",
                        coordinate=coord,
                        schedule=None,  # type: ignore
                        provenance=None,  # type: ignore
                        status=None,  # type: ignore
                        payload={},
                    )
                )
                if not evaluate(axis.availability_predicate, ctx):
                    continue

            # Add hyperparameters from this axis primitive
            for hp in axis.topology_params:
                dist = OptunaDistributionAdapter.adapt_hyperparameter(hp, coord)
                if dist is not None:
                    distributions[hp.name] = dist

        return distributions


__all__ = ["OptunaDistributionAdapter"]
