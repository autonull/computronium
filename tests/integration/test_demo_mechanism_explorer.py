"""D22 — Gallery 2.0: the mechanism explorer, rendered.

The synthesis surface (TODO23 Phase 1) as a gallery demo: for four
constraint/objective scenarios, the explorer's non-dominated Pareto
frontier over the catalog and the synthesizer's top pick with its
predicted viability. Everything here is deterministic by construction —
the catalog Pareto metadata are transcribed measurements (TODO23 §11),
the predictor fit is pinned (held-out 0.944), and `Lab.explore` /
`Lab.synthesize` run no probes. Walltime is excluded from the record
(the gallery lock hashes record["data"] at 1e-6).

This is the "constraints → live Pareto frontier → one-click synthesis"
surface of TODO23 §2, exercised end-to-end.
"""

from __future__ import annotations

from computronium_lab import Constraints, Lab

from computronium.visualization._demo_api import bars_panel, figure_spec

SEED = 0

# (scenario name, constraints, objectives) — the registered explorer panel.
SPECS = (
    ("default_digital", Constraints(substrate="digital"), ("accuracy", "stability")),
    (
        "local_credit_only",
        Constraints(substrate="digital", local_credit=True),
        ("accuracy", "memory"),
    ),
    (
        "latency_budget",
        Constraints(substrate="digital", latency_ms=5.0),
        ("accuracy", "latency"),
    ),
    (
        "continual",
        Constraints(substrate="digital", continual=True),
        ("accuracy", "adaptation_speed"),
    ),
)


def test_demo_mechanism_explorer(emit_run_record) -> None:
    lab = Lab(seed=SEED)
    top_picks: dict[str, dict] = {}
    viability_bars: dict[str, dict[str, float]] = {}

    for name, constraints, objectives in SPECS:
        spec = lab.specify(
            "classification",
            "synthetic",
            constraints=constraints,
            objectives=objectives,
        )
        result = lab.synthesize(spec)
        top_picks[name] = {
            "mechanism": result.name,
            "predicted_viability": result.predicted_viability,
            "confidence": result.confidence,
            "exploratory": result.exploratory,
            "provenance_len": len(result.provenance),
        }
        frontier = {o.name: o for o in lab.explore(spec)}
        assert frontier, f"{name}: empty frontier"
        # The predictor ranks by P(viable); the measured Pareto frontier
        # ranks by transcribed metadata. They are different orderings by
        # design — the demo records both, it does not conflate them.
        for option in frontier.values():
            viability_bars.setdefault(name, {})[option.name] = (
                option.predicted_viability
            )

    record: dict = {
        "seed": SEED,
        "scenarios": [s[0] for s in SPECS],
        "top_picks": top_picks,
        "frontier_viability": viability_bars,
    }
    record["figure"] = figure_spec(
        "D22 — mechanism explorer: predicted viability of the Pareto frontier "
        "per constraint scenario",
        bars_panel(
            viability_bars,
            ylabel="predicted viability P(viable)",
            title="synthesis scenarios",
        ),
    )
    emit_run_record("D22", "mechanism_explorer", record)

    # Live assertions — the synthesis surface must stay honest.
    for name, top in top_picks.items():
        assert top["provenance_len"] > 0, f"{name}: no provenance trace"
        assert 0.0 <= top["predicted_viability"] <= 1.0
