"""Probe: does the strict FA chain hold for each geometry?

``RandomProjectionsCredit._layered_path`` walks the act list positionally
against the 2-D weights and requires a strict chain: act ``k`` is the input to
weight ``k``, act ``k+1`` is its output, and every act shares one batch
dimension. This probe reports, per geometry, whether that chain holds.

Run: uv run python scripts/probes/t87_fa_chain_scope.py
"""

from __future__ import annotations

import torch

from computronium.ontology.geometry import (
    AttentionGeometry,
    ConvGeometry,
    FeedforwardGeometry,
    GeometryConfig,
    RecurrentGeometry,
    TransformerGeometry,
)


def _chain_report(label: str, geom, x: torch.Tensor) -> None:
    acts = geom.forward_with_intermediates(x)
    names = [n for n, p in geom.params.items() if "weight" in n and p.ndim == 2]
    n_trans = len(acts) - 1
    problems: list[str] = []
    for k in range(min(n_trans, len(names))):
        w = geom.params[names[k]]
        if k + 1 >= len(acts):
            break
        out_ok = w.shape[0] == acts[k + 1].shape[-1]
        in_ok = w.shape[1] == acts[k].shape[-1]
        if not (out_ok and in_ok):
            problems.append(
                f"k={k} {names[k]} w={tuple(w.shape)} "
                f"acts[k]={tuple(acts[k].shape)} acts[k+1]={tuple(acts[k + 1].shape)}"
            )
    batches = {a.shape[0] for a in acts}
    print(f"\n=== {label} ===")
    print(f"acts={len(acts)} weights={len(names)} n_trans={n_trans}")
    print(f"act batch dims: {sorted(batches)}")
    print("chain problems:", len(problems))
    for p in problems[:4]:
        print("   ", p)


def main() -> None:
    torch.manual_seed(0)
    _chain_report(
        "feedforward",
        FeedforwardGeometry(
            GeometryConfig.feedforward(input_dim=16, output_dim=4, hidden_dims=(8, 8))
        ),
        torch.randn(3, 16),
    )
    _chain_report(
        "recurrent",
        RecurrentGeometry(
            GeometryConfig.recurrent(input_dim=16, output_dim=4, hidden_dims=(8, 8))
        ),
        torch.randn(3, 16),
    )
    _chain_report(
        "attention",
        AttentionGeometry(
            GeometryConfig.attention(
                input_dim=16, output_dim=4, hidden_dim=8, num_layers=1, num_heads=2
            )
        ),
        torch.randn(3, 16),
    )
    _chain_report(
        "conv",
        ConvGeometry(
            GeometryConfig.conv(
                input_dim=16,
                output_dim=4,
                input_hw=(4, 4),
                conv_channels=(8,),
                pool_hw=(2, 2),
            )
        ),
        torch.randn(3, 1, 4, 4),
    )
    _chain_report(
        "transformer LM",
        TransformerGeometry(
            GeometryConfig.causal_transformer(
                vocab_size=65, d_model=8, n_layers=1, n_heads=2, seq_len=4
            )
        ),
        torch.randint(0, 65, (3, 4)),
    )
    _chain_report(
        "transformer vision",
        TransformerGeometry(
            GeometryConfig.causal_transformer(
                vocab_size=4,
                d_model=8,
                n_layers=1,
                n_heads=2,
                seq_len=4,
                patch_size=2,
                patch_embed_dim=0,
                image_hw=(4, 4),
                in_channels=1,
            )
        ),
        torch.randn(3, 1, 4, 4),
    )


if __name__ == "__main__":
    main()
