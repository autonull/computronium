"""Optuna distributions for one coordinate's active hyperparameters.

The sampled dimensions are the harvested hyperparameter specs the coordinate's
own primitive selection activates — the same `harvest_schema().active()` answer
composition uses. The previous version walked `AxisSpec.topology_params`
("structural params, not searched"), invented a `Record` to satisfy an
availability predicate, and had zero callers: the search space and the study
were looking at different hyperparameter sets (TODO46 §D3).

Availability is not asked here. `active()` already decided it by predicate, so
re-deciding it against a fabricated record would be a second source of truth
that can only disagree with the first.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from optuna.distributions import (
    BaseDistribution,
    CategoricalDistribution,
    FloatDistribution,
    IntDistribution,
)

from computronium.experiment.schema.axis import AxisKind, Scale

if TYPE_CHECKING:
    from computronium.experiment.schema.axis import Domain, HyperparameterSpec
    from computronium.experiment.schema.coordinate import Coordinate
    from computronium.experiment.schema.run_spec import RunSpec

__all__ = ["OptunaDistributionAdapter"]


class OptunaDistributionAdapter:
    """Maps a harvested hyperparameter spec to its Optuna distribution."""

    @staticmethod
    def distribution(spec: HyperparameterSpec) -> BaseDistribution | None:
        """One spec's distribution, honouring its declared kind and scale.

        Returns:
            The distribution, or ``None`` for a structural spec and for a
            domain this kind cannot express (an open range), which are not
            samplable dimensions.
        """
        domain = spec.domain
        match spec.axis_kind:
            case AxisKind.CONTINUOUS:
                bounds = _bounds(domain)
                return (
                    None
                    if bounds is None
                    else FloatDistribution(*bounds, log=_log_scale(domain, bounds))
                )
            case AxisKind.INTEGER:
                bounds = _bounds(domain)
                return (
                    None
                    if bounds is None
                    else IntDistribution(
                        int(bounds[0]),
                        int(bounds[1]),
                        log=_log_scale(domain, bounds),
                    )
                )
            case AxisKind.CATEGORICAL:
                return (
                    None
                    if not domain.members
                    else CategoricalDistribution(tuple(domain.members))
                )
            case AxisKind.STRUCTURAL:
                return None

    @staticmethod
    def distributions(
        coordinate: Coordinate, *, spec: RunSpec | None = None
    ) -> dict[str, BaseDistribution]:
        """The samplable dimensions for one coordinate.

        Args:
            coordinate: The primitive selection whose active space is sampled.
            spec: Optional run declaration. Its ``hyperparameters`` decide
                which names are sampled at all and narrow each to the declared
                domain; a spec may only narrow a harvested domain.

        Returns:
            Parameter name to distribution, for the active hyperparameters that
            have one. An empty mapping means the coordinate has no samplable
            dimension, which is a fact and not an error.

        Raises:
            InactiveHyperparameterError: The coordinate carries a parameter its
                own selection cannot use.
            ValueError: The spec sweeps a domain the primitive does not declare.
        """
        from computronium.experiment.execution.search_space import narrow_domain
        from computronium.experiment.schema.harvest import harvest_schema

        swept = {} if spec is None else dict(spec.hyperparameters)
        active = harvest_schema().active(coordinate)
        distributions: dict[str, BaseDistribution] = {}
        for hyper in active.specs:
            if swept and hyper.name not in swept:
                continue
            narrowed = (
                None
                if hyper.name not in swept
                else replace(
                    hyper,
                    domain=narrow_domain(swept[hyper.name], hyper.domain, hyper.name),
                )
            )
            distribution = OptunaDistributionAdapter.distribution(
                hyper if narrowed is None else narrowed
            )
            if distribution is not None:
                distributions[hyper.name] = distribution
        return distributions


def _log_scale(domain: Domain, bounds: tuple[float, float]) -> bool:
    """Whether a declared log scale is sampleable over these bounds.

    A range reaching zero has no logarithm; the declared intent is kept
    wherever it is satisfiable and dropped where it is not, rather than raising
    on a harvested row nobody chose.
    """
    return domain.scale is Scale.LOG and bounds[0] > 0.0


def _bounds(domain: Domain) -> tuple[float, float] | None:
    """A domain's closed bounds, or ``None`` when it has no range."""
    if domain.members is not None or domain.lo is None or domain.hi is None:
        return None
    return float(domain.lo), float(domain.hi)
