"""TODO95 S4 defect probe: does each near-chance primitive apply any update?

One step at the canonical small box (mnist, batch 4, 8 nodes), before/after
parameter snapshots. A primitive whose parameters are bit-identical before and
after applies no update at all: a defect, not a weak algorithm. A primitive
that moves but does not learn is a coordinate about the box, not a defect.

Run:
    uv run python scripts/probes/todo95_s4_fingerprint.py
"""

from __future__ import annotations

import torch

from computronium.experiment.evidence.liveness import (
    CANONICAL,
    one_step_fingerprint,
)

PROBES = (
    ("credit", "target_inversion"),
    ("credit", "pc_alm"),
    ("credit", "temporal_trace"),
    ("credit", "error_predictive_coding"),
    ("geometry", "conv"),
    ("update", "quantized_adam"),
    ("credit", "gradient"),
)


def main() -> None:
    for axis, name in PROBES:
        selection = {**CANONICAL, axis: name}
        try:
            before, after, count = one_step_fingerprint("mnist", selection)
        except Exception as exc:  # ruff: ignore[blind-except] - a probe reports
            print(f"{axis:10} {name:24} CRASH {type(exc).__name__}: {exc}")
            continue
        delta = (
            sum(
                (after[key].double() - before[key].double()).pow(2).sum().item()
                for key in before
            )
            ** 0.5
        )
        norm = sum(before[key].double().pow(2).sum().item() for key in before) ** 0.5
        moved = any(not torch.equal(before[key], after[key]) for key in before)
        print(
            f"{axis:10} {name:24} params={count:>7} moved={moved!s:5} "
            f"|dW|={delta:.3e} |W|={norm:.3e} relative={delta / norm:.3e}"
        )


if __name__ == "__main__":
    main()
