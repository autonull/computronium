"""Probe: verify min_singular_value against independent nonnormal operator.

TODO51 B5: min_singular_value = 0.93 against sigma_max = 1.005. Condition
number of 1.08 is mild for an operator measured to sit on the unit circle.
If the Jacobian is subtly wrong, every metric in Part A's campaigns is
wrong with it; if the operator is genuinely only mildly nonnormal, this is
a footnote. Cheap to settle against an independently constructed nonnormal
operator.

Run: uv run python -m scripts.probes.t51_nonnormality_verification_probe
"""

from __future__ import annotations

import torch

from computronium.experiment.execution.compose import compose_cell_system
from computronium.experiment.execution.evaluate import compute_stability_metrics
from computronium.experiment.execution.settle_operator import settle_step_operator
from computronium.experiment.schema.coordinate import Coordinate


def _system(
    dynamics: str,
    credit: str,
    geometry: str = "feedforward",
    hidden: int = 64,
    layers: int = 3,
):
    return compose_cell_system(
        coordinate=Coordinate(
            substrate="digital",
            geometry=geometry,
            dynamics=dynamics,
            plasticity="null",
            credit=credit,
            update="euclidean",
            params={"hidden_dim": hidden, "num_layers": layers, "settle_step": 0.1},
        ),
        geometry={},
        input_shape=(64,),
        output_dim=10,
        param_budget=2_000_000,
    ).system


def _radius(jac: torch.Tensor) -> float:
    singular = torch.linalg.svdvals(jac)
    if jac.shape[0] == jac.shape[1]:
        return float(torch.linalg.eigvals(jac).abs().max().item())
    return float(singular.max().item())


