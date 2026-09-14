"""Synthesis engine (TODO23 T23.1.3/1.5/1.6/1.7).

spec → hard constraint filter (substrate support, local-credit policy,
resource ceilings) → I(C,U,P) viability scoring × recipe-card priors →
ranked coordinate with a human-readable provenance trace. CEEC-governed
exploration budget applies when synthesis confidence is low.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING

from computronium.analysis.recipe_cards import lookup as lookup_card
from computronium_lab.synthesis.catalog import CATALOG, MechanismCandidate
from computronium_lab.synthesis.predictor import ViabilityModel

if TYPE_CHECKING:
    from collections.abc import Mapping

    from computronium_lab.synthesis.spec import ProblemSpec

LOW_CONFIDENCE = 0.7

# objective name → (Pareto field, maximize?)
OBJECTIVE_FIELDS: dict[str, tuple[str, bool]] = {
    "accuracy": ("accuracy", True),
    "stability": ("stability", True),
    "adaptation_speed": ("adaptation_speed", True),
    "latency": ("latency_ms", False),
    "memory": ("memory_gb", False),
}


def register_objective(name: str, *, pareto_field: str, maximize: bool) -> None:
    """Plug a new optimization objective (TODO24 §14).

    Registers ``name`` in ``OBJECTIVE_FIELDS`` (Pareto field + direction)
    and in ``KNOWN_OBJECTIVES`` so ``ProblemSpec`` validation, the
    evolution kernel (via ``objective_names``), and the frontier archive
    consume it generically. The ``FitnessMetric`` itself (objective value
    per candidate) is supplied by the caller's campaign runner.
    """
    from computronium_lab.synthesis.spec import KNOWN_OBJECTIVES

    if name in OBJECTIVE_FIELDS:
        raise ValueError(f"objective {name!r} is already registered")
    OBJECTIVE_FIELDS[name] = (pareto_field, maximize)
    KNOWN_OBJECTIVES.add(name)


class ExplorationBudgetExhausted(RuntimeError):  # noqa: N818 — CEEC gate name is pre-registered
    """CEEC gate: exploratory campaigns for this spec exceeded its budget."""


@dataclass(frozen=True, slots=True)
class SynthesisResult:
    """A synthesized mechanism coordinate with its provenance trace."""

    name: str
    coordinate: dict[str, str]
    predicted_viability: float
    confidence: float
    exploratory: bool
    card_verdict: str | None
    provenance: tuple[str, ...]
    candidate: MechanismCandidate

    def build(self, spec: ProblemSpec) -> object:
        return self.candidate.build(spec)


@dataclass(frozen=True, slots=True)
class ParetoOption:
    """One frontier point: mechanism + predicted viability + Pareto metadata."""

    name: str
    predicted_viability: float
    metrics: dict[str, float]
    provenance: str


def filter_catalog(spec: ProblemSpec) -> tuple[MechanismCandidate, ...]:
    """Hard constraint filter (T23.1.3): substrate, local-credit, resources."""
    c = spec.constraints
    kept: list[MechanismCandidate] = []
    for cand in CATALOG:
        if c.substrate not in cand.substrates:
            continue
        if c.local_credit and not cand.local_credit:
            continue
        if c.latency_ms is not None and cand.pareto.latency_ms > c.latency_ms:
            continue
        if c.memory_gb is not None and cand.pareto.memory_gb > c.memory_gb:
            continue
        kept.append(cand)
    return tuple(kept)


def screen_config(cand: MechanismCandidate, spec: ProblemSpec) -> None:
    """Hard `SystemConfig.validate()` screen for one candidate coordinate."""
    if cand.config_builder is None:
        return
    cand.config_builder(
        spec.constraints.substrate, spec.constraints.precision
    ).validate()


def card_factor(credit: str, update: str) -> tuple[float, str | None]:
    """Soft prior from the measured recipe-card verdicts (TODO16 §0.3)."""
    card = lookup_card(credit, update)
    if card is None:
        return 1.0, None
    match card.status:
        case "harm" | "closed":
            return 0.2, card.status
        case "boundary" | "peak_collapse" | "depth_wall_d2":
            return 0.5, card.status
        case "rescue" | "rescue_sharp" | "home" | "promoted":
            return 1.1, card.status
        case _:
            return 1.0, card.status


def _score_candidates(
    candidates: tuple[MechanismCandidate, ...],
    spec: ProblemSpec,
    model: ViabilityModel,
    measured: Mapping[str, float],
) -> list[tuple[float, float, str | None, MechanismCandidate]]:
    scored: list[tuple[float, float, str | None, MechanismCandidate]] = []
    for cand in candidates:
        screen_config(cand, spec)
        p = model.predict(cand.features(spec))
        factor, verdict = card_factor(cand.credit, cand.update)
        if spec.constraints.continual and cand.continual_capable:
            factor *= 1.5
        effective = max(p * factor, measured.get(cand.name, 0.0))
        scored.append((effective, p, verdict, cand))
    return scored


def synthesize(
    spec: ProblemSpec,
    model: ViabilityModel | None = None,
    campaigns_run: dict[str, int] | None = None,
    frontier: Mapping[str, float] | None = None,
) -> SynthesisResult:
    """Spec → best valid coordinate with provenance (T23.1.5/1.7).

    ``frontier`` (TODO24 T24.2.6) maps mechanism names to archived
    *measured* accuracies; a candidate wins on the max of its predicted
    viability and its measured accuracy, with the archive cited in
    provenance. Predictions alone decide when no frontier is given.
    """
    model = model or _shared_model()
    candidates = filter_catalog(spec)
    if not candidates:
        raise ValueError(
            f"no catalog mechanism satisfies constraints {spec.constraints}; "
            f"catalog: {[c.name for c in CATALOG]}"
        )

    measured = dict(frontier or {})
    scored = _score_candidates(candidates, spec, model, measured)

    scored.sort(key=lambda t: (-t[0], -t[1]))
    top_score, top_p, top_verdict, top = scored[0]
    exploratory = top_p < LOW_CONFIDENCE
    provenance = _provenance(spec, model, top, top_p, top_verdict, len(candidates))
    archived = measured.get(top.name, 0.0)
    if archived >= top_score and archived > 0.0:
        provenance = (*provenance, f"frontier_archive:measured_accuracy={archived:.3f}")

    if exploratory and campaigns_run is not None:
        key = spec.key()
        if campaigns_run.get(key, 0) >= spec.exploration_budget:
            raise ExplorationBudgetExhausted(
                f"exploration budget ({spec.exploration_budget}) exhausted for "
                f"{key!r}; pre-register a CEEC validation campaign to extend it"
            )
        campaigns_run[key] = campaigns_run.get(key, 0) + 1

    return SynthesisResult(
        name=top.name,
        coordinate=top.coordinate(),
        predicted_viability=top_p,
        confidence=top_p,
        exploratory=exploratory,
        card_verdict=top_verdict,
        provenance=provenance,
        candidate=top,
    )


def explore(
    spec: ProblemSpec, model: ViabilityModel | None = None
) -> list[ParetoOption]:
    """Pareto frontier of constraint-satisfying mechanisms (T23.1.6)."""
    model = model or _shared_model()
    candidates = filter_catalog(spec)
    fields = [OBJECTIVE_FIELDS[o] for o in spec.objectives if o in OBJECTIVE_FIELDS]
    if not fields:
        fields = [OBJECTIVE_FIELDS["accuracy"]]

    options: list[ParetoOption] = []
    for cand in candidates:
        metrics = {
            name: getattr(cand.pareto, name) for name, _ in OBJECTIVE_FIELDS.values()
        }
        options.append(
            ParetoOption(
                name=cand.name,
                predicted_viability=model.predict(cand.features(spec)),
                metrics=metrics,
                provenance=cand.provenance,
            )
        )

    def dominates(a: ParetoOption, b: ParetoOption) -> bool:
        vals_a = [a.metrics[f] if maximize else -a.metrics[f] for f, maximize in fields]
        vals_b = [b.metrics[f] if maximize else -b.metrics[f] for f, maximize in fields]
        return all(x >= y for x, y in zip(vals_a, vals_b)) and any(
            x > y for x, y in zip(vals_a, vals_b)
        )

    return [
        o for o in options if not any(dominates(w, o) for w in options if w is not o)
    ]


def _provenance(
    spec: ProblemSpec,
    model: ViabilityModel,
    cand: MechanismCandidate,
    p: float,
    verdict: str | None,
    n_kept: int,
) -> tuple[str, ...]:
    lines = [
        f"constraints {spec.constraints} → {n_kept} candidate(s) pass the hard filter",
        f"I(C,U,P) features: {cand.features(spec)!r}",
        f"predicted viability p={p:.3f} (threshold {LOW_CONFIDENCE} for "
        f"{'exploratory' if p < LOW_CONFIDENCE else 'confident'} synthesis)",
        f"recipe-card verdict: {verdict or 'none'}",
        f"model path: {model.rationale(cand.features(spec))}",
        f"mechanism evidence: {cand.provenance}",
    ]
    return tuple(lines)


@lru_cache(maxsize=1)
def _shared_model() -> ViabilityModel:
    return ViabilityModel().fit()


__all__ = [
    "OBJECTIVE_FIELDS",
    "ExplorationBudgetExhausted",
    "ParetoOption",
    "SynthesisResult",
    "card_factor",
    "explore",
    "filter_catalog",
    "register_objective",
    "screen_config",
    "synthesize",
]
