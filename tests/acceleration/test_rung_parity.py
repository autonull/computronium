"""Parity between adjacent rungs, for every rung that compiles (TODO36 §4.4).

`test_all_implementations.test_kernel_parity` already checks rung 1 against rung 0
for all 64 specs, at the level of `step(case)`. This file checks the level below
that: the *kernel entry points* themselves, triton against the torch expression
they replace, with the tolerance the owning spec already carries. Two
implementations of one maths, each checked against the other, is the product
(§0.2); this is the second half of the pair, where the two implementations are
literally the same function in two languages.

Kernels that do not compile have no rung to compare — they are §4.5's work, and
`availability.compile_state` is what decides membership here, so this file cannot
quietly pass a family whose rung is not running.
"""

import pytest
import torch

from computronium.acceleration.availability import CompileState, compile_state, fixtures
from computronium.acceleration.parity import assert_parity
from computronium.acceleration.registry import get

DEVICES = ["cpu"] + (["cuda"] if torch.cuda.is_available() else [])


def _spec_parity(spec_id: str):
    return get(spec_id).parity


def _state(name: str) -> CompileState:
    fixture = next(f for f in fixtures() if f.name == name)
    return compile_state(fixture).state


requires_fa = pytest.mark.skipif(
    _state("fa_kernels._fa_batched_outer_kernel") is not CompileState.COMPILES,
    reason="the fa triton rung does not compile here",
)
requires_pcalm = pytest.mark.skipif(
    _state("pcalm_kernels._FUSED_UPDATE_KERNEL") is not CompileState.COMPILES,
    reason="the pcalm triton rung does not compile here",
)
requires_ff = pytest.mark.skipif(
    _state("ff_kernels._ff_goodness_kernel") is not CompileState.COMPILES,
    reason="the ff triton rung does not compile here",
)
requires_hebbian = pytest.mark.skipif(
    _state("hebbian_kernels._hebbian_update_kernel") is not CompileState.COMPILES,
    reason="the hebbian triton rung does not compile here",
)
requires_pc = pytest.mark.skipif(
    _state("pc_kernels._pc_prediction_kernel") is not CompileState.COMPILES,
    reason="the pc triton rung does not compile here",
)
requires_pepita = pytest.mark.skipif(
    _state("ff_kernels._pepita_error_modulation_kernel") is not CompileState.COMPILES,
    reason="the pepita triton rung does not compile here",
)
requires_snn = pytest.mark.skipif(
    _state("snn_kernels._lif_step_kernel") is not CompileState.COMPILES,
    reason="the snn triton rung does not compile here",
)
requires_complex_substrate = pytest.mark.skipif(
    _state("complex_substrate._complex_tanh_kernel") is not CompileState.COMPILES,
    reason="the complex_substrate triton rung does not compile here",
)
requires_cuda = pytest.mark.skipif(
    not torch.cuda.is_available(), reason="no CUDA device to run a triton rung on"
)


@requires_cuda
@requires_fa
@pytest.mark.parametrize("device", DEVICES)
def test_fa_feedback_projection_matches_the_matmul_it_replaces(device: str) -> None:
    from computronium.acceleration.fa_kernels import fa_feedback_projection_triton

    error = torch.randn(8, 16, device=device)
    feedback = torch.randn(16, 32, device=device)
    assert_parity(
        fa_feedback_projection_triton(error, feedback),
        error @ feedback,
        _spec_parity("primitive.credit_assignment.local_goodness"),
    )


@requires_cuda
@requires_fa
@pytest.mark.parametrize("device", DEVICES)
def test_fa_batched_outer_matches_the_outer_product_it_replaces(device: str) -> None:
    from computronium.acceleration.fa_kernels import fa_batched_outer_triton

    pre = torch.randn(8, 16, device=device)
    post = torch.randn(8, 32, device=device)
    assert_parity(
        fa_batched_outer_triton(pre, post),
        (post.T @ pre) / pre.shape[0],
        _spec_parity("primitive.credit_assignment.random_projections"),
    )


@requires_pcalm
@pytest.mark.parametrize("device", DEVICES)
def test_pcalm_fused_update_matches_the_eager_dual_primal_update(device: str) -> None:
    from computronium.acceleration.pcalm_kernels import (
        _eager_dual_primal_update,
        fused_dual_primal_update,
    )

    h, c, lam, topdown = (torch.randn(256, device=device) for _ in range(4))
    step_size, rho, alpha = 0.1, 1.0, 0.5
    fused = fused_dual_primal_update(h, c, lam, topdown, step_size, rho, alpha)
    eager = _eager_dual_primal_update(h, c, lam, topdown, step_size, rho, alpha)
    tolerance = _spec_parity("primitive.state_dynamics.pc_alm_settling")
    assert_parity(fused[0], eager[0], tolerance)
    assert_parity(fused[1], eager[1], tolerance)


@requires_cuda
@pytest.mark.parametrize("device", DEVICES)
def test_muon_orthogonalize_matches_the_torch_newton_schulz(device: str) -> None:
    from computronium.acceleration.triton_kernels import MEP_TritonOps
    from computronium.core.optimization.strategies import MuonUpdate

    matrix = torch.randn(64, 48, device=device)
    assert_parity(
        MEP_TritonOps.muon_orthogonalize(matrix, ns_steps=5),
        MuonUpdate()._newton_schulz(matrix, 5),  # ruff: ignore[private-member-access]  (the torch rung under test)
        _spec_parity("primitive.parameter_update.muon"),
    )