def main() -> None:
    torch.manual_seed(0)

    print("=== 1. Reference: Known nonnormal operators ===")
    print()

    # Jordan block (highly nonnormal)
    n = 10
    jordan = torch.eye(n) + torch.diag(torch.ones(n - 1), diagonal=1) * 0.1
    svd_jordan = torch.linalg.svdvals(jordan)
    eig_jordan = torch.linalg.eigvals(jordan)
    rho_jordan = float(eig_jordan.abs().max().item())
    sigma_max_jordan = float(svd_jordan.max().item())
    sigma_min_jordan = float(svd_jordan.min().item())
    print("Jordan block (1 on diag, 0.1 on superdiag):")
    print(
        f"  rho={rho_jordan:.4f}, sigma_max={sigma_max_jordan:.4f}, sigma_min={sigma_min_jordan:.4f}"
    )
    print(
        f"  condition number={sigma_max_jordan / sigma_min_jordan:.4f}, nonnormality={sigma_max_jordan / rho_jordan:.4f}"
    )
    print()

    # Triangular matrix with growing entries (nonnormal)
    tri = torch.triu(torch.ones(n, n) * 0.5)
    torch.diagonal(tri)[:] = 1.0
    svd_tri = torch.linalg.svdvals(tri)
    eig_tri = torch.linalg.eigvals(tri)
    rho_tri = float(eig_tri.abs().max().item())
    sigma_max_tri = float(svd_tri.max().item())
    sigma_min_tri = float(svd_tri.min().item())
    print("Upper triangular (1 on diag, 0.5 above):")
    print(
        f"  rho={rho_tri:.4f}, sigma_max={sigma_max_tri:.4f}, sigma_min={sigma_min_tri:.4f}"
    )
    print(
        f"  condition number={sigma_max_tri / sigma_min_tri:.4f}, nonnormality={sigma_max_tri / rho_tri:.4f}"
    )
    print()

    # Nearly defective matrix
    near_def = torch.tensor([[1.0, 100.0], [0.0, 1.0]])
    svd_nd = torch.linalg.svdvals(near_def)
    eig_nd = torch.linalg.eigvals(near_def)
    rho_nd = float(eig_nd.abs().max().item())
    sigma_max_nd = float(svd_nd.max().item())
    sigma_min_nd = float(svd_nd.min().item())
    print("Nearly defective [[1, 100], [0, 1]]:")
    print(
        f"  rho={rho_nd:.4f}, sigma_max={sigma_max_nd:.4f}, sigma_min={sigma_min_nd:.4f}"
    )
    print(
        f"  condition number={sigma_max_nd / sigma_min_nd:.4f}, nonnormality={sigma_max_nd / rho_nd:.4f}"
    )
    print()

    print("=== 2. Settle-step Jacobians from real cells ===")
    print()

    configs = [
        ("energy_minimization", "thermodynamic_contrast", "feedforward"),
        ("instantaneous", "gradient", "feedforward"),
        ("predictive_settling", "thermodynamic_contrast", "feedforward"),
        ("error_predictive_coding", "thermodynamic_contrast", "feedforward"),
        ("pc_alm", "thermodynamic_contrast", "feedforward"),
        ("lazy", "gradient", "feedforward"),
    ]

    print(
        f"{'dynamics':<28}{'credit':<28}{'width':>6}{'rho':>8}{'sigma_max':>10}{'sigma_min':>10}{'cond':>8}{'nonnorm':>9}"
    )
    print("-" * 115)

    for dynamics, credit, geometry in configs:
        system = _system(dynamics, credit, geometry)
        x = torch.randn(4, 64)

        operator = settle_step_operator(system, x)
        if operator is None:
            print(
                f"{dynamics:<28}{credit:<28}{'N/A':>6}{'N/A':>8}{'N/A':>10}{'N/A':>10}{'N/A':>8}{'N/A':>9}"
            )
            continue

        step, width = operator
        jac = torch.autograd.functional.jacobian(step, torch.zeros(width))
        svd = torch.linalg.svdvals(jac)
        rho = _radius(jac)
        sigma_max = float(svd.max().item())
        sigma_min = float(svd.min().item())
        cond = sigma_max / max(sigma_min, 1e-10)
        nonnorm = sigma_max / max(rho, 1e-10)

        print(
            f"{dynamics:<28}{credit:<28}{width:>6}{rho:>8.4f}{sigma_max:>10.4f}{sigma_min:>10.4f}{cond:>8.2f}{nonnorm:>9.2f}"
        )

    print()

    print("=== 3. Full stability metrics (from evaluator) ===")
    print()

    for dynamics, credit, geometry in configs:
        system = _system(dynamics, credit, geometry)
        x = torch.randn(4, 64)
        metrics = compute_stability_metrics(system, x)

        rho = metrics.get("spectral_radius", 0.0)
        sigma_max = metrics.get("max_singular_value", 0.0)
        sigma_min = metrics.get("min_singular_value", 0.0)
        cond = sigma_max / max(sigma_min, 1e-10)
        nonnorm = metrics.get("nonnormality", 0.0)

        print(
            f"{dynamics:<28}{credit:<28}{rho:>8.4f}{sigma_max:>10.4f}{sigma_min:>10.4f}{cond:>8.2f}{nonnorm:>9.2f}"
        )

    print()

    print("=== 4. Check: Jacobian symmetry (should be asymmetric for nonnormal) ===")
    print()

    system = _system(
        "energy_minimization",
        "thermodynamic_contrast",
        "feedforward",
        hidden=32,
        layers=2,
    )
    x = torch.randn(4, 64)
    operator = settle_step_operator(system, x)
    if operator:
        step, width = operator
        jac = torch.autograd.functional.jacobian(step, torch.zeros(width))
        sym_part = (jac + jac.T) / 2
        skew_part = (jac - jac.T) / 2
        sym_norm = torch.linalg.matrix_norm(sym_part).item()
        skew_norm = torch.linalg.matrix_norm(skew_part).item()
        print(f"Symmetric part norm: {sym_norm:.4f}")
        print(f"Skew-symmetric part norm: {skew_norm:.4f}")
        print(f"Ratio (skew/sym): {skew_norm / max(sym_norm, 1e-10):.4f}")

        # Check if Jacobian is nearly normal (commutes with its transpose)
        jac_t_jac = jac.T @ jac
        jac_jac_t = jac @ jac.T
        commutator_norm = torch.linalg.matrix_norm(jac_t_jac - jac_jac_t).item()
        print(f"Commutator ||J^T J - J J^T||: {commutator_norm:.4f}")

    print()
    print("=== Summary ===")
    print("If settle-step Jacobians show mild nonnormality (condition ~1.08,")
    print("nonnormality ~1.01) like the reference Jordan block with small")
    print("superdiagonal, the operator is likely correct but genuinely mild.")
    print("If they match the highly nonnormal references, there's a bug.")


if __name__ == "__main__":
    main()
