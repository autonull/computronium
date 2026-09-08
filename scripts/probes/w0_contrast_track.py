"""W0 contrast-track probe: is the post-peak decay the OBJECTIVE or the
OPTIMIZER? (TODO14 next-step, the decisive W0 diagnostic)

Session 1 verdict: local_contrastive × muon 0.005 peaks ~600 steps
(top-1 0.190) and turns down by 3000 (0.131) under ANY schedule tested —
cosine decay extends the regime to ~1200 but the trajectory still turns.
The open question: does the per-block goodness CONTRAST itself decay as
the stream organizes (moving-target drift → the boundary is the
objective), or does the credit signal stay healthy while the updates
degrade (→ the optimizer/step axis is the lever, W0.3 ablations follow)?

Mechanism: at checkpoints {0, 200, ..., 1200} on the muon_mid arm, for
every ordered linear i, measure
    r_i   = ||G+_i - G-_i|| / ||G+_i||   (raw label contrast, pre-gate)
    gn_i  = RMS of the raw goodness-contrast gradient (pre-EMA)
with G computed exactly as ``LocalContrastiveCredit._tf_layer_grad``
does (pe excluded at the embed; attention applied at in_proj). Val
top-1/CE logged at each checkpoint to correlate signal health with the
trajectory turn.

Prediction (pre-registered): if the moving-target story is right, r_i
and gn_i on the DEEPER blocks decay materially by step 1200 vs step 200;
if instead they hold while val CE rises, the objective is not the
constraint. Embed is the fresh-weight control (w0_gain_diagnostic:
r_embed 1.08 vs 0.10-0.20 deeper, at init).

Run: ``uv run python scripts/probes/w0_contrast_track.py`` (~4 min CPU).
Walltime printed, never recorded.
"""

import time

import torch
from w0_tf_local_optimizers import (
    _ARMS,
    _build,
    _evaluate,
    _tokens,
    _val_windows,
)

CHECKPOINTS = (0, 200, 400, 600, 900, 1200)


def _contrast_row(  # ruff: ignore[too-many-locals] — measurement axis assembly
    system, x, y
) -> list[tuple[str, float, float]]:
    credit, geometry = system.credit, system.geometry
    b, t = x.shape
    y_flat = y.reshape(-1)
    linears = credit._tf_linears(geometry)
    y_neg = y_flat.view(b, t).roll(1, 0).reshape(b * t)
    rows = []
    for i, (name, lin) in enumerate(linears[:-1]):
        a_pos = credit._tf_recompute(geometry, x, y_flat, i, b, t, linears)
        a_neg = credit._tf_recompute(geometry, x, y_neg, i, b, t, linears)
        with torch.enable_grad():
            w = lin.weight.detach().requires_grad_(True)
            g_pos, g_neg = _tf_goodness(
                credit, geometry, w, a_pos, a_neg, i, y_flat, y_neg, b, t
            )
            loss = torch.nn.functional.softplus(
                credit.config.contrast_threshold
                - (g_pos.pow(2).mean() - g_neg.pow(2).mean())
            )
            (gw,) = torch.autograd.grad(loss, w)
        r = (g_pos - g_neg).norm() / (g_pos.norm() + 1e-12)
        rows.append((name, r.item(), gw.detach().pow(2).mean().sqrt().item()))
    return rows


def _tf_goodness(  # ruff: ignore[too-many-arguments, too-many-positional-arguments] — mirrors _tf_layer_grad's signature
    credit, geometry, w, a_pos, a_neg, i, y_flat, y_neg, b, t
):
    """G+/G- streams exactly as ``LocalContrastiveCredit._tf_layer_grad``."""
    g_pos = torch.nn.functional.linear(a_pos, w)
    g_neg = torch.nn.functional.linear(a_neg, w)
    if i == 0:
        emb = credit._tf_label_embedding(
            geometry.config.input_dim, geometry.d_model, w.device, w.dtype
        )
        g_pos += emb[y_flat]
        g_neg += emb[y_neg]
    elif (i - 1) % 4 == 0:
        g_pos = geometry._attention(g_pos, b, t)
        g_neg = geometry._attention(g_neg, b, t)
    return g_pos, g_neg


def main() -> int:  # ruff: ignore[too-many-locals] — probe loop
    t0 = time.time()
    train_t, val_t = _tokens()
    val = _val_windows(val_t, 0)
    from computronium.core.pipeline import run_train_step

    system = _build(0, _ARMS["muon_mid"])
    ctx, batch = 32, 32
    gen = torch.Generator().manual_seed(0)
    x = y = None
    header = f"{'step':>5} {'top-1':>6} {'CE':>6}  per-linear (r_i, grad-RMS)"
    print(header, flush=True)
    last = max(CHECKPOINTS)
    for step in range(last + 1):
        idx = torch.randint(0, len(train_t) - ctx - 1, (batch,), generator=gen)
        wins = torch.stack([train_t[i : i + ctx + 1] for i in idx])
        x, y = wins[:, :-1], wins[:, 1:].reshape(-1)
        if step in CHECKPOINTS:
            acc, ce = _evaluate(system, val)
            rows = _contrast_row(system, x, y)
            cells = "  ".join(
                f"{n.split('.')[-1]}:r={r:.3f},g={g:.2e}" for n, r, g in rows
            )
            print(f"{step:>5} {acc:.3f} {ce:.3f}  {cells}", flush=True)
        if step == last:
            break
        run_train_step(
            system.substrate,
            system.geometry,
            system.dynamics,
            system.credit,
            system.update,
            x,
            y,
        )
    print(f"\nwalltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
