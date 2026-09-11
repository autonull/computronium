"""Lab quickstart — compose, train, compare ontology presets on CPU.

Quick mode: synthetic gaussian-blob task, 1 epoch, small MLPs — seconds.
"""

from __future__ import annotations

import argparse

from computronium_lab import Lab


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=5)
    args = parser.parse_args()

    lab = Lab(quick=True)
    results = lab.compare(
        ["backprop_mlp", "eqprop_mlp", "fa_mlp"],
        task="synthetic",
        epochs=args.epochs,
    )
    print(f"{'preset':16s} {'final_loss':>10s} {'final_acc':>10s} {'walltime':>9s}")
    for r in results:
        print(
            f"{r.preset:16s} {r.final_loss:10.4f} {r.final_accuracy:10.4f} "
            f"{r.walltime_s:8.2f}s"
        )
    lab.report("lab_quickstart_report.md")
    print("report written: lab_quickstart_report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