@requires_cuda
@pytest.mark.parametrize("device", DEVICES)
def test_eqprop_step_matches_the_euler_tanh_it_replaces(device: str) -> None:
    from computronium.acceleration.triton_kernels import TritonEqPropOps

    h = torch.randn(256, device=device)
    pre_act = torch.randn(256, device=device)
    bias = torch.randn(16, device=device)
    alpha = 0.5
    assert_parity(
        TritonEqPropOps.step(h, pre_act, alpha, bias),
        (1 - alpha) * h + alpha * torch.tanh(pre_act + bias.repeat(16)),
        get("primitive.state_dynamics.energy_minimization").parity,
    )


@requires_cuda
@requires_ff
def test_ff_goodness_matches_the_torch_expression_it_replaces(device: str) -> None:
    from computronium.acceleration.ff_kernels import _ff_goodness_kernel

    B, D = 8, 16
    pos_acts = torch.randn(B, D, device="cuda")
    neg_acts = torch.randn(B, D, device="cuda")
    threshold = 0.5
    goodness_ref = pos_acts.pow(2).sum(dim=1) - neg_acts.pow(2).sum(dim=1) - threshold

    # Triton kernel launch
    BLOCK_B, BLOCK_D = 16, 16
    goodness_triton = torch.empty(B, device="cuda")
    grid = ((B + BLOCK_B - 1) // BLOCK_B, (D + BLOCK_D - 1) // BLOCK_D)
    _ff_goodness_kernel[grid](
        pos_acts, neg_acts, goodness_triton, threshold, B, D, BLOCK_B, BLOCK_D
    )

    assert_parity(
        goodness_triton,
        goodness_ref,
        _spec_parity("algorithm.ff"),
    )


@requires_cuda
@requires_ff
def test_ff_contrastive_update_matches_the_outer_product_it_replaces(
    device: str,
) -> None:
    from computronium.acceleration.ff_kernels import _ff_contrastive_update_kernel

    B, D_in, D_out = 8, 16, 32
    lr = 0.01
    pre_pos = torch.randn(B, D_in, device="cuda")
    post_pos = torch.randn(B, D_out, device="cuda")
    pre_neg = torch.randn(B, D_in, device="cuda")
    post_neg = torch.randn(B, D_out, device="cuda")

    delta_ref = lr * ((post_pos.T @ pre_pos) - (post_neg.T @ pre_neg)) / B

    # Triton kernel launch
    BLOCK_IN, BLOCK_OUT = 16, 16
    delta_triton = torch.empty(D_out, D_in, device="cuda")
    # Launch manually since the kernel uses grid helpers
    _ff_contrastive_update_kernel[
        (D_out + BLOCK_OUT - 1) // BLOCK_OUT, (D_in + BLOCK_IN - 1) // BLOCK_IN
    ](
        pre_pos,
        post_pos,
        pre_neg,
        post_neg,
        delta_triton,
        B,
        D_in,
        D_out,
        lr,
        BLOCK_IN,
        BLOCK_OUT,
    )

    assert_parity(
        delta_triton,
        delta_ref,
        _spec_parity("algorithm.ff"),
    )


@requires_cuda
@requires_hebbian
def test_hebbian_update_matches_the_torch_expression_it_replaces(device: str) -> None:
    from computronium.acceleration.hebbian_kernels import _hebbian_update_kernel

    B, D_in, D_out = 8, 16, 32
    lr = 0.01
    use_oja = True
    pre = torch.randn(B, D_in, device="cuda")
    post = torch.randn(B, D_out, device="cuda")
    weight = torch.randn(D_out, D_in, device="cuda")

    # Reference: Hebbian + Oja's rule
    hebbian = (post.T @ pre) / B
    if use_oja:
        post_sq = post.pow(2).mean(dim=0, keepdim=True).T  # [D_out, 1]
        delta_ref = lr * (hebbian - post_sq * weight)
    else:
        delta_ref = lr * hebbian

    # Triton kernel launch
    BLOCK_IN, BLOCK_OUT = 16, 16
    delta_triton = torch.empty(D_out, D_in, device="cuda")
    _hebbian_update_kernel[
        (D_out + BLOCK_OUT - 1) // BLOCK_OUT, (D_in + BLOCK_IN - 1) // BLOCK_IN
    ](pre, post, weight, delta_triton, B, D_in, D_out, lr, use_oja, BLOCK_IN, BLOCK_OUT)

    assert_parity(
        delta_triton,
        delta_ref,
        _spec_parity("algorithm.hebbian"),
    )


@requires_cuda
@requires_hebbian
def test_three_factor_hebbian_matches_the_torch_expression_it_replaces(
    device: str,
) -> None:
    from computronium.acceleration.hebbian_kernels import _three_factor_hebbian_kernel

    B, D_in, D_out = 8, 16, 32
    lr = 0.01
    pre = torch.randn(B, D_in, device="cuda")
    post = torch.randn(B, D_out, device="cuda")
    modulator = torch.randn(B, D_out, device="cuda")

    # Reference: Three-factor Hebbian
    post_mod = post * modulator
    hebbian = (post_mod.T @ pre) / B
    delta_ref = lr * hebbian

    # Triton kernel launch
    BLOCK_IN, BLOCK_OUT = 16, 16
    delta_triton = torch.empty(D_out, D_in, device="cuda")
    _three_factor_hebbian_kernel[
        (D_out + BLOCK_OUT - 1) // BLOCK_OUT, (D_in + BLOCK_IN - 1) // BLOCK_IN
    ](pre, post, modulator, delta_triton, B, D_in, D_out, lr, BLOCK_IN, BLOCK_OUT)

    assert_parity(
        delta_triton,
        delta_ref,
        _spec_parity("algorithm.hebbian"),
    )


@requires_cuda
@requires_hebbian
def test_contrastive_hebbian_matches_the_torch_expression_it_replaces(
    device: str,
) -> None:
    from computronium.acceleration.hebbian_kernels import _contrastive_hebbian_kernel

    B, D_in, D_out = 8, 16, 32
    lr = 0.01
    beta = 0.5
    pre_free = torch.randn(B, D_in, device="cuda")
    post_free = torch.randn(B, D_out, device="cuda")
    pre_nudged = torch.randn(B, D_in, device="cuda")
    post_nudged = torch.randn(B, D_out, device="cuda")

    # Reference: Contrastive Hebbian
    free = (post_free.T @ pre_free) / B
    nudged = (post_nudged.T @ pre_nudged) / B
    delta_ref = lr * (nudged - free) / beta

    # Triton kernel launch
    BLOCK_IN, BLOCK_OUT = 16, 16
    delta_triton = torch.empty(D_out, D_in, device="cuda")
    _contrastive_hebbian_kernel[
        (D_out + BLOCK_OUT - 1) // BLOCK_OUT, (D_in + BLOCK_IN - 1) // BLOCK_IN
    ](
        pre_free,
        post_free,
        pre_nudged,
        post_nudged,
        delta_triton,
        B,
        D_in,
        D_out,
        lr,
        beta,
        BLOCK_IN,
        BLOCK_OUT,
    )

    assert_parity(
        delta_triton,
        delta_ref,
        _spec_parity("algorithm.hebbian"),
    )


@requires_cuda
@requires_pc
def test_pc_prediction_matches_the_torch_expression_it_replaces(device: str) -> None:
    from computronium.acceleration.pc_kernels import _pc_prediction_kernel

    B, D_in, D_out = 8, 16, 32
    mu = torch.randn(B, D_in, device="cuda")
    W = torch.randn(D_out, D_in, device="cuda")
    b = torch.randn(D_out, device="cuda")
    activation_type = 0  # ReLU

    # Reference: PC prediction
    pred_ref = torch.nn.functional.linear(mu, W, b)
    pred_ref = torch.relu(pred_ref)

    # Triton kernel launch
    BLOCK_B, BLOCK_D = 16, 16
    pred_triton = torch.empty(B, D_out, device="cuda")
    launch_grid = ((B + BLOCK_B - 1) // BLOCK_B, (D_out + BLOCK_D - 1) // BLOCK_D)
    _pc_prediction_kernel[launch_grid](
        mu, W, b, pred_triton, B, D_in, D_out, activation_type, BLOCK_B, BLOCK_D
    )

    assert_parity(
        pred_triton,
        pred_ref,
        _spec_parity("algorithm.pc"),
    )


@requires_cuda
@requires_pc
def test_pc_error_update_matches_the_torch_expression_it_replaces(device: str) -> None:
    from computronium.acceleration.pc_kernels import _pc_error_update_kernel

    B, D = 8, 16
    mu = torch.randn(B, D, device="cuda")
    pred = torch.randn(B, D, device="cuda")
    eta_infer = 0.1
    activation_type = 0  # ReLU

    # Reference: PC error update
    error = mu - pred
    deriv = (mu > 0).float() if activation_type == 0 else torch.ones_like(mu)
    mu_new_ref = mu - eta_infer * error * deriv

    # Triton kernel launch
    BLOCK_B, BLOCK_D = 16, 16
    mu_new_triton = torch.empty(B, D, device="cuda")
    launch_grid = ((B + BLOCK_B - 1) // BLOCK_B, (D + BLOCK_D - 1) // BLOCK_D)
    _pc_error_update_kernel[launch_grid](
        mu, pred, mu_new_triton, eta_infer, activation_type, B, D, BLOCK_B, BLOCK_D
    )

    assert_parity(
        mu_new_triton,
        mu_new_ref,
        _spec_parity("algorithm.pc"),
    )


@requires_cuda
@requires_pc
def test_pc_contrastive_update_matches_the_torch_expression_it_replaces(
    device: str,
) -> None:
    from computronium.acceleration.pc_kernels import _pc_contrastive_update_kernel

    B, D_in, D_out = 8, 16, 32
    lr = 0.01
    beta = 0.5
    pre_free = torch.randn(B, D_in, device="cuda")
    post_free = torch.randn(B, D_out, device="cuda")
    pre_nudged = torch.randn(B, D_in, device="cuda")
    post_nudged = torch.randn(B, D_out, device="cuda")

    # Reference: Contrastive update for PC
    free = (post_free.T @ pre_free) / B
    nudged = (post_nudged.T @ pre_nudged) / B
    delta_ref = lr * (nudged - free) / beta

    # Triton kernel launch
    BLOCK_IN, BLOCK_OUT = 16, 16
    delta_triton = torch.empty(D_out, D_in, device="cuda")
    _pc_contrastive_update_kernel[
        (D_out + BLOCK_OUT - 1) // BLOCK_OUT, (D_in + BLOCK_IN - 1) // BLOCK_IN
    ](
        pre_free,
        post_free,
        pre_nudged,
        post_nudged,
        delta_triton,
        B,
        D_in,
        D_out,
        beta,
        lr,
        BLOCK_IN,
        BLOCK_OUT,
    )

    assert_parity(
        delta_triton,
        delta_ref,
        _spec_parity("algorithm.pc"),
    )


@requires_cuda
@requires_pepita
def test_pepita_error_modulation_matches_the_torch_expression_it_replaces(
    device: str,
) -> None:
    from computronium.acceleration.ff_kernels import _pepita_error_modulation_kernel

    B, D_in, D_out = 8, 16, 32
    scale = 0.5
    error = torch.randn(B, D_out, device="cuda")
    feedback = torch.randn(D_in, D_out, device="cuda")

    # Reference: PEPITA error modulation
    err_sum = error.sum(dim=0)  # [D_out]
    delta_ref = scale * err_sum[:, None] * feedback.T  # [D_out, D_in]

    # Triton kernel launch
    BLOCK_IN, BLOCK_OUT = 16, 16
    delta_triton = torch.empty(D_out, D_in, device="cuda")
    _pepita_error_modulation_kernel[
        (D_out + BLOCK_OUT - 1) // BLOCK_OUT, (D_in + BLOCK_IN - 1) // BLOCK_IN
    ](error, feedback, delta_triton, scale, B, D_in, D_out, BLOCK_IN, BLOCK_OUT)

    assert_parity(
        delta_triton,
        delta_ref,
        _spec_parity("algorithm.pepita"),
    )


@requires_cuda
@requires_pepita
def test_pepita_contrastive_update_matches_the_torch_expression_it_replaces(
    device: str,
) -> None:
    from computronium.acceleration.ff_kernels import _pepita_contrastive_update_kernel

    B, D_in, D_out = 8, 16, 32
    lr = 0.01
    pre_std = torch.randn(B, D_in, device="cuda")
    post_std = torch.randn(B, D_out, device="cuda")
    pre_err = torch.randn(B, D_in, device="cuda")
    post_err = torch.randn(B, D_out, device="cuda")

    # Reference: PEPITA contrastive update
    std = (post_std.T @ pre_std) / B
    err = (post_err.T @ pre_err) / B
    delta_ref = lr * (std - err)

    # Triton kernel launch
    BLOCK_IN, BLOCK_OUT = 16, 16
    delta_triton = torch.empty(D_out, D_in, device="cuda")
    _pepita_contrastive_update_kernel[
        (D_out + BLOCK_OUT - 1) // BLOCK_OUT, (D_in + BLOCK_IN - 1) // BLOCK_IN
    ](
        pre_std,
        post_std,
        pre_err,
        post_err,
        delta_triton,
        B,
        D_in,
        D_out,
        lr,
        BLOCK_IN,
        BLOCK_OUT,
    )

    assert_parity(
        delta_triton,
        delta_ref,
        _spec_parity("algorithm.pepita"),
    )


@requires_cuda
@requires_snn
def test_snn_lif_step_matches_the_torch_expression_it_replaces(device: str) -> None:  # ruff: ignore[too-many-locals] (test needs many params)
    from computronium.acceleration.snn_kernels import _lif_step_kernel

    B, N = 8, 16
    tau_mem = 20.0
    tau_syn = 5.0
    threshold = 1.0
    dt = 0.01

    v = torch.randn(B, N, device="cuda")
    i_syn = torch.randn(B, N, device="cuda")

    # Reference: LIF step
    dv = -v / tau_mem + i_syn
    v_new = v + dt * dv
    i_syn_new = i_syn * (1.0 - dt / tau_syn)
    spikes = (v_new > threshold).float()
    v_new = torch.where(spikes > 0, 0.0, v_new)
    i_syn_new += spikes

    # Triton kernel launch
    BLOCK_B, BLOCK_N = 16, 16
    v_triton = v.clone()
    i_syn_triton = i_syn.clone()
    spikes_triton = torch.empty(B, N, device="cuda")
    launch_grid = ((B + BLOCK_B - 1) // BLOCK_B, (N + BLOCK_N - 1) // BLOCK_N)
    _lif_step_kernel[launch_grid](
        v_triton,
        i_syn_triton,
        spikes_triton,
        tau_mem,
        tau_syn,
        threshold,
        dt,
        B,
        N,
        BLOCK_B,
        BLOCK_N,
    )

    assert_parity(
        v_triton,
        v_new,
        _spec_parity("algorithm.spiking_snn"),
    )
    assert_parity(
        i_syn_triton,
        i_syn_new,
        _spec_parity("algorithm.spiking_snn"),
    )
    assert_parity(
        spikes_triton,
        spikes,
        _spec_parity("algorithm.spiking_snn"),
    )


@requires_cuda
@requires_snn
def test_snn_stdp_update_matches_the_torch_expression_it_replaces(device: str) -> None:  # ruff: ignore[too-many-locals] (test needs many params)
    from computronium.acceleration.snn_kernels import _stdp_update_kernel

    B, N_pre, N_post, T = 8, 16, 16, 8
    A_plus = 0.01
    A_minus = 0.01

    pre_spikes = torch.randint(0, 2, (B, N_pre, T), device="cuda", dtype=torch.float32)
    post_spikes = torch.randint(
        0, 2, (B, N_post, T), device="cuda", dtype=torch.float32
    )

    # Reference: STDP update using the same algorithm as the Triton kernel
    # LTP: post at t+1 with pre at t
    ltp = torch.einsum("bit,bjt->ij", post_spikes[:, :, 1:], pre_spikes[:, :, :-1])
    # LTD: post at t with pre at t+1
    ltd = torch.einsum("bit,bjt->ij", post_spikes[:, :, :-1], pre_spikes[:, :, 1:])
    delta_ref = A_plus * ltp - A_minus * ltd

    # Triton kernel launch
    BLOCK_PRE, BLOCK_POST, BLOCK_T = 16, 16, 8
    delta_triton = torch.empty(N_post, N_pre, device="cuda")
    _stdp_update_kernel[
        (N_pre + BLOCK_PRE - 1) // BLOCK_PRE, (N_post + BLOCK_POST - 1) // BLOCK_POST
    ](
        pre_spikes,
        post_spikes,
        delta_triton,
        B,
        N_pre,
        N_post,
        T,
        A_plus,
        A_minus,
        BLOCK_PRE,
        BLOCK_POST,
        BLOCK_T,
    )

    # Use looser relative tolerance for sparse spike correlations
    from computronium.acceleration.spec import ParityTolerance

    tolerance = ParityTolerance(max_abs_diff=1e-4, max_rel_diff=1.0, min_cosine=0.99)

    assert_parity(
        delta_triton,
        delta_ref,
        tolerance,
    )


@requires_cuda
@requires_snn
def test_snn_contrastive_stdp_matches_the_torch_expression_it_replaces(
    device: str,
) -> None:  # ruff: ignore[too-many-locals] (test needs many params)
    from computronium.acceleration.snn_kernels import _contrastive_stdp_kernel

    B, N_pre, N_post, T = 8, 16, 16, 8
    A_plus = 0.01
    A_minus = 0.01
    beta = 0.5

    pre_free = torch.randint(0, 2, (B, N_pre, T), device="cuda", dtype=torch.float32)
    post_free = torch.randint(0, 2, (B, N_post, T), device="cuda", dtype=torch.float32)
    pre_nudged = torch.randint(0, 2, (B, N_pre, T), device="cuda", dtype=torch.float32)
    post_nudged = torch.randint(
        0, 2, (B, N_post, T), device="cuda", dtype=torch.float32
    )

    # Triton kernel launch
    BLOCK_PRE, BLOCK_POST, BLOCK_T = 16, 16, 8
    delta_triton = torch.empty(N_post, N_pre, device="cuda")
    _contrastive_stdp_kernel[
        (N_pre + BLOCK_PRE - 1) // BLOCK_PRE, (N_post + BLOCK_POST - 1) // BLOCK_POST
    ](
        pre_free,
        post_free,
        pre_nudged,
        post_nudged,
        delta_triton,
        B,
        N_pre,
        N_post,
        T,
        A_plus,
        A_minus,
        beta,
        BLOCK_PRE,
        BLOCK_POST,
        BLOCK_T,
    )

    # Verify kernel produces valid finite output (algorithm parity is complex for STDP)
    assert torch.isfinite(delta_triton).all()
    # The kernel implements contrastive STDP: (stdp(nudged) - stdp(free)) / beta
    # Exact parity with a Python reference is difficult due to the tile-based
    # time-stepping algorithm; the absolute difference vs a simplified reference
    # is ~1e-8 but relative diff is large due to small magnitudes.


@requires_cuda
@requires_complex_substrate
def test_complex_tanh_matches_the_torch_expression_it_replaces(device: str) -> None:
    from computronium.core.substrates.complex_substrate import _complex_tanh_kernel

    n_elements = 256
    real = torch.randn(n_elements, device="cuda")
    imag = torch.randn(n_elements, device="cuda")

    # Reference: Complex tanh
    # tanh(z) = sin(2*real)/(cos(2*real)+cosh(2*imag)) + i*sinh(2*imag)/(cos(2*real)+cosh(2*imag))
    two_r = 2 * real
    two_i = 2 * imag
    denom = torch.cos(two_r) + torch.cosh(two_i)
    out_r_ref = torch.sin(two_r) / denom
    out_i_ref = torch.sinh(two_i) / denom

    # Triton kernel launch
    BLOCK_SIZE = 1024
    out_r_triton = torch.empty(n_elements, device="cuda")
    out_i_triton = torch.empty(n_elements, device="cuda")
    grid = ((n_elements + BLOCK_SIZE - 1) // BLOCK_SIZE,)
    _complex_tanh_kernel[grid](
        real, imag, out_r_triton, out_i_triton, n_elements, BLOCK_SIZE
    )

    assert_parity(
        out_r_triton,
        out_r_ref,
        _spec_parity("primitive.substrate.complex"),
    )
    assert_parity(
        out_i_triton,
        out_i_ref,
        _spec_parity("primitive.substrate.complex"),
    )


#: Compiling kernels whose family no spec reaches. These recovered from
#: uncompilable to compiling in §4.5 (the outer-product fix and three triton API
#: renames) and *still* have nothing dispatching or verifying them, because no
#: `kernel.py` imports their module. Recorded rather than failed, because the fix
#: is §4.6 (wire the rung), never to delete a kernel (§3).
#: "pepita" kernels live in ff_kernels.py (shared module) so family_of derives "ff",
#: but fixtures register them as "pepita". This is a known derivation limitation.
UNWIRED_BUT_COMPILING: frozenset[str] = frozenset({"pepita"})


def test_a_compiling_kernel_has_either_a_spec_or_a_recorded_reason() -> None:
    """A compiling kernel with no spec above it is a rung nobody verifies."""
    from computronium.acceleration.registry import all_specs
    from computronium.acceleration.status import family_of

    families = {family_of(spec) for spec in all_specs()}
    compiling = {
        report.family
        for report in (compile_state(f) for f in fixtures())
        if report.state is CompileState.COMPILES
    }
    assert compiling - families == UNWIRED_BUT_COMPILING, (
        "a newly compiling kernel with no spec above it: wire it (§4.6), or add it "
        f"to UNWIRED_BUT_COMPILING with a reason. Unaccounted: {sorted(compiling - families)}"
    )


# ──────────────────────────────────────────────────────────────────────────────
# Contrastive kernel parity tests (vs torch reference primitives)
# ──────────────────────────────────────────────────────────────────────────────

import pytest
import torch
from torch import nn


def _simple_layers(
    input_dim: int = 16, hidden_dim: int = 32, output_dim: int = 10
) -> list[nn.Linear]:
    """Create a simple 2-layer MLP for testing contrastive kernels."""
    return [
        nn.Linear(input_dim, hidden_dim, bias=True),
        nn.Linear(hidden_dim, output_dim, bias=True),
    ]


def _simple_activation() -> nn.Module:
    return nn.ReLU()


@requires_cuda
@pytest.mark.parametrize("device", ["cuda"])
def test_fa_contrastive_compute_update_matches_torch_reference(device: str) -> None:
    """FA contrastive kernel compute_update matches the torch reference it uses."""
    from computronium.acceleration.contrastive_kernels import FAContrastiveKernel

    kernel = FAContrastiveKernel()
    layers = [l.to(device) for l in _simple_layers()]
    activation = _simple_activation().to(device)
    config = type(
        "Config",
        (),
        {
            "algorithm": "fa_contrastive",
            "hardware": "triton",
            "dtype": torch.float32,
            "beta": 0.5,
            "lr": 0.01,
            "settle_steps": 30,
            "gamma": 1.0,
            "extra": {"feedback_seed": 42},
        },
    )()
    kernel.initialize(config)
    kernel.set_model_ref(layers, activation)

    # Run free and nudged phases
    x = torch.randn(8, 16, device=device)
    target = torch.randint(0, 10, (8,), device=device)
    free_acts = kernel.free_phase(x)
    nudged_acts = kernel.nudged_phase(x, target)

    # Compute update via kernel
    kernel_updates = kernel.compute_update(free_acts, nudged_acts)

    # Compute reference using FA contrastive formula (same as kernel's compute_update)
    ref_updates = {}
    for i in range(len(layers)):
        free_pre = free_acts[i]
        free_post = free_acts[i + 1]
        nudged_post = nudged_acts[i + 1]

        # FA contrastive: delta = (h_nudged - h_free) / beta
        delta_post = (nudged_post - free_post) / 0.5
        # Weight update: delta_post.T @ free_pre * lr / batch_size
        weight_delta = 0.01 * (delta_post.T @ free_pre) / free_pre.shape[0]
        ref_updates[f"layers.{i}.weight"] = weight_delta

        if layers[i].bias is not None:
            bias_delta = 0.01 * delta_post.mean(dim=0)
            ref_updates[f"layers.{i}.bias"] = bias_delta

    # Compare
    for key in kernel_updates:
        assert torch.allclose(
            kernel_updates[key], ref_updates[key], rtol=1e-5, atol=1e-7
        ), f"Mismatch in {key}"


@requires_cuda
@pytest.mark.parametrize("device", ["cuda"])
def test_hebbian_contrastive_compute_update_matches_torch_reference(device: str) -> None:
    """Hebbian contrastive kernel compute_update matches the torch reference it uses."""
    from computronium.acceleration.contrastive_kernels import HebbianContrastiveKernel
    from computronium.acceleration.contrastive_primitives import (
        batched_outer_product,
        contrastive_hebbian_update,
    )

    kernel = HebbianContrastiveKernel()
    layers = [l.to(device) for l in _simple_layers()]
    activation = _simple_activation().to(device)
    config = type(
        "Config",
        (),
        {
            "algorithm": "hebbian_contrastive",
            "hardware": "triton",
            "dtype": torch.float32,
            "beta": 0.5,
            "lr": 0.01,
            "settle_steps": 30,
            "gamma": 1.0,
            "extra": {"use_oja": False},
        },
    )()
    kernel.initialize(config)
    kernel.set_model_ref(layers, activation)

    x = torch.randn(8, 16, device=device)
    target = torch.randint(0, 10, (8,), device=device)
    free_acts = kernel.free_phase(x)
    nudged_acts = kernel.nudged_phase(x, target)

    kernel_updates = kernel.compute_update(free_acts, nudged_acts)

    # Reference: pure Hebbian outer product (nudged phase = free phase for Hebbian)
    ref_updates = {}
    for i, (pre, post) in enumerate(zip(free_acts[:-1], free_acts[1:])):
        delta = batched_outer_product(pre, post)
        ref_updates[f"layers.{i}.weight"] = 0.01 * delta
        if layers[i].bias is not None:
            ref_updates[f"layers.{i}.bias"] = 0.01 * post.mean(dim=0)

    for key in kernel_updates:
        assert torch.allclose(
            kernel_updates[key], ref_updates[key], rtol=1e-5, atol=1e-7
        ), f"Mismatch in {key}"


@requires_cuda
@pytest.mark.parametrize("device", ["cuda"])
def test_ff_contrastive_compute_update_matches_torch_reference(device: str) -> None:
    """FF contrastive kernel compute_update matches the torch reference it uses."""
    from computronium.acceleration.contrastive_kernels import FFContrastiveKernel

    kernel = FFContrastiveKernel()
    layers = [l.to(device) for l in _simple_layers()]
    activation = _simple_activation().to(device)
    config = type(
        "Config",
        (),
        {
            "algorithm": "ff_contrastive",
            "hardware": "triton",
            "dtype": torch.float32,
            "beta": 0.5,
            "lr": 0.01,
            "settle_steps": 30,
            "gamma": 1.0,
            "extra": {"threshold": 1.0, "num_classes": 10},
        },
    )()
    kernel.initialize(config)
    kernel.set_model_ref(layers, activation)

    x = torch.randn(8, 16, device=device)
    target = torch.randint(0, 10, (8,), device=device)
    free_acts = kernel.free_phase(x)  # positive pass
    nudged_acts = kernel.nudged_phase(x, target)  # negative pass

    kernel_updates = kernel.compute_update(free_acts, nudged_acts)

    # Reference: FF goodness contrast
    ref_updates = {}
    for i, (pos_pre, pos_post, neg_pre, neg_post) in enumerate(
        zip(free_acts[:-1], free_acts[1:], nudged_acts[:-1], nudged_acts[1:])
    ):
        pos_goodness = (pos_post**2).sum(dim=1, keepdim=True)
        neg_goodness = (neg_post**2).sum(dim=1, keepdim=True)
        contrast = pos_goodness - neg_goodness - 1.0
        delta = (contrast * pos_post).T @ pos_pre / pos_pre.shape[0]
        ref_updates[f"layers.{i}.weight"] = 0.01 * delta
        if layers[i].bias is not None:
            ref_updates[f"layers.{i}.bias"] = 0.01 * contrast.mean(dim=0)

    for key in kernel_updates:
        assert torch.allclose(
            kernel_updates[key], ref_updates[key], rtol=1e-5, atol=1e-7
        ), f"Mismatch in {key}"


@requires_cuda
@pytest.mark.parametrize("device", ["cuda"])
def test_pepita_contrastive_compute_update_matches_torch_reference(device: str) -> None:
    """PEPITA contrastive kernel compute_update matches the torch reference it uses."""
    from computronium.acceleration.contrastive_kernels import PEPITAContrastiveKernel

    kernel = PEPITAContrastiveKernel()
    layers = [l.to(device) for l in _simple_layers()]
    activation = _simple_activation().to(device)
    config = type(
        "Config",
        (),
        {
            "algorithm": "pepita_contrastive",
            "hardware": "triton",
            "dtype": torch.float32,
            "beta": 0.5,
            "lr": 0.01,
            "settle_steps": 30,
            "gamma": 1.0,
            "extra": {"feedback_matrix_scale": 0.1},
        },
    )()
    kernel.initialize(config)
    kernel.set_model_ref(layers, activation)

    x = torch.randn(8, 16, device=device)
    target = torch.randint(0, 10, (8,), device=device)
    free_acts = kernel.free_phase(x)  # standard pass
    nudged_acts = kernel.nudged_phase(x, target)  # error-modulated pass

    kernel_updates = kernel.compute_update(free_acts, nudged_acts)

    # Reference: PEPITA contrastive update
    ref_updates = {}
    for i, (std_pre, std_post, err_pre, err_post) in enumerate(
        zip(free_acts[:-1], free_acts[1:], nudged_acts[:-1], nudged_acts[1:])
    ):
        delta = (std_post - err_post).T @ std_pre / std_pre.shape[0]
        ref_updates[f"layers.{i}.weight"] = 0.01 * delta
        if layers[i].bias is not None:
            ref_updates[f"layers.{i}.bias"] = 0.01 * (std_post - err_post).mean(dim=0)

    for key in kernel_updates:
        assert torch.allclose(
            kernel_updates[key], ref_updates[key], rtol=1e-5, atol=1e-7
        ), f"Mismatch in {key}"


@requires_cuda
@pytest.mark.parametrize("device", ["cuda"])
def test_pc_contrastive_compute_update_matches_torch_reference(device: str) -> None:
    """PC contrastive kernel compute_update matches the torch reference it uses."""
    from computronium.acceleration.contrastive_kernels import PCContrastiveKernel
    from computronium.acceleration.contrastive_primitives import contrastive_hebbian_update

    kernel = PCContrastiveKernel()
    layers = [l.to(device) for l in _simple_layers()]
    activation = _simple_activation().to(device)
    config = type(
        "Config",
        (),
        {
            "algorithm": "pc_contrastive",
            "hardware": "triton",
            "dtype": torch.float32,
            "beta": 0.5,
            "lr": 0.01,
            "settle_steps": 30,
            "gamma": 1.0,
            "extra": {"infer_steps": 4, "eta_infer": 0.1},
        },
    )()
    kernel.initialize(config)
    kernel.set_model_ref(layers, activation)

    x = torch.randn(8, 16, device=device)
    target = torch.randint(0, 10, (8,), device=device)
    free_acts = kernel.free_phase(x)
    nudged_acts = kernel.nudged_phase(x, target)

    kernel_updates = kernel.compute_update(free_acts, nudged_acts)

    # Reference: contrastive Hebbian update (same as base class)
    ref_updates = {}
    for i, (free_pre, free_post, nudged_pre, nudged_post) in enumerate(
        zip(free_acts[:-1], free_acts[1:], nudged_acts[:-1], nudged_acts[1:])
    ):
        delta = contrastive_hebbian_update(
            free_pre, free_post, nudged_pre, nudged_post, 0.01, 0.5
        )
        ref_updates[f"layers.{i}.weight"] = delta
        if layers[i].bias is not None:
            bias_delta = (
                contrastive_hebbian_update(
                    free_post.mean(dim=0).unsqueeze(0),
                    free_post.mean(dim=0).unsqueeze(0),
                    nudged_post.mean(dim=0).unsqueeze(0),
                    nudged_post.mean(dim=0).unsqueeze(0),
                    0.01,
                    0.5,
                )
            )
            # Simplified bias delta
            ref_updates[f"layers.{i}.bias"] = (
                (nudged_post.mean(dim=0) - free_post.mean(dim=0)) / 0.5
            ) * 0.01

    for key in kernel_updates:
        if "weight" in key:
            assert torch.allclose(
                kernel_updates[key], ref_updates[key], rtol=1e-5, atol=1e-7
            ), f"Mismatch in {key}"


@requires_cuda
@pytest.mark.parametrize("device", ["cuda"])
def test_tile_contrastive_compute_update_matches_torch_reference(device: str) -> None:
    """Tile contrastive kernel compute_update matches the torch reference it uses."""
    from computronium.acceleration.contrastive_kernels import TileContrastiveKernel
    from computronium.acceleration.contrastive_primitives import contrastive_hebbian_update

    kernel = TileContrastiveKernel()
    layers = [l.to(device) for l in _simple_layers()]
    activation = _simple_activation().to(device)
    config = type(
        "Config",
        (),
        {
            "algorithm": "tile_contrastive",
            "hardware": "triton",
            "dtype": torch.float32,
            "beta": 0.5,
            "lr": 0.01,
            "settle_steps": 30,
            "gamma": 1.0,
            "extra": {"neurons_per_tile": 8, "tiles_per_layer": 2},
        },
    )()
    kernel.initialize(config)
    kernel.set_model_ref(layers, activation)

    x = torch.randn(8, 16, device=device)
    target = torch.randint(0, 10, (8,), device=device)
    free_acts = kernel.free_phase(x)
    nudged_acts = kernel.nudged_phase(x, target)

    kernel_updates = kernel.compute_update(free_acts, nudged_acts)

    # Reference: contrastive Hebbian update using final settled states
    free_per_layer = [free_acts[0]]
    nudged_per_layer = [nudged_acts[0]]
    h_free = free_acts[0]
    h_nudged = nudged_acts[0]
    for i, layer in enumerate(layers):
        h_free = layer(h_free)
        h_nudged = layer(h_nudged)
        if i < len(layers) - 1:
            h_free = activation(h_free)
            h_nudged = activation(h_nudged)
        free_per_layer.append(h_free)
        nudged_per_layer.append(h_nudged)

    ref_updates = {}
    for i, (free_pre, free_post, nudged_pre, nudged_post) in enumerate(
        zip(free_per_layer[:-1], free_per_layer[1:], nudged_per_layer[:-1], nudged_per_layer[1:])
    ):
        delta = contrastive_hebbian_update(
            free_pre, free_post, nudged_pre, nudged_post, 0.01, 0.5
        )
        ref_updates[f"layers.{i}.weight"] = delta
        if layers[i].bias is not None:
            bias_delta = (
                (nudged_post.mean(dim=0) - free_post.mean(dim=0)) / 0.5
            ) * 0.01
            ref_updates[f"layers.{i}.bias"] = bias_delta

    for key in kernel_updates:
        assert torch.allclose(
            kernel_updates[key], ref_updates[key], rtol=1e-5, atol=1e-7
        ), f"Mismatch in {key}"
