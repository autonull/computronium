"""The seven-beat demonstration, dispatched through the real commands."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse

_DEMO_BEATS: tuple[tuple[str, str, str], ...] = (
    ("0", "the machine is ready", "import optuna, scipy, torchvision, duckdb"),
    ("1", "the declared space, priced", "comp run demo --dry-run"),
    ("2", "execution: cells, rounds, verdicts", "comp run demo"),
    ("3", "the ledger: what landed", "comp status"),
    ("4", "the governed result", "comp report"),
    ("5", "what is unreached", "comp coverage report"),
    ("6", "what we learned", "the three results we already own"),
)


_DEMO_RESULTS: tuple[str, ...] = (
    "deep EqProp boundary (docs/eqprop_deep_limitation.md): multi-layer vanilla "
    "EqProp does not learn — slope -1.19, R^2=0.80; DirectedEP restores the "
    "signal but not accuracy (9.2%, chance for 10 classes). Gate G2 FAILED.",
    "phantom-knob audit (docs/phantom_knob_audit.md): a search key sampled but "
    "dropped at construction poisons parity and liveness identically; detected "
    "by construction.phantom_knobs and enforced by validate_all_rule_spaces().",
    "rho(J) vs sigma_max (docs/CORRECTIONS.md): power iteration reported as a "
    "spectral radius on nonnormal J converged to 0.5 while ||J||_2 = 10.025; "
    "caught by test_jacobian_amplification and replaced by three estimators.",
)


def _demo_call(argv: list[str]) -> int:
    """Run one beat through the same parser and handler the user would."""
    from computronium.experiment.surface.cli import main

    return main(argv)


def _demo_control(store_path: str) -> tuple[bool, str]:
    """G13: the gradient arm must clear chance before a comparison is published."""
    from computronium.experiment.evidence import RecordStore, StoreConfig
    from computronium.experiment.surface.report import chance_level

    store = RecordStore(StoreConfig(path=store_path, read_only=True))
    with store:
        runs = store.query_runs()
        if not runs:
            return False, "no run in the store"
        records = [
            record
            for record in store.query_records(run_id=runs[0].run_id)
            if record.credit == "gradient"
        ]
    values = [
        float(record.payload["val_acc"])
        for record in records
        if isinstance(record.payload.get("val_acc"), (int, float))
    ]
    if not values:
        return False, "the gradient arm measured no validation accuracy"
    mean = sum(values) / len(values)
    chance = chance_level(records[0].schedule.task_id, "val_acc") or 0.0
    floor = max(3.0 * chance, chance + 0.2)
    return (
        mean > floor,
        f"gradient val_acc={mean:.4f} vs chance={chance:.2f} (floor {floor:.2f})",
    )


def _cmd_demo(args: argparse.Namespace) -> int:
    """The single entry point: seven beats over the same commands.

    No engine logic lives here. Each beat dispatches the command it names, so
    the demonstration cannot drift from the software it demonstrates.
    """
    import importlib

    store = args.store
    print("=" * 80)
    print("COMPUTRONIUM DEMO — seven beats")
    print("=" * 80)

    print(f"\n[0] {_DEMO_BEATS[0][1]}")
    try:
        for module in ("optuna", "scipy", "torchvision", "duckdb"):
            importlib.import_module(module)
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"  imports: OK; device: {device}")
    except Exception as exc:  # ruff: ignore[blind-except] - beat 0 is a smoke
        print(f"  imports failed: {exc}")
        return 1

    beats = [
        (1, ["run", "demo", "--store", store, "--dry-run"]),
        (2, ["run", "demo", "--store", store]),
        (3, ["status", "--store", store]),
        (
            4,
            ["report", "--store", store, "--format", "text"]
            + (["--run-id", args.run_id] if args.run_id else []),
        ),
        (5, ["coverage", "report", "--store", store]),
    ]
    for index, argv in beats:
        print(f"\n[{index}] {_DEMO_BEATS[index][1]}")
        print(f"  equivalent: {_DEMO_BEATS[index][2]}")
        code = _demo_call(argv)
        if code != 0:
            print(f"  beat {index} exited {code}")
            return code
        if index == 2:
            ok, message = _demo_control(store)
            print(f"  positive control: {message}")
            if not ok:
                print("  the control arm is at chance: this comparison is invalid")
                return 1

    print(f"\n[6] {_DEMO_BEATS[6][1]}")
    for line in _DEMO_RESULTS:
        print(f"  - {line}")
    return 0
