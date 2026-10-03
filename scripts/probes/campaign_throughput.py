"""What does one wall-second of a run buy? (TODO48b R8, §8.1 item 1)

``MEASURED_CELL_SECONDS`` is a *serial* per-cell cost: ``dynamics_cost.py``
times a run of one dynamics at a time and divides by the cells it stored. A
campaign, though, stores one record per seed and executes its batch 4-way
concurrent, so the two numbers differ by a factor the oracle was silently
missing — §8.1 measured a 1.5x understatement on a box whose backend runs
``max_workers=4``, and the first version of this session's own gate found a
**3.6x** one at 7.0 s/record against a published 0.710 s/cell.

Three facts are measured here, and the registry now carries all three:

1. **cell vs record.** One cell at ``n_seeds=5`` is five records. A projection
   that prices cells understates by the seed count, exactly.
2. **concurrency.** Cells run in parallel, so a run's walltime is *less* than
   the sum of its cells' serial costs. The speedup is the ratio the projection
   needs, and it is not free: a contended cell's own ``walltime_s`` inflates,
   so the same number is not comparable across concurrency levels.
3. **the two together.** What a declaration actually costs in wall seconds.

Run: ``uv run python scripts/probes/campaign_throughput.py``. It trains cells;
it is not a lock. ``tests/property/test_price_oracle_lock.py`` locks the
arithmetic the projection now does.
"""

from __future__ import annotations

import statistics
import time
from concurrent.futures import ThreadPoolExecutor

from computronium.experiment.execution.evaluate import cell_record
from computronium.experiment.schema.coordinate import Coordinate, Provenance, Schedule
from computronium.experiment.schema.run_spec import MEASURED_PARAM_BUDGET
from computronium.experiment.schema.seed_registries import seed_all_registries

# The campaign's own regime: 6 layers (the harvested default the spec inherits),
# L0, 1 epoch, batch_limit 2, hidden_dim 64, and the settle_step nearest the
# band's log centre. Measured 2026-10-03 on 16 cores + one RTX 3080.
_CAMPAIGN_PARAMS: dict[str, object] = {
    "num_layers": 6,
    "hidden_dim": 64,
    "settle_step": 0.03162,
}
_PROVENANCE = Provenance(
    env={},
    dataset="digits",
    dataset_version="1.0",
    code_sha="campaign_throughput",
    policy="campaign_throughput",
    links={},
)
_RECORDS = 8


def one_record(seed: int) -> float:
    """One seed's measurement: the store's atomic unit of cost."""
    coordinate = Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="energy_minimization",
        plasticity="fast_weights",
        credit="gradient",
        update="euclidean",
        params=dict(_CAMPAIGN_PARAMS),
    )
    schedule = Schedule(
        fidelity="L0",
        seed=seed,
        n_seeds=1,
        epochs=1,
        batch_limit=2,
        budget_id="campaign_throughput",
        task_id="digits",
        param_budget=MEASURED_PARAM_BUDGET,
    )
    return float(cell_record(coordinate, schedule, _PROVENANCE).payload["walltime_s"])


def measure(workers: int) -> tuple[float, float, float]:
    """Wall seconds, serial cell seconds, and the mean record's own time."""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        started = time.perf_counter()
        times = list(pool.map(one_record, range(_RECORDS)))
    elapsed = time.perf_counter() - started
    return elapsed, sum(times), statistics.mean(times)


def main() -> None:
    seed_all_registries()
    print(f"regime: campaign defaults {_CAMPAIGN_PARAMS}, L0, 1 epoch, batch_limit 2")
    print(
        f"{'workers':>7}  {'wall_s':>8}  {'serial_s':>9}  {'speedup':>8}  "
        f"{'record_wall_s':>13}  {'mean_record_s':>13}"
    )
    for workers in (1, 2, 4, 8):
        elapsed, serial, mean_record = measure(workers)
        print(
            f"{workers:7d}  {elapsed:8.2f}  {serial:9.2f}  {serial / elapsed:7.2f}x"
            f"  {elapsed / _RECORDS:13.3f}  {mean_record:13.3f}"
        )
    print(
        "\nThe registry's MEASURED_CELL_SECONDS is the serial column; a run's\n"
        "walltime is the serial column divided by its speedup, times n_seeds per\n"
        "cell. Neither factor is visible from the other: a projection that uses\n"
        "one and not the other is wrong by that factor, in opposite directions\n"
        "for the price table (serial) and the record count (per seed)."
    )


if __name__ == "__main__":
    main()
