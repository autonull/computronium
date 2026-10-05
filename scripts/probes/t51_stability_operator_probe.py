"""Probe: the per-step transition operator vs the whole-settle map.

Informed the TODO51 §2 fix. Campaign 2's phase diagram is (rho, sigma_max)
of the *settle step*, but `compute_stability_metrics` differentiated the
whole `settle()` w.r.t. the input x. That Jacobian is the N-step map,
J_total ~ J^N, so it reports rho_step^N (0.0087 at N=30) and cannot
separate transient amplification (sigma_max > 1) from contraction
(rho < 1) — the exact distinction the frontier is about.

This probe measures both operators on the same trained cell and prints
them side by side, plus the reference rho from the `stability` package's
own `spectral_radius_from_jacobian`.

Run: uv run python -m scripts.probes.t51_stability_operator_probe
"""

from __future__ import annotations

from typing import cast

import torch
from torch import Tensor

from computronium.experiment.execution.compose import compose_cell_system
from computronium.experiment.schema.coordinate import Coordinate, Schedule
from computronium.ontology import SystemState


def _coord(hidden: int = 64, step_size: float = 0.1) -> Coordinate:
    return Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="energy_minimization",
        plasticity="null",
        credit="thermodynamic_contrast",
        update="euclidean",
        params={
            "hidden_dim": hidden,
            "num_layers": 3,
            "settle_step": step_size,
            "settle_beta": 0.5,
            "feedback_scale": 0.5,
            "precision": "float32",
        },
    )


def _acts(system, x: Tensor) -> list[Tensor]:
    return list(system.geometry.forward_with_intermediates(x, system.substrate))


def whole_settle_jacobian(system, x: Tensor) -> Tensor:
    """What the campaign measures today: d(settled acts)/d(x)."""
    from torch.autograd.functional import jacobian

    def fn(x_in: Tensor) -> Tensor:
        state = SystemState(x=x_in, y=None)
        settled = system.dynamics.settle(state, system.geometry, system.substrate)
        return settled.activations[-1]

    return cast("Tensor", jacobian(fn, x[:1])[0, :, 0, :])


def step_jacobian(system, x: Tensor) -> Tensor:
    """d(one settle step's last hidden acts)/d(same), via the kernel."""
    from computronium.ontology._settle_kernel import (
        SubstrateSettleKernel,
        extract_layered_params,
    )

    base = [a[:1] for a in _acts(system, x)]  # one sample, full depth
    params = extract_layered_params(system.geometry)
    assert params is not None
    kernel = SubstrateSettleKernel(
        substrate=system.substrate,
        params=params,
        step_size=system.dynamics.config.step_size,
        momentum=system.dynamics.config.momentum,
        residual=params.residual,
    )
    last = -2  # last hidden slot; slot -1 is the output layer
    h = base[last][0]

    def fn(h_in: Tensor) -> Tensor:
        acts = [*base[:-2], h_in.unsqueeze(0), base[-1]]
        out, _ = kernel.step(acts, 0.0, None, None)
        return out[last][0]

    return cast("Tensor", torch.autograd.functional.jacobian(fn, h))


def main() -> None:
    torch.manual_seed(0)
    schedule = Schedule(
        fidelity="L1",
        seed=0,
        n_seeds=1,
        epochs=1,
        batch_limit=2,
        budget_id="probe",
        task_id="digits",
        param_budget=500000,
        device="cpu",
        deterministic=True,
        num_workers=0,
    )
    cell = compose_cell_system(
        coordinate=_coord(),
        geometry={},
        input_shape=(64,),
        output_dim=10,
        param_budget=500000,
    )
    system = cell.system
    x = torch.randn(4, 64)

    total = whole_settle_jacobian(system, x)
    step = step_jacobian(system, x)

    for label, jac in (("whole-settle d(out)/dx", total), ("one-step dh/dh", step)):
        sv = torch.linalg.svdvals(jac)
        rho = (
            torch.linalg.eigvals(jac).abs().max().item()
            if jac.shape[0] == jac.shape[1]
            else float("nan")
        )
        print(
            f"{label:24s} shape={tuple(jac.shape)!s:12s} "
            f"rho={rho:.4f} sigma_max={sv.max().item():.4f} "
            f"sigma_min={sv.min().item():.6f}"
        )

    horizon = system.dynamics.config.max_steps
    rho_step = torch.linalg.eigvals(step).abs().max().item()
    print(
        f"\nhorizon={horizon}  rho_step={rho_step:.4f}  rho_step^N={rho_step**horizon:.3e}"
    )


if __name__ == "__main__":
    main()
