"""W0.2 gain diagnostic (TODO14 §4): per-block label-contrast magnitude in
the transformer local_contrastive cell — measurement only, no training.

For every ordered linear i (embed, per-block in/out/ffn1/ffn2, head):
    r_i = ||G+_i - G-_i|| / ||G_i||
with G = the layer's own output stream (the goodness carrier), G+ the
true-label injection, G- the batch-rolled one. The §4 hypothesis: the
fixed label injection modulates a much larger stream by ~1%, so the
contrast's direction is noise-dominated; this pass quantifies r_i per
block BEFORE any gain sweep, so the follow-up sweep can target
controlled regimes (0.1% .. 10%) instead of searching blind.

Prediction (pre-registered): r_i ≪ 1 for all i at the current injection
gain (RMS 0.088 label vs ~0.79 stream — expected ~1-2% at the embed
output, decaying with depth as LayerNorms renormalize). If r_i is
instead already O(0.1+) somewhere, the noise-domination story is wrong
and W0.2 is not the lever.

Walltime printed, never recorded.
"""

import time

import torch

from computronium import (
    CreditAssignmentConfig,
    GeometryConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    compose_system_from_configs,
)
from computronium.data.lm import get_lm_dataset

CTX = 32
BATCH = 32
D_MODEL = 128
N_LAYERS = 2
N_HEADS = 4


def main() -> int:
    t0 = time.time()
    train_ds = get_lm_dataset("tiny_shakespeare", seq_len=CTX + 1, split="train")
    train_t = train_ds.data.long()
    gen = torch.Generator().manual_seed(0)
    idx = torch.randint(0, len(train_t) - CTX - 1, (BATCH,), generator=gen)
    wins = torch.stack([train_t[i : i + CTX + 1] for i in idx])
    x, y = wins[:, :-1], wins[:, 1:].reshape(-1)

    from computronium import ParameterUpdateConfig

    torch.manual_seed(0)
    system = compose_system_from_configs(
        SubstrateConfig.digital(),
        GeometryConfig.causal_transformer(
            vocab_size=65,
            d_model=D_MODEL,
            n_layers=N_LAYERS,
            n_heads=N_HEADS,
            seq_len=CTX,
        ),
        StateDynamicsConfig.instantaneous(),
        CreditAssignmentConfig.local_contrastive(
            ema_beta=0.99,
            readout_scale=1.0,
            sequential_lr=0.005,
            contrast_threshold=2.0,
        ),
        ParameterUpdateConfig.euclidean(step_size=0.005, grad_clip=1.0),
    )
    credit = system.credit
    geometry = system.geometry
    b, t = x.shape
    y_flat = y.reshape(-1)
    linears = credit._tf_linears(geometry)
    y_neg = y_flat.view(b, t).roll(1, 0).reshape(b * t)

    print(
        f"{'linear':>22} {'|G+|':>10} {'|G-|':>10} {'r_i':>10}",
        flush=True,
    )
    for i, (name, lin) in enumerate(linears[:-1]):
        a_pos = credit._tf_recompute(geometry, x, y_flat, i, b, t, linears)
        a_neg = credit._tf_recompute(geometry, x, y_neg, i, b, t, linears)
        with torch.no_grad():
            w = lin.weight.detach()
            g_pos = torch.nn.functional.linear(a_pos, w)
            g_neg = torch.nn.functional.linear(a_neg, w)
            if i == 0:
                # goodness excludes pe (w2_p4 contract): add label emb
                emb = credit._tf_label_embedding(65, D_MODEL, a_pos.device, a_pos.dtype)
                g_pos = g_pos + emb[y_flat]
                g_neg = g_neg + emb[y_neg]
            elif (i - 1) % 4 == 0:
                g_pos = geometry._attention(g_pos, b, t)
                g_neg = geometry._attention(g_neg, b, t)
            r = (g_pos - g_neg).norm() / (g_pos.norm() + 1e-12)
            print(
                f"{name:>22} {g_pos.norm():10.3f} {g_neg.norm():10.3f} {r:10.4f}",
                flush=True,
            )

    # The label channel's own scale at the injection point.
    emb = credit._tf_label_embedding(65, D_MODEL, torch.device("cpu"), torch.float32)
    stream_rms = 0.79  # w2_p4's measured stream RMS at the injection point
    print(
        f"\nlabel emb RMS {emb.pow(2).mean().sqrt():.3f} "
        f"(stream RMS ~{stream_rms}) -> injection contrast ~"
        f"{emb.pow(2).mean().sqrt() / stream_rms * 100:.1f}%",
        flush=True,
    )
    print(f"\nwalltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
