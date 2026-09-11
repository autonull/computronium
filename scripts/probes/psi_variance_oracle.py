"""ψ-Variance Oracle (TODO15 §1.1): is the exact mask-aware Jacobian
target separable by ReLU mask pattern, or is within-mask variance too
high for any affine (piecewise-ψ) correction?

Pure-tensor diagnostic on the frozen seed-0 D1 backbone (784→128⁴→10,
MNIST stage A). Rebuilds θ deterministically (SHA asserted against the
Session-12 lock 88f6decdb445), solves the readout ceiling ridge on
stage-B episodes, then on 1,000 FashionMNIST test images computes
per-image exact targets T_s1 = R* @ pinv(J_s1), clusters by the exact
mask pattern of layers 2-4, and reports:

- within-cluster variance of T vs across-cluster variance of the
  cluster means (top-3 clusters by frequency)
- condition number of the dominant-cluster ridge gram G_m + λI

Pre-registered verdict (TODO15 §1.1):
- within ≪ across AND cond < 1e6 → GO (piecewise-ψ validated)
- within ≈ across → NO-GO (flagship B at scale permanently closed)
- within ≪ across BUT cond > 1e6 → AMBIGUOUS (regularization redesign)

uv run python scripts/probes/psi_variance_oracle.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import hashlib
import time

import torch
from torch import nn
from w4_hidden_psi import RIDGE_LAMBDA, _LayerRidge
from w4_scaled_psi import (
    DEVICE,
    STAGE_B_EPISODES,
    _Data,
    _forward_acts,
    _onehot,
    _stage_a,
)


class _RidgeUnsolvableError(RuntimeError):
    """Ceiling ridge had no accumulated statistics."""


N_IMAGES = 1000
STREAM_S = 1
LOCK_SHA_PREFIX = "88f6decdb445"


def _fit_ceiling(system, ridge: _LayerRidge) -> tuple[torch.Tensor, torch.Tensor]:
    data = _Data()
    for _ in range(STAGE_B_EPISODES):
        x, y = data.episode("B")
        acts = _forward_acts(system, x)
        ridge.update(acts[-2], _onehot(y, 10))
    solved = ridge.solve()
    if solved is None:
        raise _RidgeUnsolvableError
    return solved


def main() -> int:
    t0 = time.time()
    system, a_mastery, sha = _stage_a(0)
    print(f"stage A mastery {a_mastery:.4f}  sha {sha[:12]}", flush=True)
    if not sha.startswith(LOCK_SHA_PREFIX):
        print(f"WARN: sha drift vs lock {LOCK_SHA_PREFIX} (continuing)")

    ceiling = _LayerRidge()
    mr, br = _fit_ceiling(system, ceiling)

    data = _Data()
    torch.manual_seed(20260909)
    x, y = data.probe("B")
    x, y = x[:N_IMAGES], y[:N_IMAGES]
    with torch.no_grad():
        streams = _forward_acts(system, x)
        post = streams[-1]
        residual = streams[-2] @ mr + br - post
        # exact stream-1 targets only (deepest reach, the D1 placement)
        weights = [
            m.weight for m in system.geometry._layers if isinstance(m, nn.Linear)
        ]
        n = len(weights)
        batch = x.shape[0]
        jacobian = weights[STREAM_S].T.unsqueeze(0).expand(batch, -1, -1)
        for k in range(STREAM_S, n - 1):
            masks = torch.diag_embed((streams[k + 1] > 0).float())
            jacobian = jacobian @ masks @ weights[k + 1].T
        pinv_j = torch.linalg.pinv(jacobian.detach().float())
        targets = (residual.unsqueeze(1) @ pinv_j).squeeze(1)  # (B, 128)

        # exact mask hash over layers 2-4 (the masks stream 1 crosses)
        mask_bits = torch.cat(
            [(streams[k + 1] > 0).flatten(1) for k in range(1, n - 1)], dim=1
        ).cpu()
        hashes = [
            hashlib.md5(row.numpy().tobytes()).hexdigest()[:8]  # ruff: ignore[hashlib-insecure-hash-function]
            for row in mask_bits
        ]

        by_cluster: dict[str, list[int]] = {}
        for i, h in enumerate(hashes):
            by_cluster.setdefault(h, []).append(i)
        top = sorted(by_cluster.items(), key=lambda kv: -len(kv[1]))[:3]
        dom = top[0][0]
        # ratchet (TODO15 §3, encountered live): singleton clusters make
        # within-variance trivially zero — variance ratios are undefined
        # without pool support. Mask-conditioning with no repeating masks
        # is NO-GO regardless of the ratio (each piecewise ridge would be
        # underdetermined).
        dom_n = len(top[0][1])
        if dom_n < 20:
            print(
                f"CLUSTERING DEGENERATE: {len(by_cluster)} masks over {batch} "
                f"images, dominant cluster n={dom_n} — no pool support; "
                "exact-mask piecewise-ψ is underdetermined per cluster.",
                flush=True,
            )
            print(
                "\nVERDICT: NO-GO (mask-conditioning provides no pooling)", flush=True
            )
            print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
            return 0
        dom = top[0][0]
        print(
            f"{len(by_cluster)} distinct masks over {batch} images; "
            f"top-3 cover {sum(len(v) for _, v in top)}",
            flush=True,
        )

        within = 0.0
        means = []
        for _, idx in top:
            t = targets[idx]
            means.append(t.mean(0))
            within += t.var(0, unbiased=False).mean().item() * len(idx)
        within /= sum(len(idx) for _, idx in top)
        means = torch.stack(means)
        across = means.var(0, unbiased=False).mean().item()
        print(f"within-cluster Var(T|mask) {within:.6f}", flush=True)
        print(f"across-cluster Var(E[T|mask]) {across:.6f}", flush=True)
        print(f"within/across ratio {within / max(across, 1e-12):.4f}", flush=True)

        idx = by_cluster[dom]
        src = streams[STREAM_S][idx]
        xa = torch.cat(
            (src, torch.ones(src.shape[0], 1, device=src.device)), dim=-1
        ).float()
        gram = xa.T @ xa
        lam = RIDGE_LAMBDA * gram.diagonal().mean().clamp_min(1e-12)
        eig = torch.linalg.eigvalsh(
            gram + lam * torch.eye(gram.shape[0], device=DEVICE)
        )
        cond = (eig[-1] / eig[0].clamp_min(1e-30)).item()
        print(f"dominant cluster n={len(idx)}  cond(G_m+λI) {cond:.3e}", flush=True)

        r_within, r_across = within, across
        go_cond = cond < 1e6
        if r_within < 0.1 * r_across and go_cond:
            verdict = "GO: piecewise-ψ mathematically validated"
        elif r_within >= 0.5 * r_across:
            verdict = "NO-GO: mask pattern does not resolve the target"
        elif r_within < 0.1 * r_across and not go_cond:
            verdict = "AMBIGUOUS: separable but ill-conditioned"
        else:
            verdict = "AMBIGUOUS: intermediate separability"
        print(f"\nVERDICT: {verdict}", flush=True)
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
