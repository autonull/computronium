"""Declarations the mechanism locks share (TODO48b R1/R2).

Internal module: `_`-prefixed per AGENTS.md. One declaration, several locks —
the whole point of TODO48b's "one fixture, many consumers" rule applied at the
property tier: the round-loop mechanisms, the price oracle and the record
versioning all read the same eight-cell space instead of each authoring a
near-miss of it.

The space is *sized by the oracle*, not by trial. The first draft declared
``thermodynamic_contrast`` beside ``instantaneous`` dynamics and had exactly one
legal cell: the pair cannot compose, and the space screens that silently
(TODO48 opportunity 3). ``price_plan`` says so before anything is launched.
"""

from __future__ import annotations

from computronium.experiment.schema import (
    MEASURED_BATCH_LIMIT,
    MEASURED_PARAM_BUDGET,
    AxisSelection,
    RunSpec,
    StructuralAxis,
)


def mechanism_spec(*, budget_seconds: float | None = 600.0) -> RunSpec:
    """Eight legal cells at the price table's measured regime, ~3 s to measure.

    Args:
        budget_seconds: The declaration's wall clock; ``None`` declares none.

    Returns:
        A spec over two substrates x two dynamics x two credit rules, all legal.
    """
    return RunSpec(
        profile="mechanism-lock",
        task="digits",
        objectives=("validation_accuracy", "walltime_total"),
        fidelity="L0",
        n_seeds=1,
        epochs=1,
        budget_seconds=budget_seconds,
        param_budget=MEASURED_PARAM_BUDGET,
        batch_limit=MEASURED_BATCH_LIMIT,
        axes=(
            AxisSelection(
                axis=StructuralAxis.SUBSTRATE, primitives=("digital", "sparse")
            ),
            AxisSelection(axis=StructuralAxis.GEOMETRY, primitives=("feedforward",)),
            AxisSelection(
                axis=StructuralAxis.DYNAMICS,
                primitives=("instantaneous", "energy_minimization"),
            ),
            AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=("fast_weights",)),
            AxisSelection(
                axis=StructuralAxis.CREDIT,
                primitives=("gradient", "random_projections"),
            ),
            AxisSelection(axis=StructuralAxis.UPDATE, primitives=("euclidean",)),
        ),
    )


def unreachable_spec() -> RunSpec:
    """A declaration that names a primitive no legal cell can reach.

    ``thermodynamic_contrast`` needs energy-based dynamics; paired with
    ``instantaneous`` it composes for nothing, so a run measures one cell and
    reports a one-member axis as if it had chosen one.
    """
    spec = mechanism_spec()
    return spec.model_copy(
        update={
            "axes": tuple(
                selection.model_copy(update={"primitives": ("thermodynamic_contrast",)})
                if selection.axis is StructuralAxis.CREDIT
                else selection
                for selection in spec.axes
            )
        }
    )


__all__ = ["mechanism_spec", "unreachable_spec"]
