"""Probe: do the new stability metrics work outside the energy-based family?

Written because the stability-plasticity campaign pins `energy_minimization` +
`thermodynamic_contrast`, so every number in TODO51 §2 came from one dynamics
primitive out of eight. `compute_stability_metrics` builds a
`SubstrateSettleKernel` to get a relaxation step, which is an EqProp-shaped
assumption; this probe runs the metrics across the whole registered dynamics
and geometry space and reports which cells produce a measurement and which
silently produce nothing.

The question is not "does it work for energy_minimization" - it does. It is
whether a metric that only answers for the family the campaign happened to pin
is a bias in the campaign's conclusions, or a gap in the metric.

Run: uv run python -m scripts.probes.t51_metric_coverage_probe
"""

from __future__ import annotations

from computronium.experiment.execution.evaluate import compute_stability_metrics
from computronium.experiment.schema.coordinate import Coordinate

# Each dynamics with a credit/geometry the framework accepts for it.
# Probing an illegal pairing measures the validity check, not the metric:
# diffusion demands recurrent geometry and non-gradient credit, spike
# integration demands temporal-trace or target-inversion credit, and
# thermodynamic contrast demands an energy-based or PC-family dynamics.
_LEGAL = {
    "energy_minimization": ("thermodynamic_contrast", "feedforward"),
    "error_predictive_coding": ("thermodynamic_contrast", "feedforward"),
    "pc_alm": ("thermodynamic_contrast", "feedforward"),
    "predictive_settling": ("thermodynamic_contrast", "feedforward"),
    "instantaneous": ("gradient", "feedforward"),
    "diffusion": ("random_projections", "recurrent"),
    "lazy": ("gradient", "feedforward"),
    "spike_integration": ("temporal_trace", "feedforward"),
}

_STABILITY = (
    "spectral_radius",
    "max_singular_value",
    "drift_spectral_radius",
    "contraction_rate",
)

_ENERGY = (
    "hopfield_energy",
    "pc_free_energy",
    "augmented_lagrangian",
    "spike_proxy_energy",
    "instantaneous_proxy_energy",
    "free_energy",
)


def _system(dynamics: str, geometry: str, credit: str):
    from computronium.experiment.execution.compose import compose_cell_system

    return compose_cell_system(
        coordinate=Coordinate(
            substrate="digital",
            geometry=geometry,
            dynamics=dynamics,
            plasticity="null",
            credit=credit,
            update="euclidean",
            params={"hidden_dim": 64, "num_layers": 3},
        ),
        geometry={},
        input_shape=(64,),
        output_dim=10,
        param_budget=2_000_000,
    ).system


def main() -> None:
    import torch

    torch.manual_seed(0)
    print(
        f"{'dynamics':<24}{'credit':<22}{'rho':>9}{'sigma':>9}"
        f"{'rho_drift':>11}{'sigma_dr':>10}"
    )
    print("-" * 85)

    gaps: list[str] = []
    for dynamics in sorted(_LEGAL):
        credit, geometry = _LEGAL[dynamics]
        try:
            metrics = compute_stability_metrics(
                _system(dynamics, geometry, credit), torch.randn(4, 64)
            )
        except Exception as exc:  # ruff: ignore[blind-except] - the probe reports, never raises
            gaps.append(f"{dynamics}/{credit}/{geometry}: {type(exc).__name__}: {exc}")
            print(f"{dynamics:<24}{credit:<22}{'RAISED':>39}")
            continue
        keys = (
            "spectral_radius",
            "max_singular_value",
            "drift_spectral_radius",
            "drift_max_singular_value",
        )
        row = [f"{metrics[k]:.4f}" if k in metrics else "--" for k in keys]
        if any(cell == "--" for cell in row):
            gaps.append(
                f"{dynamics}: missing {[k for k, c in zip(keys, row, strict=True) if c == '--']}"
            )
        print(
            f"{dynamics:<24}{credit:<22}{row[0]:>9}{row[1]:>9}{row[2]:>11}{row[3]:>10}"
        )

    print(f"\ndynamics probed: {len(_LEGAL)}")
    if gaps:
        print(f"gaps ({len(gaps)}):")
        for gap in gaps:
            print(f"  {gap}")
    else:
        print("no gaps: every dynamics produced every stability metric")

    # Also check energy metrics
    print("\n--- Energy metrics ---")
    print(
        f"{'dynamics':<24}{'family':<22}{'hopfield':>10}{'pc_fe':>10}{'aug_lag':>10}"
        f"{'spike_px':>10}{'inst_px':>10}{'free_eng':>10}"
    )
    print("-" * 96)
    energy_gaps: list[str] = []
    for dynamics in sorted(_LEGAL):
        credit, geometry = _LEGAL[dynamics]
        try:
            metrics = compute_stability_metrics(
                _system(dynamics, geometry, credit), torch.randn(4, 64)
            )
        except Exception:
            print(f"{dynamics:<24}{'N/A':<22}{'RAISED':>60}")
            continue

        # Determine expected family
        if dynamics in {"energy_minimization", "lazy", "diffusion"}:
            family = "hopfield"
            expected_key = "hopfield_energy"
        elif dynamics in {"predictive_settling", "error_predictive_coding"}:
            family = "pc_free_energy"
            expected_key = "pc_free_energy"
        elif dynamics == "pc_alm":
            family = "augmented_lagrangian"
            expected_key = "augmented_lagrangian"
        elif dynamics == "spike_integration":
            family = "spike_proxy"
            expected_key = "spike_proxy_energy"
        elif dynamics == "instantaneous":
            family = "instantaneous_proxy"
            expected_key = "instantaneous_proxy_energy"
        else:
            family = "unknown"
            expected_key = None

        energy_keys = (
            "hopfield_energy",
            "pc_free_energy",
            "augmented_lagrangian",
            "spike_proxy_energy",
            "instantaneous_proxy_energy",
            "free_energy",
        )
        energy_row = [
            f"{metrics.get(k, float('nan')):.2f}" if k in metrics else "--"
            for k in energy_keys
        ]

        # Check that the expected family metric is present
        if expected_key and expected_key not in metrics:
            energy_gaps.append(f"{dynamics}: expected {expected_key} not found")

        print(
            f"{dynamics:<24}{family:<22}{energy_row[0]:>10}{energy_row[1]:>10}"
            f"{energy_row[2]:>10}{energy_row[3]:>10}{energy_row[4]:>10}{energy_row[5]:>10}"
        )

    print(f"\nenergy gaps ({len(energy_gaps)}):")
    for gap in energy_gaps:
        print(f"  {gap}")
    if not energy_gaps:
        print("  no gaps: every dynamics produced its family-specific energy metric")


if __name__ == "__main__":
    main()
