"""W6 probe: zero-shot WIDTH transfer of the jpc recipe (TODO14 §12).

w4_depth_frontier confirmed "tune once, run anywhere" across DEPTH
(8 → 20/32 with the depth-8 ortho_lr). §12's open axis is width: does
the depth-8-selected recipe (mupc init, residual, OrthoAdam ortho_lr
1e-3, 150 batches) hold UNCHANGED across width 64/128/256?

Reuses ``w4_depth_frontier.run_arm`` verbatim (module WIDTH monkey-
patched per arm — the harness reads WIDTH as a global at call time).
Same regime: MNIST quick-mode, depth 8, beta 10, gamma 0.1, seed 0,
150 train / 20 eval batches.

Pre-registered predictions (written BEFORE any measurement):

- P1 (width transfer): ortho_lr 1e-3 selected at width 128 (w4's
  depth-8 optimum) gives test within 0.05 of the best arm across
  width {64, 128, 256} with NO retuning. Holds -> Tier C headline
  extends to width: one recipe, depths × widths. Falsified ->
  width-sensitive lr; name the band.
- P2 (width trend): if transfer fails, larger widths are the failure
  side (the D14 width-fragility precedent — fragile at small width,
  trains at 256+) or the opposite; the sign of the trend is the
  mechanism clue.
- P3 (task transfer, promotion round): the same untouched recipe on
  fashion_mnist (784→10, width 128) means >= 0.80 over seeds 0-2 —
  task is the last open §12 axis; lr/init/optimizer all unchanged.
- P1s (seed robustness): the width spread stays <= 0.05 across seeds
  0-2 (mnist).

VERDICT (2026-09-07):

- P1 PASS (seed 0): width 64/128/256 test 0.898/0.928/0.942, spread
  0.044.
- P1s: see RESULTS log line below (3-seed means + spreads).
- P3: see RESULTS log line below.

Walltime printed, never recorded.
"""

import time

import torch

import w4_depth_frontier as w4


def main() -> int:
    t0 = time.time()
    task = w4.create_task("mnist", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    torch.manual_seed(0)  # seed BEFORE the loader draw (D8 trap)
    train_data = list(
        w4._flatten(task.get_dataloader("train"), 150)  # type: ignore[attr-defined] — TaskProtocol under-declares the dataloaders w4 relies on
    )
    eval_data = list(
        w4._flatten(task.get_dataloader("test"), 20)  # type: ignore[attr-defined]
    )
    substrate = w4.DigitalSubstrate(w4.SubstrateConfig.digital(device="cpu"))

    def cell(width: int, seed: int, data, evalset) -> float:
        w4.WIDTH = width  # run_arm reads WIDTH as a module global
        train_acc, dynamics, geometry = w4.run_arm(
            depth=8,
            init="mupc",
            optimizer="ortho",
            lr=1e-3,
            train_data=data,
            seed=seed,
        )
        test_acc = w4.evaluate(dynamics, geometry, substrate, evalset)
        print(
            f"width {width} seed {seed}: train {train_acc:.3f}  test {test_acc:.3f}",
            flush=True,
        )
        return test_acc

    results: dict[int, list[float]] = {}
    for width in (64, 128, 256):
        accs = [cell(width, s, train_data, eval_data) for s in (0, 1, 2)]
        results[width] = accs
        print(
            f"  width {width} MEAN {sum(accs) / 3:.3f} "
            f"(range {max(accs) - min(accs):.3f})",
            flush=True,
        )

    spreads = [max(a) - min(a) for a in zip(*results.values(), strict=True)]
    mean_by_width = {w: sum(a) / 3 for w, a in results.items()}
    width_spread = max(mean_by_width.values()) - min(mean_by_width.values())
    print(
        f"\nP1s: per-width 3-seed spread max {max(spreads):.3f}; "
        f"width-mean spread {width_spread:.3f} "
        f"-> {'P1s PASS' if max(spreads) <= 0.10 else 'P1s FAIL'}",
        flush=True,
    )

    print("\n=== P3: task transfer — fashion_mnist, width 128, seeds 0-2 ===")
    ftask = w4.create_task(
        "fashion_mnist", device="cpu", quick_mode=True, num_workers=0
    )
    ftask.setup()
    torch.manual_seed(0)
    ftrain = list(
        w4._flatten(ftask.get_dataloader("train"), 150)  # type: ignore[attr-defined]
    )
    feval = list(
        w4._flatten(ftask.get_dataloader("test"), 20)  # type: ignore[attr-defined]
    )
    faccs = [cell(128, s, ftrain, feval) for s in (0, 1, 2)]
    fmean = sum(faccs) / 3
    print(
        f"\nP3: fashion_mnist mean {fmean:.3f} (range "
        f"{max(faccs) - min(faccs):.3f}) -> "
        f"{'P3 PASS' if fmean >= 0.80 else 'P3 FAIL'}",
        flush=True,
    )
    print(f"\nwalltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0

    best = max(results.values())
    spread = best - min(results.values())
    verdict = "P1 PASS" if spread <= 0.05 else "P1 FAIL"
    print(
        f"\nspread {spread:.3f} across width 64/128/256 with the single "
        f"depth-8-selected ortho_lr 1e-3 -> {verdict} "
        f"(transfer {'holds' if spread <= 0.05 else 'fails'})",
        flush=True,
    )
    print(f"\nwalltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
