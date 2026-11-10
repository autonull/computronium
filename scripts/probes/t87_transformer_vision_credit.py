"""Probe: act-chain alignment vs the local-credit contract.

``RandomProjectionsCredit._layered_path`` pairs acts positionally with the
2-D weights and requires a strict chain: ``acts[k+1]`` is the output of
``weight_names[k]`` and every act shares one batch dimension.

This probe prints, for each geometry, the act chain, the 2-D weight shapes and
the per-transition FA shape check, so the exact mismatch is visible.

Run: uv run python scripts/probes/t87_transformer_vision_credit.py
"""

from __future__ import annotations

import torch

from computronium.ontology.geometry import GeometryConfig, TransformerGeometry


def _vision_geometry() -> TransformerGeometry:
    return TransformerGeometry(
        GeometryConfig.causal_transformer(
            vocab_size=10,
            d_model=32,
            n_layers=2,
            n_heads=4,
            seq_len=49,
            patch_size=4,
            patch_embed_dim=0,
            image_hw=(28, 28),
            in_channels=1,
        )
    )


def _lm_geometry() -> TransformerGeometry:
    return TransformerGeometry(
        GeometryConfig.causal_transformer(
            vocab_size=65,
            d_model=32,
            n_layers=2,
            n_heads=4,
            seq_len=16,
        )
    )


def _report(label: str, geom: TransformerGeometry, x: torch.Tensor) -> None:
    acts = geom.forward_with_intermediates(x)
    names = [n for n, p in geom.params.items() if "weight" in n and p.ndim == 2]
    print(f"\n=== {label} ===")
    print(f"acts={len(acts)}  2-D weights={len(names)}")
    for i, a in enumerate(acts):
        print(f"  acts[{i}] {tuple(a.shape)}")
    for i, n in enumerate(names):
        w = geom.params[n]
        print(f"  w[{i}] {n} {tuple(w.shape)}")
    print("FA per-transition shape check (b.shape == (acts[k+1].w, acts[k].w)):")
    for k in range(len(acts) - 1):
        if k >= len(names):
            print(f"  k={k}: NO WEIGHT (surplus act)")
            continue
        w = geom.params[names[k]]
        ok_out = k + 1 < len(acts) and w.shape[0] == acts[k + 1].shape[-1]
        ok_in = k < len(acts) and w.shape[1] == acts[k].shape[-1]
        print(
            f"  k={k} {names[k]}: out_ok={ok_out} in_ok={ok_in} "
            f"batch[{k}]={acts[k].shape[0]} batch[{k + 1}]="
            f"{acts[k + 1].shape[0] if k + 1 < len(acts) else '-'}"
        )


def main() -> None:
    torch.manual_seed(0)
    _report("transformer LM", _lm_geometry(), torch.randint(0, 65, (2, 16)))
    _report("transformer vision", _vision_geometry(), torch.randn(2, 1, 28, 28))


if __name__ == "__main__":
    main()
